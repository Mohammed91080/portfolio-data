# Inégalités de revenus et croissance économique — Pays OCDE (1990–2022)

**Auteur** : Mohammed Zahi — M1 MASERATI, Université Paris-Est Créteil (UPEC)  
**Contact** : z.mohammed91080@gmail.com · [Malt](https://www.malt.fr/profile/mohammedzahi)

---

## Question de recherche

> **Les inégalités de revenus freinent-elles la croissance économique dans les pays de l'OCDE ?**

Ce projet s'inscrit dans la littérature économique fondée sur les travaux d'**Ostry, Berg & Tsangarides (2014, FMI)** et d'**Aghion et al. (1999)**, qui montrent que les inégalités élevées peuvent réduire la croissance de long terme.

---

## Compétences démontrées

| Compétence | Détail |
|---|---|
| Collecte de données | API Banque Mondiale (World Development Indicators) |
| Manipulation | `pandas` — construction d'une base panel (pays × années) |
| Visualisation | `matplotlib` + `seaborn` — 4 figures publication-ready |
| Économétrie | OLS poolé, Effets fixes pays + temps, Diff-in-Diff |
| Tests de robustesse | 3 sous-échantillons (sans COVID, sans crise, Europe) |

---

## Structure du projet

```
projet1-ocde-inegalites/
├── notebook.ipynb       ← Analyse complète (code + résultats + commentaires)
├── README.md            ← Ce fichier
└── requirements.txt     ← Packages nécessaires
```

---

## Données

Toutes les données sont téléchargées automatiquement via l'**API Banque Mondiale** (gratuite, sans clé). Aucun fichier externe n'est nécessaire.

| Indicateur | Code WDI | Rôle |
|---|---|---|
| Croissance PIB/hab. (%) | NY.GDP.PCAP.KD.ZG | Variable dépendante |
| Indice de Gini | SI.POV.GINI | Variable d'intérêt |
| PIB/hab. initial | NY.GDP.PCAP.KD | Contrôle — convergence |
| Investissement (% PIB) | NE.GDI.TOTL.ZS | Contrôle — capital |
| Ouverture commerciale | NE.TRD.GNFS.ZS | Contrôle — intégration |
| Éducation (% PIB) | SE.XPD.TOTL.GD.ZS | Contrôle — capital humain |

**Couverture** : 37 pays OCDE · 1990–2022

---

## Modèles estimés

1. **OLS Poolé** — référence naïve
2. **Effets Fixes Pays** — contrôle hétérogénéité inobservée
3. **Effets Fixes Pays + Temps** — modèle de référence
4. **Diff-in-Diff** — effet causal d'une baisse des inégalités post-2008

---

## Installation

```bash
pip install -r requirements.txt
```

Puis ouvrir `notebook.ipynb` dans Jupyter Lab ou Google Colab.

---

## Résultats principaux

Le coefficient du Gini dans le modèle à effets fixes pays + temps est **négatif et significatif**, confirmant l'hypothèse d'un effet négatif des inégalités sur la croissance dans les pays OCDE — résultat robuste à 3 spécifications alternatives.

---

## Références

- Ostry, Berg & Tsangarides (2014) — *Redistribution, Inequality, and Growth*, FMI
- Aghion, Caroli & García-Peñalosa (1999) — *Inequality and Economic Growth*, JEL
- Acemoglu & Robinson (2002) — *The Political Economy of the Kuznets Curve*, RDE
