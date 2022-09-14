## Basic functions

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib import style

style.use('bmh')


def load_img_check(image_path, resize=(256, 256)):
    # Load the image from filesystem
    image_raw = np.array(Image.open(image_path))
    img_channel = len(image_raw.shape)
    if img_channel == 3:  # get grayscale image
        image_raw = image_raw[:, :, 0]

    print('Raw Image info:', image_raw.shape)
    print('Raw Image datatype:', image_raw.dtype)

    image_raw = cv2.resize(image_raw, dsize=resize, interpolation=cv2.INTER_AREA)

    # Convert the RBG component of the image to B&W image, as a numpy (uint8) array
    image = []
    for i in range(image_raw.shape[0]):
        image.append([])
        for j in range(image_raw.shape[1]):
            image[i].append(image_raw[i][j] / 255)

    image = np.array(image)

    # Display the image
    plt.title('Big Image')
    plt.xticks(range(0, image.shape[0] + 1, 32))
    plt.yticks(range(0, image.shape[1] + 1, 32))
    plt.imshow(image, extent=[0, image.shape[0], image.shape[1], 0], cmap='gray')
    plt.show()

    return image


def plot_image(image, title: str, cmap='gray'):
    plt.title(title)
    plt.xticks(range(image.shape[0] + 1))
    plt.yticks(range(image.shape[1] + 1))
    plt.imshow(image, extent=[0, image.shape[0], image.shape[1], 0], cmap=cmap)
    plt.show()


def boundary_zero(img):
    row, col = img.shape[0], img.shape[1]

    result_img = img.copy()

    result_img[:, [0, col - 1]] = 0
    result_img[[0, row - 1], :] = 0

    return result_img


def amplitude_encode(img_data):
    image_validity_check = len(np.unique(img_data))

    # Calculate the RMS value
    rms = np.sqrt(np.sum(np.sum(img_data ** 2, axis=1)))

    image_norm = []

    if image_validity_check == 1:
        return 0

    else:
        for arr in img_data:
            for ele in arr:
                image_norm.append(ele / rms)

    # Return the normalized image as a numpy array
    return np.array(image_norm)

