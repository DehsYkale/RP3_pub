#Python3

import lao
user = lao.getUserName()
import acc
import bb
import csv
import fun_login
import fun_text_date as td
import mc
from os.path import exists
from pprint import pprint
# import pdb
import sys
import fun_text_date as td
from webbrowser import open as openbrowser

def getSkipFile():
	skipFile = 'F:/Research Department/Projects/Advisors and Markets/Nashville/SKIP Eric Deems Contacts.txt'
	# Make skipfile if it does not exitst
	file_exists = exists(skipFile)
	if file_exists is False:
		with open(skipFile, 'w', newline='') as f:
			f.write('Deems Contacts Skip File')
	return skipFile

# Check or Update skipfile
def check_update_skipfile(what_to_do):
	
	# strSkip = '{0}:{1}'.format(dAcc['NAME'], dAcc['EMAIL'])
	strSkip = dAcc['EMAIL']
	# print(strSkip)
	# ui = td.uInput('\n Continue... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	if what_to_do == 'CHECK':
		with open(skipFile, 'r') as f:
			skipit = f.read()
		if strSkip in skipit:
			return True
		else:
			return False
	elif what_to_do == 'UPDATE':
		with open(skipFile, 'a') as f:
			f.write('{0}\n'.format(strSkip))

def get_source_header_dict():
	dSource_headers = {'CATEGORY': 'CATEGORY',
						'CITY': 'CITY',
						'EMAIL': 'EMAIL',
						'COMPANY': 'ENTITY',
						'ENTITY': 'ENTITY',
						'FAX': 'FAX',
						'FIRST NAME': 'NF',
						'MIDDLE NAME': 'NM',
						'LAST NAME': 'NL',
						'FULL NAME': 'NAME',
						'MOBILE': 'MOBILE',
						'PHONE': 'PHONE',
						'PHONE COMPANY': 'PHONEENTITY',
						'PHONE HOME': 'PHONEHOME',
						'PHONE OTHER': 'PHONEOTHER',
						'STATE': 'STATE',
						'STREET': 'STREET',
						'MVP ADVISOR': 'TOP100AGENT',
						'JOB TITLE': 'TITLEPERSON',
						'ZIP': 'ZIPCODE',
						'WEBSITE': 'WEBSITE'}
	return dSource_headers

# Populate dAcc with spreadsheet data
def populate_dAcc(d):
	# Get blank dAcc
	dAcc = dicts.get_blank_account_dict()
	# Get source header dict
	dSource_headers = get_source_header_dict()
	# pprint(d)
	# Create list of source headers dict keys
	lHeaders = list(dSource_headers.keys())

	# Cycle through headers and assign to dAcc
	for hedr in lHeaders:
		if hedr in d.keys():
			if d[hedr] != None:
				dAcc_key = dSource_headers[hedr]
				if type(d[hedr]) == str:
					dAcc[dAcc_key] = d[hedr].strip()
				else:
					dAcc[dAcc_key] = d[hedr]
	
	# Remove blanks
	for l in dAcc:
		if dAcc[l] == '' or dAcc[l] == None:
			dAcc[l] = 'None'
	# Format address
	dAcc = td.address_formatter(dAcc)
	# Format email
	if dAcc['EMAIL'] != 'None':
		dAcc['EMAIL'] = dAcc['EMAIL'].lower()
	# Populate full name
	if dAcc['NAME'] == 'None':
		dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	# Add MailChimp list ID and Name
	dAcc['MCAUDID'] = '7cf1723265'  	# Nashville Audience
	dAcc['MCAUDNAME'] = 'Nashville'
	return dAcc

