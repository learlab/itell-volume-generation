"""
complexity.py
-------------
Syntactic and lexical complexity indices.

Covers:
  - Surface measures (mean sentence length, mean word length)
  - Lexical diversity: Type-Token Ratio (TTR) and MTLD
  - Syntactic depth: mean dependency distance via spaCy

Key references
--------------
Lexical diversity (MTLD):
  McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation
  study of sophisticated approaches to lexical diversity assessment. Behaviour
  Research Methods, 42(2), 381-392.

  Kyle, K., & Crossley, S. A. (2015). Automatically assessing lexical
  sophistication: Indices, tools, findings, and application. TESOL Quarterly,
  49(4), 757-786.

Syntactic complexity (dependency distance):
  Liu, H. (2008). Dependency distance as a metric of language comprehension
  difficulty. Journal of Cognitive Science, 9(2), 159-191.

  Kyle, K. (2016). Measuring syntactic development in L2 writing: Fine grained
  indices of syntactic complexity and usage-based indices of syntactic
  sophistication. Doctoral dissertation, Georgia State University.

  Lu, X. (2010). Automatic analysis of syntactic complexity in second language
  writing. International Journal of Corpus Linguistics, 15(4), 474-496.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Optional

# spaCy is optional; features degrade gracefully if unavailable
try:
    import spacy
    _nlp: Optional[spacy.language.Language] = None
    _HAS_SPACY = True
except ImportError:
    _HAS_SPACY = False
    _nlp = None


def _get_nlp():
    """Lazy-load spaCy model (en_core_web_sm)."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
        except OSError:
            raise OSError(
                "spaCy model 'en_core_web_sm' not found. "
                "Install with: python -m spacy download en_core_web_sm"
            )
    return _nlp


# ---------------------------------------------------------------------------
# Surface measures
# ---------------------------------------------------------------------------

