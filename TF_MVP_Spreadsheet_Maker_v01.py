
# Makes a csv file of MVP Deal Contacts
# Used for checking missing Contact info (Phone, Mobile, Email, Address)

import bb
import csv
from os import system
import fun_login
import lao
from pprint import pprint
import fun_text_date as td

service = fun_login.TerraForce()
# TerraForce Query
fields = 'default'
wc = "StageName__c = 'Top 100'"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
# pprint(results)
lMVPs = []
for row in results:
	lLine = [row['Market__c']]
	lLine.append(row['Name'])
	lLine.append(row['PID__c'])
	lLine.append(row['StageName__c'])
	if row['Owner_Entity__c'] != 'None':
		lLine.append(row['Owner_Entity__r']['Name'])
	else:
		lLine.append('')
	if row['AccountId__c'] != 'None':
		lLine.append(row['AccountId__r']['Name'])
		lLine.append(row['AccountId__r']['Phone'])
		lLine.append(row['AccountId__r']['PersonMobilePhone'])
		lLine.append(row['AccountId__r']['PersonEmail'])
	else:
		lLine.append('')
		lLine.append('')
		lLine.append('')
		lLine.append('')
	
	lMVPs.append(lLine)

with open('C:\TEMP\Top100.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(['Market', 'Name', 'PID', 'Stage', 'Entity', 'Person', 'Phone', 'Mobile', 'Email'])
	for line in lMVPs:
		writer.writerow(line)

lao.openFile('C:\TEMP\Top100.csv')
exit()

