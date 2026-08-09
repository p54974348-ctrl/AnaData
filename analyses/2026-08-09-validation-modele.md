# Validation du modèle « CAC 40 J+1 » — analyse des 13 premières prévisions (21/07 → 07/08/2026)

Analyse réalisée le 09/08/2026 sur les données de `docs/data/history.json` (14 séances collectées, 13 prévisions évaluées). Exercice d'analyse uniquement — aucune recommandation d'investissement.

## 1. Le régime de marché de la période

| Statistique (14 séances) | Valeur |
|---|---|
| Performance cumulée | **+4,49 %** (8 340,11 → 8 714,93) |
| Rendement moyen | **+0,32 %/jour** |
| Écart-type réalisé | 0,72 %/jour |
| Séances de hausse | **12/14 (86 %)** |
| Extrêmes | −1,64 % (23/07, Brent > 100 $) / +1,22 % (03/08, cessez-le-feu) |

Période exceptionnelle et **non représentative** : un cycle complet escalade → désescalade Iran-US (Brent 102 $ → 80 $), une décision Fed contestée, le pic de la saison des résultats, puis un rallye de 7 séances avec records en série. Les mouvements ont été dominés par des chocs binaires nocturnes, exactement le pire régime pour une prévision émise la veille au soir.

## 2. Bilan brut des 13 prévisions

