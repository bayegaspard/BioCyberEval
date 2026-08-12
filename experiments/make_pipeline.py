"""Generate figures/fig_pipeline.pdf: the benchmark-construction and evaluation
flow (Fig. 1), styled as a clean flowchart with rounded colored boxes, bold
titles, a three-way fork for the item transformations, and crisp arrows."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import config as C

plt.rcParams.update({"font.family": "DejaVu Sans"})

# fill / edge color pairs
BLUE  = ("#d4e4f4", "#2f6094")
GREEN = ("#d9ecd9", "#4a8a4a")
PINK  = ("#f7d9dd", "#b0505b")
GREY  = ("#ededed", "#8f8f8f")

fig, ax = plt.subplots(figsize=(5.6, 8.0))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(cx, cy, w, h, title, subs, colors, tsize=11, ssize=8.6):
    fill, edge = colors
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.6,rounding_size=1.4",
                 linewidth=1.2, edgecolor=edge, facecolor=fill, mutation_aspect=1))
    lines = len(subs)
    ty = cy + (h / 2) - (h / (lines + 2)) * 0.95
    ax.text(cx, ty, title, ha="center", va="center", fontsize=tsize, fontweight="bold", color="#111")
    for i, s in enumerate(subs):
        sy = ty - (h / (lines + 2)) * (i + 1)
        ax.text(cx, sy, s, ha="center", va="center", fontsize=ssize, color="#222")

def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                 mutation_scale=15, linewidth=1.4, color="#333", shrinkA=0, shrinkB=0))

FW = 92  # full width
# ---- stacked top boxes ----
box(50, 94, FW, 9, "Primary regulatory sources",
    ["(HIPAA Security Rule, 21 CFR Part 11, EU GMP Annex 11)"], BLUE)
arrow(50, 89.5, 50, 87.5)
box(50, 83, FW, 9, "Clause extraction and verification",
    ["against primary text"], BLUE)
arrow(50, 78.5, 50, 76.5)
box(50, 72, FW, 9, "Normalized control catalog",
    ["8 families: AC IA AU EN DI BK CV SM"], BLUE)

# ---- fork to three transformations ----
ax.text(50, 65.5, "Three item transformations", ha="center", va="center",
        fontsize=9.5, style="italic", color="#333")
xk, xm, xb = 19, 50, 81
ax.plot([50, 50], [67.5, 63.2], color="#333", lw=1.4)
ax.plot([xk, xb], [63.2, 63.2], color="#333", lw=1.4)
for x in (xk, xm, xb):
    arrow(x, 63.2, x, 60.2)
box(xk, 55.5, 28, 9, "Knowledge", ["MCQ (72)"], GREEN)
box(xm, 55.5, 28, 9, "Misuse", ["refuse (36)"], PINK)
box(xb, 55.5, 28, 9, "Benign", ["support (18)"], GREEN)

# ---- converge to inference ----
for x in (xk, xm, xb):
    arrow(x, 51, x, 48)
box(50, 42.5, FW, 10, "Model inference",
    ["10 open-weight LLMs (1.2 to 20.9B, 6 families)", "temperature 0, fixed seed"], GREY)
arrow(50, 37.5, 50, 35.5)
box(50, 30, FW, 10, "Scoring",
    ["deterministic: knowledge + misuse", "judge-based: benign correctness"], GREY)
arrow(50, 25, 50, 23)
box(50, 17.5, FW, 10, "Scorer cross-check",
    ["full-coverage LLM-judge assessment", "confusion matrix, precision/recall/F1"], BLUE)
arrow(50, 12.5, 50, 10.5)
box(50, 5, FW, 10, "Metrics and analysis",
    ["Wilson CIs, forest plot,", "control-level paired K vs U analysis"], GREEN)

fig.savefig(C.FIG_DIR / "fig_pipeline.pdf", bbox_inches="tight", pad_inches=0.05)
print("wrote fig_pipeline.pdf")
