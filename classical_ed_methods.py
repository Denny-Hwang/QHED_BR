"""Classical edge detection methods for comparison with QHED."""

import cv2
import numpy as np


def _prepare_gray(img, remove_noise=False):
    """Convert to grayscale uint8 and optionally apply Gaussian blur."""
    if img.dtype == np.float64 or img.dtype == np.float32:
        img_u8 = (img * 255).astype(np.uint8)
    else:
        img_u8 = img.copy()

    if len(img_u8.shape) == 3:
        img_gray = cv2.cvtColor(img_u8, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img_u8

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    return img_gray


def sobel_edge_detection(img, kernel_size=3, remove_noise=False):
    img_gray = _prepare_gray(img, remove_noise)
    sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=kernel_size)
    return cv2.addWeighted(cv2.convertScaleAbs(sobel_x), 1,
                           cv2.convertScaleAbs(sobel_y), 1, 0)


def prewitt_edge_detection(img, remove_noise=False):
    img_gray = _prepare_gray(img, remove_noise)
    kx = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
    ky = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    px = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, kx))
    py = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, ky))
    return cv2.addWeighted(px, 1, py, 1, 0)


def laplacian_edge_detection(img, remove_noise=False):
    img_gray = _prepare_gray(img, remove_noise)
    lap = cv2.Laplacian(img_gray, cv2.CV_64F)
    return cv2.convertScaleAbs(lap)


def canny_edge_detection(img, thr1=50, thr2=200, remove_noise=False):
    img_gray = _prepare_gray(img, remove_noise)
    return cv2.Canny(img_gray, thr1, thr2)
