# -*- coding: utf-8 -*-

# 
#
# Created By: Jose Alvarez

import threading
import plotly.graph_objs as go
import re
import cx_Oracle
import locale
import calendar
import pyodbc
locale.setlocale(locale.LC_ALL, '')
from collections import OrderedDict
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys, csv, io
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import datetime as dt
import numpy as np
import math
import socket # to test for internet connection
from dateutil.relativedelta import relativedelta
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
#from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QMainWindow, QDialog
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.uic import loadUiType
import os
from PandasModel import PandasModel
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.legend_handler import HandlerLine2D
from window import Ui_MainPlotWindow
from plotName import  Ui_plotNameDialog
from messageBox import Ui_msgDialog
from findBox import Ui_Find
from mainCapTool import Ui_MainWindow
from classMsgBox import msgBox

from columnsF import Ui_Columns
from percentChangeCalc import Ui_pChangeCalc
import operator
READY = 0
INPUT = 1
# We use this to get the path to the working directory
directory = os.path.dirname(os.path.abspath(__file__))


def run_dash(layout):
    app = dash.Dash()
    app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),
        html.Div(children='''
                Dash: A web application framework for Python.
                '''), dcc.Graph(id='detail-graph')])
    app.run_server(debug=False)


# THIS FUNCTION IS USED TO CHECK FOR INTERNET CONNECTION AND IT IS USED EVERY TIME THE RUN BUTTON IS CLICKED
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False
################################## =========================================== ##################################
# Function used in the find dialog box to search for items in the qtableview 
def Union(lst1, lst2, lst3,lst4,lst5,lst6): 
    final_list = sorted(list(set().union(lst1, lst2, lst3,lst4,lst5,lst6))) 
    return final_list
# To compute avg function
def Average(lst): 
    return sum(lst) / len(lst) 
# Quick function that checks if all items in a list are the same or not
def all_same(items):
    return all(x == items[0] for x in items)

# CONNECTION TO THE ORACLIENT_SQL_SERVER
#cnn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};DBQ=tppe;Uid=azureuser;Pwd=AzureDF512682!')

        
########################################################### -----------------------------------#####################################################
# THIS IS CLASS IS CRUCIALLY IMPORTANT BECAUSE IT TAKES CARE OF AUTOMATICALLY HIDING NEEDED/UNNEEDED COLUMNS, AND CREATING THE FILTER MENU
########################################################### -----------------------------------#####################################################
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
                
    def addCapacity(self,cols):
        self.dictCols = cols # We store in dictionary
        self.colList.item(0).setCheckState(Qt.Unchecked)
        # This for loop creates a new custom item per each key located in the dictionary
        i = 0


        for name in self.dictCols.keys():
#            print("List after clear Item:", self.colList.item(i).text())
            i+=1
            item = QtWidgets.QListWidgetItem() # Create new custom item
            item.setCheckState(Qt.Checked)
            item.setText(str(name)) # We name the item
            if(str(name) == 'UIDACCOUNT' or str(name) == 'CONTRACTID' or str(name) == 'CUSTOMERID'):
                item.setCheckState(Qt.Unchecked) # Set item Checked to Show
                
            else:
                item.setCheckState(Qt.Checked) # Set Item Unchecked to Hide
            self.colList.addItem(item) #add the item to the listWidget
            
    def addFAV(self,cols):
        self.dictCols = cols # We store in dictionary
        self.colList.item(0).setCheckState(Qt.Unchecked)
        # This for loop creates a new custom item per each key located in the dictionary
        i = 0


        for name in self.dictCols.keys():
#            print("List after clear Item:", self.colList.item(i).text())
            i+=1
            item = QtWidgets.QListWidgetItem() # Create new custom item
            item.setCheckState(Qt.Checked)
            item.setText(str(name)) # We name the item
            if(str(name) == 'BCKST_AVERAGE' or str(name) == 'BCKST_PEAK' or str(name) == 'BCKST_TOTAL' or str(name) == 'AVGDemand (KWHs)'):
                item.setCheckState(Qt.Unchecked) # Set item Checked to Show
                
            else:
                item.setCheckState(Qt.Checked) # Set Item Unchecked to Hide
            self.colList.addItem(item) #add the item to the listWidget

    def displayTags(self, text, IFNYISO, IFPJM):
        i = 0
        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day
        #        IFNYISO = False
        #        IFNYISO = detailYOY['MARKETCODE'].str.contains('NYISO')


        pyNyiso = dt.datetime(int(ny), 5, 1)
        pyNEPJM = dt.datetime(int(ny), 6, 1)
        now = dt.datetime(int(ny), int(nm), int(nd))
        PY2 = str(now.year - 2)[-2:]
        PY1 = str(now.year - 1)[-2:]
        NY = str(now.year)[-2:]
        NY1 = str(now.year + 1)[-2:]
        self.curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
        self.prevTStrip = 'PY ' + PY1 + '|' + PY1 + '\nTransTag'
        if (IFNYISO):
            if now < pyNyiso:
                prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                currentPY = now.year -1
            elif now >= pyNyiso:
                prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
                currentPY = now.year
        else:
            if now < pyNEPJM:
                prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                currentPY = now.year - 1
            elif now >= pyNyiso:
                prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
                currentPY = now.year

        if (text == 'Current PY CapTag'):
            for items in range(self.colList.count()):
                name = self.colList.item(items).text()

                if (str(name) == 'Account ID' or str(name) == nextStrip or str(name) == 'Load\nFactor'
                        or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(
                            name) == 'Forecasted\nPeak kW to\n CapTag Var'
                        or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(
                            name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                        or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(
                            name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Day\nCount'
                        or str(name) == 'Percent\nAlloc' or str(name) == self.curStrip or str(name) == 'TransTag\nto Peak\nkW Var'):


                    if(IFPJM == True):
                        if(str(name) == self.curStrip or str(name) == 'TransTag\nto Peak\nkW Var'):
                            self.Hide(False, self.colList.item(items).text())
                            self.colList.item(items).setCheckState(Qt.Checked)
                    else:
                        self.Hide(False, self.colList.item(items).text())
                        self.colList.item(items).setCheckState(Qt.Checked)


                else:
                    # We hide all other columns that contain 'CapTag'
                    self.Hide(True, self.colList.item(items).text())
                    self.colList.item(items).setCheckState(Qt.Unchecked)


        elif(text == 'Future PY CapTags'):
            for items in range(self.colList.count()):
                name = self.colList.item(items).text()

                if 'PY' in name and 'CapTag' in name:

                    colSplit = name.split()
                    ##                print(col)
                    years = colSplit[1].split('|')
                    yr1 = int(years[0]) + 2000
                    yr2 = int(years[1]) + 2000
                    if (yr1 > currentPY):
                        self.Hide(False, self.colList.item(items).text())
                        self.colList.item(items).setCheckState(Qt.Checked)
                    elif (yr1 < currentPY):
                        self.Hide(True, self.colList.item(items).text())
                        self.colList.item(items).setCheckState(Qt.Unchecked)

                elif (str(name) == 'Account ID' or str(name) == nextStrip or str(name) == 'Load\nFactor'
                        or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(
                            name) == 'Forecasted\nPeak kW to\n CapTag Var'
                        or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(
                            name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                        or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(
                            name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Day\nCount'
                        or str(name) == 'Percent\nAlloc'):

                    self.Hide(False,self.colList.item(items).text())
                    self.colList.item(items).setCheckState(Qt.Checked)

                elif (IFPJM == True):
                    if (str(name) == self.curStrip  or str(name) == 'TransTag\nto Peak\nkW Var'):
                        self.Hide(False, self.colList.item(items).text())
                        self.colList.item(items).setCheckState(Qt.Checked)
                else:
                    # We hide all other columns that contain 'CapTag'
                    self.Hide(True, self.colList.item(items).text())
                    self.colList.item(items).setCheckState(Qt.Unchecked)
        elif(text == 'All CapTags'):
            for items in range(self.colList.count()):
                name = self.colList.item(items).text()

                if (str(name) == 'Account ID' or ('CapTag' in str(name) and 'PY' in str(name)) or str(name) == 'Load\nFactor'
                        or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(
                            name) == 'Forecasted\nPeak kW to\n CapTag Var'
                        or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(
                            name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                        or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(
                            name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Day\nCount'
                        or str(name) == 'Percent\nAlloc'):

                    self.Hide(False, self.colList.item(items).text())
                    self.colList.item(items).setCheckState(Qt.Checked)

                elif (IFPJM == True):
                    if (str(name) == self.curStrip  or str(name) == 'TransTag\nto Peak\nkW Var'):
                        self.Hide(False, self.colList.item(items).text())
                        self.colList.item(items).setCheckState(Qt.Checked)

                else:
                    # We hide all other columns that contain 'CapTag'
                    self.Hide(True, self.colList.item(items).text())
                    self.colList.item(items).setCheckState(Qt.Unchecked)

    
    def addDetailYOY(self,cols,IFNYISO,tagYOYT,IFPJM, *args, **kwargs):
        self.ifTransTable = False
        self.ifTransTable = kwargs.get("transTable")
        if(self.ifTransTable == None):
            self.ifTransTable = False
        
        self.dictCols = cols # We store in dictionary
        self.colList.item(0).setCheckState(Qt.Unchecked)
        
        i = 0
        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day
#        IFNYISO = False
#        IFNYISO = detailYOY['MARKETCODE'].str.contains('NYISO')
        pyNyiso = dt.datetime(int(ny),5,1)
        pyNEPJM = dt.datetime(int(ny),6,1)
        now = dt.datetime(int(ny),int(nm),int(nd))
        PY2 = str(now.year-2)[-2:]
        PY1 = str(now.year-1)[-2:]
        NY =  str(now.year)[-2:]
        NY1 = str(now.year+1)[-2:]
        self.curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
        if(IFNYISO):
            if now < pyNyiso:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        else:
            if now < pyNEPJM:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        
        # This for loop creates a new custom item per each key located in the dictionary
        for name in self.dictCols.keys():
#            print("List after clear Item:", self.colList.item(i).text())
            i+=1
            item = QtWidgets.QListWidgetItem() # Create new custom item
            item.setCheckState(Qt.Checked)
            item.setText(str(name)) # We name the item
            if(tagYOYT == False):
                if(IFPJM == False):
                    if(self.ifTransTable == False):
                        if(str(name) == 'Account ID' or str(name) == nextStrip or str(name) == 'Load\nFactor'
                           or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(name) == 'Forecasted\nPeak kW to\n CapTag Var'
                           or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                           or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Day\nCount'
                           or str(name) == 'Percent\nAlloc'):
                            item.setCheckState(Qt.Checked) # Set item Checked to Show
                        else:    
                            item.setCheckState(Qt.Unchecked) # Set Item Unchecked to Hide    
                    elif(self.ifTransTable == True):
                        item.setCheckState(Qt.Unchecked)
                elif(IFPJM == True):    # IF PJM IS TRUE
                    if(self.ifTransTable == False):
                        if(str(name) == 'Account ID' or str(name) == nextStrip or str(name) == 'Load\nFactor'
                           or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(name) == 'Forecasted\nPeak kW to\n CapTag Var'
                           or str(name) == 'Profile\nCode' or str(name) == 'TransTag\nto Peak\nkW Var' or str(name) == 'Loss Class' or str(name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                           or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Percent\nAlloc'
                           or (str(name) == self.curStrip) or str(name) == 'Day\nCount'):
                            item.setCheckState(Qt.Checked) # Set item Checked to Show
                        else:    
                            item.setCheckState(Qt.Unchecked) # Set Item Unchecked to Hide    
                    elif(self.ifTransTable == True):
                        if(str(name) == 'Account ID' or str(name) == 'TransTag\nYOY Delta'):
                            item.setCheckState(Qt.Checked)
                        elif(('TransTag' not in str(name))):
                            item.setCheckState(Qt.Unchecked)
                        
                self.colList.addItem(item) #add the item to the listWidget
            elif(tagYOYT == True):
                
                if(IFPJM == False):
                    if(str(name) == 'Load\nFactor' or str(name) == 'CUSTOMERNAME' or str(name) == 'CUSTOMERID' or str(name) == 'LDC_ACCOUNT'
                       or str(name) == 'UIDACCOUNT' or str(name) == 'MARKETCODE' or str(name) == 'TAG_TYPE'
                       or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(name) == 'Forecasted\nPeak kW to\n CapTag Var'
                       or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                       or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(name) == 'Forecasted\nAnnual to\nSCA Var' or str(name) == 'Day\nCount'
                       or str(name) == 'SCA\nTotal' or str(name) == 'Percent\nAlloc'):
                        item.setCheckState(Qt.Unchecked) # Set item Unchecked to Hide 
                    else:    
                        item.setCheckState(Qt.Checked) # Set Item Checked to Show   
                else:    
                    if(str(name) == 'Load\nFactor' or str(name) == 'CUSTOMERNAME' or str(name) == 'CUSTOMERID' or str(name) == 'LDC_ACCOUNT'
                       or str(name) == 'UIDACCOUNT' or str(name) == 'MARKETCODE' or str(name) == 'TAG_TYPE'
                       or str(name) == 'Forecasted\nPeak kW' or str(name) == 'Forecasted\nAnnual kWh' or str(name) == 'Forecasted\nPeak kW to\n CapTag Var'
                       or str(name) == 'Profile\nCode' or str(name) == 'Loss Class' or str(name) == 'Summer\nPeak kW' or str(name) == 'CapTag\nFactor'
                       or str(name) == 'Summer\nPeak kW to\nCapTag Var' or str(name) == 'Forecasted\nAnnual to\nSCA Var' or ('Trans' in str(name)
                       or str(name) == 'Day\nCount' or str(name) == 'SCA\nTotal') or str(name) == 'Percent\nAlloc'):
                        item.setCheckState(Qt.Unchecked) # Set item Checked to Show
                    else:    
                        item.setCheckState(Qt.Checked) # Set Item Unchecked to Hide    
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

########################################################### -----------------------------------#####################################################
####################################################################################################################################################

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
        

# CALLS THE PCHANGE DIALOG AND RUNS THE PERCENT CHANGE CALCULATOR
class pChange(QDialog, Ui_pChangeCalc):
    def __init__(self, ):
        super(pChange, self).__init__()
        self.setupUi(self)
        self.v2Entry.textChanged.connect(self.calculate) # Signal to Calculate when text changes
        self.v1Entry.textChanged.connect(self.calculate) # Signal to Calculate when text changes
#        prNum = self.lineEdit.text()
#        revNum = self.lineEdit_2.text()
        
    
    def calculate(self,):
        _translate = QtCore.QCoreApplication.translate
        v1 = str(self.v1Entry.text())
        v2 = str(self.v2Entry.text())
        v1 = v1.replace(',','')
        v1 = v1.replace('%','')
        v2 = v2.replace(',','')
        v2 = v2.replace('%','')
        
        # (v1-v2)/(abs(v1)) *100
        try:
            v1 = float(v1)
            v2 = float(v2)
        except:
            self.pChangeRes.setText(_translate("pChangeRes", "ERROR!"))
        else:
            try:
                pChange = (v2-v1)/(abs(v1)) *100
            except:
                self.pChangeRes.setText(_translate("pChangeRes", "ERROR!"))
            else:
                if (pChange == np.nan):
                    self.pChangeRes.setText(_translate("pChangeRes", "    nan %"))
                elif (pChange == np.inf or pChange == -np.Inf):
                    self.pChangeRes.setText(_translate("pChangeRes", "    DIV/0 !"))
                else:
                    self.pChangeRes.setText(_translate("pChangeRes", "    " + str(round(pChange)) + " %"))
        # "    0.00 %"
################################################################################################################################################################
################################################################################################################################################################

class namePlot(QDialog, Ui_plotNameDialog):
    def __init__(self, plotObj, fig1):
        super(namePlot, self).__init__()
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
        if (strName == ''):
            #            print("EMPTY!")
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Empty Field. Enter again!"))
            self.msgBox1.show()
        elif (len(res) > 0):
            #            print("Enter another Name!")
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Duplicate. Enter another Name!"))
            self.msgBox1.show()

        elif (len(res) == 0):
            #            print("no duplicates")
            plotObj.addfig(strName, fig1)
            self.close()


################################################################################################################################################################
################################################################################################################################################################
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

        
# THE MAIN FUNCTION IS IN CHARGE OF DEPLOYING ALL THE NECESSARY FUNCTIONS TO RUN OUR PROGRAM
# IT EXECUTES THE DEFINED FUNCTIONS ABOVE, AS WELL AS THE FUNCTIONS IMPORTED FROM THE FILES THAT WERE CONVERTED FROM UI TO PY FILES
# THE MAIN FUNCTION SIMPLIFIES THE ABILITY TO RUN OUR GUI IN AN ELEGANT, AND REFRACTORED WAY WHICH IS MORE APPEALING AND ORGANIZE-ABLE!
# THE INIT METHOD FIRST CREATES THE NECESSARY TABLES WITH THE NECESSARY ATTRIBUTES PER TABLE,
        # EXAMPLES INCLUDE, CONTEXT MENU, CONNECT TO BUTTON CLICKS, TRIGGERS, OR FILTERS AS WELL AS SIMPLE OPERATIONS LIKE COPYING TO CB
        
class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        
        super(Main, self).__init__()
        self.setupUi(self)

        self.PDF = (appctxt.get_resource('Documentation.pdf'))

        self.PDFJS = (appctxt.get_resource('pdfjs/web/viewer.html'))
        self.PDFJS = self.PDFJS.replace("\\","/")
        self.PDFJS = 'file:///' + self.PDFJS

        test = self.PDFJS + '?file=' + self.PDF

        self.webEngineViewPDF.load(QtCore.QUrl.fromUserInput(test))

        self.figure = Figure()
        self.figure.set_edgecolor('#041318')
        self.figure.set_facecolor('#32414B')

        self.figureDV = Figure() # THIS IS THE FIGURE THAT MANAGES THE PLOTS IN THE DETAILED VIEW TAB
        self.figureDV.set_edgecolor('#041318')
        self.figureDV.set_facecolor('#32414B')
        self.figureDV.subplots_adjust(bottom=0.18)
        self.axDV = self.figureDV.gca()

        self.plot = Plot() # Creates Plot Menu Tool 

        self.figure.set_figheight(3.5)
        self.figure.subplots_adjust(bottom = 0.23,left = .18)
        self.ax = self.figure.gca()
        # self.accts2Plot.itemClicked.connect(self.onClickDetailedView)
        self.accts2Plot.currentItemChanged.connect(self.onClickDetailedView)

        # TESTING OF DASH PLOTLY
        import concurrent.futures





        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(run_dash,layout)
        #     app = future.result()


        # app.callback(dash.dependencies.Output('detail-graph', 'figure'))(self.calculateSummerPeaks())
        
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
        self.scCapTagsCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capTags,lambda: self.copySlot(self.capTags,True)) # shortcut to copy multiple values in table
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
        self.scDetailYOYcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.detailYOY,lambda: self.copySlot(self.detailYOY,True)) # Shortcut to copy is created and connected
        self.scDetailYOYcopy.setContext(Qt.WidgetShortcut) # Context is set for shortcut

        self.scDetailYOYPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.detailYOY) # Shortcut to Plot in detailed view is set
        self.scDetailYOYPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scDetailYOYPLT.activated.connect(lambda: self.detailedViewSlot(self.detailYOY))

        ######################################################################################################################

        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE DETAILED VIEW DATA FOR EACH INDIVIDUAL ACCOUNT
        self.acctDetailTableView.setContextMenuPolicy(Qt.CustomContextMenu) # Sets the policy for the context menu ( to be able to add a custom context menu)
        self.acctDetailTableViewCols = filterCols(self.acctDetailTableView) # This creates the filter meny for the acctsDetailed view table
        self.acctDetailTableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # Allows for extended selection + multi selection + single-selection
        self.acctDetailTableView.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.acctDetailTableView)) # Calls custom context menu and table is inputted
        self.scAcctDetailedView = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.acctDetailTableView) # Shortcut to find
        self.scAcctDetailedView.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scAcctDetailedView.activated.connect(lambda: self.execFind(self.acctDetailTableView)) # Shortcut for find is connected to the find function

        self.scAcctDetailedViewCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.acctDetailTableView,lambda: self.copySlot(self.acctDetailTableView,True)) # Shortcut to copy is created and connected
        self.scAcctDetailedViewCopy.setContext(Qt.WidgetShortcut) # Context is set for shortcut

        self.scAcctDetailedViewPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.acctDetailTableView) # Shortcut to Plot in detailed view is set
        self.scAcctDetailedViewPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scAcctDetailedViewPLT.activated.connect(lambda: self.detailedViewSlot(self.acctDetailTableView))

        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE CAPACITY OVERALL DATA TABLE
        self.capacity.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.capacityCols = filterCols(self.capacity) # This Creates the filter menu for the capacity overall table
        self.capacity.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capacity)) # Calls custom context menu and table is inputed
