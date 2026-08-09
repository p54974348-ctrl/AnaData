#!/usr/bin/env python3
"""Collecteur automatique de données de marché — filet de sécurité sans IA.

Alimente docs/data/history.json avec les données officielles (Yahoo Finance,
repli Stooq) pour que le tableau de bord GitHub Pages continue de fonctionner
même si les routines Claude sont arrêtées.

Règles de fusion (le collecteur ne se bat jamais avec la routine) :
- record absent pour la dernière séance → il est créé entièrement ;
- record existant → seuls les champs null/ND sont remplis, jamais d'écrasement ;
- si la clôture existante diverge de plus de 0,1 % de la clôture officielle,
  une note de divergence est ajoutée (l'arbitrage éditorial reste à la routine) ;
- prevision_active : si elle vise la nouvelle séance, elle est copiée dans le
  record et le verdict mécanique est calculé (direction, intervalle, erreur) —
  l'attribution corrigeable/irréductible reste à la routine (type=null) ;
- metriques + benchmarks + metriques_historique : recalculés intégralement à
  partir des records (déterministe, idempotent) ;
- jamais touchés : lecons, suivi_dynamique, journal_suivi, hypothèses,
  prevision_active (sauf consommation ci-dessus), rapports/.

Usage : python3 scripts/collect.py [--dry-run] [--history CHEMIN]
Sortie : code 0 (mis à jour ou rien à faire) ; 1 (erreur fatale).
"""

import argparse
import datetime as dt
import json
import sys
import time
import urllib.request

HISTORY_DEFAULT = "docs/data/history.json"

# ticker Yahoo -> (clé contexte, libellé)
CONTEXT_TICKERS = {
    "^GSPC": ("sp500", "S&P 500"),
    "^VIX": ("vix", "VIX"),
    "^IXIC": ("nasdaq", "Nasdaq Composite"),
    "^GDAXI": ("dax", "DAX 40"),
    "^STOXX50E": ("stoxx50", "Euro Stoxx 50"),
    "^N225": ("nikkei", "Nikkei 225"),
    "^HSI": ("hangseng", "Hang Seng"),
}

# repli Stooq (symboles daily CSV) pour les tickers qui y existent
STOOQ_SYMBOLS = {"^FCHI": "^cac", "^GSPC": "^spx", "^IXIC": "^ndq",
                 "^GDAXI": "^dax", "^N225": "^nkx", "^HSI": "^hsi"}

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
COLLECT_NOTE = "Collecte automatique (GitHub Actions)"


def http_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 ** (i + 1))


def http_text(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 ** (i + 1))


def fetch_yfinance(ticker):
    """Source primaire : yfinance (impersonation navigateur — passe les 429
    que Yahoo inflige aux IP des runners GitHub Actions)."""
    import yfinance as yf
    df = yf.Ticker(ticker).history(period="1mo", interval="1d", auto_adjust=False)
    bars = {}
    for idx, row in df.iterrows():
        c = row.get("Close")
        if c is None or c != c:  # NaN
            continue
        o = row.get("Open")
        v = row.get("Volume")
        bars[idx.date().isoformat()] = {
            "open": None if o is None or o != o else float(o),
            "close": float(c),
            "volume": None if v is None or v != v or v == 0 else int(v),
        }
    return bars


def fetch_yahoo(ticker):
    """Barres quotidiennes {date: {open, close, volume}} en date locale de la place."""
    last = None
    for host in ("query1", "query2"):
        try:
            d = http_json("https://" + host + ".finance.yahoo.com/v8/finance/chart/"
                          + urllib.request.quote(ticker) + "?range=1mo&interval=1d")
            break
        except Exception as e:
            last = e
    else:
        raise last
    res = d["chart"]["result"][0]
    off = res["meta"].get("gmtoffset", 0)
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    bars = {}
    for i, t in enumerate(ts):
        c = q["close"][i]
        if c is None:
            continue
        date = (dt.datetime.fromtimestamp(t, dt.timezone.utc)
                + dt.timedelta(seconds=off)).date().isoformat()
        bars[date] = {"open": q["open"][i], "close": c, "volume": q["volume"][i]}
    return bars


def fetch_stooq(ticker):
    sym = STOOQ_SYMBOLS.get(ticker)
    if not sym:
        return {}
    url = "https://stooq.com/q/d/l/?s=" + urllib.request.quote(sym) + "&i=d"
    text = http_text(url).strip()
    lines = [l for l in text.splitlines() if l]
    if not lines or not lines[0].lower().startswith("date,open"):
        raise ValueError("réponse Stooq inattendue : " + text[:80].replace("\n", " "))
    bars = {}
    for l in lines[-25:]:
        p = l.split(",")
        try:
            bars[p[0]] = {"open": float(p[1]) if p[1] else None,
                          "close": float(p[4]),
                          "volume": int(float(p[5])) if len(p) > 5 and p[5] else None}
        except (ValueError, IndexError):
            continue
    return bars


