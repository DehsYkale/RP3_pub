# Update Deal information including:
#   Buyer info
#   Seller info
#   Classification
#   Lot Type

import acc
import fun_text_date
import lao
import bb
import cpypg
from pprint import pprint
import fun_text_date as td

# Print yellow text for missing data
def color_print(strTitle, strVal, override_yellow=False):
	strText = ' {0:16}{1}'.format(strTitle, strVal)
	if strTitle == 'Stage:':
		if strVal == 'Lead':
			lao.colorText(strText, 'CYAN')
		elif strVal == 'Closed':
			lao.colorText(strText, 'Green')
		elif strVal == 'Closed Lost':
			lao.colorText(strText, 'Red')
		else:
			lao.colorText(strText, 'Blue')
		return
	if strVal == '':
		lao.colorText(strText, 'YELLOW')
	else:
		print(strText)

service = bb.sfLogin()

PID = 'FLHillsborough178995'
DID = bb.getDIDfromPID(service, PID)

# Get the Deal data
fields = 'Id,' \
		'AccountId__c,' \
			'AccountId__r.Name,' \
			'AccountId__r.FirstName,' \
			'AccountId__r.MiddleName__c,' \
			'AccountId__r.LastName,' \
			'AccountId__r.Company__r.Id,' \
			'AccountId__r.Company__r.Name,' \
			'AccountId__r.PersonTitle,' \
			'AccountId__r.BillingStreet,' \
			'AccountId__r.BillingCity,' \
			'AccountId__r.BillingState,' \
			'AccountId__r.BillingPostalCode,' \
			'AccountId__r.Phone,' \
			'AccountId__r.PersonMobilePhone,' \
			'AccountId__r.PersonHomePhone,' \
			'AccountId__r.PersonEmail,' \
			'AccountId__r.Category__c,' \
			'AccountId__r.Description,' \
			'AccountId__r.Top100__c,' \
		'Acres__c,' \
		'City__c,' \
		'Classification__c,' \
		'County__c,' \
		'CreatedById,' \
		'CreatedDate,' \
		'Description__c,' \
		'Latitude__c,' \
		'Lead_Parcel__c,' \
		'Legal_Description__c,' \
		'Location__c,' \
		'Longitude__c,' \
		'Lot_Description__c,' \
		'Lot_Type__c,' \
		'Lots__c,' \
		'Market__c,' \
		'Name,' \
		'Owner_Entity__c,' \
			'Owner_Entity__r.Name,' \
			'Owner_Entity__r.BillingStreet,' \
			'Owner_Entity__r.BillingCity,' \
			'Owner_Entity__r.BillingState,' \
			'Owner_Entity__r.BillingPostalCode,' \
			'Owner_Entity__r.Fax,' \
			'Owner_Entity__r.Phone,' \
			'Owner_Entity__r.Website,' \
			'Owner_Entity__r.Category__c,' \
		'OPR_Sent__c,' \
		'Parcels__c,' \
		'PID__c,' \
		'Research_Flag__c,' \
		'StageName__c,' \
		'State__c,' \
		'Subdivision__c,' \
		'Submarket__c,' \
		'RecordTypeId,' \
		'Zipcode__c,' \
		'Zoning__c,' \
		'(Select Agent__c, Agent_Text_Name__c, LAO_Agent__c From Commissions__r),' \
		'(Select Id,' \
			'CreatedDate,' \
			'Map_Description__c,' \
			'Record_Type_Name__c,' \
			'Name From Request_Deal__r),' \
		'(Select Id,' \
			'LastModifiedDate From Package_Information__r),' \
		'(Select Id From Offers__r),' \
		'(Select Id,' \
			'LastModifiedDate From NotesAndAttachments),' \
		'(Select Id,' \
			'LastModifiedDate From Notes),' \
		'(SELECT Id FROM Accounts_Receivable__r )'
wc = "Id = '{0}'".format(DID)
qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
results = bb.sfquery(service, qs)

dDeal = {
	'opTFID': 'None',
	'opNAME': 'None',
	'opSTREET': 'None',
	'opCITY': 'None',
	'opSTATE': 'None',
	'opZIPCODE': 'None',
	'opPHONE': 'None',
	'opMOBILE': 'None',
	'opEMAIL': 'None',
	'opEMAIL': 'None',
	'opCATEGORY': 'None',
	'oeTFID': 'None',
	'oeNAME': 'None',
	'oeSTREET': 'None',
	'oeCITY': 'None',
	'oeSTATE': 'None',
	'oeZIPCODE': 'None',
	'oePHONE': 'None',
	'oeWEBSITE': 'None',
	'oeCATEGORY': 'None'}

