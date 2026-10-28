#!/usr/bin/env python3
"""Kaynakça ve metin içi atıf denetimi (çevrimdışı). Kaynakları DOĞRULAMAZ; doğrulanacakları listeler.

Kontroller: yıl dağılımı ve güncellik (son 5/10 yıl), DOI/PMID varlığı, yinelenen kaynak,
APA (yazar–yıl) veya numaralı (Vancouver) metin içi atıf ↔ kaynakça eşleşmesi, kaynakça sırası.

Kullanım:
    python3 kaynak_denetimi.py kaynakca.txt [--metin makale.docx] [--yil 2026] [--csv dogrulama.csv]
Kaynakça dosyasında her kaynak ayrı satırda (veya numaralı) olmalıdır.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

YIL = re.compile(r"\((\d{4})[a-z]?\)|[\s.;,](\d{4})[a-z]?[;.,:)\s]")
DOI = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)
PMID = re.compile(r"PMID:?\s*(\d{5,9})", re.I)


def _oku(yol):
    p = Path(yol)
    if p.suffix.lower() == ".docx":
        import docx
        return "\n".join(x.text for x in docx.Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]", " ", s)


def kaynaklari_ayir(metin):
    satirlar = [s.strip() for s in metin.splitlines() if s.strip()]
    kaynaklar = []
    for s in satirlar:
        if re.match(r"^(\[\d+\]|\d+[.)])\s+", s) or not kaynaklar or re.match(r"^[A-ZÇĞİÖŞÜ][^\s,]+,?\s+[A-Z]", s):
            kaynaklar.append(re.sub(r"^(\[\d+\]|\d+[.)])\s+", "", s))
        else:
            kaynaklar[-1] += " " + s
    return kaynaklar


def ilk_yazar(k):
    m = re.match(r"\s*([A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü'’\-]+)", k)
    return m.group(1) if m else ""


def yil_bul(k):
    for m in YIL.finditer(k):
        y = int(m.group(1) or m.group(2))
        if 1900 <= y <= datetime.date.today().year + 1:
            return y
    return None


def denetle(kaynakca_metni, makale_metni=None, yil=None):
    yil = yil or datetime.date.today().year
    ks = kaynaklari_ayir(kaynakca_metni)
    rows = []
    for i, k in enumerate(ks, 1):
        y = yil_bul(k)
        doi = DOI.search(k)
        pm = PMID.search(k)
        rows.append({"No": i, "İlk yazar": ilk_yazar(k), "Yıl": y, "Yaş": (yil - y) if y else None,
                     "DOI": doi.group(0).rstrip(".") if doi else "", "PMID": pm.group(1) if pm else "",
                     "Kaynak": k[:110]})
    t = pd.DataFrame(rows)
    yinelenen = []
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            if SequenceMatcher(None, _norm(ks[i])[:160], _norm(ks[j])[:160]).ratio() > 0.85:
                yinelenen.append((i + 1, j + 1))
    yas = t["Yaş"].dropna()
    ozet = {"Kaynak sayısı": len(t), "Yılı bulunamayan": int(t["Yıl"].isna().sum()),
            "Son 5 yıl %": round((yas <= 5).mean() * 100, 1) if len(yas) else None,
            "Son 10 yıl %": round((yas <= 10).mean() * 100, 1) if len(yas) else None,
            "Medyan yaş": float(yas.median()) if len(yas) else None,
            "DOI/PMID yok": int(((t["DOI"] == "") & (t["PMID"] == "")).sum()),
            "Olası yinelenen": yinelenen}
    eslesme = {}
    if makale_metni:
        numarali = re.findall(r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]", makale_metni)
        if numarali:
            atif = set()
            for g in numarali:
                for parca in re.split(r"\s*,\s*", g):
                    if re.search(r"[-–]", parca):
                        a, b = map(int, re.split(r"\s*[-–]\s*", parca))
                        atif |= set(range(a, b + 1))
                    else:
                        atif.add(int(parca))
            eslesme = {"Biçim": "numaralı", "Metinde olup listede olmayan": sorted(x for x in atif if x > len(ks)),
                       "Listede olup metinde atıf yapılmayan": sorted(set(range(1, len(ks) + 1)) - atif)}
            sira = []
            for g in numarali:
                ilk = int(re.split(r"[^\d]", g.strip())[0])
                if ilk not in sira:
                    sira.append(ilk)
            beklenen = sorted(sira)
            eslesme["İlk geçiş sırası numara sırasıyla uyumlu"] = sira == beklenen
        else:
            apa = re.findall(r"([A-ZÇĞİÖŞÜ][A-Za-zçğıöşüÇĞİÖŞÜ'’\-]+)(?:\s+(?:et al\.|ve ark\.|and|&|ve)\s*(?:[A-ZÇĞİÖŞÜ][A-Za-zçğıöşü'’\-]+)?)?,?\s*\(?(\d{4})[a-z]?\)?",
                             makale_metni)
            metin_atif = {(_norm(a).strip(), int(y)) for a, y in apa if 1900 <= int(y) <= yil + 1}
            liste = {(_norm(r["İlk yazar"]).strip(), r["Yıl"]) for _, r in t.iterrows() if r["Yıl"]}
            yazarlar_liste = {a for a, _ in liste}
            eksik = sorted(f"{a} {y}" for a, y in metin_atif - liste if a in yazarlar_liste or len(a) > 3)
            eslesme = {"Biçim": "yazar–yıl",
                       "Metinde olup listede bulunamayan (kontrol et)": eksik[:40],
                       "Listede olup metinde bulunamayan (kontrol et)": sorted(f"{a} {y}" for a, y in liste - metin_atif)[:40]}
    return t, ozet, eslesme


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kaynakca")
    ap.add_argument("--metin")
    ap.add_argument("--yil", type=int)
    ap.add_argument("--csv")
    a = ap.parse_args()
    t, ozet, es = denetle(_oku(a.kaynakca), _oku(a.metin) if a.metin else None, a.yil)
    for k, v in ozet.items():
        print(f"{k}: {v}")
    if es:
        print()
        for k, v in es.items():
            print(f"{k}: {v}")
    eski = t[t["Yaş"] > 10]
    if len(eski):
        print("\n10 yıldan eski (gerekçelendirin: ölçek orijinali, Türkçe uyarlama, kuram, klasik):")
        print(eski[["No", "İlk yazar", "Yıl"]].to_string(index=False))
    if a.csv:
        t.assign(**{"Doğrulama durumu": "", "Doğrulama kaynağı": "", "İddia–kaynak uyumu": ""}).to_csv(a.csv, index=False)
        print(f"\nDoğrulama tablosu: {a.csv}")
