# Güncellik Kaydı ve Bakım Modu

Skill sürümü: 4.1 · Son genel bakım: 2026-10-28

Skill **kuralları ve yöntemleri** saklar; **literatürü saklamaz**. Konu literatürü her istekte bağlayıcılarla canlı olarak taranır, bu yüzden eskimez. Burada yalnızca zamanla değişebilen kurallar izlenir.

## İzlenen öğeler

| Öğe | Dosya | Mevcut bilgi | Son doğrulama | Kontrol kaynağı | Kontrol sıklığı |
|---|---|---|---|---|---|
| CONSORT | raporlama-yonergeleri.md | 2025 sürümü, 30 madde | 2026-10-28 | equator-network.org, consort-spirit.org | 12 ay |
| SPIRIT | raporlama-yonergeleri.md | 2025 sürümü, 34 madde | 2026-10-28 | equator-network.org | 12 ay |
| PRISMA | raporlama-yonergeleri.md | 2020 | 2026-10-28 | prisma-statement.org | 12 ay |
| STROBE, COREQ, SRQR, TREND, CROSS, CHERRIES, STARD, TRIPOD+AI, SQUIRE, CHEERS | raporlama-yonergeleri.md | tabloda belirtilen sürümler | 2026-10-28 | equator-network.org | 12 ay |
| ICMJE önerileri (yapay zekâ beyanı dahil) | hakem.md, gonderim-oncesi-denetim.md | yapay zekâ kullanımının beyanı | 2026-10-28 | icmje.org | 12 ay |
| APA stil kuralları | istatistikci.md, dil-ve-uslup.md | APA 7 | 2026-10-28 | apastyle.apa.org | 12 ay |
| Atıf güncelliği normu | literatur-tarama.md | çoğunluk son 5 yıl | 2026-10-28 | hemşirelik dergisi yazım kuralları | 24 ay |
| Yöntem kaynakları künyeleri | yontem-kaynaklari.md | 57 künye; 15 doğrulandı, 1 bulunamadı, 41 doğrulanmadı | 2026-10-28 | PubMed / Crossref / yayıncı | her bakımda (doğrulanmamış olanlardan başla) |
| Bağlayıcı kataloğu | baglayici-katalogu.md | 10 kategori | 2026-10-28 | tool_search, search_mcp_registry | her bakımda |
| Python paketleri | scripts/*.py | pingouin 0.7, sklearn 1.8, LightGBM 4.7, SHAP 0.54, semopy 2.3 ile test edildi; factor_analyzer çalışmıyor | 2026-10-28 | betik testi (sentetik veri) | her bakımda |
| İleri yöntem standartları | ileri-yontemler.md | ağ analizi raporlama, TRIPOD+AI, LPA ölçütleri, meta-analiz (REML+HKSJ) | 2026-10-28 | ilgili yöntem makaleleri, EQUATOR | 12 ay |

## Görev sırasında hafif kontrol
Bir görevde yukarıdaki öğelerden biri kullanılıyorsa ve son doğrulama tarihi kontrol sıklığını aşmışsa tek bir web_search ile güncel sürümü kontrol et. Değişiklik varsa görevi güncel bilgiyle yap ve yanıtın sonunda tek cümleyle bildir: "CONSORT'un yeni bir sürümü çıkmış; skill'i güncellemek için 'skill'i güncelle' diyebilirsiniz." Değişiklik yoksa hiçbir şey söyleme.

## Bakım modu ("skill'i güncelle", "skill bakımı")
1. Skill dosyalarını `/mnt/skills/user/akademik-makale-asistani` (veya yüklü konum) yerinden `/tmp/akademik-makale-asistani` altına kopyala; yüklü konum salt okunurdur.
2. Tablodaki her öğeyi kontrol kaynağından doğrula (web_search/web_fetch). Yalnızca birincil kaynağa (yönergenin resmi yayını, kuruluş sitesi) dayanarak değişiklik yap.
3. `tool_search` ile bağlı tüm bağlayıcıları listele; katalogda olmayan ve makale işine yarayan yenileri `baglayici-katalogu.md` tablosuna ekle. Kullanıcının istediği yeni bağlayıcıları da ekle.
4. `python3 scripts/duman_testi.py` çalıştır; başarısız modül varsa düzelt ve testi yeniden çalıştır.
4b. `yontem-kaynaklari.md` içindeki 'Doğrulanmadı' künyelerinden en fazla 15'ini PubMed/Crossref ile doğrula; künyede hata varsa düzelt, DOI ekle, Durum'u 'Doğrulandı: tarih' yap. Bulunamayanı 'Bulunamadı' diye işaretle, silme.
5. Tablodaki "Son doğrulama" tarihlerini ve sürüm numarasını güncelle (küçük düzeltme: 3.0 → 3.1; yönerge değişikliği: 3.x → 4.0).
6. Değişiklik özetini kullanıcıya göster (ne değişti, hangi kaynağa dayanarak), sonra skill'i paketle ve sun: kullanıcı "Save skill" ile kaydettiğinde güncelleme etkinleşir.
7. Kaynağı doğrulanamayan hiçbir değişikliği yapma; "belirsiz" olarak raporla.
