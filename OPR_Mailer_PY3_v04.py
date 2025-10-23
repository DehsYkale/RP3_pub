# Generate OPR Mailers

# Libraries
import aws
import bb
import dicts
import django
from django.conf import settings
import emailer
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.utils import formatdate
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

td.banner('OPR Mail PY3 v03', colorama=True)
td.console_title('OPR Mailer v03')
# Login to TerraForce
service = fun_login.TerraForce()

# get Agent Dict
dStaff = dicts.get_staff_dict(dict_type='full')

def send_to():
	lao.print_function_name('script send_to')
	oprType = 'NONE'
	lLAOOffices = dicts.get_staff_dict('marketfulllist')
	
	while 1:
		td.banner('OPR Mailer PY3 v03', colorama=True)
		
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
				'  [4] Top 100 Opportunities\n' \
				'  [5] Axio Pipeline\n' \
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
			td.banner('OPR Mailer PY3 v03', colorama=True)
			print(' 🧪 Test mode selected - OPRs will be sent to you only')
			recipients_to = ['{0} LAO <{1}@landadvisors.com>'.format(userName.upper(), userName)]
			recipients_cc = []
			sender = 'OPR TEST <research@landadvisors.com>'
			return recipients_to, recipients_cc, SENDLIST, sender, oprType
		
		elif SENDLIST == 'Q' or SENDLIST == '11':
			SENDLIST = 'Q'
			td.banner('OPR Mailer PY3 v03', colorama=True)
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
			oprType = 'TOP100'
			print(f'\n ✅ Selected: {oprType} OPRs')
			
		elif SENDLIST == '5':
			oprType = 'AXIOPIPE'
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
		else:
			# Select the market
			wc, market = lao.getCountiesInMarketWhereClause()

			if oprType == 'Listing': # Listing uses different OPR Sent date
				wc = "{0} AND OPR_Sent__c = 1964-09-11".format(wc)
			elif oprType == 'AXIOPIPE': # Listing uses different OPR Sent date
				wc = "{0} AND OPR_Sent__c = 1929-10-02".format(wc)
			else:
				wc = "{0} AND OPR_Sent__c = 1965-01-11".format(wc)

			if oprType == 'TOP100':
				wc = "{0} AND StageName__c = 'Top 100'".format(wc)
			elif oprType == 'Comp':
				wc = "{0} AND StageName__c LIKE '%Closed%'".format(wc)

		# Select Records to Send
		while 1:
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
	dHTML['AFF'] = row['Weighted_Avg_Price_Per_FF__c']
	if dHTML['AFF'] != 'None':
		# dHTML['AFF'] = td.currency_format_from_number(dHTML['AFF'])
		dHTML['AFF'] = td.currency_format_from_number(dHTML['AFF'])
	else:
		dHTML['AFF'] = 'None'
	# dHTML['CMM'] = (row['Description__c']).upper().replace('±', '+/-').replace('—', '-').replace('½', '1/2').replace("you’ll", "you'll")
	if row['Description__c'] == 'None':
		dHTML['CMM'] = 'None'
	else:
		dHTML['CMM'] = lao.charactersToASCII(row['Description__c'], charCase='UPPER')
	if row['Subdivision__c'] == 'None':
		dHTML['CMT'] = 'None'
	else:
		dHTML['CMT'] = (row['Subdivision__c']).upper()
	dHTML['CTY'] = (row['City__c']).upper()
	dHTML['DID'] = row['Id']
	dHTML['DNM'] = row['Name']
	dHTML['ENCUMB'] = ''
	dHTML['LAT'] = row['Latitude__c']
	dHTML['LOC'] = lao.charactersToASCII(row['Location__c'], charCase='UPPER')
	dHTML['LON'] = row['Longitude__c']
	# Check for Lead Parcel
	dHTML['LPR'] = (row['Lead_Parcel__c']).upper()
	dHTML['LPR'] = dHTML['LPR'].strip()
	if dHTML['LPR'] == 'NONE' or dHTML['LPR'] == '':
		dHTML['LPR'] = bb.addLeadParcel(service, dHTML['DID'])
	dHTML['NLT'] = int(row['Lots__c'])
	dHTML['PID'] = row['PID__c']
	dHTML['PLT'] = 0
	dHTML['PPP'] = 0
	dHTML['PRL'] = row['Parcels__c']
	dHTML['RDN'] = row['Recorded_Instrument_Number__c']
	dHTML['SMK'] = (row['Submarket__c']).upper()
	dHTML['STG'] = row['StageName__c']
	if dHTML['STG'] == 'Escrow':
		dHTML['ESCROW'] = True
	else:
		dHTML['ESCROW'] = False
	dHTML['STTCap'] = (row['State__c']).upper()
	dHTML['STTLow'] = (row['State__c'])
	dHTML['TTY'] = (row['Lot_Type__c']).strip()
	dHTML['TTY'] = (dHTML['TTY']).upper()
	dHTML['TYP'] = row['Type__c']
	dHTML['ZIP'] = row['Zipcode__c']
	dHTML['ZON'] = row['Zoning__c']
	if dHTML['ZON'] == '':
		dHTML['ZON'] = 'NOT AVAILABLE'
	print('\n PID: {0}'.format(dHTML['PID']))

def make_opr_map(PID):
	# Check if the OPR map exists on aws and create it if not
	if aws.aws_file_exists(PID, extention='jpg', verbose=False) is False:
		oiPIDexists = mpy.make_opr_map_api(service, PID)

def get_acres(row):
	lao.print_function_name('script get_acres')
	dHTML['ACR'] = row['Acres__c']
	if dHTML['ACR'] == 0:
		dHTML['ACR'] = 'N/A'
		if row['Lots__c'] == 0 and row['Lot_Count_Rollup__c'] == 0:
			url = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['DID'])
			webbrowser.open(url)
			print('{0} has zero (0) Acres.  Please add acres.\n'.format(dHTML['DNM']))
			sys.exit('Terminating program...')

