# Text and Date formatting

import dicts
# import fun_text_date as td
import lao
import datetime
from os import system
from pprint import pprint
import re

################################################################################
#                         ADDRESS & PHONE FORMATING 
################################################################################

# Formats Address to Title case and 
def address_formatter(dAcc):
	import lao
	
	lao.print_function_name('td def address_formatter')

	if 'STREET' in dAcc.keys():
		if dAcc['STREET'].isupper():
			dAcc['STREET'] = titlecase_street(dAcc['STREET'])
		dAcc['STREET'] = get_abbreviate_street_name(dAcc['STREET'])

	if 'CITY' in dAcc.keys():
		if dAcc['CITY'].isupper():
			dAcc['CITY'] = dAcc['CITY'].title()
	
	if 'STATE' in dAcc.keys():
		if len(dAcc['STATE']) > 2:
			dAcc['STATE'] = lao.convertState(dAcc['STATE'])
		# if dAcc['CITY'].isupper():
		# 	dAcc['CITY'] = dAcc['CITY'].title()
	return dAcc

# Abbreviates Steet words
def get_abbreviate_street_name(street):

	street = street.replace('.', '')
	street = street.replace(',', '')
	street = street.replace('\n', ' ')
	street = street.replace(' | ', ', ')
	street = street.replace(' |', ' ')
	street = street.replace('|', ' ')

	street = street.replace(' North ', ' N ')
	street = street.replace(' South ', ' S ')
	street = street.replace(' East ', ' E ')
	street = street.replace(' West ', ' W ')
	street = street.replace(' Northwest ', ' NW ')
	street = street.replace(' Northeast ', ' NE ')
	street = street.replace(' Southwest ', ' SW ')
	street = street.replace(' Southeast ', ' SE ')

	street = street.replace('Avenue', 'Ave')
	street = street.replace('Boulevard', 'Blvd')
	street = street.replace(' Circle', ' Cir')
	street = street.replace('Drive', 'Dr')
	street = street.replace('Expressway', 'Exp')
	street = street.replace('Floor', 'Fl')
	street = street.replace('Freeway', 'Fwy')
	street = street.replace('Highway', 'Hwy')
	street = street.replace('Junction', 'Jct')
	street = street.replace(' Lane', 'Ln')
	street = street.replace('Parkway', 'Pkwy')
	street = street.replace(' Street', ' St')
	street = street.replace(' Trail', 'Tr')
	street = street.replace(', Suite ', ' Ste ')
	street = street.replace(' Suite ', ' Ste ')
	street = street.replace(' Ste ', ', Ste ')
	street = street.replace(' Unit ', ' Ste ')

	street = street.replace('0TH ', '0th ')
	street = street.replace('1ST ', '1st ')
	street = street.replace('2ND ', '2nd ')
	street = street.replace('3RD ', '3rd ')
	street = street.replace('4TH ', '4th ')
	street = street.replace('5TH ', '5th ')
	street = street.replace('6TH ', '6th ')
	street = street.replace('7TH ', '7th ')
	street = street.replace('8TH ', '8th ')
	street = street.replace('9TH ', '9th ')

	return street

# Parces a single line address
def parce_single_line_address(ADDRESS, dAcc='None'):
	lao.print_function_name('td def parce_single_line_address')
	# Remove commas and extra spaces
	ADDRESS = (ADDRESS.upper()).replace(',', '').strip()
	# Remove United States
	if ADDRESS[-14:] == ' UNITED STATES':
		ADDRESS = ADDRESS[:-14]
	# Remove USA
	elif ADDRESS[-4:] == ' USA':
		ADDRESS = ADDRESS[:-4]
	elif ADDRESS[-3:] == ' US':
		ADDRESS = ADDRESS[:-3]
	
	# Remove Zip+4 if it exists
	zip_plus_four_pattern = r'\b(\d{5})-(\d{4})\b'
	if re.search(zip_plus_four_pattern, ADDRESS):
		ADDRESS = ADDRESS[:-5]

	# Split address into a list
	lAddress = ADDRESS.split()
	

	lAddress[-1] = lAddress[-1].strip()
	zipOriginal = lAddress[-1]
	# Process ZipCode
	if len(lAddress[-1]) == 6:
		lAddress[-2] = '{0}{1}'.format(lAddress[-2], lAddress[-1])
		del lAddress[-1]
	# Zip plus 4 digit zip code
	elif len(lAddress[-1]) > 5:
		if len(lAddress[-1]) == 9:
			lAddress[-1] = lAddress[-1][:-4]

	# Mannual entry if address is incomplete based lack of zip code
	if len(lAddress[-1]) != 5:
		while 1:
			print(ADDRESS)
			street = (uInput('\n Manually enter Street > ')).upper()
			zipcode = (uInput('\n Manually enter Zipcode > ')).upper()
			city, state, USA = lao.zipCodeFindCityStateCountry(zipcode)
			print('\n\n Check Addres\n')
			print(' Street:  {0}'.format(street))
			print(' City:    {0}'.format(city))
			print(' State:   {0}'.format(state))
			print(' Zipcode: {0}'.format(zipcode))
			ui = uInput('\n Approve Address [0/1] > ')
			if ui == '1':
				break
			else:
				warningMsg('\n Try again...\n')
	else:
		zipcode = lAddress[-1]
		city, state, USA = lao.zipCodeFindCityStateCountry(zipcode)
		city = city.upper()
		# Remove all text past the last occurence of the city string
		pos = ADDRESS.rfind(city)
		street = ADDRESS[:pos]
		street = street.strip()
		street = get_abbreviate_street_name(street)

		# Check if mismatch city and if so remove the city, state & zip from the street
		if city not in ADDRESS:
			lStreet = street.split(' ')
			lStreet = lStreet[:-3]
			street = ' '.join(lStreet)

	if dAcc == 'None':
		return street, city, state, zipcode
	else:
		# Add to dAcc dict
		dAcc['STREET'] = street
		dAcc['CITY'] = city
		dAcc['STATE'] = state
		dAcc['ZIPCODE'] = zipcode
		return dAcc

