"""Basic utility functions for image processing and quantum encoding."""

import cv2
import numpy as np
from PIL import Image


def load_image(image_path, resize=(256, 256)):
    """Load an image, convert to grayscale, resize, and normalize to [0, 1]."""
    image_raw = np.array(Image.open(image_path))
    if len(image_raw.shape) == 3:
        image_raw = cv2.cvtColor(image_raw, cv2.COLOR_RGB2GRAY)
    image_raw = cv2.resize(image_raw, dsize=resize, interpolation=cv2.INTER_AREA)
    image = image_raw.astype(np.float64) / 255.0
    return image


def load_image_from_array(image_array, resize=(256, 256)):
    """Load image from numpy array (e.g. uploaded file), convert to grayscale, resize, normalize."""
    if len(image_array.shape) == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    image_resized = cv2.resize(image_array, dsize=resize, interpolation=cv2.INTER_AREA)
    image = image_resized.astype(np.float64) / 255.0
    return image


def boundary_zero(img):
    """Zero out the outermost pixels of an image to prevent boundary artifacts."""
    result_img = img.copy()
    row, col = img.shape[0], img.shape[1]
    result_img[:, [0, col - 1]] = 0
    result_img[[0, row - 1], :] = 0
    return result_img


def amplitude_encode(img_data):
    """Normalize image data for quantum amplitude encoding.

    Returns a 1D array whose squared values sum to 1,
    suitable for initializing a quantum state vector.
    """
    if len(np.unique(img_data)) == 1:
        return None

    flat = img_data.flatten().astype(np.float64)
    norm = np.linalg.norm(flat)
    if norm == 0:
        return None
    return flat / norm
