"""Aplikasi Rekomendasi Outfit AI (Streamlit).
Jalankan:  streamlit run app.py"""
import streamlit as st
import engine

st.set_page_config(page_title="Rekomendasi Outfit AI", page_icon="👗", layout="wide")
st.title("👗 Rekomendasi Outfit AI")

ACARA = ["Kuliah", "Kerja", "Kondangan", "Santai", "Olahraga", "Kencan"]
GAYA = ["Kasual", "Formal", "Sporty", "Streetwear", "Elegan"]
KULIT = ["Terang", "Sedang", "Gelap"]
GENDER = ["Pria", "Wanita"]

if "profil" not in st.session_state:
    st.session_state.profil = {"gender": "Pria", "bb": 60.0, "tb": 170.0, "acara": "Kuliah", "gaya": "Kasual", "warna_kulit": "Sedang"}
if "log" not in st.session_state:
    st.session_state.log = []
p = st.session_state.profil


@st.cache_data
def kb():
    return engine.load_kb()


def terapkan_teks(teks):
    hasil = engine.ekstrak_dari_teks(teks)
    p.update(hasil)
    return hasil


# ---------------- Sidebar: profil (bisa diubah manual) ----------------
with st.sidebar:
    st.header("Profil kamu")
    p["gender"] = st.radio("Gender", GENDER, index=GENDER.index(p["gender"]), horizontal=True)
    p["bb"] = st.number_input("Berat badan (kg)", 30.0, 200.0, float(p["bb"]), 1.0)
    p["tb"] = st.number_input("Tinggi badan (cm)", 120.0, 220.0, float(p["tb"]), 1.0)
    p["acara"] = st.selectbox("Acara", ACARA, index=ACARA.index(p["acara"]))
    p["gaya"] = st.selectbox("Gaya", GAYA, index=GAYA.index(p["gaya"]))
    p["warna_kulit"] = st.selectbox("Warna kulit", KULIT, index=KULIT.index(p["warna_kulit"]))
    st.caption("Profil juga terisi otomatis dari chat, suara, atau kamera.")

tab_chat, tab_suara, tab_kamera = st.tabs(["💬 Chat", "🎤 Suara", "📷 Kamera"])

# ---------------- Chat ----------------
with tab_chat:
    st.write("Ceritakan spesifikasi tubuh dan kebutuhanmu, contoh: *saya cewek BB 52 TB 160, mau ke kondangan gaya elegan*")
    for peran, isi in st.session_state.log:
        st.chat_message(peran).write(isi)
    teks = st.chat_input("Ketik di sini...")
    if teks:
        hasil = terapkan_teks(teks)
        balasan = ("Saya tangkap: " + ", ".join(f"{k}={v}" for k, v in hasil.items())) if hasil else "Belum ada data yang terbaca. Sebutkan BB, TB, acara, atau gaya."
        st.session_state.log += [("user", teks), ("assistant", balasan)]
        st.rerun()

# ---------------- Suara ----------------
with tab_suara:
    st.write("Rekam suara, misalnya: *saya mau outfit untuk kuliah, gaya santai*")
    audio = st.audio_input("Tekan untuk merekam") if hasattr(st, "audio_input") else None
    if audio is None and not hasattr(st, "audio_input"):
        st.warning("Versi Streamlit belum mendukung rekaman. Jalankan: pip install -U streamlit")
    if audio is not None:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(audio) as src:
                data = r.record(src)
            teks_suara = r.recognize_google(data, language="id-ID")  # butuh internet
            st.success(f"Terdengar: {teks_suara}")
            hasil = terapkan_teks(teks_suara)
            st.json(hasil if hasil else {"info": "tidak ada kata kunci yang dikenali"})
        except ImportError:
            st.error("Install dulu: pip install SpeechRecognition")
        except Exception as e:
            st.error(f"Suara tidak bisa diproses ({e}). Coba rekam ulang.")

# ---------------- Kamera ----------------
with tab_kamera:
    st.write("Ambil foto wajah menghadap depan di tempat terang untuk mendeteksi warna kulit.")
    foto = st.camera_input("Foto wajah")
    if foto is None:
        foto = st.file_uploader("...atau unggah foto", type=["jpg", "jpeg", "png"])
    if foto is not None:
        label, info = engine.deteksi_warna_kulit(foto.getvalue())
        if label:
            p["warna_kulit"] = label
            st.success(f"Warna kulit terdeteksi: **{label}** ({info}). Bisa diubah manual di sidebar.")
        else:
            st.warning(info)
        st.caption("Foto hanya diproses sesaat dan tidak disimpan.")

# ---------------- Hasil ----------------
st.divider()
st.subheader("✨ Rekomendasi outfit")
try:
    h = engine.rekomendasi(p, kb())
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Profil:** {p['gender']}, {p['acara']}, gaya {p['gaya']}, kulit {p['warna_kulit']}")
        st.markdown(f"**Proporsi tubuh:** {h['tipe_tubuh']} (BMI {h['bmi']})")
        for k, v in h["outfit"].items():
            st.markdown(f"- **{k}:** {v}")
    with c2:
        st.markdown(f"**Potongan yang cocok:** {h['potongan']}")
        st.markdown(f"**Hindari:** {h['hindari_potongan']}")
        st.markdown(f"**Warna yang cocok:** {h['warna_cocok']}")
        st.markdown(f"**Hindari warna:** {h['warna_hindari']}")
        st.markdown(f"**Catatan gaya:** {h['catatan_gaya']}")
except Exception as e:
    st.error(f"Data belum lengkap: {e}")
