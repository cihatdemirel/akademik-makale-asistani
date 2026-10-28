"""İleri istatistik modelleri: düzenleyicilik/koşullu aracılık, karma modeller, GEE, ANCOVA,
eksik veri (Little MCAR, çoklu atama), eğilim skoru, E-değeri, eşdeğerlik (TOST), ROC/kesme
noktası, uyum (ICC, kappa, Bland–Altman), meta-analiz, psikometri (CFA, CR/AVE/HTMT),
baskınlık analizi, kesintili zaman serisi.

    import sys; sys.path.insert(0, "<skill>/scripts"); import ileri_modeller as im
"""
from __future__ import annotations

import itertools
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


def _p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    return "< .001" if p < .001 else f"{p:.3f}".replace("0.", ".", 1)


def _sayisal(df, cols):
    return df[cols].apply(pd.to_numeric, errors="coerce").dropna()


# ============================================================ düzenleyicilik
def duzenleyicilik(df, x, w, y, kovaryatlar=None):
    """X×W etkileşimi (ortalamaya göre merkezlenmiş), basit eğimler ve Johnson–Neyman."""
    import statsmodels.formula.api as smf
    kov = kovaryatlar or []
    d = _sayisal(df, [x, w, y] + kov).copy()
    d["_x"], d["_w"] = d[x] - d[x].mean(), d[w] - d[w].mean()
    d["_xw"] = d["_x"] * d["_w"]
    ek = (" + " + " + ".join(f"Q('{k}')" for k in kov)) if kov else ""
    m0 = smf.ols(f"Q('{y}') ~ _x + _w{ek}", d).fit()
    m1 = smf.ols(f"Q('{y}') ~ _x + _w + _xw{ek}", d).fit()
    ci = m1.conf_int()
    kats = pd.DataFrame({"B": m1.params, "SE": m1.bse, "t": m1.tvalues,
                         "p": [_p(v) for v in m1.pvalues],
                         "%95 GA": [f"{ci.loc[i, 0]:.3f}, {ci.loc[i, 1]:.3f}" for i in m1.params.index]}).round(3)
    b1, b3 = m1.params["_x"], m1.params["_xw"]
    V = m1.cov_params()
    sd_w = d["_w"].std()
    egimler = []
    for ad, wv in [("−1 SS", -sd_w), ("Ortalama", 0.0), ("+1 SS", sd_w)]:
        est = b1 + b3 * wv
        se = np.sqrt(V.loc["_x", "_x"] + wv ** 2 * V.loc["_xw", "_xw"] + 2 * wv * V.loc["_x", "_xw"])
        t = est / se
        egimler.append({"W düzeyi": ad, "W değeri": round(wv + d[w].mean(), 2), "Eğim": round(est, 3),
                        "SE": round(se, 3), "p": _p(2 * stats.t.sf(abs(t), m1.df_resid)),
                        "%95 GA": f"{est - 1.96 * se:.3f}, {est + 1.96 * se:.3f}"})
    # Johnson–Neyman: (b1 + b3 w)^2 = t^2 * var(w)
    tc = stats.t.ppf(.975, m1.df_resid)
    a = b3 ** 2 - tc ** 2 * V.loc["_xw", "_xw"]
    b = 2 * (b1 * b3 - tc ** 2 * V.loc["_x", "_xw"])
    c = b1 ** 2 - tc ** 2 * V.loc["_x", "_x"]
    disk = b * b - 4 * a * c
    jn = []
    if disk >= 0 and a != 0:
        for r in sorted([(-b - np.sqrt(disk)) / (2 * a), (-b + np.sqrt(disk)) / (2 * a)]):
            jn.append(float(round(r + d[w].mean(), 3)))
    w_aralik = (float(round(d[w].min(), 2)), float(round(d[w].max(), 2)))
    return {"katsayilar": kats, "dR2": round(m1.rsquared - m0.rsquared, 4),
            "p_etkilesim": _p(m1.pvalues["_xw"]), "basit_egimler": pd.DataFrame(egimler),
            "johnson_neyman_W": jn, "W_gozlenen_aralik": w_aralik}


# ============================================================ aracılık türleri
def _ols_b(Xmat, yvec):
    X = np.column_stack([np.ones(len(yvec)), Xmat])
    return np.linalg.lstsq(X, yvec, rcond=None)[0]


