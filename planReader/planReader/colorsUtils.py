import cv2
import numpy as np
from skimage import exposure
from scipy import interpolate


def pick_color(im, x, y, window_size):
    x1 = x - window_size
    x2 = x + window_size
    y1 = y - window_size
    y2 = y + window_size

    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    if x2 > im.shape[1] - 1:
        x2 = im.shape[1] - 1
    if y2 > im.shape[0] - 1:
        y2 = im.shape[0] - 1

    return np.mean(im[y1:y2, x1:x2], axis=(0, 1))


def improve_colors(im, x, y, window_size):
    im = im.copy()

    p2, p98 = np.percentile(im, (2, 98))
    im = exposure.rescale_intensity(
        im, in_range=(p2, p98))
    im = norm_colors(im.astype(np.float), x, y, window_size)

    im_hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HLS).astype(np.float)
    im_hsv[:, :, 2] *= 130 / np.mean(im_hsv[:, :, 2])
    im_hsv[im_hsv > 255] = 255
    im = cv2.cvtColor(im_hsv.astype(np.uint8), cv2.COLOR_HLS2RGB)

    return im


def norm_colors(im, x, y, window_size):
    im = im.copy()

    grey = pick_color(im, x, y, window_size)

    curve_r = _color_define_curve(np.mean(grey), grey[0])
    curve_g = _color_define_curve(np.mean(grey), grey[1])
    curve_b = _color_define_curve(np.mean(grey), grey[2])

    im[:, :, 0] *= _color_corr_factor(im[:, :, 0], curve_r)
    im[:, :, 1] *= _color_corr_factor(im[:, :, 1], curve_g)
    im[:, :, 2] *= _color_corr_factor(im[:, :, 2], curve_b)

    grey = pick_color(im, x, y, window_size)
    mean_grey = 200  # np.mean(grey)

    im /= grey
    im *= mean_grey

    im[im > 255] = 255
    im = np.rint(im).astype(np.uint8)

    return im


def _color_define_curve(mean, comp):
    x = np.array([0, comp / 255 - 1e-13, 1])
    y = np.array([1, mean / comp, 1])
    f = interpolate.interp1d(x, y, kind='quadratic')
    return f


def _color_corr_factor(val, f):
    return f(val / 255)
