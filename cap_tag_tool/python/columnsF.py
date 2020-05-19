# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'columnsF.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Columns(object):
    def setupUi(self, Columns):
        Columns.setObjectName("Columns")
        Columns.resize(198, 286)
        Columns.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(Columns)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Columns)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.colList = QtWidgets.QListWidget(Columns)
        self.colList.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.colList.setAlternatingRowColors(False)
        self.colList.setObjectName("colList")
        self.gridLayout.addWidget(self.colList, 1, 0, 1, 1)

        self.retranslateUi(Columns)
        QtCore.QMetaObject.connectSlotsByName(Columns)

    def retranslateUi(self, Columns):
        _translate = QtCore.QCoreApplication.translate
        Columns.setWindowTitle(_translate("Columns", "Filter Columns"))
        self.label.setText(_translate("Columns", "Columns Shown:"))
        self.colList.setSortingEnabled(False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Columns = QtWidgets.QWidget()
    ui = Ui_Columns()
    ui.setupUi(Columns)
    Columns.show()
    sys.exit(app.exec_())
