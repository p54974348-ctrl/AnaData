# AnaData — Routine quotidienne « CAC 40 J+1 »

Suivi quotidien d'un exercice de prévision du rendement J+1 de l'indice CAC 40 (PX1 / ^FCHI, Euronext Paris), avec journalisation des hypothèses, attribution des erreurs (corrigeable vs irréductible) et métriques cumulées contre la prévision naïve (rendement 0 %).

## Structure

- `ROUTINE.md` — le prompt complet de la routine (à coller chaque soir de bourse dans une nouvelle conversation, avec le dernier bloc état).
- `etat/BLOC_ETAT.json` — dernier bloc état (prévision en cours + métriques cumulées + leçons). C'est le fichier à recopier en fin de prompt lors de la prochaine exécution.
- `rapports/AAAA-MM-JJ.md` — rapport quotidien de chaque exécution.
- `INDICES.md` — fiche de référence des 8 indices suivis (cible `^FCHI` + 7 compagnons : `^GSPC`, `^VIX`, `^IXIC`, `^GDAXI`, `^STOXX50E`, `^N225`, `^HSI`) et leur rôle dans la routine.
- `docs/` — tableau de bord GitHub Pages (graphiques prévision vs réalisé, métriques, leçons), alimenté par `docs/data/history.json`. Déployé automatiquement à chaque push sur `master` via `.github/workflows/pages.yml`.

## Tableau de bord

La GitHub Page publie `docs/index.html` : rendement réalisé vs intervalle 80 % prévu, courbe de clôture, rendements quotidiens, hit rate cumulé vs 50 %, MAE modèle vs naïf, leçons et vue table. Chaque exécution quotidienne de la routine doit mettre à jour `docs/data/history.json` (nouveau record de séance, verdict de la prévision de la veille, métriques cumulées, prévision active).

## Déclenchement automatique

La routine est intégrée comme la routine « Veille IA » : une **Routine Claude planifiée** (trigger `Routine CAC 40 J+1 quotidienne`, cron `15 21 * * 1-5` UTC) reprend chaque soir de semaine la session Claude liée à ce dépôt, après la mise à disposition de la dernière donnée du jour (clôture US à 22h00 Paris ; Europe 17h35 ; Asie en journée). Elle exécute la routine complète (collecte web, évaluation, prévision, règles de suivi dynamique ±2 %), committe directement sur `master` avec vérification du push (et repli API GitHub en secours), ce qui redéploie le tableau de bord.

`.github/workflows/routine.yml` est conservé uniquement comme **secours manuel** (Actions → Run workflow ; nécessite le secret `ANTHROPIC_API_KEY`) — sa planification est désactivée pour éviter les doubles exécutions.

## Avertissement

Exercice d'analyse et de suivi de modèle uniquement. Aucune recommandation d'achat, de vente ou de prise de position.
