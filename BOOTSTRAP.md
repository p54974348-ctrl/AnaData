# PROMPT DE RECRÉATION — SYSTÈME « CAC 40 J+1 » (AnaData)

> Coller l'intégralité de ce document dans une session Claude Code disposant d'un dépôt GitHub vierge (avec GitHub Actions et GitHub Pages activables). Il recrée le système complet : routine de prévision quotidienne, tableau de bord, déclenchement automatique et filet de sécurité sans IA. Adapter uniquement les noms de dépôt/branche si besoin.

---

Tu es mon analyste quantitatif et mon ingénieur d'automatisation. Construis dans ce dépôt un système complet de suivi et de prévision quotidienne du CAC 40, nommé « CAC 40 J+1 », conforme à la spécification ci-dessous. Travaille directement sur la branche `master` (jamais de pull request), commite par étapes fonctionnelles, et vérifie chaque composant avant de passer au suivant.

## 1. Mission et règles permanentes

* Périmètre : indice CAC 40 (PX1 / `^FCHI`), Euronext Paris, fuseau Europe/Paris, séance 9h00–17h35. Chaque soir de bourse, prévoir le rendement de la séance suivante (J+1) : direction, probabilité, intervalle d'amplitude à ~80 %.
* **Honnêteté des données** : aucune valeur de marché inventée. Chaque chiffre provient d'une recherche web ou d'une API officielle, avec source et horodatage. Donnée introuvable = « ND », jamais estimée. Si deux sources divergent de plus de 0,1 % sur une clôture, signaler l'écart et arbitrer en privilégiant les articles de clôture datés (Reuters, Boursorama) sur les cotes dynamiques d'agrégateurs (pièges connus : niveaux pré-fixing, cotes périmées).
* Toute la modélisation se fait en rendements (%), jamais en points d'indice bruts.
* **Honnêteté statistique** : probabilité calibrée entre 0,50 et 0,70 (jamais plus de 0,70 sans justification exceptionnelle chiffrée). Un hit rate durable de 52–55 % est un bon résultat. Aucune conclusion statistique avant n≈40 ; revues de validation à n=40 puis n=60.
* **Jamais de recommandation d'achat, de vente ou de prise de position** — exercice d'analyse et de suivi de modèle uniquement. L'avertissement figure sur le tableau de bord et dans chaque rapport.
* Si le jour n'est pas un jour de bourse Euronext (week-end, férié), le signaler et s'arrêter.

## 2. Structure du dépôt à créer

```
ROUTINE.md                     # prompt normatif de la routine quotidienne (étapes 0-6)
INDICES.md                     # fiche des indices suivis + règles du suivi dynamique
README.md                      # architecture, rôles, planification
BOOTSTRAP.md                   # ce document
rapports/AAAA-MM-JJ.md         # un rapport par exécution (trace auditable)
analyses/                      # analyses ponctuelles (ex. validation du modèle)
docs/index.html                # tableau de bord GitHub Pages (autonome, sans dépendance)
docs/data/history.json         # SOURCE UNIQUE DE L'ÉTAT (voir §4)
scripts/collect.py             # collecteur sans IA (voir §7)
.github/workflows/pages.yml    # déploiement Pages
.github/workflows/collect.yml  # collecte automatique planifiée
```

