# İleri ve Yeni Yöntemler — Yöntem Danışmanı

## İçindekiler
1. Yöntem danışmanı: soru → yöntem
2. Proaktif öneri kuralları
3. Modül ve fonksiyon haritası
4. Yönteme özgü raporlama ve tuzaklar
5. Ortam, süre ve eksik paketler
6. Atıf notu

## 1. Yöntem danışmanı: soru → yöntem

Kullanıcının araştırma sorusunu aşağıdaki tabloyla eşleştir. Klasik yöntem uygunsa onu kullan; ileri yöntem gerçekten yeni bilgi üretiyorsa öner. Yöntemi değil soruyu merkeze al: "makine öğrenmesi kullanalım" değil, "bu soruya en iyi hangi yöntem cevap verir".

| Araştırma sorusu | Klasik | İleri / yeni seçenek | Ne kazandırır |
|---|---|---|---|
| X, Y ile ilişkili mi; ilişki dağılımın her yerinde aynı mı? | Çoklu regresyon | **Kantil regresyon** | Düşük/yüksek uçlardaki (örn. en kötü öz bakım) farklı ilişkiler |
| Hangi yordayıcı daha önemli? | Standart β | **Baskınlık analizi** | Çoklu bağlantıdan etkilenmeyen göreli önem |
| X'in Y'ye etkisi M üzerinden mi? | Basit aracılık | **Seri / paralel aracılık**, **koşullu (düzenlenmiş) aracılık** (Model 7/14) | Mekanizmanın kimde ve hangi koşulda işlediği |
| İlişki W'nin düzeyine göre değişiyor mu? | Etkileşim terimi | **Basit eğimler + Johnson–Neyman** | Etkinin anlamlı olduğu W aralığı |
| Belirtiler/yapılar birbirini nasıl etkiliyor? | Korelasyon matrisi | **Psikometrik ağ analizi** (EBICglasso, merkezilik, köprü), **ağ karşılaştırma** | Merkezî belirtiler, müdahale hedefi, iki yapı arasındaki köprüler |
| Örneklemde alt gruplar var mı? | Ortanca bölme, kümeleme | **Gizil profil analizi (LPA)** | Kişi odaklı profiller; profillere göre sonuç karşılaştırması |
| Bir sonucu (düşme, yeniden yatış, tükenmişlik) bireysel düzeyde tahmin edebilir miyiz? | Lojistik regresyon | **Makine öğrenmesi** (elastik ağ, rastgele orman, gradyan artırma) + kalibrasyon + **karar eğrisi** + **SHAP** | Tahmin performansı, klinik net fayda, açıklanabilirlik |
| RKÇ'de grup × zaman etkisi | Tekrarlı ölçüm ANOVA | **Doğrusal karma model** (ITT, eksik ölçümlü katılımcı dışlanmaz), **ANCOVA** (ön test kontrolü) | Daha az yanlılık, daha yüksek güç |
| Tekrarlı ikili/sayım sonucu | Ki-kare | **GEE** | Kişi içi bağımlılığın hesaba katılması |
| İki uygulama eşdeğer mi? | Anlamsız p = "fark yok" (yanlış) | **TOST eşdeğerlik testi** | "Fark yok" iddiasını kanıtlayabilmek |
| Gözlemsel veride tedavi/maruziyet etkisi | Düzeltilmiş regresyon | **Eğilim skoru** (eşleştirme, IPTW) + **E-değeri** | Karıştırıcı dengesi ve ölçülmemiş karıştırıcıya duyarlılık |
| Bir politika/eğitim sonrası eğilim değişti mi? | Önce–sonra karşılaştırma | **Kesintili zaman serisi** | Düzey ve eğim değişimi, eğilim kontrolü |
| Eksik veri | Liste bazında silme | **Little MCAR + çoklu atama (MICE)** | Yanlılık ve güç kaybının azalması |
| Ölçek geçerliği | Cronbach α | **DFA**, **McDonald ω**, **CR/AVE**, **HTMT**, (gerekirse) **IRT/Rasch**, **ölçme değişmezliği** | Hakemlerin artık beklediği psikometrik kanıt |
| Tanı/tarama aracı kesme noktası | — | **ROC + Youden**, bootstrap GA | Klinik kesme noktası |
| Ölçüm uyumu | Korelasyon (yanlış) | **ICC**, **ağırlıklı kappa**, **Bland–Altman** | Gerçek uyum |
| Çalışmaların birleştirilmesi | — | **Rastgele etkiler meta-analizi** (REML + HKSJ), tahmin aralığı, Egger, orman grafiği | Güncel meta-analiz standardı |
| Bulgu klinik olarak anlamlı mı? | p değeri | **MCID / yanıt veren analizi**, etki büyüklüğü + GA | Klinik yorum |
| Bulgu gücü / sıfır kanıtı | p | **Bayes faktörü** (pingouin `bayesfactor_ttest`, `bayesfactor_pearson`) | H0 lehine kanıtı da ölçebilme |
| Örneklem: tahmin modeli | 10 olay/değişken kuralı | **Riley ölçütleri** (`ml.riley_orneklem`) | TRIPOD+AI uyumlu örneklem gerekçesi |

