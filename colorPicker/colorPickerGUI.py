# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIcvra.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(504, 397)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.cbxFilename = QtWidgets.QComboBox(self.centralwidget)
        self.cbxFilename.setObjectName("cbxFilename")
        self.gridLayout.addWidget(self.cbxFilename, 4, 0, 1, 2)
        self.imView = QtWidgets.QLabel(self.centralwidget)
        self.imView.setText("")
        self.imView.setObjectName("imView")
        self.gridLayout.addWidget(self.imView, 6, 0, 1, 5)
        self.cbxColor = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxColor.sizePolicy().hasHeightForWidth())
        self.cbxColor.setSizePolicy(sizePolicy)
        self.cbxColor.setObjectName("cbxColor")
        self.cbxColor.addItem("")
        self.cbxColor.addItem("")
        self.cbxColor.addItem("")
        self.cbxColor.addItem("")
        self.cbxColor.addItem("")
        self.cbxColor.addItem("")
        self.gridLayout.addWidget(self.cbxColor, 4, 4, 1, 1)
        self.btnBack = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBack.sizePolicy().hasHeightForWidth())
        self.btnBack.setSizePolicy(sizePolicy)
        self.btnBack.setObjectName("btnBack")
        self.gridLayout.addWidget(self.btnBack, 4, 2, 1, 1)
        self.btnNext = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnNext.sizePolicy().hasHeightForWidth())
        self.btnNext.setSizePolicy(sizePolicy)
        self.btnNext.setObjectName("btnNext")
        self.gridLayout.addWidget(self.btnNext, 4, 3, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.cbxColor.setItemText(0, _translate("MainWindow", "Grey"))
        self.cbxColor.setItemText(1, _translate("MainWindow", "Blue"))
        self.cbxColor.setItemText(2, _translate("MainWindow", "Yellow"))
        self.cbxColor.setItemText(3, _translate("MainWindow", "Black"))
        self.cbxColor.setItemText(4, _translate("MainWindow", "Green"))
        self.cbxColor.setItemText(5, _translate("MainWindow", "Red"))
        self.btnBack.setText(_translate("MainWindow", "<"))
        self.btnNext.setText(_translate("MainWindow", ">"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

