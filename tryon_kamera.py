"""
tryon_kamera.py - Pakaian langsung menempel di badan pada kamera live.
Kamera browser (streamlit-webrtc) -> MediaPipe Pose -> tempel PNG pakaian.
"""
import threading

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer

import tryon

MIN_VIS = 0.5


def tempel(frame, png, cx, top, width, height):
    """Tempel png (BGRA) ke frame (BGR) dengan blending alpha. Aman di tepi layar."""
    width, height = int(width), int(height)
    if png is None or width < 10 or height < 10:
        return
    kecil = cv2.resize(png, (width, height), interpolation=cv2.INTER_AREA)
    x0, y0 = int(cx - width / 2), int(top)
    fh, fw = frame.shape[:2]
    ax0, ay0 = max(x0, 0), max(y0, 0)
    ax1, ay1 = min(x0 + width, fw), min(y0 + height, fh)
    if ax0 >= ax1 or ay0 >= ay1:
        return
    p = kecil[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
    a = p[:, :, 3:4].astype(np.float32) / 255.0
    roi = frame[ay0:ay1, ax0:ax1].astype(np.float32)
    frame[ay0:ay1, ax0:ax1] = (a * p[:, :, :3] + (1 - a) * roi).astype(np.uint8)


class OutfitProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self._lock = threading.Lock()
        self._spec = {}
        self._prev = {}

    def set_spec(self, spec):
        with self._lock:
            self._spec = dict(spec)

    def _halus(self, k, v, a=0.6):
        lama = self._prev.get(k, v)
        baru = a * lama + (1 - a) * v
        self._prev[k] = baru
        return baru

    def recv(self, frame):
        img = cv2.flip(frame.to_ndarray(format="bgr24"), 1)  # tampilan cermin
        h, w = img.shape[:2]
        hasil = self.pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        with self._lock:
            spec = dict(self._spec)

        if hasil.pose_landmarks and spec:
            lm = hasil.pose_landmarks.landmark

            def titik(i):
                return np.array([lm[i].x * w, lm[i].y * h]), lm[i].visibility

            (ls, v1), (rs, v2) = titik(11), titik(12)
            (lh, v3), (rh, v4) = titik(23), titik(24)
            (lk, v5), (rk, v6) = titik(25), titik(26)
            (la, v7), (ra, v8) = titik(27), titik(28)
            bahu_ok = min(v1, v2) > MIN_VIS
            pinggul_ok = min(v3, v4) > MIN_VIS
            lutut_ok = min(v5, v6) > MIN_VIS
            kaki_ok = min(v7, v8) > MIN_VIS

            bahu_c, pinggul_c = (ls + rs) / 2, (lh + rh) / 2
            lebar_bahu, lebar_pinggul = abs(ls[0] - rs[0]), abs(lh[0] - rh[0])
            torso = pinggul_c[1] - bahu_c[1]
            lutut_y = (lk[1] + rk[1]) / 2
            kaki_y = (la[1] + ra[1]) / 2

            atasan_nama = spec["atasan"][0].lower() if spec.get("atasan") else ""
            gaun = "dress" in atasan_nama

            # 1) bawahan dulu supaya atasan menutupi pinggang
            if spec.get("bawahan") and pinggul_ok:
                nama = spec["bawahan"][0].lower()
                if "rok" in nama and lutut_ok:
                    bawah = lutut_y + ((kaki_y - lutut_y) * 0.25 if kaki_ok else torso * 0.1)
                else:
                    bawah = kaki_y if kaki_ok else pinggul_c[1] + torso * 1.8
                atas = pinggul_c[1] - torso * 0.12
                lebar = max(lebar_pinggul * 2.0, lebar_bahu * 1.1)
                tempel(img, tryon.muat_item("bawahan", *spec["bawahan"]),
                       self._halus("b_x", pinggul_c[0]), self._halus("b_t", atas),
                       self._halus("b_w", lebar), max(bawah - atas, 20))

            # 2) atasan (dress: memanjang sampai lutut/kaki)
            if spec.get("atasan") and bahu_ok and pinggul_ok:
                atas = bahu_c[1] - torso * 0.12
                if gaun:
                    bawah = kaki_y if kaki_ok else (lutut_y if lutut_ok else pinggul_c[1] + torso * 1.2)
                    tinggi, lebar = bawah - atas, max(lebar_bahu * 1.9, lebar_pinggul * 2.2)
                else:
                    tinggi, lebar = torso * 1.30, lebar_bahu * 1.85
                tempel(img, tryon.muat_item("atasan", *spec["atasan"]),
                       self._halus("a_x", bahu_c[0]), self._halus("a_t", atas),
                       self._halus("a_w", lebar), self._halus("a_h", tinggi))

            # 3) sepatu
            if spec.get("alas-kaki") and kaki_ok:
                pusat = (la + ra) / 2
                lebar = max(abs(la[0] - ra[0]) * 1.9, lebar_bahu * 0.8)
                tinggi = lebar * 0.45
                tempel(img, tryon.muat_item("alas-kaki", *spec["alas-kaki"]),
                       self._halus("s_x", pusat[0]), self._halus("s_t", pusat[1] - tinggi * 0.35),
                       self._halus("s_w", lebar), tinggi)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def render_kamera(look):
    """Panggil dari app.py dengan satu look dari engine.rekomendasi()."""
    spec = tryon.spec_dari_look(look)
    _, hilang = tryon.gambar_spec(spec)
    if hilang:
        st.warning("Gambar pakaian belum ada di repo: " + ", ".join(hilang))

    ctx = webrtc_streamer(
        key="outfit-tryon",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=OutfitProcessor,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        async_processing=True,
    )
    if ctx.video_processor:
        ctx.video_processor.set_spec(spec)
    st.caption("Berdiri agak jauh sampai badan dari bahu sampai kaki terlihat, dengan cahaya cukup.")
