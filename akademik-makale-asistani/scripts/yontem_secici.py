#!/usr/bin/env python3
"""İstatistiksel yöntem karar motoru (kural tabanlı, deterministik).

Kullanım (Python):
    import yontem_secici as ys
    ys.karar(amac="karsilastir", sonuc="surekli", grup=2, normal=False)
    ys.veriden_karar(df, amac="karsilastir", y="puan", grup="cinsiyet")   # varsayımları veriden ölçer

Kullanım (CLI):
    python3 yontem_secici.py --amac karsilastir --sonuc surekli --grup 3 --normal hayir

Her karar: önerilen yöntem, alternatif, kontrol edilecek varsayımlar, etki büyüklüğü,
betik fonksiyonu, tek cümlelik gerekçe ve yöntem kaynağı anahtarları (references/yontem-kaynaklari.md).
Kaynak anahtarları künye değildir; makaleye yazmadan önce doğrulanır.
"""
from __future__ import annotations

import argparse
import json

AMACLAR = ["karsilastir", "iliski", "yordama", "aracilik", "duzenleyicilik", "kosullu_aracilik", "uyum",
           "tani", "olcek", "profil", "ag", "tahmin", "meta", "zaman_serisi", "nedensel", "esdegerlik",
           "guc", "eksik_veri", "sagkalim", "tekrarli"]


def _k(yontem, alternatif, varsayim, etki, fonksiyon, gerekce, kaynak, uyari=None):
    return {"yontem": yontem, "alternatif": alternatif, "varsayimlar": varsayim, "etki_buyuklugu": etki,
            "fonksiyon": fonksiyon, "gerekce": gerekce, "kaynak_anahtarlari": kaynak, "uyari": uyari or []}


