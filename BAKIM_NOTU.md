# Bakım Notu — 2026-10-28 (sürüm 4.0 → 4.1)

## Ne değişti
- `yontem-kaynaklari.md`: "Doğrulanmadı" künyelerinden 15'i Crossref (api.crossref.org) ile tarandı; 14'ü doğrulandı (yazar, yıl, başlık, dergi eşleşti), 1'i bulunamadı. Künye metinlerinde düzeltme gerekmedi.
- `guncellik-kaydi.md`: sürüm 4.1, künye sayıları güncellendi. `SKILL.md` başlığı v4.1 ile eşitlendi.
- `requirements.txt` değişmedi.

## Doğrulanan künyeler (Crossref, 2026-10-28)
| Anahtar | DOI |
|---|---|
| austin2011 | 10.1080/00273171.2011.568786 |
| bauer2005 | 10.1207/s15327906mbr4003_5 |
| bland1986 | 10.1016/s0140-6736(86)90837-8 |
| bossuyt2015 | 10.1136/bmj.h5527 |
| burger2023 | 10.1037/met0000471 |
| christodoulou2019 | 10.1016/j.jclinepi.2019.02.004 |
| collins2024 | 10.1136/bmj-2023-078378 |
| cox1972 | 10.1111/j.2517-6161.1972.tb00899.x |
| delacre2017 | 10.5334/irsp.82 |
| delacre2019 | 10.5334/irsp.198 |
| delong1988 | 10.2307/2531595 |
| epskamp2018 | 10.3758/s13428-017-0862-1 (Crossref yılı 2017 çevrimiçi; basılı 2018 — nota yazıldı) |
| faul2007 | 10.3758/bf03193146 |
| fornell1981 | 10.2307/3151312 |

## Bulunamayan
- foygel2010 (NeurIPS 2010): Crossref'te kayıt yok; `Bulunamadı` yazıldı, DOI uydurulmadı. Proceedings sayfasından elle doğrulanmalı.

Kalan "Doğrulanmadı": 41 künye (sonraki bakımda devam).

## Test
`python3 akademik-makale-asistani/scripts/duman_testi.py` → TÜMÜ GEÇTİ (7 modül).

## Belirsiz kalanlar / yapılmayanlar
- Raporlama yönergeleri (CONSORT, SPIRIT, PRISMA vb.), ICMJE, APA ve bağlayıcı kataloğu bu bakımda birincil kaynaktan yeniden kontrol edilmedi; kayıttaki tarihler (2026-10-28) önceki kontrolden geliyor ve değiştirilmedi. Bu öğeler için değişiklik yapılmadı.
- Paket sürümleri güncellenmedi (mevcut sürümlerle testler geçiyor; yeni sürüm kontrolü yapılmadı).
- Crossref kısa süreli 429 (hız sınırı) verdi; sorgular bekleyerek tekrarlandı.
