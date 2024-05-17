import numpy as np


def screen(img1, img2):
    res = np.zeros(img1.shape)

    a = img1.astype(float) / 255
    b = img2.astype(float) / 255

    for channel in range(3):
        res[:, :, channel] = 1 - (1 - a[:, :, channel]) * (1 - b[:, :, channel])

    return (res * 255).astype(np.uint8)


def overlay(img1, img2):
    res = np.zeros(img1.shape)

    a = img1.astype(float) / 255
    b = img2.astype(float) / 255

    mask = a >= 0.5

    res[~mask] = (2 * a * b)[~mask]
    res[mask] = (1 - 2 * (1 - a) * (1 - b))[mask]

    return (res * 255).astype(np.uint8)