#        self.capTags.clicked.connect(lambda: self.onSelection(self.capacity))
        self.scCapacity = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capacity) # Shortcut to find
        self.scCapacity.setContext(Qt.WidgetShortcut) # Sets context for Shortcut
        self.scCapacity.activated.connect(lambda: self.execFind(self.capacity)) # Shortcut is connected to find function
        self.scCapacityCopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capacity,lambda: self.copySlot(self.capacity,True)) # Shortcut for copying is created and connected
        self.scCapacityCopy.setContext(Qt.WidgetShortcut) # Sets fcontext for shortcut
        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE tags - YOY TABLE
        self.capTagsYOY.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.capTagsYOYCols = filterCols(self.capTagsYOY) # This Creates the filter menu for the detailYOY table
        self.capTagsYOY.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # Allows for extended selection + multi-selection + single-selection
        self.capTagsYOY.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.capTagsYOY)) # Calls custom context menu and table is inputed
        self.sccapTagsYOY = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.capTagsYOY) # Shortcut to find
        self.sccapTagsYOY.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.sccapTagsYOY.activated.connect(lambda: self.execFind(self.capTagsYOY)) # Shortcut for find is connected to the find function
        self.sccapTagsYOYcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.capTagsYOY,lambda: self.copySlot(self.capTagsYOY,True)) # Shortcut to copy is created and connected
        self.sccapTagsYOYcopy.setContext(Qt.WidgetShortcut) # Context is set for shortcut

        self.sccapTagsYOYPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.capTagsYOY) # Shortcut to Plot in detailed view is set
        self.sccapTagsYOYPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.sccapTagsYOYPLT.activated.connect(lambda: self.detailedViewSlot(self.capTagsYOY))

        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE TransTags - YOY TABLE
        self.transTagsYOY.setContextMenuPolicy(Qt.CustomContextMenu) # Creates custom context menu
        self.transTagsYOYCols = filterCols(self.transTagsYOY) # This Creates the filter menu for the detailYOY table
        self.transTagsYOY.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # Allows for extended selection + multi-selection + single-selection
        self.transTagsYOY.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.transTagsYOY)) # Calls custom context menu and table is inputed
        self.sctransTagsYOY = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.transTagsYOY) # Shortcut to find
        self.sctransTagsYOY.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.sctransTagsYOY.activated.connect(lambda: self.execFind(self.transTagsYOY)) # Shortcut for find is connected to the find function
        self.sctransTagsYOYcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.transTagsYOY,lambda: self.copySlot(self.transTagsYOY,True)) # Shortcut to copy is created and connected
        self.sctransTagsYOYcopy.setContext(Qt.WidgetShortcut) # Context is set for shortcut

        self.sctransTagsYOYPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.transTagsYOY) # Shortcut to Plot in detailed view is set
        self.sctransTagsYOYPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.sctransTagsYOYPLT.activated.connect(lambda: self.detailedViewSlot(self.transTagsYOY))

        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE METERREADSPR TABLE
#        self.mrCheckBox.setCheckState(Qt.Checked)
#         self.mrCheckBox.stateChanged.connect(self.onClickChangeMR)
        self.comboBoxMRHists.currentTextChanged[str].connect(self.onClickChangeMR)
        self.displayTagsComboBox.activated[str].connect(self.onClickChangeTags)

        self.meterReadPR.setContextMenuPolicy(Qt.CustomContextMenu) # sets the custom context menu policy and creates it
        self.meterReadPRCols = filterCols(self.meterReadPR) # This Creates the filter menu for the meter Reads PR table
        self.meterReadPR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterReadPR))  # Calls custom context menu and table is inputed
        self.scMeterReadPR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterReadPR) # Creates Shortcut to find items
        self.scMeterReadPR.activated.connect(lambda: self.execFind(self.meterReadPR)) # connects shortcut to find items with this table
        self.scMeterReadPR.setContext(Qt.WidgetShortcut) # sets the context for the shortcut
        self.scMeterReadPRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterReadPR,lambda: self.copySlot(self.meterReadPR,True)) # Creates the shortcut for multiselection as well as connecting it to copySlot
        self.scMeterReadPRcopy.setContext(Qt.WidgetShortcut) # Sets the context for the shortcut

        self.scMeterReadPRPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.meterReadPR) # Shortcut to Plot in detailed view is set
        self.scMeterReadPRPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scMeterReadPRPLT.activated.connect(lambda: self.detailedViewSlot(self.meterReadPR))

        ######################################################################################################################
        
        ######################################################################################################################
        # THIS TABLE IS IN CHARGE OF DISPLAYING THE  METERVALUES PR TABLE
        self.meterValuePR.setContextMenuPolicy(Qt.CustomContextMenu) # Creats custom context menu policy and the custom context menu itself
        self.meterValuePRCols = filterCols(self.meterValuePR) # This Creates the filter menu for the meter Values table
        self.meterValuePR.customContextMenuRequested.connect(lambda: self.contextMenuEvent(self.meterValuePR)) # Conencts the custom context menu to this table by taking it as input
        self.scMeterValuePR = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+f'), self.meterValuePR) # Creates shortcut for finding items
        self.scMeterValuePR.setContext(Qt.WidgetShortcut) # Sets the contex for the shortcut
        self.scMeterValuePR.activated.connect(lambda: self.execFind(self.meterValuePR)) # Connects the shortcut to the find function
        self.scMeterValuePRcopy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self.meterValuePR,lambda: self.copySlot(self.meterValuePR,True)) # Creates and connects the shortcut for multi-selection - copying                                                                                                                             # to the copy Slot function
        self.scMeterValuePRcopy.setContext(Qt.WidgetShortcut) # Sets the context for the shortcut

        self.scMeterValuePRPLT = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.SHIFT + Qt.Key_Z), self.meterValuePR) # Shortcut to Plot in detailed view is set
        self.scMeterValuePRPLT.setContext(Qt.WidgetShortcut) # Context is set for shortcut
        self.scMeterValuePRPLT.activated.connect(lambda: self.detailedViewSlot(self.meterValuePR))

        ######################################################################################################################
        
        self.actionQuit.triggered.connect(QtWidgets.QApplication.quit)   # ACTION TO QUIT APPLICATION IN MENU BAR
        self.actionPercent_Change_Calc.triggered.connect(self.execPChange)
        self.timeStampCheckBox1.stateChanged.connect(lambda: self.onClickTimestampCheckBox(1))
        self.timeStampCheckBox3.stateChanged.connect(lambda: self.onClickTimestampCheckBox(3))

