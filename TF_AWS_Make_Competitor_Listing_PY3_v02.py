# Make a TF record a Competitor Listing

# from amp import isOwnerIndexPIDExist, createOPRMap
from pprint import pprint
import acc
import aws
import bb
from datetime import datetime, timedelta
import dicts
import fun_login
import fun_text_date as td
import lao
import mpy
from os import system
import shutil
import sys
import webs

td.console_title('Make Competitor Listing PY3 v01')
service = fun_login.TerraForce()

# dTF DICT ********************************************************************
dTF = dicts.get_blank_tf_deal_dict()
dTF['type'] = 'lda_Opportunity__c'
# Set Record Type to Research
# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
dTF['RecordTypeID'] = '012a0000001ZSS8AAO'  # Research
dTF['OPR_Sent__c'] = '1964-09-11'
# Add Researcher OwnerId to record
dTF['OwnerId'] = bb.createdByResearch(service)
# ******************************************************************************

# LISTING SOURCE *******************************************************************
# Enter CoStar ID if source is CoStar
td.banner('Make Competitor Listing PY3 v01')
print(' LISTING SOURCE\n')
print('  0) Agent Brochure')
print('  1) Loopnet')
print('  2) CREXi')
print(' 00) Quit')
ui = td.uInput('\n Select the source > ')
if ui == '1':
	dTF['Source__c'] = u'Loopnet'
	ui = td.uInput('\n Enter Source ID > ')
	
	# TerraForce Query
	fields = 'default'
	wc = "Source_ID__c = '{0}'".format(ui)
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	if results == []:
		dTF['Source_ID__c'] = ui
	else:
		td.uInput('\n Listing already exists in TF...Continue...')
		sys.exit()
elif ui == '2':
	dTF['Source__c'] = u'CREXi'
	ui = td.uInput('\n Paste CREXi property URL > ')

	# Check if ID exits
	# fields = 'Id'
	# wc = "Source_ID__c = '{0}'".format(ui)
	# qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
	# results = bb.sfquery(service, qs)

	# TerraForce Query
	fields = 'default'
	wc = "Source_ID__c = '{0}'".format(ui)
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	if results == []:
		dTF['Source_ID__c'] = ui
	else:
		td.warningMsg('\n Listing already exists in TF.')
		td.uInput('\n Continue...')
		sys.exit()
elif ui == '00':
	exit('\n Terminating program...')
else:
	print('\n Agent Brochure...')
# ******************************************************************************

# GET PID OID ******************************************************************
aws.get_m1_file_copy(action='DOWN')
PID, OID = aws.read_Write_PID_OID(PID='Read', OID='Read')
# Open PID in browser
webs.open_pid_did(service, PID)
# ******************************************************************************

# CONFIRM PID ******************************************************************
td.banner('Make Competitor Listing PY3 v01')
while 1:
	print('\n PID: {0}'.format(PID))
	ui = td.uInput('\n Use this PID or type a new one [0/1/00] > ')
	if ui == '1' or ui == '':
		break
	elif ui == '0':
		PID = td.uInput('\n Type the PID > ').strip()
		webs.open_pid_did(service, PID)
	elif ui == '00':
		exit('\n Terminating program...')
	elif len(ui) > 3:
		PID = ui.strip()
		webs.open_pid_did(service, PID)
	else:
		td.warningMsg('\n Invalid entry...try again...')
		lao.sleep(2)
# ******************************************************************************

# SPLIT ************************************************************************
# Ask if PID needs to be split
ui = td.uInput('\n Split PID {0}? [0/1/00] > '.format(PID))
if ui == '1':
	PID = bb.splitDeal(service, PID)
	
	aws.split_PID_Instructions()
	# Assign new Lead PID attributest to polygon
	aws.make_AWS_Split_OwnerIndex_Update_Attributes_for_New_PID(OID, PID, runASW=True)
	# Color cmd window green
	system('color 2f') # green with white letters
elif ui == '00':
	exit('\n Terminating program...')
# ******************************************************************************

# OKAY TO EDIT ******************************************************************
# TerraForce Query
fields = 'default'
wc = "PID__c = '{0}'".format(PID)
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

dTF['Id'] = results[0]['Id']
DID = dTF['Id']

# Check for Type as LAO Exclusive
if results[0]['Type__c'] == 'Exclusive LAO':
	td.warningMsg('\n ***WARNING***\n\n Deal Type is Exclusive LAO!\n\n Change to --None-- and contunue.')
	td.uInput('\n Continue...')

# Check if Stage Name is Lead
if results[0]['StageName__c'] != 'Lead':
	print('\n *** WARNING! ***')
	print('\n Stage Name is {0}'.format(results[0]['StageName__c']))
	ui = td.uInput('\n Change Stage Name and [Enter] or [00] to Quit > ')
	if ui == '00':
		exit()
# ******************************************************************************

# OWNER INFO *******************************************************************
dTF['Owner_Entity__c'] = results[0]['Owner_Entity__c']
dTF['AccountId__c'] = results[0]['AccountId__c']
# ******************************************************************************

# ENTER TF INFO ****************************************************************
# Enter Acres
dTF['Acres__c'] = results[0]['Acres__c']
print('\n TF Acres: {0}'.format(dTF['Acres__c']))
ui = td.uInput('\n Change Acres or [Enter] to use existing [00] > ')
if ui != '':
	dTF['Acres__c'] = float(ui)
elif ui == '00':
	exit('\n Terminating program...')

# Enter List Price as full price or $/Ac
dTF['List_Price__c'] = td.uInput('\n List Price, add "ac" if $/ac or [Enter] for not available [00] > ')
if dTF['List_Price__c'] == '':
	dTF['List_Price__c'] = 10000
