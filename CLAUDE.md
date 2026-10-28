# Bakım ajanı talimatları (akademik-makale-asistani)

Bu depo bir Claude skill'idir: `akademik-makale-asistani/`. Senin görevin aylık bakımdır. Kullanıcıya doğrudan ulaşamazsın; yaptığın her değişiklik bir PR olarak insan onayına gider.

## Aylık bakım
1. `akademik-makale-asistani/references/guncellik-kaydi.md` dosyasındaki "Bakım modu" adımlarını uygula (adım 1'deki kopyalama gerekmez; doğrudan depodaki dosyaları düzenle).
2. Yalnızca **birincil kaynaklara** dayanarak değişiklik yap: EQUATOR Network, yönergenin resmi yayını, ICMJE, APA, PubMed/Crossref kayıtları, paket belgeleri. İkincil blog ve özet sitelerine dayanarak kural değiştirme.
3. `yontem-kaynaklari.md`: "Doğrulanmadı" durumundaki künyelerden en fazla 15'ini doğrula. Doğrulama = PubMed (eutils) veya Crossref (api.crossref.org) kaydında yazar, yıl, başlık, dergi eşleşmesi. Eşleşirse DOI ekle ve Durum'u `Doğrulandı: YYYY-AA-GG, DOI` yap. Künye hatalıysa düzelt ve notta belirt. Bulamazsan `Bulunamadı` yaz; asla tahmin edilmiş DOI yazma, satırı silme.
4. `python3 akademik-makale-asistani/scripts/duman_testi.py` çalıştır. Başarısız modül varsa en küçük düzeltmeyi yap ve testi yeniden çalıştır. Test geçmeden bitirme.
5. Paket sürümü güncellemesi gerekiyorsa `requirements.txt` içindeki sürümü yalnızca testler geçiyorsa yükselt.
6. Sürüm numarasını ve tarihleri `guncellik-kaydi.md` içinde güncelle (küçük düzeltme: 4.0 → 4.1; yönerge değişikliği: 4.x → 5.0) ve `SKILL.md` başlığındaki sürümü eşitle.
7. Depo köküne `BAKIM_NOTU.md` yaz: ne değişti, hangi birincil kaynağa dayanarak (URL), doğrulanan/bulunamayan künyeler, test sonucu, belirsiz kalanlar. Değişiklik yoksa yalnızca "Değişiklik gerekmedi" ve kontrol edilen öğeleri yaz.

## Kurallar
- Uydurma bilgi, DOI, sürüm numarası yazma. Emin değilsen değiştirme; notta "belirsiz" olarak raporla.
- `SKILL.md` frontmatter'ını (name, description) değiştirme; açıklama 1024 karakteri ve tek satırı aşmamalı, içinde ": " geçmemeli.
- Skill'in yapısını, rol tablosunu ve kurallarını yeniden yazma; yalnızca güncellik ve hata düzeltmesi yap.
- Yeni dosya ekleme yalnızca bakım için zorunluysa.
