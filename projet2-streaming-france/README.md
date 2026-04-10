# Analyse du marché du streaming vidéo en France (2019–2024)

**Auteur** : Mohammed Zahi — M1 MASERATI, Université Paris-Est Créteil (UPEC)  
**Contact** : z.mohammed91080@gmail.com · [Malt](https://www.malt.fr/profile/mohammedzahi)

---

## Contexte business

Ce projet adopte la posture d'un **Data Analyst au sein d'une Direction Marketing** qui analyse le marché du streaming vidéo français — Netflix, Canal+, Disney+, Amazon Prime, Apple TV+, OCS — pour produire des insights actionnables sur la rétention, les parts de marché et la valeur client.

---

## Compétences démontrées

| Compétence | Détail |
|---|---|
| API REST | TMDB (The Movie Database) — catalogues, genres, popularité |
| Business Analytics | Parts de marché, revenus, croissance YoY |
| Analyse catalogue | Genres, notes, popularité — identification des contenus performants |
| Modélisation churn | Régression logistique · AUC-ROC · Courbe ROC |
| Segmentation CRM | 3 segments de risque · valeur client à risque |
| Recommandations | Insights opérationnels structurés pour une Direction Marketing |

---

## Structure du projet

```
projet2-streaming-france/
├── notebook.ipynb       ← Analyse complète
├── README.md            ← Ce fichier
└── requirements.txt     ← Packages nécessaires
```

---

## Données utilisées

| Source | Type | Accès |
|---|---|---|
| **API TMDB** | Catalogues films/séries, genres, notes | Gratuite — [themoviedb.org](https://www.themoviedb.org/settings/api) |
| **ARCOM / IDATE** | Abonnés, revenus (simulés sur base publique) | Rapports publics |

> Les données d'abonnés sont simulées à partir des rapports publics ARCOM 2023 et IDATE DigiWorld 2024. Les ordres de grandeur et tendances reflètent la réalité du marché français.

---

## Configuration API TMDB

1. Créer un compte gratuit sur [themoviedb.org](https://www.themoviedb.org)
2. Aller dans Settings → API → Request an API key
3. Remplacer `VOTRE_CLE_API_TMDB_ICI` dans la cellule 1 du notebook
4. Le notebook fonctionne aussi sans clé (mode démonstration automatique)

---

## Résultats principaux

- **Netflix** domine avec 32% de part de marché en 2024, mais **Canal+** génère le plus de revenus grâce à son prix élevé
- Le **churn** est fortement prédit par le NPS, le nombre de pauses passées et le faible usage
- Le modèle logistique atteint un **AUC > 0.75**, permettant de cibler les abonnés à risque élevé
- **~25% des abonnés** sont en risque élevé de churn, représentant une valeur mensuelle significative à protéger

---

## Installation

```bash
pip install -r requirements.txt
```

Puis ouvrir `notebook.ipynb` dans Jupyter Lab ou Google Colab.

---

## Références

- ARCOM — Baromètre audiovisuel et numérique 2023
- IDATE DigiWorld — Marché du streaming France 2024
- TMDB API Documentation — themoviedb.org
