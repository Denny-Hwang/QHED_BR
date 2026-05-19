"""Per-sample QHED parameter presets.

Each sample in ``images/`` has an empirically tuned set of parameters that
produces a clean, visually clear edge map. Parameters were chosen by running
``edge_detection_stride`` over all candidates at 64x64 with patch_qb=4 and
picking thresholds that land in the "GOOD" band (edge_fraction roughly
0.05–0.22 — enough structure to be informative, sparse enough to be readable).

Each entry also carries a quality tag that the UI uses to sort and label
samples:

- ``great`` — sharp / binary edges, picture-perfect QHED demonstration
- ``good``  — real-world photo with mostly clean edges
- ``fair``  — photographic texture with smoother gradients; QHED still
  produces an output but the result is busier and less striking
"""

from __future__ import annotations

# Path is relative to the ``images/`` directory and matches what
# ``os.relpath`` produces during sample discovery (forward slashes on every
# platform — Streamlit / Streamlit Cloud always use POSIX paths).
SAMPLE_PRESETS: dict[str, dict] = {
    # ---- Synthetic / man-made: QHED's sweet spot ------------------------
    "samples/checkerboard.png":         {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.2, "tag": "great"},
    "samples/concentric_circles.png":   {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.8, "tag": "great"},
    "samples/geometric_shapes.png":     {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.6, "tag": "great"},
    "samples/maze.png":                 {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.4, "tag": "great"},
    "samples/star_pattern.png":         {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.0, "tag": "great"},
    "samples/text_blocks.png":          {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.3, "tag": "great"},
    "samples/circuit_board.png":        {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.4, "tag": "great"},
    "samples/step_gradients.png":       {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.5, "tag": "great"},
    "samples/cityscape.png":            {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.0, "tag": "great"},
    "samples/house_scene.png":          {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.6, "tag": "great"},

    # ---- Real-world photos with clean boundaries ------------------------
    "samples/coins_cc0.png":            {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.5, "tag": "good"},
    "samples/fingerprint.png":          {"img_size_exp": 6, "patch_qb": 3, "thr_ratio": 1.5, "tag": "good"},
    "samples/satellite_coastline.png":  {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "good"},
    "samples/medical_crosssection.png": {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "good"},
    "samples/horse_cc0.png":            {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "good"},
    "samples/photographer.png":         {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.6, "tag": "good"},
    "samples/brick_cc0.png":            {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.5, "tag": "good"},
    "license_plates/car_num1.jpg":      {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "good"},
    "license_plates/car_num2.jpg":      {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "good"},

    # ---- Photographic textures with smoother gradients ------------------
    # QHED still runs but the output is denser and harder to read.
    "samples/cell_cc0.png":             {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 1.2, "tag": "fair"},
    "samples/astronaut_cc0.png":        {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "fair"},
    "samples/camera_cc0.png":           {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "fair"},
    "samples/coffee_cc0.png":           {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "fair"},
    "samples/eagle_cc0.png":            {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "fair"},
}

# Display order: sharp-edge demos first, photos last.
TAG_ORDER = {"great": 0, "good": 1, "fair": 2, "unknown": 3}

# Default values for samples that aren't in the preset table (or for an
# uploaded image).
DEFAULT_PRESET = {"img_size_exp": 6, "patch_qb": 4, "thr_ratio": 0.7, "tag": "unknown"}


def get_preset(rel_path: str) -> dict:
    """Return the preset for ``rel_path`` (e.g. ``samples/checkerboard.png``).

    Falls back to :data:`DEFAULT_PRESET` for unknown paths.
    """
    rel_norm = rel_path.replace("\\", "/")
    return SAMPLE_PRESETS.get(rel_norm, DEFAULT_PRESET)


def sort_samples_by_quality(samples: list[str]) -> list[str]:
    """Sort sample relative paths with QHED-friendly ones first.

    Within each quality bucket, ties break by basename for stable order.
    """
    def key(s: str) -> tuple:
        preset = get_preset(s)
        return (TAG_ORDER.get(preset.get("tag", "unknown"), 9), s)
    return sorted(samples, key=key)
