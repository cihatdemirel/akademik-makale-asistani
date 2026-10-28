"""Psikometrik ağ analizi (Gauss grafiksel modeli, EBICglasso), merkezilik, köprü merkeziliği,
bootstrap doğruluk/kararlılık (CS katsayısı), ağ karşılaştırma testi (NCT) ve çizim.

R'deki bootnet/qgraph/networktools/NetworkComparisonTest iş akışının Python karşılığıdır.
Sonuçlar R ile birebir aynı olmayabilir (glasso uygulaması ve λ ızgarası farkı); yöntem
bölümünde Python uygulaması olduğunu belirtin.

    import sys; sys.path.insert(0, "<skill>/scripts"); import ag_analizi as ag
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


def _korelasyon(d, yontem):
    if yontem == "spearman":
        return d.rank().corr().values
    return d.corr().values


def ebicglasso(df, degiskenler, gamma=0.5, yontem="spearman", n_lambda=50, oran=0.01):
    """Kısmi korelasyon ağı. gamma: EBIC hiperparametresi (0.5 varsayılan; küçük örneklemde 0.25).
    Dönüş: kısmi korelasyon matrisi (DataFrame) ve seçilen λ."""
    from sklearn.covariance import graphical_lasso
    d = df[degiskenler].apply(pd.to_numeric, errors="coerce").dropna()
    n, p = d.shape
    S = _korelasyon(d, yontem)
    lmax = np.max(np.abs(S - np.eye(p)))
    lamlar = np.exp(np.linspace(np.log(lmax), np.log(lmax * oran), n_lambda))
    en_iyi, sec_l, sec_K = np.inf, None, None
    for lam in lamlar:
        try:
            _, K = graphical_lasso(S, alpha=lam, max_iter=200)
        except Exception:
            continue
        E = (np.abs(np.triu(K, 1)) > 1e-8).sum()
        _, logdet = np.linalg.slogdet(K)
        ll = n / 2 * (logdet - np.trace(S @ K))
        ebic = -2 * ll + E * np.log(n) + 4 * E * gamma * np.log(p)
        if ebic < en_iyi:
            en_iyi, sec_l, sec_K = ebic, lam, K
    dg = np.sqrt(np.diag(sec_K))
    W = -sec_K / np.outer(dg, dg)
    np.fill_diagonal(W, 0)
    W[np.abs(W) < 1e-8] = 0
    return pd.DataFrame(W, index=degiskenler, columns=degiskenler), sec_l


def ozet(W):
    p = W.shape[0]
    ust = W.values[np.triu_indices(p, 1)]
    return pd.DataFrame([{"Düğüm": p, "Olası kenar": len(ust), "Sıfır olmayan kenar": int((ust != 0).sum()),
                          "Yoğunluk": round((ust != 0).mean(), 3), "Ortalama |ağırlık|": round(np.abs(ust[ust != 0]).mean(), 3)
                          if (ust != 0).any() else 0, "Pozitif": int((ust > 0).sum()), "Negatif": int((ust < 0).sum())}])


def merkezilik(W, topluluklar: dict | None = None):
    """Güç, beklenen etki (EI1), yakınlık, aradalık; topluluklar verilirse köprü güç/EI.
    Yakınlık/aradalık genellikle kararsızdır; makalede güç ve beklenen etkiyi öne çıkarın."""
    import networkx as nx
    A = W.values
    adlar = list(W.index)
    G = nx.Graph()
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            if A[i, j] != 0:
                G.add_edge(adlar[i], adlar[j], weight=abs(A[i, j]), dist=1 / abs(A[i, j]))
    G.add_nodes_from(adlar)
    yak = nx.closeness_centrality(G, distance="dist")
    ara = nx.betweenness_centrality(G, weight="dist", normalized=False)
    tab = pd.DataFrame({"Güç": np.abs(A).sum(1), "Beklenen etki": A.sum(1),
                        "Yakınlık": [yak[a] for a in adlar], "Aradalık": [ara[a] for a in adlar]}, index=adlar)
    if topluluklar:
        kom = {v: k for k, vs in topluluklar.items() for v in vs}
        bg, bei = [], []
        for i, a in enumerate(adlar):
            maske = np.array([kom.get(b) != kom.get(a) for b in adlar])
            bg.append(np.abs(A[i, maske]).sum()); bei.append(A[i, maske].sum())
        tab["Köprü güç"], tab["Köprü beklenen etki"] = bg, bei
    z = (tab - tab.mean()) / tab.std(ddof=0)
    return tab.round(3), z.round(2)


def _kenar_vektor(W):
    p = W.shape[0]
    return W.values[np.triu_indices(p, 1)]


def bootstrap_kenar(df, degiskenler, n_boot=1000, seed=42, **kw):
    """Parametrik olmayan bootstrap: kenar ağırlıklarının %95 GA'sı ve sıfır olmayan oranı.
    Süre: tek çekirdekte 10–20 değişken için yaklaşık 0,3–0,5 sn/örneklem. Uzun işleri
    arka planda (nohup) çalıştırıp sonucu dosyaya yazın."""
    rng = np.random.default_rng(seed)
    d = df[degiskenler].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    W0, _ = ebicglasso(d, degiskenler, **kw)
    p = len(degiskenler)
    iu = np.triu_indices(p, 1)
    kw.setdefault("n_lambda", 30)
    from joblib import Parallel, delayed
    orneklemler = [rng.integers(0, len(d), len(d)) for _ in range(n_boot)]
    B = np.array(Parallel(n_jobs=-1)(delayed(lambda i: _kenar_vektor(ebicglasso(d.iloc[i], degiskenler, **kw)[0]))(i)
                                     for i in orneklemler))
    adlar = [f"{degiskenler[i]} — {degiskenler[j]}" for i, j in zip(*iu)]
    lo, hi = np.percentile(B, [2.5, 97.5], axis=0)
    tab = pd.DataFrame({"Kenar": adlar, "Örneklem": _kenar_vektor(W0).round(3), "Boot ort.": B.mean(0).round(3),
                        "%95 GA": [f"{a:.3f}, {b:.3f}" for a, b in zip(lo, hi)],
                        "Sıfır dışı %": ((B != 0).mean(0) * 100).round(1)})
    return tab[tab["Örneklem"] != 0].sort_values("Örneklem", key=np.abs, ascending=False).reset_index(drop=True)


def cs_katsayisi(df, degiskenler, n_boot=500, oranlar=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75),
                 olcutler=("Güç", "Beklenen etki"), seed=42, **kw):
    """Vaka düşürme bootstrap'i ile korelasyon kararlılığı (CS) katsayısı.
    CS ≥ .25 kabul edilebilir, ≥ .50 tercih edilir (Epskamp ve ark., 2018)."""
    rng = np.random.default_rng(seed)
    d = df[degiskenler].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    W0, _ = ebicglasso(d, degiskenler, **kw)
    m0, _ = merkezilik(W0)
    kw.setdefault("n_lambda", 30)
    from joblib import Parallel, delayed
    n = len(d)

    def tek(idx):
        mb, _ = merkezilik(ebicglasso(d.iloc[idx], degiskenler, **kw)[0])
        return [np.corrcoef(m0[o], mb[o])[0, 1] if mb[o].std() > 0 else 0 for o in olcutler]

    sonuc = {o: {} for o in olcutler}
    for oran in oranlar:
        kalan = int(round(n * (1 - oran)))
        kor = np.array(Parallel(n_jobs=-1)(delayed(tek)(rng.choice(n, kalan, replace=False)) for _ in range(n_boot)))
        for k, o in enumerate(olcutler):
            sonuc[o][oran] = np.mean(kor[:, k] >= 0.7)
    rows = []
    for o in olcutler:
        gecen = [r for r, v in sonuc[o].items() if v >= 0.95]
        rows.append({"Ölçüt": o, "CS katsayısı": max(gecen) if gecen else 0.0,
                     **{f"%{int(r * 100)} düşürme": round(v, 2) for r, v in sonuc[o].items()}})
    return pd.DataFrame(rows)


def ag_karsilastir(df1, df2, degiskenler, n_perm=1000, seed=42, **kw):
    """Ağ karşılaştırma testi (permütasyon): global güç farkı ve en büyük kenar farkı (yapı değişmezliği)."""
    rng = np.random.default_rng(seed)
    a = df1[degiskenler].apply(pd.to_numeric, errors="coerce").dropna()
    b = df2[degiskenler].apply(pd.to_numeric, errors="coerce").dropna()

    kw.setdefault("n_lambda", 30)

    def istatistik(x, y):
        Wa, _ = ebicglasso(x, degiskenler, **kw); Wb, _ = ebicglasso(y, degiskenler, **kw)
        ea, eb = _kenar_vektor(Wa), _kenar_vektor(Wb)
        return abs(np.abs(ea).sum() - np.abs(eb).sum()), np.max(np.abs(ea - eb)), ea, eb

    gs, me, ea, eb = istatistik(a, b)
    birlesik = pd.concat([a, b]).reset_index(drop=True)
    na = len(a)
    pg, pm = 0, 0
    for _ in range(n_perm):
        idx = rng.permutation(len(birlesik))
        g2, m2, _, _ = istatistik(birlesik.iloc[idx[:na]], birlesik.iloc[idx[na:]])
        pg += g2 >= gs; pm += m2 >= me
    return pd.DataFrame([{"Global güç (grup 1)": round(np.abs(ea).sum(), 3), "Global güç (grup 2)": round(np.abs(eb).sum(), 3),
                          "Güç farkı": round(gs, 3), "p (global güç)": round((pg + 1) / (n_perm + 1), 3),
                          "En büyük kenar farkı": round(me, 3), "p (yapı)": round((pm + 1) / (n_perm + 1), 3)}])


def ciz(W, yol, topluluklar: dict | None = None, etiketler: dict | None = None, seed=42):
    """Fruchterman–Reingold yerleşimi; mavi pozitif, kırmızı negatif kenar, kalınlık |ağırlık|."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    import networkx as nx
    A = W.values; adlar = list(W.index)
    G = nx.Graph(); G.add_nodes_from(adlar)
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            if A[i, j] != 0:
                G.add_edge(adlar[i], adlar[j], w=A[i, j])
    pos = nx.spring_layout(G, weight=None, seed=seed, k=1.2 / np.sqrt(len(adlar)))
    renkler = plt.cm.Set2.colors
    kom = {v: k for k, vs in (topluluklar or {}).items() for v in vs}
    grup_ad = list((topluluklar or {}).keys())
    dugum_renk = [renkler[grup_ad.index(kom[a]) % len(renkler)] if a in kom else "#dddddd" for a in adlar]
    mx = max(np.abs(A).max(), 1e-9)
    fig, ax = plt.subplots(figsize=(7, 6))
    for u, v, dd in G.edges(data=True):
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#2b6cb0" if dd["w"] > 0 else "#c53030",
                lw=0.5 + 6 * abs(dd["w"]) / mx, alpha=0.4 + 0.6 * abs(dd["w"]) / mx, zorder=1)
    nx.draw_networkx_nodes(G, pos, node_color=dugum_renk, node_size=900, edgecolors="black", linewidths=.8, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=etiketler or {a: a for a in adlar}, font_size=8, ax=ax)
    if topluluklar:
        for i, g in enumerate(grup_ad):
            ax.scatter([], [], color=renkler[i % len(renkler)], label=g, s=80, edgecolors="black")
        ax.legend(loc="lower left", fontsize=8, frameon=False)
    ax.axis("off"); fig.tight_layout(); fig.savefig(yol, dpi=300); plt.close(fig)
    return yol


def merkezilik_grafigi(z, yol, olcutler=("Güç", "Beklenen etki")):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, len(olcutler), figsize=(3 * len(olcutler), 0.35 * len(z) + 1), sharey=True)
    axs = np.atleast_1d(axs)
    sira = z.sort_values(olcutler[0]).index
    for ax, o in zip(axs, olcutler):
        ax.plot(z.loc[sira, o], range(len(sira)), "o-", color="black")
        ax.set_title(o, fontsize=9); ax.axvline(0, color="grey", lw=.5)
    axs[0].set_yticks(range(len(sira))); axs[0].set_yticklabels(sira, fontsize=8)
    fig.tight_layout(); fig.savefig(yol, dpi=300); plt.close(fig)
    return yol
