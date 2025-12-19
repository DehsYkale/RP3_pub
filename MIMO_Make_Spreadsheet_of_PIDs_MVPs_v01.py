

import csv
import dicts
import fun_text_date as td
import lao
import bb
import fun_login
from pprint import pprint
import webs

td.banner('Make Spreadsheet of PIDs MVPs v01')

service = fun_login.TerraForce()

# Get the spreadsheet of PIDs
spreadsheet_file = lao.guiFileOpen(path='F:/Research Department/Projects/Advisors and Markets', titlestring='Select Spreadsheet of PIDs', extension=[('Excel files', '.xlsx'), ('all files', '.*')])
dPIDs = dicts.spreadsheet_to_dict(spreadsheet_file)

print(' Select Action:')
print(' 1. Make PIDs MVP')
print(' 2. Get PID Contact MVP List')
ui = td.uInput('\n Select > ')

if ui == '1':
	for row in dPIDs:
		PID = dPIDs[row]['propertyid']
		# Further processing can be done here
		print(f'Processing PID: {PID}')

		# TerraForce Query
		fields = 'default'
		wc = f"PID__c = '{PID}'"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

		print(results[0]['StageName__c'])
		if results[0]['StageName__c'] == 'Lead':
			dup = dicts.get_blank_deal_update_dict(DID=results[0]['Id'])
			dup['StageName__c'] = 'Top 100'
			bb.tf_update_3(service, dup)

			# webs.open_pid_did(service, PID)
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
elif ui == '2':
	lMVPs = []
	with open('C:/TEMP/PID MVP List.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['PID', 'MVP Contact Name', 'Advisors MVP'])

		for row in dPIDs:
			PID = dPIDs[row]['propertyid']
			# Further processing can be done here
			print(f'Processing PID: {PID}')

			# TerraForce Query
			fields = 'default'
			wc = f"PID__c = '{PID}'"
			results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

			# print(results[0]['PID__c'])
			# print(results[0]['AccountId__r']['Name'])
			# print(results[0]['AccountId__r']['Top100__c'])
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')

			writer.writerow([PID, results[0]['AccountId__r']['Name'], results[0]['AccountId__r']['Top100__c']])

			
			# print('here1')
			# pprint(results)
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
		
lao.openFile('C:/TEMP/PID MVP List.csv')

