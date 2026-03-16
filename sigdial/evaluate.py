"""
evaluate.py
-----------
Automated discourse evaluation pipeline for iTELL AI-generated educational volumes.

Targets SIGDIAL 2026 (27th Annual Meeting of the Special Interest Group on
Discourse and Dialogue, Atlanta GA). Paper deadline: April 20, 2026.
https://2026.sigdial.org/calls/main_conference/

Research question: Do generation modes (Faithful / Simplified / Condensed /
Interactive) produce systematically different discourse profiles across cohesion,
readability, and linguistic complexity dimensions?

Usage
-----
  python evaluate.py run --input-dir path/to/jsons --output results/features.csv

  # Run only specific feature families:
  python evaluate.py run --input-dir jsons/ --output out.csv --features cohesion readability

  # Aggregate to page level instead of chunk level:
  python evaluate.py run --input-dir jsons/ --output out.csv --level page

  # After human ratings are collected, compute automated-human correlations:
  python evaluate.py correlate --feature-csv results/features.csv \
                               --human-csv results/human_ratings.csv \
                               --output results/correlations.csv

  # One-way ANOVA across modes for all features:
  python evaluate.py stats --feature-csv results/features.csv

Pipeline overview
-----------------
1. Text extraction   extractor.text_extractor  → flat records (one row per chunk)
2. Feature extraction
     Cohesion        features.cohesion          → referential, connective, semantic
     Readability     features.readability       → FK, Dale-Chall, SMOG, …
     Complexity      features.complexity        → MTLD, dep-distance, MLS, …
3. Output            CSV (one row per chunk) + per-mode summary TSV
4. Statistics        analysis.stats             → ANOVA table + correlation matrix
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Feature families available
# ---------------------------------------------------------------------------

ALL_FAMILIES = ["cohesion", "readability", "complexity"]


def _compute_features(record: dict, families: List[str]) -> dict:
    """
    Given a chunk record (from text_extractor.extract_records), compute
    all requested feature families and return a merged feature dict.
    """
    text = record.get("chunk_text", "")
    features: dict = {}

    if "cohesion" in families:
        from features.cohesion import cohesion_indices
        features.update(cohesion_indices(text))

    if "readability" in families:
        from features.readability import readability_indices
        features.update(readability_indices(text))

    if "complexity" in families:
        from features.complexity import complexity_indices
        features.update(complexity_indices(text))

    return features


# ---------------------------------------------------------------------------
# Main evaluation pipeline
# ---------------------------------------------------------------------------

def run_evaluate(
    input_dir: Path,
    output: Path,
    families: List[str],
    level: str = "chunk",
    mode_override: Optional[str] = None,
) -> None:
    """
    Extract text from all JSON files in *input_dir*, compute features,
    and write results to *output* CSV.

    Parameters
    ----------
    input_dir     : directory containing iTELL JSON files
    output        : path for the output CSV
    families      : list of feature families to compute
    level         : 'chunk' (default) or 'page' — aggregation level
    mode_override : force all files to this mode (ignores filename inference)
    """
    import pandas as pd
    from extractor.text_extractor import extract_all

    logger.info("Loading volumes from %s", input_dir)
    records = extract_all(input_dir, mode_override=mode_override)

    if not records:
        logger.error("No records loaded. Check that %s contains *.json files.", input_dir)
        sys.exit(1)

    logger.info("Loaded %d chunk records from %d files", len(records),
                len({r["volume_id"] for r in records}))

    # Aggregate to page level if requested
    if level == "page":
        records = _aggregate_to_page(records)
        logger.info("Aggregated to %d page records", len(records))

    rows = []
    total = len(records)
    for i, rec in enumerate(records, 1):
        if i % 100 == 0 or i == total:
            logger.info("  Computing features %d / %d", i, total)
        feat = _compute_features(rec, families)
        row = {
            "volume_id":   rec["volume_id"],
            "mode":        rec["mode"],
            "page_order":  rec.get("page_order"),
            "page_title":  rec.get("page_title", ""),
            "chunk_index": rec.get("chunk_index", ""),
            "chunk_type":  rec.get("chunk_type", ""),
            "chunk_header":rec.get("chunk_header", ""),
            **feat,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    logger.info("Saved feature matrix (%d rows × %d cols) to %s",
                len(df), len(df.columns), output)

    # Summary TSV
    summary_path = output.with_suffix(".summary.tsv")
    _write_summary(df, summary_path)


def _aggregate_to_page(records: list) -> list:
    """Merge all chunks within a page into a single record."""
    from collections import defaultdict
    pages: dict = defaultdict(list)
    for r in records:
        key = (r["volume_id"], r["mode"], r["page_order"])
        pages[key].append(r)

    merged = []
    for (vid, mode, order), chunks in sorted(pages.items()):
        page_text = " ".join(c["chunk_text"] for c in chunks)
        merged.append({
            "volume_id":   vid,
            "mode":        mode,
            "page_order":  order,
            "page_title":  chunks[0]["page_title"],
            "chunk_index": "",
            "chunk_type":  "page",
            "chunk_header":"",
            "chunk_text":  page_text,
            "page_text":   page_text,
            "volume_text": chunks[0]["volume_text"],
        })
    return merged


def _write_summary(df: "pd.DataFrame", path: Path) -> None:
    """Write per-mode descriptive statistics to a TSV file."""
    from analysis.stats import descriptives
    try:
        summ = descriptives(df)
        summ.to_csv(path, sep="\t")
        logger.info("Saved per-mode summary to %s", path)
    except Exception as exc:
        logger.warning("Could not write summary: %s", exc)


# ---------------------------------------------------------------------------
# Correlation subcommand (post human ratings)
# ---------------------------------------------------------------------------

def run_correlate(
    feature_csv: Path,
    human_csv: Path,
    output: Path,
    method: str = "pearson",
) -> None:
    """
    Merge feature CSV with human ratings CSV and compute automated-human
    correlation table.

    The human CSV must contain columns:
      volume_id, page_order, chunk_index  (join keys)
      + one column per rating dimension
      e.g. h_local_cohesion, h_global_coherence, h_comprehensibility,
           h_lexical_fit, h_informativeness
    """
    import pandas as pd
    from analysis.stats import human_correlation

    feat_df = pd.read_csv(feature_csv)
    human_df = pd.read_csv(human_csv)

    join_keys = [k for k in ["volume_id", "page_order", "chunk_index"]
                 if k in feat_df.columns and k in human_df.columns]

    merged = feat_df.merge(human_df, on=join_keys, how="inner")
    logger.info("Merged %d rows for correlation analysis", len(merged))

    _skip = {"volume_id", "mode", "page_order", "page_title",
             "chunk_index", "chunk_type", "chunk_header",
             "chunk_text", "page_text", "volume_text"}
    automated_cols = [c for c in feat_df.select_dtypes("number").columns
                      if c not in _skip]
    human_cols = [c for c in human_df.columns
                  if c.startswith("h_") or c not in feat_df.columns]
    human_cols = [c for c in human_cols if c not in join_keys]

    corr = human_correlation(merged, automated_cols, human_cols, method=method)
    output.parent.mkdir(parents=True, exist_ok=True)
    corr.to_csv(output)
    logger.info("Saved %s correlation table to %s", method, output)


# ---------------------------------------------------------------------------
# ANOVA subcommand
# ---------------------------------------------------------------------------

def run_stats(feature_csv: Path, output: Path) -> None:
    """Run one-way ANOVA across modes for all features and save table."""
    import pandas as pd
    from analysis.stats import anova_table

    df = pd.read_csv(feature_csv)
    table = anova_table(df)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output)
    logger.info("Saved ANOVA table to %s", output)
    logger.info("\n%s", table.to_string())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluate",
        description="K-12 AI discourse evaluation pipeline for iTELL volumes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- evaluate subcommand
    ev = sub.add_parser("run", help="Extract features from a directory of JSON volumes.")
    ev.add_argument("--input-dir", type=Path, required=True,
                    help="Directory containing iTELL JSON files.")
    ev.add_argument("--output", type=Path, default=Path("output/features.csv"),
                    help="Output CSV path (default: output/features.csv).")
    ev.add_argument(
        "--features", nargs="+", choices=ALL_FAMILIES, default=ALL_FAMILIES,
        help="Feature families to compute (default: all).",
    )
    ev.add_argument("--level", choices=["chunk", "page"], default="chunk",
                    help="Unit of analysis: 'chunk' (default) or 'page'.")
    ev.add_argument("--mode", default=None,
                    help="Force all files to this mode (overrides filename inference).")

    # -- correlate subcommand
    co = sub.add_parser("correlate", help="Compute automated-vs-human correlations.")
    co.add_argument("--feature-csv", type=Path, required=True)
    co.add_argument("--human-csv", type=Path, required=True)
    co.add_argument("--output", type=Path, default=Path("output/correlations.csv"))
    co.add_argument("--method", choices=["pearson", "spearman"], default="pearson")

    # -- stats subcommand
    st = sub.add_parser("stats", help="Run ANOVA across modes for all features.")
    st.add_argument("--feature-csv", type=Path, required=True)
    st.add_argument("--output", type=Path, default=Path("output/anova.csv"))

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_evaluate(
            input_dir=args.input_dir,
            output=args.output,
            families=args.features,
            level=args.level,
            mode_override=args.mode,
        )
    elif args.command == "correlate":
        run_correlate(
            feature_csv=args.feature_csv,
            human_csv=args.human_csv,
            output=args.output,
            method=args.method,
        )
    elif args.command == "stats":
        run_stats(feature_csv=args.feature_csv, output=args.output)


if __name__ == "__main__":
    main()
