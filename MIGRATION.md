# MIGRATION vers `PFeuillet/CacWatch`

Objectif : dupliquer ce projet vers https://github.com/PFeuillet/CacWatch **en gardant les deux dépôts fonctionnels en parallèle**. La routine IA actuelle (Routines Claude planifiées) reste liée à `p54974348-ctrl/AnaData` et n'est pas déplacée.

Le code est entièrement portable : aucun nom de dépôt ni URL en dur dans les workflows, le collecteur ou les pages (déploiement Pages relatif, commits via le `GITHUB_TOKEN` du dépôt hôte). Une copie du contenu suffit.

> Pourquoi cette migration n'a pas pu être faite automatiquement depuis la session AnaData : la session Claude Code est liée au propriétaire `p54974348-ctrl` et ne peut pas obtenir de droits d'écriture sur un dépôt d'un autre compte (`PFeuillet`). Deux options ci-dessous.

## Option A — push local (recommandée, ~2 minutes)

Sur votre machine, avec un compte ayant les droits d'écriture sur `PFeuillet/CacWatch` (créer d'abord le dépôt **vide**, sans README, s'il n'existe pas) :

```bash
git clone https://github.com/p54974348-ctrl/AnaData.git cacwatch-migration
cd cacwatch-migration
git remote set-url origin https://github.com/PFeuillet/CacWatch.git
git push -u origin master
```

L'historique git complet (rapports, analyses, collectes) est conservé.

## Option B — nouvelle session Claude Code sur CacWatch

Démarrer une session Claude Code (claude.ai/code) avec `PFeuillet/CacWatch` comme dépôt source, puis coller :

> Migre le contenu du dépôt public https://github.com/p54974348-ctrl/AnaData vers ce dépôt : récupère la branche `master` d'AnaData (dépôt public, `git fetch` anonyme), pousse-la sur `master` ici en conservant l'historique, applique les renommages cosmétiques listés dans `MIGRATION.md` §« Renommages », vérifie que le workflow `collect.yml` passe (workflow_dispatch), puis suis la checklist post-migration de `MIGRATION.md`.

## Checklist post-migration (sur CacWatch)

1. **Branche par défaut** : Settings → General → Default branch → `master`.
2. **Actions** : vérifier qu'elles sont autorisées (Settings → Actions) ; les crons de `collect.yml` (16h15 & 20h45 UTC, lun-ven) s'activent automatiquement une fois le fichier sur la branche par défaut. Lancer un premier run manuel : Actions → « Collecte automatique des données de marché » → Run workflow.
3. **GitHub Pages** : après ce premier run (qui crée/déploie la branche `gh-pages`), activer Pages : Settings → Pages → Source « Deploy from a branch » → `gh-pages` / racine. Le site sera sur **https://pfeuillet.github.io/CacWatch/**.
4. **Vérifier** : la page d'accueil (indice) et `composants.html` se chargent, et un commit « Collecte automatique — … » apparaît après le run.

## Ce qui fonctionne immédiatement sur CacWatch (sans routine IA)

Grâce au mode dégradé du collecteur, CacWatch est **autonome dès le premier run** : données officielles 2×/jour, verdicts mécaniques, métriques, prévision J+1 mécanique (badge « ⚙ sans IA »), page Composantes complète. Il tourne en mode mécanique tant qu'aucune routine IA ne lui est rattachée.

Pour rattacher plus tard une routine IA à CacWatch : créer des Routines Claude planifiées équivalentes (voir `README.md` §« Déclenchement automatique » — crons `48 16 * * 1-5` et `15 21 * * 1-5` UTC) dans une session liée à CacWatch, avec `ROUTINE.md` comme prompt normatif.

## Renommages cosmétiques (optionnels)

Seules mentions « AnaData » dans le projet (le code n'en dépend pas) :

```bash
sed -i 's/# AnaData — /# CacWatch — /' README.md
sed -i 's/SYSTÈME « CAC 40 J+1 » (AnaData)/SYSTÈME « CAC 40 J+1 » (CacWatch)/' BOOTSTRAP.md
sed -i 's/Composantes du CAC 40 — AnaData/Composantes du CAC 40 — CacWatch/' docs/composants.html
sed -i 's/au dépôt `AnaData`/au dépôt `CacWatch`/' ROUTINE.md
git commit -am "Renommage CacWatch" && git push
```

## Gouvernance : deux lignées indépendantes (règle actée le 09/08/2026)

**AnaData et CacWatch ont des cycles de vie et des définitions de besoin distincts.** La migration est un point de départ commun, pas un lien permanent :

- **Aucune synchronisation après la migration** : une évolution (IHM, collecteur, routine, données) réalisée sur l'un des deux dépôts n'impacte jamais l'autre. Pas de re-mirroring, pas de force-push d'un dépôt vers l'autre, pas de fusion de branches entre dépôts.
- **Jamais de fusion des `history.json`** des deux dépôts (états et métriques incompatibles : prévisions IA vs mécaniques, historiques divergents).
- **Portage explicite uniquement** : si une fonctionnalité développée dans un projet est souhaitée dans l'autre, elle y est ré-implémentée par une demande explicite dans la session de CE dépôt-là (le commit d'origine peut servir de référence), puis vit sa propre vie.
- **Sessions cloisonnées** : la session Claude liée à AnaData ne modifie qu'AnaData ; celle liée à CacWatch ne modifie que CacWatch. Chaque dépôt a son propre `BOOTSTRAP.md` (spécification de référence), qui évolue avec lui.
