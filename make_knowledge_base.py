"""Membuat basis pengetahuan pakar (Excel) v2.
Isi di sini adalah CONTOH awal. Ganti/lengkapi dengan data stylist atau referensi
fashion milikmu, lalu jalankan ulang file ini (atau edit pengetahuan_outfit.xlsx di Excel).

Kode gaya di daftar item: K=Kasual, F=Formal, S=Sporty, T=Streetwear, E=Elegan"""
import pandas as pd

GAYA_KODE = {"K": "Kasual", "F": "Formal", "S": "Sporty", "T": "Streetwear", "E": "Elegan"}

# (acara, gender) -> kategori -> [(item, kode_gaya)]
ITEM = {
 ("Kuliah", "Pria"): {
  "Atasan": [("Kaos polos oversize", "KT"), ("Kemeja flanel lengan panjang", "KT"), ("Polo shirt", "KFE"), ("Hoodie tipis", "ST"), ("Kemeja oxford polos", "FE")],
  "Bawahan": [("Celana chino", "KFE"), ("Jeans straight", "KT"), ("Celana jogger", "ST"), ("Celana kain slim fit", "FE")],
  "Alas kaki": [("Sneakers putih", "KTE"), ("Sepatu kets ringan", "SK"), ("Loafers", "FE"), ("Sneakers chunky", "T")],
  "Aksesori": [("Tas ransel", "KST"), ("Jam tangan minimalis", "FEK"), ("Topi baseball", "TS"), ("Tote bag kanvas", "K")]},
 ("Kuliah", "Wanita"): {
  "Atasan": [("Blouse longgar", "KE"), ("Kaos oversize", "KT"), ("Kemeja putih rapi", "FE"), ("Cardigan rajut", "KE"), ("Crop hoodie", "ST")],
  "Bawahan": [("Jeans high-waist", "KT"), ("Celana kulot", "KFE"), ("Rok midi plisket", "KE"), ("Celana jogger", "S")],
  "Alas kaki": [("Sneakers putih", "KTS"), ("Flat shoes", "FEK"), ("Loafers", "FE"), ("Sneakers chunky", "T")],
  "Aksesori": [("Tas selempang", "KE"), ("Totebag kanvas", "K"), ("Jam tangan", "FE"), ("Bucket hat", "TK")]},
 ("Kerja", "Pria"): {
  "Atasan": [("Kemeja lengan panjang polos", "FE"), ("Kemeja bergaris halus", "FK"), ("Polo shirt rapi", "KF"), ("Blazer dengan kemeja", "FE"), ("Kemeja batik modern", "FK")],
  "Bawahan": [("Celana bahan slacks", "FE"), ("Chino gelap", "FK"), ("Celana bahan slim", "FE"), ("Chino regular", "K")],
  "Alas kaki": [("Pantofel", "FE"), ("Loafers kulit", "FEK"), ("Derby shoes", "FE"), ("Sneakers kulit polos", "KT")],
  "Aksesori": [("Ikat pinggang kulit", "FEK"), ("Jam tangan klasik", "FE"), ("Tas kerja", "FEK"), ("Dasi tipis", "F")]},
 ("Kerja", "Wanita"): {
  "Atasan": [("Kemeja formal", "FE"), ("Blouse satin", "EF"), ("Blazer dengan inner polos", "FE"), ("Kemeja linen rapi", "KF"), ("Knit top rapi", "KE")],
  "Bawahan": [("Celana bahan lurus", "FE"), ("Rok midi", "FE"), ("Celana kulot bahan", "KFE"), ("Rok pensil", "FE")],
  "Alas kaki": [("Flat shoes", "FEK"), ("Loafers", "FEK"), ("Heels rendah", "FE"), ("Sneakers kulit polos", "KT")],
  "Aksesori": [("Tas kerja", "FE"), ("Anting kecil", "FEK"), ("Jam tangan", "FEK"), ("Syal tipis", "E")]},
 ("Kondangan", "Pria"): {
  "Atasan": [("Batik lengan panjang", "FEK"), ("Kemeja putih dengan jas", "FE"), ("Kemeja formal polos", "FEK"), ("Koko modern", "FEK"), ("Batik modern slim fit", "FE")],
  "Bawahan": [("Celana bahan hitam", "FE"), ("Celana bahan navy", "FE"), ("Celana bahan abu tua", "FEK"), ("Celana bahan krem", "FK")],
  "Alas kaki": [("Pantofel hitam", "FE"), ("Pantofel cokelat", "FEK"), ("Loafers", "FEK"), ("Derby shoes", "FE")],
  "Aksesori": [("Jam tangan klasik", "FE"), ("Peci", "FEK"), ("Ikat pinggang kulit", "FEK"), ("Pocket square", "E")]},
 ("Kondangan", "Wanita"): {
  "Atasan": [("Kebaya modern", "FE"), ("Dress midi brokat", "E"), ("Blouse satin dengan outer", "EF"), ("Dress A-line elegan", "E"), ("Kebaya kutubaru", "FE")],
  "Bawahan": [("Rok batik panjang", "FEK"), ("Rok span", "FE"), ("Rok plisket panjang", "EK"), ("Celana kulot formal", "F")],
  "Alas kaki": [("Heels rendah", "FE"), ("Flat shoes berhias", "EK"), ("Wedges", "EFK"), ("Sandal formal", "KF")],
  "Aksesori": [("Clutch", "FE"), ("Anting panjang", "E"), ("Bros", "FEK"), ("Selendang", "EFK")]},
 ("Santai", "Pria"): {
  "Atasan": [("Kaos polos", "KST"), ("Kemeja linen lengan pendek", "KE"), ("Polo shirt", "KF"), ("Kaos grafis", "T"), ("Jaket denim", "KT")],
  "Bawahan": [("Celana pendek chino", "K"), ("Jeans", "KT"), ("Celana cargo", "T"), ("Celana jogger", "KS")],
  "Alas kaki": [("Sneakers", "KTS"), ("Sandal gunung", "K"), ("Slip-on", "K"), ("Sneakers chunky", "T")],
  "Aksesori": [("Topi", "KTS"), ("Tas selempang kecil", "KT"), ("Kacamata hitam", "KTE"), ("Gelang tali", "K")]},
 ("Santai", "Wanita"): {
  "Atasan": [("Kaos longgar", "KT"), ("Kemeja linen oversize", "KE"), ("Tank top dengan outer", "KT"), ("Knit tipis", "KE"), ("Crop top dengan kemeja", "T")],
  "Bawahan": [("Jeans mom fit", "KT"), ("Celana kulot linen", "KE"), ("Rok denim", "KT"), ("Celana pendek", "KS")],
  "Alas kaki": [("Sneakers", "KTS"), ("Sandal tali", "KE"), ("Slip-on", "K"), ("Sneakers chunky", "T")],
  "Aksesori": [("Tote bag", "KE"), ("Kacamata hitam", "KTE"), ("Topi", "KTS"), ("Scrunchie", "K")]},
 ("Olahraga", "Pria"): {
  "Atasan": [("Kaos dry-fit", "SK"), ("Singlet olahraga", "S"), ("Jaket training", "ST"), ("Kaos kompresi", "S")],
  "Bawahan": [("Celana training", "SK"), ("Celana pendek lari", "S"), ("Jogger olahraga", "ST"), ("Legging kompresi", "S")],
  "Alas kaki": [("Sepatu lari", "S"), ("Sepatu training", "S"), ("Sepatu futsal", "S"), ("Sneakers ringan", "KT")],
  "Aksesori": [("Headband", "S"), ("Botol minum", "SK"), ("Sarung tangan gym", "S"), ("Tas gym", "ST")]},
 ("Olahraga", "Wanita"): {
  "Atasan": [("Sport top", "S"), ("Kaos dry-fit", "SK"), ("Jaket training", "ST"), ("Tank top olahraga", "S")],
  "Bawahan": [("Legging", "SK"), ("Celana training", "SK"), ("Celana pendek lari", "S"), ("Jogger olahraga", "ST")],
  "Alas kaki": [("Sepatu lari", "S"), ("Sepatu training", "S"), ("Sneakers ringan", "KT"), ("Sepatu yoga", "S")],
  "Aksesori": [("Headband", "S"), ("Botol minum", "SK"), ("Ikat rambut sport", "S"), ("Tas gym", "ST")]},
 ("Kencan", "Pria"): {
  "Atasan": [("Kemeja rapi", "FE"), ("Polo shirt", "KFE"), ("Kemeja linen", "KE"), ("Knit polo", "EK"), ("Jaket bomber dengan kaos polos", "KT")],
  "Bawahan": [("Chino gelap", "KFE"), ("Jeans slim gelap", "KT"), ("Celana bahan", "FE"), ("Celana linen", "KE")],
  "Alas kaki": [("Sneakers bersih", "KTE"), ("Loafers", "FE"), ("Chelsea boots", "ET"), ("Suede shoes", "EK")],
  "Aksesori": [("Parfum", "KFE"), ("Jam tangan", "FEK"), ("Kalung tipis", "TE"), ("Ikat pinggang kulit", "FE")]},
 ("Kencan", "Wanita"): {
  "Atasan": [("Dress casual", "KE"), ("Blouse rapi", "FE"), ("Knit top", "KE"), ("Dress satin", "E"), ("Kemeja crop dengan cardigan", "KT")],
  "Bawahan": [("Rok midi", "KE"), ("Jeans high-waist", "KT"), ("Celana kulot", "KFE"), ("Rok mini plisket", "TK")],
  "Alas kaki": [("Flat shoes", "KEF"), ("Heels rendah", "EF"), ("Sneakers bersih", "KTS"), ("Sandal hak", "EK")],
  "Aksesori": [("Anting", "KEF"), ("Tas kecil", "KEF"), ("Kalung tipis", "KE"), ("Parfum", "KFE")]},
}

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
tinggi = [
 ["Pendek", "Pilih bawahan high-waist dan atasan tidak terlalu panjang; satu warna dari atas ke bawah membuat tampak lebih tinggi."],
 ["Sedang", "Proporsi fleksibel; bebas bermain layer dan panjang pakaian."],
 ["Tinggi", "Cocok dengan layer panjang, outer longgar, dan potongan lurus; hindari bawahan yang terlalu pendek."],
]
warna_kulit = [
 ["Terang", "Warna sangat pucat (krem muda, putih tulang) yang membuat wajah pudar"],
 ["Sedang", "Warna cokelat muda yang mirip tone kulit"],
 ["Gelap", "Warna cokelat tua dan hitam di dekat wajah tanpa aksen terang"],
]
# (kulit, peran, nama, hex)
palet = [
 ("Terang", "Atasan", "Maroon", "#7B1E2B"), ("Terang", "Atasan", "Hijau botol", "#1E5B45"), ("Terang", "Atasan", "Dusty pink", "#D8A0A8"),
 ("Terang", "Atasan", "Navy", "#23325B"), ("Terang", "Atasan", "Abu tua", "#55595F"),
 ("Terang", "Netral", "Navy gelap", "#1F2A44"), ("Terang", "Netral", "Abu tua", "#4B5058"), ("Terang", "Netral", "Hitam", "#1C1C1C"),
 ("Sedang", "Atasan", "Olive", "#6B7A3A"), ("Sedang", "Atasan", "Mustard", "#D9A404"), ("Sedang", "Atasan", "Terracotta", "#C8643C"),
 ("Sedang", "Atasan", "Biru royal", "#2F55C5"), ("Sedang", "Atasan", "Putih", "#F8F8F8"),
 ("Sedang", "Netral", "Denim", "#34495E"), ("Sedang", "Netral", "Hitam", "#1C1C1C"), ("Sedang", "Netral", "Cokelat tua", "#4E342E"),
 ("Gelap", "Atasan", "Putih", "#F8F8F8"), ("Gelap", "Atasan", "Kuning cerah", "#F7D12E"), ("Gelap", "Atasan", "Oranye", "#F28C28"),
 ("Gelap", "Atasan", "Fuchsia", "#D5338F"), ("Gelap", "Atasan", "Biru elektrik", "#1E6BFF"), ("Gelap", "Atasan", "Emerald", "#0B8F5B"),
 ("Gelap", "Netral", "Denim biru", "#3F5F8F"), ("Gelap", "Netral", "Krem", "#E8DCC4"), ("Gelap", "Netral", "Hitam", "#1C1C1C"),
]
gaya = [
 ["Kasual", "Padu padan sederhana, nyaman dipakai seharian"],
 ["Formal", "Gunakan warna netral, bahan rapi, minim aksesori mencolok"],
 ["Sporty", "Tambahkan jaket training atau sneakers chunky"],
 ["Streetwear", "Pakai oversize, layering, tambah topi atau tas crossbody"],
 ["Elegan", "Pilih satu warna dominan, bahan jatuh, aksesori minimal"],
]

