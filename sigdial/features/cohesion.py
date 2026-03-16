"""
cohesion.py
-----------
Discourse cohesion indices at the chunk/page level.

Three families of features (after Coh-Metrix / TAACO):

  1. Referential cohesion  — lexical overlap between adjacent text units
     (noun overlap, argument overlap, stem overlap)

  2. Connective cohesion   — density of explicit discourse connectives
     categorised by type (additive, causal, adversative, temporal, clarifying)

  3. Semantic cohesion     — sentence-embedding cosine similarity between
     adjacent sentences (requires sentence-transformers)

Key references
--------------
Coh-Metrix / referential overlap:
  Graesser, A. C., McNamara, D. S., Louwerse, M. M., & Cai, Z. (2004).
  Coh-Metrix: Analysis of text on cohesion and language. Behavior Research
  Methods, Instruments, & Computers, 36(2), 193-202.

  McNamara, D. S., Graesser, A. C., McCarthy, P. M., & Cai, Z. (2014).
  Automated Evaluation of Text and Discourse with Coh-Metrix. Cambridge
  University Press.

TAACO / connective lexicon:
  Crossley, S. A., Kyle, K., & McNamara, D. S. (2016). The tool for the
  automatic analysis of text cohesion (TAACO): Automatic assessment of local,
  global, and text cohesion. Behavior Research Methods, 48(4), 1227-1237.

  Crossley, S. A., Skalicky, S., & Dascalu, M. (2019). Moving beyond classic
  readability formulas. Journal of Research in Reading, 42(3-4), 468-485.

Semantic similarity (sentence-transformers):
  Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings
  using siamese BERT-networks. EMNLP 2019.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# spaCy for lemmatisation and POS tagging (referential cohesion)
try:
    import spacy
    _nlp = None
    _HAS_SPACY = True
except ImportError:
    _HAS_SPACY = False
    _nlp = None

# sentence-transformers for semantic cohesion (optional)
try:
    from sentence_transformers import SentenceTransformer
    _st_model: Optional[SentenceTransformer] = None
    _HAS_ST = True
except ImportError:
    _HAS_ST = False
    _st_model = None

# numpy for cosine similarity
try:
    import numpy as np
    _HAS_NP = True
except ImportError:
    _HAS_NP = False


# ---------------------------------------------------------------------------
# Resource loading
# ---------------------------------------------------------------------------

_CONNECTIVES: Optional[Dict[str, List[str]]] = None
_RESOURCES_DIR = Path(__file__).resolve().parents[1] / "resources"


def _load_connectives() -> Dict[str, List[str]]:
    global _CONNECTIVES
    if _CONNECTIVES is None:
        path = _RESOURCES_DIR / "connectives.json"
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        # drop the _source metadata key
        _CONNECTIVES = {k: v for k, v in raw.items() if not k.startswith("_")}
    return _CONNECTIVES


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    return _nlp


def _get_st_model() -> "SentenceTransformer":
    global _st_model
    if _st_model is None:
        # all-MiniLM-L6-v2: fast, 384-dim, strong semantic similarity
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s.strip()]


def _alpha_tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def _noun_tokens(text: str) -> List[str]:
    """Return lemmatised nouns from text using spaCy POS tags."""
    nlp = _get_nlp()
    doc = nlp(text[:50_000])
    return [token.lemma_.lower() for token in doc
            if token.pos_ in {"NOUN", "PROPN"} and token.is_alpha]


def _content_tokens(text: str) -> List[str]:
    """Return lemmatised content words (nouns, verbs, adjectives, adverbs)."""
    nlp = _get_nlp()
    doc = nlp(text[:50_000])
    return [token.lemma_.lower() for token in doc
            if token.pos_ in {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}
            and token.is_alpha and not token.is_stop]


def _stem_tokens(text: str) -> List[str]:
    """Rough stemming via 5-char prefix — no dep on nltk/snowball."""
    return [w[:5] for w in _alpha_tokens(text)]


def _overlap(set_a: set, set_b: set) -> float:
    """Jaccard-style overlap: |intersection| / |union|. Returns 0 if both empty."""
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def _pairwise_mean(
    sentences: List[str],
    token_fn,
) -> float:
    """
    Mean pairwise overlap between adjacent sentence pairs using *token_fn*
    to extract the token set from each sentence.
    """
    if len(sentences) < 2:
        return float("nan")

    scores = []
    for i in range(len(sentences) - 1):
        a = set(token_fn(sentences[i]))
        b = set(token_fn(sentences[i + 1]))
        scores.append(_overlap(a, b))

    return sum(scores) / len(scores)


# ---------------------------------------------------------------------------
# 1. Referential cohesion
# ---------------------------------------------------------------------------

def noun_overlap(text: str) -> float:
    """
    Mean noun overlap between adjacent sentence pairs (local referential cohesion).
    After McNamara et al. (2014) Coh-Metrix.
    Requires spaCy.
    """
    if not _HAS_SPACY:
        return float("nan")
    sentences = _split_sentences(text)
    return _pairwise_mean(sentences, _noun_tokens)


def argument_overlap(text: str) -> float:
    """
    Mean content-word overlap between adjacent sentence pairs.
    'Argument' = noun or pronoun in Coh-Metrix; here broadened to all
    content words (nouns, verbs, adjectives, adverbs) for richer signal.
    Requires spaCy.
    """
    if not _HAS_SPACY:
        return float("nan")
    sentences = _split_sentences(text)
    return _pairwise_mean(sentences, _content_tokens)


def stem_overlap(text: str) -> float:
    """
    Mean stem-level overlap between adjacent sentence pairs.
    Uses 5-char prefix stemming (no external stemmer needed).
    Captures morphological variants missed by exact matching.
    """
    sentences = _split_sentences(text)
    return _pairwise_mean(sentences, _stem_tokens)


# ---------------------------------------------------------------------------
# 2. Connective cohesion (TAACO-style)
# ---------------------------------------------------------------------------

def _count_connectives(text: str, phrase_list: List[str]) -> int:
    """Count non-overlapping occurrences of connective phrases in *text*."""
    text_lower = text.lower()
    count = 0
    for phrase in phrase_list:
        # word-boundary match to avoid partial hits (e.g. 'so' inside 'also')
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        count += len(re.findall(pattern, text_lower))
    return count


def connective_density(text: str) -> Dict[str, float]:
    """
    Density of each connective category per 100 words.

    Returns keys:
      conn_additive, conn_causal, conn_adversative,
      conn_temporal, conn_clarifying, conn_total
    """
    connectives = _load_connectives()
    words = re.findall(r"[a-zA-Z]+", text)
    n_words = len(words) if words else 1

    result = {}
    total = 0
    for cat, phrases in connectives.items():
        count = _count_connectives(text, phrases)
        density = (count / n_words) * 100
        result[f"conn_{cat}"] = density
        total += count

    result["conn_total"] = (total / n_words) * 100
    return result


# ---------------------------------------------------------------------------
# 3. Semantic cohesion (sentence-transformers)
# ---------------------------------------------------------------------------

def _cosine(a: "np.ndarray", b: "np.ndarray") -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def semantic_overlap(text: str) -> float:
    """
    Mean cosine similarity between sentence embeddings for adjacent sentence pairs.

    Uses sentence-transformers 'all-MiniLM-L6-v2' (Reimers & Gurevych, 2019).
    Returns NaN if sentence-transformers or numpy is unavailable.
    """
    if not (_HAS_ST and _HAS_NP):
        return float("nan")

    sentences = _split_sentences(text)
    if len(sentences) < 2:
        return float("nan")

    model = _get_st_model()
    embeddings = model.encode(sentences, show_progress_bar=False)

    scores = [
        _cosine(embeddings[i], embeddings[i + 1])
        for i in range(len(embeddings) - 1)
    ]
    return sum(scores) / len(scores)


def global_semantic_overlap(sentences_a: List[str], sentences_b: List[str]) -> float:
    """
    Mean cosine similarity between *all* sentence pairs across two text units
    (e.g. two pages). Measures global / cross-paragraph cohesion.
    Returns NaN if sentence-transformers unavailable.
    """
    if not (_HAS_ST and _HAS_NP):
        return float("nan")
    if not sentences_a or not sentences_b:
        return float("nan")

    model = _get_st_model()
    emb_a = model.encode(sentences_a, show_progress_bar=False)
    emb_b = model.encode(sentences_b, show_progress_bar=False)

    scores = [
        _cosine(emb_a[i], emb_b[j])
        for i in range(len(emb_a))
        for j in range(len(emb_b))
    ]
    return sum(scores) / len(scores) if scores else float("nan")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cohesion_indices(text: str) -> Dict[str, float]:
    """
    Compute all cohesion indices for *text* and return as a flat dict.

    Referential cohesion (Coh-Metrix / McNamara et al. 2014):
      noun_overlap       – mean adjacent-sentence noun overlap (spaCy)
      argument_overlap   – mean adjacent-sentence content-word overlap (spaCy)
      stem_overlap       – mean adjacent-sentence stem overlap

    Connective cohesion (TAACO / Crossley et al. 2016):
      conn_additive      – additive connective density per 100 words
      conn_causal        – causal connective density
      conn_adversative   – adversative connective density
      conn_temporal      – temporal connective density
      conn_clarifying    – clarifying connective density
      conn_total         – total connective density

    Semantic cohesion (sentence-transformers / Reimers & Gurevych 2019):
      semantic_overlap   – mean adjacent-sentence embedding cosine similarity
    """
    result: Dict[str, float] = {}

    result["noun_overlap"] = noun_overlap(text)
    result["argument_overlap"] = argument_overlap(text)
    result["stem_overlap"] = stem_overlap(text)
    result.update(connective_density(text))
    result["semantic_overlap"] = semantic_overlap(text)

    return result