#        self.actionRestart.triggered.connect(restart_program())

        ################################################################################################################
        # DISPLAYS AN EMPTY TABLE FOR EACH OF THE TABLES - CAPACITY TAGS, DETAIL YOY, METER READS, METER VALUES, CAPACITY
        emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
        emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'YOY\nDelta'])
        emptyCaptagsYOY = pd.DataFrame(columns = ['TAGS YOY'])
        emptyTranstagsYOY = pd.DataFrame(columns = ['TRANS\nTAGS YOY'])
        emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                           'TAG_TYPE','TAG','Strip'])
        emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                            'ONPEAK_KWH','PEAKDEMAND'])
        emptyMeterReads = pd.DataFrame(columns = ['ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
        emptyDetailedView = pd.DataFrame(columns=['Account ID', 'Start\nDate','End\nDate','Start\nYear','Summer\nPeak kW','Forecasted\nPeak kW', 'Capacity Tag'])

        # THIS SETS THE MODELS IN THE QTABLEVIEWS
        self.capTags.setModel(PandasModel(emptyCapTags))
        self.capacity.setModel(PandasModel(emptyCap))
        self.capTagsYOY.setModel(PandasModel(emptyCaptagsYOY))
        self.transTagsYOY.setModel(PandasModel(emptyTranstagsYOY))
        self.detailYOY.setModel(PandasModel(emptydetailYOY))
        self.meterReadPR.setModel(PandasModel(emptyMeterReads))
        self.meterValuePR.setModel(PandasModel(emptyMeterVal))
        self.acctDetailTableView.setModel(PandasModel(emptyDetailedView))
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

        
        data['STOPTIME'] = pd.to_datetime(data['STOPTIME'])     # Convert date-type to only display Date w/o time
        data['STOPTIME'] = data['STOPTIME'].dt.date
        data['STARTTIME'] = pd.to_datetime(data['STARTTIME'])   # Convert date-type to only display Date w/o time
        data['STARTTIME'] = data['STARTTIME'].dt.date
        
        planYears = []
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
                planYears.append('PY ' +str(startDate.year)[-2:] + '|' + str(endDate.year)[-2:])
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

                    if ("MISO" in data.MARKETCODE.values):
                        maskTrans = (data['STARTTIME'] >= startDateOrig) & (data['STOPTIME'] <= endDateOrig - relativedelta(days=1)) & (data['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD')
                    else:
                        maskTrans = (data['STARTTIME'] <= startDateOrig) & (data['STOPTIME'] >= endDateOrig - relativedelta(days=1)) & (data['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD')
                        # QUESTIONING THE GREATER THAN OR EQUAL TO AND VICE-VERSA ABOVE
                    df2 = data.loc[maskTrans]
                    # transVal = df2['TAG'].sum()
                    if ("MISO" in data.MARKETCODE.values):
                        transVal = df2['TAG'].sum()/12 # We divide by 12 since MISO has a month to month tag and we want to know the avg yearly tag
                    else:

                        transVal = df2['TAG'].sum()

    
                startDateOrig = startDateOrig + relativedelta(years = 1)
                endDateOrig = endDateOrig + relativedelta(years = 1)
                        
                maskCap = (data['STARTTIME'] <= startDate) & (data['STOPTIME'] >= endDate) & (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD')
                df1 = data.loc[maskCap]
                capTag = df1['TAG'].sum()
                planYear = "June " + str(startDate.year) + " - " + "May " + str(endDate.year)
                planYears.append('PY ' +str(startDate.year)[-2:] + '|' + str(endDate.year)[-2:])
                capTags = capTags.append(pd.Series([planYear, capTag, transVal, acctCount], index = capTags.columns), ignore_index = True)
                startDate = startDate + relativedelta(years = 1)
                endDate = endDate + relativedelta(years = 1)
                acctCount = 0

       
        self.ax = self.figure.gca()
        
        N = len(capTags['Capacity Tag'])
        ind = np.arange(N)
        self.ax.clear()
        
        self.capTagsBars = self.ax.bar(ind, capTags['Capacity Tag'],0.3,color = '#061e26', label = 'CapTags')
#        self.figure.legend(self.capTagsBars,['CapTags'],loc='upper left',shadow=True,fontsize=8,markerscale=.9)
        
        self.ax.set_xticks(ind)
        self.ax.set_xticklabels(planYears, rotation = 45)
        self.ax.tick_params(labelcolor='#2ed2d0')
        self.ax.set_title('Capacity Tags YOY', color='#FFFFFF')
#        ax.set_xlabel('Planning Year', color = '#FFFFFF')
        self.ax.set_ylabel('Capacity Tag', color = '#FFFFFF')
        capTags['Capacity Tag'] = capTags.apply(lambda x: "{:,.2f}".format(x['Capacity Tag']), axis=1)
        
#        print(data.MARKETCODE)
        try:
            if(("PJM" in data.MARKETCODE.values)| ("MISO" in data.MARKETCODE.values)):
                capTags['Transmission'] = capTags.apply(lambda x: "{:,.2f}".format(x['Transmission']), axis=1) # HERE FOR MISO
        except:
            
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("Error on Captags Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
            self.msgBox1.show()
        
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
    
    def ercotData(self, prNum, revNum):
        
        sqlQuery = ("""
                    
SELECT 
    DISTINCT A.*
FROM
    pwrline.acctoverridehist B,
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
    OR A.marketcode= 'MISO'
    OR A.marketcode= 'ERCOT'
    )

ORDER BY 
    A.customername,
    A.accountid
                    """).format(prNum=prNum, revNum=revNum)



    
        data = pd.read_sql(sqlQuery,self.conn)
        self.mrDict2 = pd.Series(data['PROFILECODE'].values,index=data['ACCOUNTID']).to_dict()
        # self.lossFactorDict = pd.Series(data['LOSSFACTOR'].values, index=data['ACCOUNTID']).to_dict()
        
        return data
        
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
    B.val AS Tag,
    B.lstime
    
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
        data = pd.read_sql(sqlQuery,self.conn)
#        data = pd.read_sql(sqlQuery, self.cnn)
        if data.empty:
            return data
        else:
            if roundOrNot == 1:
                
                data['TAG'] = data.apply(lambda x: "{:,.2f}".format(x['TAG']), axis=1)
                try:
                    data['STOPTIME'] = pd.to_datetime(data['STOPTIME'])     # Convert date-type to only display Date w/o time
                    data['STOPTIME'] = data['STOPTIME'].dt.date
                    data['STARTTIME'] = pd.to_datetime(data['STARTTIME'])   # Convert date-type to only display Date w/o time
                    data['STARTTIME'] = data['STARTTIME'].dt.date
                except:
                    pass
                data = data.fillna(value = 0)
                data.replace([0,0.0],'',inplace = True)
                return data
            elif roundOrNot == 2:
                listDict = {}
                i = 0
                for col in data.columns:
                    listDict.update({col:i})
#                    print(listDict)
                    i+=1
                self.capacityCols.addCapacity(listDict)
                
            return data
    
    def detailYOYfunc(self, data):
            #### DETAIL YOY TAB ####
        
        tagDF_DM = data.copy()
        tagDF_DM['CUSTOMERNAME'].replace([None,'None'], np.nan, inplace = True) # converts any None or "None" cells to np.nan in CUSTOMERNAME column
        tagDF_DM['CUSTOMERNAME'].replace('', np.nan, inplace=True) # CONVERTS ANY EMPTY CELLS TO np.nan in CUSTOMERNAME col
        
        tagDF_DM['STARTTIME'] = pd.to_datetime(tagDF_DM['STARTTIME'])
        tagDF_DM['STOPTIME'] = pd.to_datetime(tagDF_DM['STOPTIME'])
        tagDF_DM['Strip'] = 'PY ' + tagDF_DM['STARTTIME'].dt.strftime("%y") + '|' + tagDF_DM['STOPTIME'].dt.strftime("%y") + '\nCapTag'
        tagDF_DM['Strip'] = np.where(tagDF_DM['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD', 'PY ' + tagDF_DM['STARTTIME'].dt.strftime("%y") + '|' + tagDF_DM['STOPTIME'].dt.strftime("%y") + '\nTransTag',tagDF_DM['Strip'])

        # replaces empty spots with 'nan'
        # fills in null cells with 0
#        tagDF_DM['TAG'].fillna(value = 0)
        tagDF_DM['TAG'].replace('', np.nan, inplace=True)
        tagDF_DM['TAG'].replace('nan', np.nan, inplace=True)
#        tagDF_DM['TAG'].replace(np.nan, 0, inplace=True)
        maskCapTagOvrd = (data['TAG_TYPE'] == 'CAPACITY_TAG_OVRD') # Mask Filter Tag Type by Capacity Tag Ovrd
        
        if(data['MARKETCODE'].str.contains('PJM').any() or data['MARKETCODE'].str.contains('MISO').any()):
                
            maskTrans = (data['TAG_TYPE'] == 'TRANSMISSION_TAG_OVRD')
            transTags = tagDF_DM.loc[maskTrans]

            #IF PJM WE CALCULATE THE SUM OF TAGS
            if (data['MARKETCODE'].str.contains('PJM').any()):
                pivTab2 = pd.pivot_table(transTags, columns = ['Strip'], index = ['CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','PROFILECODE','LOSS_CLASS','TAG_TYPE'], values = ['TAG'], aggfunc = np.sum)
            # IF MISO WE CALCULATE AVG OF TAGS INSTEAD
            elif (data['MARKETCODE'].str.contains('MISO').any()):
                pivTab2 = pd.pivot_table(transTags, columns = ['Strip'], index = ['CUSTOMERID', 'LDC_ACCOUNT', 'ACCOUNTID', 'UIDACCOUNT', 'MARKETCODE','PROFILECODE', 'LOSS_CLASS', 'TAG_TYPE'], values=['TAG'],aggfunc=np.mean)
            pivTabTags2 = pivTab2.reset_index(drop = True) # resets indexes to only keep the TAGS by Strips
            pivTab2 = pivTab2.reset_index(drop = False)
            
            pivTab2.columns = pivTab2.columns.get_level_values(0) # resets indexes back to normal with Tags grouped by strips (STRIPS WILL BE REMOVED TO CONCATENATE LATER)
            pivTab2.drop(columns = ['TAG'], inplace = True) # We drop any columns named 'TAG', since they will be renamed by pivTabTags
            pivTabTags2.columns = pivTabTags2.columns.get_level_values(1) # We do this to keep the names of the Yearly Strips (ie. 2018 - 2019, 2019-2020, etc.)
            transTags = pd.concat([pivTab2, pivTabTags2], axis = 1, sort = False) # We concatenate to get our goal Table with columns renamed effectively


        tagDF_DM = tagDF_DM.loc[maskCapTagOvrd] # Apply Mask Filter
        
        pivTab = pd.pivot_table(tagDF_DM, columns = ['Strip'], index = ['CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','PROFILECODE','LOSS_CLASS','TAG_TYPE'], values = ['TAG'], aggfunc = np.sum)
        pivTabTags = pivTab.reset_index(drop = True) # resets indexes to only keep the TAGS by Strips
        pivTab = pivTab.reset_index(drop = False) # resets indexes back to normal with Tags grouped by strips (STRIPS WILL BE REMOVED TO CONCATENATE LATER)
        pivTab.columns = pivTab.columns.get_level_values(0) # We keep the values from Level 0, specifically to fix renaming issue on MultiIndex tables
        pivTab.drop(columns = ['TAG'], inplace = True) # We drop any columns named 'TAG', since they will be renamed by pivTabTags
        pivTabTags.columns = pivTabTags.columns.get_level_values(1) # We do this to keep the names of the Yearly Strips (ie. 2018 - 2019, 2019-2020, etc.)
        
        tagDF_DM = pd.concat([pivTab, pivTabTags], axis = 1, sort = False) # We concatenate to get our goal Table with columns renamed effectively
        
        
        if(data['MARKETCODE'].str.contains('PJM').any()  or data['MARKETCODE'].str.contains('MISO').any()):
            tagDF_DM2 = pd.concat([tagDF_DM, transTags], axis=1, sort=False)
            tagDF_DM2 = tagDF_DM2.loc[:,~tagDF_DM2.columns.duplicated()]
            tagDF_DM2 = pd.concat([tagDF_DM, transTags], axis=1, sort=False)
            tagDF_DM2 = tagDF_DM2.loc[:,~tagDF_DM2.columns.duplicated()]
            detailYOY = tagDF_DM2
        else:
            detailYOY = tagDF_DM
            detailYOY = detailYOY.fillna(value = 0)

        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day
        PY2 = str(now.year-2)[-2:] # CHANGE HERE
        PY1 = str(now.year-1)[-2:] # CHANGE HERE
        NY =  str(now.year)[-2:] # CHANGE HERE
        NY1 = str(now.year+1)[-2:] # CHANGE HERE
        self.curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
        self.prevTStrip = 'PY ' + PY1 + '|' + PY1 + '\nTransTag'
        IFNYISO = False
        checkMin = False
        checkMax = False
        IFNYISO = detailYOY['MARKETCODE'].str.contains('NYISO').any()
        self.IFNYISO = IFNYISO
        pyNyiso = dt.datetime(int(ny),5,1)
        pyNEPJM = dt.datetime(int(ny),6,1)
        now = dt.datetime(int(ny),int(nm),int(nd))
        if(IFNYISO):
            if now < pyNyiso:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        else:
            if now < pyNEPJM:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        
        transCurrentY = False
        transPrevY = False
                 
        for i in detailYOY.columns:
            if i == prevStrip:
                checkMin = True
            if i == self.curStrip :
                transCurrentY = True
                

        for i in detailYOY.columns:
            if i ==  nextStrip:
                checkMax = True
            if i == self.prevTStrip:
                transPrevY = True
          
        
        if(checkMin and checkMax):
            v1 = detailYOY[nextStrip]
            v2 = detailYOY[prevStrip]
            
            detailYOY['YOY\nDelta'] = (v1-v2)/(abs(v2)) *100
            detailYOY['YOY\nDelta'] =detailYOY['YOY\nDelta'].replace([-np.Inf,np.inf,-np.Inf],np.nan)

        elif(checkMin):
            detailYOY['YOY\nDelta'] = 0
                
        elif(checkMax):
            detailYOY['YOY\nDelta'] = 0

        else:
            detailYOY['YOY\nDelta'] = 0

                
                    
        if(detailYOY['MARKETCODE'].str.contains('PJM').any()  or data['MARKETCODE'].str.contains('MISO').any()):
            if( transCurrentY and transPrevY):
                v1 = detailYOY[self.curStrip]
                v2 = detailYOY[self.prevTStrip]
                detailYOY['TransTag\nYOY Delta'] = (v1-v2)/(abs(v2)) *100
                
            elif(transPrevY):    
                    detailYOY['TransTag\nYOY Delta'] = 0   
                    
            elif(transCurrentY):
                    detailYOY['TransTag\nYOY Delta'] = 0  
                    

        pyNyiso = dt.datetime(int(ny),5,1)
        detailYOY = detailYOY.set_index('ACCOUNTID')
        #detailYOY.loc["Grand Total"] = detailYOY.sum()
        detailYOY = detailYOY.append(detailYOY.sum(numeric_only = True).rename('GRAND TOTAL'))
        detailYOY = detailYOY.reset_index(drop = False) 
        
        for i in range(len(detailYOY.columns) - 8):
            if(detailYOY['MARKETCODE'].str.contains('PJM').any()  or data['MARKETCODE'].str.contains('MISO').any()):
                
                if(i + 8 == len(detailYOY.columns) -1 or i + 8 == len(detailYOY.columns) -2 ):
                    detailYOY.iloc[:,i + 8] = detailYOY.apply(lambda x: "{:,.0f}%".format(x[(i + 8)]), axis=1)
                else:
                    detailYOY.iloc[:,i + 8] = detailYOY.apply(lambda x: "{:,.2f}".format(x[(i+8)]), axis=1)
#                detailYOY['YOY\nDelta'] = detailYOY.apply(lambda x: "{:,.0f}%".format(x['YOY\nDelta']), axis=1) 
            else: 
                if(i + 8 == len(detailYOY.columns) -1):
                    detailYOY.iloc[:,i + 8] = detailYOY.apply(lambda x: "{:,.0f}%".format(x[(i + 8)]), axis=1)
                else:
                    detailYOY.iloc[:,i + 8] = detailYOY.apply(lambda x: "{:,.2f}".format(x[(i+8)]), axis=1)
        detailYOY['YOY\nDelta'] = detailYOY['YOY\nDelta'].replace('nan%','nan')
        if(detailYOY['MARKETCODE'].str.contains('PJM').any()  or data['MARKETCODE'].str.contains('MISO').any()):
            detailYOY['TransTag\nYOY Delta'] = detailYOY['TransTag\nYOY Delta'].replace('nan%','nan')

        
        return detailYOY, IFNYISO
       
        
    def meterValue(self, prNum, revNum, ny):
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
INNER JOIN metervalue mv on a.uidaccount = mv.uidaccount),
summarized_df AS (
SELECT 
    mv.*,
    TO_CHAR(mv.STARTTIME, 'YYYY') || ' - ' || TO_CHAR(mv.STARTTIME, 'YYYY') AS STRIP 
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
INNER JOIN meter_value mv on oa.uidaccount = mv.account_join_id )
    SELECT ACCOUNTID, LDC_ACCOUNT,
        NAME as METRICS,VAL AS VALUE,
        STARTTIME,
        STOPTIME,
        STRIP

    FROM 
        summarized_df
                            
        """).format(prNum=prNum, revNum=revNum)
    
        
        meterVal = pd.read_sql(sqlQuery, self.conn)
        if meterVal.empty:
            favDict = {}
            empty = True
            return meterVal, meterVal, favDict, empty
        
        meterVal['STARTTIME'] = pd.to_datetime(meterVal['STARTTIME'])
        meterVal['STOPTIME'] = pd.to_datetime(meterVal['STOPTIME'])

        metValPiv2 = pd.pivot_table(meterVal, columns = ['METRICS'], index = ['ACCOUNTID','LDC_ACCOUNT', 'STARTTIME','STOPTIME', 'STRIP'], values = ['VALUE'], aggfunc = np.sum)
        metValPiv2.columns = metValPiv2.columns.droplevel()
        metValPiv2 = metValPiv2.reset_index(drop = False) # Resets Index and eliminates Multiindexing while also renaming columns automatically


        
        ##################################################################
        # This sections creates columns = np.nan if they're non-existent #
        # if an error is detecteded (meaning col doesnt exist, it will create the column)
        try:
            col = metValPiv2.columns.get_loc('AVERAGEDEMAND')
        except:
            metValPiv2['AVERAGEDEMAND'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('ANNUAL_KWH')
        except:
            metValPiv2['ANNUAL_KWH'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('PEAKDEMAND')
        except:
            metValPiv2['PEAKDEMAND'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('ONPEAK_KWH')
        except:
            metValPiv2['ONPEAK_KWH'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('OFFPEAK_KWH')
        except:
            metValPiv2['OFFPEAK_KWH'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('BCKST_AVERAGE')
        except:
            metValPiv2['BCKST_AVERAGE'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('BCKST_PEAK')
        except:
            metValPiv2['BCKST_PEAK'] = np.nan
        try:
            col = metValPiv2.columns.get_loc('BCKST_TOTAL')
        except:
            metValPiv2['BCKST_TOTAL'] = np.nan
        ##################################################################



            
        metValPiv2['STARTTIME'] = pd.to_datetime(metValPiv2['STARTTIME'])
        metValPiv2['STOPTIME'] = pd.to_datetime(metValPiv2['STOPTIME'])


        # metValPiv2['LSTIME'] = pd.to_datetime(metValPiv2['LSTIME'])
#        print(metValPiv2)
        try:
            metValPiv2 =metValPiv2[['ACCOUNTID','LDC_ACCOUNT','STARTTIME','STOPTIME','STRIP',
                                    'ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND','BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']]
        except:
            metValPiv2 =metValPiv2[['ACCOUNTID','LDC_ACCOUNT','STARTTIME','STOPTIME','STRIP',
                                        'ANNUAL_KWH','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND','BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']]

        # filter = (metValPiv2.STARTTIME.dt.year == ny)


        metValPiv2 = metValPiv2[pd.notnull(metValPiv2['ANNUAL_KWH'])]

        # with pd.option_context('display.max_rows', None, 'display.max_columns',
        #                        None):  # more options can be specified also
        #     print(metValPiv2)

        try:
            metValPiv2 = metValPiv2.loc[(metValPiv2.ANNUAL_KWH != 0 ) | ( metValPiv2.LOADFACTOR != 0 )|  (metValPiv2.AVERAGEDEMAND != 0) | (metValPiv2.ONPEAK_KWH != 0) | ( metValPiv2.OFFPEAK_KWH != 0) | (metValPiv2.PEAKDEMAND != 0) | (metValPiv2.BCKST_AVERAGE != 0) | (metValPiv2.BCKST_PEAK != 0) | (metValPiv2.BCKST_TOTAL != 0)]
        except:
            metValPiv2 = metValPiv2.loc[(metValPiv2.ANNUAL_KWH != 0 ) |  (metValPiv2.AVERAGEDEMAND != 0) | (metValPiv2.ONPEAK_KWH != 0) | ( metValPiv2.OFFPEAK_KWH != 0) | (metValPiv2.PEAKDEMAND != 0) | (metValPiv2.BCKST_AVERAGE != 0) | (metValPiv2.BCKST_PEAK != 0) | (metValPiv2.BCKST_TOTAL != 0)]
        metValPiv2 = metValPiv2.dropna(subset = ['ACCOUNTID'])
        try:
            meterValfin1_1 = pd.pivot_table(metValPiv2, index = ['STRIP', 'ACCOUNTID'], values = ['ANNUAL_KWH','LOADFACTOR','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND','BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL'],fill_value = 0, aggfunc = np.sum)
        except:
            meterValfin1_1 = pd.pivot_table(metValPiv2, index = ['STRIP', 'ACCOUNTID'], values = ['ANNUAL_KWH','AVERAGEDEMAND','ONPEAK_KWH','OFFPEAK_KWH','PEAKDEMAND','BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL'],fill_value = 0, aggfunc = np.sum)
        
        meterValFIN= meterValfin1_1.reset_index(drop = False)

        try:
            sumKWH = meterValFIN['ANNUAL_KWH'].sum()
            weightF = meterValFIN['ANNUAL_KWH']/sumKWH
            meterValFIN['LOADFACTOR'] = ((meterValFIN['ANNUAL_KWH'])/(meterValFIN['PEAKDEMAND']*8760))*100
            meterValFIN['LOADFACTOR'].replace([-np.Inf,np.inf,-np.Inf,200],np.nan,inplace = True)
            
            weight = meterValFIN['LOADFACTOR'] * weightF
            self.sumLF = weight.sum()
#            print(sumLF)
        except:
            pass
        # print(meterValFIN)

        meterValFIN = meterValFIN.sort_values(by = ['ANNUAL_KWH'],ascending = False)

        try:
            
            meterValFIN['LOADFACTOR'] = meterValFIN.apply(lambda x: "{:,.0f}%".format(x['LOADFACTOR']), axis=1)

        except:
            pass


#        meterValFIN['ANNUAL_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ANNUAL_KWH']), axis=1)
        meterValFIN['OFFPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['OFFPEAK_KWH']), axis=1)
        meterValFIN['ONPEAK_KWH'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['ONPEAK_KWH']), axis=1)
        meterValFIN['AVERAGEDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['AVERAGEDEMAND']), axis=1)
        meterValFIN['PEAKDEMAND'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['PEAKDEMAND']), axis=1)
        meterValFIN['BCKST_AVERAGE'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['BCKST_AVERAGE']), axis=1)
        meterValFIN['BCKST_PEAK'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['BCKST_PEAK']), axis=1)
        meterValFIN['BCKST_TOTAL'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['BCKST_TOTAL']), axis=1)
        try:
            meterValFIN  = meterValFIN.rename(columns = {'ACCOUNTID' : 'Account ID', 'STRIP': 'Strip','ANNUAL_KWH' : 'Forecasted\nAnnual kWh', 'OFFPEAK_KWH' : "OffPeak\nkWh",'ONPEAK_KWH' : 'OnPeak\nkWh','LOADFACTOR' : 'Load\nFactor','AVERAGEDEMAND' : 'AVGDemand (KWHs)', 'PEAKDEMAND': 'Forecasted\nPeak kW'})
            titles = ["Strip","Account ID","Forecasted\nAnnual kWh","Load\nFactor","AVGDemand (KWHs)",'OnPeak\nkWh',"OffPeak\nkWh","Forecasted\nPeak kW",'BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']
            meterValFIN = meterValFIN.reindex(columns = titles)
            
        except:
            meterValFIN  = meterValFIN.rename(columns = {'ACCOUNTID' : 'Account ID','STRIP': 'Strip','ANNUAL_KWH' : 'Forecasted\nAnnual kWh', 'OFFPEAK_KWH' : "OffPeak\nkWh",'ONPEAK_KWH' : 'OnPeak\nkWh','AVERAGEDEMAND' : 'AVGDemand (KWHs)', 'PEAKDEMAND': 'Forecasted\nPeak kW'})
            titles = ["Strip","Account ID","Forecasted\nAnnual kWh","AVGDemand (KWHs)",'OnPeak\nkWh',"OffPeak\nkWh","Forecasted\nPeak kW",'BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']
            meterValFIN = meterValFIN.reindex(columns = titles)

        meterValFIN2 = meterValFIN.copy()
        meterValFIN2['Forecasted\nAnnual kWh'] = meterValFIN.apply(lambda x: "{:.2f}".format(x['Forecasted\nAnnual kWh']), axis=1)
        meterValFIN2['Forecasted\nAnnual kWh'] = meterValFIN['Forecasted\nAnnual kWh'].astype(float)
        favDict = pd.Series(meterValFIN2['Forecasted\nAnnual kWh'].values,index=meterValFIN2['Account ID']).to_dict() # DICT
        meterValFIN['Forecasted\nAnnual kWh'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['Forecasted\nAnnual kWh']), axis=1)
        empty = False



        return meterValFIN, meterValFIN2, favDict, empty
    
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
                        -- AND a.LSTIME = mh.LSTIME
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
        
        meterRead = pd.read_sql(sqlQuery, self.conn)

        if meterRead.empty:  
            model = PandasModel(meterRead)
            mrDict = {}
            return model, meterRead
        

        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day

        # Verify this calculation on when to get summer Peaks for the 'latest' years
        startComp = dt.datetime(ny, 9, 15)
        if now < startComp:
            ny -= 1

        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME'])  # Convert the date column to datetimeformat
        # meterRead['STARTREADTIME'] = (meterRead['STARTREADTIME'].datetime.strftime('%m/%d/%Y')) # Convert the date column to only show date w/o seconds
        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME'],format="%m/%d/%Y")  # Convert the date column to only show date w/o seconds
        # meterRead['STARTREADTIME'] = meterRead['STARTREADTIME'].dt.date
        # meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].datetime.strftime('%m/%d/%Y') # Convert the date column to only show date w/o seconds
        meterRead['STOPREADTIME'] = pd.to_datetime(meterRead['STOPREADTIME'],format="%m/%d/%Y")  # Convert the date column to only show date w/o seconds
        # meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].dt.date

        meterRead['DeltaDayCount'] = abs((meterRead['STOPREADTIME'] - meterRead['STARTREADTIME']) / pd.offsets.Day(-1))
        # meterRead['DeltaDayCount'] -= 1
        # meterRead = meterRead.drop_duplicates(subset=['STARTREADTIME'], keep = 'first')
        meterRead['STARTREADTIME'] = (meterRead['STARTREADTIME'].dt.strftime('%m/%d/%Y'))  # Convert the date column to only show date w/o seconds
        meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].dt.strftime('%m/%d/%Y')  # Convert the date column to only show date w/o seconds
        meterReadpiv = pd.pivot_table(meterRead,index=['ACCOUNTID', 'PROFILE_OR_SCALAR', 'STARTREADTIME', 'STOPREADTIME'],values=['PEAKVALUE', 'STOPREADING', 'DeltaDayCount'])

        meterReadpiv.reset_index(drop=False, inplace=True)

        #########################  ------------------------------------------------------------------------   ########################################

        # WE BEGIN OUR METER READS PROCESSING HERE
        accts = pd.DataFrame(columns=['AccountID', 'StopRead', 'DeltaDayCount'])
        summerPeaks = {}
        mrDict = {}
        # self.dayCountdict = {}
        meterReadpiv6 = dict(tuple(meterReadpiv.groupby('ACCOUNTID')))
        for key in meterReadpiv6.keys():
            meterReads = meterReadpiv6[key]
            # meterReads.reset_index(drop=False,inplace=True)
            meterReads['STARTREADTIME'] = pd.to_datetime(meterReads['STARTREADTIME'], format="%m/%d/%Y")
            meterReads.sort_values(by='STARTREADTIME', inplace=True)
            meterReads.set_index('STARTREADTIME', inplace=True)
            meterReads = meterReads.loc[~meterReads.index.duplicated(keep='first')]
            meterReads = meterReads.sort_index().last('60M')
            tot = meterReads['STOPREADING'].sum()
            mrDict[key] = tot
            totDayCount = meterReads['DeltaDayCount'].sum()
            # self.dayCountdict[key] = totDayCount
            meterReads.reset_index(drop=False, inplace=True)
            meterReads = meterReads[['ACCOUNTID', 'PROFILE_OR_SCALAR', 'STARTREADTIME', 'STOPREADTIME', 'STOPREADING', 'PEAKVALUE','DeltaDayCount']]
            meterReads['STARTREADTIME'] = (meterReads['STARTREADTIME'].dt.strftime('%m/%d/%Y'))

            jun2AugPeaks = meterReads[meterReads.STARTREADTIME.str.startswith(('06/', '07/', '08/'))]  # WE GET THE SUMMER PEAK VALUES FOR JUN THROUGH AUG MONTHS
            summerPeak = jun2AugPeaks.PEAKVALUE.max()  # WE OBTAIN THE PEAK BY GETTING THE MAX OF THOSE MONTHS
            summerPeaks[key] = summerPeak

            meterReads['PROFILE_OR_SCALAR'] = self.mrDict2.get(key)  # We obtain the profile codes for each meter from the previously made dictionary
            meterReads = meterReads.append(meterReads.sum(numeric_only=True), ignore_index=True).replace(np.nan, '')
            meterReads.iloc[-1, meterReads.columns.get_loc('STOPREADTIME')] = 'Total'

            # accts[key] = tot
            accts = accts.append(pd.Series([key, tot, totDayCount], index=accts.columns), ignore_index=True)
            meterReads = meterReads.rename(columns={'ACCOUNTID': 'Account ID', 'PROFILE_OR_SCALAR': 'Profile\nCode',
                                                    'STARTREADTIME': 'Start\nRead\nTime',
                                                    'STOPREADTIME': 'Stop\nRead\nTime', 'PEAKVALUE': 'Peak\nValue',
                                                    'DeltaDayCount': 'Delta\nDay\nCount', 'STOPREADING':'Stop\nRead\nValue'})
            meterReads['Peak\nValue'].replace('', np.nan, inplace=True)
            meterReadpiv6[key] = meterReads

        accts.sort_values(by='StopRead', ascending=False, inplace=True)
        accts2 = accts['AccountID'].to_list()
        # dayCountdict = pd.Series(accts['DeltaDayCount'].values,index=accts['AccountID']).to_dict() # DAYCOUNT DICT

        from collections import OrderedDict
        self.orderedMR = OrderedDict()
        for k in accts2:
            self.orderedMR[k] = meterReadpiv6[k]

        meterReadpiv5 = pd.concat(self.orderedMR.values(), ignore_index=False)
        meterReadpiv5[['Account ID']] = meterReadpiv5[['Account ID']].where(meterReadpiv5[['Account ID']].apply(lambda x: x != x.shift()), '')
        meterReadpiv5.loc[meterReadpiv5['Account ID'] == '', 'Profile\nCode'] = ''

        meterReadpiv5['Peak\nValue'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Peak\nValue']), axis=1)
        meterReadpiv5['Delta\nDay\nCount'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Delta\nDay\nCount']),axis=1)
        meterReadpiv5['Stop\nRead\nValue'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Stop\nRead\nValue']),axis=1)

        model = PandasModel(meterReadpiv5)

        listDict = {}
        i = 0
        for col in meterReadpiv5.columns:
            listDict.update({col: i})
            #            print(listDict)
            i += 1
        self.meterReadPRCols.addItem(listDict)
        
        return model, meterReadpiv5
    
    #ONLY THE LAST 12
    def meterRead(self, prNum, revNum, months):
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
                        -- AND a.LSTIME = mh.LSTIME
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

        meterRead = pd.read_sql(sqlQuery, self.conn)

        if meterRead.empty:
            model = PandasModel(meterRead)
            mrDict = {}
            sPeakDict = {}
            self.dayCountdict = {}
            return model, mrDict, meterRead, sPeakDict, mrDict



        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day

        # Verify this calculation on when to get summer Peaks for the 'latest' years
        startComp = dt.datetime(ny, 9, 15)
        if now < startComp:
            ny -= 1

        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME'])  # Convert the date column to datetimeformat
        # meterRead['STARTREADTIME'] = (meterRead['STARTREADTIME'].datetime.strftime('%m/%d/%Y')) # Convert the date column to only show date w/o seconds
        meterRead['STARTREADTIME'] = pd.to_datetime(meterRead['STARTREADTIME'],format="%m/%d/%Y")  # Convert the date column to only show date w/o seconds
        # meterRead['STARTREADTIME'] = meterRead['STARTREADTIME'].dt.date
        # meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].datetime.strftime('%m/%d/%Y') # Convert the date column to only show date w/o seconds
        meterRead['STOPREADTIME'] = pd.to_datetime(meterRead['STOPREADTIME'],format="%m/%d/%Y")  # Convert the date column to only show date w/o seconds
        # meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].dt.date

        meterRead['DeltaDayCount'] = abs((meterRead['STOPREADTIME'] - meterRead['STARTREADTIME']) / pd.offsets.Day(-1))
        # meterRead['DeltaDayCount'] -= 1
        # meterRead = meterRead.drop_duplicates(subset=['STARTREADTIME'], keep = 'first')
        meterRead['STARTREADTIME'] = (meterRead['STARTREADTIME'].dt.strftime('%m/%d/%Y'))  # Convert the date column to only show date w/o seconds
        meterRead['STOPREADTIME'] = meterRead['STOPREADTIME'].dt.strftime('%m/%d/%Y')  # Convert the date column to only show date w/o seconds
        meterReadpiv = pd.pivot_table(meterRead,index=['ACCOUNTID', 'PROFILE_OR_SCALAR', 'STARTREADTIME', 'STOPREADTIME'],values=['PEAKVALUE', 'STOPREADING', 'DeltaDayCount'])

        meterReadpiv.reset_index(drop=False, inplace=True)

        #########################  ------------------------------------------------------------------------   ########################################

        # WE BEGIN OUR METER READS PROCESSING HERE
        accts = pd.DataFrame(columns=['AccountID', 'StopRead', 'DeltaDayCount'])
        summerPeaks = {}
        mrDict = {}
        self.dayCountdict = {}
        meterReadpiv6 = dict(tuple(meterReadpiv.groupby('ACCOUNTID')))
        for key in meterReadpiv6.keys():
            meterReads = meterReadpiv6[key]
            # meterReads.reset_index(drop=False,inplace=True)
            meterReads['STARTREADTIME'] = pd.to_datetime(meterReads['STARTREADTIME'], format="%m/%d/%Y")
            meterReads.sort_values(by='STARTREADTIME', inplace=True)
            meterReads.set_index('STARTREADTIME', inplace=True)
            meterReads = meterReads.loc[~meterReads.index.duplicated(keep='first')]
            meterReads = meterReads.sort_index().last(str(months) + 'M')
            tot = meterReads['STOPREADING'].sum()
            mrDict[key] = tot
            totDayCount = meterReads['DeltaDayCount'].sum()
            self.dayCountdict[key] = totDayCount
            meterReads.reset_index(drop=False, inplace=True)
            meterReads = meterReads[['ACCOUNTID', 'PROFILE_OR_SCALAR', 'STARTREADTIME', 'STOPREADTIME', 'STOPREADING', 'PEAKVALUE','DeltaDayCount']]
            meterReads['STARTREADTIME'] = (meterReads['STARTREADTIME'].dt.strftime('%m/%d/%Y'))

            jun2AugPeaks = meterReads[meterReads.STARTREADTIME.str.startswith(('06/', '07/', '08/'))]  # WE GET THE SUMMER PEAK VALUES FOR JUN THROUGH AUG MONTHS
            summerPeak = jun2AugPeaks.PEAKVALUE.max()  # WE OBTAIN THE PEAK BY GETTING THE MAX OF THOSE MONTHS
            summerPeaks[key] = summerPeak

            meterReads['PROFILE_OR_SCALAR'] = self.mrDict2.get(key)  # We obtain the profile codes for each meter from the previously made dictionary
            meterReads = meterReads.append(meterReads.sum(numeric_only=True), ignore_index=True).replace(np.nan, '')
            meterReads.iloc[-1, meterReads.columns.get_loc('STOPREADTIME')] = 'Total'

            # accts[key] = tot
            accts = accts.append(pd.Series([key, tot, totDayCount], index=accts.columns), ignore_index=True)
            meterReads = meterReads.rename(columns={'ACCOUNTID': 'Account ID', 'PROFILE_OR_SCALAR': 'Profile\nCode',
                                                    'STARTREADTIME': 'Start\nRead\nTime',
                                                    'STOPREADTIME': 'Stop\nRead\nTime', 'PEAKVALUE': 'Peak\nValue',
                                                    'DeltaDayCount': 'Delta\nDay\nCount', 'STOPREADING':'Stop\nRead\nValue'})
            meterReads['Peak\nValue'].replace('', np.nan, inplace=True)
            meterReadpiv6[key] = meterReads

        accts.sort_values(by='StopRead', ascending=False, inplace=True)
        accts2 = accts['AccountID'].to_list()
        # dayCountdict = pd.Series(accts['DeltaDayCount'].values,index=accts['AccountID']).to_dict() # DAYCOUNT DICT

        from collections import OrderedDict
        orderedMR = OrderedDict()
        for k in accts2:
            orderedMR[k] = meterReadpiv6[k]

        meterReadpiv5 = pd.concat(orderedMR.values(), ignore_index=False)
        meterReadpiv5[['Account ID']] = meterReadpiv5[['Account ID']].where(meterReadpiv5[['Account ID']].apply(lambda x: x != x.shift()), '')
        meterReadpiv5.loc[meterReadpiv5['Account ID'] == '', 'Profile\nCode'] = ''

        meterReadpiv5['Peak\nValue'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Peak\nValue']), axis=1)
        meterReadpiv5['Delta\nDay\nCount'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Delta\nDay\nCount']),axis=1)
        meterReadpiv5['Stop\nRead\nValue'] = meterReadpiv5.apply(lambda x: '{:,.0f}'.format(x['Stop\nRead\nValue']),axis=1)

        model = PandasModel(meterReadpiv5)

        listDict = {}
        i = 0
        for col in meterReadpiv5.columns:
            listDict.update({col: i})
            #            print(listDict)
            i += 1
        self.meterReadPRCols.addItem(listDict)

        # meterReadpiv5 is the dataframe concatenated
        # meterReadpiv6 is the dictionary of accounts
        # mrDict is dictionary of account and sums per account
        # summerPeaks is dict of accounts and summerPeaks per account
        # model is the Pandas model for meterReadpiv5


        return model, mrDict, meterReadpiv5, summerPeaks, meterReadpiv6
    
    def setEmptyTables(self,prNum, revNum):
#        _translate = QtCore.QCoreApplication.translate
        emptyCaptagsYOY = pd.DataFrame(columns = ['TAGS YOY'])
        emptyTranstagsYOY = pd.DataFrame(columns = ['TRANS\nTAGS YOY'])
        emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
        emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'YOY\nDelta'])
        emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                           'TAG_TYPE','TAG','Strip'])
        emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                                'ONPEAK_KWH','PEAKDEMAND'])
        emptyMeterReads = pd.DataFrame(columns = ['TIMESTAMP', 'ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
        emptyDetailedView = pd.DataFrame(columns=['Account ID', 'Start\nDate', 'End\nDate', 'Start\nYear', 'Summer\nPeak kW', 'Forecasted\nPeak kW','Capacity Tag'])


#        self.label_3.setText(_translate("MainWindow", "Current PR: "))
        self.capTags.setModel(PandasModel(emptyCapTags))
        self.capTagsYOY.setModel(PandasModel(emptyCaptagsYOY))
        self.transTagsYOY.setModel(PandasModel(emptyTranstagsYOY))
        self.capacity.setModel(PandasModel(emptyCap))
        self.detailYOY.setModel(PandasModel(emptydetailYOY))
        self.meterReadPR.setModel(PandasModel(emptyMeterReads))
        self.meterValuePR.setModel(PandasModel(emptyMeterVal))
        self.acctDetailTableView.setModel(PandasModel(emptyDetailedView))
        
        self.ax.cla()
        self.ax.figure.clear()
        
    def getTimeStamp(self,prNum,revNum,channel):
        sqlQuery = ("""
WITH volumes AS (
    SELECT
        recorder AS MeterID,
        channel AS "Channel",
        to_char(min(starttime),'MM/DD/YYYY') as Start_Time, 
        to_char(max(stoptime),'MM/DD/YYYY') as Stop_Time, 
        to_char(max(lstime),'MM/DD/YYYY') as "Last\nUpdated"
    FROM
        LSCHANNELCUTHEADER 
    WHERE
        channel = '{channel}'   
    GROUP BY
        recorder, channel 
),
accountsDF AS (
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
    --INNER JOIN volumes vm on accountsDF.account = vm.MeterID
        
)
SELECT
    V.MeterID,
    V."Channel",
    V.Start_Time,
    V.Stop_Time,
    V."Last\nUpdated"
FROM 
    volumes V
INNER JOIN accountsDF
ON accountsDF.Accountid = V.MeterID         
            
            
        """).format(prNum=prNum, revNum=revNum,channel=channel)

        data = pd.read_sql(sqlQuery, self.conn)
        if channel == 1:
            self.AcctTimestampCh1 = pd.Series(data['Last\nUpdated'].values, index=data['METERID']).to_dict()
        elif channel == 3:
            self.AcctTimestampCh3 = pd.Series(data['Last\nUpdated'].values, index=data['METERID']).to_dict()


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
        
        # Here we check if the user has internet connection, otherwise user will be alerted
        internetCon = is_connected()
        if internetCon == False:
            self.msgBox1 = msgBox()
            self.msgBox1.text.setText(("NO INTERNET, Check your Internet Connection!"))
            self.msgBox1.show()
            return;
        # AzureDF512682!
        # Wv5945672663!!
        try:
#         CONNECTION TO THE ORACLIENT_SQL_SERVER
            pswrd = 'Wv5945672663!!'
#            dsn_tns = cx_Oracle.makedsn('172.25.152.125', '1700', service_name='tppe.mytna.com')
            self.conn = cx_Oracle.connect('wv5945', pswrd, "tppe.mytna.com") # WORKING FOR ME
#            dsn_tns = cx_Oracle.makedsn('10.163.4.45', '1700', service_name='tppe.mytna.com')
#            self.conn = cx_Oracle.connect(user='wv5945', password='Wv5945672663!!', dsn=dsn_tns)
#            self.cnn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};DBQ=tppe;Uid=azureuser;Pwd=AzureDF512682!')
        except:
            
            try:
                self.conn = pyodbc.connect('Driver={Oracle in OraClient11g_home1};DBQ=tppe;Uid=wv5945;Pwd=Wv5945672663!!')
            except:
                self.msgBox1 = msgBox()
                self.msgBox1.text.setText(("VERIFY Your Connection to TPPE Server!"))
                self.msgBox1.show()
                return;
        
        _translate = QtCore.QCoreApplication.translate
        prNum = self.lineEdit.text()
        revNum = self.lineEdit_2.text()
        self.setEmptyTables(prNum, revNum)
        self.revNum = self.lineEdit_2.text()
        self.prNumStr = self.lineEdit.text() # Gets text from input line
        
        self.prNumStr = prNum.strip() # Strips spaces
        self.revNum = self.revNum.strip()
        
        offerNum = 'OFFER_' + self.prNumStr + '%' 
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText(offerNum, mode=cb.Clipboard)
        # self.timeStampCheckBox3.setCheckState(Qt.Unchecked)

        
        #################################################
               # CLEARS LIST WITH FILTERS PER TABLE #
        self.capTagsCols.clear()
        self.capTagsYOYCols.clear()
        self.transTagsYOYCols.clear()
        self.detailYOYCols.clear()
        self.capacityCols.clear()
        self.meterReadPRCols.clear()
        self.meterValuePRCols.clear()
        #################################################
        
        prNum = prNum.strip()
        revNum = revNum.strip()
        
        if(self.ercotCheckBox.checkState() == Qt.Checked and prNum != "" and revNum != ""):
            font = QtGui.QFont()
            font.setBold(True)
            font.setWeight(75)
#            print("ERCOT PR!!")
            self.label_3.setText(_translate("MainWindow", "Current PR:     " + prNum + "     Rev.     " + revNum))
            
            data = self.ercotData(prNum, revNum)
            ifErcot = data['MARKETCODE'].str.contains('ERCOT').any()
            if(ifErcot == False):
#                print("NOT ERCOT!")
                return
            try:
                now = dt.datetime.now()
                ny = now.year
                meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum, revNum, ny)
            except:
                try:
                    meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum, revNum, ny - 1)
                except:
                    # try:
                    #     meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum, revNum, ny-1)
                    # except:
                    self.msgBox1 = msgBox()
                    self.msgBox1.text.setText(
                        ("Error on FAV Table Step 1!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                    self.msgBox1.show()
            # self.mrCheckBox.setCheckState(Qt.Checked)

            page = self.detailTab.findChildren(QWidget,'detailTab2') # 'detailTab2' is the name of the tab in which the meter reads and FAV are
            index = self.detailTab.indexOf(page[0])
#            print('Index of Detail = ', index)
            self.detailTab.setCurrentIndex(index)
            self.meterReadM, mrDict, self.meterReadDF, sPeakDict, dictMR = self.meterRead(prNum, revNum, 12) # this is the model that only has last 12 months
            self.meterReadFullM, self.meterReadDFfull = self.meterReadfull(prNum,revNum) # this is the model that has all available data
            meterValueM, meterValueDF = self.calcVar(meterValueDF, meterValueDF2, favDict, mrDict, sPeakDict)

            meterValueDF = meterValueDF.set_index('Account ID').join(pd.Series(data.set_index('ACCOUNTID')['PROFILECODE']))# POSSIBLY WRONG CODE
            print(meterValueDF)
            meterValueDF = meterValueDF.join(pd.Series(data.set_index('ACCOUNTID')['LOSS_CLASS'])) # POSSIBLY WRONG CODE
            meterValueDF.reset_index(inplace=True,drop=False)
            meterValueDF = meterValueDF.rename(columns = {'index':'Account ID','PROFILECODE':'Profile\nCode','LOSS_CLASS':'Loss Class'})
            titles = ['Strip','Account ID','SCA\nTotal','Forecasted\nAnnual kWh','Forecasted\nAnnual to\nSCA Var','Day\nCount','Summer\nPeak kW','Load\nFactor','Forecasted\nPeak kW','Profile\nCode','Loss Class','OnPeak\nkWh','OffPeak\nkWh']
            meterValueDF = meterValueDF.reindex(columns = titles)
            i = 0
            self.meterValuePRCols.clear()
            listDict = {}
            for col in meterValueDF.columns:
                listDict.update({col: i})
                #            print(listDict)
                i += 1
            self.meterValuePRCols.addFAV(listDict)
            # print(meterValueDF)
            meterValueDF.drop_duplicates(inplace = True)
            meterValueDF['Forecasted\nAnnual kWh'] = meterValueDF['Forecasted\nAnnual kWh'].str.replace(',','').astype(float)
            meterValueDF.sort_values(by=['Forecasted\nAnnual kWh'], inplace = True, ascending = False)
            meterValueDF['Forecasted\nAnnual kWh'] = meterValueDF.apply(lambda x: "{:.2f}".format(x['Forecasted\nAnnual kWh']), axis=1)
            meterValueM = PandasModel(meterValueDF)
            if(not empty):
                #------------------------------------------------------------------------------------------------------------------
                self.meterValuePR.setModel(meterValueM)
                self.meterValuePR.setAlternatingRowColors(True)
                self.meterValuePR.setStyleSheet("alternate-background-color:#505F69;background-color: #061e26;selection-color #ffffff")
                col = meterValueDF.columns.get_loc("Strip")
                self.meterValuePR.setColumnWidth(col,70)
                col = meterValueDF.columns.get_loc("Account ID")
                self.meterValuePR.setColumnWidth(col,185)
                col = meterValueDF.columns.get_loc("Forecasted\nAnnual kWh")
                self.meterValuePR.setColumnWidth(col,90)
                col = meterValueDF.columns.get_loc("Day\nCount")
                self.meterValuePR.setColumnWidth(col,43)
                col = meterValueDF.columns.get_loc("Load\nFactor")
                self.meterValuePR.setColumnWidth(col,45)
                col = meterValueDF.columns.get_loc("Summer\nPeak kW")
                self.meterValuePR.setColumnWidth(col,60)
                col = meterValueDF.columns.get_loc("Forecasted\nPeak kW")
                self.meterValuePR.setColumnWidth(col,90)
                col = meterValueDF.columns.get_loc('OnPeak\nkWh')
                self.meterValuePR.setColumnWidth(col,76)
                col = meterValueDF.columns.get_loc("OffPeak\nkWh")
                self.meterValuePR.setColumnWidth(col,76)
#                   self.meterValuePR.setColumnWidth(7,90)
                self.meterValuePR.horizontalHeader().setFont(font)
                self.meterValuePR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterValuePR))
                self.meterValuePRCols.HideStart() # THIS IS USED TO HIDE SPECIFIED COLUMNS
                self.meterReadPR.setModel(self.meterReadM)
                self.meterReadPR.setAlternatingRowColors(True)
            try:
                col = self.meterReadDF.columns.get_loc("Account ID")
                self.meterReadPR.setColumnWidth(col,185)
                col = self.meterReadDF.columns.get_loc("Profile\nCode")
                self.meterReadPR.setColumnWidth(col,70)
                col = self.meterReadDF.columns.get_loc("Start\nRead\nTime")
                self.meterReadPR.setColumnWidth(col,75)
                col = self.meterReadDF.columns.get_loc("Stop\nRead\nTime")
                self.meterReadPR.setColumnWidth(col,75)
                col = self.meterReadDF.columns.get_loc("Stop\nRead\nValue")
                self.meterReadPR.setColumnWidth(col,90)
                col = self.meterReadDF.columns.get_loc("Peak\nValue")
                self.meterReadPR.setColumnWidth(col,65)
                col = self.meterReadDF.columns.get_loc("Delta\nDay\nCount")
                self.meterReadPR.setColumnWidth(col,58)
                self.meterReadPR.horizontalHeader().setFont(font)
            except:
                pass
            self.meterReadPR.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color #ffffff")
            self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))
            self.ax.clear()
            self.ax.figure.clear()
        
        elif(prNum == "" or revNum == ""):
            emptyCaptagsYOY = pd.DataFrame(columns = ['TAGS YOY'])
            emptyTranstagsYOY = pd.DataFrame(columns = ['TRANS\nTAGS YOY'])
            emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
            emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'YOY\nDelta'])
            emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                               'TAG_TYPE','TAG','Strip'])
            emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                                   'ONPEAK_KWH','PEAKDEMAND'])
            emptyMeterReads = pd.DataFrame(columns = ['TIMESTAMP', 'ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
            self.meterReadM = PandasModel(emptyMeterReads)
            self.meterReadFullM = PandasModel(emptyMeterReads)
            self.label_3.setText(_translate("MainWindow", "Current PR: "))
            self.capTags.setModel(PandasModel(emptyCapTags))
            self.capTagsYOY.setModel(PandasModel(emptyCaptagsYOY))
            self.transTagsYOY.setModel(PandasModel(emptyTranstagsYOY))
            self.capacity.setModel(PandasModel(emptyCap))
            self.detailYOY.setModel(PandasModel(emptydetailYOY))
            self.meterReadPR.setModel(PandasModel(emptyMeterReads))
            self.meterValuePR.setModel(PandasModel(emptyMeterVal))
            self.ax.clear()
            self.ax.figure.clear()
            
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
            # here we call to get the timestamp of latest forecast
            self.getTimeStamp(prNum, revNum, 1) # we get the channel 1 data
            self.getTimeStamp(prNum, revNum, 3) # we get the channel 3 data

            if dataMrounded.empty or dataM.empty:
                # DO NOT DO ANYTHING JUST SET EVERYTHING EMPTY
                emptyCaptagsYOY = pd.DataFrame(columns = ['TAGS YOY'])
                emptyTranstagsYOY = pd.DataFrame(columns = ['TRANS\nTAGS YOY'])
                emptyCapTags = pd.DataFrame(columns = ['Planning Year', 'Capacity Tag','Transmission','Accounts'])
                emptydetailYOY = pd.DataFrame(columns = ['ACCOUNTID', 'Year Strip','Year Strip', 'YOY\nDelta'])
                emptyCap = pd.DataFrame(columns = ['CUSTOMERNAME', 'CUSTOMERID','LDC_ACCOUNT','ACCOUNTID','UIDACCOUNT','MARKETCODE','CONTRACTID','REVISION','PROFILECODE','PROFILENAME','LOSS_CLASS','STARTTIME','STOPTIME',
                                                   'TAG_TYPE','TAG','Strip'])
                emptyMeterVal = pd.DataFrame(columns = ['Strip', 'ACCOUNTID','ANNUAL_KWH','AVERAGEDEMAND','LOADFACTOR','OFFPEAK_KWH',
                                                        'ONPEAK_KWH','PEAKDEMAND'])
                emptyMeterReads = pd.DataFrame(columns = ['TIMESTAMP', 'ACCOUNTID','PROFILE_OR_SCALAR','STARTREADTIME','STOPREADING'])
                self.label_3.setText(_translate("MainWindow", "Current PR: "))
                self.capTags.setModel(PandasModel(emptyCapTags))
                self.capTagsYOY.setModel(PandasModel(emptyCaptagsYOY))
                self.transTagsYOY.setModel(PandasModel(emptyTranstagsYOY))
                self.capacity.setModel(PandasModel(emptyCap))
                self.detailYOY.setModel(PandasModel(emptydetailYOY))
                self.meterReadPR.setModel(PandasModel(emptyMeterReads))
                self.meterValuePR.setModel(PandasModel(emptyMeterVal))
                self.ax.clear()
                self.ax.figure.clear()
                self.label_3.setText(_translate("MainWindow", "Current PR:     " + "CHECK & VERIFY" + "     Rev.     " + "CHECK & VERIFY#"))
            else:
                #------------------------------------------------------------------------------------------------------------------
                # DO EVERYTHING BELOW
                self.mrDict2 = pd.Series(dataM['PROFILECODE'].values,index=dataM['ACCOUNTID']).to_dict()

                dataMpd = PandasModel(dataMrounded)
                self.capacity.setModel(dataMpd)
                self.capacity.setAlternatingRowColors(True)
                self.capacity.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-background-color: #4c74f4;selection-color #ffffff")
                self.capacity.horizontalHeader().setFont(font)
                self.capacity.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capacity))
                self.capacityCols.HideStart()

                #------------------------------------------------------------------------------------------------------------------
                try:
                    # THIS IS IN CHARGE OF MAKING CAPTAGS FROM OVERALL DATA
                    capTagsM = self.makeCaptags(dataM)
                except:
                    # IFERROR/EXCEPTION ON MAKING CAPTAGS, SET EMPTY CAPTAG TABLE AND POP MSSG
                    self.msgBox1 = msgBox()
                    self.msgBox1.text.setText(("Error on Captags Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                    self.msgBox1.show()
                    return
                else:
                    self.capTags.setModel(capTagsM)
                    self.capTags.setAlternatingRowColors(True)
                    self.capTags.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-background-color: #21b334;selection-color #ffffff")
                    self.capTags.horizontalHeader().setFont(font)
                    self.capTags.setColumnWidth(0, 135);
                    self.capTags.setColumnWidth(1, 80)
                    self.capTags.setColumnWidth(2, 90)
                    self.capTags.setColumnWidth(3, 70)
                    self.capTags.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capTags))

                    try:
                        #                    self.figure.clear()
                        self.graphLayout.removeWidget(self.canvas)
                        self.canvas.close()
                        self.graphLayout.removeWidget(self.toolbar)
                        self.toolbar.close()
                    except:
                        #                    print("ERROR ON CLOSE CANVAS OR TOOLBAR")
                        pass
                    self.canvas = FigureCanvas(self.figure)
                    self.toolbar = NavigationToolbar(self.canvas,self,coordinates=True)
                    self.graphLayout.addWidget(self.toolbar)

                    self.graphLayout.addWidget(self.canvas)
                    self.canvas.draw()

                #                self.addToolBar(self.toolbar)
                #                self.toolItems = self.toolbar.toolitems
                #------------------------------------------------------------------------------------------------------------------


                #------------------------------------------------------------------------------------------------------------------
                # WE TRY TO MAKE THE FIRST DETAIL YOY TABLE, IF IT WORKS, WE COPY IT AND PERFORM THE NEXT OPERATIONS
                try:
                    detailYOYDF,IFNYISO = self.detailYOYfunc(dataM)
                except:

                    self.msgBox1 = msgBox()
                    self.msgBox1.text.setText(("Error on Account Details Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                    self.msgBox1.show()
                    return
                #-----------------------------------------------------------------------------------------------------------------
                # else:
                detailYOYDF2 = detailYOYDF.copy()
                IFPJM = detailYOYDF['MARKETCODE'].str.contains('PJM').any()
                IFMISO = detailYOYDF['MARKETCODE'].str.contains('MISO').any()

                # ADDED VALIDATION FOR MISO?
                if IFPJM == True or IFMISO == True:
                    self.IFPJM = True
                    IFPJM = True
                else:
                    self.IFPJM = False
                    IFPJM = False

                if(IFPJM == False):
                    detailYOYDF2 = pd.DataFrame(columns = ['TRANS\nTAGS YOY'])
                    self.transTagsYOY.setModel(PandasModel(detailYOYDF2))
                    listDict = {}
                    i = 0
                    for col in detailYOYDF2.columns:
                        listDict.update({col:i})
                        #                    print(listDict)
                        i+=1
                    self.transTagsYOYCols.addItem(listDict)


                # CATCH ERROR ON FAV TABLE
                try:
                    now = dt.datetime.now()
                    ny = now.year
                    meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum,revNum, ny)
                except:
                    try:
                        meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum, revNum, ny-1)
                    except:
                        # try:
                        #     meterValueDF, meterValueDF2, favDict, empty = self.meterValue(prNum, revNum, ny-1)
                        # except:
                        self.msgBox1 = msgBox()
                        self.msgBox1.text.setText(("Error on FAV Table Step 1!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                        self.msgBox1.show()

                print('TEST!!!')

                # CATCH ERROR ON METER READS TABLE
                # try:

                self.meterReadM, mrDict, self.meterReadDF, sPeakDict, dictMR = self.meterRead(prNum, revNum,12) # this is the model that only has last 12 months
                print('TEST AFTER METER READS!!!')
                self.meterReadFullM, self.meterReadDFfull = self.meterReadfull(prNum,revNum) # this is the model that has all available data
                self.comboBoxMRHists.setCurrentText("12 Months") # change combo box back to original default option
                self.displayTagsComboBox.setCurrentText("Current PY CapTag") # change combo box back to original default option
                # except:
                #                 #
                #                 #     self.msgBox1 = msgBox()
                #                 #     self.msgBox1.text.setText(("Error on Meter Reads Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                #                 #     self.msgBox1.show()
                #                 #     return



                # If the PR is not PJM, set the table TransTags YOY to an empty dataframe model

                if(not empty):
                    try:
                        meterValueM, meterValueDF = self.calcVar(meterValueDF, meterValueDF2, favDict, mrDict, sPeakDict)
                    except:
                        self.msgBox1 = msgBox()
                        self.msgBox1.text.setText(("Error on FAV Table Step 2!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                        self.msgBox1.show()
                        return
                    # try:
                    detailYOYM, detailYOYDF = self.detailYOYLF(detailYOYDF,meterValueDF)
                    self.detailYOYDF = detailYOYDF.copy()
                    # except:
                    #     self.msgBox1 = msgBox()
                    #     self.msgBox1.text.setText(("Error on Account Details Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                    #     self.msgBox1.show()
                    #     return

                    listDict = {}
                    capTagCols = [] # list to store indexes of captag cols
                    i = 0
                    for col in detailYOYDF.columns:

                        if 'CapTag' in col and 'PY' in col:
                            idx = detailYOYDF.columns.get_loc(col)
                            capTagCols.append(idx)

                        listDict.update({col:i})
                        #                    print(listDict)
                        i+=1

                    self.detailYOYCols.addDetailYOY(listDict,IFNYISO, False,IFPJM)
                    self.detailYOY.setModel(detailYOYM)
                    self.detailYOY.setAlternatingRowColors(True)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.detailYOY.setColumnWidth(col,200)
                    #                    col = detailYOYDF.columns.get_loc("YOY\nDelta")
                    #                    self.detailYOY.setColumnWidth(col,70)
                    col = detailYOYDF.columns.get_loc("Summer\nPeak kW")
                    self.detailYOY.setColumnWidth(col,70)
                    col = detailYOYDF.columns.get_loc("Summer\nPeak kW to\nCapTag Var")
                    self.detailYOY.setColumnWidth(col,75)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW")
                    self.detailYOY.setColumnWidth(col,72)
                    col = detailYOYDF.columns.get_loc("CapTag\nFactor")
                    self.detailYOY.setColumnWidth(col,50)
                    col = detailYOYDF.columns.get_loc("Forecasted\nAnnual to\nSCA Var")
                    self.detailYOY.setColumnWidth(col,70)
                    # for idx in range(len(capTagCols)):
                    #     self.detailYOY.setColumnWidth(idx, 65)
                    if(IFPJM):
                        col = detailYOYDF.columns.get_loc(self.curStrip)
                        self.detailYOY.setColumnWidth(col,70)
                        col = detailYOYDF.columns.get_loc('TransTag\nto Peak\nkW Var')
                        self.detailYOY.setColumnWidth(col,65)
                    col = detailYOYDF.columns.get_loc("Percent\nAlloc")
                    self.detailYOY.setColumnWidth(col,47)
                    col = detailYOYDF.columns.get_loc("Day\nCount")
                    self.detailYOY.setColumnWidth(col,43)
                    col = detailYOYDF.columns.get_loc("Load\nFactor")
                    self.detailYOY.setColumnWidth(col,50)
                    col = detailYOYDF.columns.get_loc("Forecasted\nAnnual kWh")
                    self.detailYOY.setColumnWidth(col,95)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW to\n CapTag Var")
                    self.detailYOY.setColumnWidth(col,75)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW")
                    self.detailYOY.setColumnWidth(col,100)
                    col = detailYOYDF.columns.get_loc("Loss Class")
                    self.detailYOY.setColumnWidth(col,130)

                    detailYOYM2 = PandasModel(detailYOYDF,second = True)



                    self.detailYOY.horizontalHeader().setFont(font)
                    self.detailYOY.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color: #1b83a7;selection-color #ffffff")
                    self.detailYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.detailYOY))
                    self.detailYOYCols.HideStart()

                    self.capTagsYOYCols.addDetailYOY(listDict,IFNYISO,True,IFPJM)
                    self.capTagsYOY.setModel(detailYOYM2)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.capTagsYOY.setColumnWidth(col,200)
                    self.capTagsYOY.horizontalHeader().setFont(font)
                    self.capTagsYOY.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color: #1b83a7;selection-color #ffffff")
                    self.capTagsYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capTagsYOY))
                    self.capTagsYOYCols.HideStart()

                    if(IFPJM == True):
                        detailYOYDF2 = detailYOYDF2.rename(columns = {'ACCOUNTID':'Account ID'})
                        favDictANN = pd.Series(meterValueDF['Forecasted\nAnnual kWh'].values,index=meterValueDF['Account ID']).to_dict()
                        detailYOYDF2['Forecasted\nAnnual kWh'] = ""
                        refDF = pd.Series(detailYOYDF2.index.values,index=detailYOYDF2['Account ID']).to_dict()
                        refANN = {}
                        for key,value in refDF.items():
                            valANN = favDictANN.get(key)
                            refANN[value] = valANN
                        for i in range(len(refDF)):
                            keyANN = list(refANN)[i]
                            valueANN = refANN.get(keyANN)
                            detailYOYDF2.at[keyANN,'Forecasted\nAnnual kWh'] = valueANN
                        detailYOYDF2['Forecasted\nAnnual kWh'] = detailYOYDF2['Forecasted\nAnnual kWh'].str.replace(',','').astype(float)
                        detailYOYDF2 = detailYOYDF2.sort_values(by = ['Forecasted\nAnnual kWh'],ascending = False)
                        detailYOYDF2['Forecasted\nAnnual kWh'] = detailYOYDF2.apply(lambda x: '{:,.2f}'.format(x['Forecasted\nAnnual kWh']), axis=1)


                    detailYOYM3= PandasModel(detailYOYDF2,second = True)
                    listDict2 = {}
                    i = 0
                    for col in detailYOYDF2.columns:
                        listDict2.update({col:i})
                        i+=1

                    self.transTagsYOYCols.addDetailYOY(listDict2,IFNYISO,False,IFPJM, transTable = True)
                    self.transTagsYOY.setModel(detailYOYM3)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.transTagsYOY.setColumnWidth(col,200)
                    self.transTagsYOY.horizontalHeader().setFont(font)
                    self.transTagsYOY.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color: #1b83a7;selection-color #ffffff")
                    self.transTagsYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.transTagsYOY))
                    self.transTagsYOYCols.HideStart()


                else:
                    # try:
                    meterValueM, meterValueDF = self.calcVar(meterValueDF, meterValueDF2, favDict, mrDict, sPeakDict)
                    # except:
                    #     self.msgBox1 = msgBox()
                    #     self.msgBox1.text.setText(("Error on Forecasted Annual Values Table!\nPlease Contact Jose Alvarez with\nPR and Rev# about this issue."))
                    #     self.msgBox1.show()
                    #     return
                    #                    try:
                    detailYOYM, detailYOYDF = self.detailYOYLF(detailYOYDF, meterValueDF)

                    now = dt.datetime.now()
                    ny = now.year
                    nm = now.month
                    nd = now.day
                    IFNYISO = False
                    now = dt.datetime(int(ny),int(nm),int(nd))
                    #                    PY2 = str(now.year-2)[-2:]
                    #                    PY1 = str(now.year-1)[-2:]
                    NY =  str(now.year)[-2:]
                    #                    NY1 = str(now.year+1)[-2:]
                    listDict2 = {}
                    i = 0
                    for col in detailYOYDF2.columns:
                        listDict2.update({col:i})
                        #                    print(listDict)
                        i+=1
                    detailYOYM = PandasModel(detailYOYDF)
                    detailYOYM2 = PandasModel(detailYOYDF,second = True)
                    detailYOYM3= PandasModel(detailYOYDF2,second = True)
                    #                    model = PandasModel(detailYOY)
                    listDict = {}
                    i = 0
                    for col in detailYOYDF.columns:
                        listDict.update({col:i})
                        #                print(listDict)
                        i+=1
                    self.detailYOYCols.addDetailYOY(listDict,IFNYISO, False,IFPJM)
                    self.detailYOY.setModel(detailYOYM)
                    self.detailYOY.setAlternatingRowColors(True)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.detailYOY.setColumnWidth(col,200)
                    #                    col = detailYOYDF.columns.get_loc("YOY\nDelta")
                    #                    self.detailYOY.setColumnWidth(col,70)
                    col = detailYOYDF.columns.get_loc("Summer\nPeak kW")
                    self.detailYOY.setColumnWidth(col,70)
                    col = detailYOYDF.columns.get_loc("Summer\nPeak kW to\nCapTag Var")
                    self.detailYOY.setColumnWidth(col,75)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW")
                    self.detailYOY.setColumnWidth(col,72)
                    col = detailYOYDF.columns.get_loc("CapTag\nFactor")
                    self.detailYOY.setColumnWidth(col,50)
                    if(detailYOYDF['MARKETCODE'].str.contains('PJM').any()):
                        self.curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
                        col = detailYOYDF.columns.get_loc(self.curStrip)
                        self.detailYOY.setColumnWidth(col,70)
                        col = detailYOYDF.columns.get_loc('TransTag\nto Peak\nkW Var')
                        self.detailYOY.setColumnWidth(col,65)
                    col = detailYOYDF.columns.get_loc("Forecasted\nAnnual to\nSCA Var")
                    self.detailYOY.setColumnWidth(col,60)
                    col = detailYOYDF.columns.get_loc("Percent\nAlloc")
                    self.detailYOY.setColumnWidth(col,47)
                    col = detailYOYDF.columns.get_loc("Day\nCount")
                    self.detailYOY.setColumnWidth(col,43)
                    col = detailYOYDF.columns.get_loc("Load\nFactor")
                    self.detailYOY.setColumnWidth(col,50)
                    col = detailYOYDF.columns.get_loc("Forecasted\nAnnual kWh")
                    self.detailYOY.setColumnWidth(col,95)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW to\n CapTag Var")
                    self.detailYOY.setColumnWidth(col,75)
                    col = detailYOYDF.columns.get_loc("Forecasted\nPeak kW")
                    self.detailYOY.setColumnWidth(col,100)
                    col = detailYOYDF.columns.get_loc("Profile\nCode")
                    self.detailYOY.setColumnWidth(col,74)
                    col = detailYOYDF.columns.get_loc("Loss Class")
                    self.detailYOY.setColumnWidth(col,130)

                    self.detailYOY.horizontalHeader().setFont(font)
                    self.detailYOY.setStyleSheet("alternate-background-color:#505F69;background-color: #061e26;selection-color #ffffff")
                    self.detailYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.detailYOY))
                    self.detailYOYCols.HideStart()

                    self.capTagsYOYCols.addDetailYOY(listDict,IFNYISO,True,IFPJM)
                    self.capTagsYOY.setModel(detailYOYM2)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.capTagsYOY.setColumnWidth(col,200)
                    self.capTagsYOY.horizontalHeader().setFont(font)
                    self.capTagsYOY.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color #ffffff")
                    self.capTagsYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.capTagsYOY))
                    self.capTagsYOYCols.HideStart()

                    self.transTagsYOYCols.addDetailYOY(listDict2,IFNYISO,False,IFPJM, transTable = True)
                    self.transTagsYOY.setModel(detailYOYM3)
                    col = detailYOYDF.columns.get_loc("Account ID")
                    self.transTagsYOY.setColumnWidth(col,200)
                    self.transTagsYOY.horizontalHeader().setFont(font)
                    self.transTagsYOY.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color #ffffff")
                    self.transTagsYOY.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.transTagsYOY))
                    self.transTagsYOYCols.HideStart()


                if(not empty):
                    #------------------------------------------------------------------------------------------------------------------
                    self.meterValuePR.setModel(meterValueM)
                    self.meterValuePR.setAlternatingRowColors(True)
                    self.meterValuePR.setStyleSheet("alternate-background-color:#505F69;background-color: #061e26;selection-color #ffffff")
                    col = meterValueDF.columns.get_loc("Strip")
                    self.meterValuePR.setColumnWidth(col,70)
                    col = meterValueDF.columns.get_loc("Account ID")
                    self.meterValuePR.setColumnWidth(col,185)
                    col = meterValueDF.columns.get_loc("Forecasted\nAnnual kWh")
                    self.meterValuePR.setColumnWidth(col,88)
                    col = meterValueDF.columns.get_loc("SCA\nTotal")
                    self.meterValuePR.setColumnWidth(col,90)
                    col = meterValueDF.columns.get_loc("Day\nCount")
                    self.meterValuePR.setColumnWidth(col,43)
                    col = meterValueDF.columns.get_loc("Load\nFactor")
                    self.meterValuePR.setColumnWidth(col,45)
                    col = meterValueDF.columns.get_loc("Summer\nPeak kW")
                    self.meterValuePR.setColumnWidth(col,60)
                    col = meterValueDF.columns.get_loc("Forecasted\nPeak kW")
                    self.meterValuePR.setColumnWidth(col,90)
                    col = meterValueDF.columns.get_loc('OnPeak\nkWh')
                    self.meterValuePR.setColumnWidth(col,76)
                    col = meterValueDF.columns.get_loc("OffPeak\nkWh")
                    self.meterValuePR.setColumnWidth(col,76)
                    #                    self.meterValuePR.setColumnWidth(7,90)
                    self.meterValuePR.horizontalHeader().setFont(font)
                    self.meterValuePR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterValuePR))
                    self.meterValuePRCols.HideStart() # THIS IS USED TO HIDE SPECIFIED COLUMNS
                #------------------------------------------------------------------------------------------------------------------



                self.meterReadPR.setModel(self.meterReadM)
                self.meterReadPR.setAlternatingRowColors(True)
                try:
                    col = self.meterReadDF.columns.get_loc("Account ID")
                    self.meterReadPR.setColumnWidth(col,185)
                    col = self.meterReadDF.columns.get_loc("Profile\nCode")
                    self.meterReadPR.setColumnWidth(col,70)
                    col = self.meterReadDF.columns.get_loc("Start\nRead\nTime")
                    self.meterReadPR.setColumnWidth(col,75)
                    col = self.meterReadDF.columns.get_loc("Stop\nRead\nTime")
                    self.meterReadPR.setColumnWidth(col,75)
                    col = self.meterReadDF.columns.get_loc("Stop\nRead\nValue")
                    self.meterReadPR.setColumnWidth(col,90)
                    col = self.meterReadDF.columns.get_loc("Peak\nValue")
                    self.meterReadPR.setColumnWidth(col,65)
                    col = self.meterReadDF.columns.get_loc("Delta\nDay\nCount")
                    self.meterReadPR.setColumnWidth(col,58)

                    self.meterReadPR.horizontalHeader().setFont(font)
                except:
                    pass
                self.meterReadPR.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color #ffffff")
                self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))

                if self.timeStampCheckBox1.checkState() == Qt.Checked: # this if statement takes care of whether to automatically hide or unhide ch1timestamp column
                    self.detailYOYCols.Hide(False, 'Ch1\nTimestamp')
                if self.timeStampCheckBox3.checkState() == Qt.Checked: # this if statement takes care of whether to automatically hide or unhide ch3timestamp column
                    self.detailYOYCols.Hide(False, 'Ch3\nTimestamp')
                try:
                    self.accts2Plot.clear()
                except:
                    pass
                self.acctDetail = self.prepareGraphs() # We obtain the summarize table with CapTags YOY and FPeak
                # self.calculateSummerPeaks('NEPOOL_CMP_035010120836')

    # THIS FUNCTION CALCULATES THE HISTORICAL SUMMER PEAKS FOR THE ACCOUNT THAT IS CLICKED, THEN PROCEEDS TO PLOT THE INFO ABOUT THAT ACCOUNT
    def onClickDetailedView(self,item):
        # The way this works is that the item is brought in as a parameter, we can then work with the text to find the specific
        # data we want to obtain and analyze
        # print(item.text()) # Print the text of the item for testing purposes
        try:
            self.calculateSummerPeaks(item.text())
        except:
            pass

    def calculateSummerPeaks(self, accountStr):


        # FIND A WAY TO QUERY DIRECTLY FROM TPPE METER READS QUERING SPECIFICALLY FOR EACH ACCOUNT, NOT ALL OF THEM AT THE SAME TIME
        """
        
        THIS FUNCTION WILL BE RESPONSIBLE FOR THE FOLLOWING:
            
            - GET THE DICTIONARY CONTAINING EACH DATAFRAME PER ACCOUNT 
            - CALCULATING THE SUMMER PEAKS OF EACH METER FOR EACH YEAR 60 MONTHS BACK

        
        At this point we have the meter reads separated by a dictionary of dataframes per Meter
        
        """
        # We filter the acctDetail dataframe by the accountStr we are currently observing
        acctDetail2 = self.acctDetail.get(accountStr)

        meterReads = self.orderedMR.get(accountStr) # We obtain the Meter Reads for the account we clicked on the QListWidget

        

        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day
        #
        # # Verify this calculation on when to get summer Peaks for the 'latest' years
        startComp = dt.datetime(ny,9,15) # We choose a date until when we will have the Summer Peak for the current year
        if now < startComp: # We then choose what year to use, either current year or the previous year that we already know the summer peak
            ny -=1
        #


        # mr = meterReadpiv6.get('NYISO_CONED_211306450802018')
        jun2AugPeaks = meterReads[meterReads['Start\nRead\nTime'].str.startswith(('06/', '07/', '08/'))].copy()
        jun2AugPeaks.dropna(subset=['Peak\nValue'], inplace=True, how='any')
        jun2AugPeaks['Start\nRead\nTime'] = pd.to_datetime(jun2AugPeaks['Start\nRead\nTime'], format="%m/%d/%Y")
        jun2AugPeaks['Start Year'] = (jun2AugPeaks['Start\nRead\nTime'].dt.year).astype(int)
        # jun2AugPeaks['Summer\nPeak'] = jun2AugPeaks.groupby(['Year'])['Peak\nValue'].transform(max)
        jun2AugPeaks = jun2AugPeaks.loc[jun2AugPeaks.groupby(["Account ID", "Start Year"])["Peak\nValue"].idxmax()]

        acctDetail2 = acctDetail2.merge(jun2AugPeaks, how = 'outer')


        # Here we will the missing values of the start and end columns
        # This occurs when there is more summer peaks found than there is captags
        if self.detailYOYDF['MARKETCODE'].str.contains('NEPOOL').any() or self.detailYOYDF['MARKETCODE'].str.contains('PJM').any() or self.detailYOYDF['MARKETCODE'].str.contains('MISO').any():

            acctDetail2['Start'].fillna(value = pd.to_datetime(acctDetail2['Start Year'].astype(int).astype(str)+'-06-01'), inplace = True)
            acctDetail2['Stop'].fillna(value=pd.to_datetime((acctDetail2['Start Year'].astype(int) + 1).astype(str) + '-06-01') -pd.DateOffset(days=1), inplace=True)


        elif self.detailYOYDF['MARKETCODE'].str.contains('NYISO').any():
            acctDetail2['Start'].fillna(value = pd.to_datetime(acctDetail2['Start Year'].astype(int).astype(str)+'-05-01'), inplace = True)
            acctDetail2['Stop'].fillna(value=pd.to_datetime((acctDetail2['Start Year'].astype(int) + 1).astype(str) + '-05-01') -pd.DateOffset(days=1), inplace=True)

        # The second case is when there is more captags found that summer peaks
        # Here, we will fill the missing value of the 'Start Year' Column with the year of the 'Start' Column
        acctDetail2['Start Year'].fillna(value=acctDetail2['Start'].dt.year)
        acctDetail2 = acctDetail2.sort_values(by = ['Start'], ascending=True)
        acctDetail2.reset_index(drop = True, inplace = True) # we reset the index so index values wont be out of order
        # acctDetail2['Forecasted\nPeak kW'].interpolate(method = 'pad')

        """ 
        THIS LINES BELOW REPLACE THE FUTURE SUMMER PEAKS FOR THE FUTURE CAPACITY TAGS PERIODS:
            | | | | | | | |  CURRENT CASE: 20-21, 21-31  | | | | | | | |                                                 
            V V V V V V V V                              V V V V V V V V   """
        nyIDX = (acctDetail2.index[acctDetail2['Start Year'] == ny].tolist())[0]
        colIDX = acctDetail2.columns.get_loc('Peak\nValue')
        # print(acctDetail2.iloc[nyIDX:, colIDX])
        # The line below fills the nan values after the current 'ny' year to that of the peak/max value for the 'ny'/current year
        acctDetail2.iloc[nyIDX:,colIDX].fillna(value = acctDetail2.loc[acctDetail2['Start Year'].astype(int) == ny, 'Peak\nValue'].iloc[0], inplace = True)
        acctDetail2['Forecasted\nPeak kW'].fillna(value=acctDetail2.loc[acctDetail2['Start Year'].astype(int) == ny, 'Forecasted\nPeak kW'].iloc[0], inplace=True)

        # with pd.option_context('display.max_rows', None, 'display.max_columns',
        #                        None):  # more options can be specified also
            # print(acctDetail2.loc[acctDetail2['Account ID'] == 'NEPOOL_CMP_035010120836'])
        # print("ny = ",ny)
        # print(acctDetail2.index[acctDetail2['Start Year'] == ny].tolist())

        """ #################### FORMATTING FOR FINAL RESULT TABLE BEGINS BELOW #################### """

        # The line below is in charge of renaming the columns to their appropiate new names
        acctDetail2 = acctDetail2.rename(columns = {'Capacity Tag':'Capacity\nTags','Start':'Period\nStart','Stop':
            'Period\nEnd','Start Year':'Start\nYear','Peak\nValue':'Summer\nPeaks'})
        titles = ['Account ID','Period\nStart','Period\nEnd','Start\nYear','Capacity\nTags','Forecasted\nPeak kW','Summer\nPeaks'] # list with column names reorder
        acctDetail2 = acctDetail2.reindex(columns = titles) # apply the new order of columns from list above



        acctDetail2['Period\nStart'] = pd.to_datetime(acctDetail2['Period\nStart']) # Convert to date-type to only display Date w/o time

        # acctDetail2['period'] = 'PY ' + (acctDetail2['Start\nYear']).astype(str).str[-2:] + '|' + acctDetail2['Period\nEnd'].dt.year.astype(str).str[-2:]
        acctDetail2['period'] = 'PY ' + acctDetail2['Period\nStart'].dt.year.astype(str).str[-2:] + '|' + acctDetail2['Period\nEnd'].dt.year.astype(str).str[-2:]

        acctDetail2['Period\nStart'] = acctDetail2['Period\nStart'].dt.date # Keep only date
        acctDetail2['Period\nEnd'] = pd.to_datetime(acctDetail2['Period\nEnd']) # Convert to date-type to only display Date w/o time
        acctDetail2['Period\nEnd'] = acctDetail2['Period\nEnd'].dt.date # Keep only date

        acctDetail2['Start\nYear'] = acctDetail2.apply(lambda x: "{:.0f}".format(x['Start\nYear']), axis=1)




        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        col = acctDetail2.columns.get_loc('Account ID')
        self.acctDetailTableView.setColumnWidth(col,190)

        N = len(acctDetail2['Capacity\nTags'])
        ind = np.arange(N)
        self.axDV.clear()
        # self.axDV.figure.clear()
        self.axDV.set_xticks(ind)
        self.axDV.set_xticklabels(acctDetail2['period'].tolist(), rotation=45)
        self.axDV.tick_params(labelcolor='#2ed2d0')
        self.axDV = self.figureDV.gca()

        # self.axDV.cla()

        import matplotlib.dates as mdates
        years = mdates.YearLocator()  # every year
        # self.axDV.xaxis.set_major_locator(years)
        self.figureDV.autofmt_xdate()
        width = .30

        # acctDetail2['Capacity\nTags'] = (acctDetail2['Capacity\nTags'].str.replace(',','')).replace([np.nan,'nan'],0).astype(float)
        # acctDetail2['Forecasted\nPeak kW'] = (acctDetail2['Forecasted\nPeak kW'].str.replace(',','')).replace([np.nan,'nan'],0).astype(float)
        acctDetail2['Summer\nPeaks'] =  acctDetail2['Summer\nPeaks'].astype(float)



        self.capTagsBarsDV = self.axDV.bar(ind-width/2, (acctDetail2['Capacity\nTags'].str.replace(',','')).replace([np.nan,'nan'],0).astype(float), 0.30, color='#061e26', label='CapTags')
        self.fPeakDV = self.axDV.plot(ind, (acctDetail2['Forecasted\nPeak kW'].str.replace(',','')).replace([np.nan,'nan'],0).astype(float), 0.3, color='#bf54ba', dashes=[6, 2], label='F-Peak')
        self.sPeakBarsDV = self.axDV.bar(ind+width/2, acctDetail2['Summer\nPeaks'].replace(np.nan, 0), 0.30, color='#e29016',label='S-Peak')
        # self.sPeaksDV = self.axDV.plot(acctDetail2['Start\nYear'],acctDetail2['Summer\nPeaks'].replace(np.nan,0), 0.8, color='#c67715', label='S-Peak',drawstyle='steps')
        self.axDV.set_title('Account DetailYOY', color='#FFFFFF')

        # import threading
        # import dash
        # import dash_core_components as dcc
        # import dash_html_components as html
        import plotly.graph_objs as go

        trace1 = go.Bar(x=acctDetail2['Start\nYear'], y=acctDetail2['Capacity\nTags'], name='CapTags')
        trace2 = go.Bar(x=acctDetail2['Start\nYear'], y=acctDetail2['Summer\nPeaks'], name='S-Peak')

        # def run_dash(data, layout):
        #     app = dash.Dash()
        #     app.layout = html.Div(children=[
        #         html.H1(children='Hello Dash'),
        #         html.Div(children='''
        #                 Dash: A web application framework for Python.
        #                 '''), dcc.Graph(id='example-graph', figure={'data': [trace1,trace2], 'layout': layout})])
        #     app.run_server(debug=False)


        data = [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'}, {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'}]
        layout = {'title': 'Account Detail YOY'}
        # threading.Thread(target=run_dash, args=(data, layout), daemon=True).start()



        try:
            self.layoutDV.removeWidget(self.canvasDV)
            self.canvasDV.close()
            self.layoutDV.removeWidget(self.toolbarDV)
            self.toolbarDV.close()
        except:
            pass



        self.canvasDV = FigureCanvas(self.figureDV)
        self.toolbarDV = NavigationToolbar(self.canvasDV,self,coordinates=True) # Declare the toolbar as an object
        self.layoutDV.addWidget(self.toolbarDV) # This adds the toolbar tools to the plot
        self.layoutDV.addWidget(self.canvasDV)
        self.canvasDV.draw()
        # handles, labels = [(a + b) for a, b in zip(self.axDV.get_legend_handles_labels(), self.axDV.get_legend_handles_labels())]
        handles, labels = self.axDV.get_legend_handles_labels()
        handles = handles[-3:]
        labels = labels[-3:]
        # print(handles,'\n',labels)
        self.figureDV.legend(handles, labels, loc = 'center left',fontsize=9,markerscale=.9,shadow=True)

        acctDetail2['Summer\nPeaks'] = acctDetail2.apply(lambda x: "{:,.2f}".format(x['Summer\nPeaks']), axis=1)

        self.acctDetailTableView.horizontalHeader().setFont(font)
        self.acctDetailTableView.setAlternatingRowColors(True)
        self.acctDetailTableView.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color: #1b83a7;selection-color #ffffff")
        self.acctDetailTableView.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.acctDetailTableView))
        self.acctDetailTableViewCols.HideStart()

        acctDetail2.drop(columns=['period'], inplace=True)
        self.acctDetailTableView.setModel(PandasModel(acctDetail2))  # Make the pandas model for the QTableView

        return {'data': [trace1,trace2], 'layout':go.Layout(title =  ' Account Detail YOY')}

    def prepareGraphs(self):
        
        # THIS FUNCTION WILL BE IN CHARGE OF PREPARING FOR THE GRAPHS PER ACCOUNT THAT WILL BE STORED IN A DICTIONARY
        """
        THIS DICTIONARY WILL CONTAIN THE FOLLOWING:
            
            The KEY: Will be a string type variable with each Account as a key
            The VALUE: The value will be a dataframe type variable containing the following info about the account:
                - TAGS YOY
                - FORECASTED PEAK ( WE ONLY HAVE ONE OVERALL F-PEAK CURRENTLY )
                - THERE WILL BE ANOTHER TABLE IN CHARGE OF SCANNING THE METER READS TABLE AND KEEPING THOSE VALUES PERTAINING TO SUMMER PEAKS YOY
        
        """
        tagYears = []
        acctDetail = pd.DataFrame(columns=['Account ID','Start','Stop'])
        acctDetail['Account ID'] = pd.Series(self.detailYOYDF['Account ID'])
        for col in self.detailYOYDF.columns:
            if 'PY' in col and 'CapTag' in col:
                acctDetail = acctDetail.join(pd.Series(self.detailYOYDF[col]))
                colSplit = col.split()
##                print(col)
                years = colSplit[1].split('|')
                yr1 = int(years[0]) + 2000
                yr2 = int(years[1]) + 2000
                tagYears.append(col)
#                yr1 = dt.date(yr1,1,1)
#                yr2 = dt.date(yr2,1,1)
#                self.detailYOYDF.rename(columns = {col:yr1})
            elif col == 'Forecasted\nPeak kW':
                acctDetail = acctDetail.join(pd.Series(self.detailYOYDF[col]))
            
        acctDetail.drop(acctDetail.tail(1).index,inplace=True)
#        print(acctDetail)
        # At this point, our new dataframe has the specific columns we need to begin the pivot table
#        acctDetail = pd.pivot_table(acctDetail, index = ['Account ID','Forecasted\nPeak kW'],values=tagYears)
        acctDetail = pd.melt(acctDetail, id_vars=['Account ID','Forecasted\nPeak kW'], value_vars = tagYears)
        if self.detailYOYDF['MARKETCODE'].str.contains('NEPOOL').any() or self.detailYOYDF['MARKETCODE'].str.contains('PJM').any() or self.detailYOYDF['MARKETCODE'].str.contains('MISO').any():
            acctDetail['Start'] = pd.to_datetime(((((acctDetail['variable'].str.split(expand = True))[1].str.split('|',expand = True))[0]).astype(int) + 2000).astype(str)+'-06-01')
            acctDetail['Stop'] = pd.to_datetime(((((acctDetail['variable'].str.split(expand = True))[1].str.split('|',expand = True))[1]).astype(int) + 2000).astype(str)+'-06-01') -pd.DateOffset(days=1)

        elif self.detailYOYDF['MARKETCODE'].str.contains('NYISO').any():
            acctDetail['Start'] = pd.to_datetime(((((acctDetail['variable'].str.split(expand = True))[1].str.split('|',expand = True))[0]).astype(int) + 2000).astype(str)+'-05-01')
            acctDetail['Stop'] = pd.to_datetime(((((acctDetail['variable'].str.split(expand = True))[1].str.split('|',expand = True))[1]).astype(int) + 2000).astype(str)+'-05-01') -pd.DateOffset(days=1)
                      
        acctDetail.drop(columns= ['variable'], inplace = True)

        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #     print(acctDetail)
        
        acctDetail['Start Year'] = (acctDetail['Start'].dt.year).astype(int)
#        acctDetail['Start'] = (acctDetail['variable'].str.split())[1]
#        colSplit = (acctDetail['variable'].str.split(expand = True))
#        acctDetail['variable'] = colSplit[1].str.split('|')
        acctDetail = acctDetail.rename(columns = {'value':'Capacity Tag'})

        # print('TEST!!!!')

        for i in acctDetail['Account ID'].unique():
            # print(i)
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            self.accts2Plot.addItem(item)
            #check to add filter column option just bc
        # listDict = pd.Series(acctDetail[''])
        # self.mrDict2 = pd.Series(data['PROFILECODE'].values, index=data['ACCOUNTID']).to_dict()

#        print(acctDetail)
        acctDetail = dict(tuple(acctDetail.groupby('Account ID')))
        
        return acctDetail
        
          
    #------------------------------------------------------------------------------------------------------------------
    def detailYOYLF(self, detailYOY, meterValFIN):
        detailYOY = detailYOY.rename(columns = {'ACCOUNTID':'Account ID','PROFILECODE':'Profile\nCode','LOSS_CLASS':'Loss Class'})
#        print('TESTPRINT',meterValFIN['Load\nFactor'])
        meterValFIN['Load\nFactor'] = meterValFIN['Load\nFactor'].str.rstrip("%").astype(float)
        refLF = pd.Series(detailYOY.index.values,index=detailYOY['Account ID']).to_dict()
        favDictIDRSCA = pd.Series(meterValFIN['Forecasted\nAnnual to\nSCA Var'].values,index=meterValFIN['Account ID']).to_dict()
        favDictPD = pd.Series(meterValFIN['Forecasted\nPeak kW'].values,index=meterValFIN['Account ID']).to_dict()
        favDictANN = pd.Series(meterValFIN['Forecasted\nAnnual kWh'].values,index=meterValFIN['Account ID']).to_dict()
        favDictLF = pd.Series(meterValFIN['Load\nFactor'].values,index=meterValFIN['Account ID']).to_dict()
        favDictSM = pd.Series(meterValFIN['Summer\nPeak kW'].values,index=meterValFIN['Account ID']).to_dict()
        favDictDayCount = pd.Series(meterValFIN['Day\nCount'].values,index=meterValFIN['Account ID']).to_dict()
        favDictST = pd.Series(meterValFIN['SCA\nTotal'].values,index=meterValFIN['Account ID']).to_dict()
#        print(favDictLF)
        now = dt.datetime.now()
        ny = now.year
        
        nm = now.month
        nd = now.day
        IFNYISO = False
        now = dt.datetime(int(ny),int(nm),int(nd))
        PY2 = str(now.year-2)[-2:]
        PY1 = str(now.year-1)[-2:]
        NY =  str(now.year)[-2:]
        NY1 = str(now.year+1)[-2:]
        detailYOYLF = detailYOY.copy()
        if(detailYOYLF['MARKETCODE'].str.contains('PJM').any() or detailYOYLF['MARKETCODE'].str.contains('MISO').any()):
            curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
            self.curStrip = curStrip
            transStrip = detailYOYLF[curStrip]            
            detailYOYLF.drop(columns = [curStrip],inplace= True)
#        meanLF = meterValFIN['Load\nFactor'].mean()
        

        pcode = detailYOYLF['Profile\nCode']
        lclass = detailYOYLF['Loss Class']
#        detailYOYLF['Percent\nAlloc'] = ""
        detailYOYLF.insert(loc = 1, column = 'Percent\nAlloc', value = "")
        detailYOYLF.drop(columns = ['Profile\nCode','Loss Class'],inplace= True)
        detailYOYLF['Forecasted\nPeak kW'] = ""
        detailYOYLF['Var %'] = ""
        detailYOYLF['Summer\nPeak kW'] = ""
        detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = ""
        if(detailYOYLF['MARKETCODE'].str.contains('PJM').any() or detailYOYLF['MARKETCODE'].str.contains('MISO').any()):
            detailYOYLF[curStrip] = transStrip
            detailYOYLF['TransTag\nto Peak\nkW Var'] = ""
        detailYOYLF['CapTag\nFactor'] = ""
        detailYOYLF['Load\nFactor'] = ""
        detailYOYLF['SCA\nTotal'] = ""
        detailYOYLF['Forecasted\nAnnual kWh'] = ""
        detailYOYLF['Forecasted\nAnnual to\nSCA Var'] = ""
        detailYOYLF['Day\nCount'] = ""
        
        detailYOYLF['Profile\nCode'] = pcode
        detailYOYLF['Loss Class'] = lclass
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Profile\nCode')] = ''
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Loss Class')] = ''
        IFNYISO = detailYOYLF['MARKETCODE'].str.contains('NYISO').any()
        pyNyiso = dt.datetime(int(ny),5,1)
        pyNEPJM = dt.datetime(int(ny),6,1)
        
        if(IFNYISO):
            if now < pyNyiso:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        else:
            if now < pyNEPJM:
                 prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                 nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
            elif now >= pyNyiso:
                 prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                 nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
        refIDRSCA = {}
        refLF2 = {}
        refPD = {}
        refANN = {}
        refSM = {}
        refDC = {} #day count
        refST = {} #SCA TOTAL
        for key,value in refLF.items():
            valIDRSCA = favDictIDRSCA.get(key)
            refIDRSCA[value] = valIDRSCA
            valLF = favDictLF.get(key)
            refLF2[value] = valLF
            valPD = favDictPD.get(key)
            refPD[value] = valPD
            valANN = favDictANN.get(key)
            refANN[value] = valANN
            valSM = favDictSM.get(key)
            refSM[value] = valSM
            valDC =favDictDayCount.get(key)
            refDC[value] = valDC
            valST = favDictST.get(key)
            refST[value] = valST
#            print(val)
            
        for i in range(len(refLF)):
            keyIDRSCA = list(refIDRSCA)[i]
            keyLF = list(refLF2)[i]
            keyPD = list(refPD)[i]
            keyANN = list(refANN)[i]
            keySM = list(refSM)[i]
            keyDC = list(refDC)[i]
            keyST = list(refST)[i]
            valueIDRSCA = refIDRSCA.get(keyIDRSCA)
            valueLF = refLF2.get(keyLF)
            valuePD = refPD.get(keyPD)
            valueANN = refANN.get(keyANN)
            valueSM = refSM.get(keySM)
            valueDC = refDC.get(keyDC)
            valueST = refST.get(keyST)
            detailYOYLF.at[keyIDRSCA,'Forecasted\nAnnual to\nSCA Var'] = valueIDRSCA
            detailYOYLF.at[keyLF,'Load\nFactor'] = valueLF   
            detailYOYLF.at[keyPD,'Forecasted\nPeak kW'] = valuePD
            detailYOYLF.at[keyANN,'Forecasted\nAnnual kWh'] = valueANN
            detailYOYLF.at[keySM,'Summer\nPeak kW'] = valueSM
            detailYOYLF.at[keyDC,'Day\nCount'] = valueDC
            detailYOYLF.at[keyST,'SCA\nTotal'] = valueST

        #IGNORE THIS
#        psCT = prevStrip+'\nCapTag'
#        nsCT = nextStrip+'\nCapTag'
        
        detailYOYLF['SCA\nTotal'] = detailYOYLF['SCA\nTotal'].str.replace(',','').astype(float) # MAYBE TBD
        detailYOYLF['Forecasted\nPeak kW'] = detailYOYLF['Forecasted\nPeak kW'].str.replace(',','').astype(float)
        detailYOYLF['Forecasted\nAnnual kWh'] = detailYOYLF['Forecasted\nAnnual kWh'].str.replace(',','').astype(float)
        detailYOYLF = detailYOYLF.sort_values(by = ['Forecasted\nAnnual kWh'],ascending = False)
        detailYOYLF['Summer\nPeak kW'] = detailYOYLF['Summer\nPeak kW'].str.replace(',','').astype(float)
        
#        print(detailYOYLF[nextStrip])
        try:
            detailYOYLF[nextStrip] = detailYOYLF[nextStrip].replace(r'^\s*$', np.nan, regex=True)
            detailYOYLF[nextStrip] = detailYOYLF[nextStrip].str.replace(',','').astype(float)
        except:
            detailYOYLF[nextStrip] = detailYOYLF[nextStrip].astype(float)
        #DONE- fixed pchange
        detailYOYLF['Var %'] = (((detailYOYLF['Forecasted\nPeak kW']).astype(float)-(detailYOYLF[nextStrip]).astype(float))/(abs((detailYOYLF[nextStrip]).astype(float)))) *100
        
        # HERE WE CALCULATE THE SUM OF THE SCA\NTOTAL COLUMN
        sumSCA = detailYOYLF['SCA\nTotal'].sum()
        detailYOYLF.iloc[-1,detailYOYLF.columns.get_loc('SCA\nTotal')] = sumSCA
        detailYOYLF['SCA\nTotal'] = detailYOYLF.apply(lambda x: '{:,.0f}'.format(x['SCA\nTotal']), axis =1)
        
        
        #HERE WE CALCULATE THE WEIGHT ACCORDING TOO THE FORECASTED ANNUAL KWH
        sumKWH = detailYOYLF['Forecasted\nAnnual kWh'].sum()
        weightF = detailYOYLF['Forecasted\nAnnual kWh']/sumKWH
        detailYOYLF['Percent\nAlloc'] = weightF.copy() *100
        detailYOYLF['Percent\nAlloc'] = detailYOYLF['Percent\nAlloc'].round()
        detailYOYLF['Percent\nAlloc'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['Percent\nAlloc']), axis =1)
        detailYOYLF.iloc[-1,detailYOYLF.columns.get_loc('Percent\nAlloc')] = ''
        ##################---------------------------------###################        
        
        if(detailYOYLF['MARKETCODE'].str.contains('PJM').any() or detailYOYLF['MARKETCODE'].str.contains('MISO').any()):
            toFloat = detailYOYLF[curStrip].str.replace(',','').astype(float).copy()
            detailYOYLF['TransTag\nto Peak\nkW Var'] = (((detailYOYLF['Forecasted\nPeak kW']).astype(float)-toFloat)/(abs(toFloat))) *100 # DONE
            detailYOYLF['TransTag\nto Peak\nkW Var'] = detailYOYLF['TransTag\nto Peak\nkW Var'].replace([-np.Inf,np.inf,-np.Inf,200],np.nan)
            
            # HERE WE CALCULATE THE WEIGHTED AVG OF THE TransTag\nto Peak\nkW Var COLUMN DEPENDENT ON THE FORECASTED ANNUAL KWH
            weight = detailYOYLF['TransTag\nto Peak\nkW Var'] *weightF
            weightAvg = weight.sum()
            detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('TransTag\nto Peak\nkW Var')] = weightAvg
            ##################---------------------------------###################
            
            detailYOYLF['TransTag\nto Peak\nkW Var'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['TransTag\nto Peak\nkW Var']), axis =1)
            detailYOYLF['TransTag\nto Peak\nkW Var'] = detailYOYLF['TransTag\nto Peak\nkW Var'].replace('nan%','nan')
        try:
            # DONE
            detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = (((detailYOYLF['Summer\nPeak kW']).astype(float)-(detailYOYLF[nextStrip]).astype(float))/(abs(detailYOYLF[nextStrip]).astype(float))) *100
            detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = detailYOYLF['Summer\nPeak kW to\nCapTag Var'].replace([-np.Inf,np.inf,-np.Inf,200],np.nan)
            meanVAR = detailYOYLF['Summer\nPeak kW to\nCapTag Var'].mean()
            detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Summer\nPeak kW to\nCapTag Var')] = meanVAR
            
            # HERE WE CALCULATE THE WEIGHTED AVG OF THE Summer\nPeak kW to\nCapTag Var COLUMN DEPENDENT ON THE FORECASTED ANNUAL KWH
            weight = detailYOYLF['Summer\nPeak kW to\nCapTag Var'] *weightF
            weightAvg = weight.sum()
            detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Summer\nPeak kW to\nCapTag Var')] = weightAvg
            ##################---------------------------------###################
            
            detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['Summer\nPeak kW to\nCapTag Var']), axis =1)
            detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = detailYOYLF['Summer\nPeak kW to\nCapTag Var'].replace('nan%','nan')
            detailYOYLF['Summer\nPeak kW to\nCapTag Var'] = detailYOYLF['Summer\nPeak kW to\nCapTag Var'].replace('None%','nan')
        except:
           print("no working")
        
        # HERE WE CALCULATE THE CAPTAG FACTOR 
        detailYOYLF['CapTag\nFactor'] = ((detailYOYLF['Forecasted\nAnnual kWh'])/(detailYOYLF[nextStrip]*8760))*100
        detailYOYLF['CapTag\nFactor'] = detailYOYLF['CapTag\nFactor'].replace([-np.Inf,np.inf,-np.Inf],np.nan)
        ##################---------------------------------###################
        
        # HERE WE CALCULATE THE WEIGHTED AVG OF THE CAPTAGFACTOR COLUMN DEPENDENT ON THE FORECASTED ANNUAL KWH
        weightCapTagFactor = detailYOYLF['CapTag\nFactor'] *weightF
        weightAvgCapTagFactor = weightCapTagFactor.sum()
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('CapTag\nFactor')] = weightAvgCapTagFactor
        ##################---------------------------------###################
        
        # HERE WE CALCULATE THE WEIGHTED AVG OF THE Forecasted\nPeak kW to\n CapTag Var COLUMN DEPENDENT ON THE FORECASTED ANNUAL KWH
        detailYOYLF['Var %'] = detailYOYLF['Var %'].replace([-np.Inf,np.inf,-np.Inf],np.nan)
        weight = detailYOYLF['Var %'] *weightF
        weightAvg = weight.sum()
        weightAvg = int(round(weightAvg))
