import cv2
import numpy as np

from sklearn import mixture


def keep_color(im, model):
    out = np.zeros(im.shape[:2], dtype=np.uint8)

    for i in range(im.shape[0]):
        line = im[i, :, :].astype(np.float32)
        results = model.predict(line)

        out[i, :] = results

    return out


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