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
# # Convert EWX .json file to dataframe (or .csv)
#%% [markdown]
# ### To Do: 
# 1. calculate heartbeat (length b/t time intervals) for every pred. year
# 2. get length of yearly forecasts (to confirm hourly intervals)
#%% [markdown]
# ### Import libraries

#%%
get_ipython().run_line_magic('matplotlib', 'notebook')
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
import json
import os
os.getcwd()


#%%
filepath = 'C:\\Users\\wb5888\\Documents\\EWX'

def sortdir(filepath, num):
    os.chdir(filepath)
    files = np.array(os.listdir())
    time = []
    for file in files:
        sys_time = round(os.path.getmtime(filepath + "\\" + file))
        time.append(datetime.fromtimestamp(sys_time))

    time = np.array(time)
    lab = ['files']
    filedf = pd.DataFrame(files, columns = lab)

    filedf['time'] = time
    filedf = filedf.sort_values(by = 'time', axis = 0, ascending = False).reset_index(drop = True)

    print("files found in dir: ", filepath)
    print(filedf.head(num))
    return(filedf.head(num))

#%% [markdown]
# ### Find downloaded .json file

#%%
filedf = sortdir(filepath, 5)


#%%
files = filedf.files[[0]]
files

#%% [markdown]
# ### Parse .json, save time & forecast values to dataframe

#%%
for f in files:
    forecasts = json_parse_csv(f)

#forecasts2 = json_parse_csv(filedf.files[1])


#%%
def json_parse_csv(file):
    
    with open(file) as raw:
        print("loading json...")
        data = json.load(raw) #raw json file
        acct = data['account'] #get account data
        ch3 = acct['timeseriesdataidr'] #dictionary of acct attributes
        n = len(ch3)
        
        reads = ch3[0]['reads']
        master_df = pd.DataFrame.from_dict(reads)
        
        print('found ', n, 'reads, creating dataset.')
        
        filename = file.split('_')[1:]
        filename = '_'.join(filename)
        filename = filename.replace('.json', '.csv')
        
        reads = ch3[0]['reads']
        master_df = pd.DataFrame.from_dict(reads)
        
        print('found ', n, 'reads, creating dataset.')
        
        for i in range(1,n):
            reads = ch3[i]['reads']
            temp = pd.DataFrame.from_dict(reads)
            
            tempname = "_".join([filename.split('.')[0], 'year', str(i), '.csv'])
            #print('writing {}'.format(tempname))
            
            #temp.to_csv(tempname, header = True, index = False)
            master_df = pd.concat([master_df, temp]).reset_index(drop = True)
        
        print(master_df.head())
        print(master_df.tail())
        
    
        print("saving to dataframe...")
    
    print('writing file to csv')
    master_df.to_csv(filename, sep = ",", header = True, index = False)
    return(master_df)

#%% [markdown]
# ### Plot data

#%%
year = [int(string.split('-')[0]) for string in forecasts.t]
year_ind = [(date < 2020) for date in year]
forecasts.iloc[0:sum(year_ind),:] .plot(x = 't', y = 'v')


#%%
forecasts2.plot(x = 't', y = 'v', color = 'orange')


#%%
os.getcwd()
output = sortdir(filepath, 20)
file = output.files[1]
print('')
print('using file {}'.format(file))


#%%
with open(file) as raw:
        print("loading json...")
        data = json.load(raw) #raw json file
        acct = data['account'] #get account data
        ch3 = acct['timeseriesdataidr'] #dictionary of acct attributes
        n = len(ch3)
        
        filename = file.split('_')[1:]
        filename = '_'.join(filename)
        filename = filename.replace('.json', '.csv')
        
        reads = ch3[0]['reads']
        caps = pd.DataFrame.from_records(acct['captag'])
        caps.to_csv(''.join['CAP', filename])
        master_df = pd.DataFrame.from_dict(reads)
        
        print('found ', n, 'reads, creating dataset.')
        
        for i in range(1,n):
            reads = ch3[i]['reads']
            temp = pd.DataFrame.from_dict(reads)
            filename = "_".join([acct, 'year', str(i), '.json'])
            temp.to_csv(filename, header = True, index = False)
            master_df = pd.concat([master_df, temp]).reset_index(drop = True)
        
        print(master_df.head())
        print(master_df.tail())
        
    
        print("saving to dataframe...")
    
    mastername = filename.split('.')[0]
    mastername = '_'.join([filename, 'master.json'])

    print('writing file to csv')
    master_df.to_csv(filename, sep = ",", header = True, index = False)
    return(master_df)


#%%
for k, v in acct.items():
    print(k)
    print(len(v))


#%%
caps = pd.DataFrame.from_records(acct['captag'])


#%%
output.files[4]


#%%
file.split('_')[1:]


#%%



