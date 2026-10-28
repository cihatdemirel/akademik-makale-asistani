# Gönderim Öncesi Denetim

Editör çalışmalarında masa reddinin en sık nedenleri: kapsam uyumsuzluğu, zayıf gerekçe (araştırma ihtiyacının kurulamaması), desen kusurları, anlaşılması güç yazım ve yazım kurallarına uyulmaması. Denetimi bu sırayla yap.

## 1. Dergi uyumu (masa reddi)
- [ ] Konu derginin kapsamında; dergi son 2–3 yılda benzer makaleler yayımlamış.
- [ ] Uluslararası okura katkı açık (yerel çalışma algısı kırılmış).
- [ ] Kelime sınırı, özet yapısı, kaynak stili ve sayısı, tablo/şekil sınırı uygun.
- [ ] Zorunlu kutucuklar ve beyanlar eksiksiz.
- [ ] Kapak mektubu: boşluk, katkı ve dergiyle uyum 3–4 cümlede.

## 2. Gerekçe ve özgünlük
- [ ] Girişte boşluk somut olarak tanımlanmış (yalnızca "az çalışma var" değil, neyin bilinmediği ve neden önemli olduğu).
- [ ] Amaç/hipotez boşlukla birebir örtüşüyor.
- [ ] Başlık, özet ve amaç aynı değişkenleri aynı adlarla anıyor.

## 3. Yöntem
- [ ] Desen soruya uygun.
- [ ] A priori güç analizi tam raporlanmış.
- [ ] Ölçeklerin Türkçe geçerlik-güvenirlik kaynağı ve bu örneklemdeki güvenirlik değeri var.
- [ ] Karıştırıcı değişkenler gerekçeli biçimde kontrol edilmiş.
- [ ] Kayıp veri, varsayım kontrolleri ve çoklu karşılaştırma ele alınmış.
- [ ] Uygun raporlama yönergesi izlenmiş, checklist hazır.
- [ ] Etik kurul bilgisi ve (RKÇ ise) kayıt numarası var.

## 4. Bulgular ve yorum
- [ ] Tablo ve metin sayıları tutarlı; n'ler toplanıyor (`istatistik_denetimi.py`: p yeniden hesaplama, GRIM, yüzde).
- [ ] Etki büyüklüğü ve GA verilmiş.
- [ ] Nedensellik dili desene uygun.
- [ ] Tartışma tüm ana bulguları literatürle ilişkilendiriyor; anlamsız bulgular da tartışılmış.
- [ ] Sınırlılıklar dürüst ve sonuca etkisiyle birlikte.
- [ ] Sonuç veriyle sınırlı; uygulama önerileri somut.

## 5. Dil ve kaynaklar
- [ ] Abartılı ve mekanik ifadeler temizlenmiş.
- [ ] Terim ve kısaltma tutarlılığı sağlanmış.
- [ ] Kaynakların büyük kısmı son 5 yıldan; eski kaynaklar gerekçeli.
- [ ] Tüm kaynaklar doğrulanmış (`kaynak_denetimi.py` + `kaynak-butunlugu.md`); geri çekilmiş veya yağmacı dergi kaynağı yok.
- [ ] Benzerlik oranı kontrol edilmiş (özellikle yöntem bölümünde kendi eski metinlerinden alıntı).
- [ ] Yapay zekâ kullanımı dergi politikasına göre beyan edilmiş.

## Rapor şablonu

```
## Gönderim öncesi değerlendirme: [kısa başlık]

**Masa reddi riski:** Yüksek / Orta / Düşük — [1–2 cümle gerekçe]
**Önerilen raporlama yönergesi:** [ad + sürüm]
**Kelime durumu:** [toplam / sınır; bütçeyi aşan bölüm]

### Kritik sorunlar (düzeltilmeden gönderilmemeli)
1. [Sorun] — [neden önemli] — [nasıl düzeltilir]

### Önemli sorunlar (hakem büyük olasılıkla soracak)
1. …

### Küçük düzeltmeler
- …

### Güçlü yanlar
- [en fazla 2–3 madde]

### Öncelikli 5 eylem
1. …
```
