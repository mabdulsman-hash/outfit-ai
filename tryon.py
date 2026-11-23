"""
tryon.py - Gambar pakaian sungguhan untuk outfit-ai.

Struktur folder (nama file = nama item di Excel, huruf kecil, spasi jadi "-"):
  assets/atasan/polo-shirt.png
  assets/bawahan/jeans-straight.png
  assets/alas-kaki/sepatu-kets-ringan.png

Aturan pemilihan gambar:
  1) Kalau ada file persis per warna, mis. polo-shirt-olive.png -> dipakai apa adanya.
  2) Kalau tidak, dipakai polo-shirt.png lalu DIWARNAI otomatis sesuai warna rekomendasi
     (bayangan dan lipatan kain dari foto asli tetap terlihat).
     Untuk ini, pakai foto pakaian yang warnanya putih/abu terang atau netral.

Jalankan `python daftar_gambar.py` untuk melihat daftar file yang dibutuhkan.
"""
import os
import re

import cv2
import numpy as np

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_cache = {}


def slug(teks):
    return re.sub(r"[^a-z0-9]+", "-", str(teks).lower()).strip("-")


def hex_ke_bgr(hex_):
    h = hex_.lstrip("#")
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], dtype=np.float32)


def _baca_bgra(path):
    if not os.path.exists(path):
        return None
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 3:
        img = np.concatenate([img, np.full(img.shape[:2] + (1,), 255, np.uint8)], axis=2)
    return img


def _warnai(bgra, hex_):
    """Ganti warna dasar pakaian ke hex_, pertahankan shading dari foto asli."""
    bgr = bgra[:, :, :3].astype(np.float32)
    alpha = bgra[:, :, 3]
    gray = cv2.cvtColor(bgra[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    pix = gray[alpha > 128]
    acuan = max(float(np.median(pix)) if pix.size else 200.0, 1.0)
    shade = np.clip(gray / acuan, 0.0, 1.6)[:, :, None]
    out = np.clip(hex_ke_bgr(hex_)[None, None, :] * shade, 0, 255)
    return np.concatenate([out.astype(np.uint8), alpha[:, :, None]], axis=2)


def muat_item(kategori, item, hex_=None, warna_nama=""):
    """Return gambar BGRA atau None kalau file belum ada."""
    if not item:
        return None
    key = (kategori, item, hex_, warna_nama)
    if key in _cache:
        return _cache[key]
    folder = os.path.join(ASSET_DIR, slug(kategori))
    hasil = None
    if warna_nama:
        persis = _baca_bgra(os.path.join(folder, f"{slug(item)}-{slug(warna_nama)}.png"))
        if persis is not None:
            hasil = persis
    if hasil is None:
        dasar = _baca_bgra(os.path.join(folder, f"{slug(item)}.png"))
        if dasar is not None:
            hasil = _warnai(dasar, hex_) if hex_ else dasar
    _cache[key] = hasil
    return hasil


def spec_dari_look(look):
    """Ubah satu look dari engine.rekomendasi() menjadi spesifikasi gambar."""
    gaun = "dress" in look["atasan"].lower()
    return {
        "atasan": (look["atasan"], look["hex_atasan"], look["warna_atasan"]),
        "bawahan": None if gaun else (look["bawahan"], look["hex_bawahan"], look["warna_bawahan"]),
        "alas-kaki": (look["alas_kaki"], look["hex_sepatu"], look["warna_sepatu"]),
    }


def gambar_spec(spec):
    """Muat semua gambar untuk spec. Return (dict gambar, daftar file yang belum ada)."""
    gambar, hilang = {}, []
    for kat, v in spec.items():
        if v is None:
            continue
        img = muat_item(kat, *v)
        if img is None:
            hilang.append(f"assets/{kat}/{slug(v[0])}.png")
        else:
            gambar[kat] = img
    return gambar, hilang


def komposisi_flatlay(spec, lebar=420):
    """Susun atasan, bawahan, sepatu secara vertikal di latar putih. Return bytes PNG,
    atau None kalau ada gambar yang belum tersedia."""
    gambar, hilang = gambar_spec(spec)
    if hilang:
        return None
    urutan = [("atasan", 0.80), ("bawahan", 0.60), ("alas-kaki", 0.50)]
    potongan = []
    for kat, skala in urutan:
        img = gambar.get(kat)
        if img is None:
            continue
        w = int(lebar * skala)
        h = max(int(img.shape[0] * w / img.shape[1]), 1)
        potongan.append(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    jarak = 14
    tinggi = sum(p.shape[0] for p in potongan) + jarak * (len(potongan) + 1)
    kanvas = np.full((tinggi, lebar, 3), 246, np.uint8)
    y = jarak
    for p in potongan:
        x = (lebar - p.shape[1]) // 2
        a = p[:, :, 3:4].astype(np.float32) / 255.0
        roi = kanvas[y:y + p.shape[0], x:x + p.shape[1]].astype(np.float32)
        kanvas[y:y + p.shape[0], x:x + p.shape[1]] = (a * p[:, :, :3] + (1 - a) * roi).astype(np.uint8)
        y += p.shape[0] + jarak
    ok, buf = cv2.imencode(".png", kanvas)
    return buf.tobytes() if ok else None
