"""Home / landing page.

Three quick-start cards, each pointing at a synthetic image where QHED's
edge map is dramatic and clean (sharp / binary edges, low pixel-density
artefacts). Each card pulls its parameters from
:mod:`ui.presets.SAMPLE_PRESETS`, so the values shown here stay in sync
with the per-sample defaults the Interactive Edge Detection page uses.
"""

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
from ui.presets import SAMPLE_PRESETS

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")

# Three samples that *visibly* show what QHED is for: a regular pattern, a
# curved pattern, and a sparse-shape composition. All synthetic, all give an
# edge map that traces the input crisply.
CARDS = [
    {
        "rel": "samples/checkerboard.png",
        "label_key": "home.card_checkerboard",
        "blurb_key": "home.blurb_checkerboard",
    },
    {
        "rel": "samples/concentric_circles.png",
        "label_key": "home.card_circles",
        "blurb_key": "home.blurb_circles",
    },
    {
        "rel": "samples/geometric_shapes.png",
        "label_key": "home.card_shapes",
        "blurb_key": "home.blurb_shapes",
    },
]


def _load_sample(rel_path: str) -> np.ndarray | None:
    path = os.path.join(IMAGE_DIR, rel_path)
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path))


def _run_card(gray: np.ndarray, patch_qb: int, thr_ratio: float):
    """Run QHED + Sobel on a card's image and return the timings/results."""
    start = time.time()
    qhed_res, _ = edge_detection_stride(
        gray,
        width_qb=patch_qb,
        thr_ratio=thr_ratio,
        stride_mode="with_restoration",
        patch_boundary_zero=True,
    )
    qhed_time = time.time() - start

    start = time.time()
    sobel_res = sobel_edge_detection((gray * 255).astype(np.uint8))
    sobel_time = time.time() - start
    return qhed_res, qhed_time, sobel_res, sobel_time


def _open_in_lab(rel: str) -> None:
    """Preselect a sample then switch to the Interactive Edge Detection page."""
    st.session_state["__preselected_sample"] = rel
    try:
        st.switch_page("app_pages/edge_detection.py")
    except Exception:
        # st.switch_page may not be available with custom st.navigation in all
        # Streamlit versions; fall back to a hint.
        st.toast("Open the **Interactive Edge Detection** page in the sidebar.")


def render() -> None:
    st.title(t("home.title"))
    st.markdown(f"**{t('home.subtitle')}**")
    st.markdown(t("home.intro"))
    st.markdown("---")

    st.header(t("home.quickstart"))
    st.caption(t("home.quickstart_hint"))

    cols = st.columns(len(CARDS))
    for col, card in zip(cols, CARDS):
        with col, st.container(border=True):
            raw = _load_sample(card["rel"])
            if raw is None:
                st.warning(f"Missing sample: {card['rel']}")
                continue

            preset = SAMPLE_PRESETS.get(card["rel"], {})
            patch_qb = preset.get("patch_qb", 4)
            thr_ratio = preset.get("thr_ratio", 0.7)
            img_size = 2 ** preset.get("img_size_exp", 6)

            st.markdown(f"**{t(card['label_key'])}**")
            st.caption(t(card["blurb_key"]))
            st.image(raw, use_container_width=True)
            st.caption(
                f"`{img_size}×{img_size}` · patch `2^{patch_qb}` · "
                f"thr `{thr_ratio:.1f}`"
            )

            run_key = f"home_run_{card['rel']}"
            open_key = f"home_open_{card['rel']}"

            if st.button(t("home.run_button"), key=run_key, use_container_width=True,
                         type="primary"):
                gray = load_image_from_array(raw, resize=(img_size, img_size))
                with st.spinner(""):
                    qhed_res, qhed_t, sobel_res, sobel_t = _run_card(gray, patch_qb, thr_ratio)
                st.image(qhed_res.astype(float), clamp=True,
                         caption=f"QHED · {qhed_t:.2f}s",
                         use_container_width=True)
                st.image(sobel_res, clamp=True,
                         caption=f"Sobel · {sobel_t*1000:.1f}ms",
                         use_container_width=True)

            if st.button(t("home.go_to_lab"), key=open_key, use_container_width=True):
                _open_in_lab(card["rel"])

    st.markdown("---")
    st.markdown(t("home.explore_more"))
