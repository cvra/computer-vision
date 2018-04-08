import yaml
import numpy as np

import cv2
import cv2.aruco as aruco

from os.path import join

from .colorsUtils import norm_colors, \
                         improve_colors, \
                         pick_color, \
                         crop_on_color_map
from .colorsSegm import Colors
from .drawingUtils import draw_points, lut
from .drawingUtils import draw_points, lut

from .colorsLabel import keep_color, \
                         clean_label, \
                         find_colors, \
                         find_class_center
from enum import Enum


class PlayingSide(Enum):
    GREEN = -1
    ORANGE = 1


def debug_writefiles(path, im,  pts, greypos,
                     im_proc1, im_proc2, im_proc3,
                     im_proc4, im_proc5, im_proc6,
                     im_proc7, im_proc8, im_aruco):

    cv2.imwrite(join(path, 'out_aruco.png'), cv2.cvtColor(
        im_aruco, cv2.COLOR_RGB2BGR))
    cv2.imwrite(join(path, 'out1.png'), cv2.cvtColor(
        draw_points(im, pts), cv2.COLOR_RGB2BGR))
    cv2.imwrite(join(path, 'out2.png'), cv2.cvtColor(draw_points(
        im, greypos[np.newaxis, :]), cv2.COLOR_RGB2BGR))
    cv2.imwrite(join(path, 'out3.png'), cv2.cvtColor(np.vstack([im_proc1, im_proc2,
                                                                im_proc3, im_proc4]),
                                                     cv2.COLOR_RGB2BGR))
    cv2.imwrite(join(path, 'out4.png'), np.vstack(
        [im_proc5, im_proc6, im_proc7]))
    cv2.imwrite(join(path, 'out5.png'), cv2.cvtColor(
        im_proc8, cv2.COLOR_RGB2BGR))


class planReader():
    def __init__(self, config_path='conf.yaml', config_color='colors.yaml',
                 debug=False, debugpath='./'):
        self.debug = debug
        self.debugpath = debugpath

        self.playing_side = None

        # load config
        self.conf, self.conf_colors = self.load_config(
            config_path, config_color)
        self.cameraMatrix = self.conf['camera']['cameraMatrix']
        self.distCoeffs = self.conf['camera']['distCoeffs']

        self.aruco_id = self.conf['ArUco']['id']
        self.aruco_dict = self.conf['ArUco']['dict']
        self.aruco_height = self.conf['ArUco']['height']

        self.colors_util = Colors(self.conf_colors['colorsGroup'],
                                  self.conf_colors['color_idx'])

    def get_colormap_pts(self):
        if self.playing_side == PlayingSide.GREEN:
            areaY = self.conf['colorMap']['greenSide']['areaY']
            areaX = self.conf['colorMap']['greenSide']['areaX']
        else:
            areaY = self.conf['colorMap']['orangeSide']['areaY']
            areaX = self.conf['colorMap']['orangeSide']['areaX']

        areaHeight = self.conf['colorMap']['areaHeight']
        areaWidth = self.conf['colorMap']['areaWidth']

        return np.array([[areaY - areaHeight / 2, areaX - areaWidth / 2, 0],
                         [areaY - areaHeight / 2, areaX + areaWidth / 2, 0],
                         [areaY + areaHeight / 2, areaX + areaWidth / 2, 0],
                         [areaY + areaHeight / 2, areaX - areaWidth / 2, 0]],
                        dtype=np.float)

    def get_grey_pts(self):
        if self.playing_side == PlayingSide.GREEN:
            grey_pos = np.array([[self.conf['colorMap']['greenSide']['greyY'],
                                  self.conf['colorMap']['greenSide']['greyX'],
                                  0]], dtype=np.float)
        else:
            grey_pos = np.array([[self.conf['colorMap']['orangeSide']['greyY'],
                                  self.conf['colorMap']['orangeSide']['greyX'],
                                  0]], dtype=np.float)
        return grey_pos

    def load_config(self, conf_path, colors_path):
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

    def detect_aruco(self, im):
        aruco_dict = aruco.Dictionary_get(self.aruco_dict)
        param = aruco.DetectorParameters_create()

        corners, ids, _ = aruco.detectMarkers(im, aruco_dict, parameters=param)

        sel_id = np.argwhere(ids == self.aruco_id)
        if sel_id.shape[0]:
            idx = sel_id[0][0]

            corners = [corners[idx]]
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                                  self.aruco_height,
                                                                  self.cameraMatrix,
                                                                  self.distCoeffs)
        else:
            corners, rvecs, tvecs = None, None, None

        return corners, rvecs, tvecs

    def drawAruco(self, im, corners, rvecs, tvecs):
        im = aruco.drawDetectedMarkers(im.copy(), corners)
        aruco.drawAxis(im, self.cameraMatrix, self.distCoeffs,
                       rvecs[0, ...], tvecs[0, ...], 20)
        return im

    def process(self, im):
        corners, rvecs, tvecs = self.detect_aruco(im)

        if corners is None:
            return []

        if np.sign(np.squeeze(rvecs / np.linalg.norm(rvecs))[0]) > 0:
            self.playing_side = PlayingSide.ORANGE
        else:
            self.playing_side = PlayingSide.GREEN

        pts, _ = cv2.projectPoints(self.get_colormap_pts(), rvecs, tvecs,
                                   self.cameraMatrix, self.distCoeffs)
        pts = np.rint(pts.squeeze()).astype(np.int)

        greypos, _ = cv2.projectPoints(self.get_grey_pts(), rvecs, tvecs,
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
            im_aruco = self.drawAruco(im, corners, rvecs, tvecs)

            debug_writefiles(self.debugpath, im,  pts, greypos,
                             im_proc1, im_proc2, im_proc3,
                             im_proc4, im_proc5, im_proc6,
                             im_proc7, im_proc8, im_aruco)

        color_blobs = find_class_center(im_proc7, self.colors_util.idx2color,
                                        im_proc8)
        colors = find_colors(color_blobs)

        return colors
