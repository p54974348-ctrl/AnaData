# AnaData — Routine quotidienne « CAC 40 J+1 »

Suivi quotidien d'un exercice de prévision du rendement J+1 de l'indice CAC 40 (PX1 / ^FCHI, Euronext Paris), avec journalisation des hypothèses, attribution des erreurs (corrigeable vs irréductible) et métriques cumulées contre la prévision naïve (rendement 0 %).

## Structure

- `ROUTINE.md` — le prompt complet de la routine (à coller chaque soir de bourse dans une nouvelle conversation, avec le dernier bloc état).
- `etat/BLOC_ETAT.json` — dernier bloc état (prévision en cours + métriques cumulées + leçons). C'est le fichier à recopier en fin de prompt lors de la prochaine exécution.
- `rapports/AAAA-MM-JJ.md` — rapport quotidien de chaque exécution.

## Avertissement

Exercice d'analyse et de suivi de modèle uniquement. Aucune recommandation d'achat, de vente ou de prise de position.
