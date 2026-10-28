# Önerilen Skill'ler · Recommended Skills

Akademik çalışmada işe yarayabilecek, başkaları tarafından geliştirilmiş skill koleksiyonları. Bu depo onların **kopyasını barındırmaz**; yalnızca bağlantı verir. Böylece her koleksiyon kendi yazarı tarafından güncel tutulur ve lisans koşulları korunur.

Third-party skill collections that may be useful for academic work. This repository links to them and does not redistribute copies.

> **Güvenlik notu:** Skill'ler çalıştırılabilir kod içerebilir. Yalnızca güvendiğiniz kaynaklardan kurun ve kurmadan önce içeriğine göz atın.
> **Lisans notu:** Lisanslar listenin hazırlandığı tarihte (Ekim 2026) kontrol edildi. Kullanmadan önce ilgili deponun LICENSE dosyasına bakın; lisanslar değişebilir.

| Koleksiyon | Ne işe yarar | Lisans | Not |
|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic'in resmî skill deposu: skill yazmayı öğreten örnekler, `skill-creator` (yeni skill oluşturma), `template-skill` ve Agent Skills tanımı | Örnek skill'ler Apache 2.0; belge skill'leri (docx, pdf, pptx, xlsx) yalnızca kaynağı görülebilir, açık kaynak değil | Claude.ai'de belge skill'leri zaten yerleşik; kendi skill'inizi yazmak için başlangıç noktası |
| [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) | 140'ı aşkın bilimsel skill: literatür taraması, bilimsel bilgi tabanları, veri analizi ve görselleştirme kütüphaneleri | MIT | Ağırlık biyomedikal ve hesaplamalı bilimlerde; hemşirelik için literatür ve analiz skill'lerini seçerek kullanın |
| [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) | Genel amaçlı bilimsel yazım yardımcısı | MIT | Akademik Makale Asistanı'yla görev alanı örtüşür; ikisini aynı anda açık tutmayın |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | Araştırma → yazım → hakem değerlendirmesi → revizyon → son hâl akışı; sistematik derleme, Sokratik araştırma rehberliği, çok rollü hakem simülasyonu | CC BY-NC 4.0 (ticari olmayan kullanım) | Kapsamlı ama ağır; Claude Code eklentisi olarak tasarlanmış |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Topluluk skill'lerinin kategorilere ayrılmış derleme listesi | Liste deposu | Yeni skill keşfetmek için |

## Nasıl kurulur · Installation

- **Claude Code:** Her deponun README'sindeki `/plugin marketplace add ...` komutunu kullanın.
- **Claude.ai:** Depoyu ZIP olarak indirin (Code → Download ZIP), kullanmak istediğiniz skill klasörünü (içinde `SKILL.md` olan) ayrıca ZIP'leyin ve Claude'daki skill yükleme bölümünden yükleyin.

## Çakışma uyarısı · Overlap

Aynı işi yapan birden fazla skill açıkken (ör. iki farklı "makale yazım" skill'i) Claude hangisini kullanacağını tahmin etmek zorunda kalır ve sonuçlar tutarsızlaşabilir. Benzer görevler için tek bir skill'i açık tutun.

## Öneri · Suggest a collection

Listeye eklenmesini istediğiniz bir koleksiyon varsa bir Issue açın: depo bağlantısı, lisansı ve akademisyenler için neden yararlı olduğu.
