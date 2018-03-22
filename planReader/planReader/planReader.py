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

from .colorsSegm import Colors


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


def readImage(path):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    im = cv2.resize(im, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im


def detectAruco(im, aruco_dict, conf, cameraMatrix, distCoeffs):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    param = aruco.DetectorParameters_create()

    corners, ids, _ = aruco.detectMarkers(im, aruco_dict, parameters=param)

    # This is ugly
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


def drawAruco(im, corners, rvecs, tvecs, cameraMatrix, distCoeffs):
    im = aruco.drawDetectedMarkers(im.copy(), corners)
    aruco.drawAxis(im, cameraMatrix, distCoeffs,
                   rvecs[0, ...], tvecs[0, ...], 20)
    return im


def keepColor(im, model):
    out = np.zeros(im.shape[:2], dtype=np.uint8)

    for i in range(im.shape[0]):
        line = im[i, :, :].astype(np.float32)
        results = model.predict(line)

        out[i, :] = results

    return out


def cropOnColorMap(im, pts, width, height):
    pts_proj = np.float32([[width, 0], [0, 0], [0, height], [width, height]])

    M = cv2.getPerspectiveTransform(pts.astype(np.float32), pts_proj)

    dst = cv2.warpPerspective(im, M, (width, height))
    return dst


def color_define_curve(mean, comp):
    x = np.array([0, comp / 255, 1])
    y = np.array([1, mean / comp, 1])
    f = interpolate.interp1d(x, y, kind='quadratic')
    return f


def color_corr_factor(val, f):
    return f(val / 255)


def normColor(im, mean_grey):
    im = im.copy()

    grey = np.mean(im[:, :4, :], axis=(0, 1))

    curve_r = color_define_curve(np.mean(grey), grey[0])
    curve_g = color_define_curve(np.mean(grey), grey[1])
    curve_b = color_define_curve(np.mean(grey), grey[2])

    im[:, :, 0] *= color_corr_factor(im[:, :, 0], curve_r)
    im[:, :, 1] *= color_corr_factor(im[:, :, 1], curve_g)
    im[:, :, 2] *= color_corr_factor(im[:, :, 2], curve_b)

    grey = np.mean(im[:, :4, :], axis=(0, 1))

    mean_grey = 200  # np.mean(grey)

    im /= grey
    im *= mean_grey

    im[im > 255] = 255
    im = np.rint(im).astype(np.uint8)

    return im


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

    for label in [label for label in labels if label != 0 and label != 7]:
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


def lut(im):
    im = np.repeat(im[:, :, np.newaxis], 3, axis=2)

    lut = np.zeros((256, 1, 3), dtype=np.uint8)
    lut[0, 0, :] = np.array([255, 255, 255], dtype=np.uint8)  # other
    lut[1, 0, :] = np.array([255, 0, 0], dtype=np.uint8)      # red
    lut[2, 0, :] = np.array([0, 0, 255], dtype=np.uint8)      # blue
    lut[3, 0, :] = np.array([0, 255, 0], dtype=np.uint8)      # green
    lut[4, 0, :] = np.array([255, 255, 0], dtype=np.uint8)    # yellow
    lut[5, 0, :] = np.array([255, 127, 0], dtype=np.uint8)    # orange
    lut[6, 0, :] = np.array([0, 0, 0], dtype=np.uint8)        # black
    lut[7, 0, :] = np.array([255, 255, 255], dtype=np.uint8)  # white

    cv2.LUT(im, lut, im)
    return im


def improve_colors(im, mean_grey):
    im = im.copy()

    p2, p98 = np.percentile(im, (2, 98))
    im = exposure.rescale_intensity(
        im, in_range=(p2, p98))
    im = normColor(im.astype(np.float), mean_grey)

    im_hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HLS).astype(np.float)
    im_hsv[:, :, 2] *= 130 / np.mean(im_hsv[:, :, 2])
    im_hsv[im_hsv > 255] = 255
    im = cv2.cvtColor(im_hsv.astype(np.uint8), cv2.COLOR_HLS2RGB)

    return im


class planReader():
    def __init__(self, config_path='conf.yaml', config_color='colors.yaml'):
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

        self.points = np.array([[areaY + areaHeight / 2, areaX + areaWidth / 2, 0],
                                [areaY + areaHeight / 2, areaX - areaWidth / 2, 0],
                                [areaY - areaHeight / 2, areaX - areaWidth / 2, 0],
                                [areaY - areaHeight / 2, areaX + areaWidth / 2, 0]])

    def process(self, im):
        corners, rvecs, tvecs = detectAruco(
            im, aruco.DICT_6X6_250,
            self.conf['ArUco'],
            self.cameraMatrix,
            self.distCoeffs)

        pts, _ = cv2.projectPoints(self.points, rvecs, tvecs,
                                   self.cameraMatrix, self.distCoeffs)
        pts = np.rint(pts.squeeze()).astype(np.int)

        im_proc1 = cropOnColorMap(im, pts, self.conf['process']['winWidth'],
                                  self.conf['process']['winHeight'])
        im_proc2 = cv2.GaussianBlur(im_proc1, (self.conf['process']['blur'],
                                               self.conf['process']['blur']),0)

        im_proc3 = normColor(im_proc2.astype(np.float),
                             self.conf['process']['meanGrey'])

        # Adaptive Equalization
        # Contrast stretching
        im_proc4 = improve_colors(im_proc3, self.conf['process']['meanGrey'])

        im_proc5 = keepColor(im_proc4, self.colors_util.model)
        im_proc6 = clean_label(im_proc5, self.conf['process']['morphKernel'])
        im_proc7 = clean_label(im_proc6, self.conf['process']['morphKernel'])
        im_proc8 = lut(im_proc7)

        color_blobs = find_class_center(im_proc7, self.colors_util.idx2color, 
                                        im_proc8)
        colors = find_colors(color_blobs)

        return colors


#for path in glob.glob('../images/im*.jpg'):
#    im = readImage(path)
#    print(process_image(im))
