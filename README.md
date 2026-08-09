# AnaData — Routine quotidienne « CAC 40 J+1 »

Suivi quotidien d'un exercice de prévision du rendement J+1 de l'indice CAC 40 (PX1 / ^FCHI, Euronext Paris), avec journalisation des hypothèses, attribution des erreurs (corrigeable vs irréductible) et métriques cumulées contre la prévision naïve (rendement 0 %).

## Structure

- `ROUTINE.md` — le prompt complet de la routine (référence normative ; pour une exécution manuelle hors dépôt, recopier le BLOC ÉTAT du dernier compte rendu).
- `rapports/AAAA-MM-JJ.md` — rapport quotidien de chaque exécution (trace auditable).
- `INDICES.md` — fiche de référence des 8 indices suivis (cible `^FCHI` + 7 compagnons : `^GSPC`, `^VIX`, `^IXIC`, `^GDAXI`, `^STOXX50E`, `^N225`, `^HSI`) et leur rôle dans la routine.
- `docs/` — tableau de bord GitHub Pages (graphiques prévision vs réalisé, métriques, leçons), alimenté par `docs/data/history.json` — **source unique de l'état de la routine** (records quotidiens, prévision active, métriques cumulées, suivi dynamique, leçons). Déployé automatiquement à chaque push sur `master` via `.github/workflows/pages.yml`.
- `scripts/collect.py` — collecteur automatique sans IA (voir ci-dessous), lancé par `.github/workflows/collect.yml`.

## Tableau de bord

La GitHub Page publie `docs/index.html` : rendement réalisé vs intervalle 80 % prévu, courbe de clôture, rendements quotidiens, hit rate cumulé vs 50 %, MAE modèle vs naïf, leçons et vue table. Chaque exécution quotidienne de la routine doit mettre à jour `docs/data/history.json` (nouveau record de séance, verdict de la prévision de la veille, métriques cumulées, prévision active).

**Page « Composantes »** (`docs/composants.html`) : les 40 valeurs du CAC 40 dans l'ordre de l'indice (rang = capitalisation boursière officielle, proxy documenté du poids Euronext en flottant plafonné), affichées par groupes de 10. Pour chaque valeur : dernière clôture en premier, variation du jour, **écart vs le prévisionnel émis à J-1 pour l'indice** (variation de la valeur − milieu de l'intervalle 80 % prévu), sparkline et historique antichronologique complet avec l'écart par séance. Données : `docs/data/cac40.json` (composition, maintenue à chaque revue trimestrielle Euronext) et `docs/data/composants.json` (séries + rangs, alimenté par le collecteur).

## Déclenchement automatique

La routine est intégrée comme la routine « Veille IA », via deux **Routines Claude planifiées** (jours de semaine, heures calées sur la mise à disposition des valeurs) :

| Trigger | Heure (UTC) | Rôle |
|---|---|---|
| Instantané européen | `48 16 * * 1-5` (après la clôture Euronext de 17h35 Paris) | Rafraîchit `docs/data/history.json` avec les clôtures définitives Europe/Asie et le contexte US « en séance ». Aucune prévision, aucune évaluation, aucun mouvement du suivi dynamique. |
| Routine complète J+1 | `15 21 * * 1-5` (après la clôture US de 22h00 Paris) | Complète le record du jour (US définitif), évalue la prévision de la veille, met à jour métriques/leçons/suivi dynamique, émet la prévision J+1, écrit le rapport. |

Chaque trigger committe directement sur `master` avec vérification du push (repli API GitHub en secours), ce qui redéploie le tableau de bord. Le record quotidien est unique : l'instantané le crée, la routine du soir le complète (jamais de doublon).

En cas d'exécution manquée, relancer la routine à la main : demander l'exécution dans la session Claude liée au dépôt, ou coller `ROUTINE.md` + le dernier BLOC ÉTAT dans une nouvelle conversation.

## Collecte automatique sans IA (filet de sécurité)

Pour que le tableau de bord continue de fonctionner **même si les routines Claude sont arrêtées**, un collecteur autonome (`scripts/collect.py`, Python standard, zéro dépendance) tourne sur GitHub Actions (`.github/workflows/collect.yml`) les jours de semaine à 16h15 UTC (après la clôture Euronext) et 20h45 UTC (après la clôture US) — juste avant les runs Claude, qui trouvent ainsi les chiffres officiels déjà en place.

Ce qu'il fait :
- récupère les clôtures/ouvertures/volumes officiels (API Yahoo Finance, repli Stooq) du CAC 40 et des 7 indices compagnons ;
- **fusion non destructive** de `docs/data/history.json` : crée le record du jour s'il manque, ne remplit que les champs `null`/ND, n'écrase jamais une valeur posée par la routine ; toute divergence > 0,1 % avec la clôture enregistrée est signalée en note (l'arbitrage reste à la routine) ;
- **évaluation mécanique** : si la prévision active vise la séance collectée, il la consomme et calcule le verdict (direction, intervalle, erreur) et recalcule métriques et benchmarks — l'attribution corrigeable/irréductible, les leçons, le suivi dynamique et la prévision J+1 restent du ressort exclusif de la routine IA ;
- committe sur `master` et redéploie Pages directement (un push `GITHUB_TOKEN` ne déclenche pas le workflow Pages).

- **prévision mécanique de secours** : si la prévision active est périmée et qu'aucune prévision IA n'a été émise, le collecteur en émet une lui-même en appliquant les règles codifiées par la routine — direction par persistance corrigée du signal US fort (L7), probabilité plafonnée à 0,55 (L5, binaires non analysables sans IA), intervalle 1,28 × σ20 élargi selon le régime VIX. Elle est marquée `source: mécanique` (badge « ⚙ sans IA » sur le tableau de bord et dans le record évalué) et la routine IA, dès qu'elle retourne, la remplace par sa prévision complète.

Répartition des rôles : le collecteur garantit des **données fraîches et officielles** et une **continuité de prévision dégradée mais honnête** ; les routines Claude apportent la lecture de l'actualité, l'arbitrage des sources, l'attribution des erreurs, les leçons et la prévision J+1 informée. Sans routine, le cycle complet (collecte → prévision → verdict → métriques) continue en mode mécanique.

## Avertissement

Exercice d'analyse et de suivi de modèle uniquement. Aucune recommandation d'achat, de vente ou de prise de position.