#        print(weightAvg)
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Var %')] = weightAvg
#        print(detailYOYLF['Var %'])
        ##################---------------------------------###################
        
        # HERE WE CALCULATE THE WEIGHTED AVG OF THE Day\nCount COLUMN DEPENDENT ON THE FORECASTED ANNUAL KWH
        dayCount = detailYOYLF['Day\nCount'].str.replace('%','')
        dayCount = dayCount.str.replace(',','').astype(float)
        weight = dayCount *weightF
        weightAvg = weight.sum()
        weightAvg = int(round(weightAvg))
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Day\nCount')] = weightAvg
        ##################---------------------------------###################
        
        # HERE WE CALCULATE THE WEIGHTED AVG OF THE FAV ANNUAL TO SCA VARIANCE
        FASCA = detailYOYLF['Forecasted\nAnnual to\nSCA Var'].str.replace('%','')
        FASCA = FASCA.str.replace(',','').astype(float)
        weightAnnualtoSCA = FASCA*weightF
        weightAvgAnnualtoSCA = weightAnnualtoSCA.sum() # Get the sum of this column
        weightAvgAnnualtoSCA = "{0:.0f}%".format(weightAvgAnnualtoSCA)
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Forecasted\nAnnual to\nSCA Var')] = weightAvgAnnualtoSCA
        detailYOYLF['Forecasted\nAnnual to\nSCA Var'] = detailYOYLF['Forecasted\nAnnual to\nSCA Var'].replace('nan%','nan')
        ##################---------------------------------###################
        
        
        
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Forecasted\nAnnual kWh')] = sumKWH
        detailYOYLF['Forecasted\nAnnual kWh'] = detailYOYLF.apply(lambda x: '{:,.2f}'.format(x['Forecasted\nAnnual kWh']), axis=1)

        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Load\nFactor')] = self.sumLF # Set the mean of the LF Column
        sumPeakDem = detailYOYLF['Forecasted\nPeak kW'].sum() # Get the sum of the Forecasted\nPeak kW column
        
        countYears = (dt.datetime.now().year + 5) - 2016
        peakSumlst = [sumPeakDem]*countYears
        peakSum = pd.Series(peakSumlst)
        ind = np.arange(countYears)
        self.fPeak = self.ax.plot(ind, peakSum,0.3,color = '#bf54ba', dashes=[6,2], label = 'Peak')
        self.figure.legend(self.capTagsBars,['CapTags'],loc='upper left',shadow=True,fontsize=8,markerscale=.9)
        self.figure.legend(self.fPeak,['F-Peak'],loc='upper right',shadow=True,fontsize=8,markerscale=.9)
        
        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Forecasted\nPeak kW')] = sumPeakDem # Set the sum OF Forecasted\nPeak kW column to last row in respective col
        detailYOYLF['Forecasted\nPeak kW'] = detailYOYLF.apply(lambda x: '{:,.2f}'.format(x['Forecasted\nPeak kW']), axis =1)
        detailYOYLF['CapTag\nFactor'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['CapTag\nFactor']), axis =1)
        detailYOYLF['CapTag\nFactor'] = detailYOYLF['CapTag\nFactor'].replace('nan%','nan')
        
        summerPeak = detailYOYLF['Summer\nPeak kW'].sum()
