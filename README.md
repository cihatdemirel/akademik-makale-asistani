# Akademik Makale Asistanı · Academic Manuscript Assistant

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Testler](https://github.com/cihatdemirel/akademik-makale-asistani/actions/workflows/test.yml/badge.svg)](https://github.com/cihatdemirel/akademik-makale-asistani/actions/workflows/test.yml)

**TR** · Sağlık bilimleri ve hemşirelik araştırmacıları için, makalenin her aşamasında çalışan bir Claude skill'i. Soruya göre literatür tarayıcı, istatistikçi, yazar, dil editörü ya da hakem rolüne geçer. Kaynakları bir araçla doğrulamadan yazmaz; analiz kararlarını yayımlanmış yöntem kaynaklarına dayandırır.

**EN** · A Claude skill for health sciences and nursing researchers that supports every stage of a manuscript. It switches roles as needed: literature searcher, statistician, author, language editor or peer reviewer. It never writes a reference it has not verified with a tool, and it grounds every analytic decision in published methodological sources.

---

## Ne yapar? · What it does

| Rol · Role | Örnek · Example |
|---|---|
| Literatür · Literature | PubMed, Scite, Consensus, Elicit ile kaynak bulma ve künye/DOI doğrulama · finding and verifying sources |
| İstatistik · Statistics | Kural tabanlı yöntem seçimi, SPSS/Excel verisinin analizi, aracılık/düzenleyicilik, karma modeller, meta-analiz, makine öğrenmesi, ağ analizi · rule-based method selection and analysis |
| Denetim · Checks | p değerlerinin yeniden hesaplanması (statcheck mantığı), GRIM, kaynakça güncelliği · statistical and reference consistency checks |
| Yazım · Writing | Bölüm planı, kelime bütçesi, doğal akademik dil · section planning and natural academic prose |
| Hakem · Review | Gönderim öncesi denetim, hakem raporu, hakemlere yanıt · pre-submission audit, review reports, rebuttal letters |
| Yönergeler · Guidelines | CONSORT 2025, SPIRIT 2025, STROBE, PRISMA 2020, COREQ, TRIPOD+AI |
Akademik çalışmalar için önerilen diğer skill koleksiyonları: [ONERILEN-SKILLER.md](ONERILEN-SKILLER.md)
## Kurulum · Installation

1. [Releases](https://github.com/cihatdemirel/akademik-makale-asistani/releases) bölümünden en yeni `akademik-makale-asistani.skill` dosyasını indirin · Download the latest `.skill` file from Releases.
2. Claude'da skill yükleme bölümünden yükleyin · Upload it in Claude's skills section.
3. Bir makale isteğiyle kullanmaya başlayın · Start with any manuscript-related request, e.g. *"Bu veri için hangi analiz uygun?"*

## Güncel kalma · Staying current

Her ayın 1'inde Claude Code, raporlama yönergelerini ve yöntem künyelerini birincil kaynaklardan kontrol eder, testleri çalıştırır ve değişiklikleri bir pull request olarak sunar. Hiçbir değişiklik bakımcının onayı olmadan yayımlanmaz. Ayrıntılar: `CLAUDE.md`.

On the 1st of every month, Claude Code checks reporting guidelines and method references against primary sources, runs the test suite and proposes changes as a pull request. Nothing is released without maintainer approval.

## Önemli uyarı · Disclaimer

Bu araç istatistik danışmanlığının, etik kurul değerlendirmesinin ve yazarın sorumluluğunun yerini tutmaz. Tüm analizler, kaynaklar ve metinler yazar tarafından kontrol edilmelidir. Dergi politikası gerektiriyorsa yapay zekâ kullanımı beyan edilmelidir.

This tool does not replace statistical consultation, ethics review or author responsibility. All analyses, references and text must be checked by the author. Disclose AI use where journal policy requires it.

## Atıf · Citation

Bu aracı kullandıysanız lütfen sağdaki **"Cite this repository"** düğmesindeki künyeyle atıf yapın · If you use this tool, please cite it via **"Cite this repository"**.

## Lisans · License

Kod (`scripts/`): [MIT](LICENSE) · Rehber metinleri (`references/`, `SKILL.md`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
