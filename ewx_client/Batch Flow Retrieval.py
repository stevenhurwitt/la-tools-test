#!/usr/bin/env python
# coding: utf-8

# ## Retrieve EWX Flow ID

# In[8]:


import os
import time
import json
import logging
import pprint

import numpy as np
import pandas as pd
import datetime as dt
logging.getLogger().setLevel(logging.INFO)
import energyworx_client.storage as storage
from energyworx_client.client import EWX
import unittest
from energyworx_public.domain import KeyValue, Tag, Channel, Datasource
from energyworx_public import enums
from energyworx_public.rule import AbstractRule, RuleResult, Detector, PREPARE_DATASOURCE_IDS_KEY, HEARTBEAT_COLUMN_TEMPLATE
from energyworx_client.rule_importer import RuleImporter

import warnings
warnings.filterwarnings(action='ignore')

namespace_id = 'na.engie.com'
ewx_client = EWX(namespace_id=namespace_id)
pp = pprint.PrettyPrinter(indent = 1)


# In[ ]:





# # get_flow

# ### retrieves EWX flow data based on *flow_id*.

# In[2]:


def get_flow(flow_id):
    flow_data_query = "SELECT  struct(timestamp, struct(flow_id, array[STRUCT(channel_classifier_id, value, ARRAY(SELECT AS STRUCT annotation, sequence_id, ARRAY_AGG(STRUCT(key, value))))] AS channel) AS flow) AS row     FROM flows      WHERE timestamp > '{start_timestamp}'     AND timestamp <= '{end_timestamp}'     AND flow_id IN ('{flow_id}')     GROUP BY timestamp, flow_id, channel_classifier_id, value     ORDER BY timestamp, flow_id desc"
    
    flow = flow_id
    query = flow_data_query.format(flow_id=flow, start_timestamp='2017-01-09T00:00:00', end_timestamp='2020-10-09T17:00:00')
    flow_df = ewx_client.execute_query(query, limit=999999)

    print('downloaded flow df.')
    
    #forecast_yr = dt.datetime.strptime('01-01-2019 00:00:00', '%m-%d-%Y %H:%M:%S')
    return(flow_df)

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


# # flow_ids

# In[7]:


meter = 'NEPOOL_BECO_26701281052'
flow_id = 'ffa7c3e82139429095914b60e67cb0e8'
flow_df = get_flow(flow_id)


# In[10]:


plot_channels(flow_df.dropna(subset=["FORECAST"]), ["FORECAST"], chart_type='line', title='VEE_RESULT') # start='2017-01-09T16:00:00', end='2018-10-09T17:00:00'


# In[70]:


filename = ''.join([meter, '_ch3.csv'])
storage.to_csv(flow_df, filename)


# # Get 30 recent flows from .json

# In[ ]:


audit = storage.read_file('audit-errors-102319.csv')
audit.head()


# In[ ]:





# In[5]:


flow_list = '[{"datasource_id":"NEPOOL_PSNH_80059230112","flow_id":"a06d64a3865644f797317fbd32cf4f42","flow_timestamp":"10\\/21\\/2019 8:48","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_RGE_R01000051576205","flow_id":"dbe812da177c47db97d96672b76e5696","flow_timestamp":"10\\/21\\/2019 8:41","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_5983734144","flow_id":"4468b19c83ac4789b610b56958f8d249","flow_timestamp":"10\\/21\\/2019 8:38","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_80050140344","flow_id":"3d161345529b467f80a001ab13d675b6","flow_timestamp":"10\\/21\\/2019 8:33","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_80048130316","flow_id":"ebaff5cd44734544bbf90bd296f5ff04","flow_timestamp":"10\\/21\\/2019 8:30","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_80050140260","flow_id":"58277bfade8c4d459b092e68f39e73d9","flow_timestamp":"10\\/21\\/2019 8:29","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_80043880345","flow_id":"7379a2e7152a47aa8f83e707f81d99a0","flow_timestamp":"10\\/21\\/2019 8:24","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_CMBRDG_28520480014","flow_id":"49a8a3501f3d478d9ce835a87fef82f8","flow_timestamp":"10\\/21\\/2019 8:01","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_CMBRDG_11498170023","flow_id":"66a0e492d308425fa27b6a6a5c476e48","flow_timestamp":"10\\/21\\/2019 7:57","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_0083047009","flow_id":"93a78187b54c4a88a00895cca4567fed","flow_timestamp":"10\\/21\\/2019 7:37","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_1140634001","flow_id":"e71fd5559f3e457eb4d7ab6124bec661","flow_timestamp":"10\\/21\\/2019 7:37","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_9276464100","flow_id":"b5f6299cb2b14c3c90ca5fd4a79f2c6b","flow_timestamp":"10\\/21\\/2019 7:37","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_2892619100","flow_id":"301d829dcb5d408ba6f122a3ecbe9f72","flow_timestamp":"10\\/20\\/2019 8:19","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NYSEG_N01000006810873","flow_id":"769058aa483c4d31a750be87985b3d1d","flow_timestamp":"10\\/20\\/2019 8:19","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_4980412006","flow_id":"708b783f287f416898fe465e498602c4","flow_timestamp":"10\\/20\\/2019 8:17","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_RGE_R01000052419819","flow_id":"758e5bc5fbd74702b772581aab2666dc","flow_timestamp":"10\\/20\\/2019 8:17","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NYSEG_N01000004159943","flow_id":"87161ed9e1c44e6ebc120f450f19c51f","flow_timestamp":"10\\/20\\/2019 8:16","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_56697185056_818411008","flow_id":"aec4ce9effb040a0b9195320ddc2bbf5","flow_timestamp":"10\\/20\\/2019 8:16","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NYSEG_N01000015844863","flow_id":"9cafa97711754b8cb734a31b42d342db","flow_timestamp":"10\\/20\\/2019 8:16","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NYSEG_N01000000218941","flow_id":"0ba605d0fce9491991d7f38a541cac27","flow_timestamp":"10\\/20\\/2019 8:16","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_56222185019_200511000","flow_id":"f1c2a513d9394c748e66690c0d7eb1d3","flow_timestamp":"10\\/20\\/2019 8:15","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_56883285009_861511000","flow_id":"b465177ea16c425f937e0f58aaabffc8","flow_timestamp":"10\\/20\\/2019 8:15","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NIMO_9339534001","flow_id":"e66952afde5649aaab52a4780e7e273d","flow_timestamp":"10\\/20\\/2019 8:15","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_NYSEG_N01000005956776","flow_id":"c0b6764281e94256a4967ed94ddfec41","flow_timestamp":"10\\/20\\/2019 8:09","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_PSNH_56879121010_608190001","flow_id":"8bba33f87a574db1aabce47b18e11f4a","flow_timestamp":"10\\/20\\/2019 8:07","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_CENTHUD_8671050000","flow_id":"9c36351b62be4be7b49ef79e1f961398","flow_timestamp":"10\\/20\\/2019 8:07","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_CLP_51095395083_294081009","flow_id":"513f00710f7940c19187dfbbfd24f34d","flow_timestamp":"10\\/19\\/2019 11:05","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_ORU_5235106087","flow_id":"d3391f7488df40ab99bcb93ca9ded9a1","flow_timestamp":"10\\/19\\/2019 10:42","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NYISO_ORU_0060032037","flow_id":"dfeb5fbc32e8461d8632f634fb1ca2c7","flow_timestamp":"10\\/19\\/2019 10:42","channel_classifier_id":"FORECAST","flow_type":"scenario"},{"datasource_id":"NEPOOL_CMP_035014916890","flow_id":"3f371f049be345f4ba3e45d8c12bea39","flow_timestamp":"10\\/19\\/2019 6:40","channel_classifier_id":"FORECAST","flow_type":"scenario"}]'
flow_list = json.loads(flow_list)
flow_list = pd.DataFrame.from_records(flow_list)


# ## Batch thru flows

# In[6]:


for i, flow in enumerate(flow_list.flow_id):
    ds = flow_list.datasource_id[i]
    print('getting flow {} of {}, datasource: {}.'.format(i+1, len(flow_list.flow_id), flow_list.datasource_id[i]))
    flow_df = get_flow(flow)
    
    plot_channels(flow_df.dropna(subset=["FORECAST"]), ["FORECAST"], chart_type='line', title='VEE_RESULT') # start='2017-01-09T16:00:00', end='2018-10-09T17:00:00'


# In[ ]:


print(flow.head())
print('...')
print(flow.tail())


