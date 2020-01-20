import numpy as np
import pandas as pd
import datetime as dt
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import cx_Oracle
import time
import math
import os

''' wrappers for database connections to SQL databases '''
''' takes query & db as a string and returns a list of results '''

def OracleAPI(query, db):
    
    
    tppe = dict([('uid', 'tesi_interface'), ('pwd', 'peint88'), ('ip', '172.25.152.125'), ('port', '1700'), ('service_name', 'tppe.mytna.com')])
    
    lpss = dict([('uid', 'tesi_interface'), ('pwd', 'lpssint88'), ('ip', '172.25.152.12'), ('port', '1737'), ('service_name', 'tplpss.mytna.com')])
    
    tpint = dict([('uid', 'tesi_interface'), ('pwd', 'intint88'), ('ip', '172.25.152.12'), ('port', '1737'), ('service_name', 'tpint.mytna.com')])
    
    if db == 'tppe':
        auth = tppe
    
    elif db == 'lpss':
        auth = lpss
    
    elif db == 'tpint':
        auth = tpint
    
    else:
        print('database not recognized, try: tppe, lpss or tpint.')
        return(None)
    
    dsn = cx_Oracle.makedsn(auth['ip'], auth['port'], service_name=auth['service_name'])
    
    result_list = []
    con = cx_Oracle.connect(auth['uid'], auth['pwd'], auth['service_name'])
    cur = con.cursor()
    cur.execute(query)
    
    columns = [i[0] for i in cur.description]

    result_list = []
    
    for result in cur:
        result_list.append(result)
        i = len(result_list)
        if (i > 0 and i % 1000 == 0):
            print('done with {}.'.format(i))
    
    print('finished with {} results, outputting dataframe.'. format(len(result_list)))
    result = pd.DataFrame(result_list)
    result.columns = columns
        
    return(result)