def _ci(dagilim):
    return np.percentile(dagilim, [2.5, 97.5])


def seri_aracilik(df, x, m1, m2, y, kovaryatlar=None, n_boot=5000, seed=42):
    """X → M1 → M2 → Y (PROCESS Model 6). Dolaylı etkiler ve yüzdelik bootstrap GA."""
    kov = kovaryatlar or []
    d = _sayisal(df, [x, m1, m2, y] + kov).values
    rng = np.random.default_rng(seed)
    K = d[:, 4:] if kov else np.empty((len(d), 0))

    def hesap(D, Kk):
        X, M1, M2, Y = D[:, 0], D[:, 1], D[:, 2], D[:, 3]
        a1 = _ols_b(np.column_stack([X, Kk]), M1)[1]
        bm2 = _ols_b(np.column_stack([X, M1, Kk]), M2)
        a2, d21 = bm2[1], bm2[2]
        by = _ols_b(np.column_stack([X, M1, M2, Kk]), Y)
        cp, b1, b2 = by[1], by[2], by[3]
        return np.array([a1 * b1, a2 * b2, a1 * d21 * b2, a1 * b1 + a2 * b2 + a1 * d21 * b2, cp])

    est = hesap(d, K)
    boots = np.array([hesap(d[i], K[i]) for i in (rng.integers(0, len(d), len(d)) for _ in range(n_boot))])
    adlar = [f"X→{m1}→Y", f"X→{m2}→Y", f"X→{m1}→{m2}→Y", "Toplam dolaylı", "Doğrudan (c′)"]
    rows = []
    for i, ad in enumerate(adlar):
        lo, hi = _ci(boots[:, i])
        rows.append({"Etki": ad, "Tahmin": round(est[i], 4), "Boot SE": round(boots[:, i].std(), 4),
                     "%95 GA": f"{lo:.4f}, {hi:.4f}", "Anlamlı": "evet" if lo * hi > 0 else "hayır"})
    return pd.DataFrame(rows)


def kosullu_aracilik(df, x, m, y, w, model=7, kovaryatlar=None, n_boot=5000, seed=42):
    """Düzenlenmiş aracılık. model=7: W, X→M yolunu; model=14: W, M→Y yolunu düzenler.
    Koşullu dolaylı etkiler (W: −1SS, ort, +1SS) ve düzenlenmiş aracılık indeksi."""
    kov = kovaryatlar or []
    d = _sayisal(df, [x, m, y, w] + kov).copy()
    for c in (x, w, m):
        d[c] = d[c] - d[c].mean()
    D = d.values
    rng = np.random.default_rng(seed)
    sd_w = d[w].std()

    def hesap(A):
        X, M, Y, W = A[:, 0], A[:, 1], A[:, 2], A[:, 3]
        K = A[:, 4:]
        if model == 7:
            bm = _ols_b(np.column_stack([X, W, X * W, K]), M)
            a1, a3 = bm[1], bm[3]
            by = _ols_b(np.column_stack([X, M, K]), Y)
            b = by[2]
            cond = [(a1 + a3 * wv) * b for wv in (-sd_w, 0, sd_w)]
            indeks = a3 * b
        else:
            a = _ols_b(np.column_stack([X, K]), M)[1]
            by = _ols_b(np.column_stack([X, M, W, M * W, K]), Y)
            b1, b3 = by[2], by[4]
            cond = [a * (b1 + b3 * wv) for wv in (-sd_w, 0, sd_w)]
            indeks = a * b3
        return np.array(cond + [indeks])

    est = hesap(D)
    boots = np.array([hesap(D[rng.integers(0, len(D), len(D))]) for _ in range(n_boot)])
    adlar = ["Koşullu dolaylı (W −1 SS)", "Koşullu dolaylı (W ort.)", "Koşullu dolaylı (W +1 SS)",
             "Düzenlenmiş aracılık indeksi"]
    rows = []
    for i, ad in enumerate(adlar):
        lo, hi = _ci(boots[:, i])
        rows.append({"Etki": ad, "Tahmin": round(est[i], 4), "Boot SE": round(boots[:, i].std(), 4),
                     "%95 GA": f"{lo:.4f}, {hi:.4f}", "Anlamlı": "evet" if lo * hi > 0 else "hayır"})
    return pd.DataFrame(rows)


# ============================================================ RKÇ ve tekrarlı ölçüm
def ancova(df, y, grup, kovaryatlar):
    import pingouin as pg
    d = df[[y, grup] + kovaryatlar].dropna()
    r = pg.ancova(data=d, dv=y, between=grup, covar=kovaryatlar)
    import statsmodels.formula.api as smf
    m = smf.ols(f"Q('{y}') ~ C(Q('{grup}')) + " + " + ".join(f"Q('{k}')" for k in kovaryatlar), d).fit()
    ort = {k: d[k].mean() for k in kovaryatlar}
    dz = []
    for g in d[grup].unique():
        satir = pd.DataFrame([{**ort, grup: g}])
        pr = m.get_prediction(satir).summary_frame()
        dz.append({"Grup": g, "Düzeltilmiş ort.": round(pr["mean"].iloc[0], 2),
                   "SE": round(pr["mean_se"].iloc[0], 2),
                   "%95 GA": f"{pr['mean_ci_lower'].iloc[0]:.2f}, {pr['mean_ci_upper'].iloc[0]:.2f}"})
    return {"ancova": r.round(4), "duzeltilmis_ortalamalar": pd.DataFrame(dz)}


def karma_model(df_uzun, y, zaman, grup, kimlik, rastgele_egim=False):
    """Doğrusal karma model: y ~ grup * zaman + (1 | kimlik). Uzun formatta veri ister.
    RKÇ'de ITT analizi için önerilir; eksik ölçümü olan katılımcıları dışlamaz."""
    import statsmodels.formula.api as smf
    d = df_uzun[[y, zaman, grup, kimlik]].dropna()
    f = f"Q('{y}') ~ C(Q('{grup}')) * C(Q('{zaman}'))"
    m = smf.mixedlm(f, d, groups=d[kimlik], re_formula=f"~Q('{zaman}')" if rastgele_egim else None)
    r = m.fit(reml=True, method="lbfgs")
    ci = r.conf_int()
    tab = pd.DataFrame({"B": r.params, "SE": r.bse, "z": r.tvalues, "p": [_p(v) for v in r.pvalues],
                        "%95 GA": [f"{ci.loc[i, 0]:.3f}, {ci.loc[i, 1]:.3f}" for i in r.params.index]})
    return {"sabit_etkiler": tab.round(3), "n_gozlem": int(r.nobs), "n_kisi": d[kimlik].nunique(),
            "AIC": round(r.aic, 2) if r.aic == r.aic else "REML: AIC yok", "uyari": "Etkileşim terimleri grup×zaman farkını gösterir."}


def gee(df_uzun, y, X, kimlik, aile="gaussian", korelasyon="exchangeable"):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    d = df_uzun[[y, kimlik] + X].dropna()
    fam = {"gaussian": sm.families.Gaussian(), "binomial": sm.families.Binomial(),
           "poisson": sm.families.Poisson()}[aile]
    cs = {"exchangeable": sm.cov_struct.Exchangeable(), "ar1": sm.cov_struct.Autoregressive(),
          "independence": sm.cov_struct.Independence()}[korelasyon]
    r = smf.gee(f"Q('{y}') ~ " + " + ".join(f"Q('{v}')" for v in X), kimlik, d, family=fam, cov_struct=cs).fit()
    ci = r.conf_int()
    tab = pd.DataFrame({"B": r.params, "Robust SE": r.bse, "p": [_p(v) for v in r.pvalues],
                        "%95 GA": [f"{ci.loc[i, 0]:.3f}, {ci.loc[i, 1]:.3f}" for i in r.params.index]})
    if aile in ("binomial", "poisson"):
        tab["exp(B)"] = np.exp(r.params).round(3)
    return tab.round(3)


def tost(x1, x2, sinir, bagimli=False):
    """Eşdeğerlik testi (iki tek yönlü test). sinir: ham ölçekte eşdeğerlik sınırı (±)."""
    import pingouin as pg
    return pg.tost(np.asarray(x1, float), np.asarray(x2, float), bound=sinir, paired=bagimli).round(4)


