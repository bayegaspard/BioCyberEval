"""All paper figures, drawn at final print size from saved results.

Every figure reads its numbers from results/ (summary.json, paired_analysis.json,
validation_judgments.jsonl); nothing is refit here, so redrawing a figure can
never change a reported number.

Print conventions (IEEE compsoc, measured from IEEEtran.cls):
  column width 3.375 in, text width 7.0 in. Figures are drawn at these widths
  and included at 100%, so the 7 pt type below is 7 pt on the page.
  Fonts are embedded as TrueType (pdf.fonttype 42), as IEEE PDF eXpress
  requires; matplotlib's default Type 3 output is rejected.

Color roles (validated with the dataviz palette validator):
  outcome polarity  Refuse #256abf (blue) / Ambiguous #c3c2b7 (neutral) /
                    Comply #e34948 (red), a diverging pair with a gray midpoint;
                    Comply also carries a hatch so the figure survives grayscale.
  frameworks        categorical slots 1 to 3 (#2a78d6, #eb6834, #1baf7a),
                    always paired with a text label.
  magnitude         one-hue blue ramp (heatmap, confusion matrix).

  python3 figures.py            # redraw every figure
"""
from __future__ import annotations
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.patheffects as pe
import numpy as np
import config as C
from stats_util import wilson_ci

COL, FULL = 3.375, 7.0   # inches
HALO = [pe.withStroke(linewidth=1.6, foreground="white")]

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, RULE = "#e1e0d9", "#c3c2b7"
REFUSE, NEUTRAL, COMPLY = "#256abf", "#c3c2b7", "#e34948"
FW_COLOR = {"HIPAA": "#2a78d6", "Part11": "#eb6834", "GxP": "#1baf7a"}
FW_NAME = {"HIPAA": "HIPAA", "Part11": "21 CFR Part 11", "GxP": "GxP / Annex 11"}
BLUE_RAMP = ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
             "#256abf", "#184f95", "#0d366b"]
SEQ = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
FAMILY_MARKER = {"Llama": "o", "Qwen": "s", "Mistral": "^", "Gemma": "D",
                 "DeepSeek": "v", "GPT-OSS": "P"}
FAM_CODE = {"Access Control & Authorization": "AC", "Identity & Authentication": "IA",
            "Audit Trail & Logging": "AU", "Encryption & Transmission Security": "EN",
            "Data Integrity & Non-repudiation": "DI", "Backup, Availability & Contingency": "BK",
            "Configuration, Validation & Change Control": "CV",
            "Security Management, Risk & Incident Response": "SM"}

plt.rcParams.update({
    "font.family": "Arial", "font.size": 7, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "text.color": INK, "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.5,
    "legend.frameon": False, "hatch.color": "white", "hatch.linewidth": 0.6,
    "savefig.dpi": 600, "figure.dpi": 150,
})


