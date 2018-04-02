import sys
import glob
import yaml
import argparse
import numpy as np

from PIL import Image
from PIL.ImageQt import ImageQt
from os.path import join, basename, isfile

from planReader.colorsUtils import norm_colors, improve_colors, pick_color

COLOR_NAMES = ['Grey', 'Blue', 'Yellow', 'Black', 'Green', 'Orange']
WINDOW_SIZE = 5


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('im_path',
                        help='Path to the PNG images folder.')
    parser.add_argument('--colors', dest='color_path',
                        default='colors.yaml',
                        help='File generate by the colorPickerApp.')
    parser.add_argument('--out', dest='output',
                        default='colors.yaml',
                        help='Output file.')

    return parser.parse_args()


def extract_colors(path, filename, im_size, colors, window_size):
    colorset = dict()
    for colorname in COLOR_NAMES:
        colorset[colorname] = list()

    im = open_im(path, filename, im_size)

    greypos = colors['Grey'][0]
    x_grey = greypos['x']
    y_grey = greypos['y']

    grey = pick_color(im, x_grey, y_grey, window_size)

    im_opt = im.copy()
    im_opt = norm_colors(im.astype(np.float), grey)
    im_opt = improve_colors(im_opt)

    for colorname, colorlist in colors.items():
        for sample in colorlist:
            x = sample['x']
            y = sample['y']
            color = pick_color(im_opt, x, y, 3)
            colorset[colorname].append(color.tolist())

    return colorset


def open_im(path, filename, im_size):
    im = Image.open(join(path, filename))
    im = im.convert('RGB')
    im.thumbnail(im_size, Image.ANTIALIAS)
    im = np.array(im)
    return im


def mergedict(source, dest):
    dest = dest.copy()
    for key, elem in source.items():
        if key in dest.keys():
            dest[key] += elem
        else:
            dest[key] = elem
    return dest


def main():
    args = parse_args()

    colorset = dict()

    with open(args.color_path, 'r') as f:
        pickerstruct = yaml.load(f)

    im_size = pickerstruct['IM_SIZE']

    for filename, colors in pickerstruct['Images'].items():
        is_empty = True

        for colorname, colorlist in colors.items():
            if colorlist:
                is_empty = False

        if not is_empty:
            colors = extract_colors(args.im_path, filename,
                                    im_size, colors, WINDOW_SIZE)
            colorset = mergedict(colors, colorset)

    out_dict = dict()
    out_dict['colorsGroup'] = colorset

    color_idx = {'Other': 0, 'Blue': 1, 'Green': 2,
                 'Yellow': 3, 'Orange': 4, 'Black': 5, 'Grey': 6}
    out_dict['color_idx'] = color_idx

    with open(args.output, 'w') as f:
        yaml.dump(out_dict, f, default_flow_style=False)

if __name__ == "__main__":
    main()
