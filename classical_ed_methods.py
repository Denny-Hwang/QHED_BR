import cv2
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import style
style.use('bmh')

def sobel_edge_detection(img, kernel_size=3, remove_noise=False):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    img_sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
    img_sobel_x = cv2.convertScaleAbs(img_sobel_x)

    img_sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=kernel_size)
    img_sobel_y = cv2.convertScaleAbs(img_sobel_y)

    img_sobel = cv2.addWeighted(img_sobel_x, 1, img_sobel_y, 1, 0)

    return img_sobel


def sobel_edge_detection2(img, remove_noise=False):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    sobel_x = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    sobel_y = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])

    sobel_x = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, sobel_x))
    sobel_y = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, sobel_y))

    sobel = cv2.addWeighted(sobel_x, 1, sobel_y, 1, 0)

    return sobel


def prewitt_edge_detection(img, remove_noise=False):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    prewitt_x = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
    prewitt_y = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])

    prewitt_x = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, prewitt_x))
    prewitt_y = cv2.convertScaleAbs(cv2.filter2D(img_gray, -1, prewitt_y))

    prewitt = cv2.addWeighted(prewitt_x, 1, prewitt_y, 1, 0)

    return prewitt


def laplacian_edge_detection(img, depth=cv2.CV_64F, remove_noise=False):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    laplacian_edge = cv2.Laplacian(img_gray, depth)

    return laplacian_edge


def canny_edge_detection(img, thr1=50, thr2=200, remove_noise=False):
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img

    if remove_noise:
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)

    canny_edge = cv2.Canny(img_gray, thr1, thr2)

    return canny_edge