def karar(amac: str, sonuc: str = "surekli", grup: int = 2, eslestirilmis: bool = False, olcum: int = 1,
          n: int | None = None, normal: bool | None = None, varyans_esit: bool | None = None,
          kovaryat: bool = False, kumeli: bool = False, yordayici: int | None = None, olay: int | None = None,
          beklenen_kucuk: bool = False, desen: str = "kesitsel") -> dict:
    """amac: AMACLAR'dan biri. sonuc: surekli | ikili | sirali | sayim | kategorik | sure.
    normal/varyans_esit None ise 'kontrol et' kabul edilir. desen: kesitsel | rkc | kohort | yari_deneysel."""
    u = []
    if desen == "kesitsel" and amac in ("aracilik", "kosullu_aracilik", "ag", "yordama", "nedensel"):
        u.append("Kesitsel desen: sonuçlar ilişkiseldir; nedensel dil kullanmayın.")
    if n is not None and n < 30 and amac in ("karsilastir", "iliski") and normal is None:
        u.append("n < 30: normallik testi düşük güçlüdür; dağılım grafiği ve parametrik olmayan alternatif değerlendirin.")

    if amac == "karsilastir":
        if kumeli or olcum > 1 or eslestirilmis:
            return karar("tekrarli", sonuc=sonuc, grup=grup, olcum=max(olcum, 2), normal=normal, kovaryat=kovaryat,
                         desen=desen, n=n)
        if sonuc in ("ikili", "kategorik"):
            if beklenen_kucuk:
                return _k("Fisher kesin testi", "Fisher–Freeman–Halton (r×c)", ["beklenen frekans < 5 hücre oranı"],
                          "OR (2×2) / Cramér V", "ist.ki_kare", "Beklenen frekanslar küçük olduğunda ki-kare yaklaşımı güvenilmez.",
                          ["agresti2013"], u)
            return _k("Pearson ki-kare", "Fisher kesin (beklenen < 5)", ["bağımsız gözlemler", "beklenen frekans ≥ 5 (hücrelerin ≥ %80'i)"],
                      "Cramér V / OR", "ist.ki_kare", "İki kategorik değişkenin bağımsızlığı sınanır.", ["agresti2013"], u)
        if sonuc == "sirali":
            return _k("Mann–Whitney U" if grup == 2 else "Kruskal–Wallis + Dunn (Holm)", "Sıralı lojistik regresyon (kovaryat varsa)",
                      ["bağımsız gözlemler"], "r = Z/√N" if grup == 2 else "ε²",
                      "ist.grup_karsilastir(parametrik=False)", "Sıralı sonuçta ortalama tanımsızdır; sıra temelli test uygundur.",
                      ["conover1999"], u)
        if kovaryat:
            return _k("ANCOVA (düzeltilmiş ortalamalar)", "Çoklu doğrusal regresyon (grup kukla değişkeni)",
                      ["kovaryat–grup etkileşimi yok (eğim homojenliği)", "artıkların normalliği", "varyans homojenliği"],
                      "kısmi η², düzeltilmiş ortalama farkı ve GA", "im.ancova",
                      "Kovaryat (ör. ön test) kontrolü güç ve kesinliği artırır.",
                      ["vickers2001", "field2018"], u)
        if grup == 2:
            if normal is False:
                return _k("Mann–Whitney U", "Bootstrap ortalama farkı GA'sı", ["bağımsız gözlemler", "benzer dağılım şekli (medyan yorumu için)"],
                          "r = Z/√N", "ist.grup_karsilastir", "Normallik sağlanmadı; sıra temelli test uygundur.",
                          ["conover1999"], u)
            ad = "Welch t testi" if varyans_esit is not True else "Bağımsız örneklem t testi"
            return _k(ad, "Mann–Whitney U (normallik yoksa)", ["normallik (grup başına)", "varyans homojenliği (Levene)"],
                      "Cohen d / Hedges g ve %95 GA", "ist.grup_karsilastir",
                      "İki bağımsız grup ortalaması; Welch varyans eşitsizliğine dayanıklıdır ve varsayılan olarak önerilir.",
                      ["delacre2017", "lakens2013"], u)
        if normal is False:
            return _k("Kruskal–Wallis + Dunn (Holm düzeltmesi)", "Welch ANOVA (n büyükse)", ["bağımsız gözlemler"],
                      "ε²", "ist.grup_karsilastir", "Normallik sağlanmadı; sıra temelli k-grup testi.", ["conover1999", "holm1979"], u)
        ad = "Welch ANOVA + Games–Howell" if varyans_esit is False else "Tek yönlü ANOVA + Tukey HSD"
        return _k(ad, "Kruskal–Wallis (normallik yoksa)", ["normallik", "varyans homojenliği (Levene)"],
                  "η² / ω²", "ist.grup_karsilastir", "k bağımsız grup ortalaması; post hoc testle çoklu karşılaştırma kontrol edilir.",
                  ["field2018", "delacre2019"], u)

    if amac == "tekrarli":
        if sonuc in ("ikili", "sayim"):
            return _k("GEE (binom/Poisson, değiştirilebilir korelasyon)", "Genelleştirilmiş doğrusal karma model",
                      ["korelasyon yapısının uygunluğu", "yeterli küme sayısı"], "OR/IRR ve %95 GA",
                      "im.gee", "Kişi içi bağımlılık altında popülasyon ortalaması etkisi tahmin edilir.", ["liang1986"], u)
        if desen == "rkc" or grup >= 2:
            return _k("Doğrusal karma model (grup × zaman, rastgele kesişim; ITT)", "Karma ANOVA (eksik veri yoksa)",
                      ["artıkların normalliği", "rastgele etki yapısı", "eksik verinin MAR olması"],
                      "grup × zaman farkı (B) ve %95 GA; gerekirse d", "im.karma_model",
                      "Eksik ölçümü olan katılımcıları dışlamadan tüm veriyi kullanır; RKÇ'de ITT ile uyumludur.",
                      ["twisk2013", "hopewell2025"], u)
        if olcum == 2:
            if normal is False:
                return _k("Wilcoxon işaretli sıralar", "Bootstrap fark GA'sı", ["fark puanlarının simetrisi"], "r = Z/√N",
                          "ist.bagimli_karsilastir", "Fark puanları normal değil.", ["conover1999"], u)
            return _k("Bağımlı örneklem t testi", "Wilcoxon (normallik yoksa)", ["fark puanlarının normalliği"], "d_z ve %95 GA",
                      "ist.bagimli_karsilastir", "Aynı kişide iki ölçüm.", ["lakens2013"], u)
        return _k("Tekrarlı ölçüm ANOVA (Greenhouse–Geisser) veya doğrusal karma model", "Friedman (normallik yoksa)",
                  ["küresellik (Mauchly)", "normallik"], "kısmi η²", "im.karma_model / pingouin.rm_anova",
                  "Aynı kişide ≥3 ölçüm; eksik veri varsa karma model tercih edilir.", ["twisk2013"], u)

    if amac == "iliski":
        if sonuc in ("ikili", "kategorik"):
            return karar("karsilastir", sonuc=sonuc, grup=grup, beklenen_kucuk=beklenen_kucuk)
        if normal is False or sonuc == "sirali":
            return _k("Spearman ρ", "Kendall τ (küçük n, çok bağ)", ["monoton ilişki"], "ρ ve %95 GA", "ist.korelasyon(yontem='spearman')",
                      "Normallik yok veya sıralı veri.", ["field2018"], u)
        return _k("Pearson r", "Spearman ρ", ["doğrusallık", "iki değişkenli normallik", "aykırı değer yok"], "r ve %95 GA",
                  "ist.korelasyon", "İki sürekli değişken arasında doğrusal ilişki.", ["field2018"], u)

    if amac == "yordama":
        if yordayici and n and sonuc == "surekli" and n / yordayici < 10:
            u.append(f"Gözlem/yordayıcı = {n / yordayici:.1f} (<10): aşırı uyum riski; yordayıcı sayısını azaltın veya cezalı regresyon kullanın.")
        if sonuc == "ikili":
            if olay and yordayici and olay / yordayici < 10:
                u.append(f"Olay/parametre = {olay / yordayici:.1f} (<10): Firth veya cezalı lojistik regresyon önerilir.")
            return _k("Çoklu lojistik regresyon", "Firth/cezalı lojistik (az olay)", ["doğrusallık (logit; sürekli yordayıcılar)",
                      "çoklu bağlantı yok (VIF < 5)", "etkili gözlem yok"], "OR ve %95 GA, Nagelkerke R², AUC",
                      "ist.lojistik", "İkili sonucun bağımsız ilişkili faktörleri.", ["hosmer2013", "peduzzi1996"], u)
        if sonuc == "sirali":
            return _k("Sıralı lojistik regresyon (orantılı odds)", "Çok kategorili lojistik (varsayım bozulursa)",
                      ["orantılı odds varsayımı"], "OR ve %95 GA", "statsmodels OrderedModel", "Sıralı sonuç.", ["agresti2013"], u)
        if sonuc == "sayim":
            return _k("Poisson / negatif binom regresyon", "Sıfır şişirilmiş model (fazla sıfır)", ["aşırı yayılım"], "IRR ve %95 GA",
                      "statsmodels GLM", "Sayım sonucu.", ["hilbe2011"], u)
        if sonuc == "sure":
            return karar("sagkalim")
        if normal is False:
            return _k("Kantil regresyon (τ = .25/.50/.75)", "Sağlam (robust) regresyon; bootstrap GA",
                      ["kantil başına doğrusallık"], "B ve %95 GA (kantil başına)", "ist.kantil_regresyon",
                      "Artıklar normal değil veya ilişkinin dağılımın uçlarında farklı olması bekleniyor.", ["koenker1978", "koenker2005"], u)
        return _k("Hiyerarşik çoklu doğrusal regresyon", "Kantil regresyon (artıklar normal değilse)",
                  ["doğrusallık", "artıkların normalliği ve eş varyansı", "VIF < 5", "bağımsız artıklar", "etkili gözlem (Cook)"],
                  "B, β, ΔR², f²", "ist.regresyon", "Kontrol değişkenlerinden sonra odak yordayıcıların ek katkısı sınanır.",
                  ["field2018", "cohen2003"], u)

    if amac == "aracilik":
        return _k("Basit aracılık, yüzdelik bootstrap (≥5000) dolaylı etki", "Seri/paralel aracılık (birden çok aracı)",
                  ["doğrusallık", "ölçüm hatası düşük", "zamansal sıralama kuramla gerekçeli"], "ab ve %95 bootstrap GA; tamamen standartlaştırılmış etki",
                  "ist.aracilik / im.seri_aracilik", "Dolaylı etki normal dağılmadığından bootstrap GA önerilir (Sobel yerine).",
                  ["hayes2022", "preacher2008"], u + ["Kesitsel aracılık nedensel süreç kanıtı değildir (statistical mediation)."])
    if amac == "duzenleyicilik":
        return _k("Merkezlenmiş etkileşim terimli regresyon + basit eğimler + Johnson–Neyman", "Çok gruplu analiz (W kategorikse)",
                  ["etkileşim teriminde yeterli güç", "doğrusallık"], "ΔR², koşullu etkiler ve GA", "im.duzenleyicilik",
                  "Etkinin W'nin hangi değer aralığında anlamlı olduğu gösterilir.", ["hayes2022", "bauer2005"], u)
    if amac == "kosullu_aracilik":
        return _k("Koşullu süreç modeli (PROCESS Model 7/14 mantığı), düzenlenmiş aracılık indeksi", "Çok gruplu aracılık",
                  ["aracılık ve düzenleyicilik varsayımları"], "indeks ve %95 bootstrap GA; koşullu dolaylı etkiler",
                  "im.kosullu_aracilik", "Aracılık etkisinin W'ye bağlı değişimi tek indeksle sınanır.", ["hayes2015", "hayes2022"], u)
    if amac == "uyum":
        if sonuc in ("kategorik", "sirali", "ikili"):
            return _k("Cohen kappa (sıralıda ağırlıklı kappa)", "Krippendorff α (çok değerlendirici)", ["aynı birimlerin bağımsız değerlendirilmesi"],
                      "κ ve %95 GA", "im.kappa", "Şansa göre düzeltilmiş uyum.", ["mchugh2012"], u)
        return _k("ICC (iki yönlü, mutlak uyum; tek/ortalama ölçüm türü belirtilerek) + Bland–Altman", "Lin CCC",
                  ["normallik", "model türünün gerekçesi"], "ICC ve %95 GA; uyum sınırları", "im.icc / im.bland_altman",
                  "Korelasyon uyumu göstermez; ICC ve uyum sınırları gerekir.", ["koo2016", "bland1986"], u)
    if amac == "tani":
        return _k("ROC analizi, AUC (bootstrap/DeLong GA), Youden kesme noktası", "Sınıflandırma tablosu (duyarlılık, özgüllük, PPV, NPV)",
                  ["referans standardın geçerliği", "örneklemin hedef popülasyonu temsili"], "AUC ve GA; duyarlılık/özgüllük",
                  "im.roc_kesme", "Kesme noktası aynı veriden seçildiğinde iyimserdir; doğrulama örneği önerilir.",
                  ["delong1988", "youden1950", "bossuyt2015"], u)
    if amac == "olcek":
        return _k("DFA (yapı geçerliği) + McDonald ω + CR/AVE + HTMT", "AFA (yeni ölçek), IRT/Rasch (madde düzeyi)",
                  ["yeterli örneklem (≈ ≥200)", "çok değişkenli normallik (yoksa sağlam kestirici)"], "CFI, TLI, RMSEA, SRMR; ω; AVE",
                  "im.dfa / im.cr_ave / im.htmt / ist.guvenirlik", "Uyarlama çalışmasında kuramsal yapı DFA ile sınanır.",
                  ["hu1999", "mcdonald1999", "fornell1981", "henseler2015"], u)
    if amac == "profil":
        if n and n < 300:
            u.append("n < 300: LPA'da küçük sınıflar kararsızdır; sonuçları temkinli raporlayın.")
        return _k("Gizil profil analizi (Gauss karışım; 1–6 profil)", "k-ortalamalar kümeleme (keşif)",
                  ["yerel bağımsızlık (diyagonal model)", "standartlaştırılmış göstergeler"], "BIC/SABIC, entropi, en küçük sınıf %",
                  "ml.gizil_profil", "Kişi odaklı alt grupların belirlenmesi.", ["spurk2020", "nylund2007"], u)
    if amac == "ag":
        return _k("Gauss grafiksel model (EBICglasso, Spearman) + bootstrap doğruluk + CS katsayısı", "Ağ karşılaştırma testi (iki grup)",
                  ["yeterli örneklem (düğüm sayısına göre)", "madde içerik örtüşmesinin kontrolü"], "kenar ağırlıkları; güç/beklenen etki; CS",
                  "ag.ebicglasso / ag.bootstrap_kenar / ag.cs_katsayisi", "Değişkenlerin birbirine koşullu bağımlılık yapısı incelenir.",
                  ["epskamp2018", "burger2023", "friedman2008", "foygel2010"], u + ["Kesitsel ağ nedensel değildir."])
    if amac == "tahmin":
        if olay is not None and yordayici:
            u.append("Örneklem gerekçesi için ml.riley_orneklem kullanın.")
        return _k("Cezalı lojistik (elastik ağ) ile ML modellerinin (RF, gradyan artırma) tekrarlı ÇD karşılaştırması",
                  "Yalnızca cezalı regresyon (n < 200 veya az olay)", ["veri sızıntısı yok (pipeline)", "yeterli olay (Riley)"],
                  "AUC + GA, kalibrasyon eğimi/kesişimi, Brier, karar eğrisi", "ml.siniflandirma / ml.karar_egrisi / ml.aciklanabilirlik",
                  "Ayırt edicilik yanında kalibrasyon ve klinik net fayda raporlanmalıdır.",
                  ["collins2024", "riley2020", "vancalster2019", "vickers2006", "christodoulou2019", "lundberg2017"], u)
    if amac == "meta":
        return _k("Rastgele etkiler meta-analizi (REML + HKSJ), tahmin aralığı", "Sabit etki (yalnızca homojen ve aynı popülasyon)",
                  ["etki büyüklüklerinin karşılaştırılabilirliği", "k ≥ 10 değilse yayın yanlılığı testi yok"], "birleşik etki, GA, PI, τ², I²",
                  "im.meta_analiz / im.orman_grafigi", "Çalışmalar arası heterojenlik beklenir; HKSJ küçük k'da daha iyi kapsama sağlar.",
                  ["intHout2014", "higgins2002", "sterne2011", "page2021"], u)
    if amac == "zaman_serisi":
        return _k("Kesintili zaman serisi (bölümlü regresyon, Newey–West SE)", "ARIMA", ["≥ 8 ölçüm noktası önce/sonra (tercihen)", "otokorelasyon"],
                  "düzey ve eğim değişimi ve GA", "im.kesintili_zaman_serisi", "Önceki eğilim kontrol edilerek müdahale etkisi.", ["wagner2002"], u)
    if amac == "nedensel":
        return _k("Eğilim skoru (eşleştirme veya IPTW) + denge (|SMD| < .10) + E-değeri", "DAG ile seçilmiş kovaryatlarla düzeltilmiş regresyon",
                  ["ölçülmemiş karıştırıcı yok (varsayım)", "ortak destek (overlap)"], "ATT/ATE farkı ve GA; E-değeri",
                  "im.egilim_skoru / im.e_degeri", "Gözlemsel veride ölçülen karıştırıcıların dengelenmesi.",
                  ["austin2011", "vanderweele2017"], u)
    if amac == "esdegerlik":
        return _k("TOST eşdeğerlik testi (önceden belirlenmiş sınır)", "Bayes faktörü", ["eşdeğerlik sınırının klinik gerekçesi"],
                  "fark ve %90 GA", "im.tost", "Anlamsız p 'fark yok' kanıtı değildir.", ["lakens2017"], u)
    if amac == "guc":
        return _k("A priori güç analizi (α, güç, etki büyüklüğü kaynağı)", "Duyarlılık güç analizi (örneklem sabitse)",
                  ["etki büyüklüğünün literatür/pilot dayanağı"], "—", "ist.guc_analizi / ml.riley_orneklem",
                  "Post hoc (gözlenen) güç bilgi vermez.", ["faul2007", "hoenig2001"], u)
    if amac == "eksik_veri":
        return _k("Little MCAR testi + çoklu atama (MICE, m ≥ 20)", "Tam bilgi en çok olabilirlik (FIML)", ["MAR varsayımı"],
                  "Rubin kurallarıyla birleştirilmiş tahminler", "im.little_mcar / im.coklu_atama_ols",
                  "Liste bazında silme MCAR dışında yanlılık yaratır.", ["little1988", "vanbuuren2011"], u)
    if amac == "sagkalim":
        return _k("Kaplan–Meier + log-rank; Cox orantılı tehlikeler", "Parametrik sağkalım; rakip riskler (Fine–Gray)",
                  ["orantılı tehlikeler (Schoenfeld)", "bilgi vermeyen sansürleme"], "HR ve %95 GA; medyan süre",
                  "lifelines (KaplanMeierFitter, CoxPHFitter)", "Olaya kadar geçen süre ve sansürleme.", ["cox1972"], u)
    raise ValueError(f"amac şunlardan biri olmalı: {', '.join(AMACLAR)}")


def veriden_karar(df, amac, y, grup=None, x=None, **kw):
    """Normallik ve varyans eşitliğini veriden ölçüp karar verir; ölçümleri de döndürür."""
    import numpy as np
    from scipy import stats
    olcum = {}
    s = df[y].dropna()
    sonuc = kw.pop("sonuc", None) or ("ikili" if s.nunique() == 2 else "surekli")
    normal = None
    if sonuc == "surekli":
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from istatistik import normallik_karari
        gruplar = [g[y].dropna().values for _, g in df.groupby(grup)] if grup else [s.values]
        sonuclar = []
        for g in gruplar:
            nk = normallik_karari(g)
            olcum.setdefault("grup_normallik", []).append(nk)
            if nk["normal"] is not None:
                sonuclar.append(nk["normal"])
        normal = all(sonuclar) if sonuclar else None
        if grup and len(gruplar) >= 2:
            lev = stats.levene(*gruplar).pvalue
            olcum["levene_p"] = round(lev, 3)
            kw["varyans_esit"] = lev >= .05
    k = karar(amac, sonuc=sonuc, grup=df[grup].nunique() if grup else 1, n=len(s), normal=normal, **kw)
    k["olcumler"] = olcum
    k["karar_kurali"] = "Normallik: Kim (2013) örneklem büyüklüğüne bağlı çarpıklık/basıklık ölçütü [kim2013]; varyans: Levene p ≥ .05 (Welch varsayılan) [delacre2017]"
    k["kaynak_anahtarlari"] = sorted(set(k["kaynak_anahtarlari"]) | {"kim2013"})
    return k


