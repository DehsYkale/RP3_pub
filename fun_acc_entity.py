# Functions to Find or Create an Entity in TF

import acc
import bb
import lao
import fun_text_date as td
from pprint import pprint

# Get the Name of the Entity from dAcc or have the user enter if 'None'
def get_entity_name(dAcc):
	lao.print_function_name('fae def get_entity_name')

	if dAcc['ENTITY'] == 'None':
		acc.printUIInput(dAcc)
		if '@' in dAcc['EMAIL']:
			print('\n Googled email...')
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(dAcc['EMAIL']))
		dAcc['ENTITY'] = td.uInput('\n Enter Full Business or Person Name [00] > ').upper()
		if dAcc['ENTITY']  == '00':
			exit('\n Terminating program...')
		dAcc['ENTITY'] = dAcc['ENTITY'].replace("'", '')
		# uiName = True
	return dAcc

# Determine if NAME is an Entity/Business/Company
def is_entity(dAcc):
	lao.print_function_name('fae def is_entity')

	user_confirmed_entity = True

	# Skip blanks or None
	if dAcc['ENTITY'] == '':
		dAcc['ENTITY'] = 'None'
	if dAcc['ENTITY'] == 'None':
		user_confirmed_entity = False
		return dAcc, user_confirmed_entity

	if lao.coTF(dAcc['ENTITY']) is False:
		
		while 1:
			print('\n Is {0} a Entity/Business?\n'.format(dAcc['ENTITY']))
			print('  1] Yes')
			print('  2] No')
			print(' 00] Quit')
			ui = td.uInput('\n > ')
			# If ENTITY is not a Business/Company then return NONE
			if ui == '0' or ui == '2':
				dAcc['NAME'] = dAcc['ENTITY']
				dAcc['ENTITY'], dAcc['EID']= 'None', 'None'
				user_confirmed_entity = False
				return dAcc, user_confirmed_entity
			elif ui == '1':
				dAcc['ENTITY'] = dAcc['ENTITY'].upper()
				break
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				td.warningMsg('\n Invalid entry...try again...\n')
	
	return dAcc, user_confirmed_entity

# Build Entity NAME query string
def get_entity_name_query_string(dAcc):
	lao.print_function_name('fae def get_entity_name_query_string')
	NAMECLEAN = dAcc['ENTITY'].replace(',','')
	NAMESPLIT = NAMECLEAN.split()

	if len(NAMESPLIT) > 2:
		# Remove 'The'
		if (NAMESPLIT[0]).upper() == 'THE':
			NAMEQUERY = '%{0} {1}'.format(NAMESPLIT[1], NAMESPLIT[2])
		elif NAMESPLIT[1] == '&' or NAMESPLIT[1] == 'AND':
			NAMEQUERY = '{0} {1} {2}'.format(NAMESPLIT[0], NAMESPLIT[1], NAMESPLIT[2])
		elif (NAMESPLIT[0].upper() == 'CITY' or NAMESPLIT[0].upper() == 'TOWN') and NAMESPLIT[1].upper() == 'OF':
			NAMEQUERY = '{0} {1} {2}'.format(NAMESPLIT[0], NAMESPLIT[1], NAMESPLIT[2])
		else:
			NAMEQUERY = '{0} {1} {2}'.format(NAMESPLIT[0], NAMESPLIT[1], NAMESPLIT[2])
	elif len(NAMESPLIT) == 2:
		lCOSUFIX = 'LLC L.L.C. INC LTD LP LPPP'
		if NAMESPLIT[1].upper() in lCOSUFIX:
			NAMEQUERY = NAMESPLIT[0]
		elif NAMESPLIT[0].upper() == 'THE':
			NAMEQUERY = '%{0}'.format(NAMESPLIT[1])
		else:
			NAMEQUERY = '{0} {1}'.format(NAMESPLIT[0], NAMESPLIT[1])
	else:
		NAMEQUERY = NAMESPLIT[0]
	
	return NAMEQUERY

# Query TF to see if Entity record exists returning results
def query_tf_for_entity_name(service, NAMEQUERY):
	lao.print_function_name('fae def query_tf_for_entity_name')
	firsttime = True
	# Select Entities based on Name
	while 1:
		# TerraForce Query
		wc = f"IsPersonAccount != TRUE AND Name LIKE '{NAMEQUERY}%'"
		results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
		business_dict = results
		# If results are null then search only the first word in name
		# if firsttime and results == []:
		# 	NAMESPLIT = NAMEQUERY.split()
		# 	if len(NAMESPLIT) > 1:
		# 		NAMESPLIT = NAMESPLIT[:-1]
		# 		NAMEQUERY = ' '.join(NAMESPLIT)
		# 	if len(NAMESPLIT[0]) <= 5: # Skip 1 name search short first words
		# 		break
		# 	else:
		# 		NAMEQUERY = NAMESPLIT[0]
		# 		firsttime = False
		# else:
		# 	break
		if results == []:
			NAMESPLIT = NAMEQUERY.split()
			NAMESPLIT = NAMESPLIT[:-1]
			if NAMESPLIT == []:
				break
			if len(NAMESPLIT) == 1 and len(NAMESPLIT[0]) <= 5:
				break
			NAMEQUERY = ' '.join(NAMESPLIT)
		else:
			break

	return results

# User to select exiting Entity TF record or none
def select_matching_entity_in_tf(results, dAcc):
	lao.print_function_name('fae def select_matching_entity_in_tf')

	i = 0
	print(' [ 0] No Match')
	for row in results:
		n = str(i+1)
		streetAbb = row['BillingStreet']
		streetAbb = streetAbb.replace('\n', ' ').replace('\r', '')
		streetAbb = td.get_abbreviate_street_name(streetAbb)
		# Printing Entity
		if dAcc['ENTITY'].upper() in row['Name'].upper() or row['Name'].upper() in dAcc['ENTITY'].upper():
			lSTREET = dAcc['STREET'].split()
			if lSTREET[0] in streetAbb:
				td.instrMsg(' [{0:>2}] {1:30.30} | {2:25.25} | {3:10.10} | {4:2.2} | {5}'.format(n, row['Name'], streetAbb, row['BillingCity'], row['BillingState'], row['Phone']))
			else:
				strText = ' [{0:>2}] {1:30.30} | {2:25.25} | {3:10.10} | {4:2.2} | {5}'.format(n, row['Name'], streetAbb, row['BillingCity'], row['BillingState'], row['Phone'])
				td.colorText(strText, 'CYAN')
		else:
			print(' [{0:>2}] {1:30.30} | {2:25.25} | {3:10.10} | {4:2.2} | {5}'.format(n, row['Name'], streetAbb, row['BillingCity'], row['BillingState'], row['Phone']))
		i=i+1
	
	while 1:
		print('\n [ ##]  Select Entity number')
		print(' [  0]  No Match')
		print(' [999]  Add City to Entity Name')
		print(' [ 00]  Quit\n')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		try:
			ui = int(ui)
		except (SyntaxError, ValueError):
			td.warningMsg('\n Entry must be a number, try again...\n')
			continue
		break
	
	return ui

# No matching Entity in TF user to input new name or continue with existing name
def no_matching_entity_in_tf(dAcc):
	lao.print_function_name('fae def no_matching_entity_in_tf')

	confirm_entity_name = True
	new_entity_name = False
	print(' No matching Entity Account in TerraForce...')
	print('   > [Enter] to use this one')
	print('   > Type a different Name')
	print(' 00) Quit')
	ui = td.uInput('\n --> ').upper()
	if ui == '00':
		exit('Terminating program...')
	elif len(ui) > 1:
		dAcc['ENTITY'] = ui
		new_entity_name = True
	# add City to NAME
	elif ui == 999:
		# Let user type a city if none listed
		if dAcc['CITY'] == 'None':
			td.warningMsg('\n No City listed with Entity')
			msg = \
				'\n   > [Enter] for none' \
				'\n   > Type a CITY name' \
				'\n 00) Quit'
			print(msg)
			temp_city = td.uInput('\n --> ')
			if temp_city == '00':
				exit('\n Terminating program...')
			elif len(temp_city) > 1:
				dAcc['ENTITY'] = '{0} - {1}'.format(dAcc['ENTITY'], temp_city)
				new_entity_name = True
			else:
				ui = 0
				confirm_entity_name = False
		else:
			dAcc['ENTITY'] = '{0} - {1}'.format(dAcc['ENTITY'], dAcc['CITY'])
			new_entity_name = True
	else:
		ui = 0
		dont_confirm_entity_name = True
	
	return dAcc, ui, new_entity_name, confirm_entity_name

