import cv2
import numpy as np


def resize(img, scale):
    return cv2.resize(img, (
        int(img.shape[1] * scale) or 1,
        int(img.shape[0] * scale) or 1,
    ), interpolation=cv2.INTER_AREA)


def paste(img1, img2, coord):
    cy = abs(coord[1]) if coord[1] < 0 else 0
    cx = abs(coord[0]) if coord[0] < 0 else 0

    if cx or cy:
        img2 = img2[cy:img2.shape[0], cx:img2.shape[1], :]
        coord = (max(coord[0], 0), max(coord[1], 0))

    y1, y2 = coord[1], coord[1] + img2.shape[0]
    x1, x2 = coord[0], coord[0] + img2.shape[1]

    cy = y2 - img1.shape[0] if y2 > img1.shape[0] else 0
    cx = x2 - img1.shape[1] if x2 > img1.shape[1] else 0

    if cx or cy:
        img2 = img2[0:img2.shape[0] - cy, 0:img2.shape[1] - cx, :]

    alpha_s = img2[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    img1 = img1.copy()
    for c in range(0, 3):
        img1[y1:y2, x1:x2, c] = (alpha_s * img2[:, :, c] +
                                 alpha_l * img1[y1:y2, x1:x2, c])

    return img1


def maximum(img1, img2, coord):
    # x, y = coord
    # bh, bw = img1.shape[:2]
    # fh, fw = img2.shape[:2]
    #
    # ow_xm = x + fw
    # ow_xp = bw + fw - 1
    #
    # if not (0 < ow_xm < ow_xp and 0 < y + fh < bh + fh - 1):
    #     return
    #
    # if ow_xm < fw:
    #     img2 = img2[ow_xm:, :]
    #
    # print(ow_xp, coord)

    x, y = coord
    if x < 0:
        img2 = img2[:, -x:]
        x = 0
    if x + img2.shape[1] > img1.shape[1]:
        img2 = img2[:, :img1.shape[1] - x]
    if y < 0:
        img2 = img2[-y:, :]
        y = 0
    if y + img2.shape[0] > img1.shape[0]:
        img2 = img2[:img1.shape[0] - y, :]

    h, w = img2.shape[:2]
    img1[y:y + h, x:x + w] = np.maximum(img1[y:y + h, x:x + w], img2)


def crop(img, x, y, w, h):
    return img[y:y + h, x: x + w]
