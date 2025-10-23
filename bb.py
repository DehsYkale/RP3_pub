#! python3

# SalesForce (formally BeatBox) based functions

import base64
from collections import OrderedDict
from datetime import datetime
import dicts
import fun_login
import fun_text_date as td
import lao
import os
import pickle
from pprint import pprint
from re import sub as resub
from sys import exit
from webbrowser import open as openbrowser
import webs

# Check Account Type
def chooseAccountCategory(service, AID='None'):

	while 1:
		if AID != 'None':
			# TerraForce Query
			fields = 'default'
			wc = "Id = '{0}'".format(AID)
			results = tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
			CAT = results[0]['Category__c']
			
			NAM = (results[0]['Name']).upper()
			print(' {0}'.format(NAM))
			if 'Agent Land' in CAT:
				return 'BROKERAGE'
			elif 'Buyer Agricultural' in CAT:
				return 'AGRICULTURAL'
			elif 'Buyer Commercial' in CAT:
				return 'COMMERCIAL'
			elif 'Buyer Homebuilder' in CAT:
				return 'HOMEBUILDER'
			elif 'Buyer Hotel' in CAT:
				return 'HOTEL'
			elif 'Buyer Industrial' in CAT:
				return 'INDUSTRIAL'
			elif 'Buyer Multifamily' in CAT:
				return 'MULTIFAMILY'
			elif 'Buyer Office' in CAT:
				return 'OFFICE'
			elif 'Buyer Other' in CAT:
				return 'OTHER'
			elif 'Buyer Non-Profit' in CAT:
				return 'NON-PROFIT'
			elif 'Buyer Retail' in CAT:
				return 'RETAIL'
			elif 'Developer' in CAT:
				return 'DEVELOPER'
			elif 'Government' in CAT:
				return 'GOVERNMENT'
			elif 'Land Banker' in CAT:
				return 'LAND BANKER'
			elif 'Lot Investor' in CAT:
				return 'LOT INVESTOR'
			elif 'Investor' in CAT:
				return 'INVESTOR'
			elif 'Medical' in CAT:
				return 'MEDICAL'
			elif 'Schools' in CAT:
				return 'SCHOOLS'
			elif 'Utility' in CAT:
				return 'UTILITY'
			elif 'Commercial Banking' in CAT:
				return 'FINANCIAL'
			elif 'Consultant Engineering' in CAT:
				return 'ENGINEERING'
			elif 'TRUST' in NAM:
				return 'INVESTOR'
			elif ' FARM ' in NAM:
				return 'AGRICULTURAL'
			elif ' FARMS' in NAM:
				return 'AGRICULTURAL'
			elif 'INVESTMENT' in NAM:
				return 'INVESTOR'
			elif 'DEVELOPMENT' in NAM:
				return 'DEVELOPER'
			elif 'ENGINEERING' in NAM:
				return 'ENGINEERING'

		menu =' Choose an Entity/Business Category:\n\n' \
			  '  1) Agricultural\n' \
			  '  2) Architect\n' \
			  '  3) Brokerage\n' \
			  '  4) Commercial\n' \
			  '  5) Developer\n' \
			  '  6) Engineering\n' \
			  '  7) Financial/Banking\n' \
			  '  8) Government\n' \
			  '  9) Homebuilder\n' \
			  ' 10) Hotel\n' \
			  ' 11) Industrial\n' \
			  ' 12) Investor\n' \
			  ' 13) Land Banker\n' \
			  ' 14) Lot Investor\n' \
			  ' 15) Medical\n' \
			  ' 16) Multifamily\n' \
			  ' 17) Non-Profit\n' \
			  ' 18) Office\n' \
			  ' 19) Other\n' \
			  ' 20) Retail\n' \
			  ' 21) Schools\n' \
			  ' 22) Utility\n'
		td.colorText(menu, 'GREEN')

		while 1:
			ui = td.uInput('\n Enter selection > ')
			if ui == '1':
				uiCAT = 'Buyer Agricultural'

			elif ui == '2':
				uiCAT = 'Consultant Architect Land Planning'

			elif ui == '3':
				uiCAT = 'Agent Land'

			elif ui == '4':
				uiCAT = 'Buyer Commercial'

			elif ui == '5':
				uiCAT = 'Developer'

			elif ui == '6':
				uiCAT = 'Consultant Engineering'

			elif ui == '7':
				uiCAT = 'Commercial Banking'

			elif ui == '8':
				uiCAT = 'Government'

			elif ui == '9':
				uiCAT = 'Buyer Homebuilder'

			elif ui == '10':
				uiCAT = 'Buyer Hotel'

			elif ui == '11':
				uiCAT = 'Buyer Industrial'

			elif ui == '12':
				uiCAT = 'Investor'

			elif ui == '13':
				uiCAT = 'Lot Investor'

			elif ui == '14':
				uiCAT = 'Lot Investor'

			elif ui == '15':
				uiCAT = 'Medical'

			elif ui == '16':
				uiCAT = 'Buyer Multifamily'

			elif ui == '17':
				uiCAT = 'Buyer Non-Profit'

			elif ui == '18':
				uiCAT = 'Buyer Office'

			elif ui == '19':
				uiCAT = 'Buyer Other'

			elif ui == '20':
				uiCAT = 'Buyer Retail'

			elif ui == '21':
				uiCAT = 'Schools'

			elif ui == '22':
				uiCAT = 'Utility'
			
			elif ui == '23':
				uiCAT = 'Church'

			else:
				print('Invalid input try agina...\n')

		# Catch old habbits

			td.warningMsg('\n You selected Category {0}.'.format(uiCAT.upper()))
			ui = td.uInput('\n Is this correct? [0/1] > ')
			if ui == '0' or ui == '':
				'\n Try again...'
			else:
				break

		if AID != 'None':
			if CAT == 'None':
				CAT = uiCAT
			else:
				CAT = f'{CAT};{uiCAT}'
			od = {'type': 'Account', 'Id': AID, 'Category__c': uiCAT}
			upresults = tf_update_3(service, od)
		else:
			return uiCAT

# Determine if variable is a DID or a PID
def isDIDorPID(didpid):
	lStateAbb = lao.getCounties('StateAbb')
	for state in lStateAbb:
		if state == didpid[:2]:
			return 'PID'
	return 'DID'

# Check if LAO Deal Closed or Escrow
def is_LAO_Deal(service, didpid):
	tfIdType = isDIDorPID(didpid)
	# fields = 'Id, PID__c, StageName__c'
	if tfIdType == 'DID':
		wc = "Id = '{0}'".format(didpid)
	else:
		wc = "PID__c = '{0}'".format(didpid)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
	# TerraForce Query
	fields = 'default'
	# wc = "s{1}".format(fields, wc)"
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	if results == []:
		td.warningMsg(' is_LAO_Deal function found no TF record found for {0}'.format(didpid))
		lao.holdup()
		return False, 'No TF Record'
	if results[0]['StageName__c'] == 'Closed' or results[0]['StageName__c'] == 'Escrow':
		return True, results[0]['StageName__c'] 
	else:
		return False, results[0]['StageName__c'] 

# Given a PID return Record ID (DID)
def getDIDfromPID(service, pid, openinbrowser=False, warning_pause=True):
	# qs = "SELECT Id FROM lda_Opportunity__c WHERE PID__c = '{0}'".format(pid)
	# TerraForce Query
	fields = 'default'
	wc = "PID__c = '{0}'".format(pid)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	try:
		DID = results[0]['Id']
	except IndexError:
		td.warningMsg('\n PID {0} does not exist in TF.'.format(pid))
		# print(' (bb.getDIDfromPID function)')
		ui = td.uInput('\n Continue... > ')
		return 'No PID Exists'
	if openinbrowser:
		openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))
	return DID

# Given a PID return Record ID (DID)
def getPIDfromDID(service, DID):
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# qs = "SELECT PID__c FROM lda_Opportunity__c WHERE Id = '{0}'".format(DID)
	return results[0]['PID__c']

# Search for existing Business/Entity Account in TF and create one if it does not exist
# Returns NAME, AID, RTY
def findCreateAccountEntity(service, NAME = 'None', CITY = 'None', STATE = 'None', URL = 'None', STREET = 'None', ZIPCODE = 'None', PHONE = 'None', CATEGROY = 'None'):
	while 1:
		# have user enter name if none given
		# uiName tracks if user input the business name
		uiName = False
		while 1:
			jump = False
			if NAME == 'None':
				NAME = (td.uInput('\n Enter Full Business or Person Name > ')).upper()
				NAME = NAME.replace("'", '')
				uiName = True

			# Check if NAME is a business/company
			if lao.coTF(NAME) is False:
				while 1:
					print('\n Is {0} a Business?\n'.format(NAME))
					print(' 1) Yes')
					print(' 2) No')
					ui = td.uInput('\n > ')
					# If NAME is not a Business/Company then return NONE
					if ui == '0' or ui == '2':
						AID, RTY = 'None', 'None'
						business_dict = {'type': 'Account', 'Name': NAME}
						return NAME, AID, RTY, business_dict
					elif ui == '1':
						NAME = NAME.upper()
						break
					else:
						td.warningMsg('\n Invalid entry...try again...\n')

			# Remove apostrophe
			NAME = NAME.split("'", 1)[0]

			print('\n Checking TerraForce for Business Account...\n')
			NAME = NAME.replace('K HOVNANIAN', 'K. HOVNANIAN')
			NAME = NAME.replace('MATTAMY HOMES', 'Mattamy Arizona, LLC')
			NAME = NAME.replace('L L C', 'LLC')
			NAMEHIGHLIGHT = '{0} : {1} : {2}'.format(NAME, CITY, STATE)
			NAMEHIGHLIGHT = NAMEHIGHLIGHT.replace(' : None', '')
			lao.highlight(NAMEHIGHLIGHT)
			NAMECLEAN = NAME.replace(',','')
			NAMESPLIT = NAMECLEAN.split(' ')

			if len(NAMESPLIT) > 2:
				# Remove 'The'
				if (NAMESPLIT[0]).upper() == 'THE':
					del NAMESPLIT[0]
					NAMEQUERY = '%{0} {1}'.format(NAMESPLIT[0], NAMESPLIT[1])
				elif NAMESPLIT[1] == '&' or NAMESPLIT[1] == 'AND':
					NAMEQUERY = '{0} {1} {2}'.format(NAMESPLIT[0], NAMESPLIT[1], NAMESPLIT[2])
				elif (NAMESPLIT[0].upper() == 'CITY' or NAMESPLIT[0].upper() == 'TOWN') and NAMESPLIT[1].upper() == 'OF':
					NAMEQUERY = '{0} {1} {2}'.format(NAMESPLIT[0], NAMESPLIT[1], NAMESPLIT[2])
				else:
					NAMEQUERY = '{0} {1}'.format(NAMESPLIT[0], NAMESPLIT[1])
			elif len(NAMESPLIT) == 2:
				NAMEQUERY = '{0} {1}'.format(NAMESPLIT[0], NAMESPLIT[1])
			else:
				NAMEQUERY = NAMESPLIT[0]
			# qs = "SELECT Id, Name, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone, Category__c  FROM Account WHERE IsPersonAccount != TRUE AND Name LIKE '{0}%'".format(NAMEQUERY)


			secondQueryTry = False
			while 1:
				# qs = "SELECT Id, Name, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone, Category__c  FROM Account WHERE IsPersonAccount != TRUE AND Name LIKE '{0}%'".format(NAMEQUERY)
				# TerraForce Query
				fields = 'default'
				wc = "IsPersonAccount != TRUE AND Name LIKE '{0}%'".format(NAMEQUERY)
				results = tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

				if results == [] and len(NAMESPLIT) >= 2:
					if secondQueryTry:
						break
					if len(NAMESPLIT[0]) > 1:
						NAMEQUERY = '{0} '.format(NAMESPLIT[0]) # Add space to prevent partial word hits
						secondQueryTry = True
					else:
						break
				else:
					break

			business_dict = results

			# Print select from existing records menu
			if results != []:
				i = 0
				print('\n [0 ]  No Match')
				for row in results:
					# Include State if not None
					if STATE == row['BillingState']:
						stateMatchName = 'XX {0}'.format(row['Name'])
					else:
						stateMatchName = row['Name']
					n = str(i+1)
					if 'XX ' in stateMatchName:
						td.instrMsg(' [%-2s]  %-40s  %-25s %s'%(n,stateMatchName,row['BillingCity'],row['BillingState']))
					else:
						print(' [%-2s]  %-40s  %-25s %s'%(n,stateMatchName,row['BillingCity'],row['BillingState']))
					i=i+1
				while 1:
					try:
						user_input = int(td.uInput('\n Select entity or 0 for no match or 9999 to add City to Entity Name... > '))
					except (SyntaxError, ValueError):
						td.warningMsg('\n Entry must be a number, try again...\n')
						continue
					break
			else:
				print('\n No matching Business Account in TerraForce...\n')
				print(f' [Enter] to use {NAME}')
				print(f'      1] to type DIFFERENT Business Name')
				print(f'     00] Quit')
				ui = td.uInput('\n Select > '.format(NAME))
				if ui == 'Q' or ui == '00':
					exit(' Terminating program...')
				elif ui == '1':
					NAME = (td.uInput('\n Enter full Business Name > ')).upper()
					NAME = NAME.replace("'", '')
					continue
				elif len(ui) > 2:
					NAME = ui.upper()
					continue
				else:
					user_input = 0
					jump = True

			# add City to NAME
			if user_input == 9999:
				if CITY == 'None':
					print('\n No City listed with Entity...\n')
					user_input = 0
				else:
					NAME = '{0} - {1}'.format(NAME, CITY)
					continue

			# add business to Accounts if non-existant
			if user_input == 0:
				# open URL if provided
				if URL != 'None':
					openbrowser(URL)
					# lao.click(1475,575)
				# if user did not input the Business name (uiName = False)
				# then ask user if they want to modify the business name
				if jump is False:
					# ui = (td.uInput('\n Type DIFFERENT Business Name, [00] Quit or [Enter] to use {0}.\n > '.format(NAME)))
					print(f' [Enter] to use {NAME}')
					print(f'      1] to type DIFFERENT Business Name')
					print(f'     00] Quit')
					ui = td.uInput('\n Select > '.format(NAME))
					if ui == 'Q' or ui == '00':
						exit(' Terminating program...')
					elif ui == '1':
						NAME = (td.uInput('\n Enter full Business Name > ')).upper()
						NAME = NAME.replace("'", '')
						continue
					elif len(ui) > 2:
						NAME = ui.upper()
						continue
					# if ui != '':
					# 	NAME = ui.upper()
					# 	continue

				# User to enter address
				if STREET == 'None':
					STREET = (td.uInput('\n Type in Street, [Enter] for no address > '))
					STREET = td.titlecase_street(STREET)
				if STREET == 'So':
					NAME = None
					continue
				elif STREET != '':
					if ZIPCODE == 'None':
						while 1:
							ZIP = td.uInput('\n Enter Zip Code > ')
							ZIP = ZIP.strip()
							if len(ZIP) > 6:
								ZIP = ZIP[:5]
								break
							else:
								break
						CTY, STT, USA = lao.zipCodeFindCityStateCountry(ZIP)
					else:
						CTY, STT, ZIP = CITY, STATE, ZIPCODE
					print('\n\n {0}\n {1}, {2} {3}\n'.format(STREET, CTY, STT, ZIP))
				else:
					CTY, STT, ZIP = '', '', ''

				# User to enter Phone
				if PHONE == 'None':
					while 1:
						print('\n [Enter] for no phone number')
						print('      1] to type phone number (any format)')
						print('      2] to Google name')
						print('     00] Quit')
						ui = td.uInput('\n Select > ')
						if ui == '1':
							PHONE = td.uInput('\n Enter Phone Number > ')
							break
						if ui == '2':
							if STATE != 'None':
								openbrowser('https://www.google.com.tr/search?q={0}+{1}'.format(NAME, STATE))
							else:
								openbrowser('https://www.google.com.tr/search?q={0}'.format(NAME))
						elif len(ui) >= 10:
							PHONE = td.phoneFormat(ui)
							break
						elif ui == '00':
							exit(' Terminating program...')
						elif ui == '':
							break
						elif len(ui) < 10 and ui != '':
							td.warningMsg('\n Invalid input...try again...\n')
						else:
							td.warningMsg('\n Invalid input...try again...\n')

				# User to enter Category
				if CATEGROY == 'None':
					uiCAT = chooseAccountCategory(service)
				else:
					uiCAT = CATEGROY

				# Proper case the name
				if NAME != None:
					NAME = lao.propercase(NAME)

				business_dict = {'type': 'Account', 'Name': NAME, 'BillingStreet': STREET, 'BillingCity': CTY, 'BillingState': STT, 'BillingPostalCode': ZIP, 'Phone': PHONE, 'Category__c': uiCAT}
				try:
					AID = tf_create_3(service, business_dict)
					# AID = create_results[0]['id']
				except:
					td.warningMsg('\n Could not create record, blocked by TF anti-dup program...\n\n Enter record manually...opening TF...\n')
					openbrowser('https://landadvisors.my.salesforce.com/setup/ui/recordtypeselect.jsp?ent=Account&retURL=%2Fa0L%2Fo&save_new_url=%2F001%2Fe%3FretURL%3D%252Fa0L%252Fo')
					print(' {0}\n {1}\n {2}\n {3}\n {4}\n'.format(NAME, STREET, CTY, STT, ZIP, PHONE))
					AID = td.uInput(' Enter Account ID > ')
			else:
				user_input = user_input-1
				try:
					NAME = results[user_input]['Name']
				except IndexError:
					td.warningMsg('\n Invalid selection...try again...')
					continue
				AID = results[user_input]['Id']
				business_dict = results[user_input]
			break

		RTY = 'Business Account'

		return NAME, AID, RTY, business_dict

# Search for existing Person Account in TF and create one if it does not exist
def findCreateAccountPerson(service, NAME = 'None', CITY = 'None', STATE = 'None', URL = 'None', STREET = 'None', ZIPCODE = 'None', PHONE = 'None', EMAIL = 'None', EID = 'None', MOBILE = 'None',  AGENT = 'None', COMPANY = 'None', CCID= 'None', FASTMODE=False, stateOfOrigin='None'):
	user = lao.getUserName()
	# have user enter name if none given
	if NAME == 'None':
		# No Person with Unknown Entity
		if 'UNKNOWN' in COMPANY.upper():
			return 'None', 'None', 'None'

		NAME = (td.uInput('\n Enter full Person Name or [Enter] to skip > ')).upper()
		if NAME == '':
			return 'None', 'None', 'None'

	while 1:
		HIGHLIGHTNAME = '{0}  :  {1}  :  {2}  :  {3}'.format(NAME, COMPANY, CITY, STATE)
		lao.highlight(HIGHLIGHTNAME)
		if FASTMODE:
			break
		else:
			ui = (td.uInput(' Type a different Name, [00] Quit or [Enter] to use this one > ')).upper()
			if ui == '':
				break
			elif ui == 'Q' or ui == '00':
				exit('Terminating program...')
			elif len(ui) < 2:
				td.warningMsg('\n Invalid input...try agaiin...')
			else:
				NAME = ui
	if FASTMODE:
		lNAME = NAME.split(' ')
		lenName = len(lNAME)
		if lenName > 2:
			if lenName == 3 and 'VAN' == lNAME[1] or 'Van' == lNAME[1]:
				NL = '{0} {1}'.format(lNAME[1], lNAME[2])
			else:
				NL = lNAME[lenName-1]
			NF = lNAME[0]
		else:
			NF, NL = NAME.split(' ')
		NFI = NF[:1]
		NM = ''
	else:
		NAME, NF, NM, NL = td.parse_person(NAME)
		NFI = NF[:1]
	NL = NL.replace("'", "")

	# check if Person exits in TF
	if user == 'none':
		import accounts
		ui = accounts.listPersons(service, NF, NL, COMPANY, stateOfOrigin)
	else:
		# qs = "SELECT FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState, Id, Category__c, Company__c, Company__r.Name, Name, CreatedById, Description, PersonEmail, Phone, PersonHasOptedOutOfEmail, PersonContactId FROM Account WHERE LastName = '" + NL + "' AND "

		wc = "LastName = '" + NL + "' AND ".format(NL)

		matchPotential = True
		matchDefinate = False

		# check for name variations and add to query
		if 'WILL' in NF.upper() or 'BILL' in NF.upper():
			addToQS = "(FirstName LIKE 'Will%' or FirstName LIKE 'Bill%')"
		elif 'JIM' in NF.upper() or 'JAMES' in NF.upper():
			addToQS = "(FirstName LIKE 'Jim%' or FirstName LIKE 'James%')"
		elif 'MIKE' in NF.upper() or 'MICHAEL' in NF.upper():
			addToQS = "(FirstName LIKE 'Mike%' or FirstName LIKE 'Michael%')"
		elif 'TOM' in NF.upper() or 'THOMAS' in NF.upper():
			addToQS = "(FirstName LIKE 'Tom%' or FirstName LIKE 'Thomas%')"
		elif 'ROB' in NF.upper() or 'BOB' in NF.upper():
			addToQS = "(FirstName LIKE 'Rob%' or FirstName LIKE 'Bob%')"
		elif 'STEW' in NF.upper() or 'STUA' in NF.upper():
			addToQS = "(FirstName LIKE 'Stew%' or FirstName LIKE 'Stua%')"
		elif 'SEAN' in NF.upper() or 'SHAWN' in NF.upper():
			addToQS = "(FirstName LIKE 'Sean%' or FirstName LIKE 'Shawn%')"
		else:
			addToQS = "FirstName LIKE '{0}%'".format(NFI)
			matchPotential = False
		wc = '{0}{1}'.format(wc, addToQS)
		# TerraForce Query
		fields = 'default'
		results = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
		
		#list matches to choose from
		ui = 0
		if results != []:
			# Get Area Code by State dict
			dAreaCodes = lao.getAreaCodesDict()
			print('-' * 50)
			print('\n {0}'.format(NAME))
			print(' {0}'.format(STREET))
			print(' {0}, {1} {2}'.format(CITY, STATE, ZIPCODE))
			td.instrMsg('\n Select Existing TerraForce Record or 0 for No Match\n')
			print(' 0 )  No Match')
			i = 0
			autoMatchCount = 0
			for row in results:
				i += 1
				n = str(i)
				# Get Company for list if exists
				company = ''
				if row['Company__r'] != '':
					# Handle both dictionary and string cases for Company__r
					if row['Company__r'] and row['Company__r'] != '':
						if isinstance(row['Company__r'], dict):
							# Company__r contains the related object data
							company = row['Company__r']['Name']
						else:
							# Company__r contains only the ID string - use it as fallback
							company = str(row['Company__r'])
					else:
						company = ''
				# Construct Full Name for List
				fullName = '{0} {1} {2}'.format(row['FirstName'], row['MiddleName__c'], row['LastName'])
				# Check if an Exact Match
				if NF.upper() == row['FirstName'].upper():
					fullName = 'XX {0}'.format(fullName)
					matchPotential = True
					# Check if Company matches
					if company != '':
						if company.upper() == COMPANY.upper():
							matchDefinate = True
						elif len(company) > 16:
							if company[:15].upper() == COMPANY[:15].upper():
								matchDefinate = True
				elif NF[:4].upper() == row['FirstName'][:4].upper():
					fullName = '44 {0}'.format(fullName)
					matchPotential = True
				elif NF[:3].upper() == row['FirstName'][:3].upper():
					fullName = '33 {0}'.format(fullName)
					matchPotential = True
				elif NF[:2].upper() == row['FirstName'][:2].upper():
					fullName = '22 {0}'.format(fullName)
					matchPotential = True

				# Add State
				if row['BillingState'] != '':
					state = row['BillingState']
				# If no State then deduce it from Area Code
				elif row['Phone'] != '':
					areaCode = td.phoneFormat(row['Phone'], 'MailChimp')[:3]
					try:
						state = '{0}(Ph)'.format(dAreaCodes[areaCode])
					except KeyError:
						state = ''
				else:
					state = ''
				# Print the Index Number, Name, Company, City, State & Created By
				if 'XX ' in fullName:
					td.instrMsg(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
				elif '22 ' in fullName or '33 ' in fullName or '44 'in fullName:
					# lao.cyanMsg(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
					td.colorText(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']), 'CYAN')
				else:
					print(' %-2s)  %-20s  %-20s  %-20s %-6s  %s'%(n, fullName, company, row['BillingCity'],state, row['PersonEmail']))
				if (stateOfOrigin in state and 'XX ' in fullName):
					autoMatchCount += 1
					autoMatchUI = n
				if matchDefinate:
					autoMatchUI = n
					break
			while 1:
				if FASTMODE is True and matchPotential is False:
					ui = 0
					break
				elif FASTMODE is True and autoMatchCount == 1:
					ui = int(autoMatchUI)
					break
				elif FASTMODE is True and matchDefinate is True:
					ui = int(autoMatchUI)
					break
				td.instrMsg('\n Type 411 & Index number (i.e. 4111 for the 1st on the list) to open TF record for a listed Account')
				try:
					ui = int(td.uInput('\n Select person or 0 for no match... > '))
				except SyntaxError:
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

	# Return Name and ID if already in TF
	if ui > 0:
		ui -= 1
		NAME = results[ui]['FirstName'] + ' ' + results[ui]['LastName']
		AID = results[ui]['Id']
		print('\n {0} selected...'.format(NAME))
		results[ui]['ValidEmail'] = ''

		# Update blank fields
		# BillingCity, BillingState, Id, Category__c, Company__c, Company__r.Name, Name, CreatedById, Description, PersonEmail, Phone,
		update = False
		dup = {'type': 'Account', 'id': AID}

		# Add address if none
		if results[ui]['BillingStreet'] == '' and STREET != 'None':
			STREET = td.titlecase_street(STREET)
			dup['BillingStreet'] = STREET
			dup['BillingCity'] = CITY.title()
			dup['BillingState'] = STATE
			dup['BillingPostalCode'] = ZIPCODE
			update = True

		# Add Phone if none or not matching
		if results[ui]['Phone'] == '' and PHONE != 'None':
			dup['Phone'] = PHONE
			update = True

		# Add Phone if different from number already entered
		elif results[ui]['Phone'] != '' and PHONE != 'None':
			tfPhone = results[ui]['Phone']
			tfPhone = resub(r"\D", "", tfPhone)
			uiPhone = resub(r"\D", "", PHONE)
			if tfPhone != uiPhone:
				dup['PersonOtherPhone'] = PHONE

		# Add company if None
		if results[ui]['Company__c'] == '' and EID != 'None':
			dup['Company__c'] = EID
			update = True

		# Update Email
		if EMAIL != 'None':
			# Add Email to Account if blank
			if results[ui]['PersonEmail'] == '':  # Add Email to Account
				dup['PersonEmail'] = EMAIL
				update = True
			elif results[ui]['PersonEmail'].lower() != EMAIL.lower():
				uin = td.uInput('\n Update Email Address? [0/1] > ')
				if uin == '1':
					dup['PersonEmail'] = EMAIL
					update = True
		if update:
			upResults = tf_update_3(service, dup, 'Person Record')

		RTY = results[ui]
		# print(NAME, AID, RTY)
		# td.uInput('Hold 1')
		return NAME, AID, RTY

	# Add new Person to TF
	elif ui == 0:
		# get info from Entity
		if EID != 'None':
			# qs = "SELECT BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone FROM Account WHERE Id = '{0}'".format(EID)
			# TerraForce Query
			fields = 'default'
			wc = "Id = '{0}'".format(EID)
			ent_results = tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
			if ent_results[0]['BillingStreet'] != '':
				STREET = ent_results[0]['BillingStreet']
				STREET = td.titlecase_street(STREET)
				CITY = ent_results[0]['BillingCity'].title()
				STATE = ent_results[0]['BillingState']
				ZIPCODE = ent_results[0]['BillingPostalCode']
				PHONE = ent_results[0]['Phone']

		NAME = ' {0} {1}'.format(NF, NL)
		print('\n {0} is a new Person...'.format(NAME))
		if STREET == 'None':
			STREET = (td.uInput('\n Type in Street, [Enter] for no address\n > '))
			STREET = td.titlecase_street(STREET)
		if STREET != '' and ZIPCODE == 'None':
			while 1:
				ZIPCODE = td.uInput('\n Enter Zipcode Code > ')
				if ZIPCODE == '':
					td.warningMsg('\nInvalid entry...try again...\n')
					continue
				ZIPCODE = ZIPCODE.strip()
				if len(ZIPCODE) > 6:
					ZIPCODE = ZIPCODE[:5]
					break
				else:
					break
			CITY, STATE, USA = lao.zipCodeFindCityStateCountry(ZIPCODE)
			print('\n\n {0}\n {1}, {2} {3}\n'.format(STREET, CITY, STATE, ZIPCODE))
		elif STREET == '' and ZIPCODE == 'None':
			CITY, STATE, ZIPCODE = '', '', ''

		# User to enter Phone
		PHONE, MOBILE, descriptionPhone = 'None', 'None', 'None'
		if PHONE == 'Skip':
			PHONE == 'None'
		elif PHONE == 'None' or PHONE == '':
			print('\n\n {0}\n {1}\n {2}, {3} {4}'.format(NAME, STREET, CITY, STATE, ZIPCODE))
			while 1:
				ui = (td.uInput('\n\n Enter phone number (any format),\n   [1] True People Search\n   [2] Fast People Search\n   [Enter] for none...\n > ')).upper()
				if ui == '1':
					if NM == '':
						tps_name = '{0}%20{1}'.format(NF, NL)
					else:
						tps_name = '{0}%20{1}%20{2}'.format(NF, NM, NL)
					tps_url = 'https://www.truepeoplesearch.com/results?name={0}&citystatezip={1},%20{2}'.format(tps_name, CITY, STATE)
					openbrowser(tps_url)
					PHONE, MOBILE, descriptionPhone = lao.getTruePeopleSearchPhoneNumbers()
					break
				elif ui == '2':
					if NM == '':
						fps_name = '{0}-{1}'.format(NF, NL)
					else:
						fps_name = '{0}-{1}-{2}'.format(NF, NM, NL)
					fps_url = 'https://www.fastpeoplesearch.com/name/{0}_{1}-{2}'.format(fps_name, CITY, STATE)
					openbrowser(fps_url)
				elif ui != '':
					PHONE = td.phoneFormat(ui)
					break
				else:
					PHONE = 'None'
					break

		# Enter Mobile if provided
		if MOBILE != 'None':
			if '(' not in MOBILE:
				formattedPhone = td.phoneFormat(MOBILE)
				if formattedPhone != 'Skip':
					MOBILE = formattedPhone

		# User to enter Email
		if EMAIL == 'None':
			while 1:
				EMAIL = (td.uInput('\n Type Email or [Enter] for none > ')).upper()
				if EMAIL == '':
					break
				elif '@' in EMAIL:
					break
				else:
					td.warningMsg('\n Invalid email address...try again...\n')

		# Create Person Account
		print('\n Creating Person Account: {0}'.format(NAME))
		object_dict = {'type': 'Account', 'FirstName': NF, 'LastName': NL, 'BillingStreet': STREET, 'BillingCity': CITY, 'BillingState': STATE, 'BillingPostalCode': ZIPCODE}
		if PHONE != 'None' and PHONE != 'Skip':
			object_dict['Phone'] = PHONE
		if EMAIL != 'None' and EMAIL != 'Not':
			object_dict['PersonEmail'] = EMAIL
		if NM != '':
			object_dict['MiddleName__c'] = NM
		if EID != 'None':
			object_dict['Company__c'] = EID
		if MOBILE != 'None' and MOBILE != 'Skip':
			object_dict['PersonMobilePhone'] = MOBILE
		if descriptionPhone != 'None':
			object_dict['Description'] = descriptionPhone
		

		# Assemble Category List
		categoryList = ''

		if AGENT != 'None':
			for agentRow in AGENT:
				categoryList = '{0};{1}'.format(categoryList, agentRow)
			#categoryList.append(AGENT)
		if categoryList != '':
			categoryList = categoryList.replace(';', '', 1)
			print(categoryList)
			object_dict['Category__c'] = categoryList
		if CCID != 'None':
			object_dict['CC_ID__c'] = CCID
		try:
			AID = tf_create_3(service, object_dict)
			# AID = person_results[0]['id']
		except:
			print('\n Could not create record, blocked by TF anti-dup program...')
			print('\n Enter record manually...opening TF...\n')
			openbrowser('https://landadvisors.my.salesforce.com/setup/ui/recordtypeselect.jsp?ent=Account&retURL=%2Fa0L%2Fo&save_new_url=%2F001%2Fe%3FretURL%3D%252Fa0L%252Fo')
			print(' {0}\n {1}\n {2}\n {3}\n {4}\n {5}\n'.format(NAME, STREET, CITY, STATE, ZIPCODE, PHONE))
			AID = td.uInput(' Enter Account ID > ')

	RTY = 'Person Account'
	return NAME, AID, RTY

# Checks Entity for existence of Person(s) (Employees, Child Relationships and Offers) and lets user select a Person for Deal record.
def findPersonsOfEntity(service, EID = 'None', person = 'None'):
	if EID == 'None':
		# return '', 'None', 'Person Account'
		# print('', 'None', 'Person Account')
		pass
	else:
		# find employees of an Entity
		# qs = "SELECT Id, Name, FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState FROM Account WHERE Company__c = '{0}'".format(EID)

		# TerraForce Query
		fields = 'Id, Name, FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState'
		wc = "Company__c = '{0}'".format(EID)
		dEmp = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

		# Check if Entity has Child relationships and let user choose and Employee
		# qs = "Select Id, Name, (Select ChildAccount__r.Id, ChildAccount__r.FirstName, ChildAccount__r.LastName, ChildAccount__r.BillingStreet, ChildAccount__r.MiddleName__c, ChildAccount__r.Name, ChildAccount__r.BillingCity, ChildAccount__r.BillingState From AccountLinks__r) From Account a where Id = '{0}'".format(EID)

		# TerraForce Query
		fields = 'Id, Name, (Select ChildAccount__r.Id, ChildAccount__r.FirstName, ChildAccount__r.LastName, ChildAccount__r.BillingStreet, ChildAccount__r.MiddleName__c, ChildAccount__r.Name, ChildAccount__r.BillingCity, ChildAccount__r.BillingState From AccountLinks__r)'
		wc = "Id = '{0}'".format(EID)
		dChild = tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

		# Check if Entity has Deals with Persons and let user choose a Person
		# qs = "SELECT Id, AccountId__c, AccountId__r.Name, AccountId__r.FirstName, AccountId__r.MiddleName__c, AccountId__r.LastName, AccountId__r.BillingStreet, AccountId__r.BillingCity, AccountId__r.BillingState FROM lda_Opportunity__c WHERE Owner_Entity__c = '{0}'".format(EID)

		# TerraForce Query
		fields = 'Id, AccountId__c, AccountId__r.Name, AccountId__r.FirstName, AccountId__r.MiddleName__c, AccountId__r.LastName, AccountId__r.BillingStreet, AccountId__r.BillingCity, AccountId__r.BillingState'
		wc = "Owner_Entity__c = '{0}'".format(EID)
		dDeals = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

		# Check Offers for Person Account
		# qs = "SELECT Id, Buyer__r.Id, Buyer__r.Name, Buyer__r.FirstName, Buyer__r.MiddleName__c, Buyer__r.LastName, Buyer__r.BillingStreet, Buyer__r.BillingCity, Buyer__r.BillingState FROM lda_Offer__c WHERE Buyer_Entity__c = '{0}'".format(EID)

		# TerraForce Query
		fields = 'Id, Buyer__r.Id, Buyer__r.Name, Buyer__r.FirstName, Buyer__r.MiddleName__c, Buyer__r.LastName, Buyer__r.BillingStreet, Buyer__r.BillingCity, Buyer__r.BillingState'
		wc = "Buyer_Entity__c = '{0}'".format(EID)
		dOffers = tf_query_3(service, rec_type='Offer', where_clause=wc, limit=None, fields=fields)

		for row in dOffers:
			if row['Buyer__r'] == '':
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
				dTemp['type'] = 'Account'
				dEmp.append(dTemp)

		if dChild[0]['AccountLinks__r'] != 'None':
			for row in dChild[0]['AccountLinks__r']['records']:
				if row['ChildAccount__r'] == 'None':
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
					dTemp['type'] = 'Account'
					dEmp.append(dTemp)

		for row in dDeals:
			if row['AccountId__c'] == '':
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
				dTemp['type'] = 'Account'
				dEmp.append(dTemp)
		
		if dEmp != []:
			print('\n Employees:\n')
			i = 0
			print(' 0) NO MATCH')

			# print list of possible matches
			for row in dEmp:
				i = i + 1
				if row['MiddleName__c'] is None or row['MiddleName__c'] == 'None':
					personname = '{0} {1}'.format(row['FirstName'], row['LastName'])
				else:
					personname = '{0} {1} {2}'.format(row['FirstName'], row['MiddleName__c'], row['LastName'])
				if personname != '':
					print('{:2}) {:<25} {:<30} {:<15} {:2}'.format(i, personname[:25], row['BillingStreet'][:30], row['BillingCity'][:15], row['BillingState']))
			while 1:
				try:
					matchNum = int(td.uInput('\n Enter match number or 0 for no match. >  '))
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
				RTY = 'Person Account'
				print('\n Returning PERSON: {0}'.format(PERSON))
				return PERSON, PERSONID, RTY

		if person == 'None':
			PERSON, PERSONID, RTY = 'None', 'None', 'Person Account'
			return PERSON, PERSONID, RTY

# Delete Existing Lot Details Function
def deleteExistingLotDetails(service, DID):
	# Only select Lot Description RecordTypeID
	# qs = "SELECT Id, Name FROM lda_Lot_Detail__c WHERE Opportunity__c = '{0}' AND RecordTypeID = '{1}'".format(DID, '012a0000001ZSiZAAW')
	# TerraForce Query
	fields = 'default'
	wc = "Opportunity__c = '{0}' AND RecordTypeID = '{1}'".format(DID, '012a0000001ZSiZAAW')
	lotdetailsresults = tf_query_3(service, rec_type='LotDetail', where_clause=wc, limit=None, fields=fields)
	if lotdetailsresults == []:
		return
	for lotdetailsrow in lotdetailsresults:
		LDID = lotdetailsrow['Id']
		# sfdelete(service, LDID)
		tf_delete_3(service, LDID, 'lda_Lot_Detail__c')
	print('\n Existing Lot Detail records deleted...\n')

# Add a Note to the TF Record
def addNote(service, DID, title, body):
	noted = {}
	noted['type'] = 'Note'
	noted['ParentId'] = DID
	noted['Title'] = title
	noted['Body'] = body
	noteId = tf_create_3(service, noted, 'Note')

# Format date to SalesForce format
def formatDateToSF(date): #formatSalesForceDate
	# In -> 09/20/2013
	# Return - > YYYY-MM-DDThh:mm:ss+hh:mm
	MO,DY,YR = date.split('/')
	if len(YR) == 2:	#change 2 digit year to 4 digit year
		YR = '20{0}'.format(YR)
	if len(MO) == 1:	#change 1 digit month to 2 digit month
		MO = '0{0}'.format(MO)
	if len(DY) == 1:	#change 1 digit day to 2 digit day
		DY = '0{0}'.format(DY)
	date = YR+'-'+MO+'-'+DY+'T00:00:00+00:00'
	return date

def lineno():
	from inspect import currentframe
	# """Returns the current line number in our program."""
	return currentframe().f_back.f_lineno

# Checks if Account exists in TF and returns TEXT, PERSON, INFO & Account Id (AID)
def qAccount(text, person, service):
	#set default values
	AID = 'None'
	TEXT = text
	PERSON = 'NO PERSON'
	INFO = 'NO INFO'

	# exceptions
	if 'D R HORTON' in text:
		text = 'DR Horton - Scottsdale'

	print('\n Checking TerraForce for Business Account...(bb.qAccount)')
	lao.highlight(text)
	if lao.coTF(text) is False:
		print('Hold on {0} is not a business...(bb.qAccount)'.format(text))
		person = text
		TEXT = 'NO TEXT'
		PERSON = findPersonsOfEntity(service, AID, person)
		return TEXT, PERSON, INFO, AID

	#remove commas
	if 'K. HOVNANIAN' not in text:  #exception for K. HOVNANIAN
		text = lao.pcr(text)		#remove commas and periods
	person = lao.pcr(person)        #remove commas and periods
	splitText = text.split(' ')		#split string into separate words
	if len(splitText) >= 3:			#is string greater than three words then use first two else use first
		textPart = '{0} {1}'.format(splitText[0], splitText[1])
	else:
		textPart = splitText[0]
	textPart = textPart + '%'		#add % wild card to string

	#log into TerraForce and query Account for textPart placing the result in rec
	# qs = "SELECT Id, Name, Phone, BillingStreet, BillingCity, BillingState, BillingPostalCode FROM Account WHERE Name LIKE '{0}'".format(textPart)
	# TerraForce Query
	fields = 'default'
	wc = "Name LIKE '{0}'".format(textPart)
	results = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)


	#return null values if no match was found
	if rec == []:
		return TEXT, PERSON, INFO, AID

	#create Business Account selection list
	i = 0
	busNoMatch = False
	print('\n 0)  NO MATCH')
	for row in rec:
		i = i + 1
		if lao.coTF(row['Name']) == True:
			print('{:2})  {:<45} {:<20} {:2}'.format(i, row['Name'][:43], row['BillingCity'], row['BillingState']))
			busNoMatch = True

	if busNoMatch is False:
		print('No business')
		return TEXT, PERSON, INFO, AID

	print
	matchNum = int(td.uInput(' Enter match number or 0 for no match (bb.qAccount(1)): '))
	matchNum = matchNum - 1	#reduce the match number by one to match the row list
	if matchNum >= 0:	#did the user select a match? - Yes
		AID = rec[matchNum]['Id']
		TEXT = rec[matchNum]['Name']
		PERSON = findPersonsOfEntity(service, AID, person)
		#confirm complete address
		if rec[matchNum]['BillingStreet'] =='' or \
				rec[matchNum]['BillingCity'] =='' or \
				rec[matchNum]['BillingState'] =='' or \
				rec[matchNum]['BillingPostalCode'] =='':
			return TEXT, PERSON, INFO, AID
		INFO = '{}\r\n{}, {} {}'.format(rec[matchNum]['BillingStreet'],rec[matchNum]['BillingCity'],rec[matchNum]['BillingState'],rec[matchNum]['BillingPostalCode'])
		return TEXT, PERSON, INFO, AID
	else:				#did the user select a match? - No
		return TEXT, PERSON, INFO, AID #using default values

# Checks if Account exists in TF based on partial name and returns TEXT, PERSON, INFO & Account Id (AID)
def qAccountPartialName(text):
	print('\n Checking TerraForce for Business Account (bb.qAccountPartialName)...')
	lao.highlight(text)
	service = fun_login.TerraForce()
	
	query_string = "SELECT Id, Name, BillingStreet, BillingCity, BillingState, BillingPostalCode  FROM Account WHERE Name LIKE '{0}%%'".format(text)
	query_result = service.query(query_string)
	rec = query_result['records']  # dictionary of results!
	if rec != []:
		i = 0
		print('[0 ]  No Match')
		for row in rec:
			n = str(i+1)
			print('[%-2s]  %-40s  %-25s {0}'.format(n,row['Name'],row['BillingCity'],row['BillingState']))
			i=i+1
		user_input = int(td.uInput('\n Select entity or 0 for no match... > '))
	else:
		print('\n No matching Business Account in TerraForce...\n')
		user_input = 0
	if user_input == 0:
		TEXT = 'false'
		PERSON = 'false'
		AIDTXT = ''
		AIDPRS = ''
		return TEXT, AIDTXT, PERSON, AIDPRS
	else:
		user_input = user_input-1
		TEXT = rec[user_input]['Name']
		AIDTXT = rec[user_input]['Id']

	#check to see if TEXT is a person
	#William Stegeman 0013000000SXjLYAA1 William Stegeman 0013000000SXjLYAA1
	if lao.coTF(TEXT) == False:
		PERSON = TEXT
		AIDPRS = AIDTXT
		TEXT = ''
		AIDTXT = ''
		return TEXT, AIDTXT, PERSON, AIDPRS

	#check for persons/employees of user input
	query_string = "SELECT Id, BillingStreet, BillingCity, BillingState, BillingPostalCode, Name FROM Account WHERE Company__c = '{0}'".format(AIDTXT)
	query_result = service.query(query_string)
	rec = query_result['records']  # dictionary of results!
	i = 0
	print('\n Employees: \n[0 ]  No Match')
	for row in rec:
		n = str(i+1)
		print('[%-2s]  %-30s  %-25s {0}'.format(n,row['Name'],row['BillingCity'],row['BillingState']))
		i=i+1
	user_input = input('\r\nSelect person or 0 for no match... > ')
	if user_input == 0:
		PERSON = 'false'
		AIDPRS = ''
	else:
		user_input = user_input-1
		PERSON = rec[user_input]['Name']
		AIDPRS = rec[user_input]['Id']
	return TEXT, AIDTXT, PERSON, AIDPRS

# Determines if the Recorded Doc Number is already in SalesForce, Returns True of False
def RDNexistDeal(service, RDN):
	# qs = "SELECT Id FROM lda_Opportunity__c WHERE Recorded_Instrument_Number__c = '{0}'".format(RDN)
	# TerraForce Query
	fields = 'default'
	wc = "Recorded_Instrument_Number__c = '{0}'".format(RDN)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	if len(results) >= 1:
		return True
	else:
		return False

# Get Deal data as dictionary of all data or a single field
def getLeadDealData(service, didpid, dealVar='All'):
	# Check if didpid is a dictionary
	try:
		didpid = didpid['Id']
	except TypeError:
		pass
	# If didpid is a PID get the DID
	didorpid = isDIDorPID(didpid)
	if didorpid == 'PID':
		DID = getDIDfromPID(service, didpid)
	else:
		DID = didpid
	# Handle if no PID exists
	if DID == 'No PID Exists':
		return 'No PID Exists'
	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	# Return data user requested
	if dealVar == 'All':
		return results[0]
	elif dealVar == 'Acres':
		return results[0]['Acres__c']
	elif dealVar == 'City':
		return results[0]['City__c']
	elif dealVar == 'Classification':
		return results[0]['Classification__c']
	elif dealVar == 'County':
		return results[0]['County__c']
	elif dealVar == 'DealName':
		return results[0]['Name']
	elif dealVar == 'Description':
		return results[0]['Description__c']
	elif dealVar == 'IdEntity':
		return results[0]['Owner_Entity__c']
	elif dealVar == 'IdPerson':
		return results[0]['AccountId__c']
	elif dealVar == 'Location':
		return results[0]['Location__c']
	elif dealVar == 'LonLat':
		return results[0]['Longitude__c'], results[0]['Latitude__c']
	elif dealVar == 'LotType':
		return results[0]['Lot_Type__c']
	elif dealVar == 'Lots':
		return results[0]['Lots__c']	
	elif dealVar == 'Market':
		if 'AZParcelsYuma' in didpid or 'CAParcelsRiverside' in didpid or 'CAParcelsImperial' in didpid:
			return 'Yuma'
		print(results[0]['State__c'])
		print(results[0]['County__c'])
		if results[0]['Market__c'] == '':
			dCounties = lao.getCounties('FullDict')
			for i in dCounties:
				if dCounties[i]['StateFull'] == results[0]['State__c'] and (dCounties[i]['County'] == results[0]['County__c'] or dCounties[i]['ArcName'] == results[0]['County__c']):
					return dCounties[i]['Market']
		return results[0]['Market__c']
	elif dealVar == 'NameEntity':
		return results[0]['Owner_Entity__r']['Name']
	elif dealVar == 'NamePerson':
		return results[0]['AccountId__r']['Name']
	elif dealVar == 'OPR_Sent':
		return results[0]['OPR_Sent__c']
	elif dealVar == 'Parcels':
		return results[0]['Parcels__c']
	elif dealVar == 'StageName':
		return results[0]['StageName__c']
	elif dealVar == 'State':
		return results[0]['State__c']
	elif dealVar == 'Subdivision':
		return results[0]['Subdivision__c']
	elif dealVar == 'Submarket':
		return results[0]['Submarket__c']
	elif dealVar == 'Zipcode':
		return results[0]['Zipcode__c']
	elif dealVar == 'Zoning':
		return results[0]['Zoning__c']

# Print results of an Update or Creat
def printResults(results, type = 'Create or Update'):
	if results[0]['success']:
		print('\nSuccessful {0} - ID: {1}'.format(results[0]['id'], type))
		if type == 'Create':  # return the new record ID if one is Created
			return results[0]['id']  # return new ID
	else:
		print('\nFailed to {0}'.format(type))
		print(results)
		ui = td.uInput('[Y/T/1] to Terminate Program or [Enter] to Continue\n > ')
		if ui == '':
			if type == 'Create':
				return 'None'
		else:
			exit('\nTerminating program...')

# Sets Deal's OPR_Sent__c to today's date
def sentToUsers(service, results = 'None'):
	if results == 'None':
		# qs = "SELECT Id FROM lda_Opportunity__c WHERE OPR_Sent__c = 1965-01-11 AND Classification__c != ''"
		# TerraForce Query
		fields = 'default'
		wc = "OPR_Sent__c = 1965-01-11 AND Classification__c != ''"
		results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	for row in results:		#loop through query results
		SentID = row['Id']
		today = td.today_date()
		# today = '1965-01-12'
		object_dict = {'type': 'lda_Opportunity__c', 'Id': SentID, 'OPR_Sent__c': today}
		up_results = tf_update_3(service, object_dict)
	print('Sent to Users updated')

# SalesForce Create record object
def tf_create_3(service, object_dict):
	from simple_salesforce.exceptions import SalesforceResourceNotFound, SalesforceMalformedRequest
	import lao
	# user = lao.getUserName()
	lao.print_function_name(' [bb def tf_create_3]')

	# Delete None Values from object_dict
	lDel = []
	for key in object_dict.keys():
		if object_dict[key] == 'None' or object_dict[key] == 'Skip' or object_dict[key] == '' or object_dict[key] == None:
			lDel.append(key)
	for key in lDel:
		del object_dict[key]

	# Get the account type
	tf_object_type = object_dict['type']
	del object_dict['type']

	# The LAO Employee USER ID not the contact ID
	# Get the Researcher's USER ID from LAO Staff spreadsheet
	# Add user as the Deal TF record owner
	if tf_object_type == 'lda_Opportunity__c' or tf_object_type == 'Account':
		object_dict['OwnerId'] = lao.getUser_tfUserID()

	str_tf_service = f'service.{tf_object_type}.create({object_dict})'

	# Update TF object
	print(f'\n Creating {tf_object_type}...')
	try:
		results = eval(str_tf_service)
		td.colorText(f' {tf_object_type} created successfully...', 'GREEN')
		return results['id']
	except (SalesforceResourceNotFound, SalesforceMalformedRequest) as e:
		tf_fail_message(e, object_dict, tf_object_type)
		return 'Create Failed'

# SalesForce Delete record object
def tf_delete_3(service, tf_object_id, tf_object_type):
	# Build TF delete string
	str_tf_service = f'service.{tf_object_type}.delete("{tf_object_id}")'
	# Delete TF object
	print(f'\n Deleting {tf_object_type}...')
	try:
		results = eval(str_tf_service)
		td.colorText('\n Delete successful...\n', 'GREEN')
		return 'Delete Successful'
	except:
		td.warningMsg('\n Could not delete record.\n')
		print(str_tf_service)
		return 'Delete Failed'

# SalesForce Update record object
def tf_update_3(service, object_dict):
	from simple_salesforce.exceptions import SalesforceResourceNotFound
	from simple_salesforce.exceptions import SalesforceMalformedRequest
	import lao
	from pprint import pprint

	lao.print_function_name('bb def tf_update_3')

	# CLEAN DICT ##########################################################
	# Delete None Values from object_dict
	object_dict_cleaned = {}
	for key in object_dict.keys():
		# Assign None value to Owner_Entity__c if its value is 'None'
		if key == 'Owner_Entity__c':
			if object_dict['Owner_Entity__c'] == 'None' or object_dict['Owner_Entity__c'] == None:
				object_dict_cleaned['Owner_Entity__c'] = ''
		if key == 'AccountId__c':
			if object_dict['AccountId__c'] == 'None' or object_dict['AccountId__c'] == None:
				object_dict_cleaned['AccountId__c'] = ''
		# Skip keys with None values
		elif object_dict[key] == 'None' or object_dict[key] == 'Skip' or object_dict[key] == 0:
			continue
		else:
			object_dict_cleaned[key] = object_dict[key]
	
	# Get the account type and object id
	tf_object_type = object_dict_cleaned['type']
	del object_dict_cleaned['type']
	if 'Id' in object_dict_cleaned:
		tf_object_id = object_dict_cleaned['Id']
		del object_dict_cleaned['Id']
	else:
		tf_object_id = object_dict_cleaned['id']
		del object_dict_cleaned['id']
	
	# The LAO Employee USER ID not the contact ID
	# Get the Researcher's USER ID from LAO Staff spreadsheet
	# Add user as the Deal TF record owner
	if tf_object_type == 'lda_Opportunity__c' or tf_object_type == 'Account':
		object_dict_cleaned['OwnerId'] = lao.getUser_tfUserID()

	# Build TF update strings
	# Service: Reset Verified field to False
	if tf_object_type == 'lda_Opportunity__c':
		dReset_verified = {'Verified__c': False}
		str_tf_service_reset_verified = f'service.{tf_object_type}.update("{tf_object_id}", {dReset_verified})'
		results = eval(str_tf_service_reset_verified)
	
	# print('here1634')
	# print(f'\n tf_object_type {tf_object_type} with tf_object_id: {tf_object_id}...')
	# print(f'object_dict_cleaned: {object_dict_cleaned}')
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	# Service: Update TF object
	str_tf_service = f'service.{tf_object_type}.update("{tf_object_id}", {object_dict_cleaned})'
	# Update TF object
	try:
		results = eval(str_tf_service)
		if results == 204:
			td.colorText('\n Update successful...', 'GREEN')
			return tf_object_id
	except (SalesforceResourceNotFound, SalesforceMalformedRequest) as e:
		tf_fail_message(e.content, object_dict, tf_object_type)
		return 'Update Failed'

# SelesForce Query
def tf_query_3(service, rec_type, where_clause, limit=None, fields='default'):
	import acc
	from pprint import pprint

	# PERSON ###############################################
	if rec_type == 'Contact':
		if fields == 'default':
			fields = dicts.get_TF_contact_query_fields()
		query_string = "SELECT {0} FROM Contact WHERE {1}".format(fields, where_clause)
	# DEAL ###############################################
	elif rec_type == 'Deal':
		if fields == 'default':
			fields = dicts.get_TF_deal_query_fields()
		query_string = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, where_clause)
	# ENTITY ###############################################
	elif rec_type == 'Entity':
		if fields == 'default':
			fields = dicts.get_TF_entity_query_fields()
		query_string = "SELECT {0} FROM Account WHERE {1}".format(fields, where_clause)
	# LOT DETAILS ###############################################
	elif rec_type == 'LotDetail':
		if fields == 'default':
			fields = dicts.get_TF_lot_detail_query_fields()
		query_string = "SELECT {0} FROM lda_Lot_Detail__c WHERE {1}".format(fields, where_clause)
	# OFFER ###############################################
	elif rec_type == 'Offer':
		if fields == 'default':
			fields = dicts.get_TF_offer_query_fields()
		query_string = "SELECT {0} FROM lda_Offer__c WHERE {1}".format(fields, where_clause)
	# PACKAGE ###############################################
	elif rec_type == 'Package':
		if fields == 'default':
			fields = dicts.get_TF_package_query_fields()
		query_string = "SELECT {0} FROM lda_Package_Information__c WHERE {1}".format(fields, where_clause)
	# PERSON ###############################################
	elif rec_type == 'Person':
		if fields == 'default':
			fields = dicts.get_TF_person_query_fields()
		query_string = "SELECT {0} FROM Account WHERE {1}".format(fields, where_clause)
	# REQUEST ###############################################
	elif rec_type == 'Request':
		if fields == 'default':
			fields = dicts.get_TF_request_query_fields()
		query_string = "SELECT {0} FROM lda_Request__c WHERE {1}".format(fields, where_clause)
	# TASK ###############################################
	elif rec_type == 'Task':
		if fields == 'default':
			fields = dicts.get_TF_task_query_fields()
		query_string = "SELECT {0} FROM Task WHERE {1}".format(fields, where_clause)
	# CODE DID NOT SPECIFY rec_type ###############################################
	else:
		td.warningMsg(f'\n Invalid rec_type * {rec_type} *...\n Must be Person, Entity, Deal, LotDetail, Offer, Package or Task...')
		exit('\n Terminating program...')
	
	# Add LIMIT if given
	if limit != None:
		query_string = "{0} LIMIT {1}".format(query_string, limit)

	from collections import OrderedDict
	query_result = service.query_all(query_string)
	records = query_result['records']  # dictionary of results!
	records = replace_dict_none_values(records)
	return records

# LIGHTNING NOTE FUNCTIONS (New) ################################################
def create_tf_lightning_note(service, title, content, parent_id):
	"""
	Creates a Lightning Note using LAO's existing tf_create_3 function from bb.py.
	
	Args:
		service: Authenticated Salesforce connection from fun_login.TerraForce()
		title (str): Note title
		content (str): Note content
		parent_id (str): Contact/Account ID to attach the note to
	
	Returns:
		dict: Success status and created record info
	"""
	
	try:
		import bb  # Import your bb library
		
		# Step 1: Create ContentVersion (the actual note content)
		# Encode content as base64 for Salesforce
		content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
		
		content_version_data = {
			'type': 'ContentVersion',
			'Title': title,
			'PathOnClient': f"{title}.snote",  # .snote extension for Salesforce Notes
			'VersionData': content_base64,
			'ContentLocation': 'S',  # S = Salesforce
			'Origin': 'H'  # H = Chatter (for Notes)
		}
		
		# Create the ContentVersion using your existing tf_create_3 function
		print(f'\n Creating Lightning Note: {title}...')
		content_version_id = tf_create_3(service, content_version_data)
		
		if content_version_id == 'Create Failed':
			return {
				'success': False,
				'error': 'Failed to create ContentVersion'
			}
		
		# Step 2: Get the ContentDocumentId from the created ContentVersion
		# Use your existing tf_query_3 function - but we need to handle ContentVersion queries
		try:
			# Query ContentVersion directly since it's not in your tf_query_3 rec_types
			query_string = f"SELECT ContentDocumentId FROM ContentVersion WHERE Id = '{content_version_id}'"
			query_result = service.query(query_string)
			
			if query_result['totalSize'] == 0:
				return {
					'success': False,
					'error': 'Could not retrieve ContentDocumentId'
				}
			
			content_document_id = query_result['records'][0]['ContentDocumentId']
		except Exception as e:
			return {
				'success': False,
				'error': f'Error querying ContentDocumentId: {str(e)}'
			}
		
		# Step 3: Create ContentDocumentLink to associate the note with the parent record
		content_link_data = {
			'type': 'ContentDocumentLink',
			'ContentDocumentId': content_document_id,
			'LinkedEntityId': parent_id,
			'ShareType': 'V',  # V = Viewer access
			'Visibility': 'AllUsers'  # Visible to all users with access to parent record
		}
		
		# Create the ContentDocumentLink using your existing tf_create_3 function
		content_link_id = bb.tf_create_3(service, content_link_data)
		
		if content_link_id == 'Create Failed':
			return {
				'success': False,
				'error': 'Failed to create ContentDocumentLink'
			}
		
		return {
			'success': True,
			'content_document_id': content_document_id,
			'content_document_link_id': content_link_id,
			'note_title': title,
			'parent_id': parent_id,
			'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		}
		
	except Exception as e:
		return {
			'success': False,
			'error': f"Exception creating Lightning note: {str(e)}"
		}
	
# Get update dictionary for TerraForce update
def get_update_dict(results='None', id='None', account_type='None'):
	if results != 'None':
		id = results[0]['Id']
		account_type = results[0]['attributes']['type']
		dup = {'type': account_type, 'id': id}
		return dup

# TF create & update fail message
def tf_fail_message(results, object_dict, tf_object_type):
	td.warningMsg('\n {0} was not created...\n'.format(tf_object_type))
	print(results)
	print()
	print(f' Object type: {tf_object_type}')
	print()
	pprint(object_dict)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
# Replace None (null) values with string 'None'

def replace_dict_none_values(dictionary):
	if isinstance(dictionary, list):
		for i in range(len(dictionary)):
			dictionary[i] = replace_dict_none_values(dictionary[i])
	elif isinstance(dictionary, dict):
		for key in dictionary:
			dictionary[key] = replace_dict_none_values(dictionary[key])
	elif dictionary is None:
		dictionary = 'None'
	return dictionary

def sfgetdeleted(service):
	from datetime import datetime, timedelta
	now = datetime.now()
	print(now)
	then = now - timedelta(7)
	print(then)
	results = service.getDeleted('lda_Opportunity__c', then, now)
	print(results)

# close deal typically after offer has been created
def closeDeal(DID, service):
	od = {'type':'lda_Opportunity__c', 'Id':DID, 'StageName__c':'Closed Lost'}
	results = tf_update_3(service, od)
	return results

def findbypriceandacre(price_acre, service):
	if ' ' in price_acre:
		price_acre = price_acre.split()
		price = price_acre[0]
		acre = price_acre[1]
		acre = float(acre)
	else:
		price = price_acre
		acre = False
	price = price.replace('$','').replace(',','')
	price = float(price)
	qs = "SELECT Acres__c, Id, Name, Sale_Price__c FROM lda_Opportunity__c WHERE PID__c LIKE 'AZ%' AND Sale_Price__c = " + str(price)
	

	# TerraForce Query
	fields = 'default'
	wc = "PID__c LIKE 'AZ%' AND Sale_Price__c = " + str(price)
	if acre is not False:
		wc = f'{wc} AND Acres__c = {acre}'
		# wc = wc + ' AND Acres__c = ' + str(acre)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	if results != []:
		for row in results:
			print('Deal:  {0}\nAcres: {1}\nID:    {2}\n'.format(row['Name'], row['Acres__c'], row['Id']))
	else:
		print('\n No Deals selected.')

# Create Lot Details for a Deal
def LotDetail(service, DID):

	# qs = "SELECT ID, Name, Acres__c, Classification__c, Lot_Type__c, Lots__c, Sale_Date__c, Sale_Price__c FROM lda_Opportunity__c WHERE Id = '{0}'".format(DID)

	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	PRC = results[0]['Sale_Price__c']
	TTY = results[0]['Lot_Type__c']
	ACR = results[0]['Acres__c']
	classification = results[0]['Classification__c']
	totalLots = results[0]['Lots__c']
	LDT = '012a0000001ZSiZAAW' # Lot Description

	# Apartment and High Densisty Assisted Living are 0 for width & depth so autofill
	if 'Apartment Traditional' in classification or 'High Density Assisted Living' in classification:
		print('\n This is a {0} Deal...auto-entering Lot Details...'.format(classification))
		if totalLots == 0:
			td.warningMsg('\n Numer of Units is zero...')
			totalLots = int(td.uInput('\n Enter the number of Units > '))
			if totalLots == '' or totalLots == 0:
				td.warningMsg('\n Lot Details not entered.')
				lao.holdup()
		name = 'PART 1/1'
		width, depth = 0, 0
		dOffer = {'type': 'lda_Lot_Detail__c', 'Opportunity__c': DID, 'RecordTypeId': LDT, 'Name': name,
			  'Lot_Count__c': totalLots, 'Lot_Width__c': width, 'Lot_Depth__c': depth, 'Price_per_parcel__c': PRC}
		tf_create_3(service, dOffer)
		return totalLots

	# User to enter lot details
	while 1:

		uiNoLots = td.uInput('\n No of PARTS\n\n   Enter number of Lot Detail Parts to be entered or...\n\n   [E]stimate at #.# lots/acre\n\n  > ')
		if len(uiNoLots) > 2:
			td.warningMsg('Invalid entry...try again...')
			continue
		break
	if uiNoLots.upper() == 'E':
		lotDensity = float(td.uInput('\n Enter lot density lots/acre > '))
		estimate = True
		count = int(ACR * lotDensity)
		uiNoLots = 1
		width = 0
		depth = 0
		print
		print(ACR)
	else:
		estimate = False
		uiNoLots = int(uiNoLots)
		lotlist = [[] for i in range(uiNoLots)]
		j = 0
		while 1:
			name = 'PART {0}/{1}'.format(j + 1, uiNoLots)

			while 1:
				print('\n Enter Lot Count, Width & Depth separated by spaces...')
				ui = td.uInput('\n {0} > '.format(name))

				# assign variables for width, depth and lot count
				lotvals = ui.split()

				# check for bad entry
				if len(lotvals) == 3:
					count, width, depth = int(lotvals[0]), int(lotvals[1]), int(lotvals[2])
					print(width, depth, count)
					# Let user enter a Lot Description
					lotDescription = td.uInput('\n Add Lot Description or [Enter] for none > ')
					if lotDescription != '':
						name = '{0} {1}'.format(name, lotDescription)
					break
				else:
					td.warningMsg('Invalid entry...try again...')

			# create lot list dictionary
			lotdetails = {'name': name, 'width': width, 'depth': depth, 'count': count}
			lotlist[j].append(lotdetails)

			# exit entry loop
			if (uiNoLots - 1) == j:
				print
				for row in lotlist:
					print(row)
				print
				print('Data entry complete.')
				break
			j += 1

	# calaculate $/FF if more than 1 record
	totalLots, totalFF = 0, 0
	if uiNoLots > 1:
		for row in lotlist:
			totalLots = totalLots + row[0]['count']
			totalFF = totalFF + ((row[0]['width']) * (row[0]['count']))
		if PRC > 0 and totalFF > 0:
			PFF = PRC / totalFF
		else:
			PFF = 0

		for row in lotlist:
			name, count, width, depth = row[0]['name'], row[0]['count'], row[0]['width'], row[0]['depth']
			PPP = PFF * count * width
			print(name, count, width, depth, PFF, PPP)
			dOffer = {'type': 'lda_Lot_Detail__c', 'Opportunity__c': DID, 'RecordTypeId': LDT, 'Name': name, 'Lot_Count__c': count, 'Lot_Width__c': width, 'Lot_Depth__c': depth, 'Price_per_parcel__c': PPP}
			crResults = tf_create_3(service, dOffer)
		return 0
	else: # Create the Lot Detail
		totalLots = count
		if estimate:
			name = 'PART 1/1 Estimated lots at {0:0.1f} lots/acre'.format(lotDensity)
		else:
			name = 'PART 1/1'
		dOffer = {'type': 'lda_Lot_Detail__c', 'Opportunity__c': DID, 'RecordTypeId': LDT, 'Name': name, 'Lot_Count__c': count, 'Lot_Width__c': width, 'Lot_Depth__c': depth, 'Price_per_parcel__c': PRC}
		tf_create_3(service, dOffer)
		return totalLots

def tf_create_lead_of_sale_deal(service, PID=False, DEALID='None'):
	print
	# TerraForce Query
	fields = "Id, Acres__c, City__c, Classification__c, County__c, Description__c, Keyword_Group__c, Latitude__c, Lead_Parcel__c, Location__c, Longitude__c, Lot_Description__c, Lots__c, Lot_Type__c, Parcels__c, State__c, Subdivision__c, Submarket__c, Zipcode__c, Zoning__c, Source__c, Source_ID__c, StageName__c"
	if PID:
		wc = "PID__c = '{0}'".format(PID)
	else:
		wc = "Id = '{0}'".format(DEALID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	
	if len(results) == 1:
		print('\n Creating Lead/Ownership record...\n')
	else:
		print(' Deal {0} not found.'.format(PID))
		return 'None'

	dd = results[0]
	
	# Check if PID is Closed
	if not 'Closed' in dd['StageName__c']:
		td.warningMsg('\n Stage Name is {0}'.format(dd['StageName__c']))
		ui = td.uInput(' Make Lead? [0/1] > ')
		if ui != '1':
			td.warningMsg('\n You are trying to make a Lead on a PID that is not Closed.')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			return
		
	# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	dd['type'] = 'lda_Opportunity__c'
	dd['RecordTypeID'] = '012a0000001ZSS5AAO' # Brokerage

	# Change County
	if 'Maricopa' in dd['County__c']:
		dd['County__c'] = 'Maricopa'
	elif 'Pinal' in dd['County__c']:
		dd["County__c"] = 'Pinal'

	# TerraForce Query
	fields = 'default'
	wc = "DealID__c = '{0}' AND Offer_Status__c = 'Accepted'".format(dd['Id'])
	results = tf_query_3(service, rec_type='Offer', where_clause=wc, limit=None, fields=fields)
	
	# Add Offer's Entity adn Person to Lead
	if results[0]['Buyer_Entity__r'] != 'None':
		dd['Owner_Entity__c'] = results[0]['Buyer_Entity__r']['Id']
	if results[0]['Buyer__r'] != 'None':
		dd['AccountId__c'] = results[0]['Buyer__r']['Id']

	dd['Parent_Opportunity__c'] = dd['Id']

	# Make Deal Name
	if results[0]['Buyer_Entity__r'] != 'None':
		NAME = results[0]['Buyer_Entity__r']['Name']
	else:
		NAME = results[0]['Buyer__r']['Name']
	
	# Shorten Name if too long
	while 1:
		if len(NAME) > 50:
			lNAME = NAME.split()
			lNAME = lNAME[0:-1]
			NAME = ' '.join(lNAME)
		else:
			break

	dd['Name'] = '{0} {1:.1f} Ac'.format(NAME, dd['Acres__c'])
	dd['StageName__c'] = 'Lead'
	if dd['Keyword_Group__c'] == '':
		dd['Keyword_Group__c'] = PID
	del dd['Id']
	
	# Create Lead
	DID = tf_create_3(service, dd)
	
	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	PIDnew = results[0]['PID__c']
	# DID = results[0]['Id']
	print('\n New Ownership PID: {0}...'.format(PIDnew))

	# Create Ownership polygon for new PID
	while 1:
		td.instrMsg(f'\n Create Ownership polygon for new PID?')
		print('  1) Yes')
		print('  2) No')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			print('  Creating Ownership polygon...')
			import mpy
			oi_results = mpy.oi_make_from_pid(PID=PID, PIDnew=PIDnew)
			break
		elif ui == '2':
			print('  Not creating Ownership polygon.')
			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			print('  Invalid selection, exiting...')
			exit('\n Terminating program...')
	return PIDnew

def openVizzdaReport(service):
	while 1:
		lao.banner('Open Vizzda Report')
		ui = (td.uInput('Enter PID or VID or [00] Quit > ')).upper()
		if 'AZ' in ui:
			# qs = "SELECT Source_ID__c FROM lda_Opportunity__c WHERE PID__c = '{0}'".format(ui)

			# TerraForce Query
			fields = 'default'
			wc = "PID__c = '{0}'".format(ui)
			results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
			VID = results[0]['Source_ID__c']
		elif ui == 'Q' or ui == '00':
			return
		else:
			VID = ui
		openbrowser('https://www2.vizzda.com//detail/{0}'.format(VID))

def openVizzdaReturnPID(service, VID):
	# TerraForce Query
	fields = 'default'
	wc = "Source_ID__c = '{0}'".format(VID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# qs = "SELECT PID__c FROM lda_Opportunity__c WHERE Source_ID__c = '{0}'".format(VID)

	if results == []:
		return 'None'
	PID = results[0]['PID__c']
	openbrowser('https://www2.vizzda.com//detail/{0}'.format(VID))
	return PID

def openPandZPID(service, PID):
	td.warningMsg('\n bb openPandZPID depreciated use web.open_pid_did() instead')
	# from webs import openTFDID
	# # qs = "SELECT Id, StageName__c FROM lda_Opportunity__c WHERE PID__c = '{0}'".format(PID)

	# # TerraForce Query
	# fields = 'default'
	# wc = "PID__c = '{0}'".format(PID)
	# results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# if results != []:
	# 	driver = openTFDID(results[0]['Id'])
	# 	return results[0]['StageName__c'], driver
	# return 'None', 'None'

def copyPIDtoClipboard(service, DID, root):
	# qs = "SELECT PID__c FROM lda_Opportunity__c WHERE Id = '{0}'".format(DID)

	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	PID = results[0]['PID__c']
	root.clipboard_clear()
	root.clipboard_append(PID)
	input('New PID {0} copied to clipboard...Continue... > '.format(PID))
	return PID

def isLAODeal(service, PID='None', DID='None'):
	while 1:
		# qs = "SELECT Id, RecordTypeId, Type__c, StageName__c, (SELECT Offer_Status__c FROM Offers__r), (SELECT Agent__c FROM Commissions__r) FROM lda_Opportunity__c WHERE PID__c = '{0}'".format(PID)

		# TerraForce Query
		fields = 'default'
		wc = "PID__c = '{0}'".format(PID)
		results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		# No results cuz could not find PID
		if results == []:
			td.warningMsg('\n Could not find PID {0} in TerraForce...try again...'.format(PID))
			return 'Try Again'
		DID = results[0]['Id']
		LAOquit = False
		if results[0]['RecordTypeId'] == '012a0000001ZSS5AAO' and results[0]['Type__c'] == 'Exclusive LAO':
			openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))
			td.warningMsg('\n********** WARNING LAO Exclusive & Brokerage Lead **********')
			td.uInput('\n Change LAO Exclusive to None...continue...')
		if results[0]['StageName__c'] != 'Lead':
			LAOquit = True
			td.warningMsg('\n********** WARNING Record is not a Lead!! **********')
			td.warningMsg('********** Stage Name: {0} **********'.format(results[0]['StageName__c']))
		if results[0]['Offers__r'] != 'None':
			offer_status = results[0]['Offers__r']['records'][0]['Offer_Status__c']
			if offer_status == 'Pending' or offer_status == 'Accepted':
				LAOquit = True
				td.warningMsg(f'\n********** WARNING Deal has {offer_status} Offer!! **********')
		if results[0]['Commissions__r'] != 'None':
			LAOquit = True
			td.warningMsg('\n********** WARNING Deal has Commissions present!! **********')
		if LAOquit is True:
			openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))
			ui = (td.uInput('\n Recommend Quitting!!\n\n [00] Quit or [C]ontinue > ')).upper()
			if ui == 'Q' or ui == '00':
				exit('Terminating program...')
			elif ui == 'C':
				return
		else:
			return

def isCompetitorListing(service, PID):
	print
	# fields = 'Id, RecordTypeId, Type__c, StageName__c, (SELECT Offer_Status__c FROM Offers__r), (SELECT Agent__c FROM Commissions__r)'
	# wc = "PID__c = '{0}'".format(PID)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "PID__c = '{0}'".format(PID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# No results cuz could not find PID
	if results == []:
		td.warningMsg('\n Could not find PID {0} in TerraForce...try again...'.format(PID))
		return 'Try Again'
	if results[0]['RecordTypeId'] == '012a0000001ZSS8AAO':
		if results[0]['StageName__c'] == 'Lead':
			if results[0]['Commissions__r'] != []:
				return True

def tfRecordInfo(service, PID, isFixPIDScript=False):
	from datetime import datetime
	from pprint import pprint

	rd = getLeadDealData(service, didpid=PID, dealVar='All')
	rd['PackageExists'], rd['CommissonExists'], rd['RequestExists'], rd['OfferExists'], rd['AccReceivableExists'], rd['NoteExists'], rd['OkToEdit'], rd['InitialLotOption'] = False, False, False, False, False, False, False, False
	if rd['Lot_Type__c'] == 'Initial Lot Option':
		rd['InitialLotOption'] = True
	# if len(rd['Package_Information__r']) > 0:
	if rd['Package_Information__r'] != 'None':
		# for i in range(0, len(rd['Package_Information__r'])):
		# 	if rd['Package_Information__r'][i]['LastModifiedDate'] > datetime(2014,12,31,0,0,0):
		rd['PackageExists'] = True
	if rd['Commissions__r'] != 'None':
		for row in rd['Commissions__r']['records']:
			if row['LAO_Agent__c'] == 1:
				rd['CommissonExists'] = True
				break
	if rd['Request_Deal__r'] != 'None':
		# for i in range(0, len(rd['Request_Deal__r']['records'])):
		# 	created_date = datetime.strptime(rd['Request_Deal__r']['records'][i]['CreatedDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
		# 	if created_date> datetime(2014, 12, 31, tzinfo=created_date.tzinfo):
		rd['RequestExists'] = True
	if rd['Offers__r'] != 'None' and not 'Initial Lot Option' in rd['Lot_Type__c']:
		rd['OfferExists'] = True
	if rd['NotesAndAttachments'] != 'None':
		# for i in range(0, len(rd['NotesAndAttachments'])):
		# 	if rd['NotesAndAttachments'][i]['LastModifiedDate'] > datetime(2014,12,31,0,0,0):
		rd['NoteExists'] = True
	if rd['Notes'] != 'None':
		# for i in range(0, len(rd['Notes'])):
		# 	if rd['Notes'][i]['LastModifiedDate'] > datetime(2014,12,31,0,0,0):
		rd['NoteExists'] = True
	if rd['Accounts_Receivable__r'] != 'None':
		rd['AccReceivableExists'] = True
	if 'Lead' in rd['StageName__c'] or 'Lead' in rd['StageName__c'] or 'Target' in rd['StageName__c'] or 'Initial Lot Option' in rd['Lot_Type__c']:
		rd['OkToEdit'] = True
	if isFixPIDScript:
		if rd['StageName__c'] != 'Closed' or rd['StageName__c'] != 'Escrow':
			rd['OkToEdit'] = True
	# Competitor Listing in escrow (Reserach type and Escrow)
	if rd['RecordTypeId'] == '012a0000001ZSS8AAO' and rd['StageName__c'] == 'Escrow':
		rd['OkToEdit'] = True
	return rd

def splitDeal(service, PID):
	from webs import openTFDID

	# TerraForce Query
	fields = 'default'
	wc = "PID__C = '{0}'".format(PID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	for row in results:
		dNewPID = row
		dNewPID['List_Price__c'] = 10000
		dNewPID['type'] = 'lda_Opportunity__c'

		dOldPID = {}
		dOldPID['type'] = 'lda_Opportunity__c'
		dOldPID['Id'] = row['Id']
		dOldPID['Acres__c'] = row['Acres__c']
		dOldPID['Lots__c'] = row['Lots__c']

		# Enter Acres
		while 1:
			print('\n Enter Acres to Split\n\n Existing Acres: {0}'.format(dOldPID['Acres__c']))
			dNewPID['Acres__c'] = float(td.uInput('\n Enter Acres to Split > '))
			if dNewPID['Acres__c'] == '':
				td.warningMsg('\n No value entered...try again...')
				continue
			elif dNewPID['Acres__c'] >= dOldPID['Acres__c']:
				td.warningMsg('\n Total Split Acres cannot equal or exceed Total Existing Acres...try again...\n')
				continue
			dOldPID['Acres__c'] = dOldPID['Acres__c'] - dNewPID['Acres__c']
			break

		# Enter Lots
		if dNewPID['Lots__c'] > 0:
			while 1:
				print('\n Enter Lots to Split\n\n Existing Lots: {0}'.format(dOldPID['Lots__c']))
				dNewPID['Lots__c'] = float(td.uInput('\n Enter Number of Lots > '))
				if dNewPID['Lots__c'] == '':
					dNewPID['Lots__c'] = 0
				if dNewPID['Lots__c'] == 0:
					break
				if dNewPID['Lots__c'] > dOldPID['Lots__c']:
					td.warningMsg('\n Total Split Lots cannot exceed Total Existing Lots...try again...\n')
					continue
				if dNewPID['Lots__c'] > 0:
					dOldPID['Lots__c'] = dOldPID['Lots__c'] - dNewPID['Lots__c']
					break
	
		# Deal Name
		if row['Subdivision__c'] != '':
			dNewPID['Name'] = '{0} {1} Ac'.format(row['Subdivision__c'], dNewPID['Acres__c'])
		if row['Location__c'] != '':
			dNewPID['Name'] = '{0} {1} Ac'.format(row['Location__c'], dNewPID['Acres__c'])
		elif row['Owner_Entity__c'] != '':
			dNewPID['Name'] = '{0} {1} Ac'.format(row['Owner_Entity__r']['Name'][:60], dNewPID['Acres__c'])
		else:
			dNewPID['Name'] = '{0} {1} Ac'.format(row['AccountId__r']['Name'], dNewPID['Acres__c'])

		print(dNewPID['Name'])

		# Check for long version county names
		if 'Maricopa' in dNewPID['County__c']:
			dNewPID['County__c'] = 'Maricopa'
		elif 'Pinal' in dNewPID['County__c']:
			dNewPID['County__c'] = 'Pinal'

		del dNewPID['Id']
		del dNewPID['AccountId__r']
		del dNewPID['CreatedById']
		del dNewPID['CreatedDate']
		del dNewPID['Digitized__c']
		del dNewPID['LastModifiedDate']
		del dNewPID['LastModifiedById']
		del dNewPID['Lot_Price_Rollup__c']
		del dNewPID['Market__c']
		del dNewPID['Owner_Entity__r']
		del dNewPID['PID__c']
		del dNewPID['Price_Per_Acre__c']
		del dNewPID['Report_Acres__c']
		del dNewPID['Verified_By__c']
		del dNewPID['Verified_On__c']
		del dNewPID['Verified__c']
	
		newDID = tf_create_3(service, dNewPID)
		upResults = tf_update_3(service, dOldPID)

		# Open new PID in TerraForce
		webs.open_pid_did(service, newDID)

		# Get new PID from TerraForce
		# TerraForce Query
		fields = 'default'
		wc = f"Id = '{newDID}'"
		results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
				
		return results[0]['PID__c'], results[0]['Id']

def setOPR_SentToTodaysDate(service):
	today = td.today_date()
	# fields = 'Id'
	# wc = "OPR_Sent__c = 1965-01-11 and Sale_Date__c < 2017-11-01"
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "OPR_Sent__c = 1965-01-11 and Sale_Date__c < 2017-11-01"
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	for row in results:
		upDict = row
		upDict['OPR_Sent__c'] = today
		up_results = tf_update_3(service, upDict)

# Returns the OPR Sent Date
def getOPR_SentDate(service, DID):
	# fields = 'Id, OPR_Sent__c'
	# wc = "Id = '{0}'".format(DID)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	return results[0]['OPR_Sent__c']

def formatVizzdaVPNParcels(service, apn):
	if 'VPN' in apn:
		fixedAPN = apn.replace('VPN-', '').replace('_', '')
		print(fixedAPN)
		if fixedAPN[:1].isdigit():
			fixedAPN = fixedAPN.replace('-', '')
			fixedAPN = '{0}-{1}-{2} (por)'.format(fixedAPN[:3], fixedAPN[3:5], fixedAPN[5:])
	return apn

def selectAgentForCommission(service, DID, state):

	dd = {}
	dd['DealID__c'] = DID
	dd['type'] = 'lda_Commission__c'
	dd['Agent_Order__c '] = 1

	while 1:
		lao.banner('Select Agent for Commission')

		lStateAgent = []
		# Get Agent dict
		dAgent = dicts.get_staff_dict(dict_type='full')


		for agent in dAgent:
			if state in dAgent[agent]['State'] and dAgent[agent]['Roll'] == 'Agent' and dAgent[agent]['LAO'] == 'Yes':
				agentInfo = '{0:20} {1}'.format(agent, dAgent[agent]['Office'])
				lStateAgent.append(agentInfo)

		for i in range(0, len(lStateAgent)):
			print('{0:2}) {1}'.format(i, lStateAgent[i]))
		ui = td.uInput('\n Select Agent or [Enter] to quit > ')
		if ui == '':
			break
		print

		print(lStateAgent[int(ui)])
		selectedAgent = lStateAgent[int(ui)]

		for row in dAgent:
			if row in selectedAgent:
				dd['Agent__c'] = dAgent[row]['Id']
				break
		results = tf_create_3(service, dd)

def marketsUnsentOPRs(service):
	import datetime
	lao.banner('Markets with OPRs to Send')
	# fields = 'County__c, Market__c, StageName__c, OPR_Sent__c'
	# wc = "OPR_Sent__c = 1965-01-11 or OPR_Sent__c = 1964-09-11"
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "OPR_Sent__c = 1965-01-11 or OPR_Sent__c = 1964-09-11"
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	lMarket = []
	lao.getCounties('CountysMarket')
	print
	for row in results:
		comps = '{0} Comps'.format(row['Market__c'])
		listings = '{0} Listings'.format(row['Market__c'])
		if comps in lMarket or listings in lMarket:
			continue
		else:
			if row['OPR_Sent__c'] == datetime.date(1965, 1, 11):
				comps = '{0} Comps'.format(row['Market__c'])
				lMarket.append(comps)
				print(comps)
				print
			elif row['OPR_Sent__c'] == datetime.date(1964, 9, 11):
				listings = '{0} Listings'.format(row['Market__c'])
				lMarket.append(listings)
				print(listings)
				print

		# print(row['StageName__c'])
		# print(row['OPR_Sent__c'])

def openTFPID(service, PID):
	# from webs import open_chrome
	# TerraForce Query
	fields = 'default'
	wc = "PID__c = '{0}'".format(PID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	
	if results == []:
		return 'None'
	DID = results[0]['Id']
	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))

	return DID

def addLeadParcel(service, DID):
	# fields = 'Id, PID__c, Lead_Parcel__c, Parcels__c'
	# wc = "Id = '{0}'".format(DID)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	for row in results:
		dd = row
		PID = dd['PID__c']
		if dd['Parcels__c'] != '':
			if '\n' in dd['Parcels__c']:
				parSplit = dd['Parcels__c'].split('\n')
			elif ', ' in dd['Parcels__c']:
				parSplit = dd['Parcels__c'].split(', ')
			else:
				parSplit = dd['Parcels__c'].split(',')
			dd['Lead_Parcel__c'] = parSplit[0]
	try:
		tf_update_3(service, dd, 'Deal add Lead Parcel')
	except:
		pass
	try:
		return dd['Lead_Parcel__c']
	except KeyError:
		td.warningMsg('\n PID {0} is missing Parcels.  Fix and try again.'.format(PID))
		openTFPID(service, PID)
		exit('\n Terminating program...')

def getContactInfo(service, CID):
	# fields = 'Id, '
	# wc = ""
	# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = ""
	results = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

# Select all Deal Fields by DID
def get_All_Deal_Info(service, didpid):
	# Get DID if PID
	if isDIDorPID(didpid) == 'PID':
		DID = getDIDfromPID(service, didpid)
	else:
		DID = didpid
	fields = "Owner_Entity__r.BillingCountry, Owner_Entity__r.BillingPostalCode, Owner_Entity__r.BillingState, Owner_Entity__r.BillingCity, Owner_Entity__r.BillingStreet, Owner_Entity__r.Phone, Owner_Entity__r.Name, Owner_Entity__r.Id, Owner_Entity__c, AccountId__r.MiddleName__c, AccountId__r.PersonEmail, AccountId__r.BillingCountry, AccountId__r.BillingPostalCode, AccountId__r.BillingState, AccountId__r.BillingCity, AccountId__r.BillingStreet, AccountId__r.Phone, AccountId__r.FirstName, AccountId__r.LastName, AccountId__r.Name, AccountId__r.Id, AccountId__c, Beneficiary__r.Id, Beneficiary__r.Name,  Loan_Amount__c, Zoning__c, Type__c, Zipcode__c, Submarket__c, Subdivision__c, StageName__c, State__c, Source__c, Source_ID__c, Sale_Price__c, Sale_Date__c, Recorded_Instrument_Number__c, PID__c, Parcels__c, Name, Market__c, Lots__c, Lot_Type__c, Lot_Description__c, Longitude__c, Location__c, Legal_Description__c, Lead_Parcel__c, Latitude__c, Keyword_Group__c, Id,General_Plan__c, Description__c, County__c, Country__c, Classification__c, City__c, Buyer_Acting_As__c, Acres__c, (Select Id, Name, Buyer_Entity__c, Buyer_Entity__r.Name, Buyer_Entity__r.BillingCountry, Buyer_Entity__r.BillingPostalCode, Buyer_Entity__r.BillingState, Buyer_Entity__r.BillingCity, Buyer_Entity__r.BillingStreet, Buyer_Entity__r.Phone,  Buyer_Entity__r.Id, Buyer__c, Buyer__r.MiddleName__c, Buyer__r.PersonEmail, Buyer__r.BillingCountry, Buyer__r.BillingPostalCode, Buyer__r.BillingState, Buyer__r.BillingCity, Buyer__r.BillingStreet, Buyer__r.Phone, Buyer__r.FirstName, Buyer__r.LastName, Buyer__r.Name, Buyer__r.Id, Offer_Date__c, Offer_Price__c, Offer_Status__c From Offers__r WHERE Offer_Status__c = 'Accepted'), (Select Id, StageName__c From Opportunities__r)"
	wc = "Id = '{}'".format(DID)
	results = querySF(service, fields, wc)
	return results[0]

def updateAccountInfo(service, AID, street, zipcode, phone, email):
	dUp = {}
	dUp['type'] = 'Account'
	dUp['Id'] = AID
	if street != '':
		street = td.titlecase_street(street)
		dUp['BillingStreet'] = street
	if zipcode != '':
		dUp['BillingPostalCode'] = zipcode
		dUp['BillingCity'], dUp['BillingCity'], dUp['BillingCountry'] = lao.zipCodeFindCityStateCountry(zipcode)
	if phone != '':
		formattedPhone = td.phoneFormat(phone)
		if formattedPhone != 'Skip':
			dUp['Phone'] = formattedPhone
	if email != '':
		dUp['PersonEmail'] = email
	tf_update_3(service, dUp, 'Update Account Info')

def createdByResearch(service, DealID='None', PropertyID='None', user='None', updateDeal=False):
	if user == 'None':
		user = lao.getUserName()
	# The LAO Employee USER ID not the contact ID
	# Get the Researcher's USER ID from LAO Staff spreadsheet
	dStaff = dicts.get_staff_dict()
	for staff in dStaff:
		if dStaff[staff]['Email'] == user:
			UserID = dStaff[staff]['UserID']
	if updateDeal:
		if DealID == 'None' and PropertyID != 'None':
			DealID = getDIDfromPID(service, PropertyID)
		dd = {}
		dd['type'] = 'lda_Opportunity__c'
		dd['Id'] = DealID
		dd['OwnerId'] = UserID
		tf_update_3(service, dd)
	else:
		return UserID

def getTFAccounts(service, dictType='None'):
	if dictType == 'Emails':
		# TerraForce Query
		fields = 'default'
		wc = "PersonEmail <> ''"
		results = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
		return results

def removeRequestResearchFlag(service, DID):
	upd = {}
	upd['type'] = 'lda_Opportunity__c'
	upd['Id'] = DID
	upd['Research_Flag__c'] = False
	tf_update_3(service, upd, 'Remove Research Request Flag')

def stageNameToCancelled(service, DID):
	upd = {}
	upd['type'] = 'lda_Opportunity__c'
	upd['Id'] = DID
	upd['StageName__c'] = 'Cancelled'
	tf_update_3(service, upd, 'Stage Name to Canceled')

def getTFFields(tffields):

	# Universal Fields
	if tffields == 'universal':
		tffields = 'Id, PID__c, Recorded_Instrument_Number__c, Lot_Type__c, Classification__c, Market__c, County__c, Submarket__c, Subdivision__c, Location__c, City__c, Buyer_Acting_As__c, Report_Acres__c, Price_Per_Acre__c, Weighted_Avg_Price_Per_FF__c, Sale_Price__c, Lots__c, Price_Per_Lot__c, Lot_Price_Rollup__c, Sale_Date__c, Description__c, Latitude__c, Longitude__c, StageName__c, List_Date__c, Listing_Expiration_Date__c, List_Price__c'
	# Record Creators
	elif tffields == 'recordcreators':
		tffields = 'Owner.Name, CreatedBy.Name, CreatedDate, LastModifiedBy.Name, LastModifiedDate'
	# Seller Info
	elif tffields == 'sellerfields':
		tffields = 'AccountId__r.Id, AccountId__r.Name, AccountId__r.Phone, AccountId__r.PersonMobilePhone, AccountId__r.PersonEmail, AccountId__r.Top100__c, Owner_Entity__r.Id, Owner_Entity__r.Name'
	# Add Buyer Info
	elif tffields == 'offerfields':
		tffields = "(SELECT Buyer__r.Id, Buyer__r.Name,  Buyer__r.Phone,  Buyer__r.PersonMobilePhone,  Buyer__r.PersonEmail,  Buyer__r.Top100__c, Buyer_Entity__r.Id, Buyer_Entity__r.Name FROM Offers__r where Offer_Status__c = 'Accepted')"
	# Loan Fields
	elif tffields == 'loanfields':
		tffields = 'Beneficiary__r.Id, Beneficiary__r.Name,  Loan_Amount__c'
	# Lot Details Info
	elif tffields == 'lotdetailfields':
		tffields = "(Select Name, Lot_Count__c, Lot_Width__c, Lot_Depth__c, Price_per_parcel__c, Price_per_Front_Foot__c, Price_per_Lot__c From Lot_Details__r WHERE RecordTypeID != '012a0000001ZSieAAG')"
	# Commission Fields
	elif tffields == 'commissionfields':
		tffields = "(SELECT Agent__c, Agent__r.Name, LAO_Agent__c, Agent__r.Phone, Agent__r.PersonEmail, Agent__r.Company__r.Name FROM Commissions__r)"
	# Source Info
	elif tffields == 'sourcefields':
		tffields = 'lda_Opportunity__c.Source__c, lda_Opportunity__c.Source_ID__c'
	return tffields

# Change from Deal Type to Reserach
def changeDealTypeToReserach(service, DID):
	# Create Update Dict
	ud = {}
	ud['Id'] = DID
	ud['type'] = 'lda_Opportunity__c'
	# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	ud['RecordTypeID'] = '012a0000001ZSS8AAO'  # Research
	tf_update_3(service, ud, 'Deal Type to Research')

def getStageName(service, PID):
	# Check if Stage Name is Closed
	# fields = 'Id, PID__c, StageName__c'
	# wc = "PID__c = '{0}'".format(PID)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	wc = "PID__c = '{0}'".format(PID)
	results = tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	return results[0]['StageName__c']

# Get Agent's Contacts from TF that have an email
def getAgentContactsDict(service, agentName, withEmail=False):
	print('\n Getting TF contacts...')
	# fields = 'Id, Category__c, CC_ID__c, Company__c, Company__r.Name, Description, Name, FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone, PersonMobilePhone, PersonHomePhone, PersonEmail, PersonHasOptedOutOfEmail, PersonTitle'
	# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)

	# TerraForce Query
	fields = 'default'
	if withEmail:
		wc = "PersonEmail <> '' AND (Category__c INCLUDES ('{0}') OR Top100__c INCLUDES ('{0}'))".format(agentName)
	else:
		wc = "Category__c INCLUDES ('{0}') OR Top100__c INCLUDES ('{0}')".format(agentName)
	results = tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

	return results