def ozet_metin(k: dict) -> str:
    """Sohbette kısa sunum için tek blok metin."""
    satir = [f"Yöntem: {k['yontem']}", f"Alternatif: {k['alternatif']}", f"Gerekçe: {k['gerekce']}",
             f"Kontrol: {'; '.join(k['varsayimlar'])}", f"Etki büyüklüğü: {k['etki_buyuklugu']}",
             f"Kaynak anahtarları: {', '.join(k['kaynak_anahtarlari'])} (doğrulanmadan kaynakçaya girmez)"]
    if k.get("uyari"):
        satir.append("Uyarı: " + " ".join(k["uyari"]))
    return "\n".join(satir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--amac", required=True, choices=AMACLAR)
    ap.add_argument("--sonuc", default="surekli")
    ap.add_argument("--grup", type=int, default=2)
    ap.add_argument("--olcum", type=int, default=1)
    ap.add_argument("--n", type=int)
    ap.add_argument("--normal", choices=["evet", "hayir"])
    ap.add_argument("--kovaryat", action="store_true")
    ap.add_argument("--desen", default="kesitsel")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    k = karar(a.amac, sonuc=a.sonuc, grup=a.grup, olcum=a.olcum, n=a.n,
              normal=None if a.normal is None else a.normal == "evet", kovaryat=a.kovaryat, desen=a.desen)
    print(json.dumps(k, ensure_ascii=False, indent=1) if a.json else ozet_metin(k))
