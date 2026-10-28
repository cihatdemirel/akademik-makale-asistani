# Akademik Makale Asistanı · otomatik bakımlı Claude skill'i

Her ayın 1'inde Claude Code bir GitHub sunucusunda çalışır. Yönergeleri ve yöntem künyelerini birincil kaynaklardan kontrol eder, testleri çalıştırır ve değişiklikleri **sizin onayınıza** bir PR olarak sunar. Onayladığınızda yeni `.skill` dosyası otomatik paketlenir.

## Kurulum (bir kez, ~20 dakika)

1. **Depo oluşturun.** GitHub → New repository → ad: `akademik-makale-asistani` → **Private** → Create.
2. **Dosyaları yükleyin.** Bu klasörün tüm içeriğini (gizli `.github` klasörü dahil) depoya yükleyin.
   - En kolayı GitHub Desktop: depoyu bilgisayara klonlayın, bu dosyaları içine kopyalayın, Commit → Push.
   - Komut satırıyla:
     ```bash
     cd akademik-makale-asistani-repo
     git init && git add . && git commit -m "ilk sürüm"
     git branch -M main
     git remote add origin https://github.com/KULLANICI_ADINIZ/akademik-makale-asistani.git
     git push -u origin main
     ```
   - Web arayüzünden sürükle-bırak yaparsanız `.github` klasörünün yüklendiğini kontrol edin (macOS gizli klasörleri göstermeyebilir).
3. **API anahtarı.** console.anthropic.com → API Keys → yeni anahtar. Depoda Settings → Secrets and variables → Actions → New repository secret → Name: `ANTHROPIC_API_KEY`, Secret: anahtarınız.
   - API kullanımı Claude aboneliğinizden **ayrı ücretlendirilir**. Console'da aylık harcama sınırı koymanızı öneririm.
4. **Claude GitHub uygulaması.** github.com/apps/claude → Install → yalnızca bu depoyu seçin.
5. **İş akışı izinleri.** Depoda Settings → Actions → General → Workflow permissions → "Read and write permissions" ve "Allow GitHub Actions to create and approve pull requests" kutusunu işaretleyin → Save.
6. **İlk deneme.** Actions sekmesi → "Aylık skill bakımı" → Run workflow. 10–40 dakika sürebilir.

## Her ay ne yapacaksınız (~5 dakika)

1. GitHub'dan "Aylık skill bakımı" PR bildirimi gelir.
2. PR açıklamasındaki bakım notunu okuyun: ne değişti, hangi kaynağa dayanarak.
3. "Files changed" sekmesinde değişikliklere göz atın. "Testler" kontrolü yeşil olmalı.
4. Uygunsa **Merge**. Uygun değilse PR'ı kapatın ya da yorum yazın.
5. Merge sonrası Releases bölümünde yeni sürüm oluşur → `akademik-makale-asistani.skill` dosyasını indirin → Claude'daki skill yükleme bölümünden yükleyin (aynı adlı skill güncellenir).

## Güvenlik ve sınırlar
- Ajan hiçbir değişikliği doğrudan ana dala yazmaz; her şey sizin onayınızla birleşir.
- `CLAUDE.md` ajanın kurallarını içerir: yalnızca birincil kaynak, uydurma DOI yok, test geçmeden bitirme yok.
- Claude.ai tarafına yükleme elle yapılır; GitHub ile Claude.ai arasında otomatik eşitleme yoktur.
- Maliyeti sınırlamak için `skill-bakim.yml` içindeki `--max-turns` değerini düşürebilir ya da `cron` satırını üç ayda bir (`0 6 1 */3 *`) yapabilirsiniz.
