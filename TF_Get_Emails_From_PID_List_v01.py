# Get the contacts and email addresses from a slist of PIDS

import lao
import bb
import csv
import fun_login
import fun_text_date as td
from pprint import pprint

service = fun_login.TerraForce()

# filename = 'F:\Research Department\maps\Congressional Districts/Buckeye_District_2_Land_Owners.xlsx'
filename = 'F:\Research Department\maps\Congressional Districts/Maricopa_Board_of_Supervisors_District_4.xlsx'
dict = lao.spreadsheetToDict(filename)
# out_filename = 'F:\Research Department\maps\Congressional Districts/Maricopa_District_4_Land_Owners_Emails.csv'
out_filename = 'F:\Research Department\maps\Congressional Districts/ricopa_Board_of_Supervisors_District_4.csv'

dEmails = {}

# ('West Surprise', 'East Surprise', 'Tonopah', 'South Peoria', 'South Surprise', 'North Goodyear', 'North Peoria', 'North Surprise', 'Verrado', 'Wittmann', 'Sun Cities', 'North Buckeye', 'West Buckeye', 'Northwest Maricopa County', 'East Buckeye', 'Lake Pleasant', 'Goodyear')



# count = 0
# for row in dict:
# 	PID = dict[row]['PID']
# 	print(PID)
	# TerraForce Query
fields = 'default'
# wc = f"PID__c = '{PID}'"
wc = "Submarket__c IN ('West Surprise','East Surprise','Tonopah', 'South Peoria', 'South Surprise', 'North Goodyear', 'North Peoria', 'North Surprise', 'Verrado', 'Wittmann', 'Sun Cities', 'North Buckeye', 'West Buckeye', 'Northwest Maricopa County', 'East Buckeye', 'Lake Pleasant', 'Goodyear') AND StageName__c <> 'Closed' AND StageName__c <> 'Closed Lost'"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
print(len(results))
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')
for r in results:
	# print('here1')
	# pprint(r)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	# if 'Closed' in r['StageName__c']:
	# 	print('here3 CLOSED')
	# 	break
	# if r['RecordTypeId'] != '012a0000001ZSS8AAO':
	# 	print('here4 NOT RESEARCH TYPE')
	# 	break
	p = r['AccountId__r']
	e = r['Owner_Entity__r']
	# pprint(d)
	if p != 'None':
		if p['PersonEmail'] != 'None':
			PID = r['PID__c']
			email = p['PersonEmail']
			person = p['Name']

			if e != 'None':
				entity = e['Name']				
			else:
				entity = 'none'

			if email in dEmails:
				print('here1 EXISTING')
				acres = dEmails[email]['Acres']
				try:
					acres = float(acres) + float(r['Acres__c'])
				except TypeError:
					break
				dEmails[email]['Acres'] = acres
			else:
				print('here2 NEW')
				dEmails[email] ={
					'Person': person,
					'Entity': entity,
					'PID': PID,
					'Acres': float(r['Acres__c'])
					}
		# break

# print('here1')
# pprint(dEmails)
# ui = td.uInput('\n Continue [00]... > ')
# if ui == '00':
# 	exit('\n Terminating program...')

with open(out_filename, 'w', newline='') as f:
	fout = csv.writer(f)
	header = ['Person', 'Company', 'Email', 'PID', 'Acres']
	fout.writerow(header)
	for email in dEmails:
		fout.writerow([dEmails[email]['Person'], dEmails[email]['Entity'], email, dEmails[email]['PID'], dEmails[email]['Acres']])

lao.openFile(out_filename)
				# ui = td.uInput('\n Continue [00]... > ')
				# if ui == '00':
				# 	exit('\n Terminating program...')