def get_classification(row):
	lao.print_function_name('script get_classification')
	# Convert Classification to upper case
	dHTML['CLA'] = row['Classification__c'].split(';')
	
	# Check for Classification	
	if dHTML['CLA'] == []:
		td.warningMsg('\n This PID does not have a Classification...', colorama=True)
		webs.openTFDID(row['Id'])
		exit(' Program terminated.')

	else:
		if len(dHTML['CLA']) == 1:
			dHTML['CLA'] = dHTML['CLA'][0]
		elif len(dHTML['CLA']) == 2 and 'Office' in dHTML['CLA'] and 'Retail' in dHTML['CLA']:
			dHTML['CLA'] = 'COMMERCIAL'
		elif len(dHTML['CLA']) == 3 and 'Office' in dHTML['CLA'] and 'Retail' in dHTML['CLA'] and 'Industrial' in dHTML['CLA']:
			dHTML['CLA'] = 'INDUSTRIAL/COMMERCIAL'
		elif len(dHTML['CLA']) > 2:
			if 'Residential' in dHTML['CLA']:
				dHTML['CLA'] = 'RESIDENTIAL'
			elif 'Apartment Traditional' in dHTML['CLA'] and ('Office' in dHTML['CLA'] or 'Retail' in dHTML['CLA']):
				dHTML['CLA'] = 'MIXED USE'
			else:
				dHTML['CLA'] = dHTML['CLA'][0]
		else:
			dHTML['CLA'] = dHTML['CLA'][0]
	dHTML['CLA'] = dHTML['CLA'].upper()

def get_development_status(row):
	lao.print_function_name('script get_development_status')
	if row['Development_Status__c'] == '':
		dHTML['DEVSTAT'] = 'None'
	else:
		dHTML['DEVSTAT'] = row['Development_Status__c'].upper()

def get_county(row):
	lao.print_function_name('script get_county')
	dHTML['COU'] = (row['County__c']).upper()
	if 'MARICOPA' in dHTML['COU']:
		dHTML['COU'] = 'MARICOPA'
	elif 'PINAL' in dHTML['COU']:
		dHTML['COU'] = 'PINAL'

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


	dHTML['STAGENAME'] = results[0]['StageName__c']
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
				dHTML['LISTAGENTNAME'] = agent['Agent__r']['Name'].upper()
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
	elif dHTML['STAGENAME'] == 'Closed Lost':
		dHTML['LAOACT'] = 0

def get_comp_fields(row, recipients_to):
	lao.print_function_name('script get_comp_fields')
	dHTML['BAA'] = (row['Buyer_Acting_As__c']).upper()
	dHTML['ENCUMB'] = (row['Encumbrance_Rating__c']).upper()
	dHTML['DTE'] = row['Sale_Date__c']
	dHTML['DTE'] = td.date_engine(dHTML['DTE'], outformat='opr', informat='TF')

	if row['Sale_Price__c'] == 10000:
		dHTML['PRC'] = 10000
		dHTML['PPA'] = 10000
		dHTML['PPAraw'] = 10000
		dHTML['PRCNUM'] = 10000
	else:
		dHTML['PRC'] = row['Sale_Price__c']
		dHTML['PPA'] = float(dHTML['PRC']) / float(dHTML['ACR'])
		dHTML['PPAraw'] = dHTML['PPA']
		dHTML['PPA'] = '$' + '{:,.0f}'.format(dHTML['PPA'])
		dHTML['PRCNUM'] = dHTML['PRC']
		# Caclulate Price per Sq Foot
		sq_ft = float(dHTML['ACR']) * 43560
		dHTML['PPSQFT'] = float(dHTML['PRC']) / sq_ft
		dHTML['PPSQFTraw'] = dHTML['PPSQFT']
		dHTML['PPSQFT'] = '$' + '{:,.2f}'.format(dHTML['PPSQFT'])

	# Apartment/Assisted Living Unit Fields
	if (dHTML['CLA'] == 'APARTMENT' or dHTML['CLA'] == 'APARTMENT TRADITIONAL' or  'ASSISTED LIVING' in dHTML['CLA']) and dHTML['NLT'] > 0:
		dHTML['LOT'] = 'APARTMENT'
		dHTML['PPU'] = dHTML['PRC'] / dHTML['NLT']
		dHTML['PPU'] = '$' + '{:,.0f}'.format(dHTML['PPU'])
		dHTML['MTF'] = True
	elif dHTML['TTY'] == 'Raw Acreage':
		dHTML['LOT'] = 'RAW ACREAGE'
		dHTML['MFT'] = False
	else:
		dHTML['LOT'] = 'RESIDENTIAL'
		dHTML['MFT'] = False

	# Add GV to Whale Sales outside of Scottsdale
	if SENDLIST != 'Q' and SENDLIST != 'T':
		if dHTML['PRC'] >= 15000000 and 'Greg Vogel <gvogel@landadvisors.com>' not in recipients_to:
			recipients_to.append('Greg Vogel <gvogel@landadvisors.com>')

	dHTML['PRC'] = '$' + '{:,.0f}'.format(dHTML['PRC'])

def get_top100_fields():
	lao.print_function_name('script get_top100_fields')
	dHTML['DTE'] = 'None'
	dHTML['PNZ'] = 'None'
	dHTML['LOT'] = 'TOP100'

def get_axio_pipeline_fields():
	lao.print_function_name('script get_axio_pipeline_fields')
	dHTML['LOT'] = 'AXIOPIPE'
	dHTML['PNZ'] = 'None'