dDeal = results[0]
# results = bb.getLeadDealData(service, PID, dealVar='All')

lao.banner('TF Deal Updater v01')
# pprint(dDeal)
print
print(' PID:            {0}'.format(dDeal['PID__c']))
print(' Deal Name:      {0}'.format(dDeal['Name']))
color_print('Market:', dDeal['Market__c'])
color_print('Stage:', dDeal['StageName__c'])
print(' Acres:          {0}'.format(dDeal['Acres__c']))
classification = ', '.join(dDeal['Classification__c'])
color_print('Classification:', classification)
color_print('Lot Type:', dDeal['Lot_Type__c'])
print('-' * 50)
if dDeal['AccountId__c'] != '':
	res = dDeal['AccountId__r']
	color_print('Owner Person:', res['Name'])
	if res['Company__r'] == '':
		color_print('Company:', res['Company__r'])
	else:
		color_print('Company:', res['Company__r']['Name'])
	color_print('Address:', res['BillingStreet'])
	csz = '{0}, {1} {2}'.format(res['BillingCity'], res['BillingState'], res['BillingPostalCode'])
	if res['BillingCity'] == '' or res['BillingState'] == '' or res['BillingPostalCode'] == '':
		override_yellow = True
	else:
		override_yellow = False
	color_print('', csz, override_yellow)
	color_print('Phone:', res['Phone'])
	color_print('Mobile:', res['PersonMobilePhone'])
	color_print('Email:', res['PersonEmail'])

else:
	color_print('Owner Person:', '')
print
if dDeal['Owner_Entity__c'] != '':
	res = dDeal['Owner_Entity__r']
	color_print('Owner Entity:', res['Name'])
	color_print('Address:', res['BillingStreet'])
	csz = '{0}, {1} {2}'.format(res['BillingCity'], res['BillingState'], res['BillingPostalCode'])
	if res['BillingCity'] == '' or res['BillingState'] == '' or res['BillingPostalCode'] == '':
		override_yellow = True
	else:
		override_yellow = False
	color_print('', csz, override_yellow)
	color_print('Phone:', res['Phone'])
	color_print('Website:', res['Website'])
else:
	color_print('Owner Entity:', '')

# pprint(dDeal)

print('-' * 50)
print('\n Select item to update:')
print('\n  1) Deal Info')
print('\n  2) Owner Info')
print('\n 00) Quit')
ui = td.uInput('\n Select > ')
if ui == '00':
	exit('\n Terminating program...')
elif ui == '1':
	print('\n Update Deal Info')
elif ui == '2':
	print('\n Update Owner Info')
	dAcc = acc.getBlankAccountDictionary()
	# Populate dAcc fields with TF data
	res = dDeal['AccountId__r']
	dAcc['AID'] = dDeal['AccountId__c']
	dAcc['CATEGORY'] = res['Category__c']
	dAcc['CITY'] = res['BillingCity']
	dAcc['DESCRIPTION'] = res['Description']
	if res['Company__r'] != '':
		dAcc['EID'] = res['Company__r']		# Entity ID
		dAcc['ENTITY'] = res['Company__r']['Name']
	dAcc['EMAIL'] = res['PersonEmail'].lower()
	dAcc['MOBILE'] = res['PersonMobilePhone']
	dAcc['NAME'] = res['Name']			# Person Name
	dAcc['NF'] = res['FirstName']			# First Name
	dAcc['NM'] = res['MiddleName__c']			# Middle Name
	dAcc['NL'] = res['LastName']			# Last Name
	dAcc['PHONE'] = res['Phone']
	dAcc['PHONEHOME'] = res['PersonHomePhone']
	dAcc['STATE'] = td.make_title_case(res['BillingState'])
	dAcc['STREET'] = td.titlecase_street(res['BillingStreet'])
	dAcc['TITLEPERSON'] = td.make_title_case(res['PersonTitle'])
	try:
		dAcc['TOP100AGENT'] = res['Top100__c']
	except KeyError:
		pass
	dAcc['ZIPCODE'] = res['BillingPostalCode']
	for key in dAcc:
		if dAcc[key] == '':
			dAcc[key] = 'None'
	dAcc = cpypg.get_contact_info_from_webpage(dAcc)
	pprint(dAcc)



