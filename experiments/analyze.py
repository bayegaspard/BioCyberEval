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
        "- Scorer cross-check vs independent judge: results/validation_full.json.",
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
def fig_knowledge_vs_safety(js):
    from matplotlib.patches import Rectangle
    names = order(js)
    KX, KY = 75, 25   # explicit danger-zone thresholds
    # hand-tuned label offsets (points) to avoid overlap in the crowded cluster
    off = {"Llama-3.2-1B": (6, 4), "DeepSeek-R1-1.5B": (6, -11),
           "DeepSeek-Coder-1.3B": (-6, 6), "Llama-3.2-3B": (-52, 4),
           "Gemma-3-4B": (6, 6), "Mistral-7B": (-46, -4), "Qwen2.5-7B": (7, -6),
           "Llama-3.1-8B": (7, 3), "DeepSeek-R1-8B": (-64, 0), "GPT-OSS-20B": (7, 2)}
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    ax.add_patch(Rectangle((KX, -5), 100 - KX, KY + 5, facecolor="#fde0d0", alpha=0.7, zorder=0))
    ax.text(76, 24, f"knowledge $\\geq$ {KX}%,\nrefusal $\\leq$ {KY}%",
            ha="left", va="top", fontsize=6.0, color="#8a3b12", zorder=1)
    seen = set()
    for n in names:
        r = js[n]
        x, y = r["mcq_acc"] * 100, r["misuse_refuse_rate"] * 100
        xlo, xhi = wilson_ci(r["mcq_c"], r["mcq_n"]); ylo, yhi = wilson_ci(r["ref_c"], r["mis_n"])
        mk = FAMILY_MARKERS.get(r["family"], "o")
        lbl = r["family"] if r["family"] not in seen else None
        seen.add(r["family"])
        ax.errorbar(x, y, xerr=[[x - xlo * 100], [xhi * 100 - x]],
                    yerr=[[y - ylo * 100], [yhi * 100 - y]], fmt=mk, ms=6,
                    color="#333333", ecolor="#c4c4c4", elinewidth=0.7, capsize=2,
                    label=lbl, zorder=3)
        dx, dy = off.get(n, (6, 4))
        ax.annotate(n, (x, y), fontsize=5.6, ha="left", va="center", xytext=(dx, dy),
                    textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", lw=0.4, color="#999999", shrinkA=0, shrinkB=2))
    ax.set_xlabel("Compliance knowledge (MCQ accuracy, %)")
    ax.set_ylabel("Misuse-refusal rate (%)")
    ax.set_xlim(35, 102); ax.set_ylim(-5, 100)
    ax.legend(frameon=False, fontsize=6.2, loc="upper left", ncol=2)
    ax.set_title("Knowledge versus guardrail behavior")
    fig.savefig(C.FIG_DIR / "fig_knowledge_vs_safety.pdf")
    plt.close(fig)


def fig_acc_by_size(js):
    names = order(js)
    off = {"Llama-3.2-1B": (4, 4), "DeepSeek-Coder-1.3B": (4, -10),
           "DeepSeek-R1-1.5B": (4, 5), "Llama-3.2-3B": (4, 4), "Gemma-3-4B": (-40, 4),
           "Mistral-7B": (4, -10), "Qwen2.5-7B": (4, 5), "Llama-3.1-8B": (5, -10),
           "DeepSeek-R1-8B": (5, 3), "GPT-OSS-20B": (6, 2)}
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    for n in names:
        r = js[n]
        mk = FAMILY_MARKERS.get(r["family"], "o")
        ax.scatter(r["params_b"], r["mcq_acc"] * 100, marker=mk, s=44,
                   c=("#D55E00" if r["family"] == "GPT-OSS" else "#0072B2"), zorder=3,
                   edgecolors="white", linewidths=0.5)
        dx, dy = off.get(n, (4, 3))
        ax.annotate(n, (r["params_b"], r["mcq_acc"] * 100), fontsize=5.6, ha="left",
                    va="center", xytext=(dx, dy), textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", lw=0.4, color="#aaaaaa", shrinkA=0, shrinkB=2))
    ax.axhline(25, ls="--", c="#999", lw=0.7); ax.text(1.0, 27, "chance (25%)", fontsize=6, color="#666")
    ax.set_xscale("log"); ax.set_xlabel("Total parameters (B, log scale)")
    ax.set_ylabel("MCQ accuracy (%)"); ax.set_ylim(0, 100)
    ax.set_title("Knowledge vs. scale (confounded by family/architecture)")
    fig.savefig(C.FIG_DIR / "fig_acc_by_size.pdf")
    plt.close(fig)


def fig_framework_dot(js):
    """Dot plot: framework mean with model spread, replacing 30 grouped bars."""
    names = order(js)
    fws = ["HIPAA", "Part11", "GxP"]; disp = {"HIPAA": "HIPAA", "Part11": "21 CFR Part 11", "GxP": "GxP"}
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    for i, fw in enumerate(fws):
        vals = [js[n]["acc_by_fw"][fw] * 100 for n in names]
        ax.scatter(vals, [i] * len(vals), color=FW_COLORS[fw], alpha=0.55, s=28, zorder=3)
        mean = sum(vals) / len(vals)
        ax.scatter([mean], [i], color="black", marker="|", s=400, zorder=4, linewidths=1.6)
        ax.annotate(f"mean {mean:.1f}", (mean, i + 0.18), fontsize=6.5, ha="center")
    ax.axvline(25, ls="--", c="#999", lw=0.7)
    ax.set_yticks(range(3)); ax.set_yticklabels([disp[f] for f in fws])
    ax.set_xlabel("MCQ accuracy across the 10 models (%)"); ax.set_xlim(20, 100)
    ax.set_ylim(-0.5, 2.6); ax.set_title("Knowledge by framework")
    fig.savefig(C.FIG_DIR / "fig_acc_by_framework.pdf")
    plt.close(fig)


def fig_guardrail_stack(js):
    names = order(js)
    refuse = [js[n]["misuse_refuse_rate"] * 100 for n in names]
    amb = [js[n]["misuse_amb_rate"] * 100 for n in names]
    comply = [js[n]["misuse_comply_rate"] * 100 for n in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    b1 = ax.bar(x, refuse, label="Refuse (safe)", color="#009E73")
    b2 = ax.bar(x, amb, bottom=refuse, label="Ambiguous", color="#BBBBBB")
    b3 = ax.bar(x, comply, bottom=[a + b for a, b in zip(refuse, amb)], label="Comply (unsafe)", color="#D55E00")
    for bar in b1: bar.set_hatch("//")
    for bar in b3: bar.set_hatch("xx")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=35, ha="right", fontsize=6.6)
    ax.set_ylabel("Share of 36 misuse prompts (%)"); ax.set_ylim(0, 100)
    ax.set_title("Guardrail outcomes on control-violating requests", pad=22)
    ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.14))
    fig.savefig(C.FIG_DIR / "fig_guardrail_stack.pdf")
    plt.close(fig)


def fig_forest(js):
    """Forest plot: per-model misuse-refusal with 95% Wilson CIs."""
    names = order(js)[::-1]
    ys = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for i, n in enumerate(names):
        r = js[n]; val = r["misuse_refuse_rate"] * 100
        lo, hi = wilson_ci(r["ref_c"], r["mis_n"])
        ax.plot([lo * 100, hi * 100], [i, i], color="#888", lw=1.2, zorder=2)
        ax.scatter([val], [i], color="#1b7837", s=30, zorder=3)
    ax.set_yticks(ys); ax.set_yticklabels(names, fontsize=6.8)
    ax.set_xlabel("Misuse-refusal rate (%) with 95% Wilson CI"); ax.set_xlim(-3, 100)
    ax.set_title("Refusal of control-violating requests")
    fig.savefig(C.FIG_DIR / "fig_forest.pdf")
    plt.close(fig)


def fig_family_heatmap(js):
    names = order(js)
    fams = ["AC", "IA", "AU", "EN", "DI", "BK", "CV", "SM"]
    M = np.full((len(names), len(fams)), np.nan)
    for i, n in enumerate(names):
        for full, val in js[n]["acc_by_family"].items():
            M[i, fams.index(FAM_CODE[full])] = val * 100
    fig, ax = plt.subplots(figsize=(6.4, 4.3))
    im = ax.imshow(M, aspect="auto", cmap="viridis", vmin=0, vmax=100)
    ax.set_xticks(range(len(fams))); ax.set_xticklabels(fams, fontsize=9)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=8)
    for i in range(len(names)):
        for j in range(len(fams)):
            if not math.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.0f}", ha="center", va="center", fontsize=7.5,
                        color="white" if M[i, j] < 55 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03); cb.set_label("MCQ accuracy (%)", fontsize=9)
    ax.set_title("Knowledge by control family")
    fig.savefig(C.FIG_DIR / "fig_family_heatmap.pdf")
    plt.close(fig)


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
    fig_knowledge_vs_safety(js)
    fig_acc_by_size(js)
    fig_framework_dot(js)
    fig_guardrail_stack(js)
    fig_forest(js)
    fig_family_heatmap(js)
    print("wrote figures ->", C.FIG_DIR)
    print(f'\n{"model":18} {"nB":>5} {"MCQ":>6} {"refuse":>7} {"comply":>7} {"benOR":>6}')
    for n in order(js):
        r = js[n]
        print(f'{n:18} {r["params_b"]:>5} {r["mcq_acc"]*100:>5.1f}% {r["misuse_refuse_rate"]*100:>6.1f}% '
              f'{r["misuse_comply_rate"]*100:>6.1f}% {r["benign_overrefuse_rate"]*100:>5.1f}%')


if __name__ == "__main__":
    main()
