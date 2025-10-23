
import bb
import csv
from os import system
import dicts
import fun_login
import lao
from pprint import pprint
import fun_text_date as td


td.banner('PIDs in Opportunity Zones v01')

service = fun_login.TerraForce()

dOwnerships = dicts.spreadsheet_to_dict(r'F:\Research Department\maps\Opportunity Zones\Maricopa_PIDs_in_OZ.xlsx')
lPIDs = []
lMaster = [['TF', 'PID', 'Deal Name', 'Classification', 'Lot Type', 'Acres', 'Lots', 'Lot Description', 'Zoning', 'City', 'Submarket', 'Location', 'Owner Entity', 'Contact', 'Phone', 'Mobile', 'Email', 'Website', 'Address', 'Record Type', 'Description']]
# 	mobile	phone	email	entitywebsite	billingaddress	recordtype

counter = 1
resetting = 1

for row in dOwnerships:
	r = dOwnerships[row]['pid']
	lPIDs.append(r)
	counter += 1
	if counter == 100:

		# Create query string for TF
		quoted_items = [f"'{str(item)}'" for item in lPIDs]
		qPIDs = ','.join(quoted_items)

		# TerraForce Query
		fields = 'default'
		wc = f"PID__c in ({qPIDs}) and StageName__c = 'Lead'"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		for row in results:
			# pprint(row)
			# =HYPERLINK("https://landadvisors.my.salesforce.com/a0O1300000RV6YsEAL", "TF")
			deal_link = f'=HYPERLINK("https://landadvisors.my.salesforce.com/{row["Id"]}", "TF")'
			lLine = [deal_link]
			lLine.append(row['PID__c'])
			lLine.append(row['Name'])
			lLine.append(row['Classification__c'])
			lLine.append(row['Lot_Type__c'])
			lLine.append(row['Acres__c'])
			lLine.append(row['Lots__c'])
			lLine.append(row['Lot_Description__c'])
			lLine.append(row['Zoning__c'])
			lLine.append(row['City__c'])
			lLine.append(row['Submarket__c'])
			lLine.append(row['Location__c'])
			if row['Owner_Entity__c'] != 'None':
				lLine.append(row['Owner_Entity__r']['Name'])
				website = row['Owner_Entity__r']['Website']
			else:
				lLine.append('')
				website = ''
			if row['AccountId__c'] != 'None':
				# Build address
				if row['AccountId__r']['BillingStreet'] != None:
					address = row['AccountId__r']['BillingStreet']
					address = f'{address}, {row["AccountId__r"]["BillingCity"]}, {row["AccountId__r"]["BillingState"]} {row["AccountId__r"]["BillingPostalCode"]}'
				else:
					address = ''
				lLine.append(row['AccountId__r']['Name'])
				lLine.append(row['AccountId__r']['Phone'])
				lLine.append(row['AccountId__r']['PersonMobilePhone'])
				lLine.append(row['AccountId__r']['PersonEmail'])
				lLine.append(website)
				lLine.append(address)
			else:
				lLine.append('')
				lLine.append('')
				lLine.append('')
				lLine.append('')
				lLine.append(website)
				lLine.append('')
			lLine.append(dicts.get_record_type(row['RecordTypeId']))
			lLine.append(row['Description__c'])
	
			lMaster.append(lLine)

			# Reset counter and list
			print(f' {resetting} Resetting counter and list...')
			resetting += 1
			counter = 1
			lPIDs = []

			# print('here1')
			# pprint(row)
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
	

with open(r'C:\TEMP\Ownerships in OZ.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerows(lMaster)

lao.openFile(r'C:\TEMP\Ownerships in OZ.csv')

exit()


