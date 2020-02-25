# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'messageBox.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_msgDialog(object):
    def setupUi(self, msgDialog):
        msgDialog.setObjectName("msgDialog")
        msgDialog.resize(250, 62)
        msgDialog.setMinimumSize(QtCore.QSize(0, 0))
        msgDialog.setMaximumSize(QtCore.QSize(250, 62))
        self.gridLayout = QtWidgets.QGridLayout(msgDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.text = QtWidgets.QLabel(msgDialog)
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.text.setObjectName("text")
        self.gridLayout.addWidget(self.text, 0, 0, 1, 2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.OKbutton = QtWidgets.QDialogButtonBox(msgDialog)
        self.OKbutton.setMaximumSize(QtCore.QSize(50, 50))
        self.OKbutton.setOrientation(QtCore.Qt.Vertical)
        self.OKbutton.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.OKbutton.setObjectName("OKbutton")
        self.gridLayout_2.addWidget(self.OKbutton, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 2)

        self.retranslateUi(msgDialog)
        self.OKbutton.accepted.connect(msgDialog.close)
        QtCore.QMetaObject.connectSlotsByName(msgDialog)

    def retranslateUi(self, msgDialog):
        _translate = QtCore.QCoreApplication.translate
        msgDialog.setWindowTitle(_translate("msgDialog", "Dialog"))
        self.text.setText(_translate("msgDialog", "Text here!"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    msgDialog = QtWidgets.QDialog()
    ui = Ui_msgDialog()
    ui.setupUi(msgDialog)
    msgDialog.show()
    sys.exit(app.exec_())

