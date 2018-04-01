import sys
import glob
import yaml
import argparse

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtWidgets, QtGui, QtCore
from os.path import join, basename, isfile

from colorPickerGUI import Ui_MainWindow


MAX_SIZE = 1000, 1000
COLOR_NAMES = ['Grey', 'Blue', 'Yellow', 'Black', 'Green', 'Orange']


class ImageColorSet():
    def __init__(self, path, color_path='color.yaml'):
        self.path = path
        self.color_path = color_path

        self.img_list = [basename(elem)
                         for elem in glob.glob(join(path, '*.png'))]

        if isfile(color_path):
            self.load()
        else:
            self.colorset = dict()
            self.colorset['im_dim'] = list(MAX_SIZE)
            for elem in self.img_list:
                self.colorset[elem] = dict()
                for colorname in COLOR_NAMES:
                    self.colorset[elem][colorname] = list()

    def __getitem__(self, index):
        im = Image.open(join(self.path, self.img_list[index]))
        im = im.convert('RGB')
        im.thumbnail(MAX_SIZE, Image.ANTIALIAS)
        return im

    def __len__(self):
        return len(self.img_list)

    def add_color_ref(self, index, colorname, x, y):
        self.colorset[self.img_list[index]][colorname].append({'x': x, 'y': y})
        self.save()

    def save(self):
        with open(self.color_path, 'w') as f:
            yaml.dump(self.colorset, f, default_flow_style=False)

    def load(self):
        with open(self.color_path, 'r') as f:
            self.colorset = yaml.load(f)


class GUI(Ui_MainWindow):
    def __init__(self, MainWindow, images_set):
        self.setupUi(MainWindow)

        self.images_set = images_set
        self.image = None
        self.imidx = 0

        self.btnBack.clicked.connect(self.cb_back_click)
        self.btnNext.clicked.connect(self.cb_next_click)
        self.cbxColor.currentIndexChanged.connect(self.cb_color_change)
        self.cbxFilename.currentIndexChanged.connect(self.cb_filename_change)
        self.imView.mousePressEvent = self.cb_im_view_click

        self.colorname = self.cbxColor.itemText(0)

        for elem in self.images_set.img_list:
            self.cbxFilename.addItem(elem)

        self.load_im()

    def cb_back_click(self, e):
        self.imidx -= 1
        if self.imidx < 0:
            self.imidx = len(self.images_set) - 1
        self.load_im()
        self.cbxFilename.setCurrentIndex(self.imidx)

    def cb_next_click(self, e):
        self.imidx += 1
        if self.imidx >= len(self.images_set):
            self.imidx = 0
        self.load_im()
        self.cbxFilename.setCurrentIndex(self.imidx)

    def cb_color_change(self, e):
        self.colorname = self.cbxColor.itemText(e)

    def cb_filename_change(self, e):
        self.imidx = e
        self.load_im()

    def cb_im_view_click(self, e):
        self.images_set.add_color_ref(self.imidx, self.colorname, e.x(), e.y())

    def load_im(self):
        self.image = self.images_set[self.imidx]
        qim = ImageQt(self.image)
        pix = QtGui.QPixmap.fromImage(qim)
        self.imView.setPixmap(pix)
        self.imView.update()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Left:
            self.cb_back_click(None)
        if e.key() == QtCore.Qt.Key_Right:
            self.cb_next_click(None)
        if e.key() == QtCore.Qt.Key_O:
            self.set_colorname('Orange')
        if e.key() == QtCore.Qt.Key_B:
            self.set_colorname('Blue')
        if e.key() == QtCore.Qt.Key_G:
            self.set_colorname('Grey')
        if e.key() == QtCore.Qt.Key_N:
            self.set_colorname('Black')
        if e.key() == QtCore.Qt.Key_Y:
            self.set_colorname('Yellow')
        if e.key() == QtCore.Qt.Key_V:
            self.set_colorname('Green')

    def set_colorname(self, colorname):
        index = self.cbxColor.findText(colorname, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbxColor.setCurrentIndex(index)
            self.colorname = colorname


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, im_path, color_path):
        super(ApplicationWindow, self).__init__()

        self.images_set = ImageColorSet(im_path, color_path)
        self.ui = GUI(self, self.images_set)

    def keyPressEvent(self, e):
        self.ui.keyPressEvent(e)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('im_path',
                        help='Path to the PNG images folder.')
    parser.add_argument('--output', dest='color_path',
                        default='colors.yaml',
                        help='Output files.')

    return parser.parse_args()


def main():
    args = parse_args()

    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow(args.im_path, args.color_path)
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
