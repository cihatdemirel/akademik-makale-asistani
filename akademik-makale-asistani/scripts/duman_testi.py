#!/usr/bin/env python3
"""Tüm betiklerin sentetik veriyle hızlı testi. Bakım modunda ve GitHub iş akışında çalıştırılır.
Çıkış kodu 0 = hepsi geçti. Kullanım: python3 duman_testi.py"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
n = 240
x = rng.normal(0, 1, n); w = rng.normal(0, 1, n); m = .5 * x + rng.normal(0, 1, n); y = .4 * m + .2 * x + rng.normal(0, 1, n)
df = pd.DataFrame(dict(x=x, w=w, m=m, y=y, yas=rng.normal(50, 10, n), g=rng.choice(["A", "B"], n),
                       g3=rng.choice(["A", "B", "C"], n), olay=(rng.random(n) < .35).astype(int),
                       once=x, sonra=x + rng.normal(.3, 1, n)))
for i in range(4):
    df[f"i{i}"] = x + rng.normal(0, .8, n)

testler = []


def test(ad):
    def sar(f):
        testler.append((ad, f)); return f
    return sar


@test("istatistik")
def _():
    import istatistik as ist
    ist.tanimlayici(df, ["x"]); ist.normallik(df, ["x"]); ist.grup_karsilastir(df, "y", "g"); ist.grup_karsilastir(df, "y", "g3")
    ist.bagimli_karsilastir(df, "once", "sonra"); ist.ki_kare(df, "g", "g3"); ist.korelasyon(df, ["x", "y"])
    assert ist.guvenirlik(df, [f"i{i}" for i in range(4)])["Cronbach α"].iloc[0] > .7
    ist.regresyon(df, "y", None, bloklar=[["yas"], ["x", "m"]]); ist.lojistik(df, "olay", ["x"])
    ist.aracilik(df, x="x", m="m", y="y", n_boot=200); ist.kantil_regresyon(df, "y", ["x"])
    assert ist.guc_analizi(test="t", etki=.5)["Gerekli n"].iloc[0] == 128


@test("ileri_modeller")
def _():
    import ileri_modeller as im
    im.duzenleyicilik(df, "x", "w", "y"); im.seri_aracilik(df, "x", "m", "w", "y", n_boot=100)
    im.kosullu_aracilik(df, "x", "m", "y", "w", n_boot=100); im.ancova(df, "y", "g", ["yas"])
    im.little_mcar(df.assign(y=df.y.mask(rng.random(n) < .1)), ["x", "y"]); im.e_degeri(1.8, 1.2)
    g, v = im.hedges_g(10, 3, 40, 9, 3, 40); im.meta_analiz([g, g * .8, g * 1.2], [v, v, v])
    im.roc_kesme(df.olay, df.x, n_boot=100); im.baskinlik_analizi(df, "y", ["x", "m"])
    im.dfa(df, "F =~ i0 + i1 + i2 + i3")


@test("makine_ogrenmesi")
def _():
    import makine_ogrenmesi as ml
    r = ml.siniflandirma(df, "olay", ["x", "yas", "g"], modeller=["Lojistik (elastik ağ)"], katman=3, tekrar=1)
    ml.karar_egrisi(r["y"], r["oof"]); assert ml.riley_orneklem(24, .174, r2cs=.288)["Gerekli n"].iloc[0] == 662  # pmsampsize örneği: 662 (EPP 4.8)
    ml.gizil_profil(df, ["x", "w"], k_aralik=range(1, 3))


@test("ag_analizi")
def _():
    import ag_analizi as ag
    W, _ = ag.ebicglasso(df, ["x", "m", "y", "w"]); ag.merkezilik(W)


@test("yontem_secici")
def _():
    import yontem_secici as ys
    for a in ys.AMACLAR:
        ys.karar(a)
    assert "Welch" in ys.karar("karsilastir", grup=2)["yontem"]


@test("istatistik_denetimi")
def _():
    import istatistik_denetimi as sd
    r = sd.denetle("t(118) = 2.41, p = .018 and t(45) = 1.20, p = .03")
    assert list(r["Durum"]) == ["tutarlı", "BÜYÜK HATA: anlamlılık kararı değişiyor"]
    assert sd.grim(3.47, 28)["tutarlı"] is False and sd.grim(3.46, 28)["tutarlı"] is True


@test("kaynak_denetimi")
def _():
    import kaynak_denetimi as kd
    t, o, e = kd.denetle("Kim, H. Y. (2013). Title. Journal.\nHayes, A. F. (2022). Book. Guilford.", "(Hayes, 2022)", 2026)
    assert o["Kaynak sayısı"] == 2


hata = 0
for ad, f in testler:
    try:
        f(); print(f"✓ {ad}")
    except Exception:
        hata += 1; print(f"✗ {ad}"); traceback.print_exc(limit=2)
print("Sonuç:", "TÜMÜ GEÇTİ" if not hata else f"{hata} modül başarısız")
sys.exit(1 if hata else 0)