def get_pnz_fields(row):
	lao.print_function_name('script get_pnz_fields')
	
	
	dHTML['LOT'] = 'P&Z'
	dHTML['PNZ'] = 'PNZ'
	dHTML['PNZAPPLICANTID'] = row['Zoning_Applicant__c']
	try:
		dHTML['PNZAPPLICANT'] = (row['Zoning_Applicant__r']['Name']).upper()
	except TypeError:
		td.warningMsg(' Zoning Applicant field cannot be blank!', colorama=True)
		url = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['DID'])
		webbrowser.open(url)
		exit('\n Terminating Program...')
	dHTML['PNZAPPLICANTurl'] = 'https://landadvisors.my.salesforce.com/%s' % dHTML['PNZAPPLICANTID']
	dHTML['PNZCASE'] = row['Case_Plan__c']
	# PNZCITYPLANNER = 'None'
	dHTML['PNZCITYPLANNERID'] = row['City_Planner__c']
	if dHTML['PNZCITYPLANNERID'] != '':
		dHTML['PNZCITYPLANNER'] = (row['City_Planner__r']['Name']).upper()
	else:
		dHTML['PNZCITYPLANNER'] = ''
	dHTML['PNZCITYPLANNERurl'] = 'https://landadvisors.my.salesforce.com/%s' % dHTML['PNZCITYPLANNERID']
	dHTML['PNZDES'] = row['P_Z_Description__c'].replace('±', '+/-').replace('—', '-')
	dHTML['PNZDTE'] = row['P_Z_Last_Event_Date__c']
	dHTML['DTE'] = 'None'
	dHTML['BTX'] = 'P&Z'
	dHTML['BPR'] = 'P&Z'
	dHTML['BTXcat'] = 'P&Z'
	dHTML['BAA'] = 'P&Z'

def get_listing_fields(row):
	lao.print_function_name('script get_listing_fields')
	dHTML['LOT'] = 'Listing'
	dHTML['LISTPRC'] = row['List_Price__c']
	if dHTML['LISTPRC'] == None or dHTML['LISTPRC'] == 10000:
		dHTML['LISTPRC'] = 'N/A'
		dHTML['LISTPPA'] = 'N/A'
	else:
		listPPA = dHTML['LISTPRC'] / dHTML['ACR']
		dHTML['LISTPPA'] = '${:,.0f}'.format(listPPA)
		dHTML['LISTPRC'] = '${:,.0f}'.format(dHTML['LISTPRC'])
	dHTML['LISTDTE'] = row['List_Date__c']
	dHTML['LISTEXPIRE'] = row['Listing_Expiration_Date__c']

	# Check if Package Exists
	# try:
		# code = urlopen('https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(dHTML['PID'])).code
	# brochure_exists = webs.awsFileExists('{0}_competitors_package.pdf'.format(dHTML['PID']))
	brochure_exists = aws.aws_file_exists(f'{dHTML['PID']}_competitors_package.pdf', extention='png', verbose=False)
	if brochure_exists:
		dHTML['BROCHUREURL'] = 'https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(dHTML['PID'])
	# except:
	else:
		dHTML['BROCHUREURL'] = False

# Build Comps Table
def get_listing_comps_table(row, oprType, market):
	lao.print_function_name('script get_listing_comps_table')

	# Calc min max coords
	dCords = mpy.get_bounding_box_coords(row['Latitude__c'], row['Longitude__c'], 10)
	minX = dCords['west_lon']
	maxX = dCords['east_lon']
	minY = dCords['south_lat']
	maxY = dCords['north_lat']

	# Set Date to last 3 years
	date = td.less_time_ago('MONTH', 36)

	# # Lot Type
	# LTY = row['Lot_Type__c']
	# # Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	# fields = 'PID__c, Id, Acres__c, Price_Per_Acre__c, Price_Per_Lot__c, Lots__c, Weighted_Avg_Price_Per_FF__c, Sale_Date__c, Sale_Price__c'

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
	compsTable = ''
	for pid in results:
		OPRLink = 'https://landadvisors.lightning.force.com/lightning/r/lda_Opportunity__c/{0}/view'.format(pid['Id'])
		L5Link = webs.get_L5_url('', market, pid['PID__c'])
		compPrice = '${:,.0f}'.format(pid['Sale_Price__c'])
		compPricePerAcre = '${:,.0f}'.format(pid['Price_Per_Acre__c'])
		compSaleDate = (td.date_engine(pid['Sale_Date__c'], outformat='opr', informat='TF'))
		compsRow = "<tr><td><a href='{0}'>{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td><a href='{6}'>L5</a></td></tr>".format(OPRLink, pid['PID__c'], compSaleDate,  compPrice, pid['Acres__c'], compPricePerAcre, L5Link)
		compsTable = '{0}{1}'.format(compsTable, compsRow)
	compsTable = compsTable.replace(' /', '/')
	dHTML['LISTINGCOMPSTABLE'] = compsTable

