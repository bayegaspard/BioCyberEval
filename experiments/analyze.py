"""Aggregate raw results into CSVs, a JSON summary, LaTeX (table + macros), and
publication figures, with Wilson confidence intervals and correlation intervals.

Reads results/raw/<Model>.jsonl (complete files only). Safe to re-run.
"""
from __future__ import annotations
import json, math
from collections import defaultdict, Counter

import config as C
from stats_util import wilson_ci, fmt_ci, pearson_ci, spearman

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "legend.fontsize": 7.5, "figure.dpi": 200, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})

N_ITEMS = len(json.loads(C.BENCH_FILE.read_text()))
LADDER = C.MODEL_LADDER
# Okabe-Ito colorblind-safe palette
FW_COLORS = {"HIPAA": "#0072B2", "Part11": "#E69F00", "GxP": "#009E73"}
FAMILY_MARKERS = {"Llama": "o", "Qwen": "s", "Mistral": "^", "Gemma": "D",
                  "DeepSeek": "v", "GPT-OSS": "P"}
FAM_CODE = {"Access Control & Authorization": "AC", "Identity & Authentication": "IA",
            "Audit Trail & Logging": "AU", "Encryption & Transmission Security": "EN",
            "Data Integrity & Non-repudiation": "DI", "Backup, Availability & Contingency": "BK",
            "Configuration, Validation & Change Control": "CV",
            "Security Management, Risk & Incident Response": "SM"}


def load():
    rows, complete = [], {}
    for (name, tag, params, size, family, reasoning) in LADDER:
        p = C.RAW_DIR / f"{name}.jsonl"
        if not p.exists():
            continue
        recs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        if len(recs) < N_ITEMS:
            continue
        complete[name] = {"params": params, "size": size, "family": family, "reasoning": reasoning}
        rows.extend(recs)
    return rows, complete


def summarize(rows):
    per = defaultdict(lambda: {
        "mcq_n": 0, "mcq_correct": 0, "mcq_unparseable": 0,
        "misuse_n": 0, "misuse_refuse": 0, "misuse_comply": 0, "misuse_amb": 0,
        "benign_n": 0, "benign_help": 0, "benign_overrefuse": 0,
        "mcq_by_fw": defaultdict(lambda: [0, 0]),
        "mcq_by_fam": defaultdict(lambda: [0, 0]),
    })
    for r in rows:
        m = per[r["model"]]; tt = r["task_type"]; sc = r["score"]
        fw = r["framework"]; fam = r["control_family"]
        if tt == "mcq":
            m["mcq_n"] += 1; m["mcq_correct"] += sc["value"]
            m["mcq_unparseable"] += (0 if sc["parseable"] else 1)
            m["mcq_by_fw"][fw][0] += sc["value"]; m["mcq_by_fw"][fw][1] += 1
            m["mcq_by_fam"][fam][0] += sc["value"]; m["mcq_by_fam"][fam][1] += 1
        elif tt == "misuse":
            m["misuse_n"] += 1; m["misuse_refuse"] += sc["safe"]
            m["misuse_comply"] += sc["unsafe"]; m["misuse_amb"] += int(sc["label"] == "AMBIGUOUS")
        else:
            m["benign_n"] += 1; m["benign_help"] += sc["helped"]
            m["benign_overrefuse"] += sc["over_refused"]
    return per


def rate(a, b):
    return (a / b) if b else float("nan")


def order(js):
    return [n for (n, *_) in LADDER if n in js]


def build_js(per, complete):
    js = {}
    for (name, tag, params, size, family, reasoning) in LADDER:
        if name not in per:
            continue
        m = per[name]
        js[name] = {
            "params_b": params, "size_class": size, "family": family, "reasoning": reasoning,
            "mcq_c": m["mcq_correct"], "mcq_n": m["mcq_n"],
            "mcq_acc": rate(m["mcq_correct"], m["mcq_n"]),
            "mcq_unparseable": m["mcq_unparseable"],
            "ref_c": m["misuse_refuse"], "mis_n": m["misuse_n"],
            "misuse_refuse_rate": rate(m["misuse_refuse"], m["misuse_n"]),
            "com_c": m["misuse_comply"],
            "misuse_comply_rate": rate(m["misuse_comply"], m["misuse_n"]),
            "misuse_amb_rate": rate(m["misuse_amb"], m["misuse_n"]),
            "ben_or_c": m["benign_overrefuse"], "ben_n": m["benign_n"],
            "benign_overrefuse_rate": rate(m["benign_overrefuse"], m["benign_n"]),
            "acc_by_fw": {fw: rate(*m["mcq_by_fw"][fw]) for fw in ("HIPAA", "Part11", "GxP")},
            "acc_by_family": {fam: rate(*v) for fam, v in m["mcq_by_fam"].items()},
        }
    return js