rows = []
for (acara, gender), kat in ITEM.items():
    for k, items in kat.items():
        for nama, kode in items:
            rows.append([acara, gender, k, nama, ",".join(GAYA_KODE[c] for c in kode)])

with pd.ExcelWriter("pengetahuan_outfit.xlsx") as w:
    pd.DataFrame(rows, columns=["Acara", "Gender", "Kategori", "Item", "Gaya_Cocok"]).to_excel(w, sheet_name="Item", index=False)
    pd.DataFrame(tipe_tubuh, columns=["Tipe_Tubuh", "Gender", "Potongan_Disarankan", "Hindari"]).to_excel(w, sheet_name="Tipe_Tubuh", index=False)
    pd.DataFrame(tinggi, columns=["Tinggi", "Saran"]).to_excel(w, sheet_name="Tinggi", index=False)
    pd.DataFrame(warna_kulit, columns=["Warna_Kulit", "Warna_Hindari"]).to_excel(w, sheet_name="Warna_Kulit", index=False)
    pd.DataFrame(palet, columns=["Warna_Kulit", "Peran", "Nama", "Hex"]).to_excel(w, sheet_name="Palet", index=False)
    pd.DataFrame(gaya, columns=["Gaya", "Catatan"]).to_excel(w, sheet_name="Gaya", index=False)
print("pengetahuan_outfit.xlsx dibuat:", len(rows), "item")