#        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Forecasted\nAnnual to\nSCA Var')] = self.fPeakSCAVarAVG

        detailYOYLF.iloc[-1, detailYOYLF.columns.get_loc('Summer\nPeak kW')] = summerPeak
        detailYOYLF['Summer\nPeak kW'].fillna(value=pd.np.nan, inplace=True) 
        
        detailYOYLF['Var %'] = detailYOYLF['Var %'].replace([-np.Inf,np.inf,-np.Inf,200],np.nan)
        detailYOYLF['Var %'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['Var %']), axis =1)
        try:
            detailYOYLF['Var %'] = detailYOYLF['Var %'].replace('nan%','nan')
            
        except:
            pass
        try:
            detailYOYLF['Var %'] = detailYOYLF['Var %'].replace('None%','nan')
        except:
            pass
        
        detailYOYLF.fillna(value = np.nan, inplace = True)
        
        meterValFIN.fillna(value = np.nan, inplace = True)
        detailYOYLF['Load\nFactor'] = detailYOYLF.apply(lambda x: '{:,.0f}%'.format(x['Load\nFactor']), axis =1)
        
        meterValFIN['Load\nFactor'] = meterValFIN.apply(lambda x: "{:,.0f}%".format(x['Load\nFactor']), axis=1) 
        detailYOYLF['Load\nFactor'] = detailYOYLF['Load\nFactor'].replace('nan%','nan')
        detailYOYLF['Summer\nPeak kW'] = detailYOYLF.apply(lambda x: "{:,.2f}".format(x['Summer\nPeak kW']), axis=1)
        detailYOYLF[nextStrip] = detailYOYLF.apply(lambda x: "{:,.2f}".format(x[nextStrip]), axis=1)

        detailYOYLF = detailYOYLF.rename(columns = {"YOY\nDelta":'YOY\nDelta','Var %':'Forecasted\nPeak kW to\n CapTag Var'})

        detailYOYLF.insert(loc=1, column='Ch3\nTimestamp', value="")
        detailYOYLF.insert(loc=1, column='Ch1\nTimestamp', value="")


        detailYOYLF.loc[:,'Ch3\nTimestamp'] = detailYOYLF['Account ID'].map(self.AcctTimestampCh3) # join dictionary to dataframe
        detailYOYLF.loc[:,'Ch1\nTimestamp'] = detailYOYLF['Account ID'].map(self.AcctTimestampCh1)


        model = PandasModel(detailYOYLF)
        

        return model, detailYOYLF

    def calcVar(self, meterValFIN, meterValFIN2, favDict, mrDict, sPeakDict):
        varDiff = {}
        for key,value in mrDict.items():
            v1 = favDict.get(key)
            v2 = mrDict.get(key)
            try:
                
                pDiff = (v1-v2)/(abs(v2)) *100
                varDiff[key] = pDiff
            except:
                varDiff[key] = float('NaN')
                
                
        varTable = pd.DataFrame.from_dict(varDiff, orient='index',columns = ['%Diff vs Meter Reads'])
        #varTable.reset_index(drop = False, inplace = True)
        varTable = varTable.rename_axis('Account ID').reset_index()
