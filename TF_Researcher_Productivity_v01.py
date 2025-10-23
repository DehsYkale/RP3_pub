# Get Productivity Metrics of Researchers From TerraForce


import bb
import csv
from os import system
import dicts
import fun_login
import lao
from pprint import pprint
import fun_text_date as td


td.banner('TF Researcher Productivity v01')

service = fun_login.TerraForce()

# Get TF UserId of all Staff
dStaff = dicts.get_staff_dict(dict_type='userids', skipFormerEmployees=False)

# Get TF UserId of Researchers
dResearchers = dicts.get_staff_dict(dict_type='researchers', skipFormerEmployees=True)
# pprint(dResearchers)
lResearchers = list(dResearchers.values())
lResearchers = [f"'{x}'" for x in lResearchers]
lResearchers = ', '.join(lResearchers)

# TerraForce Query
print('\n Querying TerraForce Deals...')
fields = 'default'
wc = f"OwnerId IN ({lResearchers})"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

print(' Writing Deals to CSV...')

lDeals = []
for row in results:

	# Format the data
	owner, created_by, last_mod_by = 'None', 'None', 'None'
	for name in dStaff:
		rec_id = dStaff[name]
		if rec_id in row['OwnerId']:
			owner = name
		if rec_id in row['CreatedById']:
			created_by = name
		if rec_id in row['LastModifiedById']:
			last_mod_by = name
	# Format Dates
	created_date = td.date_engine(row['CreatedDate'], outformat='TF', informat='iso')
	mod_date = td.date_engine(row['LastModifiedDate'], outformat='TF', informat='iso')
	opr_sent = td.date_engine(row['OPR_Sent__c'], outformat='slash', informat='TF')

	lLine = [row['Market__c']]
	lLine.append(row['Name'])
	lLine.append(row['PID__c'])
	lLine.append(row['StageName__c'])
	lLine.append(created_by)
	lLine.append(created_date)
	lLine.append(owner)
	lLine.append(last_mod_by)
	lLine.append(mod_date)
	lLine.append(opr_sent)
	
	lDeals.append(lLine)

with open('C:\\TEMP\\Researcher Deals.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(['Market', 'Name', 'PID', 'Stage', 'Created By', 'Created Date', 'Owner', 'Last Mod By', 'Last Mod Date', 'OPR Sent'])
	for line in lDeals:
		writer.writerow(line)

lao.openFile('C:\\TEMP\\Researcher Deals.csv')
exit()


