# Rekomendasi Outfit AI

Sistem rekomendasi outfit berbasis aturan pakar (Excel) + Python.
Input: chat (BB, TB, acara, gaya), suara, dan foto wajah (warna kulit).

## Menjalankan
    pip install -r requirements.txt
    python make_knowledge_base.py      # membuat pengetahuan_outfit.xlsx (sudah disertakan)
    streamlit run app.py

Tanpa tampilan web, cukup:  python engine.py

## Struktur
- make_knowledge_base.py : membuat basis pengetahuan pakar di Excel
- pengetahuan_outfit.xlsx : aturan (Tipe_Tubuh, Warna_Kulit, Acara, Gaya) - edit sesuai pakar
- engine.py : hitung BMI, deteksi warna kulit (OpenCV), baca teks, cocokkan aturan
- app.py : antarmuka Streamlit (tab Chat, Suara, Kamera)

## Catatan
- Isi Excel adalah contoh awal; ganti dengan data pakar/stylist untuk proyekmu.
- Suara memakai Google Speech (bahasa id-ID), butuh internet.
- Deteksi warna kulit bersifat perkiraan dan sensitif pada cahaya; hasilnya bisa diubah manual.