def get_seller_owner(row):
	lao.print_function_name('script get_seller_owner')
	# Get Seller/Owner Entity Name, Person and Category
	dHTML['STXID'] = row['Owner_Entity__c']
	# No Owner Entity
	if dHTML['STXID'] == 'None':
		dHTML['STX'], dHTML['STXurl'], dHTML['STXcat'], dHTML['STXphn'] = '', '', '', 'UNKNOWN'
	# Add Owner Entity
	else:
		dHTML['STXurl'] = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['STXID'])
		dHTML['STX'] = (row['Owner_Entity__r']['Name']).upper()
		if row['Owner_Entity__r']['Phone'] != '':
			dHTML['STXphn'] = row['Owner_Entity__r']['Phone']
		else:
			dHTML['STXphn'] = 'UNKNOWN'

	# No Person Account
	if row['AccountId__r'] == 'None':
		dHTML['SPR'], dHTML['SPRurl'], dHTML['SPRT100'], dHTML['SPRT100url'], dHTML['SPRphn'], dHTML['SPRemail'], dHTML['SPRcity'], dHTML['SPRstate'] = '', '', '', '', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN'
	# Add Person Account
	else:
		dHTML['SPR'] = (row['AccountId__r']['Name']).upper()
		dHTML['SPRurl'] = 'https://landadvisors.my.salesforce.com/%s' % row['AccountId__c']
		# Check if Top 100
		dHTML['SPRT100url'] = 'https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}'.format(row['AccountId__c'])

		if row['AccountId__r']['PersonMobilePhone'] != '':
			dHTML['SPRphn'] = row['AccountId__r']['PersonMobilePhone']
		elif row['AccountId__r']['Phone'] != '':
			dHTML['SPRphn'] = row['AccountId__r']['Phone']
		else:
			dHTML['SPRphn'] = 'UNKNOWN'

		if row['AccountId__r']['PersonEmail'] != '':
			dHTML['SPRemail'] = row['AccountId__r']['PersonEmail']
		else:
			dHTML['SPRemail'] = 'UNKNOWN'

		# Add Top 100 link
		if row['AccountId__r']['Top100__c'] == 'None':
			dHTML['SPRT100'] = 'MAKE MVP'
		else:
			str_top100_agents = row['AccountId__r']['Top100__c'].replace(';', ', ')
			dHTML['SPR'] = '{0} ({1})'.format(dHTML['SPR'], str_top100_agents)
			dHTML['SPRT100'] = 'EDIT MVP'

		# Add City & State
		if row['AccountId__r']['BillingCity'] != '':
			dHTML['SPRcity'] = row['AccountId__r']['BillingCity']
		else:
			dHTML['SPRcity'] = 'UNKNOWN'
		if row['AccountId__r']['BillingState'] != '':
			dHTML['SPRstate'] = row['AccountId__r']['BillingState']
		else:
			dHTML['SPRstate'] = 'UNKNOWN'
	
	if dHTML['STXID'] != 'None':
		dHTML['STXcat'] = bb.chooseAccountCategory(service, dHTML['STXID'])
	else:
		# do not assign a person name to a business
		dHTML['STX'] = ''

def get_buyer(row):
	lao.print_function_name('script get_buyer')

	# Check if Buyer Person exists and if not set BPR to Unknown
	if row['Offers__r']['records'][0]['Buyer__r'] == 'None':
		dHTML['BPR'] = ''
	else:
		dHTML['BPR'] = (row['Offers__r']['records'][0]['Buyer__r']['Name']).upper()
		dHTML['BPRurl'] = 'https://landadvisors.my.salesforce.com/{0}'.format(row['Offers__r']['records'][0]['Buyer__r']['Id'])
		
		# Check Top 100
		if row['Offers__r']['records'][0]['Buyer__r']['Top100__c'] == 'None':
			dHTML['BPRT100'] = 'MAKE MVP'
		else:
			# Make Buyer Person Top100 link
			dHTML['BPRT100url'] = 'https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}'.format(row['Offers__r']['records'][0]['Buyer__r']['Id'])
			str_top100_agents = row['Offers__r']['records'][0]['Buyer__r']['Top100__c'].replace(';', ', ')
			dHTML['BPR'] = '{0} ({1})'.format(dHTML['BPR'], str_top100_agents)
			dHTML['BPRT100'] = 'EDIT MVP'
	
	# Check for Buyer Entity
	if row['Offers__r']['records'][0]['Buyer_Entity__r'] == 'None':
		dHTML['BTX'], dHTML['BTXID'], dHTML['BTXurl'], dHTML['BTXcat'] = '', '', '', ''
	else:
		dHTML['BTX'] = (row['Offers__r']['records'][0]['Buyer_Entity__r']['Name']).upper()
		dHTML['BTXID'] = row['Offers__r']['records'][0]['Buyer_Entity__r']['Id']
		dHTML['BTXurl'] = 'https://landadvisors.my.salesforce.com/{0}'.format(dHTML['BTXID'])
		dHTML['BTXcat'] = bb.chooseAccountCategory(service, dHTML['BTXID'])

def get_beneficiary(row):
	lao.print_function_name('script get_beneficiary')
	if row['Beneficiary__c'] != 'None':
		dHTML['BENEFICIARY'] = (row['Beneficiary__r']['Name']).upper()
		dHTML['BNFurl'] = 'https://landadvisors.my.salesforce.com/{0}'.format(row['Beneficiary__c'])
		dHTML['LOANAMOUNT'] = '$' + '{:,.0f}'.format(row['Loan_Amount__c'])
		dHTML['LOANDATE'] = row['Loan_Date__c']
	else:
		dHTML['BENEFICIARY'], dHTML['BNFurl'], dHTML['LOANAMOUNT'] = False, 'None', 'None'

