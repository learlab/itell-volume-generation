"""
text_extractor.py
-----------------
Load iTELL JSON volumes and convert them into flat records suitable for
linguistic analysis. Each record represents one chunk (the finest-grain
unit of analysis). Page- and volume-level text strings are also attached
so that global cohesion indices can be computed.

iTELL JSON schema (from src/pipeline/models.py):
  NewVolume
    .Title, .Description, .VolumeSummary
    .Pages: list[NewPage]
      .Title, .Order, .ReferenceSummary
      .Content: list[NewChunk | NewPlainChunk]
        NewChunk:      __component = "page.chunk"
                       .Header, .Text (HTML), .KeyPhrase, .Question, .ConstructedResponse
        NewPlainChunk: __component = "page.plain-chunk"
                       .Header, .Text (HTML)
"""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# HTML stripping
# ---------------------------------------------------------------------------

class _StripHTML(HTMLParser):
    """Minimal HTML → plain-text converter (no external deps)."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def strip_html(raw: str) -> str:
    """Return plain text from an HTML string, collapsing whitespace."""
    parser = _StripHTML()
    parser.feed(html.unescape(raw))
    text = parser.get_text()
    # collapse runs of whitespace / newlines
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Mode inference
# ---------------------------------------------------------------------------

_KNOWN_MODES = {"faithful", "simplified", "condensed", "interactive"}


def _infer_mode(filename: str, mode_override: Optional[str] = None) -> str:
    """
    Infer generation mode from the JSON filename.

    Expected naming convention:  <anything>_<mode>.json
    e.g.  chapter3_faithful.json, vol01_simplified.json

    If no mode token is found, returns "unknown".
    """
    if mode_override:
        return mode_override.lower()

    stem = Path(filename).stem.lower()
    for part in reversed(stem.split("_")):
        if part in _KNOWN_MODES:
            return part
    return "unknown"


# ---------------------------------------------------------------------------
# Core loaders
# ---------------------------------------------------------------------------

def load_volume(json_path: Path) -> Dict[str, Any]:
    """Return the raw parsed JSON dict for one volume file."""
    with open(json_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_records(
    json_path: Path,
    volume_id: Optional[str] = None,
    mode_override: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Parse one iTELL JSON file and return a list of chunk-level records.

    Each record is a flat dict with:
      volume_id       – filename stem (or caller-supplied id)
      mode            – generation mode inferred from filename
      page_order      – integer page index (1-based)
      page_title      – page Title field
      chunk_index     – 0-based position within page
      chunk_type      – "chunk" or "plain-chunk"
      chunk_header    – chunk Header field
      chunk_text      – plain text of chunk (HTML stripped)
      page_text       – concatenated plain text of all chunks on this page
      volume_text     – concatenated plain text of entire volume

    Cohesion features that compare adjacent chunks should use chunk_text
    within the same (volume_id, page_order) group.
    Global/volume-level features should use volume_text.
    """
    json_path = Path(json_path)
    raw = load_volume(json_path)

    vid = volume_id or json_path.stem
    mode = _infer_mode(json_path.name, mode_override)

    # Build page texts first so we can attach volume_text
    pages_data: List[Dict[str, Any]] = []

    for page in raw.get("Pages", []):
        page_title = page.get("Title", "")
        page_order = int(page.get("Order", 0))
        chunks = page.get("Content", [])

        chunk_records = []
        for idx, chunk in enumerate(chunks):
            component = chunk.get("__component", "")
            chunk_type = "plain-chunk" if "plain" in component else "chunk"
            raw_text = chunk.get("Text", "")
            plain = strip_html(raw_text)

            chunk_records.append(
                {
                    "volume_id": vid,
                    "mode": mode,
                    "page_order": page_order,
                    "page_title": page_title,
                    "chunk_index": idx,
                    "chunk_type": chunk_type,
                    "chunk_header": chunk.get("Header", ""),
                    "chunk_text": plain,
                    # page_text and volume_text filled below
                }
            )

        page_text = " ".join(r["chunk_text"] for r in chunk_records)
        pages_data.append({"page_text": page_text, "records": chunk_records})

    volume_text = " ".join(p["page_text"] for p in pages_data)

    records: List[Dict[str, Any]] = []
    for page in pages_data:
        for rec in page["records"]:
            rec["page_text"] = page["page_text"]
            rec["volume_text"] = volume_text
            records.append(rec)

    return records


def extract_all(
    input_dir: Path,
    mode_override: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Walk *input_dir* for all *.json files and return the combined record list.
    Skips files that cannot be parsed (logs a warning).
    """
    import logging

    logger = logging.getLogger(__name__)
    all_records: List[Dict[str, Any]] = []

    for json_path in sorted(Path(input_dir).glob("*.json")):
        try:
            records = extract_records(json_path, mode_override=mode_override)
            all_records.extend(records)
            logger.info("Loaded %d chunks from %s", len(records), json_path.name)
        except Exception as exc:
            logger.warning("Skipping %s: %s", json_path.name, exc)

    return all_records