# ============================================================ eksik veri
def little_mcar(df, cols):
    """Little'ın MCAR testi (EM tahminleri yerine çift yönlü silme ortalaması/kovaryansı ile yaklaşık)."""
    d = df[cols].apply(pd.to_numeric, errors="coerce")
    mu = d.mean().values
    S = d.cov().values
    desen = d.isna()
    toplam, sd = 0.0, 0
    for _, grup in d.groupby(desen.apply(lambda r: tuple(r), axis=1)):
        gozlenen = ~grup.isna().iloc[0].values
        if gozlenen.sum() == 0:
            continue
        nj = len(grup)
        fark = grup.values[:, gozlenen].mean(axis=0) - mu[gozlenen]
        Sj = S[np.ix_(gozlenen, gozlenen)]
        toplam += nj * fark @ np.linalg.pinv(Sj) @ fark
        sd += gozlenen.sum()
    sd -= len(cols)
    p = stats.chi2.sf(toplam, sd) if sd > 0 else np.nan
    return pd.DataFrame([{"χ²": round(toplam, 2), "sd": sd, "p": _p(p), "Eksik desen sayısı":
                          desen.drop_duplicates().shape[0], "Toplam eksik %": round(desen.values.mean() * 100, 2),
                          "Yorum": "MCAR reddedilmedi" if p > .05 else "MCAR reddedildi (MAR/MNAR olası)"}])


def coklu_atama_ols(df, y, X, m=20, n_burn=10, seed=42):
    """Zincirleme denklemlerle çoklu atama (MICE) + Rubin kurallarıyla birleştirilmiş OLS."""
    from statsmodels.imputation import mice
    import statsmodels.api as sm
    np.random.seed(seed)
    d = df[[y] + X].apply(pd.to_numeric, errors="coerce")
    d.columns = [f"v{i}" for i in range(len(d.columns))]
    harita = dict(zip(d.columns, [y] + X))
    imp = mice.MICEData(d)
    formul = "v0 ~ " + " + ".join(d.columns[1:])
    r = mice.MICE(formul, sm.OLS, imp).fit(n_burn, m)
    ci = r.conf_int()
    adlar = ["Sabit"] + [harita[c] for c in d.columns[1:]]
    return pd.DataFrame({"Değişken": adlar, "B": np.round(r.params, 3), "SE": np.round(r.bse, 3),
                         "p": [_p(v) for v in r.pvalues],
                         "%95 GA": [f"{a:.3f}, {b:.3f}" for a, b in np.asarray(ci)],
                         "FMI": np.round(r.frac_miss_info, 3)})


# ============================================================ nedensel çıkarım
def egilim_skoru(df, tedavi, kovaryatlar, y=None, kaliper=0.2, seed=42):
    """1:1 en yakın komşu eşleştirme (logit PS, kaliper=0.2×SS) + IPTW. SMD denge tablosu."""
    from sklearn.linear_model import LogisticRegression
    d = df[[tedavi] + kovaryatlar + ([y] if y else [])].dropna().reset_index(drop=True)
    X = pd.get_dummies(d[kovaryatlar], drop_first=True).astype(float)
    T = d[tedavi].astype(int).values
    ps = LogisticRegression(max_iter=2000, C=1e6).fit(X, T).predict_proba(X)[:, 1]
    lg = np.log(ps / (1 - ps))
    cap = kaliper * lg.std()
    rng = np.random.default_rng(seed)
    tedavili = rng.permutation(np.where(T == 1)[0])
    kontrol = set(np.where(T == 0)[0])
    ciftler = []
    for i in tedavili:
        if not kontrol:
            break
        k = np.array(sorted(kontrol))
        j = k[np.argmin(np.abs(lg[k] - lg[i]))]
        if abs(lg[j] - lg[i]) <= cap:
            ciftler.append((i, j))
            kontrol.remove(j)
    idx = [a for p in ciftler for a in p]

    def smd(XX, TT, w=None):
        w = np.ones(len(TT)) if w is None else w
        out = {}
        for c in XX.columns:
            v = XX[c].values
            m1 = np.average(v[TT == 1], weights=w[TT == 1]); m0 = np.average(v[TT == 0], weights=w[TT == 0])
            s = np.sqrt((v[TT == 1].var(ddof=1) + v[TT == 0].var(ddof=1)) / 2)
            out[c] = (m1 - m0) / s if s > 0 else 0
        return out
    w_iptw = np.where(T == 1, 1 / ps, 1 / (1 - ps))
    denge = pd.DataFrame({"SMD önce": smd(X, T), "SMD eşleştirme sonrası": smd(X.iloc[idx], T[idx]),
                          "SMD IPTW": smd(X, T, w_iptw)}).round(3)
    sonuc = {"denge": denge, "eslesen_cift": len(ciftler), "tedavili_n": int(T.sum()),
             "not": "|SMD| < 0.10 iyi denge kabul edilir."}
    if y:
        yv = d[y].astype(float).values
        att = yv[[a for a, _ in ciftler]].mean() - yv[[b for _, b in ciftler]].mean()
        ate = np.average(yv[T == 1], weights=w_iptw[T == 1]) - np.average(yv[T == 0], weights=w_iptw[T == 0])
        sonuc["etki"] = pd.DataFrame([{"ATT (eşleştirme) fark": round(att, 3), "ATE (IPTW) fark": round(ate, 3)}])
    return sonuc


