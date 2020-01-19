import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.setCentralWidget(self.table)
        data1 = ['row1','row2','row3','row4']
        data2 = ['1','2.0','3.00000001','3.9999999']

        self.table.setRowCount(4)

        for index in range(4):
            item1 = QTableWidgetItem(data1[index])
            self.table.setItem(index,0,item1)
            item2 = QTableWidgetItem(data2[index])
            self.table.setItem(index,1,item2)
            self.btn_sell = QPushButton('Edit')
            self.btn_sell.clicked.connect(self.handleButtonClicked)
            self.table.setCellWidget(index,2,self.btn_sell)

    def handleButtonClicked(self):
        button = QtGui.qApp.focusWidget()
        # or button = self.sender()
        index = self.table.indexAt(button.pos())
        if index.isValid():
            print(index.row(), index.column())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())