def get_lot_details():
	lao.print_function_name('script get_lot_details')
	# qs = "SELECT Acres__c, Lot_Count__c, Lot_Depth__c, Lot_Width__c, Name, Price_per_Front_Foot__c, Price_per_Lot__c, Price_per_parcel__c FROM lda_Lot_Detail__c WHERE Opportunity__c = '%s' AND RecordTypeId = '012a0000001ZSiZAAW'" % dHTML['DID']
	# lot_dict = bb.sfquery(service, qs)
	# TerraForce Query
	fields = 'default'
	wc = "Opportunity__c = '{0}' AND RecordTypeId = '012a0000001ZSiZAAW'".format(dHTML['DID'])
	lot_dict = bb.tf_query_3(service, rec_type='LotDetail', where_clause=wc, limit=None, fields=fields)
	dHTML['PFFFloat'] = 501
	if dHTML['LOT'] != 'APARTMENT':
		if dHTML['TTY'] == 'PLATTED AND ENGINEERED':
			dHTML['LOT'] = 'PIPE'
			dHTML['LBN'] = 'WTF'  # Needed to generate the lot table
		elif dHTML['TTY'] == 'PARTIALLY IMPROVED':
			dHTML['LOT'] = 'PIPE'
			dHTML['LBN'] = 'WTF'  # Needed to generate the lot table
		elif dHTML['TTY'] == 'RAW ACREAGE':
			dHTML['LOT'] = 'PIPE'
		elif dHTML['TTY'] == 'INITIAL LOT OPTION':
			dHTML['LOT'] = 'LOTS'
			dHTML['LBN'] = 'WTF'  # Needed to generate the lot table
		else:
			dHTML['LOT'] = 'LOTS'
			dHTML['LBN'] = 'WTF'  # Needed to generate the lot table
	dHTML['PPP'] = 0
	dHTML['NLG'] = 0  # Number of Lot Groups
	dHTML['LTC'] = 0  # Lot Count (total of groups)
	dHTML['TOTALFF'] = 0
	dHTML['LST'] = ''  # List of groups in HTML
	dHTML['LTW'] = ''
	if lot_dict == []:
		return True
	for row in lot_dict:
		
		if row['Price_per_Lot__c'] == None:
			return False
		dHTML['NLG'] += 1
		dHTML['LAC'] = row['Acres__c']
		dHTML['LTCSINGLE'] = row['Lot_Count__c']
		dHTML['LTC'] = dHTML['LTC'] + int(dHTML['LTCSINGLE'])
		# Check for blank dimensions
		try:
			dHTML['LTD'] = int(row['Lot_Depth__c'])
		except TypeError:
			dHTML['LTD'] = None
		if dHTML['LTD'] == 0:
			dHTML['LTD'] = None
		if dHTML['LTD'] is None:
			dHTML['LTD'] = 'None'
			dHTML['LTW'] = 'None'
			dHTML['PFF'] = 'None'
			dHTML['AFF'] = 'None'
			dHTML['PFFFloat'] = 'None'
		else:
			dHTML['LTW'] = int(row['Lot_Width__c'])
			dHTML['TOTALFF'] = dHTML['TOTALFF'] + (dHTML['LTW'] * dHTML['LTCSINGLE'])
			# AFF = AFF + float(PFF)
			if dHTML['LTW'] == 0:
				dHTML['PFFFloat'] = 0
				dHTML['PFF'] = 0
			else:
				if dHTML['STG'] != 'Lead':
					dHTML['PFF'] = row['Price_per_Front_Foot__c']
					dHTML['PFFFloat'] = float(dHTML['PFF'])  #check if PFF is below $500 variable
					dHTML['PFF'] = td.currency_format_from_number(dHTML['PFF'])
				else:
					dHTML['PFF'] = 0

		dHTML['PLT'] = row['Price_per_Lot__c']
		try:
			dHTML['PLT'] = td.currency_format_from_number(dHTML['PLT'])
		except TypeError:
			td.warningMsg('\n Lot Detail is missing Price.', colorama=True)
			sys.exit('\n Terminaiting program...continue...')
		dHTML['PPP'] = row['Price_per_parcel__c']
		dHTML['PPP'] = td.currency_format_from_number(dHTML['PPP'])

		if dHTML['AFF'] == 'None':
			dHTML['TAG'] = "<tr><td></td><td>%d</td><td>%d</td><td>N/A</td><td>%s</td><td>%s</td><td>N/A</td><td>" % (dHTML['NLG'], dHTML['LTCSINGLE'], dHTML['PPP'], dHTML['PLT'])
		else:
			dHTML['TAG'] = "<tr><td></td><td>%d</td><td>%d</td><td>%s' x %s'</td><td>%s</td><td>%s</td><td>%s</td><td>" % (dHTML['NLG'], dHTML['LTCSINGLE'], dHTML['LTW'], dHTML['LTD'], dHTML['PPP'], dHTML['PLT'], dHTML['PFF'])
		dHTML['LST'] = dHTML['LST'] + dHTML['TAG']
	# Use Lot Details Count if not 0 rather than Lots__c
	if dHTML['LTC'] != 0:
		dHTML['NLT'] = dHTML['LTC']
	return True

def get_opr_title(oprType, recipients_to):
	lao.print_function_name('script get_opr_title')
	subCLA = dHTML['CLA'].title()
	subCTY = dHTML['CTY'].title()
	LANDTYPE = 'None'

	# MVP OPR Title
	if oprType == 'TOP100':
		dHTML['TLT'] = 'LAO Opportunity: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TLT'] = dHTML['TLT'].replace('±', '+/-')
	# P&Z OPR Title
	elif oprType == 'P&Z':
		dHTML['TLT'] = 'P&Z: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TLT'] = dHTML['TLT'].replace('±', '+/-')
	# LISTING OPR Title
	elif oprType == 'Listing':
		if dHTML['LISTPRC'] == 'N/A':
			dHTML['TLT'] = 'For Sale: {0} Land in {1}'.format(subCLA, subCTY)
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
				dHTML['TLT'] = 'For Sale: {0} Land in {1}'.format(subCLA, subCTY)
			else:
				dHTML['TLT'] = 'For Sale: {0} {1} Land in {2}'.format(DOLLARS, subCLA, subCTY)
			dHTML['TLT'] = dHTML['TLT'].replace('±', '+/-')
	elif oprType == 'AXIOPIPE':
		dHTML['TLT'] = 'Axio Pipeline: {0} Land in {1}'.format(subCLA, subCTY)
		dHTML['TLT'] = dHTML['TLT'].replace('±', '+/-')

	elif dHTML['CLA'].upper() == 'APARTMENT':
		LANDTYPE = 'Apartment'
	elif dHTML['CLA'].upper() == 'APARTMENT HORIZONTAL':
		LANDTYPE = 'Horizontal Apt'
	elif dHTML['CLA'].upper() == 'APARTMENT TRADITIONAL':
		LANDTYPE = 'Traditional Apt'
	elif dHTML['CLA'].upper() == 'HIGH DENSITY ASSISTED LIVING':
		LANDTYPE = 'High Density Assisted Living'
	elif dHTML['CLA'].upper() == 'COMMERCIAL':
		LANDTYPE = 'Commercial'
	elif dHTML['TTY'] == 'RAW ACREAGE':
		LANDTYPE = '{0} Acreage'.format(subCLA)
	elif dHTML['TTY'] == 'FINISHED LOTS':
		LANDTYPE = 'Finished Lot'
	elif dHTML['TTY'] == 'PLATTED AND ENGINEERED':
		LANDTYPE = 'P&E Lot'
	elif dHTML['TTY'] == 'PARTIALLY IMPROVED':
		LANDTYPE = 'Partially Improved Lot'
	elif dHTML['TTY'] == 'INITIAL LOT OPTION':
		LANDTYPE = 'Rolling Lot Option'
	elif dHTML['TTY'] == 'COVERED LAND':
		LANDTYPE = 'Covered Land'
	else:
		dHTML['LANDTYPE'] = subCLA

	if oprType == 'Comp':
		if float(dHTML['PRCNUM']) == 10000:
			DOLLARS = 'None'
		elif float(dHTML['PRCNUM']) >= 1000000:
			DOLLARS = '$' + '{:,.1f}'.format(dHTML['PRCNUM'] / 1000000) + 'M'
		else:
			DOLLARS = '$' + '{:,.0f}'.format(dHTML['PRCNUM'] / 1000) + 'K'
		if DOLLARS == 'None':
			dHTML['TLT'] = '{0} Deal in {1}'.format(LANDTYPE, subCTY)
		else:
			dHTML['TLT'] = '{0} {1} Deal in {2}'.format(DOLLARS, LANDTYPE, subCTY)
		if dHTML['STG'] == 'Closed' or dHTML['STG'] == 'Escrow':
			dHTML['TLT'] = 'LAO {0}'.format(dHTML['TLT'])
			# Add GV & BR to LAO Deals
			if SENDLIST != 'Q' and SENDLIST != 'T':
				if 'Greg Vogel <gvogel@landadvisors.com>' not in recipients_to:
					recipients_to.append('Greg Vogel <gvogel@landadvisors.com>')
				if 'Brian Rosener <rrosener@landadvisors.com>' not in recipients_to:
					recipients_to.append('Brian Rosener <rrosener@landadvisors.com>')
		dHTML['TLT'] = dHTML['TLT'].replace('±', '+/-')

