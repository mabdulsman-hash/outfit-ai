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


def rekomendasi(profil, kb):
    """profil: dict gender, bb, tb, acara, gaya, warna_kulit. Mengembalikan dict saran."""
    g = profil["gender"]
    tipe = tipe_tubuh(profil["bb"], profil["tb"])
    a = kb["Acara"].query("Acara == @profil['acara'] and Gender == @g").iloc[0]
    tb_row = kb["Tipe_Tubuh"].query("Tipe_Tubuh == @tipe and Gender == @g").iloc[0]
    k_row = kb["Warna_Kulit"].query("Warna_Kulit == @profil['warna_kulit']").iloc[0]
    gaya = kb["Gaya"].query("Gaya == @profil['gaya']").iloc[0]
    return {
        "bmi": round(hitung_bmi(profil["bb"], profil["tb"]), 1),
        "tipe_tubuh": tipe,
        "outfit": {"Atasan": a.Atasan, "Bawahan": a.Bawahan, "Alas kaki": a.Alas_Kaki, "Aksesori": a.Aksesori},
        "potongan": tb_row.Potongan_Disarankan,
        "hindari_potongan": tb_row.Hindari,
        "warna_cocok": k_row.Warna_Cocok,
        "warna_hindari": k_row.Warna_Hindari,
        "catatan_gaya": gaya.Catatan,
    }


if __name__ == "__main__":
    kb = load_kb()
    teks = input("Ceritakan (contoh: saya cowok BB 60 TB 170, mau ke kondangan gaya formal): ")
    p = {"gender": "Pria", "bb": 60, "tb": 170, "acara": "Kuliah", "gaya": "Kasual", "warna_kulit": "Sedang"}
    p.update(ekstrak_dari_teks(teks))
    from pprint import pprint
    pprint(rekomendasi(p, kb), sort_dicts=False)
