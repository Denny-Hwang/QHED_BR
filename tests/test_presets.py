"""Tests for the per-sample QHED preset table.

These don't run QHED — they just verify the table is well-formed and that
the helper functions behave the way the UI relies on.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.presets import (  # noqa: E402
    DEFAULT_PRESET,
    SAMPLE_PRESETS,
    TAG_ORDER,
    get_preset,
    sort_samples_by_quality,
)


REQUIRED_KEYS = {"img_size_exp", "patch_qb", "thr_ratio", "tag"}
VALID_TAGS = set(TAG_ORDER.keys())


def test_every_preset_is_well_formed():
    for rel, preset in SAMPLE_PRESETS.items():
        assert REQUIRED_KEYS.issubset(preset.keys()), f"{rel} missing keys"
        assert isinstance(preset["img_size_exp"], int)
        assert isinstance(preset["patch_qb"], int)
        assert isinstance(preset["thr_ratio"], (int, float))
        assert preset["tag"] in VALID_TAGS, f"{rel} bad tag {preset['tag']}"

        # Threshold ratio slider in app_pages/edge_detection.py is bounded
        # to [0.1, 2.0]; presets must fit.
        assert 0.1 <= preset["thr_ratio"] <= 2.0

        # Image size selectbox exposes 2^4 .. 2^8.
        assert 4 <= preset["img_size_exp"] <= 8

        # Patch qubits 3..8, and must fit in the chosen image size.
        assert 3 <= preset["patch_qb"] <= 8
        assert preset["patch_qb"] <= preset["img_size_exp"], (
            f"{rel}: patch {2**preset['patch_qb']} too big for image "
            f"{2**preset['img_size_exp']}"
        )


def test_get_preset_returns_default_for_unknown():
    assert get_preset("samples/does_not_exist.png") is DEFAULT_PRESET


def test_get_preset_normalises_backslashes():
    expected = SAMPLE_PRESETS["samples/checkerboard.png"]
    assert get_preset("samples\\checkerboard.png") is expected


def test_sort_samples_puts_great_first():
    samples = [
        "samples/eagle_cc0.png",          # fair
        "samples/checkerboard.png",       # great
        "samples/coins_cc0.png",          # good
    ]
    ordered = sort_samples_by_quality(samples)
    tags = [get_preset(s)["tag"] for s in ordered]
    assert tags == ["great", "good", "fair"]


def test_landing_card_samples_are_great():
    """The home page features three cards; each must have a 'great' preset
    so the landing demo is impressive."""
    landing = [
        "samples/checkerboard.png",
        "samples/concentric_circles.png",
        "samples/geometric_shapes.png",
    ]
    for rel in landing:
        assert rel in SAMPLE_PRESETS, f"{rel} missing"
        assert SAMPLE_PRESETS[rel]["tag"] == "great"


def test_cat_image_is_removed():
    """The cat image was unsuitable for QHED and was deliberately removed —
    if it sneaks back in, the preset table should not regress to include it.
    """
    assert "samples/cat_cc0.png" not in SAMPLE_PRESETS
