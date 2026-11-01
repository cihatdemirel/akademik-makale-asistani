# Bakım Notu — 2026-11-01 (sürüm 4.1 → 4.2)

## Ne değişti
- `yontem-kaynaklari.md`: "Doğrulanmadı" künyelerinden 15'i Crossref (api.crossref.org) ile tarandı; 14'ü doğrulandı (yazar, yıl, başlık, dergi eşleşti), 1'i bulunamadı. Künye metinlerinde düzeltme gerekmedi.
- `guncellik-kaydi.md`: sürüm 4.2, künye sayıları (29 doğrulandı, 2 bulunamadı, 26 doğrulanmadı), genel bakım tarihi ve Python paketi satırının tarihi güncellendi. `SKILL.md` başlığı v4.2 ile eşitlendi.
- `requirements.txt` değişmedi.

## Doğrulanan künyeler (Crossref, 2026-11-01)
| Anahtar | DOI |
|---|---|
| friedman2008 | 10.1093/biostatistics/kxm045 |
| hayes2015 | 10.1080/00273171.2014.962683 |
| henseler2015 | 10.1007/s11747-014-0403-8 (Crossref çevrimiçi yılı 2014; basılı 2015 — nota yazıldı) |
| higgins2002 | 10.1002/sim.1186 |
| hoenig2001 | 10.1198/000313001300339897 |
| hu1999 | 10.1080/10705519909540118 |
| intHout2014 | 10.1186/1471-2288-14-25 |
| kim2013 | 10.5395/rde.2013.38.1.52 |
| koenker1978 | 10.2307/1913643 |
| koo2016 | 10.1016/j.jcm.2016.02.012 |
| lakens2013 | 10.3389/fpsyg.2013.00863 |
| lakens2017 | 10.1177/1948550617697177 (Crossref kaydında başlık kısa: "Equivalence Tests"; yazar, dergi, yıl eşleşti) |
| liang1986 | 10.1093/biomet/73.1.13 |
| little1988 | 10.1080/01621459.1988.10478722 |

## Bulunamayan
- holm1979 (Scandinavian Journal of Statistics): Crossref araması yalnızca Holland & Copenhaver 1987 (Biometrics) kayıtlarını döndürdü; Holm 1979 için kayıt yok. `Bulunamadı` yazıldı, DOI uydurulmadı. JSTOR'dan elle doğrulanmalı.
- (Önceki bakımdan) foygel2010: Bulunamadı olarak kalıyor.

Kalan "Doğrulanmadı": 26 künye (çoğu kitap ve Crossref'te taranmamış makaleler; sonraki bakımda devam).

## Test
`python3 akademik-makale-asistani/scripts/duman_testi.py` → TÜMÜ GEÇTİ.

## Belirsiz kalanlar / yapılmayanlar
- Raporlama yönergeleri (CONSORT, SPIRIT, PRISMA vb.), ICMJE, APA, atıf güncelliği normu ve bağlayıcı kataloğu bu bakımda birincil kaynaktan yeniden kontrol edilmedi; kayıttaki tarihleri (2026-10-28) değiştirilmedi. Bu öğeler için değişiklik yapılmadı; kontrol sıklıkları (12–24 ay) henüz dolmadı.
- Paket sürümleri güncellenmedi (mevcut sürümlerle testler geçiyor; yeni sürüm kontrolü yapılmadı).
- Bağlayıcı kataloğu için `tool_search` bu ortamda yoktu; kontrol edilemedi.
