# Generate OPR Mailers

# Libraries
import aws
import bb
import dicts
import django
from django.conf import settings
import emailer
import fun_login
import fun_text_date as td
import lao
# from amp import isOwnerIndexPIDExist, createOPRMap
import mpy
import os
import sys
import smtplib
import webbrowser
# import datetime
from webbrowser import open as openbrowser
import webs
from pprint import pprint
# import pprint as pp

# Set up Django templates
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [r'F:/Research Department/Code/RP3/templates']
	}
]
settings.configure(TEMPLATES=TEMPLATES)
from django.template import Template, Context
django.setup()

td.banner('OPR Mail PY3 v06', colorama=True)
td.console_title('OPR Mailer v06')
# Login to TerraForce
service = fun_login.TerraForce()

# get Agent Dict
dStaff = dicts.get_staff_dict(dict_type='full')

def selectMarket(includeUSA = False):
	lMarkets = lao.getCounties('Market')
	count = 1
	td.banner('Select LAO Market')
	for market in lMarkets:
		print(' {0:2}) {1}'.format(count, market))
		count += 1

	# Include USA for GV National Report
	if includeUSA:
		print(' {0:2}) {1}'.format(count, 'USA'))
	print(' 00) Quit')
	ui = td.uInput('\n Select Market > ')
	# Quit program
	if ui == '00':
		exit(' Terminating program...')
	# GV Whale Sales report which covers multiple USA markets
	elif int(ui) == count:
		return 'USA'
	ui = int(ui) - 1
	market = lMarkets[ui]
	return market

def send_to():
	lao.print_function_name('script send_to')
	oprType = 'NONE'
	lLAOOffices = dicts.get_staff_dict('marketfulllist')
	
	while 1:
		td.banner('OPR Mailer PY3 v06', colorama=True)
		
		if oprType == 'NONE':
			msg = \
				' ---------------------------------------\n' \
				'  🛠️  UTILITIES\n' \
				' ---------------------------------------\n' \
				'  [C] Create OPR Map\n' \
				'  [M] Upload Maps to FTP\n' \
				'\n' \
				' ---------------------------------------\n' \
				'  📊 OPR TYPES\n' \
				' ---------------------------------------\n' \
				'  [1] Comps (Comparable Sales)\n' \
				'  [2] Competitor Listings\n' \
				'  [3] Planning & Zoning Updates\n' \
				'  [4] Requests, Ownerships or Debt\n' \
				'  [5] Axio Pipeline\n' \
				'  [6] PIR OPR\n' \
				'  [7] PIR AI\n' \
				'\n' \
				' [00] Quit\n'

			print(msg)
			SENDLIST = td.uInput('\n Select > ')
			
		elif oprType == 'P&Z':
			msg = \
				'  PLANNING & ZONING OPTIONS\n\n' \
				' ---------------------------------------\n' \
				'  🔍 QUALITY CONTROL\n' \
				' ---------------------------------------\n' \
				'  [11] QC Report\n' \
				'  [22] Test OPRs\n' \
				'  [R] Return to Main Menu\n' \
				'\n' \
				' ---------------------------------------\n' \
				'  📤 SEND TO ADVISORS\n' \
				'  Type market name exactly as shown:\n' \
				'\n' \
				'  • Scottsdale\n' \
				' ---------------------------------------\n' \
				'\n' \
				'  [00] Quit\n'

			print(msg)
			SENDLIST = td.uInput('\n Type market or select option > ')

		else:
			# Display current OPR type with color
			td.colorText(f'\n 📋 Current OPR Type: {oprType}\n', 'GREEN', colorama=True)

			# TESTING - Auto select market
			if oprType == 'PIR_OPR' or oprType == 'PIR_Comp':
				SENDLIST = '22'
			
			# END TESTING
			else:

				# Format office list in columns for better readability
				offices_formatted = []
				for i, office in enumerate(lLAOOffices):
					offices_formatted.append(f'  • {office}')
				
				offices_display = '\n'.join(offices_formatted)
				
				msg = \
					f' {oprType.upper()} OPTIONS\n' \
					' ---------------------------------------\n' \
					'  🔍 QUALITY CONTROL\n' \
					' ---------------------------------------\n' \
					'  [11] QC Report\n' \
					'  [22] Test OPRs\n' \
					'  [R] Return to Main Menu\n' \
					'\n' \
					' ---------------------------------------\n' \
					'  📤 SEND TO ADVISORS & EAs\n' \
					'  Type market name exactly as shown below:\n' \
					' ---------------------------------------\n' \
					f'{offices_display}\n' \
					'\n' \
					'  [00] Quit\n' \

				print(msg)
				SENDLIST = td.uInput('\n Select market or option > ')

		# Process user input
		# Upper case single letter entries
		if len(SENDLIST) == 1:
			SENDLIST = SENDLIST.upper()
			
		if SENDLIST == 'M':
			print('\n 📤 Uploading maps to FTP server...')
			# Copies jpeg map files created 'today' from C:\TEMP to LAO FTP site
			aws.sync_opr_maps_comp_listings_folders_to_s3(delete_files=False)
			print(' ✅ Upload complete!')
			td.uInput('\n Press Enter to continue...')
			
		elif SENDLIST == 'C':
			print('\n 🗺️  Creating OPR Map...')
			OPRPID = td.uInput('\n Enter PID: ')
			mpy.make_opr_map_api(service, OPRPID)
			print(' ✅ Map creation complete!')
			td.uInput('\n Press Enter to continue...')
			
		elif SENDLIST == 'T' or SENDLIST == '22':
			SENDLIST = 'T'
			td.banner('OPR Mailer PY3 v06', colorama=True)
			print(' 🧪 Test mode selected - OPRs will be sent to you only')
			recipients_to = ['{0} LAO <{1}@landadvisors.com>'.format(userName.upper(), userName)]
			recipients_cc = []
			sender = 'OPR TEST <research@landadvisors.com>'
			return recipients_to, recipients_cc, SENDLIST, sender, oprType
		
		elif SENDLIST == 'Q' or SENDLIST == '11':
			SENDLIST = 'Q'
			td.banner('OPR Mailer PY3 v06', colorama=True)
			print(' 🔍 Quality Control mode selected')
			sender, recipients_to, recipients_cc = '', [], []
			return recipients_to, recipients_cc, SENDLIST, sender, oprType
			
		elif SENDLIST == 'R':
			oprType = 'NONE'
			
		elif SENDLIST == '00':
			sys.exit('\n Program terminated...')
			
		elif SENDLIST == '1':
			oprType = 'Comp'
			print(f'\n ✅ Selected: {oprType} OPRs')
			
		elif SENDLIST == '2':
			oprType = 'Listing'
			print(f'\n ✅ Selected: {oprType} OPRs')
			
		elif SENDLIST == '3':
			oprType = 'P&Z'
			print(f'\n ✅ Selected: {oprType} OPRs')
			
		elif SENDLIST == '4':
			oprType = 'Request'
			print(f'\n ✅ Selected: {oprType} OPRs')
			
		elif SENDLIST == '5':
			oprType = 'AXIOPIPE'
			print(f'\n ✅ Selected: {oprType} OPRs')

		elif SENDLIST == '6':
			oprType = 'PIR_OPR'
			print(f'\n ✅ Selected: {oprType} OPRs')
		
		elif SENDLIST == '7':
			oprType = 'PIR_Comp'
			print(f'\n ✅ Selected: {oprType} OPRs')

		elif SENDLIST in lLAOOffices:
			print(f'\n 📤 Preparing to send {oprType} OPRs to {SENDLIST} market...')
			recipients_to, recipients_cc = recipientComps(SENDLIST)
			sender = '{0} {1} <research@landadvisors.com>'.format(SENDLIST, oprType)
			return recipients_to, recipients_cc, SENDLIST, sender, oprType
			
		else:
			print('\n ❌ Invalid selection. Please try again.')
			td.warningMsg(' "{0}" is not a valid option.'.format(SENDLIST), colorama=True)
			td.uInput('\n Enter to continue...')

def recipientComps(sendListMarket):
	lao.print_function_name('script recipientComps')
	lDoNotSendRolls = ['Marketing', 'Management', 'Capital', 'Events', 'DA', 'IT', 'Escrow', 'Mapping']
	recipients_to, recipients_cc = [], []
	for staff in dStaff:
		if dStaff[staff]['Roll'] in lDoNotSendRolls or dStaff[staff]['LAO'] == 'No':
			continue
		# Create list of to recipients
		elif dStaff[staff]['Roll'] == 'Research':
			nameEmail = '{0} <{1}@landadvisors.com>'.format(staff, dStaff[staff]['Email'])
			recipients_cc.append(nameEmail)
		elif sendListMarket in dStaff[staff]['Markets']:
			nameEmail = '{0} <{1}@landadvisors.com>'.format(staff, dStaff[staff]['Email'])
			recipients_to.append(nameEmail)
		

	# Return recipient
	return recipients_to, recipients_cc

