"""
Simulateur de la Coupe du Monde 2026
====================================

Pipeline complet, 100 % reproductible :

1.  Données réelles : ~50 000 matchs internationaux (1872 -> 2026, dataset martj42).
2.  Notes Elo calculées match après match sur tout l'historique
    (avantage du terrain + amplitude du score).
3.  Modèle de buts de Poisson : les buts marqués par une équipe sont ajustés
    par régression de Poisson sur l'écart d'Elo et le facteur "à domicile".
4.  Simulation de match : tirage des scores -> probabilités Victoire / Nul / Défaite.
5.  Monte Carlo du tournoi au format Coupe du Monde 2026
    (48 équipes, 12 groupes de 4, 32 qualifiés, élimination directe)
    -> probabilité de titre de chaque équipe.

Auteur : Mohammed Zahi — portfolio data.
"""

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

RNG = np.random.default_rng(42)

# --------------------------------------------------------------------------- #
# 1. Données
# --------------------------------------------------------------------------- #
DATA_URL = ("https://raw.githubusercontent.com/martj42/"
            "international_results/master/results.csv")


def load_matches(path="data/results.csv"):
    import os, urllib.request
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print("   téléchargement du jeu de données…")
        urllib.request.urlretrieve(DATA_URL, path)
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.dropna(subset=["home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = df["neutral"].astype(str).str.upper().eq("TRUE")
    return df.sort_values("date").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 2. Notes Elo
# --------------------------------------------------------------------------- #
def compute_elo(df, base=1500.0, K=30.0, home_adv=70.0):
    """Elo façon 'World Football Elo' : K pondéré par l'amplitude du score.
    Renvoie les notes finales + les notes AVANT chaque match (pour la régression)."""
    elo = {}
    pre_home = np.empty(len(df))
    pre_away = np.empty(len(df))
    for i, r in enumerate(df.itertuples(index=False)):
        h, a = r.home_team, r.away_team
        eh = elo.get(h, base)
        ea = elo.get(a, base)
        pre_home[i], pre_away[i] = eh, ea
        adv = 0.0 if r.neutral else home_adv
        exp_h = 1.0 / (1.0 + 10 ** (-((eh + adv) - ea) / 400.0))
        gd = abs(r.home_score - r.away_score)
        g = 1.0 if gd <= 1 else (1.5 if gd == 2 else (11 + gd) / 8.0)  # amplitude
        res_h = 1.0 if r.home_score > r.away_score else (0.5 if r.home_score == r.away_score else 0.0)
        delta = K * g * (res_h - exp_h)
        elo[h] = eh + delta
        elo[a] = ea - delta
    df = df.copy()
    df["elo_home_pre"] = pre_home
    df["elo_away_pre"] = pre_away
    return elo, df


# --------------------------------------------------------------------------- #
# 3. Modèle de buts (Poisson)
# --------------------------------------------------------------------------- #
def fit_goal_model(df, since="2006-01-01"):
    """Régression de Poisson : buts ~ écart d'Elo + à domicile.
    Chaque match donne deux lignes (une par équipe)."""
    d = df[df["date"] >= since].copy()
    home = pd.DataFrame({
        "goals": d["home_score"].values,
        "elo_diff": (d["elo_home_pre"] - d["elo_away_pre"]).values,
        "is_home": np.where(d["neutral"].values, 0.0, 1.0),
    })
    away = pd.DataFrame({
        "goals": d["away_score"].values,
        "elo_diff": (d["elo_away_pre"] - d["elo_home_pre"]).values,
        "is_home": 0.0,  # l'équipe à l'extérieur ne bénéficie jamais du terrain
    })
    long = pd.concat([home, away], ignore_index=True)
    X = sm.add_constant(long[["elo_diff", "is_home"]])
    model = sm.GLM(long["goals"], X, family=sm.families.Poisson()).fit()
    return model


def lam(model, elo_diff, is_home=0.0):
    b = model.params
    return float(np.exp(b["const"] + b["elo_diff"] * elo_diff + b["is_home"] * is_home))


# --------------------------------------------------------------------------- #
# 4. Simulation d'un match
# --------------------------------------------------------------------------- #
def match_probabilities(model, elo_a, elo_b, n=200_000):
    """Probabilités V/N/D de A contre B (terrain neutre) par tirage de Poisson."""
    la = lam(model, elo_a - elo_b)
    lb = lam(model, elo_b - elo_a)
    ga = RNG.poisson(la, n)
    gb = RNG.poisson(lb, n)
    return (np.mean(ga > gb), np.mean(ga == gb), np.mean(ga < gb), la, lb)


# --------------------------------------------------------------------------- #
# 5. Monte Carlo du tournoi (format Coupe du Monde 2026)
# --------------------------------------------------------------------------- #
def build_field(elo, n=48):
    """Les 48 meilleures sélections par Elo (proxy transparent des 48 qualifiées)."""
    ranked = sorted(elo.items(), key=lambda kv: kv[1], reverse=True)[:n]
    teams = [t for t, _ in ranked]
    ratings = np.array([elo[t] for t in teams])
    return teams, ratings


def precompute_lambdas(model, ratings):
    """Matrice n x n des buts attendus (terrain neutre) : LAM[i, j] = buts de i contre j."""
    n = len(ratings)
    diff = ratings[:, None] - ratings[None, :]
    b = model.params
    return np.exp(b["const"] + b["elo_diff"] * diff)  # is_home = 0 (neutre)


def sim_match(LAM, i, j):
    return RNG.poisson(LAM[i, j]), RNG.poisson(LAM[j, i])


def sim_knockout(LAM, i, j, ratings):
    gi, gj = sim_match(LAM, i, j)
    if gi > gj:
        return i
    if gj > gi:
        return j
    # tirs au but : léger avantage à la meilleure équipe (via Elo)
    p = 1.0 / (1.0 + 10 ** (-(ratings[i] - ratings[j]) / 400.0))
    return i if RNG.random() < p else j


def draw_groups(n=48, pots=4, rng=RNG):
    """12 groupes de 4 : un tirage par pot (équipes déjà classées par Elo)."""
    g = 12
    per_pot = n // pots  # 12
    groups = [[] for _ in range(g)]
    for p in range(pots):
        pot = list(range(p * per_pot, (p + 1) * per_pot))
        rng.shuffle(pot)
        for gi in range(g):
            groups[gi].append(pot[gi])
    return groups


def sim_tournament(LAM, ratings):
    groups = draw_groups(len(ratings))
    pts = {}
    gf = {}
    ga = {}
    for gr in groups:
        for t in gr:
            pts[t] = gf[t] = ga[t] = 0
        for a_i in range(4):
            for b_i in range(a_i + 1, 4):
                i, j = gr[a_i], gr[b_i]
                gi, gj = sim_match(LAM, i, j)
                gf[i] += gi; ga[i] += gj; gf[j] += gj; ga[j] += gi
                if gi > gj:
                    pts[i] += 3
                elif gj > gi:
                    pts[j] += 3
                else:
                    pts[i] += 1; pts[j] += 1

    def rank(team):
        return (pts[team], gf[team] - ga[team], gf[team], RNG.random())

    qualified, thirds = [], []
    for gr in groups:
        ordered = sorted(gr, key=rank, reverse=True)
        qualified += ordered[:2]
        thirds.append(ordered[2])
    thirds = sorted(thirds, key=rank, reverse=True)[:8]
    bracket = qualified + thirds            # 32 équipes
    RNG.shuffle(bracket)                    # appariement neutre
    while len(bracket) > 1:
        bracket = [sim_knockout(LAM, bracket[k], bracket[k + 1], ratings)
                   for k in range(0, len(bracket), 2)]
    return bracket[0]


def monte_carlo(LAM, ratings, teams, n_sim=5000):
    titles = np.zeros(len(teams))
    for _ in range(n_sim):
        titles[sim_tournament(LAM, ratings)] += 1
    return pd.DataFrame({"equipe": teams, "elo": ratings.round(0),
                         "proba_titre": titles / n_sim}).sort_values(
                         "proba_titre", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Programme principal
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print(">> Chargement des données…")
    df = load_matches()
    print(f"   {len(df):,} matchs de {df.date.min().date()} à {df.date.max().date()}")

    print(">> Calcul des notes Elo…")
    elo, df = compute_elo(df)

    print(">> Ajustement du modèle de buts (Poisson)…")
    model = fit_goal_model(df)
    print(model.params.to_string())

    teams, ratings = build_field(elo, 48)
    print("\n>> Top 10 des équipes par Elo :")
    for t in teams[:10]:
        print(f"   {t:<22} {elo[t]:6.0f}")

    LAM = precompute_lambdas(model, ratings)

    print("\n>> Exemple — France vs Maroc (terrain neutre) :")
    pf, pn, pm, lf, lm_ = match_probabilities(model, elo["France"], elo["Morocco"])
    print(f"   Victoire France {pf:5.1%} | Nul {pn:5.1%} | Victoire Maroc {pm:5.1%}")
    print(f"   buts attendus : France {lf:.2f} - {lm_:.2f} Maroc")

    print("\n>> Simulation Monte Carlo du tournoi (5 000 éditions)…")
    odds = monte_carlo(LAM, ratings, teams, n_sim=5000)
    print(odds.head(15).to_string(index=False))

    # Exports
    odds.to_csv("figures/title_odds.csv", index=False)
    export = {
        "generated": str(pd.Timestamp.now().date()),
        "model": {"const": float(model.params["const"]),
                   "elo_diff": float(model.params["elo_diff"]),
                   "is_home": float(model.params["is_home"])},
        "teams": [{"name": t, "elo": round(float(elo[t]), 1)} for t in teams],
        "title_odds": [{"name": r.equipe, "p": round(float(r.proba_titre), 4)}
                        for r in odds.itertuples(index=False)],
    }
    with open("figures/model_export.json", "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)
    print("\n>> Exports écrits dans figures/ (title_odds.csv, model_export.json)")
