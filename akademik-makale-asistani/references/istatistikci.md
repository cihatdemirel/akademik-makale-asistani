# Rol: İstatistikçi

Temel analizler bu dosyada; ileri ve yeni yöntemler (ağ analizi, makine öğrenmesi, gizil profil, koşullu aracılık, karma model, eğilim skoru, meta-analiz, psikometri, eşdeğerlik vb.) ve **yöntem danışmanı** tablosu `ileri-yontemler.md` içinde. Her analiz isteğinde önce oradaki soru → yöntem tablosuna bak; daha uygun bir yöntem varsa istenen analizden sonra kısaca öner.

## İçindekiler
1. Çalışma akışı
2. Test seçimi
3. Betik kullanımı
4. Raporlama kalıpları
5. Sık hatalar (hakem bunları sorar)
6. Sınırlar

## 1. Çalışma akışı

1. **Veriyi tanı:** Değişken listesi, tipleri, SPSS etiketleri, eksik değer sayısı, aykırı değerler, ters puanlanan maddeler. Ölçek toplam puanları hazır değilse madde puanlarından hesapla (ters maddeleri sor ya da ölçek kaynağından doğrula).
2. **Yöntem seçimi:** `yontem_secici.veriden_karar` (veri varsa) veya `karar` ile; gerekçe ve kaynak anahtarlarını rapora ekle. İleri seçenekler için `ileri-yontemler.md` §1.
3. **Araştırma sorusunu analize çevir:** Her amaç/hipotez için bağımlı ve bağımsız değişken, ölçüm düzeyi, desen. Bunu kullanıcıya bir tabloyla göster; belirsizlik varsa tek soruyla netleştir.
4. **Varsayımlar:** Normallik (Kim 2013: n<50 |z|<1.96; 50–299 |z|<3.29; ≥300 |çarpıklık|≤2, |basıklık|≤7; Shapiro–Wilk bilgi amaçlı; grafikle birlikte), varyans homojenliği (Levene), doğrusallık, çoklu bağlantı (VIF<5), artıkların dağılımı, etkili gözlemler (Cook's d).
5. **Analiz:** Kodu çalıştırarak yap. Her sonuçta etki büyüklüğü ve %95 GA. Seed sabitle. Normallik kararı `ist.normallik` (Kim 2013 ölçütü) ile verilir.
6. **Rapor:** APA 7 tabloları (Tablo 1 tanımlayıcı, sonra ana analiz) + Bulgular metni + Yöntem bölümüne eklenecek "Data analysis" paragrafı + kullanılan kod.
7. **Denetim:** Bulgular metnini `istatistik_denetimi.denetle(metin)` ile kontrol et; tablo n'leri ve yüzdeleri tutarlı mı bak.
8. **Yorum notu:** Bulguların klinik anlamı, sınırlılıklar, hakemin soracağı noktalar.

## 2. Test seçimi

| Soru | Parametrik | Parametrik olmayan | Etki büyüklüğü |
|---|---|---|---|
| 2 bağımsız grup | Bağımsız t (eşit olmayan varyansta Welch) | Mann–Whitney U | Cohen d / Hedges g; r = Z/√N |
| 3+ bağımsız grup | Tek yönlü ANOVA (Welch ANOVA) + Tukey/Games–Howell | Kruskal–Wallis + Dunn (Bonferroni/Holm) | η² / ω²; ε² |
| 2 ölçüm (aynı kişi) | Bağımlı t | Wilcoxon | d_z; r |
| 3+ ölçüm | Tekrarlı ölçüm ANOVA (küresellik, Greenhouse–Geisser) | Friedman | partial η²; Kendall W |
| Grup × zaman (RKÇ) | Doğrusal karma model (tercih, ITT) veya karma ANOVA | — | grup farkı ve GA |
| RKÇ son ölçüm, ön test kontrolü | ANCOVA | — | partial η², düzeltilmiş ortalamalar |
| Kategorik ilişki | Ki-kare (beklenen <5 ise Fisher) | — | Cramér V; OR |
| İki sürekli değişken | Pearson r | Spearman ρ | r |
| Sürekli sonucu yordama | Çoklu doğrusal regresyon (hiyerarşik) | Kantil regresyon | R², ΔR², f², β |
| İkili sonuç | Lojistik regresyon | — | OR (%95 GA), Nagelkerke R², AUC |
| Aracılık | Bootstrap dolaylı etki (≥5000) | — | a, b, c, c′, ab ve %95 GA |
| Ölçek güvenirliği | Cronbach α, McDonald ω | — | — |
| Örneklem büyüklüğü | statsmodels güç analizi; tahmin modelinde Riley ölçütleri | — | — |

İleri seçenekler (düzenleyicilik, seri/koşullu aracılık, GEE, LPA, ağ, ML, meta-analiz, DFA, eğilim skoru vb.) için `ileri-yontemler.md`.

Örneklem/model oranı: doğrusal regresyonda kabaca ≥10–15 gözlem/yordayıcı; lojistikte olay/parametre ≥10 bir alt sınırdır, tahmin modelinde Riley ölçütlerini kullan.

## 3. Betik kullanımı

```python
import sys; sys.path.insert(0, "<skill_klasoru>/scripts")
import istatistik as ist

df, etiketler = ist.yukle("/mnt/user-data/uploads/veri.sav")   # .sav, .xlsx, .csv
ist.veri_ozeti(df)
ist.tanimlayici(df, ["yas", "olcek_toplam"])
ist.kategorik_tablo(df, ["cinsiyet", "egitim"])
ist.normallik(df, ["olcek_toplam"])
ist.grup_karsilastir(df, "olcek_toplam", "cinsiyet")   # varsayıma göre test + etki büyüklüğü (+ post hoc)
ist.bagimli_karsilastir(df, "once", "sonra")
ist.ki_kare(df, "cinsiyet", "grup")
ist.korelasyon(df, ["a", "b", "c"], yontem="pearson")
ist.guvenirlik(df, ["m1", "m2", "m3"])                 # α ve ω
ist.regresyon(df, "y", None, bloklar=[["yas", "cinsiyet_K"], ["x1", "x2"]])   # hiyerarşik, VIF
ist.lojistik(df, "olay", ["x1", "x2"])
ist.aracilik(df, x="aile_destegi", m="izolasyon", y="yasam_doyumu", kovaryatlar=["yas"])
ist.kantil_regresyon(df, "y", ["x1", "x2"], kantiller=[0.25, 0.5, 0.75])
ist.guc_analizi(test="t", etki=0.5, alfa=0.05, guc=0.80, kayip=0.10)
ist.apa_kaydet({"Tablo 1": tablo1, "Tablo 2": tablo2}, "/mnt/user-data/outputs/tablolar.xlsx")
```

Kategorik değişkenleri regresyona almadan önce kukla değişkene çevir (`pd.get_dummies(..., drop_first=True)`).

Kullanıcı yalnızca SPSS/JASP/Jamovi çıktısı yapıştırırsa yeniden hesaplama; çıktıyı yorumla, tutarsızlıkları (sd, n, p uyumu) kontrol et ve APA metnine çevir.

## 4. Raporlama kalıpları (APA 7)

- t testi: *t*(118) = 2.41, *p* = .018, *d* = 0.44, 95% CI [0.08, 0.80]
- ANOVA: *F*(2, 297) = 5.62, *p* = .004, η² = .04
- Mann–Whitney: *U* = 1450.5, *z* = −2.31, *p* = .021, *r* = .21
- Ki-kare: χ²(2, *N* = 300) = 8.14, *p* = .017, Cramér's *V* = .16
- Korelasyon: *r*(298) = .34, *p* < .001
- Regresyon: Model 2 ek olarak varyansın %12'sini açıkladı, Δ*R*² = .12, *F*change(2, 293) = 21.4, *p* < .001; β = .28, *p* < .001
- Aracılık: dolaylı etki *ab* = 0.12, %95 bootstrap GA [0.05, 0.21] (5000 yeniden örnekleme)
- Lojistik: OR = 2.14, %95 GA [1.31, 3.49], *p* = .002

Ondalık: genellikle 2; p için 3; 1'i aşamayan değerlerde (r, β, p) baştaki sıfır yazılmaz (APA). Vancouver/AMA dergilerinde derginin kuralına uy.

"Data analysis" paragrafı: yazılım ve sürümü, eksik veri yönetimi, normallik değerlendirmesi, testler, varsayım kontrolleri, çoklu karşılaştırma düzeltmesi, anlamlılık düzeyi, etki büyüklüğü ölçütleri ve yorum eşikleri.

## 5. Sık hatalar (hakem bunları sorar)

- Kesitsel aracılık analizini nedensel süreç gibi sunmak → "statistical mediation" dili, sınırlılıklarda belirt.
- Post hoc güç analizi → elde edilen etki büyüklüğü + GA veya duyarlılık güç analizi ("bu örneklemle saptanabilecek en küçük etki").
- Yalnızca p raporlamak, etki büyüklüğü vermemek.
- Çok sayıda karşılaştırmada düzeltme yapmamak.
- Likert madde düzeyinde parametrik test; ya da ölçek toplamını gereksiz yere parametrik olmayan teste sokmak.
- Tek değişkenli anlamlılığa göre değişken seçip regresyona almak (gerekçe kuram/literatür/DAG olmalı).
- RKÇ'de grup içi öntest–sontest karşılaştırmasını etkililik kanıtı saymak; gruplar arası analiz şart.
- RKÇ başlangıç özelliklerinde p değeri raporlamak (CONSORT önermez).
- Ölçeğin bu örneklemdeki güvenirliğini vermemek.
- Anlamsız farkı "eşdeğerlik" diye yorumlamak (TOST gerekir).

## 6. Sınırlar

Ortamda R yoktur; lavaan/PROCESS/bootnet çıktıları Python eşdeğerleriyle üretilir ve küçük sayısal farklar olabilir. Karmaşık modellerde (çok düzeyli SEM, gizil büyüme, çok gruplu değişmezlik, polikorik ağlar) analizi yap ama bağımsız doğrulama öner. Her sonucu kodu ve paket sürümleriyle birlikte ver ki tekrarlanabilsin. Ortam ve paket ayrıntısı: `ileri-yontemler.md` §5.
