"""Sağlık bilimleri makaleleri için istatistik yardımcıları.

İçe aktarma:
    import sys; sys.path.insert(0, "<skill>/scripts"); import istatistik as ist

Tüm fonksiyonlar pandas.DataFrame döndürür. Gerekli paketler: pandas, numpy, scipy,
statsmodels, pingouin (opsiyonel: pyreadstat .sav için).
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------- yükleme
def yukle(yol: str):
    """(.sav | .xlsx | .xls | .csv) dosyasını yükler. (df, etiketler) döndürür."""
    p = Path(yol)
    etiketler = {}
    if p.suffix.lower() == ".sav":
        import pyreadstat
        df, meta = pyreadstat.read_sav(str(p))
        etiketler = {"degisken": meta.column_names_to_labels, "deger": meta.variable_value_labels}
    elif p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p, sep=None, engine="python")
    return df, etiketler


def veri_ozeti(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        s = df[c]
        rows.append({
            "Değişken": c, "Tip": str(s.dtype), "n": int(s.notna().sum()),
            "Eksik": int(s.isna().sum()), "Eksik %": round(s.isna().mean() * 100, 1),
            "Benzersiz": int(s.nunique()),
            "Min": s.min() if pd.api.types.is_numeric_dtype(s) else "",
            "Maks": s.max() if pd.api.types.is_numeric_dtype(s) else "",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- tanımlayıcı
def tanimlayici(df, degiskenler):
    rows = []
    for v in degiskenler:
        s = pd.to_numeric(df[v], errors="coerce").dropna()
        q1, q3 = s.quantile([.25, .75])
        rows.append({
            "Değişken": v, "n": len(s), "Ort": round(s.mean(), 2), "SS": round(s.std(ddof=1), 2),
            "Medyan": round(s.median(), 2), "ÇAA": f"{q1:.2f}–{q3:.2f}",
            "Min–Maks": f"{s.min():.2f}–{s.max():.2f}",
            "Çarpıklık": round(stats.skew(s, bias=False), 2),
            "Basıklık": round(stats.kurtosis(s, bias=False), 2),
        })
    return pd.DataFrame(rows)


def kategorik_tablo(df, degiskenler):
    rows = []
    for v in degiskenler:
        vc = df[v].value_counts(dropna=False)
        for k, n in vc.items():
            rows.append({"Değişken": v, "Kategori": k, "n": int(n),
                         "%": round(n / vc.sum() * 100, 1)})
    return pd.DataFrame(rows)


def normallik_karari(x):
    """Kim (2013) ölçütü: n<50 |z| < 1.96; 50≤n<300 |z| < 3.29 (çarpıklık ve basıklık z-puanı);
    n≥300 |çarpıklık| ≤ 2 ve |fazla basıklık| ≤ 7. Shapiro–Wilk bilgi amaçlı raporlanır."""
    x = pd.Series(x).dropna().astype(float).values
    n = len(x)
    if n < 8:
        return {"n": n, "normal": None, "kural": "n < 8: değerlendirilemez"}
    sk, ku = stats.skew(x, bias=False), stats.kurtosis(x, bias=False)
    se_sk = np.sqrt(6 * n * (n - 1) / ((n - 2) * (n + 1) * (n + 3)))
    se_ku = 2 * se_sk * np.sqrt((n ** 2 - 1) / ((n - 3) * (n + 5)))
    zs, zk = sk / se_sk, ku / se_ku
    if n < 50:
        ok, kural = abs(zs) < 1.96 and abs(zk) < 1.96, "n<50: |z| < 1.96"
    elif n < 300:
        ok, kural = abs(zs) < 3.29 and abs(zk) < 3.29, "50≤n<300: |z| < 3.29"
    else:
        ok, kural = abs(sk) <= 2 and abs(ku) <= 7, "n≥300: |çarpıklık| ≤ 2, |basıklık| ≤ 7"
    sw = stats.shapiro(x)[1] if n <= 5000 else np.nan
    return {"n": n, "carpiklik": round(sk, 2), "basiklik": round(ku, 2), "z_carpiklik": round(zs, 2),
            "z_basiklik": round(zk, 2), "shapiro_p": round(sw, 3) if sw == sw else None,
            "normal": bool(ok), "kural": kural + " (Kim, 2013)"}


def normallik(df, degiskenler):
    rows = []
    for v in degiskenler:
        k = normallik_karari(pd.to_numeric(df[v], errors="coerce"))
        rows.append({"Değişken": v, "n": k["n"], "Çarpıklık": k.get("carpiklik"), "z": k.get("z_carpiklik"),
                     "Basıklık": k.get("basiklik"), "z ": k.get("z_basiklik"), "Shapiro p": k.get("shapiro_p"),
                     "Karar": {True: "normal kabul", False: "normal değil", None: "değerlendirilemez"}[k["normal"]],
                     "Kural": k["kural"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- karşılaştırma
def _k(df, *adlar):
    """pingouin sürümleri arası sütun adı farkını giderir (p-val / p_val vb.)."""
    for a in adlar:
        for c in (a, a.replace("-", "_"), a.replace("%", "")):
            if c in df.columns:
                return df[c]
    raise KeyError(adlar)


def _normal_mi(x):
    return bool(normallik_karari(x)["normal"])


def grup_karsilastir(df, bagimli, grup, parametrik: bool | None = None):
    """Bağımsız gruplar. Varsayımlara göre test seçer ve etki büyüklüğü verir."""
    import pingouin as pg
    d = df[[bagimli, grup]].dropna()
    gruplar = [g[bagimli].values for _, g in d.groupby(grup)]
    adlar = list(d.groupby(grup).groups.keys())
    if parametrik is None:
        parametrik = all(_normal_mi(g) for g in gruplar)
    ozet = d.groupby(grup)[bagimli].agg(n="count", Ort="mean", SS="std", Medyan="median").round(2)
    sonuc = {}
    if len(gruplar) == 2:
        if parametrik:
            lev_p = stats.levene(*gruplar).pvalue
            r = pg.ttest(gruplar[0], gruplar[1], correction=lev_p < .05)
            sonuc = {"Test": "Welch t" if lev_p < .05 else "Bağımsız t",
                     "İstatistik": round(float(r["T"].iloc[0]), 2), "sd": round(float(r["dof"].iloc[0]), 2),
                     "p": float(_k(r, "p-val").iloc[0]), "Etki": f"d = {float(_k(r, 'cohen-d').iloc[0]):.2f}",
                     "%95 GA (fark)": "{:.2f}, {:.2f}".format(*_k(r, "CI95%").iloc[0]), "Levene p": round(lev_p, 3)}
        else:
            u, p = stats.mannwhitneyu(gruplar[0], gruplar[1], alternative="two-sided")
            n1, n2 = len(gruplar[0]), len(gruplar[1])
            z = stats.norm.isf(p / 2)
            sonuc = {"Test": "Mann–Whitney U", "İstatistik": round(u, 1), "sd": "",
                     "p": p, "Etki": f"r = {z / np.sqrt(n1 + n2):.2f}", "z": round(z, 2)}
    else:
        if parametrik:
            lev_p = stats.levene(*gruplar).pvalue
            if lev_p < .05:
                r = pg.welch_anova(data=d, dv=bagimli, between=grup)
                post = pg.pairwise_gameshowell(data=d, dv=bagimli, between=grup)
                ad = "Welch ANOVA (+ Games–Howell)"
            else:
                r = pg.anova(data=d, dv=bagimli, between=grup, detailed=False)
                post = pg.pairwise_tukey(data=d, dv=bagimli, between=grup)
                ad = "Tek yönlü ANOVA (+ Tukey)"
            sonuc = {"Test": ad, "İstatistik": round(float(r["F"].iloc[0]), 2),
                     "sd": f"{r['ddof1'].iloc[0]:.0f}, {r['ddof2'].iloc[0]:.2f}",
                     "p": float(_k(r, "p-unc").iloc[0]), "Etki": f"η² = {float(r['np2'].iloc[0]):.3f}",
                     "Levene p": round(lev_p, 3)}
        else:
            h, p = stats.kruskal(*gruplar)
            n = sum(len(g) for g in gruplar)
            eps2 = h / ((n ** 2 - 1) / (n + 1))
            post = pg.pairwise_tests(data=d, dv=bagimli, between=grup, parametric=False, padjust="holm")
            sonuc = {"Test": "Kruskal–Wallis (+ Holm düzeltmeli ikili)", "İstatistik": round(h, 2),
                     "sd": len(gruplar) - 1, "p": p, "Etki": f"ε² = {eps2:.3f}"}
        sonuc["post_hoc"] = post
    sonuc["p"] = _p(sonuc["p"])
    post_hoc = sonuc.pop("post_hoc", None)
    out = {"ozet": ozet, "test": pd.DataFrame([sonuc])}
    if post_hoc is not None:
        out["post_hoc"] = post_hoc
    return out


def bagimli_karsilastir(df, once, sonra, parametrik: bool | None = None):
    import pingouin as pg
    d = df[[once, sonra]].dropna()
    fark = d[sonra] - d[once]
    if parametrik is None:
        parametrik = _normal_mi(fark)
    if parametrik:
        r = pg.ttest(d[sonra], d[once], paired=True)
        res = {"Test": "Bağımlı t", "İstatistik": round(float(r["T"].iloc[0]), 2),
               "sd": int(r["dof"].iloc[0]), "p": _p(float(_k(r, "p-val").iloc[0])),
               "Etki": f"d = {float(_k(r, 'cohen-d').iloc[0]):.2f}"}
    else:
        w, p = stats.wilcoxon(d[sonra], d[once])
        z = stats.norm.isf(p / 2)
        res = {"Test": "Wilcoxon", "İstatistik": round(w, 1), "sd": "", "p": _p(p),
               "Etki": f"r = {z / np.sqrt(len(d)):.2f}"}
    return pd.DataFrame([res])


def ki_kare(df, a, b):
    tab = pd.crosstab(df[a], df[b])
    chi2, p, dof, beklenen = stats.chi2_contingency(tab, correction=False)
    n = tab.values.sum()
    v = np.sqrt(chi2 / (n * (min(tab.shape) - 1)))
    test = "Ki-kare"
    if (beklenen < 5).mean() > .2 and tab.shape == (2, 2):
        _, p = stats.fisher_exact(tab)
        test = "Fisher kesin"
    return {"tablo": tab, "test": pd.DataFrame([{
        "Test": test, "χ²": round(chi2, 2), "sd": dof, "N": n, "p": _p(p),
        "Cramér V": round(v, 3), "Beklenen<5 hücre %": round((beklenen < 5).mean() * 100, 1)}])}


# ---------------------------------------------------------------- ilişki
def korelasyon(df, degiskenler, yontem="pearson"):
    d = df[degiskenler].apply(pd.to_numeric, errors="coerce")
    r = pd.DataFrame(index=degiskenler, columns=degiskenler, dtype=object)
    for i, a in enumerate(degiskenler):
        for j, b in enumerate(degiskenler):
            if j > i:
                r.loc[a, b] = ""
                continue
            if a == b:
                r.loc[a, b] = "1"
                continue
            x = d[[a, b]].dropna()
            f = stats.pearsonr if yontem == "pearson" else stats.spearmanr
            rv, p = f(x[a], x[b])
            yildiz = "**" if p < .01 else "*" if p < .05 else ""
            r.loc[a, b] = f"{rv:.2f}{yildiz}".replace("0.", ".", 1) if rv >= 0 else f"{rv:.2f}{yildiz}".replace("-0.", "-.", 1)
    return r


def _omega_tek_faktor(d, iter_=200):
    """Tek faktörlü temel eksen faktörlemesiyle (PAF) McDonald ω_total."""
    try:
        R = np.corrcoef(d.values, rowvar=False)
        h2 = 1 - 1 / np.diag(np.linalg.inv(R))
        for _ in range(iter_):
            Rr = R.copy(); np.fill_diagonal(Rr, h2)
            val, vec = np.linalg.eigh(Rr)
            l = vec[:, -1] * np.sqrt(max(val[-1], 0))
            yeni = np.clip(l ** 2, 0, 0.999)
            if np.max(np.abs(yeni - h2)) < 1e-6:
                break
            h2 = yeni
        l = np.abs(l)
        return float(l.sum() ** 2 / (l.sum() ** 2 + (1 - l ** 2).sum()))
    except Exception:
        return np.nan


def guvenirlik(df, maddeler):
    import pingouin as pg
    d = df[maddeler].apply(pd.to_numeric, errors="coerce").dropna()
    alpha, ci = pg.cronbach_alpha(data=d)
    omega = _omega_tek_faktor(d)
    return pd.DataFrame([{"Madde sayısı": len(maddeler), "n": len(d),
                          "Cronbach α": round(alpha, 3), "α %95 GA": f"{ci[0]:.2f}–{ci[1]:.2f}",
                          "McDonald ω": round(omega, 3) if not np.isnan(omega) else "hesaplanamadı"}])


# ---------------------------------------------------------------- modeller
def regresyon(df, y, x, bloklar=None):
    """Doğrusal regresyon. bloklar verilirse hiyerarşik (kümülatif) modeller kurar."""
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    bloklar = bloklar or [x]
    tum = [v for b in bloklar for v in b]
    d = df[[y] + tum].apply(pd.to_numeric, errors="coerce").dropna()
    z = (d - d.mean()) / d.std(ddof=1)
    modeller, katsayi_tablolari, onceki = [], [], None
    kumulatif = []
    for i, b in enumerate(bloklar, 1):
        kumulatif += b
        X = sm.add_constant(d[kumulatif])
        m = sm.OLS(d[y], X).fit()
        mz = sm.OLS(z[y], sm.add_constant(z[kumulatif])).fit()
        ci = m.conf_int()
        vif = {v: variance_inflation_factor(X.values, j) for j, v in enumerate(X.columns) if v != "const"}
        kt = pd.DataFrame({
            "Model": i, "Değişken": kumulatif, "B": m.params[kumulatif].round(3).values,
            "SE": m.bse[kumulatif].round(3).values, "β": mz.params[kumulatif].round(3).values,
            "t": m.tvalues[kumulatif].round(2).values, "p": [_p(p) for p in m.pvalues[kumulatif]],
            "%95 GA": [f"{ci.loc[v, 0]:.2f}, {ci.loc[v, 1]:.2f}" for v in kumulatif],
            "VIF": [round(vif[v], 2) for v in kumulatif]})
        satir = {"Model": i, "R²": round(m.rsquared, 3), "Düz. R²": round(m.rsquared_adj, 3),
                 "F": round(m.fvalue, 2), "sd": f"{int(m.df_model)}, {int(m.df_resid)}",
                 "p": _p(m.f_pvalue), "n": int(m.nobs)}
        if onceki is not None:
            fch, pch, dfd = m.compare_f_test(onceki)
            satir.update({"ΔR²": round(m.rsquared - onceki.rsquared, 3),
                          "F değişim": round(fch, 2), "p değişim": _p(pch)})
        modeller.append(satir)
        katsayi_tablolari.append(kt)
        onceki = m
    return {"modeller": pd.DataFrame(modeller), "katsayilar": pd.concat(katsayi_tablolari),
            "f2_son": round(onceki.rsquared / (1 - onceki.rsquared), 3)}


def lojistik(df, y, x):
    import statsmodels.api as sm
    d = df[[y] + x].apply(pd.to_numeric, errors="coerce").dropna()
    m = sm.Logit(d[y], sm.add_constant(d[x])).fit(disp=0)
    ci = np.exp(m.conf_int())
    n = m.nobs
    cs = 1 - np.exp((m.llnull - m.llf) * 2 / n)
    nag = cs / (1 - np.exp(m.llnull * 2 / n))
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(d[y], m.predict())
    tab = pd.DataFrame({"Değişken": x, "B": m.params[x].round(3).values,
                        "SE": m.bse[x].round(3).values, "OR": np.exp(m.params[x]).round(2).values,
                        "%95 GA": [f"{ci.loc[v, 0]:.2f}–{ci.loc[v, 1]:.2f}" for v in x],
                        "p": [_p(p) for p in m.pvalues[x]]})
    return {"katsayilar": tab, "model": pd.DataFrame([{
        "n": int(n), "Olay": int(d[y].sum()), "Nagelkerke R²": round(nag, 3),
        "AUC": round(auc, 3), "LR χ²": round(m.llr, 2), "p": _p(m.llr_pvalue)}])}


def aracilik(df, x, m, y, kovaryatlar=None, n_boot=5000, seed=42):
    """Basit aracılık (PROCESS Model 4 mantığı), yüzdelik bootstrap GA."""
    import pingouin as pg
    kov = kovaryatlar or []
    d = df[[x, m, y] + kov].apply(pd.to_numeric, errors="coerce").dropna()
    r = pg.mediation_analysis(data=d, x=x, m=m, y=y, covar=kov or None,
                              n_boot=n_boot, seed=seed, return_dist=False)
    r = r.rename(columns={"path": "Yol", "coef": "B", "se": "SE", "pval": "p",
                          "CI[2.5%]": "%95 GA alt", "CI[97.5%]": "%95 GA üst", "CI2.5": "%95 GA alt", "CI97.5": "%95 GA üst", "sig": "Anlamlı"})
    ad = {f"{m} ~ X": "a", f"Y ~ {m}": "b", "Total": "c (toplam)", "Direct": "c′ (doğrudan)",
          "Indirect": "ab (dolaylı)"}
    r["Yol"] = r["Yol"].map(lambda s: ad.get(s, s))
    r["p"] = r["p"].map(_p)
    return r.round(3)


def kantil_regresyon(df, y, x, kantiller=(0.25, 0.5, 0.75)):
    import statsmodels.formula.api as smf
    d = df[[y] + x].apply(pd.to_numeric, errors="coerce").dropna()
    formul = f"Q('{y}') ~ " + " + ".join(f"Q('{v}')" for v in x)
    rows = []
    for q in kantiller:
        m = smf.quantreg(formul, d).fit(q=q)
        ci = m.conf_int()
        for v in x:
            k = f"Q('{v}')"
            rows.append({"Kantil": q, "Değişken": v, "B": round(m.params[k], 3),
                         "SE": round(m.bse[k], 3), "%95 GA": f"{ci.loc[k, 0]:.2f}, {ci.loc[k, 1]:.2f}",
                         "p": _p(m.pvalues[k]), "Pseudo R²": round(m.prsquared, 3)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- güç
def guc_analizi(test="t", etki=0.5, alfa=0.05, guc=0.80, grup_sayisi=3, yordayici=3, kayip=0.0):
    """Gerekli örneklem. test: t | anova | korelasyon | regresyon | ki_kare.
    etki: d (t), f (anova), r (korelasyon), f² (regresyon), w (ki_kare)."""
    from statsmodels.stats import power as pw
    if test == "t":
        n = pw.TTestIndPower().solve_power(effect_size=etki, alpha=alfa, power=guc)
        toplam = 2 * np.ceil(n)
        ayrinti = f"grup başına {int(np.ceil(n))}"
    elif test == "anova":
        toplam = np.ceil(pw.FTestAnovaPower().solve_power(effect_size=etki, alpha=alfa, power=guc,
                                                         k_groups=grup_sayisi))
        ayrinti = f"{grup_sayisi} grup"
    elif test == "korelasyon":
        zr = np.arctanh(etki)
        toplam = np.ceil(((stats.norm.ppf(1 - alfa / 2) + stats.norm.ppf(guc)) / zr) ** 2 + 3)
        ayrinti = "iki yönlü"
    elif test == "regresyon":
        toplam = None
        for n in range(yordayici + 5, 5000):
            lam = etki * n
            fkrit = stats.f.ppf(1 - alfa, yordayici, n - yordayici - 1)
            if 1 - stats.ncf.cdf(fkrit, yordayici, n - yordayici - 1, lam) >= guc:
                toplam = n
                break
        ayrinti = f"{yordayici} yordayıcı (R² ≠ 0)"
    elif test == "ki_kare":
        toplam = np.ceil(pw.GofChisquarePower().solve_power(effect_size=etki, alpha=alfa,
                                                            power=guc, n_bins=grup_sayisi))
        ayrinti = f"{grup_sayisi} kategori"
    else:
        raise ValueError("test: t | anova | korelasyon | regresyon | ki_kare")
    kayipli = int(np.ceil(toplam / (1 - kayip))) if kayip else int(toplam)
    return pd.DataFrame([{"Test": test, "Etki": etki, "α": alfa, "Güç": guc, "Ayrıntı": ayrinti,
                          "Gerekli n": int(toplam), f"Kayıp %{int(kayip*100)} ile": kayipli}])


# ---------------------------------------------------------------- çıktı
def _p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    return "< .001" if p < .001 else f"{p:.3f}".replace("0.", ".", 1)


def apa_kaydet(tablolar: dict, yol: str):
    """{'Tablo 1': df, ...} sözlüğünü tek Excel dosyasına sayfa sayfa yazar."""
    with pd.ExcelWriter(yol) as w:
        for ad, t in tablolar.items():
            (t.reset_index() if not isinstance(t.index, pd.RangeIndex) else t).to_excel(
                w, sheet_name=str(ad)[:31], index=False)
    return yol