# Have user confirm Entity Name
def user_confirm_entity_name(dAcc):
	lao.print_function_name('fae def user_confirm_entity_name')

	print('\n CONFIRM BUSINESS NAME')
	new_entity_name = False
	td.colorText('\n {0}'.format(dAcc['ENTITY']), 'ORANGE')
	# msg = \
	# 	'\n   > [Enter] to use OR type DIFFERENT business name [00] > ' \
	# 	'\n   > Type DIFFERENT Business Name' \
	# 	'\n 00) Quit'
	# print(msg)
	ui = td.uInput('\n [Enter] to use OR type DIFFERENT business name [00] > ')
	if ui == 'Q' or ui == '00':
		exit(' Terminating program...')
	if ui != '':
		dAcc['ENTITY'] = ui.title()
		new_entity_name = True
	
	return dAcc, new_entity_name

# Webpage dict
def get_webpage_dict(dAcc):
	lao.print_function_name('fae def get_webpage_dict')

	dWpg = {
		'LPAGE': 'None', 			# List of lines of webpage from paste from clipboard
		'AID': dAcc['AID'],
		'NAME': dAcc['NAME'],
		'NF': dAcc['NF'],				# First Name
		'NM': dAcc['NM'],				# Middle Name
		'NL': dAcc['NL'],				# Last Name
		'TITLEPERSON': dAcc['TITLEPERSON'],
		'EID' : dAcc['EID'],
		'ENTITY': dAcc['ENTITY'],
		'ADDRESSFULL': dAcc['ADDRESSFULL'],  # Full address if listed
		'SOURCE': 'None',
		'STREET': dAcc['STREET'],
		'CITY': dAcc['CITY'],
		'STATE': dAcc['STATE'],
		'ZIPCODE': dAcc['ZIPCODE'],
		'PHONE': dAcc['PHONE'],
		'MOBILE': dAcc['MOBILE'],
		'EMAIL': dAcc['EMAIL'],
		'CATEGORY': dAcc['CATEGORY'],
		'DESCRIPTION': dAcc['DESCRIPTION'],
		'PHONEDESCRIPTION': 'Possible Phone Numbers:',
		'EMAILDESCRIPTION': 'Possible Emails:',
		'WEBSITE': dAcc['WEBSITE'],
		'SOURCE': dAcc['SOURCE'],
		'INFOCONFIRMED': False}

	return dWpg

# Print the Account Master Menu
def account_info_menu_master(dAcc):
	lao.print_function_name('fae def account_menu_master')

	# Get Webpage dict
	dWpg = get_webpage_dict(dAcc)

	# lao.banner('Contact Info Update (cpypg.py)')

	td.colorText('   1) Accept Info', 'CYAN')
	td.colorText('   2) Reject Info and Try Again', 'CYAN')
	td.colorText('  00) Quit\n', 'CYAN')
	msg = \
		'  Select number to modify\n\n' \
		'  10) Entity:      {0}\n' \
		'  11) Person:      {1}\n' \
		'  12) Title:       {2}\n\n' \
		'  13) Address:     {3}\n' \
		'  14)              {4}, {5} {6}\n\n' \
		'  15) Phone:       {7}\n' \
		'  16) Mobile:      {8}\n' \
		'  17) Email:       {9}\n' \
		'  18) Website:     {10}\n\n' \
		.format(
			dWpg['ENTITY'],
			dWpg['NAME'],
			dWpg['TITLEPERSON'],
			dWpg['STREET'],
			dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'],
			dWpg['PHONE'],
			dWpg['MOBILE'],
			dWpg['EMAIL'],
			dWpg['WEBSITE'])
	print(msg)









