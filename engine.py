"""Mesin rekomendasi outfit: aturan pakar (Excel) + deteksi warna kulit dari foto
+ pembacaan teks (chat/suara)."""
import re
import numpy as np
import pandas as pd

KB_PATH = "pengetahuan_outfit.xlsx"
ACARA_KATA = {
    "Kuliah": ["kuliah", "kampus", "kelas"],
    "Kerja": ["kerja", "kantor", "interview", "wawancara", "meeting", "rapat"],
    "Kondangan": ["kondangan", "pesta", "nikah", "pernikahan", "resepsi", "wisuda"],
    "Santai": ["santai", "jalan", "nongkrong", "mall", "liburan", "main"],
    "Olahraga": ["olahraga", "gym", "lari", "futsal", "senam"],
    "Kencan": ["kencan", "date", "dinner", "makan malam"],
}
GAYA_KATA = {
    "Kasual": ["kasual", "casual", "simpel", "simple", "santai"],
    "Formal": ["formal", "rapi", "resmi"],
    "Sporty": ["sporty", "sporti", "olahraga"],
    "Streetwear": ["street", "streetwear", "oversize", "kekinian"],
    "Elegan": ["elegan", "elegant", "anggun", "classy"],
}


def load_kb(path=KB_PATH):
    return pd.read_excel(path, sheet_name=None)


def hitung_bmi(bb, tb):
    return bb / ((tb / 100) ** 2)


def tipe_tubuh(bb, tb):
    """Pengelompokan proporsi (dari BMI) untuk memilih potongan pakaian."""
    bmi = hitung_bmi(bb, tb)
    if bmi < 18.5:
        return "Ramping"
    if bmi < 25:
        return "Proporsional"
    if bmi < 30:
        return "Berisi"
    return "Besar"


def ekstrak_dari_teks(teks):
    """Membaca BB, TB, gender, acara, dan gaya dari kalimat bebas (chat / hasil suara)."""
    t = teks.lower()
    hasil = {}
    m = re.search(r"(?:bb|berat(?: badan)?)\D{0,6}(\d{2,3})", t)
    if m:
        hasil["bb"] = float(m.group(1))
    m = re.search(r"(?:tb|tinggi(?: badan)?)\D{0,6}(\d{2,3})", t)
    if m:
        hasil["tb"] = float(m.group(1))
    if re.search(r"\b(wanita|perempuan|cewek|cewe)\b", t):
        hasil["gender"] = "Wanita"
    elif re.search(r"\b(pria|laki|cowok|cowo)\b", t):
        hasil["gender"] = "Pria"
    for nama, kata in ACARA_KATA.items():
        if any(k in t for k in kata):
            hasil["acara"] = nama
            break
    for nama, kata in GAYA_KATA.items():
        if any(k in t for k in kata):
            hasil["gaya"] = nama
            break
    return hasil


def klasifikasi_kulit(roi_bgr):
    """Klasifikasi Terang/Sedang/Gelap dari potongan gambar wajah (BGR)."""
    import cv2
    ycrcb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2YCrCb)
    mask = cv2.inRange(ycrcb, (0, 133, 77), (255, 173, 127)) > 0
    lab = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2LAB)
    piksel = lab[mask] if mask.sum() > 50 else lab.reshape(-1, 3)
    L = float(np.median(piksel[:, 0])) / 255 * 100  # skala 0-100
    label = "Terang" if L >= 65 else "Sedang" if L >= 48 else "Gelap"
    return label, f"Kecerahan kulit (L*) ~ {L:.0f}"