#        print(sPeakDict)
#         print(meterValFIN2)
        ref = pd.Series(meterValFIN2.index.values,index=meterValFIN2['Account ID']).to_dict()
        meterValFIN['Var %'] = "" # percent difference
        meterValFIN['Summer\nPeak kW'] = ""
        meterValFIN['SCA\nTotal'] = ""
        meterValFIN['Day\nCount'] = ""
        ref2 = {}
        refSummer = {}
        refTotSCA = {}
        refDayCount = {}
        for key,value in ref.items():
            v1 = varDiff.get(key) # get the variance
            v2 = sPeakDict.get(key) # Get the Summer Max Peak
            v3 = mrDict.get(key) # Get the total SCA 
            v4 = self.dayCountdict.get(key)
            ref2[value] = v1
            refSummer[value] = v2
            refTotSCA[value] = v3
            refDayCount[value] = v4
        
        for i in range(len(ref2)):
            keyPdiff = list(ref2)[i]
            keySummerP = list(refSummer)[i]
            keyTotSCA = list(refTotSCA)[i]
            keyDayCount = list(refDayCount)[i]
            valPdiff = ref2.get(keyPdiff)
            valSummerP = refSummer.get(keySummerP)
            valTotSCA = refTotSCA.get(keyTotSCA)
            valDayCount = refDayCount.get(keyDayCount)
            meterValFIN.at[keyPdiff,'Var %'] = valPdiff
            meterValFIN.at[keySummerP,'Summer\nPeak kW'] = valSummerP
            meterValFIN.at[keyTotSCA,'SCA\nTotal'] = valTotSCA
            meterValFIN.at[keyDayCount,'Day\nCount'] = valDayCount
            
        meterValFIN['Summer\nPeak kW'].fillna(value=pd.np.nan, inplace=True)
        meterValFIN['Summer\nPeak kW'].replace('',pd.np.nan,inplace = True)
        
        meterValFIN['Var %'].fillna(value=pd.np.nan, inplace=True)
        meterValFIN['Var %'].replace('',pd.np.nan,inplace = True)
        meterValFIN['Var %'].replace([-np.Inf,np.inf,-np.Inf,200],pd.np.nan,inplace = True)
        
        meterValFIN['SCA\nTotal'].fillna(value=pd.np.nan, inplace=True)
        meterValFIN['SCA\nTotal'].replace('',pd.np.nan,inplace = True)
        meterValFIN['SCA\nTotal'].replace([-np.Inf,np.inf,-np.Inf,200],pd.np.nan,inplace = True)
        meterValFIN['SCA\nTotal'] = meterValFIN.apply(lambda x: "{:,.0f}".format(x['SCA\nTotal']), axis=1)
        
        meterValFIN['Day\nCount'].fillna(value=pd.np.nan, inplace=True)
        meterValFIN['Day\nCount'].replace('',pd.np.nan,inplace = True)
        meterValFIN['Day\nCount'].replace([-np.Inf,np.inf,-np.Inf,200],pd.np.nan,inplace = True)
        meterValFIN['Day\nCount'] = meterValFIN.apply(lambda x: "{:,.0f}".format(x['Day\nCount']), axis=1)
#        meterValFIN['Var %'].fillna(value = 0)
#        self.fPeakSCAVarAVG = meterValFIN['Var %'].mean()
#        self.fPeakSCAVarAVG = "{0:.0f}%".format(self.fPeakSCAVarAVG)
        meterValFIN['Var %'] = meterValFIN.apply(lambda x: "{:,.0f}%".format(x['Var %']), axis=1)
        meterValFIN['Summer\nPeak kW'] = meterValFIN.apply(lambda x: "{:,.2f}".format(x['Summer\nPeak kW']), axis=1)
        try:
            meterValFIN['Var %'] = meterValFIN['Var %'].replace('nan%','nan')
        except:
            pass
        try:
            meterValFIN['Var %'] = meterValFIN['Var %'].replace('None%','nan')
        except:
            pass
        try:
            meterValFIN = meterValFIN.rename(columns={'Var %':'Forecasted\nAnnual to\nSCA Var'})
            titles = ["Strip","Account ID",'SCA\nTotal',"Forecasted\nAnnual kWh",'Forecasted\nAnnual to\nSCA Var','Day\nCount',"Summer\nPeak kW","Load\nFactor","Forecasted\nPeak kW","AVGDemand (KWHs)",'OnPeak\nkWh',"OffPeak\nkWh",'BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']
            meterValFIN = meterValFIN.reindex(columns = titles) # 
        except:
            # IN CASE LOAD FACTOR DOES NOT EXIST
            meterValFIN = meterValFIN.rename(columns={'Var %':'Forecasted\nAnnual to\nSCA Var'})
            titles = ["Strip","Account ID",'SCA\nTotal',"Forecasted\nAnnual kWh",'Forecasted\nAnnual to\nSCA Var','Day\nCount',"Summer\nPeak kW","Forecasted\nPeak kW","AVGDemand (KWHs)",'OnPeak\nkWh',"OffPeak\nkWh",'BCKST_AVERAGE','BCKST_PEAK','BCKST_TOTAL']
            meterValFIN = meterValFIN.reindex(columns = titles)
        
        model = PandasModel(meterValFIN)
        listDict = {}
        i = 0
        for col in meterValFIN.columns:
            listDict.update({col:i})
