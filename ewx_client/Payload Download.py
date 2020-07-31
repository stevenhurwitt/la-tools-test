#!/usr/bin/env python
# coding: utf-8

# ## Creating a Custom Flow Configuration with the Energyworx Client
# This sample notebook demonstrates how to create and delete a custom flowconfiguration, how to start a run with this flowconfiguration and poll it from our flow, and finally how to download the data. 

# In[1]:


import pandas as pd
import numpy as np
import json
import time
import math
import os
import sys
import matplotlib.pyplot as plt
from pprint import pprint
from energyworx_client.client import EWX
from energyworx_client import storage

namespace = 'na.engie.com'

api = EWX(namespace)


# ## Define Functions

# In[4]:


##searches for meter
#returns result, ingestion results, response results (df's)
def meter_search(tag):
    file_result = api.search_files(tags = tag)['items']
    file_df = pd.DataFrame(file_result)
    
    ingest = file_df[file_df.readOnly == True]
    response = file_df[file_df.readOnly == False]
    
    ingest.reset_index(drop = True, inplace = True)
    response.reset_index(drop = True, inplace = True)
    
    return(file_df, ingest, response)

##downloads response given blobkey
def download_response(blobkey):
    json_str = api.download_file(blob_key = blobkey)
    parse = json.loads(json_str)
    
    acct = parse['account']
    data = acct['timeseriesdataidr'][0]
    forecast = data['reads']
    
    ch3 = pd.DataFrame(forecast)
    ch3.columns = [str(c) for c in ch3.columns]
    ch3['t'] = pd.to_datetime(ch3['t'])
    ch3['v'] = pd.to_numeric(ch3['v'])
    
    return(ch3)

## downloads ingest give blobkey
def download_ingest(blobkey):
    json_str = api.download_file(blob_key = blobkey)
    parse = json.loads(json_str)
    
    acct = parse['account']
    data = acct['timeseriesdataidr'][0]
    ingest = data['reads']
    
    idr = pd.DataFrame(ingest)
    idr.columns = [str(c) for c in idr.columns]
    idr['t'] = pd.to_datetime(idr['t'])
    idr['v'] = pd.to_numeric(idr['v'])
    
    return(idr)

##parse json into csv
#loads raw and writes as name
def json_parse_csv(raw, name):
    
    #print "loading json..."
    data = json.loads(raw) #raw json file
    acct = data['account'] #get account data
    ch3 = acct['timeseriesdataidr'] #dictionary of acct attributes
    n = len(ch3)
        
    reads = ch3[0]['reads']
    
    caps = acct['captag']

    caps_df = pd.DataFrame(caps)
    caps_df['start'] = pd.to_datetime(caps_df['start'])
    caps_df['stop'] = pd.to_datetime(caps_df['stop'])
    caps_df.v = [float(val) for val in caps_df.v]
    rows = caps_df.shape[0]
    
    master_df = pd.DataFrame.from_dict(reads)
        
    #print 'found {} reads, creating dataset.'.format(n)
        
    filename = name.split('_')
    filename = '_'.join(filename)
    filename = filename.replace('.json', '.csv')
    meter = filename.split('.')[0]
    
    caps_df['meter'] = [meter]*rows
    
    #display(caps_df)
        
    for i in range(1,n):
        reads = ch3[i]['reads']
        temp = pd.DataFrame.from_dict(reads)
            
        tempname = "_".join([filename.split('.')[0], 'year', str(i), '.csv'])
        full_temp = os.path.join(write, tempname)
        #print 'writing {}'.format(tempname)
            
        storage.to_csv(temp, full_temp)
        master_df = pd.concat([master_df, temp]).reset_index(drop = True)
        
    master_df.v = [float(val) for val in master_df.v]
    master_df.t = pd.DatetimeIndex(pd.to_datetime(master_df.t))
    master_df.set_index("t", inplace = True, drop = True)
    #print(master_df.head())
    #print(master_df.tail())
        
    
    #print "saving to dataframe..."
    
    #print 'writing file to csv' 
    master_file = os.path.join(write, filename)
    storage.to_csv(master_df, master_file)
    return(master_df, caps_df)

