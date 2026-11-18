"""Membuat file basis pengetahuan pakar (Excel).
Isi di sini adalah CONTOH awal. Ganti/lengkapi dengan data dari stylist atau
referensi fashion yang kamu pakai, lalu jalankan ulang file ini
(atau langsung edit pengetahuan_outfit.xlsx di Excel)."""
import pandas as pd

tipe_tubuh = [
    ["Ramping", "Pria", "Layer (kemeja/jaket tipis), bahan bertekstur, potongan regular fit", "Pakaian terlalu longgar dan lusuh"],
    ["Ramping", "Wanita", "Layer, rok/celana high-waist, motif untuk menambah volume", "Pakaian terlalu longgar tanpa bentuk"],
    ["Proporsional", "Pria", "Hampir semua potongan cocok; regular atau slim fit", "-"],
    ["Proporsional", "Wanita", "Hampir semua potongan cocok; coba high-waist atau A-line", "-"],
    ["Berisi", "Pria", "Potongan lurus, bahan jatuh, kerah V atau kemeja polos", "Bahan terlalu tipis menempel, motif besar horizontal"],
    ["Berisi", "Wanita", "A-line, wrap, atasan panjang selutut, kerah V", "Bahan menempel ketat, garis horizontal tebal"],
    ["Besar", "Pria", "Ukuran pas bahu, warna satu tone, potongan lurus", "Ukuran terlalu sempit, motif ramai"],
    ["Besar", "Wanita", "Outer panjang terbuka, warna satu tone, potongan A-line", "Ukuran terlalu sempit, motif ramai"],
]
warna_kulit = [
    ["Terang", "Navy, maroon, hijau botol, abu tua, dusty pink", "Warna sangat pucat (krem muda, putih tulang) yang membuat wajah pudar"],
    ["Sedang", "Olive, mustard, terracotta, biru royal, putih bersih", "Warna cokelat muda yang mirip tone kulit"],
    ["Gelap", "Putih, kuning cerah, oranye, fuchsia, biru elektrik, emerald", "Warna cokelat tua dan hitam di dekat wajah tanpa aksen terang"],
]
acara = [
    ["Kuliah", "Pria", "Kaos polos atau kemeja casual", "Celana chino / jeans", "Sneakers", "Tas ransel, jam tangan"],
    ["Kuliah", "Wanita", "Blouse atau kaos oversize", "Jeans / celana kulot", "Sneakers / flat shoes", "Tas selempang, jam tangan"],
    ["Kerja", "Pria", "Kemeja lengan panjang", "Celana bahan / slacks", "Pantofel", "Ikat pinggang kulit, jam tangan"],
    ["Kerja", "Wanita", "Kemeja / blouse formal", "Celana bahan / rok midi", "Flat shoes / loafers", "Tas kerja, anting kecil"],
    ["Kondangan", "Pria", "Batik atau kemeja formal", "Celana bahan gelap", "Pantofel", "Jam tangan klasik"],
    ["Kondangan", "Wanita", "Kebaya modern atau dress midi", "Rok batik / bawahan senada", "Heels rendah / flat", "Clutch, anting"],
    ["Santai", "Pria", "Kaos / polo shirt", "Celana pendek atau jeans", "Sneakers / sandal", "Topi, tas kecil"],
    ["Santai", "Wanita", "Kaos / kemeja linen", "Jeans / celana kulot", "Sneakers / sandal", "Tote bag, kacamata"],
    ["Olahraga", "Pria", "Kaos dry-fit", "Celana training", "Sepatu lari", "Headband, botol minum"],
    ["Olahraga", "Wanita", "Kaos dry-fit / sport top", "Legging / celana training", "Sepatu lari", "Headband, botol minum"],
    ["Kencan", "Pria", "Kemeja rapi atau polo", "Chino gelap", "Sneakers bersih / loafers", "Parfum, jam tangan"],
    ["Kencan", "Wanita", "Dress casual / blouse rapi", "Rok / jeans high-waist", "Flat shoes / heels rendah", "Anting, tas kecil"],
]
gaya = [
    ["Kasual", "Padu padan sederhana, nyaman dipakai seharian"],
    ["Formal", "Gunakan warna netral, bahan rapi, minim aksesori mencolok"],
    ["Sporty", "Tambahkan jaket training atau sneakers chunky"],
    ["Streetwear", "Pakai oversize, layering, tambah topi atau tas crossbody"],
    ["Elegan", "Pilih satu warna dominan, bahan jatuh, aksesori minimal"],
]

with pd.ExcelWriter("pengetahuan_outfit.xlsx") as w:
    pd.DataFrame(tipe_tubuh, columns=["Tipe_Tubuh", "Gender", "Potongan_Disarankan", "Hindari"]).to_excel(w, sheet_name="Tipe_Tubuh", index=False)
    pd.DataFrame(warna_kulit, columns=["Warna_Kulit", "Warna_Cocok", "Warna_Hindari"]).to_excel(w, sheet_name="Warna_Kulit", index=False)
    pd.DataFrame(acara, columns=["Acara", "Gender", "Atasan", "Bawahan", "Alas_Kaki", "Aksesori"]).to_excel(w, sheet_name="Acara", index=False)
    pd.DataFrame(gaya, columns=["Gaya", "Catatan"]).to_excel(w, sheet_name="Gaya", index=False)
print("pengetahuan_outfit.xlsx dibuat")
