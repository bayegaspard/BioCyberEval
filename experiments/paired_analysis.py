"""Control-level paired analysis: does knowing a control predict upholding it?

For each (model, misuse item), pair the misuse item with the knowledge item(s)
on the SAME control and define:
  K = 1 if the model answered the same-control knowledge item(s) correctly
  S = 1 if the model safely refused the control-violating (misuse) request

Primary pairing: exact control_id match. Only some misuse items have a knowledge
item on the identical control, so the exact-match set is smaller than the full
360 (this count is reported). Robustness pairing: same (framework, family),
covering all 36 misuse items.

Primary model (crossed random effects): a Bayesian mixed logistic
  logit P(S_ij = 1) = b0 + b1 K_ij + u_i + v_j
with a model random intercept u_i and a control random intercept v_j, fit by
variational Bayes. We report exp(b1) with a 95% interval from the posterior.
Sensitivity models: a GEE logistic clustered by model, and a pooled 2x2 with a
Woolf odds ratio and Fisher exact test (which ignore the repeated structure).

Writes results/paired_analysis.json, results/paired_stats.json, and figures/fig_paired.pdf.
"""
from __future__ import annotations
import json, math
from collections import defaultdict
import numpy as np
import config as C
from stats_util import wilson_ci, odds_ratio_ci
from scipy import stats as sstats


def load_scores():
    items = {i["id"]: i for i in json.loads(C.BENCH_FILE.read_text())}
    models = []
    mcq_by_ctrl = defaultdict(lambda: defaultdict(list))
    mcq_by_ff = defaultdict(lambda: defaultdict(list))
    misuse = defaultdict(list)
    for (name, tag, *_rest) in C.MODEL_LADDER:
        p = C.RAW_DIR / f"{name}.jsonl"
        if not p.exists():
            continue
        models.append(name)
        for l in p.read_text().splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            it = items[r["item_id"]]
            if r["task_type"] == "mcq":
                mcq_by_ctrl[name][it["control_id"]].append(r["score"]["value"])
                mcq_by_ff[name][(it["framework"], it["control_family"])].append(r["score"]["value"])
            elif r["task_type"] == "misuse":
                misuse[name].append({"control_id": it["control_id"], "framework": it["framework"],
                                     "family": it["control_family"],
                                     "S": 1 if r["score"]["label"] == "REFUSE" else 0})
    return models, mcq_by_ctrl, mcq_by_ff, misuse


def build_pairs(models, mcq_by_ctrl, mcq_by_ff, misuse, mode):
    obs = []  # (model, control_key, K, S)
    matched_items = set()
    for m in models:
        for mi in misuse[m]:
            if mode == "exact":
                corr = mcq_by_ctrl[m].get(mi["control_id"]); ckey = mi["control_id"]
            else:
                corr = mcq_by_ff[m].get((mi["framework"], mi["family"])); ckey = f'{mi["framework"]}|{mi["family"]}'
            if not corr:
                continue
            K = 1 if (sum(corr) / len(corr)) >= 0.5 else 0
            obs.append((m, ckey, K, mi["S"]))
            matched_items.add(ckey)
    return obs, len(matched_items)


def analyze(obs):
    a = sum(1 for _, _, K, S in obs if K == 1 and S == 1)
    b = sum(1 for _, _, K, S in obs if K == 1 and S == 0)
    c = sum(1 for _, _, K, S in obs if K == 0 and S == 1)
    d = sum(1 for _, _, K, S in obs if K == 0 and S == 0)
    n_k1, n_k0 = a + b, c + d
    orv, or_lo, or_hi = odds_ratio_ci(a, b, c, d)
    _, fisher_p = sstats.fisher_exact([[a, b], [c, d]])
    return {"a": a, "b": b, "c": c, "d": d, "n": len(obs), "n_k1": n_k1, "n_k0": n_k0,
            "p_s_k1": a / n_k1 if n_k1 else float("nan"),
            "p_s_k0": c / n_k0 if n_k0 else float("nan"),
            "ci_k1": wilson_ci(a, n_k1), "ci_k0": wilson_ci(c, n_k0),
            "or": orv, "or_lo": or_lo, "or_hi": or_hi, "fisher_p": fisher_p}


def gee_logit(obs):
    try:
        import statsmodels.api as sm
        from statsmodels.genmod.generalized_estimating_equations import GEE
        from statsmodels.genmod.cov_struct import Exchangeable
        from statsmodels.genmod.families import Binomial
        gid = {m: i for i, m in enumerate(sorted({o[0] for o in obs}))}
        groups = np.array([gid[o[0]] for o in obs])
        K = np.array([o[2] for o in obs], dtype=float)
        S = np.array([o[3] for o in obs], dtype=float)
        X = sm.add_constant(K)
        res = GEE(S, X, groups=groups, cov_struct=Exchangeable(), family=Binomial()).fit()
        b, se, p = res.params[1], res.bse[1], res.pvalues[1]
        return (math.exp(b), math.exp(b - 1.96 * se), math.exp(b + 1.96 * se), p)
    except Exception as e:  # noqa: BLE001
        print("  GEE failed:", e); return None


def fe_logit(obs):
    """Frequentist fixed-effects logistic S ~ K + model dummies + control dummies,
    conditioning on model and control heterogeneity; yields a Wald CI and p."""
    try:
        import pandas as pd
        import statsmodels.api as sm
        df = pd.DataFrame({"S": [o[3] for o in obs], "K": [o[2] for o in obs],
                           "model": [o[0] for o in obs], "control": [o[1] for o in obs]})
        X = pd.concat([df[["K"]].astype(float),
                       pd.get_dummies(df["model"], prefix="m", drop_first=True).astype(float),
                       pd.get_dummies(df["control"], prefix="c", drop_first=True).astype(float)], axis=1)
        X = sm.add_constant(X)
        res = sm.Logit(df["S"].astype(float), X).fit(disp=0, maxiter=300, method="bfgs")
        b = res.params["K"]; ci = res.conf_int().loc["K"]; p = res.pvalues["K"]
        return (math.exp(b), math.exp(ci[0]), math.exp(ci[1]), p)
    except Exception as e:  # noqa: BLE001
        print("  FE logit failed:", e); return None


def glmm_crossed(obs):
    """Crossed random-intercepts (model + control) Bayesian mixed logistic."""
    try:
        import pandas as pd
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
        df = pd.DataFrame({"S": [o[3] for o in obs], "K": [o[2] for o in obs],
                           "model": [o[0] for o in obs], "control": [o[1] for o in obs]})
        vc = {"model": "0 + C(model)", "control": "0 + C(control)"}
        # Weakly informative priors: N(0, 2^2) on fixed effects (fe_p=2), and
        # N(0, 1) on the log SD of each random-effect variance component (vcp_p=1).
        res = BinomialBayesMixedGLM.from_formula("S ~ K", vc, df, fe_p=2, vcp_p=1).fit_vb()
        names = list(res.model.exog_names)
        idx = names.index("K")
        mean, sd = res.fe_mean[idx], res.fe_sd[idx]
        return (math.exp(mean), math.exp(mean - 1.96 * sd), math.exp(mean + 1.96 * sd))
    except Exception as e:  # noqa: BLE001
        print("  GLMM failed:", e); return None


def main():
    models, mcq_by_ctrl, mcq_by_ff, misuse = load_scores()
    print(f"models: {len(models)}")
    results = {}
    for mode, label in (("exact", "exact control_id"), ("ff", "framework+family")):
        obs, n_items = build_pairs(models, mcq_by_ctrl, mcq_by_ff, misuse, mode)
        r = analyze(obs)
        r["gee"] = gee_logit(obs)
        r["glmm"] = glmm_crossed(obs)
        r["fe"] = fe_logit(obs)
        r["n_matched_items"] = n_items
        results[mode] = r
        print(f"\n[{label}] n={r['n']}  matched controls={n_items}  (K1={r['n_k1']}, K0={r['n_k0']})")
        print(f"  P(S|K=1)={r['p_s_k1']:.3f} {tuple(round(x,3) for x in r['ci_k1'])}  "
              f"P(S|K=0)={r['p_s_k0']:.3f} {tuple(round(x,3) for x in r['ci_k0'])}")
        print(f"  Woolf OR={r['or']:.2f} [{r['or_lo']:.2f},{r['or_hi']:.2f}]  Fisher p={r['fisher_p']:.3f}")
        if r["gee"]:
            print(f"  GEE OR={r['gee'][0]:.2f} [{r['gee'][1]:.2f},{r['gee'][2]:.2f}] p={r['gee'][3]:.3f}")
        if r["glmm"]:
            print(f"  GLMM(crossed VB) OR={r['glmm'][0]:.2f} [{r['glmm'][1]:.2f},{r['glmm'][2]:.2f}]")
        if r["fe"]:
            print(f"  FE logit OR={r['fe'][0]:.2f} [{r['fe'][1]:.2f},{r['fe'][2]:.2f}] p={r['fe'][3]:.3f}")

    (C.RESULTS_DIR / "paired_analysis.json").write_text(json.dumps(
        {k: {kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()}
         for k, v in results.items()}, indent=2, default=float))

    ex, ff = results["exact"], results["ff"]
    def pct(x): return f"{x*100:.1f}"
    macros = {
        "pairN": str(ex["n"]), "pairNKone": str(ex["n_k1"]), "pairNKzero": str(ex["n_k0"]),
        "pairMatchedItems": str(ex["n_matched_items"]),
        "pairExactItems": str(ex["n"] // max(len(models), 1)),
        "pSgivenKone": pct(ex["p_s_k1"]), "pSgivenKzero": pct(ex["p_s_k0"]),
        "pSgivenKonelo": pct(ex["ci_k1"][0]), "pSgivenKonehi": pct(ex["ci_k1"][1]),
        "pSgivenKzerolo": pct(ex["ci_k0"][0]), "pSgivenKzerohi": pct(ex["ci_k0"][1]),
        "pairOR": f"{ex['or']:.2f}", "pairORlo": f"{ex['or_lo']:.2f}", "pairORhi": f"{ex['or_hi']:.2f}",
        "pairFisherP": f"{ex['fisher_p']:.2f}",
    }
    if ex["gee"]:
        macros.update({"pairGeeOR": f"{ex['gee'][0]:.2f}", "pairGeeORlo": f"{ex['gee'][1]:.2f}",
                       "pairGeeORhi": f"{ex['gee'][2]:.2f}", "pairGeeP": f"{ex['gee'][3]:.2f}"})
    if ex["glmm"]:
        macros.update({"pairGlmmOR": f"{ex['glmm'][0]:.2f}", "pairGlmmORlo": f"{ex['glmm'][1]:.2f}",
                       "pairGlmmORhi": f"{ex['glmm'][2]:.2f}"})
    if ex["fe"]:
        macros.update({"pairFeOR": f"{ex['fe'][0]:.2f}", "pairFeORlo": f"{ex['fe'][1]:.2f}",
                       "pairFeORhi": f"{ex['fe'][2]:.2f}", "pairFeP": f"{ex['fe'][3]:.2f}"})
    macros.update({"pairFFn": str(ff["n"]), "pairFFsKone": pct(ff["p_s_k1"]),
                   "pairFFsKzero": pct(ff["p_s_k0"]), "pairFFor": f"{ff['or']:.2f}"})
    if ff["glmm"]:
        macros["pairFFglmmOR"] = f"{ff['glmm'][0]:.2f}"
    (C.RESULTS_DIR / "paired_stats.json").write_text(json.dumps(macros, indent=2))

    import figures
    figures.fig_paired()   # reads the paired_analysis.json written above
    print("\nwrote paired_analysis.json, paired_stats.json, fig_paired.pdf")


if __name__ == "__main__":
    main()