def write_csvs(rows, js):
    with open(C.RESULTS_DIR / "scores_long.csv", "w") as f:
        f.write("model,params_b,item_id,framework,task_type,control_family,metric,value,label\n")
        for r in rows:
            sc = r["score"]; tt = r["task_type"]
            if tt == "mcq":
                val, lab = sc["value"], (sc["pred"] or "NA")
            elif tt == "misuse":
                val, lab = sc["safe"], sc["label"]
            else:
                val, lab = sc["helped"], sc["label"]
            f.write(f'{r["model"]},{js[r["model"]]["params_b"]},{r["item_id"]},{r["framework"]},{tt},'
                    f'"{r["control_family"]}",{sc["metric"]},{val},{lab}\n')
    hdr = ("model,params_b,size_class,family,reasoning,mcq_acc,mcq_ci_lo,mcq_ci_hi,"
           "misuse_refuse_rate,refuse_ci_lo,refuse_ci_hi,misuse_comply_rate,"
           "misuse_amb_rate,benign_overrefuse_rate,acc_HIPAA,acc_Part11,acc_GxP\n")
    lines = [hdr]
    for n in order(js):
        r = js[n]
        mlo, mhi = wilson_ci(r["mcq_c"], r["mcq_n"])
        rlo, rhi = wilson_ci(r["ref_c"], r["mis_n"])
        lines.append(f'{n},{r["params_b"]},{r["size_class"]},{r["family"]},{r["reasoning"]},'
                     f'{r["mcq_acc"]:.4f},{mlo:.4f},{mhi:.4f},'
                     f'{r["misuse_refuse_rate"]:.4f},{rlo:.4f},{rhi:.4f},'
                     f'{r["misuse_comply_rate"]:.4f},{r["misuse_amb_rate"]:.4f},'
                     f'{r["benign_overrefuse_rate"]:.4f},'
                     f'{r["acc_by_fw"]["HIPAA"]:.4f},{r["acc_by_fw"]["Part11"]:.4f},{r["acc_by_fw"]["GxP"]:.4f}\n')
    (C.RESULTS_DIR / "summary.csv").write_text("".join(lines))
    (C.RESULTS_DIR / "summary.json").write_text(json.dumps(js, indent=2))


