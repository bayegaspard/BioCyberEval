"""Shared statistics helpers: Wilson intervals, Fisher correlation intervals,
odds ratios. Kept dependency-light (math + scipy for tail probabilities)."""
from __future__ import annotations
import math
from scipy import stats


def wilson_ci(k: int, n: int, z: float = 1.96):
    """95% Wilson score interval for a binomial proportion (lo, hi)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fmt_ci(k: int, n: int, as_pct: bool = True):
    lo, hi = wilson_ci(k, n)
    if as_pct:
        return f"{lo*100:.1f}", f"{hi*100:.1f}"
    return f"{lo:.3f}", f"{hi:.3f}"


def pearson_ci(r: float, n: int, z: float = 1.96):
    """Fisher z 95% CI for a Pearson correlation, plus two-sided p-value."""
    if n < 4 or abs(r) >= 1:
        return (float("nan"), float("nan"), float("nan"))
    zf = math.atanh(r)
    se = 1 / math.sqrt(n - 3)
    lo = math.tanh(zf - z * se)
    hi = math.tanh(zf + z * se)
    t = r * math.sqrt((n - 2) / (1 - r * r))
    p = 2 * stats.t.sf(abs(t), n - 2)
    return (lo, hi, p)


def spearman(xs, ys):
    rho, p = stats.spearmanr(xs, ys)
    return float(rho), float(p)


def odds_ratio_ci(a: int, b: int, c: int, d: int):
    """OR for a 2x2 table [[a,b],[c,d]] with Haldane-Anscombe 0.5 correction and
    Woolf 95% CI. Returns (or, lo, hi)."""
    a2, b2, c2, d2 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    orv = (a2 * d2) / (b2 * c2)
    se = math.sqrt(1 / a2 + 1 / b2 + 1 / c2 + 1 / d2)
    lo = math.exp(math.log(orv) - 1.96 * se)
    hi = math.exp(math.log(orv) + 1.96 * se)
    return (orv, lo, hi)
