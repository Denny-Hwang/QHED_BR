"""Page 3 — Interactive Edge Detection (with caching + i18n)."""

from __future__ import annotations

import os
import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image

from basicFunctions import load_image_from_array
from qhed import edge_detection_stride
from ui.helpers import (
    fig_to_bytes,
    img_to_bytes,
    run_classical_cached,
    run_qhed_cached,
)
from ui.i18n import t
from ui.presets import DEFAULT_PRESET, get_preset, sort_samples_by_quality

_TAG_BADGE = {
    "great": ("ed.tag_great", "#4CAF50"),
    "good":  ("ed.tag_good",  "#2196F3"),
    "fair":  ("ed.tag_fair",  "#FF9800"),
    "unknown": (None, None),
}


def _tag_badge(tag: str) -> str:
    """Render a coloured pill for a sample's QHED-quality tag."""
    key, color = _TAG_BADGE.get(tag, (None, None))
    if key is None or color is None:
        return ""
    return (
        f'<span style="background-color:{color};color:white;'
        f'padding:2px 10px;border-radius:10px;font-size:0.78em;'
        f'font-weight:500;margin-left:6px;">{t(key)}</span>'
    )


def _select_image() -> tuple[np.ndarray | None, str | None]:
    """Return ``(image_array, relative_path_or_None)``.

    The relative path is ``None`` for uploads — callers use it to look up
    per-sample QHED parameter presets.
    """
    image_source = st.radio(
        t("ed.source_label"),
        [t("ed.source_sample"), t("ed.source_upload")],
        horizontal=True,
    )

    if image_source == t("ed.source_sample"):
        img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
        exts = (".png", ".jpg", ".jpeg", ".bmp")
        available = []
        for root, _dirs, files in os.walk(img_dir):
            for f in sorted(files):
                if f.lower().endswith(exts):
                    rel = os.path.relpath(os.path.join(root, f), img_dir)
                    available.append(rel.replace(os.sep, "/"))
        if not available:
            st.warning("No sample images found in ./images/")
            return None, None
        # QHED-friendly samples first so the dropdown defaults to a great demo.
        available = sort_samples_by_quality(available)

        pre = st.session_state.pop("__preselected_sample", None)
        default_idx = available.index(pre) if pre in available else 0

        def _fmt(rel: str) -> str:
            tag = get_preset(rel).get("tag", "unknown")
            mark = {"great": "★ ", "good": "● ", "fair": "○ "}.get(tag, "")
            return f"{mark}{rel}"

        selected = st.selectbox(
            "Select sample image",
            available,
            index=default_idx,
            format_func=_fmt,
            key="__ed_sample_path",
        )
        tag = get_preset(selected).get("tag", "unknown")
        badge = _tag_badge(tag)
        if badge:
            st.markdown(f"**Selected:** `{selected}` {badge}", unsafe_allow_html=True)
        else:
            st.caption(f"Selected: {selected}")

        img_path = os.path.join(img_dir, selected.replace("/", os.sep))
        raw = np.array(Image.open(img_path))
        st.image(raw, use_container_width=False, width=300)
        return raw, selected

    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "bmp"])
    if uploaded:
        raw = np.array(Image.open(uploaded))
        st.image(raw, caption="Uploaded image", width=300)
        return raw, None
    return None, None


def _apply_preset_if_sample_changed(sample_path: str | None) -> bool:
    """If the selected sample has changed since last render, write its preset
    into session state so the parameter widgets pick it up on this run.

    Returns ``True`` when a preset was applied (i.e. the form was reset)."""
    last = st.session_state.get("__ed_last_sample")
    if sample_path == last:
        return False

    preset = get_preset(sample_path) if sample_path else DEFAULT_PRESET
    st.session_state["__ed_img_size_exp"] = preset["img_size_exp"]
    st.session_state["__ed_patch_qb"] = preset["patch_qb"]
    st.session_state["__ed_thr_ratio"] = float(preset["thr_ratio"])
    st.session_state["__ed_last_sample"] = sample_path
    return True


