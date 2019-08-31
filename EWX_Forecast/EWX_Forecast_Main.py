# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'EWX_Forecast'))
	print(os.getcwd())
except:
	pass
#%%
from IPython import get_ipython

#%% [markdown]
# # Forecast/Timeshift

#%%
get_ipython().run_line_magic('matplotlib', 'notebook')
import os
import pandas as pd
import EWX_forecast as ewx

basepath = "/home/jupyter-engiela/la-tools-test"
os.chdir(basepath)
json_files = os.path.join(basepath, 'json')
csv_files = os.path.join(basepath, 'csv')


print('working in {}'.format(basepath))


#%%
files = ewx.sortdir(csv_files, 5)


#%%
myfiles = files.files[[0]]
myfiles


#%%
for f in myfiles:
    ch3 = ewx.forecast_main(f, 10, csv_files, csv_files)


#%%
ch3[ch3.index.year < 2021].plot(y = 'v')
#ch3.plot(y = 'v')


#%%
for f in files.files[:2]:
    os.chdir(json_files)
    csv = ewx.parse_ewx(f)
    fname = "_".join(f.split('_')[1:])
    writename = fname.replace('.json', '.csv')
    os.chdir(csv_files)
    csv.to_csv(writename)


#%%
files = ewx.sortdir(csv_files, 20)


#%%
a = [len(a.split('_')) > 3 for a in files.files]

b = []
for fname in files.files:
    try:
        out = (fname.split('_')[3] == 'timeshift.csv')
        
    except:
        out = False
    
    b.append(out)
    
c = [a and b for a, b in zip(a, b)]


#%%
import datetime as dt

ts = files.files[c]
now = dt.datetime.today()

for fname in ts:
    tmp = pd.read_csv(fname, header = None)
    tmp.columns = ['t', 'v']
    tmp['t'] = pd.to_datetime(tmp['t'])
    index = [t < now for t in tmp.t]
    tmp2 = tmp[index]
    tmp2.to_csv(fname, header = None, index = None)
    print('wrote {} to disk.'.format(fname))


#%%



