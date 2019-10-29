#!/usr/bin/env python
# coding: utf-8

# In[7]:


import os
import time
import logging
import pprint
logging.getLogger().setLevel(logging.INFO)
from energyworx_client.storage import read_file, to_csv
from energyworx_client.client import EWX
import unittest
from energyworx_public.domain import KeyValue, Tag, Channel, Datasource
from energyworx_public import enums
from energyworx_public.rule import AbstractRule, RuleResult, Detector
from energyworx_client.rule_importer import RuleImporter

namespace_id = 'na.engie.com'
ewx_client = EWX(namespace_id=namespace_id)
pp = pprint.PrettyPrinter(indent = 1)


# # 1. Getting familiar with the envrionment

# ## 1.1 available packages

# In[8]:


conda 


# In[9]:


get_ipython().system(' pip freeze')


# In[10]:


dir(energyworx_client.client)


# Note: energyworx-client==0.1

# ## 1.2 check Python version

# In[11]:


from platform import python_version
print(python_version())


# ## 1.3 Jupyter notebook useful keyboard shortcuts

# Editing mode (double click on the cell)
# - In Editing mode, to run a cell and move to the next cell ---> shift + enter 

# Command mode (esc or click on the left blank area of a cell) 
# - insert a cell above ---> a
# - insert a cell below ---> b
# - delete a cell ---> dd
# - undo delete ---> z

# # 2. Interact with csv files

# ## 2.1 Read a csv file with read_csv function

# In[12]:


df = read_csv('test-data.csv') 


# In[13]:


df.head(5)


# In[14]:


df.tail()


# Notice there are empty rows and columns that is not needed

# ## 2.2 Data cleaning basics

# ### 2.2.1 Select a subset of a dataframe

# In[15]:


needed_columns = df.columns[7:9] # Note that the index 8 is not included
needed_columns


# In[16]:


# Selecting a subset of the dataframe
df = df[needed_columns]


# ### 2.2.2 Handling missing data

# In[17]:


get_ipython().run_line_magic('pinfo', 'pd.DataFrame.dropna')


# In[18]:


# Technics to deal with NaNs 
df.dropna(inplace=True, how='any')


# #### Excercise: try to change arguements of the dropna and notice the difference in result

# In[19]:


# Check If there are still empty values
df.isnull().sum()


# ### 2.2.3 Statistics of the dataframe

# In[47]:


# For the columns with only float type, you can check for statistics
df.describe()


# In[48]:


# Why not all the columns are shown in the statistics table? Check for datatype of each column, Columns with mixed types are stored with the object dtype
df.dtypes


# ####  Try to convert datetime to datetime64 type

# In[49]:


pd.to_datetime(df['READING_DATETIME'], utc=True)


# Referenece for datetime format: http://strftime.org/

# In[12]:


df.dtypes


# ### 2.3 Dataframe slicing

# In[50]:


df.index = df['READING_DATETIME']
del df['READING_DATETIME']
df.index


# ### 2.4 Export to csv 

# df.to_csv('cleaned_dataframe') will fail because it's a pandas function, trying to write to your local disk and it's not allowed

# In[51]:


to_csv(df, 'cleaned_dataframe.csv')


# # 3. Get to know energyworx client

# ## 3.1 All available functions with EWX object

# ### Excersice: check how to use the function list_datasources and execute_query. For those functions, which parameters are required, which are optional?

# ## 3.2 Energyworx Client
# Initialize the Energyworx client and retrieve a list of datasources

# In[20]:


namespace_id = 'na.engie.com'
ewx_client = EWX(namespace_id=namespace_id)


# In[21]:


#dir(ewx_client)


# In[22]:


datasources = ewx_client.list_datasources(limit=10)
for datasource in datasources.get('datasources'):
    try:
        ch = datasource.get('channels')
        tags = datasource.get('tags')
        #pp.pprint(tags[0])
        print(datasource.get('id'))
        print(ch[0]['classifier'])
    
        print('-----------')
        
    except:
        pass


# In[23]:


#datasource.keys()


# In[60]:


PR = '1-IFF3XL'
pr_meters = ''.join(["SELECT datasource_id FROM tags, UNNEST (properties) props WHERE props.key = 'prnumber' AND props.value = '",PR, "'"])
ewx_client.execute_query(pr_meters)


# In[31]:


flow_id = """SELECT datasource_id, flow_id, flow_timestamp, channel_classifier_id, flow_type
FROM flow_metadata

WHERE STRUCT (datasource_id, flow_timestamp) IN
  (SELECT AS STRUCT datasource_id, MAX(flow_timestamp) AS flow_timestamp 
  FROM flow_metadata
  GROUP BY datasource_id)

AND datasource_id IN (
  SELECT datasource_id
  FROM tags, UNNEST(properties) as props
  WHERE tag = 'metadata'
  AND props.key = 'market'
  AND (props.value = 'NEPOOL' OR props.value = 'NYISO')
)

AND flow_timestamp > '2019-10-01T00:00:00 America/Chicago'
  
ORDER BY flow_timestamp DESC"""

