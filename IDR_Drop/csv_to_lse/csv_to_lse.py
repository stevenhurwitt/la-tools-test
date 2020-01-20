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
