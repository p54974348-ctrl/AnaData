# Indices à plus fort impact sur le CAC 40 — Fiche de référence

Liste resserrée aux indices ayant un impact mesurable sur la séance parisienne, organisés par rôle dans la routine J+1.

## 1. La cible

| Indice | Ticker Yahoo | Rôle | À savoir |
|---|---|---|---|
| CAC 40 | `^FCHI` | Variable à prévoir | Indice **prix** (hors dividendes), revue trimestrielle de la composition |

## 2. Moteurs overnight — clôture US (22h00, heure de Paris)

| Indice | Ticker Yahoo | Impact sur le CAC |
|---|---|---|
| S&P 500 | `^GSPC` | Premier prédicteur du gap d'ouverture parisien ; référence mondiale du risque actions |
| VIX | `^VIX` | Régime de volatilité : sert à calibrer la largeur de l'intervalle 80 % de la prévision |
| Nasdaq Composite | `^IXIC` | Sentiment tech ; signal complémentaire quand il diverge du S&P 500 |

## 3. Co-mouvement européen — même séance (9h00–17h35)

| Indice | Ticker Yahoo | Impact sur le CAC |
|---|---|---|
| DAX 40 | `^GDAXI` | Corrélation la plus forte avec le CAC ; **indice total return** (ne pas comparer les performances brutes) |
| Euro Stoxx 50 | `^STOXX50E` | Pouls de la zone euro, référence des dérivés européens |

## 4. Séance asiatique — nuit (connue avant l'ouverture de Paris à 9h00)

| Indice | Ticker Yahoo | Impact sur le CAC |
|---|---|---|
| Nikkei 225 | `^N225` | Première lecture du sentiment de risque overnight ; pondéré par les prix |
| Hang Seng | `^HSI` | Canal Chine : impact direct sur le luxe (LVMH, Hermès, Kering…), poids lourd du CAC |

## 5. Suivi dynamique (automatique)

Le noyau des 8 indices ci-dessus est **immuable** : il ne peut jamais être modifié par les règles automatiques. En complément, une liste dynamique évolue chaque soir selon des règles fixes :

| Règle | Détail |
|---|---|
| **Ajout** | Tout indice hors noyau dont la variation de la séance est **≥ +2,0 %** entre au suivi dynamique le soir même (date, niveau et raison journalisés) |
| **Retrait** | Tout indice du suivi dynamique dont la variation de la séance est **≤ −2,0 %** en est retiré automatiquement le soir même |
| **Réadmission** | Un indice retiré peut revenir s'il redéclenche la règle d'ajout |
| **Univers scanné** | Les grands indices de la liste « retirés » ci-dessous + KOSPI (`^KS11`), TAIEX (`^TWII`), Nasdaq-100 (`^NDX`), Dow (`^DJI`), Russell 2000 (`^RUT`), FTSE 100 (`^FTSE`), CSI 300, Nifty 50, ASX 200 |

Les indices du suivi dynamique sont collectés à l'Étape 1 comme les indices du noyau et apparaissent dans le contexte du tableau de bord tant qu'ils sont suivis.

## Retirés de la liste (impact marginal sur le CAC)

- **Dow Jones** — redondant avec le S&P 500, méthodologie datée (pondération par les prix, 30 valeurs).
- **Russell 2000** — small caps US, faible transmission directe vers Paris.
- **FTSE 100** — peu d'apport au-delà du couple DAX / Euro Stoxx, bruit de change GBP.
- **Shanghai Composite / CSI 300** — le Hang Seng suffit comme proxy Chine (données plus fiables, horaires proches).
- **MSCI World / Emerging Markets** — références de long terme, pas des moteurs de séance.
- **Nasdaq-100, SBF 120, IBEX, FTSE MIB, AEX, SMI, BEL 20, Nifty, Sensex, KOSPI, ASX 200** — corrélés mais sans information additionnelle exploitable à J+1.

---

> **Rappels pratiques** : DAX = total return vs CAC = prix, ne jamais comparer les performances brutes. Toujours aligner les fuseaux avant de croiser les séries (clôture US du jour J‑1 → séance Paris du jour J). Ces 8 tickers correspondent exactement à la collecte de l'Étape 1 de la routine.
