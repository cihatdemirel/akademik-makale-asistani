#!/usr/bin/env python3
"""Akademik metinde mekanik / yapay zekâ benzeri üslup işaretlerini listeler.

Kullanım:
    python3 stil_denetimi.py metin.txt|metin.docx|-  [--dil tr|en]

Betik karar vermez; düzenlemede dikkat edilecek yerleri gösterir.
"""
import argparse
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

EN_KALIP = [
    "delve", "intricate", "multifaceted", "nuanced", "tapestry", "realm", "landscape",
    "pivotal", "crucial", "paramount", "vital role", "plays a key role", "plays a crucial role",
    "plays a pivotal role", "underscore", "underscores", "highlighting", "shed light", "sheds light",
    "pave the way", "paves the way", "is a testament", "it is worth noting", "it is important to note",
    "notably", "foster", "fostering", "leverage", "navigate", "navigating", "comprehensive understanding",
    "in today's", "ever-evolving", "rapidly evolving", "not only", "a myriad", "plethora",
    "studies have shown", "it is widely", "seamless", "holistic approach", "groundbreaking",
    "in conclusion", "furthermore", "moreover", "additionally",
]
TR_KALIP = [
    "önemli bir rol oynamaktadır", "önemli rol oynamaktadır", "büyük önem taşımaktadır",
    "büyük önem arz etmektedir", "kritik öneme sahiptir", "kritik bir öneme sahiptir",
    "dikkat çekmektedir", "ışık tutmaktadır", "ışık tutacaktır", "bu bağlamda", "bu doğrultuda",
    "söz konusu", "nitekim", "öte yandan", "bunun yanı sıra", "ayrıca", "sonuç olarak",
    "literatürde", "görülmektedir", "bilinmektedir", "düşünülmektedir", "olarak ifade edilmektedir",
    "yapılmaktadır", "sağlanmaktadır", "katkı sunmaktadır", "çok boyutlu", "bütüncül",
]
BAGLAC_EN = ("furthermore", "moreover", "additionally", "in addition", "however", "therefore",
             "consequently", "notably", "importantly", "overall")
BAGLAC_TR = ("ayrıca", "bunun yanı sıra", "öte yandan", "bu bağlamda", "bu doğrultuda",
             "dolayısıyla", "nitekim", "buna ek olarak", "sonuç olarak", "bununla birlikte")


def oku(yol):
    if yol == "-":
        return sys.stdin.read()
    p = Path(yol)
    if p.suffix.lower() == ".docx":
        import docx
        return "\n".join(par.text for par in docx.Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")


def cumleler(metin):
    metin = re.sub(r"\s+", " ", metin)
    parcalar = re.split(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ(])", metin)
    return [c.strip() for c in parcalar if len(c.split()) >= 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dosya")
    ap.add_argument("--dil", choices=["tr", "en"])
    a = ap.parse_args()
    metin = oku(a.dosya)
    dil = a.dil or ("tr" if len(re.findall(r"[çğışöüÇĞİŞÖÜ]", metin)) / max(len(metin), 1) > 0.01 else "en")
    kucuk = metin.lower()
    cs = cumleler(metin)
    uz = [len(c.split()) for c in cs]

    print(f"Dil: {dil} | Cümle: {len(cs)} | Kelime: {len(metin.split())}")
    if uz:
        sd = statistics.pstdev(uz)
        print(f"Cümle uzunluğu: ort {statistics.mean(uz):.1f}, SS {sd:.1f}, en uzun {max(uz)}")
        if sd < 5 and len(uz) >= 6:
            print("  ! Cümle uzunlukları çok benzer (tekdüze ritim).")
        uzun = [c for c in cs if len(c.split()) > 35]
        if uzun:
            print(f"  ! 35 kelimeyi aşan {len(uzun)} cümle var; ilk: \"{uzun[0][:90]}…\"")

    kaliplar = TR_KALIP if dil == "tr" else EN_KALIP
    bulunan = Counter()
    for k in kaliplar:
        n = len(re.findall(r"(?<!\w)" + re.escape(k) + r"(?!\w)", kucuk))
        if n:
            bulunan[k] = n
    if bulunan:
        print("\nSık görülen kalıplar:")
        for k, n in bulunan.most_common():
            print(f"  {k}: {n}")

    baglac = BAGLAC_TR if dil == "tr" else BAGLAC_EN
    acilis = [next((b for b in baglac if c.lower().startswith(b)), None) for c in cs]
    ard = sum(1 for i in range(1, len(acilis)) if acilis[i] and acilis[i - 1])
    oran = sum(1 for x in acilis if x) / max(len(cs), 1)
    print(f"\nBağlaçla başlayan cümle oranı: %{oran * 100:.0f} | ardışık bağlaç açılışı: {ard}")
    if oran > 0.25 or ard:
        print("  ! Geçişler bağlaca fazla yaslanıyor.")

    if dil == "tr":
        sonlar = [re.sub(r"[.!?]+$", "", c).split()[-1].lower() for c in cs if c.split()]
        mek = sum(1 for s in sonlar if re.search(r"(mekte|makta)d[ıi]r$", s))
        print(f"'-mektedir/-maktadır' ile biten cümle: {mek}/{len(sonlar)} (%{mek / max(len(sonlar), 1) * 100:.0f})")
        seri = max((len(list(g)) for k, g in __import__("itertools").groupby(
            [bool(re.search(r"(mekte|makta)d[ıi]r$", s)) for s in sonlar]) if k), default=0)
        if seri >= 3:
            print(f"  ! Arka arkaya {seri} cümle aynı ekle bitiyor.")
    else:
        ing = len(re.findall(r",\s+\w+ing\b[^.]*\.", metin))
        print(f"Cümle sonuna eklenmiş -ing yan cümlesi: {ing}")

    tire = metin.count("—") + metin.count(" – ")
    print(f"Uzun tire: {tire}")
    print("\nNot: Bu liste karar vermez; bağlama göre değerlendirilir. Terim tutarlılığı her zaman önceliklidir.")


if __name__ == "__main__":
    main()