# ## Analyst classify - good or bad

# In[ ]:


flowclass = []
#flow_class.apend()


# In[ ]:





# # To Do

# classify as good or bad flows (scrape year data, all markets) - submodels

# In[ ]:





# In[ ]:





# ## Datasource

# In[ ]:


dir(Datasource.from_message)


# In[11]:


ds_dict = ewx_client.get_datasource(meter)
ds = Datasource.from_message(ds_dict)


# In[12]:


forecast_ch = ds.get_channel_by_classifier('FORECAST')
forecast_hb = ds.get_channel_by_classifier('FORECAST_HEARTBEAT')


# In[13]:


ch = ds.channels
ch_class = [c.classifier for c in ds.channels]
ch_class_dict = []
for i, chclass in enumerate(ch_class):
    
    ch_class_dict.append((chclass, ch[i]))
    
ch_class_dict = dict(ch_class_dict)
ch_class_dict


# In[44]:


ds.get_channel_by_classifier('DELIVERY_SCALAR')


# ## Flow Rules/Designs

# In[53]:


energy_sum_check = RuleImporter().load_module("validation","energy_sum_check").EnergySumCheck
rule = energy_sum_check(dataframe=flow_df, source_column='FORECAST', datasource=None)


# In[54]:


flow_df3 = pd.DataFrame(flow_df['VEE_RESULT'][:5])
flow_df3


# In[8]:


flow_df2 = pd.DataFrame(flow_df['FORECAST'][6:])
time_diff = flow_df2.index.to_series().diff()
time_diff = time_diff.dt.seconds
flow_df2['FORECAST_HEARTBEAT'] = time_diff


# In[9]:


flow_df2.head()


# In[10]:


gap_check = RuleImporter().load_module("validation","gap_check").GapCheck
rule = gap_check(dataframe=flow_df2, source_column='FORECAST', datasource=None)


# In[53]:


rule_result = rule.apply()


# In[34]:


class EnergySumCheck(AbstractRule):
    def prepare_context(self, channel_classifier, **kwargs):
        return {'prepare_datasource_ids': [self.datasource.id]}

    def apply(self, channel_classifier, threshold=20.0, **kwargs):
        """
        Places flags at the end of a period where the IDR sum is different from the scalar energy usage.
        The difference is calculated in percentages

        Rule checks based on  (if SUM(INTERVAL) <> SCALAR USAGE +/- "X"%)

        Args:
            channel_classifier (str): id of the channel
            threshold (float): error percentage --> allowed percentage 'off' the scalar value

        Returns:
            RuleResult: object with a flag column (result) and meta data (metadata)

        Raises:
            TypeError: If the threshold is not an integer

            ValueError: If threshold is a negative number or higher than 100
        """
        import pandas as pd
        import numpy as np

        if not isinstance(threshold, int) and not isinstance(threshold, float) or np.isnan(threshold):
            raise TypeError("inappropriate type for threshold: {threshold_type}".format(threshold_type=type(threshold)))
        elif threshold < 0 or threshold > 100:
            raise ValueError("inappropriate value for threshold {threshold}".format(threshold=threshold))

        if channel_classifier is None:
            raise ValueError("No channel classifier entered")

        first_idr_date = self.dataframe.index[0]
        last_idr_date = self.dataframe.index[-1]

        # Get the other channel based on the channel_classifier
        # from the datasource between the first and last idr dates
        scalar_df = self.load_side_input(datasource_id=self.datasource.id, channel_id=channel_classifier,
                                         start=first_idr_date, end=last_idr_date)

        # Only search for the heartbeat if a data frame is found
        if scalar_df is not None and not scalar_df.empty:
            # rename the data channel to channel_classifier
            scalar_df.rename(columns={scalar_df.columns[0]: channel_classifier}, inplace=True)
            scalar_df[HEARTBEAT_COLUMN_TEMPLATE.format(channel_classifier)] = self.load_side_input(
                datasource_id=self.datasource.id,
                channel_id=HEARTBEAT_COLUMN_TEMPLATE.format(channel_classifier),
                start=first_idr_date, end=last_idr_date)

        if scalar_df is None or scalar_df.empty:
            logger.info("No data found for channel classifier {}".format(channel_classifier))
            return RuleResult(result=None)
        else:
            logger.info("Found {} scalar reads.".format(str(len(scalar_df))))

        df = self.dataframe[[self.source_column, self.source_heartbeat_column]].copy()
        flag_col = 'FLAG:energy_sum_check'
        df[flag_col] = np.nan

        scalar_heartbeat = scalar_df[HEARTBEAT_COLUMN_TEMPLATE.format(channel_classifier)]
        scalar_df['STOP'] = scalar_df.index
        scalar_df['HB_TIME'] = pd.to_timedelta(scalar_heartbeat, unit='s')
        scalar_df['START'] = scalar_df['STOP'].subtract(scalar_df['HB_TIME']).dt.tz_localize('UTC')

        # Get the sum of the idr values between each start - stop for rows in scalar_df
        scalar_df['IDR_SUM'] = map(lambda start, stop: df[self.source_column].loc[start: stop].sum(),
                                   scalar_df['START'], scalar_df['STOP'])

        first_idr_date = df.index[0]
        last_idr_date = df.index[-1]
        if last_idr_date < scalar_df['STOP'].index[0]:
            logger.warn(
                "Stopping validation energy_sum_check; the scalar values occur in the future compared to the idr values.")
            return RuleResult(result=df[flag_col])

        if scalar_df['START'][0] < first_idr_date:
            logger.warn("First idr date falls after start date scalar read; skipping this period.")
            return RuleResult(result=df[flag_col])

        # Calculate the percentage of difference between IDR_SUM and the scalar values
        scalar_df['percentage'] = (scalar_df['IDR_SUM'] - scalar_df[channel_classifier]) / scalar_df[channel_classifier] * 100

        flag_filter = ((scalar_df['percentage'] < -threshold) | (scalar_df['percentage'] > threshold)) & self.data_filter
        if not any(flag_filter):
            return RuleResult(result=df[flag_col])

        # Get the count of the idr values between each start - stop for rows in scalar_df
        scalar_df.loc[flag_filter, 'nr_idr_values'] = map(lambda start, stop:
                                                          df[self.source_column].loc[start: stop].count(),
                                                          scalar_df.loc[flag_filter, 'START'],
                                                          scalar_df.loc[flag_filter, 'STOP'])

        # Calculate expected amount of idr values based on timeframe / heartbeat
        scalar_df.loc[flag_filter, 'expected'] = map(lambda start, stop:
                                                     (stop - (start + (pd.to_timedelta(df[self.source_heartbeat_column].loc[start],unit='s')))).total_seconds() /
                                                     df[self.source_heartbeat_column].loc[stop] + 1,
                                                     scalar_df.loc[flag_filter, 'START'],
                                                     scalar_df.loc[flag_filter, 'STOP'])  # +1 since 'nr points' = 'nr intervals' + 1

        scalar_df.loc[flag_filter, 'missing_values'] = scalar_df.loc[flag_filter, 'expected'].subtract(
            scalar_df.loc[flag_filter, 'nr_idr_values'])

        # Flag each start where flag_filter = True
        for index, row in scalar_df.loc[flag_filter].iterrows():
            flag_date = df.loc[row['START']:row['STOP']].index[-1]  # find a valid date to put the annotation on
            df.loc[flag_date, 'idr_sum'] = row['IDR_SUM']
            df.loc[flag_date, 'scalar_read'] = row.loc[channel_classifier]
            df.loc[flag_date, 'start'] = str(row.loc['START'])
            df.loc[flag_date, 'stop'] = str(row.loc['STOP'])
            df.loc[flag_date, 'missing_values'] = row.loc['missing_values']
            df.loc[flag_date, flag_col] = dict(df.loc[[flag_date], ['idr_sum', 'scalar_read', 'start', 'stop', 'missing_values']].to_dict(
                orient='records')[0])  # TODO Once dicts are properly supported, the map function needs to be removed

        return RuleResult(result=df[flag_col])


# In[61]:


energy_sum_check = RuleImporter().load_module("validation","energy_sum_check").EnergySumCheck
rule = energy_sum_check(dataframe=flow_df2, source_column='FORECAST', datasource=ds)


# In[62]:


rule_result = rule.apply('FORECAST', margin = 20)


# In[67]:


flow_df2['FORECAST_HEARTBEAT'].diff(1)


# In[ ]:




