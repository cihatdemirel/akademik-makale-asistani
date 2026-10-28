# Bağlayıcı Kataloğu (işleve göre)

Bu katalog bağlayıcıları **adıyla değil işleviyle** tanımlar. Böylece ileride eklenen bir bağlayıcı, adı burada geçmese bile doğru işe atanır.

## Keşif yöntemi (her oturumda)
1. Görevin gerektirdiği işlev kategorisini aşağıdaki tablodan belirle.
2. `tool_search` ile o kategorinin anahtar kelimelerini ara (örn. "literature search", "citation", "clinical trials"). Dönen her aracın açıklamasını oku; kategoriye uyuyorsa kullan.
3. Aynı kategoride birden çok araç varsa tabloda verilen öncelik sırasını izle; tabloda olmayan yeni bir araç bulunduysa açıklamasına göre sıraya yerleştir ve kullanıcıya bir cümleyle bildir ("Yeni bağlı X aracını da kullandım").
4. Kategori için hiç araç yoksa ve görev kullanıcının kendi verisini gerektiriyorsa `search_mcp_registry` ile dizini ara; uygun sonuç varsa `suggest_connectors` ile öner. Yalnızca dış bilgi gerekiyorsa web_search ile devam et.
5. Kullanıcı yeni bir bağlayıcının sürekli kullanılmasını isterse bu tabloya bir satır ekle (Bakım modu, `guncellik-kaydi.md`).

## Kategoriler

| Kategori | Ne için | Arama anahtar kelimeleri | Bilinen araçlar (öncelik sırasıyla) |
|---|---|---|---|
| Biyomedikal literatür | Makale bulma, MeSH, metadata, PMC tam metni | pubmed, literature, articles, biomedical | PubMed → Elicit → Wiley Scholar Gateway |
| Kanıt sentezi | Bir iddia için kanıtın yönü ve gücü | consensus, evidence, claims | Consensus → Scite |
| Atıf bağlamı ve güvenilirlik | Destekleyen/çürüten atıflar, geri çekilme, atıf ağı, kaynakça | citation, scite, retraction, bibliography | Scite |
| Klinik çalışma kayıtları | Kayıtlı/devam eden RKÇ, sonuç değişkenleri, sponsor | clinical trials, NCT, registry | Clinical Trials → Elicit (trials) |
| Sistematik tarama/rapor | Geniş tarama, tarama raporu, sistematik derleme iş akışı | systematic review, report, research agent | Elicit (kullanıcı onayıyla; kota ve zaman harcar) |
| Türkçe tezler ve ulusal literatür | YÖK Tez Merkezi, Türkçe ölçek uyarlamaları, ulusal veri | tez, yök, thesis, turkish | yöktez tarama (bağlıysa); yoksa web_search (DergiPark, TR Dizin) |
| Kullanıcının dosyaları | Taslak, veri seti, hakem yorumları | drive, onedrive, sharepoint, documents | Google Drive, Microsoft 365 |
| Şekil ve görsel | Kavramsal model, akış diyagramı, bilimsel çizim | figure, diagram, illustration | BioRender (bağlıysa); yoksa Visualizer/SVG |
| Takvim ve iletişim | Gönderim tarihleri, ortak yazarlarla yazışma | calendar, email | Google Calendar, Gmail (yalnızca kullanıcı isterse) |
| Eğitim/ürün bilgisi | Claude özellikleri ve iş akışları | academy, docs | Claude Academy |

## Kurallar
- Kullanıcının e-posta, takvim ve dosya araçlarına yalnızca görev gerçekten gerektiriyorsa ve kullanıcının isteğiyle eriş.
- Hakemliği yapılan gizli bir makaleyi dış araçlara (tarama raporu, paylaşım) gönderme.
- Bir aracın sonucunu kaynakçaya koymadan önce `literatur-tarama.md` §3 doğrulamasını uygula; araç ne olursa olsun.