Ne conserver aucun fichier inutile dans le dépôt (pas de fichiers temporaires, de brouillons, de doublons d'état).

## 3. Indices suivis

**Noyau immuable de 8 indices** (ne change JAMAIS) :

| Ticker | Indice | Rôle |
|---|---|---|
| `^FCHI` | CAC 40 | cible |
| `^GSPC` | S&P 500 | moteur overnight US |
| `^VIX` | VIX | régime de volatilité (détecteur de régime) |
| `^IXIC` | Nasdaq Composite | moteur overnight US (tech) |
| `^GDAXI` | DAX 40 | co-mouvement européen — **total return** : ne pas comparer sa performance brute au CAC (indice prix) |
| `^STOXX50E` | Euro Stoxx 50 | co-mouvement européen |
| `^N225` | Nikkei 225 | séance asiatique de la nuit |
| `^HSI` | Hang Seng | canal Chine/luxe |

Compléments collectés : EUR/USD, Brent, taux 10 ans (OAT ou Bund). Le canal pétrole se raisonne en VARIATION (momentum), pas en niveau.

**Suivi dynamique** (liste additionnelle, automatique) : tout indice hors noyau en séance à **≥ +2,0 %** est ajouté ; tout indice du suivi dynamique à **≤ −2,0 %** en est retiré. Chaque mouvement est journalisé (date, variation, raison) dans `journal_suivi`.

## 4. Source unique de l'état : `docs/data/history.json`

Schéma (tous les champs numériques peuvent être `null` = ND) :

```json
{
  "indice": "CAC 40 (^FCHI)",
  "routine": "CAC40_J+1",
  "derniere_maj": "AAAA-MM-JJ",
  "suivi_noyau": ["^FCHI", "^GSPC", "^VIX", "^IXIC", "^GDAXI", "^STOXX50E", "^N225", "^HSI"],
  "suivi_dynamique": [{"ticker": "", "nom": "", "ajoute_le": "", "var_pct_ajout": 0, "raison": ""}],
  "journal_suivi": [{"date": "", "action": "ajout|retrait|aucun", "ticker": null, "var_pct": null, "note": ""}],
  "records": [{
    "date": "AAAA-MM-JJ", "cloture": 0, "rendement_pct": 0, "gap_pct": null, "intra_pct": null,
    "ouverture": null, "volume": null,
    "prevision": {"direction": "hausse|baisse", "probabilite": 0.5, "intervalle_80pct": [-1, 1], "source": "présent seulement si mécanique"},
    "verdict": {"direction_ok": true, "dans_intervalle": true, "erreur_pct": 0, "type": "corrigeable|irréductible|null", "cause": ""},
    "note": "",
    "contexte": {"sp500": {"niveau": 0, "var_pct": 0, "note": ""}, "vix": {}, "nasdaq": {}, "dax": {}, "stoxx50": {}, "nikkei": {}, "hangseng": {}}
  }],
  "prevision_active": {"seance_cible": "", "direction": "", "probabilite": 0.5, "intervalle_80pct": [-1, 1], "hypotheses": ["3 à 5 hypothèses journalisées"], "source": "présent seulement si mécanique"},
  "metriques": {"n": 0, "hit_rate": null, "mae_pct": null, "mae_naif_pct": null, "couverture_intervalle": null, "brier": null,
    "note_convention": "prévision ponctuelle = milieu de l'intervalle 80 % pour la MAE (garde-fou d'amplitude, pas une mesure directionnelle)",
    "benchmarks": {"hit_rate_persistance": null, "hit_rate_toujours_hausse": null, "note": "persistance = prédire le signe de la veille (ex ante) ; toujours-hausse = référence de régime (ex post). Le modèle n'a de valeur directionnelle démontrée que s'il bat durablement la persistance."}},
  "metriques_historique": [{"date": "", "n": 0, "hit_rate": 0, "mae_pct": 0, "mae_naif_pct": 0, "couverture": 0, "brier": 0}],
  "lecons": [{"texte": "", "statut": "OBSERVÉE ×1 | CONFIRMÉE (×3 : dates)"}]
}
```

Règle absolue : **un seul record par séance**. Tout processus qui trouve un record existant le complète (champs `null` uniquement), jamais ne le duplique ni n'écrase une valeur posée.

## 5. La routine quotidienne (à écrire dans `ROUTINE.md`)

Étapes exécutées dans l'ordre, réponse compacte lisible sur mobile :

* **Étape 0 — État** : lire `docs/data/history.json`. S'il n'existe pas : initialiser un historique vide, « Jour 1 », sauter l'Étape 3.
* **Étape 1 — Collecte** (recherche web obligatoire) : le collecteur automatique (§7) peut avoir pré-rempli le record — le compléter, vérifier sa clôture contre la presse. CAC (clôture J, clôture J-1, ouverture pour décomposer gap/intraséance — si introuvable en presse, chercher dans les données historiques Yahoo/Investing —, volume), les 7 compagnons + EUR/USD + Brent + taux 10 ans, 3-5 faits d'actualité expliquant la séance, agenda du lendemain (macro, banques centrales, résultats de composantes). Appliquer les règles du suivi dynamique (§3). Sources : Boursorama, ABC Bourse, Yahoo Finance, Euronext, Investing, Reuters.
* **Étape 2 — Réalisé** : rendement J en %, décomposé gap + intraséance si possible ; explication en 2-3 lignes fondée uniquement sur l'actualité collectée.
* **Étape 3 — Évaluation de la prévision d'hier** (cœur de la routine) : direction correcte ? dans l'intervalle ? erreur en pt%. Si un verdict mécanique existe (type=null), le vérifier et le compléter. Classer l'erreur : **CORRIGEABLE** (un facteur connaissable hier soir a été ignoré ou mal pondéré — lequel, en reprenant les hypothèses journalisées) ou **IRRÉDUCTIBLE** (information nouvelle imprévisible — laquelle). Mettre à jour : n, hit rate, MAE, MAE naïve, couverture 80 %, Brier, et les **benchmarks** hit rate de la persistance et du « toujours hausse ».
* **Étape 4 — Apprentissage** : liste « Leçons » (7 max, actionnables). Une leçon observée 3 fois passe **[CONFIRMÉE]** et s'applique systématiquement ; une leçon contredite 2 fois est **retirée**.
* **Étape 5 — Prévision J+1** : si `prevision_active` porte `source` mécanique, la remplacer. Direction + probabilité 0,50–0,70 ; intervalle 80 % basé sur le σ des ~20 derniers rendements (proxy VIX tant que n<20 ; **dès n=20, σ réalisé** — le VIX, qui surestime d'une prime de risque, ne sert plus que de détecteur de régime), élargi si VIX élevé ou événement majeur à l'agenda ; 3-5 hypothèses explicites (elles servent à l'attribution du lendemain) ; risques identifiés.
* **Étape 6 — Rapport** au format fixe (tableau marché, verdict, métriques modèle vs naïf, leçons, prévision, bloc état) écrit dans `rapports/AAAA-MM-JJ.md` ; mise à jour intégrale de `history.json` ; commit et push directs sur `master`.

Leçons de démarrage à pré-charger (héritées de la première campagne, statut OBSERVÉE — elles devront reconquérir leurs confirmations) :
1. Les publications des poids lourds du CAC dominent les séances — pondérer explicitement, dans les deux sens.
2. Risque de queue en matérialisation ⇒ élargir la borne exposée de l'intervalle.
3. Canal pétrole en VARIATION (±4 %/jour), pas en niveau.
4. Catalyseurs binaires non résolus au moment de la prévision ⇒ probabilité ≤ ~0,55 et intervalle large des deux côtés.
5. Balayer les dépêches du soir avant d'émettre.
6. **Biais contrarien (L7)** : ne prédire « baisse » contre un rallye que sur signal négatif fort (gap US < −0,5 % ou choc identifié) ; « prises de bénéfices » seul ne suffit jamais.

## 6. Tableau de bord GitHub Pages (`docs/index.html`)

Page unique autonome (HTML/CSS/JS vanilla, SVG natif, **aucune dépendance externe**), qui charge `data/history.json` et affiche, sur une **fenêtre glissante de 30 jours** :

* Tuiles KPI : séances évaluées, hit rate (avec repères « hasard 50 % · persistance X % · touj. hausse Y % »), MAE modèle vs naïf, couverture 80 %, Brier.
* Carte « Prévision active » : direction, probabilité, intervalle, hypothèses ; badge « ⚙ prévision mécanique (sans IA) » si `source` mécanique.
* Graphique intervalle prévu vs rendement réalisé (bandes + points, la prévision active en surbrillance).
* Courbe de clôture ; barres de rendements quotidiens (hausse/baisse).
* Contexte marchés : bande de « top movers » (chips triées, indices à ≥ +2 % mis en avant), graphique et table triée par variation (fortes progressions marquées ▲, note DAX total return).
* Indices suivis : noyau fixe + table du suivi dynamique.
* Hit rate cumulé (lignes de référence pointillées : 50 %, persistance, toujours-hausse) ; MAE modèle vs naïf.
* Leçons actives avec badges de statut (CONFIRMÉE en couleur d'accent).
* Table de données détaillées (date, clôture, rendement, gap, intraséance, prévision, verdicts ✓/✗).
* Design : thème clair/sombre (`prefers-color-scheme` + bascule `data-theme`), palette sobre (accent #2a78d6/#3987e5, rouge réservé aux baisses/erreurs), lignes 2 px, tooltips au survol, responsive mobile, avertissement « aucune recommandation d'investissement » en pied de page.

Déploiement : workflow `pages.yml` (déclenché sur push `master` touchant `docs/**` + `workflow_dispatch`) publiant `./docs` sur la branche `gh-pages` via `peaceiris/actions-gh-pages@v4`. L'activation initiale de Pages (Settings → Pages → branche `gh-pages`) est une action manuelle du propriétaire — la demander explicitement.

## 7. Collecteur automatique sans IA (`scripts/collect.py` + `collect.yml`)

Objectif : **le site et le cycle de prévision continuent de fonctionner même si les routines IA sont arrêtées.**

* Planification (`collect.yml`) : jours de semaine à **16h15 UTC** (après la clôture Euronext) et **20h45 UTC** (après la clôture US) — volontairement AVANT les runs IA (§8) pour qu'ils trouvent les chiffres officiels en place. Plus `workflow_dispatch` pour les tests. Le workflow installe `yfinance`, exécute le script, committe `docs/data/history.json` si modifié, et **redéploie Pages lui-même** (un push effectué avec `GITHUB_TOKEN` ne déclenche pas le workflow Pages).
* Sources en cascade : **yfinance** (impersonation navigateur — indispensable, Yahoo renvoie 429 aux IP des runners GitHub) → API brute Yahoo chart (`query1`/`query2`) → CSV Stooq (parsing validé : rejeter proprement toute réponse non-CSV). Requêtes espacées de ~1,5 s. Échec total = abandon SANS modification (exit 1), jamais de données inventées.
* **Fusion non destructive** : crée le record de la dernière séance s'il manque ; ne remplit que les champs `null`/ND (clôture, rendement, gap, intraséance, ouverture, volume, contextes) ; n'écrase jamais une valeur existante ; toute divergence > 0,1 % avec la clôture enregistrée est signalée par une note « ⚠ divergence collecteur » (l'arbitrage reste à l'IA).
* **Évaluation mécanique** : si `prevision_active` vise la séance collectée, la copier dans le record (avec son éventuelle `source`) et calculer le verdict (direction_ok, dans_intervalle, erreur vs milieu d'intervalle ; `type: null`, cause « évaluation mécanique — attribution à faire par la routine »). Recalculer intégralement, de façon déterministe et idempotente, `metriques` + `benchmarks` + `metriques_historique` à partir des records.
* **Prévision mécanique de secours** : si la prévision active est périmée (consommée/dépassée) et non remplacée par l'IA, en émettre une : direction = persistance (signe du jour) corrigée du signal US fort (S&P < −0,5 % ⇒ baisse ; > +0,5 % ⇒ hausse) conformément à L7 ; probabilité 0,52/0,54/0,55 selon la convergence des signaux (plafond L5 : les binaires du lendemain ne sont pas analysables sans IA) ; intervalle = 1,28 × σ des ~20 derniers rendements, élargi ×1,25 (défaut), ×1,4 (VIX ≥ 20) ou ×1,8 (VIX ≥ 25) ; 3 hypothèses générées ; champ `source: "mécanique …"`. Une prévision IA à jour n'est **jamais** écrasée ; une prévision mécanique est remplaçable (par l'IA ou par un run collecteur ultérieur avec données plus fraîches). Idempotence stricte : relancer sans nouvelles données ne produit aucun commit.
* Restent du ressort EXCLUSIF de l'IA : attribution corrigeable/irréductible, leçons, suivi dynamique, notes rédigées, rapports.

## 8. Déclenchement automatique des routines IA

Créer deux **Routines Claude planifiées** (triggers cron UTC, jours de semaine, liées à la session du dépôt) :

| Routine | Cron UTC | Rôle |
|---|---|---|
| Instantané européen | `48 16 * * 1-5` | Rafraîchit `history.json` (clôtures définitives Europe/Asie, contexte US en séance). AUCUNE prévision, évaluation ni mouvement de watchlist. Commit unique « Instantané européen — séance du &lt;date&gt; ». |
| Routine complète J+1 | `15 21 * * 1-5` | Exécute `ROUTINE.md` en entier : complète le record (US définitif, balayage des dépêches du soir), évalue, apprend, prévoit, rapporte, committe. |

Garde-fous dans les prompts des triggers : anti-doublon (un seul record par séance — compléter, jamais recréer) ; vérification du push avec repli API GitHub ; en cas d'échec total de push, coller le rapport en clair dans la conversation. En cas d'exécution manquée, la routine peut être relancée à la main (ou le collecteur assure l'intérim).

## 9. Validation avant mise en service

1. Tester la logique de fusion du collecteur hors ligne (option `--mock` du script) : complétion sans écrasement, création de record, consommation de prévision, verdict mécanique, chaînage de prévisions mécaniques sur plusieurs jours simulés, idempotence.
2. Vérifier que le recalcul mécanique des métriques reproduit exactement les métriques de référence sur données connues.
3. Rendre le tableau de bord dans un navigateur headless : zéro erreur JS, tous les cas limites (record sans prévision, sans verdict, contexte ND, listes vides « Jour 1 »).
4. Déclencher `collect.yml` par `workflow_dispatch` et vérifier le run réel de bout en bout (collecte → commit → déploiement Pages), puis un second run confirmant le no-op.
5. Vérifier l'URL publique de la page.

## 10. Résilience attendue (résumé)

Trois niveaux : (1) routine IA complète — analyse, attribution, leçons, prévision informée ; (2) IA arrêtée — le collecteur maintient données officielles, verdicts, métriques et une prévision mécanique honnête, marquée comme telle ; (3) tout arrêté — la page reste servie par GitHub Pages sur le dernier état publié. La mort silencieuse est impossible : chaque niveau laisse une trace datée (`derniere_maj`, commits, badges).