def get_links():
	lao.print_function_name('script get_links')
	# Set location of the OPR Map
	dHTML['MAP'] = 'https://request-server.s3.amazonaws.com/maps/{0}.jpg'.format(dHTML['PID'])
	# openbrowser(dHTML['MAP'])
	# dHTML['MAP'] = 'https://request-server.s3.amazonaws.com/maps/{0}.png'.format(dHTML['PID'])
	if 'MARICOPA' in dHTML['COU']:
		dHTML['RDNLink'] = (dHTML['RDN'][2:]).replace('-', '')
		dHTML['RDC'] = 'http://recorder.maricopa.gov/recdocdata/GetRecDataRecentDetail.aspx?rec=%s' % dHTML['RDNLink']
		dHTML['LPL'] = 'http://mcassessor.maricopa.gov/?s=%s' % dHTML['LPR']
	elif 'PINAL' in dHTML['COU']:
		dHTML['RDC'] = 'http://www.pinalcountyaz.gov/Recorder/Pages/DocumentSearch.aspx?fy=%s&fn=%s' % (dHTML['RDN'][:4], dHTML['RDN'][5:])
		dHTML['LPL'] = 'http://www.pinalcountyaz.gov/ASSESSOR/Pages/ParcelSearch.aspx'
	else:
		dHTML['RDC'] = ''
		dHTML['LPL'] = ''

	# L5 link
	# create L5 Market Name & ZoomTo&mapid==## dictionary
	dHTML['L5L'] = webs.get_L5_url(oprType, market, dHTML['PID'])

def get_html_template(oprType):
	lao.print_function_name('script get_html_template')
	# Get html template
	if oprType == 'Comp':
		return open(r'F:\Research Department\Code\RP3\templates\opr_comps_09.html', 'r').read()
	elif oprType == 'Listing':
		return open(r'F:\Research Department\Code\RP3\templates\opr_listing_01.html', 'r').read()
	elif oprType == 'P&Z':
		return open(r'F:\Research Department\Code\RP3\templates\opr_planning_zoning_04.html',
					'r').read()
	elif oprType == 'TOP100':
		return open(r'F:\Research Department\Code\RP3\templates\top_100_02.html',
					'r', encoding='utf-8').read()
	elif oprType == 'OPRNOTIFICATION':
		return open(r'F:\Research Department\Code\RP3\templates\you_got_oprs.html',
					'r').read()
	elif oprType == 'AXIOPIPE':
		return open(r'F:\Research Department\Code\RP3\templates\opr_axio_pipe_01.html', 'r').read()

def get_recipient_top100(names):
	lao.print_function_name('script get_recipient_top100')
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
	# msg['Subject'] = 'OPR: {0}'.format(dHTML['TLT'])
	# msg['From'] = sender
	# msg['Date'] = formatdate(localtime=True)

	if oprType == 'TOP100' and SENDLIST.upper() != 'T':
		recipients_to = get_recipient_top100(dHTML['AGENTNAMES'])

	# assign Template
	t = Template(html)
	c = Context(dHTML)
	html = t.render(c)

	subject = 'OPR: {0}'.format(dHTML['TLT'])
	body = html
	sender_email = sender

	return subject, body, sender_email, recipients_to


# Add today's date to the Deal's OPR_Sent__c field
def mark_deal_as_sent(today, DID):
	lao.print_function_name('script mark_deal_as_sent')
	dUp = {'type': 'lda_Opportunity__c', 'Id': DID, 'OPR_Sent__c': today}
	up_results = bb.tf_update_3(service, dUp)