def render() -> None:
    st.title(t("ed.title"))
    st.markdown(t("ed.subtitle"))

    st.header(t("ed.section_select"))
    input_image, sample_path = _select_image()

    if input_image is None:
        st.info(t("ed.info_select_image"))
        st.stop()

    # When the user switches sample, refresh the parameter form with that
    # sample's tuned preset. The rerun guarantees the widgets below pick up
    # the new session-state values on their next render.
    if _apply_preset_if_sample_changed(sample_path):
        st.rerun()

    st.header(t("ed.section_params"))
    if sample_path and get_preset(sample_path).get("tag") != "unknown":
        st.info(f"{t('ed.preset_applied')} {t('ed.preset_hint')}")

    img_size_options = list(range(4, 9))
    img_size_default = st.session_state.get("__ed_img_size_exp", 6)
    patch_qb_default = st.session_state.get("__ed_patch_qb", 4)
    thr_default = float(st.session_state.get("__ed_thr_ratio", 0.7))

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        img_size_idx = img_size_options.index(img_size_default) if img_size_default in img_size_options else 2
        img_size_exp = st.selectbox(
            t("ed.param_image_size"),
            img_size_options,
            index=img_size_idx,
            format_func=lambda x: f"{2**x}x{2**x} ({2**(2*x):,} pixels)",
            key="__ed_img_size_exp",
        )
        img_size = 2 ** img_size_exp

    with col_p2:
        max_patch_qb = min(img_size_exp, 8)
        patch_qb_options = list(range(3, max_patch_qb + 1))
        if not patch_qb_options:
            st.error("Image too small for minimum patch size (8x8). Increase image size to at least 16x16.")
            st.stop()
        # If the preset value is out of range for the current image size,
        # fall back to the largest legal option.
        if patch_qb_default not in patch_qb_options:
            patch_qb_default = patch_qb_options[-1]
            st.session_state["__ed_patch_qb"] = patch_qb_default
        patch_qb = st.selectbox(
            t("ed.param_patch_qb"),
            patch_qb_options,
            index=patch_qb_options.index(patch_qb_default),
            format_func=lambda x: f"{x} qb/dim -> {2**x}x{2**x} patch ({2*x+1} total qubits)",
            key="__ed_patch_qb",
        )

    with col_p3:
        thr_ratio = st.slider(
            t("ed.param_threshold"), 0.1, 2.0, thr_default, 0.1,
            key="__ed_thr_ratio",
        )

    est_patch_size = 2 ** patch_qb
    est_total_qb = 2 * patch_qb + 1
    est_stride = max(est_patch_size - 2, 1)
    est_patches = int(np.ceil((img_size - 2) / est_stride)) ** 2 if img_size > est_patch_size else 1
    est_state_mb = (2 ** est_total_qb) * 16 / 1e6
    est_encode_gates = 2 ** (est_total_qb - 1)

    if patch_qb >= 7:
        st.error(
            f"Patch size {est_patch_size}x{est_patch_size} ({est_total_qb} qubits): "
            f"amplitude encoding synthesises ~{est_encode_gates:,} gates per patch. "
            f"Expect minutes per patch — try a smaller patch (k ≤ 6) first."
        )
    elif patch_qb >= 6:
        st.warning(
            f"Patch size {est_patch_size}x{est_patch_size} ({est_total_qb} qubits): "
            f"amplitude encoding synthesises ~{est_encode_gates:,} gates per patch "
            f"(statevector ≈ {est_state_mb:.1f} MB)."
        )
    if est_patches > 500:
        st.warning(f"~{est_patches} patches estimated. Consider larger patches or smaller image.")

    col_p4, col_p5 = st.columns(2)
    with col_p4:
        stride_mode = st.selectbox(
            t("ed.param_br_mode"),
            ["with_restoration", "without_restoration"],
            format_func=lambda x: t("ed.br_with") if x == "with_restoration" else t("ed.br_without"),
        )
    with col_p5:
        remove_noise = st.checkbox(t("ed.param_remove_noise"), value=False)

    gray = load_image_from_array(input_image, resize=(img_size, img_size))

    st.header(t("ed.section_results"))
    tabs = st.tabs([t("ed.tab_qhed"), t("ed.tab_classical"), t("ed.tab_compare")])

    # ---- TAB 1: QHED ----
    with tabs[0]:
        st.subheader("Quantum Hadamard Edge Detection")
        patch_size = 2 ** patch_qb
        total_data_qubits = 2 * patch_qb
        total_qubits = total_data_qubits + 1
        n_patches_no_overlap = (img_size // patch_size) ** 2
        br_stride = max(patch_size - 2, 1)
        n_patches_overlap = int(np.ceil((img_size - 2) / br_stride)) ** 2 if patch_size > 2 else img_size ** 2

        st.markdown(f"""
        **Configuration:**
        - Image: {img_size}x{img_size} pixels
        - Patch: {patch_size}x{patch_size} pixels
        - Qubits per patch: {total_qubits} ({total_data_qubits} data + 1 ancilla)
        - Patches (no overlap): ~{n_patches_no_overlap}
        - Patches (with overlap): ~{n_patches_overlap}
        - Mode: {'With' if stride_mode == 'with_restoration' else 'Without'} Boundary Restoration
        """)

        if st.button(t("ed.run_qhed"), type="primary", key="ed_run_qhed"):
            try:
                with st.spinner(""):
                    start = time.time()
                    result, n_patches, was_cached = run_qhed_cached(
                        gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                        stride_mode=stride_mode, patch_boundary_zero=True,
                    )
                    elapsed = time.time() - start
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

            badge = f" {t('ed.cached_badge')}" if was_cached else ""
            st.success(f"{t('ed.completed_in')} {elapsed:.2f}s | {n_patches} patches{badge}")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown(f"**{t('ed.original')}**")
                st.image(gray, clamp=True, use_container_width=True)
            with col_r2:
                st.markdown(f"**QHED ({'BR' if stride_mode == 'with_restoration' else 'No BR'})**")
                st.image(result.astype(float), clamp=True, use_container_width=True)

            st.session_state["qhed_result"] = result
            st.session_state["qhed_time"] = elapsed
            st.session_state["qhed_gray"] = gray

            st.download_button(
                t("ed.download_qhed"),
                img_to_bytes(result),
                file_name="qhed_result.png",
                mime="image/png",
            )

        if st.button(t("ed.compare_modes"), key="ed_compare_modes"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**{t('ed.original')}**")
                st.image(gray, clamp=True, use_container_width=True)
            try:
                with st.spinner(""):
                    start1 = time.time()
                    result_no_br, n1, _ = run_qhed_cached(
                        gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                        stride_mode="without_restoration", patch_boundary_zero=True,
                    )
                    time_no_br = time.time() - start1

                    start2 = time.time()
                    result_br, n2, _ = run_qhed_cached(
                        gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                        stride_mode="with_restoration", patch_boundary_zero=True,
                    )
                    time_br = time.time() - start2
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

            with col_b:
                st.markdown(f"**Without Restoration** ({n1} patches, {time_no_br:.2f}s)")
                st.image(result_no_br.astype(float), clamp=True, use_container_width=True)
            with col_c:
                st.markdown(f"**With Restoration** ({n2} patches, {time_br:.2f}s)")
                st.image(result_br.astype(float), clamp=True, use_container_width=True)

            fig_comp, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(gray, cmap="gray"); axes[0].set_title("Original"); axes[0].axis("off")
            axes[1].imshow(result_no_br, cmap="gray"); axes[1].set_title(f"QHED w/o BR ({n1} patches)"); axes[1].axis("off")
            axes[2].imshow(result_br, cmap="gray"); axes[2].set_title(f"QHED w/ BR ({n2} patches)"); axes[2].axis("off")
            plt.tight_layout()
            st.download_button(
                t("ed.download_comparison"),
                fig_to_bytes(fig_comp, dpi=200),
                file_name="qhed_br_comparison.png",
                mime="image/png",
            )
            plt.close(fig_comp)

    # ---- TAB 2: Classical ----
    with tabs[1]:
        st.subheader("Classical Edge Detection Methods")

        methods = st.multiselect(
            "Select methods to run",
            ["Sobel", "Prewitt", "Laplacian", "Canny"],
            default=["Sobel", "Canny"],
        )

        col_canny1, col_canny2 = st.columns(2)
        with col_canny1:
            canny_thr1 = st.slider("Canny threshold 1", 0, 255, 50) if "Canny" in methods else 50
        with col_canny2:
            canny_thr2 = st.slider("Canny threshold 2", 0, 255, 200) if "Canny" in methods else 200

        sobel_ksize = 3
        if "Sobel" in methods:
            sobel_ksize = st.selectbox("Sobel kernel size", [3, 5, 7], index=0)

        if st.button(t("ed.run_classical"), type="primary", key="ed_run_classical"):
            results_classical = {}
            timings = {}
            for m in methods:
                start = time.time()
                kw = {"remove_noise": remove_noise}
                if m == "Sobel":
                    kw["sobel_ksize"] = sobel_ksize
                if m == "Canny":
                    kw["canny_thr1"] = canny_thr1
                    kw["canny_thr2"] = canny_thr2
                results_classical[m] = run_classical_cached(gray, m, **kw)
                timings[m] = time.time() - start

            st.session_state["classical_results"] = results_classical
            st.session_state["classical_timings"] = timings

            n_methods = len(methods)
            cols = st.columns(min(n_methods + 1, 4))
            with cols[0]:
                st.markdown(f"**{t('ed.original')}**")
                st.image(gray, clamp=True, use_container_width=True)
            for idx, m in enumerate(methods):
                with cols[(idx + 1) % len(cols)]:
                    st.markdown(f"**{m}** ({timings[m]*1000:.1f} ms)")
                    st.image(results_classical[m], clamp=True, use_container_width=True)

            n_total = n_methods + 1
            fig_cl, axes = plt.subplots(1, n_total, figsize=(5 * n_total, 5))
            axes[0].imshow(gray, cmap="gray"); axes[0].set_title("Original"); axes[0].axis("off")
            for idx, m in enumerate(methods):
                axes[idx + 1].imshow(results_classical[m], cmap="gray")
                axes[idx + 1].set_title(f"{m} ({timings[m]*1000:.1f}ms)")
                axes[idx + 1].axis("off")
            plt.tight_layout()
            st.download_button(
                t("ed.download_classical"),
                fig_to_bytes(fig_cl, dpi=200),
                file_name="classical_edge_detection.png",
                mime="image/png",
            )
            plt.close(fig_cl)

    # ---- TAB 3: Comparison ----
    with tabs[2]:
        st.subheader("QHED vs Classical Edge Detection")
        st.markdown(
            "Run both QHED and classical methods first (in the other tabs), then "
            "come here to see the side-by-side comparison. Or click below to run "
            "everything at once."
        )

        if st.button(t("ed.run_full"), type="primary", key="ed_run_full"):
            all_results = {}
            all_times = {}
            try:
                with st.spinner(""):
                    start = time.time()
                    qhed_res, n_q, _ = run_qhed_cached(
                        gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                        stride_mode=stride_mode, patch_boundary_zero=True,
                    )
                    all_results["QHED"] = qhed_res.astype(float)
                    all_times["QHED"] = time.time() - start
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

            for name in ("Sobel", "Canny", "Prewitt", "Laplacian"):
                start = time.time()
                all_results[name] = run_classical_cached(gray, name, remove_noise=remove_noise)
                all_times[name] = time.time() - start

            n_total = len(all_results) + 1
            fig_all, axes = plt.subplots(1, n_total, figsize=(4 * n_total, 4))
            axes[0].imshow(gray, cmap="gray")
            axes[0].set_title("Original", fontsize=11)
            axes[0].axis("off")
            for idx, (name, result) in enumerate(all_results.items()):
                axes[idx + 1].imshow(result, cmap="gray")
                t_str = f"{all_times[name]*1000:.1f}ms" if all_times[name] < 1 else f"{all_times[name]:.2f}s"
                axes[idx + 1].set_title(f"{name}\n({t_str})", fontsize=11)
                axes[idx + 1].axis("off")
            plt.tight_layout()
            st.pyplot(fig_all)
            st.download_button(
                t("ed.download_full"),
                fig_to_bytes(fig_all, dpi=200),
                file_name="full_comparison.png",
                mime="image/png",
            )
            plt.close(fig_all)

            st.markdown("### Execution Time Comparison")
            timing_data = {
                k: f"{v*1000:.1f} ms" if v < 1 else f"{v:.2f} s"
                for k, v in all_times.items()
            }
            st.table(timing_data)

            st.session_state["qhed_result"] = qhed_res
            st.session_state["qhed_time"] = all_times["QHED"]
            st.session_state["qhed_gray"] = gray
