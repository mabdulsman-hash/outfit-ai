"""Menampilkan daftar file PNG yang dibutuhkan (dan mana yang belum ada).
Jalankan:  python daftar_gambar.py
Opsi:      python daftar_gambar.py --buat-folder   (membuat folder assets/ kosong)"""
import os
import sys

import pandas as pd

from tryon import ASSET_DIR, slug

item = pd.read_excel("pengetahuan_outfit.xlsx", sheet_name="Item")
kategori = ["Atasan", "Bawahan", "Alas kaki"]

if "--buat-folder" in sys.argv:
    for k in kategori:
        os.makedirs(os.path.join(ASSET_DIR, slug(k)), exist_ok=True)

total = ada = 0
for k in kategori:
    print(f"\n== {k} -> assets/{slug(k)}/")
    for nama in sorted(item[item.Kategori == k].Item.unique()):
        berkas = f"{slug(nama)}.png"
        sudah = os.path.exists(os.path.join(ASSET_DIR, slug(k), berkas))
        total += 1
        ada += sudah
        print(f"  [{'x' if sudah else ' '}] {berkas}   <- {nama}")
print(f"\nSudah ada {ada} dari {total} gambar.")
