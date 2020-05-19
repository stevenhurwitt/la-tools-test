# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainPlotWindow(object):
    def setupUi(self, MainPlotWindow):
        MainPlotWindow.setObjectName("MainPlotWindow")
        MainPlotWindow.resize(840, 491)
        self.centralwidget = QtWidgets.QWidget(MainPlotWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.vsButton = QtWidgets.QPushButton(self.centralwidget)
        self.vsButton.setObjectName("vsButton")
        self.horizontalLayout.addWidget(self.vsButton)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 2, 1)
        self.mplwindow = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplwindow.sizePolicy().hasHeightForWidth())
        self.mplwindow.setSizePolicy(sizePolicy)
        self.mplwindow.setObjectName("mplwindow")
        self.mplvl = QtWidgets.QVBoxLayout(self.mplwindow)
        self.mplvl.setObjectName("mplvl")
        self.gridLayout.addWidget(self.mplwindow, 0, 0, 3, 1)
        self.mplfigs = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplfigs.sizePolicy().hasHeightForWidth())
        self.mplfigs.setSizePolicy(sizePolicy)
        self.mplfigs.setMaximumSize(QtCore.QSize(200, 16777215))
        self.mplfigs.setObjectName("mplfigs")
        self.gridLayout.addWidget(self.mplfigs, 2, 1, 1, 1)
        MainPlotWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainPlotWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 840, 21))
        self.menubar.setObjectName("menubar")
        self.menuQuick_Menu = QtWidgets.QMenu(self.menubar)
        self.menuQuick_Menu.setObjectName("menuQuick_Menu")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainPlotWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainPlotWindow)
        self.statusbar.setObjectName("statusbar")
        MainPlotWindow.setStatusBar(self.statusbar)
        self.actionClose = QtWidgets.QAction(MainPlotWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionClearData = QtWidgets.QAction(MainPlotWindow)
        self.actionClearData.setObjectName("actionClearData")
        self.menuQuick_Menu.addAction(self.actionClose)
        self.menuEdit.addAction(self.actionClearData)
        self.menubar.addAction(self.menuQuick_Menu.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainPlotWindow)
        QtCore.QMetaObject.connectSlotsByName(MainPlotWindow)

    def retranslateUi(self, MainPlotWindow):
        _translate = QtCore.QCoreApplication.translate
        MainPlotWindow.setWindowTitle(_translate("MainPlotWindow", "Plot Tool"))
        self.clearButton.setText(_translate("MainPlotWindow", "Clear Data"))
        self.vsButton.setText(_translate("MainPlotWindow", "Versus"))
        self.menuQuick_Menu.setTitle(_translate("MainPlotWindow", "File"))
        self.menuEdit.setTitle(_translate("MainPlotWindow", "Edit"))
        self.actionClose.setText(_translate("MainPlotWindow", "Close"))
        self.actionClearData.setText(_translate("MainPlotWindow", "Clear Data"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainPlotWindow = QtWidgets.QMainWindow()
    ui = Ui_MainPlotWindow()
    ui.setupUi(MainPlotWindow)
    MainPlotWindow.show()
    sys.exit(app.exec_())
