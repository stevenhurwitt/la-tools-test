# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'percentChangeCalc.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_pChangeCalc(object):
    def setupUi(self, pChangeCalc):
        pChangeCalc.setObjectName("pChangeCalc")
        pChangeCalc.resize(228, 139)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pChangeCalc.sizePolicy().hasHeightForWidth())
        pChangeCalc.setSizePolicy(sizePolicy)
        pChangeCalc.setMaximumSize(QtCore.QSize(264, 139))
        self.gridLayout = QtWidgets.QGridLayout(pChangeCalc)
        self.gridLayout.setObjectName("gridLayout")
        self.v1Label = QtWidgets.QLabel(pChangeCalc)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.v1Label.sizePolicy().hasHeightForWidth())
        self.v1Label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Franklin Gothic Medium")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.v1Label.setFont(font)
        self.v1Label.setObjectName("v1Label")
        self.gridLayout.addWidget(self.v1Label, 1, 1, 1, 1)
        self.v2Entry = QtWidgets.QLineEdit(pChangeCalc)
        self.v2Entry.setAlignment(QtCore.Qt.AlignCenter)
        self.v2Entry.setDragEnabled(True)
        self.v2Entry.setObjectName("v2Entry")
        self.gridLayout.addWidget(self.v2Entry, 2, 2, 1, 1)
        self.v1Entry = QtWidgets.QLineEdit(pChangeCalc)
        self.v1Entry.setAlignment(QtCore.Qt.AlignCenter)
        self.v1Entry.setDragEnabled(True)
        self.v1Entry.setObjectName("v1Entry")
        self.gridLayout.addWidget(self.v1Entry, 1, 2, 1, 1)
        self.v2Label = QtWidgets.QLabel(pChangeCalc)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.v2Label.sizePolicy().hasHeightForWidth())
        self.v2Label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Franklin Gothic Medium")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.v2Label.setFont(font)
        self.v2Label.setObjectName("v2Label")
        self.gridLayout.addWidget(self.v2Label, 2, 1, 1, 1)
        self.pChangeTitle = QtWidgets.QLabel(pChangeCalc)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pChangeTitle.sizePolicy().hasHeightForWidth())
        self.pChangeTitle.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Franklin Gothic Medium")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.pChangeTitle.setFont(font)
        self.pChangeTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.pChangeTitle.setObjectName("pChangeTitle")
        self.gridLayout.addWidget(self.pChangeTitle, 0, 1, 1, 2)
        self.pChangeRes = QtWidgets.QLabel(pChangeCalc)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pChangeRes.setFont(font)
        self.pChangeRes.setAlignment(QtCore.Qt.AlignCenter)
        self.pChangeRes.setObjectName("pChangeRes")
        self.gridLayout.addWidget(self.pChangeRes, 3, 1, 1, 2)
        self.pChangeButtons = QtWidgets.QDialogButtonBox(pChangeCalc)
        self.pChangeButtons.setOrientation(QtCore.Qt.Horizontal)
        self.pChangeButtons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.pChangeButtons.setCenterButtons(True)
        self.pChangeButtons.setObjectName("pChangeButtons")
        self.gridLayout.addWidget(self.pChangeButtons, 4, 1, 1, 2)

        self.retranslateUi(pChangeCalc)
        self.pChangeButtons.accepted.connect(pChangeCalc.accept)
        self.pChangeButtons.rejected.connect(pChangeCalc.reject)
        QtCore.QMetaObject.connectSlotsByName(pChangeCalc)
        pChangeCalc.setTabOrder(self.v1Entry, self.v2Entry)

    def retranslateUi(self, pChangeCalc):
        _translate = QtCore.QCoreApplication.translate
        pChangeCalc.setWindowTitle(_translate("pChangeCalc", "Percent Change Calculator"))
        self.v1Label.setText(_translate("pChangeCalc", "V1:"))
        self.v2Entry.setPlaceholderText(_translate("pChangeCalc", "\"New\" Value"))
        self.v1Entry.setPlaceholderText(_translate("pChangeCalc", "\"Original\" Value"))
        self.v2Label.setText(_translate("pChangeCalc", "V2:"))
        self.pChangeTitle.setText(_translate("pChangeCalc", "% Change Calculator"))
        self.pChangeRes.setText(_translate("pChangeCalc", "    0.00 %"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    pChangeCalc = QtWidgets.QDialog()
    ui = Ui_pChangeCalc()
    ui.setupUi(pChangeCalc)
    pChangeCalc.show()
    sys.exit(app.exec_())

