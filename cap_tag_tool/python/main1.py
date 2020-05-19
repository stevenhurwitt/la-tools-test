# -*- coding: utf-8 -*-

# 
#
# Created By: Jose Alvarez 
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys, csv, io, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel
import pyodbc
import pandas as pd
import datetime as dt
import numpy as np
from dateutil.relativedelta import relativedelta
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QMainWindow
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.uic import loadUiType
 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

os.chdir('/media/steven/samsung_t5/la-tools-test/cap_tag_tool/python')

Ui_MainWindow, QMainWindow = loadUiType('window.ui')
Ui_plotNameDialog, QDialog = loadUiType('plotName.ui')
Ui_msgDialog, QDialog = loadUiType('messageBox.ui')
def all_same(items):
    return all(x == items[0] for x in items)

# CONNECTION TO THE ORACLIENT_SQL_SERVER
#cnn = pyodbc.connect('Driver=/etc/odbcinst.ini;DBQ=tppe;Uid=azureuser;Pwd=AzureDF512682!')

""" (('Home', 'Reset original view', 'home', 'home'), ('Back', 'Back to previous view', 'back', 'back'), ('Forward', 'Forward to next view', 'forward', 'forward'), (None, None, None, None), ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'), (None, None, None, None), ('Save', 'Save the figure', 'filesave', 'save_figure')) """

class msgBox(QDialog, Ui_msgDialog):
    def __init__(self,):
        super(msgBox, self).__init__()
        self.setupUi(self)
        
class namePlot(QDialog, Ui_plotNameDialog):
    def __init__(self, plotObj, fig1):
        super(namePlot,self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.pushOK.setAutoDefault(False)
        self.pushOK.setDefault(False)
        self.pushCancel.setAutoDefault(False)
        self.pushCancel.setDefault(False)
        self.plotNameInput.returnPressed.connect(lambda: self.onClickOk(plotObj, fig1))
        self.pushOK.clicked.connect(lambda: self.onClickOk(plotObj, fig1))
        self.pushCancel.clicked.connect(lambda: self.close())
 
    def onClickOk(self, plotObj, fig1):
        _translate = QtCore.QCoreApplication.translate
        strName = self.plotNameInput.text()
        res = plotObj.mplfigs.findItems(strName, Qt.MatchExactly)
        if(strName == ''):
            print("EMPTY!")
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Empty Field. Enter again!"))
            self.msgBox1.show()
        elif(len(res) > 0):
            print("Enter another Name!") 
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Duplicate. Enter another Name!"))
            self.msgBox1.show()
            
        elif(len(res) == 0):
            print("no duplicates")
            plotObj.addfig(strName, fig1)
            self.close()

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.fig_dict = {}
        self.mplfigs.itemClicked.connect(self.changefig)
        self.clearButton.clicked.connect(self.clearList)
        self.actionClearData.triggered.connect(self.clearList)
        self.actionClose.triggered.connect(lambda: self.close())
        fig = Figure()
        self.addmpl(fig)
    
    def changefig(self, item):
        text = item.text()
        self.rmmpl()
        self.addmpl(self.fig_dict[text])
        
    def clearList(self):
#        while(self.mplfigs.count() > 0):
#            self.mplfigs.takeItem()
        self.mplfigs.clear()
        
    def addfig(self, name, fig):
        self.fig_dict[name] = fig
        self.mplfigs.addItem(name)
 
    def addmpl(self, fig):
        
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self,coordinates = True)

        self.addToolBar(self.toolbar)
        self.toolItems = self.toolbar.toolitems
#        print(self.toolItems)
          
    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close() 
        
class Ui_Find(object):
    # THIS CLASS IS THE POP UP FIND/CTRL+F WIDGET USED TO FIND ITEMS IN A TABLE
    # THE UI IS SET UP AS WELL AS THE ALGORITHM THAT STORES THE ITEMS FOUND AND SPANS THROUGH THEM WITH THE
    # NEXT AND PREVIOUS BUTTONS
    def setupUi(self, Find, table):
        Find.setObjectName("Find")
        Find.resize(242, 74)
        Find.setMaximumSize(QtCore.QSize(500, 82))
        font = QtGui.QFont()
        font.setFamily("Arial")
        Find.setFont(font)
        Find.setStyleSheet("background-color: rgb(244, 254, 255);")
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
        self.label_2.setMinimumSize(QtCore.QSize(32, 0))
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
        self.pushButton_2 = QtWidgets.QPushButton(Find)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_4.addWidget(self.pushButton_2, 0, 0, 1, 1)
        
        self.pushButton = QtWidgets.QPushButton(Find)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_4.addWidget(self.pushButton, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_4, 1, 0, 1, 1)
        
        self.pushButton.setAutoDefault(False)
        self.pushButton.setDefault(False)
        self.pushButton_2.setDefault(False)
        self.pushButton_2.setAutoDefault(False)
        self.pushButton_3.setDefault(False)
        self.pushButton_3.setAutoDefault(False)
        
        self.searchClicked = False
        self.pushButton_3.clicked.connect(lambda: self.onClickSearch(table), Qt.UniqueConnection)
        self.pushButton.clicked.connect(lambda: self.onClickNext(table), Qt.UniqueConnection)
        self.pushButton_2.clicked.connect(lambda: self.onClickPrev(table), Qt.UniqueConnection)
        
        self.lineEdit.returnPressed.connect(lambda: self.onClickSearch(table))
        self.lineEdit.setFocusPolicy(Qt.StrongFocus)
        QtWidgets.QShortcut(QtGui.QKeySequence("Alt+d"), self.lineEdit, self.setFocus)
        QtWidgets.QShortcut(Qt.Key_Space, self.lineEdit, self.setFocus)
        QtWidgets.QShortcut(Qt.Key_Up, self.pushButton_2, self.pushButton_2.animateClick)
        QtWidgets.QShortcut(Qt.Key_Down, self.pushButton, self.pushButton.animateClick)
        QtWidgets.QShortcut(Qt.Key_Left, self.pushButton_2, self.pushButton_2.animateClick)
        QtWidgets.QShortcut(Qt.Key_Right, self.pushButton, self.pushButton.animateClick)
        

        self.retranslateUi(Find)
        QtCore.QMetaObject.connectSlotsByName(Find)
        

    def setFocus(self):
        self.lineEdit.setFocus()
        
    def retranslateUi(self, Find):
        _translate = QtCore.QCoreApplication.translate
        Find.setWindowTitle(_translate("Find", "Find Items"))
        self.label.setText(_translate("Find", "Find:"))
        self.label_2.setText(_translate("Find", "0 / 0"))
        self.pushButton_3.setText(_translate("Find", "Search"))
        self.pushButton_2.setText(_translate("Find", "Previous"))
        self.pushButton.setText(_translate("Find", "Next"))
        
    @QtCore.pyqtSlot()    
    def onClickPrev(self, table):
        # THIS SLOT MANAGES THE EVENT OF CLICKING THE PREVIOUS BUTTON IN THE FIND DIALOG BOX
        if self.searchClicked == True:
            _translate = QtCore.QCoreApplication.translate
            self.index -= 1
            # CHECK TO SEE IF ARRAY STORING INDEXES OF ITEMS FOUND WILL BE OUT OF BOUNDS
            if(self.index < 0):
                self.index = self.numResults - 1
                table.selectionModel().clearSelection() # Clear any current selections before selecting found item
                self.label_2.setText(_translate("Find", str((self.index +1)) + " / " + str(self.numResults)))
                table.selectionModel().select(self.matches[self.index], QtCore.QItemSelectionModel.Select)
                table.scrollTo(self.matches[self.index])
            
            # CHECK TO SEE IF ARRAY STORING INDEXES OF ITEMS FOUND WILL BE OUT OF BOUNDS
            elif(self.index >= 0):
                table.selectionModel().clearSelection() # Clear any current selections before selecting found item
                self.label_2.setText(_translate("Find", str((self.index +1)) + " / " + str(self.numResults)))
                table.selectionModel().select(self.matches[self.index], QtCore.QItemSelectionModel.Select)
                table.scrollTo(self.matches[self.index])
        
        
    @QtCore.pyqtSlot()    
    def onClickNext(self, table):
        # THIS SLOT MANAGES THE EVENT OF CLICKING THE ENXT BUTTTON IN THE FIND DIALOG BOX
        if self.searchClicked == True:
            _translate = QtCore.QCoreApplication.translate
            self.index += 1
            
            if(self.index < self.numResults):
                
                table.selectionModel().clearSelection()
                self.label_2.setText(_translate("Find", str((self.index +1)) + " / " + str(self.numResults)))
                table.selectionModel().select(self.matches[self.index], QtCore.QItemSelectionModel.Select)
                table.scrollTo(self.matches[self.index])
                
            elif(self.index == self.numResults):
                self.index = 0
                table.selectionModel().clearSelection()
                self.label_2.setText(_translate("Find", str((self.index +1)) + " / " + str(self.numResults)))
                table.selectionModel().select(self.matches[self.index], QtCore.QItemSelectionModel.Select)
                table.scrollTo(self.matches[self.index])
        
    @QtCore.pyqtSlot()        
    def onClickSearch(self, table):