# Populate dAcc with spreadsheet data
def dAccPopulate(d):
	dAcc = dicts.get_blank_account_dict()
	pprint(d)
	# Categories separated by semicolon ;
	# Example Buyer Commercial;Eric Deems;Market Insights
	if 'CATEGORY' in d.keys():
		if d['CATEGORY'] != None:
			dAcc['CATEGORY'] = d['CATEGORY']
	if 'CITY' in d.keys():
		if d['CITY'] != None:
			dAcc['CITY'] = d['CITY']
	if 'EMAIL' in d.keys():
		tempEmail = d['EMAIL'].encode('utf8')
		dAcc['EMAIL'] = tempEmail.lower()
	if 'COMPANY' in d.keys():
		dAcc['ENTITY'] = d['COMPANY']				# Company
	if 'FAX' in d.keys():
		dAcc['FAX'] = d['FAX']						# Fax
	dAcc['MCAUDID'] = '7cf1723265'  				# Nashville Audience
	dAcc['MCAUDNAME'] = 'Nashville'
	if 'FIRST NAME' in d.keys():
		dAcc['NF'] = d['FIRST NAME'].strip()		# First Name
	if 'MIDDLE NAME' in d.keys():
		dAcc['NM'] = d['MIDDLE NAME'].strip()		# Middle Name
	if 'LAST NAME' in d.keys():
		dAcc['NL'] = d['LAST NAME'].strip()
	if 'FULL NAME' in d.keys():
		dAcc['NAME'] = d['FULL NAME'].strip()		# Person Name
	else:
		dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL']) ## Person Name
	if 'FAX' in d.keys():
		dAcc['FAX'] = d['FAX']
	if 'MOBILE' in d.keys():
		dAcc['MOBILE'] = d['MOBILE']	# Person Mobile Phone
	if 'PHONE' in d.keys():
		dAcc['PHONE'] = d['PHONE']
	if 'PHONE COMPANY' in d.keys():
		dAcc['PHONEENTITY'] = d['PHONE COMPANY']
	if 'PHONE HOME' in d.keys():
		dAcc['PHONEHOME'] = d['HOME PHONE']
	if 'PHONE OTHER' in d.keys():
		dAcc['PHONEOTHER'] = d['PHONE OTHER']
	if 'STATE' in d.keys():
		dAcc['STATE'] = d['STATE']
	if 'STREET' in d.keys():
		dAcc['STREET'] = d['STREET']
	if 'MVP ADVISOR' in d.keys():
		dAcc['TOP100AGENT'] = d['MVP ADVISOR']
	if 'JOB TITLE' in d.keys():
		dAcc['TITLEPERSON'] = d['JOB TITLE']
	if 'ZIPCODE' in d.keys():
		dAcc['ZIPCODE'] = str(d['ZIPCODE'])[:5]
	if 'WEBSITE' in d.keys():
		dAcc['WEBSITE'] = d['WEBSITE']
	# Remove blanks
	for l in dAcc:
		if dAcc[l] == '':
			dAcc[l] = 'None'
	dAcc = td.address_formatter(dAcc)
	# pprint(dAcc)
	# exit()
	return dAcc

# Fix Address for missing City, State & Zipcode
def fix_Address_Missing_City_State_Zipcode(dAcc):
	if dAcc['STREET'] != 'None':
		# Enter Zip Code
		if dAcc['CITY'] == 'None' or dAcc['STATE'] == 'None' or dAcc['ZIPCODE'] == 'None':
			td.warningMsg('\n MISSING ADDRESS INFO')
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(dAcc['STREET']))
			dAcc['ZIPCODE'] = td.uInput('\n Type Zip Code or [Enter] for None [00] > ')
			if dAcc['ZIPCODE'] == '':
				dAcc['ZIPCODE'] = 'None'
			elif dAcc['ZIPCODE'] == '00':
				exit('\n Terminating program...')
			else:
				dAcc['CITY'], dAcc['STATE'], USA = lao.zipCodeFindCityStateCountry(dAcc['ZIPCODE'])
	return dAcc

# # Populate MC Campaign IDs
def populate_MC_Campaign_IDs(dAcc):
	dCat = {}
	if 'Agent Land' in dAcc['CATEGORY']:
		dCat[u'10203230e7'] = True
	if 'Build to Rent' in dAcc['CATEGORY']:
		dCat[u'd3dc063c83'] = True
	if 'Buyer Homebuilder' in dAcc['CATEGORY']:
		dCat[u'd83c9e38a4'] = True
	if 'Buyer Industrial' in dAcc['CATEGORY']:
		dCat[u'a4ccbc38ce'] = True
	if 'Buyer Multifamily' in dAcc['CATEGORY']:
		dCat[u'fb403603c9'] = True
		dCat[u'ea75c759f4'] = True
	if 'Buyer Office' in dAcc['CATEGORY'] or 'Buyer Retail' in dAcc['CATEGORY']:
		dCat[u'ab8e528cc3'] = True
	if 'Developer' in dAcc['CATEGORY']:
		dCat[u'ab8e528cc3'] = True
	if 'Investor' in dAcc['CATEGORY']:
		dCat[u'34ff6f3023'] = True
	if 'Large Landowner' in dAcc['CATEGORY']:
		dCat[u'c50f7e42fe'] = True
	if 'Lender Hard Money' in dAcc['CATEGORY'] or 'Private Equity' in dAcc['CATEGORY']:
		dCat[u'800da3e435'] = True
	if 'Government' in dAcc['CATEGORY']:
		dCat[u'95542f4aee'] = True


	# Market Insights 
	dCat[u'e5aeee0272'] = True
	
	dAcc['MCLCAMPAIGNIDS'] = dCat
	return dAcc

 # Format phone

