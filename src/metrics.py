import argparse
import json
import csv
import re
import html
import unicodedata
from typing import Dict, Any, List, Tuple, Optional

try:
    import evaluate
    BLEURT_AVAILABLE = True
    print("BLEURT loaded successfully!")
except Exception as e:
    print(f"Failed to load BLEURT: {e}")
    BLEURT_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    from rapidfuzz import process, fuzz
    FUZZY_AVAILABLE = True
    print("rapidfuzz loaded successfully!")
except Exception as e:
    print(f"Failed to load rapidfuzz: {e}")
    FUZZY_AVAILABLE = False

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def load_json(path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file, return None if there's a syntax error"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON syntax error in {path}: {e}")
        print(f"  -> Skipping this file, values will be blank in output")
        return None
    except FileNotFoundError:
        print(f"WARNING: File not found: {path}")
        return None


def clean_text(s: str) -> str:
    s = "" if s is None else str(s)
    s = html.unescape(s)
    s = TAG_RE.sub(" ", s)
    s = unicodedata.normalize("NFKC", s)
    s = WS_RE.sub(" ", s).strip()
    return s


def levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # Ensure a is the shorter string to reduce memory
    if len(a) > len(b):
        a, b = b, a

    previous_row = list(range(len(a) + 1))
    for j, bj in enumerate(b, start=1):
        current_row = [j]
        aj_prev = None
        for i, ai in enumerate(a, start=1):
            substitution_cost = 0 if ai == bj else 1
            insert_cost = current_row[i - 1] + 1
            delete_cost = previous_row[i] + 1
            replace_cost = previous_row[i - 1] + substitution_cost
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        previous_row = current_row
    return previous_row[-1]


def strip_html(text: str) -> str:
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize Unicode (e.g., fancy quotes)
    text = unicodedata.normalize("NFKC", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_page_levenshtein(title: str, content_items: List[Dict[str, Any]], lowercase: bool = True) -> str:
    parts: List[str] = [title or ""]
    for item in content_items or []:
        text = item.get("Text", "")
        if not isinstance(text, str):
            continue
        parts.append(text)
    combined = "\n".join(parts)
    cleaned = strip_html(combined)
    if lowercase:
        cleaned = cleaned.lower()
    return cleaned


def build_pages_map_levenshtein(data_obj: Optional[Dict[str, Any]], lowercase: bool = True) -> Dict[int, Tuple[str, str]]:
    pages: Dict[int, Tuple[str, str]] = {}
    if data_obj is None:
        return pages
    # Check for different possible key names
    page_list = data_obj.get("data", []) or data_obj.get("pages", []) or data_obj.get("Pages", [])

    for idx, page in enumerate(page_list):
        order = page.get("Order")
        if order is None:
            order = idx  # Use index if Order doesn't exist
        title = page.get("Title", "")
        content = page.get("Content", [])
        if not isinstance(order, int):
            try:
                order = int(order)
            except Exception:
                order = idx  # Use index as fallback
        processed = preprocess_page_levenshtein(title, content, lowercase=lowercase)
        pages[order] = (title, processed)
    return pages


def rouge_l_f_score(ref: str, hyp: str) -> float:
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return WS_RE.split(text.strip())
    
    def _lcs_length(a: List[str], b: List[str]) -> int:
        if not a or not b:
            return 0
        la, lb = len(a), len(b)
        if la < lb:
            a, b = b, a
            la, lb = lb, la
        prev = [0] * (lb + 1)
        for i in range(1, la + 1):
            cur = [0]
            ai = a[i - 1]
            for j in range(1, lb + 1):
                if ai == b[j - 1]:
                    cur.append(prev[j - 1] + 1)
                else:
                    cur.append(max(prev[j], cur[-1]))
            prev = cur
        return prev[-1]
    
    ref_toks = _tokenize(ref)
    hyp_toks = _tokenize(hyp)
    if not ref_toks or not hyp_toks:
        return 0.0
    lcs = _lcs_length(ref_toks, hyp_toks)
    prec = lcs / len(hyp_toks)
    rec = lcs / len(ref_toks)
    if prec + rec == 0:
        return 0.0
    beta2 = 1.2 * 1.2
    return (1 + beta2) * prec * rec / (rec + beta2 * prec)


def bleu_sentence(ref: str, hyp: str, max_n: int = 4) -> float:
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return WS_RE.split(text.strip())
    
    def _ngram_counts(tokens: List[str], n: int) -> Dict[Tuple[str, ...], int]:
        counts: Dict[Tuple[str, ...], int] = {}
        if n <= 0 or len(tokens) < n:
            return counts
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i : i + n])
            counts[ngram] = counts.get(ngram, 0) + 1
        return counts
    
    ref_tokens = _tokenize(ref)
    hyp_tokens = _tokenize(hyp)
    if not ref_tokens or not hyp_tokens:
        return 0.0

    precisions: List[float] = []
    for n in range(1, max_n + 1):
        ref_counts = _ngram_counts(ref_tokens, n)
        hyp_counts = _ngram_counts(hyp_tokens, n)
        if not hyp_counts:
            precisions.append(0.0)
            continue
        match = 0
        total = 0
        for ng, c in hyp_counts.items():
            total += c
            match += min(c, ref_counts.get(ng, 0))
        epsilon = 1e-9
        precisions.append((match + epsilon) / (total + epsilon))

    c = len(hyp_tokens)
    r = len(ref_tokens)
    if c == 0:
        return 0.0
    if c > r:
        bp = 1.0
    else:
        from math import exp
        bp = exp(1 - r / c)

    from math import log, exp
    score = bp * exp(sum((1.0 / max_n) * log(p) for p in precisions))
    return float(score)


def extract_chapter_index(title: str) -> Optional[int]:
    """Extract chapter number from title"""
    if not title:
        return None
    m = re.search(r"\bchapter\s*(\d{1,2})\b", title, flags=re.IGNORECASE)
    if m:
        try:
            n = int(m.group(1))
            return n if 1 <= n <= 4 else None
        except Exception:
            return None
    if len(title) >= 9 and title[:8].lower() == "chapter " and title[8].isdigit():
        n = int(title[8])
        if 1 <= n <= 4:
            return n
    return None


def normalize_title_for_csv(title: str, ch: int) -> str:
    """Normalize title for CSV output"""
    if not title:
        return f"Chapter {ch}"
    t = re.sub(r"\s+", " ", title).strip()
    return t if t.lower().startswith(f"chapter {ch}") else f"Chapter {ch}: {t}"


def collect_chapter_texts(data_obj: Optional[Dict[str, Any]], use_raw_title: bool = False) -> Tuple[List[str], List[str]]:
    texts = ["", "", "", ""]
    titles: List[Optional[str]] = [None, None, None, None]
    if data_obj is not None:
        # Check for different possible key names - same as build_pages_map_levenshtein
        page_list = data_obj.get("data", []) or data_obj.get("pages", []) or data_obj.get("Pages", [])
        for p in page_list:
            title = p.get("Title", "")
            ch = extract_chapter_index(title)
            if ch is None:
                continue
            parts: List[str] = []
            for item in p.get("Content", []) or []:
                t = item.get("Text")
                if t:
                    parts.append(clean_text(str(t)))
            combined = " ".join(parts).strip()
            if combined:
                i = ch - 1
                texts[i] = (texts[i] + " " + combined).strip()
                if titles[i] is None:
                    titles[i] = title.strip() if use_raw_title else normalize_title_for_csv(title, ch)
    for i in range(4):
        if titles[i] is None:
            titles[i] = f"Chapter {i+1}"
    return texts, [t for t in titles]


def bleurt_preprocess_piece(title: str, text: str, lowercase: bool = False) -> str:
    def strip_html_bs4(s: str) -> str:
        if not FUZZY_AVAILABLE:
            return clean_text(s or "")
        s = html.unescape(s or "")
        return BeautifulSoup(s, "lxml").get_text(separator=" ")
    
    def normalize_ws_punct(s: str) -> str:
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\s*\n\s*", "\n", s)
        s = re.sub(r"\s{2,}", " ", s)
        return s.strip()
    
    t = f"{title}\n\n{text}" if title else (text or "")
    t = strip_html_bs4(t)
    t = normalize_ws_punct(t)
    if lowercase:
        t = t.lower()
    return t


def title_key(s: str) -> str:
    """Normalize title for matching"""
    def normalize_ws_punct(s: str) -> str:
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\s*\n\s*", "\n", s)
        s = re.sub(r"\s{2,}", " ", s)
        return s.strip()
    return normalize_ws_punct(s).lower()


def align_by_title_fuzzy(keys_ref: List[str], keys_other: List[str]) -> Dict[str, str]:
    """Fuzzy title alignment"""
    mapping: Dict[str, str] = {}
    ref_set = set(keys_ref)
    for k in keys_other:
        if k in ref_set:
            mapping[k] = k
        elif FUZZY_AVAILABLE:
            best = process.extractOne(k, list(ref_set), scorer=fuzz.WRatio)
            # Lower threshold to 60 for better matching
            if best and best[1] >= 60:
                mapping[k] = best[0]
    return mapping


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True, help="Original/reference JSON file")
    ap.add_argument("--models", nargs="+", required=True, help="One or more model JSON files to compare")
    ap.add_argument("--out", default="master.csv")
    ap.add_argument("--case-insensitive", action="store_true")
    ap.add_argument("--no-rouge", action="store_true", help="Disable ROUGE computation")
    ap.add_argument("--no-bleu", action="store_true", help="Disable BLEU computation")
    ap.add_argument("--no-bleurt", action="store_true", help="Disable BLEURT computation")
    args = ap.parse_args()

    # Extract source name from original file path
    import os
    source_name = os.path.splitext(os.path.basename(args.original))[0]

    # Load original data
    orig = load_json(args.original)

    # Load all model data and extract names
    models_info = []
    for model_path in args.models:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        model_data = load_json(model_path)
        models_info.append({
            "name": model_name,
            "path": model_path,
            "data": model_data,
            "valid": model_data is not None
        })

    print(f"Source: {source_name}")
    print(f"Models: {[m['name'] for m in models_info]}")

    lowercase = args.case_insensitive

    # Build page maps for original and all models
    orig_pages = build_pages_map_levenshtein(orig, lowercase=lowercase)

    models_pages = []
    for model_info in models_info:
        pages = build_pages_map_levenshtein(model_info["data"], lowercase=lowercase)
        models_pages.append(pages)
        # print(f"{model_info['name']} pages: {list(pages.keys())}")

    # print(f"Original pages: {list(orig_pages.keys())}")

    use_rouge = not args.no_rouge
    use_bleu = not args.no_bleu
    use_bleurt = not args.no_bleurt and BLEURT_AVAILABLE

    # BLEU chapter texts
    ref_texts, ref_titles = collect_chapter_texts(orig, use_raw_title=True)

    models_texts = []
    for model_info in models_info:
        texts, _ = collect_chapter_texts(model_info["data"])
        models_texts.append(texts)

    # print(f"BLEU chapter text lengths:")
    # print(f"  Reference: {[len(t) for t in ref_texts]}")
    # for i, model_info in enumerate(models_info):
        # print(f"  {model_info['name']}: {[len(t) for t in models_texts[i]]}")

    # BLEURT setup
    bleurt_metric = None
    if use_bleurt:
        try:
            bleurt_metric = evaluate.load("bleurt", "bleurt-20")
            print("BLEURT metric loaded successfully!")
        except Exception as e:
            print(f"Failed to load BLEURT metric: {e}")
            use_bleurt = False

    orders_sorted = sorted(orig_pages.keys())

    # Collect all scores in a nested structure: {order: {metric: {model_name: score}}}
    all_scores: Dict[int, Dict[str, Any]] = {}

    for order in orders_sorted:
        title, ref = orig_pages.get(order, ("", ""))

        all_scores[order] = {"title": title}

        # Initialize metric dictionaries for all models
        all_scores[order]["levenshtein"] = {}
        if use_rouge:
            all_scores[order]["rouge"] = {}
        if use_bleu:
            all_scores[order]["bleu"] = {}
        all_scores[order]["bleurt"] = {}

        # Compute scores for each model
        for model_idx, model_info in enumerate(models_info):
            model_name = model_info["name"]
            model_valid = model_info["valid"]
            model_pages = models_pages[model_idx]
            model_texts = models_texts[model_idx]

            _t_model, hyp_model = model_pages.get(order, (title, ""))

            # Levenshtein
            lev = levenshtein_distance(ref, hyp_model) if model_valid else None
            all_scores[order]["levenshtein"][model_name] = lev

            # ROUGE
            if use_rouge:
                rouge = rouge_l_f_score(ref, hyp_model or "") if model_valid else None
                all_scores[order]["rouge"][model_name] = rouge

            # BLEU
            if use_bleu:
                ch_idx = extract_chapter_index(title)
                use_chapter_level = ch_idx is not None and 1 <= ch_idx <= 4

                if use_chapter_level:
                    i = ch_idx - 1
                    if model_valid and len(model_texts[i]) > 0:
                        bleu = bleu_sentence(ref_texts[i], model_texts[i])
                    elif model_valid:
                        bleu = bleu_sentence(ref, hyp_model)
                    else:
                        bleu = None
                else:
                    # Page-level comparison
                    bleu = bleu_sentence(ref, hyp_model) if model_valid else None

                all_scores[order]["bleu"][model_name] = bleu

            # BLEURT (will be filled in later)
            all_scores[order]["bleurt"][model_name] = None

    # Determine which metrics to include
    metrics = ["levenshtein"]
    if use_rouge:
        metrics.append("rouge")
    if use_bleu:
        metrics.append("bleu")
    metrics.append("bleurt")

    fieldnames = ["Reference JSON", "Content", "Model"] + metrics

    # Load existing CSV if it exists for append/update mode
    import pandas as pd
    existing_df = None
    if os.path.exists(args.out):
        try:
            existing_df = pd.read_csv(args.out)
            # print(f"Loaded existing CSV with {len(existing_df)} rows")
        except Exception as e:
            # print(f"Could not load existing CSV: {e}")
            existing_df = None

    # Collect new rows to add/update
    new_rows = []
    for order in orders_sorted:
        title = all_scores[order]["title"]

        # Write row for each model
        for model_info in models_info:
            model_name = model_info["name"]
            row = {"Reference JSON": source_name, "Content": title, "Model": model_name}
            for metric in metrics:
                if metric in all_scores[order]:
                    row[metric] = all_scores[order][metric].get(model_name)
                else:
                    row[metric] = None
            new_rows.append(row)

    # Create new dataframe from new rows
    new_df = pd.DataFrame(new_rows, columns=fieldnames)

    # Merge with existing data if present
    if existing_df is not None:
        # Remove duplicates based on (Reference JSON, Content, Model) tuple - keep old data for non-matching rows
        # First, identify rows in existing_df that should be replaced
        mask = existing_df.apply(
            lambda row: any(
                row['Reference JSON'] == new_row['Reference JSON'] and
                row['Content'] == new_row['Content'] and
                row['Model'] == new_row['Model']
                for new_row in new_rows
            ),
            axis=1
        )
        # Keep rows that don't match any new rows
        kept_df = existing_df[~mask]
        # Combine kept rows with new rows
        final_df = pd.concat([kept_df, new_df], ignore_index=True)
        # print(f"Updated {mask.sum()} existing rows, kept {len(kept_df)} unchanged rows, added {len(new_df)} new/updated rows")
    else:
        final_df = new_df
        # print(f"Created new CSV with {len(final_df)} rows")

    # Write to CSV
    final_df.to_csv(args.out, index=False)

    if use_bleurt and bleurt_metric is not None:
        print("Computing BLEURT scores...")

        def extract_pages(struct):
            pages = None
            if isinstance(struct, dict):
                if "data" in struct and isinstance(struct["data"], list):
                    pages = struct["data"]
                elif "pages" in struct and isinstance(struct["pages"], list):
                    pages = struct["pages"]
                elif "Pages" in struct and isinstance(struct["Pages"], list):
                    pages = struct["Pages"]
            if pages is None and isinstance(struct, list):
                pages = struct
            if pages is None:
                raise ValueError("Unrecognized JSON shape. Expected list or dict with 'data' or 'pages'.")

            out = []
            for idx, p in enumerate(pages):
                if not isinstance(p, dict):
                    continue
                title = p.get("Title") or p.get("title") or p.get("name") or ""
                text = p.get("Text") or p.get("text") or ""
                if not text:
                    content = p.get("Content") or p.get("content") or []
                    if isinstance(content, list):
                        parts = []
                        for it in content:
                            if isinstance(it, dict):
                                t = it.get("Text") or it.get("text") or ""
                                if t:
                                    parts.append(t if isinstance(t, str) else str(t))
                        text = " ".join(parts)
                out.append({"Title": title, "Text": text, "Order": p.get("Order", idx)})
            return out

        def to_page_map(struct):
            result = {}
            if struct is None:
                return result
            for rec in extract_pages(struct):
                pre = bleurt_preprocess_piece(rec["Title"], rec["Text"], lowercase=False)
                key = title_key(rec["Title"])
                result[key] = {"Title": rec["Title"], "Text": pre, "Order": rec["Order"]}
            return result

        def align_by_title_fuzzy_local(keys_ref, keys_other):
            mapping = {}
            ref_set = set(keys_ref)
            for k in keys_other:
                if k in ref_set:
                    mapping[k] = k
                elif FUZZY_AVAILABLE:
                    best = process.extractOne(k, list(ref_set), scorer=fuzz.WRatio)
                    # print(f"    Fuzzy match: '{k}' -> '{best[0]}' (score: {best[1]})")
                    # Lower threshold to 60 for better matching
                    if best and best[1] >= 60:
                        mapping[k] = best[0]
            return mapping

        m_orig = to_page_map(orig)

        # Build page maps for all models
        models_page_maps = []
        for model_info in models_info:
            m_model = to_page_map(model_info["data"])
            models_page_maps.append(m_model)
            # print(f"  {model_info['name']} page keys: {list(m_model.keys())}")

        # print(f"  Original page keys: {list(m_orig.keys())}")

        keys_orig = list(m_orig.keys())

        # Build mappings for all models
        models_mappings = []
        for i, model_info in enumerate(models_info):
            mapping = align_by_title_fuzzy_local(keys_orig, list(models_page_maps[i].keys()))
            models_mappings.append(mapping)
            # print(f"  {model_info['name']} to Original mapping: {mapping}")

        # Compute BLEURT for each page and each model
        for okey, o in m_orig.items():
            order = o["Order"]
            orig_text = o["Text"]

            # Process each model
            for model_idx, model_info in enumerate(models_info):
                model_name = model_info["name"]
                model_valid = model_info["valid"]
                model_page_map = models_page_maps[model_idx]
                model_mapping = models_mappings[model_idx]

                model_text = None
                model_keys_for_this = [k for k, v in model_mapping.items() if v == okey]
                if model_keys_for_this:
                    model_text = model_page_map[model_keys_for_this[0]]["Text"]

                # print(f"  Order {order}: orig_key='{okey}', {model_name}_keys={model_keys_for_this}")

                # Compute BLEURT score - only if source data is valid
                model_score = None
                if model_valid and model_text:
                    try:
                        res = bleurt_metric.compute(predictions=[model_text], references=[orig_text])
                        model_score = res["scores"][0]
                    except Exception:
                        pass

                # Update the all_scores dictionary
                all_scores[order]["bleurt"][model_name] = model_score

        print(f"  Computed BLEURT for {len(all_scores)} pages across {len(models_info)} models")

        # Rewrite the CSV with updated BLEURT scores
        df = pd.read_csv(args.out)
        print(f"  CSV has {len(df)} rows")

        # Update BLEURT column in the dataframe
        for idx, row in df.iterrows():
            ref_json = row['Reference JSON']
            content = row['Content']
            model = row['Model']

            # Only update rows that match current source
            if ref_json == source_name:
                # Find the order for this content
                for order in orders_sorted:
                    if all_scores[order]["title"] == content:
                        if model in all_scores[order]["bleurt"]:
                            df.at[idx, 'bleurt'] = all_scores[order]["bleurt"][model]
                        break

        df.to_csv(args.out, index=False)
        print(f"  Updated CSV with BLEURT scores")

    print(f"Wrote aggregated scores → {args.out}")


if __name__ == "__main__":
    main()