## 2. Proaktif öneri kuralları

- Kullanıcı bir analiz isterken tabloda daha uygun bir seçenek varsa, istenen analizi yaptıktan sonra **tek paragrafta** öner: ne kazandırır, ek veri gerekir mi, hakem algısı.
- Öneriyi yalnızca veri yapısı izin veriyorsa yap (örn. LPA için n ≥ ~300 ve en az 3–4 gösterge; ağ analizi için değişken başına yeterli örneklem ve sıralı/sürekli veri; ML için Riley ölçütlerini karşılayan örneklem).
- Küçük örneklemde (n < 200) karmaşık ML'yi önermek yerine cezalı regresyonu öner; bunun gerekçesini söyle.
- Kesitsel veride ağ, aracılık veya ML sonuçlarının nedensel olmadığını her öneride belirt.
- "Moda" olduğu için yöntem önerme. Hakemin "neden bu yöntem?" sorusuna tek cümlelik net cevap yoksa önerme.

## 3. Modül ve fonksiyon haritası

```python
import sys; sys.path.insert(0, "<skill>/scripts")
import istatistik as ist          # temel: yükleme, tanımlayıcı, testler, regresyon, aracılık, güç
import ileri_modeller as im       # ileri modeller
import makine_ogrenmesi as ml     # ML ve gizil profil
import ag_analizi as ag           # ağ analizi
```

| Görev | Fonksiyon |
|---|---|
| Düzenleyicilik, Johnson–Neyman | `im.duzenleyicilik(df, x, w, y, kovaryatlar)` |
| Seri aracılık (Model 6) | `im.seri_aracilik(df, x, m1, m2, y)` |
| Paralel aracılık | `pingouin.mediation_analysis(..., m=[m1, m2])` |
| Koşullu aracılık (Model 7/14) | `im.kosullu_aracilik(df, x, m, y, w, model=7)` |
| ANCOVA + düzeltilmiş ortalamalar | `im.ancova(df, y, grup, [ontest])` |
| Doğrusal karma model (uzun veri) | `im.karma_model(df_uzun, y, zaman, grup, kimlik)` |
| GEE | `im.gee(df_uzun, y, X, kimlik, aile="binomial")` |
| Eşdeğerlik | `im.tost(x1, x2, sinir)` |
| Little MCAR / MICE | `im.little_mcar(df, cols)`, `im.coklu_atama_ols(df, y, X, m=20)` |
| Eğilim skoru, E-değeri | `im.egilim_skoru(df, tedavi, kov, y)`, `im.e_degeri(rr, gu_alt)` |
| Kesintili zaman serisi | `im.kesintili_zaman_serisi(df, y, zaman, mudahale_zamani)` |
| ROC/kesme, ICC, kappa, Bland–Altman | `im.roc_kesme`, `im.icc`, `im.kappa`, `im.bland_altman` |
| Meta-analiz + orman grafiği | `im.hedges_g(...)`, `im.meta_analiz(etki, varyans, calismalar)`, `im.orman_grafigi(sonuc, yol)` |
| DFA, CR/AVE, HTMT | `im.dfa(df, "F1 =~ a + b + c")`, `im.cr_ave({...})`, `im.htmt(df, {...})` |
| Baskınlık analizi | `im.baskinlik_analizi(df, y, X)` |
| ML sınıflandırma / regresyon | `ml.siniflandirma(df, y, X, ayarla=True)`, `ml.regresyon_ml(...)` |
| AUC GA, kalibrasyon, karar eğrisi | `ml.auc_ga(y, p)`, `ml.kalibrasyon_grafigi(y, p, yol)`, `ml.karar_egrisi(y, {...}, yol=...)` |
| SHAP / permütasyon önemi | `ml.aciklanabilirlik(df, y, X, model="Rastgele orman", yol=...)` |
| Tahmin modeli örneklemi | `ml.riley_orneklem(param_sayisi, prevalans, r2cs)` |
| Gizil profil analizi | `ml.gizil_profil(df, gostergeler)`, `ml.profil_ozeti(sonuc, "diag", k)` |
| Ağ tahmini, özet, merkezilik | `ag.ebicglasso(df, v)`, `ag.ozet(W)`, `ag.merkezilik(W, topluluklar)` |
| Ağ doğruluk ve kararlılık | `ag.bootstrap_kenar(df, v)`, `ag.cs_katsayisi(df, v)` |
| Ağ karşılaştırma | `ag.ag_karsilastir(df1, df2, v)` |
| Ağ ve merkezilik grafiği | `ag.ciz(W, yol, topluluklar)`, `ag.merkezilik_grafigi(z, yol)` |

## 4. Yönteme özgü raporlama ve tuzaklar

