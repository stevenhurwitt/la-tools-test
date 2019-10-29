#!/usr/bin/env python
# coding: utf-8

# # Audit Event Errors

# In[2]:


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


# In[4]:


audit = """SELECT DISTINCT subs.subject, source, props.KEY, props.value, message, Cast (timestamp as DATETIME) as maxDate
FROM audit_events, Unnest(subjects) as subs, Unnest(properties) as props
WHERE severity = 'ERROR'
and subs.subject_type = 'datasource'
and message NOT LIKE '%Heartbeat cannot be calculated%'
and props.KEY IN ('rule_function', 'step')
and props.value NOT IN ('vee_postdeal_payload_response')
ORDER BY maxdate DESC"""


# In[5]:


#ewx_client.execute_query(audit, limit = 9999)


# In[ ]:




