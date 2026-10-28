"""Klinik/hemşirelik verisinde makine öğrenmesi (TRIPOD+AI ile uyumlu raporlama için).

Denetimli: sınıflandırma ve regresyon (tekrarlı çapraz doğrulama, isteğe bağlı iç içe ayarlama),
ayırt edicilik (AUC + bootstrap GA), kalibrasyon (eğim, kesişim, Brier), karar eğrisi analizi,
açıklanabilirlik (SHAP / permütasyon önemi).
Denetimsiz: gizil profil analizi (Gauss karışım modeli), k-ortalamalar kümeleme.

    import sys; sys.path.insert(0, "<skill>/scripts"); import makine_ogrenmesi as ml
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.metrics import (roc_auc_score, brier_score_loss, accuracy_score, recall_score,
                             f1_score, mean_squared_error, mean_absolute_error, r2_score)
from sklearn.model_selection import RepeatedStratifiedKFold, RepeatedKFold, GridSearchCV, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC, SVR


def _on_isleme(X):
    kat = [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]
    say = [c for c in X.columns if c not in kat]
    return ColumnTransformer([
        ("say", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), say),
        ("kat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore", drop="if_binary"))]), kat)])


def _modeller(tur, seed):
    if tur == "sinif":
        m = {"Lojistik (elastik ağ)": (LogisticRegression(penalty="elasticnet", solver="saga", l1_ratio=.5,
                                                          C=1.0, max_iter=5000, class_weight="balanced"),
                                       {"m__C": [0.01, 0.1, 1, 10], "m__l1_ratio": [0.1, 0.5, 0.9]}),
             "Rastgele orman": (RandomForestClassifier(n_estimators=500, min_samples_leaf=5,
                                                       class_weight="balanced", random_state=seed, n_jobs=-1),
                                {"m__max_depth": [None, 5, 10], "m__min_samples_leaf": [1, 5, 10]}),
             "SVM (RBF)": (SVC(probability=True, class_weight="balanced", random_state=seed),
                           {"m__C": [0.1, 1, 10], "m__gamma": ["scale", 0.01, 0.1]})}
        try:
            from lightgbm import LGBMClassifier
            m["Gradyan artırma (LightGBM)"] = (LGBMClassifier(n_estimators=300, learning_rate=.05, num_leaves=15,
                                                              min_child_samples=10, class_weight="balanced",
                                                              random_state=seed, verbose=-1),
                                               {"m__num_leaves": [7, 15, 31], "m__learning_rate": [0.03, 0.1]})
        except ImportError:
            pass
    else:
        m = {"Elastik ağ": (ElasticNet(alpha=.1, l1_ratio=.5, max_iter=10000),
                            {"m__alpha": [0.01, 0.1, 1], "m__l1_ratio": [0.1, 0.5, 0.9]}),
             "Rastgele orman": (RandomForestRegressor(n_estimators=500, min_samples_leaf=5, random_state=seed, n_jobs=-1),
                                {"m__max_depth": [None, 5, 10], "m__min_samples_leaf": [1, 5, 10]}),
             "SVR (RBF)": (SVR(), {"m__C": [0.1, 1, 10]})}
        try:
            from lightgbm import LGBMRegressor
            m["Gradyan artırma (LightGBM)"] = (LGBMRegressor(n_estimators=300, learning_rate=.05, num_leaves=15,
                                                             min_child_samples=10, random_state=seed, verbose=-1),
                                               {"m__num_leaves": [7, 15, 31], "m__learning_rate": [0.03, 0.1]})
        except ImportError:
            pass
    return m


def _kalibrasyon(y, p):
    import statsmodels.api as sm
    p = np.clip(p, 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    egim = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit().params[1]
    kesisim = sm.GLM(y, np.ones_like(lp), family=sm.families.Binomial(), offset=lp).fit().params[0]
    return egim, kesisim


def siniflandirma(df, y, X, modeller=None, katman=5, tekrar=5, ayarla=False, seed=42):
    """Tekrarlı tabakalı k-katlı ÇD ile model karşılaştırması. ayarla=True: iç içe ÇD ile hiperparametre.
    Dönüş: performans tablosu ve katman dışı (out-of-fold) tahminler."""
    d = df[[y] + X].dropna(subset=[y]).reset_index(drop=True)
    Xd, yv = d[X], d[y].astype(int).values
    tum = _modeller("sinif", seed)
    secili = {k: v for k, v in tum.items() if (modeller is None or k in modeller)}
    cv = RepeatedStratifiedKFold(n_splits=katman, n_repeats=tekrar, random_state=seed)
    satirlar, oof = [], {}
    for ad, (mdl, izgara) in secili.items():
        pipe = Pipeline([("on", _on_isleme(Xd)), ("m", mdl)])
        tahmin = np.zeros((tekrar, len(yv)))
        aucs, briers, sens, spec, f1s = [], [], [], [], []
        for i, (tr, te) in enumerate(cv.split(Xd, yv)):
            est = GridSearchCV(pipe, izgara, cv=StratifiedKFold(3, shuffle=True, random_state=seed),
                               scoring="roc_auc", n_jobs=-1) if ayarla else pipe
            est.fit(Xd.iloc[tr], yv[tr])
            p = est.predict_proba(Xd.iloc[te])[:, 1]
            tahmin[i // katman, te] = p
            yhat = (p >= .5).astype(int)
            aucs.append(roc_auc_score(yv[te], p)); briers.append(brier_score_loss(yv[te], p))
            sens.append(recall_score(yv[te], yhat)); spec.append(recall_score(yv[te], yhat, pos_label=0))
            f1s.append(f1_score(yv[te], yhat))
        p_ort = tahmin.mean(axis=0)
        oof[ad] = p_ort
        egim, kes = _kalibrasyon(yv, p_ort)
        satirlar.append({"Model": ad, "AUC": f"{np.mean(aucs):.3f} ± {np.std(aucs):.3f}",
                         "Duyarlılık": f"{np.mean(sens):.3f}", "Özgüllük": f"{np.mean(spec):.3f}",
                         "F1": f"{np.mean(f1s):.3f}", "Brier": f"{np.mean(briers):.3f}",
                         "Kalibrasyon eğimi": round(egim, 2), "Kalibrasyon kesişimi": round(kes, 2)})
    olay = int(yv.sum())
    uyari = []
    if olay / max(len(X), 1) < 10:
        uyari.append(f"Olay/yordayıcı oranı düşük ({olay}/{len(X)}); aşırı uyum riski. Ceza (elastik ağ) ve dış geçerleme önerilir.")
    if len(yv) < 200:
        uyari.append("n < 200: karmaşık modeller (orman, gradyan artırma) lojistik regresyona üstün olmayabilir; bunu açıkça raporlayın.")
    return {"performans": pd.DataFrame(satirlar), "oof": oof, "y": yv, "n": len(yv), "olay": olay,
            "uyarilar": uyari, "cv": f"{tekrar}×{katman}-katlı tekrarlı tabakalı ÇD" + (" (iç içe ayarlama)" if ayarla else "")}


def regresyon_ml(df, y, X, modeller=None, katman=5, tekrar=5, ayarla=False, seed=42):
    d = df[[y] + X].dropna(subset=[y]).reset_index(drop=True)
    Xd, yv = d[X], d[y].astype(float).values
    secili = {k: v for k, v in _modeller("reg", seed).items() if (modeller is None or k in modeller)}
    cv = RepeatedKFold(n_splits=katman, n_repeats=tekrar, random_state=seed)
    rows = []
    for ad, (mdl, izgara) in secili.items():
        pipe = Pipeline([("on", _on_isleme(Xd)), ("m", mdl)])
        r2, rmse, mae = [], [], []
        for tr, te in cv.split(Xd):
            est = GridSearchCV(pipe, izgara, cv=KFold(3, shuffle=True, random_state=seed), n_jobs=-1) if ayarla else pipe
            est.fit(Xd.iloc[tr], yv[tr]); p = est.predict(Xd.iloc[te])
            r2.append(r2_score(yv[te], p)); rmse.append(np.sqrt(mean_squared_error(yv[te], p)))
            mae.append(mean_absolute_error(yv[te], p))
        rows.append({"Model": ad, "R²": f"{np.mean(r2):.3f} ± {np.std(r2):.3f}",
                     "RMSE": f"{np.mean(rmse):.3f}", "MAE": f"{np.mean(mae):.3f}"})
    return pd.DataFrame(rows)


def auc_ga(y, p, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) == 2:
            bs.append(roc_auc_score(y[i], p[i]))
    return round(roc_auc_score(y, p), 3), tuple(np.round(np.percentile(bs, [2.5, 97.5]), 3))


def karar_egrisi(y, olasiliklar: dict, esikler=None, yol=None):
    """Karar eğrisi analizi (Vickers): net fayda. olasiliklar: {'Model': p, ...}."""
    esikler = np.arange(0.05, 0.61, 0.05) if esikler is None else np.asarray(esikler)
    y = np.asarray(y); n = len(y); prev = y.mean()
    rows = []
    for t in esikler:
        r = {"Eşik": round(t, 2), "Hepsine uygula": round(prev - (1 - prev) * t / (1 - t), 4), "Hiçbirine": 0.0}
        for ad, p in olasiliklar.items():
            pos = p >= t
            tp, fp = np.sum(pos & (y == 1)), np.sum(pos & (y == 0))
            r[ad] = round(tp / n - fp / n * t / (1 - t), 4)
        rows.append(r)
    tab = pd.DataFrame(rows)
    if yol:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        for c in tab.columns[1:]:
            ax.plot(tab["Eşik"], tab[c], label=c, ls="--" if c in ("Hepsine uygula", "Hiçbirine") else "-")
        ax.set_ylim(min(-0.05, tab.iloc[:, 1:].min().min()), prev + .05)
        ax.set_xlabel("Eşik olasılık"); ax.set_ylabel("Net fayda"); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(yol, dpi=300); plt.close(fig)
    return tab


def kalibrasyon_grafigi(y, p, yol, bins=10):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from sklearn.calibration import calibration_curve
    fy, fp = calibration_curve(y, p, n_bins=bins, strategy="quantile")
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0, 1], [0, 1], "k--", lw=.8); ax.plot(fp, fy, "o-")
    ax.set_xlabel("Tahmin edilen olasılık"); ax.set_ylabel("Gözlenen oran")
    fig.tight_layout(); fig.savefig(yol, dpi=300); plt.close(fig)
    return yol


def aciklanabilirlik(df, y, X, model="Rastgele orman", tur="sinif", yol=None, seed=42):
    """Tüm veride modeli eğitip SHAP (ağaç modelleri) ya da permütasyon önemi verir.
    Not: Önem ≠ nedensellik; rapor ederken bunu belirtin."""
    d = df[[y] + X].dropna(subset=[y]).reset_index(drop=True)
    mdl = _modeller("sinif" if tur == "sinif" else "reg", seed)[model][0]
    pipe = Pipeline([("on", _on_isleme(d[X])), ("m", mdl)]).fit(d[X], d[y])
    Xt = pipe.named_steps["on"].transform(d[X])
    Xt = Xt.toarray() if hasattr(Xt, "toarray") else Xt
    adlar = [a.split("__", 1)[1] for a in pipe.named_steps["on"].get_feature_names_out()]
    try:
        import shap
        ex = shap.TreeExplainer(pipe.named_steps["m"]) if ("orman" in model.lower() or "LightGBM" in model) \
            else shap.LinearExplainer(pipe.named_steps["m"], Xt)
        sv = ex.shap_values(Xt)
        if isinstance(sv, list):
            sv = sv[1]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[:, :, 1]
        onem = pd.DataFrame({"Değişken": adlar, "Ortalama |SHAP|": np.abs(sv).mean(0)})
        yontem = "SHAP"
        if yol:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
            shap.summary_plot(sv, Xt, feature_names=adlar, show=False)
            plt.tight_layout(); plt.savefig(yol, dpi=300); plt.close()
    except Exception:
        from sklearn.inspection import permutation_importance
        r = permutation_importance(pipe, d[X], d[y], n_repeats=20, random_state=seed,
                                   scoring="roc_auc" if tur == "sinif" else "r2")
        onem = pd.DataFrame({"Değişken": X, "Permütasyon önemi": r.importances_mean})
        yontem = "Permütasyon"
    return onem.sort_values(onem.columns[1], ascending=False).round(4).reset_index(drop=True), yontem


# ------------------------------------------------------------ denetimsiz
def gizil_profil(df, degiskenler, k_aralik=range(1, 7), standartlastir=True, seed=42):
    """Gizil profil analizi (Gauss karışım modeli; diyagonal ve tam kovaryans).
    Seçim: düşük BIC, entropi ≥ .80, en küçük sınıf ≥ %5 ve kuramsal yorumlanabilirlik."""
    from sklearn.mixture import GaussianMixture
    d = df[degiskenler].apply(pd.to_numeric, errors="coerce").dropna()
    Z = (d - d.mean()) / d.std() if standartlastir else d
    rows, modeller = [], {}
    for cov in ("diag", "full"):
        for k in k_aralik:
            g = GaussianMixture(k, covariance_type=cov, n_init=20, random_state=seed).fit(Z)
            post = g.predict_proba(Z)
            ent = 1.0 if k == 1 else 1 + np.sum(post * np.log(np.clip(post, 1e-12, 1))) / (len(Z) * np.log(k))
            n_s = np.bincount(post.argmax(1), minlength=k)
            n_par = g._n_parameters()
            bic = g.bic(Z)
            sabic = -2 * g.score(Z) * len(Z) + n_par * np.log((len(Z) + 2) / 24)
            rows.append({"Kovaryans": cov, "k": k, "LL": round(g.score(Z) * len(Z), 2), "AIC": round(g.aic(Z), 2),
                         "BIC": round(bic, 2), "SABIC": round(sabic, 2), "Entropi": round(ent, 3),
                         "En küçük sınıf %": round(n_s.min() / len(Z) * 100, 1)})
            modeller[(cov, k)] = g
    return {"uyum": pd.DataFrame(rows), "modeller": modeller, "Z": Z, "veri": d,
            "not": "BLRT/LMR testi bu uygulamada yok; seçimi BIC/SABIC, entropi, sınıf büyüklüğü ve yorumlanabilirlikle gerekçelendirin."}


def profil_ozeti(sonuc, kovaryans, k):
    g = sonuc["modeller"][(kovaryans, k)]
    etiket = g.predict(sonuc["Z"])
    v = sonuc["veri"].assign(Profil=etiket + 1)
    ozet = v.groupby("Profil").agg(["mean", "std"]).round(2)
    ozet.insert(0, ("n", ""), v["Profil"].value_counts().sort_index())
    return ozet, v["Profil"]


# ------------------------------------------------------------ örneklem büyüklüğü
def riley_orneklem(yordayici_param, prevalans, r2cs=None, buzulme=0.9, delta=0.05, kesisim_hata=0.05):
    """İkili sonuçlu tahmin modeli için en küçük örneklem (Riley ve ark. ölçütleri 1–3).
    yordayici_param: aday parametre sayısı (kategorik değişkenlerde kukla sayısı dahil).
    r2cs: beklenen Cox–Snell R²; verilmezse R²max'ın %15'i (temkinli varsayım) kullanılır."""
    phi = prevalans
    lnl = phi * np.log(phi) + (1 - phi) * np.log(1 - phi)
    r2max = 1 - np.exp(2 * lnl)
    r2 = r2cs if r2cs is not None else 0.15 * r2max
    n1 = yordayici_param / ((buzulme - 1) * np.log(1 - r2 / buzulme))
    S2 = r2 / (r2 + delta * r2max)
    n2 = yordayici_param / ((S2 - 1) * np.log(1 - r2 / S2))
    n3 = (1.96 / kesisim_hata) ** 2 * phi * (1 - phi)
    n = int(np.ceil(max(n1, n2, n3)))
    return pd.DataFrame([{"R²cs varsayımı": round(r2, 3), "R²max": round(r2max, 3),
                          "Ölçüt 1 (büzülme ≥ .90)": int(np.ceil(n1)), "Ölçüt 2 (iyimserlik ≤ .05)": int(np.ceil(n2)),
                          "Ölçüt 3 (kesişim kesinliği)": int(np.ceil(n3)), "Gerekli n": n,
                          "Gerekli olay": int(np.ceil(n * phi)), "Olay/parametre": round(n * phi / yordayici_param, 1)}])
