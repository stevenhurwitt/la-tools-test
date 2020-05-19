# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 07:54:50 2019

@author: WV5945

"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import datetime as dt
import calendar


class PandasModel(QtCore.QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None, *args, **kwargs): 
        ifTrue = False
        self.ifTrue = kwargs.get("second")
#        print(ifTrue)
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self.minD = 0
        self.maxD = 0
        try:
            length = len(self._df.index) # Get # of rows 
            deltaSet = self._df['YOY\nDelta'].iloc[:length-1].str.replace(',','')
            deltaSet = deltaSet.str.replace('%','').astype(float)
            sumD = deltaSet.sum()
#            minD = deltaSet.min()
#            maxD = deltaSet.max()
        except:
            pass
        else:
            self.minD = -100
            self.maxD = 100
            self.sumD = sumD
        now = dt.datetime.now()
        ny = now.year
        nm = now.month
        nd = now.day
        pyNyiso = dt.datetime(int(ny),5,1)
        pyNEPJM = dt.datetime(int(ny),6,1)
        now = dt.datetime(int(ny),int(nm),int(nd))
        PY2 = str(now.year-2)[-2:]
        PY1 = str(now.year-1)[-2:]
        NY =  str(now.year)[-2:]
        NY1 = str(now.year+1)[-2:]
        self.curStrip = 'PY ' + NY + '|' + NY + '\nTransTag'
        self.prevTStrip = 'PY ' + PY1 + '|' + PY1 + '\nTransTag'
        try:
            IFNYISO = self._df['MARKETCODE'].str.contains('NYISO').any()
            
        except:
            pass
        else:        
        
            if(IFNYISO):
                if now < pyNyiso:
                    self.prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                    self.nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                elif now >= pyNyiso:
                    self.prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                    self.nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
            else:
                if now < pyNEPJM:
                    self.prevStrip = 'PY ' + PY2 + '|' + PY1 + '\nCapTag'
                    self.nextStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                elif now >= pyNyiso:
                    self.prevStrip = 'PY ' + PY1 + '|' + NY + '\nCapTag'
                    self.nextStrip = 'PY ' + NY + '|' + NY1 + '\nCapTag'
                    
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


                if str(self._df.iloc[index.row(),index.column()-1]) == 'Total':
                    bgc = QtGui.QColor()
                    bgc.setNamedColor("#219897")
                    return bgc
                try:
                    colDF = self.getColumnNumber('TransTag\nYOY Delta')
                    length = len(self._df.index) # Get # of rows

                except:

                    pass
                else:

                    if index.column() == colDF:

                        dist = abs(self.minD - self.maxD)
#                        print('max: ',self.maxD)
#                        print('min: ',self.minD)
                        thres = [0]*92
                        for i in range(len(thres)):
                            if i == 0:
                                thres[i] = 0
                            else:
                                thres[i] = thres[i-1] + dist/91
                        indexVal = (str(self._df.iloc[index.row(),index.column()]).replace(',',''))
                        indexVal = float(indexVal.replace('%',''))
                        if(index.row() != length-1):
                            deltaset = self._df['TransTag\nYOY Delta'].str.replace(',','')
                            avg = deltaset.str.replace('%','').astype(float).mean()
                            for i in range(len(thres)):

                                if(avg == 0):
                                    bgc = QtGui.QColor()
                                    bgc.setNamedColor("#061e26")
                                    return bgc
#                                elif(indexVal >= 100):
                                elif(indexVal == np.nan or indexVal == 'nan%' or indexVal == 'nan' or indexVal == None or indexVal == 'None'):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(0, 225, 102, 255)
                                    return bgc
                                elif(indexVal >= 100):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(92, 225, 102, 255)
                                    return bgc
                                elif(indexVal <= -100):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(0, 225, 102, 255)
                                    return bgc

                                elif(i == len(thres)-1):
##                                    print('this is the current length: ', length-1)
##                                    print('this is the index row: ',index.row())
##                                    print("Green")
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(92, 225, 102, 255)
                                    return bgc
                                elif(indexVal >= self.minD + thres[i] and indexVal <= self.minD + thres[i+1]):


                                    bgc = QtGui.QColor()
                                    bgc.setHsl(i, 225, 102,255)
                                    return bgc
                try:
                    colSY = self.getColumnNumber('Start\nYear')
                    colPS = self.getColumnNumber('Period\nStart') # Period Start
                    colPE = self.getColumnNumber('Period\nEnd') # Period End
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
                    nm = now.month
                    nd = now.day

                    valAcctID = self._df.iloc[index.row(),self.getColumnNumber('Account ID')] # we get the index of the account ID column and then get the val
                    market = str(valAcctID).split('_')[0]

                    if market == 'NEPOOL' or market == 'PJM' or market == 'MISO':
                        py = dt.datetime(int(ny), 6, 1)
                    elif market == 'NYISO':
                        py = dt.datetime(int(ny), 5, 1)

                    if now >= py:
                        planYear = ny
                    elif now < py:
                        planYear = ny-1

                    valSY = self._df.iloc[index.row(), colSY] # Start Year

                    if (int(valSY) == planYear):
                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#219897")
                        return bgc

                try:
                    colDF = self.getColumnNumber('YOY\nDelta')
                    length = len(self._df.index) # Get # of rows

                except:

                    pass
                else:

                    if index.column() == colDF:

                        dist = abs(self.minD - self.maxD)
#                        print('max: ',self.maxD)
#                        print('min: ',self.minD)
                        thres = [0]*92
                        for i in range(len(thres)):
                            if i == 0:
                                thres[i] = 0
                            else:
                                thres[i] = thres[i-1] + dist/91
                        indexVal = (str(self._df.iloc[index.row(),index.column()]).replace(',',''))
                        indexVal = float(indexVal.replace('%',''))
                        if(index.row() != length-1):
                            deltaset = self._df['YOY\nDelta'].str.replace(',','')
                            avg = deltaset.str.replace('%','').astype(float).mean()
                            for i in range(len(thres)):

                                if(avg == 0):
                                    bgc = QtGui.QColor()
                                    bgc.setNamedColor("#061e26")
                                    return bgc
#                                elif(indexVal >= 100):
                                elif(indexVal == np.nan or indexVal == 'nan%' or indexVal == 'nan' or indexVal == None or indexVal == 'None'):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(0, 225, 102, 255)
                                    return bgc
                                elif(indexVal >= 100):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(92, 225, 102, 255)
                                    return bgc
                                elif(indexVal <= -100):
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(0, 225, 102, 255)
                                    return bgc

                                elif(i == len(thres)-1):
##                                    print('this is the current length: ', length-1)
##                                    print('this is the index row: ',index.row())
##                                    print("Green")
                                    bgc = QtGui.QColor()
                                    bgc.setHsl(92, 225, 102, 255)
                                    return bgc
                                elif(indexVal >= self.minD + thres[i] and indexVal <= self.minD + thres[i+1]):


                                    bgc = QtGui.QColor()
                                    bgc.setHsl(i, 225, 102,255)
                                    return bgc
                        elif(index.row() == length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#219897")
                            return bgc
                    else:
                        if(index.row() == length-1 ):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#219897")
                            return bgc

                # CAPTAG TABLE AND PREVIOUS STRIP
                try:
                    colDF = self.getColumnNumber(self.prevStrip)
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF and self.ifTrue == True:
                        if(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#505F69")
                            return bgc
                # TRANSTAG TABLE AND CURRENT T STRIP
                try:
                    colDF = self.getColumnNumber(self.curStrip)
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF and self.ifTrue == True :
                        if(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#505F69")
                            return bgc
                # TRANSTAG TABLE AND PREVIOUS T STRIP
                try:
                    colDF = self.getColumnNumber(self.prevTStrip)
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF and self.ifTrue == True :
                        if(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#505F69")
                            return bgc
                # CAPTAG TABLE AND NEXT STRIP
                try:
                    colDF = self.getColumnNumber(self.nextStrip)
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF and self.ifTrue == True :
                        if(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#505F69")
                            return bgc

                # ------------------------------------------------------------------------
                if index.column() ==3:
                    if str(self._df.iloc[index.row(),index.column()]) == 'Total':

                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#219897")
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
                            bgc.setNamedColor("#219897")
                            return bgc

                try:
                    colDF = self.getColumnNumber('SCA\nTotal')
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(self._df.iloc[index.row(),colDF] == None or self._df.iloc[index.row(),colDF] == "None"):
                            return
                        indexVal = float((self._df.iloc[index.row(),index.column()]).replace(',',''))
                        if indexVal == np.nan or np.isnan(indexVal):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor('#a02432')
                            return bgc

                try:
                    colDF = self.getColumnNumber('Day\nCount')
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(self._df.iloc[index.row(),colDF] == None or self._df.iloc[index.row(),colDF] == "None"):
                            return
                        indexVal = float((self._df.iloc[index.row(),index.column()]).replace(',',''))
                        if indexVal == np.nan or np.isnan(indexVal):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor('#a02432')
                            return bgc
                # ------------------------------------------------------------------------
                try:
                    colDF = self.getColumnNumber('Delta\nDay\nCount')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if str(self._df.iloc[index.row(),index.column()-2]) == 'Total':
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#219897")
                            return bgc
                # ------------------------------------------------------------------------
                try:
                    colDF = self.getColumnNumber('Peak\nValue')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if str(self._df.iloc[index.row(),index.column()-2]) == 'Total':
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#219897")
                            return bgc
                    elif index.column() -1 == colDF:
                        if str(self._df.iloc[index.row(),index.column()-3]) == 'Total':
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#219897")
                            return bgc

                # THIS WILL HIGHLIGHT RED THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 10% OR IF NONE/EMPTY
                try:
                    colDF = self.getColumnNumber('Forecasted\nPeak kW to\n CapTag Var')
                    colCurrentStripPeak = self.getColumnNumber('Forecasted\nPeak kW') # We get the index of the current strip column
                    colCurCT = self.getColumnNumber(self.nextStrip)
                except:
                    pass
                else:
                    if index.column() == colDF:
                        valCCT = self._df.iloc[index.row(),colCurCT]
                        val = self._df.iloc[index.row(),colDF]
                        peakVal = self._df.iloc[index.row(),colCurrentStripPeak]

                        try:
                            valCCT = (valCCT.replace(',',''))
                            valCCT = float(valCCT.replace('%',''))
#                            print(valCCT)
                            peakVal  = (peakVal.replace(',',''))
                            peakVal = float(peakVal.replace('%',''))

                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc
                        else:
                            #cct = current capacity tag
#                            if (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None') and (valCCT == 0):
#                                if(valCCT == 0) and (peakVal > 0):

#                                return bgc
                            if (peakVal <= 100 and (valF >= 10.0 or valF <= -10.0)) or (peakVal <= 100 and (valCCT == 0 and peakVal > 0) and (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None')):

                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e39d1c')
                                return bgc
                            elif ((peakVal > 100 and peakVal <= 500) and (valF >= 10.0 or valF <= -10.0)) or ((peakVal > 100 and peakVal <= 500) and (valCCT == 0 and peakVal > 0) and (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None')):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e17614')
                                return bgc
                            elif ((peakVal > 500 and peakVal <= 1000) and (valF >= 10.0 or valF <= -10.0)) or ((peakVal > 500 and peakVal <= 1000) and (valCCT == 0 and peakVal > 0) and (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None')):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#d5432a')
                                return bgc
                            elif ((peakVal > 1000) and (valF >= 10.0 or valF <= -10.0)) or ((peakVal > 1000) and (valCCT == 0 and peakVal > 0) and (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None')):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#a02432')
                                return bgc

                try:
                    colDF = self.getColumnNumber('TransTag\nto Peak\nkW Var')
                    colCurrentStrip = self.getColumnNumber('Forecasted\nPeak kW') # We get the index of the current strip column
                except:
                    pass
                else:
                    if index.column() == colDF:

                        val = self._df.iloc[index.row(),colDF]
                        tagVal = self._df.iloc[index.row(),colCurrentStrip]

                        try:


                            tagVal = (tagVal.replace(',',''))
                            tagVal = float(tagVal.replace('%',''))

                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))


                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc
                        else:
                            if val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None':
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc
                            elif tagVal <= 100 and (valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e39d1c')
                                return bgc
                            elif (tagVal > 100 and tagVal <= 500) and (valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e17614')
                                return bgc
                            elif (tagVal > 500 and tagVal <= 1000) and (valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#d5432a')
                                return bgc
                            elif (tagVal > 1000) and (valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#a02432')
                                return bgc


                # ---------------------------------------------------------------------------
                """ This will highlight a cell red in the Loss Class column if it contains 
                a meter with a high voltage description """
                try:
                    colDF = self.getColumnNumber('Loss Class')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        val = self._df.iloc[index.row(),colDF]
                        ifHighV = False
                        if "PRIMARYHV" in val or "primaryhv" in val:
                            ifHighV = True
                        else:
                            ifHighV = False
                        if(ifHighV):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#a02432")
                            return bgc


                try:
                    colSP = self.getColumnNumber('Summer\nPeak kW')
                    colDF = self.getColumnNumber('Summer\nPeak kW to\nCapTag Var')
                    colCurrentStrip = self.getColumnNumber('Forecasted\nPeak kW') # We get the index of the current strip column
                    colST = self.getColumnNumber('SCA\nTotal') # We get the index of the SCA Total
                except:
                    pass
                else:
                    if index.column() == colDF:

                        valSP = self._df.iloc[index.row(),colSP]
                        val = self._df.iloc[index.row(),colDF]
                        tagVal = self._df.iloc[index.row(),colCurrentStrip]
                        valST = self._df.iloc[index.row(),colST]

                        try:
                            valSP = (valSP.replace(',',''))
                            valSP = float(valSP.replace('%',''))  # value in the summer peak kW column at same row

                            valST = (valST.replace(',',''))
                            valST = float(valST.replace('%',''))
#                            print(valST)

                            tagVal = (tagVal.replace(',',''))
                            tagVal = float(tagVal.replace('%',''))

                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None') :
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
#                                print('test')
                                return bgc
                        else:
                            if (val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None') and (valSP == 0.00 or
                               valSP == 0 or valSP == 0.0 or valSP == np.nan or valSP == 'nan' or valSP == 'None' or valSP == None or np.isnan(valSP)) and (valST == 0 or valST == np.nan or valST == 'nan' or valST == None or np.isnan(valST)) :
#                                bgc = QtGui.QColor()
#                                bgc.setNamedColor("#a02432")
#                                print('test',' valST = ', valST)
                                return
                            elif (valSP == 0.00 or valSP == 0 or valSP == 0.0 or valSP == np.nan or valSP == 'nan' or valSP == 'None' or valSP == None or np.isnan(valSP)) and (valF == -100.0 or valF == -100):
                                return

                            elif tagVal <= 100 and (valF >= 10.0 or valF <= -10.0):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e39d1c')
                                return bgc
                            elif (tagVal > 100 and tagVal <= 500) and (valF >= 10.0 or valF <= -10.0):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e17614')
                                return bgc
                            elif (tagVal > 500 and tagVal <= 1000) and (valF >= 10.0 or valF <= -10.0):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#d5432a')
                                return bgc
                            elif (tagVal > 1000) and (valF >= 10.0 or valF <= -10.0):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#a02432')
                                return bgc
                try:
                    colDF = self.getColumnNumber('Forecasted\nAnnual to\nSCA Var')
                    colCurrentStrip = self.getColumnNumber('Forecasted\nPeak kW') # We get the index of the current strip column
                except:
                    pass
                else:
                    if index.column() == colDF:

                        val = self._df.iloc[index.row(),colDF]
                        tagVal = self._df.iloc[index.row(),colCurrentStrip]

                        try:
                            tagVal = (tagVal.replace(',',''))
                            tagVal = float(tagVal.replace('%',''))

                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc
                        else:
                            if val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None':
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc
                            elif tagVal <= 100 and (valF >= 5.0 or valF <= -5.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e39d1c')
                                return bgc
                            elif (tagVal > 100 and tagVal <= 500) and (valF >= 5.0 or valF <= -5.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#e17614')
                                return bgc
                            elif (tagVal > 500 and tagVal <= 1000) and (valF >= 5.0 or valF <= -5.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#d5432a')
                                return bgc
                            elif (tagVal > 1000) and (valF >= 5.0 or valF <= -5.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                bgc = QtGui.QColor()
                                bgc.setNamedColor('#a02432')
                                return bgc
                try:

                    colDF = self.getColumnNumber('Ch1\nTimestamp')

                except:

                    pass
                else:

                        if index.column() == colDF:
                            timestamps = pd.to_datetime(self._df['Ch1\nTimestamp'])
                            maxDate = timestamps.max()
                            threeMonths = maxDate - relativedelta(months = 3)
                            sixMonths = maxDate - relativedelta(months = 6)
                            currentRowDate = timestamps.iloc[index.row()]

                            # print(currentDate)
                            if currentRowDate < threeMonths and currentRowDate >= sixMonths:
                                # print("orange")
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#d5432a")
                                return bgc
                            elif currentRowDate < sixMonths:
                                # print("red")
                                bgc = QtGui.QColor()
                                bgc.setNamedColor("#a02432")
                                return bgc

                try:
                    colDF = self.getColumnNumber('Ch3\nTimestamp')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        timestamps = pd.to_datetime(self._df['Ch3\nTimestamp'])
                        maxDate = timestamps.max()
                        threeMonths = maxDate - relativedelta(months=3)
                        sixMonths = maxDate - relativedelta(months=6)
                        currentRowDate = timestamps.iloc[index.row()]

                        # print(currentDate)
                        if currentRowDate < threeMonths and currentRowDate >= sixMonths:
                            # print("orange")
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#d5432a")
                            return bgc
                        elif currentRowDate < sixMonths:
                            # print("red")
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#a02432")
                            return bgc

                # HIGHLIGHT ENTIRE ROW PINK OF IF FORECASTED ANNUAL kWh is 0 or SCA total/m is 0 33,615,826.18
                try:
                    colDF = self.getColumnNumber('Forecasted\nAnnual kWh')
                    colDF2 = self.getColumnNumber('SCA\nTotal')
                    colCurrentStrip = self.getColumnNumber('Forecasted\nPeak kW') # We get the index of the current strip column
                    length = len(self._df.index)
                except:
                    pass
                else:

                    tagVal = self._df.iloc[index.row(),colCurrentStrip]
                    valSCA = self._df.iloc[index.row(),colCurrentStrip]


                    try:
                        tagVal = (tagVal.replace(',',''))
                        tagVal = float(tagVal.replace('%',''))

                        valSCA = (valSCA.replace(',',''))
                        valSCA = float(valSCA.replace('%',''))

                    except:
                        pass
                    else:

                        indexVal = float((self._df.iloc[index.row(),colDF]).replace(',',''))
                        if(self._df.iloc[index.row(),colDF2] == None or self._df.iloc[index.row(),colDF2] == "None"):
                            return
#                        indexVal2 = float((self._df.iloc[index.row(),colDF2]))
                        if (indexVal == 0 or valSCA == 0): #SCA\NTOTAL == 0 pink
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#b649a4")
                            return bgc
                        elif(indexVal == np.nan or np.isnan(indexVal) or indexVal == None):
                            return

                # ---------------------------------------------------------------------------
                """ This will highlight a row purple if it contains 
                a CapTag == 0 and it is not a lighting account """
                try:
                    colDF = self.getColumnNumber('Profile\nCode')
                    tagCol = self.getColumnNumber(self.nextStrip)
                    detYOYVer = self.getColumnNumber('Forecasted\nPeak kW') # make sure we are in the correct table

                except:
                    pass
                else:

                    val = str(self._df.iloc[index.row(),colDF])
                    tagVal = self._df.iloc[index.row(),tagCol]

                    tagVal = (tagVal.replace(',',''))
                    tagVal = float(tagVal.replace('%',''))


                    if((tagVal == 0 or tagVal == 0.00) and not (('LITE' in val) or ('ROLA' in val) or ('TL' in val) or ( 'SL' in val) or
                       ('OL' in val) or ('Lighting' in val) or ('LIGHTING' in val) or ('Deemed' in val) or ('DEEMED' in val) or ('S00' in val))):

                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#7c3dc2")
                        return bgc

                # This will highlight the previous year red in Capacity Tags table if
                # the current year tag and the previous year tag are equivalent
                try:
                    colDF = self.getColumnNumber('Planning Year')
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
                    nm = now.month
                    nd = now.day
#                    print(str(ny))
                    firstMonth = str(self._df.iloc[index.row(),colDF].split()[0])
                    toNum = {name: num for num, name in enumerate(calendar.month_name) if num}
                    firstMonth = toNum[firstMonth]
                    firstYear = str(self._df.iloc[index.row(),colDF].split()[1])
                    secondMonth = str(self._df.iloc[index.row(),colDF].split()[3])
                    secondMonth = toNum[secondMonth]
                    secondYear = str(self._df.iloc[index.row(),colDF].split()[4])
                    try:
                        firstDate = dt.datetime(int(firstYear),int(firstMonth),1)
                        secondDate = dt.datetime(int(secondYear),int(secondMonth),1)
                        now = dt.datetime(int(ny),int(nm),int(nd))
                    except:
#                        print('ERROR: ', secondMonth, secondYear)
                        pass

                    if((now >= firstDate) & (now < secondDate)):
                        if(self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()+1, colDF+1]):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#a02432")
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
                    ny = int(now.year)
                    nm = now.month
                    nd = now.day
#                    print(str(ny))
                    firstMonth = str(self._df.iloc[index.row(),colDF].split()[0])
                    toNum = {name: num for num, name in enumerate(calendar.month_name) if num}
                    firstMonth = toNum[firstMonth]
                    firstYear = str(self._df.iloc[index.row(),colDF].split()[1])
                    secondMonth = str(self._df.iloc[index.row(),colDF].split()[3])
                    secondMonth = toNum[secondMonth]
                    secondYear = str(self._df.iloc[index.row(),colDF].split()[4])
#                    print(int(firstMonth),'   ',int(firstYear))
                    try:
                        firstDate = dt.datetime(int(firstYear),int(firstMonth),1)
                        secondDate = dt.datetime(int(secondYear),int(secondMonth),1)
                        now = dt.datetime(int(ny),int(nm),int(nd))
                    except:
#                        print('ERROR: ', secondMonth, secondYear)
                        pass
#                    print(secondDate)
                    # 
                    if((now >= firstDate) & (now < secondDate)) & (self._df.iloc[index.row(),colDF +1] == self._df.iloc[index.row()-1, colDF+1]) :
                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#a02432")
                        return bgc
                    elif((now >= firstDate) & (now < secondDate)):
#                        print("PRESENT YEAR FOUND!")
                        bgc = QtGui.QColor()
                        bgc.setNamedColor("#219897")
                        return bgc

                # ------------------------------------------------------------------------
            elif role == Qt.TextColorRole:
                
                
                try:
                    colDF = self.getColumnNumber('YOY\nDelta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        deltaset = self._df['YOY\nDelta'].str.replace(',','')
                        avg = deltaset.str.replace('%','').astype(float).mean()
                        if(avg == 0):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor('#FFFFFF')
                            return bgc
                        elif(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#000000")
                            return bgc
                        
                try:
                    colDF = self.getColumnNumber('TransTag\nYOY Delta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        deltaset = self._df['TransTag\nYOY Delta'].str.replace(',','')
                        avg = deltaset.str.replace('%','').astype(float).mean()
                        if(avg == 0):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor('#FFFFFF')
                            return bgc
                        elif(index.row() != length-1):
                            bgc = QtGui.QColor()
                            bgc.setNamedColor("#000000")
                            return bgc
                
                
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            
            # ---------------------------------------------------------------------------------------------
            
            elif role == Qt.FontRole:

                try:
                    colSY = self.getColumnNumber('Start\nYear')
                    colPS = self.getColumnNumber('Period\nStart') # Period Start
                    colPE = self.getColumnNumber('Period\nEnd') # Period End
                except:
                    pass
                else:
                    now = dt.datetime.now()
                    ny = now.year - 1
                    nm = now.month
                    nd = now.day

                    valAcctID = self._df.iloc[index.row(),self.getColumnNumber('Account ID')] # we get the index of the account ID column and then get the val
                    market = str(valAcctID).split('_')[0]

                    if market == 'NEPOOL' or market == 'PJM' or market == 'MISO':
                        py = dt.datetime(int(ny), 6, 1)
                    elif market == 'NYISO':
                        py = dt.datetime(int(ny), 5, 1)

                    if now >= py:
                        planYear = ny
                    elif now < py:
                        planYear = ny-1

                    valSY = self._df.iloc[index.row(), colSY] # Start Year

                    if (int(valSY) == planYear):
                        font = QtGui.QFont()
                        font.setBold(True)
                        font.setPointSize(9)
                        return font

                try:
                    colDF = self.getColumnNumber('SCA\nTotal')
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(self._df.iloc[index.row(),colDF] == None or self._df.iloc[index.row(),colDF] == "None"):
                            return
                        indexVal = float((self._df.iloc[index.row(),index.column()]).replace(',',''))
                        if indexVal == np.nan or np.isnan(indexVal):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                
                try:
                    colDF = self.getColumnNumber('Day\nCount')
                    length = len(self._df.index) # Get # of rows
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(self._df.iloc[index.row(),colDF] == None or self._df.iloc[index.row(),colDF] == "None"):
                            return
                        indexVal = float(str(self._df.iloc[index.row(),index.column()]).replace(',',''))
                        if indexVal == np.nan or np.isnan(indexVal):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                
                try:
                    colDF = self.getColumnNumber(self.prevStrip)
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                        
                try:
                    colDF = self.getColumnNumber(self.nextStrip)
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                        
                try:
                    colDF = self.getColumnNumber(self.curStrip)
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                        
                try:
                    colDF = self.getColumnNumber(self.prevTStrip)
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font

                try:
                    colDF = self.getColumnNumber('Forecasted\nAnnual to\nSCA Var')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                        else:
                            if valF >= 5.0 or valF <= -5.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None':
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font

                # THIS WILL BOLD THE TEXT IN THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 5% OR IF NONE/EMPTY  
                try:
                    colDF = self.getColumnNumber('Summer\nPeak kW to\nCapTag Var')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
#                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
#                                font = QtGui.QFont()
#                                font.setBold(True)
#                                font.setPointSize(9)
#                                return font
                            return
                        else:
                            if valF >= 10.0 or valF <= -10.0:
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                            
                # THIS WILL BOLD THE TEXT IN THE CELLS IN THE % DIFFERENCE COLUMN IF VARIANCE IS >= 10% OR IF NONE/EMPTY  
                try:
                    colDF = self.getColumnNumber('TransTag\nto Peak\nkW Var')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                        else:
                            if valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None:
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                            
                try:
                    colDF = self.getColumnNumber('Forecasted\nPeak kW to\n CapTag Var')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        
                        val = self._df.iloc[index.row(),colDF]
                        try:   
                            valF = (val.replace(',',''))
                            valF = float(valF.replace('%',''))
                        except:
                            if(val == np.nan or val == 'nan%' or val == 'nan' or val == None or val == 'None'):
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                        else:
                            if valF >= 10.0 or valF <= -10.0 or val == np.nan or val == 'nan%' or val == 'nan' or val == None:
                                font = QtGui.QFont()
                                font.setBold(True)
                                font.setPointSize(9)
                                return font
                # ---------------------------------------------------------------------------
                """ This will highlight a cell red in the Loss Class column if it contains 
                a meter with a high voltage description """
                try:
                    colDF = self.getColumnNumber('Loss Class')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        val = self._df.iloc[index.row(),colDF]
                        ifHighV = False
                        ifHighV = self._df['Loss Class'].str.contains('PRIMARYHV').any()
                        if(ifHighV):
                            font = QtGui.QFont()
                            font.setBold(True)
                            font.setPointSize(9)
                            return font
                # ---------------------------------------------------------------------------

                try:
                    colDF = self.getColumnNumber('TransTag\nYOY Delta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont() 
                            font.setBold(True)
                            return font

                try:
                    colDF = self.getColumnNumber('YOY\nDelta')
                    length = len(self._df.index) # Get # of rows 
                except:
                    pass
                else:
                    if index.column() == colDF:
                        if(index.row() != length-1):
                            font = QtGui.QFont() 
                            font.setBold(True)
                            return font
                        elif(index.row() == length-1 ):
                            font = QtGui.QFont() 
                            font.setBold(True)
                            return font
                            
                    elif(index.row() == length-1 ):
                        font = QtGui.QFont() 
                        font.setBold(True)
                        return font

                # This will bold out a cell if the time stamp in either the ch1 or ch3 timestamp columns are  older than 3 or six months
                # try:
                try:

                    colDF = self.getColumnNumber('Ch1\nTimestamp')

                except:

                    pass
                else:

                        if index.column() == colDF:
                            timestamps = pd.to_datetime(self._df['Ch1\nTimestamp'])
                            maxDate = timestamps.max()
                            threeMonths = maxDate - relativedelta(months = 3)
                            sixMonths = maxDate - relativedelta(months = 6)
                            currentRowDate = timestamps.iloc[index.row()]

                            # print(currentDate)
                            if currentRowDate < threeMonths and currentRowDate >= sixMonths:
                                # print("orange")
                                font = QtGui.QFont()
                                font.setBold(True)
                                return font
                            elif currentRowDate < sixMonths:
                                # print("red")
                                font = QtGui.QFont()
                                font.setBold(True)
                                return font

                try:
                    colDF = self.getColumnNumber('Ch3\nTimestamp')
                except:
                    pass
                else:
                    if index.column() == colDF:
                        timestamps = pd.to_datetime(self._df['Ch3\nTimestamp'])
                        maxDate = timestamps.max()
                        threeMonths = maxDate - relativedelta(months=3)
                        sixMonths = maxDate - relativedelta(months=6)
                        currentRowDate = timestamps.iloc[index.row()]

                        # print(currentDate)
                        if currentRowDate < threeMonths and currentRowDate >= sixMonths:
                            # print("orange")
                            font = QtGui.QFont()
                            font.setBold(True)
                            return font
                        elif currentRowDate < sixMonths:
                            # print("red")
                            font = QtGui.QFont()
                            font.setBold(True)
                            return font
                # ------------------------------------------------------------------------
                try:
                    colDF = self.getColumnNumber('Delta\nDay\nCount')                     
                except:
                    pass
                else:
                    
                    if str(self._df.iloc[index.row(),index.column()]) == 'Total' or str(
                            self._df.iloc[index.row(),index.column()-1]) == 'Total' or str(
                                    self._df.iloc[index.row(),index.column()-2]) == 'Total' or str(
                                            self._df.iloc[index.row(),index.column()-3]) == 'Total':
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
                    nm = now.month
                    nd = now.day
#                    print(str(ny))
                    firstMonth = str(self._df.iloc[index.row(),colDF].split()[0])
                    toNum = {name: num for num, name in enumerate(calendar.month_name) if num}
                    firstMonth = toNum[firstMonth]
                    firstYear = str(self._df.iloc[index.row(),colDF].split()[1])
                    secondMonth = str(self._df.iloc[index.row(),colDF].split()[3])
                    secondMonth = toNum[secondMonth]
                    secondYear = str(self._df.iloc[index.row(),colDF].split()[4])
                    try:
                        firstDate = dt.datetime(int(firstYear),int(firstMonth),1)
                        secondDate = dt.datetime(int(secondYear),int(secondMonth),1)
                        now = dt.datetime(int(ny),int(nm),int(nd))
                    except:
#                        print('ERROR: ', secondMonth, secondYear)
                        pass

                    if((now >= firstDate) & (now < secondDate)):
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
                    ny = int(now.year)
                    nm = now.month
                    nd = now.day
#                    print(str(ny))
                    firstMonth = str(self._df.iloc[index.row(),colDF].split()[0])
                    toNum = {name: num for num, name in enumerate(calendar.month_name) if num}
                    firstMonth = toNum[firstMonth]
                    firstYear = str(self._df.iloc[index.row(),colDF].split()[1])
                    secondMonth = str(self._df.iloc[index.row(),colDF].split()[3])
                    secondMonth = toNum[secondMonth]
                    secondYear = str(self._df.iloc[index.row(),colDF].split()[4])
#                    print(int(firstMonth),'   ',int(firstYear))
                    try:
                        firstDate = dt.datetime(int(firstYear),int(firstMonth),1)
                        secondDate = dt.datetime(int(secondYear),int(secondMonth),1)
                        now = dt.datetime(int(ny),int(nm),int(nd))
                    except:
#                        print('ERROR: ', secondMonth, secondYear)
                        pass
#                    print(secondDate)
                    # 
                    if((now >= firstDate) & (now < secondDate)):

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