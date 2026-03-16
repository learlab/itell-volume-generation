"""
stats.py
--------
Statistical analysis of the automated feature matrix.

Provides:
  - descriptives(df)            per-mode mean / SD / n for every feature
  - run_anova(df, feature)      one-way ANOVA + Tukey HSD across modes
  - run_mixed_model(df, feat)   linear mixed model (mode fixed, volume random)
  - correlation_matrix(df)      Pearson r between automated indices
  - human_correlation(df, ...)  Pearson/Spearman r of automated vs. human ratings

All functions accept a pandas DataFrame whose columns include at minimum:
  'mode'       – generation mode string
  'volume_id'  – source volume identifier (used as random effect)
  + one column per feature index

Dependencies: pandas, scipy, statsmodels, pingouin (optional, for ICC)
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------

def descriptives(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    group_col: str = "mode",
) -> pd.DataFrame:
    """
    Return mean, SD, and n per group for all numeric feature columns.

    Parameters
    ----------
    df : DataFrame with at least *group_col* and numeric feature columns.
    feature_cols : list of column names to summarise; defaults to all numeric cols
                   except group / id columns.
    group_col : column to group by (default 'mode').

    Returns
    -------
    DataFrame indexed by (group_col, feature) with columns [mean, std, n].
    """
    _id_cols = {"volume_id", "mode", "page_order", "page_title",
                "chunk_index", "chunk_type", "chunk_header",
                "chunk_text", "page_text", "volume_text"}

    if feature_cols is None:
        feature_cols = [
            c for c in df.select_dtypes("number").columns
            if c not in _id_cols
        ]

    records = []
    for mode, grp in df.groupby(group_col):
        for feat in feature_cols:
            col = grp[feat].dropna()
            records.append({
                group_col: mode,
                "feature": feat,
                "mean": col.mean(),
                "std": col.std(),
                "n": len(col),
            })

    return pd.DataFrame(records).set_index([group_col, "feature"])


# ---------------------------------------------------------------------------
# One-way ANOVA + post-hoc Tukey HSD
# ---------------------------------------------------------------------------

def run_anova(
    df: pd.DataFrame,
    feature: str,
    group_col: str = "mode",
) -> Dict:
    """
    One-way ANOVA testing whether *feature* differs across *group_col* levels.

    Returns a dict with:
      F          – F-statistic
      p_anova    – p-value from one-way ANOVA
      eta_sq     – eta-squared effect size
      tukey      – DataFrame of pairwise Tukey HSD comparisons (requires statsmodels)

    References
    ----------
    Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.).
    """
    from scipy import stats as sps

    groups = [
        grp[feature].dropna().values
        for _, grp in df.groupby(group_col)
    ]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 2:
        return {"F": float("nan"), "p_anova": float("nan"),
                "eta_sq": float("nan"), "tukey": None}

    F, p = sps.f_oneway(*groups)

    # eta-squared = SS_between / SS_total
    grand_mean = df[feature].mean()
    ss_between = sum(
        len(g) * (g.mean() - grand_mean) ** 2 for g in groups
    )
    ss_total = sum(((v - grand_mean) ** 2) for g in groups for v in g)
    eta_sq = ss_between / ss_total if ss_total > 0 else float("nan")

    # Tukey HSD via statsmodels (optional)
    tukey_df = None
    try:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        sub = df[[group_col, feature]].dropna()
        result = pairwise_tukeyhsd(sub[feature], sub[group_col], alpha=0.05)
        tukey_df = pd.DataFrame(
            data=result._results_table.data[1:],
            columns=result._results_table.data[0],
        )
    except ImportError:
        pass

    return {"F": F, "p_anova": p, "eta_sq": eta_sq, "tukey": tukey_df}


def anova_table(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    group_col: str = "mode",
) -> pd.DataFrame:
    """
    Run one-way ANOVA for every feature and return a summary table.

    Returns DataFrame with columns [feature, F, p_anova, eta_sq].
    """
    _id_cols = {"volume_id", "mode", "page_order", "page_title",
                "chunk_index", "chunk_type", "chunk_header",
                "chunk_text", "page_text", "volume_text"}

    if feature_cols is None:
        feature_cols = [
            c for c in df.select_dtypes("number").columns
            if c not in _id_cols
        ]

    rows = []
    for feat in feature_cols:
        res = run_anova(df, feat, group_col)
        rows.append({
            "feature": feat,
            "F": res["F"],
            "p_anova": res["p_anova"],
            "eta_sq": res["eta_sq"],
        })

    result = pd.DataFrame(rows)

    # Bonferroni-corrected alpha flag
    alpha_corrected = 0.05 / max(len(rows), 1)
    result["sig_bonferroni"] = result["p_anova"] < alpha_corrected

    return result.set_index("feature").sort_values("p_anova")


# ---------------------------------------------------------------------------
# Linear mixed model (mode fixed, volume random)
# ---------------------------------------------------------------------------

def run_mixed_model(
    df: pd.DataFrame,
    feature: str,
    fixed_col: str = "mode",
    random_col: str = "volume_id",
) -> "statsmodels.regression.mixed_linear_model.MixedLMResults":
    """
    Fit a linear mixed model:  feature ~ mode  (random intercept per volume).

    Accounts for non-independence of chunks from the same source volume.
    Requires statsmodels.

    Returns the fitted MixedLM result object (call .summary() to print).
    """
    try:
        import statsmodels.formula.api as smf
    except ImportError as exc:
        raise ImportError(
            "statsmodels is required for mixed models. "
            "Install with: pip install statsmodels"
        ) from exc

    sub = df[[feature, fixed_col, random_col]].dropna()
    formula = f"{feature} ~ C({fixed_col})"
    model = smf.mixedlm(formula, sub, groups=sub[random_col])
    return model.fit(reml=True, method="lbfgs")


# ---------------------------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------------------------

def correlation_matrix(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Pairwise correlation between all automated feature indices.

    Parameters
    ----------
    method : 'pearson' or 'spearman'

    Returns
    -------
    Square DataFrame of correlation coefficients.
    """
    _id_cols = {"volume_id", "mode", "page_order", "page_title",
                "chunk_index", "chunk_type", "chunk_header",
                "chunk_text", "page_text", "volume_text"}

    if feature_cols is None:
        feature_cols = [
            c for c in df.select_dtypes("number").columns
            if c not in _id_cols
        ]

    return df[feature_cols].corr(method=method)