# Titlecase Street Address String
def titlecase_street(street):
	if street.isupper():
		if 'PO BOX' in street:
			street = street.replace('PO BOX', 'PO Box')
		elif 'P O BOX' in street:
			street= street.replace('P O BOX', 'PO Box ')
		elif 'P.O. BOX' in street:
			street= street.replace('P.O. BOX', 'PO Box ')
		elif street[:4] == 'BOX ':
			street = street.replace('BOX ', 'PO Box ')
		else:
			street = ' '.join([i.title() if i.isalpha() else i.lower() for i in street.split()]) # titlecases everything but ordinals (ie. 3RD to 3rd)
		if ' Sr ' in street:
			street = street.replace(' Sr ', ' SR ')
		if ' Cr ' in street:
			street = street.replace(' Cr ', ' CR ')
		if ' Fm ' in street:
			street = street.replace(' Fm ', ' FM ')
		if ' u.s. ' in street:
			street = street.replace(' u.s. ', ' U.S. ')
	return street

# Paste and address and format it
def clipboard_address_formatter(dAcc):
	import win32clipboard
	while 1:
		address = uInput('\n Paste address and [Enter] > ')
		# get clipboard data
		if address == '':
			win32clipboard.OpenClipboard()
			data = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
		else:
			while 1:
				data = uInput(' Continue > ')
				if data == '':
					break
				else:
					address = '{0} {1}'.format(address, data)
			data = address

	
		print('\n{0}'.format(data))
		ui = uInput('\n Use this data [0/1/00] > ')
		if ui == '0':
			continue

		# Format address
		elif ui == '1':
			# Remove carrage returns
			data = data.replace('\r\n', ' ')

			# Parce the single line address
			street, city, state, zipcode = parce_single_line_address(data)
			
			# Remove full state name from street
			stateNameFull = (lao.convertState(state)).upper()
			lStreet = street.split(' ')
			if lStreet[-1] == stateNameFull:
				del lStreet[-1]
				street = ' '.join(lStreet)

			# Title case street and city
			street = street.title()
			city = city.title()

			# User to confirm address
			print('\n Street:   {0}'.format(street))
			print(' City:     {0}'.format(city))
			print(' State:    {0}'.format(state))
			print(' Zip Code: {0}'.format(zipcode))
			ui = uInput('\n Use this Address [0/1/00] > ')
			if ui == '0':
				pass
			elif ui == '1':
				dAcc['STREET'] = street
				dAcc['CITY'] = city
				dAcc['STATE'] = state
				dAcc['ZIPCODE'] = zipcode
				break
			elif ui == '00':
				exit('\n Terminating program...')
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			warningMsg('\n Invalid input...try again...')
	return dAcc

# Format any phone number to (###) ###-#### Ext ### (default)
def phoneFormat(phone, phoneFormat='default'):
	# If phone is a float convert to string
	if isinstance(phone, float):
		phone = str(phone)
		phone = phone.replace('.0', '')
	# Skip foreign countries
	if '+' in phone and '+1 ' not in phone and '+1.' not in phone and '+1-' not in phone:
		return phone

	# Remove all characters except for digits
	while 1:
		try:
			# phoneDigits = filter(lambda x: x.isdigit(), phone)
			phoneDigits = ''.join(filter(str.isdigit, phone))
			
		
			break
		except TypeError:
			phone = str(int(phone))

	# Remove USA country code
	if phoneDigits[:1] == '1':
		phoneDigits = phoneDigits[1:]

	if len(phoneDigits) < 10:
		warningMsg(f'\n Invalid phone number: {phone} : only {len(phoneDigits)} digits found...')
		return 'Skip'
	elif phoneFormat == 'MailChimp':
		phone = '{0}-{1}-{2}'.format(phoneDigits[:3], phoneDigits[3:6], phoneDigits[6:10])
	elif len(phoneDigits) > 10:
		phone = '({0}) {1}-{2} Ext {3}'.format(phoneDigits[:3], phoneDigits[3:6], phoneDigits[6:10], phoneDigits[10:])
	else:
		phone = '({0}) {1}-{2}'.format(phoneDigits[:3], phoneDigits[3:6], phoneDigits[6:10])
	return phone

################################################################################
#                              TEXT FORMATING 
################################################################################

# Clears the console and create a banner based on agrument
#   colorama is used for scipts that use django bc it does not support colored
def banner(title, colorama=False):
	import fjson

	function_status = fjson.read_bill_script_msgs_on_off('Banner')
	if function_status == 'Off':
		system('cls')

	ban1 = '        '+('-' * (len(title)+4))
	ban2 = ' ------|'+(' ' * (len(title)+4))+'|------'
	ban3a = '  \\    |  '
	ban3b = '  |    /'
	ban4 = '   \\   |'+ (' ' * (len(title)+4)) + '|   /'
	ban5 = '   /    '+ ('-' * (len(title)+4)) + '    \\'
	ban6 = '  /      )'+ (' ' * (len(title))) + '(      \\'
	ban7 = ' --------'+ (' ' * (len(title))) + '  --------'
	

	# if colorama:
	from colorama import Fore, Back, Style
	print
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban1}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban2}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban3a}{Style.RESET_ALL}', end = '')
	print(f'{title}', end = '')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban3b}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban4}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban5}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban6}{Style.RESET_ALL}')
	print(f'{Fore.BLUE}{Style.BRIGHT}{ban7}{Style.RESET_ALL}\n')
	# else:
	# 	from colored import Fore, Back, Style
	# 	print
	# 	print(f'{Fore.dodger_blue_2}{ban1}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban2}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban3a}{Style.reset}', end = '')
	# 	print(f'{title}', end = '')
	# 	print(f'{Fore.dodger_blue_2}{ban3b}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban4}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban5}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban6}{Style.reset}')
	# 	print(f'{Fore.dodger_blue_2}{ban7}\n{Style.reset}')
	# 	print

# Convert 2 letter state code to full state name and vice versa
def convert_state(state):
	state = state.strip()
	if len(state) > 2:
		state = state.title()
	dState_abbriviations = dicts.get_state_abbriviations_dict()
	return dState_abbriviations[state]

# pass a int or decimal currency and return $###,###
def currency_format_from_number(NUMBER):
	if NUMBER == 'None':
		return 'None'
	NUMBER = int(float(NUMBER))
	NUMBER = '$'+'{:,.0f}'.format(NUMBER)
	return NUMBER

# Make text title case
def make_title_case(txt, onlyIfAllCaps=True):
	# Ignore two letter state codes
	if len(txt) <= 2:
		return txt
	if onlyIfAllCaps:
		if txt.isupper():
			return txt.title()
		else:
			return txt
	return txt.title()

# Convert number with or without commas to integer
def txt_to_int(val):
	try:
		val = val.replace(',', '')
	except AttributeError:
		pass
	try:
		val = int(val)
	except ValueError:
		warningMsg(f'Error: fun_text_date.py def txt_to_int(val)')
		print(f'Error: {val}')
		print(' Returning val = Error')
		return 'Error'
	return val

# Standardize Builder Names based on 
def standarize_builder_names(name, dHB_Rename='None', market='None'):

	# Set default values
	type_pubic_private = 'Private'
	not_in_builder_rename_list = True

	# Load the rename file if not passed in argument
	if dHB_Rename == 'None':
		renameFile = '{0}BuilderRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
		dHB_Rename = lao.spreadsheetToDict(renameFile)


	for row in dHB_Rename:
		# Boise Brighton Homes exception
		if market == 'BOI' and 'BRIGHTON' in name.upper():
			not_in_builder_rename_list = False
			break
		elif dHB_Rename[row]['BUILDER'].upper() == name.upper():
		# if name.upper() in dHB_Rename[row]['BUILDER'].upper() :
			name = dHB_Rename[row]['RENAME']
			type_pubic_private = dHB_Rename[row]['TYPE']
			not_in_builder_rename_list = False
			break
	return name, type_pubic_private, not_in_builder_rename_list

# Standardize MPC Names based on 
def standarize_MPC_names(name, dMPC_Rename='None'):
	name = name.replace(',', '').strip()
	if dMPC_Rename == 'None':
		renameFile = '{0}MPCRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
		dMPC_Rename = lao.spreadsheetToDict(renameFile)
	for row in dMPC_Rename:
		if dMPC_Rename[row]['MPC'].upper() == name.upper():
			try:
				name = dMPC_Rename[row]['RENAME']
			except AttributeError:
				pass
			break
	return name

# Standarize Lender Names
def standarize_lender_names(name, dLender_Rename='None'):
	if dLender_Rename == 'None':
		renameFile = '{0}LenderRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
		dLender_Rename = lao.spreadsheetToDict(renameFile)
	for row in dLender_Rename:
		if dLender_Rename[row]['LENDER'].upper() == name.upper():
			try:
				name = dLender_Rename[row]['RENAME']
			except AttributeError:
				pass
			break
	return name

# Sets the title of the console window to use for finding it with os
def console_title(title):
	import os
	os.system(f'title {title}')

# Print in color
#   colorama is used for scipts that use django bc it does not support colored
def colorText(text, color, colorama=False):
	color = color.upper()

	if colorama:
		from colorama import Fore, Back, Style
		color = color.upper()
		if color == 'BLUE':
			print(f'{Fore.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}')
		if color == 'CYAN':
			print(f'{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}')
		if color == 'GREEN':
			print(f'{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}')
		if color == 'PURPLE':
			print(f'{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}')
		if color == 'RED':
			print(f'{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}')
		if color == 'YELLOW':
			print(f'{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}')
	else:
		from colored import Fore, Back, Style
		if color == 'BLUE':
			print(f'{Fore.dodger_blue_2}{text}{Style.reset}')
		if color == 'BROWN':
			print(f'{Fore.sandy_brown}{text}{Style.reset}')
		if color == 'CYAN':
			print(f'{Fore.cyan_1}{text}{Style.reset}')
		if color == 'GREY' or color == 'GRAY':
			print(f'{Fore.grey_54}{text}{Style.reset}')
		if color == 'GREEN':
			print(f'{Fore.green_1}{text}{Style.reset}')
		if color == 'ORANGE':
			print(f'{Fore.orange_1}{text}{Style.reset}')
		if color == 'PINK':
			print(f'{Fore.hot_pink_1b}{text}{Style.reset}')
		if color == 'PURPLE':
			print(f'{Fore.purple_1b}{text}{Style.reset}')
		if color == 'RED':
			print(f'{Fore.indian_red_1c}{text}{Style.reset}')
		if color == 'YELLOW':
			print(f'{Fore.yellow_2}{text}{Style.reset}')

def color_on_off(color='Off'):
	from colored import Fore, Back, Style

	if color == 'BLUE':
		print(f'{Fore.dodger_blue_2}')
	elif color == 'BROWN':
		print(f'{Fore.sandy_brown}')
	elif color == 'CYAN':
		print(f'{Fore.cyan_1}')
	elif color == 'GREY' or color == 'GRAY':
		print(f'{Fore.grey_54}')
	elif color == 'GREEN':
		print(f'{Fore.green_1}')
	elif color == 'ORANGE':
		print(f'{Fore.orange_1}')
	elif color == 'PINK':
		print(f'{Fore.hot_pink_1b}')
	elif color == 'PURPLE':
		print(f'{Fore.purple_1b}')
	elif color == 'RED':
		print(f'{Fore.indian_red_1c}')
	elif color == 'YELLOW':
		print(f'{Fore.yellow_2}')
	elif color == 'OFF':
		print(f'{Style.reset}')
	else:
		warningMsg('\n Invalid color option in td.color_on_off...')
		ui = uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

# User Input text
def uInput(text, colorama=False):
	if colorama:
		from colorama import Fore, Style
		if text[:2] == '\n ':
			text = text[2:]
			ui = input(f'\n👉 {Fore.BLUE}{text}{Style.RESET_ALL}')
		else:
			ui = input(f'👉 {Fore.BLUE}{text}{Style.RESET_ALL}')
	else:
		from colored import Fore, Style
		if text[:2] == '\n ':
			text = text[2:]
			ui = input(f'\n👉 {Fore.cyan_1}{text}{Style.reset}')
		else:
			ui = input(f'👉 {Fore.cyan_1}{text}{Style.reset}')

	# ui = input(f'\033[96m{text}\033[00m')
	ui = ui.strip()
	return ui

# Print cyan instruction message
#   colorama is used for scipts that use django bc it does not support colored
def instrMsg(text, colorama=False):
	if colorama:
		from colorama import Fore, Style
		print(f'{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}')
	else:
		from colored import Fore, Style
		print(f'{Fore.green_1}{text}{Style.reset}')

# Print yellow warning message
#   colorama is used for scipts that use django bc it does not support colored
def warningMsg(text, colorama=False):
	if colorama:
		from colorama import Fore, Style
		if text[:2] == '\n ':
			text = text[2:]
			print(f'\n⚠️ {Fore.YELLOW}{text}{Style.RESET_ALL}')
		else:
			print(f'⚠️ {Fore.YELLOW}{text}{Style.RESET_ALL}')
	else:
		from colored import Fore, Style
		if text[:2] == '\n ':
			text = text[2:]
			print(f'\n⚠️ {Fore.yellow_2}{text}{Style.reset}')
		else:
			print(f'⚠️ {Fore.yellow_2}{text}{Style.reset}')

# Format Entity NAM
def format_entity_name(entity):
	lao.print_function_name('td def format_entity_name')

	entity = entity.title()
	# Remove period & apostrophe
	entity = entity.replace('.', '')
	entity = entity.replace("'", "")
	# Format Entity suffixes
	dic = {' Llc': ' LLC',
		'L L C': 'LLC',
		' Lp': ' LP',
		' Llp': ' LLP',
		' L L P': ' LLP',
		' Lllp': ' LLLP',
		' Pc': ' PC',
		'K Hovnanian': 'K. Hovnanian'}
	for i, j in dic.items():
		entity = entity.replace(i,j)

	return entity

# Format number to K, M or B (thousands, millions or billions)
def format_number_to_k_m_b(num):
	# Check if negative
	num_is_negative = False
	if int(num) < 0:
		num_is_negative = True
	
	num = abs(num)

	if int(num) >= 1000000000:
		formatted_num = f'{num / 1000000000:.1f}B'
	elif int(num) >= 1000000:
		formatted_num = f'{num / 1000000:.1f}M'
	elif int(num) >= 1000:
		formatted_num = f'{num / 1000:.1f}K'
	else:
		formatted_num = num
	
	if num_is_negative:
		formatted_num = f'-{formatted_num}'
	return formatted_num

# Capitalize Entity Types ############################################################
def format_entity_names(entity_name):
	entity_name_formatted = ''
	lEntity_name = entity_name.split()
	for txt in lEntity_name:
		# Capitalize if txt is 3 characters and does not contain a vowel
		if not any(char in txt for char in 'aeiouAEIOU'):
			txt = txt.upper()
		else:
			txt = txt.title()
		if ',' in txt and ', ' not in txt:
			txt = txt.replace(',', ', ')
		entity_name_formatted = f'{entity_name_formatted} {txt}'
	entity_name_formatted = entity_name_formatted.strip()
	return entity_name_formatted

# Standarize/clean homebuilder & subdivision names
def standarize_hb_and_sub_names(fin, dData, dRename, market):

	# Standarize/clean homebuilder names
	for row in dData:
		if 'BenchmarkObservedClosings' in fin:
			dData[row]['Builder'], pub_prvt, not_in = standarize_builder_names(dData[row]['Builder'], dRename,  market)

			# Add (P) to public builders
			if pub_prvt == 'Public':
				dData[row]['Builder'] = f'{dData[row]["Builder"]} (P)'
		# Standarize/clean MPC names
		elif 'Subdivisions' in fin:
			# Use Subdivision name if Community (MPC) is '-N/C'
			if '-N/C' in dData[row]['Community']:
				sub_name = dData[row]['Subdivision']
			else:
				sub_name = dData[row]['Community']
			dData[row]['Community'] = standarize_MPC_names(sub_name, dRename)
		else:
			print('Error: wrong data type in standarize_names function!')
			exit()

	return dData

# Get the LAO market abbreviation
def get_market_abbreviation(market, county='None'):
	from lao import getCounties
	
	# Temp fix
	if market == 'Georgia':
		return 'Altanta', 'GA'
	elif market == 'Knoxville':
		return 'Nashville', 'TN'


	dCounties = getCounties('FullDict')
	marketAbb = 'None'
	county = county.replace(' ', '').replace('.', '')

	for row in dCounties:
		if county != 'None':
			if market.upper() == dCounties[row]['Market'].upper():
				print(market)
				print(county)
				print(dCounties[row]['County'])
				print
				if county.upper() == dCounties[row]['County'].upper() or county.upper() == dCounties[row]['ArcName'].upper():
					marketAbb = dCounties[row]['MarketAbb']
					stateAbb = dCounties[row]['State']
					break
		else:
			if market.upper() == dCounties[row]['Market'].upper():
				marketAbb = dCounties[row]['MarketAbb']
				stateAbb = dCounties[row]['State']
				break
	# Error check
	if marketAbb == 'None':
		warningMsg('\n Could not determine marketAbb...')
		print('\n Market: {0}'.format(market))
		print(' County: {0}'.format(county))
		warningMsg('\n Terminating program...')
		lao.holdup()
		exit()

	return marketAbb, stateAbb

################################################################################
#                                    PDF FORMATING 
################################################################################

# Open PDF file and return object, reader and number of pages
def open_pdf(pdf_file):
	import PyPDF2
	# if PyPDF2 == 'None':
	# 	import PyPDF2
	# creating a pdf file object
	pdfFileObj = open(pdf_file, 'rb')
	# creating a pdf reader object
	# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	pdf_objcet = PyPDF2.PdfReader(pdfFileObj)
	# printing number of pages in pdf file
	# print(' Pages:  {0}'.format(pdf_objcet.numPages))
	intPages = len(pdf_objcet.pages)
	print(f' Pages:  {intPages}')
	
	return pdfFileObj, pdf_objcet, intPages

# Read pdf data
def read_pdf_data_metrostudy_builders(pdf_objcet, intPages):
	lBuilderData = []
	for page_num in range(0, intPages):
		# pageObj = pdf_objcet.getPage(page_num)
		pageObj = pdf_objcet.pages[page_num]

		# extracting text from page
		pageText = pageObj.extract_text()
		lpageText = pageText.split('\n')

		for row in lpageText:
			if row != '':
				lBuilderData.append(row)

	lBuilderDataCleaned = []
	writeit = True
	for line in lBuilderData:
		if 'Residential Survey' in line:
			writeit = False
		elif '**Inv Supply' in line:
			writeit = True
			continue
		if writeit:
			lBuilderDataCleaned.append(line)
	# 			f.write('{0}\r\n'.format(line))
	# lao.openFile('C:/TEMP/bld.txt')
	# exit()
	return lBuilderDataCleaned

# PERSON FORMATING ###################################################

# parses a persons name from a name or the dAcc dict
def parse_person(PERSON, ask_name_arragement_possiblities=True):
	lao.print_function_name('td def parcePerson')
	# Check if dAcc dict
	if isinstance(PERSON, dict):
		dAcc = PERSON
		PERSON = dAcc['NAME']
		return_dict = True
	else:
		return_dict = False
	PFN, PLN, PMN = '','',''
	print('\n{0}\n'.format(PERSON))
	# remove commas, '&' and other stuff
	dic = {',':'',' & ':' '}

	# for i, j in dic.iteritems():
	for i, j in dic.items():
		PERSON = PERSON.replace(i,j)

	# Proper case the PERSON
	PERSON = propercase(PERSON)

	str = PERSON.split(' ')
	
	i = 0
	print('-' * 50)
	# First and Last Name
	if len(str) == 2:
		if ask_name_arragement_possiblities:
			while 1:
				print('\n Name Arrangement Possibilities\n')
				print('  1) {0} {1}'.format(str[0], str[1]))
				print('  2) {0} {1}'.format(str[1], str[0]))
				print(' 00) Quit')
				ui = uInput('\n Enter match number > ')
				if ui == '1':
					PFN, PMN, PLN = str[0],'',str[1]
					break
				elif ui == '2':
					PFN, PMN, PLN = str[1],'',str[0]
					break
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					warningMsg('\n Invalid input, try again...\n')
			PERSON = f'{PFN} {PLN}'
		else:
			PFN, PMN, PLN = str[0],'',str[1]
	# Name with Suffix
	elif str[2] == 'JR' or str[2] == 'JR.' or str[2] == 'SR' or str[2] == 'SR.' or str[2] == 'II' or str[2] == 'III':
		PFN, PMN = str[0], ''
		PLN = '{0} {1}'.format(str[1], str[2])
	# First, Middle & Last Name
	else:
		if ask_name_arragement_possiblities:
			print('\n Name Arrangement Possibilities\n')
			print(' 0) NO MATCH')
			print(' 1) {0} {1} {2}'.format(str[0], str[1], str[2])) # First, Last, Middle
			print(' 2) {0} {1} {2}'.format(str[1], str[2], str[0])) # Last, First, Middle
			print(' 3) {0} {1}'.format( str[0], str[1])) # First, Last
			print(' 4) {0} {1}'.format(str[1], str[0])) # Last, First
			ui = uInput('\n Enter match number or 0 for no match > ')
			if ui == '1':
				l_2_last_names = ['VAN', 'VON', 'SAINT', 'ST', 'DE', 'DEL']
				if str[1].upper() in l_2_last_names:
					PFN, PNM, PLN = str[0], '', '{0} {1}'.format(str[1], str[2])
				else:
					PFN, PMN, PLN = str[0],str[1],str[2]
			elif ui == '2':
				PFN, PMN, PLN = str[1], str[2], str[0]
			elif ui == '3':
				PFN, PMN, PLN = str[0], '', str[1]
			elif ui == '4':
				PFN, PMN, PLN = str[1], '', str[0]
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				for name in str:
					i = i + 1
					print('{:2}) {:20}'.format(i, name))
				print
				f = uInput('Select First Name > ')
				print
				l = uInput('Select Last Name > ')
				print
				try:
					m = uInput('Select Middle Name/Initial ([ENTER] if none)...')
				except:
					m = 0
				if m == '':
					m = 0
				i = 0
				for name in str:
					i = i + 1
					if i == int(f):
						PFN = name
					elif i == int(l):
						PLN = name
					elif i == int(m):
						PMN = name
				print(PFN, PMN, PLN)
		else:
			PFN, PMN, PLN = str[0],str[1],str[2]
		PERSON = '{0} {1}'.format(PFN, PLN)

	if return_dict:
		dAcc['NAME'] = PERSON
		dAcc['NF'] = PFN
		dAcc['NM'] = PMN
		dAcc['NL'] = PLN
		dAcc['NFI'] = dAcc['NF'][:1]
		return dAcc
	else:
		return PERSON, PFN, PMN, PLN

# Propercase Person or Entity
def propercase(name, confirm = True):

	# Check to see if name is already proper case
	for i in range(97, 122):
		if chr(i) in name:
			for i in range(65, 90):
				if chr(i) in name:
					return name
	name = name.upper()
	print(name)
	# make exception lists
	threeLetterTitleList = ['AIR', 'ANN', 'AVE', 'BAY', 'BIG', 'CIR', 'CO', 'DEV', 'DR', 'ELM', 'FWY', 'GEN', 'HOF', 'HWY',  'INC', 'JR', 'LAS', 'LIV', 'LN', 'LTD', 'LOT', 'MTN', 'NEW', 'NY', 'OAK', 'OLD', 'ONE', 'PHX', 'PL', 'REV', 'ROY', 'RD', 'RD,', 'RIM', 'RIO', 'RON', 'SAN', 'SKY', 'SON', 'SR', 'ST', 'STE', 'SUN', 'TAN', 'TEN', 'THE', 'TOM', 'TOP', 'TR', 'TWO', 'VAN', 'WAY']
	threeLetterCapsList = ['AZ', 'BOX', 'FBO', 'IH', 'IRA', 'JEN', 'IMH', 'PO', 'RE', 'USA', 'II', 'III', 'IV', 'VI', 'VII', 'IX', 'XI', 'XII', 'XIII', 'XIV', 'XVI', 'XIX', 'NE', 'SE']
	threeLetterLowerList = ['AN', 'AND', 'OF', 'OF,', 'LAW', '1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH']
	fourLetterCapsList = ['XIII', 'XVII', 'VIII', 'GCHI', 'NSHE', 'REIT']
	fourLetterLowerList = ['11TH', '12TH', '13TH']
	fourLetterTitleList = ['BLVD', 'PTNR']
	numberLowerList = ['1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH']

	print('-' * 50)
	print('\n Title Casing Name\n')
	print(' Upper :   {0}'.format(name))

	# Strip commas and periods
	name = name.replace(',', '').replace('.', '')

	# Key no vowel combinations uppercase
	splitName = name.split()
	fixedName = ''
	for sn in splitName:
		if len(sn) == 1:
			fixedName = '{0} {1}'.format(fixedName, sn)
			continue

		found = False
		if len(sn) <= 3:
			for n3 in threeLetterTitleList:
				if sn == n3:
					fixedName = '{0} {1}'.format(fixedName, sn.title())
					found = True
			if found:
				continue
			for n3 in threeLetterCapsList:
				if sn == n3:
					fixedName = '{0} {1}'.format(fixedName, sn)
					found = True
			if found:
				continue
			for n3 in threeLetterLowerList:
				if sn == n3:
					fixedName = '{0} {1}'.format(fixedName, sn.lower())
					found = True
			if found:
				continue

		if len(sn) == 4:
			for n4 in fourLetterCapsList:
				if sn == n4:
					fixedName = '{0} {1}'.format(fixedName, sn)
					found = True
			if found:
				continue
			for n4 in fourLetterLowerList:
				if sn == n4:
					fixedName = '{0} {1}'.format(fixedName, sn.lower())
					found = True
			if found:
				continue
			for n4 in fourLetterTitleList:
				if sn == n4:
					fixedName = '{0} {1}'.format(fixedName, sn.title())
					found = True
			if found:
				continue

		if 'A' in sn or 'E' in sn or 'I' in sn or 'O' in sn or 'U' in sn or 'Y' in sn:
			if len(sn) <= 3:
				# ui = uInput('\n-- > {0}\n\n1) All Caps\n2) All Lower\n3) Title case\n\nSelect > '.format(sn))
				print('\n -- > Choose format\n\n1) {0}   [Title Case]\n2) {1}   [Lower Case]\n3) {2}   [All Caps]\n\n'.format(sn.title(), sn.lower(), sn.upper()))
				ui = uInput(' Select > ')
				if ui == '1':
					fixedName = '{0} {1}'.format(fixedName, sn.title())
				elif ui == '2':
					fixedName = '{0} {1}'.format(fixedName, sn.lower())
				elif ui == '3':
					fixedName = '{0} {1}'.format(fixedName, sn.upper())
			else:
				fixedName = '{0} {1}'.format(fixedName, sn.title())
		else:
			for n3 in numberLowerList:
				if n3 in sn:
					fixedName = '{0} {1}'.format(fixedName, sn.lower())
					found = True
			if found:
				continue

			fixedName = '{0} {1}'.format(fixedName, sn)

	fixedName = fixedName.strip()

	print('\n Fixed :   {0}'.format(fixedName))
	print

	if confirm:
		print('  1) Yes')
		print('  2) No')
		print('  3) All Caps')
		print(' 00) Quit program')
		print(' ...or type name manually...')
		ui = uInput('\n Select or Type > ')

		while 1:
			if ui == '00':
				exit('\n Terminating program...')
			elif ui == '1':
				return fixedName
			elif ui.upper() == 'C' or ui == '2':
				return name
			elif ui == '3':
				return name
			elif ui == '4':
				exit('\n Terminating program...')
			elif len(ui) > 2:
				return ui
			else:
				warningMsg('\nInvalid input...try again...')
				ui = uInput('\n Select or Type > ')
	else:
		return  fixedName

################################################################################
#                            DATE FUNCTIONS 
################################################################################

# Format date types TF, slash, dash, 6 characters, 8 characters
def date_engine(date, outformat='TF', informat='unknown'):
	if informat == 'unknown':
		if '12:00:00' in date and '/' in date:
			informat = 'CoStar'
		elif '/' in date:
			informat = 'slash'
		elif '-' in date:
			if len(date) == 10 and (date[:2] == '19' or date[:2] == '20'):
				informat = 'TF'
			else:
				informat = 'dash'
		elif len(date) == 6:
			if date[-4:-2] == '20' or date[-4:-2] == '19':
				informat = 'monthyear'
			else:
				informat = 'six'
		elif len(date) == 8:
			informat = 'eight'
		elif date == '' or date == 'today':
			informat = 'today'
		elif len(date) == 13:
			informat = 'milliseconds'

	if informat == 'slash':
		lDate = date.split('/')
	elif informat == 'dash':
		lDate = date.split('-')
	elif informat == 'CoStar':
		date = date.replace(' 12:00:00 AM', '')
		lDate = date.split('/')
	elif informat == 'TF' and outformat == 'opr':
		# Parse the input date string
		date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
		# Format the date into the desired format
		formatted_date = date_obj.strftime("%b %d, %Y").upper()
		return formatted_date
	elif informat == 'datetime' and outformat == 'ddmmyyyy':
		if date == None:
			return ''
		else:
			formatted_date = date.strftime("%m/%d/%Y")
			return formatted_date
	elif informat == 'TF':
		if date == 'None':
			return 'None'
		lDateTF = date.split('-')
		lDate = [lDateTF[1], lDateTF[2], lDateTF[0]]
		
	elif informat == 'monthyear':
		lDate = [date[:2], '01', date[4:]]
	elif informat == 'six' or informat == 'eight':
		lDate = [date[:2], date[2:4], date[4:]]
	elif informat == 'iso':
		date_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
		return date_obj.strftime('%m/%d/%Y')
	elif informat == 'today':
		from datetime import date
		today = date.today()
		if outformat == 'TF':
			return today.strftime('%Y-%m-%d')
		elif outformat == 'slash':
			return today.strftime('%m/%d/%Y')
		elif outformat == 'dash':
			return today.strftime('%m-%d-%Y')
		elif outformat == 'unknown':
			return today.strftime('%m-%d-%Y')
	elif informat == 'milliseconds':
		try:
			timestamp_ms = int(date)
			timestamp_seconds = timestamp_ms / 1000
			return datetime.datetime.fromtimestamp(timestamp_seconds).date()
		except (ValueError, TypeError):
			return None
	else:
		print('Unknown format')
		return 'error unknown format'

	# Assign to variables to make it easier to read
	# year = int(lDate[2])
	# month = int(lDate[0])
	# day = int(lDate[1])

	year = lDate[2]
	month = lDate[0]
	day = lDate[1]

	# Add leading zeros to month and day if needed
	if len(month) == 1:
		month = '0{0}'.format(month)
	if len(day) == 1:
		day = '0{0}'.format(day)
	if len(year) == 2:
		year = '20{0}'.format(year)

	if outformat == 'TF':
		# YYYY-MM-DD
		date = '{0}-{1}-{2}'.format(year, month, day)
	elif outformat == 'slash':
		# YYYY/MM/DD
		date = '{0}/{1}/{2}'.format(month, day, year)
	elif outformat == 'dash':
		# MM-DD-YYYY
		date = '{0}-{1}-{2}'.format(month, day, year)
	elif outformat == 'opr':
		date = date.strftime('%b %d, %Y').upper()
	elif outformat == 'tf_query':
		date = datetime.datetime(int(year),int( month), int(day))
		date = date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
	elif outformat == 'datetime.datetime':
		date = datetime.datetime(int(year), int(month), int(day))

	return date

# Today's date in 'TF' (YYY-MM-DD), 'slash' (MM/DD/YYY) or 'ArcMap' (YYYY_MM_DD) formats
def today_date(dateformat='TF', include_time=False):
	from datetime import date
	# Get date
	d = date.today().isoformat()
	if dateformat == 'TF':  # YYYY-MM-DD
		pass
	elif dateformat == 'slash':  # MM/DD/YYYY
		d = d.split('-')
		d = '{0}/{1}/{2}'.format(d[1], d[2], d[0])
	elif dateformat == 'ArcMap':  # YYYY_MM_DD
		d = d.split('-')
		d = '{0}_{1}_{2}'.format(d[0], d[1], d[2])
	elif dateformat == 'datetime':
		d = date.today()
	# Get time
	if include_time:
		from datetime import datetime
		now = datetime.now()
		t = now.strftime("%H:%M:%S")
		return d, t
	else:
		return d

# Return date difference from today's date by days, weeks, months or years
def less_time_ago(unit_type, n, use_isoformat=True):
	from datetime import date
	from datetime import timedelta

	if use_isoformat:
		if unit_type == 'DAY':
			return (date.today() - timedelta(n)).isoformat()
		elif unit_type == 'WEEK':
			return (date.today() - timedelta(7 * n)).isoformat()
		elif unit_type == 'MONTH':
			return (date.today() - timedelta(31 * n)).isoformat()
		elif unit_type == 'YEAR':
			return (date.today() - timedelta(365.25 * n)).isoformat()
	else:
		if unit_type == 'DAY':
			return (date.today() - timedelta(n))
		elif unit_type == 'WEEK':
			return (date.today() - timedelta(7 * n))
		elif unit_type == 'MONTH':
			return (date.today() - timedelta(31 * n))
		elif unit_type == 'YEAR':
			return (date.today() - timedelta(365.25 * n))

# Add 4 weeks to a date
def weeks_difference(strDate='None', no_weeks='None', is_start='None'):
	from datetime import datetime, timedelta

	while 1:
		if strDate == 'None':
			strDate = uInput('Enter a start or end date (MMDDYY): ')
		# Extract month, day, and year from the input string
		month = int(strDate[:2])
		day = int(strDate[2:4])
		year = 2000 + int(strDate[4:6])  # Assuming 21st century dates (00-99)
		
		if no_weeks == 'None':
			print(f'\n Date: {month}/{day}/{year}')
			no_weeks = uInput('\n Enter number of weeks to select > ')
			no_weeks = int(no_weeks)
		# Ask user if this is the start date or end date
		# print(f'\n Date: {month}/{day}/{year}')
		if is_start is True:
			ui = '1'
		elif is_start is False:
			ui = '2'
		else:
			print('\n Is this the start date or end date?')
			print('\n  1) Start Date')
			print('  2) End Date')
			print(' 00) Quit')
			ui = uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			start_date_str = strDate
			# Create a datetime object from the extracted values
			start_date = datetime(year, month, day)
			end_date = start_date + timedelta(weeks=no_weeks)
			# Format the end date back to the MMDDYY string format
			end_date_str = end_date.strftime('%m%d%y')
			break
		elif ui == '2':
			end_date_str = strDate
			# Create a datetime object from the extracted values
			end_date = datetime(year, month, day)
			start_date = end_date - timedelta(weeks=no_weeks)
			# Format the start date back to the MMDDYY string format
			start_date_str = start_date.strftime('%m%d%y')
			break
		else:
			warningMsg('\n Invalid input, try again...\n')
			strDate
			lao.sleep(1)

	return start_date_str, end_date_str

# Function to convert a date string to a datetime object
def convert_to_datetime(strDate):
	try:
		if '/' in strDate:
			lDate = strDate.split('/')
		elif '-' in strDate:
			lDate = strDate.split('-')
	except TypeError:
		return datetime.datetime.fromisoformat(strDate)
	# Check if the year is the first value or the third value
	if len(lDate[0]) == 4:
		year = int(lDate[0])
		month = int(lDate[1])
		day = int(lDate[2])
	else:
		year = int(lDate[2])
		month = int(lDate[0])
		day = int(lDate[1])
	return datetime.datetime(year, month, day)

# Returns current or last quarter date
def getDateQuarter(lastquarter=True, two_qrts_ago=False):
	from datetime import date
	d = date.today().isoformat()
	d = d.split('-')
	year = d[0]
	month = int(d[1])
	if month >= 1 and month <= 3:
		quarter = 1
	elif month >= 4 and month <= 6:
		quarter = 2
	elif month >= 7 and month <= 9:
		quarter = 3
	elif month >= 10 and month <= 12:
		quarter = 4
	if lastquarter:
		quarter -= 1
		if quarter == 0:
			year = int(year) - 1
			quarter = 4
	if two_qrts_ago:
		quarter -= 2
		if quarter == 0:
			year = int(year) - 1
			quarter = 4
		elif quarter == -1:
			year = int(year) - 1
			quarter = 3
	yearquarter = '{0}Q{1}'.format(year, quarter)
	return yearquarter

# Difference in days bewteen two dates:
def days_diff_from_today(date):
	today_date = datetime.date.today()
	date_format = "%Y-%m-%d"
	today_date = datetime.strptime(today_date, date_format)
	date = datetime.strptime(date, date_format)
	# date = convert_to_datetime(date)
	delta = date - today_date
	return abs(delta.days)

# Convert datetime format to d/m/y
def convert_datetime_to_readable(date_obj, separator='/'):
	# Check if strDate is type datetime
	if not isinstance(date_obj, datetime.datetime):
		date_obj = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')
	# 	if separator == '/':
	# 		formatted_date = strDate.strftime('%d/%m/%Y')
	# 	elif separator == '-':
	# 		formatted_date = strDate.strftime('%Y-%m-%d')
	# 	elif separator == '_':
	# 		formatted_date = date_obj.strftime('%d_%m_%Y')
	# else:
	# 	# Parse the input date string
	# 	date_obj = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')
		# Format the date object to the desired format
	if separator == '/':
		formatted_date = date_obj.strftime('%d/%m/%Y')
	elif separator == '-':
		formatted_date = date_obj.strftime('%Y-%m-%d')
	elif separator == '_':
		formatted_date = date_obj.strftime('%d_%m_%Y')
	return formatted_date

# Convert date string to datetime object
def make_tf_date():
	while 1:
		print('\n Date format Month Day Year no punctuation (013113 = Jan. 31, 2013)')
		DTE = uInput('\n Enter Date: > ')
		if '/' in DTE:
			warningMsg('\n Invalid Date format, try again...\n')
		elif len(DTE) == 6:
			DTE = '20{0}-{1}-{2}'.format(DTE[4:], DTE[:2], DTE[2:4])
			# DTE = DTE[:2] + '/' + DTE[2:4] + '/20' + DTE[4:]
			break
		elif len(DTE) == 8:
			DTE = '{0}-{1}-{2}'.format(DTE[4:], DTE[2:4], DTE[:2])
			# DTE = DTE[:2] + '/' + DTE[2:4] + '/' + DTE[4:]
			break
		else:
			warningMsg('\n Invalid Date format, try again...\n')
	return DTE

# Extract date from file name
def get_date_from_filename(filename):
	# Extract YYYY-MM from filename like "RLB Permits 2024-12 KEY CLEANED.csv"
	import re
	from datetime import datetime
	from calendar import monthrange
	
	# Find YYYY-MM pattern in filename
	date_pattern = r'(\d{4})-(\d{2})'
	match = re.search(date_pattern, filename)
	
	if match:
		year = int(match.group(1))
		month = int(match.group(2))
		
		# Get the last day of the month
		_, last_day = monthrange(year, month)
		
		# Create datetime object for last day of month
		file_date = datetime(year, month, last_day)
		return file_date
	else:
		raise ValueError(f"Could not extract date from filename: {filename}")

# Get the year to date start date i.e. January 1st of the current year in datetime format
def get_ytd_start():
	"""
	Returns January 1st of the current year based on today's date
	
	Returns:
		datetime: January 1st of the current year
	"""
	from datetime import datetime
	today = datetime.today()
	return datetime(today.year, 1, 1)

# Check if a date is within the last six months and return a specific OPR Send date if it is
def send_opr(date):
	"""
	Takes a date in format YYYY-MM-DD and returns '1965-01-11' if the date
	is within the last six months, otherwise returns 'None'.
	
	Args:
		date (str): Date string in format YYYY-MM-DD (e.g., '2025-07-01')
	
	Returns:
		str: '1965-01-11' if date is within last 6 months, otherwise 'None'
	"""
	try:
		# Parse the input date
		input_date = datetime.datetime.strptime(date, '%Y-%m-%d')
		
		# Get current date
		current_date = datetime.datetime.now()
		
		# Calculate date 6 months ago
		six_months_ago = current_date - datetime.timedelta(days=180)  # Approximating 6 months as 180 days
		
		# Check if input date is within the last 6 months
		if input_date >= six_months_ago and input_date <= current_date:
			return '1965-01-11'
		else:
			return 'None'
			
	except ValueError:
		# Return 'None' if date format is invalid
		return 'None'

def get_last_day_of_previous_month():
	"""
	Returns the last day of the previous month based on today's date
	
	Returns:
		datetime: Last day of previous month at 11:59:59 PM
	"""
	from datetime import datetime, timedelta
	
	# Get first day of current month
	today = datetime.today()
	first_day_current = datetime(today.year, today.month, 1)
	
	# Subtract one day to get last day of previous month
	last_day_previous = first_day_current - timedelta(days=1)
	
	# Set time to end of day
	last_day_previous = datetime(
		last_day_previous.year,
		last_day_previous.month,
		last_day_previous.day,
		23, 59, 59
	)
	
	return last_day_previous