datasource_id = ('NEPOOL_MECO_8760281014')
query = flow_id.format(datasource_id = datasource_id)
print flow_id
ewx_client.execute_query(query = flow_id, limit = 10)


# In[32]:


audit = "SELECT DISTINCT subs.subject, source, props.KEY, props.value, message, Cast (timestamp as DATETIME) as maxDate FROM audit_events, Unnest(subjects) as subs, Unnest(properties) as props WHERE severity = 'ERROR' and subs.subject_type = 'datasource' and subs.subject LIKE '%NEPOOL%' and message NOT LIKE '%Heartbeat cannot be calculated%' and props.KEY IN ('rule_function', 'step') and props.value NOT IN ('vee_postdeal_payload_response') ORDER BY maxdate DESC"
print audit


# In[33]:


result = ewx_client.execute_query(audit, limit = 100)
result


# In[64]:


type(result)


# ## 3.3 Raw data retrieval
# Here we are going to execute an EQL query to retrieve RAW data

# In[55]:


get_ipython().run_line_magic('pinfo', 'EWX.execute_query')


# In[39]:


raw_data_query = "SELECT timestamp, ARRAY[STRUCT(channel AS channel_classifier, value AS value)] AS raw FROM INGEST WHERE timestamp > '{start_timestamp}' AND timestamp <= '{end_timestamp}' AND datasource_id IN '{datasource_id}' AND channel_classifier_id IN '{channel_classifier_id}' GROUP BY timestamp, channel, value ORDER BY timestamp asc"
channel_classifier_id=('DELIVERY_IDR', 
                       'DELIVERY_SCALAR'
                      )
datasource_id=('NEPOOL_NRI_3480800014')
query = raw_data_query.format(datasource_id=datasource_id, channel_classifier_id=channel_classifier_id, start_timestamp='2019-10-09T00:00:00', end_timestamp='2019-10-31T17:00:00 ')
print query


# In[40]:


timeseries_df = ewx_client.execute_query(query, limit=9999)
timeseries_df.head(5)


# In[119]:


timeseries_df.tail(5)


# In[69]:


timeseries_df.to_csv('NEPOOL_CLP_51071606057_342913008.csv')


# ## 3.4 Retrieve flow data

# In[2]:


def get_flow(flow_id):
    flow_data_query = "SELECT  struct(timestamp, struct(flow_id, array[STRUCT(channel_classifier_id, value, ARRAY(SELECT AS STRUCT annotation, sequence_id, ARRAY_AGG(STRUCT(key, value))))] AS channel) AS flow) AS row     FROM flows      WHERE timestamp > '{start_timestamp}'     AND timestamp <= '{end_timestamp}'     AND flow_id IN ('{flow_id}')     GROUP BY timestamp, flow_id, channel_classifier_id, value     ORDER BY timestamp, flow_id desc"
    
    flow = flow_id
    query = flow_data_query.format(flow_id=flow, start_timestamp='2017-01-09T00:00:00', end_timestamp='2020-10-09T17:00:00')
    print query
    flow_df = ewx_client.execute_query(query, limit=999999)
    return(flow_df)


# In[12]:


flow_id = 'd3391f7488df40ab99bcb93ca9ded9a1'
flow_df = get_flow(flow_id)


# In[69]:


datasource = """SELECT DISTINCT subs.subject, source, props.KEY, props.value, message, Cast (timestamp as DATETIME) as maxDate
FROM audit_events, Unnest(subjects) as subs, Unnest(properties) as props
WHERE subs.subject_type = 'datasource'
and props.KEY in ('flow_id')
and props.value IN ('{flow_id}')
ORDER BY maxdate DESC"""
datasource.format(flow_id = flow_id)
ewx_client.execute_query(datasource, limit = 999)


# In[44]:


to_csv(flow_df, 'NEPOOL_MECO_8760281014_ch3.csv')


# ## 3.5 Example plotting function

# In[7]:


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
get_ipython().run_line_magic('matplotlib', 'inline')

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def scatter_flags(series, flags, ax):
    """ Adds dots to the plot that indicate flags.
    """
    flag_locations = series[flags.index]
    ax.scatter(flags.index, flag_locations, color='r', s=30)

