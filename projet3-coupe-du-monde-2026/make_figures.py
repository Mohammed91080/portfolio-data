"""Graphiques du projet, aux couleurs du portfolio (fond bleu nuit)."""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.stats import poisson

BG, PANEL, FG, MUTED = "#0B1220", "#121F38", "#E7EDF7", "#92A1B9"
BLUE, BLUE2, AMBER = "#1A56DB", "#3B82F6", "#F59E0B"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": "#24324d", "font.size": 11,
})

# ---- 1. Probabilités de titre (top 15) ----
odds = pd.read_csv("figures/title_odds.csv").head(15).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 6.2))
colors = [AMBER if i == len(odds) - 1 else BLUE2 for i in range(len(odds))]
ax.barh(odds["equipe"], odds["proba_titre"] * 100, color=colors, edgecolor="none")
for y, v in enumerate(odds["proba_titre"] * 100):
    ax.text(v + 0.3, y, f"{v:.1f}%", va="center", color=FG, fontsize=10)
ax.set_title("Coupe du Monde 2026 — probabilité de titre (simulation Monte Carlo)",
             color=FG, fontsize=13, fontweight="bold", pad=14, loc="left")
ax.set_xlabel("Probabilité de remporter le tournoi (%)")
ax.spines[["top", "right"]].set_visible(False)
ax.margins(x=0.08)
fig.tight_layout()
fig.savefig("figures/title_odds.png", dpi=150)
print("figures/title_odds.png")

# ---- 2. Carte de chaleur des scores France - Maroc ----
with open("figures/model_export.json", encoding="utf-8") as f:
    exp = json.load(f)
m = exp["model"]
elo = {t["name"]: t["elo"] for t in exp["teams"]}
def lam(d):
    return np.exp(m["const"] + m["elo_diff"] * d)
lf, lm_ = lam(elo["France"] - elo["Morocco"]), lam(elo["Morocco"] - elo["France"])
N = 6
P = np.outer(poisson.pmf(np.arange(N), lf), poisson.pmf(np.arange(N), lm_)) * 100

fig, ax = plt.subplots(figsize=(7.2, 6))
im = ax.imshow(P, cmap="magma", origin="lower")
for i in range(N):
    for j in range(N):
        ax.text(j, i, f"{P[i, j]:.1f}", ha="center", va="center",
                color="white" if P[i, j] < P.max() * 0.6 else "black", fontsize=9)
ax.set_xticks(range(N)); ax.set_yticks(range(N))
ax.set_xlabel("Buts Maroc"); ax.set_ylabel("Buts France")
ax.set_title("Probabilité de chaque score (%) — France vs Maroc, terrain neutre",
             color=FG, fontsize=12, fontweight="bold", pad=12, loc="left")
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.ax.tick_params(colors=MUTED)
fig.tight_layout()
fig.savefig("figures/score_heatmap_fr_ma.png", dpi=150)
print("figures/score_heatmap_fr_ma.png")
