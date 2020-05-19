# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotName.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_plotNameDialog(object):
    def setupUi(self, plotNameDialog):
        plotNameDialog.setObjectName("plotNameDialog")
        plotNameDialog.resize(301, 41)
        self.gridLayout = QtWidgets.QGridLayout(plotNameDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushOK = QtWidgets.QPushButton(plotNameDialog)
        self.pushOK.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushOK.setObjectName("pushOK")
        self.gridLayout.addWidget(self.pushOK, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(plotNameDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.plotNameInput = QtWidgets.QLineEdit(plotNameDialog)
        self.plotNameInput.setObjectName("plotNameInput")
        self.gridLayout.addWidget(self.plotNameInput, 1, 1, 1, 1)
        self.pushCancel = QtWidgets.QPushButton(plotNameDialog)
        self.pushCancel.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushCancel.setObjectName("pushCancel")
        self.gridLayout.addWidget(self.pushCancel, 1, 3, 1, 1)

        self.retranslateUi(plotNameDialog)
        QtCore.QMetaObject.connectSlotsByName(plotNameDialog)

    def retranslateUi(self, plotNameDialog):
        _translate = QtCore.QCoreApplication.translate
        plotNameDialog.setWindowTitle(_translate("plotNameDialog", "Dialog"))
        self.pushOK.setText(_translate("plotNameDialog", "OK"))
        self.label.setText(_translate("plotNameDialog", "Plot Name:"))
        self.pushCancel.setText(_translate("plotNameDialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    plotNameDialog = QtWidgets.QDialog()
    ui = Ui_plotNameDialog()
    ui.setupUi(plotNameDialog)
    plotNameDialog.show()
    sys.exit(app.exec_())