def deteksi_warna_kulit(image_bytes):
    """Deteksi wajah (OpenCV Haar Cascade) lalu klasifikasi warna kulit dari piksel
    kulit di area tengah wajah. Return (label, info) atau (None, pesan)."""
    import cv2
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return None, "Gambar tidak bisa dibaca."
    if not hasattr(cv2, "CascadeClassifier"):
        return None, "OpenCV versi ini tidak punya detektor wajah. Pasang: pip install \"opencv-python<5\""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    wajah = cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
    if len(wajah) == 0:
        return None, "Wajah tidak terdeteksi. Coba foto lebih terang dan menghadap depan."
    x, y, w, h = max(wajah, key=lambda r: r[2] * r[3])
    roi = img[y + h // 4: y + 3 * h // 4, x + w // 4: x + 3 * w // 4]
    return klasifikasi_kulit(roi)


SKIN_HEX = {"Terang": "#F1C9A5", "Sedang": "#D2A06F", "Gelap": "#8D5A3B"}
LEBAR = {"Ramping": 0.85, "Proporsional": 1.0, "Berisi": 1.15, "Besar": 1.3}


def kategori_tinggi(tb):
    return "Pendek" if tb < 160 else "Sedang" if tb <= 175 else "Tinggi"


TETANGGA = {"Kasual": ["Streetwear", "Sporty", "Elegan"], "Formal": ["Elegan", "Kasual"], "Sporty": ["Kasual", "Streetwear"],
            "Streetwear": ["Kasual", "Sporty"], "Elegan": ["Formal", "Kasual"]}


def _pilih_item(df, acara, gender, kategori, gaya, rng, n):
    """Utamakan item yang cocok gaya, lalu gaya yang berdekatan, baru sisanya."""
    d = df[(df.Acara == acara) & (df.Gender == gender) & (df.Kategori == kategori)]
    tags = {r.Item: [x.strip() for x in r.Gaya_Cocok.split(",")] for r in d.itertuples()}
    cocok = [i for i, t in tags.items() if gaya in t]
    dekat = [i for i, t in tags.items() if i not in cocok and any(x in t for x in TETANGGA[gaya])]
    lain = [i for i in tags if i not in cocok and i not in dekat]
    for grup in (cocok, dekat, lain):
        rng.shuffle(grup)
    hasil = (cocok + dekat + lain)[:n]
    while len(hasil) < n:
        hasil.append(hasil[len(hasil) % max(len(hasil), 1)])
    return hasil


def gambar_maneken(look, profil, tipe):
    """Membuat gambar SVG maneken berwarna sesuai look, tipe tubuh, tinggi, dan warna kulit."""
    f = LEBAR[tipe]
    leg = max(95, min(150, 120 + (profil["tb"] - 170) * 0.7))
    skin = SKIN_HEX[profil["warna_kulit"]]
    top, bot, shoe = look["hex_atasan"], look["hex_bawahan"], look["hex_sepatu"]
    cx, y0 = 100, 20
    t = look["atasan"].lower()
    gaun = any(k in t for k in ("dress", "kebaya"))
    rok = gaun or "rok" in look["bawahan"].lower()
    if "dress" in t:
        bot = top
    w_t = 74 * f
    y_t0, y_t1 = y0 + 62, y0 + 62 + 92
    H = int(y_t1 + leg + 50)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 {H}" width="200" height="{H}">',
             f'<rect x="{cx-3}" y="{y0+40}" width="6" height="26" fill="{skin}"/>',
             f'<circle cx="{cx}" cy="{y0+22}" r="22" fill="{skin}"/>']
    # lengan
    parts.append(f'<rect x="{cx - w_t/2 - 16}" y="{y_t0}" width="16" height="62" rx="8" fill="{top}"/>')
    parts.append(f'<rect x="{cx + w_t/2}" y="{y_t0}" width="16" height="62" rx="8" fill="{top}"/>')
    parts.append(f'<circle cx="{cx - w_t/2 - 8}" cy="{y_t0+68}" r="7" fill="{skin}"/><circle cx="{cx + w_t/2 + 8}" cy="{y_t0+68}" r="7" fill="{skin}"/>')
    # badan
    parts.append(f'<path d="M{cx-w_t/2},{y_t0} L{cx+w_t/2},{y_t0} L{cx+w_t/2*0.92},{y_t1} L{cx-w_t/2*0.92},{y_t1} Z" fill="{top}"/>')
    ykaki = y_t1 + leg
    if rok:
        warna_rok = top if gaun else bot
        lebar_bawah = w_t * 1.25
        parts.append(f'<path d="M{cx-w_t/2*0.92},{y_t1-4} L{cx+w_t/2*0.92},{y_t1-4} L{cx+lebar_bawah/2},{ykaki-leg*0.25} L{cx-lebar_bawah/2},{ykaki-leg*0.25} Z" fill="{warna_rok}"/>')
        parts.append(f'<rect x="{cx-14*f}" y="{ykaki-leg*0.25}" width="11" height="{leg*0.25}" fill="{skin}"/><rect x="{cx+3*f}" y="{ykaki-leg*0.25}" width="11" height="{leg*0.25}" fill="{skin}"/>')
    else:
        parts.append(f'<rect x="{cx-w_t/2*0.92}" y="{y_t1-4}" width="{w_t*0.92/2-1}" height="{leg+4}" rx="3" fill="{bot}"/>')
        parts.append(f'<rect x="{cx+1}" y="{y_t1-4}" width="{w_t*0.92/2-1}" height="{leg+4}" rx="3" fill="{bot}"/>')
    parts.append(f'<ellipse cx="{cx - w_t*0.23}" cy="{ykaki+6}" rx="17" ry="8" fill="{shoe}"/><ellipse cx="{cx + w_t*0.23}" cy="{ykaki+6}" rx="17" ry="8" fill="{shoe}"/>')
    parts.append("</svg>")
    return "".join(parts)