def human_correlation(
    df: pd.DataFrame,
    automated_cols: List[str],
    human_cols: List[str],
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Pearson or Spearman correlation between automated feature indices and
    human rating dimensions.

    Parameters
    ----------
    automated_cols : list of automated index column names
    human_cols     : list of human rating column names
                     (e.g. ['h_cohesion', 'h_comprehensibility', 'h_complexity'])
    method         : 'pearson' or 'spearman'

    Returns
    -------
    DataFrame of shape (len(automated_cols), len(human_cols)) with r values.
    Significant correlations (p < .05) are noted via a companion p-value table
    printed to stdout.
    """
    from scipy import stats as sps

    rows = []
    for a_col in automated_cols:
        row = {}
        for h_col in human_cols:
            sub = df[[a_col, h_col]].dropna()
            if len(sub) < 3:
                row[h_col] = float("nan")
                continue
            if method == "spearman":
                r, p = sps.spearmanr(sub[a_col], sub[h_col])
            else:
                r, p = sps.pearsonr(sub[a_col], sub[h_col])
            row[h_col] = r
            # flag significance
            if p < 0.05:
                row[f"{h_col}_sig"] = "*" if p < 0.05 else ""
                if p < 0.01:
                    row[f"{h_col}_sig"] = "**"
                if p < 0.001:
                    row[f"{h_col}_sig"] = "***"
            else:
                row[f"{h_col}_sig"] = ""
        rows.append({"feature": a_col, **row})

    return pd.DataFrame(rows).set_index("feature")


# ---------------------------------------------------------------------------
# Inter-rater reliability
# ---------------------------------------------------------------------------

def interrater_reliability(
    ratings: pd.DataFrame,
    rater_cols: List[str],
    method: str = "krippendorff",
) -> float:
    """
    Compute inter-rater reliability across *rater_cols*.

    Parameters
    ----------
    ratings    : DataFrame where each row is an item and each column a rater.
    rater_cols : columns containing rater scores.
    method     : 'krippendorff' (requires krippendorff package) or
                 'icc' (requires pingouin).

    Returns
    -------
    Alpha (Krippendorff) or ICC2 value.

    References
    ----------
    Krippendorff, K. (2011). Computing Krippendorff's Alpha-Reliability.
    Gwet, K. L. (2014). Handbook of Inter-Rater Reliability (4th ed.).
    """
    data = ratings[rater_cols].values

    if method == "krippendorff":
        try:
            import krippendorff
            return krippendorff.alpha(reliability_data=data.T)
        except ImportError as exc:
            raise ImportError(
                "krippendorff package required. Install: pip install krippendorff"
            ) from exc

    if method == "icc":
        try:
            import pingouin as pg
        except ImportError as exc:
            raise ImportError(
                "pingouin required for ICC. Install: pip install pingouin"
            ) from exc

        long = (
            ratings[rater_cols]
            .reset_index()
            .melt(id_vars="index", var_name="rater", value_name="score")
            .rename(columns={"index": "item"})
        )
        icc_result = pg.intraclass_corr(
            data=long, targets="item", raters="rater", ratings="score"
        )
        return float(icc_result.set_index("Type").loc["ICC2", "ICC"])

    raise ValueError(f"Unknown method '{method}'. Use 'krippendorff' or 'icc'.")