def save(fig, name):
    fig.savefig(C.FIG_DIR / name, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def load_summary():
    js = json.loads((C.RESULTS_DIR / "summary.json").read_text())
    names = [n for (n, *_r) in C.MODEL_LADDER if n in js]
    return js, names


def judge_refusal():
    out = {}
    for l in (C.RESULTS_DIR / "validation_judgments.jsonl").read_text().splitlines():
        if l.strip():
            d = json.loads(l)
            if d["task_type"] == "misuse":
                out.setdefault(d["model"], []).append(d["judge_label"] == "REFUSE")
    return {m: sum(v) / len(v) for m, v in out.items()}


def xgrid(ax):
    ax.grid(axis="x", color=GRID, lw=0.5); ax.set_axisbelow(True)


def ygrid(ax):
    ax.grid(axis="y", color=GRID, lw=0.5); ax.set_axisbelow(True)


# --------------------------------------------------------------------------- 1
def fig_pipeline():
    """Six-stage left-to-right flow across the full text width."""
    fig = plt.figure(figsize=(FULL, 1.95))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 28); ax.axis("off")
    stages = [(0.3, "1", "Regulatory sources"), (17.0, "2", "Control catalog"),
              (33.7, "3", "Benchmark items"), (50.4, "4", "Model inference"),
              (67.1, "5", "Scoring"), (83.8, "6", "Analysis")]
    W = 15.9

    def card(x, y, w, h, lines, accent=None, dashed=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.6",
                                    lw=0.6, ec=MUTED if not dashed else INK2, fc="white",
                                    ls=(0, (2.5, 1.5)) if dashed else "-", mutation_aspect=0.6))
        if accent:
            ax.add_patch(Rectangle((x, y + 0.35), 0.75, h - 0.7, lw=0, fc=accent))
        tx = x + (1.5 if accent else 1.0)
        n = len(lines); step = 1.85
        top = y + h / 2 + step * (n - 1) / 2
        for i, (txt, bold) in enumerate(lines):
            ax.text(tx, top - i * step, txt, ha="left", va="center", fontsize=6.3 if bold else 5.9,
                    fontweight="bold" if bold else "normal", color=INK if bold else INK2)

    for x, k, title in stages:
        ax.add_patch(FancyBboxPatch((x, 0.4), W, 27.0, boxstyle="round,pad=0,rounding_size=0.8",
                                    lw=0, fc="#f6f5f2", mutation_aspect=0.6))
        ax.text(x + 1.0, 25.4, k, fontsize=6.5, fontweight="bold", color="white", ha="center",
                va="center", bbox=dict(boxstyle="circle,pad=0.18", fc=INK, ec="none"))
        ax.text(x + 2.3, 25.4, title, fontsize=7, fontweight="bold", va="center", color=INK)

    # 1 sources
    card(1.1, 15.2, 14.3, 7.6, [("HIPAA Security Rule", True), ("45 CFR 164, Subpart C", False),
                                ("technical safeguards", False)])
    card(1.1, 8.6, 14.3, 5.7, [("21 CFR Part 11", True), ("e-records, e-signatures", False)])
    card(1.1, 2.0, 14.3, 5.7, [("EU GMP Annex 11", True), ("with ALCOA+ principles", False)])
    # 2 catalog
    card(17.8, 15.2, 14.3, 7.6, [("Clause extraction", True), ("verified against", False),
                                 ("primary text", False)])
    card(17.8, 2.0, 14.3, 12.3, [("Normalized catalog", True), ("8 control families", False),
                                 ("AC IA AU EN", False), ("DI BK CV SM", False),
                                 ("mapped to", False), ("NIST CSF 2.0", False)])
    # 3 items
    card(34.5, 17.4, 14.3, 5.4, [("Knowledge (72)", True), ("multiple choice", False)], accent=REFUSE)
    card(34.5, 10.7, 14.3, 5.4, [("Misuse (36)", True), ("should refuse", False)], accent=COMPLY)
    card(34.5, 4.0, 14.3, 5.4, [("Benign (18)", True), ("should help correctly", False)],
         accent=FW_COLOR["GxP"])
    ax.text(41.65, 2.3, "126 items, clause-traceable", ha="center", fontsize=5.6, color=INK2,
            style="italic")
    # 4 inference
    card(51.2, 2.0, 14.3, 20.8, [("10 open-weight LLMs", True), ("6 families", False),
                                 ("1.2 to 20.9B parameters", False), ("", False),
                                 ("Ollama, quantized", True), ("temperature 0, seed 42", False),
                                 ("neutral persona", False), ("1024 new tokens", False)])
    # 5 scoring
    card(67.9, 13.4, 14.3, 9.4, [("Deterministic", True), ("knowledge: answer key", False),
                                 ("misuse: regex for the", False), ("harmful artifact", False)])
    card(67.9, 2.0, 14.3, 8.6, [("LLM judge", True), ("GPT-OSS-20B", False), ("benign correctness", False),
                                ("relabels all 360 misuse", False)],
         dashed=True)
    ax.annotate("", xy=(80.5, 13.3), xytext=(80.5, 10.7),
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=INK2, ls=(0, (2, 1.2)),
                                mutation_scale=6))
    ax.text(79.9, 12.0, "cross-check", fontsize=5.4, color=INK2, va="center", ha="right",
            style="italic")
    # 6 analysis
    card(84.6, 15.2, 14.3, 7.6, [("Rates", True), ("Wilson 95% CIs", False),
                                 ("both scorers reported", False)])
    card(84.6, 8.6, 14.3, 5.7, [("Failure modes", True), ("type, family, manner", False)])
    card(84.6, 2.0, 14.3, 5.7, [("Paired K vs. U", True), ("FE, GEE, Bayesian", False)])

    # stage-to-stage arrows
    for x, *_ in stages[:-1]:
        ax.annotate("", xy=(x + W + 1.15, 13.0), xytext=(x + W - 0.2, 13.0),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK, mutation_scale=7,
                                    shrinkA=0, shrinkB=0))
    save(fig, "fig_pipeline.pdf")


