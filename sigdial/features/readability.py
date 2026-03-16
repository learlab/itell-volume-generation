"""
readability.py
--------------
Readability / comprehension indices for a text string.

Wraps the `textstat` library, which implements the standard formulae.
All indices are defined at chunk or page level; call with chunk_text
for fine-grained analysis or page_text for broader estimates.

Key references
--------------
- Flesch (1948). A new readability yardstick. Journal of Applied Psychology.
- Kincaid et al. (1975). Derivation of New Readability Formulas for Navy
  Enlisted Personnel. Research Branch Report 8-75. Navy.
- Dale & Chall (1948). A formula for predicting readability. Educational
  Research Bulletin.
- McLaughlin (1969). SMOG Grading — A New Readability Formula. Journal of
  Reading.
- Coleman & Liau (1975). A computer readability formula designed with machine
  readability in mind. Journal of Applied Psychology.
- Gunning (1952). The Technique of Clear Writing. McGraw-Hill.
- Crossley, Skalicky & Dascalu (2019). Moving beyond classic readability
  formulas: New methods and new models. Journal of Research in Reading, 42(3-4).
"""

from __future__ import annotations

from typing import Dict

try:
    import textstat
    _HAS_TEXTSTAT = True
except ImportError:
    _HAS_TEXTSTAT = False


def readability_indices(text: str) -> Dict[str, float]:
    """
    Compute a battery of readability indices for *text*.

    Returns a dict with keys:

      flesch_reading_ease     – 0-100, higher = easier (Flesch 1948)
      flesch_kincaid_grade    – US grade level (Kincaid et al. 1975)
      dale_chall              – grade equivalent (Dale & Chall 1948)
      smog_index              – grade level, robust for short texts (McLaughlin 1969)
      coleman_liau_index      – grade level from character counts (Coleman & Liau 1975)
      gunning_fog             – grade level penalising complex words (Gunning 1952)
      automated_readability   – ARI, character/word/sentence counts
      linsear_write           – designed for technical manuals

    If *text* is too short for a formula (e.g. < 30 words), the value is NaN.
    Requires: pip install textstat
    """
    import math

    nan = float("nan")

    if not _HAS_TEXTSTAT:
        raise ImportError(
            "textstat is required for readability features. "
            "Install with: pip install textstat"
        )

    if not text or len(text.split()) < 5:
        return {k: nan for k in [
            "flesch_reading_ease", "flesch_kincaid_grade", "dale_chall",
            "smog_index", "coleman_liau_index", "gunning_fog",
            "automated_readability", "linsear_write",
        ]}

    def _safe(fn):
        try:
            val = fn()
            return float(val) if val is not None else nan
        except Exception:
            return nan

    return {
        "flesch_reading_ease":  _safe(lambda: textstat.flesch_reading_ease(text)),
        "flesch_kincaid_grade": _safe(lambda: textstat.flesch_kincaid_grade(text)),
        "dale_chall":           _safe(lambda: textstat.dale_chall_readability_score(text)),
        "smog_index":           _safe(lambda: textstat.smog_index(text)),
        "coleman_liau_index":   _safe(lambda: textstat.coleman_liau_index(text)),
        "gunning_fog":          _safe(lambda: textstat.gunning_fog(text)),
        "automated_readability":_safe(lambda: textstat.automated_readability_index(text)),
        "linsear_write":        _safe(lambda: textstat.linsear_write_formula(text)),
    }