#            print(listDict)
            i+=1
        self.meterValuePRCols.addFAV(listDict)
        #print(model)
        return model, meterValFIN

    # THIS FUNCITON HANDLES WHEN EITHER CHECKBOX IS CLICKED/CHANGED THAT HANDLE THE TIMESTAMP HIDE/UNHIDES
    def onClickTimestampCheckBox(self, channel):
        if channel == 1:
            if (self.timeStampCheckBox1.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch1\nTimestamp')
                # pending to check/uncheck on filter
                # print("Display TimeStamp")
            elif (self.timeStampCheckBox1.checkState() == Qt.Unchecked):
                self.detailYOYCols.Hide(True, 'Ch1\nTimestamp')
                # pending to check/uncheck on filter
                # print("Hide Timestamp")
        elif channel == 3:
            if (self.timeStampCheckBox3.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch3\nTimestamp')
                # pending to check/uncheck on filter
                # print("Display TimeStamp")
            elif (self.timeStampCheckBox3.checkState() == Qt.Unchecked):
                self.detailYOYCols.Hide(True, 'Ch3\nTimestamp')
                # pending to check/uncheck on filter
                # print("Hide Timestamp")


    def onClickChangeTags(self, text):
        if (text == 'Current PY CapTag'):
            self.detailYOYCols.displayTags(text,self.IFNYISO,self.IFPJM)
            # print('current')
            if (self.timeStampCheckBox1.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch1\nTimestamp')
            if (self.timeStampCheckBox3.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch3\nTimestamp')

        elif(text == 'Future PY CapTags'):
            self.detailYOYCols.displayTags(text,self.IFNYISO,self.IFPJM)
            if (self.timeStampCheckBox1.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch1\nTimestamp')
            if (self.timeStampCheckBox3.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch3\nTimestamp')
            # print('future')
        elif(text == 'All CapTags'):
            self.detailYOYCols.displayTags(text,self.IFNYISO,self.IFPJM)
            if (self.timeStampCheckBox1.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch1\nTimestamp')
            if (self.timeStampCheckBox3.checkState() == Qt.Checked):
                self.detailYOYCols.Hide(False, 'Ch3\nTimestamp')
            # print('all captags')



    def onClickChangeMR(self, text):

        # this will be the function in charge of displaying the Meter Reads PR table
        # deciding whether to displaying it or not, depending on the status of checked or unchecked
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        if(self.comboBoxMRHists.currentText() == '12 Months'):
            
            try:
                # self.meterReadM, mrDict, self.meterReadDF, sPeakDict = self.meterRead(self.prNumStr, self.revNum, 12)
#                self.meterReadPR.setModel(None)
                self.meterReadPR.setModel(self.meterReadM)
                self.meterReadPR.setAlternatingRowColors(True)
            except:
                pass
        elif(self.comboBoxMRHists.currentText() == '36 Months'):

            try:
                # 505F69
                # self.meterReadPR.setModel(None)
                self.meterReadFullMCust, mrDict2, self.meterReadDF2, sPeakDict2, dictMR = self.meterRead(self.prNumStr, self.revNum, 36)
                self.meterReadPR.setModel(self.meterReadFullMCust)
                self.meterReadPR.setAlternatingRowColors(True)
            except:
                pass
        elif(self.comboBoxMRHists.currentText() == '60 Months'):

            try:
                # self.meterReadPR.setModel(None)
                # self.meterReadFullMCust, mrDict2, self.meterReadDF2, sPeakDict2, dictMR = self.meterRead(self.prNumStr, self.revNum, 60)
                self.meterReadPR.setModel(self.meterReadFullM)
                self.meterReadPR.setAlternatingRowColors(True)
            except:
                pass
        try:
            col = self.meterReadDF.columns.get_loc("Account ID")
            self.meterReadPR.setColumnWidth(col,185)
            col = self.meterReadDF.columns.get_loc("Profile\nCode")
            self.meterReadPR.setColumnWidth(col,70)
            col = self.meterReadDF.columns.get_loc("Start\nRead\nTime")
            self.meterReadPR.setColumnWidth(col,75)
            col = self.meterReadDF.columns.get_loc("Stop\nRead\nTime")
            self.meterReadPR.setColumnWidth(col,75)
            col = self.meterReadDF.columns.get_loc("Stop\nRead\nValue")
            self.meterReadPR.setColumnWidth(col,90)
            col = self.meterReadDF.columns.get_loc("Peak\nValue")
            self.meterReadPR.setColumnWidth(col,65)
            col = self.meterReadDF.columns.get_loc("Delta\nDay\nCount")
            self.meterReadPR.setColumnWidth(col,58)
            self.meterReadPR.horizontalHeader().setFont(font)
        except:
            pass
        self.meterReadPR.horizontalHeader().setFont(font)
        self.meterReadPR.setStyleSheet("alternate-background-color: #505F69;background-color: #061e26;selection-color #ffffff")
        self.meterReadPR.selectionModel().selectionChanged.connect(lambda: self.onSelection(self.meterReadPR))

        
# The context menu is in charge of handling the right click menu, and the events occured when a specific button is clicked.
    def contextMenuEvent(self, table):
        
        self.menu = QMenu(self) 
        copyAction = self.menu.addAction("Copy     Ctrl+C") # context menu action added for copy
        findAction = self.menu.addAction("Find       Ctr+F") # context menu action added for find
        findDetailAction = self.menu.addAction("More Info    Shift+Z") # context menu action added for shortcut to detailed view
        pChangeAction = self.menu.addAction("Percent Change") # context menu added for percent change calculator
        plotAction = self.menu.addMenu("Plot Menu") # context menu action for plot menu
        plotList = plotAction.addAction("Add to Plot List") # child of plot menu
        plot = plotAction.addAction("Plot")  # child of plot menu
        copyWHeadsAction = self.menu.addAction("Copy w/ Headers") # context menu action added to copy selected cells w/ headers included
        filterAction = self.menu.addAction("Filter Columns") # context menu action added to open the Filter columns menu
        
        
        index = table.selectionModel().currentIndex() # Current Index
        row = index.row() # gets index of current row selected in table
        col = index.column()  # gets index of current column selected in table

        copyAction.triggered.connect(lambda: self.copySlot(table, True)) # when copy button is pressed, call copySlot function
        copyWHeadsAction.triggered.connect(lambda: self.copySlot(table, False)) # when copy button is pressed, call copySlot function
        pChangeAction.triggered.connect(self.execPChange)
        findDetailAction.triggered.connect(lambda: self.detailedViewSlot(table)) # when the More info button is pressed, call detailedView slot function
        findAction.triggered.connect(lambda: self.execFind(table)) # when find button is pressed, call execFind Function to open a Find Window
        
        plot.triggered.connect(self.plotSlot)
        plotList.triggered.connect(lambda: self.addList(table)) # when plot button is pressed, call plotslot function
        filterAction.triggered.connect(lambda: self.showColFilt(table))
        # add other required actions
        self.menu.popup(QtGui.QCursor.pos()) # Pops custom context menu to cursor's position
        
    def execPChange(self):
        self.pChange = pChange()
        self.pChange.show()

        
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
        elif table == self.capTagsYOY:
            self.capTagsYOYCols.show()
        elif table == self.transTagsYOY:
            self.transTagsYOYCols.show()
    
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
#                print(valStr)
                if(valStr != 'nan'):
                    try:
                        
                        val = float(valStr.replace(',',''))
#                        print(val)
                        # if val is type float, convert to float with empty space replacing commas
                        listP.append(val) # Append to list as float
                        
                    except:
#                        print("ERROR! STR DETECTED NOT CONVERTABLE")
                        try:
#                            print('TEST ',valStr)
                            val = valStr.replace(',','')
#                            print('TEST ',valStr.replace('%',''))
                            val = float(val.replace('%',''))
                            listP.append(val)
#                            print(val)
                        except:
#                            print(valStr)
                            listP.append(0)
                else:
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

    # THIS IS THE CUSTOM CONTEXT MENU SLOT THAT WILL ACT AS A SHORTCUT FROM OTHER TABLES TO THE DETAILED VIEW TAB
    def detailedViewSlot(self, table):
        # AcctID_idx = table.columns.get_loc("Account ID")

        acceptable = False
        selection = table.selectedIndexes()
        if len(selection) == 1:
            for index in selection:
                # item = index.data()
                row = index.row()
                # item = str(item)
                # print('---------------------------')
                header = table.model().headerData(index.column(),Qt.Horizontal)
                for i in range(table.model().columnCount()):
                    h = table.model().headerData(i,Qt.Horizontal)
                    if h == 'Account ID':
                        colIDX = i
                        break
                acct = table.model().index(row,colIDX).data()
                # print('THIS IS THE ACCOUNT!!!    ', acct)

                # If no acct ID string found
                if acct == '' or acct == np.nan:
                    # print(item)
                    acceptable = False
                    self.msgBox1 = msgBox()
                    self.msgBox1.text.setText(("Warning!\nString to search Account ID empty.\nVerify Account ID column is populated."))
                    self.msgBox1.show()
                    acceptable = False
                #
                else:
                    acceptable = True

        # else, a message window will open saying only available for Account ID column!
        else:
            self.msgBox1 = msgBox()
            self.msgBox1.show()
            self.msgBox1.text.setText(("Warning!\nOnly available per Account/Row!"))
            acceptable = False
        # at this point we have the item
        if acceptable == True: # If we pass the criteria to be able to search for an Account ID in the detailed view tab

            page = self.detailTab.findChildren(QWidget,'detailedViewTab')  # 'detailedViewTab' is the name of the tab in which the detailed View tab is located
            index = self.detailTab.indexOf(page[0]) # Here we get the index of the tab we are looking for
            #            print('Index of Detail = ', index)
            self.detailTab.setCurrentIndex(index) # We set the current index to that of the index we found

            # We obtain a pointer to the item we are looking for, that is, the string for the Account ID that was clicked,
            item = (self.accts2Plot.findItems(acct, Qt.MatchExactly)) # The pointer
            self.accts2Plot.clearSelection() # Before we go to the item that was clicked, we clear what was previously selected
            # print(item)

            self.accts2Plot.setCurrentItem(item[0],QtCore.QItemSelectionModel.Select)


    # THIS FUNCTION IS THE OPERATION INVOLVED WITH THE COPY SLOT IN THE RIGHT CLICK CONTEXT MENU
    def copySlot(self, table, condition):

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
    
        
import qdarkstyle 
if __name__ == "__main__":
    layout = {'title': 'Account Detail YOY'}
    # threading.Thread(target=run_dash, args=(layout), daemon=True).start()
    appctxt = ApplicationContext()
    Ui = Main()
    appctxt.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Ui.showMaximized()
    sys.exit(appctxt.app.exec_())
    
    
    
    
    
    
    
    
    
    
    