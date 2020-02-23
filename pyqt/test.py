import operator  # used for sorting
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
from time import time
import threading
import datetime as dt
import pandas as pd
import numpy as np
import json
import os

os.chdir('C://Users/wb5888/Documents/la-tools-test/IDR_Drop/Logins')
filename = 'email_bodies_12_31_2019.json'

with open(filename, 'r') as email:
    email = json.load(email)
    email = json.loads(email)
    
email_df = pd.DataFrame.from_dict(email)
email_df = email_df.T
email_df['date'] = pd.to_datetime(email_df['date'])
email_df.set_index('date', drop = False, inplace = True)
email_df.sort_index(inplace = True, ascending = False)
util = []

for a in email_df.accts:
    leading = a[0][:2]
    if leading == '80':
        util.append('PSNH')
    elif leading == '51':
        util.append('CLP')
    elif leading == '54':
        util.append('WMECO')
    else:
        util.append('NSTAR_NGRID')
        
email_df['util'] = util

recent = max(email_df.date) - dt.timedelta(days = 31)
email_df = email_df[[d > recent for d in email_df.date]]

n = email_df.shape[0]
p = email_df.shape[1]

col1 = email_df.accts
col2 = email_df.date.astype(str)
col3 = email_df.name
col4 = email_df.pw
col5 = email_df.user
col6 = email_df.util

### construct pyqt table
class MyWindow(QtWidgets.QWidget):
    def __init__(self, dataList, header, *args):
        QtWidgets.QMainWindow.__init__(self, *args)
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_model = MyTableModel(self, dataList, header)
        self.table_view = QtWidgets.QTableView()
        #self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # bind cell click to a method reference
        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)

        self.table_view.setModel(self.table_model)
        # enable sorting
        self.table_view.setSortingEnabled(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def update_model(self, datalist, header):
        self.table_model2 = MyTableModel(self, dataList, header)
        self.table_view.setModel(self.table_model2)
        self.table_view.update()

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass


class MyTableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        self.timer = QtCore.QTimer()
        self.change_flag = True
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(1000)
        
        # self.rowCheckStateMap = {}

    def setDataList(self, mylist):
        self.mylist = mylist
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def updateModel(self):
        if self.change_flag is True:
            """dataList2 = []
            for index, row in email_df.iterrows():
                my_list = [QtWidgets.QCheckBox("Download")]
                my_list.append(list(row))
                dataList2.append(my_list)"""
            header = ['Download', 'Accounts', 'Date', 'Name', 'Password', 'User', 'Utility', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
            dataList2 = []
            for i in range(0,n):
                master = []
                checkbox1 = QtWidgets.QCheckBox("")
                checkbox1.setChecked(False)

                master.append(checkbox1)
                master.append(col1[i][0])
                master.append(col2[i])
                if type(col3[i]) == list:
                    master.append(col3[i][0])
                else:
                    master.append(col3[i])
                master.append(col4[i])
                master.append(col5[i])
                master.append(col6[i])

                dataList2.append(master)
            self.change_flag = False
        elif self.change_flag is False:
            """dataList2 = []
            for index, row in email_df.iterrows():
                my_list = [QtWidgets.QCheckBox("Download")]
                my_list.append(list(row))
                dataList2.append(my_list)"""
            header = ['Download', 'Accounts', 'Date', 'Name', 'Password', 'User', 'Utility', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
            dataList2 = []
            for i in range(0,n):
                master = []
                checkbox1 = QtWidgets.QCheckBox("")
                checkbox1.setChecked(False)

                master.append(checkbox1)
                master.append(col1[i][0])
                master.append(col2[i])
                if type(col3[i]) == list:
                    master.append(col3[i][0])
                else:
                    master.append(col3[i])
                master.append(col4[i])
                master.append(col5[i])
                master.append(col6[i])

                dataList2.append(master)
            self.change_flag = True

        self.mylist = dataList2
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            value = self.mylist[index.row()][index.column()].text()
        else:
            value = self.mylist[index.row()][index.column()]
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
                if self.mylist[index.row()][index.column()].isChecked():
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        # print(">>> sort() col = ", col)
        if col != 0:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.mylist.reverse()
            self.emit(SIGNAL("layoutChanged()"))

    def flags(self, index):
        if not index.isValid():
            return None
        # print(">>> flags() index.column() = ", index.column())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value == QtCore.Qt.Checked:
                self.mylist[index.row()][index.column()].setChecked(True)
                self.mylist[index.row()][index.column()].setText("")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])     
            else:
                self.mylist[index.row()][index.column()].setChecked(False)
                self.mylist[index.row()][index.column()].setText("")
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        print(">>> setData() index.row = ", index.row())
        print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True

def timer_func(win, mylist):
    print(">>> timer_func()")
    win.table_model.setDataList(mylist)
    win.table_view.repaint()
    win.table_view.update()

# def timer_func(num):
#     print(">>> timer_func() num = ", num)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ### read in email logins
    os.chdir('C://Users/wb5888/Documents/la-tools-test/IDR_Drop/Logins')
    filename = 'email_bodies_12_31_2019.json'

    with open(filename, 'r') as email:
        email = json.load(email)
        email = json.loads(email)
    
    email_df = pd.DataFrame.from_dict(email)
    email_df = email_df.T
    email_df['date'] = pd.to_datetime(email_df['date'])
    email_df.set_index('date', drop = False, inplace = True)
    email_df.sort_index(inplace = True, ascending = False)
    util = []

    for a in email_df.accts:
        leading = a[0][:2]
        if leading == '80':
            util.append('PSNH')
        elif leading == '51':
            util.append('CLP')
        elif leading == '54':
            util.append('WMECO')
        else:
            util.append('NSTAR_NGRID')
        
    email_df['util'] = util

    recent = max(email_df.date) - dt.timedelta(days = 31)
    email_df = email_df[[d > recent for d in email_df.date]]

    n = email_df.shape[0]
    p = email_df.shape[1]

    col1 = email_df.accts
    col2 = email_df.date.astype(str)
    col3 = email_df.name
    col4 = email_df.pw
    col5 = email_df.user
    col6 = email_df.util

    # you could process a CSV file to create this data
    header = ['Download', 'Accounts', 'Date', 'Name', 'Password', 'User', 'Utility', '卖持仓', '持仓盈亏', '平仓盈亏', '手续费', '净盈亏', '成交量', '成交金额', 'A成交率', 'B成交率', '交易模型', '下单算法']
    #header = ['download', 'accts', 'date', 'name', 'pw', 'user', 'utility']
    # a list of (fname, lname, age, weight) tuples
    dataList = []
    for i in range(0,n):
        master = []
        checkbox1 = QtWidgets.QCheckBox("")
        checkbox1.setChecked(False)

        master.append(checkbox1)
        master.append(col1[i][0])
        master.append(col2[i])
        if type(col3[i]) == list:
            master.append(col3[i][0])
        else:
            master.append(col3[i])
        master.append(col4[i])
        master.append(col5[i])
        master.append(col6[i])

        print(master)
        dataList.append(master)

    """checkbox1 = QtWidgets.QCheckBox("")
    checkbox1.setChecked(False)
    
    dataList = [
        [checkbox1, 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '03', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '04', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '01', 'zn1705,zn1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '02', 'ru1705,ru1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '02', 'ni1705,ni1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        [QtWidgets.QCheckBox(""), 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    ]"""

    win = MyWindow(dataList, header)
    win.show()
    # win.table_model.setDataList(dataList)
    # timer = threading.Timer(10, timer_func, (win, dataList2))
    # timer.start()
    app.exec_()