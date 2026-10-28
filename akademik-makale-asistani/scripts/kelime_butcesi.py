#!/usr/bin/env python3
"""Makale taslağındaki bölüm kelime sayılarını çıkarır ve hedef bütçeyle karşılaştırır.

Kullanım:
    python3 kelime_butcesi.py taslak.docx [--hedef 4500] [--dil tr|en]

--hedef : İngilizce ana metin hedefi (özet/kaynak/tablo hariç). Varsayılan 4500.
--dil   : Taslağın dili. Belirtilmezse otomatik tahmin edilir.
Türkçe taslakta İngilizce karşılık 1,20–1,35 katsayısıyla tahmin edilir (yaklaşık).
"""
import argparse
import re
import sys
from pathlib import Path

BOLUMLER = {
    "Özet": ["abstract", "özet", "oz", "summary"],
    "Giriş": ["introduction", "background", "giriş", "giris", "arka plan"],
    "Yöntem": ["methods", "method", "materials and methods", "methodology",
               "yöntem", "yontem", "gereç ve yöntem", "gereç ve yöntemler", "yöntemler"],
    "Bulgular": ["results", "findings", "bulgular"],
    "Tartışma": ["discussion", "tartışma", "tartisma"],
    "Sonuç": ["conclusion", "conclusions", "sonuç", "sonuc", "sonuçlar",
              "sonuç ve öneriler", "implications for practice",
              "implications for nursing practice", "relevance to clinical practice"],
    "Kaynaklar": ["references", "kaynaklar", "kaynakça", "bibliography"],
}
ORANLAR = {  # ana metin payı (alt, üst)
    "Giriş": (0.12, 0.18),
    "Yöntem": (0.25, 0.30),
    "Bulgular": (0.20, 0.25),
    "Tartışma": (0.28, 0.32),
    "Sonuç": (0.04, 0.06),
}
TR_EN = (1.20, 1.35)


def satirlari_oku(yol: Path):
    if yol.suffix.lower() == ".docx":
        try:
            import docx
        except ImportError:
            sys.exit("python-docx gerekli: pip install python-docx --break-system-packages")
        d = docx.Document(str(yol))
        satirlar = []
        for p in d.paragraphs:
            stil = (p.style.name or "").lower() if p.style is not None else ""
            satirlar.append((p.text.strip(), "heading" in stil or "başlık" in stil))
        return satirlar
    metin = yol.read_text(encoding="utf-8", errors="ignore")
    return [(s.strip().lstrip("#").strip(), s.strip().startswith("#")) for s in metin.splitlines()]


def bolum_bul(metin: str):
    temiz = re.sub(r"^[\d\.\s]+", "", metin).strip().rstrip(":").lower()
    if len(temiz) > 45:
        return None
    for ad, anahtarlar in BOLUMLER.items():
        if temiz in anahtarlar:
            return ad
    return None


def kelime(metin: str) -> int:
    return len(re.findall(r"[^\s]+", metin))


def dil_tahmin(metin: str) -> str:
    tr = len(re.findall(r"[çğışöüÇĞİŞÖÜ]", metin))
    return "tr" if tr / max(len(metin), 1) > 0.01 else "en"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dosya")
    ap.add_argument("--hedef", type=int, default=4500)
    ap.add_argument("--dil", choices=["tr", "en"])
    a = ap.parse_args()

    satirlar = satirlari_oku(Path(a.dosya))
    sayim, aktif, tum = {}, None, []
    for metin, baslik_stili in satirlar:
        if not metin:
            continue
        b = bolum_bul(metin)
        if b and (baslik_stili or len(metin) < 45):
            aktif = b
            sayim.setdefault(b, 0)
            continue
        tum.append(metin)
        if aktif:
            sayim[aktif] = sayim.get(aktif, 0) + kelime(metin)

    dil = a.dil or dil_tahmin(" ".join(tum))
    ana = sum(v for k, v in sayim.items() if k in ORANLAR)
    if not sayim:
        print("Bölüm başlığı bulunamadı. Başlıkları 'Introduction/Giriş' gibi ayrı satırlara yazın.")
        print(f"Toplam kelime: {kelime(' '.join(tum))}")
        return

    print(f"Dil: {'Türkçe' if dil == 'tr' else 'İngilizce'} | İngilizce ana metin hedefi: {a.hedef}")
    if dil == "tr":
        print(f"Türkçe ana metin hedefi ≈ {round(a.hedef / TR_EN[1])}–{round(a.hedef / TR_EN[0])} kelime (tahmini)")
    print()
    bas = f"{'Bölüm':<10}{'Kelime':>8}{'Pay':>7}   {'Hedef (EN)':<14}"
    if dil == "tr":
        bas += f"{'Tahmini EN':<14}"
    print(bas + "Durum")
    print("-" * len(bas + "Durum"))
    for ad in BOLUMLER:
        if ad not in sayim:
            continue
        n = sayim[ad]
        satir = f"{ad:<10}{n:>8}"
        if ad in ORANLAR:
            alt, ust = ORANLAR[ad]
            h_alt, h_ust = round(a.hedef * alt), round(a.hedef * ust)
            pay = n / ana if ana else 0
            satir += f"{pay:>7.0%}   {f'{h_alt}–{h_ust}':<14}"
            if dil == "tr":
                e_alt, e_ust = round(n * TR_EN[0]), round(n * TR_EN[1])
                satir += f"{f'{e_alt}–{e_ust}':<14}"
                ref = (e_alt + e_ust) / 2
            else:
                ref = n
            durum = "uygun" if h_alt * 0.9 <= ref <= h_ust * 1.1 else ("kısa" if ref < h_alt else "uzun")
            satir += durum
        else:
            satir += f"{'':>7}   {'250 (özet)' if ad == 'Özet' else '—':<14}"
            if dil == "tr":
                satir += f"{'':<14}"
        print(satir)
    print("-" * len(bas + "Durum"))
    toplam = f"Ana metin toplamı: {ana}"
    if dil == "tr":
        toplam += f" (≈ {round(ana * TR_EN[0])}–{round(ana * TR_EN[1])} İngilizce kelime, tahmini)"
    print(toplam)
    eksik = [b for b in ORANLAR if b not in sayim]
    if eksik:
        print("Bulunamayan bölümler: " + ", ".join(eksik))


if __name__ == "__main__":
    main()