def qc(oprType, market):
	lao.print_function_name('script qc')
	# QC Routines
	transLink = '<a href="https://landadvisors.my.salesforce.com/{0}"><font color="red">{1} -- {2}</font></a><br>'.format(dHTML['DID'], dHTML['LOT'], dHTML['PID'])
	if dHTML['SOURCE'] == 'Vizzda':
		transLink = '{0}<a href="{1}"><font color="red">Vizzda Link</font></a><br>'.format(transLink, dHTML['SOURCELINK'])
	if market == 'Tucson' and dHTML['SOURCELINK'] != '':
		transLink = '{0}<a href="{1}"><font color="red">RED News Link</font></a><br>'.format(transLink, dHTML['SOURCELINK'])
	if dHTML['SOURCE'] == 'Reonomy':
		transLink = '{0}<a href="{1}"><font color="red">Reonomy Link</font></a><br>'.format(transLink,dHTML['SOURCELINK'])
	errorVar = transLink

	if dHTML['LPR'] == '' or dHTML['LPR'].upper() == 'NONE':
		errorVar = errorVar + 'Lead Parcel is Missing<br>'
	if dHTML['PRL'] == '' or dHTML['PRL'].upper() == 'NONE':
		errorVar = errorVar + 'Parcels are Missing<br>'
	if dHTML['CMT'] == '' and dHTML['CLA'] == '%RESIDENTIAL%':
		errorVar = errorVar + 'Missing Subdivision<br>'
	if 'APARTMENT' in dHTML['CLA'] and dHTML['NLT'] == 0 and dHTML['SOURCE'] != 'CREXI' and  dHTML['SOURCE'] != 'Costar' and dHTML['TTY'] != 'RAW ACREAGE':
		errorVar = errorVar + 'Missing Number of Apt Units<br>'
	if 'DISTRESSED' in dHTML['CLA']:
		errorVar = errorVar + 'Classification is Distressed<br>'
	if 'ASSISTED LIVING' in dHTML['CLA'] and dHTML['NLT'] == 0 and dHTML['SOURCE'] != 'Costar':
		errorVar = errorVar + 'Missing Number of Assisted Living Units<br>'
	if dHTML['LOC'] == dHTML['CMT'] and dHTML['LOC'] != '':
		errorVar = errorVar + 'Location & Subdivision are the Same<br>'
	if dHTML['LON'] == '' or dHTML['LAT'] == '':
		errorVar = errorVar + 'No Lon/Lat<br>'
	if dHTML['TTY'] == 'ROLLING LOT OPTION':
		errorVar = errorVar + 'Rolling Lot Option change to Initial Lot Option<br>'
	if dHTML['TTY'] != 'RAW ACREAGE' and dHTML['NLT'] == 0:
		errorVar = errorVar + '{0} Missing Lot Details<br>'.format(dHTML['TTY'])
	if oprType != 'Listing' and dHTML['LOC'] == '':
		errorVar = errorVar + 'Missing Location<br>'
	if oprType == 'Listing' and dHTML['BROCHUREURL'] is False:
		if not dHTML['PID'][:2] == 'ID': # Skip Idaho
			errorVar = errorVar + 'Missing Listing Brochure<br>'
	if dHTML['CTY'] == '':
		errorVar = errorVar + 'Missing City<br>'
	if dHTML['TTY'] == '':
		errorVar = errorVar + 'Missing Lot Type<br>'
	if dHTML['ACR'] == 'N/A' or dHTML['ACR'] == 0:
		errorVar = errorVar + 'Zero Acres<br>'
	if dHTML['ACR'] == 1:
		errorVar = errorVar + 'Acres = 1 Please confirm Acres<br>'
	if (dHTML['ZON'] == 'None') and (dHTML['COU'] == 'MARICOPA'):
		errorVar = errorVar + '-- *** Caution Missing Zoning *** --<br>'
	if 'CITY' in dHTML['ZON'] or 'TOWN' in dHTML['ZON'] or 'MARICOPA' in dHTML['ZON']:
		errorVar = errorVar + '--- DO NOT EMAIL --- City or Town in Zoning --- DO NOT EMAIL ---<br>'
	if dHTML['STXcat'] == '' and dHTML['STX'] != '':
		errorVar = errorVar + '<a href="https://landadvisors.my.salesforce.com/%s"><font color="red">Seller Entity</font></a> missing Category<br>' % dHTML['STXID']
	if dHTML['CLA'] == '' or dHTML['CLA'] == 'NONE':
		errorVar = errorVar + 'Missing Classification<br>'
	if 'Closed' in dHTML['STG']:
		if 'AGRICULTURAL' in dHTML['CLA'] and dHTML['PPAraw'] > 40000:
			errorVar = errorVar + 'Agricultural land price is high<br>'
	if dHTML['TTY'] != 'Raw Acreage':
		if dHTML['LOT'] == 'PARCELS':
			errorVar = errorVar + 'Missing Lot Breakdown<br>'
		if dHTML['CMT'] == '':
			errorVar = errorVar + 'Missing Subdivision<br>'
	if dHTML['NLT'] != 0 and dHTML['TTY'] == 'Raw Acreage':
		errorVar = errorVar + 'Number of Lots is NOT 0 and Lot Type is Raw Acreage<br>'
	lStates = ['AL', 'AZ', 'FL', 'GA', 'ID', 'KS', 'MO', 'NC', 'NM', 'NV', 'SC', 'TN', 'TX', 'UT']
	for state in lStates:
		if state in dHTML['LPR']:
			errorVar = errorVar + 'Lead Parcel is a PID<br>'
			break

	if market == 'Scottsdale' or market == 'Tucson':
		if '&' in dHTML['CMT']:
			errorVar = errorVar + '"&" in Subdivision Name<br> Subdivision: ' + dHTML['CMT'] + '<br>'
		if '&' not in dHTML['LOC']:
			errorVar = errorVar + 'Bad Location Formating<br>'
		if dHTML['SMK'] == '':
			errorVar = errorVar + 'Missing Submarket<br>'
		if dHTML['SPR'] == '':
			errorVar = errorVar + '-- *** Caution Missing Owner/Seller Person *** --<br>'

	if oprType == 'Comp': # dHTML['PNZ'] != 'PNZ':
		if dHTML['BAA'] == '':
			errorVar = errorVar + 'Missing Buyer Acting As<br>'
		if dHTML['BTXcat'] == '' and dHTML['BTX'] != '':
			errorVar = '{0}<a href="https://landadvisors.my.salesforce.com/{1}"><font color="red">Buyer Entity</font></a> missing Category<br>'.format(
				errorVar, dHTML['BTXID'])
		if dHTML['BPR'] == '' and (market == 'Scottsdale' or market == 'Tucson'):
			errorVar = errorVar + '-- *** Caution Missing Buyer Person *** --<br>'
		try:
			if dHTML['PPP'] == 0 and dHTML['LST'] != '':
				errorVar = errorVar + 'Missing Price Per Parcel<br>'
		except NameError:
			pass
		if dHTML['BTX'] == '' and dHTML['BPR'] == '':
			errorVar = errorVar + 'Missing Buyer Entity<br>'
		if dHTML['BTX'] == dHTML['STX'] and dHTML['BTX'] != '':
			errorVar = errorVar + 'Buyer Entity & Owner/Seller Entity are the same<br>'
		if dHTML['BPR'] == dHTML['SPR'] and dHTML['BPR'] != '':
			errorVar = errorVar + 'Buyer Person & Owner/Seller Person are the same<br>'
		try:
			if dHTML['LTW'] != '' and dHTML['LTW'] != 0 and dHTML['LTW'] != None:
				if dHTML['PFFFloat'] < 500 and dHTML['LOT'] == 'LOTS' and dHTML['LTW'] < 100:
					errorVar = errorVar + 'Price per Front Foot is Low<br>PFF = ' + dHTML['PFF'] + '<br>'
				if dHTML['LTW'] < 30 and dHTML['LTW'] > 100 and market == 'Scottsdale':
					errorVar = errorVar + 'Odd Lot Width (<30 or >100)<br>PFF = ' + dHTML['PFF'] + '<br>'
				if dHTML['LTW'] != '':
					if dHTML['PFFFloat'] > 1700 and dHTML['LTW'] >= 35 and oprType != 'P&Z':  # dHTML['PNZ'] != 'PNZ':
						errorVar = errorVar + 'Price per Front Foot is High<br>PFF = ' + dHTML['PFF'] + '<br>'
					if dHTML['TTY'] == 'Platted and Engineered' and dHTML[
						'PFFFloat'] > 1000 and oprType != 'P&Z':  # dHTML['PNZ'] != 'PNZ':
						errorVar = errorVar + 'P&E Lots have High Front Foot Price and could be Finished Lots instead<br>'
		except(NameError, TypeError) as e:
			pass

	if oprType == 'P&Z':
		if dHTML['PNZCITYPLANNER'] == '':
			errorVar = errorVar + 'No City Planner<br>'

	# Check if the OPR map exists on aws and create it if not
	# if webs.awsFileExists('{0}'.format(dHTML['PID'])) is False:
	# 	oiPIDexists = mpy.make_opr_map_api('{0}'.format(dHTML['PID']))
	# 	if oiPIDexists is False:
	# 		errorVar = errorVar + 'OPR map could not be created.<b.>'
	return errorVar, transLink