def create_query_string(service, sendlist, oprType):
	lao.print_function_name('script create_query_string')
	
	while 1:
		# P&Z is only Scottsdale
		if oprType == 'P&Z':
			# fields = "{0}, (SELECT Title, Body FROM Notes WHERE Title LIKE 'Vizzda%')".format(fields)
			wc = "OPR_Sent__c = 1965-01-11 AND (County__c LIKE '%Maricopa%' or County__c LIKE '%Pinal%') AND Sale_Date__c = NULL AND StageName__c != 'Top 100' "
			market = 'Scottsdale'
		# TESTING - Auto select market
		elif oprType == 'PIR_OPR' or oprType == 'PIR_Comp':
			market = 'Scottsdale'
		# END TESTING
		else:
			# Select the market
			wc, market = lao.getCountiesInMarketWhereClause()

			if oprType == 'Listing': # Listing uses different OPR Sent date
				wc = "{0} AND OPR_Sent__c = 1964-09-11".format(wc)
			elif oprType == 'AXIOPIPE': # Listing uses different OPR Sent date
				wc = "{0} AND OPR_Sent__c = 1929-10-02".format(wc)
			elif oprType == 'Request':
				wc = "{0} AND OPR_Sent__c = 1994-10-01".format(wc)
			else:
				wc = "{0} AND OPR_Sent__c = 1965-01-11".format(wc)

			if oprType == 'Request':
				wc = "{0} AND (StageName__c = 'Top 100' or StageName__c = 'Lead')".format(wc)
			elif oprType == 'Comp':
				wc = "{0} AND StageName__c LIKE '%Closed%'".format(wc)

		# Select Records to Send
		while 1:
			# TEMP TEST test CODE
			if oprType == 'PIR_OPR' or oprType == 'PIR_Comp':
				ui = 'AZPinal258934'
				# ui = 'FLSarasota295605'
			else:
				print('\n\n SEND...\n\n')
				print(' [Enter] to Send')
				print('  [Type] a PID')
				print('    [00] Quit')
				ui = td.uInput('\n Select > ').upper()
			if ui == '' or ui == 'A':
				# wc = "{0}(OPR_Sent__c = 1965-01-11)".format(wc)
				break
			elif len(ui) > 3:
				ui = ui.strip()
				wc = "PID__c = '{0}'".format(ui)
				break
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				td.warningMsg('\n Invalid entry, try again...', colorama=True)
		
		
		# print('here1')
		# pprint(wc)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		
		# TerraForce Query
		fields = 'default'
		# wc = "soql_statement"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

		if results == []:
			td.warningMsg('\n No results found, try again...', colorama=True)
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
		return results, market

def get_universal_fields(row):
	lao.print_function_name('script get_universal_fields')
	dHTML['Weighted_Avg_Price_Per_FF__c'] = row['Weighted_Avg_Price_Per_FF__c']
	if dHTML['Weighted_Avg_Price_Per_FF__c'] != 'None':
		# dHTML['Weighted_Avg_Price_Per_FF__c'] = td.currency_format_from_number(dHTML['Weighted_Avg_Price_Per_FF__c'])
		dHTML['Weighted_Avg_Price_Per_FF__c'] = td.currency_format_from_number(dHTML['Weighted_Avg_Price_Per_FF__c'])
	else:
		dHTML['Weighted_Avg_Price_Per_FF__c'] = 'None'
	if row['Description__c'] == 'None':
		dHTML['Description__c'] = 'None'
	else:
		dHTML['Description__c'] = lao.charactersToASCII(row['Description__c'], charCase='None')
	if row['Subdivision__c'] == 'None':
		dHTML['Subdivision__c'] = 'None'
	else:
		dHTML['Subdivision__c'] = (row['Subdivision__c']).title()
	dHTML['City__c'] = (row['City__c']).title()
	dHTML['Id'] = row['Id']
	dHTML['Name'] = row['Name']
	dHTML['Encumbrance_Rating__c '] = ''
	dHTML['Latitude__c'] = row['Latitude__c']
	dHTML['Property_Comps_Table'] = False
	dHTML['Location__c'] = lao.charactersToASCII(row['Location__c'], charCase='TITLE')
	dHTML['Longitude__c'] = row['Longitude__c']
	# Check for Lead Parcel
	dHTML['Lot_Table'] = '' # HTML table of lot details
	dHTML['Lot_Width__c'] = 0
	dHTML['Lead_Parcel__c'] = (row['Lead_Parcel__c']).upper()
	dHTML['Lead_Parcel__c'] = dHTML['Lead_Parcel__c'].strip()
	if dHTML['Lead_Parcel__c'] == 'NONE' or dHTML['Lead_Parcel__c'] == '':
		dHTML['Lead_Parcel__c'] = bb.addLeadParcel(service, dHTML['Id'])
	dHTML['Lots__c'] = int(row['Lots__c'])
	dHTML['PID__c'] = row['PID__c']
	dHTML['Price_per_Lot__c'] = 0
	dHTML['Price_per_parcel__c'] = 0
	dHTML['Parcels__c'] = row['Parcels__c']
	# Truncate Parcels to 100 characters for email
	if len(dHTML['Parcels__c']) > 100:
		dHTML['Parcels__c'] = f'{dHTML['Parcels__c'][:100]}...'
	dHTML['Recorded_Instrument_Number__c '] = row['Recorded_Instrument_Number__c']
	dHTML['Submarket__c'] = (row['Submarket__c']).title()
	dHTML['StageName__c'] = row['StageName__c']
	if dHTML['StageName__c'] == 'Escrow':
		dHTML['ESCROW'] = True
	else:
		dHTML['ESCROW'] = False
	dHTML['State__c'] = (row['State__c'])
	dHTML['Lot_Type__c'] = (row['Lot_Type__c']).strip()
	dHTML['Type__c'] = row['Type__c']
	dHTML['Zipcode__c'] = row['Zipcode__c']
	dHTML['Zoning__c'] = row['Zoning__c']
	if dHTML['Zoning__c'] == '':
		dHTML['Zoning__c'] = 'NOT AVAILABLE'
	print('\n PID: {0}'.format(dHTML['PID__c']))

def make_opr_map(PID):
	# Check if the OPR map exists on aws and create it if not
	if aws.aws_file_exists(PID, extention='jpg', verbose=False) is False:
		oiPIDexists = mpy.make_opr_map_api(service, PID)

def get_acres(row):
	lao.print_function_name('script get_acres')
	dHTML['Acres__c'] = f"{float(row['Acres__c'] or 0):,.2f}"
	if dHTML['Acres__c'] == 0:
		dHTML['Acres__c'] = 'N/A'
		if row['Lots__c'] == 0 and row['Lot_Count_Rollup__c'] == 0:
			url = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['Id'])
			webbrowser.open(url)
			print('{0} has zero (0) Acres.  Please add acres.\n'.format(dHTML['DNM']))
			sys.exit('Terminating program...')

def get_classification(row):
	lao.print_function_name('script get_classification')
	# Convert Classification to upper case
	dHTML['Classification__c'] = row['Classification__c'].split(';')
	
	# Check for Classification	
	if dHTML['Classification__c'] == []:
		td.warningMsg('\n This PID does not have a Classification...', colorama=True)
		webs.openTFDID(row['Id'])
		exit(' Program terminated.')

	else:
		if len(dHTML['Classification__c']) == 1:
			dHTML['Classification__c'] = dHTML['Classification__c'][0].title()
		elif len(dHTML['Classification__c']) == 2 and 'Office' in dHTML['Classification__c'] and 'Retail' in dHTML['Classification__c']:
			dHTML['Classification__c'] = 'Commercial'
		elif len(dHTML['Classification__c']) == 3 and 'Office' in dHTML['Classification__c'] and 'Retail' in dHTML['Classification__c'] and 'Industrial' in dHTML['Classification__c']:
			dHTML['Classification__c'] = 'Industrial/Commercial'
		elif len(dHTML['Classification__c']) > 2:
			if 'Residential' in dHTML['Classification__c']:
				dHTML['Classification__c'] = 'Residential'
			elif 'Apartment Traditional' in dHTML['Classification__c'] and ('Office' in dHTML['Classification__c'] or 'Retail' in dHTML['Classification__c']):
				dHTML['Classification__c'] = 'Mixed Use'
			else:
				dHTML['Classification__c'] = dHTML['Classification__c'][0]
		else:
			dHTML['Classification__c'] = dHTML['Classification__c'][0]

def get_development_status(row):
	lao.print_function_name('script get_development_status')
	if row['Development_Status__c'] == '':
		dHTML['DEVSTAT'] = 'None'
	else:
		dHTML['DEVSTAT'] = row['Development_Status__c']

def get_county(row):
	lao.print_function_name('script get_county')
	dHTML['County__c'] = (row['County__c']).title()
	if 'Maricopa' in dHTML['County__c']:
		dHTML['County__c'] = 'Maricopa'
	elif 'Pinal' in dHTML['County__c']:
		dHTML['County__c'] = 'Pinal'

def get_source(row):
	lao.print_function_name('script get_source')
	dHTML['SOURCE'] = (row['Source__c'])
	if dHTML['SOURCE'] == 'Vizzda':
		dHTML['SOURCELINK'] = 'https://www2.vizzda.com/detail/{0}'.format(row['Source_ID__c'])
	elif dHTML['SOURCE'] == 'RED News':
		# OLD dHTML['SOURCELINK'] = 'https://www.redailycomps.com/REDC/Comp.asp?ID={0}&NoComment='.format(row['Source_ID__c'])
		dHTML['SOURCELINK'] = 'https://realestatedaily-news.com/displaycomp/?ID={0}&NoComment='.format(row['Source_ID__c'])
	elif dHTML['SOURCE'] == 'Reonomy':
		dHTML['SOURCELINK'] = row['Source_ID__c']
	elif dHTML['SOURCE'] == 'CREXi' and row['Source_ID__c'] != '':
		dHTML['SOURCELINK'] = row['Source_ID__c']
	elif dHTML['SOURCE'] == 'Loopnet' and row['Source_ID__c'] != '':
		dHTML['SOURCE'] = 'LOOPNET'
		dHTML['SOURCELINK'] = row['Source_ID__c']
	else:
		dHTML['SOURCELINK'] = ''

