# Account Entry Funtcions for TerraForce

import lao
import bb
import cpypg
import dicts
import fun_text_date as td
import mc
from pprint import pprint
import pyperclip
import re
from rapidfuzz import fuzz, process
from sys import exit
from webbrowser import open as openbrowser
import webs

def getBlankAccountDictionary():
	td.warningMsg('\n acc.getBlankAccountDictionary() is deprecated. Use dicts.get_blank_account_dict() instead.')
	exit('\n Terminating program...')

# Populate dAcc from TerraForce data with AID, EID or PID
def populate_dAcc_from_tf(service, ContactID, dAcc='None'):
	# Check if existing TF dictionary exisits

	if dAcc == 'None':
		dAcc = dicts.get_blank_account_dict()
	
	# Check if ContactID a PID and
	lStatesAbb = lao.getCounties('StateAbb')
	if ContactID[:2] in lStatesAbb:
		PID = ContactID
		# TerraForce Query
		wc = "PID__c = '{PID}'".format(PID=PID)
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None)
		if results:
			d = results[0]
			if d['AccountId__c'] != 'None':
				ContactID = d['AccountId__c']
			elif d['Owner_Entity__c'] != 'None':
				ContactID = d['Owner_Entity__c']
		else:
			td.warningMsg(f"\n No Deal found for PID: {PID}")
			return dAcc

	# TerraForce Query
	rec_type = 'Person'
	wc = f"Id = '{ContactID}'"
	results = bb.tf_query_3(service, rec_type=rec_type, where_clause=wc, limit=None)
	d = results[0]

	# Check if Person or Entity
	if d['FirstName'] == 'None' and d['LastName'] == 'None':
		rec_type = 'Entity'
		wc = f"Id = '{ContactID}'"
		results = bb.tf_query_3(service, rec_type=rec_type, where_clause=wc, limit=None)
		d = results[0]

	# Populate dAcc fields with TF data
	dAcc['CATEGORY'] = d['Category__c']
	dAcc['CITY'] = d['BillingCity']
	dAcc['DESCRIPTION'] = d['Description']
	dAcc['LINKEDIN'] = d['LinkedIn_Url__c']
	dAcc['PHONE'] = d['Phone']
	dAcc['STATE'] = td.make_title_case(d['BillingState'])
	dAcc['STREET'] = td.titlecase_street(d['BillingStreet'])
	dAcc['WEBSITE'] = d['Website']
	dAcc['ZIPCODE'] = d['BillingPostalCode']

	if rec_type == 'Person':
		dAcc['AID'] = d['Id']
		dAcc['CCID'] = d['CC_ID__c']
		if d['Company__c'] != 'None':
			dAcc['EID'] = d['Company__c']		# Entity ID
			dAcc['ENTITY'] = d['Company__r']['Name']
		dAcc['EMAIL'] = d['PersonEmail'].lower()
		dAcc['EMAILOPTOUT'] = d['PersonHasOptedOutOfEmail']
			# Company
		dAcc['MOBILE'] = d['PersonMobilePhone']
		dAcc['NAME'] = d['Name']			# Person Name
		dAcc['NF'] = d['FirstName']			# First Name
		dAcc['NM'] = d['MiddleName__c']			# Middle Name
		dAcc['NL'] = d['LastName']			# Last Name
		dAcc['PHONEHOME'] = d['PersonHomePhone']
		dAcc['TITLEPERSON'] = td.make_title_case(d['PersonTitle'])
		try:
			dAcc['TOP100AGENT'] = d['Top100__c']
		except KeyError:
			pass

	elif rec_type == 'Entity':
		dAcc['EID'] = d['Id']				# Entity ID
		dAcc['ENTITY'] = d['Name']			# Entity Name

	dAcc = td.address_formatter(dAcc)
	return dAcc

# Build Account Dictionary
def buildAccountDictionary(d):
	td.warningMsg('\n acc.buildAccountDictionary() is deprecated.')

# Have user enter a contact name if none given
def enterContactName(d):

	if d['NAME'] == 'None':
		# No Person with Unknown Entity
		if 'UNKNOWN' in d['ENTITY'].upper():
			d['NAME'] = 'None'
			return d
		# Check websites for Entity contact
		# elif d['ENTITY'] != 'None:
			# from webs import getEntityContact
		# 	driver = getEntityContact(d['ENTITY'], STATE=d['STATE'])
		d['NAME'] = (td.uInput('\n Enter full Person Name, [Enter] to skip or [00] to Quit > ')).upper()
		if d['NAME'] == '00':
			exit('\n Terminating program...')
		if d['NAME'] == '':
			d['NAME'] = 'None'
			return d
		else:
			return d
	else:
		return d

# Let the user change the name of the contact
def changeNameOption(dAcc):
	td.banner('Confirm Contact Name')
	lao.print_function_name('acc def changeNameOption')
	
	while 1:
		# Remove CRs from BillingStreet
		# print_dAcc_info(dAcc, highlight='PERSON')
		print(' Confirm or Change Contact Name')
		td.colorText('\n {0}'.format(dAcc['NAME']), 'ORANGE')
		ui = (td.uInput('\n - Type a different Name\n - [Enter] to use this one\n - Quit [00]\n\n --> ')).upper()
		print(ui)
		if ui == '':
			dAcc['AUTOFORMAT'] = True
			break
		elif ui == 'Q' or ui == '00':
			exit('Terminating program...')
		else:
			# NAME, CITY, STATE = ui, '', ''
			dAcc['NAME'] = ui
			break
	return dAcc

# Format the contact name into First, Middle & Last Name
def formatContactName(dAcc):
	# import lao
	lao.print_function_name('acc def formatContactName')

	if dAcc['FASTMODE'] or dAcc['AUTOFORMAT']:
		lNAME = dAcc['NAME'].split(' ')
		lenName = len(lNAME)
		if lenName > 2:
			if lenName == 3:  # and 'VAN' == lNAME[1] or 'Van' == lNAME[1]:
				l_2_last_names = ['VAN', 'VON', 'SAINT', 'ST', 'DE', 'DEL']
				if lNAME[1].upper() in l_2_last_names:
					dAcc['NL'] = '{0} {1}'.format(lNAME[1], lNAME[2])
				else:
					dAcc['NL'] = lNAME[lenName-1]
			dAcc['NF'] = lNAME[0]
		else:
			dAcc['NF'], dAcc['NL'] = dAcc['NAME'].split(' ')
		dAcc['NFI'] = dAcc['NF'][:1]
		dAcc['NM'] = ''
	else:
		dAcc['NAME'], dAcc['NF'], dAcc['NM'], dAcc['NL'] = td.parse_person(dAcc['NAME'])
		dAcc['NFI'] = dAcc['NF'][:1]
	dAcc['NL'] = dAcc['NL'].replace("'", "")
	return dAcc

def getContactTFInfo(service, AID):
	# TerraForce Query
	wc = f"Id = '{AID}'"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
	return results[0]

# Check if person exists in TF
def queryTFForContact(service, dAcc):
	lao.print_function_name('acc def formatContactName')

	# qs = "SELECT FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState, BillingPostalCode, Id, Category__c, Company__c, Company__r.Name, Name, CreatedById, Description, PersonEmail, Phone, PersonMobilePhone, PersonHomePhone, PersonHasOptedOutOfEmail, PersonContactId FROM Account WHERE LastName = '" + dAcc['NL'] + "' AND "
	wc = "LastName = '{NL}' AND ".format(**dAcc)

	matchDefinate = False
	matchPotential = True
	
	# check for name variations and add to query
	if 'WILL' in dAcc['NF'].upper() or 'BILL' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Will%' or FirstName LIKE 'Bill%')"
	elif 'JIM' in dAcc['NF'].upper() or 'JAMES' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Jim%' or FirstName LIKE 'James%')"
	elif 'DAVE' in dAcc['NF'].upper() or 'DAVID' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Dav%' or FirstName LIKE 'David%')"
	elif 'MIKE' in dAcc['NF'].upper() or 'MICHAEL' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Mike%' or FirstName LIKE 'Michael%')"
	elif 'TOM' in dAcc['NF'].upper() or 'THOMAS' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Tom%' or FirstName LIKE 'Thomas%')"
	elif 'ROB' in dAcc['NF'].upper() or 'BOB' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Rob%' or FirstName LIKE 'Bob%')"
	elif 'STEW' in dAcc['NF'].upper() or 'STUA' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Stew%' or FirstName LIKE 'Stua%')"
	elif 'SEAN' in dAcc['NF'].upper() or 'SHAWN' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Sean%' or FirstName LIKE 'Shawn%')"
	elif 'TIM' in dAcc['NF'].upper() or 'TIMOTHY' in dAcc['NF'].upper():
		addToQS = "(FirstName LIKE 'Tim%' or FirstName LIKE 'Timothy%')"
	else:
		# addToQS = "FirstName LIKE '{0}%'".format(dAcc['NFI'])
		addToQS = "FirstName LIKE '{NFI}%'".format(**dAcc)
		matchPotential = False
	# qs = '{0}{1}'.format(qs, addToQS)
	wc = f'{wc}{addToQS}'
	# print(wc)
	# print()

	# results = bb.sfXquery(service, qs)
	# TerraForce Query
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
	return results, matchDefinate, matchPotential
	# print(results)

