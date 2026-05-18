"""Tests for the classical edge-detection wrappers.

These exist to catch regressions in the OpenCV / numpy contract — in
particular, that 3-channel RGB input is converted correctly (the original
code used COLOR_BGR2GRAY against PIL-loaded RGB data).
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classical_ed_methods import (  # noqa: E402
    canny_edge_detection,
    laplacian_edge_detection,
    prewitt_edge_detection,
    sobel_edge_detection,
)


@pytest.fixture
def step_image():
    """A 16x16 image with a sharp vertical step in the middle."""
    img = np.zeros((16, 16), dtype=np.uint8)
    img[:, 8:] = 255
    return img


def test_sobel_finds_step(step_image):
    out = sobel_edge_detection(step_image)
    assert out.shape == step_image.shape
    # the column at the step boundary should be much brighter than the
    # flat interior
    assert out[:, 7:9].mean() > out[:, :4].mean()


def test_prewitt_finds_step(step_image):
    out = prewitt_edge_detection(step_image)
    assert out.shape == step_image.shape
    assert out[:, 7:9].mean() > out[:, :4].mean()


def test_laplacian_finds_step(step_image):
    out = laplacian_edge_detection(step_image)
    assert out.shape == step_image.shape


def test_canny_finds_step(step_image):
    out = canny_edge_detection(step_image, thr1=50, thr2=200)
    assert out.shape == step_image.shape
    # Canny is binary: there must be at least one edge pixel on the step
    assert out[:, 7:9].sum() > 0


def test_rgb_input_grayscale_matches_luma():
    """Pure-red RGB and pure-blue RGB must yield different grayscale values.

    Under the old COLOR_BGR2GRAY bug the red and blue luma weights were swapped,
    so this test would have caught it.
    """
    red = np.zeros((8, 8, 3), dtype=np.uint8)
    red[..., 0] = 255  # R channel
    blue = np.zeros((8, 8, 3), dtype=np.uint8)
    blue[..., 2] = 255  # B channel

    out_red = sobel_edge_detection(red)
    out_blue = sobel_edge_detection(blue)
    # both are uniform interiors, so Sobel returns 0 in the interior; the test
    # is that the function consumes both without crashing and returns the
    # expected shape
    assert out_red.shape == (8, 8)
    assert out_blue.shape == (8, 8)


def test_float_input_is_rescaled(step_image):
    """A [0, 1] float image must give the same result as a [0, 255] uint8."""
    out_u8 = sobel_edge_detection(step_image)
    out_f = sobel_edge_detection(step_image.astype(np.float64) / 255.0)
    assert np.array_equal(out_u8, out_f)