def lao_activity(PID):
	lao.print_function_name('script lao_activity')

	# Get Agent Dict of TF Ids
	dAgent_name = dicts.get_staff_dict('tfid')

	# TerraForce Query
	fields = 'default'
	wc = f"PID__c = '{PID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)


	dHTML['StageName__c'] = results[0]['StageName__c']
	dCommissions = results[0]['Commissions__r']
	dHTML['AGENTNAMES'] = ''
	dHTML['LISTAGENTID'] = ''
	dHTML['LISTAGENTNAME'] = ''
	dHTML['LISTAGENTPHONE'] = ''
	dHTML['LISTAGENTPERSONEMAIL'] = ''
	dHTML['LAOACT'] = 0

	if dCommissions == 'None':
		dHTML['AGENTNAMES'] = 'None'
	else:
		dCommissions = dCommissions['records']

		# Cycle through listing agents
		for agent in dCommissions:
			# LAO Agents
			if agent['LAO_Agent__c'] == 1:
				dHTML['LAOACT'] = 1
				agentid = (agent['Agent__c'])[:-3]
				name = dAgent_name.get(agentid)# .replace('_', ' ')
				# Skip if non-LAO agent
				try:
					name = name.replace('.', '')
				except AttributeError:
					continue
				if name != 'None' and name != None:
					dHTML['AGENTNAMES'] = '{0}, {1}'.format(dHTML['AGENTNAMES'], name)
			# Competitor Agents
			else:
				dHTML['LISTAGENTID'] = agent['Agent__c']# ['Id']
				dHTML['LISTAGENTNAME'] = agent['Agent__r']['Name']
				dHTML['LISTAGENTPHONE'] = agent['Agent__r']['Phone']
				dHTML['LISTAGENTEMAIL'] = agent['Agent__r']['PersonEmail']
				if agent['Agent__r']['Company__r'] == 'None':
					dHTML['LISTAGENTCOMPANY'] = ''
				else:
					dHTML['LISTAGENTCOMPANY'] = agent['Agent__r']['Company__r']['Name']
				dHTML['LISTAGENTURL'] = 'https://landadvisors.my.salesforce.com/%s' % dHTML['LISTAGENTID']

		# Remove initial blank or none name from agent list
		dHTML['AGENTNAMES'] = dHTML['AGENTNAMES'][2:]

	# Remove single offers on non-lao deals with no activity
	if dHTML['AGENTNAMES'] == 'None':
		dHTML['LAOACT'] = 0
	# Exclude agents in the OPR for deals that may have LAO agents but are not LAO sales
	elif dHTML['StageName__c'] == 'Closed Lost':
		dHTML['LAOACT'] = 0

def get_comp_fields(row, recipients_to):
	lao.print_function_name('script get_comp_fields')
	dHTML['Buyer_Acting_As__c'] = (row['Buyer_Acting_As__c'])
	dHTML['Encumbrance_Rating__c '] = (row['Encumbrance_Rating__c'])
	dHTML['Sale_Date__c'] = row['Sale_Date__c']
	dHTML['Sale_Date__c'] = td.date_engine(dHTML['Sale_Date__c'], outformat='opr', informat='TF')

	if row['Sale_Price__c'] == 10000:
		dHTML['Sale_Price__c'] = 10000
		dHTML['PPA'] = 10000
		dHTML['PPAraw'] = 10000
		dHTML['PRCNUM'] = 10000
	else:
		dHTML['Sale_Price__c'] = row['Sale_Price__c']
		dHTML['PPA'] = float(dHTML['Sale_Price__c']) / float(dHTML['Acres__c'])
		dHTML['PPAraw'] = dHTML['PPA']
		dHTML['PPA'] = '$' + '{:,.0f}'.format(dHTML['PPA'])
		dHTML['PRCNUM'] = dHTML['Sale_Price__c']
		# Caclulate Price per Sq Foot
		sq_ft = float(dHTML['Acres__c']) * 43560
		dHTML['PPSQFT'] = float(dHTML['Sale_Price__c']) / sq_ft
		dHTML['PPSQFTraw'] = dHTML['PPSQFT']
		dHTML['PPSQFT'] = '$' + '{:,.2f}'.format(dHTML['PPSQFT'])

	# Apartment/Assisted Living Unit Fields
	if (dHTML['Classification__c'] == 'Apartment' or dHTML['Classification__c'] == 'Apartment Traditional' or  'Assisted Living' in dHTML['Classification__c']) and dHTML['Lots__c'] > 0:
		# dHTML['Lot_Type__c'] = 'Apartment'
		dHTML['PPU'] = dHTML['Sale_Price__c'] / dHTML['Lots__c']
		dHTML['PPU'] = '$' + '{:,.0f}'.format(dHTML['PPU'])
		dHTML['MTF'] = True
	elif dHTML['Lot_Type__c'] == 'Raw Acreage':
		dHTML['Lot_Type__c'] = 'Raw Acreage'
		dHTML['MFT'] = False
	else:
		# dHTML['Lot_Type__c'] = 'Residential'
		dHTML['MFT'] = False

	# Add GV to Whale Sales outside of Scottsdale
	if SENDLIST != 'Q' and SENDLIST != 'T':
		if dHTML['Sale_Price__c'] >= 15000000 and 'Greg Vogel <gvogel@landadvisors.com>' not in recipients_to:
			recipients_to.append('Greg Vogel <gvogel@landadvisors.com>')

	dHTML['Sale_Price__c'] = '$' + '{:,.0f}'.format(dHTML['Sale_Price__c'])

def get_request_fields():
	lao.print_function_name('script get_request_fields')
	dHTML['Sale_Date__c '] = 'None'
	dHTML['PNZ'] = 'None'
	# dHTML['Lot_Type__c'] = 'TOP100'

def get_pir_fields():
	lao.print_function_name('script get_pir_fields')
	dHTML['Sale_Date__c '] = 'None'
	dHTML['PNZ'] = 'None'
	# dHTML['Lot_Type__c'] = 'PIR'

def get_axio_pipeline_fields():
	lao.print_function_name('script get_axio_pipeline_fields')
	dHTML['Lot_Type__c'] = 'AXIOPIPE'
	dHTML['PNZ'] = 'None'

def get_pnz_fields(row):
	lao.print_function_name('script get_pnz_fields')
	
	
	dHTML['Lot_Type__c'] = 'P&Z'
	dHTML['PNZ'] = 'PNZ'
	dHTML['PNZAPPLICANTID'] = row['Zoning_Applicant__c']
	try:
		dHTML['PNZAPPLICANT'] = (row['Zoning_Applicant__r']['Name'])
	except TypeError:
		td.warningMsg(' Zoning Applicant field cannot be blank!', colorama=True)
		url = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['Id'])
		webbrowser.open(url)
		exit('\n Terminating Program...')
	dHTML['PNZAPPLICANTurl'] = 'https://landadvisors.my.salesforce.com/%s' % dHTML['PNZAPPLICANTID']
	# PNZCASE > Case_Plan__c
	dHTML['Case_Plan__c'] = row['Case_Plan__c']
	# PNZCITYPLANNER = 'None'
	# PNZCITYPLANNERID = City_Planner__c
	dHTML['City_Planner__c'] = row['City_Planner__c']
	if dHTML['City_Planner__c'] != '':
		# PNZCITYPLANNER = City_Planner__r_Name
		dHTML['City_Planner__r_Name'] = (row['City_Planner__r']['Name'])
	else:
		dHTML['City_Planner__r_Name'] = ''
	# PNZCITYPLANNERurl > City_Planner__c_url
	dHTML['City_Planner__c_url'] = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['City_Planner__c'])
	# PNZDES > P_Z_Description__c
	dHTML['P_Z_Description__c'] = row['P_Z_Description__c'].replace('±', '+/-').replace('—', '-')
	# PNZDTE > P_Z_Last_Event_Date__c
	dHTML['P_Z_Last_Event_Date__c'] = row['P_Z_Last_Event_Date__c']
	dHTML['Sale_Date__c '] = 'None'
	dHTML['Buyer_Entity__r_Name'] = 'P&Z'
	dHTML['Buyer__r_Name'] = 'P&Z'
	dHTML['Buyer_Entity__r_Category__c'] = 'P&Z'
	dHTML['Buyer_Acting_As__c'] = 'P&Z'

def get_listing_fields(row):
	lao.print_function_name('script get_listing_fields')
	dHTML['Lot_Type__c'] = 'Listing'
	dHTML['LISTPRC'] = row['List_Price__c']
	if dHTML['LISTPRC'] == None or dHTML['LISTPRC'] == 10000:
		dHTML['LISTPRC'] = 'N/A'
		dHTML['LISTPPA'] = 'N/A'
	else:
		listPPA = dHTML['LISTPRC'] / dHTML['Acres__c']
		dHTML['LISTPPA'] = '${:,.0f}'.format(listPPA)
		dHTML['LISTPRC'] = '${:,.0f}'.format(dHTML['LISTPRC'])
	dHTML['LISTDTE'] = row['List_Date__c']
	dHTML['LISTEXPIRE'] = row['Listing_Expiration_Date__c']

	# Check if Package Exists
	# try:
		# code = urlopen('https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(dHTML['PID__c'])).code
	# brochure_exists = webs.awsFileExists('{0}_competitors_package.pdf'.format(dHTML['PID__c']))
	brochure_exists = aws.aws_file_exists(f'{dHTML['PID__c']}_competitors_package.pdf', extention='png', verbose=False)
	if brochure_exists:
		dHTML['BROCHUREURL'] = 'https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(dHTML['PID__c'])
	# except:
	else:
		dHTML['BROCHUREURL'] = False

# Build Comps Table
def get_property_comps_table(row, market):
	lao.print_function_name('script get_property_comps_table')

	# Calc min max coords
	dCords = mpy.get_bounding_box_coords(row['Latitude__c'], row['Longitude__c'], 10)
	minX = dCords['west_lon']
	maxX = dCords['east_lon']
	minY = dCords['south_lat']
	maxY = dCords['north_lat']

	# Set Date to last 3 years
	date = td.less_time_ago('MONTH', 36)

	# Bulid Classification include list
	lClassification = row['Classification__c'].split(';')
	# Add Office to Medical Classification list
	if 'Medical' in lClassification and 'Office' not in lClassification:
		lClassification.append('Office')
	cla = ', '.join(f"'{item}'" for item in lClassification)

	# Set min max acreage multipliers
	min_acre_nultiplyer = 0.5
	max_acre_nultiplyer = 1.5

	while 1:
		# Calc Acres
		minAc = row['Acres__c'] * min_acre_nultiplyer
		maxAC = row['Acres__c'] * max_acre_nultiplyer

		# TerraForce Query
		fields = 'default'
		wc = f"StageName__c LIKE '%Closed%' AND (Longitude__c > {minX} AND Longitude__c < {maxX}) AND (Latitude__c > {minY} AND Latitude__c < {maxY}) AND Sale_Date__c > {date} AND Acres__c > {minAc} AND Acres__c < {maxAC} AND (RecordTypeId = '012a0000001ZSS5AAO' OR RecordTypeId = '012a0000001ZSS8AAO') AND (Classification__c INCLUDES ({cla}))"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		
		# Check if any comps to list if not try a larger min max acreage once
		if max_acre_nultiplyer == 2:
			break
		if results == []:
			min_acre_nultiplyer = 0.25
			max_acre_nultiplyer = 2
		else:
			break

	# Build Comps Table
	if results == []:
		dHTML['Property_Comps_Table'] = False
		return
	compsTable = ''
	for pid in results:
		OPRLink = 'https://landadvisors.lightning.force.com/lightning/r/lda_Opportunity__c/{0}/view'.format(pid['Id'])
		L5Link = webs.get_L5_url('', market, pid['PID__c'])
		compPrice = '${:,.0f}'.format(pid['Sale_Price__c'])
		compPricePerAcre = '${:,.0f}'.format(pid['Price_Per_Acre__c'])
		compSaleDate = (td.date_engine(pid['Sale_Date__c'], outformat='opr', informat='TF'))
		compsRow = "<tr><td><a href='{0}'>{1}</a></td><td align='center'>{2}</td><td align='right'>{3}</td><td align='right'>{4}</td><td align='right'>{5}</td><td align='center'><a href='{6}'>L5</a></td></tr>".format(OPRLink, pid['PID__c'], compSaleDate,  compPrice, pid['Acres__c'], compPricePerAcre, L5Link)
		compsTable = '{0}{1}'.format(compsTable, compsRow)
	compsTable = compsTable.replace(' /', '/')
	dHTML['Property_Comps_Table'] = compsTable
	
	# print('here2')
	# pprint(dHTML['Property_Comps_Table'])
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

def get_seller_owner(row):
	lao.print_function_name('script get_seller_owner')
	# Get Seller/Owner Entity Name, Person and Category
	dHTML['slr_Owner_Entity__c'] = row['Owner_Entity__c']
	# No Owner Entity
	if dHTML['slr_Owner_Entity__c'] == 'None':
		dHTML['slr_Owner_Entity__r_Name'], dHTML['slr_Owner_Entity__r_url'], dHTML['slr_Owner_Entity__r_Category__c'], dHTML['slr_Owner_Entity__r_Phone'] = '', '', '', 'UNKNOWN'
	# Add Owner Entity
	else:
		dHTML['slr_Owner_Entity__r_url'] = 'https://client-dashboard.landadvisors.workers.dev/dashboard/{0}'.format(dHTML['slr_Owner_Entity__c'])
		dHTML['slr_Owner_Entity__r_Name'] = (row['Owner_Entity__r']['Name'])
		print(dHTML['slr_Owner_Entity__r_Name'])
		if row['Owner_Entity__r']['BillingStreet'] != '':
			dHTML['slr_Owner_Entity__r_BillingStreet'] = row['Owner_Entity__r']['BillingStreet'].title()
			dHTML['slr_Owner_Entity__r_BillingCity'] = row['Owner_Entity__r']['BillingCity'].title()
			dHTML['slr_Owner_Entity__r_BillingState'] = row['Owner_Entity__r']['BillingState']
			dHTML['slr_Owner_Entity__r_BillingPostalCode'] = row['Owner_Entity__r']['BillingPostalCode'][:5]
		else:
			dHTML['slr_Owner_Entity__r_BillingStreet'] = 'UNKNOWN'
		if row['Owner_Entity__r']['Phone'] != '':
			dHTML['slr_Owner_Entity__r_Phone'] = row['Owner_Entity__r']['Phone']
		else:
			dHTML['slr_Owner_Entity__r_Phone'] = 'UNKNOWN'
		if row['Owner_Entity__r']['Website'] != '':
			dHTML['slr_Owner_Entity__r_Website'] = row['Owner_Entity__r']['Website'].lower()
		else:
			dHTML['slr_Owner_Entity__r_Website'] = 'UNKNOWN'

	# No Person Account
	if row['AccountId__r'] == 'None':
		dHTML['slr_AccountId__r_Name'], dHTML['slr_AccountId__c_url'], dHTML['SPRT100'], dHTML['SPRT100url'], dHTML['SPRphn'], dHTML['SPRemail'], dHTML['SPRcity'], dHTML['SPRstate'] = '', '', '', '', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN'
	# Add Person Account
	else:
		dHTML['slr_AccountId__r_Name'] = (row['AccountId__r']['Name']).title()
		# SPRurl > AccountId__c_url
		dHTML['slr_AccountId__c_url'] = 'https://client-dashboard.landadvisors.workers.dev/dashboard/{0}'.format(row['AccountId__c'])
		# Check if Top 100
		dHTML['SPRT100url'] = 'https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}'.format(row['AccountId__c'])

		if row['AccountId__r']['PersonMobilePhone'] != '':
			# SPRphn > slr_AccountId__r_PersonMobilePhone
			dHTML['slr_AccountId__r_PersonMobilePhone'] = row['AccountId__r']['PersonMobilePhone']
		elif row['AccountId__r']['Phone'] != '':
			# SPRphn > slr_AccountId__r_Phone
			dHTML['slr_AccountId__r_Phone'] = row['AccountId__r']['Phone']
		else:
			dHTML['slr_AccountId__r_Phone'] = 'UNKNOWN'

		if row['AccountId__r']['PersonEmail'] != '':
			# SPRemail > slr_AccountId__r_PersonEmail
			dHTML['slr_AccountId__r_PersonEmail'] = row['AccountId__r']['PersonEmail']
		else:
			dHTML['slr_AccountId__r_PersonEmail'] = 'UNKNOWN'

		# Add Top 100 link
		if row['AccountId__r']['Top100__c'] == 'None':
			# SPRT100 > slr_AccountId__r_Top100
			dHTML['slr_AccountId__r_Top100'] = 'MAKE MVP'
		else:
			str_top100_agents = row['AccountId__r']['Top100__c'].replace(';', ', ')
			dHTML['slr_AccountId__r_Name'] = '{0} ({1})'.format(dHTML['slr_AccountId__r_Name'], str_top100_agents)
			dHTML['slr_AccountId__r_Top100'] = 'EDIT MVP'

		# Add City & State
		if row['AccountId__r']['BillingCity'] != '':
			# SPRcity > slr_AccountId__r_BillingCity
			dHTML['slr_AccountId__r_BillingCity'] = row['AccountId__r']['BillingCity']
		else:
			dHTML['slr_AccountId__r_BillingCity'] = 'UNKNOWN'
		# SPRstate > slr_AccountId__r_BillingState
		if row['AccountId__r']['BillingState'] != '':
			dHTML['slr_AccountId__r_BillingState'] = row['AccountId__r']['BillingState']
		else:
			dHTML['slr_AccountId__r_BillingState'] = 'UNKNOWN'

	if dHTML['slr_Owner_Entity__c'] != 'None':
		dHTML['slr_Owner_Entity__r_Category__c'] = bb.chooseAccountCategory(service, dHTML['slr_Owner_Entity__c'])
		dHTML['slr_Owner_Entity__r_Category__c'] = dHTML['slr_Owner_Entity__r_Category__c'].title()
	else:
		# do not assign a person name to a business
		dHTML['slr_Owner_Entity__r_Name'] = ''

