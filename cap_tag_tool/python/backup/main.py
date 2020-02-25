# -*- coding: utf-8 -*-

# 
#
# Created By: Jose Alvarez 
import locale
import datetime
locale.setlocale(locale.LC_ALL, '')
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys, csv, io
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel
import pyodbc
import pandas as pd
import datetime as dt
import numpy as np
import math
from dateutil.relativedelta import relativedelta
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QMainWindow, QDialog
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.uic import loadUiType
 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from window import Ui_MainPlotWindow
from plotName import  Ui_plotNameDialog
from messageBox import Ui_msgDialog
from findBox import Ui_Find
from mainCapTool import Ui_MainWindow
from columnsF import Ui_Columns
from MainWindowCalculator import Ui_MainWindowCalculator
import operator
READY = 0
INPUT = 1

#Ui_MainPlotWindow, QMainWindow = loadUiType('window.ui') # PLOT TOOL WINDOW
#Ui_plotNameDialog, QDialog = loadUiType('plotName.ui') # DIALOG TO NAME PLOTS
#Ui_msgDialog, QDialog = loadUiType('messageBox.ui') # DIALOG BOX TO DISPLAY CUSTOM MESSAGES/WARNINGS
#Ui_Find, QDialog = loadUiType('findBox.ui') # DIALOG TO FIND ITEMS
#Ui_MainWindow, QMainWindow = loadUiType('mainCapTool.ui') # MAIN WINDOW
#Ui_Columns, QWidget = loadUiType('columnsF.ui') # MAIN WINDOW
def Union(lst1, lst2, lst3,lst4,lst5,lst6): 
    final_list = sorted(list(set().union(lst1, lst2, lst3,lst4,lst5,lst6))) 
    return final_list
def Average(lst): 
    return sum(lst) / len(lst) 

def all_same(items):
    return all(x == items[0] for x in items)

# CONNECTION TO THE ORACLIENT_SQL_SERVER
cnn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};DBQ=tppe;Uid=azureuser;Pwd=AzureDF512682!')

""" (('Home', 'Reset original view', 'home', 'home'), ('Back', 'Back to previous view', 'back', 'back'), ('Forward', 'Forward to next view', 'forward', 'forward'), (None, None, None, None), ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'), (None, None, None, None), ('Save', 'Save the figure', 'filesave', 'save_figure')) """

class calculator(QMainWindow, Ui_MainWindowCalculator):
    def __init__(self, *args, **kwargs):
        super(calculator, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Setup numbers.
        for n in range(0, 10):
            getattr(self, 'pushButton_n%s' % n).pressed.connect(lambda v=n: self.input_number(v))

        # Setup operations.
        self.pushButton_add.pressed.connect(lambda: self.operation(operator.add))
        self.pushButton_sub.pressed.connect(lambda: self.operation(operator.sub))
        self.pushButton_mul.pressed.connect(lambda: self.operation(operator.mul))
        self.pushButton_div.pressed.connect(lambda: self.operation(operator.truediv))  # operator.div for Python2.7

        self.pushButton_pc.pressed.connect(self.operation_pc)
        self.pushButton_eq.pressed.connect(self.equals)

        # Setup actions
        self.actionReset.triggered.connect(self.reset)
        self.pushButton_ac.pressed.connect(self.reset)

        self.actionExit.triggered.connect(self.close)

        self.pushButton_m.pressed.connect(self.memory_store)
        self.pushButton_mr.pressed.connect(self.memory_recall)

        self.memory = 0
        self.reset()

        self.show()

    def display(self):
        self.lcdNumber.display(self.stack[-1])

    def reset(self):
        self.state = READY
        self.stack = [0]
        self.last_operation = None
        self.current_op = None
        self.display()

    def memory_store(self):
        self.memory = self.lcdNumber.value()

    def memory_recall(self):
        self.state = INPUT
        self.stack[-1] = self.memory
        self.display()

    def input_number(self, v):
        if self.state == READY:
            self.state = INPUT
            self.stack[-1] = v
        else:
            self.stack[-1] = self.stack[-1] * 10 + v

        self.display()

    def operation(self, op):
        if self.current_op:  # Complete the current operation
            self.equals()

        self.stack.append(0)
        self.state = INPUT
        self.current_op = op

    def operation_pc(self):
        self.state = INPUT
        self.stack[-1] *= 0.01
        self.display()

    def equals(self):
        # Support to allow '=' to repeat previous operation
        # if no further input has been added.
        if self.state == READY and self.last_operation:
            s, self.current_op = self.last_operation
            self.stack.append(s)

        if self.current_op:
            self.last_operation = self.stack[-1], self.current_op

            try:
                self.stack = [self.current_op(*self.stack)]
            except Exception:
                self.lcdNumber.display('Err')
                self.stack = [0]
            else:
                self.current_op = None
                self.state = READY
                self.display()

class msgBox(QDialog, Ui_msgDialog):
    def __init__(self,):
        super(msgBox, self).__init__()
        self.setupUi(self)
        
class filterCols(QWidget, Ui_Columns):
    def __init__(self,table):
        self.table = table # copy table by reference to original
        super(filterCols,self).__init__()
        self.setupUi(self) # Ui is setup for filter
        self.selectAll = QtWidgets.QListWidgetItem() 
        self.selectAll.setText("Select All")
        self.selectAll.setCheckState(Qt.Checked)
        self.colList.addItem(self.selectAll)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.dictCols = {} # Dictionary that stores index and name of columns
        self.colList.itemChanged.connect(self.createConnections) # Signal when an item is clicked, and calls Create Connections
        
    def createConnections(self, item):
        # We check if it becomes checked or unchecked, and we decide whether to hide or unhide the specified column
        
        col = item.text()
        if((item == self.selectAll) and (item.checkState() == Qt.Checked)):
            #Select All Checkboxes and Unhide everything
            for items in range(self.colList.count()):
                self.colList.item(items).setCheckState(Qt.Checked)
                self.Hide(False,self.colList.item(items).text())
                
        elif((item == self.selectAll) & (item.checkState() == Qt.Unchecked)):
            #Unselect All Checkboxes and Hide everything
            for items in range(self.colList.count()):
                self.colList.item(items).setCheckState(Qt.Unchecked)
                self.Hide(True,self.colList.item(items).text())
            
        if(item.checkState() == Qt.Checked):
            self.Hide(False,col)
            
        elif(item.checkState() == Qt.Unchecked):
            self.Hide(True,col)

            
    def Hide(self, boolean,col):
        if(col != 'Select All'):
            if(boolean):
                self.table.setColumnHidden(self.dictCols.get(col),True)
            else:
                self.table.setColumnHidden(self.dictCols.get(col),False)
                
    def addDetailYOY(self,cols):
        self.dictCols = cols # We store in dictionary
        self.colList.item(0).setCheckState(Qt.Unchecked)
        # This for loop creates a new custom item per each key located in the dictionary
        i = 0
        now = dt.datetime.now()
        prevStrip = str(now.year-1) + ' - ' + str(now.year)
        nextStrip = str(now.year) + ' - ' + str(now.year+1) 
        for name in self.dictCols.keys():
#            print("List after clear Item:", self.colList.item(i).text())
            i+=1
            item = QtWidgets.QListWidgetItem() # Create new custom item
            item.setCheckState(Qt.Checked)
            item.setText(str(name)) # We name the item
            if(str(name) == 'ACCOUNTID' or str(name) == prevStrip or str(name) == nextStrip or str(name) == 'Delta'):
                item.setCheckState(Qt.Checked) # Set item Checked to Show
                
            else:
                item.setCheckState(Qt.Unchecked) # Set Item Unchecked to Hide
            self.colList.addItem(item) #add the item to the listWidget
            
    def clear(self):
        self.colList.clear()   
        self.selectAll = QtWidgets.QListWidgetItem() 
        self.selectAll.setText("Select All")
        self.colList.addItem(self.selectAll)
    
    def HideStart(self):
        for items in range(self.colList.count()):
            if items != 0: # We do this to avoid the first index in the list which is the select all button
                if (self.colList.item(items).checkState() == Qt.Unchecked):
                    self.Hide(True,self.colList.item(items).text())
#                    print("We Set Hidden:", self.colList.item(items).text())
                elif(self.colList.item(items).checkState() == Qt.Checked):
                    self.Hide(False,self.colList.item(items).text())
#                    print("We Set Unhidden", self.colList.item(items).text())
#    
    def addItem(self,cols):
        self.dictCols = cols # We store in dictionary
        
        # This for loop creates a new custom item per each key located in the dictionary
        for name in self.dictCols.keys():
            item = QtWidgets.QListWidgetItem()  # Create new custom item
            item.setText(str(name)) # Set text of item
            item.setCheckState(Qt.Checked) # We set the state of the item
            self.colList.addItem(item) #add the item to the listWidget
#            item = self.colList.item(i)
        allChecked = True
        for items in range(self.colList.count()):
            if (self.colList.item(items).checkState == Qt.Unchecked):
                allChecked = False
        if(allChecked):
            self.colList.item(0).setCheckState(Qt.Checked)
        else:
            self.colList.item(0).setCheckState(Qt.Unchecked)
            

class findMenu(QDialog, Ui_Find):
    # THIS CLASS IS THE POP UP FIND/CTRL+F WIDGET USED TO FIND ITEMS IN A TABLE
    # THE UI IS SET UP AS WELL AS THE ALGORITHM THAT STORES THE ITEMS FOUND AND SPANS THROUGH THEM WITH THE
    # NEXT AND PREVIOUS BUTTONS
    def __init__(self,table):
        super(findMenu,self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
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
        text = text.strip()
        isNumber = False
        try:
            numText = float(text)
        except:
            pass
        else:
            isNumber = True
            f4Text = '{0:.0f}'.format(numText)
            iText = '{0:,.0f}'.format(numText)
            intText = int(numText)
            
            fText = '{0:,.2f}'.format(numText)
            f3Text = '{0:.2f}'.format(numText)
            f2Text = '{0:.1f}'.format(numText)
            f1Text = '{0:,.1f}'.format(numText)
            
            
#            print('this is the text!!', fText)
            
        if(text != ''):
            self.searchClicked = True
            model = table.model()
            self.tempList = []
            self.tempList1 = []
            self.tempList2 = []
            self.tempList3 = []
            self.tempList4 = []
            self.tempList5 = []
            self.tempList6 = []
            self.matches = []
            
            self.numOfColumns = model.columnCount()
            for i in range(0,self.numOfColumns):
                                    
                start = model.index(0, i)
                if(isNumber == True):
                    if (float(f3Text) > intText):
#                        print("test ", float(f3Text)," greater than ", intText)
                        self.tempList2 = model.match(start, Qt.DisplayRole, fText, -1, Qt.MatchContains) 
                        self.tempList5 = model.match(start, Qt.DisplayRole, f3Text, -1, Qt.MatchContains)  
                        self.tempList4 = model.match(start, Qt.DisplayRole, f2Text, -1, Qt.MatchContains) 
                        self.tempList1 = model.match(start, Qt.DisplayRole, f1Text, -1, Qt.MatchContains)  
                        
                    else:    
#                        print("test ", float(f3Text)," equal to ", intText)
                        self.tempList3 = model.match(start, Qt.DisplayRole, iText, -1, Qt.MatchContains)    
                        self.tempList6 = model.match(start, Qt.DisplayRole, f4Text, -1, Qt.MatchContains) 
                    
                    
                    self.tempList = Union(self.tempList2,self.tempList3,self.tempList4,self.tempList1,self.tempList5,self.tempList6)
#                    print(set(self.tempList1) | set(self.tempList2) | set(self.tempList3) | set(self.tempList4) | set(self.tempList5) | set(self.tempList6), ' THIS!')
#                    self.tempList = set(self.tempList1) | set(self.tempList2) | set(self.tempList3) | set(self.tempList4) | set(self.tempList5) | set(self.tempList6)
                else:
                    #Its just text/string
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
        strName = self.plotNameInput.text()
        res = plotObj.mplfigs.findItems(strName, Qt.MatchExactly)
        if(strName == ''):
#            print("EMPTY!")
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Empty Field. Enter again!"))
            self.msgBox1.show()
        elif(len(res) > 0):
#            print("Enter another Name!") 
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Duplicate. Enter another Name!"))
            self.msgBox1.show()
            
        elif(len(res) == 0):
#            print("no duplicates")
            plotObj.addfig(strName, fig1)
            self.close()

# CLASS THAT MANAGES THE PLOT TOOL MENU
class Plot(QMainWindow, Ui_MainPlotWindow):
    def __init__(self, ):
        super(Plot, self).__init__()
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

###################################### ------------------------------------------------------ #####################################
###################################### --------------------START PANDAS MODEL---------------- #####################################
###################################### ------------------------------------------------------ #####################################
# CREATES MODEL FOR QTABLEVIEWS IN PYQT
class PandasModel(QtCore.QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self.minD = 0
        self.maxD = 0
        try:
            length = len(self._df.index) # Get # of rows 
            sumD = self._df['Delta'].iloc[:length-1].str.replace(',','').astype(float).sum()
            minD = self._df['Delta'].iloc[:length-1].str.replace(',','').astype(float).min()
            maxD = self._df['Delta'].iloc[:length-1].str.replace(',','').astype(float).max()
        except:
            pass
        else:
            self.minD = minD
            self.maxD = maxD
            self.sumD = sumD
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

        if( index.isValid()):
#            print(str(self._df.iloc[index.row(), index.column()]))
            
            
            if role == QtCore.Qt.DisplayRole:
                return str(self._df.iloc[index.row(), index.column()])
            
            if role == Qt.BackgroundRole:
#                                
                if str(self._df.iloc[index.row(),index.column()-1]) == 'Total':
                    bgc = QtGui.QColor()
                    bgc.setNamedColor("#534b4b")
                    return bgc  
                try:
                    colDF = self.getColumnNumber('Delta')  
                    length = len(self._df.index) # Get # of rows 
                    
                except:
                    
                    pass
                else:      

                    if index.column() == colDF:

                        dist = abs(self.minD - self.maxD)                        
                        
                        thres = [0]*92
                        for i in range(len(thres)):
                            if i == 0:
                                thres[i] = 0
                            else:
                                thres[i] = thres[i-1] + dist/91
                        indexVal = float(str(self._df.iloc[index.row(),index.column()]).replace(',',''))
                        if(index.row() != length-1):
                            for i in range(len(thres)):
                                
                                if(i == len(thres)-1):
##                                    print('this is the current length: ', length-1)
##                                    print('this is the index row: ',index.row())
##                                    print("Green")
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(92, 255, 174, 255)
                                    return bgc
                                elif(indexVal >= self.minD + thres[i] and indexVal <= self.minD + thres[i+1]):
                                    
                                    
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(i, 255, 174,255)
                                    return bgc
                        elif(index.row() == length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#135c75")
                            return bgc
                    else:
                        if(index.row() == length-1 ):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#135c75")
                            return bgc
                # ------------------------------------------------------------------------
                if index.column() ==2:
                    if str(self._df.iloc[index.row(),index.column()]) == 'Total':

                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#534b4b")
                        return bgc
                # ------------------------------------------------------------------------
                try:
                    colDF = self.getColumnNumber('Stop Read Value')   
                except:
                    pass
                else:      
                    if index.column() == colDF:
                        if str(self._df.iloc[index.row(),index.column()-1]) == 'Total':
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#534b4b")
                            return bgc 
                # ------------------------------------------------------------------------
                try:
                    colDF = self.getColumnNumber('Peak Value')   
                except:
                    pass
                else:      
                    if index.column() == colDF:
                        if str(self._df.iloc[index.row(),index.column()-2]) == 'Total':
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#534b4b")
                            return bgc  
                # THIS WILL HIGHLIGHT RED THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 5% OR IF NONE/EMPTY     
                try:
                    colDF = self.getColumnNumber('% Difference')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = float(val.replace(',',''))
                        except:
                            if(val == np.nan or val == 'nan'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#d85463")
                                return bgc
                        else:
                            if valF >= 5.0 or val == np.nan or val == 'nan':
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#d85462')
                                return bgc
                # ------------------------------------------------------------------------   
                # This will highlight the previous year red in Capacity Tags table if 
                # the current year tag and the previous year tag are equivalent
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
#                    print(str(ny))
                    # 
                    if((str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])) ):
                        if(self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()+1, colDF+1]):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#d85463")
                            return bgc
                # ------------------------------------------------------------------------
                # This will highlight the current year red in Capacity Tags table if 
                # the current year tag and the previous year tag are equivalent
                # OTHERWISE, it will only highlight it orange to show current year
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year
#                    print(str(ny))
                    # 
                    if((str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])) & (self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()-1, colDF+1]) ):
                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#d85463")
                        return bgc
                    elif(str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])):
#                        print("PRESENT YEAR FOUND!")
                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#fb8d00")
                        return bgc

                # ------------------------------------------------------------------------
            elif role == Qt.TextColorRole:
                # THIS WILL CHANGE TEXT TO WHITE THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 5% OR IF NONE/EMPTY     
                try:
                    colDF = self.getColumnNumber('% Difference')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = float(val.replace(',',''))
                        except:
                            if(val == np.nan or val == 'nan'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#FFFFFF")
                                return bgc
                        else:
                            if valF >= 5.0 or val == np.nan or val == 'nan':
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#FFFFFF')
                                return bgc
                
                try:
                    colDF = self.getColumnNumber('Delta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() == length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#FFFFFF")
                            return bgc
                    else:
                        if(index.row() == length-1 ):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#FFFFFF")
                            return bgc
                # ------------------------------------------------------------------------
                # This will set the font color equal to white for prev year in capacity tags
                # table if current tag and prev tag are equivalent
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
#                    print(str(ny))
                    # 
                    if((str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])) ):
                        if(self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()+1, colDF+1]):
                            tc = QtGui.QColor()
                            tc.setNamedColor("#FFFFFF")
                            return tc
                # ------------------------------------------------------------------------
                # This will set the font color equal to white for current year
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year
#                    print(str(ny))
                    if(str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])):
#                        print("PRESENT YEAR FOUND!")
                        tc = QtGui.QColor()
                        tc.setNamedColor("#FFFFFF")
                        return tc
                # ------------------------------------------------------------------------
                if str(self._df.iloc[index.row(),index.column()]) == 'Total':
                    tc = QtGui.QColor()
                    tc.setNamedColor("#FFFFFF")
                    return tc
                elif str(self._df.iloc[index.row(),index.column()-1]) == 'Total':
                    tc = QtGui.QColor()
                    tc.setNamedColor("#FFFFFF")
                    return tc
                elif str(self._df.iloc[index.row(),index.column()-2]) == 'Total':
                    tc = QtGui.QColor()
                    tc.setNamedColor("#FFFFFF")
                    return tc
            # ---------------------------------------------------------------------------------------------
                
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            
            # ---------------------------------------------------------------------------------------------
            
            elif role == Qt.FontRole:
                # THIS WILL BOLD THE TEXT IN THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 5% OR IF NONE/EMPTY     
                try:
                    colDF = self.getColumnNumber('% Difference')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = float(val.replace(',',''))
                        except:
                            if(val == np.nan or val == 'nan'):
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                        else:
                            if valF >= 5.0 or val == np.nan or val == 'nan':
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                
                try:
                    colDF = self.getColumnNumber('Delta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() == length-1):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                    else:
                        if(index.row() == length-1 ):
                            font = QtGui.QFont() 
                            font.setBold(True)
                            return font
                # ------------------------------------------------------------------------
                if str(self._df.iloc[index.row(),index.column()]) == 'Total':
                    font = QtGui.QFont() 
                    font.setBold(True)
                    return font

                elif str(self._df.iloc[index.row(),index.column()-1]) == 'Total':
                    font = QtGui.QFont() 
                    font.setBold(True)
                    return font
                elif str(self._df.iloc[index.row(),index.column()-2]) == 'Total':
                    font = QtGui.QFont() 
                    font.setBold(True)
                    return font
                # ------------------------------------------------------------------------
                # This will bold the font of the prev year in the capacity tags table
                # when the prev tag and the current tag are equivalent
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
#                    print(str(ny))
                    # 
                    if((str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])) ):
                        if(self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()+1, colDF+1]):
                            font = QtGui.QFont() 
                            font.setBold(True)
                            return font
                # ------------------------------------------------------------------------   
                # This will bold the font of the current year in the capacity tags table                     
                try:
                    colDF = self.getColumnNumber('Planning Year')   
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year
#                    print(str(ny))
                    if(str(ny) == str(self._df.iloc[index.row(),colDF].split()[1])): #colDF bc
                        font = QtGui.QFont() 
                        font.setBold(True)
                        return font
                    
        if role != QtCore.Qt.DisplayRole:
                return QtCore.QVariant()
            
        if not index.isValid():
            return QtCore.QVariant()
        
        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))
    
    def getColumnNumber(self, string):
        '''
        Given a string that identifies a label/column, 
        return the location of that label/column.
        This enables the config file columns to be moved around. 
        '''    
        
        col = self._df.columns.get_loc(string)
        return (col)
            
    
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
################################################### ------------------------------------------------------ #####################################
################################################### --------------------END PANDAS MODEL------------------ #####################################
################################################### ------------------------------------------------------ #####################################
        
# THE MAIN FUNCTION IS IN CHARGE OF DEPLOYING ALL THE NECESSARY FUNCTIONS TO RUN OUR PROGRAM
# IT EXECUTES THE DEFINED FUNCTIONS ABOVE, AS WELL AS THE FUNCTIONS IMPORTED FROM THE FILES THAT WERE CONVERTED FROM UI TO PY FILES
# THE MAIN FUNCTION SIMPLIFIES THE ABILITY TO RUN OUR GUI IN AN ELEGANT, AND REFRACTORED WAY WHICH IS MORE APPEALING AND ORGANIZE-ABLE!
# THE INIT METHOD FIRST CREATES THE NECESSARY TABLES WITH THE NECESSARY ATTRIBUTES PER TABLE,
        # EXAMPLES INCLUDE, CONTEXT MENU, CONNECT TO BUTTON CLICKS, TRIGGERS, OR FILTERS AS WELL AS SIMPLE OPERATIONS LIKE COPYING TO CB
        
class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.plot = Plot() # Creates Plot Menu Tool
        ######################################################################################################################
        # THIS BUTTON IS IN CHARGE OF CLICKING AND RUNNING THE ALGORITHM TO PULL AND QUERY THE DATA FROM PE
        self.pushButton.setWhatsThis("Queries PR# and Rev# from Lodestar PE")
        self.pushButton.clicked.connect(self.on_click)  # PUSH BUTTON IS CALLED HERE
        self.pushButton.setAutoDefault(True)
        self.pushButton_2.clicked.connect(self.on_clickOffer)
        self.pushButton_2.setAutoDefault(True)
        ######################################################################################################################
        
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE TABLE OF CAPACITY TAGS
        self.capTagsCols = filterCols(self.capTags) # This Creates the filter menu for the captags table
        self.capTags.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.capTags.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # Selection mode on table
        self.capTags.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked) # not working, table is not editable
        self.capTags.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capTags)) # The custom context menu is requested and the table is inputed
                                                                                                     #  as an argument to calculate different things
#        self.capTags.clicked.connect(lambda: self.onSelection(self.capTags))   # This allows the summary footer to calculate values        
        self.scCapTags = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capTags) # Shortcut to find values on table
        self.scCapTags.setContext(Qt.WidgetShortcut) # Sets the context of the shortcut
        self.scCapTags.activated.connect(lambda: self.execFind(self.capTags)) # Connects the shortcut to the find function
        self.scCapTagsCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capTags,lambda: self.copySlot(self.capTags)) # shortcut to copy multiple values in table
        self.scCapTagsCopy.setContext(Qt.WidgetShortcut) # Sets the context of the shortcut
        
        
        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE DETAIL - YOY TABLE
        self.detailYOY.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.detailYOYCols = filterCols(self.detailYOY) # This Creates the filter menu for the detailYOY table
        self.detailYOY.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # Allows for extended selection + multi-selection + single-selection
        self.detailYOY.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.detailYOY)) # Calls custom context menu and table is inputed
        self.scDetailYOY = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.detailYOY) # Shortcut to find
        self.scDetailYOY.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scDetailYOY.activated.connect(lambda: self.execFind(self.detailYOY)) # Shortcut for find is connected to the find function
        self.scDetailYOYcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.detailYOY,lambda: self.copySlot(self.detailYOY)) # Shortcut to copy is created and connected
        self.scDetailYOYcopy.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE CAPACITY OVERALL DATA TABLE
        self.capacity.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.capacityCols = filterCols(self.capacity) # This Creates the filter menu for the capacity overall table
        self.capacity.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capacity)) # Calls custom context menu and table is inputed
#        self.capTags.clicked.connect(lambda: self.onSelection(self.capacity))
        self.scCapacity = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capacity) # Shortcut to find
        self.scCapacity.setContext(Qt.WidgetShortcut) # Sets context for Shortcut
        self.scCapacity.activated.connect(lambda: self.execFind(self.capacity)) # Shortcut is connected to find function
        self.scCapacityCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capacity,lambda: self.copySlot(self.capacity)) # Shortcut for copying is created and connected
        self.scCapacityCopy.setContext(Qt.WidgetShortcut) # Sets fcontext for shortcut
        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE METERREADSPR TABLE
#        self.mrCheckBox.setCheckState(Qt.Checked)
        self.mrCheckBox.stateChanged.connect(self.onClickChangeMR)
        
        self.meterReadPR.setContextMenuPolicy(Qt.CustomContextMenu) # sets the custom context menu policy and creates it
        self.meterReadPRCols = filterCols(self.meterReadPR) # This Creates the filter menu for the meter Reads PR table
        self.meterReadPR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterReadPR))  # Calls custom context menu and table is inputed
        self.scMeterReadPR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterReadPR) # Creates Shortcut to find items
        self.scMeterReadPR.activated.connect(lambda: self.execFind(self.meterReadPR)) # connects shortcut to find items with this table
        self.scMeterReadPR.setContext(Qt.WidgetShortcut) # sets the context for the shortcut
        self.scMeterReadPRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterReadPR,lambda: self.copySlot(self.meterReadPR)) # Creates the shortcut for multiselection as well as connecting it to copySlot
        self.scMeterReadPRcopy.setContext(Qt.WidgetShortcut) # Sets the context for the shortcut
        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE  METERVALUES PR TABLE
        self.meterValuePR.setContextMenuPolicy(Qt.CustomContextMenu) # Creats custom context menu policy and the custom context menu itself
        self.meterValuePRCols = filterCols(self.meterValuePR) # This Creates the filter menu for the meter Values table
        self.meterValuePR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterValuePR)) # Conencts the custom context menu to this table by taking it as input
        self.scMeterValuePR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterValuePR) # Creates shortcut for finding items
        self.scMeterValuePR.setContext(Qt.WidgetShortcut) # Sets the contex for the shortcut
        self.scMeterValuePR.activated.connect(lambda: self.execFind(self.meterValuePR)) # Connects the shortcut to the find function
        self.scMeterValuePRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterValuePR,lambda: self.copySlot(self.meterValuePR)) # Creates and connects the shortcut for multi-selection - copying  
                                                                                                                                                # to the copy Slot function
        self.scMeterValuePRcopy.setContext(Qt.WidgetShortcut) # Sets the context for the shortcut
        ######################################################################################################################
        
        self.actionQuit.triggered.connect(QtWidgets.QApplication.quit)   # ACTION TO QUIT APPLICATION IN MENU BAR   
        

        ################################################################################################################
        # DISPLAYS AN EMPTY TABLE FOR EACH OF THE TABLES - CAPACITY TAGS, DETAIL YOY, METER READS, METER VALUES, CAPACITY
        emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
        emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'Delta'])
        emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                           'TAG_TYPE','TAG','Strip'])
        emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                            'ONPEAK_KWH','PEAKDEMAND'])
        emptyMeterReads = pd.DataFrame(columns = ['ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])  
                      
        # THIS SETS THE MODELS IN THE QTABLEVIEWS
        self.capTags.setModel(PandasModel(emptyCapTags))
        self.capacity.setModel(PandasModel(emptyCap))
        self.detailYOY.setModel(PandasModel(emptydetailYOY))
        self.meterReadPR.setModel(PandasModel(emptyMeterReads))
        self.meterValuePR.setModel(PandasModel(emptyMeterVal))
        #################################################################################################################
        
        # SETS THE TAB ORDER OF THE VARIOUS WIDGETS IN THE MAINWINDOW (WHAT'S FOCUSED NEXT AFTER PRESSING TAB)
        self.setTabOrder(self.lineEdit, self.lineEdit_2)
        self.setTabOrder(self.lineEdit_2, self.pushButton)
        self.setTabOrder(self.pushButton, self.pushButton_2)
        self.lineEdit.returnPressed.connect(self.on_click) # Shortcut for --> When return is connected, On_click function is called and starts pulling data
        self.lineEdit_2.returnPressed.connect(self.on_click) # Shortcut for --> When return is connected, On_click function is called and starts pulling data
        
    # VARIANT TO USE AS SHORTCUT -- **** NEEDS MORE RESEARCH ***
    def on_key(self, key, table):
        # conditions for specific keys
        if key == QtGui.QKeySequence('Ctrl+f'):
            self.execFind(table)
    
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
            startYear = 2016 # WHAT YEAR TO START DISPLAYING TAGS FROM
            now = dt.datetime.now()
            currentY = now.year
            lastPlanYear = currentY + 5  ## CHANGE HERE UNTIL WHAT PLAN YEAR
            rangeY = lastPlanYear - startYear
            
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
            startYear = 2016 # WHAT YEAR TO START DISPLAYING TAGS FROM
            now = dt.datetime.now()
            currentY = now.year
            lastPlanYear = currentY + 5  ## CHANGE HERE UNTIL WHAT PLAN YEAR
            rangeY = lastPlanYear - startYear
            
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
#        capTags['Transmission'] = pd.to_numeric(['Transmission'], 'ignore')
        capTags['Capacity Tag'] = capTags.apply(lambda x: "{:,.2f}".format(x['Capacity Tag']), axis=1)
        try:
            capTags['Transmission'] = capTags.apply(lambda x: "{:,.2f}".format(x['Transmission']), axis=1)
        except:
            pass
        
        model = PandasModel(capTags)
        
        # Here we will add the names of the columns to a dictionary
        # Key will be name of column, value is the index of the column
        listDict = {}
        i = 0
        for col in capTags.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.capTagsCols.addItem(listDict)
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
        if data.empty:
            return data
        else:
            if roundOrNot == 1:
                data = data.fillna(value = 0)
                data['TAG'] = data.apply(lambda x: "{:,.2f}".format(x['TAG']), axis=1)
                data['STOPTIME'] = pd.to_datetime(data['STOPTIME'])     # Convert date-type to only display Date w/o time
                data['STOPTIME'] = data['STOPTIME'].dt.date
                data['STARTTIME'] = pd.to_datetime(data['STARTTIME'])   # Convert date-type to only display Date w/o time
                data['STARTTIME'] = data['STARTTIME'].dt.date
                data.replace([0,0.0],'',inplace = True)
                return data
            elif roundOrNot == 2:
                listDict = {}
                i = 0
                for col in data.columns:
                    listDict.update({col:i})
#                    print(listDict)
                    i+=1
                self.capacityCols.addItem(listDict)
                
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
        
        pivTab = pd.pivot_table(tagDF_DM, columns = ['Strip'], index = ['CUSTOMERNAME','CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE'], values = ['TAG'], aggfunc = np.sum)
        pivTabTags = pivTab.reset_index(drop = True) # resets indexes to only keep the TAGS by Strips
        pivTab = pivTab.reset_index(drop = False) # resets indexes back to normal with Tags grouped by strips (STRIPS WILL BE REMOVED TO CONCATENATE LATER)
        pivTab.columns = pivTab.columns.get_level_values(0) # We keep the values from Level 0, specifically to fix renaming issue on MultiIndex tables
        pivTab.drop(columns = ['TAG'], inplace = True) # We drop any columns named 'TAG', since they will be renamed by pivTabTags
        pivTabTags.columns = pivTabTags.columns.get_level_values(1) # We do this to keep the names of the Yearly Strips (ie. 2018 - 2019, 2019-2020, etc.)
        
        tagDF_DM = pd.concat([pivTab, pivTabTags], axis = 1, sort = False) # We concatenate to get our goal Table with columns renamed effectively
        
        detailYOY = tagDF_DM
        detailYOY = detailYOY.fillna(value = 0)
        checkMin = False
        checkMax = False
        now = dt.datetime.now()
        prevStrip = str(now.year-1) + ' - ' + str(now.year)
        nextStrip = str(now.year) + ' - ' + str(now.year+1) 
        for i in detailYOY.columns:
            if i == prevStrip:
                checkMin = True

        for i in detailYOY.columns:
            if i ==  nextStrip:
                checkMax = True
                
        
        if(checkMin and checkMax):
            detailYOY['Delta'] = detailYOY[nextStrip] - detailYOY[prevStrip] 
            detailYOY = detailYOY.sort_values(by = [nextStrip],ascending = False)
        elif(checkMin):
            detailYOY['Delta'] = 0 - detailYOY[prevStrip]
            detailYOY = detailYOY.sort_values(by = [prevStrip],ascending = False)
        elif(checkMax):
            detailYOY['Delta'] = detailYOY[nextStrip]
            detailYOY = detailYOY.sort_values(by = [nextStrip],ascending = False)
        
        
        detailYOY = detailYOY.set_index('ACCOUNTID')
        #detailYOY.loc["Grand Total"] = detailYOY.sum()
        detailYOY = detailYOY.append(detailYOY.sum(numeric_only = True).rename('GRAND TOTAL'))
        detailYOY = detailYOY.reset_index(drop = False) 
        detailYOY = detailYOY.fillna(value = '')
        for i in range(len(detailYOY.columns) - 6):
            detailYOY.iloc[:,i + 6] = detailYOY.apply(lambda x: "{:,.2f}".format(x[(i+6)]), axis=1)
#        detailYOY['TAG'] = detailYOY['TAG'].apply(lambda x: "{:,.2f}".format(x,axis=1))            WE DONT NEED THIS ANYMORE!
        detailYOY.replace([0,0.0],'',inplace = True)
        model = PandasModel(detailYOY)
        listDict = {}
        i = 0
        for col in detailYOY.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.detailYOYCols.addDetailYOY(listDict)
    
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
        try:
            metValPiv2 =metValPiv2[['ACCOUNT_JOIN_ID','LDC_ACCOUNT','ACCOUNTID',
                                    'UIDACCOUNT','READDATE','UIDBILLDETERMINANT','STARTTIME','STOPTIME',
                                    'STRVAL','LSUSER', 'LSTIME','Strip',
                                    'ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND']]
        except:
            metValPiv2 =metValPiv2[['ACCOUNT_JOIN_ID','LDC_ACCOUNT','ACCOUNTID',
                                    'UIDACCOUNT','READDATE','UIDBILLDETERMINANT','STARTTIME','STOPTIME',
                                    'STRVAL','LSUSER', 'LSTIME','Strip',
                                    'ANNUAL_KWH','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND']]
        
        filter = (metValPiv2.STARTTIME.dt.year >= 2018)
        metValPiv2.where(filter, inplace = True)
        metValPiv2 = metValPiv2.dropna(subset = ['ACCOUNTID'])
        metValPiv2 = metValPiv2.fillna(value = 0)
        try:
            metValPiv2 = metValPiv2.loc[(metValPiv2.ANNUAL_KWH != 0 ) | ( metValPiv2.LOADFACTOR != 0 )|  (metValPiv2.AVERAGEDEMAND != 0) | (metValPiv2.ONPEAK_KWH != 0) | ( metValPiv2.OFFPEAK_KWH != 0) | (metValPiv2.PEAKDEMAND != 0)]
        except:
            metValPiv2 = metValPiv2.loc[(metValPiv2.ANNUAL_KWH != 0 ) | (metValPiv2.AVERAGEDEMAND != 0) | (metValPiv2.ONPEAK_KWH != 0) | ( metValPiv2.OFFPEAK_KWH != 0) | (metValPiv2.PEAKDEMAND != 0)]
        metValPiv2 = metValPiv2.dropna(subset = ['ACCOUNTID'])
        try:
            meterValfin1_1 = pd.pivot_table(metValPiv2, index = ['Strip', 'ACCOUNTID'], values = ['ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND'],fill_value = 0, aggfunc = np.sum)
        except:
            meterValfin1_1 = pd.pivot_table(metValPiv2, index = ['Strip', 'ACCOUNTID'], values = ['ANNUAL_KWH','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND'],fill_value = 0, aggfunc = np.sum)
        
        meterValFIN= meterValfin1_1.reset_index(drop = False)
        
        meterValFIN.loc[:,['OFFPEAK_KWH','ONPEAK_KWH']] /= 1000
        try:
            meterValFIN.loc[:,['LOADFACTOR']] *= 100
        except:
            pass
        meterValFIN = meterValFIN.sort_values(by = ['ANNUAL_KWH'],ascending = False)
        try:
            meterValFIN['LOADFACTOR'] = meterValFIN.apply(lambda x: "{:,.2f}%".format(x['LOADFACTOR']), axis=1) 
        except:
            pass
#        meterValFIN['ANNUAL_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ANNUAL_KWH']), axis=1)
        meterValFIN['OFFPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['OFFPEAK_KWH']), axis=1)
        meterValFIN['ONPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ONPEAK_KWH']), axis=1)
        meterValFIN['AVERAGEDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['AVERAGEDEMAND']), axis=1)
        meterValFIN['PEAKDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['PEAKDEMAND']), axis=1)
        try:
            meterValFIN = meterValFIN.rename(columns = {"ACCOUNTID":"Account ID", "ANNUAL_KWH" : "Annual KWHs", "OFFPEAK_KWH" : "OffPeak MWHs","ONPEAK_KWH" : "OnPeak MWHs","LOADFACTOR" : "LF (%)","AVERAGEDEMAND" : "AvgDemand", "PEAKDEMAND": "PeakDemand"})
        except:
            meterValFIN = meterValFIN.rename(columns = {"ACCOUNTID":"Account ID", "ANNUAL_KWH" : "Annual KWHs", "OFFPEAK_KWH" : "OffPeak MWHs","ONPEAK_KWH" : "OnPeak MWHs","AVERAGEDEMAND" : "AvgDemand", "PEAKDEMAND": "PeakDemand"})
        meterValFIN2 = meterValFIN.copy()
        meterValFIN2['Annual KWHs'] = meterValFIN.apply(lambda x: "{:.2f}".format(x['Annual KWHs']), axis=1)
        meterValFIN2['Annual KWHs'] = meterValFIN['Annual KWHs'].astype(float)
        favDict = pd.Series(meterValFIN2['Annual KWHs'].values,index=meterValFIN2['Account ID']).to_dict() # DICT
        meterValFIN['Annual KWHs'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['Annual KWHs']), axis=1)
#        model = PandasModel(meterValFIN)
#        listDict = {}
#        i = 0
#        for col in meterValFIN.columns:
#            listDict.update({col:i})
##            print(listDict)
#            i+
#        self.meterValuePRCols.addItem(listDict)
        #print(model)
        return meterValFIN, meterValFIN2, favDict
    def meterReadfull(self, prNum, revNum):
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
                    /*WHERE
                        -- This was added to get only the last 12 months of data
                        mr.STARTREADTIME >= add_months(trunc(sysdate,'month'),-16) 
                        AND mr.STARTREADTIME < trunc(sysdate, 'month') */
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
        
        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME']) # Convert the date column to datetimeformat
        meterRead['STARTREADTIME'] = meterRead['STARTREADTIME'].dt.strftime('%m/%d/%Y') # Convert the date column to only show date w/o seconds
        meterReadpiv = pd.pivot_table(meterRead,index = ['ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME'],values =['PEAKVALUE','STOPREADING'])

        # We unstack levels while summing Stop Read Values
        meterReadpiv2 = meterReadpiv.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['STOPREADING'].sum().unstack()
        meterReadpiv2 = meterReadpiv2.reindex(sorted(meterReadpiv2.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv2 = meterReadpiv2.stack().to_frame('STOPREADING')       
        meterReadpiv2 = meterReadpiv2.reset_index(drop = False)
        meterReadpiv2  = meterReadpiv2.groupby('ACCOUNTID').tail(36)
        
        # We unstack levels while summing Stop Read Values
        meterReadpiv2 = meterReadpiv2.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['STOPREADING'].sum().unstack()
        meterReadpiv2 = meterReadpiv2.reindex(sorted(meterReadpiv2.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv2['Total'] = meterReadpiv2.sum(axis=1)
        meterReadpiv2 = meterReadpiv2.sort_values(by = ['Total'],ascending = False)
        meterReadpiv2 = meterReadpiv2.stack().to_frame('STOPREADING')    
        
        meterReadpiv3 = meterReadpiv.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['PEAKVALUE'].sum().unstack()
        meterReadpiv3 = meterReadpiv3.reindex(sorted(meterReadpiv3.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv3 = meterReadpiv3.stack().to_frame('PEAKVALUE')  
        meterReadpiv3 = meterReadpiv3.reset_index(drop = False)
        meterReadpiv3 = meterReadpiv3.groupby(['ACCOUNTID']).tail(36)
        
        meterReadpiv3 = meterReadpiv3.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['PEAKVALUE'].sum().unstack()
        meterReadpiv3 = meterReadpiv3.reindex(sorted(meterReadpiv3.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv3['Total'] = meterReadpiv3.sum(axis=1)
        
        meterReadpiv3 = meterReadpiv3.sort_values(by = ['Total'],ascending = False)
        meterReadpiv3 = meterReadpiv3.stack().to_frame('PEAKVALUE')       

        meterReadpiv2 = meterReadpiv2.reset_index(drop = False) # We drop multindexes and set them regular
        meterReadpiv2 = meterReadpiv2.rename(columns = {'ACCOUNTID': 'Account ID', 'PROFILE_OR_SCALAR':'Profile/Scalar', # RENAME columns
                                                        'STARTREADTIME':'Start Read Time','STOPREADING':'Stop Read Value'})
     
        meterReadpiv3 = meterReadpiv3.reset_index(drop = False)
        meterReadpiv3 = meterReadpiv3.rename(columns = {'ACCOUNTID':'Account ID','PROFILE_OR_SCALAR':'Profile/Scalar',
                                                            'STARTREADTIME':'Start Read Time','PEAKVALUE':'Peak Value'})   
     
    
#        meterReadpiv2['Stop Read Value'] = meterReadpiv2['Stop Read Value'].astype(int) # We convert Stop read value to Int for ease of view
        meterReadpiv2['Stop Read Value'] = meterReadpiv2['Stop Read Value'].map('{:,.0f}'.format)
#        meterReadpiv3['Peak Value'] = meterReadpiv3['Peak Value'].astype(int) # We convert Stop read value to Int for ease of view
        meterReadpiv3['Peak Value'] = meterReadpiv3['Peak Value'].map('{:,.0f}'.format)
        
        meterReadpiv2[['Account ID']] = meterReadpiv2[['Account ID']].where(meterReadpiv2[['Account ID']]. # Here we simulate table as if it were multindex 
                     apply(lambda x: x!= x.shift()), '') # by removing repeating rows such as Account ID and Profile/Scalar, repeating Account IDs replaced w/ '' (blank)
        meterReadpiv2.loc[meterReadpiv2['Account ID'] == '', 'Profile/Scalar'] = '' # Here we replace values in Scalar with '' (blank) if row in Account ID is '' (blank)
        
        meterReadpiv3[['Account ID']] = meterReadpiv3[['Account ID']].where(meterReadpiv3[['Account ID']].apply(lambda x: x!= x.shift()),'')
        meterReadpiv3.loc[meterReadpiv3['Account ID'] == '', 'Profile/Scalar'] = ''
        
        meterReadpiv2['Peak Value'] = meterReadpiv3['Peak Value']
        #meterReadpiv2.index += 1 # OPTION TO START INDEXES AT TABLE, (((TO HELP REGULAR USERS NOT LIKE NERDS WHO COUNT FROM ZERO !!)))
        model = PandasModel(meterReadpiv2) # convert table to a Pandas Model used by the QT Gui engine
        
        listDict = {}
        i = 0
        for col in meterReadpiv2.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.meterReadPRCols.addItem(listDict)
        
        return model
    
    #ONLY THE LAST 12
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
                    /*WHERE
                        -- This was added to get only the last 12 months of data
                        mr.STARTREADTIME >= add_months(trunc(sysdate,'month'),-16) 
                        AND mr.STARTREADTIME < trunc(sysdate, 'month') */
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
        
        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME']) # Convert the date column to datetimeformat
        meterRead['STARTREADTIME'] = meterRead['STARTREADTIME'].dt.strftime('%m/%d/%Y') # Convert the date column to only show date w/o seconds
        meterReadpiv = pd.pivot_table(meterRead,index = ['ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME'],values =['PEAKVALUE','STOPREADING'])

        # We unstack levels while summing Stop Read Values
        meterReadpiv2 = meterReadpiv.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['STOPREADING'].sum().unstack()
        meterReadpiv2 = meterReadpiv2.reindex(sorted(meterReadpiv2.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv2 = meterReadpiv2.stack().to_frame('STOPREADING')       
        meterReadpiv2 = meterReadpiv2.reset_index(drop = False)
        meterReadpiv2  = meterReadpiv2.groupby('ACCOUNTID').tail(12)
        
        # We unstack levels while summing Stop Read Values
        meterReadpiv2 = meterReadpiv2.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['STOPREADING'].sum().unstack()
        meterReadpiv2 = meterReadpiv2.reindex(sorted(meterReadpiv2.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv2['Total'] = meterReadpiv2.sum(axis=1)
        meterReadpiv2 = meterReadpiv2.sort_values(by = ['Total'],ascending = False)
        totalMR = meterReadpiv2.reset_index(drop = False)
        totalMR = totalMR[['ACCOUNTID','Total']].copy()
        mrDict = pd.Series(totalMR['Total'].values,index=totalMR['ACCOUNTID']).to_dict()
        meterReadpiv2 = meterReadpiv2.stack().to_frame('STOPREADING')    
        
        meterReadpiv3 = meterReadpiv.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['PEAKVALUE'].sum().unstack()
        meterReadpiv3 = meterReadpiv3.reindex(sorted(meterReadpiv3.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv3 = meterReadpiv3.stack().to_frame('PEAKVALUE')  
        meterReadpiv3 = meterReadpiv3.reset_index(drop = False)
        meterReadpiv3 = meterReadpiv3.groupby(['ACCOUNTID']).tail(12)
        
        meterReadpiv3 = meterReadpiv3.groupby(["ACCOUNTID", "PROFILE_OR_SCALAR","STARTREADTIME"])['PEAKVALUE'].sum().unstack()
        meterReadpiv3 = meterReadpiv3.reindex(sorted(meterReadpiv3.columns,  key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')), axis = 1)
        meterReadpiv3['Total'] = meterReadpiv3.sum(axis=1)
        
        meterReadpiv3 = meterReadpiv3.sort_values(by = ['Total'],ascending = False)
        meterReadpiv3 = meterReadpiv3.stack().to_frame('PEAKVALUE')       

        meterReadpiv2 = meterReadpiv2.reset_index(drop = False) # We drop multindexes and set them regular
        meterReadpiv2 = meterReadpiv2.rename(columns = {'ACCOUNTID': 'Account ID', 'PROFILE_OR_SCALAR':'Profile/Scalar', # RENAME columns
                                                        'STARTREADTIME':'Start Read Time','STOPREADING':'Stop Read Value'})
     
        meterReadpiv3 = meterReadpiv3.reset_index(drop = False)
        meterReadpiv3 = meterReadpiv3.rename(columns = {'ACCOUNTID':'Account ID','PROFILE_OR_SCALAR':'Profile/Scalar',
                                                            'STARTREADTIME':'Start Read Time','PEAKVALUE':'Peak Value'})   
     
    
#        meterReadpiv2['Stop Read Value'] = meterReadpiv2['Stop Read Value'].astype(int) # We convert Stop read value to Int for ease of view
        meterReadpiv2['Stop Read Value'] = meterReadpiv2['Stop Read Value'].map('{:,.0f}'.format)
#        meterReadpiv3['Peak Value'] = meterReadpiv3['Peak Value'].astype(int) # We convert Stop read value to Int for ease of view
        meterReadpiv3['Peak Value'] = meterReadpiv3['Peak Value'].map('{:,.0f}'.format)
        
        meterReadpiv2[['Account ID']] = meterReadpiv2[['Account ID']].where(meterReadpiv2[['Account ID']]. # Here we simulate table as if it were multindex 
                     apply(lambda x: x!= x.shift()), '') # by removing repeating rows such as Account ID and Profile/Scalar, repeating Account IDs replaced w/ '' (blank)
        meterReadpiv2.loc[meterReadpiv2['Account ID'] == '', 'Profile/Scalar'] = '' # Here we replace values in Scalar with '' (blank) if row in Account ID is '' (blank)
        
        meterReadpiv3[['Account ID']] = meterReadpiv3[['Account ID']].where(meterReadpiv3[['Account ID']].apply(lambda x: x!= x.shift()),'')
        meterReadpiv3.loc[meterReadpiv3['Account ID'] == '', 'Profile/Scalar'] = ''
        
        meterReadpiv2['Peak Value'] = meterReadpiv3['Peak Value']
        #meterReadpiv2.index += 1 # OPTION TO START INDEXES AT TABLE, (((TO HELP REGULAR USERS NOT LIKE NERDS WHO COUNT FROM ZERO !!)))
        model = PandasModel(meterReadpiv2) # convert table to a Pandas Model used by the QT Gui engine
        
        listDict = {}
        i = 0
        for col in meterReadpiv2.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.meterReadPRCols.addItem(listDict)
        
        return model, mrDict
    
    # THIS FUNCTION COPIES THE OFFER # TO THE CLIPBOARD
    def on_clickOffer(self):  
#        prNum = self.lineEdit.text() # Gets text from input line
#        prNum = prNum.strip() # Strips spaces
        offerNum = 'OFFER_' + self.prNumStr + '%' 
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText(offerNum, mode=cb.Clipboard)
    
    # THIS FUNCTION IS CALLED WHEN PUSH BUTTON IS PUSHED, AND STARTS THE ALGORITHM TO PULL AND QUERY DATA FROM PE
    def on_click(self):
        
        _translate = QtCore.QCoreApplication.translate
        prNum = self.lineEdit.text()
        revNum = self.lineEdit_2.text()
        
        self.revNum = self.lineEdit_2.text()
        self.prNumStr = self.lineEdit.text() # Gets text from input line
        
        self.prNumStr = prNum.strip() # Strips spaces
        self.revNum = self.revNum.strip()
        
        offerNum = 'OFFER_' + self.prNumStr + '%' 
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText(offerNum, mode=cb.Clipboard)
        
        #################################################
               # CLEARS LIST WITH FILTERS PER TABLE #
        self.capTagsCols.clear()
        self.detailYOYCols.clear()
        self.capacityCols.clear()
        self.meterReadPRCols.clear()
        self.meterValuePRCols.clear()
        #################################################
        
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
            self.meterReadM = PandasModel(emptyMeterReads)
            self.meterReadFullM = PandasModel(emptyMeterReads)
            self.label_3.setText(_translate("MainWindow", "Current PR: "))
            self.capTags.setModel(PandasModel(emptyCapTags))
            self.capacity.setModel(PandasModel(emptyCap))
            self.detailYOY.setModel(PandasModel(emptydetailYOY))
            self.meterReadPR.setModel(PandasModel(emptyMeterReads))
            self.meterValuePR.setModel(PandasModel(emptyMeterVal))
            if(prNum == ""):
                self.label_3.setText(_translate("MainWindow", "Current PR:     " + "N/A" + "     Rev.     " + revNum))
            elif(revNum == ""):
                self.label_3.setText(_translate("MainWindow", "Current PR:     " + prNum + "     Rev.     " + "N/A"))
                
        else:
            self.label_3.setText(_translate("MainWindow", "Current PR:     " + prNum + "     Rev.     " + revNum))
            font = QtGui.QFont()
            font.setBold(True)
            font.setWeight(75)
            dataMrounded = self.getData(prNum, revNum, 1)
            dataM = self.getData(prNum, revNum, 2)
            if dataMrounded.empty or dataM.empty:
                # DO NOT DO ANYTHING JUST SET EVERYTHING EMPTY
                
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
                self.label_3.setText(_translate("MainWindow", "Current PR:     " + "CHECK & VERIFY" + "     Rev.     " + "CHECK & VERIFY#"))
            else:
                #------------------------------------------------------------------------------------------------------------------
                # DO EVERYTHING BELOW
                dataMpd = PandasModel(dataMrounded)
                self.capacity.setModel(dataMpd)
                self.capacity.setAlternatingRowColors(True)
                self.capacity.setStyleSheet("alternate-background-color: #e7e5e2;background-color: #ffffff;selection-background-color: #4c74f4")
                self.capacity.horizontalHeader().setFont(font)
                self.capacity.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capacity))
                #------------------------------------------------------------------------------------------------------------------
                capTagsM = self.makeCaptags(dataM)
                self.capTags.setModel(capTagsM)
                self.capTags.setAlternatingRowColors(True)
                self.capTags.setStyleSheet("alternate-background-color: #BEF3C5;background-color: #ffffff;selection-background-color: #21b334;selection-color #ffffff")    
                self.capTags.horizontalHeader().setFont(font)
                self.capTags.setColumnWidth(0, ((self.capTags.columnWidth(0)+self.capTags.columnWidth(1)+self.capTags.columnWidth(2)+self.capTags.columnWidth(3))/4)+40);
                self.capTags.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capTags))
                #------------------------------------------------------------------------------------------------------------------
                detailYOYM = self.detailYOYfunc(dataM)
                self.detailYOY.setModel(detailYOYM)
                self.detailYOY.setAlternatingRowColors(True)
                self.detailYOY.setColumnWidth(0,200)
                self.detailYOY.horizontalHeader().setFont(font)
                self.detailYOY.setStyleSheet("alternate-background-color:#daf1f9;background-color: #ffffff;selection-background-color: #1b83a7")
                self.detailYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.detailYOY))
                self.detailYOYCols.HideStart()
                #------------------------------------------------------------------------------------------------------------------
#                meterValueM = self.meterValue(prNum, revNum)
                meterValueDF, meterValueDF2, favDict = self.meterValue(prNum,revNum)
                self.mrCheckBox.setCheckState(Qt.Checked)
                self.meterReadM, mrDict = self.meterRead(prNum, revNum) # this is the model that only has last 12 months
                meterValueM = self.calcVar(meterValueDF, meterValueDF2, favDict, mrDict)        
                #------------------------------------------------------------------------------------------------------------------
                self.meterValuePR.setModel(meterValueM)
                self.meterValuePR.setAlternatingRowColors(True)
                self.meterValuePR.setStyleSheet("alternate-background-color:#daf1f9;background-color: #ffffff;selection-background-color: #1b83a7")
                self.meterValuePR.setColumnWidth(0,70)
                self.meterValuePR.setColumnWidth(1,185)
                self.meterValuePR.setColumnWidth(3,90)
                self.meterValuePR.setColumnWidth(4,80)
                self.meterValuePR.setColumnWidth(7,90)
                self.meterValuePR.horizontalHeader().setFont(font)
                self.meterValuePR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterValuePR))
                #------------------------------------------------------------------------------------------------------------------
                
                
                self.meterReadFullM = self.meterReadfull(prNum,revNum) # this is the model that has all available data
                self.meterReadPR.setModel(self.meterReadM)
                self.meterReadPR.setAlternatingRowColors(True)
                self.meterReadPR.setColumnWidth(0,185)
                self.meterReadPR.horizontalHeader().setFont(font)
                self.meterReadPR.setStyleSheet("alternate-background-color: #BEF3C5;background-color: #ffffff;selection-background-color: #21b334")
                self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))
                #------------------------------------------------------------------------------------------------------------------
    
    def calcVar(self, meterValFIN, meterValFIN2, favDict, mrDict):
        varDiff = {}
        for key,value in mrDict.items():
            v1 = favDict.get(key)
            v2 = mrDict.get(key)
            pDiff = abs((v1-v2)/((v1+v2)/2)) *100
            varDiff[key] = pDiff
            
        varTable = pd.DataFrame.from_dict(varDiff, orient='index',columns = ['%Diff vs Meter Reads'])
        #varTable.reset_index(drop = False, inplace = True)
        varTable = varTable.rename_axis('Account ID').reset_index()
        
        ref = pd.Series(meterValFIN2.index.values,index=meterValFIN2['Account ID']).to_dict()
        meterValFIN['% Difference'] = ""
        ref2 = {}
        for key,value in ref.items():
            v1 = varDiff.get(key) # get the variance
            ref2[value] = v1
        
        for key,value in ref2.items():
            meterValFIN.at[key,'% Difference'] = value
        meterValFIN['% Difference'].fillna(value=pd.np.nan, inplace=True)
        meterValFIN['% Difference'].fillna(value = 0)
        meterValFIN['% Difference'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['% Difference']), axis=1)
        try:
            order = ['Strip','Account ID','Annual KWHs','% Difference','AvgDemand','LF (%)','OffPeak MWHs','OnPeak MWHs','PeakDemand']
            meterValFIN = meterValFIN.reindex(columns = order) # 
        except:
            # IN CASE LOAD FACTOR DOES NOT EXIST
            order = ['Strip','Account ID','Annual KWHs','% Difference','AvgDemand','OffPeak MWHs','OnPeak MWHs','PeakDemand']
            meterValFIN = meterValFIN.reindex(columns = order)
        
        model = PandasModel(meterValFIN)
        listDict = {}
        i = 0
        for col in meterValFIN.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.meterValuePRCols.addItem(listDict)
        #print(model)
        return model
    
    def onClickChangeMR(self):
#        prNum = self.lineEdit.text()
#        revNum = self.lineEdit_2.text()
#        meterReadM = self.meterRead(prNum, revNum)
#        meterReadFullM = self.meterReadfull(prNum,revNum)
        # this will be the function in charge of displaying the Meter Reads PR table
        # deciding whether to displaying it or not, depending on the status of checked or unchecked
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        if(self.mrCheckBox.checkState() == Qt.Checked):
            
            try:
                
#                self.meterReadPR.setModel(None)
                self.meterReadPR.setModel(self.meterReadM)
                self.meterReadPR.setAlternatingRowColors(True)
                self.meterReadPR.setColumnWidth(0,185)
                self.meterReadPR.horizontalHeader().setFont(font)
                self.meterReadPR.setStyleSheet("alternate-background-color: #BEF3C5;background-color: #ffffff;selection-background-color: #21b334")
                self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))
            except:
                pass
        elif(self.mrCheckBox.checkState() == Qt.Unchecked):
            
            try:
                
#                self.meterReadPR.setModel(None)
                self.meterReadPR.setModel(self.meterReadFullM)
                self.meterReadPR.setAlternatingRowColors(True)
                self.meterReadPR.setColumnWidth(0,185)
                self.meterReadPR.horizontalHeader().setFont(font)
                self.meterReadPR.setStyleSheet("alternate-background-color: #BEF3C5;background-color: #ffffff;selection-background-color: #21b334")
                self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))
            except:
                pass
        
    
    def contextMenuEvent(self, table):
        
        self.menu = QMenu(self) 
        copyAction = self.menu.addAction("Copy     Ctrl+C") # context menu action added
        findAction = self.menu.addAction("Find       Ctr+F") # context menu action added
        calculatorAction = self.menu.addAction("Calculator")
        plotAction = self.menu.addMenu("Plot Menu")
        plotList = plotAction.addAction("Add to Plot List")
        plot = plotAction.addAction("Plot")
        copyWHeadsAction = self.menu.addAction("Copy w/ Headers")
        filterAction = self.menu.addAction("Filter Columns")
        
        
        index = table.selectionModel().currentIndex() # Current Index
        row = index.row() # gets index of current row selected in table
        col = index.column()  # gets index of current column selected in table

        copyAction.triggered.connect(lambda: self.copySlot(table, True)) # when copy button is pressed, call copySlot function
        copyWHeadsAction.triggered.connect(lambda: self.copySlot(table, False)) # when copy button is pressed, call copySlot function
        calculatorAction.triggered.connect(self.execCalculator)
        findAction.triggered.connect(lambda: self.execFind(table)) # when find button is pressed, call execFind Function to open a Find Window
        
        plot.triggered.connect(self.plotSlot)
        plotList.triggered.connect(lambda: self.addList(table)) # when plot button is pressed, call plotslot function
        filterAction.triggered.connect(lambda: self.showColFilt(table))
        # add other required actions
        self.menu.popup(QtGui.QCursor.pos()) # Pops custom context menu to cursor's position
    def execCalculator(self):
        self.calc = calculator()
        self.calc.show()
        
    def showColFilt(self, table):
        if table == self.capTags:
            self.capTagsCols.show()
        elif table == self.detailYOY:
            
            self.detailYOYCols.show()
        elif table == self.capacity:
            self.capacityCols.show()
        elif table == self.meterReadPR:
            self.meterReadPRCols.show()
        elif table == self.meterValuePR:
            self.meterValuePRCols.show()
    
    def execFind(self, table):
        # THIS FUNCTION OPENS A NEW WINDOW WITH A FIND FUNCTIONALITY #
        
        self.findWindow = findMenu(table) # New Window is created
        self.findWindow.show() # Show find window   
    
    #############################################################################################
    #############################################################################################
    # THIS METHOD CALCULATES SUMMARY FOOTER DATA SUCH AS SUM, COUNT, AND AVG OF SELECTED ITEMS#
    # WORKS BY UPDATING THE DATA EVERY TIME THE CURRENT SELECTION IS CHANGED (ie. selecting a different index in the table, an item in different table, etc.)
    def onSelection(self, table):
        _translate = QtCore.QCoreApplication.translate
        selection = table.selectedIndexes() # Stores selected item indexes in a list
        if selection:
            listP = [] # Creates empty list to store values of selected items
            for index in selection:            
                val = index.data()
                valStr = str(val) # Convert value to str for comparison

                try:

                    val = float(valStr.replace(',',''))
#                    print(val)
                    # if val is type float, convert to float with empty space replacing commas
                    listP.append(val) # Append to list as float
                    
                except:
#                    print("ERROR! STR DETECTED NOT CONVERTABLE")
                    listP.append(0)
                
                    
                
                # LIST IS FILLED WITH VALUES SELECTED
            if(len(listP) != 0):
                # CHECKS IF LIST IS NOT EMPTY TO AVOID DIVIDING BY ZERO IN AVG FUNCTION
                sumSelection = sum(listP)
                avgSelection = Average(listP)
                countSelection = len(listP)
                self.summFooter.setText(_translate("MainWindow", "Sum: " + str('{0:,.2f}'.format(sumSelection)) + "        Count: " + str(countSelection) + "        Avg: " + str('{0:,.2f}'.format(avgSelection)) + "                                    "))
    #############################################################################################
    #############################################################################################
    
    def plotSlot(self):
        self.plot.show()
    
    def addList(self, table):

        selection = table.selectedIndexes()
        if selection:
            
            listP = []
            rows = sorted(index.row() for index in selection) # returns a list of rows
            columns = sorted(index.column() for index in selection) # returns a list of columns
            cond = all_same(columns)
#            headerName = str(table.model().headerData(columns[0], Qt.Horizontal)) ## ADD CONDITION HERE IF NAME EXISTS ALREADY,
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
                
                self.namePlot = namePlot(self.plot, fig1)
                self.namePlot.show()
                self.namePlot.plotNameInput.setFocusPolicy(Qt.StrongFocus)
                self.namePlot.plotNameInput.setFocus()
            else:
                # CREATE DIALOG SAYING ONLY SELECT ON COLUMNS
#                print("ERROR!")
                self.msgBox1 = msgBox()
                self.msgBox1.text.setText(("Only Columns Allowed!"))
                self.msgBox1.show()
            
    
    def copySlot(self, table, condition):
        # get the text inside selected cell (if any)
#        cell = table.model().index(row,col).data()

        selection = table.selectedIndexes()
        if selection:
            result = 0
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rows = list(dict.fromkeys(rows)) # we count the amount of rows we selected by distinct row indexes
            columns = list(dict.fromkeys(columns)) # we count the amount of columns we selected by distinct col indexes
            colcount = len(columns)
            rowcount = len(rows)
#            print('len = ', len(columns))
            table1 = [[''] * colcount for _ in range(rowcount)]
            table2 = [[''] * colcount for _ in range(rowcount +1)]
#            print('sel = ',len(selection))
            for i in range(len(columns)):
                
#                print('colcount = ',colcount)
#                print(selection[i].column(),"THIS")
                table2[0][i] = table.model().headerData(selection[i].column(),Qt.Horizontal)
            i = 0
            col = 0
            row = 0
            for index in selection:
                i +=1
#                row = index.row() - rows[0]
#                column = index.column() - columns[0]
#                print('column = ' , col)
#                print(table.model().headerData(index.column(),Qt.Horizontal))
                table1[row][col] = index.data()
                table2[row+1][col] = index.data()
                val = index.data()
                try:
                    result += float(val.replace(',',''))
                except:
                    pass
                col +=1
                if col == colcount:
                    col = 0
                    row += 1
#            print (result)
            if(condition):
                if (i != 1):
                    stream = io.StringIO()
                    csv.writer(stream, dialect = 'excel-tab').writerows(table1)
                    QApplication.clipboard().setText(stream.getvalue())
                elif(i ==1):
                    QApplication.clipboard().setText(val)
            else:
                if (i != 1):
                    stream = io.StringIO()
                    csv.writer(stream, dialect = 'excel-tab').writerows(table2)
                    QApplication.clipboard().setText(stream.getvalue())
                elif(i ==1):
                    QApplication.clipboard().setText(val)
    
        

if __name__ == "__main__":
    appctxt = ApplicationContext()
    Ui = Main()
    appctxt.app.setStyle('Fusion')
    Ui.showMaximized()
    sys.exit(appctxt.app.exec_())
    
    
    
    
    
    
    
    
    
    
    