def rekomendasi(profil, kb, variasi=0, jumlah=3):
    """Menyusun beberapa look lengkap yang unik untuk tiap orang.
    profil: gender, bb, tb, acara, gaya, warna_kulit (opsional: nama). variasi: angka untuk minta set look lain."""
    import random
    g, a, gy, kulit = profil["gender"], profil["acara"], profil["gaya"], profil["warna_kulit"]
    tipe = tipe_tubuh(profil["bb"], profil["tb"])
    tinggi = kategori_tinggi(profil["tb"])
    rng = random.Random(f"{g}|{a}|{gy}|{kulit}|{profil['bb']}|{profil['tb']}|{variasi}")

    item = kb["Item"]
    pil = {k: _pilih_item(item, a, g, k, gy, rng, jumlah) for k in ["Atasan", "Bawahan", "Alas kaki", "Aksesori"]}
    palet = kb["Palet"][kb["Palet"].Warna_Kulit == kulit]
    warna_atasan = list(palet[palet.Peran == "Atasan"].itertuples())
    warna_netral = list(palet[palet.Peran == "Netral"].itertuples())
    rng.shuffle(warna_atasan)
    rng.shuffle(warna_netral)

    tb_row = kb["Tipe_Tubuh"].query("Tipe_Tubuh == @tipe and Gender == @g").iloc[0]
    k_row = kb["Warna_Kulit"].query("Warna_Kulit == @kulit").iloc[0]
    t_row = kb["Tinggi"].query("Tinggi == @tinggi").iloc[0]
    gaya_row = kb["Gaya"].query("Gaya == @gy").iloc[0]

    looks = []
    for i in range(jumlah):
        wa = warna_atasan[i % len(warna_atasan)]
        wb = warna_netral[i % len(warna_netral)]
        ws = warna_netral[(i + 1) % len(warna_netral)]
        look = {
            "nama": f"Look {i+1}",
            "atasan": pil["Atasan"][i], "warna_atasan": wa.Nama, "hex_atasan": wa.Hex,
            "bawahan": pil["Bawahan"][i], "warna_bawahan": wb.Nama, "hex_bawahan": wb.Hex,
            "alas_kaki": pil["Alas kaki"][i], "warna_sepatu": ws.Nama, "hex_sepatu": ws.Hex,
            "aksesori": pil["Aksesori"][i],
        }
        if "dress" in look["atasan"].lower():
            look["bawahan"] = "(menyatu dengan dress)"
            look["warna_bawahan"] = ""
        look["svg"] = gambar_maneken(look, profil, tipe)
        looks.append(look)

    return {
        "bmi": round(hitung_bmi(profil["bb"], profil["tb"]), 1),
        "tipe_tubuh": tipe, "kategori_tinggi": tinggi,
        "looks": looks,
        "potongan": tb_row.Potongan_Disarankan, "hindari_potongan": tb_row.Hindari,
        "saran_tinggi": t_row.Saran,
        "warna_hindari": k_row.Warna_Hindari,
        "catatan_gaya": gaya_row.Catatan,
    }


if __name__ == "__main__":
    kb = load_kb()
    teks = input("Ceritakan (contoh: saya cowok BB 60 TB 170, mau ke kondangan gaya formal): ")
    p = {"gender": "Pria", "bb": 60, "tb": 170, "acara": "Kuliah", "gaya": "Kasual", "warna_kulit": "Sedang"}
    p.update(ekstrak_dari_teks(teks))
    from pprint import pprint
    h = rekomendasi(p, kb)
    h = {k: v for k, v in h.items() if k != 'looks'} | {'looks': [{k: v for k, v in l.items() if k != 'svg'} for l in h['looks']]}
    pprint(h, sort_dicts=False)
