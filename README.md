# AnaData — Routine quotidienne « CAC 40 J+1 »

Suivi quotidien d'un exercice de prévision du rendement J+1 de l'indice CAC 40 (PX1 / ^FCHI, Euronext Paris), avec journalisation des hypothèses, attribution des erreurs (corrigeable vs irréductible) et métriques cumulées contre la prévision naïve (rendement 0 %).

## Structure

- `ROUTINE.md` — le prompt complet de la routine (à coller chaque soir de bourse dans une nouvelle conversation, avec le dernier bloc état).
- `etat/BLOC_ETAT.json` — dernier bloc état (prévision en cours + métriques cumulées + leçons). C'est le fichier à recopier en fin de prompt lors de la prochaine exécution.
- `rapports/AAAA-MM-JJ.md` — rapport quotidien de chaque exécution.
- `docs/` — tableau de bord GitHub Pages (graphiques prévision vs réalisé, métriques, leçons), alimenté par `docs/data/history.json`. Déployé automatiquement à chaque push sur `master` via `.github/workflows/pages.yml`.

## Tableau de bord

La GitHub Page publie `docs/index.html` : rendement réalisé vs intervalle 80 % prévu, courbe de clôture, rendements quotidiens, hit rate cumulé vs 50 %, MAE modèle vs naïf, leçons et vue table. Chaque exécution quotidienne de la routine doit mettre à jour `docs/data/history.json` (nouveau record de séance, verdict de la prévision de la veille, métriques cumulées, prévision active).

## Avertissement

Exercice d'analyse et de suivi de modèle uniquement. Aucune recommandation d'achat, de vente ou de prise de position.
