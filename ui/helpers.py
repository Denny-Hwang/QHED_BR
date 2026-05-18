"""Shared helpers: figure conversion, image hashing, cached QHED / classical
edge detection.

The caching layer turns repeated parameter tweaks into instant lookups —
the QHED run for a given (image, patch_qb, threshold, mode) is computed
exactly once per session.
"""

from __future__ import annotations

import hashlib
import io

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# ---------------------------------------------------------------------------
# Figure / image serialisation
# ---------------------------------------------------------------------------

def fig_to_bytes(fig, dpi: int = 150) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()


def img_to_bytes(img_array, cmap: str = "gray") -> bytes:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img_array, cmap=cmap)
    ax.axis("off")
    data = fig_to_bytes(fig)
    plt.close(fig)
    return data


# ---------------------------------------------------------------------------
# Image fingerprinting (for cache keys)
# ---------------------------------------------------------------------------

def image_hash(img: np.ndarray) -> str:
    """Stable, short fingerprint of an image array for use as a cache key."""
    arr = np.ascontiguousarray(img)
    h = hashlib.sha1()
    h.update(str(arr.shape).encode())
    h.update(str(arr.dtype).encode())
    h.update(arr.tobytes())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Cached QHED / classical edge detection
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False, max_entries=32)
def cached_qhed_stride(
    img_hash: str,
    img_bytes: bytes,
    img_shape: tuple,
    img_dtype: str,
    width_qb: int,
    thr_ratio: float,
    stride_mode: str,
    patch_boundary_zero: bool,
):
    """Run ``edge_detection_stride`` and cache the result.

    The cache key is the image fingerprint plus the explicit parameters, so
    re-runs with the same configuration return instantly. The image is passed
    as bytes + shape + dtype to make Streamlit's hashing cheap and stable.

    Returns ``(result_img, n_patches)``.
    """
    from qhed import edge_detection_stride

    img = np.frombuffer(img_bytes, dtype=np.dtype(img_dtype)).reshape(img_shape)
    return edge_detection_stride(
        img,
        width_qb=width_qb,
        thr_ratio=thr_ratio,
        stride_mode=stride_mode,
        patch_boundary_zero=patch_boundary_zero,
    )


def run_qhed_cached(img: np.ndarray, width_qb: int, thr_ratio: float,
                    stride_mode: str = "with_restoration",
                    patch_boundary_zero: bool = True):
    """User-friendly wrapper around :func:`cached_qhed_stride`.

    Returns ``(result_img, n_patches, was_cached)``. The third element tells
    the UI whether the lookup hit the cache (useful for a "cached" badge).
    """
    img = np.ascontiguousarray(img)
    h = image_hash(img)
    key = ("qhed", h, width_qb, thr_ratio, stride_mode, patch_boundary_zero)
    seen = st.session_state.setdefault("__qhed_seen_keys", set())
    was_cached = key in seen
    result, n_patches = cached_qhed_stride(
        h, img.tobytes(), img.shape, str(img.dtype),
        width_qb, thr_ratio, stride_mode, patch_boundary_zero,
    )
    seen.add(key)
    return result, n_patches, was_cached


@st.cache_data(show_spinner=False, max_entries=32)
def cached_classical(
    img_hash: str,
    img_bytes: bytes,
    img_shape: tuple,
    img_dtype: str,
    method: str,
    remove_noise: bool,
    canny_thr1: int = 50,
    canny_thr2: int = 200,
    sobel_ksize: int = 3,
):
    """Cached wrapper for the classical edge-detection methods."""
    from classical_ed_methods import (
        canny_edge_detection,
        laplacian_edge_detection,
        prewitt_edge_detection,
        sobel_edge_detection,
    )

    img = np.frombuffer(img_bytes, dtype=np.dtype(img_dtype)).reshape(img_shape)
    img_u8 = (img * 255).astype(np.uint8) if img.dtype != np.uint8 else img

    if method == "Sobel":
        return sobel_edge_detection(img_u8, kernel_size=sobel_ksize, remove_noise=remove_noise)
    if method == "Prewitt":
        return prewitt_edge_detection(img_u8, remove_noise=remove_noise)
    if method == "Laplacian":
        return laplacian_edge_detection(img_u8, remove_noise=remove_noise)
    if method == "Canny":
        return canny_edge_detection(img_u8, thr1=canny_thr1, thr2=canny_thr2, remove_noise=remove_noise)
    raise ValueError(f"Unknown method: {method}")


def run_classical_cached(img: np.ndarray, method: str, remove_noise: bool = False,
                          **kwargs):
    img = np.ascontiguousarray(img)
    h = image_hash(img)
    return cached_classical(
        h, img.tobytes(), img.shape, str(img.dtype),
        method, remove_noise, **kwargs,
    )
