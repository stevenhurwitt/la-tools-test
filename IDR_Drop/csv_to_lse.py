import datetime as dt
import pandas as pd
import numpy as np
import json
import math
import time
import os

import requests
import flask

base = 'C:\\Users\wb5888\Documents\IDR Data'
os.chdir(base)
print('changed directory: {}'.format(base))

file = 'CLP_51328633000_660162009_IDR_vert.csv'

data = pd.read_csv(file, header = None)
data.columns = ['t', 'v']
data['t'] = pd.to_datetime(data['t'])
data.set_index(['t'], inplace = True, drop = True)
data['v'] = pd.to_numeric(data['v'])
print('read data file: {}.'.format(file))

print(data.head())
print('...')
print(data.tail())
n = len(data.v)
master = []

for i, v in enumerate(data.v):

    if i == 0:
        new_line = []
        
        if i < 10:
            j = ''.join(['0', str(i)])
        else:
            j = i
            
        line = ''.join(['1000000', str(j), ','])
        new = str(v) + ',,,'
        new_line = ''.join([line, new])
        #print(new_line)
        
    
    if (i > 0 and i % 24 == 0):
        
        if i < 10:
            j = ''.join(['0', str(i)])
        else:
            j = i
            
        line = ''.join(['10000000', str(i), ','])
        new = ''.join([str(v), ',,,'])
        new_line = ''.join([line, new])
        #print(new_line)
        
    elif (i > 0 and i % 24 != 0):
        
        if i < 10:
            j = ''.join(['0', str(i)])
        else:
            j = i
            
        new = ''.join([str(v), ',,,'])
        new_line = ''.join([new_line, new])
        #print(new_line)


    if (n % 1000 == 0 and i > 0):
        print('done with {} of {}.'.format(i, n))
        

    master.append(new_line)

print(master)
