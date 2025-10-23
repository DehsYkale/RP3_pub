# Take a spreadsheet of PIDs and check if the StageName is Lead and change it to Top 100 (MVP)

from pprint import pprint
import lao
import bb
import fun_login

service = fun_login.TerraForce()

filename = 'F:/Research Department/Projects/Advisors and Markets/Nancy Surak/Tampa MVP PIDs 2023-09.xlsx'
dPIDs = lao.spreadsheetToDict(filename)
for row in dPIDs:
	PID = dPIDs[row]['PID']
	print(PID)
	# TerraForce Query
	fields = 'default'
	wc = "PID__c = '{0}'".format(PID)
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	stage_name = results[0]['StageName__c']
	account_type = 'lda_Opportunity__c'
	DID = results[0]['Id']
	if stage_name == 'Lead':
		dup = {'type': 'lda_Opportunity__c',
				'id': DID,
				'StageName__c': 'Top 100'}
		bb.tf_update_3(service, dup)
		

exit('\n Fin...')