# Safe Deal Delete
def safe_deal_delete(service, PID):
	lao.print_function_name('bb def safe_deal_delete')
	import mpy
	import webbrowser

	user, initials = lao.getUserName(initials=True)
		# Check if LAO Deal
	wd = tfRecordInfo(service, PID)

	# Check if Deal is okay to delete.
	# Deal must be StageName Lead with no payments or offers
	hardStop = False
	if wd == 'None':
		td.warningMsg('\n TF Record/PID {0} not found.\n\n Canceling delete...'.format(PID))
		hardStop = True
	if wd['AccReceivableExists']:
		td.warningMsg('\n WARNING: Cannot delete Deals with Payments')
		hardStop = True
	if wd['CommissonExists']:
		td.warningMsg('\n WARNING: LAO Agent in Commissions!')
		hardStop = True
	if wd['OfferExists']:
		td.warningMsg('\n WARNING: Cannot delete Deals with Offer(s)!')
		hardStop = True
	if hardStop:
		td.warningMsg('\n WARNING: This is a hard stop.  Canceling delete...')
		td.uInput('\n Continue... ')
		return
	
	cancelDelete = False
	if wd['OkToEdit'] is False:
		td.warningMsg('\n WARNING: Colosed Deal. Cannot delete Deals that are not Leads!')
		cancelDelete = True
	if wd['PackageExists']:
		td.warningMsg('\n WARNING: Recent Package exists!')
		td.warningMsg('\n If LAO Package do not delete TF Record')
		print('\n  1) LAO Package exists')
		print('\n  2) No LAO Package')
		print('\n 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			td.warningMsg('\n Canceling delete...')
			cancelDelete = True
		elif ui == '2':
			print('\n Continuing with delete...')
		elif ui == '00':
			exit('\n Terminating program...')
	if wd['RequestExists']:
		td.warningMsg('\n WARNING: Recent Request exists!')
		td.warningMsg('\n Check Request for Package or Map Request')
		print('\n  1) Request Package or Map exists')
		print('\n  2) Request is for the creation of the Deal')
		print('\n 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			td.warningMsg('\n Canceling delete...')
			cancelDelete = True
		elif ui == '2':
			print('\n Continuing with delete...')
		elif ui == '00':
			exit('\n Terminating program...')
	if wd['NoteExists']:
		td.warningMsg('\n WARNING: Recent Note(s) exists!')
		td.warningMsg('\n Check Notes')
		print('\n  1) Important Note exists')
		print('\n  2) Notes are not important')
		print('\n 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			td.warningMsg('\n Canceling delete...')
			cancelDelete = True
		elif ui == '2':
			print('\n Continuing with delete...')
		elif ui == '00':
			exit('\n Terminating program...')

	DID = wd['Id']

	if cancelDelete:
		if user == 'blandis' or user == 'avidela' or user == 'lkane':
			webbrowser.open('https://landadvisors.my.salesforce.com/{0}'.format(DID))
			lao.click()
			td.warningMsg('\n You are authorized to override warnings....')
			ui = (td.uInput('\n Type [OK] to delete > ')).upper()
			if ui == 'OK':
				td.uInput('\n Continuing with the delete...')
			else:
				td.warningMsg('\n Canceling delete...')
				td.uInput('\n Continue... ')
				return
		else:
			td.warningMsg('\n You are not authorized to delete this Deal.')
			td.warningMsg('\n Contact Bill or Alec for assistance...')
			td.warningMsg('\n Canceling delete...')
			td.uInput('\n Continue... ')
			return

	td.banner('M1 Safe Delete PID v01')

	# print(' Click Zoom to {0} button in ArcMap.\n'.format(PID))

	dUpdate = dicts.get_blank_deal_update_dict(DID)

	if wd['Lot_Type__c'] == 'Initial Lot Option':
		ui = '1'
	else:
		print(' Select Description or type your own...\n\n 1) Initial Lot Option\n 2) Built Out\n 3) Merge with same owner of adjacent PID\n 4) Duplicate\n 5) Subdivided Multiple Times\n 6) Government Land or Flood Control\n 7) Agent requested delete\n 8) Test PID\n 9) Missing Polygon Duplicate\n\n  10) Delete Polygon NOT not TF Record\n 11) Cancel Delete')
		ui = td.uInput('\n Select or Type Description > ')
	if ui == '1':
		while 1:
			ui = td.uInput('\n Record is an Initial Lot Option...Is it Built Out [0/1] > ')
			if ui == '1':
				dUpdate['Lot_Type__c'] = 'Lot Option Built Out'
				rectype = 'Initial Lot Option'
				break
			elif ui == '0':
				td.warningMsg('\n Canceling delete...')
				td.uInput('\n Continue...')
				break
			else:
				td.warningMsg('\n Invalid response...')
				td.uInput('\n Try again...')
	elif ui == '2':
		dUpdate['Description__c'] = 'Deleted built out. {0}'.format(initials)
		rectype = 'Built Out'
	elif ui == '3':
		dUpdate['Description__c'] = 'Deleted merged with same owner of adjacent PID. {0}'.format(initials)
		rectype = 'Merged'
	elif ui == '4':
		ui = (td.uInput('\n Enter PID that is {0} duplicate > '.format(PID))).upper()
		dUpdate['Description__c'] = 'Deleted duplicate record of {0}. {1}'.format(ui, initials)
		rectype = 'Duplicate'
	elif ui == '5':
		dUpdate['Description__c'] = 'PID has been subdivided beyond all recognition and no longer has a unified ownership. {0}'.format(initials)
		rectype = 'Subdivided'
	elif ui == '6':
		dUpdate['Description__c'] = 'Deleted government land or flood control. {0}'.format(initials)
		rectype = 'Subdivided'
	elif ui == '7':
		dUpdate['Description__c'] = 'Deleted per agent request. {0}'.format(initials)
		rectype = 'Subdivided'
	elif ui == '8':
		dUpdate['Description__c'] = 'Test PID. {0}'.format(initials)
		rectype = 'Subdivided'
	elif ui == '8':
		dUpdate['Description__c'] = 'Missing Polygon Duplicate. {0}'.format(initials)
		rectype = 'Duplicate'
	elif ui == '10':
		# Skip deleting TF Record, only deleting OwnerIndex PID
		ui = td.uInput('\n Only delete the OwnerIndex polygon [0/1/00] > ')
		if ui == '0':
			td.warningMsg('\n Canceling polygon delete...')
			td.uInput('\n Continue...')
			return
		elif ui == '1':
			oi_result = mpy.oi_delete_poly(PID)
		elif ui == '00':
			exit('\n Terminating program...')
	elif ui == '10':
		td.warningMsg('\n Canceling delete...')
		td.uInput('\n Continue...')
		return
	else:
		dUpdate['Description__c'] = '{0} {1}'.format(ui, initials)
		rectype = 'Custom'

	# Confirm Delete
	while 1:
		td.banner('Confirm Delete')

		ui = td.uInput('\n Delete {0}? [0/1/00] > '.format(PID))
		if ui == '00':
			td.warningMsg('\n Delete canceled...')
			exit('\n Terminating program...')
		elif ui == '1':
			results = tf_update_3(service, dUpdate)
			if rectype != 'Initial Lot Option':
				results = tf_delete_3(service, DID, 'lda_Opportunity__c')
				print('\n TF record {0} deleted...'.format(PID))
				# Delete the polygon
				if mpy.get_OID_from_PID(PID) is not None:
					oi_result = mpy.oi_delete_poly(PID)
			else:
				print('\n Record {0} Initial Lot Option changed to Lot Option Built Out...'.format(PID))
			break
		elif ui == '0':
			td.warningMsg('\n Delete canceled...')
			td.uInput('\n Continue...')
			break
		else:
			td.warningMsg('\n Invalid input...try again...')

# User to add number of Lots
def add_lots_details(dTF):
	# Return 0 Lots if Cover Land or Raw Acreage
	if dTF['Lot_Type__c'] == 'Cover Land' or dTF['Lot_Type__c'] == 'Raw Acreage':
		dTF['Lots__c'] = 0
		return dTF

	deals_details_menu(dTF, 'Lots', 'Lots')

	# Ask user to enter number of Lots
	ui = td.uInput('\n Enter TOTAL Number of Lots [00] > ')
	if ui == '00':
		exit('\n Terminating program...')
	if ui == '' or int(ui) < 1:
		dTF['Lots__c'] = 0
	else:
		dTF['Lots__c'] = int(ui)

	return dTF

# User to select from List
def select_from_list(dTF, tf_field):
	start_over = False
	# Assign variable list(s) and title
	if tf_field == 'Classification__c':
		title = 'Classification'
		lList = dicts.get_classification_list()

	elif tf_field == 'Lot_Type__c':
		# Lot Type is always Raw Acreage if not Residential or Apartment
		lList = dicts.get_non_raw_acreage_classifications_list()
		if dTF['Classification__c'] not in lList:
			dTF['Lot_Type__c'] = 'Raw Acreage'
			return dTF,start_over
		# Not Raw Acreage so get Lot Type list
		title = 'Lot Type'
		lList = dicts.get_lot_type_list()

	elif tf_field == 'Development_Status__c':
		# Development Status only appies to Multifamily
		lList = dicts.get_multifamily_classifications_list()
		if dTF['Classification__c'] not in lList:
			dTF['Development_Status__c'] = 'None'
			return dTF, start_over
		# Is Multifamily so get Development Status list
		title = 'Development Status'
		lList = dicts.get_development_status_list()

	elif tf_field == 'Buyer_Acting_As__c':
		title = 'Buyer Acting As'
		lList = dicts.get_buyer_acting_as_list()
	
	# Ask user to select from list
	lenList = len(lList)
	while 1:
		deals_details_menu(dTF, title, dTF['StageName__c'])

		print(f'\n    - {title} -\n')
		# Print list
		for i in range(1, lenList):
			print(' {0:>2}) {1}'.format(i, lList[i]))
		if tf_field != 'Buyer_Acting_As__c':
			td.colorText(f'\n 88) Keep Current {title}', 'GREEN')
		print('\n 99) Start Over')
		print(' 00) Quit')
		ui = td.uInput(f'\n Select {title} > ').upper()
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '99':
			start_over = True
			return dTF, start_over
		elif ui == '88':
			return dTF, start_over
		try:
			if ui == '' or int(ui) < 1 or int(ui) > (lenList - 1):
				td.warningMsg(' Invalid input...try again...')
				lao.sleep(1)
				continue
		except ValueError:
			td.warningMsg(' Invalid input...try again...')
			lao.sleep(1)
			continue
		# Assign selected value to field
		dTF[tf_field] = lList[(int(ui))]
		print(f'\n {title} Selected')
		td.colorText('\n {0}'.format(lList[(int(ui))]), 'ORANGE')
		if dTF[tf_field] == 'Commercial':
			dTF[tf_field] = 'Office;Retail'
		elif dTF[tf_field] == 'Leave Blank':
			dTF[tf_field] = 'None'
		return dTF, start_over

def deals_details_menu(dTF, title, stage_name='Closed'):
	td.banner(f'Select {title}')
	# Print the values of all fields
	if title == 'Classification':
		td.colorText('\n Classification:     {0}'.format(dTF['Classification__c']), 'YELLOW')
	else:
		print('\n Classification:     {0}'.format(dTF['Classification__c']))

	if title == 'Lot Type':
		td.colorText(' Lot Type:           {0}'.format(dTF['Lot_Type__c']), 'YELLOW')
	else:
		print(' Lot Type:           {0}'.format(dTF['Lot_Type__c']))
	# Print Lots if not Cover Land or Raw Acreage
	if dTF['Lot_Type__c'] != 'Cover Land' and dTF['Lot_Type__c'] != 'Raw Acreage':
		if title == 'Lots':
			td.colorText(' Lots:               {0}'.format(dTF['Lots__c']), 'YELLOW')
		else:
			print(' Lots:               {0}'.format(dTF['Lots__c']))
	# Development Status only applies to Multifamily
	lList = dicts.get_multifamily_classifications_list()
	if dTF['Classification__c'] in lList:
		if title == 'Development Status':
			td.colorText(' Development Status:  {0}'.format(dTF['Development_Status__c']), 'YELLOW')
		else:
			print(' Development Status: {0}'.format(dTF['Development_Status__c']))
	
	# Buyer Acting As only applies to Closed Sales
	if 'Closed' in stage_name:
		if title == 'Buyer Acting As':
			td.colorText(' Buyer Acting As:    {0}'.format(dTF['Buyer_Acting_As__c']), 'YELLOW')
		else:
			print(' Buyer Acting As:    {0}'.format(dTF['Buyer_Acting_As__c']))

	# Print Zoning if Classification
	if title == 'Classification':
		td.colorText('\n Zoning: {0}'.format(dTF['Zoning__c']), 'ORANGE')

# Populate Deal Details
# Add Classification, Lot Type, Lots, Development Status and Buyer Acting As
def populate_deal_details(dTF, is_sale_record):

	while 1:
		# dTF['Classification__c'] = 'None'
		# dTF['Lot_Type__c'] = 'None'
		# dTF['Lots__c'] = 0
		# dTF['Development_Status__c'] = 'None'
		# dTF['Buyer_Acting_As__c'] = 'None'
		# Add Classification
		dTF, start_over = select_from_list(dTF, 'Classification__c')
		if start_over:
			continue
		# Add Lot Type
		dTF, start_over  = select_from_list(dTF, 'Lot_Type__c')
		if start_over:
			continue
		# dTF = select_lot_type(dTF)
		# Add number of Lots
		dTF  = add_lots_details(dTF)
		# Add Development Status
		dTF, start_over  = select_from_list(dTF, 'Development_Status__c')
		if start_over:
			continue
		# Add Buyer Acting As
		# if 'Closed' in dTF['StageName__c']:
		if is_sale_record:
			dTF, start_over  = select_from_list(dTF, 'Buyer_Acting_As__c')
			if start_over:
				continue

		# User to confirm selections
		if is_sale_record:
			deals_details_menu(dTF, 'Confirm Deal Details', 'Closed')
		else:
			deals_details_menu(dTF, 'Confirm Deal Details', dTF['StageName__c'])

		print('\n Confirm Deal Details')
		print('  1) Confirm')
		print('  0) Start Over')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			break
		else:
			td.warningMsg('\n Start over...')
			lao.sleep(1)
	return dTF

# OLD TF FUNCTIONS NOT USED **************************************************************
# SelesForce Query
def sfquery(service, query_string):
	td.warningMsg('\n bb.sfquery() no longer valid.\n\n Use bb.tf_query_3()')
	print(query_string)
	exit('\n Terminating program...')

# Login to LAO SalesForce account, Returns service
def sfLogin():  #SalesForceService
	td.warningMsg('\n bb.sfLogin() no longer valid.\n\n Use fun_login.TerraForce()')
	exit('\n Terminating program...')

# SalesForce Update record object
def sfupdate(service, object_dict, msg='Record', quit_if_fail=True, verbose_it=True):
	td.warningMsg('\n bb.sfupdate() no longer valid.\n\n Use bb.tf_update_3()')
	pprint(object_dict)
	exit('\n Terminating program...')

def querySF(service, fields, wc):
	# SalesForce Update record object
	td.warningMsg('\n bb.querySF() no longer valid.\n\n Use bb.tf_query_3()')
	exit('\n Terminating program...')

# Old Create TF record not used any more
def sfcreate(service, object_dict, msg='Record'):
	td.warningMsg('\n Function bb.sfcreate replaced by bb.tf_create_3')
	exit('\n Terminating program...')

# SalesForce Delete record object
def sfdelete(service, record_id):
	td.warningMsg('\n Function bb.sfdelete replaced by bb.tf_delete_3')
	print(record_id)
	exit('\n Terminating program...')
	# results = service.delete(record_id)
	# return results

def load_contacts_from_cache():
	"""Load contacts from cache file if it exists and was created today."""
	cache_file = 'C:/TEMP/tf_contacts_cache.pkl'
	
	# Check if cache file exists
	if not os.path.exists(cache_file):
		print(f' Warning: Contacts cache file not found: {cache_file}')
		return None
		
	# Check if file was created today
	file_timestamp = datetime.fromtimestamp(os.path.getmtime(cache_file))
	today = datetime.now()
	if file_timestamp.date() != today.date():
		print(f' Warning: Contacts cache file is outdated: {file_timestamp.date()}')
		return None
		
	try:
		with open(cache_file, 'rb') as f:
			print(f' Loading contacts from cache file ({file_timestamp})...')
			return pickle.load(f)
	except:
		return None

def save_contacts_to_cache(contacts):
    """Save contacts dictionary to cache file."""
    cache_file = 'C:/TEMP/tf_contacts_cache.pkl'
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(contacts, f)
    except Exception as e:
        print(f' Warning: Failed to save contacts cache: {str(e)}')

# Modified version of the original contacts loading code
def get_contacts_dict(service):
    """Get contacts either from cache or from Salesforce."""
    # Try to load from cache first
    cached_contacts = load_contacts_from_cache()
    if cached_contacts is not None:
        print(f'\n Using cached contacts from today ({len(cached_contacts)} records)...\n')
        return cached_contacts
        
    # If no valid cache, query Salesforce
    print('\n * Generating TF Account dictionary\n This takes a minute, please standby...\n')
    contacts = getTFAccounts(service, 'Emails')
    contacts_dict = {contact['PersonEmail']: contact for contact in contacts}
    
    # Save to cache for future use
    save_contacts_to_cache(contacts_dict)
    
    print(f' Found {len(contacts_dict)} contacts with email addresses...')
    return contacts_dict