def get_buyer(row):
	lao.print_function_name('script get_buyer')

	# Check if Buyer Person exists and if not set BPR to Unknown
	if row['Offers__r']['records'][0]['Buyer__r'] == 'None':
		dHTML['Buyer__r_Name'] = ''
	else:
		dHTML['Buyer__r_Name'] = (row['Offers__r']['records'][0]['Buyer__r']['Name'])
		dHTML['Buyer__r_url'] = 'https://client-dashboard.landadvisors.workers.dev/dashboard/{0}'.format(row['Offers__r']['records'][0]['Buyer__r']['Id'])
		
		# Check Top 100
		if row['Offers__r']['records'][0]['Buyer__r']['Top100__c'] == 'None':
			dHTML['BPRT100'] = 'MAKE MVP'
		else:
			# Make Buyer Person Top100 link
			dHTML['BPRT100url'] = 'https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}'.format(row['Offers__r']['records'][0]['Buyer__r']['Id'])
			str_top100_agents = row['Offers__r']['records'][0]['Buyer__r']['Top100__c'].replace(';', ', ')
			dHTML['Buyer__r_Name'] = '{0} ({1})'.format(dHTML['Buyer__r_Name'], str_top100_agents)
			dHTML['BPRT100'] = 'EDIT MVP'
	
	# Check for Buyer Entity
	if row['Offers__r']['records'][0]['Buyer_Entity__r'] == 'None':
		dHTML['Buyer_Entity__r_Name'], dHTML['Buyer_Entity__r_Id'], dHTML['Buyer_Entity__r_url'], dHTML['Buyer_Entity__r_Category__c'] = '', '', '', ''
	else:
		# BTX > Buyer_Entity__r_Name
		dHTML['Buyer_Entity__r_Name'] = (row['Offers__r']['records'][0]['Buyer_Entity__r']['Name'])
		# BTXID > Buyer_Entity__r_Id
		dHTML['Buyer_Entity__r_Id'] = row['Offers__r']['records'][0]['Buyer_Entity__r']['Id']
		# BTXurl > Buyer_Entity__r_url
		dHTML['Buyer_Entity__r_url'] = 'https://client-dashboard.landadvisors.workers.dev/dashboard/{0}'.format(dHTML['Buyer_Entity__r_Id'])
		# BTXcat > Buyer_Entity__r_Category__c
		dHTML['Buyer_Entity__r_Category__c'] = bb.chooseAccountCategory(service, dHTML['Buyer_Entity__r_Id']).title()

def get_beneficiary(row):
	lao.print_function_name('script get_beneficiary')
	if row['Beneficiary__c'] != 'None':
		dHTML['Beneficiary__c_Name'] = (row['Beneficiary__r']['Name'])
		dHTML['Beneficiary__c_url'] = 'https://landadvisors.my.salesforce.com/{0}'.format(row['Beneficiary__c'])
	else:
		dHTML['Beneficiary__c_Name'] = False
	if row['Beneficiary_Contact__c'] != 'None':
		dHTML['Beneficiary_Contact__c_Name'] = (row['Beneficiary_Contact__r']['Name'])
		dHTML['Beneficiary_Contact__c_url'] = 'https://landadvisors.my.salesforce.com/{0}'.format(row['Beneficiary_Contact__c'])
	else:
		dHTML['Beneficiary_Contact__c_Name'] = False
	if row['Loan_Amount__c'] != 'None':
		dHTML['Loan_Amount__c'] = '$' + '{:,.0f}'.format(row['Loan_Amount__c'])
	dHTML['Loan_Date__c'] = row['Loan_Date__c']
	
	if row['Encumbrance_Rating__c'] == 'None':
		dHTML['Encumbrance_Rating__c'] = False
	else:
		dHTML['Encumbrance_Rating__c'] = row['Encumbrance_Rating__c']

def get_lot_details():
	lao.print_function_name('script get_lot_details')

	# TerraForce Query
	fields = 'default'
	wc = "Opportunity__c = '{0}' AND RecordTypeId = '012a0000001ZSiZAAW'".format(dHTML['Id'])
	lot_dict = bb.tf_query_3(service, rec_type='LotDetail', where_clause=wc, limit=None, fields=fields)

	dHTML['Price_Front_Foot_Float'] = 501  # Minimum price per front foot to trigger warning

	if 'Apartment' not in dHTML['Lot_Type__c']:
		if dHTML['Lot_Type__c'] == 'Platted and Engineered':
			# dHTML['Lot_Type__c'] = 'PIPE'
			dHTML['Add_Lot_Table'] = 'TRUE'  # Needed to generate the lot table
		elif dHTML['Lot_Type__c'] == 'Partially Improved':
			# dHTML['Lot_Type__c'] = 'PIPE'
			dHTML['Add_Lot_Table'] = 'TRUE'  # Needed to generate the lot table
		elif dHTML['Lot_Type__c'] == 'Initial Lot Option':
			# dHTML['Lot_Type__c'] = 'LOTS'
			dHTML['Add_Lot_Table'] = 'TRUE'  # Needed to generate the lot table
		else:
			# dHTML['Lot_Type__c'] = 'LOTS'
			dHTML['Add_Lot_Table'] = 'TRUE'  # Needed to generate the lot table
	dHTML['Price_per_parcel__c'] = 0
	dHTML['Num_Lot_Groups'] = 0  # Number of Lot Groups in Lot Details table
	dHTML['Total_Lots_All_Groups'] = 0  # Lot Count (total of groups)
	dHTML['Total_Front_Foot'] = 0
	dHTML['Lot_Table'] = ''  # HTML table of lot details
	dHTML['Lot_Width__c'] = ''
	dHTML['avg_front_foot'] = 0

	if lot_dict == []:
		return True
	
	for row in lot_dict:
		
		if row['Price_per_Lot__c'] == None:
			return False
		
		dHTML['Num_Lot_Groups'] += 1
		# dHTML['LAC'] = row['Acres__c']
		dHTML['LTCSINGLE'] = row['Lot_Count__c']
		dHTML['Total_Lots_All_Groups'] = dHTML['Total_Lots_All_Groups'] + int(dHTML['LTCSINGLE'])
		# Check for blank dimensions
		try:
			dHTML['Lot_Depth__c'] = int(row['Lot_Depth__c'])
		except TypeError:
			dHTML['Lot_Depth__c'] = None
		if dHTML['Lot_Depth__c'] == 0:
			dHTML['Lot_Depth__c'] = None
		if dHTML['Lot_Depth__c'] is None:
			dHTML['Lot_Depth__c'] = 'None'
			dHTML['Lot_Width__c'] = 'None'
			dHTML['price_per_front_foot'] = 'None'
			dHTML['avg_front_foot'] = 'None'
			dHTML['Price_Front_Foot_Float'] = 'None'
		else:
			dHTML['Lot_Width__c'] = int(row['Lot_Width__c'])
			dHTML['Total_Front_Foot'] = dHTML['Total_Front_Foot'] + (dHTML['Lot_Width__c'] * dHTML['LTCSINGLE'])
			# dHTML['avg_front_foot'] = dHTML['avg_front_foot'] + float(dHTML['price_per_front_foot'])
			if dHTML['Lot_Width__c'] == 0:
				dHTML['Price_Front_Foot_Float'] = 0
				dHTML['price_per_front_foot'] = 0
			else:
				if dHTML['StageName__c'] != 'Lead':
					dHTML['price_per_front_foot'] = row['Price_per_Front_Foot__c']
					dHTML['Price_Front_Foot_Float'] = float(dHTML['price_per_front_foot'])  #check if PFF is below $500 variable
					dHTML['price_per_front_foot'] = td.currency_format_from_number(dHTML['price_per_front_foot'])
				else:
					# dHTML['price_per_front_foot'] = 0
					if dHTML['price_per_front_foot'] != 0 and dHTML['price_per_front_foot'] != 'None':
						dHTML['avg_front_foot'] = dHTML['avg_front_foot'] + float(dHTML['Price_Front_Foot_Float'])

		dHTML['Price_per_Lot__c'] = row['Price_per_Lot__c']
		try:
			dHTML['Price_per_Lot__c'] = td.currency_format_from_number(dHTML['Price_per_Lot__c'])
		except TypeError:
			td.warningMsg('\n Lot Detail is missing Price.', colorama=True)
			sys.exit('\n Terminaiting program...continue...')
		dHTML['Price_per_parcel__c'] = row['Price_per_parcel__c']
		dHTML['Price_per_parcel__c'] = td.currency_format_from_number(dHTML['Price_per_parcel__c'])

		if dHTML['avg_front_foot'] == 'None':
			dHTML['TAG'] = "<tr><td>%d</td><td>%d</td><td>N/A</td><td>%s</td><td>%s</td><td>N/A</td></tr>" % (dHTML['Num_Lot_Groups'], dHTML['LTCSINGLE'], dHTML['Price_per_parcel__c'], dHTML['Price_per_Lot__c'])
		else:
			dHTML['TAG'] = "<tr><td align='center'>%d</td><td align='center'>%d</td><td align='center'>%s' x %s'</td><td align='right'>%s</td><td align='right'>%s</td><td align='right'>%s</td></tr>" % (dHTML['Num_Lot_Groups'], dHTML['LTCSINGLE'], dHTML['Lot_Width__c'], dHTML['Lot_Depth__c'], dHTML['Price_per_parcel__c'], dHTML['Price_per_Lot__c'], dHTML['price_per_front_foot'])
		dHTML['Lot_Table'] = dHTML['Lot_Table'] + dHTML['TAG']
	# Use Lot Details Count if not 0 rather than Lots__c
	if dHTML['Total_Lots_All_Groups'] != 0:
		dHTML['Lots__c'] = dHTML['Total_Lots_All_Groups']
	return True

def get_opr_title(oprType, recipients_to):
	lao.print_function_name('script get_opr_title')
	subCLA = dHTML['Classification__c'].title()
	subCTY = dHTML['City__c'].title()
	LANDTYPE = 'None'

	# MVP OPR Title
	if oprType == 'Request':
		if dHTML['Encumbrance_Rating__c']:
			dHTML['TITLE'] = 'Distressed: {0} Land in {1}'.format(subCLA, subCTY)
		else:
			dHTML['TITLE'] = 'Opportunity: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')
	# P&Z OPR Title
	elif oprType == 'P&Z':
		dHTML['TITLE'] = 'P&Z: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')
	# # PIR OPR Title
	# elif oprType == 'PIR_OPR' or oprType == 'PIR_Comp':
	# 	dHTML['TITLE'] = 'PIR: {0} Land in {1}'.format(subCLA, subCTY)
	# 	dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')
	# LISTING OPR Title
	elif oprType == 'Listing':
		if dHTML['LISTPRC'] == 'N/A':
			dHTML['TITLE'] = 'For Sale: {0} Land in {1}'.format(subCLA, subCTY)
		else:
			listPriceFloat = dHTML['LISTPRC'].replace('$', '').replace(',', '')
			listPriceFloat = float(listPriceFloat)
			if listPriceFloat == 10000:
				DOLLARS = 'None'
			elif listPriceFloat >= 1000000:
				DOLLARS = '$' + '{:,.1f}'.format(listPriceFloat / 1000000) + 'M'
			else:
				DOLLARS = '$' + '{:,.0f}'.format(listPriceFloat / 1000) + 'K'
			if DOLLARS == 'None':
				dHTML['TITLE'] = 'For Sale: {0} Land in {1}'.format(subCLA, subCTY)
			else:
				dHTML['TITLE'] = 'For Sale: {0} {1} Land in {2}'.format(DOLLARS, subCLA, subCTY)
			dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')
	elif oprType == 'AXIOPIPE':
		dHTML['TITLE'] = 'Axio Pipeline: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')

	elif dHTML['Classification__c'].title() == 'Apartment':
		LANDTYPE = 'Apartment'
	elif dHTML['Classification__c'].title() == 'Apartment Horizontal':
		LANDTYPE = 'Horizontal Apt'
	elif dHTML['Classification__c'].title() == 'Apartment Traditional':
		LANDTYPE = 'Traditional Apt'
	elif dHTML['Classification__c'].title() == 'High Density Assisted Living':
		LANDTYPE = 'High Density Assisted Living'
	elif dHTML['Classification__c'].title() == 'Commercial':
		LANDTYPE = 'Commercial'
	elif dHTML['Lot_Type__c'] == 'Raw Acreage':
		LANDTYPE = '{0} Acreage'.format(subCLA)
	elif dHTML['Lot_Type__c'] == 'Finished Lots':
		LANDTYPE = 'Finished Lot'
	elif dHTML['Lot_Type__c'] == 'Platted and Engineered':
		LANDTYPE = 'P&E Lot'
	elif dHTML['Lot_Type__c'] == 'Partially Improved':
		LANDTYPE = 'Partially Improved Lot'
	elif dHTML['Lot_Type__c'] == 'Rolling Lot Option':
		LANDTYPE = 'Rolling Lot Option'
	elif dHTML['Lot_Type__c'] == 'Initial Lot Option':
		LANDTYPE = 'Initial Lot Option'
	elif dHTML['Lot_Type__c'] == 'Covered Land':
		LANDTYPE = 'Covered Land'
	else:
		dHTML['LANDTYPE'] = subCLA

	if oprType == 'Comp' or oprType == 'PIR_Comp':
		if float(dHTML['PRCNUM']) == 10000:
			DOLLARS = 'None'
		elif float(dHTML['PRCNUM']) >= 1000000:
			DOLLARS = '$' + '{:,.1f}'.format(dHTML['PRCNUM'] / 1000000) + 'M'
		else:
			DOLLARS = '$' + '{:,.0f}'.format(dHTML['PRCNUM'] / 1000) + 'K'
		if DOLLARS == 'None':
			dHTML['TITLE'] = '{0} Project in {1}'.format(LANDTYPE, subCTY)
		else:
			dHTML['TITLE'] = '{0} {1} Project in {2}'.format(DOLLARS, LANDTYPE, subCTY)
		if dHTML['StageName__c'] == 'Closed' or dHTML['StageName__c'] == 'Escrow':
			dHTML['TITLE'] = 'LAO {0}'.format(dHTML['TITLE'])
			# Add GV & BR to LAO Deals
			if SENDLIST != 'Q' and SENDLIST != 'T':
				if 'Greg Vogel <gvogel@landadvisors.com>' not in recipients_to:
					recipients_to.append('Greg Vogel <gvogel@landadvisors.com>')
				if 'Brian Rosener <rrosener@landadvisors.com>' not in recipients_to:
					recipients_to.append('Brian Rosener <rrosener@landadvisors.com>')
		dHTML['TITLE'] = dHTML['TITLE'].replace('±', '+/-')

def get_links():
	lao.print_function_name('script get_links')
	# Set location of the OPR Map
	dHTML['MAP'] = 'https://request-server.s3.amazonaws.com/maps/{0}.jpg'.format(dHTML['PID__c'])
	# openbrowser(dHTML['MAP'])
	# dHTML['MAP'] = 'https://request-server.s3.amazonaws.com/maps/{0}.png'.format(dHTML['PID__c'])
	if 'MARICOPA' in dHTML['County__c']:
		dHTML['RDNLink'] = (dHTML['Recorded_Instrument_Number__c '][2:]).replace('-', '')
		dHTML['RDC'] = 'http://recorder.maricopa.gov/recdocdata/GetRecDataRecentDetail.aspx?rec=%s' % dHTML['RDNLink']
		dHTML['LPL'] = 'http://mcassessor.maricopa.gov/?s=%s' % dHTML['Lead_Parcel__c']
	elif 'PINAL' in dHTML['County__c']:
		dHTML['RDC'] = 'http://www.pinalcountyaz.gov/Recorder/Pages/DocumentSearch.aspx?fy=%s&fn=%s' % (dHTML['Recorded_Instrument_Number__c '][:4], dHTML['Recorded_Instrument_Number__c '][5:])
		dHTML['LPL'] = 'http://www.pinalcountyaz.gov/ASSESSOR/Pages/ParcelSearch.aspx'
	else:
		dHTML['RDC'] = ''
		dHTML['LPL'] = ''

	# L5 link
	# create L5 Market Name & ZoomTo&mapid==## dictionary
	dHTML['L5L'] = webs.get_L5_url(oprType, market, dHTML['PID__c'])

def get_html_template(oprType):
	lao.print_function_name('script get_html_template')
	# Get html template
	if oprType == 'Comp':
		return open(r'F:\Research Department\Code\RP3\templates\pir_comps_02.html', 'r').read()
	elif oprType == 'Listing':
		return open(r'F:\Research Department\Code\RP3\templates\opr_listing_01.html', 'r').read()
	elif oprType == 'P&Z':
		return open(r'F:\Research Department\Code\RP3\templates\opr_planning_zoning_04.html', 'r').read()
	elif oprType == 'Request':
		# return open(r'F:\Research Department\Code\RP3\templates\top_100_02.html',
					# 'r', encoding='utf-8').read()
		return open(r'F:\Research Department\Code\RP3\templates\pir_request_01.html', 'r', encoding='utf-8').read()
	elif oprType == 'OPRNOTIFICATION':
		return open(r'F:\Research Department\Code\RP3\templates\you_got_oprs.html',
					'r').read()
	elif oprType == 'AXIOPIPE':
		return open(r'F:\Research Department\Code\RP3\templates\opr_axio_pipe_01.html', 'r').read()
	elif oprType == 'PIR_OPR':
		return open(r'F:\Research Department\Code\RP3\templates\pir_opr_01.html', 'r', encoding='utf-8').read()
	# elif oprType == 'PIR_Comp':
	# 	return open(r'F:\Research Department\Code\RP3\templates\pir_ai_01.html', 'r', encoding='utf-8').read()
	elif oprType == 'PIR_Comp':
		return open(r'F:\Research Department\Code\RP3\templates\pir_comps_02.html', 'r', encoding='utf-8').read()

def get_recipient_request(names):
	lao.print_function_name('script get_recipient_request')
	recipients_to = ['Bill Landis <blandis@landadvisors.com>', 'Ethan Granger <egranger@landadvisors.com>', 'Alec Videla <avidela@landadvisors.com']
	names = names.split(', ')
	# Find Agents in Top 100 Commission list
	office = 'None'

	for name in names:
		for staff in dStaff:
			staff = staff.replace('.', '')
			if name == staff and dStaff[staff]['Roll'] != 'Research' and dStaff[staff]['LAO'] == 'Yes':
				skipIt = False
				for rec in recipients_to:
					if name in rec:
						skipIt = True
				if skipIt:
					continue
				nameEmail = '{0} <{1}@landadvisors.com>'.format(staff, dStaff[staff]['Email'])
				office = dStaff[staff]['Office']
				recipients_to.append(nameEmail)

	for name in names:
		print(name)
		if 'Bret Rinehart' in name or 'Ryan Semro' in name or 'Ryan ' in name:
			recipients_to.append('Kathleene Hansen <khansen@landadvisors.com>')
			return recipients_to
		elif 'Chad Russell' in name or 'Bobby Wuertz' in name or 'Dave Lords' in name or 'Kirk McCarville' in name or 'Michele Pino' in name or 'Mike Brinkley' in name or 'Mike Schwab' in name or 'Ben Heglie' in name:
			recipients_to.append('Sara Angorn <sangorn@landadvisors.com>')
			return recipients_to
		elif 'Greg Vogel' in name or 'Wesley Campbell' in name:
			recipients_to.append('Jennifer Bittner <jbittner@landadvisors.com>')
			return recipients_to
		elif 'Rick Bressan' in name:
			return recipients_to
	for staff in dStaff:
		if (dStaff[staff]['Office'] in office and dStaff[staff]['Roll'] == 'EA') or dStaff[staff]['Roll'] == 'Research':
			nameEmail = '{0} <{1}@landadvisors.com>'.format(staff, dStaff[staff]['Email'])
			recipients_to.append(nameEmail)
	return recipients_to

def build_opr_message(recipients_to, SENDLIST, sender, oprType, html):
	lao.print_function_name('script build_opr_message')
	# msg = MIMEMultipart('alternative')
	# msg['Subject'] = 'OPR: {0}'.format(dHTML['TITLE'])
	# msg['From'] = sender
	# msg['Date'] = formatdate(localtime=True)

	if oprType == 'Request' and SENDLIST.upper() != 'T':
		recipients_to = get_recipient_request(dHTML['AGENTNAMES'])

	# assign Template
	t = Template(html)
	c = Context(dHTML)
	html = t.render(c)

	subject = 'OPR: {0}'.format(dHTML['TITLE'])
	body = html
	sender_email = sender

	return subject, body, sender_email, recipients_to

# Add today's date to the Deal's OPR_Sent__c field
def mark_deal_as_sent(today):
	lao.print_function_name('script mark_deal_as_sent')
	dUp = {'type': 'lda_Opportunity__c', 'Id': dHTML['Id'], 'OPR_Sent__c': today}
	up_results = bb.tf_update_3(service, dUp)

def qc(oprType, market):
	lao.print_function_name('script qc')
	# QC Routines
	transLink = '<a href="https://landadvisors.my.salesforce.com/{0}"><font color="red">{1} -- {2}</font></a><br>'.format(dHTML['Id'], dHTML['Lot_Type__c'], dHTML['PID__c'])
	if dHTML['SOURCE'] == 'Vizzda':
		transLink = '{0}<a href="{1}"><font color="red">Vizzda Link</font></a><br>'.format(transLink, dHTML['SOURCELINK'])
	if market == 'Tucson' and dHTML['SOURCELINK'] != '':
		transLink = '{0}<a href="{1}"><font color="red">RED News Link</font></a><br>'.format(transLink, dHTML['SOURCELINK'])
	if dHTML['SOURCE'] == 'Reonomy':
		transLink = '{0}<a href="{1}"><font color="red">Reonomy Link</font></a><br>'.format(transLink,dHTML['SOURCELINK'])
	errorVar = transLink

	if dHTML['Lead_Parcel__c'] == '' or dHTML['Lead_Parcel__c'].upper() == 'NONE':
		errorVar = errorVar + 'Lead Parcel is Missing<br>'
	if dHTML['Parcels__c'] == '' or dHTML['Parcels__c'].upper() == 'NONE':
		errorVar = errorVar + 'Parcels are Missing<br>'
	if dHTML['Subdivision__c'] == '' and dHTML['Classification__c'] == '%RESIDENTIAL%':
		errorVar = errorVar + 'Missing Subdivision<br>'
	if 'Apartment' in dHTML['Classification__c'] and dHTML['Lots__c'] == 0 and dHTML['SOURCE'] != 'CREXI' and  dHTML['SOURCE'] != 'Costar' and dHTML['Lot_Type__c'] != 'Raw Acreage':
		errorVar = errorVar + 'Missing Number of Apt Units<br>'
	if 'DISTRESSED' in dHTML['Classification__c']:
		errorVar = errorVar + 'Classification is Distressed<br>'
	if 'ASSISTED LIVING' in dHTML['Classification__c'] and dHTML['Lots__c'] == 0 and dHTML['SOURCE'] != 'Costar':
		errorVar = errorVar + 'Missing Number of Assisted Living Units<br>'
	if dHTML['Location__c'] == dHTML['Subdivision__c'] and dHTML['Location__c'] != '':
		errorVar = errorVar + 'Location & Subdivision are the Same<br>'
	if dHTML['Longitude__c'] == '' or dHTML['Latitude__c'] == '':
		errorVar = errorVar + 'No Lon/Lat<br>'
	if dHTML['Lot_Type__c'] == 'Rolling Lot Option':
		errorVar = errorVar + 'Rolling Lot Option change to Initial Lot Option<br>'
	if dHTML['Lot_Type__c'] != 'Raw Acreage' and dHTML['Lots__c'] == 0:
		errorVar = errorVar + '{0} Missing Lot Details<br>'.format(dHTML['Lot_Type__c'])
	if oprType != 'Listing' and dHTML['Location__c'] == '':
		errorVar = errorVar + 'Missing Location<br>'
	if oprType == 'Listing' and dHTML['BROCHUREURL'] is False:
		if not dHTML['PID__c'][:2] == 'ID': # Skip Idaho
			errorVar = errorVar + 'Missing Listing Brochure<br>'
	if dHTML['City__c'] == '':
		errorVar = errorVar + 'Missing City<br>'
	if dHTML['Lot_Type__c'] == '':
		errorVar = errorVar + 'Missing Lot Type<br>'
	if dHTML['Acres__c'] == 'N/A' or dHTML['Acres__c'] == 0:
		errorVar = errorVar + 'Zero Acres<br>'
	if dHTML['Acres__c'] == 1:
		errorVar = errorVar + 'Acres = 1 Please confirm Acres<br>'
	if (dHTML['Zoning__c'] == 'None') and (dHTML['County__c'] == 'Maricopa'):
		errorVar = errorVar + '-- *** Caution Missing Zoning *** --<br>'
	if 'CITY' in dHTML['Zoning__c'] or 'TOWN' in dHTML['Zoning__c'] or 'Maricopa' in dHTML['Zoning__c']:
		errorVar = errorVar + '--- DO NOT EMAIL --- City or Town in Zoning --- DO NOT EMAIL ---<br>'
	if dHTML['slr_Owner_Entity__r_Category__c'] == '' and dHTML['slr_Owner_Entity__r_Name'] != '':
		errorVar = errorVar + '<a href="https://landadvisors.my.salesforce.com/%s"><font color="red">Seller Entity</font></a> missing Category<br>' % dHTML['slr_Owner_Entity__c']
	if dHTML['Classification__c'] == '' or dHTML['Classification__c'] == 'NONE':
		errorVar = errorVar + 'Missing Classification<br>'
	if 'Closed' in dHTML['StageName__c']:
		if 'AGRICULTURAL' in dHTML['Classification__c'] and dHTML['PPAraw'] > 40000:
			errorVar = errorVar + 'Agricultural land price is high<br>'
	if dHTML['Lot_Type__c'] != 'Raw Acreage':
		if dHTML['Lot_Type__c'] == 'PARCELS':
			errorVar = errorVar + 'Missing Lot Breakdown<br>'
		if dHTML['Subdivision__c'] == '':
			errorVar = errorVar + 'Missing Subdivision<br>'
	if dHTML['Lots__c'] != 0 and dHTML['Lot_Type__c'] == 'Raw Acreage':
		errorVar = errorVar + 'Number of Lots is NOT 0 and Lot Type is Raw Acreage<br>'
	lStates = ['AL', 'AZ', 'FL', 'GA', 'ID', 'KS', 'MO', 'NC', 'NM', 'NV', 'SC', 'TN', 'TX', 'UT']
	for state in lStates:
		if state in dHTML['Lead_Parcel__c']:
			errorVar = errorVar + 'Lead Parcel is a PID<br>'
			break

	if market == 'Scottsdale' or market == 'Tucson':
		if '&' in dHTML['Subdivision__c']:
			errorVar = errorVar + '"&" in Subdivision Name<br> Subdivision: ' + dHTML['Subdivision__c'] + '<br>'
		if '&' not in dHTML['Location__c'] and dHTML['Location__c'] != '':
			errorVar = errorVar + 'Bad Location Formating<br>'
		if dHTML['Submarket__c'] == '':
			errorVar = errorVar + 'Missing Submarket<br>'
		if dHTML['slr_AccountId__r_Name'] == '':
			errorVar = errorVar + '-- *** Caution Missing Owner/Seller Person *** --<br>'

	if oprType == 'Comp': # dHTML['PNZ'] != 'PNZ':
		if dHTML['Buyer_Acting_As__c'] == 'None':
			errorVar = errorVar + 'Missing Buyer Acting As<br>'
		if dHTML['Buyer_Entity__r_Category__c'] == '' and dHTML['Buyer_Entity__r_Name'] != '':
			errorVar = '{0}<a href="https://landadvisors.my.salesforce.com/{1}"><font color="red">Buyer Entity</font></a> missing Category<br>'.format(
				errorVar, dHTML['Buyer_Entity__r_Id'])
		if dHTML['Buyer__r_Name'] == '' and (market == 'Scottsdale' or market == 'Tucson'):
			errorVar = errorVar + '-- *** Caution Missing Buyer Person *** --<br>'
		try:
			if dHTML['Price_per_parcel__c'] == 0 and dHTML['Lot_Table'] != '':
				errorVar = errorVar + 'Missing Price Per Parcel<br>'
		except NameError:
			pass
		if dHTML['Buyer_Entity__r_Name'] == '' and dHTML['Buyer__r_Name'] == '':
			errorVar = errorVar + 'Missing Buyer Entity<br>'
		if dHTML['Buyer_Entity__r_Name'] == dHTML['slr_Owner_Entity__r_Name'] and dHTML['Buyer_Entity__r_Name'] != '':
			errorVar = errorVar + 'Buyer Entity & Owner/Seller Entity are the same<br>'
		if dHTML['Buyer__r_Name'] == dHTML['slr_AccountId__r_Name'] and dHTML['Buyer__r_Name'] != '':
			errorVar = errorVar + 'Buyer Person & Owner/Seller Person are the same<br>'
		try:
			if dHTML['Lot_Width__c'] != '' and dHTML['Lot_Width__c'] != 0 and dHTML['Lot_Width__c'] != None:
				if dHTML['Price_Front_Foot_Float'] < 500 and dHTML['Lot_Type__c'] == 'LOTS' and dHTML['Lot_Width__c'] < 100:
					errorVar = errorVar + 'Price per Front Foot is Low<br>PFF = ' + dHTML['price_per_front_foot'] + '<br>'
				if dHTML['Lot_Width__c'] < 30 and dHTML['Lot_Width__c'] > 100 and market == 'Scottsdale':
					errorVar = errorVar + 'Odd Lot Width (<30 or >100)<br>PFF = ' + dHTML['price_per_front_foot'] + '<br>'
				if dHTML['Lot_Width__c'] != '':
					if dHTML['Price_Front_Foot_Float'] > 1700 and dHTML['Lot_Width__c'] >= 35 and oprType != 'P&Z':  # dHTML['PNZ'] != 'PNZ':
						errorVar = errorVar + 'Price per Front Foot is High<br>PFF = ' + dHTML['price_per_front_foot'] + '<br>'
					if dHTML['Lot_Type__c'] == 'Platted and Engineered' and dHTML[
						'Price_Front_Foot_Float'] > 1000 and oprType != 'P&Z':  # dHTML['PNZ'] != 'PNZ':
						errorVar = errorVar + 'P&E Lots have High Front Foot Price and could be Finished Lots instead<br>'
		except(NameError, TypeError) as e:
			pass

	if oprType == 'P&Z':
		if dHTML['PNZCITYPLANNER'] == '':
			errorVar = errorVar + 'No City Planner<br>'
	return errorVar, transLink

def assemble_error_mail_string(errorMail, errorVar, transLink):
	lao.print_function_name('script assemble_error_mail_string')
	if errorVar != transLink:
		errorMail = '{0}{1}'.format(errorMail, errorVar)
	else:
		transLink = '<a href="https://landadvisors.my.salesforce.com/{0}"><font color="green">{1} -- {2}</font></a><br>'.format(dHTML['Id'], dHTML['Lot_Type__c'], dHTML['PID__c'])
		errorMail = '{0}{1}'.format(errorMail, transLink)
	if dHTML['Description__c'] != '':
		errorMail = '{0}<font color="gray">Comment:   {1}</font><br><br>'.format(errorMail, dHTML['Description__c'])
	else:
		errorMail = '{0}<br>'.format(errorMail)

	return errorMail

def sendQCEmail(errorMail, qcCount, userName):
	lao.print_function_name('script sendQCEmail')
	qcHeader = '<head><title>OPR QC Results</title></head>'
	errorMail = qcHeader + 'OPR QC Results (' + str(qcCount) + ' transfers)<br><br>' + errorMail
	sender = 'OPR QC Results <research@landadvisors.com>'
	# sender = 'OPR QC Results <blandis@landadvisors.com>'
	recipients_to = ['{0} LAO <{1}@landadvisors.com>'.format(userName.upper(), userName)]

	# msg = MIMEMultipart('alternative')
	# msg['Subject'] = 'OPR QC Results'
	# msg['From'] = sender
	# msg['To'] = ','.join(recipients_to)
	# msg['Date'] = formatdate(localtime=True)

	#create body of the message as plain text and html
	# text = ''
	html = errorMail

	qc_subject = 'OPR QC Results'
	qc_body = errorMail
	qc_sender_email = sender
	qc_recipients = recipients_to

	return qc_subject, qc_body, qc_sender_email, qc_recipients

def send_opr_sent_notification(oprType):
	lao.print_function_name('script send_opr_sent_notification')
	# oprHeader = '<head><title>You Got OPRs</title></head>'
	sender = 'LAO Research <research@landadvisors.com>'
	if oprType == 'Comp':
		subjectOPRType = 'Comp'
	elif oprType == 'Listing':
		subjectOPRType = 'Competitor Listing'
	elif oprType == 'P&Z':
		subjectOPRType = 'Planning & Zoning'
	elif oprType == 'Request':
		subjectOPRType = 'Opportunity Property'

	subject = 'You Got {0} OPRs'.format(subjectOPRType)
	body = get_html_template('OPRNOTIFICATION')
	sender_email = sender

	return sender_email, subject, body
	# return sender, msg

def qc_complete_verification(PID, action='Read or Write'):
	qc_verified_filename = 'C:/Users/Public/Public Mapfiles/M1_Files/OPR QC Verified.txt'
	if not os.path.exists(qc_verified_filename):
		with open(qc_verified_filename, 'w') as f:
			f.write('OPR QC Verified')
			print(f'\n Created {qc_verified_filename} file.')
	if action == 'Read':
		with open(qc_verified_filename, 'r') as f:
			if PID in f.read():
				return True
		return False
	elif action == 'Write':
		with open(qc_verified_filename, 'a') as f:
			f.write('\n' + PID)

	
# START PROGRAM ###########################################################
while 1:
	# Get user name
	userName = lao.getUserName()

	# choose who to send it to.
	recipients_to, recipients_cc, SENDLIST, sender, oprType = send_to()

	# If no recipients_cc change variable to a value of None
	if recipients_cc == []:
		recipients_cc = None

	today = td.date_engine('today')
	errorMail = ''
	qcCount = 0

	results, market = create_query_string(service, SENDLIST, oprType)
	if results == []:
		continue
	sent_results = results

	for row in results:
		# HTML Django Dictionary
		dHTML = {}

		get_universal_fields(row)
		make_opr_map(dHTML['PID__c'])
		get_acres(row)
		get_classification(row)
		get_development_status(row)
		get_county(row)
		get_source(row)
		lao_activity(dHTML['PID__c'])
		get_seller_owner(row)
		get_beneficiary(row)

		# Comp fields
		
		if oprType == 'Comp':
			get_comp_fields(row, recipients_to)
			get_buyer(row)
			# Lot Details
			if dHTML['Lots__c'] > 0 and not 'Apartment' in dHTML['Classification__c']:
				get_lot_details()
			
			# if get_lot_details() == False:  # Skip temporarily to figure out fix
			# 	td.uInput('\n Skipped making OPR cuz missing Price per Lot in Lot Details...Continue...')
			# 	continue

		# Request Fields
		elif oprType == 'Request':
			get_request_fields()
			get_property_comps_table(row, market)
		# P&Z Fields
		elif oprType == 'P&Z':
			get_pnz_fields(row)
		# Listing Fields
		elif oprType == 'Listing':
			get_listing_fields(row)
			get_property_comps_table(row, market)
		elif oprType == 'AXIOPIPE':
			get_axio_pipeline_fields()
			get_property_comps_table(row, market)
		# PIR Fields
		elif oprType == 'PIR_Comp':
			get_pir_fields()
			get_comp_fields(row, recipients_to)
			get_buyer(row)

		get_links()
		get_opr_title(oprType, recipients_to)

		html = get_html_template(oprType)

		
		print('here1')
		pprint(dHTML)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		

		
		
		# Send OPR to Market recipients
		if SENDLIST.upper() != 'Q': # Skip sending OPRs if sending QC
			# Check if OPR has been QC'd
			if len(SENDLIST) >= 3:
				if qc_complete_verification(dHTML['PID__c'], 'Read') is False:
					print()
					print('!'*40)
					td.warningMsg(f' OPR {dHTML["PID"]} has not been QC\'d.')
					print('!'*40)
					print('\n  1) Restart OPR Mailer and QC OPRs')
					print(' 00) Quit')
					ui = td.uInput('\n Select > ')
					if ui != '1':
						exit('\n Terminating program...')
					break
			# Build OPR Message
			subject, body, sender_email, recipients_to = build_opr_message(recipients_to, SENDLIST, sender, oprType, html)

			# Save body as html file for reference
			html_filename = f'C:/TEMP/{dHTML["PID__c"]}_{dHTML["Lot_Type__c"]}_OPR.html'
			with open(html_filename, 'w', encoding='utf-8') as f:
				f.write(body)
			print(f'\n Saved {html_filename} file.')
			openbrowser(html_filename)

			# TEST PIR ###############################################################
			# if oprType == 'PIR_OPR' or oprType == 'PIR_Comp':
			# 	pass
			# else:
			dSend_results = emailer.send_email_ses(subject, body, sender_email, recipients_to, cc=recipients_cc, bcc=None, attachments=None)
			# Change OPR Sent date to today if OPR successfuly sent
			if SENDLIST.upper() != 'T' and dSend_results['success'] is True:
				mark_deal_as_sent(today)
			# Add OPR to QC list
			if SENDLIST.upper() == 'T':
				qc_complete_verification(dHTML['PID__c'], 'Write')
				# if dHTML['PID__c'] not in lOPR_qc:
				# 	lOPR_qc.append(dHTML['PID__c'])

		# Build Error Message if sending QC or Test
		if SENDLIST.upper() == 'Q' or SENDLIST.upper() == 'T':
			errorVar, transLink = qc(oprType, market)
			errorMail = assemble_error_mail_string(errorMail, errorVar, transLink)
			qcCount += 1
	
	
	# Send QC Email Message if sending QC or Test
	if SENDLIST.upper() == 'Q' or SENDLIST.upper() == 'T':
			qc_subject, qc_body, qc_sender_email, qc_recipients = sendQCEmail(errorMail, qcCount, userName)
			emailer.send_email_ses(qc_subject, qc_body, qc_sender_email, qc_recipients, cc=None, bcc=None, attachments=None)
	else:
		# Send You Got OPRs email
		if 'Rick Hildreth <rhildreth@landadvisors.com>' in recipients_to:
			sender_email, subject, body = send_opr_sent_notification(oprType)
			emailer.send_email_ses(subject, body, sender_email, recipients_to, cc=recipients_cc, bcc=None, attachments=None)

exit('\n Fin')

