# AnaData — Routine quotidienne « CAC 40 J+1 »

Suivi quotidien d'un exercice de prévision du rendement J+1 de l'indice CAC 40 (PX1 / ^FCHI, Euronext Paris), avec journalisation des hypothèses, attribution des erreurs (corrigeable vs irréductible) et métriques cumulées contre la prévision naïve (rendement 0 %).

## Structure

- `ROUTINE.md` — le prompt complet de la routine (référence normative ; pour une exécution manuelle hors dépôt, recopier le BLOC ÉTAT du dernier compte rendu).
- `rapports/AAAA-MM-JJ.md` — rapport quotidien de chaque exécution (trace auditable).
- `INDICES.md` — fiche de référence des 8 indices suivis (cible `^FCHI` + 7 compagnons : `^GSPC`, `^VIX`, `^IXIC`, `^GDAXI`, `^STOXX50E`, `^N225`, `^HSI`) et leur rôle dans la routine.
- `docs/` — tableau de bord GitHub Pages (graphiques prévision vs réalisé, métriques, leçons), alimenté par `docs/data/history.json` — **source unique de l'état de la routine** (records quotidiens, prévision active, métriques cumulées, suivi dynamique, leçons). Déployé automatiquement à chaque push sur `master` via `.github/workflows/pages.yml`.

## Tableau de bord

La GitHub Page publie `docs/index.html` : rendement réalisé vs intervalle 80 % prévu, courbe de clôture, rendements quotidiens, hit rate cumulé vs 50 %, MAE modèle vs naïf, leçons et vue table. Chaque exécution quotidienne de la routine doit mettre à jour `docs/data/history.json` (nouveau record de séance, verdict de la prévision de la veille, métriques cumulées, prévision active).

## Déclenchement automatique

La routine est intégrée comme la routine « Veille IA », via deux **Routines Claude planifiées** (jours de semaine, heures calées sur la mise à disposition des valeurs) :

| Trigger | Heure (UTC) | Rôle |
|---|---|---|
| Instantané européen | `48 16 * * 1-5` (après la clôture Euronext de 17h35 Paris) | Rafraîchit `docs/data/history.json` avec les clôtures définitives Europe/Asie et le contexte US « en séance ». Aucune prévision, aucune évaluation, aucun mouvement du suivi dynamique. |
| Routine complète J+1 | `15 21 * * 1-5` (après la clôture US de 22h00 Paris) | Complète le record du jour (US définitif), évalue la prévision de la veille, met à jour métriques/leçons/suivi dynamique, émet la prévision J+1, écrit le rapport. |

Chaque trigger committe directement sur `master` avec vérification du push (repli API GitHub en secours), ce qui redéploie le tableau de bord. Le record quotidien est unique : l'instantané le crée, la routine du soir le complète (jamais de doublon).

En cas d'exécution manquée, relancer la routine à la main : demander l'exécution dans la session Claude liée au dépôt, ou coller `ROUTINE.md` + le dernier BLOC ÉTAT dans une nouvelle conversation.

## Avertissement

Exercice d'analyse et de suivi de modèle uniquement. Aucune recommandation d'achat, de vente ou de prise de position.