#        self.pushButton_3.clicked.disconnect()
        _translate = QtCore.QCoreApplication.translate
        text = self.lineEdit.text()
        
        if(text != ''):
            self.searchClicked = True
            model = table.model()
            self.tempList = []
            self.matches = []
            
            self.numOfColumns = model.columnCount()
            for i in range(0,self.numOfColumns):
                                    
                start = model.index(0, i)
                self.tempList = model.match(start, Qt.DisplayRole, text, -1, Qt.MatchContains) 
                if(len(self.tempList) != 0):
                    self.matches.extend(self.tempList)
                self.tempList.clear()
                
                
            self.numResults = len(self.matches)
            
            if(self.numResults == 0):
                self.label_2.setText(_translate("Find", "0 / 0"))
                self.searchClicked = False
            else:
                focused_widget = QApplication.focusWidget()
                focused_widget.clearFocus()
                self.index = 0
                table.selectionModel().clearSelection()
                table.selectionModel().select(self.matches[self.index], QtCore.QItemSelectionModel.Select)
                table.scrollTo(self.matches[self.index])
                self.label_2.setText(_translate("Find", "1 / " + str(self.numResults)))
                
        else:
            
            self.label_2.setText(_translate("Find", "0 / 0"))
            self.searchClicked = False
        
        
            
        
class PandasModel(QtCore.QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if role == Qt.BackgroundRole:
            if index.column() == 3:
                val = QSqlQueryModel.data(self, index(index.row(), 3), Qt.DisplayRole)
                if int(val.value()) < 0:
                    return QtGui.QBrush(Qt.yellow)
        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()



class Ui_MainWindow(object):
    
    def on_key(self, key, table):
        # conditions for specific keys
        if key == QtGui.QKeySequence('Ctrl+f'):
            self.execFind(table)
            
    def setupUi(self, MainWindow, ctx):
        MainWindow.setObjectName("MainWindow")
        
        self.main = Main() # CREATES PLOT MENU
        

        MainWindow.setStyleSheet("background-color: rgb(240, 240, 240); selection-background-color: rgb(24, 124, 255);")
        MainWindow.setIconSize(QtCore.QSize(24, 24))
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.detailTab = QtWidgets.QTabWidget(self.centralwidget)
        self.detailTab.setStyleSheet("")
        self.detailTab.setIconSize(QtCore.QSize(30, 30))
        self.detailTab.setObjectName("detailTab")
        self.controlTab = QtWidgets.QWidget()
        self.controlTab.setObjectName("controlTab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.controlTab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        
        
        self.label = QtWidgets.QLabel(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.controlTab)
        self.lineEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.controlTab)
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        
        self.tabOrder = QWidget(MainWindow) 
        self.tabOrder.setTabOrder(self.lineEdit, self.lineEdit_2)
        self.lineEdit.returnPressed.connect(self.on_click)
        self.lineEdit_2.returnPressed.connect(self.on_click)
        
        ####### PUSH BUTTON ###########
        self.pushButton = QtWidgets.QPushButton(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setWhatsThis("Queries PR# and Rev# from Lodestar PE")
        self.pushButton.setStyleSheet("border-color: rgb(175, 203, 203);\n"
"\n"
"")
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 2)
        self.pushButton.clicked.connect(self.on_click)  # PUSH BUTTON IS CALLED HERE
        self.pushButton.setAutoDefault(True)
        ##################################
        
        self.label_3 = QtWidgets.QLabel(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)
        
        ####### PUSH BUTTON 2 ###########
        self.pushButton_2 = QtWidgets.QPushButton(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 3, 0, 1, 2)
        self.pushButton_2.clicked.connect(self.on_clickOffer)
        self.pushButton_2.setAutoDefault(True)
        ##################################
        
        self.label_4 = QtWidgets.QLabel(self.controlTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        
        ###########  Detail YOY Table  #################
        self.detailYOY = QtWidgets.QTableView(self.controlTab)
        self.detailYOY.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.detailYOY.setDragEnabled(True)
        self.detailYOY.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.detailYOY.setSortingEnabled(True)
        self.detailYOY.setObjectName("detailYOY")
        self.detailYOY.setContextMenuPolicy(Qt.CustomContextMenu)
        self.detailYOY.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.detailYOY))
        self.gridLayout.addWidget(self.detailYOY, 1, 2, 5, 1)
        self.scDetailYOY = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.detailYOY)
        self.scDetailYOY.setContext(Qt.WidgetShortcut)
        self.scDetailYOY.activated.connect(lambda: self.execFind(self.detailYOY))
        self.scDetailYOYcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.detailYOY,lambda: self.copySlot(self.detailYOY))
        self.scDetailYOYcopy.setContext(Qt.WidgetShortcut)
        ################################################
        
        ###########  Capacity Tags Table  #################
        self.capTags = QtWidgets.QTableView(self.controlTab)
        self.capTags.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.capTags.setDragEnabled(True)
        self.capTags.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.capTags.setSortingEnabled(True)
        self.capTags.setObjectName("capTags")
        self.capTags.setContextMenuPolicy(Qt.CustomContextMenu)
        self.capTags.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.capTags.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.capTags.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capTags))
        self.gridLayout.addWidget(self.capTags, 5, 0, 1, 2)
        self.scCapTags = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capTags)
        self.scCapTags.setContext(Qt.WidgetShortcut)
        self.scCapTags.activated.connect(lambda: self.execFind(self.capTags))
        self.scCapTagsCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capTags,lambda: self.copySlot(self.capTags))
        self.scCapTagsCopy.setContext(Qt.WidgetShortcut)


        ###################################################
         
        self.horizontalLayout_3.addLayout(self.gridLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)
        self.detailTab.addTab(self.controlTab, "")
        self.capacityTab = QtWidgets.QWidget()
        self.capacityTab.setObjectName("capacityTab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.capacityTab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.capacityTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        
        ###########  Capacity Table  #################
        self.capacity = QtWidgets.QTableView(self.capacityTab)
        self.capacity.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.capacity.setDragEnabled(True)
        self.capacity.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.capacity.setSortingEnabled(True)
        self.capacity.setObjectName("capacity")
        self.capacity.setContextMenuPolicy(Qt.CustomContextMenu)
        self.capacity.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capacity))
        self.verticalLayout_2.addWidget(self.capacity)
        self.scCapacity = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capacity)
        self.scCapacity.setContext(Qt.WidgetShortcut)
        self.scCapacity.activated.connect(lambda: self.execFind(self.capacity))
        self.scCapacityCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capacity,lambda: self.copySlot(self.capacity))
        self.scCapacityCopy.setContext(Qt.WidgetShortcut)
        ###################################################
        
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.detailTab.addTab(self.capacityTab, "")
        self.detailTab1 = QtWidgets.QWidget()
        self.detailTab1.setObjectName("detailTab1")
        
        self.gridLayout_2 = QtWidgets.QGridLayout(self.detailTab1)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setVerticalSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_6 = QtWidgets.QLabel(self.detailTab1)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 2, 1, 1)
        
        ###########  METER VALUE PR Table  #################
        self.meterValuePR = QtWidgets.QTableView(self.detailTab1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.meterValuePR.sizePolicy().hasHeightForWidth())
        self.meterValuePR.setSizePolicy(sizePolicy)
        self.meterValuePR.setMinimumSize(QtCore.QSize(0, 192))
        #self.meterValuePR.setMaximumSize(QtCore.QSize(600, 1080))
        self.meterValuePR.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.meterValuePR.setDragEnabled(True)
        self.meterValuePR.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.meterValuePR.setSortingEnabled(True)
        self.meterValuePR.setObjectName("meterValuePR")
        self.meterValuePR.setContextMenuPolicy(Qt.CustomContextMenu)
        self.meterValuePR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterValuePR))
        self.gridLayout_2.addWidget(self.meterValuePR, 1, 0, 1, 2)
        self.scMeterValuePR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterValuePR)
        self.scMeterValuePR.setContext(Qt.WidgetShortcut)
        self.scMeterValuePR.activated.connect(lambda: self.execFind(self.meterValuePR))
        self.scMeterValuePRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterValuePR,lambda: self.copySlot(self.meterValuePR))
        self.scMeterValuePRcopy.setContext(Qt.WidgetShortcut)
        ####################################################
        
        ###########  METER Reads PR Table  #################
        self.meterReadPR = QtWidgets.QTableView(self.detailTab1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.meterReadPR.sizePolicy().hasHeightForWidth())
        self.meterReadPR.setSizePolicy(sizePolicy)
        self.meterReadPR.setMinimumSize(QtCore.QSize(640, 192))
        self.meterReadPR.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.meterReadPR.setDragEnabled(True)
        self.meterReadPR.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.meterReadPR.setSortingEnabled(True)
        self.meterReadPR.setObjectName("meterReadPR")
        self.meterReadPR.setContextMenuPolicy(Qt.CustomContextMenu)
        self.meterReadPR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterReadPR))
        self.gridLayout_2.addWidget(self.meterReadPR, 1, 2, 1, 1)
        self.scMeterReadPR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterReadPR)
        self.scMeterReadPR.activated.connect(lambda: self.execFind(self.meterReadPR))
        self.scMeterReadPR.setContext(Qt.WidgetShortcut)
        self.scMeterReadPRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterReadPR,lambda: self.copySlot(self.meterReadPR))
        self.scMeterReadPRcopy.setContext(Qt.WidgetShortcut)
        ####################################################
        
        
        
        self.label_7 = QtWidgets.QLabel(self.detailTab1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 0, 0, 1, 2)
        self.detailTab.addTab(self.detailTab1, "")
        self.horizontalLayout.addWidget(self.detailTab)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 834, 21))

        font = QtGui.QFont()
        font.setFamily("Arial")
        
        self.menuBar.setFont(font)
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.menuFile.setFont(font)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        ######## MENU BAR ACTION TO QUIT #########
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.triggered.connect(QtWidgets.QApplication.quit)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.actionQuit.setFont(font)
        self.actionQuit.setObjectName("actionQuit")
        ###########################################
        self.menuFile.addAction(self.actionQuit)
        self.menuBar.addAction(self.menuFile.menuAction())
        
       
        # Creates empty Tables at Pop up and appropiately sets the empty model to each QtableView
        emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
        emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'Delta'])
        emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                           'TAG_TYPE','TAG','Strip'])
        emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                            'ONPEAK_KWH','PEAKDEMAND'])
        emptyMeterReads = pd.DataFrame(columns = ['TIMESTAMP', 'ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
        
        self.capTags.setModel(PandasModel(emptyCapTags))
        self.capacity.setModel(PandasModel(emptyCap))
        self.detailYOY.setModel(PandasModel(emptydetailYOY))
        self.meterReadPR.setModel(PandasModel(emptyMeterReads))
        self.meterValuePR.setModel(PandasModel(emptyMeterVal))
        ###################################################################################################

        self.retranslateUi(MainWindow)
        self.detailTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Capacity Tag Tool"))
        self.label_3.setText(_translate("MainWindow", "Current PR: "))
        self.label.setText(_translate("MainWindow", "PR# :"))
        self.label_2.setText(_translate("MainWindow", "Revision# :"))
        self.pushButton.setText(_translate("MainWindow", "Click To Produce Capacity Tags"))
        self.label_4.setText(_translate("MainWindow", "Detail YOY"))
        self.pushButton_2.setText(_translate("MainWindow", "Copy OFFER_% to Clipboard"))
        self.detailTab.setTabText(self.detailTab.indexOf(self.controlTab), _translate("MainWindow", "Control"))
        self.label_5.setText(_translate("MainWindow", "OVERALL DATA"))
        self.detailTab.setTabText(self.detailTab.indexOf(self.capacityTab), _translate("MainWindow", "Capacity"))
        self.label_6.setText(_translate("MainWindow", "Meter - Reads:"))
        self.label_7.setText(_translate("MainWindow", "Meter - Values Info:"))
        self.detailTab.setTabText(self.detailTab.indexOf(self.detailTab1), _translate("MainWindow", "Detail"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))

    def makeCaptags(self, data):
               

        # data.to_clipboard(index=False) # copying dataframe to clipboard
        
        data['STOPTIME'] = pd.to_datetime(data['STOPTIME'])     # Convert date-type to only display Date w/o time
        data['STOPTIME'] = data['STOPTIME'].dt.date
        data['STARTTIME'] = pd.to_datetime(data['STARTTIME'])   # Convert date-type to only display Date w/o time
        data['STARTTIME'] = data['STARTTIME'].dt.date
        # topdata = data.head() # Returns the top n (5 by default) rows of a data frame or series
        # QUESTION!! Why do this? are you trying to get the top of (like just on top), or top 5 by tag Quantity?
        
        
        if("NYISO" in data.MARKETCODE.values):
            
            startDateOrig = dt.date(2016,1,1)
            endDateOrig = dt.date(2017,1,1)
            startDate = dt.date(2016,1,1)
            endDate = dt.date(2017,1,1)
            
            lastPlanYear = dt.date(2024,1,1)  ## CHANGE HERE UNTIL WHAT PLAN YEAR
            rangeY = lastPlanYear - startDate
            rangeY = (rangeY.days/365)
            rangeY = int(rangeY)
            capTags = capTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag', 'Transmission', 'Accounts'])
            for i in range(rangeY):
                
                if i == 0:
                    startDate = startDate + relativedelta(months = 4) # STARTS IN MAY
                    endDate = endDate + relativedelta(months = 4) - relativedelta(days = 1) # ENDS UNTIL LAST OF APRIL
                    
                maskAccts = (data['STARTTIME'] <= (startDateOrig + relativedelta(months = 4))) & (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD') & (data['STOPTIME'] >=  (endDateOrig + relativedelta(months = 4) - relativedelta(days = 1)))# For NYISO MAY -> APRIL
                acctCount = len(data.loc[maskAccts].index)
                    
                if(("NYISO" in data.MARKETCODE.values) | ("NEPOOL" in data.MARKETCODE.values)):
                        
                    transVal = "N/A"
                else:
                    
                    maskTrans = (data['STARTTIME'] <= startDateOrig) & (data['STOPTIME'] >= endDateOrig - relativedelta(days = 1)) & (data['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD')
                    df2 = data.loc[maskTrans]
                    transVal = df2['TAG'].sum()
                    
                startDateOrig = startDateOrig + relativedelta(years = 1)
                endDateOrig = endDateOrig + relativedelta(years = 1)
                    
                    
                maskCap = (data['STARTTIME'] <= startDate) & (data['STOPTIME'] >= endDate) & (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD')
                df1 = data.loc[maskCap]
                capTag = df1['TAG'].sum()
                planYear = "May " + str(startDate.year) + " - " + "April " + str(endDate.year)
                capTags = capTags.append(pd.Series([planYear, capTag, transVal, acctCount], index = capTags.columns), ignore_index = True)
                startDate = startDate + relativedelta(years = 1)
                endDate = endDate + relativedelta(years = 1)
                acctCount = 0
                
        else:
            
            startDateOrig = dt.date(2016,1,1)
            endDateOrig = dt.date(2017,1,1)
            startDate = dt.date(2016,1,1)
            endDate = dt.date(2017,1,1)
            lastPlanYear = dt.date(2024,1,1)  ## CHANGE HERE UNTIL WHAT PLAN YEAR
            rangeY = lastPlanYear - startDate
            rangeY = (rangeY.days/365)
            rangeY = int(rangeY)
            capTags = capTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag', 'Transmission', 'Accounts'])
            for i in range(rangeY):
                
                if i == 0:
                    startDate = startDate + relativedelta(months = 5)
                    endDate = endDate + relativedelta(months = 5) - relativedelta(days = 1)
    
                maskAccts = (data['STARTTIME'] <= (startDateOrig + relativedelta(months = 5))) & (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD') & (data['STOPTIME'] >=  (endDateOrig + relativedelta(months = 5) - relativedelta(days = 1)))# FOR NOT(NYISO) JUNE -> MAY
                acctCount = len(data.loc[maskAccts].index)
        
                if(("NYISO" in data.MARKETCODE.values) | ("NEPOOL" in data.MARKETCODE.values)):
        
                    transVal = "N/A"
                else:
                    
                    maskTrans = (data['STARTTIME'] <= startDateOrig) & (data['STOPTIME'] >= endDateOrig - relativedelta(days = 1)) & (data['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD')
                    df2 = data.loc[maskTrans]
                    transVal = df2['TAG'].sum()
        
    
                startDateOrig = startDateOrig + relativedelta(years = 1)
                endDateOrig = endDateOrig + relativedelta(years = 1)
                        
                maskCap = (data['STARTTIME'] <= startDate) & (data['STOPTIME'] >= endDate) & (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD')
                df1 = data.loc[maskCap]
                capTag = df1['TAG'].sum()
                planYear = "June " + str(startDate.year) + " - " + "May " + str(endDate.year)
                capTags = capTags.append(pd.Series([planYear, capTag, transVal, acctCount], index = capTags.columns), ignore_index = True)
                startDate = startDate + relativedelta(years = 1)
                endDate = endDate + relativedelta(years = 1)
                acctCount = 0
        #capTags['Capacity Tag'] = capTags['Capacity Tag'].round(decimals = 2)
        capTags['Capacity Tag'] = capTags.apply(lambda x: "{:,.2f}".format(x['Capacity Tag']), axis=1)
        
        model = PandasModel(capTags)
        return model
        
    def getData(self, prNum, revNum, roundOrNot):
        # ------------------------------------
        # SQL query
        # ------------------------------------

        sqlQuery = ("""
        SELECT 
    DISTINCT A.*,
    B.starttime,
    B.stoptime,
    B.overridecode AS Tag_Type,
    B.val AS Tag
    
FROM pwrline.acctoverridehist B,
(SELECT 
    DISTINCT F.name AS CustomerName,
    F.Customerid,
    B.name as LDC_Account,
    B.Accountid,
    D.uidaccount,
    D.marketcode,
    A.Contractid,
    A.Revision,
    PC.PROFILECODE,
    PC.PROFILENAME,
    LC.LOSSCODE|| '-' || LC.LOSSNAME AS LOSS_CLASS
FROM 
    pwrline.account B,
    pwrline.lscmcontract A,
    pwrline.lscmcontractitem C, 
    pwrline.acctservicehist D,
    pwrline.customer F, 
    pwrline.profileclass PC,
    pwrline.lossclass LC
WHERE
    C.uidcontract = A.uidcontract
    AND C.uidaccount=B.uidaccount
    AND B.uidaccount=D.uidaccount
    AND D.UIDPROFILECLASS = PC.uidprofileclass
    AND D.uidlossclass = LC.uidlossclass
    AND A.contractid = '{prNum}' 
    AND A.revision = '{revNum}' 
    AND  B.uidcustomer=F.uidcustomer) A
WHERE 
    A.uidaccount=B.uidaccount
    AND (A.marketcode='PJM'
    OR A.marketcode='NEPOOL'
    OR A.marketcode= 'NYISO'
    OR A.marketcode= 'MISO')
    AND (B.overridecode = 'TRANSMISSION_TAG_OVRD'
    OR B.overridecode='CAPACITY_TAG_OVRD'
    OR B.overridecode='VEE_COMPLETE_OVRD'
    OR B.overridecode='FT_FUEL_SOURCE')
ORDER BY 
    A.customername,
    B.overridecode,
    A.accountid,
    B.starttime
 
        """).format(prNum=prNum, revNum=revNum)
    
        #  1-BRHNXP+    
        # -------------------------------------
    
        # ------------------------------------- {:,.2f}
        
        data = pd.read_sql(sqlQuery, cnn)
        if roundOrNot == 1:
            data = data.fillna(value = 0)
            data['TAG'] = data.apply(lambda x: "{:,.2f}".format(x['TAG']), axis=1)
            data.replace([0,0.0],'',inplace = True)
            return data
        elif roundOrNot == 2:
            return data
    
    def detailYOYfunc(self, data):
            #### DETAIL YOY TAB ####
    
        tagDF_DM = data
        tagDF_DM['CUSTOMERNAME'].replace('', np.nan, inplace=True) # CONVERTS ANY EMPTY CELLS TO "nan"
        tagDF_DM.dropna(subset = ['CUSTOMERNAME'], inplace = True) # DROPS ANY "nan" values
        tagDF_DM['STARTTIME'] = pd.to_datetime(tagDF_DM['STARTTIME'])
        tagDF_DM['STOPTIME'] = pd.to_datetime(tagDF_DM['STOPTIME'])
        tagDF_DM['Strip'] = tagDF_DM['STARTTIME'].dt.strftime("%Y") + ' - ' + tagDF_DM['STOPTIME'].dt.strftime("%Y")
        
        # replaces empty spots with 'nan'
        # fills in null cells with 0
        tagDF_DM['TAG'].fillna(value = 0)
        tagDF_DM['TAG'].replace('', np.nan, inplace=True)
        tagDF_DM['TAG'].replace('nan', np.nan, inplace=True)
        tagDF_DM['TAG'].replace(np.nan, 0, inplace=True)
        maskCapTagOvrd = (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD') # Mask Filter Tag Type by Capacity Tag Ovrd
        tagDF_DM = tagDF_DM.loc[maskCapTagOvrd] # Apply Mask Filter
        
        tagDF_DM['STOPTIME'] = pd.to_datetime(tagDF_DM['STOPTIME'])     # Convert date-type to only display Date w/o time
        tagDF_DM['STOPTIME'] = tagDF_DM['STOPTIME'].dt.date
        tagDF_DM['STARTTIME'] = pd.to_datetime(tagDF_DM['STARTTIME'])   # Convert date-type to only display Date w/o time
        tagDF_DM['STARTTIME'] = tagDF_DM['STARTTIME'].dt.date
        
        pivTab = pd.pivot_table(tagDF_DM, columns = ['Strip'], index = ['CUSTOMERNAME','CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','STARTTIME','STOPTIME'], values = ['TAG'], aggfunc = np.sum)
        pivTab = pivTab.reset_index(drop = True) # resets indexes back to normal
        # pivTab.columns = pivTab.columns.get_level_values(1)
        pivTab.columns = pivTab.columns.droplevel() # eliminates renaming problem in columns
        
        
        tagDF_DM = pd.concat([tagDF_DM, pivTab], axis = 1, sort = False)
        detailYOY = pd.pivot_table(tagDF_DM,index = ['ACCOUNTID'], columns = ['Strip'], values = ['2018 - 2019', '2019 - 2020']) # , margins = True, margins_name = 'Total', aggfunc = sum
        detailYOY.columns = detailYOY.columns.droplevel() 
        detailYOY = detailYOY.fillna(value = 0)
        
        detailYOY['Delta'] = detailYOY['2018 - 2019'] - detailYOY['2019 - 2020']
        detailYOY = detailYOY.append(detailYOY.sum().rename('GRAND TOTAL'))
        detailYOY = detailYOY.reset_index(drop = False)
        
        
        detailYOY['Delta'] = detailYOY.apply(lambda x: "{:,.2f}".format(x['Delta']), axis=1)
        detailYOY['2018 - 2019'] = detailYOY.apply(lambda x: "{:,.2f}".format(x['2018 - 2019']), axis=1)
        detailYOY['2019 - 2020'] = detailYOY.apply(lambda x: "{:,.2f}".format(x['2019 - 2020']), axis=1)
        
        detailYOY.replace([0,0.0],'',inplace = True)
        model = PandasModel(detailYOY)
        
        return model
       
        
    def meterValue(self, prNum, revNum):
        """  SQL QUERY TO BRING IN DATA TO THE METER VALUE (PR) POWER QUERY  """

        sqlQuery = ("""
                    WITH meter_value AS
                    ( 
                            SELECT 
                            a.uidaccount AS account_join_id,
                            a.name LDC_ACCOUNT,
                            a.ACCOUNTID,
                            mv.* 
                            FROM account a 
                            INNER JOIN metervalue mv on a.uidaccount = mv.uidaccount)
                    SELECT mv.*
                    FROM ( 
                            SELECT DISTINCT
                            B.name AS LDC_Account,
                            B.Accountid,
                            D.uidaccount
                            FROM 
                            pwrline.account B,
                            pwrline.lscmcontract A,
                            pwrline.lscmcontractitem C,
                            pwrline.acctservicehist D,
                            pwrline.customer F
                            WHERE
                            C.uidcontract=A.uidcontract
                            AND C.uidaccount=B.uidaccount
                            AND B.uidaccount=D.uidaccount 
                            AND B.uidcustomer=F.uidcustomer 
                            AND a.contractid = '{prNum}' 
                            AND a.revision = '{revNum}'   
                            ) oa 
                            INNER JOIN meter_value mv on oa.uidaccount = mv.account_join_id 
                            
        """).format(prNum=prNum, revNum=revNum)
        
        meterVal = pd.read_sql(sqlQuery, cnn)
        meterVal['STARTTIME'] = pd.to_datetime(meterVal['STARTTIME'])
        meterVal['STOPTIME'] = pd.to_datetime(meterVal['STOPTIME'])
        meterVal['READDATE'] = pd.to_datetime(meterVal['READDATE'])
        meterVal['Strip'] = meterVal['STARTTIME'].dt.strftime("%Y") + ' - ' + meterVal['STOPTIME'].dt.strftime("%Y")
        
        
        metValPiv2 = pd.pivot_table(meterVal, columns = ['NAME'], index = ['ACCOUNT_JOIN_ID','LDC_ACCOUNT','ACCOUNTID',
                                    'UIDACCOUNT','READDATE','UIDBILLDETERMINANT','STARTTIME','STOPTIME',
                                    'STRVAL','LSUSER', 'LSTIME','Strip'], values = ['VAL'], aggfunc = np.sum)
        metValPiv2.columns = metValPiv2.columns.droplevel()
        metValPiv2 = metValPiv2.reset_index(drop = False) # Resets Index and eliminates Multiindexing while also renaming columns automatically
        
        metValPiv2['STARTTIME'] = pd.to_datetime(metValPiv2['STARTTIME'])
        metValPiv2['STOPTIME'] = pd.to_datetime(metValPiv2['STOPTIME'])
        metValPiv2['READDATE'] = pd.to_datetime(metValPiv2['READDATE'])
        
        #metValPiv['STARTTIME'] = metValPiv['STARTTIME'].dt.date
        #metValPiv['STOPTIME'] = metValPiv['STOPTIME'].dt.date
        #metValPiv['READDATE'] = metValPiv['READDATE'].dt.date
        
        metValPiv2 =metValPiv2[['ACCOUNT_JOIN_ID','LDC_ACCOUNT','ACCOUNTID',
                                'UIDACCOUNT','READDATE','UIDBILLDETERMINANT','STARTTIME','STOPTIME',
                                'STRVAL','LSUSER', 'LSTIME','Strip',
                                'ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND']]
        
        
        filter = (metValPiv2.STARTTIME.dt.year >= 2018)
        metValPiv2.where(filter, inplace = True)
        metValPiv2 = metValPiv2.dropna(subset = ['ACCOUNTID'])
        metValPiv2 = metValPiv2.fillna(value = 0)
        
        metValPiv2 = metValPiv2.loc[(metValPiv2.ANNUAL_KWH != 0 ) | ( metValPiv2.LOADFACTOR != 0 )|  (metValPiv2.AVERAGEDEMAND != 0) | (metValPiv2.ONPEAK_KWH != 0) | ( metValPiv2.OFFPEAK_KWH != 0) | (metValPiv2.PEAKDEMAND != 0)]
        metValPiv2 = metValPiv2.dropna(subset = ['ACCOUNTID'])
        meterValfin1_1 = pd.pivot_table(metValPiv2, index = ['Strip', 'ACCOUNTID'], values = ['ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND'],fill_value = 0, aggfunc = np.sum)
        meterValFIN= meterValfin1_1.reset_index(drop = False)
        
        metValPiv2 = metValPiv2.melt(id_vars = ['ACCOUNT_JOIN_ID','LDC_ACCOUNT','ACCOUNTID',
                                                'UIDACCOUNT','READDATE','UIDBILLDETERMINANT','STARTTIME','STOPTIME',
                                                'STRVAL','LSUSER', 'LSTIME','Strip'],
                    var_name = 'NAME',
                    value_name = 'VALUE')
        
        
        meterValfin2_1 = pd.pivot_table(metValPiv2, index = ['Strip', 'ACCOUNTID','NAME'], values = ['VALUE'],fill_value = 0, aggfunc = np.sum)
        meterValfin2_2 = meterValfin2_1.reset_index(drop = False)
        
        meterValFIN.loc[:,['ANNUAL_KWH','OFFPEAK_KWH','ONPEAK_KWH']] /= 1000
        meterValFIN.loc[:,['LOADFACTOR']] *= 100
        meterValFIN['LOADFACTOR'] = meterValFIN.apply(lambda x: "{:,.2f}%".format(x['LOADFACTOR']), axis=1) 
        meterValFIN['ANNUAL_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ANNUAL_KWH']), axis=1)
        meterValFIN['OFFPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['OFFPEAK_KWH']), axis=1)
        meterValFIN['ONPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ONPEAK_KWH']), axis=1)
        meterValFIN['AVERAGEDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['AVERAGEDEMAND']), axis=1)
        meterValFIN['PEAKDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['PEAKDEMAND']), axis=1)
        meterValFIN = meterValFIN.rename(columns = {"ACCOUNTID":"Account ID", "ANNUAL_KWH" : "Annual MWHs", "OFFPEAK_KWH" : "OffPeak MWHs","ONPEAK_KWH" : "OnPeak MWHs","LOADFACTOR" : "Load Factor (%)","AVERAGEDEMAND" : "AVG Demand (KWHs)", "PEAKDEMAND": "Peak Demand (KWHs)"})
        
        model = PandasModel(meterValFIN)
        #print(model)
        return model
        
    
    def meterRead(self, prNum, revNum):
        sqlQuery = ("""
                    WITH meter_read AS
                    ( 
                    SELECT
                        a.name LDC_ACCOUNT,
                        a.ACCOUNTID,
                        a.UIDACCOUNT AS account_join_id,
                        mh.LSTIME AS TIMESTAMP,
                        CASE WHEN mr.PROFILESTATUSFLAG = 'Y' 
                        THEN 'PROFILED' 
                        WHEN mr.PROFILESTATUSFLAG = 'N'
                        THEN 'SCALAR'
                        ELSE NULL 
                        END AS PROFILE_OR_SCALAR,
                        mr.STARTREADTIME,
                        mr.STOPREADTIME,
                        mr.STARTREADING,
                        mr.STOPREADING,
                        mr.PEAKTIME,
                        mr.PEAKVALUE
                    FROM PWRLINE.ACCOUNT a 
                        INNER JOIN PWRLINE.METERHISTORY mh 
                        ON a.UIDACCOUNT = mh.UIDACCOUNT
                        AND a.LSTIME = mh.LSTIME
                        INNER JOIN PWRLINE.METERREAD mr 
                        ON mh.UIDMETER = mr.UIDMETER
                    WHERE
                        mr.STARTREADTIME >= add_months(trunc(sysdate,'month'),-12) 
                        AND mr.STARTREADTIME < trunc(sysdate, 'month')
                    )
                    SELECT
                        mr.*
                    FROM ( select distinct  B.name as LDC_Account, B.Accountid,
                          D.uidaccount
                          FROM 
                              pwrline.account B,
                              pwrline.lscmcontract A,
                              pwrline.lscmcontractitem C, 
                              pwrline.acctservicehist D,
                              pwrline.customer F 
                          WHERE 
                              C.uidcontract=A.uidcontract
                              AND C.uidaccount=B.uidaccount
                              AND B.uidaccount=D.uidaccount 
                              AND B.uidcustomer=F.uidcustomer
                              AND A.contractid = '{prNum}' 
                              AND A.revision = '{revNum}'  
                          ) 
                        oa INNER JOIN meter_read mr 
                        ON oa.uidaccount = mr.account_join_id
        """).format(prNum=prNum, revNum=revNum)
        
        meterRead = pd.read_sql(sqlQuery, cnn)
        
        
        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME'])
        meterReadpiv = pd.pivot_table(meterRead,index = ['ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME'],values =['STOPREADING'])
        
        meterReadpiv2 = meterReadpiv.reset_index(drop = False)
        meterReadpiv2 = meterReadpiv2.rename(columns = {'ACCOUNTID':'Account ID','PROFILE_OR_SCALAR':'Profile/Scalar',
                                                        'STARTREADTIME':'Start Read Time','STOPREADING':'Stop Read Value'})
    
        meterReadpiv2['Start Read Time'] = pd.to_datetime(meterReadpiv2['Start Read Time'])
        meterReadpiv2['Stop Read Value'] = meterReadpiv2['Stop Read Value'].astype(int)
        #meterReadpiv2['Start Read Time'] = meterReadpiv2['Start Read Time'].dt.date
        meterReadpiv2['Start Read Time'] = meterReadpiv2['Start Read Time'].dt.strftime('%m/%d/%Y')
        
        meterReadpiv2[['Account ID']] = meterReadpiv2[['Account ID']].where(meterReadpiv2[['Account ID']].apply(lambda x: x!= x.shift()),'')
        meterReadpiv2.loc[meterReadpiv2['Account ID'] == '', 'Profile/Scalar'] = ''
        meterReadpiv2['Stop Read Value'] = meterReadpiv2.apply(lambda x: "{:,}".format(x['Stop Read Value']), axis=1)
        model = PandasModel(meterReadpiv2)
        return model
    
    def on_clickOffer(self):
        
        prNum = self.lineEdit.text()
        prNum = prNum.strip()
        offerNum = 'OFFER_' + prNum + '%'
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText(offerNum, mode=cb.Clipboard)
        
    def on_click(self):
        
        _translate = QtCore.QCoreApplication.translate
        prNum = self.lineEdit.text()
        revNum = self.lineEdit_2.text()
        
        prNum = prNum.strip()
        revNum = revNum.strip()
        if(prNum == "" or revNum == ""):
            
            emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
            emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'Delta'])
            emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                               'TAG_TYPE','TAG','Strip'])
            emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                                   'ONPEAK_KWH','PEAKDEMAND'])
            emptyMeterReads = pd.DataFrame(columns = ['TIMESTAMP', 'ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
            self.label_3.setText(_translate("MainWindow", "Current PR: "))
            self.capTags.setModel(PandasModel(emptyCapTags))
            self.capacity.setModel(PandasModel(emptyCap))
            self.detailYOY.setModel(PandasModel(emptydetailYOY))
            self.meterReadPR.setModel(PandasModel(emptyMeterReads))
            self.meterValuePR.setModel(PandasModel(emptyMeterVal))
        else:
            self.label_3.setText(_translate("MainWindow", "Current PR:     " + prNum + "     Rev.     " + revNum))
            font = QtGui.QFont()
            font.setBold(True)
            font.setWeight(75)
            dataMrounded = self.getData(prNum, revNum, 1)
            dataM = self.getData(prNum, revNum, 2)
            dataMpd = PandasModel(dataMrounded)
            self.capacity.setModel(dataMpd)
            self.capacity.setAlternatingRowColors(True)
            self.capacity.horizontalHeader().setFont(font)
            capTagsM = self.makeCaptags(dataM)
            self.capTags.setModel(capTagsM)
            self.capTags.setAlternatingRowColors(True)
            self.capTags.setStyleSheet("alternate-background-color: #f0c9cc;background-color: #ffffff;selection-background-color: #cb4851")
            
            
            self.capTags.horizontalHeader().setFont(font)
            self.capTags.setColumnWidth(0, ((self.capTags.columnWidth(0)+self.capTags.columnWidth(1)+self.capTags.columnWidth(2)+self.capTags.columnWidth(3))/4)+40);
            detailYOYM = self.detailYOYfunc(dataM)
            self.detailYOY.setModel(detailYOYM)
            self.detailYOY.setAlternatingRowColors(True)
            self.detailYOY.setColumnWidth(0,200)
            self.detailYOY.horizontalHeader().setFont(font)
            self.detailYOY.setStyleSheet("alternate-background-color:#daf1f9;background-color: #ffffff;selection-background-color: #1b83a7")
            meterValueM = self.meterValue(prNum, revNum)
            self.meterValuePR.setModel(meterValueM)
            self.meterValuePR.setAlternatingRowColors(True)
            self.meterValuePR.setStyleSheet("alternate-background-color:#daf1f9;background-color: #ffffff;selection-background-color: #1b83a7")
            self.meterValuePR.setColumnWidth(0,70)
            self.meterValuePR.setColumnWidth(1,185)
            self.meterValuePR.setColumnWidth(3,130)
            self.meterValuePR.setColumnWidth(7,130)
            self.meterValuePR.horizontalHeader().setFont(font)
            meterReadM = self.meterRead(prNum, revNum)
            self.meterReadPR.setModel(meterReadM)
            self.meterReadPR.setAlternatingRowColors(True)
            self.meterReadPR.setColumnWidth(0,185)
            self.meterReadPR.horizontalHeader().setFont(font)
            self.meterReadPR.setStyleSheet("alternate-background-color: #f0c9cc;background-color: #ffffff;selection-background-color: #cb4851")
    def contextMenuEvent(self, table):
        #QtWidgets.QWidget(MainWindow) 
        
        self.menu = QMenu(MainWindow) 
        copyAction = self.menu.addAction("Copy     Ctrl+C") # context menu action added
        findAction = self.menu.addAction("Find       Ctr+F") # context menu action added
        plotAction = self.menu.addMenu("Plot Menu")
        plotList = plotAction.addAction("Add to Plot List")
        plot = plotAction.addAction("Plot")
        index = table.selectionModel().currentIndex() # Current Index
        row = index.row() # gets index of current row selected in table
        col = index.column()  # gets index of current column selected in table

        copyAction.triggered.connect(lambda: self.copySlot(table)) # when copy button is pressed, call copySlot function

        findAction.triggered.connect(lambda: self.execFind(table)) # when find button is pressed, call execFind Function to open a Find Window
        
        plot.triggered.connect(self.plotSlot)
        plotList.triggered.connect(lambda: self.addList(table)) # when plot button is pressed, call plotslot function
        
        # add other required actions
        self.menu.popup(QtGui.QCursor.pos()) # Pops custom context menu to cursor's position
    
    def execFind(self, table):
        # THIS FUNCTION OPENS A NEW WINDOW WITH A FIND FUNCTIONALITY #
        
        self.findDialog = Ui_Find()
        self.findWindow = QtWidgets.QDialog() # New Window is created
        
        self.findDialog.setupUi(self.findWindow, table) # UI of the new  window is set up and find is started concurrently
        self.findWindow.show() # Show find window   
    
    def plotSlot(self):
        self.main.show()
    
    def addList(self, table):

        selection = table.selectedIndexes()
        if selection:
            
            listP = []
            rows = sorted(index.row() for index in selection) # returns a list of rows
            columns = sorted(index.column() for index in selection) # returns a list of columns
            cond = all_same(columns)
            headerName = str(table.model().headerData(columns[0], Qt.Horizontal)) ## ADD CONDITION HERE IF NAME EXISTS ALREADY,
            ## ASK USER FOR NAME? OR JUST RENAME IT CONVENTIONALLY?
            if (cond == True):
                rowcount = rows[-1] - rows[0] + 1
                colcount = columns[-1] - columns[0] + 1
                table1 = [[''] * colcount for _ in range(rowcount)]
                for index in selection:
                    row = index.row() - rows[0]
                    column = index.column() - columns[0]
                    table1[row][column] = index.data()
                    val = index.data()
                    listP.append(float(val.replace(',','')))
                fig1 = Figure()
                ax1f1 = fig1.add_subplot(111)
                ax1f1.plot(listP)
                # Don't allow the axis to be on top of your data
                ax1f1.set_axisbelow(True)
                
                # Turn on the minor TICKS, which are required for the minor GRID
                ax1f1.minorticks_on()
                
                # Customize the major grid
                ax1f1.grid(which='major', linestyle='-', linewidth='0.4', color='red')
                # Customize the minor grid
                ax1f1.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
                
                self.namePlot = namePlot(self.main, fig1)
                self.namePlot.show()
                self.namePlot.plotNameInput.setFocusPolicy(Qt.StrongFocus)
                self.namePlot.plotNameInput.setFocus()
            else:
                # CREATE DIALOG SAYING ONLY SELECT ON COLUMNS
                print("ERROR!")
                self.msgBox1 = msgBox()
                self.msgBox1.text.setText(("Only Columns Allowed!"))
                self.msgBox1.show()
            
    
    def copySlot(self, table):
        # get the text inside selected cell (if any)
#        cell = table.model().index(row,col).data()
#        
#        
#        
#         # Copies Text to clipboard
#        cb = QApplication.clipboard()
#        cb.clear(mode=cb.Clipboard )
#        cb.setText(cell, mode=cb.Clipboard)
        
        selection = table.selectedIndexes()
        if selection:
            result = 0
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table1 = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table1[row][column] = index.data()
                val = index.data()
                result += float(val.replace(',',''))
            print (result)
            stream = io.StringIO()
            csv.writer(stream, dialect = 'excel-tab').writerows(table1)
            QApplication.clipboard().setText(stream.getvalue())
            

        
if __name__ == "__main__":
    
    appctxt = ApplicationContext()
    MainWindow = QtWidgets.QMainWindow() # Creates Window
    ui = Ui_MainWindow() # Creates Object of Our Application Class
    ui.setupUi(MainWindow, appctxt) # UI is setup
    appctxt.app.setStyle('Fusion') # Fusion style
    MainWindow.showMaximized() 
    sys.exit(appctxt.app.exec_()) 