def fetch_bars(ticker):
    try:
        bars = fetch_yfinance(ticker)
        if bars:
            return bars, "yfinance"
    except ImportError:
        pass
    except Exception as e:
        print(f"  {ticker}: yfinance KO ({e}), essai API brute", file=sys.stderr)
    try:
        bars = fetch_yahoo(ticker)
        if bars:
            return bars, "yahoo"
    except Exception as e:
        print(f"  {ticker}: Yahoo KO ({e}), essai Stooq", file=sys.stderr)
    try:
        bars = fetch_stooq(ticker)
        if bars:
            return bars, "stooq"
    except Exception as e:
        print(f"  {ticker}: Stooq KO ({e})", file=sys.stderr)
    return {}, None


def rnd(v, n=2):
    return None if v is None else round(v, n)


def pct(new, old):
    if new is None or old in (None, 0):
        return None
    return (new / old - 1.0) * 100.0


def is_nd(v):
    return v is None or v == "ND"


def prev_of(bars, date):
    prior = sorted(k for k in bars if k < date)
    return bars[prior[-1]] if prior else None


def next_business_day(iso):
    d = dt.date.fromisoformat(iso) + dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d.isoformat()


def mechanical_forecast(records, seance):
    """Prévision J+1 de secours, appliquant les règles codifiées par la routine IA :
    - direction : persistance (signe du jour), corrigée par le signal US fort
      (S&P < −0,5 % ⇒ baisse autorisée ; S&P > +0,5 % ⇒ hausse) — conforme à L7 ;
    - probabilité : plafonnée à 0,55 (L5 — les binaires du lendemain ne sont pas
      analysables mécaniquement) ;
    - intervalle 80 % : 1,28 × σ des ~20 derniers rendements, élargi selon le
      régime VIX (détecteur de régime, décision « σ20 réalisé » de l'Étape 5).
    """
    rec = next(r for r in records if r["date"] == seance)
    ret = rec.get("rendement_pct")
    if ret is None:
        return None
    sp = ((rec.get("contexte") or {}).get("sp500") or {}).get("var_pct")
    score = (1 if ret > 0 else -1 if ret < 0 else 0)
    if sp is not None:
        score += (1 if sp > 0.5 else -1 if sp < -0.5 else 0)
    direction = "hausse" if score >= 0 else "baisse"
    proba = {0: 0.52, 1: 0.54}.get(abs(score), 0.55)

    rets = [r["rendement_pct"] for r in records if r.get("rendement_pct") is not None][-20:]
    if len(rets) >= 5:
        mean = sum(rets) / len(rets)
        sigma = (sum((x - mean) ** 2 for x in rets) / (len(rets) - 1)) ** 0.5
        half = 1.28 * sigma
    else:
        half = 1.0
    vix = ((rec.get("contexte") or {}).get("vix") or {}).get("niveau")
    widen = 1.8 if (vix or 0) >= 25 else 1.4 if (vix or 0) >= 20 else 1.25
    half = max(0.8, round(half * widen, 1))

    return {
        "seance_cible": next_business_day(seance),
        "direction": direction,
        "probabilite": proba,
        "intervalle_80pct": [-half, half],
        "hypotheses": [
            f"H1 (mécanique, persistance/L7) : rendement du jour {ret:+.2f} %"
            + (f", S&P 500 {sp:+.2f} %" if sp is not None else "")
            + f" → direction « {direction} »",
            f"H2 (L5) : agenda et binaires du lendemain non analysables sans IA → probabilité plafonnée à {proba:.2f}",
            f"H3 (σ20/VIX) : σ des {len(rets)} derniers rendements × 1,28, élargi ×{widen}"
            + (f" (VIX {vix})" if vix is not None else " (VIX ND)")
            + f" → ±{half} %",
        ],
        "source": "mécanique (collecteur automatique) — modèle de secours codifié par la routine IA ; remplacée par la prévision IA si la routine tourne",
    }


