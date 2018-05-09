import sys
import glob
import yaml
import argparse

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox

from os.path import join, basename, isfile
from colorPickerGUI import Ui_MainWindow
from buildColorsCollection import buildColorsCollection

MAX_SIZE = 1000, 1000
COLORS = {'Grey': (127, 127, 127),
          'Blue': (0, 0, 255),
          'Yellow': (255, 255, 0),
          'Black': (0, 0, 0),
          'Green': (0, 255, 0),
          'Orange': (255, 127, 0)}

class ImageColorSet():
    def __init__(self, path):
        self.path = path

        self.img_list = [basename(elem)
                         for elem in glob.glob(join(path, '*.png'))]

        #if isfile(color_path):
        #    self.load()
        #else:
        self.colorset = dict()
        self.colorset['IM_SIZE'] = list(MAX_SIZE)
        self.colorset['Images'] = dict()
        for elem in self.img_list:
            self.colorset['Images'][elem] = dict()
            for colorname in COLORS.keys():
                self.colorset['Images'][elem][colorname] = list()

    def __getitem__(self, index):
        im = Image.open(join(self.path, self.img_list[index]))
        im = im.convert('RGB')
        im.thumbnail(MAX_SIZE, Image.ANTIALIAS)
        return im

    def __len__(self):
        return len(self.img_list)

    def add_color_ref(self, index, colorname, x, y):
        self.colorset['Images'][self.img_list[index]
                                ][colorname].append({'x': x, 'y': y})
        #self.save()

    #def save(self):
    #    with open(self.color_path, 'w') as f:
    #        yaml.dump(self.colorset, f, default_flow_style=False)

    #def load(self):
    #    with open(self.color_path, 'r') as f:
    #        self.colorset = yaml.load(f)


class GUI(Ui_MainWindow):
    def __init__(self, MainWindow, images_set, im_path, color_path='color.yaml'):
        self.setupUi(MainWindow)
        self.main_window = MainWindow
        self.color_path = color_path

        self.images_set = images_set
        self.image = None
        self.imidx = 0

        self.im_path = im_path
        self.is_grey_set = False

        self.btnBack.clicked.connect(self.cb_back_click)
        self.btnNext.clicked.connect(self.cb_next_click)
        self.btnSave.clicked.connect(self.cb_save_click)
        self.cbxColor.currentIndexChanged.connect(self.cb_color_change)
        self.cbxFilename.currentIndexChanged.connect(self.cb_filename_change)
        self.imView.mousePressEvent = self.cb_im_view_click

        self.colorname = self.cbxColor.itemText(0)

        for elem in self.images_set.img_list:
            self.cbxFilename.addItem(elem)

        self.load_im(self.colorname)

    def cb_save_click(self, e):
        buildColorsCollection(self.im_path, self.images_set.colorset, self.color_path)

    def cb_back_click(self, e):
        self.imidx -= 1
        if self.imidx < 0:
            self.imidx = len(self.images_set) - 1
        self.load_im(self.colorname)
        self.cbxFilename.setCurrentIndex(self.imidx)
        self.is_grey_set = False
        self.cbxColor.setEnabled(False)
        self.set_colorname('Grey', COLORS['Grey'])

    def cb_next_click(self, e):
        self.imidx += 1
        if self.imidx >= len(self.images_set):
            self.imidx = 0
        self.load_im(self.colorname)
        self.cbxFilename.setCurrentIndex(self.imidx)
        self.is_grey_set = False
        self.cbxColor.setEnabled(False)
        self.set_colorname('Grey', COLORS['Grey'])

    def cb_color_change(self, e):
        self.colorname = self.cbxColor.itemText(e)
        self.load_im(self.colorname)


    def cb_filename_change(self, e):
        self.imidx = e
        self.load_im(self.colorname)
        self.is_grey_set = False
        self.cbxColor.setEnabled(False)

    def cb_im_view_click(self, e):
        self.images_set.add_color_ref(self.imidx, self.colorname, e.x(), e.y())
        self.is_grey_set = True
        self.cbxColor.setEnabled(True)
        print('Add {} sample'.format(self.colorname))

    def load_im(self, color=None):
        self.image = self.images_set[self.imidx]

        if color:
            draw = ImageDraw.Draw(self.image)
            draw.rectangle([(4, 4), (36, 36)], fill=(0, 0, 0))
            draw.rectangle([(5, 5), (35, 35)], fill=color)
            del draw

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
            if self.is_grey_set:
                self.set_colorname('Orange', COLORS['Orange'])
            else:
                QMessageBox.about(self.main_window, 'Alert', 'Grey not set yet for this image! Please set it before selecting colors.')
        
        if e.key() == QtCore.Qt.Key_B:
            if self.is_grey_set:
                self.set_colorname('Blue', COLORS['Blue'])
            else:
                QMessageBox.about(self.main_window, 'Alert', 'Grey not set yet for this image! Please set it before selecting colors.')
        
        if e.key() == QtCore.Qt.Key_G:
            self.set_colorname('Grey', COLORS['Grey'])
        
        if e.key() == QtCore.Qt.Key_N:
            if self.is_grey_set:
                self.set_colorname('Black', COLORS['Black'])
            else:
                QMessageBox.about(self.main_window, 'Alert', 'Grey not set yet for this image! Please set it before selecting colors.')
        
        if e.key() == QtCore.Qt.Key_J or e.key() == QtCore.Qt.Key_Y:
            if self.is_grey_set:
                self.set_colorname('Yellow', COLORS['Yellow'])
            else:
                QMessageBox.about(self.main_window, 'Alert', 'Grey not set yet for this image! Please set it before selecting colors.')
        
        if e.key() == QtCore.Qt.Key_V:
            if self.is_grey_set:
                self.set_colorname('Green', COLORS['Green'])
            else:
                QMessageBox.about(self.main_window, 'Alert', 'Grey not set yet for this image! Please set it before selecting colors.')

    def set_colorname(self, colorname, color):
        index = self.cbxColor.findText(colorname, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbxColor.setCurrentIndex(index)
            self.colorname = colorname
        else:
            print('noo')
        self.load_im(color)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, im_path, color_path):
        super(ApplicationWindow, self).__init__()

        self.images_set = ImageColorSet(im_path)
        self.ui = GUI(self, self.images_set, im_path, color_path)

    def keyPressEvent(self, e):
        self.ui.keyPressEvent(e)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('im_path',
                        help='Path to the PNG images folder.')
    parser.add_argument('--output', dest='color_path',
                        default='colors.yaml',
                        help='Output colors configuration file.')

    return parser.parse_args()


def main():
    args = parse_args()

    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow(args.im_path, args.color_path)
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