# Format phone numbers
def formatPhoneNumbers(dAcc):
	if dAcc['FAX'] != 'None':
		dAcc['FAX'] = td.phoneFormat(dAcc['FAX'])
		if dAcc['FAX'] == 'Skip':
			dAcc['FAX'] = 'None'
	if dAcc['PHONE'] != 'None':
		dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
		if dAcc['PHONE'] == 'Skip':
			dAcc['PHONE'] = 'None'
	if dAcc['PHONEHOME'] != 'None':
		dAcc['PHONEHOME'] = td.phoneFormat(dAcc['PHONEHOME'])
		if dAcc['PHONEHOME'] == 'Skip':
			dAcc['PHONEHOME'] = 'None'
	if dAcc['PHONEOTHER'] != 'None':
		dAcc['PHONEOTHER'] = td.phoneFormat(dAcc['PHONEOTHER'])
		if dAcc['PHONEOTHER'] == 'Skip':
			dAcc['PHONEOTHER'] = 'None'
	if dAcc['MOBILE'] != 'None':
		dAcc['MOBILE'] = td.phoneFormat(dAcc['MOBILE'])
		if dAcc['MOBILE'] == 'Skip':
			dAcc['MOBILE'] = 'None'
	return dAcc

# Clear screen and print user input progress
def printUIInput(dAcc):
	lao.banner('Contact TFMC Import')
	if lao.getUserName() == 'blandis':
		td.colorText(' [main def printUIInput]', 'YELLOW')
	msg = \
		' Record {0} of {1}\n\n' \
		' Entity             {2}\n' \
		' Contact Name       {3}\n\n' \
		' Address            {4}\n' \
		'                    {5}, {6} {7}\n\n' \
		' Phone              {8}\n' \
		' Mobile             {9}\n\n' \
		' MC Audience        {10}\n' \
		' Email              {11}\n' \
		' Category           {12}\n' \
		' ---------------------------------------------------------\n' \
	.format(
		rowCount,
		fileNoRows,
		dAcc['ENTITY'],
		dAcc['NAME'],
		dAcc['STREET'],
		dAcc['CITY'],
		dAcc['STATE'],
		dAcc['ZIPCODE'],
		dAcc['PHONE'],
		dAcc['MOBILE'],
		dAcc['MCAUDNAME'],
		dAcc['EMAIL'],
		dAcc['CATEGORY'])
	print(msg)