def assemble_error_mail_string(errorMail, errorVar, transLink):
	lao.print_function_name('script assemble_error_mail_string')
	if errorVar != transLink:
		errorMail = '{0}{1}'.format(errorMail, errorVar)
	else:
		transLink = '<a href="https://landadvisors.my.salesforce.com/{0}"><font color="green">{1} -- {2}</font></a><br>'.format(dHTML['DID'], dHTML['LOT'], dHTML['PID'])
		errorMail = '{0}{1}'.format(errorMail, transLink)
	if dHTML['CMM'] != '':
		errorMail = '{0}<font color="gray">Comment:   {1}</font><br><br>'.format(errorMail, dHTML['CMM'])
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
	elif oprType == 'TOP100':
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
		make_opr_map(dHTML['PID'])
		get_acres(row)
		get_classification(row)
		get_development_status(row)
		get_county(row)
		get_source(row)
		lao_activity(dHTML['PID'])
		get_seller_owner(row)
		get_beneficiary(row)

		# Comp fields
		
		if oprType == 'Comp':
			get_comp_fields(row, recipients_to)
			get_buyer(row)
			
			if get_lot_details() == False:  # Skip temporarily to figure out fix
				td.uInput('\n Skipped making OPR cuz missing Price per Lot in Lot Details...Continue...')
				continue

		# Top 100 Fields
		elif oprType == 'TOP100':
			get_top100_fields()
			get_listing_comps_table(row, oprType, market)
		# P&Z Fields
		elif oprType == 'P&Z':
			get_pnz_fields(row)
		# Listing Fields
		elif oprType == 'Listing':
			get_listing_fields(row)
			get_listing_comps_table(row, oprType, market)
		elif oprType == 'AXIOPIPE':
			get_axio_pipeline_fields()
			get_listing_comps_table(row, oprType, market)

		get_links()
		get_opr_title(oprType, recipients_to)

		html = get_html_template(oprType)
		
		# Send OPR to Market recipients
		if SENDLIST.upper() != 'Q': # Skip sending OPRs if sending QC
			# Check if OPR has been QC'd
			if len(SENDLIST) >= 3:
				if qc_complete_verification(dHTML['PID'], 'Read') is False:
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
			html_filename = f'C:/TEMP/{dHTML["PID"]}_{dHTML["LOT"]}_OPR.html'
			with open(html_filename, 'w', encoding='utf-8') as f:
				f.write(body)
			print(f'\n Saved {html_filename} file.')

			# print(f"Subject: {subject}")
			# print(f"Sender: {sender_email}")
			# print(f"Recipients To: {recipients_to}")
			# print(f"Recipients CC: {recipients_cc}")
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')

			dSend_results = emailer.send_email_ses(subject, body, sender_email, recipients_to, cc=recipients_cc, bcc=None, attachments=None)
			# Change OPR Sent date to today if OPR successfuly sent
			if SENDLIST.upper() != 'T' and dSend_results['success'] is True:
				mark_deal_as_sent(today, dHTML['DID'])
			# Add OPR to QC list
			if SENDLIST.upper() == 'T':
				qc_complete_verification(dHTML['PID'], 'Write')
				# if dHTML['PID'] not in lOPR_qc:
				# 	lOPR_qc.append(dHTML['PID'])

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