# User to select possible matches in TF
def selectPotentialContactMatchesInTF(results, dAcc, matchDefinate, matchPotential):
	lao.print_function_name('acc def selectPotentialContactMatchesInTF')

	#list matches to choose from
	ui = 0
	# Get Area Code by State dict
	dAreaCodes = lao.getAreaCodesDict()
	print('     {0:22.22} {1:23.23} {2:15.15} {3:2.2} {4:14.14} {5}'.format(dAcc['NAME'], dAcc['ENTITY'], dAcc['CITY'], dAcc['STATE'], dAcc['PHONE'], dAcc['EMAIL']))
	print('-' * 50)
	td.instrMsg(' Select existing TF record\n')
	print(' 0 ) No Match')
	i = 0
	autoMatchCount = 0
	for raw_row in results:
		row = raw_row
		# Replace null rows with ''
		for key in row:
			if row[key] is None:
				row[key] = ''
		i += 1
		n = str(i)
		# Get Company for list if exists
		company = ''
		if row['Company__r'] != 'None':
			company = row['Company__r']['Name']
		# Construct Full Name for List
		if row['MiddleName__c'] == 'None':
			fullName = '{0} {1}'.format(row['FirstName'], row['LastName'])
		else:
			fullName = '{0} {1} {2}'.format(row['FirstName'], row['MiddleName__c'], row['LastName'])
		# Check if an Exact Match
		if dAcc['NF'].upper() == row['FirstName'].upper():
			fullName = 'XX {0}'.format(fullName)
			matchPotential = True
			# Check if Company matches
			if company != '':
				if company.upper() == dAcc['ENTITY'].upper():
					matchDefinate = True
				elif len(company) > 16:
					if company[:15].upper() == dAcc['ENTITY'][:15].upper():
						matchDefinate = True
		elif dAcc['NF'][:4].upper() == row['FirstName'][:4].upper():
			fullName = '44 {0}'.format(fullName)
			matchPotential = True
		elif dAcc['NF'][:3].upper() == row['FirstName'][:3].upper():
			fullName = '33 {0}'.format(fullName)
			matchPotential = True
		elif dAcc['NF'][:2].upper() == row['FirstName'][:2].upper():
			fullName = '22 {0}'.format(fullName)
			matchPotential = True

		# Add State
		if row['BillingState'] != 'None':
			state = row['BillingState']
		# If no State then deduce it from Area Code
		elif row['Phone'] != 'None':
			areaCode = td.phoneFormat(row['Phone'], 'MailChimp')[:3]
			try:
				state = '{0}(Ph)'.format(dAreaCodes[areaCode])
			except KeyError:
				state = ''
		else:
			state = ''
		# Print the Index Number, Name, Company, City, State & Created By
		if 'XX ' in fullName:
			fullName = fullName.replace('XX ', '')
			# print('      {0:20}  {1:20}  {2:20} {3:2} {4:14} {4}'.format(dAcc['NAME'], dAcc['ENTITY'], dAcc['CITY'], dAcc['STATE'], dAcc['PHONE',] dAcc['EMAIL']))
			td.instrMsg(' {0:2}) {1:22.22} {2:23.23} {3:15.15} {4:2.2} {5:14.14} {6}'.format(n, fullName, company, row['BillingCity'],state, row['Phone'], row['PersonEmail']))
			#td.instrMsg(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
		elif '22 ' in fullName or '33 ' in fullName or '44 'in fullName:
			fullName = fullName.replace('22 ', '')
			# lao.cyanMsg(' {0:2}) {1:22.22} {2:23.23} {3:15.15} {4:2.2} {5:14.14} {6}'.format(n, fullName, company, row['BillingCity'],state, row['Phone'], row['PersonEmail']))
			td.colorText(' {0:2}) {1:22.22} {2:23.23} {3:15.15} {4:2.2} {5:14.14} {6}'.format(n, fullName, company, row['BillingCity'],state, row['Phone'], row['PersonEmail']), 'CYAN')
			# lao.cyanMsg(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
		else:
			print(' {0:2}) {1:22.22} {2:23.23} {3:15.15} {4:2.2} {5:14.14} {6}'.format(n, fullName, company, row['BillingCity'],state, row['Phone'], row['PersonEmail']))
			#print(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
		if (dAcc['STATEOFORIGIN'] in state and 'XX ' in fullName):
			autoMatchCount += 1
			autoMatchUI = n
		if matchDefinate:
			autoMatchUI = n
			break
	# User select from possible matches in TF
	while 1:
		if dAcc['FASTMODE'] is True and matchPotential is False:
			ui = 0
			break
		elif dAcc['FASTMODE'] is True and autoMatchCount == 1:
			ui = int(autoMatchUI)
			break
		elif dAcc['FASTMODE'] is True and matchDefinate is True:
			ui = int(autoMatchUI)
			break
		td.instrMsg('\n Type 411 & Index number (i.e. 4111 for the 1st on the list) to open TF record for a listed Account or 1000 to skip')
		try:
			ui = int(td.uInput('\n Select person or 0 for no match... > '))
		except (SyntaxError, ValueError):
			td.warningMsg('\n Entry must be a number, try again...\n')
			continue
		# Open in browser
		if '411' in str(ui):
			sui = str(ui)
			sui = sui.replace('411', '')
			sui = int(sui) - 1
			aid = results[sui]['Id']
			openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(aid))
			continue
		break
	return ui

# Convert dAcc field that are None (null) or '' to 'None'
def dict_blank_fields_to_none(dictionary):
	lao.print_function_name('acc def dict_blank_fields_to_none', skipit=True)

	for key in dictionary:
		if dictionary[key] == '' or dictionary[key] == None:
			dictionary[key] = 'None'
	return dictionary

# Get the data of existing TF Contact and update blank fields
def getUpdateExistingContactData(service, dAcc, dTFCon):
	lao.print_function_name('acc def getUpdateExistingContactData')
	
	dAcc = dict_blank_fields_to_none(dAcc)
	dTFCon = dict_blank_fields_to_none(dTFCon)

	dAcc['UPDATERECORD'] = False
	dAcc['NF'] = dTFCon['FirstName']
	dAcc['NL'] = dTFCon['LastName']
	dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	dAcc['AID'] = dTFCon['Id']
	print('\n {0} selected...Updating existing account...'.format(dAcc['NAME'] ))
	dTFCon['ValidEmail'] = ''

	# Update blank fields
	# BillingCity, BillingState, Id, Category__c, Company__c, Company__r.Name, Name, CreatedById, Description, PersonEmail, Phone,
	dup = {'type': 'Account', 'id': dAcc['AID']}

	# Add address if none
	if dTFCon['BillingStreet'] == 'None':
		if dAcc['STREET'] != 'None':
			STREET = td.titlecase_street(dAcc['STREET'])
			dup['BillingStreet'] = STREET
			dup['BillingCity'] = dAcc['CITY'].title()
			dup['BillingState'] = dAcc['STATE']
			dAcc['STATEOFORIGIN'] = dAcc['STATE']
			dup['BillingPostalCode'] = dAcc['ZIPCODE']
			dAcc['UPDATERECORD'] = True
		# No Billing Address so ask user to enter one if available
		else:
			td.warningMsg('\n Contact is missing an address...')
			dAcc = get_missing_address(dAcc, search_for='Person Address')

	# Address Mismatch allow user to update
	if dAcc['STREET'] != 'None':
		update_account = False
		mismatch_street = False
		mismatch_city = False
		mismatch_state = False
		mismatch_zipcode = False
		lStreet = dAcc['STREET'].split(' ')
		if not lStreet[0].upper() in dTFCon['BillingStreet'].upper():
			update_account = True
			mismatch_street = True
		if not lStreet[1].upper() in dTFCon['BillingStreet'].upper():
			update_account = True
			mismatch_street = True
		if dAcc['CITY'] != 'None' and dTFCon['BillingCity'].upper() != dAcc['CITY'].upper():
			update_account = True
			mismatch_city = True
		if dAcc['STATE'] != 'None' and dTFCon['BillingState'].upper() != dAcc['STATE'].upper():
			update_account = True
			mismatch_state = True
		if dAcc['ZIPCODE'] != 'None' and str(dTFCon['BillingPostalCode']) != str(dAcc['ZIPCODE']):
			update_account = True
			mismatch_zipcode = True
		if update_account:
			td.warningMsg('\n POSSIBLE ADDRESS MISMATCH\n')
			msg = \
				' ADDRESS IN TF      {0}\n' \
				'                    {1}, {2} {3}\n\n' \
				' UPDATE ADDRESS     {4}\n' \
				'                    {5}, {6} {7}\n' \
			.format(
				dTFCon['BillingStreet'],
				dTFCon['BillingCity'],
				dTFCon['BillingState'],
				dTFCon['BillingPostalCode'],
				dAcc['STREET'],
				dAcc['CITY'],
				dAcc['STATE'],
				dAcc['ZIPCODE'])
			print(msg)

			# Update Address ask user
			if mismatch_street:
				ui = td.uInput('\n Update Address in TF [0/1/00] > ')
				if ui == '1':
					STREET = td.titlecase_street(dAcc['STREET'])
					dup['BillingStreet'] = STREET
					dup['BillingCity'] = dAcc['CITY'].title()
					dup['BillingState'] = dAcc['STATE']
					dup['BillingPostalCode'] = dAcc['ZIPCODE']
					print('\n Address updated...\n')
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n Address not updated.')
				mismatch_city = False
				mismatch_state = False
				mismatch_zipcode = False
			if mismatch_city:
				ui = td.uInput('\n Update CITY in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingCity'] = dAcc['CITY'].title()
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n City not updated.')
			if mismatch_state:
				ui = td.uInput('\n Update STATE in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingState'] = dAcc['STATE']
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n State not updated.')
			if mismatch_zipcode:
				ui = td.uInput('\n Update ZIP CODE in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingPostalCode'] = dAcc['ZIPCODE']
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n Zip Code not updated.')

	# Add Category
	if 'CATEGORY' in dAcc.keys():
		if dAcc['CATEGORY'] != 'None':
			dAcc['UPDATERECORD'] = True
			# Create a list of dAcc Categories
			if ';' in dAcc['CATEGORY']:
				lCategory_dACC = dAcc['CATEGORY'].split(';')
			else:
				lCategory_dAcc = [dAcc['CATEGORY']]
			
			# Create a list of dTFCon Categories
			if dTFCon['Category__c'] == 'None':
				lCategory_dTFCon = []
			elif ';' in dTFCon['Category__c']:
				lCategory_dTFCon = dTFCon['Category__c'].split(';')
			
			# Write Categories to dup
			dup['Category__c'] = ';'.join(lCategory_dAcc)
			if lCategory_dTFCon != []:
				for cat in lCategory_dTFCon:
					dup['Category__c'] = '{0};{1}'.format(dup['Category__c'], cat)

	# Add Mobile
	if dTFCon['PersonMobilePhone'] == 'None' and dAcc['MOBILE'] != 'None':
		dAcc['MOBILE'] = td.phoneFormat(dAcc['MOBILE'])
		dup['PersonMobilePhone'] = dAcc['MOBILE']
		dAcc['UPDATERECORD'] = True

	# Add Home Phone
	try:
		if dTFCon['PersonHomePhone'] == 'None' and dAcc['PHONEHOME'] != 'None':
			dAcc['PHONEHOME'] = td.phoneFormat(dAcc['PHONEHOME'])
			dup['PersonHomePhone'] = dAcc['PHONEHOME']
			dAcc['UPDATERECORD'] = True
	except KeyError:
		pass

	# Add Phone if None
	if dTFCon['Phone'] == 'None' and dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
		dup['Phone'] = dAcc['PHONE']
		dAcc['UPDATERECORD'] = True

	# Add Phone to 'Other Phone' if different from number already entered
	elif dTFCon['Phone'] != 'None' and dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		# Remove punctuation just leaving digits
		tfPhone = re.sub("[^0-9]", "", dTFCon['Phone'])
		uiPhone = re.sub("[^0-9]", "", dAcc['PHONE'])
		if tfPhone != uiPhone:
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			dup['PersonOtherPhone'] = dAcc['PHONE']
			dAcc['UPDATERECORD'] = True
	
	# Give user option to add Phone if none exists
	elif dTFCon['Phone'] == 'None' and dAcc['PHONE'] == 'None' and dTFCon['PersonMobilePhone'] == 'None' and dAcc['MOBILE'] == 'None':
		# dAcc = enterPhoneNumber(dAcc)
		dAcc = get_missing_phone(dAcc, search_for='Person Phone')
		if dAcc['PHONE'] != 'None' or dAcc['PHONE'] != 'Skip':
			dup['Phone'] = dAcc['PHONE']
			dAcc['UPDATERECORD'] = True

	# Update Company
	if dAcc['EID'] != 'None' and dTFCon['Company__c'] == 'None':
		dup['Company__c'] = dAcc['EID']
	elif dAcc['ENTITY'] != 'None' and dTFCon['Company__c'] == 'None':
		dAcc = find_create_account_entity(service, dAcc)
		dup['Company__c'] = dAcc['EID']
		dAcc['UPDATERECORD'] = True
	# Mismatched companies
	elif dAcc['EID'] != 'None' and dTFCon['Company__c'] != 'None':
		if dAcc['EID'] != dTFCon['Company__c']:
			td.warningMsg('\n POSSIBLE COMPANY MISMATCH\n')
			msg = \
				' COMPANY IN TF     {0}\n\n' \
				' UPDATE COMPANY    {1}\n' \
			.format(
				dTFCon['Company__r']['Name'],
				dAcc['ENTITY'])
			print(msg)
			ui = td.uInput('\n Update company in TF [0/1/00] > ')
			if ui == '1':
				dup['Company__c'] = dAcc['EID']
			elif ui == '00':
				exit('\n Terminating program...')
	# Update Email
	if dAcc['EMAIL'] != 'None':
		# Add Email to Account if blank
		if dTFCon['PersonEmail'] == 'None':  # Add Email to Account
			dup['PersonEmail'] = dAcc['EMAIL']
			dAcc['UPDATERECORD'] = True
		elif dTFCon['PersonEmail'].lower() != dAcc['EMAIL'].lower():
			print('\n Email in TF: {0}'.format(dTFCon['PersonEmail'].lower()))
			print(' New Email  : {0}'.format(dAcc['EMAIL'].lower()))
			uin = td.uInput('\n Update Email Address? [0/1/00] > ')
			if uin == '1':
				if dTFCon['PersonEmail'].lower() in dTFCon['Description']:
					pass
				elif dTFCon['Description'] == 'None':
					dAcc['DESCRIPTION'] = 'Possible email: {0}'.format(dTFCon['PersonEmail'].lower())
				elif uin == '00':
					exit('\n Terminating program...')
				else:
					dAcc['DESCRIPTION'] = '{0}\r\nPossible email: {0}'.format(dTFCon['Description'], dTFCon['PersonEmail'].lower())
				dup['PersonEmail'] = dAcc['EMAIL']
				dup['Description'] = dAcc['DESCRIPTION']
				dAcc['UPDATERECORD'] = True
	elif dAcc['EMAIL'] == 'None' and dTFCon['PersonEmail'] == 'None':
		while 1:
			uin = td.uInput('\n Add Email Address or [Enter] for none > ')
			if uin == '':
				break
			elif '@' not in uin:
				td.warningMsg('\n Improperly formatted email address...try again...')
			else:
				dAcc['EMAIL'] = uin
				dup['PersonEmail'] = dAcc['EMAIL']
				dAcc['UPDATERECORD'] = True
				break

	if dAcc['UPDATERECORD'] is True:
		bb.tf_update_3(service, dup)
		dAcc['UPDATERECORD'] = False

	return dAcc