# --------------------------------------------------------------------------- 2
def fig_acc_by_size(js, names):
    off = {"Llama-3.2-1B": (-2, -7, "left"), "DeepSeek-Coder-1.3B": (6, 0, "left"),
           "DeepSeek-R1-1.5B": (6, 0, "left"), "Llama-3.2-3B": (-5, 5, "right"),
           "Gemma-3-4B": (0, -7, "center"), "Mistral-7B": (-5, -5, "right"),
           "Qwen2.5-7B": (-4, 6, "right"), "Llama-3.1-8B": (5, 5, "left"),
           "DeepSeek-R1-8B": (6, -4, "left"), "GPT-OSS-20B": (0, 7, "center")}
    fig, ax = plt.subplots(figsize=(COL, 2.15))
    ygrid(ax)
    ax.axhline(25, ls=(0, (3, 2)), c=MUTED, lw=0.6)
    ax.text(1.08, 27, "chance (25%)", fontsize=5.8, color=INK2)
    for n in names:
        r = js[n]; x, y = r["params_b"], r["mcq_acc"] * 100
        ax.scatter(x, y, marker=FAMILY_MARKER[r["family"]], s=22, c=REFUSE, ec="white",
                   lw=0.5, zorder=3)
        dx, dy, h = off[n]
        ax.annotate(n, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=5.6,
                    color=INK2, ha=h, va="center", path_effects=HALO, zorder=4)
    ax.set_xscale("log"); ax.set_xlim(1.0, 30); ax.set_ylim(0, 100)
    ax.set_xticks([1, 2, 5, 10, 20]); ax.set_xticklabels(["1", "2", "5", "10", "20"])
    ax.minorticks_off()
    ax.set_xlabel("Total parameters (billions, log scale)")
    ax.set_ylabel("Knowledge accuracy (%)")
    ax.legend(handles=fam_handles(js, names), loc="lower right", ncol=3, fontsize=5.8,
              handletextpad=0.2, columnspacing=0.8, borderaxespad=0.2)
    save(fig, "fig_acc_by_size.pdf")


def fam_handles(js, names, color=REFUSE):
    seen = []
    for n in names:
        f = js[n]["family"]
        if f not in seen:
            seen.append(f)
    return [Line2D([], [], marker=FAMILY_MARKER[f], ls="", ms=4, mfc=color, mec="white",
                   mew=0.4, label=f) for f in seen]


# --------------------------------------------------------------------------- 3
def fig_framework_dot(js, names):
    fws = ["HIPAA", "Part11", "GxP"]
    fig, ax = plt.subplots(figsize=(COL, 1.45))
    xgrid(ax)
    ax.axvline(25, ls=(0, (3, 2)), c=MUTED, lw=0.6)
    ax.text(26, 2.42, "chance", fontsize=5.8, color=INK2, va="center")
    for i, fw in enumerate(fws):
        vals = [js[n]["acc_by_fw"][fw] * 100 for n in names]
        jitter = np.linspace(-0.12, 0.12, len(vals))
        ax.scatter(vals, i + jitter, s=11, color=FW_COLOR[fw], ec="white", lw=0.4, zorder=3)
        m = sum(vals) / len(vals)
        ax.plot([m, m], [i - 0.3, i + 0.3], color=INK, lw=1.2, zorder=4)
        ax.text(m, i + 0.36, f"mean {m:.1f}", fontsize=5.8, ha="center", va="bottom", color=INK)
    ax.set_yticks(range(3)); ax.set_yticklabels([FW_NAME[f] for f in fws])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(20, 100); ax.set_ylim(-0.5, 2.6)
    ax.set_xlabel("Knowledge accuracy per model (%)")
    save(fig, "fig_acc_by_framework.pdf")


# --------------------------------------------------------------------------- 4
def fig_guardrail_stack(js, names):
    rows = names[::-1]
    y = np.arange(len(rows))
    ref = np.array([js[n]["misuse_refuse_rate"] * 100 for n in rows])
    amb = np.array([js[n]["misuse_amb_rate"] * 100 for n in rows])
    com = np.array([js[n]["misuse_comply_rate"] * 100 for n in rows])
    fig, ax = plt.subplots(figsize=(COL, 2.35))
    kw = dict(height=0.68, ec="white", lw=0.7)
    ax.barh(y, ref, color=REFUSE, label="Refuse (safe)", **kw)
    ax.barh(y, amb, left=ref, color=NEUTRAL, label="Ambiguous", **kw)
    ax.barh(y, com, left=ref + amb, color=COMPLY, hatch="//////", label="Comply (unsafe)", **kw)
    for yi, r, c in zip(y, ref, com):
        if r >= 9:
            ax.text(r - 1.2, yi, f"{r:.0f}", ha="right", va="center", fontsize=5.6, color="white")
        if c >= 9:
            ax.text(99, yi, f"{c:.0f}", ha="right", va="center", fontsize=5.6, color="white",
                    bbox=dict(boxstyle="square,pad=0.08", fc=COMPLY, ec="none"))
    ax.set_yticks(y); ax.set_yticklabels(rows); ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Share of the 36 misuse requests (%)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=3, fontsize=6.2,
              handlelength=1.3, handletextpad=0.4, columnspacing=1.0, borderaxespad=0.1)
    save(fig, "fig_guardrail_stack.pdf")


# --------------------------------------------------------------------------- 5
def fig_forest(js, names):
    jref = judge_refusal()
    rows = names[::-1]
    fig, ax = plt.subplots(figsize=(COL, 2.3))
    xgrid(ax)
    for i, n in enumerate(rows):
        r = js[n]; v = r["misuse_refuse_rate"] * 100
        lo, hi = wilson_ci(r["ref_c"], r["mis_n"])
        ax.plot([lo * 100, hi * 100], [i, i], color=REFUSE, lw=1.0, alpha=0.55,
                solid_capstyle="butt", zorder=2)
        ax.scatter(v, i, s=16, color=REFUSE, zorder=3, ec="white", lw=0.4)
        ax.scatter(jref[n] * 100, i, s=16, facecolor="white", ec=INK, lw=0.7, marker="D", zorder=4)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows); ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-2, 102); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Misuse-refusal rate (%)")
    h = [Line2D([], [], color=REFUSE, marker="o", ms=4, mec="white", mew=0.4, lw=1.0,
                label="Deterministic scorer, 95% Wilson CI"),
         Line2D([], [], color=INK, marker="D", ms=3.6, mfc="white", mew=0.7, ls="",
                label="LLM judge")]
    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, fontsize=6.0,
              handletextpad=0.4, columnspacing=1.0, borderaxespad=0.1)
    save(fig, "fig_forest.pdf")


# --------------------------------------------------------------------------- 6
def fig_knowledge_vs_safety(js, names):
    KX, KY = 75, 25
    off = {"Llama-3.2-1B": (5, 5, "left"), "DeepSeek-R1-1.5B": (0, 17, "center"),
           "DeepSeek-Coder-1.3B": (0, 7, "center"), "Llama-3.2-3B": (-5, 4, "right"),
           "Gemma-3-4B": (6, 0, "left"), "Mistral-7B": (0, 7, "center"),
           "Qwen2.5-7B": (5, 0, "left"), "Llama-3.1-8B": (5, 3, "left"),
           "DeepSeek-R1-8B": (-5, 3, "right"), "GPT-OSS-20B": (5, 4, "left")}
    fig, ax = plt.subplots(figsize=(COL, 2.55))
    ax.add_patch(Rectangle((KX, -4), 106 - KX, KY + 4, fc=COMPLY, alpha=0.08, lw=0, zorder=0))
    ax.text(105, KY - 1.5, f"knowledge $\\geq$ {KX}%, refusal $\\leq$ {KY}%", ha="right",
            va="top", fontsize=5.4, color="#a3302f", path_effects=HALO, zorder=4)
    for n in names:
        r = js[n]; x, y = r["mcq_acc"] * 100, r["misuse_refuse_rate"] * 100
        xlo, xhi = wilson_ci(r["mcq_c"], r["mcq_n"]); ylo, yhi = wilson_ci(r["ref_c"], r["mis_n"])
        ax.errorbar(x, y, xerr=[[x - xlo * 100], [xhi * 100 - x]],
                    yerr=[[y - ylo * 100], [yhi * 100 - y]], fmt="none", ecolor=RULE,
                    elinewidth=0.6, capsize=0, zorder=2)
        ax.scatter(x, y, marker=FAMILY_MARKER[r["family"]], s=20, c=INK, ec="white", lw=0.4,
                   zorder=3)
        dx, dy, h = off[n]
        leader = dict(arrowstyle="-", lw=0.4, color=MUTED, shrinkA=1.5, shrinkB=2.5) \
            if abs(dy) > 10 else None
        ax.annotate(n, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=5.5,
                    color=INK2, ha=h, va="center", zorder=4, path_effects=HALO,
                    arrowprops=leader)
    ax.set_xlim(26, 106); ax.set_ylim(-4, 100); ax.set_xticks(range(30, 101, 10))
    ax.set_xlabel("Knowledge accuracy (%)"); ax.set_ylabel("Misuse-refusal rate (%)")
    ax.legend(handles=fam_handles(js, names, INK), loc="upper left", ncol=3, fontsize=5.8,
              handletextpad=0.2, columnspacing=0.8, borderaxespad=0.1)
    save(fig, "fig_knowledge_vs_safety.pdf")