# ------------------------------- summary -----------------------------------
def write_summary(js):
    names = order(js)
    pd = C.RESULTS_DIR; pd.mkdir(parents=True, exist_ok=True)

    def pct(x):
        return f"{x*100:.1f}"

    # ---- Markdown results table with Wilson CIs ----
    MD = ["# BioCyberEval results", "",
          "Per-model knowledge and guardrail results (10 open-weight models).",
          "MCQ = compliance-knowledge accuracy (72 items); Refuse/Comply = guardrail",
          "outcome on 36 misuse items; brackets are 95% Wilson intervals. Deterministic",
          "scoring, temperature 0.", "",
          "| Model | Size (B) | Family | MCQ % [95% CI] | Refuse % [95% CI] | Comply % [95% CI] |",
          "|---|---|---|---|---|---|"]
    for n in names:
        r = js[n]
        mlo, mhi = fmt_ci(r["mcq_c"], r["mcq_n"])
        rlo, rhi = fmt_ci(r["ref_c"], r["mis_n"])
        clo, chi = fmt_ci(r["com_c"], r["mis_n"])
        MD.append(f'| {n} | {r["params_b"]:.1f} | {r["family"]} | '
                  f'{pct(r["mcq_acc"])} [{mlo}-{mhi}] | '
                  f'{pct(r["misuse_refuse_rate"])} [{rlo}-{rhi}] | '
                  f'{pct(r["misuse_comply_rate"])} [{clo}-{chi}] |')

    # ---- aggregates ----
    accs = [js[n]["mcq_acc"] for n in names]
    refs = [js[n]["misuse_refuse_rate"] for n in names]
    comps = [js[n]["misuse_comply_rate"] for n in names]
    ors = [js[n]["benign_overrefuse_rate"] for n in names]
    sizes = [js[n]["params_b"] for n in names]
    logsizes = [math.log10(s) for s in sizes]

    # correlations with CIs / p / Spearman + sensitivity
    r_sa, ci_sa_lo, ci_sa_hi, p_sa = _pearson(logsizes, accs)
    rho_sa, prho_sa = spearman(sizes, accs)
    dense = [n for n in names if js[n]["family"] != "GPT-OSS"]  # exclude MoE
    r_sa_d, _, _, p_sa_d = _pearson([math.log10(js[n]["params_b"]) for n in dense],
                                    [js[n]["mcq_acc"] for n in dense])
    r_ar, ci_ar_lo, ci_ar_hi, p_ar = _pearson(accs, refs)
    # within-family Llama scaling
    llama = [n for n in names if js[n]["family"] == "Llama"]
    rho_llama, _ = spearman([js[n]["params_b"] for n in llama], [js[n]["mcq_acc"] for n in llama]) if len(llama) > 2 else (float("nan"), 1)

    best_mcq = max(names, key=lambda n: js[n]["mcq_acc"])
    worst_mcq = min(names, key=lambda n: js[n]["mcq_acc"])
    worst_ref = min(names, key=lambda n: js[n]["misuse_refuse_rate"])
    best_ref = max(names, key=lambda n: js[n]["misuse_refuse_rate"])
    max_comply = max(names, key=lambda n: js[n]["misuse_comply_rate"])

    fw_means = {fw: sum(js[n]["acc_by_fw"][fw] for n in names) / len(names) for fw in ("HIPAA", "Part11", "GxP")}
    hardest_fw = min(fw_means, key=fw_means.get); easiest_fw = max(fw_means, key=fw_means.get)

    fam_means = {}
    for fam in FAM_CODE:
        vals = [js[n]["acc_by_family"].get(fam) for n in names if js[n]["acc_by_family"].get(fam) is not None]
        if vals:
            fam_means[fam] = sum(vals) / len(vals)
    fam_sorted = sorted(fam_means, key=fam_means.get)
    weakest = [FAM_CODE[f] for f in fam_sorted[:2]]
    strongest = [FAM_CODE[f] for f in fam_sorted[-3:][::-1]]

    n_comply_high = sum(1 for n in names if js[n]["misuse_comply_rate"] >= 0.25)

    FWNAME = {"HIPAA": "HIPAA", "Part11": "21 CFR Part 11", "GxP": "GxP"}
    macros = {
        "NModels": str(len(names)), "NItems": "126", "NMCQ": "72", "NMisuse": "36",
        "NBenign": "18", "NFrameworks": "3", "NFamilies": "8",
        "meanMCQ": pct(sum(accs) / len(accs)), "minMCQ": pct(min(accs)), "maxMCQ": pct(max(accs)),
        "bestMCQmodel": best_mcq, "worstMCQmodel": worst_mcq,
        "bestMCQval": pct(js[best_mcq]["mcq_acc"]), "worstMCQval": pct(js[worst_mcq]["mcq_acc"]),
        "meanRefuse": pct(sum(refs) / len(refs)), "minRefuse": pct(min(refs)), "maxRefuse": pct(max(refs)),
        "worstRefuseModel": worst_ref, "worstRefuseVal": pct(js[worst_ref]["misuse_refuse_rate"]),
        "bestRefuseModel": best_ref, "bestRefuseVal": pct(js[best_ref]["misuse_refuse_rate"]),
        "meanComply": pct(sum(comps) / len(comps)), "maxComply": pct(max(comps)),
        "maxComplyModel": max_comply, "maxComplyVal": pct(js[max_comply]["misuse_comply_rate"]),
        "meanOverRefuse": pct(sum(ors) / len(ors)), "minOverRefuse": pct(min(ors)), "maxOverRefuse": pct(max(ors)),
        "hardestFW": FWNAME[hardest_fw], "hardestFWval": pct(fw_means[hardest_fw]),
        "easiestFW": FWNAME[easiest_fw], "easiestFWval": pct(fw_means[easiest_fw]),
        "fwHIPAA": pct(fw_means["HIPAA"]), "fwPartEleven": pct(fw_means["Part11"]), "fwGxP": pct(fw_means["GxP"]),
        "weakFamilies": ", ".join(weakest), "strongFamilies": ", ".join(strongest),
        "nComplyHigh": str(n_comply_high),
        "corrSizeAcc": f"{r_sa:.2f}", "corrSizeAccLo": f"{ci_sa_lo:.2f}", "corrSizeAccHi": f"{ci_sa_hi:.2f}",
        "corrSizeAccP": f"{p_sa:.3f}", "spearSizeAcc": f"{rho_sa:.2f}", "spearSizeAccP": f"{prho_sa:.3f}",
        "corrSizeAccDense": f"{r_sa_d:.2f}", "corrSizeAccDenseP": f"{p_sa_d:.3f}",
        "corrAccRefuse": f"{r_ar:.2f}", "corrAccRefuseLo": f"{ci_ar_lo:.2f}", "corrAccRefuseHi": f"{ci_ar_hi:.2f}",
        "corrAccRefuseP": f"{p_ar:.3f}",
        "spearLlama": f"{rho_llama:.2f}",
        "overRefuseWilsonHi": fmt_ci(0, js[names[0]]["ben_n"])[1],  # upper Wilson for 0/18
    }
    import json as _json
    (pd / "stats.json").write_text(_json.dumps(macros, indent=2))
    MD.extend(["", "## Key statistics", "",
        f"- Models: {len(names)}; items: 126 (72 knowledge / 36 misuse / 18 benign).",
        f"- Knowledge (MCQ): mean {macros['meanMCQ']}%, range {macros['minMCQ']}-{macros['maxMCQ']}%.",
        f"- Misuse refusal: mean {macros['meanRefuse']}%, range {macros['minRefuse']}-{macros['maxRefuse']}%; mean comply {macros['meanComply']}%.",
        f"- Knowledge vs scale: Pearson r={macros['corrSizeAcc']} (p={macros['corrSizeAccP']}); Spearman rho={macros['spearSizeAcc']} (p={macros['spearSizeAccP']}); dense-only r={macros['corrSizeAccDense']}.",
        f"- Knowledge vs refusal (model level): Pearson r={macros['corrAccRefuse']}, 95% CI [{macros['corrAccRefuseLo']}, {macros['corrAccRefuseHi']}], p={macros['corrAccRefuseP']}.",
        f"- Framework means: HIPAA {macros['fwHIPAA']}%, Part 11 {macros['fwPartEleven']}%, GxP {macros['fwGxP']}%.",
        f"- Weakest control families: {macros['weakFamilies']}; strongest: {macros['strongFamilies']}.",
        "- Control-level paired K-vs-U analysis: results/paired_analysis.json.",
        "- Scorer cross-check vs LLM judge: results/validation_full.json.",
        "- Benign correctness (judge-based): results/benign_correctness.csv (from sensitivity.py)."])
    (pd / "SUMMARY.md").write_text("\n".join(MD) + "\n")
    print("wrote results/SUMMARY.md, results/stats.json, and figures/*.pdf")
    return js


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return (float("nan"),) * 4
    r = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)
    lo, hi, p = pearson_ci(r, n)
    return r, lo, hi, p


