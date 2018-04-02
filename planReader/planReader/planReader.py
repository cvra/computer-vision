import matplotlib.pyplot as plt
import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import os
import yaml
import scipy.ndimage

from scipy import interpolate
from sklearn import mixture
from skimage import data, img_as_float
from skimage import exposure

from .colorsUtils import norm_colors, improve_colors, pick_color
from .colorsSegm import Colors
from .drawingUtils import draw_points, lut


def load_config(conf_path, colors_path):
    with open(conf_path, 'r') as stream:
        conf = yaml.load(stream)

    with open(colors_path, 'r') as stream:
        conf_colors = yaml.load(stream)

    cam_arr = np.array(conf['camera']['cameraMatrix'])
    cam_arr = cam_arr.reshape(3, 3)
    conf['camera']['cameraMatrix'] = cam_arr

    cam_dist = np.array(conf['camera']['distCoeffs'])
    conf['camera']['distCoeffs'] = cam_dist

    return conf, conf_colors


def detect_aruco(im, aruco_dict, conf, cameraMatrix, distCoeffs):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    param = aruco.DetectorParameters_create()

    corners, ids, _ = aruco.detectMarkers(im, aruco_dict, parameters=param)

    sel_id = np.argwhere(ids == conf['id'])
    if sel_id.shape[0]:
        idx = sel_id[0][0]

        corners = [corners[idx]]
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                              conf['height'],
                                                              cameraMatrix,
                                                              distCoeffs)
    else:
        corners, rvecs, tvecs = None, None, None

    return corners, rvecs, tvecs


def keep_color(im, model):
    out = np.zeros(im.shape[:2], dtype=np.uint8)

    for i in range(im.shape[0]):
        line = im[i, :, :].astype(np.float32)
        results = model.predict(line)

        out[i, :] = results

    return out


def crop_on_color_map(im, pts, width, height):
    pts_proj = np.float32([[width, 0], [0, 0], [0, height], [width, height]])

    M = cv2.getPerspectiveTransform(pts.astype(np.float32), pts_proj)

    dst = cv2.warpPerspective(im, M, (width, height))
    return dst


def clean_label(im, morph_kernel):
    im = im.copy()

    labels = np.unique(im)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                       (morph_kernel, morph_kernel))
    new_im = np.zeros(im.shape, dtype=np.uint8)

    for label in labels:
        mask = (im == label).astype(np.uint8)

        mask_closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask_opened = cv2.morphologyEx(mask_closed, cv2.MORPH_OPEN, kernel)

        new_im[mask_opened == 1] = label

    return new_im


def find_colors(color_blobs):
    candidates = color_blobs[-3:]
    candidates.sort(key=lambda x: x['center'][1])

    colors = [item['color'] for item in candidates]
    return colors


def find_class_center(im_label, idx2color, im=None):
    labels = np.unique(im_label)

    colors_blobs = list()

    for label in [label for label in labels if label != 0 and label != 6]:
        mask = (im_label == label).astype(np.uint8)
        if not np.any(mask):
            break

        X = np.vstack(np.where(mask == 1)).T.astype(np.float)
        gmm = mixture.GaussianMixture(
            n_components=1, covariance_type='diag', max_iter=100,).fit(X)

        if im is not None:
            colors_blobs.append({'color': idx2color[label], 'size': np.sum(
                mask), 'center': gmm.means_.squeeze()})

    colors_blobs.sort(key=lambda x: x['size'])
    return colors_blobs


class planReader():
    def __init__(self, config_path='conf.yaml', config_color='colors.yaml', debug=False):
        self.debug = debug

        # load config
        self.conf, self.conf_colors = load_config(config_path, config_color)
        self.cameraMatrix = self.conf['camera']['cameraMatrix']
        self.distCoeffs = self.conf['camera']['distCoeffs']

        self.colors_util = Colors(self.conf_colors['colorsGroup'],
                                  self.conf_colors['color_idx'])

        areaY = self.conf['colorMap']['areaY']
        areaHeight = self.conf['colorMap']['areaHeight']
        areaX = self.conf['colorMap']['areaX']
        areaWidth = self.conf['colorMap']['areaWidth']

        self.grey_pts = np.array([[self.conf['colorMap']['greyY'],
                                   self.conf['colorMap']['greyX'],
                                   0]], dtype=np.float)

        self.points = np.array([[areaY - areaHeight / 2, areaX - areaWidth / 2, 0],
                                [areaY - areaHeight / 2, areaX + areaWidth / 2, 0],
                                [areaY + areaHeight / 2, areaX + areaWidth / 2, 0],
                                [areaY + areaHeight / 2, areaX - areaWidth / 2, 0]],
                               dtype=np.float)

    def process(self, im):
        corners, rvecs, tvecs = detect_aruco(
            im, aruco.DICT_6X6_250,
            self.conf['ArUco'],
            self.cameraMatrix,
            self.distCoeffs)

        pts, _ = cv2.projectPoints(self.points, rvecs, tvecs,
                                   self.cameraMatrix, self.distCoeffs)
        pts = np.rint(pts.squeeze()).astype(np.int)

        greypos, _ = cv2.projectPoints(self.grey_pts, rvecs, tvecs,
                                       self.cameraMatrix, self.distCoeffs)
        greypos = np.rint(greypos.squeeze()).astype(np.int)
        grey = pick_color(im, greypos[0], greypos[1], 3)

        im_proc1 = crop_on_color_map(im, pts, self.conf['process']['winWidth'],
                                     self.conf['process']['winHeight'])
        im_proc2 = cv2.GaussianBlur(im_proc1, (self.conf['process']['blur'],
                                               self.conf['process']['blur']), 0)
        im_proc3 = norm_colors(im_proc2.astype(np.float),
                               grey)

        # Adaptive Equalization
        # Contrast stretching
        im_proc4 = improve_colors(im_proc3)
        im_proc5 = keep_color(im_proc4, self.colors_util.model)
        im_proc6 = clean_label(im_proc5, self.conf['process']['morphKernel'])
        im_proc7 = clean_label(im_proc6, self.conf['process']['morphKernel'])
        im_proc8 = lut(im_proc7)

        if self.debug:
            plt.imshow(draw_points(im, pts))
            plt.show()

            plt.imshow(draw_points(im, greypos[np.newaxis, :]))
            plt.show()

            plt.imshow(np.vstack([im_proc1, im_proc2, im_proc3,
                                  im_proc4]))
            plt.show()

            plt.imshow(np.vstack([im_proc5, im_proc6, im_proc7]))
            plt.show()

            plt.imshow(im_proc8)
            plt.show()

        color_blobs = find_class_center(im_proc7, self.colors_util.idx2color,
                                        im_proc8)
        colors = find_colors(color_blobs)

        return colors