##searches for meter filenames (meter)
#returns merged ch3 and cap tags
def grab_ch3(meter):
    
    #iterate thru meters in PR (in EWX)
    PR_data = pd.DataFrame()
    cap_tags = pd.DataFrame()
    
    try:
        file_result = api.search_files(filename = meter)['items']

        #pp.pprint(file_result)
        file_df = pd.DataFrame(file_result)
        file_sub = file_df[['filename', 'tags', 'blobKey', 'createdDatetime']]
        response = file_sub[[file_sub.createdDatetime == max(file_sub.createdDatetime)]]
        this_file = "_".join(response.filename[0].split('_')[1:])
        print(response)
            
        if not response.empty:
            
            print 'grabbing ch 3 for {}...'.format(this_file)

            json_file = api.download_file(blob_key = response.blobKey[0])
        
            print '...'
            ch3_output, tags = json_parse_csv(json_file, this_file)
            cap_tags = pd.concat([cap_tags, tags], axis = 0)
            
            ch3_output.columns = [uniq_meter[index]]
            print 'downloaded, merging w/ PR dataframe...'
            PR_data = pd.concat([PR_data, ch3_output], axis = 1)
            display(PR_data.head())
            print '...'
            display(PR_data.tail())
                
            
    except:
        print 'error, meter {}.'.format(meter)

    cap_tags.drop_duplicates(keep = 'first', inplace = True)
    return(PR_data, cap_tags)

##searches for meter with PR data, captag 
#outputs PR/captag data
def data_search(meter, PR_data, cap_tags):
    
    file_result = api.search_files(tags = meter)['items']
    
    file_df = pd.DataFrame(file_result)
    file_sub = file_df[['filename', 'tags', 'blobKey', 'createdDatetime']]
    file_sub = file_sub[['response' in tag for tag in file_sub.tags]]
    response = file_sub[[a == max(file_sub.createdDatetime) for a in file_sub.createdDatetime]]
    this_file = "_".join(response.filename[0].split('_')[1:])
    metername = this_file.split('.')[0]
            
    if not response.empty:
            
        print 'grabbing ch 3 for {}...'.format(this_file)

        json_file = api.download_file(blob_key = response.blobKey[0])
        
        #print '...'
        ch3_output, tags = json_parse_csv(json_file, this_file)
        cap_tags = pd.concat([cap_tags, tags], axis = 0)
            
        ch3_output.columns = [metername]
        print 'downloaded, merging w/ PR dataframe...'
        PR_data = pd.concat([PR_data, ch3_output], axis = 1)
        #print '...'
        
    else:
        print 'forcast not found for {}.'.format(meter)
        
    return(PR_data, cap_tags)

def single_query(query, lim, job, pg, result_data):
    
    if job and pg:
        meta_data  = api.execute_query(query, limit = lim, raw_result = True, job_id = job, page_token = pg) 
    
    else:
        meta_data  = api.execute_query(query, limit = lim, raw_result = True)
    
    try:
        pt = str(meta_data['pageToken']) #get page token
        tot = int(meta_data['metadata']['totalRows']) #get total rows
        job = str(meta_data['reference']['jobId']) #get job id
        
    except:
        print 'no page token needed.'
        pt = None
        job = None
        tot = None

    var_fields = [] #get var names

    for f in meta_data['metadata']['fields']:
        var_fields.append(str(f['field']))
        
    p = len(var_fields)
        
    for row in meta_data['rows']:
        try:
            final_row = []
            for r in row['f']:
                final_row.append(str(r['v']))
                
            result_data.append(final_row)
            
        except:
            print 'row error'
        
        
    return(result_data, tot, pt, job, var_fields)

def large_query(query, num):
    
    tot_start = time.time()
    result = []
    print 'starting query...'
    start = time.time()
    result, n, pt, job, var = single_query(query, num, None, None, result)
    end = time.time()
    m = len(result)
    i = 0
    elapse = round(end - start, 2)
    print 'done with {} out of {} rows in {} seconds.'.format(m, n, elapse)
    
    batch = int(math.ceil(n/num))
    print 'running {} more batches:'.format(batch)
    
    while i < batch and batch > 0:
        try:
            start = time.time()
            print 'running batch {}...'.format(i+1)
            
            result, n, pt, job, var = single_query(query, num, job, pt, result)
            batch = int(math.ceil(n/num))
            
            end = time.time()
            elapse = round(end - start, 2)
            m = len(result)
            
            print 'done with {} out of {} rows in {} seconds,'.format(m, n, elapse)
            i += 1
            print 'ran batch {} of {}.'.format(i, batch)
            
            if (n - m) < num:
                num = n - m
        
        except:
            print 'error (hopefully out of rows to query).'
            i += 1
    
    tot_end = time.time()
    print 'query finished in {} total seconds.'.format(round(tot_end-tot_start, 2))
    return(result, var)
    


# In[3]:


query = '''SELECT DISTINCT subs.subject, source, props.KEY, props.value, message, Cast (timestamp as DATETIME) as maxDate
FROM audit_events, Unnest(subjects) as subs, Unnest(properties) as props
WHERE severity = 'ERROR'
and subs.subject_type = 'datasource'
and subs.subject LIKE '%NEPOOL%'
and message NOT LIKE '%Heartbeat cannot be calculated%'
and props.KEY IN ('rule_function', 'step')
and props.value NOT IN ('vee_postdeal_payload_response')
ORDER BY maxdate DESC'''


# In[ ]:





# ## Get Accounts in PR

# Can change batch size in *large_query()* function

# In[5]:


PR = '1-J1W23H_5'
acct_query = ''.join(["SELECT datasource_id FROM tags, UNNEST (properties) props WHERE props.key = 'prnumber' AND props.value = '",PR, "'"])
print 'using query: {}'.format(acct_query)
pr_result, pr_var = single_query(acct_query, 100, None, None, [])
pr_result_df = pd.DataFrame(pr_result)
pr_result_df = pr_result_df[[0]]
pr_result_df.columns = ['meters']
pr_result_df = pr_result_df.drop_duplicates()


# In[15]:


PR = '1-J1W23H_5'
acct_query = ''.join(["SELECT datasource_id FROM tags, UNNEST (properties) props WHERE props.key = 'prnumber' AND props.value = '",PR, "'"])
print 'using query: {}'.format(acct_query)
api.execute_query(acct_query)


# In[7]:


meters = ['NYISO_NIMO_5478724109', 'NYISO_NIMO_8746912012', 'NYISO_NIMO_5335080106', 'NYISO_NIMO_3945100106', 'NYISO_NIMO_4626272100']
meters


# In[9]:


#files, ingest, response = meter_search(meters[0])


# In[10]:


rec_response = max(response.lastUpdatedDatetime)
rec_resp_blob = str(response.blobKey[response.lastUpdatedDatetime == rec_response][0])
response_file = api.download_file(blob_key = rec_resp_blob)


# In[20]:


pd.DataFrame(response_file['timeseriesdata'][0]['reads'])


# In[ ]:





# In[10]:


PR, caps = json_parse_csv(response_file, meters[0])


# In[13]:


#storage.to_csv(customer_list,'customer_list.csv')


# In[ ]:





# ### Loading an account
# City_Keyword1[i])
# When requesting datasources from the API, they can easily be searched on tags. In this case all datasources up to 10 with 'market=PJM' are queried.

# In[11]:


meters[1]


# In[12]:


query_str = ''.join(['id = ', str(meters[1])])
result, n, job, pg, var = single_query(query_str, 10, None, None, [])

result.head()


# Listing the runs from a specific datasource

# In[26]:


datasource_runs = api.run(meters[1])
for i in datasource_runs.get('items'):
    pprint(i['runId'])


# #### Loading a run

# In[8]:


#timeseries_df = api.get_run(run_id='827f412225ed40ceaac13ca2bfa332d5', 
#                            start_timestamp='2015-01-01T00:00:00.000000',
#                            end_timestamp='2017-01-01T00:00:00.000000')
#timeseries_df.head(5)

flow_query = " SELECT STRUCT(timestamp, STRUCT(flow_id, ARRAY[STRUCT(channel_classifier_id, value, "             "ARRAY(SELECT AS STRUCT annotation, sequence_id, ARRAY_AGG(STRUCT(key, value))))] AS channel) AS flow) AS row "             "FROM flows WHERE flow_id IN ({flow_ids}) "             "AND timestamp > '{start_timestamp}' AND timestamp <= '{end_timestamp}' "             "GROUP BY timestamp, flow_id, channel_classifier_id, value ORDER BY timestamp, flow_id"
        
timeseries_df = api.execute_query(flow_query.format( flow_ids='503900540a8948ed9a7aa5e975b16136', start_timestamp='2017-08-01T00:00:00', end_timestamp='2019-08-01T00:00:00')
, limit=50000000)
timeseries_df.tail()


# #### Visualizing the raw data
# Pick a run, each of them has a column 'DELIVERY_IDR', which is the raw data that we need.

# In[ ]:


timeseries_df = pd.DataFrame(timeseries_df.loc[:, 'DELIVERY_IDR'].dropna())

f, ax = plt.subplots(1, figsize=(40,10))
timeseries_df.plot(ax=ax, legend='best');


# #### Creating a runconfiguration
# Apply rules in sequences on the raw data. A runconfiguration is a list of sequences that contain rules. The rules in a sequence will then be applied in consecutive order. 
# 
# This part shows how to create a sequence, and how to set parameters/thresholds for a rule.

# In[ ]:


# first sequence
sequence_1 = {"name": "Cleansing",
             "description": "sequence 1",
             "ruleConfigs": [{"function": "fix2359",    # list of rules to be applied in this sequence
                        "type": "cleaning",
                        "displayName": "Fix time 23:59:59"},
                    {"function": "shift_start_to_end",
                        "type": "cleaning",
                        "displayName": "Shift start to end"},
                    {"function": "localize",
                        "type":"cleaning",
                        "displayName": "Localize"}]}

sequence_2 = {"name": "Validation",
             "description": "sequence 2",
             "destinationColumn": "MERGED",    # at end of sequence, results are merged in MERGED column         # sequence continues on results of previous sequence
             "ruleConfigs":[{"function":"zero_reads",
                               "type": "validation",
                               "displayName": "Check zero reads",
                               "params":[{"key": "margin",             # to adjust a threshold/parameter of a rule, otherwise default is used.
                                             "displayName": "Margin",
                                             "value": "0.01",          # for example, you might want to change zero reads to another value than 0.01.
                                             "valueType": "float"}]},
                            {"function": "anomaly_check",
                              "type": "validation",
                              "displayName": "Anomaly Detector"}]}

sequence_3 = {"name": "Informational",
             "description": "sequence 3",
             "destinationColumn": "MERGED",
             "sourceColumn": "MERGED",
             "ruleConfigs": [{"function":"holiday_check",
                                 "type":"validation",
                                 "displayName": "Check holidays"},
                             {"function":"check_dst",
                                 "type":"validation",
                                 "displayName": "Check DST"}]}

sequence_4 = {"name": "Forecasting",
             "description": "sequence 4",
             "destinationColumn": "MERGED",
             "sourceColumn": "MERGED",
             "ruleConfigs": [{"function": "forecast",
                                 "type": "estimation",
                                 "displayName": "Forecast",
                                 "params": [{"displayName": "Months forwards",
                                                "key": "months_forward",
                                                "value": "12",
                                                "valueType":"int"},
                                            {"displayName": "Reset month day",
                                                "key": "reset_month_day",
                                                "value": "6",
                                                "valueType": "int"},
                                            {"displayName": "Keep slope percentage",
                                                "key": "keep_slope_perc",
                                                "value": "100",
                                                "valueType": "int"},
                                            {"displayName": "From start of year",
                                                "key": "from_start_of_year",
                                                "value": "true",
                                                "valueType": "bool"}]}]}

flow_configuration = api.create_runconfig(name="SampleFlowConfiguration", description="Example for creating a flow configuration in a notebook", sequence_configs=[sequence_1, sequence_2, sequence_3, sequence_4])
pprint(flow_configuration)


# Starting the run and storing the run_id. It is important to set *persist* to *False*, because this will ensure the run is not saved, but waits to be polled.

# In[ ]:


flowId = str(flow_configuration.get('id'))
custom_run = api.start_run(datasource_identifiers=['PJM_UTILITY_00001'], runconfiguration_id=flowId, persist=False)
pprint(custom_run)


# #### Polling
# We need to wait for the run to go through all the flows, so wait for a bit before polling. Once we've succesfully polled the result, we can take a look at the data.

# In[ ]:


result_df = api.poll_run(custom_run.get('referenceId'))


# #### Results
# Now we've polled the resulting run, we can take a look at the results. There are 4 columns, the first is the original data, FORECAST contains the values of the rule 'forecast' that was applied, MERGED is the combination of FORECAST and DELIVERY_IDR (in this case)

# In[ ]:


result_df.head()


# In[ ]:


f, ax = plt.subplots(1, figsize=(40,10))
result_df.DELIVERY_IDR.plot(legend='best')
result_df.FORECAST.plot(alpha=0.6, legend='best')
plt.show();


# #### Saving the data to your directory
# With the following code you can save the dataframe to your own directory within datalab, after that you can easily download it so save it locally.

# In[ ]:


to_csv(result_df, "PJM_UTILITY_00001_{}.csv".format(custom_run.get('referenceId')))


# #### Deleting the Flow Configuration
# You might want to delete a flow configuration, for example, because it didn't yield what you wanted. This shows how you go about deleting it.

# In[6]:


namespace1 = 'public.energyworx.com'
api = EWX(namespace=namespace1)
raw_data = api.get_raw(datasource_id = 'KLGA',start_timestamp ='1900',end_timestamp = '2000')


# In[ ]:


deleted_flow_configuration = api.delete_runconfig(id=flowId)
pprint(deleted_flow_configuration)


# In[5]:


search_query


# In[ ]:




