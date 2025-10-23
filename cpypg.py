#! python3

import fun_text_date as td
import lao
import pyperclip
from pprint import pprint
import webs

def start_cpypg(dAcc):
	lao.print_function_name('cpypg def start_cpypg')

	# Title case Address
	if dAcc['STREET'] != 'None':
		dAcc = td.address_formatter(dAcc)
	# Build dWpg dict
	dWpg = get_webpage_dict(dAcc)
	if dAcc['STREET'] != 'None':
		info_print_confirm(dWpg, dAcc, confirm_it=True)
	else:
		info_print_confirm(dWpg, dAcc, confirm_it=False)
		# Get contact from webpage
		dAcc = get_contact_info_from_webpage(dAcc)
	return dAcc

def update_TF_with_dACC(dAcc, record_type):
	lao.print_function_name('cpypg def update_TF_with_dACC')

	# Create dict of dAcc to TF field conversions
	# record_type determines if it is a Person to update or and Entity
	# Add universal fields
	dAcc_2_TF_dup = {
		'CATEGORY': 'Category__c',
		'CITY': 'BillingCity',
		'DESCRIPTION': 'Description__c',
		'PHONE': 'Phone',
		'STATE': 'BillingState',
		'STREET': 'BillingStreet',
		'TITLEPERSON': 'PersonTitle',
		'ZIPCODE': 'BillingPostalCode'}
	# Add PERSON fields
	if record_type == 'PERSON':
		dTemp = {
			'AID': 'Id',					# Account Person ID
			'EID': 'Company__c',			# Person's company (ENTITY) 
			'EMAIL': 'PersonEmail',			# Email
			'MOBILE': 'PersonMobilePhone',	# Person Mobile Phone
			'NF': 'FirstName',				# First Name
			'NM': 'MiddleName__c',			# Middle Name
			'NL': 'LastName',				# Last Name
			'PHONEHOME': 'PersonHomePhone',	# Home Phone
			'TITLEPERSON': 'PersonTitle',	# Person's Title
			'TOP100AGENT': 'Top100__c'}		# Top 100 (MVP) Advisors List
	# Add ENTITY fields
	elif record_type == 'ENTITY':
		dTemp = {
			'EID': 'Id',					# Account Entity ID
			'ENTITY': 'Name',				# Entity Name
			'WEBSITE': 'Website'}			# Website
	dAcc_2_TF_dup.update(dTemp)
	
	# Create the dict to use to update TF by cycling through dAcc_2_TF_dup keys
	dup = {'type': 'Account'}
	for key in dAcc_2_TF_dup.keys():
		if dAcc[key] != 'None' and dAcc[key] != '' and dAcc[key] != []:
			dup[dAcc_2_TF_dup[key]] = dAcc[key]
	# Update or Create Entity or Contact Person
	# if record_type == 'ENTITY':
	# 	# Existing Entity - Update
	# 	if 'Id' in dup.keys():

	print

# Webpage dict
def get_webpage_dict(dAcc):
	lao.print_function_name('cpypg def get_webpage_dict')

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
		'DESCRIPTION': dAcc['DESCRIPTION'],
		'PHONEDESCRIPTION': 'Possible Phone Numbers:',
		'EMAILDESCRIPTION': 'Possible Emails:',
		'WEBSITE': dAcc['WEBSITE'],
		'SOURCE': dAcc['SOURCE'],
		'INFOCONFIRMED': False}
	return dWpg

# Load the webpage into the dWpg dict
def load_webpage_to_dict(dWpg):
	lao.print_function_name('cpypg def load_webpage_to_dict')

	txtPage = pyperclip.paste()
	# txtPage = txtPage.encode('utf-8','ignore')
	dWpg['LPAGE'] = txtPage.split('\r\n')
	return dWpg

# Determine source of the copied information on the clipboard
def get_source(dWpg):
	lao.print_function_name('cpypg def get_source')

	while 1:
		print('\n Copy webpage from DnB, Google, OpenCorporates, Sunbiz or Yellow Pages')
		print(' or copy an address')
		lao.holdup()
		dWpg = load_webpage_to_dict(dWpg)
		
		for row in dWpg['LPAGE']:
			# print(row)
			if 'TruePeopleSearch' in row:
				dWpg['SOURCE'] = 'TruePeopleSearch'
				break
			elif 'OpenCorporates' in row:
				dWpg['SOURCE'] = 'OpenCorporates'
				break
			elif 'Dun & Bradstreet Cloud' in row:
				dWpg['SOURCE'] = 'Dun & Bradstreet Cloud'
				break
			elif 'Search & Build a List' in row:
				dWpg['SOURCE'] = 'D&B Hoovers'
				break
			elif 'D&B Hoovers' in row:
				dWpg['SOURCE'] = 'D&B Hoovers'
				break
			# elif 'CORE' in row:
			# 	dWpg['SOURCE'] = 'D&B Hoovers'
			# 	break
			elif 'Real Yellow Pages' in row:
				dWpg['SOURCE'] = 'Real Yellow Pages'
				break
			elif 'SmartLinx' in row:
				dWpg['SOURCE'] = 'Nexis'
				break
			elif 'Google' in row:
				dWpg['SOURCE'] = 'Google'
				break
			elif 'Florida Division of Corporations' in row:
				dWpg['SOURCE'] = 'Sunbiz'
				break
			elif 'Arizona Corporation Commission' in row:
				dWpg['SOURCE'] = 'Arizona Corporation Commission'
				break
			elif 'FastPeopleSearch' in row:
				dWpg['SOURCE'] = 'FastPeopleSearch'
				break
			elif 'USA people search logo' in row:
				dWpg['SOURCE'] = 'USA People Search'
				break
		# Check if copied text is an address if last 5 characters are digits
		len_LPAGE = len(dWpg['LPAGE']) - 1
		if len_LPAGE <= 6:
			isZip = dWpg['LPAGE'][len_LPAGE][-5:]
			if isZip.isdigit():
				dWpg['SOURCE'] = 'Address Only'
				
		# Undetermined source ask user what to do
		if dWpg['SOURCE'] == 'None':
			while 1:
				td.warningMsg('\n Could not determine webpage Source...')
				print('\n   1) This is an address')
				print('\n   2) Try again')
				print('\n   3) Cancel copy webpage')
				print('\n  00) quit')
				ui = td.uInput('\n Select > ')
				if ui == '00':
					exit('\n Terminating program...')
				elif ui == '1':
					dWpg['SOURCE'] = 'Address Only'
					break
				elif ui == '2':
					print('\n Trying again...')
					lao.sleep(1)
					break
				elif ui == '3':
					dWpg['SOURCE'] = 'Canceled'
					td.warningMsg('\n Canceling copy webpage')
					lao.sleep(1)
					return dWpg
				else:
					td.warningMsg('\n Invalid input...try again...')
		else:
			break
		# Address Only
		if dWpg['SOURCE'] == 'Address Only':
			break
	td.warningMsg('\n Source: {0}'.format(dWpg['SOURCE']))
	return dWpg

# Assemble the Description
def assemble_description(dWpg):
	lao.print_function_name('cpypg def assemble_description')

	if dWpg['PHONEDESCRIPTION'] != 'Possible Phone Numbers:':
			dWpg['DESCRIPTION'] = dWpg['PHONEDESCRIPTION']
	if dWpg['EMAILDESCRIPTION'] != 'Possible Emails:':
		if dWpg['DESCRIPTION'] == 'None':
			dWpg['DESCRIPTION'] = dWpg['EMAILDESCRIPTION']
		else:
			dWpg['DESCRIPTION'] = '{0}\n\n{1}'.format(dWpg['PHONEDESCRIPTION'], dWpg['EMAILDESCRIPTION'])
	return dWpg

# Parce Person's Name
def parce_person_name(dAcc):
	lao.print_function_name('cpypg def parce_person_name')

	PFN, PLN, PMN = '','',''

	# Remove commas, '&' and other stuff
	dic = {',':'',' & ':' '}
	for i, j in dic.items():
		name = dAcc['NAME'].replace(i,j)

	# Proper case the person's name and create list by spaces ' '
	name = lao.propercase(name)
	lName = name.split(' ')

	# Add name components to dAcc
	if len(lName) == 2:
		dAcc['NF'] = lName[0]
		dAcc['NL'] = lName[1]
	elif len(lName) == 3:
		# Name with sufix
		if lName[2] == 'JR' or lName[2] == 'JR.' or lName[2] == 'SR' or lName[2] == 'SR.' or lName[2] == 'II' or lName[2] == 'III':
			dAcc['NF'] = lName[0]
			dAcc['NL'] = lName[1]
		else:
			dAcc['NF'] = lName[0]
			dAcc['NM'] = lName[1]
			dAcc['NL'] = lName[2]
	else:
		dAcc = td.parse_person(dAcc)

	return dAcc

# Print dAcc and dWpg
def compare_dAcc_and_dWpg(strField, strAcc, strWpg, dWpg):
	lao.print_function_name('cpypg def compare_dAcc_and_dWpg')

	while 1:
		info_print_confirm(dWpg, dAcc='None', confirm_it=False)
		data_source = '{0}:'.format(dWpg['SOURCE'])
		print('-' * 50)
		td.colorText('  Select Info: {0}\n'.format(strField), 'YELLOW')
		print('  1) {0:20}  {1}'.format('TerraForce:', strAcc))
		print('  2) {0:20}  {1}'.format(data_source, strWpg))
		print('     - or type different {0} value'.format(strField))
		print('\n 00) Quit')
	
		ui = td.uInput('\n Select info to use or type in info > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			return strAcc, strAcc
		elif ui == '2':
			return strWpg, strWpg
		elif len(ui) > 2:
			return ui, ui
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)

# Update dAcc with dWpg
def update_dAcc_with_dWpg(dAcc, dWpg, compare_it=True):
	lao.print_function_name('cpypg def update_dAcc_with_dWpg')

	lao.banner('Update Contact Info')
	lFields = ['ENTITY', 'NAME', 'TITLEPERSON', 'STREET', 'CITY', 'STATE', 'ZIPCODE', 'PHONE', 'MOBILE', 'EMAIL', 'WEBSITE', 'DESCRIPTION']

	for strField in lFields:
		strAcc, strWpg = '', ''
		# Update dAcc
		if dWpg[strField] != 'None':                 # Skip 'None' values
			if dAcc[strField] == 'None':             # Update dAcc if 'None' value
				dAcc[strField] = dWpg[strField]
		# Update dWpg
		if dAcc[strField] != 'None':                 # Skip 'None' values
			if dWpg[strField] == 'None':             # Update dAcc if 'None' value
				dWpg[strField] = dAcc[strField]
		

		if dAcc[strField] != dWpg[strField]:   # Have use confirm if vals !=
			strAcc = dAcc[strField]
			strWpg = dWpg[strField]
			if compare_it:                       # Have user pick the field value
				dAcc[strField], dWpg[strField] = compare_dAcc_and_dWpg(strField, strAcc, strWpg, dWpg)

				# Add to Description if email or phone has changed
				if strField in 'PHONE MOBILE EMAIL':
					if strAcc != dAcc[strField]:
						strField_titlecase = strField.title()
						# Skip if phone or email is already in the Description
						if strAcc in dAcc['DESCRIPTION']:
							pass
						elif dAcc['DESCRIPTION'] == 'None':
							dAcc['DESCRIPTION'] = f'Possible {strField_titlecase}:\n{strAcc}'
						else:
							dAcc['DESCRIPTION'] = '{0}\nPossible {1}:\n{2}'.format(dAcc['DESCRIPTION'], strField_titlecase, strAcc)
				# if strField == 'PHONE':
				# 	if strAcc != dAcc['PHONE']:
				# 		if dAcc['DESCRIPTION'] == 'None':
				# 			dAcc['DESCRIPTION'] = f'Possible Phone Number:\n{strAcc}'
				# 		elif strAcc in dAcc['DESCRIPTION']:
				# 			pass
				# 		else:
				# 			dAcc['DESCRIPTION'] = '{0}\nPossible Phone Number:\n{1}'.format(dAcc['DESCRIPTION'], strAcc)
				# elif strField == 'MOBILE':
				# 	if strAcc != dAcc['MOBILE']:
				# 		if dAcc['DESCRIPTION'] == 'None':
				# 			dAcc['DESCRIPTION'] = f'\nPossible Mobile Number:\n{strAcc}'
				# 		elif strAcc in dAcc['DESCRIPTION']:
				# 			pass
				# 		else:
				# 			dAcc['DESCRIPTION'] = '{0}\nPossible Mobile Number:\n{1}'.format(dAcc['DESCRIPTION'], strAcc)
				# elif strField == 'EMAIL':
				# 	if strAcc != dAcc['EMAIL']:
				# 		if dAcc['DESCRIPTION'] == 'None':
				# 			dAcc['DESCRIPTION'] = f'\nPossible Email:\n{strAcc}'
				# 		elif strAcc in dAcc['DESCRIPTION']:
				# 			pass
				# 		else:
				# 			dAcc['DESCRIPTION'] = '{0}\nPossible Email:\n{1}'.format(dAcc['DESCRIPTION'], strAcc)
			else:  # User has already determined the field value so update dAcc
				dAcc[strField] = dWpg[strField]
			
	return dAcc

# Perform the Copy Page scrape
def get_contact_info_from_webpage(dAcc):
	lao.print_function_name('cpypg def get_contact_info_from_webpage')

	while 1:
		dWpg = get_webpage_dict(dAcc)
		
				
		# Determine Source and run the appropriate function to scrape info
		dWpg = get_source(dWpg)

		if dWpg['SOURCE'] == 'Address Only':
			dWpg = Address_Only(dWpg)
		elif dWpg['SOURCE'] == 'Arizona Corporation Commission':
			dWpg = Arizona_Corporation_Commission(dWpg)
		elif dWpg['SOURCE'] == 'D&B Hoovers':
			dWpg = DnB_Hoovers(dWpg)
		elif dWpg['SOURCE'] == 'Dun & Bradstreet Cloud':
			dWpg = Dun_Bradstreet_Cloud(dWpg)
		elif dWpg['SOURCE'] == 'FastPeopleSearch':
			dWpg = Fast_People_Search(dWpg)
		elif dWpg['SOURCE'] == 'Google':
			dWpg = Google(dWpg)
		elif dWpg['SOURCE'] == 'Nexis':
			dWpg = Nexis(dWpg)
		elif dWpg['SOURCE'] == 'OpenCorporates':
			dAcc, dWpg = OpenCorporates(dAcc, dWpg)
		elif dWpg['SOURCE'] == 'Real Yellow Pages':
			dWpg = Real_Yellow_Pages(dWpg)
		elif dWpg['SOURCE'] == 'Sunbiz':
			dWpg = Sunbiz(dWpg)
		elif dWpg['SOURCE'] == 'TruePeopleSearch':
			dWpg = True_People_Search(dWpg)
		elif dWpg['SOURCE'] == 'USA People Search':
			dWpg = USA_People_Search(dWpg)
		
		# Assemble Description
		dWpg = assemble_description(dWpg)

		# Update dAcc with dWpg
		dAcc = update_dAcc_with_dWpg(dAcc, dWpg, compare_it=True)

		# Have the user confirm the info collected or start the copy process over
		dAcc, dWpg = info_print_confirm(dWpg, dAcc, confirm_it=True)

		if dWpg['INFOCONFIRMED']:
			dAcc = update_dAcc_with_dWpg(dAcc, dWpg, compare_it=False)
			# Parce Person NAME
			if dAcc['NAME'] != 'None':
				dAcc = parce_person_name(dAcc)
			# Proper case Entity
			if dAcc['ENTITY'] != 'None':
				dAcc['ENTITY'] = lao.propercase(dAcc['ENTITY'])
			return dAcc
		else:
			td.warningMsg('\n Starting copy process over...')
			lao.sleep(1)
	
	return dAcc

# Print scraped info and have use confirm it
def info_print_confirm(dWpg, dAcc='None', confirm_it=True):
	lao.print_function_name('cpypg def info_print_confirm')

	while 1:
		print('-' * 50)
		td.banner('Contact Info Update (cpypg.py)')

		print('CONTACT INFO - Source: {0}\n'.format(dWpg['SOURCE']))
		if confirm_it:
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
		else:
			msg = \
				'  Entity:      {0}\n' \
				'  Person:      {1}\n' \
				'  Title:       {2}\n\n' \
				'  Address:     {3}\n' \
				'               {4}, {5} {6}\n\n' \
				'  Phone:       {7}\n' \
				'  Mobile:      {8}\n' \
				'  Email:       {9}\n' \
				'  Website:     {10}\n\n' \
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
		if confirm_it:
			ui = td.uInput('\n Select > ')
			if ui == '00':
				exit('\n Terminating program...')
			elif ui == '1':
				dWpg['INFOCONFIRMED'] = True
				return dAcc, dWpg
			elif ui == '2':
				dWpg['INFOCONFIRMED'] = False
				return dAcc, dWpg
			elif ui == '10':
				dWpg['ENTITY'] = td.uInput('\n Type new Entity > ')
				dWpg['ENTITY'] = dWpg['ENTITY'].strip()
				dAcc['ENTITY'] = dWpg['ENTITY']
			elif ui == '11':
				dWpg['NAME'] = td.uInput('\n Type new Person > ')
				dWpg['NAME'] = dWpg['NAME'].strip()
				dAcc['NAME'] = dWpg['NAME']
			elif ui == '12':
				dWpg['TITLEPERSON'] = td.uInput('\n Type new Title > ')
				dWpg['TITLEPERSON'] = dWpg['TITLEPERSON'].strip()
				dAcc['TITLEPERSON'] = dWpg['TITLEPERSON']
			elif ui == '13':
				dWpg['STREET'] = td.uInput('\n Type new Street > ')
				dWpg['STREET'] = dWpg['STREET'].strip()
				dWpg = td.address_formatter(dWpg)
				dAcc['STREET'] = dWpg['STREET']
			elif ui == '14':
				dWpg['ZIPCODE'] = td.uInput('\n Type new Zip Code > ')
				dWpg['ZIPCODE'] = dWpg['ZIPCODE'].strip()
				dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
				dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'] = dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] 
			elif ui == '15':
				dWpg['PHONE'] = td.uInput('\n Type new Phone > ')
				dWpg['PHONE'] = dWpg['PHONE'].strip()
				dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
				dAcc['PHONE'] = dWpg['PHONE']
			elif ui == '16':
				dWpg['MOBILE'] = td.uInput('\n Type new Mobile > ')
				dWpg['MOBILE'] = dWpg['MOBILE'].strip()
				dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
				dAcc['MOBILE'] = dWpg['MOBILE']
			elif ui == '17':
				dWpg['EMAIL'] = td.uInput('\n Type new Email > ')
				dWpg['EMAIL'] = dWpg['EMAIL'].strip()
				dAcc['EMAIL'] = dWpg['EMAIL']
			elif ui == '18':
				dWpg['WEBSITE'] = td.uInput('\n Type new Website > ')
				dWpg['WEBSITE'] = dWpg['WEBSITE'].strip()
				dAcc['WEBSITE'] = dWpg['WEBSITE']
			# User pasted email
			elif '@' in ui and '.' in ui:
				dWpg['EMAIL'] = ui.strip()
				dWpg['EMAIL'] = dWpg['EMAIL'].lower()
				dAcc['EMAIL'] = dWpg['EMAIL']
			# User pasted website
			elif 'https:' in ui:
				dWpg['WEBSITE'] = ui.strip()
				dAcc['WEBSITE'] = dWpg['WEBSITE']
			elif 'www.' in ui:
				dWpg['WEBSITE'] = ui.strip()
				dAcc['WEBSITE'] = dWpg['WEBSITE']
			# User pasted phone
			elif len(ui) > 2:
				try:
					# phoneDigits = filter(lambda x: x.isdigit(), phone)
					phoneDigits = ''.join(filter(str.isdigit, ui))
					dWpg['PHONE'] = phoneDigits.strip()
					dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
					dAcc['PHONE'] = dWpg['PHONE']
				except TypeError:
					td.warningMsg('\n Invalid input try again...')
			else:
				td.warningMsg('\n Invalid input try again...')
				lao.sleep(1)
			# Remove Blanks
			for row in dWpg:
				if row == '':
					dWpg[row] == 'None'
			
		else:			
			return dAcc, dWpg

# Account info final confirmation
# Print scraped info and have user confirm it
# def info_print_final_confirm(dWpg, dAcc='None', confirm_it=True):
def info_print_final_confirm(dAcc):
	lao.print_function_name('cpypg def info_print_confirm')

	while 1:
		print('-' * 50)
		td.banner('Contact Info Final Confirm')

		print('CONTACT INFO\n')
		td.colorText('   1) Accept Info', 'CYAN')
		# td.colorText('   2) Reject Info and Try Again', 'CYAN')
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
				dAcc['ENTITY'],
				dAcc['NAME'],
				dAcc['TITLEPERSON'],
				dAcc['STREET'],
				dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'],
				dAcc['PHONE'],
				dAcc['MOBILE'],
				dAcc['EMAIL'],
				dAcc['WEBSITE'])
		print(msg)

		print(' Select an option to modify or Accept the Info')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			return dAcc
		elif ui == '10':
			dAcc['ENTITY'] = td.uInput('\n Type new Entity > ')
			dAcc['ENTITY'] = dAcc['ENTITY'].strip()
		elif ui == '11':
			dAcc['NAME'] = td.uInput('\n Type new Person > ')
			dAcc['NAME'] = dAcc['NAME'].strip()
		elif ui == '12':
			dAcc['TITLEPERSON'] = td.uInput('\n Type new Title > ')
			dAcc['TITLEPERSON'] = dAcc['TITLEPERSON'].strip()
		elif ui == '13':
			dAcc['STREET'] = td.uInput('\n Type new Street > ')
			dAcc['STREET'] = dAcc['STREET'].strip()
			dAcc = td.address_formatter(dAcc)

		elif ui == '14':
			dAcc['ZIPCODE'] = td.uInput('\n Type new Zip Code > ')
			dAcc['ZIPCODE'] = dAcc['ZIPCODE'].strip()
			dAcc['CITY'], dAcc['STATE'], USA = lao.zipCodeFindCityStateCountry(dAcc['ZIPCODE'])
		elif ui == '15':
			dAcc['PHONE'] = td.uInput('\n Type new Phone > ')
			dAcc['PHONE'] = dAcc['PHONE'].strip()
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
		elif ui == '16':
			dAcc['MOBILE'] = td.uInput('\n Type new Mobile > ')
			dAcc['MOBILE'] = dAcc['MOBILE'].strip()
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
		elif ui == '17':
			dAcc['EMAIL'] = td.uInput('\n Type new Email > ')
			dAcc['EMAIL'] = dAcc['EMAIL'].strip()

		elif ui == '18':
			dAcc['WEBSITE'] = td.uInput('\n Type new Website > ')
			dAcc['WEBSITE'] = dAcc['WEBSITE'].strip()
		# User pasted email
		elif '@' in ui and '.' in ui:
			dAcc['EMAIL'] = ui.strip()
			dAcc['EMAIL'] = dAcc['EMAIL'].lower()
		# User pasted website
		elif 'https:' in ui:
			dAcc['WEBSITE'] = ui.strip()
		elif 'www.' in ui:
			dAcc['WEBSITE'] = ui.strip()
		# User pasted phone
		elif len(ui) > 2:
			try:
				# phoneDigits = filter(lambda x: x.isdigit(), phone)
				phoneDigits = ''.join(filter(str.isdigit, ui))
				dAcc['PHONE'] = phoneDigits.strip()
				dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			except TypeError:
				td.warningMsg('\n Invalid input try again...')
				lao.sleep(1)
		else:
			td.warningMsg('\n Invalid input try again...')
			lao.sleep(1)
		# Remove Blanks
		for row in dAcc:
			if row == '':
				dAcc[row] == 'None'
			
		

		
# WEBPAGE SCRAPES -------------------------------------------------------

# Address Only
def Address_Only(dWpg):
	lao.print_function_name('cpypg def Address_Only')

	address = ''
	for i, element in enumerate(dWpg['LPAGE']):
		address = '{0} {1}'.format(address, dWpg['LPAGE'][i])
	address = address.strip()
	# Remove pipe
	address = address.replace(' | ', ' ')
	while 1:
		print('\n Address')
		td.colorText('\n  {0}'.format(address), 'GREEN')
		ui = td.uInput('\n Accept address [0/1/00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(address)
			dWpg = td.address_formatter(dWpg)
			break
		elif ui == '0':
			td.warningMsg('\n Address rejected...')
			lao.sleep(1)
			break
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(1)
	return dWpg

# Arizona Corporation Commission
def Arizona_Corporation_Commission(dWpg):
	lao.print_function_name('cpypg def Arizona_Corporation_Commission')
	# Get Address
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Attention:Address:' in element:
			address = dWpg['LPAGE'][i]
			address = address.replace('Attention:Address:', '')
			if 'County:' in address:
				end_line = address.find('County:')
				address = address[:end_line]
			address = address.replace(', USA', '')
			address = address.strip()
			print(address)
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(address)
			dWpg = td.address_formatter(dWpg)
			dWpg['STREET'] = td.get_abbreviate_street_name(dWpg['STREET'])
			break

	# Get Enitity
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Entity Name:' in element:
			entity = dWpg['LPAGE'][i].replace('Entity Name:', '')
			end_line = entity.find('Entity ID:')
			entity = entity[:end_line]
			dWpg['ENTITY'] = td.propercase(entity)


	# Get Contact Name
	end_get_contact_name = False
	while end_get_contact_name is False:
		for i, element in enumerate(dWpg['LPAGE']):
			if 'Title\tName' in element:
				i_count = 1
				print('\n Contact Persons')
				print('\n 0) None')
				end_principal_information = False
				while end_principal_information is False:
					lTitle_Name = dWpg['LPAGE'][i + i_count].split('\t')
					if lTitle_Name[1] != '':
						print('\n {0}) {1}, {2}'.format(i_count, lTitle_Name[1], lTitle_Name[0]))
					i_count += 1
					if 'Previous' in dWpg['LPAGE'][i + i_count] or 'Page 1' in dWpg['LPAGE'][i + i_count]:
						end_principal_information = True
				print('\n 00) Quit')
				ui = td.uInput('\n Select > ')
				if ui == '0':
					end_get_contact_name = True
					break
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					i_selected = int(ui)
					lTitle_Name = dWpg['LPAGE'][i + i_selected].split('\t')
					# Catch no name selected
					if lTitle_Name[1] == '':
						td.warningMsg('\n No contact name selected...try again...')
						lao.sleep(3)
						break
					dWpg['NAME'] = lTitle_Name[1]
					dWpg = td.parse_person(dWpg)
					print(dWpg['NAME'])
					end_get_contact_name = True

	return dWpg

# Dun & Bradstreet Cloud
def Dun_Bradstreet_Cloud(dWpg):
	lao.print_function_name('cpypg def Dun_Bradstreet_Cloud')

	for i, element in enumerate(dWpg['LPAGE']):
		if 'D&B Business Directory' in element:
			dWpg['ENTITY'] = dWpg['LPAGE'][i + 2]
			dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Key Principal: ' in element:
			dWpg['NAME'] = dWpg['LPAGE'][i]
			dWpg['NAME'] = dWpg['NAME'].replace('Key Principal: ', '')
			dWpg['NAME'] = dWpg['NAME'].replace(' See more contacts', '')
			dWpg['NAME'] = dWpg['NAME'].strip()
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Address: ' in element:
			dWpg['ADDRESSFULL'] = dWpg['LPAGE'][i].replace('Address: ', '')
			dWpg['ADDRESSFULL'] = dWpg['ADDRESSFULL'].replace('See other locations', '')
			dWpg['ADDRESSFULL'] = dWpg['ADDRESSFULL'].replace('United States', '')
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(dWpg['ADDRESSFULL'])
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Website: ' in element:
			dWpg['WEBSITE'] = dWpg['LPAGE'][i].replace('Website: ', '')
			break

	return dWpg

# D&B Hoovers
def DnB_Hoovers(dWpg):
	lao.print_function_name('cpypg def DnB_Hoovers')

	# Is company or person
	if 'EMPLOYEES' in dWpg['LPAGE'] or 'Employees' in dWpg['LPAGE']:
		is_entity = True
	else:
		is_entity = False
	# print(is_entity)

	# is ENTITY
	if is_entity:
		# Find index of ", United States" the line right after the company name
		for i, element in enumerate(dWpg['LPAGE']):
			if ',  United States' in element:
				break
			if ',  Canada' in element:
				break
			if ', United States' in element:
				break
			if ', Canada' in element:
				break
		else:
			td.warningMsg(' "United States" or "Canada" string not found')
			exit('\n Terminating program...')

		# Scrape Entity
		dWpg['ENTITY'] = dWpg['LPAGE'][i - 2]
		dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])

		# Scrape Phone and Website
		phone_website = dWpg['LPAGE'][i + 1]
		if phone_website == '':
			print('no phone')
		else:
			dWpg['PHONE'] = phone_website[3:15]
			dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
			if dWpg['PHONE'] == 'Skip':
				dWpg['PHONE'] = 'None'
			if dWpg['PHONE'] == 'None':
				if 'www.' in phone_website and '.com' in phone_website:
					dWpg['WEBSITE'] = phone_website.strip()
			else:
				dWpg['WEBSITE'] = phone_website[15:]
			if dWpg['WEBSITE'] == '':
				dWpg['WEBSITE'] = 'None'

		# Scrape Address
		i = dWpg['LPAGE'].index('Address')
		dWpg['STREET'] = dWpg['LPAGE'][i + 1]
		csz = dWpg['LPAGE'][i + 2]
		lcsz = csz.split(', ')
		dWpg['ZIPCODE'] = lcsz[2][:5]
		dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
		dWpg = td.address_formatter(dWpg)

		# Select Contacts
		# Check for Contacts if dAcc/dWpg 'NAME' is 'None'
		if dWpg['NAME'] == 'None':
			# Determine if Contacts are listed
			i = dWpg['LPAGE'].index('OneStop')
			if dWpg['LPAGE'][i + 2] == '0':
				td.warningMsg('\n No Contacts in DnB record...\n')
				lao.sleep(3)
			else:
				i = dWpg['LPAGE'].index('Contacts')
				i_count = 0
				print('\n Entity: {0}'.format(dWpg['ENTITY']))
				print('         {0}'.format(dWpg['STREET']))
				print('         {0}, {1} {2}'.format(dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE']))
				print('\n Possible Contacts\n')
				print('  0) None')
				while 1:
					i_count += 1
					if 'View All' in dWpg['LPAGE'][i + i_count]:
						break
					else:
						print('  {0}) {1}'.format(i_count, dWpg['LPAGE'][i + i_count])) # Person Name
						i_count += 1
						print('       {0}'.format(dWpg['LPAGE'][i + i_count])) # Title
						
				print('\n 00) Quit')
				ui = td.uInput('\n Select Contact or Type a Name > ')
				if ui == '00':
					exit('\n Terminating program...')
				elif ui == '0':
					print('\n No Contact selected...')
					lao.sleep(1)
				elif ui.isdigit():
					# Remove Person NAME title
					lPerson = dWpg['LPAGE'][i + int(ui)].split(', ')
					dWpg['NAME'] = lPerson[0]
					dWpg['TITLEPERSON'] = dWpg['LPAGE'][i + int(ui) + 1].title()
				else:
					dWpg['NAME'] = ui

		return dWpg
	# is Person/NAME
	else:
		# Find the line with the person's name
		for i, element in enumerate(dWpg['LPAGE']):
			if 'Closest Industry Peers' in element:
				pos_start = i + 1
				break
		else:
			print(' index not found')
		# Find end point in LPAGE list
		for i, element in enumerate(dWpg['LPAGE']):
			if 'D-U-N-S' in element:
				pos_end = i - 1
				break
		else:
			print(' index not found')
		
		# Create selection menu list
		lMenu = []
		lExclude_Terms = ['Technologies in Use',
						'FINANCIALS',
						'Financial Report (Standardized)',
						'Income Statements',
						'Balance Sheets',
						'Cash Flows',
						'Stock Report',
						'Senior Management (General)',
						'Most Senior Contact',
						'Back to Results']
		for i in range(pos_start, pos_end):
			add_to_lMenu = True
			for term in lExclude_Terms:
				if term in dWpg['LPAGE'][i]:
					add_to_lMenu = False
			if add_to_lMenu:
				lMenu.append(dWpg['LPAGE'][i])

		# Best guess populate dWpg
		dWpg['NAME'] = lMenu[0]
		dWpg['TITLEPERSON'] = lMenu[1]
		# Find Address, ENTITY in lMenu
		for i, element in enumerate(lMenu):
			if ' United States' == element[-14:]:
				dWpg['ENTITY'] = lMenu[i - 2]
				dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])
				dWpg['STREET'] = lMenu[i - 1]
				csz = lMenu[i]
				lcsz = csz.split(', ')
				dWpg['ZIPCODE'] = lcsz[2][:5]
				dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
				dWpg = td.address_formatter(dWpg)
				break
		# Remove ENTITY if it maches Peron NAME
		if dWpg['ENTITY'] == dWpg['NAME']:
			dWpg['ENTITY'] = 'None'
		# Find Phone in lMenu
		for i, element in enumerate(lMenu):
			if '+1' in element and '-' in element:
				dWpg['PHONE'] = lMenu[i][3:15]
				dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
				dWpg['WEBSITE'] = lMenu[i][15:]
				if dWpg['WEBSITE'] == '':
					dWpg['WEBSITE'] = 'None'
			if '+1' in element and not '-' in element:
				dWpg['MOBILE'] = lMenu[i][2:]
				dWpg['MOBILE'] = td.phoneFormat(dWpg['MOBILE'])
			if not '+1' in element and '-' in element:
				maybe_mobile = lMenu[i].replace('-', '')
				# print(maybe_mobile)
				# exit()
				if maybe_mobile.isdigit():
					dWpg['MOBILE'] = td.phoneFormat(lMenu[i])
		# Replace PHONE with MOBILE if mobile is populated and phone is not
		if dWpg['PHONE'] == 'None' and dWpg['MOBILE'] != 'None':
			dWpg['PHONE'] = dWpg['MOBILE']
			dWpg['MOBILE'] = 'None'
		# Find EMAIL in lMenu
		for i, element in enumerate(lMenu):
			if '@' in element:
				dWpg['EMAIL'] = lMenu[i]
				break

		info_print_confirm(dWpg, dAcc='None', confirm_it=False)

		# Selecttion menu
		i_menu = 0
		print('\n Selection Menu')
		print('-' * 50)
		for row in lMenu:
			print('   {0}) {1}'.format(i_menu, row))
			i_menu += 1
		print('\n 00) Quit')

		ui = td.uInput('\n Select... > ')
		if ui == '00':
			exit('\n Terminating program...')

	return dWpg

# Fast People Search
def Fast_People_Search(dWpg):
	lao.print_function_name('cpypg def Fast_People_Search')

	#Stop if not the FastPeopleSearch Detailed page
	if not 'Search for...' in dWpg['LPAGE'][1]:
		td.warningMsg(' \n Use the Detailed FastPeopleSearch page...try again...')
		lao.holdup()
		return dWpg

	lLine = dWpg['LPAGE']

	# Find Address
	for i, line in enumerate(lLine):
		if 'Address' in line:
			# The next line contains the address
			dWpg['STREET'] = lLine[i + 1].strip()
			# The next line contains the city, state, and zipcode
			lcity_state_zip = lLine[i + 2].strip().split(' ')
			dWpg['CITY'] = lcity_state_zip[0].strip()
			dWpg['STATE'] = lcity_state_zip[1].strip()
			dWpg['ZIPCODE'] = lcity_state_zip[2].strip()
			break

	# Find Phone Numbers Staring Line
	is_phone = False
	for i, line in enumerate(lLine):
		if 'Phone Numbers' in line:
			i_phone = i
			is_phone = True
			break

	# Make list of Phone Numbers
	if is_phone:
		lPhones = []
		dWpg['PHONEDESCRIPTION'] = 'Possible Phone Numbers:'
		for i in range(i_phone, len(lLine)):
			if lLine[i][:1] == '(':
					lPhones.append(f'{lLine[i][:14]} : {lLine[i + 1].strip()}')
			if 'Sponsored By' in lLine[i]:
				break

		for phone in lPhones:
			# print(phone)
			if 'Wireless' in phone and dWpg['MOBILE'] == 'None':
				dWpg['MOBILE'] = phone[:14]
			elif 'Landline' in phone and dWpg['PHONE'] == 'None':
				dWpg['PHONE'] = phone[:14]
			dWpg['PHONEDESCRIPTION'] = f"{dWpg['PHONEDESCRIPTION']}\n {phone}"

	# Find Email Staring Line
	is_email = False
	for i, line in enumerate(lLine):
		if 'Email' in line:
			i_email = i + 2
			is_email = True
			break

	# Make list of Emails
	if is_email:
		lEmails = []
		for i in range(i_email, len(lLine)):
			if '@' in lLine[i]:
				lEmails.append(lLine[i].strip())
			else:
				break
		# Verify Emails	
		dWpg['EMAIL'], dWpg['EMAILDESCRIPTION'] = webs.email_validation(lEmails, return_description=True)


	return dWpg

# Google
def Google(dWpg):
	lao.print_function_name('cpypg def Google')

	for i, element in enumerate(dWpg['LPAGE']):
		if 'Address: ' in element:
			dWpg['ADDRESSFULL'] = dWpg['LPAGE'][i].replace('Address: ', '')
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(dWpg['ADDRESSFULL'])
		if 'Phone: ' in element:
			dWpg['PHONE'] = dWpg['LPAGE'][i].replace('Phone: ', '')
			dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'])
		
	return dWpg

# Lexis Nexis
def Nexis(dWpg):
	lao.print_function_name('cpypg def Nexis')

	# Is company or person
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Business Summary' in element:
			is_entity = True
			break
		if 'Subject Summary' in element:
			is_entity = False
			break

	# is ENTITY
	if is_entity:
		for i, element in enumerate(dWpg['LPAGE']):
			if 'Business Summary' in element:
				dWpg['ENTITY'] = dWpg['LPAGE'][i + 2]
				dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])
				if 'public filings' in dWpg['LPAGE'][i + 3]:
					dWpg['STREET'] = dWpg['LPAGE'][i + 4]
					csz = dWpg['LPAGE'][i + 5]
				else:
					dWpg['STREET'] = dWpg['LPAGE'][i + 3]
					csz = dWpg['LPAGE'][i + 4]
				lcsz = csz.split(' ')
				dWpg['ZIPCODE'] = lcsz[2][:5]
				dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
				dWpg = td.address_formatter(dWpg)

# OpenCorporates
def OpenCorporates(dAcc, dWpg):
	lao.print_function_name('cpypg def OpenCorporates')

	print('\n OpenCorporates')
	try:
		i = dWpg['LPAGE'].index('Company Number')
	except ValueError:
		td.warningMsg('\n OpenCorporates paste did not work...try again...')
		return dAcc, dWpg
	dWpg['ENTITY'] = dWpg['LPAGE'][i - 1]
	dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])
	try:
		i = dWpg['LPAGE'].index('Registered Address')
		dWpg['STREET'] = dWpg['LPAGE'][i + 1]
		dWpg['ZIPCODE'] = dWpg['LPAGE'][i + 3]
		dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
		dWpg = td.address_formatter(dWpg)
		did_not_find_it = False
	except ValueError:
		did_not_find_it = True
	if did_not_find_it:
		did_not_find_it = False
		try:
			i = dWpg['LPAGE'].index('Head Office Address')
			dWpg['ADDRESS'] = dWpg['LPAGE'][i + 1]
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'],  = td.parce_single_line_address(dWpg['ADDRESS'])
		except ValueError:
			did_not_find_it = True
	if did_not_find_it:
		did_not_find_it = False
		try:
			i = dWpg['LPAGE'].index('Mailing Address')
			dWpg['ADDRESS'] = dWpg['LPAGE'][i + 1]
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'],  = td.parce_single_line_address(dWpg['ADDRESS'])
			print(dWpg['ADDRESS'])
		except ValueError:
			td.warningMsg('\n Could not find address in OpenCorporates.')
			lao.holdup()
	if dWpg['STREET'] != 'None':
		dWpg = td.address_formatter(dWpg)
	

	# Get Contacts
	# Print contact and address in dWpg
	print('\n Entity: {0}'.format(dWpg['ENTITY']))
	print('         {0}'.format(dWpg['STREET']))
	print('         {0}, {1} {2}'.format(dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE']))

	# Check if any contacts exist and if not return dAcc, dWpg
	if dWpg['LPAGE'].count('Directors / Officers') == 0:
		td.warningMsg('\n No Contacts in OpenCorporates record...\n')
		lao.sleep(2)
		return dAcc, dWpg
	
	# Find index of "Directors / Officers" to start printing contacts
	i_count = 0
	i = dWpg['LPAGE'].index('Directors / Officers')

	# Print Possible Contacts
	print('\n Possible Contacts\n')
	# Print current contact if it exists
	if dAcc['NAME'] != 'None':
		td.colorText(f"  0) {dAcc['NAME']} (Current contact)", 'GREEN')
	else:
		print('  0) None')
	
	# Print all contacts in OpenCorporates page
	# Stop terms to stop printing contacts
	lStop_Terms = ['Websites', 'RSS feed icon', 'Recent filings', 'Branches', 'Identifiers', 'Company Addresses', 'Registry Page', 'While we strive', 'Trademark registrations', 'Company filings']
	# Set if a person was found variable
	person_found = False
	while 1:
		i_count += 1
		# Check if we reached the end of the contacts section
		if any(term in dWpg['LPAGE'][i + i_count] for term in lStop_Terms):
			break
		else:
			# Skip Enities, Companies, and other non-person entries
			lPerson = dWpg['LPAGE'][i + i_count].split(', ') # Split name and title
			if lao.coTF(lPerson[0]) is True:
				continue
			else:
				# Print contact
				print(f"  {i_count}) {dWpg['LPAGE'][i + i_count]}")
				person_found = True

	# Check if a person was found
	if person_found is False:
		td.warningMsg('\n No Contacts in OpenCorporates record...\n')
		lao.sleep(2)
		return dAcc, dWpg
	
	print('\n 00) Quit')
	ui = td.uInput('\n Select Contact or Type a Name > ')

	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '0':
		if dAcc['NAME'] != 'None':
			print(f"\n Current contact {dAcc['NAME']} selected...")
			dWpg['NAME'] = dAcc['NAME']
		else:
			print('\n No Contact selected...')
		lao.sleep(1)
	elif ui.isdigit():
		# Remove Person NAME title
		lPerson = dWpg['LPAGE'][i + int(ui)].split(', ')
		dWpg['NAME'] = lPerson[0]
		dAcc['NAME'] = dWpg['NAME'] 
	else:
		dWpg['NAME'] = ui
		dAcc['NAME'] = dWpg['NAME'] 

	return dAcc, dWpg

# Real Yellow Pages
def Real_Yellow_Pages(dWpg):
	lao.print_function_name('cpypg def Real_Yellow_Pages')

	for i, element in enumerate(dWpg['LPAGE']):
		if 'CLOSED NOW' in element or 'OPEN NOW' in element:
			dWpg['ENTITY'] = dWpg['LPAGE'][i - 3]
			dWpg['ENTITY'] = dWpg['ENTITY'].replace('\xef\xbb\xbf', '')
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Phone: ' in element:
			dWpg['PHONE'] = dWpg['LPAGE'][i].replace('Phone: ', '')
			dWpg['PHONE'] = td.phoneFormat(dWpg['PHONE'], '')
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Address: ' in element:
			dWpg['ADDRESSFULL'] = dWpg['LPAGE'][i].replace('Address: ', '')
			dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(dWpg['ADDRESSFULL'])
			break
	for i, element in enumerate(dWpg['LPAGE']):
		if 'Website: ' in element:
			dWpg['WEBSITE'] = dWpg['LPAGE'][i].replace('Website: ', '')
	return dWpg

# Sunbiz Florida
def Sunbiz(dWpg):
	lao.print_function_name('cpypg def Sunbiz')

	print('\n Sunbiz')
	i = dWpg['LPAGE'].index('Detail by Entity Name')
	dWpg['ENTITY'] = dWpg['LPAGE'][i + 3]
	dWpg['ENTITY'] = td.format_entity_name(dWpg['ENTITY'])
	i = dWpg['LPAGE'].index('Principal Address')
	dWpg['STREET'] = dWpg['LPAGE'][i + 1]
	csz = dWpg['LPAGE'][i + 2]
	lcsz = csz.split(', ')
	dWpg['ZIPCODE'] = lcsz[2][:5]
	dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
	dWpg = td.address_formatter(dWpg)

	# Get Contact
	i_count = 0
	i = dWpg['LPAGE'].index('Name & Address')
	print('\n Entity: {0}'.format(dWpg['ENTITY']))
	print('         {0}'.format(dWpg['STREET']))
	print('         {0}, {1} {2}'.format(dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE']))
	print('\n Possible Contacts\n')
	print('  0) None')
	while 1:
		i_count += 1
		if 'Annual Reports' in dWpg['LPAGE'][i + i_count]:
			break
		elif dWpg['LPAGE'][i + i_count] == '':
			continue
		elif 'Title' in dWpg['LPAGE'][i + i_count]:
			print('  {0}) {1}'.format(i_count, dWpg['LPAGE'][i + i_count]))
			print('       {0}'.format(i_count, dWpg['LPAGE'][i + i_count] + 2))
			i_count = i_count + 2

			
	print('\n 00) Quit')
	ui = td.uInput('\n Select Contact or Type a Name > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '0':
		print('\n No Contact selected...')
		lao.sleep(1)
	elif ui.isdigit():
		dWpg['NAME'] = dWpg['LPAGE'][i + int(ui) + 2]
	else:
		dWpg['NAME'] = ui

	return dWpg

# True People Search
def True_People_Search(dWpg):
	lao.print_function_name('cpypg def True_People_Search')

	# Person Name is one item before Current Address
	while 1:
		try:
			i = dWpg['LPAGE'].index('Name Search Phone Search Address Search Email Search')
			break
		except ValueError:
			td.warningMsg('\n True People Search paste did not work.')
			td.warningMsg('\n Make sure you the broswer window is wide enough to see\n "Name Search Phone Search Address Search Email Search" at the top of the page.\n Select all and copy the page.')

			ui = td.uInput('\n [Enter] to try again or [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			else:
				return dWpg
	
	dWpg['NAME'] = dWpg['LPAGE'][i + 1]
	
	# Street, city, state, zipcode are next two items in LPAGE list
	i = dWpg['LPAGE'].index('Current Address')
	# Check if 'recently reported address' line is befor the address
	if 'recently reported address' in dWpg['LPAGE'][i + 1]:
		dWpg['STREET'] = dWpg['LPAGE'][i + 2]
		lcsz = dWpg['LPAGE'][i + 3].split(' ')
		dWpg['ZIPCODE'] = lcsz[-1]
	else:
		dWpg['STREET'] = dWpg['LPAGE'][i + 1]
		lcsz = dWpg['LPAGE'][i + 2].split(' ')
		dWpg['ZIPCODE'] = lcsz[-1]
	dWpg['CITY'], dWpg['STATE'], USA = lao.zipCodeFindCityStateCountry(dWpg['ZIPCODE'])
	
	dWpg = td.address_formatter(dWpg)
		
	# Get first Landline and Wireless phone numbers and Emails
	lEmails = []
	# Check if TPS list Phone Numbers and get index if it does
	try:
		i = dWpg['LPAGE'].index('Phone Numbers')
		phone_numbers_exist = True
	except ValueError:
		phone_numbers_exist = False
	if phone_numbers_exist:
		while 1:
			i += 1
			# End loop at "Background Report"
			if 'Background Report' in dWpg['LPAGE'][i]:
				break
			# Get first Landline phone
			if 'Landline' in dWpg['LPAGE'][i] and dWpg['PHONE'] == 'None':
					dWpg['PHONE'] = dWpg['LPAGE'][i][:14]
			# Get first Mobile phome
			elif 'Wireless' in dWpg['LPAGE'][i] and dWpg['MOBILE'] == 'None':
				dWpg['MOBILE'] = dWpg['LPAGE'][i][:14]

	# Make Description entry of phone numbers and reported date
	if phone_numbers_exist:
		i = dWpg['LPAGE'].index('Phone Numbers')
		while 1:
			i += 1
			# End loop at "Background Report"
			if 'Background Report' in dWpg['LPAGE'][i]:
				break
			if 'Landline' in dWpg['LPAGE'][i] or 'Wireless' in dWpg['LPAGE'][i]:
				# Add Phone
				# Add Last Reported
				if 'Possible Primary Phone' in dWpg['LPAGE'][i + 1]:
					dWpg['PHONEDESCRIPTION'] = '{0}\n {1} {2}'.format(dWpg['PHONEDESCRIPTION'], dWpg['LPAGE'][i], dWpg['LPAGE'][i + 2])
				elif 'Verizon' in dWpg['LPAGE'][i]:
					continue
				else:
					dWpg['PHONEDESCRIPTION'] = '{0}\n {1} {2}'.format(dWpg['PHONEDESCRIPTION'], dWpg['LPAGE'][i], dWpg['LPAGE'][i + 1])

	# Get Emails
	for row in dWpg['LPAGE']:
		if '@' in row and not 'truepeoplesearch.com' in row:
			lEmails.append(row.strip())

	# Add emails to Description emails
	# print(lEmails)
	if lEmails == []:
		dWpg['EMAILDESCRIPTION'] = 'Possible Emails:'
	else:
		dWpg['EMAIL'], dWpg['EMAILDESCRIPTION'] = webs.email_validation(lEmails, return_description=True)

	return dWpg

# USA People Search
def USA_People_Search(dWpg):
	lao.print_function_name('cpypg def USA_People_Search')

	# Person Name is one item before Current Address
	while 1:
		try:
			i = dWpg['LPAGE'].index('USA people search logo')
			break
		except ValueError:
			td.warningMsg('\n USA People Search paste did not work.')
			td.warningMsg('\n Make sure you the broswer window is wide enough to see\n "Name Search Phone Search Address Search Email Search" at the top of the page.\n Select all and copy the page.')

			ui = td.uInput('\n [Enter] to try again or [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			else:
				return dWpg
	
	
	
	# Street, city, state, zipcode are next two items in LPAGE list
	i = dWpg['LPAGE'].index(' Current Address:')
	print(dWpg['LPAGE'][i - 1])
	print(dWpg['LPAGE'][i])
	print(dWpg['LPAGE'][i + 2])
	name_temp = dWpg['LPAGE'][i - 1]
	# Example: William S Landis, Age 60
	dWpg['NAME'] = name_temp.split(',')[0].strip()
	# Full Address
	dWpg['STREET'], dWpg['CITY'], dWpg['STATE'], dWpg['ZIPCODE'] = td.parce_single_line_address(dWpg['LPAGE'][i + 2])
	
	dWpg = td.address_formatter(dWpg)
		

	# Check if TPS list Phone Numbers and get index if it does
	try:
		i = dWpg['LPAGE'].index(' Current Phone Number:')
		phone_numbers_exist = True
	except ValueError:
		phone_numbers_exist = False
	if phone_numbers_exist:
			# Get first Landline phone
			if 'Landline' in dWpg['LPAGE'][i + 2] and dWpg['PHONE'] == 'None':
					dWpg['PHONE'] = dWpg['LPAGE'][i + 2][:14]
			# Get first Mobile phone
			elif 'Wireless' in dWpg['LPAGE'][i + 2] and dWpg['MOBILE'] == 'None':
				dWpg['MOBILE'] = dWpg['LPAGE'][i + 2][:14]

	# Make Description entry of phone numbers and reported date
	try:
		i = dWpg['LPAGE'].index(' Prior Phone Numbers:')
		phone_numbers_exist = True
	except ValueError:
		phone_numbers_exist = False
	
	if phone_numbers_exist:
		i += 1
		while 1:
			i += 1
			# End loop at "Show More..."
			if 'Show More...' in dWpg['LPAGE'][i]:
				break
			else:
				dWpg['PHONEDESCRIPTION'] = '{0}\n {1}'.format(dWpg['PHONEDESCRIPTION'], dWpg['LPAGE'][i])

	return dWpg


