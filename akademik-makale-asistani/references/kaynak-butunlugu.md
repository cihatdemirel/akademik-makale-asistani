# Kaynak Bütünlüğü Protokolü

Uydurma veya hatalı kaynak, bir makale için en ağır hatadır. Bu protokol her rolde geçerlidir ve diğer tüm talimatlardan önce gelir.

## 1. Kesin kurallar
1. Kaynakçaya ya da metne giren her kaynak, **bu oturumda bir araçla** (PubMed, Scite, Consensus, Elicit, Wiley, web_fetch ile yayıncı/DOI sayfası) görülmüş olmalıdır. Bellekten künye, DOI, PMID, cilt/sayfa yazılmaz.
2. Kaynağa atfedilen her iddia o kaynağın özetinde veya tam metninde bulunmalıdır. Yalnızca başlığa bakılarak iddia atfedilmez.
3. Doğrulanamayan yere `[KAYNAK GEREKLİ: konu]` konur ve kullanıcıya açıkça söylenir. Boşluğu doldurmak için benzer bir kaynak "uydurulmaz" veya "yaklaşık" künye yazılmaz.
4. İkincil atıf yapılmaz (derlemede anılan çalışma, birincil kaynak görülmeden atıflanmaz).
5. Geri çekilmiş makale kullanılmaz; düzeltme (erratum) varsa belirtilir.
6. Kullanıcının verdiği kaynaklar da doğrulanır; hata bulunursa düzeltme önerilir, sessizce değiştirilmez.
7. `yontem-kaynaklari.md` künyeleri taslaktır; kullanılmadan önce bu protokolle doğrulanır.

## 2. Doğrulama adımları (kaynak başına)
1. **Varlık:** DOI veya PMID ile kayıt bulunur (PubMed `get_article_metadata`, `lookup_article_by_citation`; Scite; ya da web_fetch ile doi.org/yayıncı sayfası).
2. **Künye eşleşmesi:** yazarlar (ilk yazar ve sayı), yıl, başlık, dergi, cilt/sayı/sayfa veya makale numarası, DOI.
3. **İçerik:** atfedilen bulgu/sayı özette veya tam metinde var mı; yön ve büyüklük doğru mu; desen doğru aktarılmış mı (kesitsel bulgu "etki" diye aktarılmamış mı).
4. **Durum:** geri çekilme/düzeltme (Scite veya web araması), yağmacı dergi şüphesi.
5. **Etiket:** Doğrulandı / Kısmen (yalnızca özetten; künye eksik) / Doğrulanamadı / Sorunlu (geri çekilmiş, uyumsuz iddia).

## 3. Çıktı biçimi
Kaynak üretilen veya denetlenen her yanıtta, metnin altına kısa bir tablo:

| # | Kaynak (Yazar, Yıl) | DOI/PMID | Doğrulama | İddia uyumu |
|---|---|---|---|---|

Tüm kaynaklar "Doğrulandı" ise tek satırlık not yeterlidir ("12 kaynak PubMed ile doğrulandı"). Token tasarrufu için tabloyu yalnızca sorun varsa ya da kullanıcı isterse ayrıntılı ver.

## 4. Kaynakça denetimi (kullanıcı listesi)
1. `python3 scripts/kaynak_denetimi.py kaynakca.txt --metin makale.docx --csv dogrulama.csv` → güncellik, yinelenen, DOI eksikliği, metin–liste eşleşmesi.
2. DOI'si olmayan ve şüpheli kaynakları önceliklendirerek §2'yi uygula (önce eksik/şüpheli olanlar; hepsini tek tek açmak gerekmiyorsa toplu PubMed araması).
3. Sonucu §3 tablosuyla ver.

## 5. Atıf yerleştirme kuralları
- Bir cümle birden çok iddia içeriyorsa atıf ilgili iddianın hemen yanına konur.
- "Studies have shown" gibi atıfsız genellemeler yazılmaz; ya atıf ya silme.
- Sayı veren cümlede (prevalans, etki büyüklüğü) kaynak zorunludur.
- Kendi kendine atıf yalnızca gerçekten ilgiliyse; oranı %10–15'i aşmasın.
- Hedef dergiden atıf zorlanmaz.