# Get Entity Info
def getEntityInfo(service, dAcc):
	lao.print_function_name('acc def getEntityInfo')
	# TerraForce Query
	wc = "Id = '{EID}'".format(**dAcc)
	ent_results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None)

	if dAcc['STREET'] == 'None' and ent_results[0]['BillingStreet'] != 'None':
		dAcc['STREET'] = ent_results[0]['BillingStreet']
		dAcc['CITY'] = ent_results[0]['BillingCity']
		dAcc['STATE'] = ent_results[0]['BillingState']
		dAcc['STATEOFORIGIN'] = ent_results[0]['BillingState']
		dAcc['ZIPCODE'] = ent_results[0]['BillingPostalCode']
		# dAcc = addressFormater(dAcc)
		dAcc = td.address_formatter(dAcc)
	if dAcc['PHONE'] == 'None' and  ent_results[0]['Phone'] != 'None':
		dAcc['PHONE'] = ent_results[0]['Phone']

	return dAcc
	
# Add new Contact Info
def addNewContactInfo(dAcc):
	lao.print_function_name('acc def addNewContactInfo')

	dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	print('\n This is a new Person...')
	print('\n {0}\n {1}\n {2}, {3} {4}\n Phone: {5}\n Email: {6}'.format(dAcc['NAME'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'], dAcc['PHONE'], dAcc['EMAIL']))
	# User input Address
	if dAcc['STREET'] == 'None':
		dAcc = get_missing_address(dAcc, search_for='Person Address') 
	if dAcc['STREET'] == '':
		dAcc['STREET'] = 'None'

	return dAcc

# User to enter Phone
def enterPhoneNumber(dAcc):
	lao.print_function_name('acc def enterPhoneNumber')

	# PHONE, MOBILE, descriptionPhone = 'None', 'None', 'None'
	# while 1:
	if dAcc['PHONE'] == 'Skip':
		dAcc['PHONE'] = 'None'
		return dAcc
	elif dAcc['PHONE'] == 'None' or dAcc['PHONE'] == '':
		dAcc = cpypg.start_cpypg(dAcc)
		return dAcc
		# Format name if first name key does not exist
		if not 'NF' in dAcc:
			dAcc = formatContactName(dAcc)
		while 1:
			print('\n {0}\n {1}\n {2}\n {3}, {4} {5}\n'.format(dAcc['NAME'], dAcc['ENTITY'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))
			print('\n\n Enter phone number (any format),\n   [ 1] True People Search\n   [ 2] Fast People Search\n   [Enter] for none\n   [00] Quit\n').upper()
			ui = td.uInput(' Phone > ')
			if ui == '1':
				if 'NM' in dAcc:
					if dAcc['NM'] == '':
						tps_name = '{0}%20{1}'.format(dAcc['NF'], dAcc['NL'])
					else:
						tps_name = '{0}%20{1}%20{2}'.format(dAcc['NF'], dAcc['NM'], dAcc['NL'])
				else:
					dAcc['NM'] = ''
					tps_name = '{0}%20{1}'.format(dAcc['NF'], dAcc['NL'])
				tps_url = 'https://www.truepeoplesearch.com/results?name={0}&citystatezip={1},%20{2}'.format(tps_name, dAcc['CITY'], dAcc['STATE'])
				openbrowser(tps_url)
				dAcc['PHONE'], dAcc['MOBILE'], dAcc['DESCRIPTION'] = lao.getTruePeopleSearchPhoneNumbers()
				break
			elif ui == '2':
				if dAcc['NM'] == '':
					fps_name = '{0}-{1}'.format(dAcc['NF'], dAcc['NL'])
				else:
					fps_name = '{0}-{1}-{2}'.format(dAcc['NF'], dAcc['NM'], dAcc['NL'])
				fps_url = 'https://www.fastpeoplesearch.com/name/{0}_{1}-{2}'.format(fps_name, dAcc['CITY'], dAcc['STATE'])
				openbrowser(fps_url)
			elif ui != '':
				dAcc['PHONE'] = td.phoneFormat(ui)
				break
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				dAcc['PHONE'] = 'None'
				break

	return dAcc

# Create Contact
def createNewContact(service, dAcc):
	lao.print_function_name('acc def createNewContact')

	print('\n Creating Person Account: {0}'.format(dAcc['NAME']))
	# Build dictionary
	dCreate = {'type': 'Account', 'FirstName': dAcc['NF'], 'LastName': dAcc['NL']}
	if dAcc['STREET'] != 'None':
		STREET = td.titlecase_street(dAcc['STREET'])
		dCreate['BillingStreet'] = STREET
		dCreate['BillingCity'] = dAcc['CITY'].title()
		dCreate['BillingState'] = dAcc['STATE']
		dCreate['BillingPostalCode'] = dAcc['ZIPCODE']
	if dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		dCreate['Phone'] = dAcc['PHONE']
	if 'PHONEOTHER' in dAcc.keys():
		if dAcc['PHONEOTHER'] != 'None' and dAcc['PHONEOTHER'] != 'Skip':
			dCreate['PersonOtherPhone'] = dAcc['PHONEOTHER']
	if dAcc['EMAIL'] != 'None' and dAcc['EMAIL'] != 'Not':
		dCreate['PersonEmail'] = dAcc['EMAIL']
	if dAcc['NM'] != 'None' and dAcc['NM'] != '':
		dCreate['MiddleName__c'] = dAcc['NM']
	if dAcc['EID'] != 'None':
		dCreate['Company__c'] = dAcc['EID']
	if dAcc['MOBILE'] != 'None' and dAcc['MOBILE'] != 'Skip':
		dCreate['PersonMobilePhone'] = dAcc['MOBILE']
	if dAcc['DESCRIPTION'] != 'None':
		dCreate['Description'] = dAcc['DESCRIPTION']
	if 'CATEGORY' in dAcc.keys():
		if dAcc['CATEGORY'] != 'None':
			dCreate['Category__c'] = dAcc['CATEGORY']
	if 'TITLEPERSON' in dAcc.keys():
		if dAcc['TITLEPERSON'] != 'None':
			dCreate['PersonTitle'] = dAcc['TITLEPERSON']
	if 'WEBSITE' in dAcc.keys():
		if dAcc['WEBSITE'] != 'None':
			dCreate['Website'] = dAcc['WEBSITE']


	# Assemble Category List
	categoryList = ''

	if dAcc['AGENT'] != 'None':
		for agentRow in dAcc['AGENT']:
			categoryList = '{0};{1}'.format(categoryList, agentRow)
	if categoryList != '':
		categoryList = categoryList.replace(';', '', 1)
		print(categoryList)
		dCreate['Category__c'] = categoryList
	if dAcc['CCID'] != 'None':
		dCreate['CC_ID__c'] = dAcc['CCID']

	# try:
	dAcc['AID'] = bb.tf_create_3(service, dCreate)

	# Create a Note for the contact
	if dAcc['NOTETITLE'] != 'None':
		bb.create_tf_lightning_note(service, dAcc['NOTETITLE'], dAcc['NOTECONTENT'], dAcc['AID'])
	# except:
	# 	td.warningMsg('\n Could not create record, blocked by TF anti-dup program...')
	# 	print('\n Enter record manually...opening TF...\n')
	# 	openbrowser('https://landadvisors.my.salesforce.com/setup/ui/recordtypeselect.jsp?ent=Account&retURL=%2Fa0L%2Fo&save_new_url=%2F001%2Fe%3FretURL%3D%252Fa0L%252Fo')
	# 	print(' {0}\n {1}\n {2}\n {3}\n {4}\n {5}\n {6}\n {7}'.format(dAcc['NAME'], dAcc['ENTITY'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'], dAcc['PHONE'], dAcc['EMAIL']))
	# 	dAcc['AID'] = td.uInput('\n Enter Account ID [00] > ')
	# 	if dAcc['AID'] == '00':
	# 		exit('\n Terminating program...')

	RTY = 'Person Account'
	return dAcc, RTY

# Create Contact from dAcc dict
def update_existing_contact(service, dAcc):
	lao.print_function_name('acc def update_existing_contact')
	print('\n Updating Person Account: {0}'.format(dAcc['NAME']))
	# Build dictionary
	dUpdate = {'type': 'Account', 'Id': dAcc['AID'], 'FirstName': dAcc['NF'], 'LastName': dAcc['NL']}
	if dAcc['STREET'] != 'None':
		STREET = td.titlecase_street(dAcc['STREET'])
		dUpdate['BillingStreet'] = STREET
		dUpdate['BillingCity'] = dAcc['CITY'].title()
		dUpdate['BillingState'] = dAcc['STATE']
		dUpdate['BillingPostalCode'] = dAcc['ZIPCODE']
	if dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		dUpdate['Phone'] = dAcc['PHONE']
	if 'PHONEOTHER' in dAcc.keys():
		if dAcc['PHONEOTHER'] != 'None' and dAcc['PHONEOTHER'] != 'Skip':
			dUpdate['PersonOtherPhone'] = dAcc['PHONEOTHER']
	if dAcc['EMAIL'] != 'None' and dAcc['EMAIL'] != 'Not':
		dUpdate['PersonEmail'] = dAcc['EMAIL']
	if dAcc['NM'] != 'None' and dAcc['NM'] != '':
		dUpdate['MiddleName__c'] = dAcc['NM']
	if dAcc['EID'] != 'None':
		dUpdate['Company__c'] = dAcc['EID']
	if dAcc['MOBILE'] != 'None' and dAcc['MOBILE'] != 'Skip':
		dUpdate['PersonMobilePhone'] = dAcc['MOBILE']
	if dAcc['DESCRIPTION'] != 'None':
		dUpdate['Description'] = dAcc['DESCRIPTION']
	if 'TITLEPERSON' in dAcc.keys():
		if dAcc['TITLEPERSON'] != 'None':
			dUpdate['PersonTitle'] = dAcc['TITLEPERSON']

	# Handle Categories and Top100 (MVP)
	if dAcc['CATEGORY'] != 'None' or dAcc['TOP100AGENT'] != 'None':
		wc = "Id = '{AID}'".format(**dAcc)
		results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
		
		# Initialize category lists
		current_categories = []
		current_top100 = []
		
		# Get existing categories if any
		if results[0]['Category__c'] not in [None, 'None', '']:
			if isinstance(results[0]['Category__c'], list):
				current_categories = results[0]['Category__c']
			else:
				current_categories = [cat.strip() for cat in results[0]['Category__c'].split(';') if cat.strip()]
				
		# Get existing top100 if any
		if results[0]['Top100__c'] not in [None, 'None', '']:
			if isinstance(results[0]['Top100__c'], list):
				current_top100 = results[0]['Top100__c']
			else:
				current_top100 = [top.strip() for top in results[0]['Top100__c'].split(';') if top.strip()]

		# Add new categories
		if dAcc['CATEGORY'] != 'None':
			new_categories = dAcc['CATEGORY'] if isinstance(dAcc['CATEGORY'], list) else [dAcc['CATEGORY']]
			for cat in new_categories:
				if cat not in current_categories:
					current_categories.append(cat)
			if current_categories:
				dUpdate['Category__c'] = ';'.join(current_categories)

		# Add new top100 agents
		if dAcc['TOP100AGENT'] != 'None':
			new_top100 = dAcc['TOP100AGENT'] if isinstance(dAcc['TOP100AGENT'], list) else [dAcc['TOP100AGENT']]
			for top in new_top100:
				if top not in current_top100:
					current_top100.append(top)
			if current_top100:
				dUpdate['Top100__c'] = ';'.join(current_top100)

	# # Assemble Category & Top100 (MVP) List
	# if dAcc['CATEGORY'] != 'None' or dAcc['TOP100AGENT'] != 'None':
	# 	# TerraForce Query
	# 	wc = "Id = '{AID}'".format(**dAcc)
	# 	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
	# 	lCategory = results[0]['Category__c']
	# 	lTop100 = results[0]['Top100__c']
	# 	if dAcc['CATEGORY'] != 'None':
	# 		for row in dAcc['CATEGORY']:
	# 			if not row in lCategory:
	# 				lCategory.append(row)
	# 		dUpdate['Category__c'] = lCategory
	# 	if dAcc['TOP100AGENT'] != 'None':
	# 		for row in dAcc['TOP100AGENT']:
	# 			if not row in lTop100:
	# 				lTop100.append(row)
	# 		dUpdate['Top100__c'] = lTop100

	# pprint(dUpdate)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	try:
		person_results = bb.tf_update_3(service, dUpdate)
		# dAcc['AID'] = person_results[0]['id']
	except:
		td.warningMsg('\n Could not update record, blocked by TF anti-dup program...')
		print('\n Enter record manually...opening TF...\n')
		openbrowser('https://landadvisors.my.salesforce.com/setup/ui/recordtypeselect.jsp?ent=Account&retURL=%2Fa0L%2Fo&save_new_url=%2F001%2Fe%3FretURL%3D%252Fa0L%252Fo')
		print(' {0}\n {1}\n {2}\n {3}\n {4}\n {5}\n'.format(dAcc['NAME'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'], dAcc['PHONE']))
		dAcc['AID'] = td.uInput(' Enter Account ID [00] > ')
		if dAcc['AID'] == '00':
			exit('\n Terminating program...')

	return person_results
	# RTY = 'Person Account'
	return dAcc

# plaoarses a persons name
def parse_person(dAcc):
	lao.print_function_name('acc def parcePerson')

	PERSON = dAcc['NAME']
	PFN, PLN, PMN = '','',''
	print('\n{0}\n'.format(PERSON))
	# remove commas, '&' and other stuff
	dic = {',':'',' & ':' '}
	for i, j in dic.items():
		PERSON = PERSON.replace(i,j)

	# Proper case the PERSON
	PERSON = lao.propercase(PERSON)

	str = PERSON.split(' ')
	# for i in range(0, len(str)-1):
	# 	str[i] = str[i].strip()
	i = 0
	print('-' * 50)
	# Two name Name
	if len(str) == 2:
		while 1:
			print('\n Name Arrangement Possibilities\n')
			print('  1) {0} {1}'.format(str[0], str[1]))
			print('  2) {0} {1}'.format(str[1], str[0]))
			print(' 00) Quit')
			ui = td.uInput('\n Enter match number > ')
			if ui == '1':
				PFN, PMN, PLN = str[0],'',str[1]
				break
			elif ui == '2':
				PFN, PMN, PLN = str[1],'',str[0]
				break
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				td.warningMsg('\n Invalid input, try again...\n')
	# Name with sufix
	elif str[2] == 'JR' or str[2] == 'JR.' or str[2] == 'SR' or str[2] == 'SR.' or str[2] == 'II' or str[2] == 'III':
		PFN, PMN = str[0], ''
		PLN = '{0} {1}'.format(str[1], str[2])
	# Name with Middle Initial
	else:
		print('\n Name Arrangement Possibilities\n')
		print('  0) NO MATCH')
		print('  1) {0} {1} {2}'.format(str[0], str[1], str[2]))
		print('  2) {0} {1} {2}'.format(str[1], str[2], str[0]))
		print(' 00) Quit')
		ui = td.uInput('\n Enter match number or 0 for no match > ')
		if ui == '1':
			l_2_last_names = ['VAN', 'VON', 'SAINT', 'ST', 'DE', 'DEL']
			if str[1].upper() in l_2_last_names:
				PFN, PNM, PLN = str[0], '', '{0} {1}'.format(str[1], str[2])
			else:
				PFN, PMN, PLN = str[0],str[1],str[2]
		elif ui == '2':
			PFN, PMN, PLN = str[1], str[2], str[0]
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			for name in str:
				i = i + 1
				print('{:2}) {:20}'.format(i, name))
			print
			f = input('Select First Name...')
			print
			l = input('Select Last Name... ')
			print
			try:
				m = input('Select Middle Name/Initial ([ENTER] if none)...')
			except:
				m = 0
			i = 0
			for name in str:
				i = i + 1
				if i == f:
					PFN = name
				if i == l:
					PLN = name
				if i == m:
					PMN = name
	dAcc['NAME'] = '{0} {1}'.format(PFN,PLN)
	dAcc['NF'] = PFN
	dAcc['NL'] = PLN
	return dAcc

# Search for existing Person Account in TF and create one if it does not exist
def find_create_account_person(service, dAcc):
	import fun_update_contact as upcon
	from pprint import pprint
	lao.print_function_name('acc def find_create_account_person')

	# Find Person(s) associated with Entity getUpdateExistingContactDataif Entity exists
	if dAcc['EID'] != 'None' and dAcc['NAME'] == 'None':

		# Check TF if Entity has persons associated with it
		# and allow user to choose one
		dAcc['NAME'], dAcc['AID'] = find_persons_of_entity(service, EID=dAcc['EID'], person='None')

		if dAcc['AID'] != 'None':
			dContact = getContactTFInfo(service, dAcc['AID'] )
			dAcc = upcon.update_contact(service, dAcc, dContact)
			return dAcc['NAME'], dAcc['AID'], dAcc # (RTY)
		
	# Have user enter a contact name if none given
	if dAcc['NAME'] == 'None':
		dAcc = get_missing_person(dAcc)
		
	if dAcc['NAME'] == 'None':
		return 'None', 'None', dAcc

	# Let the user change the name of the contact
	if not dAcc['FASTMODE']:
		dAcc = td.parse_person(dAcc)
		dAcc = changeNameOption(dAcc)
	
	# Format the contact name into First, Middle & Last Name
	dAcc = formatContactName(dAcc)

	# Check if person exists in TF
	results, matchDefinate, matchPotential  = queryTFForContact(service, dAcc)

	# User select posible Accounts that exist in TF
	#   [] value means there is not a matching contact in TF
	newContact = False
	personInTF = None
	if results != []:
		personInTF = selectPotentialContactMatchesInTF(results, dAcc, matchDefinate, matchPotential)
		if personInTF == 0:
			newContact = True
		# Skip record
		elif personInTF == 1000:
			return 'None', 'None', 'None'
	else:
		newContact = True

	# Use existing contact in TF and update their data if blank
	if newContact is False:
		index = personInTF - 1
		dContact = results[index]
		
		# Return AID if DELETECONTACT is True
		if dAcc['DELETECONTACT'] is True:
			dAcc['AID'] = dContact['Id']
			return dAcc
		
		# Update dAcc with dContact data
		dAcc['AID'] = dContact['Id']
		dAcc['TITLEPERSON'] = dContact['PersonTitle']
		dAcc['PHONE'] = dContact['Phone']
		dAcc['STREET'] = dContact['BillingStreet']
		dAcc['CITY'] = dContact['BillingCity']
		dAcc['STATE'] = dContact['BillingState']
		dAcc['ZIPCODE'] = dContact['BillingPostalCode']
		dAcc['MOBILE'] = dContact['PersonMobilePhone']
		dAcc['EMAIL'] = dContact['PersonEmail']
		dAcc['WEBSITE'] = dContact['Website']
		if dContact['Company__c'] != 'None':
			dAcc['EID'] = dContact['Company__c']
			dAcc['ENTITY'] = dContact['Company__r']['Name']
			# Add ENTITY info to dAcc if not already there
			if dAcc['STREET'] == 'None' and dContact['Company__r']['BillingStreet'] != 'None':
				dAcc['STREET'] = dContact['Company__r']['BillingStreet']
				dAcc['CITY'] = dContact['Company__r']['BillingCity']
				dAcc['STATE'] = dContact['Company__r']['BillingState']
				dAcc['ZIPCODE'] = dContact['Company__r']['BillingPostalCode']
			if dAcc['PHONE'] == 'None' and  dContact['Company__r']['Phone'] != 'None':
				dAcc['PHONE'] = dContact['Company__r']['Phone']
			if dAcc['WEBSITE'] == 'None' and dContact['Company__r']['Website'] != 'None':
				dAcc['WEBSITE'] = dContact['Company__r']['Website']
		
		dAcc = upcon.update_contact(service, dAcc, dContact)
		newContact = False
	else:
		newContact = True

	# Add new person or select from list of Entity Contacts
	if dAcc['NAME'] == 'None':
		# Get Contact info from Entity
		if dAcc['EID'] != 'None':
			dAcc = getEntityInfo(service, dAcc)
	
	# Adding new Contact
	#   Skip of Uknown
	if 'UNKNOWN' in dAcc['NAME'].upper() or 'UNKNOWN' in dAcc['ENTITY'].upper():
		newContact = False # Skip adding Contact

	if newContact:

		# Check for Entity info if EID is in the dictionary
		if dAcc['EID'] != 'None':
			dAcc = getEntityInfo(service, dAcc) #zzzzzzzzzzzzzzzzzzzzzzzzz

		# Add address
		if dAcc['STREET'] == 'None':
			dAcc = get_missing_address(dAcc, search_for='Person Address')

		# Assume Phone/Mobile exists if there are numbers in the string else
		# have user enter phone
		if any(i.isdigit() for i in dAcc['PHONE']) or any(i.isdigit() for i in dAcc['MOBILE']):
			pass
		else:
			dAcc = get_missing_phone(dAcc, search_for='Person Phone')
		if dAcc['EMAIL'] == 'None' and dAcc['FASTMODE'] is False:
			# dAcc = enterEmail(dAcc)
			dAcc['EMAIL'] = mc.enterVerifyEmail()
			if dAcc['EMAIL'] == '':
				dAcc['EMAIL'] = 'None'

		# Check if Entity was added in the get_missing_address or get_missing_phone functions
		if dAcc['ENTITY'] != 'None' and dAcc['EID'] == 'None':
			dAcc = find_create_account_entity(service, dAcc)

		# Give user the option to make final changes to the contact
		dAcc = cpypg.info_print_final_confirm(dAcc)

		dAcc, RTY = createNewContact(service, dAcc)

	print

	return dAcc['NAME'], dAcc['AID'], dAcc # (RTY)

def find_create_account_entity(service, dAcc):
	import fun_acc_entity as fae
	import lao
	lao.print_function_name('acc def find_create_account_entity')

	while 1:
		# have user enter name if none given
		# uiName tracks if user input the business name
		# uiName = False
		while 1:
			confirm_entity_name = True
			# Check if Entity Name is None and if so have the user enter it
			dAcc = fae.get_entity_name(dAcc)

			# Determine if NAME is an Entity/Business/Company
			dAcc, user_confirmed_entity = fae.is_entity(dAcc)
			if user_confirmed_entity is False:
				return dAcc
			
			# Check TF for Entity Account
			print('\n Checking TerraForce for Enity Account...')
			# Format Entity NAME
			dAcc['ENTITY'] = td.format_entity_name(dAcc['ENTITY'])

			# Print Entity Name and Info
			streetAbb = td.get_abbreviate_street_name(dAcc['STREET'])
			NAMEHIGHLIGHT = '\n\n      {0:30.30} | {1:25.25} | {2:10.10} | {3:2.2} | {4}'.format(dAcc['ENTITY'], streetAbb, dAcc['CITY'], dAcc['STATE'], dAcc['PHONE'])
			td.colorText(NAMEHIGHLIGHT, 'ORANGE')
			print(' ' + '-' * 100 + '\n')

			# Get Entity NAME query string
			NAMEQUERY = fae.get_entity_name_query_string(dAcc)

			# Query TF to see if Entity record exists returning results
			results = fae.query_tf_for_entity_name(service, NAMEQUERY)

			# Print select from existing records menu
			if results != []:
				# User to select exiting Entity TF record or none
				user_input = fae.select_matching_entity_in_tf(results, dAcc)
				new_entity_name = False

			# No matching Entity in TF user to input new name or continue with existing name
			else:
				dAcc, user_input, new_entity_name, confirm_entity_name = fae.no_matching_entity_in_tf(dAcc)
			
			# User entered different Entity name loop to the begining
			if new_entity_name:
				continue

			# User did not select a listed Entity
			if user_input == 0:
				# if user did not input the Business name (uiName = False)
				#   then ask user if they want to modify the business name
				if confirm_entity_name:
					# Have user confirm Entity Name
					dAcc, new_entity_name = fae.user_confirm_entity_name(dAcc)
				# User entered different Entity name loop to the begining
				if new_entity_name:
					continue

				# User to enter address
				website_search_done = False
				if dAcc['STREET'] == 'None' or dAcc['CITY'] == 'None' or dAcc['STATE'] == 'None' or dAcc['ZIPCODE'] == 'None':
					dAcc = get_missing_address(dAcc, search_for='Entity Address')
					website_search_done = True

				# User to enter Phone
				if dAcc['PHONE'] == 'None':
					dAcc = get_missing_phone(dAcc, search_for='Entity Phone')
					website_search_done = True
				
				if website_search_done is False:
					dAcc = get_general_info(dAcc)
					website_search_done = True

				# '\n  1) Copy/Paste webpage' \
				# '\n  2) Accept info' \
				# '\n     Select field number to edit' \
				# '\n 00) Quit\n'


				# Let user change the Entity name for a True Owner/Buyer if research into the Entity reveals one
				print('\n Did you find a True Owner/Buyer?')
				# Have user confirm Entity Name
				dAcc, new_entity_name = fae.user_confirm_entity_name(dAcc)
				# User entered different Entity name loop to the begining
				if new_entity_name:
					continue

				# User to enter Category
				if dAcc['CATEGORY'] == 'None':
					dAcc['CATEGORY'] = bb.chooseAccountCategory(service)
				
				if dAcc['WEBSITE'] == 'None':
					dAcc['WEBSITE'] = ''


				dNewEntity = {'type': 'Account', 'Name': dAcc['ENTITY'], 'Category__c': dAcc['CATEGORY']}
				if dAcc['STREET'] != 'None':
					dNewEntity['BillingStreet'] = dAcc['STREET']
					dNewEntity['BillingCity'] = dAcc['CITY']
					dNewEntity['BillingState'] = dAcc['STATE']
					dNewEntity['BillingPostalCode'] = dAcc['ZIPCODE']
				if dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
					dNewEntity['Phone'] = dAcc['PHONE']
				if dAcc['WEBSITE'] != 'None':
					dNewEntity['Website'] = dAcc['WEBSITE']
				# Create Entity in TF
				try:
					dAcc['EID'] = bb.tf_create_3(service, dNewEntity)
					# dAcc['EID'] = create_results[0]['id']
				# Capture if TF detects duplicate Entity
				except:
					td.warningMsg('\n Could not create record, blocked by TF anti-dup program...\n\n Enter record manually...opening TF...\n')
					openbrowser('https://landadvisors.my.salesforce.com/setup/ui/recordtypeselect.jsp?ent=Account&retURL=%2Fa0L%2Fo&save_new_url=%2F001%2Fe%3FretURL%3D%252Fa0L%252Fo')
					print(f" {dAcc['ENTITY']}\n {dAcc['STREET']}\n {dAcc['CITY']}\n {dAcc['STATE']}\n {dAcc['ZIPCODE']}\n {dAcc['PHONE']}\n {dAcc['EMAIL']}\n")
					dAcc['EID'] = td.uInput(' Enter Account ID [00] > ')
					if dAcc['EID'] == '00':
						exit('\n Terminating program...')
			
			# User selected an existing Entity in TF
			# Assign selected Entity to EID
			else:
				user_input = user_input-1
				try:
					dAcc['ENTITY'] = results[user_input]['Name']
				except IndexError:
					td.warningMsg('\n Invalid selection...try again...')
					continue
				dAcc['EID'] = results[user_input]['Id']

				# Populate dAcc with selected Entity Address for blank fields
				if dAcc['STREET'] == 'None' and results[user_input]['BillingStreet'] != 'None':
					dAcc['STREET'] = results[user_input]['BillingStreet']
					dAcc['CITY'] = results[user_input]['BillingCity']
					dAcc['STATE'] = results[user_input]['BillingState']
					dAcc['ZIPCODE'] = results[user_input]['BillingPostalCode']
					# dAcc = addressFormater(dAcc)
					dAcc = td.address_formatter(dAcc)
				
				# Populate TF Entity record with dAcc data for blank Address fields
				dupEntity = {'type': 'Account', 'Id': 'None'}
				if dAcc['STREET'] != 'None' and results[user_input]['BillingStreet'] == 'None':
					dupEntity['Id'] = results[user_input]['Id']
					dupEntity['BillingStreet'] = dAcc['STREET']
					dupEntity['BillingCity'] = dAcc['CITY']
					dupEntity['BillingState'] = dAcc['STATE']
					dupEntity['BillingPostalCode'] = dAcc['ZIPCODE']

				# User populate Entity address from web
				if dAcc['STREET'] == 'None' and results[user_input]['BillingStreet'] == 'None':
					dAcc = get_missing_address(dAcc, search_for='Entity Address')
					if dAcc['STREET'] != 'None':
						dupEntity['Id'] = results[user_input]['Id']
						dupEntity['BillingStreet'] = dAcc['STREET']
						dupEntity['BillingCity'] = dAcc['CITY']
						dupEntity['BillingState'] = dAcc['STATE']
						dupEntity['BillingPostalCode'] = dAcc['ZIPCODE']


				# Populate dAcc with selected Entity Phone for blank fields
				if dAcc['PHONE'] == 'None' and results[user_input]['Phone'] != 'None':
					dAcc['PHONE'] = results[user_input]['Phone']
				
				# Populate TF Entity record with dAcc data for blank Phone field
				if dAcc['PHONE'] != 'None' and results[user_input]['Phone'] == 'None':
					dupEntity['Id'] = results[user_input]['Id']
					dupEntity['Phone'] = dAcc['PHONE']

				# User to enter Phone if None in dAcc or results dict
				if dAcc['PHONE'] == 'None' and results[user_input]['Phone'] == 'None':
					# webs.open_google_email_domain_browser(dAcc)
					dAcc = get_missing_phone(dAcc, search_for='Entity Phone')
					# dAcc['PHONE'] = td.uInput('\n Type Phone or [Enter] for none > ')
					if dAcc['PHONE'] == '':
						dAcc['PHONE'] = 'None'
				
				# Populate Website
				if dAcc['WEBSITE'] == 'None' and results[user_input]['Website'] != 'None':
						dAcc['WEBSITE'] = results[user_input]['Website']
				if dAcc['WEBSITE'] != 'None' and results[user_input]['Website'] == '':
						dupEntity['Website'] = dAcc['WEBSITE']
				
				# Update Name
				if dAcc['ENTITY'] != results[user_input]['Name']:
					dupEntity['Name'] = dAcc['ENTITY']

				# Update TF Entity record with dAcc date if dupEntity Id exists
				if dupEntity['Id'] != 'None':
					
					print('here112')
					pprint(dupEntity)
					ui = td.uInput('\n Continue [00]... > ')
					if ui == '00':
						exit('\n Terminating program...')
					
					bb.tf_update_3(service, dupEntity)

				business_dict = results[user_input]
			break
		
		return dAcc

# Checks Entity for existence of Person(s) (Employees, Child Relationships and Offers) and lets user select a Person for Deal record.
def find_persons_of_entity(service, EID = 'None', person = 'None', returnDict = False):
	lao.print_function_name('acc def find_persons_of_entity')

	if EID == 'None':
		pass
	else:
		# find employees of an Entity
		# TerraForce Query
		wc = f"Company__c = '{EID}'"
		dEmp = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)

		# Check if Entity has Child relationships and let user choose and Employee
		# TerraForce Query
		fields = 'default'
		wc = f"Id = '{EID}'"
		dChild = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

		# Check if Entity has Deals with Persons and let user choose a Person
		# TerraForce Query
		fields = 'default'
		wc = f"Owner_Entity__c = '{EID}'"
		dDeals = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

		# Check Offers for Person Account
		# TerraForce Query
		fields = 'default'
		wc = f"Buyer_Entity__c = '{EID}'"
		dOffers = bb.tf_query_3(service, rec_type='Offer', where_clause=wc, limit=None, fields=fields)

		for row in dOffers:
			if row['Buyer__r'] == 'None':
				continue
			notExist = True
			for emp in dEmp:
				if row['Buyer__r']['Id'] == emp['Id']:
					notExist = False
			if notExist:
				dTemp = {}
				dTemp['Name'] = row['Buyer__r']['Name']
				dTemp['FirstName'] = row['Buyer__r']['FirstName']
				dTemp['LastName'] = row['Buyer__r']['LastName']
				dTemp['BillingCity'] = row['Buyer__r']['BillingCity'].title()
				dTemp['BillingState'] = row['Buyer__r']['BillingState']
				STREET = td.titlecase_street(row['Buyer__r']['BillingStreet'])
				dTemp['BillingStreet'] = STREET
				dTemp['Id'] = row['Buyer__r']['Id']
				dTemp['MiddleName__c'] = row['Buyer__r']['MiddleName__c']
				dTemp['Phone'] = row['Buyer__r']['Phone']
				dTemp['PersonEmail'] = row['Buyer__r']['PersonEmail']
				dTemp['type'] = 'Account'
				dTemp['TF_SOURCE'] = 'O'
				dEmp.append(dTemp)
		
		if dChild[0]['AccountLinks__r'] != 'None':
			# No Child Relationships
			for row in dChild[0]['AccountLinks__r']['records']:
				if row['ChildAccount__r'] == 'None':
					continue
				# Child Relationship is not a Person
				if row['ChildAccount__r']['LastName'] == 'None':
					continue
				notExist = True
				for emp in dEmp:
					if row['ChildAccount__r']['Id'] == emp['Id']:
						notExist = False
				if notExist:
					dTemp = {}
					dTemp['Name'] = row['ChildAccount__r']['Name']
					dTemp['FirstName'] = row['ChildAccount__r']['FirstName']
					dTemp['LastName'] = row['ChildAccount__r']['LastName']
					dTemp['BillingCity'] = row['ChildAccount__r']['BillingCity'].title()
					dTemp['BillingState'] = row['ChildAccount__r']['BillingState']
					STREET = td.titlecase_street(row['ChildAccount__r']['BillingStreet'])
					dTemp['BillingStreet'] = STREET
					dTemp['Id'] = row['ChildAccount__r']['Id']
					dTemp['MiddleName__c'] = row['ChildAccount__r']['MiddleName__c']
					dTemp['Phone'] = row['ChildAccount__r']['Phone']
					dTemp['PersonEmail'] = row['ChildAccount__r']['PersonEmail']
					dTemp['type'] = 'Account'
					dTemp['TF_SOURCE'] = 'C'
					dEmp.append(dTemp)

		for row in dDeals:
			if row['AccountId__c'] == 'None':
				continue
			notExist = True
			for emp in dEmp:
				if row['AccountId__c'] == emp['Id']:
					notExist = False
			if notExist:
				dTemp = {}
				dTemp['Name'] = row['AccountId__r']['Name']
				dTemp['FirstName'] = row['AccountId__r']['FirstName']
				dTemp['LastName'] = row['AccountId__r']['LastName']
				dTemp['BillingCity'] = row['AccountId__r']['BillingCity'].title()
				dTemp['BillingState'] = row['AccountId__r']['BillingState']
				STREET = td.titlecase_street(row['AccountId__r']['BillingStreet'])
				dTemp['BillingStreet'] = STREET
				dTemp['Id'] = row['AccountId__c']
				dTemp['MiddleName__c'] = row['AccountId__r']['MiddleName__c']
				dTemp['Phone'] = row['AccountId__r']['Phone']
				dTemp['PersonEmail'] = row['AccountId__r']['PersonEmail']
				dTemp['type'] = 'Account'
				dTemp['TF_SOURCE'] = 'D'
				dEmp.append(dTemp)
		
		# Return Dictionary
		if returnDict:
			return dEmp
		
		# 	#td.uInput(row['AccountId__r']['Name'])
		if dEmp != []:
			print('\n Employees:\n')
			i = 0
			print('  0) No Match')
			
			# print list of possible matches
			for row in dEmp:
				i = i + 1
				personname = 'None'
				if row['MiddleName__c'] == 'None':
					personname = '{0} {1}'.format(row['FirstName'], row['LastName'])
				else:
					personname = '{0} {1} {2}'.format(row['FirstName'], row['MiddleName__c'], row['LastName'])
				if 'TF_SOURCE' in row:
					tf_source = row['TF_SOURCE']
				else:
					tf_source = 'E'
				if personname != 'None':
					# Remove CRs from BillingStreet
					streetAbb = row['BillingStreet']
					streetAbb = streetAbb.replace('\n', ' ').replace('\r', '')
					streetAbb = td.get_abbreviate_street_name(streetAbb)
					print(' {0:2}) {1:22.22} ({2}) {3:32.32} {4:15.15} {5:2.2} {6:14.14}'.format(i, personname, tf_source, streetAbb, row['BillingCity'], row['BillingState'], row['Phone']))
			print(' 00) Quit')
			# User to select match
			while 1:
				matchNum = td.uInput('\n Enter match number or 0 for no match. >  ')
				if matchNum == '00':
					exit('\n Terminating program...')
				try:
					matchNum = int(matchNum)
					if matchNum > i or matchNum == '':
						td.warningMsg('Invalid entry...try again...')
						continue
					break
				except (SyntaxError, ValueError):
					td.warningMsg('\nInvalid input...try again...')
					continue
			matchNum = matchNum - 1  # reduce the match number by one to match the row list
			if matchNum >= 0 and matchNum <= i:
				PERSON = dEmp[matchNum]['Name']
				PERSONID = dEmp[matchNum]['Id']
				# RTY = 'Person Account'
				print(f'\n Returning PERSON: {PERSON}')
				# return PERSON, PERSONID, RTY
				return PERSON, PERSONID

		if person == 'None':
			# PERSON, PERSONID, RTY = 'None', 'None', 'Person Account'
			# return PERSON, PERSONID, RTY
			print('\n No PERSON selected...')
			PERSON, PERSONID = 'None', 'None'
			return PERSON, PERSONID

# parses and address into street, city, state and zip
def parseAddress(address, dAcc):
	lao.print_function_name('acc def parseAddress')

	lAddress = address.splitlines()
	if len(lAddress) == 1:
		lAddress = address.split(', ')
		print(lAddress)
		dAcc['STREET'] = td.titlecase_street(lAddress[0])
		dAcc['CITY'] = lAddress[1].title()
		lStateZip = lAddress[1].split(' ')
		dAcc['STATE'] = lStateZip[0].upper()
		dAcc['ZIPCODE'] = lStateZip[1]
	else:
		dAcc['STREET'] = td.titlecase_street(lAddress[0])
		cityStateZip = lAddress[1]
		if ',' in cityStateZip:
			lcityStateZip = cityStateZip.split(',')
			dAcc['CITY'] = lcityStateZip[0].title()
			lStateZip = lcityStateZip[1]
			lStateZip = lStateZip.split()
			dAcc['STATE'] = lStateZip[0].upper()
			dAcc['ZIPCODE'] = lStateZip[1]
		else:
			print(cityStateZip)
			dAcc['CITY'] = (td.uInput('Enter City  > ')).title()
			dAcc['STATE'] = (td.uInput('Enter State > ')).upper()
			ZIP = cityStateZip[-5:]
	# dAcc = addressFormater(dAcc)
	dAcc = td.address_formatter(dAcc)
	return dAcc

# Print dAcc info
def print_dAcc_info(dAcc, highlight='None'):
	print('\n  Contact Info')
	print('-' * 50 + '\n')
	if highlight == 'ENTITY':
		td.colorText('  Entity:      {ENTITY}'.format(**dAcc), 'ORANGE')
	else:
		print('  Entity:      {ENTITY}'.format(**dAcc))
	if highlight == 'PERSON':
		td.colorText('  Person:      {NAME}'.format(**dAcc), 'ORANGE')
	else:
		print('  Person:      {NAME}'.format(**dAcc))
	msg = \
	'  Title:       {TITLEPERSON}\n\n' \
	'  Address:     {STREET}\n' \
	'               {CITY}, {STATE} {ZIPCODE}\n\n' \
	'  Phone:       {PHONE}\n' \
	'  Mobile:      {MOBILE}\n' \
	'  Email:       {EMAIL}\n' \
	'  Website:     {WEBSITE}\n\n' \
	.format(**dAcc)
	print(msg)

# Open website menu to research contact info
# search_for values: Entity Address, Entity Phone, General, Person Address, Person Name, Person Phone
#########################################################################################
# Calls fuction in webs.open_contact_websites ###########################################
#########################################################################################
def open_contact_websites_menu(dAcc, search_for='None'):
	lao.print_function_name('acc def open_contact_websites_menu')
	
	# Print dAcc info and websites menu
	print_dAcc_info(dAcc)

	# print('here2')
	# print('\n search_for = {0}'.format(search_for))

	msg_address = \
		'\n COPY/PASTE OPTIONS' \
		'\n  1) Copy/Paste webpage' \
		'\n  2) Type/paste in full address' \
		'\n  3) Type/paste in street & suite\n' \
		'\n ACCEPT INFO OPTIONS' \
		'\n  4) Accept Info' \
		'\n 99) No address leave blank' \
		'\n 00) Quit\n'
	msg_phone = \
		'\n COPY/PASTE OPTIONS' \
		'\n  1) Copy/Paste webpage' \
		'\n  2) Type or paste in phone\n' \
		'\n NO PHONE OPTIONS' \
		'\n 99) No phone leave blank' \
		'\n 00) Quit\n'
	msg_person = \
		'\n     Type in Person Name' \
		'\n 99) No Person leave blank' \
		'\n 00) Quit\n'
	msg_general = \
		'\n  1) Copy/Paste webpage' \
		'\n  2) Accept info' \
		'\n     Select field number to edit' \
		'\n 00) Quit\n'
	msg_search_sites_entity = \
		'\n GOOGLE (optional)                OPEN WEBSITE (optional)' \
		'\n  10) Entity Name & Address         20) AZ Corporation Commission' \
		'\n  11) Entity Name Only              21) Dunn & Bradstreet Hoovers' \
		'\n  14) Address Only                  23) Florida Sunbiz' \
		'\n  15) Email                         24) OpenCorporates' \
		'\n                                    25) Yellow Pages' \
		'\n\n EnformionGO (optional)         AI PROMPT TO CLIPBOARD (optional)' \
		'\n  35) Entity Name                   50) AI Prompt' \
		'\n  '
	msg_search_sites_person = \
		'\n GOOGLE (optional)                Fast People Search (optional)' \
		'\n  12) Person Name & Address         22) Name' \
		'\n  13) Person Name Only' \
		'\n  14) Address Only                  25) Yellow Pages'\
		'\n  15) Email' \
		'\n\n TRUEPEOPLESEARCH (optional)    USA-People-Search (optional)' \
		'\n  30) Name                          32) Name' \
		'\n  31) Address                       33) Address' \
		'\n\n EnformionGO (optional)         AI PROMPT TO CLIPBOARD (optional)' \
		'\n  34) Person Name                   50) AI Prompt' \
		'\n  '
	msg_search_sites_general = \
		'\n GOOGLE (optional)                OPEN WEBSITE (optional)' \
		'\n  10) Entity Name & Address         20) AZ Corporation Commission' \
		'\n  11) Entity Name Only              21) Dunn & Bradstreet Hoovers' \
		'\n  12) Person Name & Address         22) Fast People Search' \
		'\n  13) Person Name Only              23) Florida Sunbiz' \
		'\n  14) Address Only                  24) OpenCorporates' \
		'\n  15) Email                         25) Yellow Pages' \
		'\n\n TRUEPEOPLESEARCH (optional)    USA-People-Search (optional)' \
		'\n  30) Name                          32) Name' \
		'\n  31) Address                       33) Address' \
		'\n\n EnformionGO (optional)         AI PROMPT TO CLIPBOARD (optional)' \
		'\n  34) Person Name                   50) AI Prompt' \
		'\n  35) Entity Name' \
		'\n'
	
	# Copy/Paste Address options
	if search_for == 'Entity Address':
		td.colorText('\n ENTITY - ENTER ADDRESS', 'ORANGE')
		td.colorText('-'*50, 'ORANGE')
		td.colorText(msg_address, 'ORANGE')
		td.colorText(msg_search_sites_entity, 'ORANGE')
	elif search_for == 'Person Address':
		td.colorText('\n PERSON - ENTER ADDRESS', 'ORANGE')
		td.colorText('-'*50, 'ORANGE')
		td.colorText(msg_address, 'ORANGE')
		td.colorText(msg_search_sites_person, 'ORANGE')
	elif search_for == 'Entity Phone':
		td.colorText('\n ENTITY - ENTER PHONE', 'CYAN')
		td.colorText('-'*50, 'CYAN')
		td.colorText(msg_phone, 'CYAN')
		td.colorText(msg_search_sites_entity, 'CYAN')
	elif search_for == 'Person Phone':
		td.colorText('\n PERSON - ENTER PHONE', 'CYAN')
		td.colorText('-'*50, 'CYAN')
		td.colorText(msg_phone, 'CYAN')
		td.colorText(msg_search_sites_person, 'CYAN')
	elif search_for == 'Person Name':
		td.colorText('\n PERSON - ENTER Name', 'GREEN')
		td.colorText('-'*50, 'GREEN')
		td.colorText(msg_person, 'GREEN')
		td.colorText(msg_search_sites_entity, 'GREEN')
	elif search_for == 'General':
		print(msg_general)
		print(msg_search_sites_general)

	# Get Entity domain if email provided
	if dAcc['EMAIL'] != 'None':
		lemail = dAcc['EMAIL'].split('@')
		entity_domain = lemail[1]
		skipDomains = ['gmail.com', 'aol.com', 'hotmail.com', 'yahoo.com', 'landadvisors.com', 'att.net', 'bellsouth.net', '.rr.com', 'comcast.net', 'cox.net', 'earthlink.net', 'icloud.com', 'me.com', 'msn.com', 'outlook.com', 'qwestoffice.net', 'qwest.net', 'realtor.com', 'sbcglobal.net', 'swbell.net', 'asu.edu', 'remax.com', 'netzero.net', 'netscape.net', 'live.com']
		if not entity_domain in skipDomains:
			msg = \
				'\n\n DOMAINS (optional)' \
				'\n 40) Entity domain open website {0}' \
				'\n 41) Entity domain check TerraForce {0}' \
				.format(entity_domain)

			if 'Address' in search_for:
				td.colorText(msg, 'ORANGE')
			elif 'Person Name' in search_for:
				td.colorText(msg, 'GREEN')
			elif 'Phone' in search_for:
				td.colorText(msg, 'CYAN')
			elif 'General' in search_for:
				print(msg)
	
	# Update this with new website selection numbers
	lWebsite_ref_numbers = ['10', '11', '12', '13', '14', '15', '20', '21', '22', '23', '24', '25', '26', '30', '31', '32', '33', '34', '35', '40', '41', '50']
	return lWebsite_ref_numbers

# Get General information if Phone and Address are populated
def get_general_info(dAcc):
	td.banner('Enter Phone')
	lao.print_function_name('acc def get_general_info')
	
	# Straight to TF
	if dAcc['STRAIGHT2TF'] is True:
		return dAcc
		
	lWebsite_ref_numbers = open_contact_websites_menu(dAcc, search_for='General')

	# User to select action
	while 1:
		dAcc['PHONE'] = td.uInput('\n Enter Phone or Option > ')
		# Paste from webpage
		if dAcc['PHONE'] == '1':
			dAcc['PHONE'] = 'None'
			dAcc = cpypg.get_contact_info_from_webpage(dAcc)
			return dAcc
		# No Phone
		elif dAcc['PHONE'] == '2':
			dAcc['PHONE'] = 'None'
			return dAcc
		# Quit
		elif dAcc['PHONE'] == '00':
			exit('\n Terminating program...')
		
		# User chose webiste to open
		elif dAcc['PHONE'] in lWebsite_ref_numbers:
			dAcc = webs.open_contact_websites(dAcc, dAcc['PHONE'])
			dAcc['PHONE'] = 'None'


		elif len(dAcc['PHONE']) > 6:
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			print('\n\n ENTERED PHONE: {0}\n'.format(dAcc['PHONE']))
			ui = td.uInput('\n Accept Phone [0/1/00] > ')
			if ui == '1':
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
	return dAcc

def get_missing_person(dAcc):
	td.banner('Enter Person')
	lao.print_function_name('acc def get_missing_person')
	
	# Straight to TF
	if dAcc['STRAIGHT2TF'] is True:
		return dAcc
		
	lWebsite_ref_numbers = open_contact_websites_menu(dAcc, search_for='Person Name')

	# User to select action
	
	while 1:
		dAcc['NAME'] = (td.uInput('\n Enter Person Name > '))
		# Paste from webpage
		if dAcc['NAME'] == '1':
			td.warningMsg('\n You must type in the name.')
			lao.sleep(2)
			# dAcc['NAME'] = 'None'
			# dAcc = cpypg.get_contact_info_from_webpage(dAcc)
			# return dAcc
		# No Person
		elif dAcc['NAME'] == '99':
			dAcc['NAME'] = 'None'
			return dAcc
		# Quit
		elif dAcc['NAME'] == '00':
			exit('\n Terminating program...')
		
		# User chose webiste to open
		elif dAcc['NAME'] in lWebsite_ref_numbers:
			dAcc = webs.open_contact_websites(dAcc, dAcc['NAME'])
			dAcc['NAME'] = 'None'

		elif len(dAcc['NAME']) > 5 and ' ' in dAcc['NAME']:
			print('\n\n ENTERED PERSON: {0}\n'.format(dAcc['NAME']))
			ui = td.uInput('\n Accept Person [0/1/00] > ')
			if ui == '1':
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
		else:
			td.warningMsg('\n You must type in the name.')
			lao.sleep(2)
	return dAcc

# Get missing Address by typing or pasting from webpage
def get_missing_phone(dAcc, search_for):
	td.banner('Enter Phone')
	lao.print_function_name('acc def get_missing_phone')
	
	# Straight to TF
	if dAcc['STRAIGHT2TF'] is True:
		return dAcc
		
	# lWebsite_ref_numbers = open_contact_websites_menu(dAcc, search_for='Phone')

	# User to select action
	
	while 1:

		lWebsite_ref_numbers = open_contact_websites_menu(dAcc, search_for=search_for)

		dAcc['PHONE'] = (td.uInput('\n --> '))
		# Paste from webpage
		if dAcc['PHONE'] == '1':
			dAcc['PHONE'] = 'None'
			dAcc = cpypg.get_contact_info_from_webpage(dAcc)
			return dAcc
		# Type or Paste Phone
		elif dAcc['PHONE'] == '2':
			dAcc['PHONE'] = td.uInput('\n Enter Phone > ')
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			print('\n\n ENTERED PHONE: {0}\n'.format(dAcc['PHONE']))
			ui = td.uInput('\n Accept Phone [0/1/00] > ')
			if ui == '1':
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
			return dAcc
		# No Phone
		elif dAcc['PHONE'] == '99':
			dAcc['PHONE'] = 'None'
			return dAcc
		# Quit
		elif dAcc['PHONE'] == '00':
			exit('\n Terminating program...')
		
		# User chose webiste to open
		elif dAcc['PHONE'] in lWebsite_ref_numbers:
			website_number = dAcc['PHONE']
			dAcc['PHONE'] = 'None'
			dAcc = webs.open_contact_websites(dAcc, website_number)
			if dAcc['PHONE'] != 'None':
				return dAcc

		elif len(dAcc['PHONE']) > 6:
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			print('\n\n ENTERED PHONE: {0}\n'.format(dAcc['PHONE']))
			ui = td.uInput('\n Accept Phone [0/1/00] > ')
			if ui == '1':
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
	return dAcc

# Get missing Address by typing or pasting from webpage
def get_missing_address(dAcc, search_for):
	td.banner('Enter Address')
	lao.print_function_name(f'acc def get_missing_address search_for={search_for}')

	# User to select action
	while 1:
		lWebsite_ref_numbers = open_contact_websites_menu(dAcc, search_for=search_for)

		dAcc['STREET'] = (td.uInput('\n Enter address or option > ')).title()
		# Paste from webpage
		if dAcc['STREET'] == '1':
			dAcc['STREET'] = 'None'
			dAcc = cpypg.start_cpypg(dAcc)
			return dAcc
		# Copy/Paste Address Options
		elif dAcc['STREET'] == '2':
			# Remove CRs from clipboard
			clipboard_text = pyperclip.paste()
			clipboard_text = clipboard_text.replace('\n', ' ').replace('\r', '')
			pyperclip.copy(clipboard_text)
			# Paste Address from clipboard
			dAcc['STREET'] = td.uInput('\n Enter full address > ')
			# dAcc = parseAddress(dAcc['STREET'], dAcc)
			dAcc = td.parce_single_line_address(dAcc['STREET'], dAcc=dAcc)
			print('\n\n {0}\n {1}, {2} {3}\n'.format(dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))
			ui = td.uInput('\n Accept Address [0/1/00] > ')
			if ui == '1':
				dAcc = cpypg.start_cpypg(dAcc)
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
			return dAcc
		elif dAcc['STREET'] == '3':
			dAcc['STREET'] = td.uInput('\n Enter street & suite > ')
			if dAcc['ZIPCODE'] == 'None':
				while 1:
					dAcc['ZIPCODE'] = td.uInput('\n Enter Zip Code > ')
					dAcc['ZIPCODE'] = dAcc['ZIPCODE'].strip()
					if len(dAcc['ZIPCODE']) > 6:
						dAcc['ZIPCODE'] = dAcc['ZIPCODE'][:5]
						break
					else:
						break
				dAcc['CITY'], dAcc['STATE'], USA = lao.zipCodeFindCityStateCountry(dAcc['ZIPCODE'])
			dAcc = td.address_formatter(dAcc)
			print('\n\n {0}\n {1}, {2} {3}\n'.format(dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))
			ui = td.uInput('\n Accept Address [0/1/00] > ')
			if ui == '1':
				dAcc = cpypg.start_cpypg(dAcc)
				return dAcc
			elif ui == '0':
				continue
			elif ui == '00':
				exit('\n Terminating program...')
			return dAcc
		# Accept Info
		elif dAcc['STREET'] == '4':
			dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'] = 'None', 'None', 'None', 'None'
			dAcc['STRAIGHT2TF'] = True
			return dAcc
		# No Address
		elif dAcc['STREET'] == '99':
			dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'] = 'None', 'None', 'None', 'None'
			return dAcc
		
		# Quit
		elif dAcc['STREET'] == '00':
			exit('\n Terminating program...')
		
		# User chose webiste to open from lWebsite_number
		elif dAcc['STREET'] in lWebsite_ref_numbers:
			website_number = dAcc['STREET']
			dAcc['STREET'] = 'None'
			dAcc = webs.open_contact_websites(dAcc, website_number)
			# return dAcc

		# User typed Address
		else:
			td.warningMsg('\n Invalid entry...please select an option...')
			lao.sleep(2)
			continue

# Formats Address to Title case and 
def addressFormater(dAcc):
	td.warningMsg('\n acc def addressFormater no longer valid...\n Use td.address_formatter')
	exit('\n Terminating program...')

# Make Person MVP based on DID (Deal ID) or AID (Account ID)
def make_person_mvp_and_market_mailer(service, AID='None', didpid='None', make_market_mailer=True):
	lao.print_function_name('acc def defmake_person_mvp_and_market_mailer')

	dAcc = dicts.get_blank_account_dict()

	if AID == 'None':
		# Get DID if PID
		if bb.isDIDorPID(didpid) == 'PID':
			DID = bb.getDIDfromPID(service, didpid)
		else:
			DID = didpid

		
		# Get market from DID
		dDeal = bb.getLeadDealData(service, DID, dealVar='All')
		market = dDeal['Market__c']
		# Get Person (Account) info
		# Check if Deal has a Person in the Account field
		if dDeal['AccountId__c'] == '':
			td.warningMsg(' Deal does not have a person associated with it.')
			lao.holdup()
		dAcc['AID'] = dDeal['AccountId__c']
	else:
		dAcc['AID'] = AID
		ui = td.uInput('\n Enter 3 letter Market > ')
		if len(ui) == 3:
			marketAbb = ui.upper()

	# Populate dAcc with Account info
	dAcc = populate_dAcc_from_tf(service, dAcc['AID'], dAcc=dAcc)
	# Determine Agent(s) from market
	dAgent = dicts.get_staff_dict()
	# Cleat TOP100AGENT as the update_existing_contact function will add the Agent(s) if others exist
	dAcc['TOP100AGENT'] = 'None'
	for agent in dAgent:
		if dAgent[agent]['Roll'] == 'Agent':
			if marketAbb in dAgent[agent]['marketAbb']:
				if dAcc['TOP100AGENT'] == 'None':
					dAcc['TOP100AGENT'] = [agent]
				elif not agent in dAcc['TOP100AGENT']:
					dAcc['TOP100AGENT'] = f'{dAcc["TOP100AGENT"]};{agent}'
	
	# Add Market Mailer to Category if make Market Mailer is True
	if make_market_mailer:
		dAcc['CATEGORY'] = ['Market Mailer']

	dAcc = update_existing_contact(service, dAcc)

#####################################################################
# AI Company/Contact functions
#####################################################################

def select_company_from_json(json_data):
	"""
	Lists all companies from the JSON data and prompts user to select one.
	
	Args:
		json_data: Dictionary containing the company search results
		
	Returns:
		Dictionary containing the selected company's data
	"""
	companies_list = []
	
	# Add primary company
	if json_data['companies']['primary']:
		primary = json_data['companies']['primary'].copy()
		primary['company_type'] = 'Primary'
		companies_list.append(primary)
	
	# Add parent company
	if json_data['companies']['parent_company']:
		parent = json_data['companies']['parent_company'].copy()
		parent['company_type'] = 'Parent'
		companies_list.append(parent)
	
	# Add subsidiaries
	for subsidiary in json_data['companies']['subsidiaries']:
		sub = subsidiary.copy()
		sub['company_type'] = 'Subsidiary'
		companies_list.append(sub)
	
	# Add affiliates
	for affiliate in json_data['companies']['affiliates']:
		aff = affiliate.copy()
		aff['company_type'] = 'Affiliate'
		companies_list.append(aff)
	
	# Display companies
	print("\n" + "="*80)
	print("AVAILABLE COMPANIES")
	print("="*80)
	
	for idx, company in enumerate(companies_list, 1):
		print(f"\n[{idx}] {company['company_type'].upper()}: {company['Name']}")
		print(f"    Address: {company.get('BillingStreet', '')}, {company.get('BillingCity', '')}, {company.get('BillingState', '')} {company.get('BillingPostalCode', '')}")
		print(f"    Category: {company.get('Category__c', 'N/A')}")
		print(f"    Phone: {company.get('Phone', 'N/A')}")
		print(f"    Website: {company.get('Website', 'N/A')}")
		print(f"    LinkedIn: {company.get('LinkedIn_Url__c', 'N/A')}")
		print(f"    Relationship: {company.get('relationship', 'N/A')}")
		if company.get('ownership_percentage'):
			print(f"    Ownership %: {company['ownership_percentage']}")
		print(f"    Description: {company.get('Description', 'N/A')}...")
	
	# Display search metadata
	print("\n" + "="*80)
	print("SEARCH METADATA")
	print("="*80)
	
	metadata = json_data.get('search_metadata', {})
	
	print(f"\nConfidence Level: {metadata.get('confidence_level', 'N/A')}")
	
	print(f"\nCorporate Structure Notes:")
	print(f"{metadata.get('corporate_structure_notes', 'N/A')}")
	
	print(f"\nNotes:")
	print(f"{metadata.get('notes', 'N/A')}")
	
	print("\n" + "="*80)
	
	# Get user selection
	while True:
		ui = td.uInput(f"\nSelect a company (1-{len(companies_list)}): ").strip()
		if ui.isdigit() and 1 <= int(ui) <= len(companies_list):
			selected_company = companies_list[int(ui) - 1]
			print(f"\nSelected: {selected_company['Name']} ({selected_company['company_type']})")
			return selected_company
		print(f"Invalid selection. Please enter a number between 1 and {len(companies_list)}.")


def fuzzy_search_company(service, company_name, threshold=70, limit=10):
	"""
	Search Salesforce for companies using fuzzy matching logic with intelligent parsing
	
	Handles complex names like "Dynasty Farms, Inc. dba Pacific International Marketing (PIM)"
	by breaking them into searchable components
	
	Parameters:
	- service: Salesforce client object from fun_login.Terraforce()
	- company_name: The company name to search for
	- threshold: Minimum similarity score (0-100) to include in results. Default 70.
	- limit: Maximum number of results to return per component. Default 10.
	
	Returns:
	- List of tuples: (similarity_score, record_dict, matched_component)
	"""
	
	# Parse the company name into searchable components
	search_components = parse_company_name(company_name)
	
	# Query all companies from TF
	where_clause = "IsPersonAccount = false"
	all_companies = bb.tf_query_3(service, rec_type='Entity', where_clause=where_clause, limit=None, fields='default')
	
	if not all_companies:
		return []
	
	# Create a mapping of company names to records
	company_map = {record['Name']: record for record in all_companies if record.get('Name')}
	
	# Search for each component
	all_results = []
	seen_ids = set()  # Track IDs to avoid duplicates
	
	for component in search_components:
		matches = process.extract(
			component,
			company_map.keys(),
			scorer=fuzz.token_sort_ratio,
			score_cutoff=threshold,
			limit=limit
		)
		
		for match_name, score, _ in matches:
			record = company_map[match_name]
			record_id = record['Id']
			
			# Only add if not already found (keep highest score)
			if record_id not in seen_ids:
				seen_ids.add(record_id)
				all_results.append((score, record, component))
	
	# Sort by score descending
	all_results.sort(key=lambda x: x[0], reverse=True)
	
	return all_results

def xxxxparse_company_name(company_name):
	"""
	Parse a complex company name into searchable components
	
	Handles patterns like:
	- "Company A dba Company B"
	- "Company A d/b/a Company B"
	- "Company (Acronym)"
	- "Company, Inc."
	"""
	components = []
	
	# Split on common separators for multiple business names
	# dba, d/b/a, aka, a/k/a, fka, f/k/a
	separators = r'\s+(?:dba|d/b/a|aka|a/k/a|fka|f/k/a)\s+'
	parts = re.split(separators, company_name, flags=re.IGNORECASE)
	
	for part in parts:
		# Remove parenthetical content (often acronyms)
		part_no_parens = re.sub(r'\([^)]*\)', '', part).strip()
		
		# Remove common business suffixes for better matching
		cleaned = remove_business_suffixes(part_no_parens)
		
		if cleaned:
			components.append(cleaned)
		
		# Also add the version with parenthetical content removed but suffixes intact
		if part_no_parens and part_no_parens != cleaned:
			components.append(part_no_parens)
	
	# Remove duplicates while preserving order
	seen = set()
	unique_components = []
	for comp in components:
		comp_lower = comp.lower()
		if comp_lower not in seen:
			seen.add(comp_lower)
			unique_components.append(comp)
	
	return unique_components

def remove_business_suffixes(name):
	"""Remove common business suffixes like Inc, LLC, Corp, etc."""
	# Common business suffixes
	suffixes = [
		r',?\s+Inc\.?$',
		r',?\s+LLC\.?$',
		r',?\s+L\.L\.C\.?$',
		r',?\s+Corp\.?$',
		r',?\s+Corporation$',
		r',?\s+Ltd\.?$',
		r',?\s+Limited$',
		r',?\s+Co\.?$',
		r',?\s+Company$',
		r',?\s+LP\.?$',
		r',?\s+LLP\.?$',
		r',?\s+LLLP\.?$',
		r',?\s+P\.C\.?$',
	]
	
	result = name
	for suffix in suffixes:
		result = re.sub(suffix, '', result, flags=re.IGNORECASE)
	
	return result.strip()

def fuzzy_search_company_debug(service, company_name, threshold=70, limit=10):
	"""
	Debug version to see what's happening at each step
	"""
	print(f"\n=== DEBUGGING FUZZY SEARCH ===")
	print(f"Original search: '{company_name}'")
	print(f"Threshold: {threshold}")
	
	# Parse the company name into searchable components
	search_components = parse_company_name(company_name)
	print(f"\nParsed components: {search_components}")
	
	# Query all companies from TF
	where_clause = "IsPersonAccount = false"
	print(f"\nQuerying TF with: {where_clause}")
	all_companies = bb.tf_query_3(service, rec_type='Entity', where_clause=where_clause, limit=None, fields='default')
	
	print(f"Retrieved {len(all_companies) if all_companies else 0} companies")
	
	if not all_companies:
		print("No companies retrieved from TF!")
		return []
	
	# Show a few sample company names
	print(f"\nSample company names from TF:")
	for i, rec in enumerate(all_companies[:5]):
		print(f"  {i+1}. {rec.get('Name', 'NO NAME')}")
	
	# Create a mapping of company names to records
	company_map = {record['Name']: record for record in all_companies if record.get('Name')}
	print(f"\nTotal companies with names: {len(company_map)}")
	
	# Search for each component
	all_results = []
	seen_ids = set()
	
	for component in search_components:
		print(f"\n--- Searching for component: '{component}' ---")
		
		# Try different matching algorithms
		matches_token = process.extract(
			component,
			company_map.keys(),
			scorer=fuzz.token_sort_ratio,
			score_cutoff=threshold,
			limit=limit
		)
		print(f"token_sort_ratio matches: {len(matches_token)}")
		
		matches_partial = process.extract(
			component,
			company_map.keys(),
			scorer=fuzz.partial_ratio,
			score_cutoff=threshold,
			limit=limit
		)
		print(f"partial_ratio matches: {len(matches_partial)}")
		
		# Show top matches even if below threshold
		all_scores = [(fuzz.token_sort_ratio(component, name), name) for name in list(company_map.keys())[:100]]
		all_scores.sort(reverse=True)
		print(f"Top 5 matches (no threshold):")
		for score, name in all_scores[:5]:
			print(f"  {score}% - {name}")
		
		for match_name, score, _ in matches_token:
			record = company_map[match_name]
			record_id = record['Id']
			
			if record_id not in seen_ids:
				seen_ids.add(record_id)
				all_results.append((score, record, component))
	
	# Sort by score descending
	all_results.sort(key=lambda x: x[0], reverse=True)
	
	print(f"\n=== FINAL RESULTS: {len(all_results)} matches ===")
	return all_results


def parse_company_name(company_name):
	"""Parse a complex company name into searchable components"""
	components = []
	
	# Split on common separators for multiple business names
	separators = r'\s+(?:dba|d/b/a|aka|a/k/a|fka|f/k/a)\s+'
	parts = re.split(separators, company_name, flags=re.IGNORECASE)
	
	for part in parts:
		# Remove parenthetical content
		part_no_parens = re.sub(r'\([^)]*\)', '', part).strip()
		
		# Remove common business suffixes
		cleaned = remove_business_suffixes(part_no_parens)
		
		if cleaned:
			components.append(cleaned)
		
		# Also add the version with suffixes intact
		if part_no_parens and part_no_parens != cleaned:
			components.append(part_no_parens)
	
	# Remove duplicates while preserving order
	seen = set()
	unique_components = []
	for comp in components:
		comp_lower = comp.lower()
		if comp_lower not in seen:
			seen.add(comp_lower)
			unique_components.append(comp)
	
	return unique_components



	
	return result.strip()