def _tokenize_sentences(text: str) -> List[str]:
    """Rough sentence splitter that does not require spaCy."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s.strip()]


def _tokenize_words(text: str) -> List[str]:
    """Lowercase alphabetic tokens only (strips punctuation)."""
    return re.findall(r"[a-zA-Z]+", text.lower())


def mean_sentence_length(text: str) -> float:
    """Average number of words per sentence."""
    sentences = _tokenize_sentences(text)
    if not sentences:
        return float("nan")
    lengths = [len(_tokenize_words(s)) for s in sentences]
    return sum(lengths) / len(lengths)


def mean_word_length(text: str) -> float:
    """Average number of characters per word (alphabetic tokens)."""
    words = _tokenize_words(text)
    if not words:
        return float("nan")
    return sum(len(w) for w in words) / len(words)


def sentence_count(text: str) -> int:
    return len(_tokenize_sentences(text))


def word_count(text: str) -> int:
    return len(_tokenize_words(text))


# ---------------------------------------------------------------------------
# Type-Token Ratio (TTR)  — naive baseline; use MTLD for variable-length texts
# ---------------------------------------------------------------------------

def ttr(text: str) -> float:
    """
    Simple Type-Token Ratio.
    NOTE: TTR is sensitive to text length. Prefer MTLD for texts of unequal length.
    Retained here as a baseline / sanity check.
    """
    tokens = _tokenize_words(text)
    if not tokens:
        return float("nan")
    return len(set(tokens)) / len(tokens)


# ---------------------------------------------------------------------------
# MTLD — Measure of Textual Lexical Diversity
# (McCarthy & Jarvis, 2010)
# ---------------------------------------------------------------------------

_MTLD_THRESHOLD = 0.720  # standard threshold from McCarthy & Jarvis (2010)
_MTLD_MIN_TOKENS = 50    # texts shorter than this return NaN


def _mtld_one_pass(tokens: List[str], threshold: float) -> float:
    """
    Single-direction MTLD pass.
    Counts how many 'factors' of threshold-length sequences exist.
    Returns the mean factor size (== MTLD for this direction).
    """
    if not tokens:
        return float("nan")

    types_seen: set = set()
    token_count = 0
    factors = 0.0

    for token in tokens:
        types_seen.add(token)
        token_count += 1
        current_ttr = len(types_seen) / token_count

        if current_ttr <= threshold:
            factors += 1.0
            types_seen = set()
            token_count = 0

    # partial factor for the remaining window
    if token_count > 0:
        current_ttr = len(types_seen) / token_count
        if current_ttr < 1.0:
            partial = (1.0 - current_ttr) / (1.0 - threshold)
        else:
            partial = 0.0
        factors += partial

    if factors == 0:
        return float("nan")

    return len(tokens) / factors


def mtld(text: str, threshold: float = _MTLD_THRESHOLD) -> float:
    """
    Measure of Textual Lexical Diversity (MTLD).

    Averages forward and backward passes, making it direction-independent.
    Returns NaN for texts shorter than _MTLD_MIN_TOKENS.

    McCarthy, P. M., & Jarvis, S. (2010). Behaviour Research Methods, 42(2).
    """
    tokens = _tokenize_words(text)
    if len(tokens) < _MTLD_MIN_TOKENS:
        return float("nan")

    forward = _mtld_one_pass(tokens, threshold)
    backward = _mtld_one_pass(list(reversed(tokens)), threshold)

    if math.isnan(forward) and math.isnan(backward):
        return float("nan")
    if math.isnan(forward):
        return backward
    if math.isnan(backward):
        return forward
    return (forward + backward) / 2.0


# ---------------------------------------------------------------------------
# Dependency distance (spaCy required)
# ---------------------------------------------------------------------------

def mean_dependency_distance(text: str) -> float:
    """
    Mean Dependency Distance (MDD) across all tokens in *text*.

    MDD = mean |position(token) - position(head)| for all non-root tokens.
    Higher values indicate more complex, long-range syntactic relationships.

    Liu, H. (2008). Journal of Cognitive Science, 9(2), 159-191.

    Requires spaCy model 'en_core_web_sm' (or better).
    Returns NaN if spaCy is unavailable.
    """
    if not _HAS_SPACY:
        return float("nan")

    nlp = _get_nlp()
    doc = nlp(text[:100_000])  # guard against extremely long inputs

    distances = []
    for token in doc:
        if token.dep_ != "ROOT":
            distances.append(abs(token.i - token.head.i))

    return sum(distances) / len(distances) if distances else float("nan")


def max_dependency_depth(text: str) -> float:
    """
    Mean of the maximum dependency tree depth across sentences.
    Captures deepest nesting; complements MDD.
    Requires spaCy.
    """
    if not _HAS_SPACY:
        return float("nan")

    nlp = _get_nlp()
    doc = nlp(text[:100_000])

    def _depth(token, memo={}):
        if token in memo:
            return memo[token]
        if list(token.children):
            d = 1 + max(_depth(c, memo) for c in token.children)
        else:
            d = 0
        memo[token] = d
        return d

    depths = []
    for sent in doc.sents:
        roots = [t for t in sent if t.dep_ == "ROOT"]
        if roots:
            depths.append(_depth(roots[0], {}))

    return sum(depths) / len(depths) if depths else float("nan")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def complexity_indices(text: str) -> Dict[str, float]:
    """
    Compute all complexity indices for *text* and return as a flat dict.

    Keys:
      word_count               – total word count
      sentence_count           – total sentence count
      mean_sentence_length     – avg words per sentence
      mean_word_length         – avg characters per word
      ttr                      – type-token ratio (length-sensitive, use cautiously)
      mtld                     – measure of textual lexical diversity (McCarthy & Jarvis 2010)
      mean_dependency_distance – mean |head - dependent| distance (Liu 2008) [spaCy]
      max_dependency_depth     – mean max tree depth per sentence [spaCy]
    """
    return {
        "word_count":               float(word_count(text)),
        "sentence_count":           float(sentence_count(text)),
        "mean_sentence_length":     mean_sentence_length(text),
        "mean_word_length":         mean_word_length(text),
        "ttr":                      ttr(text),
        "mtld":                     mtld(text),
        "mean_dependency_distance": mean_dependency_distance(text),
        "max_dependency_depth":     max_dependency_depth(text),
    }