# ------------------------------- figures -----------------------------------
# Figures are drawn by figures.py from results/summary.json (single source of style).


def main():
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    rows, complete = load()
    if not complete:
        print("no complete model files yet"); return
    per = summarize(rows)
    js = build_js(per, complete)
    write_csvs(rows, js)
    print(f"complete models ({len(js)}):", ", ".join(order(js)))
    write_summary(js)
    import figures
    names = order(js)
    figures.fig_knowledge_vs_safety(js, names)
    figures.fig_acc_by_size(js, names)
    figures.fig_framework_dot(js, names)
    figures.fig_guardrail_stack(js, names)
    figures.fig_forest(js, names)
    figures.fig_family_heatmap(js, names)
    print("wrote figures ->", C.FIG_DIR)
    print(f'\n{"model":18} {"nB":>5} {"MCQ":>6} {"refuse":>7} {"comply":>7} {"benOR":>6}')
    for n in order(js):
        r = js[n]
        print(f'{n:18} {r["params_b"]:>5} {r["mcq_acc"]*100:>5.1f}% {r["misuse_refuse_rate"]*100:>6.1f}% '
              f'{r["misuse_comply_rate"]*100:>6.1f}% {r["benign_overrefuse_rate"]*100:>5.1f}%')


if __name__ == "__main__":
    main()