| Métrique | Modèle | Naïf (0 %) | Cible/repère |
|---|---|---|---|
| Hit rate directionnel | 8/13 (61,5 %) | 50 % | 52–55 % visé |
| MAE (convention milieu d'intervalle) | 0,72 pt% | **0,66 pt%** | battre le naïf |
| Couverture intervalle 80 % | **11/13 (84,6 %)** | — | ~80 % ✓ |
| Brier | 0,2446 | 0,25 | < 0,25 ✓ (de peu) |

## 3. Le diagnostic central : une asymétrie directionnelle massive

| Prévisions | n | Correctes | Taux |
|---|---|---|---|
| « hausse » | 8 | 7 | **87,5 %** |
| « baisse » | 5 | 1 | **20 %** |

**Toutes les erreurs directionnelles sauf une sont des « baisse » prédites pendant le rallye** (24/07, 30/07, 06/08, 07/08 ; la 5e erreur, 29/07, est une « hausse » démentie par un choc géopolitique nocturne). C'est un biais contrarien systématique, désormais codifié (leçon L7) : l'argument « prises de bénéfices après N hausses » a été utilisé 4 fois et s'est trompé 4 fois.

## 4. Confrontation à des benchmarks que la routine ne suivait pas

| Stratégie | Hit rate | Brier |
|---|---|---|
| **Modèle** | 61,5 % | 0,2446 |
| Pile ou face | 50 % | 0,25 |
| **Persistance** (prédire le signe de la veille) — implémentable ex ante | **69,2 %** | — |
| « Toujours hausse » — connu seulement ex post | **84,6 %** | 0,218 (p=0,55) / 0,169 (p=0,65) |

Lecture honnête : sur cette période, le modèle bat le hasard mais **pas la simple persistance**, et reste loin du « toujours hausse » (qui bénéficie d'un biais de rétrospection, mais quantifie ce que le biais contrarien a coûté). Le hit rate de 61,5 % à n=13 a un intervalle de confiance d'environ [35 % ; 84 %] : **aucune conclusion statistique n'est possible**, ni positive ni négative.

## 5. Les intervalles : le point fort

- Couverture 84,6 % pour une cible de 80 % — convergence propre après un début difficile (50 % à n=2) : les leçons L2 (élargir la borne exposée) et L5 (binaires ⇒ intervalle large) ont visiblement corrigé le tir.
- Largeur moyenne 2,71 pts ⇒ σ implicite ~1,06 %/j vs σ réalisé 0,72 %/j : les intervalles sont **~45 % plus larges que la volatilité réalisée**. Ce conservatisme est en partie justifié (les deux sorties d'intervalle, −1,64 % et +0,92 % hors bornes asymétriques, sont des queues réelles), mais un resserrement progressif est possible à mesure que σ20 devient calculable sur données réelles.

## 6. Les probabilités : calibration asymétrique

- Sur les prévisions « hausse » : p moyen ≈ 0,54, réussite 87,5 % → **sous-confiance** massive côté hausse.
- Sur les prévisions « baisse » : p moyen ≈ 0,55, réussite 20 % → **sur-confiance** côté baisse.
- Le plafonnement L5 (p ≤ 0,55 face aux binaires) a rempli son rôle : malgré 5 erreurs de direction, le Brier reste sous le hasard — les erreurs ont coûté peu car elles étaient peu confiantes. Le seul Brier vraiment cher est le p=0,60 du 30/07 (0,36), précisément la séance qui a motivé L5.

## 7. La MAE : une convention à revoir

La convention « prévision ponctuelle = milieu de l'intervalle » produit des points proches de 0 → la MAE du modèle suit mécaniquement celle du naïf (|rendement|) et ne peut le battre que marginalement. **En l'état, la MAE ne mesure presque rien** : l'information directionnelle du modèle n'y est pas injectée. Deux options : (a) assumer que la MAE est un simple garde-fou et le documenter ; (b) définir un point prévisionnel directionnel (p. ex. milieu ± un décalage lié à la direction et au drift), ce qui rendrait la MAE discriminante.

## 8. Le processus d'évaluation lui-même : ce qui a prouvé sa valeur

1. **Le pipeline de données honnête a fonctionné** : 4 divergences de sources détectées et résolues (dont deux clôtures erronées d'agrégateurs corrigées aux runs du soir — 29/07 et 03/08) ; les ND sont restés ND.
2. **L'attribution corrigeable/irréductible produit des règles falsifiables** : 7 leçons dont 4 confirmées ×3 (poids lourds, pétrole en variation, calibration binaire) — chacune est traçable à des séances précises et a modifié le comportement des prévisions suivantes de façon mesurable (couverture 50 % → 85 % ; Brier plafonné).
3. **Limites du processus** : gap/intraséance quasi jamais décomposés (ouverture introuvable dans les sources de presse — chronique), volume jamais trouvé, Asie parfois ND, et le piège des cotes pré-fixing/agrégateurs est documenté mais demande de la vigilance.

## 9. Verdict de pertinence

**Le cadre d'évaluation est pertinent et fonctionne** (couverture sur cible, Brier maîtrisé, apprentissage démontrable, honnêteté des données). **La valeur prédictive directionnelle n'est pas démontrée** : sur ce régime de rallye, le modèle fait moins bien que la persistance naïve, à cause d'un biais contrarien identifié et désormais codifié (L7). n=13 interdit toute conclusion définitive — le rendez-vous statistique sérieux est vers n≈40-60 (2-3 mois).

## 10. Recommandations (à valider avant application)

1. **Ajouter deux benchmarks au suivi permanent** : persistance (implémentable ex ante) et « toujours hausse » (référence de régime) — hit rate et Brier, aux côtés du naïf. C'est le vrai test d'utilité du modèle.
2. **Appliquer strictement L7** (déjà actif) : pas de « baisse » contre un rallye sans signal négatif fort ; l'effet devrait se lire directement dans le hit rate des prochaines semaines.
3. **Décider du sort de la MAE** : documenter son rôle de garde-fou, ou passer à un point prévisionnel directionnel.
4. **Resserrement progressif des intervalles** quand σ20 réel sera disponible (dès n=20), en gardant l'élargissement événementiel (L2/L5).
5. **Collecte** : tenter systématiquement l'ouverture via les données historiques (Yahoo/Investing « historical data ») pour décomposer gap/intraséance, au moins hebdomadairement.
6. **Ne pas réagir aux métriques avant n≈40** : la discipline actuelle (proba 0,50-0,70, benchmark naïf, attribution) est le bon cadre pour laisser les données trancher.
