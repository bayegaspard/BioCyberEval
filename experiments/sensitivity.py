"""Sensitivity analyses requested in review round 2.

1. Judge-label sensitivity: recompute the headline guardrail finding using the
   independent judge's labels instead of the rule-based scorer, excluding
   GPT-OSS-20B's self-judged responses (the judge is GPT-OSS-20B). Reports the
   judge-based mean refusal rate over the other nine models and re-runs the
   exact-control paired analysis (crossed model+control random effects) with S
   defined by the judge, to check that "knowledge does not predict upholding"
   is not an artifact of the rule-based scorer.

2. Per-model benign correctness (Table IV): correct help / incorrect help /
   over-refusal per model from the judge's benign labels, with Wilson intervals
   on the correct-help rate.

Writes results/sensitivity_stats.json and results/benign_correctness.csv.
"""
from __future__ import annotations
import json, math
from collections import defaultdict
import config as C
from stats_util import wilson_ci
from scoring import effective_benign_label

JUDGMENTS = C.RESULTS_DIR / "validation_judgments.jsonl"
JUDGE_MODEL = "GPT-OSS-20B"


def load():
    items = {i["id"]: i for i in json.loads(C.BENCH_FILE.read_text())}
    # judge labels
    jmis = defaultdict(dict)   # model -> item_id -> judge label (misuse)
    jben = defaultdict(dict)   # model -> item_id -> judge label (benign)
    for l in JUDGMENTS.read_text().splitlines():
        if not l.strip():
            continue
        d = json.loads(l)
        (jmis if d["task_type"] == "misuse" else jben)[d["model"]][d["item_id"]] = d["judge_label"]
    # knowledge correctness by control per model (for paired sensitivity)
    mcq_by_ctrl = defaultdict(lambda: defaultdict(list))
    misuse_ctrl = {}   # item_id -> control_id
    for (name, tag, *_r) in C.MODEL_LADDER:
        p = C.RAW_DIR / f"{name}.jsonl"
        if not p.exists():
            continue
        for l in p.read_text().splitlines():
            if not l.strip():
                continue
            r = json.loads(l); it = items[r["item_id"]]
            if r["task_type"] == "mcq":
                mcq_by_ctrl[name][it["control_id"]].append(r["score"]["value"])
            elif r["task_type"] == "misuse":
                misuse_ctrl[r["item_id"]] = it["control_id"]
            elif r["task_type"] == "benign" and r["item_id"] in jben[name]:
                jben[name][r["item_id"]] = effective_benign_label(jben[name][r["item_id"]],
                                                                  r["response"])
    models = [n for (n, *_r) in C.MODEL_LADDER if (C.RAW_DIR / f"{n}.jsonl").exists()]
    return models, jmis, jben, mcq_by_ctrl, misuse_ctrl


def glmm_or(obs):
    try:
        import pandas as pd
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
        df = pd.DataFrame({"S": [o[3] for o in obs], "K": [o[2] for o in obs],
                           "model": [o[0] for o in obs], "control": [o[1] for o in obs]})
        res = BinomialBayesMixedGLM.from_formula(
            "S ~ K", {"model": "0 + C(model)", "control": "0 + C(control)"}, df).fit_vb()
        idx = list(res.model.exog_names).index("K")
        m, sd = res.fe_mean[idx], res.fe_sd[idx]
        return (math.exp(m), math.exp(m - 1.96 * sd), math.exp(m + 1.96 * sd))
    except Exception as e:  # noqa: BLE001
        print("  GLMM failed:", e); return None


