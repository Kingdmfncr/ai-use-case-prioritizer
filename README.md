# 🧠 AI Use Case Prioritizer

**Framework de priorisation des projets IA pour équipes Produit & Data**

> Construit avec l'IA — Portfolio Gisèle Metouck

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-use-case-prioritizer.streamlit.app)

---

## Pourquoi cet outil ?

Chaque équipe Produit ou Data fait face au même problème : trop d'idées IA, pas assez de ressources. Sans méthode, les projets sont choisis par intuition ou politique interne — pas par valeur réelle.

Cet outil applique un scoring composite sur 5 dimensions pour objectiver la décision et identifier les Quick Wins, Strategic Bets, Fill-ins et projets à déprioritiser.

---

## Fonctionnalités

| Onglet | Ce qu'il fait |
|--------|---------------|
| **Cas d'Usage** | Saisir, modifier, supprimer des cas d'usage avec 5 critères de scoring |
| **Matrice** | Bubble chart Impact × Faisabilité avec quadrants automatiques |
| **Classement** | Ranking pondéré + profil radar par cas d'usage |
| **Simulation** | Comparaison de 4 profils de pondération (ROI, rapidité, sécurité…) |
| **Rapport & IA** | Narrative exécutive (Claude Haiku) + export PDF |

---

## Modèle de scoring

```
Score = Σ (dimension × poids) / Σ poids
```

| Dimension | Poids défaut | Description |
|-----------|-------------|-------------|
| Impact Business | 30% | Potentiel de revenus / réduction de coûts |
| Faisabilité Technique | 25% | Qualité des données + maturité engineering |
| Délai de Valeur | 20% | Temps avant le premier résultat mesurable |
| Alignement Stratégique | 15% | Cohérence avec les OKRs de l'entreprise |
| Risque & Conformité | 10% | RGPD, éthique IA, risques opérationnels |

Poids configurables via la sidebar.

---

## Quadrants de priorisation

| Quadrant | Critère | Action |
|----------|---------|--------|
| 🟢 **Quick Win** | Impact ≥ 6 + Faisabilité ≥ 6 | Lancer immédiatement |
| 🟡 **Strategic Bet** | Impact ≥ 6 + Faisabilité < 6 | Planifier à 12-18 mois |
| 🔵 **Fill-in** | Impact < 6 + Faisabilité ≥ 6 | Pipeline secondaire |
| 🔴 **Questionable** | Impact < 6 + Faisabilité < 6 | Déprioritiser |

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Interface | Streamlit |
| Visualisations | Plotly (bubble, radar, grouped bar) |
| IA narrative | Anthropic Claude Haiku (BYOK) |
| Export | fpdf2 |
| Design | Premium Dark (design system portfolio) |

---

## Données pré-chargées

8 cas d'usage secteur Luxe/Mode/Beauté :
- Chatbot SAV personnalisé
- Prédiction tendances mode (Computer Vision)
- Moteur de recommandation produit
- Détection fraude e-commerce
- Optimisation inventaire prédictive
- Personnalisation email marketing
- Analyse sentiment réseaux sociaux
- Virtual Try-On (AR)

Chargez vos propres cas d'usage ou modifiez les existants.

---

## Déploiement

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Clé API Anthropic :** BYOK (Bring Your Own Key) — saisie en sidebar, jamais stockée.

---

*Construit avec l'IA — Gisèle Metouck | Data Analyst & IA Builder*