elif 'AC' in dTF['List_Price__c'].upper():
	dTF['List_Price__c'] = dTF['List_Price__c'].replace('$', '').replace(',', '')
	dTF['List_Price__c'] = dTF['List_Price__c'].replace('AC', '').replace('ac', '')
	dTF['List_Price__c'] = dTF['List_Price__c'].strip()
	dTF['List_Price__c'] = float(dTF['List_Price__c']) * float(dTF['Acres__c'])
elif dTF['List_Price__c'] == '00':
	exit('\n Terminating program...')
else:
	dTF['List_Price__c'] = dTF['List_Price__c'].replace('$', '').replace(',', '')
	dTF['List_Price__c'] = dTF['List_Price__c'].strip()

# Enter Listing Date
while 1:
	print('\n Date format Month Day Year no punctuation (013113 = Jan. 31, 2013)')
	list_date = td.uInput('\n Type Listing Date or [ENTER] for todays date > ')
	if list_date == '':
		# list_date = lao.todayDate()
		list_date = td.today_date()
		break
	else:
		list_date = list_date.replace('/', '').replace('\\', '').replace('-', '')
		MO = list_date[:2]
		DY = list_date[2:4]
		YR = list_date[4:]
		if len(list_date) == 6:
			list_date = '20%s-%s-%s' % (YR, MO, DY)
			break
		elif len(list_date) == 8:
			list_date = '%s-%s-%s' % (YR, MO, DY)
			break
		else:
			print('Invalid date format, try again...')

# Calculate Listing Expiration Date
expired_date = datetime.strptime(list_date, '%Y-%m-%d')
expired_date = expired_date + timedelta(days=180)
expired_date = expired_date.strftime('%Y-%m-%d')
dTF['List_Date__c'] = list_date
dTF['Listing_Expiration_Date__c'] = expired_date

# Enter Zoning
ui = td.uInput('\n Add Zoning or [Enter] for none > ')
if ui != '':
	dTF['Zoning__c'] = ui.upper()
else:
	dTF['Zoning__c'] = 'None'

# Populate Deal Details
dTF = bb.populate_deal_details(dTF, is_sale_record=False)


#Update the PID
bb.tf_update_3(service, dTF)

# ******************************************************************************

# ENTER AGENT INFO *************************************************************
# Enter Listing Agent
endloop = False
dAcc = dicts.get_blank_account_dict()
dAcc['ENTITY'] = td.uInput('\n Enter Listing Agent or Company > ')
while endloop is False:
	td.banner('Select Listing Agent/Company')
	print('\n Listing Agent or Company:  {0}'.format(dAcc['ENTITY']))

	dAcc = acc.find_create_account_entity(service, dAcc)

	if dAcc['EID'] != 'None' and dAcc['AID'] == 'None':
		dAcc['NAME'], dAcc['AID'] = acc.find_persons_of_entity(service, dAcc['EID'])
	if dAcc['AID'] == 'None':
		temp1, temp2, dAcc = acc.find_create_account_person(service, dAcc)
		
	# Add Listing Agent's firm if blank
	# fields = 'Id, Company__c, Name, BillingCity, BillingState'
	# wc = "Id = '{0}'".format(SPRID)
	# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	# results = bb.sfquery(service, qs)
	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(dAcc['AID'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	if results[0]['Company__c'] == '':
		city = results[0]['BillingCity']
		state = results[0]['BillingState']
		td.warningMsg('\n Listing Agents Company/Firm is blank.')
		ui = td.uInput('\n Enter Listing Agents Firm or [0] for none > ')
		if ui == '0' or ui == '':
			pass
		else:
			dAcc = acc.find_create_account_entity(service, dAcc)
			upd = {}
			upd['type'] = 'Account'
			upd['Id'] = dAcc['AID']
			upd['Company__c'] = dAcc['Company__c']
			# upResults = bb.sfupdate(service, upd)
			upResults = bb.tf_update_3(service, upd)

	# Create Commission Object for Competing Agent
	dCommission = {}
	dCommission['DealID__c'] = dTF['Id']
	dCommission['type'] = 'lda_Commission__c'
	dCommission['Agent_Order__c'] = 1
	dCommission['Agent__c'] = dAcc['AID']
	
	# Create Commission record
	results = bb.tf_create_3(service, dCommission)
	print('\n {0} added to Commissions'.format(dAcc['NAME']))

	# Add another Listing Agent
	while 1:
		print('\n Type another Listing Agent or [Enter] to continue...')
		listingAgent = td.uInput('\n > ')
		if listingAgent == '':
			endloop = True
			break
		elif len(listingAgent) > 3:
			dAcc['NAME'] = listingAgent
			dAcc['AccountId__c'] = 'None'
			break
		else:
			td.warningMsg('\n Invalid entry...try again...')
			lao.sleep(2)
# ******************************************************************************

# UPLOAD PACKAGE  *****************************************************************
# Add Competitors Package
package_new_fileName = ''
while 1:
	td.banner("Add Competitor's Package")
	ui = td.uInput('\n Add Competitor Package? [0/1/00] > ')
	if ui == '1':
		package_new_fileName = aws.upload_listing_package_to_aws(service, PID)
		break
	elif ui == '0':
		print('\n No package added...')
		break
	elif ui == '00':
		exit('\n Terminating program...')
	else:
		td.warningMsg('\n Invalid input...try again')
# ******************************************************************************


# Open the PID in browser
webs.open_pid_did(service, DID)

# Create OPR Map
mpy.make_opr_map_api(service, PID)

exit()