def plot_channels(df, channels, chart_type='line', start=None, end=None, flags=None, flag_channel=None, title=None):
    """ Plots the selected channels of the dataframe.
    Args:
    df (dataframe)
    channels (list)
    chart_type (str): line or scatter
    start (str): example: '2017-01-09T16:00:00', if not provided, plot from the first index
    end (str) : example: '2018-10-09T17:00:00', if not provided, plot until the last index
    flags (pd.Series): a series of dict
    flag_channel (str): channel classifier that the annotation is put on
    title (str): title of the chart
    
    
    """
    if not start:
        start = min(df.index)
    if not end:
        end = max(df.index)
    fig, ax = plt.subplots(figsize=(30, 7))
    if chart_type == 'scatter':
        cmap = get_cmap(len(channels)+1)
        for index, channel in enumerate(channels):
            ax.scatter(df[start:end].index, df[channel], s=10, c=cmap(index), label=channel, edgecolors='none')
            ax.set_title(title if title else str(channels))
        ax.legend()
        ax.grid(True)
    else:
        df.loc[start:end, channels].plot(ax=ax, title=title if title else str(channels))
    if flags is not None:
        scatter_flags(df[flag_channel], flags, ax)
    plt.show()


# In[9]:


#plot_channels(flow_df, ["FORECAST"], chart_type='scatter', title='VEE_RESULT') # start='2017-01-09T16:00:00', end='2018-10-09T17:00:00'


# In[10]:


plot_channels(flow_df.dropna(subset=["FORECAST"]), ["FORECAST"], chart_type='line', title='VEE_RESULT') # start='2017-01-09T16:00:00', end='2018-10-09T17:00:00'


# In[13]:


plot_channels(flow_df, ['DELIVERY_SCALAR', 
                       'FORECAST',
                       'VEE_RESULT'], chart_type='line', start='2017-01-09T16:00:00', end='2020-10-09T17:00:00', title=flow_id)


# In[14]:


# A quick way to plot line graph
flow_df.plot()


# # 4. Run a pluggable rule on a datasource, example: ZeroReads

# ### tips: check documentations of an object to understand how to initiate a rule

# In[11]:


get_ipython().run_line_magic('pinfo', 'AbstractRule')


# In[148]:


get_ipython().run_line_magic('pinfo', 'Detector')


# In[149]:


get_ipython().run_line_magic('pinfo', 'RuleResult')


# In[10]:


get_ipython().run_line_magic('pinfo', 'RuleImporter.load_module')


# In[15]:


# Load the zero reads rule from the users rule_lib
zero_reads_class = RuleImporter().load_module("validation","zero_reads").ZeroReads


# In[16]:


zero_reads_class = RuleImporter().load_module("validation","zero_reads").ZeroReads
rule = zero_reads_class(dataframe=flow_df, source_column='VEE_RESULT', datasource=None)


# In[ ]:





# In[ ]:





# In[17]:


rule_result = rule.apply(margin=1000)


# In[18]:


rule_result.result.head()


# In[30]:


plot_channels(flow_df, ['FORECAST'], flags=rule_result.result, flag_channel='FORECAST', title="zero_reads_result")


# In[45]:


import energyworx_public.domain as domain
ds_dict = ewx_client.get_datasource('NEPOOL_MECO_8760281014')
ds = domain.Datasource.from_message(ds_dict)


# In[50]:


domain.Datasource.get_channel_by_classifier(ds, 'DELIVERY_SCALAR_HEARTBEAT')


# In[23]:


outlier_class = RuleImporter().load_module("validation", "scalar_usage_outliers_check").ScalarUsageOutliersCheck
rule = outlier_class(dataframe = flow_df, source_column='DELIVERY_SCALAR', datasource=ds)
rule_result = rule.apply(threshold_low = .8, threshold_high = 1.2)


# In[24]:


dip_spike_class = RuleImporter().load_module("validation", "periodicity_or_interval_dip_spike_outlier").PeriodicityOrIntervalDipSpikeOutlier
rule = dip_spike_class(dataframe = flow_df, source_column = 'DELIVERY_SCALAR', datasource = ds)
rule.apply(load_shape_type = 'day_seasonal')
rule.result.head()


# In[23]:


gauge_reads = RuleImporter().load_module("validation", "gauge_reads_outliers_check").GaugeReadsOutliersCheck
rule = gauge_reads(dataframe = flow_df, source_column = 'DELIVERY_SCALAR', datasource = ds)
rule.apply(threshold_low=0.75, threshold_high=1.25, days_delta=30)
rule.result.head()


# In[56]:


energy_sum = RuleImporter().load_module("validation", "energy_sum_check").EnergySumCheck
rule = energy_sum(dataframe = flow_df, source_column = 'DELIVERY_IDR', datasource = ds)
rule.apply('DELIVERY_IDR', threshold=20)
rule.result.head()


# In[230]:


pp.pprint(ds_dict)


# In[50]:


first = ds.channels.__getitem__(6)
hb = domain.Datasource.get_channel_by_classifier(ds, 'DELIVERY_SCALAR_HEARTBEAT')
print hb.flow_configuration_id()


# In[49]:


dir(domain.Datasource)


# In[220]:


dir(AbstractRule)


# In[215]:


scalar = domain.Datasource.get_channel_by_classifier(ds, channel_classifier = 'DELIVERY_SCALAR')
scalar.to_message()


# In[245]:


dir(domain.Channel)


# In[ ]:




