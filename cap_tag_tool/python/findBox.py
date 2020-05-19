# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'findBox.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Find(object):
    def setupUi(self, Find):
        Find.setObjectName("Find")
        Find.resize(298, 74)
        Find.setMaximumSize(QtCore.QSize(500, 82))
        font = QtGui.QFont()
        font.setFamily("Arial")
        Find.setFont(font)
        Find.setStyleSheet("")
        Find.setSizeGripEnabled(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(Find)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(Find)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Find)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(60, 0))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 3, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(Find)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setDragEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_3.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Find)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMaximumSize(QtCore.QSize(45, 16777215))
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.pushButton = QtWidgets.QPushButton(Find)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_4.addWidget(self.pushButton, 0, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Find)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_4.addWidget(self.pushButton_2, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_4, 1, 0, 1, 1)

        self.retranslateUi(Find)
        QtCore.QMetaObject.connectSlotsByName(Find)

    def retranslateUi(self, Find):
        _translate = QtCore.QCoreApplication.translate
        Find.setWindowTitle(_translate("Find", "Find Items"))
        self.label.setText(_translate("Find", "Find:"))
        self.label_2.setText(_translate("Find", "17 / 17"))
        self.pushButton_3.setText(_translate("Find", "Search"))
        self.pushButton.setText(_translate("Find", "Next"))
        self.pushButton_2.setText(_translate("Find", "Previous"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Find = QtWidgets.QDialog()
    ui = Ui_Find()
    ui.setupUi(Find)
    Find.show()
    sys.exit(app.exec_())