# --------------------------------------------------------------------------- 7
def fig_paired():
    ex = json.loads((C.RESULTS_DIR / "paired_analysis.json").read_text())["exact"]
    rows = [("Did not know the control (K=0)", ex["p_s_k0"], ex["ci_k0"], ex["n_k0"], ex["c"]),
            ("Knew the control (K=1)", ex["p_s_k1"], ex["ci_k1"], ex["n_k1"], ex["a"])]
    fig, ax = plt.subplots(figsize=(COL, 1.15))
    xgrid(ax)
    for i, (lab, p, (lo, hi), n, k) in enumerate(rows[::-1]):
        ax.plot([lo * 100, hi * 100], [i, i], color=REFUSE, lw=1.4, alpha=0.55,
                solid_capstyle="butt")
        ax.scatter(p * 100, i, s=26, color=REFUSE, ec="white", lw=0.5, zorder=3)
        ax.text(hi * 100 + 1.5, i, f"{p*100:.1f}%  ({k} of {n} pairs)", va="center",
                fontsize=6.0, color=INK2)
    ax.set_yticks([0, 1]); ax.set_yticklabels([r[0] for r in rows[::-1]])
    ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.6, 1.6); ax.set_xlim(0, 80); ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("Safe-refusal rate on the matched misuse item (%)")
    save(fig, "fig_paired.pdf")


# --------------------------------------------------------------------------- 8
def fig_family_heatmap(js, names):
    fams = ["AC", "IA", "AU", "EN", "DI", "BK", "CV", "SM"]
    M = np.full((len(names), len(fams)), np.nan)
    for i, n in enumerate(names):
        for full, v in js[n]["acc_by_family"].items():
            M[i, fams.index(FAM_CODE[full])] = v * 100
    fig, ax = plt.subplots(figsize=(COL, 2.45))
    im = ax.imshow(M, aspect="auto", cmap=SEQ, vmin=0, vmax=100)
    ax.set_xticks(range(len(fams))); ax.set_xticklabels(fams)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
    ax.tick_params(length=0); ax.xaxis.tick_top()
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(fams)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(names)), minor=True)
    ax.grid(which="minor", color="white", lw=0.8); ax.tick_params(which="minor", length=0)
    for i in range(len(names)):
        for j in range(len(fams)):
            if not math.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=5.6,
                        color="white" if M[i, j] >= 60 else INK)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, ticks=[0, 50, 100])
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=5.8, length=2, width=0.5)
    cb.set_label("Knowledge accuracy (%)", fontsize=6.2)
    save(fig, "fig_family_heatmap.pdf")


# --------------------------------------------------------------------------- 9
def fig_confusion():
    labels = ["REFUSE", "AMBIGUOUS", "COMPLY"]
    disp = ["Refuse", "Ambiguous", "Comply"]
    M = np.zeros((3, 3), int)
    for l in (C.RESULTS_DIR / "validation_judgments.jsonl").read_text().splitlines():
        if l.strip():
            d = json.loads(l)
            if d["task_type"] == "misuse":
                M[labels.index(d["rule_label"]), labels.index(d["judge_label"])] += 1
    fig, ax = plt.subplots(figsize=(2.45, 1.75))
    ax.imshow(M, cmap=SEQ, vmin=0, vmax=M.max())
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=6.8,
                    color="white" if M[i, j] > 0.55 * M.max() else INK,
                    fontweight="bold" if i == j and M[i, j] else "normal")
    ax.set_xticks(range(3)); ax.set_xticklabels(disp)
    ax.set_yticks(range(3)); ax.set_yticklabels([f"{d}  ({M[i].sum()})" for i, d in enumerate(disp)])
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, 3), minor=True); ax.set_yticks(np.arange(-0.5, 3), minor=True)
    ax.grid(which="minor", color="white", lw=1.0); ax.tick_params(which="minor", length=0)
    ax.set_xlabel(f"LLM judge (n = {M.sum()})", labelpad=4)
    ax.set_ylabel("Deterministic scorer")
    save(fig, "fig_confusion.pdf")


def main():
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    js, names = load_summary()
    fig_pipeline()
    fig_acc_by_size(js, names)
    fig_framework_dot(js, names)
    fig_guardrail_stack(js, names)
    fig_forest(js, names)
    fig_knowledge_vs_safety(js, names)
    fig_paired()
    fig_family_heatmap(js, names)
    fig_confusion()
    print("wrote 9 figures to", C.FIG_DIR)


if __name__ == "__main__":
    main()
