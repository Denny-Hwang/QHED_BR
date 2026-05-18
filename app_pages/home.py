"""Home / landing page — quick-start cards + project pitch."""

from __future__ import annotations

import os
import time

import numpy as np
import streamlit as st
from PIL import Image

from basicFunctions import load_image_from_array
from classical_ed_methods import sobel_edge_detection
from qhed import edge_detection_stride
from ui.i18n import t


IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "samples")

# Curated quick-start samples — small enough that QHED finishes in a couple of
# seconds even on a free Streamlit Cloud worker.
SAMPLES = [
    ("home.card_cat", "cat_cc0.png"),
    ("home.card_coastline", "satellite_coastline.png"),
    ("home.card_fingerprint", "fingerprint.png"),
]

SAMPLE_SIZE = 64  # 64x64 — fits in 6 qubits/dim, but we use 3 qb (8x8 patches)
SAMPLE_PATCH_QB = 3
SAMPLE_THR = 0.7


def _load_sample(filename: str) -> np.ndarray | None:
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path))


def _run_sample(gray: np.ndarray):
    start = time.time()
    qhed_res, _ = edge_detection_stride(
        gray,
        width_qb=SAMPLE_PATCH_QB,
        thr_ratio=SAMPLE_THR,
        stride_mode="with_restoration",
        patch_boundary_zero=True,
    )
    qhed_time = time.time() - start

    start = time.time()
    gray_u8 = (gray * 255).astype(np.uint8)
    sobel_res = sobel_edge_detection(gray_u8)
    sobel_time = time.time() - start
    return qhed_res, qhed_time, sobel_res, sobel_time


def render() -> None:
    st.title(t("home.title"))
    st.markdown(f"**{t('home.subtitle')}**")
    st.markdown(t("home.intro"))
    st.markdown("---")

    st.header(t("home.quickstart"))
    st.caption(t("home.quickstart_hint"))

    cols = st.columns(len(SAMPLES))
    for col, (label_key, filename) in zip(cols, SAMPLES):
        with col:
            with st.container(border=True):
                raw = _load_sample(filename)
                if raw is None:
                    st.warning(f"Missing sample: {filename}")
                    continue
                st.markdown(f"**{t(label_key)}**")
                st.image(raw, use_container_width=True)
                run_key = f"home_run_{filename}"
                if st.button(t("home.run_button"), key=run_key, use_container_width=True):
                    gray = load_image_from_array(raw, resize=(SAMPLE_SIZE, SAMPLE_SIZE))
                    with st.spinner(""):
                        qhed_res, qhed_t, sobel_res, sobel_t = _run_sample(gray)
                    st.image(qhed_res.astype(float), clamp=True,
                             caption=f"QHED · {qhed_t:.2f}s",
                             use_container_width=True)
                    st.image(sobel_res, clamp=True,
                             caption=f"Sobel · {sobel_t*1000:.1f}ms",
                             use_container_width=True)

    st.markdown("---")
    st.markdown(t("home.explore_more"))