def e_degeri(tahmin, gu_alt=None, tur="RR", olay_nadir=True):
    """VanderWeele & Ding E-değeri. tur: RR | OR (nadir olayda RR≈OR; yaygınsa √OR dönüşümü)."""
    def ev(rr):
        rr = 1 / rr if rr < 1 else rr
        return rr + np.sqrt(rr * (rr - 1))
    donus = (lambda v: v) if (tur == "RR" or olay_nadir) else (lambda v: np.sqrt(v))
    rr = donus(tahmin)
    out = {"E-değeri (tahmin)": round(ev(rr), 2)}
    if gu_alt is not None:
        g = donus(gu_alt)
        out["E-değeri (GA sınırı)"] = 1.0 if (rr > 1 and g <= 1) or (rr < 1 and g >= 1) else round(ev(g), 2)
    return pd.DataFrame([out])


def kesintili_zaman_serisi(df, y, zaman, mudahale_zamani, gecikme=1):
    """Bölümlü regresyon (Newey–West SE): düzey ve eğim değişimi."""
    import statsmodels.formula.api as smf
    d = df[[y, zaman]].dropna().sort_values(zaman).copy()
    d["sonra"] = (d[zaman] >= mudahale_zamani).astype(int)
    d["sonra_zaman"] = np.where(d["sonra"] == 1, d[zaman] - mudahale_zamani, 0)
    r = smf.ols(f"Q('{y}') ~ Q('{zaman}') + sonra + sonra_zaman", d).fit(cov_type="HAC", cov_kwds={"maxlags": gecikme})
    ci = r.conf_int()
    return pd.DataFrame({"B": r.params, "SE": r.bse, "p": [_p(v) for v in r.pvalues],
                         "%95 GA": [f"{ci.loc[i, 0]:.3f}, {ci.loc[i, 1]:.3f}" for i in r.params.index]},
                        ).rename(index={"sonra": "Düzey değişimi", "sonra_zaman": "Eğim değişimi"}).round(3)


# ============================================================ tanı / uyum
def roc_kesme(y, skor, n_boot=2000, seed=42):
    from sklearn.metrics import roc_auc_score, roc_curve
    y, skor = np.asarray(y), np.asarray(skor, float)
    auc = roc_auc_score(y, skor)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) == 2:
            bs.append(roc_auc_score(y[i], skor[i]))
    fpr, tpr, th = roc_curve(y, skor)
    j = np.argmax(tpr - fpr)
    return pd.DataFrame([{"AUC": round(auc, 3), "%95 GA": "{:.3f}, {:.3f}".format(*np.percentile(bs, [2.5, 97.5])),
                          "Youden kesme noktası (≥)": round(th[j], 3), "Duyarlılık": round(tpr[j], 3),
                          "Özgüllük": round(1 - fpr[j], 3), "Youden J": round(tpr[j] - fpr[j], 3)}])


def icc(df_uzun, hedef, degerlendirici, puan):
    import pingouin as pg
    return pg.intraclass_corr(data=df_uzun, targets=hedef, raters=degerlendirici, ratings=puan).round(3)


def kappa(r1, r2, agirlik=None):
    from sklearn.metrics import cohen_kappa_score
    return round(cohen_kappa_score(r1, r2, weights=agirlik), 3)


def bland_altman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    f = a - b
    m, s = f.mean(), f.std(ddof=1)
    return pd.DataFrame([{"Ortalama fark (yanlılık)": round(m, 3), "Alt uyum sınırı": round(m - 1.96 * s, 3),
                          "Üst uyum sınırı": round(m + 1.96 * s, 3),
                          "Orantısal yanlılık p": _p(stats.linregress((a + b) / 2, f).pvalue)}])


# ============================================================ meta-analiz
def hedges_g(m1, s1, n1, m2, s2, n2):
    """Ortalama/SS/n'den Hedges g ve varyansı."""
    sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    d = (m1 - m2) / sp
    J = 1 - 3 / (4 * (n1 + n2) - 9)
    g = J * d
    v = J ** 2 * ((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return g, v


def meta_analiz(etki, varyans, calismalar=None, yontem="REML", hksj=True):
    """Rastgele etkiler meta-analizi. yontem: REML | DL. hksj: Hartung–Knapp–Sidik–Jonkman GA.
    Çıktı: birleşik etki, GA, tahmin aralığı, τ², I², Q, Egger testi (k ≥ 10 önerilir)."""
    y, v = np.asarray(etki, float), np.asarray(varyans, float)
    k = len(y)
    w = 1 / v
    mu_fe = np.sum(w * y) / w.sum()
    Q = np.sum(w * (y - mu_fe) ** 2)
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c)
    if yontem == "REML":
        for _ in range(200):
            wr = 1 / (v + tau2)
            mu = np.sum(wr * y) / wr.sum()
            yeni = max(0.0, np.sum(wr ** 2 * ((y - mu) ** 2 - v)) / np.sum(wr ** 2) + 1 / wr.sum())
            if abs(yeni - tau2) < 1e-10:
                break
            tau2 = yeni
    wr = 1 / (v + tau2)
    mu = np.sum(wr * y) / wr.sum()
    se = np.sqrt(1 / wr.sum())
    if hksj and k > 1:
        q = np.sum(wr * (y - mu) ** 2) / (k - 1)
        se = np.sqrt(q / wr.sum())
        kr = stats.t.ppf(.975, k - 1)
        p = 2 * stats.t.sf(abs(mu / se), k - 1)
    else:
        kr = 1.96
        p = 2 * stats.norm.sf(abs(mu / se))
    I2 = max(0.0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0.0
    pi_t = stats.t.ppf(.975, k - 2) if k > 2 else np.nan
    pi = (mu - pi_t * np.sqrt(tau2 + se ** 2), mu + pi_t * np.sqrt(tau2 + se ** 2))
    hassasiyet = 1 / np.sqrt(v)
    if k > 2 and np.ptp(hassasiyet) > 1e-12:
        eg = stats.linregress(hassasiyet, y / np.sqrt(v))
        eg_p = 2 * stats.t.sf(abs(eg.intercept / eg.intercept_stderr), k - 2)
    else:
        eg_p = np.nan
    ozet = pd.DataFrame([{"k": k, "Birleşik etki": round(mu, 3), "SE": round(se, 3),
                          "%95 GA": f"{mu - kr * se:.3f}, {mu + kr * se:.3f}", "p": _p(p),
                          "%95 Tahmin aralığı": f"{pi[0]:.3f}, {pi[1]:.3f}" if k > 2 else "k<3",
                          "τ²": round(tau2, 4), "I² %": round(I2, 1), "Q": round(Q, 2),
                          "Q p": _p(stats.chi2.sf(Q, k - 1)), "Egger p": _p(eg_p) + (" (k<10: yorumlama)" if k < 10 else ""),
                          "Yöntem": f"{yontem}{' + HKSJ' if hksj else ''}"}])
    tek = pd.DataFrame({"Çalışma": calismalar or [f"Ç{i + 1}" for i in range(k)], "Etki": y.round(3),
                        "%95 GA": [f"{a - 1.96 * np.sqrt(b):.3f}, {a + 1.96 * np.sqrt(b):.3f}" for a, b in zip(y, v)],
                        "Ağırlık %": (wr / wr.sum() * 100).round(1)})
    return {"ozet": ozet, "calismalar": tek, "_mu": mu, "_ci": (mu - kr * se, mu + kr * se)}


def orman_grafigi(sonuc, yol, etiket="Hedges g"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = sonuc["calismalar"]
    k = len(t)
    fig, ax = plt.subplots(figsize=(7, 0.45 * k + 1.6))
    for i, r in t.iterrows():
        lo, hi = map(float, r["%95 GA"].split(", "))
        yy = k - i
        ax.plot([lo, hi], [yy, yy], color="black", lw=1)
        ax.plot(r["Etki"], yy, "s", color="black", ms=3 + r["Ağırlık %"] / 4)
    mu, (lo, hi) = sonuc["_mu"], sonuc["_ci"]
    ax.fill([lo, mu, hi, mu], [0, 0.3, 0, -0.3], color="black")
    ax.axvline(0, color="grey", ls="--", lw=.8)
    ax.set_yticks(list(range(k, 0, -1)) + [0]); ax.set_yticklabels(list(t["Çalışma"]) + ["Rastgele etkiler"])
    ax.set_xlabel(etiket); fig.tight_layout(); fig.savefig(yol, dpi=300); plt.close(fig)
    return yol


# ============================================================ psikometri
def dfa(df, model_tanimi):
    """Doğrulayıcı faktör analizi (semopy). model_tanimi: 'F1 =~ m1 + m2 + m3\\nF2 =~ m4 + m5 + m6'."""
    import semopy
    m = semopy.Model(model_tanimi)
    m.fit(df)
    st = semopy.calc_stats(m).T
    uyum = st.loc[["chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA", "GFI", "AIC", "BIC"]].T.round(3)
    est = m.inspect(std_est=True)
    yuk = est[est["op"] == "~"][["lval", "rval", "Estimate", "Est. Std", "p-value"]]
    yuk = yuk.rename(columns={"lval": "Madde", "rval": "Faktör", "Est. Std": "Std. yük", "p-value": "p"})
    return {"uyum": uyum, "yukler": yuk.round(3), "not": "Ölçüt: CFI/TLI ≥ .90 (≥ .95 iyi), RMSEA ≤ .08 (≤ .06 iyi), SRMR ≤ .08."}


def cr_ave(std_yukler: dict):
    """{'F1': [yükler], ...} → Bileşik güvenirlik (CR) ve açıklanan ortalama varyans (AVE)."""
    rows = []
    for f, l in std_yukler.items():
        l = np.asarray(l, float)
        cr = l.sum() ** 2 / (l.sum() ** 2 + (1 - l ** 2).sum())
        rows.append({"Faktör": f, "CR": round(cr, 3), "AVE": round((l ** 2).mean(), 3),
                     "√AVE": round(np.sqrt((l ** 2).mean()), 3)})
    return pd.DataFrame(rows)


def htmt(df, faktorler: dict):
    """Heterotrait–monotrait oranı (ayırt edici geçerlik; < .85 veya < .90)."""
    R = df[[m for v in faktorler.values() for m in v]].corr().abs()
    adlar = list(faktorler)
    out = pd.DataFrame(index=adlar, columns=adlar, dtype=float)
    for a, b in itertools.combinations(adlar, 2):
        het = R.loc[faktorler[a], faktorler[b]].values.mean()
        def mono(f):
            sub = R.loc[faktorler[f], faktorler[f]].values
            return sub[np.triu_indices_from(sub, 1)].mean()
        out.loc[b, a] = round(het / np.sqrt(mono(a) * mono(b)), 3)
    return out


# ============================================================ göreli önem
def baskinlik_analizi(df, y, X):
    """Genel baskınlık ağırlıkları (Budescu). ≤ 12 yordayıcı önerilir."""
    import statsmodels.api as sm
    d = _sayisal(df, [y] + X)
    def r2(alt):
        if not alt:
            return 0.0
        return sm.OLS(d[y], sm.add_constant(d[list(alt)])).fit().rsquared
    cache = {}
    for k in range(len(X) + 1):
        for s in itertools.combinations(X, k):
            cache[frozenset(s)] = r2(s)
    agirlik = {}
    for x in X:
        digerleri = [v for v in X if v != x]
        katki = []
        for k in range(len(digerleri) + 1):
            katki.append(np.mean([cache[frozenset(s) | {x}] - cache[frozenset(s)]
                                  for s in itertools.combinations(digerleri, k)]))
        agirlik[x] = np.mean(katki)
    toplam = cache[frozenset(X)]
    return pd.DataFrame({"Genel baskınlık": agirlik}).assign(
        **{"R² içindeki pay %": lambda t: (t["Genel baskınlık"] / toplam * 100).round(1)}
    ).round(4).sort_values("Genel baskınlık", ascending=False)
