# Function to create a Fox Hunter json dAcc dictionary

import acc
import dicts
import fjson
import fun_login
import fun_text_date as td
from pprint import pprint

def confirm_valide_Fox_Hunter_json(dFox):
	required_keys = ['companies', 'contacts']
	for key in required_keys:
		if key not in dFox:
			print(f"❌ Missing key: {key}")
			return False
	
	# Check companies sub-keys
	company_keys = ['primary', 'parent_company']
	for ckey in company_keys:
		if ckey not in dFox['companies']:
			print(f"❌ Missing company key: {ckey}")
			return False
	
	# Check contacts is a list
	if not isinstance(dFox['contacts'], list):
		print("❌ 'contacts' should be a list")
		return False
	
	return True

def get_Fox_Hunter_dAcc(dFox):
	dAcc = dicts.get_blank_account_dict()

	# Use parent company if available else primary company
	if dFox['companies']['parent_company'] == None:
		dEntity = dFox['companies']['primary']
		FOXENTITYTYPE = 'primary'
	else:
		dEntity = dFox['companies']['parent_company']
		FOXENTITYTYPE = 'parent_company'
	
	# Entity details
	dAcc['ENTITY'] = dEntity['Name']
	dAcc['STREET'] = dEntity['BillingStreet']
	dAcc['CITY'] = dEntity['BillingCity']
	dAcc['STATE'] = dEntity['BillingState']
	dAcc['ZIP'] = dEntity['BillingPostalCode']
	dAcc['PHONE'] = dEntity['Phone']
	dAcc['PHONEENTITY'] = dEntity['Phone']
	dAcc['WEBSITE'] = dEntity['Website']
	dAcc['CATEGORY'] = dEntity['Category__c']
	dAcc['DESCRIPTION'] = dEntity['Description']
	dAcc['LINKEDINENTITY'] = dEntity['LinkedIn_Url__c']
	dAcc['FHENTITYTYPE'] = FOXENTITYTYPE
	# Person details
	dPerson = dFox['contacts']
	for row in dPerson:
		if row['priority_rank'] == 1:
			dAcc['NF'] = row['FirstName']
			dAcc['NL'] = row['LastName']
			dAcc['NM'] = row['MiddleName__c']
			dAcc['TITLE'] = row['PersonTitle']
			dAcc['EMAIL'] = row['PersonEmail']
			dAcc['PHONEPERSONAL'] = row['Phone']
			dAcc['MOBILE'] = row['PersonMobilePhone']
			dAcc['LINKEDIN'] = row['LinkedIn_Url__c']
			break
	
	# Assemble peron full name
	if dAcc['NM'] != 'None' and dAcc['NM'] != '':
		dAcc['NAME'] = f"{dAcc['NF']} {dAcc['NM']} {dAcc['NL']}"
	else:
		dAcc['NAME'] = f"{dAcc['NF']} {dAcc['NL']}"


	for row in dAcc:
		if dAcc[row] == '':
			dAcc[row] = 'None'

	return dAcc

td.banner('ai Fox Hunter json to Acc dict v01')

service = fun_login.TerraForce()

filepath = 'F:/Research Department/Code/Contact Files'
filename = 'Company_Search_TAVARES TWENTY-FIVE I LLC_20251229_114320.json'
fullpath = f'{filepath}/{filename}'

dFox = fjson.getJsonDict(fullpath)

for row in dFox:
	print(f'\nRow: {row}')
	pprint(dFox[row])
exit()

dAcc = get_Fox_Hunter_dAcc(dFox)
pprint(dAcc)
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')

# Find Create Account Entity
dAcc = acc.find_create_account_entity(service, dAcc)

dAcc = acc.find_create_account_person(service, dAcc)
pprint(dAcc)
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')

print('\n Process complete.')