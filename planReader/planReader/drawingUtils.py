import numpy as np
import cv2
import cv2.aruco as aruco


def draw_aruco(im, corners, rvecs, tvecs, cameraMatrix, distCoeffs):
    im = aruco.drawDetectedMarkers(im.copy(), corners)
    aruco.drawAxis(im, cameraMatrix, distCoeffs,
                   rvecs[0, ...], tvecs[0, ...], 20)
    return im


def draw_points(im, pts):
    im = im.copy()
    for p in pts:
        cv2.circle(im, (p[0], p[1]), 8, (255, 0, 0), -1)
    return im


def lut(im):
    im = np.repeat(im[:, :, np.newaxis], 3, axis=2)

    lut = np.zeros((256, 1, 3), dtype=np.uint8)
    lut[0, 0, :] = np.array([255, 255, 255], dtype=np.uint8)  # other
    lut[1, 0, :] = np.array([0, 0, 255], dtype=np.uint8)      # blue
    lut[2, 0, :] = np.array([0, 255, 0], dtype=np.uint8)      # green
    lut[3, 0, :] = np.array([255, 255, 0], dtype=np.uint8)    # yellow
    lut[4, 0, :] = np.array([255, 127, 0], dtype=np.uint8)    # orange
    lut[5, 0, :] = np.array([0, 0, 0], dtype=np.uint8)        # black
    lut[6, 0, :] = np.array([255, 255, 255], dtype=np.uint8)  # grey

    cv2.LUT(im, lut, im)
    return im