def mechanical_metrics(records):
    """Recalcule metriques/benchmarks depuis les records évalués. Déterministe."""
    ev = [r for r in records if r.get("verdict") and r.get("prevision")
          and r["verdict"].get("direction_ok") is not None
          and r.get("rendement_pct") is not None]
    if not ev:
        return None
    n = len(ev)
    idx = {r["date"]: i for i, r in enumerate(records)}
    hits = mae = maen = cov = brier = pers = th = 0.0
    for r in ev:
        ret = r["rendement_pct"]
        lo, hi = r["prevision"]["intervalle_80pct"]
        p = r["prevision"]["probabilite"]
        p_h = p if r["prevision"]["direction"] == "hausse" else 1 - p
        up = ret > 0
        hits += 1 if r["verdict"]["direction_ok"] else 0
        mae += abs(ret - (lo + hi) / 2)
        maen += abs(ret)
        cov += 1 if lo <= ret <= hi else 0
        brier += (p_h - (1 if up else 0)) ** 2
        i = idx[r["date"]]
        prev_ret = records[i - 1].get("rendement_pct") if i > 0 else None
        if prev_ret is not None and (prev_ret > 0) == up:
            pers += 1
        if up:
            th += 1
    return {
        "n": n,
        "hit_rate": round(hits / n, 3),
        "mae_pct": round(mae / n, 2),
        "mae_naif_pct": round(maen / n, 2),
        "couverture_intervalle": round(cov / n, 3),
        "brier": round(brier / n, 4),
        "persistance": round(pers / n, 3),
        "toujours_hausse": round(th / n, 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default=HISTORY_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", help="fichier JSON {ticker: {date: {open,close,volume}}} pour tests hors ligne")
    args = ap.parse_args()

    with open(args.history, encoding="utf-8") as f:
        hist = json.load(f)

    if args.mock:
        with open(args.mock, encoding="utf-8") as f:
            mock = json.load(f)
        all_bars = {t: (mock.get(t, {}), "mock") for t in ["^FCHI"] + list(CONTEXT_TICKERS)}
    else:
        all_bars = {}
        for i, t in enumerate(["^FCHI"] + list(CONTEXT_TICKERS)):
            if i:
                time.sleep(1.5)  # espacer les requêtes (limites de débit Yahoo)
            all_bars[t] = fetch_bars(t)
            print(f"  {t}: {len(all_bars[t][0])} barres ({all_bars[t][1]})")

    cac_bars, cac_src = all_bars["^FCHI"]
    if not cac_bars:
        print("Aucune donnée CAC 40 disponible (Yahoo et Stooq KO) — abandon sans modification.", file=sys.stderr)
        return 1

    seance = max(cac_bars)
    bar = cac_bars[seance]
    prev = prev_of(cac_bars, seance)
    prev_close = prev["close"] if prev else None

    records = hist["records"]
    by_date = {r["date"]: r for r in records}
    changed = []

    if seance not in by_date:
        rec = {"date": seance, "cloture": None, "rendement_pct": None,
               "gap_pct": None, "intra_pct": None, "prevision": None,
               "verdict": None, "note": COLLECT_NOTE + f" — source {cac_src}.",
               "contexte": {}}
        # insertion triée par date
        pos = len([r for r in records if r["date"] < seance])
        records.insert(pos, rec)
        by_date[seance] = rec
        changed.append(f"record {seance} créé")
    rec = by_date[seance]

    # -- CAC : remplir les champs manquants uniquement
    close_off = rnd(bar["close"])
    if is_nd(rec.get("cloture")):
        rec["cloture"] = close_off
        changed.append(f"clôture {close_off}")
    elif close_off and abs(rec["cloture"] / close_off - 1) > 0.001:
        flag = f"⚠ divergence collecteur : clôture officielle {cac_src} {close_off} vs {rec['cloture']} enregistrée (>0,1 %) — à arbitrer."
        if flag not in (rec.get("note") or ""):
            rec["note"] = ((rec.get("note") or "").rstrip() + " " + flag).strip()
            changed.append("note de divergence")
    if is_nd(rec.get("rendement_pct")) and prev_close:
        rec["rendement_pct"] = rnd(pct(rec["cloture"], prev_close))
        changed.append(f"rendement {rec['rendement_pct']} %")
    if is_nd(rec.get("gap_pct")) and bar.get("open") and prev_close:
        rec["gap_pct"] = rnd(pct(bar["open"], prev_close))
        rec.setdefault("ouverture", rnd(bar["open"]))
        changed.append(f"gap {rec['gap_pct']} %")
    if is_nd(rec.get("intra_pct")) and bar.get("open") and rec.get("cloture"):
        rec["intra_pct"] = rnd(pct(rec["cloture"], bar["open"]))
        changed.append(f"intraséance {rec['intra_pct']} %")
    if is_nd(rec.get("volume")) and bar.get("volume"):
        rec["volume"] = bar["volume"]
        changed.append("volume")

    # -- Contexte : remplir niveau/var manquants pour la même date calendaire
    ctx = rec.setdefault("contexte", {})
    for ticker, (key, label) in CONTEXT_TICKERS.items():
        bars, src = all_bars.get(ticker, ({}, None))
        b = bars.get(seance)
        if not b:
            continue
        slot = ctx.setdefault(key, {"niveau": None, "var_pct": None, "note": ""})
        pb = prev_of(bars, seance)
        if is_nd(slot.get("niveau")):
            slot["niveau"] = rnd(b["close"])
            if is_nd(slot.get("var_pct")) and pb:
                slot["var_pct"] = rnd(pct(b["close"], pb["close"]))
            extra = f"clôture officielle ({src}, collecte automatique)"
            slot["note"] = (slot.get("note") or "").strip() or extra
            changed.append(f"contexte {key}")
        elif is_nd(slot.get("var_pct")) and pb:
            slot["var_pct"] = rnd(pct(b["close"], pb["close"]))
            changed.append(f"contexte {key} (var)")

    # -- Prévision active : consommation + verdict mécanique
    pa = hist.get("prevision_active")
    if (pa and pa.get("seance_cible") == seance and rec.get("prevision") is None
            and rec.get("rendement_pct") is not None):
        rec["prevision"] = {"direction": pa["direction"],
                            "probabilite": pa["probabilite"],
                            "intervalle_80pct": list(pa["intervalle_80pct"])}
        if pa.get("source"):
            rec["prevision"]["source"] = pa["source"]
        changed.append("prévision active consommée")
    if (rec.get("prevision") and rec.get("verdict") is None
            and rec.get("rendement_pct") is not None):
        ret = rec["rendement_pct"]
        lo, hi = rec["prevision"]["intervalle_80pct"]
        mid = (lo + hi) / 2
        rec["verdict"] = {
            "direction_ok": (ret > 0) == (rec["prevision"]["direction"] == "hausse"),
            "dans_intervalle": lo <= ret <= hi,
            "erreur_pct": rnd(abs(ret - mid)),
            "type": None,
            "cause": "évaluation mécanique (collecte automatique) — attribution corrigeable/irréductible à faire par la routine",
        }
        changed.append("verdict mécanique")

    # -- Prévision mécanique de secours : uniquement si la prévision active est
    # périmée (déjà consommée ou dépassée). La routine IA, si elle tourne,
    # la remplacera par sa propre prévision au run suivant.
    if pa is None or pa.get("seance_cible") <= seance:
        mf = mechanical_forecast(records, seance)
        # remplaçable : pas de prévision, prévision dépassée, ou prévision
        # mécanique antérieure (une prévision IA à jour n'est jamais écrasée)
        replaceable = (pa is None or pa.get("seance_cible") < mf["seance_cible"]
                       or bool(pa.get("source"))) if mf else False
        if mf and replaceable and pa != mf:
            hist["prevision_active"] = mf
            changed.append(f"prévision mécanique émise pour {mf['seance_cible']} "
                           f"({mf['direction']} p={mf['probabilite']})")

    # -- Métriques : recalcul intégral déterministe
    m = mechanical_metrics(records)
    if m:
        mtr = hist.setdefault("metriques", {})
        core = {"n": m["n"], "hit_rate": m["hit_rate"], "mae_pct": m["mae_pct"],
                "mae_naif_pct": m["mae_naif_pct"],
                "couverture_intervalle": m["couverture_intervalle"], "brier": m["brier"]}
        if any(mtr.get(k) != v for k, v in core.items()):
            mtr.update(core)
            changed.append(f"métriques (n={m['n']})")
        bm = mtr.setdefault("benchmarks", {})
        if (bm.get("hit_rate_persistance") != m["persistance"]
                or bm.get("hit_rate_toujours_hausse") != m["toujours_hausse"]):
            bm["hit_rate_persistance"] = m["persistance"]
            bm["hit_rate_toujours_hausse"] = m["toujours_hausse"]
            changed.append("benchmarks")
        mh = hist.setdefault("metriques_historique", [])
        entry = {"date": seance, "n": m["n"], "hit_rate": m["hit_rate"],
                 "mae_pct": m["mae_pct"], "mae_naif_pct": m["mae_naif_pct"],
                 "couverture": m["couverture_intervalle"], "brier": m["brier"]}
        # une entrée par date de séance évaluée ; on n'ajoute que si la séance a un verdict
        if by_date[seance].get("verdict") and not any(e["date"] == seance for e in mh):
            mh.append(entry)
            mh.sort(key=lambda e: e["date"])
            changed.append("metriques_historique")

    if not changed:
        print(f"Rien à faire : {seance} déjà complet.")
        return 0

    hist["derniere_maj"] = seance
    print(f"Séance {seance} — modifications : " + ", ".join(changed))
    if args.dry_run:
        print("(dry-run : fichier non écrit)")
        return 0
    with open(args.history, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