# Check if email exists for skip
def is_email():
	if dAcc['EMAIL'] == 'None':
		return False, 'None'
	# fields = 'Id'
	# wc = "PersonEmail = '{0}'".format(dAcc['EMAIL'])
	# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	# results = bb.sfquery(service, qs)
	# TerraForce Query
	fields = 'default'
	wc = "PersonEmail = '{0}'".format(dAcc['EMAIL'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	if results == []:
		return False, 'None'
	else:
		return True, results

# User Confirm data entry
def confirm_data_entry():
	while 1:
		printUIInput(dAcc)

		print('\n  1) Open TF')
		print('\n  2) Next Contact')
		print('\n 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			openbrowser('https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view'.format(dAcc['AID']))
		else:
			# Write email to skip/complete file
			check_update_skipfile('UPDATE')
			break
	return

# Add Category
def add_categories(dAcc, din, dup):

	# Add existing Categories to str variable
	if din['Category__c'] == 'None':
		str_category = 'None'
	else:
		str_category = din['Category__c']

	# Add dAcc Categories if not in str variable
	if not dAcc['CATEGORY'] == 'None':
		if str_category == 'None':
			str_category = dAcc['CATEGORY']
		else:
			lCategory_dAcc = dAcc['CATEGORY'].split(';')
			for cat in lCategory_dAcc:
				if not cat in str_category:
					str_category = '{0};{1}'.format(str_category, dAcc['CATEGORY'])

	if str_category == 'None':
		str_category = 'Market Insights'
		dAcc['UPDATERECORD'] = True
	elif not 'Market Insights' in str_category:
		str_category = f'{str_category};Market Insights'
		dAcc['UPDATERECORD'] = True
	
	if str_category == 'None':
		str_category = 'Eric Deems'
		dAcc['UPDATERECORD'] = True
	elif not 'Eric Deems' in str_category:
		str_category = f'{str_category};Eric Deems'
		dAcc['UPDATERECORD'] = True

	if dAcc['UPDATERECORD'] is True:
		dup['Category__c'] = str_category
		dAcc['CATEGORY'] = str_category

	return dAcc, dup

# pdb.set_trace()
client = fun_login.MailChimp()
service = fun_login.TerraForce()
inFile = 'F:/Research Department/Projects/Advisors and Markets/Nashville/Deems Contact List Use Me 2023-09-06.xlsx'
skipFile = getSkipFile()
dContactsSprdSht = lao.spreadsheetToDict(inFile)
user = lao.getUserName()

# Determine the number of rows in the spreadsheet/dict
fileNoRows = len(dContactsSprdSht)

rowCount = 0
for contact in dContactsSprdSht:

	rowCount += 1
	# dAcc = dAccPopulate(dContactsSprdSht[contact])
	dAcc = populate_dAcc(dContactsSprdSht[contact])
	dAccOriginal = dAcc.copy()

	# Skip records already entered
	if check_update_skipfile('CHECK'):
		continue
	
	# Skip Contacts if email found in TF but add Categories
	printUIInput(dAcc)
	email_exist, results = is_email()
	if email_exist:
		print('\n Email exists in TF...updating Categories...\n')
		# Only update Categories
		for row in results:
			# Create update dict (dup)
			dup = {}
			dup['type'] = row['attributes']['type']
			dup['Id'] = row['Id']
			dAcc, dup = add_categories(dAcc, row, dup)
			if dAcc['UPDATERECORD'] is True:
				bb.tf_update_3(service, dup)
			break
		# Write NAME to skip/complete file
		check_update_skipfile('UPDATE')
		continue

	printUIInput(dAcc)
	# Fix Address for missing City, State & Zipcode
	dAcc = fix_Address_Missing_City_State_Zipcode(dAcc)

	# Format phone
	dAcc = formatPhoneNumbers(dAcc)

	printUIInput(dAcc)
	# Check TF for Entity
	if dAcc['ENTITY'] != 'None':
		dAcc = acc.find_create_account_entity(service, dAcc)
	
	printUIInput(dAcc)
	# Check TF for Person
	tmp1, tmp2, dAcc = acc.find_create_account_person(service, dAcc)

	# MC Add/Update Contact
	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(dAcc['AID'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	# pprint(results)
	# Update Category
	for row in results:
		# Create update dict (dup)
		dup = {}
		dup['type'] = row['attributes']['type']
		dup['Id'] = row['Id']

		# Add Categories
		dAcc, dup = add_categories(dAcc, row, dup)



		
		# Update Person's Entity
		if dAcc['ENTITY'] != dAccOriginal['ENTITY']:
			if dAcc['EID'] != 'None':
				dup['Company__c'] = dAcc['EID']
				dAcc['UPDATERECORD'] = True
		
		# Update MVP
		if dAcc['TOP100AGENT'] != 'None':
			if not dAcc['TOP100AGENT'] in dup['Top100__c']:
				dup['Top100__c'].append(dAcc['TOP100AGENT'])
				dAcc['UPDATERECORD'] = True

	# pprint(dup)
	# exit()
	if dAcc['UPDATERECORD'] is True:
		bb.tf_update_3(service, dup)

	

	# Write to MailChimp
	# if dAcc['EMAIL'] != 'None':
	# 	dAcc['EMAIL'] = mc.enterVerifyEmail(email=dAcc['EMAIL'])
	# 	# Populate MC Campaign IDs
	# 	dAcc = populate_MC_Campaign_IDs(dAcc)
	# 	dMC, dTags = dicts.get_mailchimp_add_update_dict(dAcc)
	# 	is_mc_successful = mc.addUpdateMember(client, listID=dAcc['MCAUDID'], dMC=dMC, upDateOnly=False, dTags=dTags)
	
	# Confirm data entry
	is_mc_successful = False
	confirm_data_entry()

	
exit()

