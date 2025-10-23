# Delete old listings

import bb
import lao
import fun_login
import fun_text_date as td
from pprint import pprint
from symbols import ALERT, DONE, ERROR, INFO, SUCCESS

service = fun_login.TerraForce()

market = 'Boise'

# TerraForce Query
fields = 'default'
wc = "Market__c = '{0}' AND StageName__c = 'Lead' AND RecordTypeID = '012a0000001ZSS8AAO' AND CreatedDate <= 2025-01-01T00:00:00.000Z".format(market)
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=2, fields=fields)

pprint(results)