def main():
    models, jmis, jben, mcq_by_ctrl, misuse_ctrl = load()

    # ---- 1a. judge-based mean refusal excluding the self-judged model ----
    non_self = [m for m in models if m != JUDGE_MODEL]
    judge_ref = {}
    for m in models:
        labs = list(jmis[m].values())
        judge_ref[m] = sum(1 for x in labs if x == "REFUSE") / len(labs) if labs else float("nan")
    sens_ref_mean = sum(judge_ref[m] for m in non_self) / len(non_self)

    # ---- 1b. judge-based exact-control paired analysis, excluding self-judge ----
    obs = []
    for m in non_self:
        for item_id, jlabel in jmis[m].items():
            ctrl = misuse_ctrl[item_id]
            corr = mcq_by_ctrl[m].get(ctrl)
            if not corr:
                continue
            K = 1 if sum(corr) / len(corr) >= 0.5 else 0
            S = 1 if jlabel == "REFUSE" else 0
            obs.append((m, ctrl, K, S))
    a = sum(1 for _, _, K, S in obs if K and S); b = sum(1 for _, _, K, S in obs if K and not S)
    c = sum(1 for _, _, K, S in obs if not K and S); d = sum(1 for _, _, K, S in obs if not K and not S)
    p_k1 = a / (a + b) if a + b else float("nan"); p_k0 = c / (c + d) if c + d else float("nan")
    glmm = glmm_or(obs)

    # ---- 2. per-model benign correctness (Table IV) ----
    rows = []
    tot = defaultdict(int)
    for (name, tag, params, size, family, reasoning) in C.MODEL_LADDER:
        if name not in jben:
            continue
        labs = list(jben[name].values()); nb = len(labs)
        cr = sum(1 for x in labs if x == "CORRECT_HELP")
        ic = sum(1 for x in labs if x == "INCORRECT_HELP")
        orf = sum(1 for x in labs if x == "OVER_REFUSE")
        tot["cr"] += cr; tot["ic"] += ic; tot["orf"] += orf; tot["n"] += nb
        if name != "GPT-OSS-20B":  # exclude the self-judged model
            tot["cr_excl"] += cr; tot["n_excl"] += nb
        lo, hi = wilson_ci(cr, nb)
        rows.append((name, cr, ic, orf, nb, lo, hi))

    csv = ["model,correct_pct,correct_ci_lo,correct_ci_hi,incorrect_pct,over_refuse_pct,n"]
    for (name, cr, ic, orf, nb, lo, hi) in rows:
        csv.append(f"{name},{cr/nb*100:.1f},{lo*100:.1f},{hi*100:.1f},"
                   f"{ic/nb*100:.1f},{orf/nb*100:.1f},{nb}")
    (C.RESULTS_DIR / "benign_correctness.csv").write_text("\n".join(csv) + "\n")

    def pct(x): return f"{x*100:.1f}"
    macros = {
        "sensRefuseMean": pct(sens_ref_mean),
        "sensPairN": str(len(obs)), "sensPairSKone": pct(p_k1), "sensPairSKzero": pct(p_k0),
    }
    if glmm:
        macros.update({"sensPairOR": f"{glmm[0]:.2f}", "sensPairORlo": f"{glmm[1]:.2f}",
                       "sensPairORhi": f"{glmm[2]:.2f}"})
    macros["benignCorrectMean"] = pct(tot["cr"] / tot["n"])
    macros["benignIncorrectMean"] = pct(tot["ic"] / tot["n"])
    macros["benignCorrectExcl"] = pct(tot["cr_excl"] / tot["n_excl"])
    macros["benignCorrectExclCount"] = str(tot["cr_excl"])
    macros["benignExclN"] = str(tot["n_excl"])
    (C.RESULTS_DIR / "sensitivity_stats.json").write_text(json.dumps(macros, indent=2))

    print(f"judge-based mean refusal (excl {JUDGE_MODEL}): {sens_ref_mean*100:.1f}%")
    print(f"judge-based exact paired: P(S|K=1)={p_k1*100:.1f}% P(S|K=0)={p_k0*100:.1f}% n={len(obs)}")
    if glmm:
        print(f"judge-based crossed GLMM OR={glmm[0]:.2f} [{glmm[1]:.2f},{glmm[2]:.2f}]")
    print(f"benign: correct {tot['cr']/tot['n']*100:.1f}%, incorrect {tot['ic']/tot['n']*100:.1f}%")
    print("wrote sensitivity_stats.json, benign_correctness.csv")


if __name__ == "__main__":
    main()