**Ağ analizi:** Tahmin yöntemi (EBICglasso, γ), korelasyon türü (sıralı veride Spearman; polikorik bu ortamda yok), düğüm sayısı ve örneklem, kenar doğruluğu (bootstrap GA), merkezilik kararlılığı (CS ≥ .25, tercihen ≥ .50), yalnızca kararlı merkezilik ölçütlerini yorumlama, topluluk tanımı (köprü analizi için). Yakınlık/aradalık genellikle kararsızdır; güç ve beklenen etkiyi öne çıkar. Kesitsel ağ nedensel değildir. Benzer içerikli maddeler (topolojik örtüşme) ağı şişirir; maddeleri seçerken bunu kontrol et.

**Makine öğrenmesi (TRIPOD+AI):** Veri kaynağı ve tarihleri, sonuç tanımı, aday yordayıcılar ve ön işleme, eksik veri yönetimi, örneklem gerekçesi (Riley), doğrulama şeması (tekrarlı/iç içe ÇD; mümkünse zamansal veya dış geçerleme), ayırt edicilik (AUC ve GA), **kalibrasyon** (eğim, kesişim, grafik; yalnızca AUC yetmez), klinik fayda (karar eğrisi), açıklanabilirlik (SHAP; önem ≠ nedensellik), adalet/alt grup performansı, kod ve paylaşım. Karmaşık modeli seçmeden önce lojistik regresyonla karşılaştır; üstünlük yoksa basit modeli tercih et ve bunu açıkça yaz. Ön işlemeyi (atama, ölçekleme) çapraz doğrulamanın içinde yap; betik bunu pipeline ile sağlar.

**Gizil profil analizi:** Göstergeler standartlaştırılır; 1–6 profil denenir; BIC/SABIC, entropi (≥ .80), en küçük sınıf (≥ %5), yorumlanabilirlik birlikte değerlendirilir. BLRT/LMR bu ortamda yok; R (tidyLPA/mclust) veya Mplus ile doğrulama önerilebilir. Profilleri sonuçla karşılaştırırken sınıflandırma belirsizliğine dikkat (BCH/3-adımlı yaklaşım ideal).

**Koşullu aracılık:** İndeksin GA'sı sıfırı içermiyorsa düzenlenmiş aracılık vardır; koşullu dolaylı etkileri W'nin −1SS/ort/+1SS düzeylerinde ver. Kesitsel veride "mekanizma kanıtlandı" deme.

**Karma model:** Rastgele etki yapısını gerekçelendir; ITT ilkesini belirt; etkileşim katsayılarını grup × zaman farkı olarak yorumla; gerekirse tahmin edilen ortalamalar grafiği ver.

**Eğilim skoru:** Kovaryat seçimi kuram/DAG ile; denge |SMD| < .10; eşleşmeyen tedavili sayısını raporla; sonuçla birlikte E-değeri ver.

**Meta-analiz:** REML + HKSJ, tahmin aralığı mutlaka; I² tek başına heterojenlik ölçüsü değildir; k < 10 iken yayın yanlılığı testlerini yorumlama; yanlılık riski (RoB 2 / ROBINS-I) ve GRADE ayrıca gerekir.

**Psikometri:** Ölçek uyarlamasında DFA uyum ölçütleri, standart yükler, ω, CR/AVE, HTMT; gerekirse ölçme değişmezliği (yapısal → metrik → skaler; ΔCFI ≤ .01). Çok gruplu değişmezlik bu ortamda sınırlıdır; gerekirse R lavaan veya JASP ile doğrulama öner.

## 5. Ortam, süre ve eksik paketler

- Mevcut: pandas, scipy, statsmodels, pingouin, scikit-learn, LightGBM, SHAP, networkx, semopy, lifelines, pyreadstat, matplotlib, seaborn.
- Bu ortamda çalışmayan: factor_analyzer (sklearn uyumsuzluğu) → ω ve AFA için betikteki kendi uygulamalar kullanılır.
- Gerekirse kurulabilir (`pip install --break-system-packages`): `girth` (IRT/Rasch), `pymc` + `arviz` (tam Bayesçi modeller; kurulumu ağır), `xgboost`, `imbalanced-learn`. Kurmadan önce kullanıcıya gerekip gerekmediğini değerlendir.
- R yoktur. Polikorik korelasyon, BLRT, PROCESS/lavaan'a özgü çıktılar birebir üretilemez; yöntem bölümünde Python paketlerini ve sürümlerini yaz.
- Süre: ağ bootstrap'i tek çekirdekte 10–20 değişkende örneklem başına ~0,3–0,7 sn (1000 örneklem ≈ 5–12 dk); CS katsayısı daha uzundur. Uzun işleri `nohup python3 analiz.py > log.txt 2>&1 &` ile arka planda çalıştır ve aralıklarla kontrol et. ML'de iç içe ayarlama süreyi 5–10 kat artırır.
- Her analizde `random_state/seed` sabitle ve kodu çıktıyla birlikte kullanıcıya ver (tekrarlanabilirlik).

## 6. Atıf notu

Yöntem kaynakları `yontem-kaynaklari.md` içinde anahtarlarıyla listelidir; makaleye yazılmadan önce `kaynak-butunlugu.md` protokolüyle doğrulanır.
