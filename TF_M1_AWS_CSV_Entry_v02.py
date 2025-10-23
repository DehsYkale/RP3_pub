# Import data from TF formated CSV (CSV_TF_Formater_v##.py) into TF


import acc
import aws
import bb
from bs4 import BeautifulSoup
from colored import Fore, Back, Style
from datetime import datetime
import dicts
import fjson
import fun_login
import fun_text_date as td
td.banner('TF M1 AWS CSV Entry v02')
import lao
import mpy
from pprint import pprint
from time import sleep
from sys import exit
import sys
from webbrowser import open as openbrowser
from webs import selenium_LAO_Data_Sites_Login
from webs import getReonomyReportHTML, getEntityContact

# Assign TF Field Values to a new Record
def assignTFfieldsFromSpreadsheet(dTF):
	lao.print_function_name('script def assignTFfieldsFromSpreadsheet')

	# Deal Dict, Seller Dict, Buyer Dict, Offer Dict, Print Dict, Commission Dict
	sdAcc = dicts.get_blank_account_dict()
	bdAcc = dicts.get_blank_account_dict()
	dOffer, dPrint, dCommision = {}, {}, {}

	# Seller Dictionary
	sdAcc['ENTITY'], dPrint['Seller_Entity'] = dTF['Seller Entity'], dTF['Seller Entity']
	sdAcc['NAME'], dPrint['Seller_Person'] = dTF['Seller Person'], dTF['Seller Person']
	sdAcc['STREET'] = dTF['Seller Street']
	sdAcc['CITY'] = dTF['Seller City']
	sdAcc['STATE'] = dTF['Seller State']
	sdAcc['ZIPCODE'] = dTF['Seller Zip']
	sdAcc['COUNTRY'] = dTF['Seller Country']
	sdAcc['PHONE'] = dTF['Seller Phone']
	sdAcc['EMAIL'] = dTF['Seller Email']
	
	# Buyer Dictionary
	bdAcc['ENTITY'], dPrint['Buyer_Entity'] = dTF['Buyer Entity'], dTF['Buyer Entity']
	bdAcc['NAME'], dPrint['Buyer_Person'] = dTF['Buyer Person'], dTF['Buyer Person']
	bdAcc['STREET'] = dTF['Buyer Street']
	bdAcc['CITY'] = dTF['Buyer City']
	bdAcc['STATE'] = dTF['Buyer State']
	bdAcc['ZIPCODE'] = dTF['Buyer Zip']
	bdAcc['COUNTRY'] = dTF['Buyer Country']
	bdAcc['PHONE'] = dTF['Buyer Phone']
	bdAcc['Email'] = dTF['Buyer Email']

	if dTF['Acres__c'] == 'None':
		dTF['Acres__c'], dPrint['Acres'] = 0, 0
	else:
		dTF['Acres__c'], dPrint['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])
	if dTF['City__c'] == 'None':
		dPrint['CITY'] = 'None'
	else:
		dPrint['CITY'] = dTF['City__c']
	dPrint['Classification'] = dTF['Classification__c']
	if dTF['Country__c'] == 'None':
		dTF['Country__c'] = 'United States'
	if dTF['County__c'] == 'None':
		td.warningMsg('\n No County listed in data! Terminating program...')
		exit()
	else:
		dTF['County__c'] = dTF['County__c'].replace(' ', '')  # Remove spaces from county name
		dPrint['County'] = dTF['County__c']
	if dTF['Latitude__c'] != 'None':
		dTF['Latitude__c'], dPrint['Latitude'] = (dTF['Latitude__c']).strip(), (dTF['Latitude__c']).strip()
	else:
		dPrint['Latitude'] = 'None'
	dTF['Lead_Parcel__c'], dPrint['Lead_Parcel'] = (dTF['Lead_Parcel__c']).strip(' '), (dTF['Lead_Parcel__c']).strip(' ')
	dPrint['Location'] = dTF['Location__c']
	if dTF['Longitude__c'] == 'None':
		dPrint['Longitude'] = 'None'
	else:
		dTF['Longitude__c'], dPrint['Longitude'] = (dTF['Longitude__c']).strip(), (dTF['Longitude__c']).strip()
	if dTF['Lots__c'] == 'None':
		dPrint['Lots'] = 'None'
	else:
		dTF['Lots__c'], dPrint['Lots'] = int(dTF['Lots__c']), int(dTF['Lots__c'])
	dPrint['Parcels'] = dTF['Parcels__c']
	dPrint['PID'] = 'New'
	if dTF['Recorded_Instrument_Number__c'] == 'None':
		dPrint['RDN'] = 'None'
	else:
		dPrint['RDN'] = dTF['Recorded_Instrument_Number__c']
	if dTF['Sale_Date__c'] != 'None': # and dTF['Sale_Price__c'] != 'None':
		sDate = td.date_engine(dTF['Sale_Date__c'])
		if datetime.now() > datetime.strptime(sDate, '%Y-%m-%d'):
			dTF['Sale_Date__c'], dPrint['Sale_Date'] = td.date_engine(dTF['Sale_Date__c']), td.date_engine(dTF['Sale_Date__c'])
			# row[39] = 'None'
		else:
			dPrint['Sale_Date'] = 'None'
	else:
		dPrint['Sale_Date'] = 'None'
	if dTF['Sale_Price__c'] == 'None':
		dTF['Sale_Price__c'], dPrint['Sale_Price'] = '10000', 'None'
	else:
		salePrice = (dTF['Sale_Price__c']).replace('$', '').replace(',', '')
		dTF['Sale_Price__c'], dPrint['Sale_Price'] = salePrice, salePrice
	if dTF['Source__c'] == 'None':
		dTF['Source__c'] = 'LAO'
	dPrint['Source_ID'] = dTF['Source_ID__c']
	if dTF['State__c'] == 'None':
		dTF['STATE'] = lao.get_state_of_market(dTF['Market__c'], dTF['County__c'])
	if len(dTF['State__c']) == 2:
		dTF['State__c'] = td.convert_state(dTF['State__c'])
	dPrint['Subdivision'] = dTF['Subdivision__c']
	dPrint['Zoning'] = dTF['Zoning__c']
	if dTF['List_Date__c'] == 'None':
		dPrint['List_Date'] = 'None'
	else:
		dTF['List_Date__c'] = td.date_engine(dTF['List_Date__c'])
		dPrint['List_Date'] = dTF['List_Date__c']
	if dTF['List_Price__c'] == 'None':
		dPrint['List_Price'] = 'None'
	else:
		dPrint['List_Price'] = dTF['List_Price__c']
		dTF['List_Price__c'] = (dTF['List_Price__c']).replace('$', '').replace(',', '')
		if int(dTF['List_Price__c']) == 0:
			dTF['List_Price__c'] = 10000
			dPrint['List_Price'] = '$10,000'
	if '$' in dTF['Terms__c']:
		del dTF['Terms__c']
	if dTF['Sale_Date__c'] == 'None' or dTF['Sale_Price__c'] == 'None':
		if dTF['MLS Status'] == 'Sold':
			dTF['OPR_Sent__c'] = '1965-01-11'
		else:
			dTF['OPR_Sent__c'] = '1964-09-11'
	else:
		dTF['OPR_Sent__c'] = '1965-01-11'


	# Default Fields
	dTF['RecordTypeID'] = '012a0000001ZSS8AAO' # Research Type
	dTF['type'] = 'lda_Opportunity__c'
	dTF['Verified__c'] = True

	dPrint['Status'] = dTF['MLS Status']

	# Offer Dictionary
	if dTF['Sale_Date__c'] != 'None' and dTF['Sale_Price__c'] != 'None' and dPrint['Status'] == 'Sold':
		dOffer['type'] = 'lda_Offer__c'
		dOffer['Offer_Price__c'] = dTF['Sale_Price__c']
		dOffer['Offer_Date__c'] = dTF['Sale_Date__c']
		dOffer['Offer_Status__c'] = 'Accepted'
		dOffer['Date_Accepted__c'] = dTF['Sale_Date__c']
	# Listing and Selling Agents
	dPrint['ListEntity'] = dTF['List Entity']
	dPrint['ListAgent'] = dTF['List Agent']
	dPrint['SellAgent'] = dTF['Buyer Agent']
	# Commission Listing Agent Dict
	dCommision['Agent'] = dTF['List Agent']
	dCommision['AgentPhone'] = dTF['List Agent Phone']
	dCommision['AgentEmail'] = dTF['List Agent Email']
	# Mortgage/Deed of Trust Info
	if dTF['Lender'] != 'None' and dTF['Loan_Amount__c'] != 'None':
		dTF['Beneficiary__c'], dPrint['Beneficiary__c'] = dTF['Lender'], dTF['Lender']
		dTF['Loan_Amount__c'] = dTF['Loan_Amount__c'].replace('$', '').replace(',', '')
		if dTF['Loan_Date__c'] != 'None':
			dTF['Loan_Date__c'] = td.date_engine(dTF['Loan_Date__c'])
	else:
		del dTF['Loan_Amount__c']
		del dTF['Loan_Date__c']

	return dTF, sdAcc, bdAcc, dOffer, dPrint, dCommision

# Assign TF Field Values to an existing Lead
def assignTFfieldsFromLeadDeal(dTF, dLead, sdAcc, bdAcc):
	lao.print_function_name('script def assignTFfieldsFromLeadDeal')

	# Check if Acres is different from TF record
	if float(dLead['Acres__c']) >= 0 and dTF['Acres__c'] == 'None':
		skipping = 0
	elif float(dLead['Acres__c']) != float(dTF['Acres__c']):
		printinfo(dPrint, 'acres')
		print(' Choose Acres value:\n\n 1) {0:15}{1}\n 2) {2:15}{3}\n Or Type in Acres'.format('TerraForce', dLead['Acres__c'], dTF['Source__c'], dTF['Acres__c']))
		ui = td.uInput('\n Select or Type > ')
		if ui == '2':
			dTF['Acres__c'], dPrint['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])
		elif ui == '1' or ui == '':
			dTF['Acres__c'], dPrint['Acres'] = float(dLead['Acres__c']), float(dLead['Acres__c'])
		else:
			dTF['Acres__c'], dPrint['Acres'] = float(ui), float(ui)
	else:
		dTF['Acres__c'], dPrint['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])

	# Use existing owner from TF record
	# sdAcc = {}
	printinfo(dPrint, 'seller')
	print(f' Existing Owner of PID {dLead['PID__c']}\n')
	if dLead['Owner_Entity__r'] != 'None':
		print(' Entity: {0}\n'.format(dLead['Owner_Entity__r']['Name']))
	else:
		print(' Entity: None')
	if dLead['AccountId__r'] != 'None':
		print(' Person: {0}\n'.format(dLead['AccountId__r']['Name']))
	else:
		print(' Person: None')

	while 1:
		print('\n Select Roll')
		print('\n  1] Seller')
		print('  2] Buyer')
		print('  3] Neither')
		print(' 00] Quit')
		ui = td.uInput('\n Roll > ')
		if ui == '1':
			# Assign Ownership's Owner values to sdAcc
			if dLead['Owner_Entity__r'] != 'None':
				sdAcc['ENTITY'], dPrint['Seller_Entity'] = dLead['Owner_Entity__r']['Name'], dLead['Owner_Entity__r']['Name']
				sdAcc['EID'] = dLead['Owner_Entity__c']
				if dLead['Owner_Entity__r']['BillingStreet'] != 'None':
					sdAcc['STREET'] = dLead['Owner_Entity__r']['BillingStreet']
					sdAcc['CITY'] = dLead['Owner_Entity__r']['BillingCity']
					sdAcc['STATE'] = dLead['Owner_Entity__r']['BillingState']
					sdAcc['ZIPCODE'] = dLead['Owner_Entity__r']['BillingPostalCode']
				if dLead['Owner_Entity__r']['Phone'] != 'None':
					sdAcc['PHONEENTITY'] = dLead['Owner_Entity__r']['Phone']
			if dLead['AccountId__r'] != 'None':
				sdAcc['NAME'], dPrint['Seller_Person'] = dLead['AccountId__r']['Name'], dLead['AccountId__r']['Name']
				sdAcc['AID'] = dLead['AccountId__c']
				if dLead['AccountId__r']['BillingStreet'] != 'None' and sdAcc['STREET'] == 'None':
					sdAcc['STREET'] = dLead['AccountId__r']['BillingStreet']
					sdAcc['CITY'] = dLead['AccountId__r']['BillingCity']
					sdAcc['STATE'] = dLead['AccountId__r']['BillingState']
					sdAcc['ZIPCODE'] = dLead['AccountId__r']['BillingPostalCode']
				sdAcc['PHONE'] = dLead['AccountId__r']['Phone']
				sdAcc['MOBILE'] = dLead['AccountId__r']['PersonMobilePhone']
				sdAcc['EMAIL'] = dLead['AccountId__r']['PersonEmail']

			# useExistingOwner = False
			break
		elif ui == '2':
			# Assign Ownership's Owner values to bdAcc
			if dLead['Owner_Entity__r'] != 'None':
				bdAcc['ENTITY'], dPrint['Buyer_Entity'] = dLead['Owner_Entity__r']['Name'], dLead['Owner_Entity__r']['Name']
				bdAcc['EID'] = dLead['Owner_Entity__c']
				if dLead['Owner_Entity__r']['BillingStreet'] != 'None':
					bdAcc['STREET'] = dLead['Owner_Entity__r']['BillingStreet']
					bdAcc['CITY'] = dLead['Owner_Entity__r']['BillingCity']
					bdAcc['STATE'] = dLead['Owner_Entity__r']['BillingState']
					bdAcc['ZIPCODE'] = dLead['Owner_Entity__r']['BillingPostalCode']
				if dLead['Owner_Entity__r']['Phone'] != 'None':
					bdAcc['PHONEENTITY'] = dLead['Owner_Entity__r']['Phone']
			if dLead['AccountId__r'] != 'None':
				bdAcc['NAME'], dPrint['Buyer_Person'] = dLead['AccountId__r']['Name'], dLead['AccountId__r']['Name']
				bdAcc['AID'] = dLead['AccountId__c']
				if dLead['AccountId__r']['BillingStreet'] != 'None' and bdAcc['STREET'] == 'None':
					bdAcc['STREET'] = dLead['AccountId__r']['BillingStreet']
					bdAcc['CITY'] = dLead['AccountId__r']['BillingCity']
					bdAcc['STATE'] = dLead['AccountId__r']['BillingState']
					bdAcc['ZIPCODE'] = dLead['AccountId__r']['BillingPostalCode']
				bdAcc['PHONE'] = dLead['AccountId__r']['Phone']
				bdAcc['MOBILE'] = dLead['AccountId__r']['PersonMobilePhone']
				bdAcc['EMAIL'] = dLead['AccountId__r']['PersonEmail']
			# useExistingOwner = True
			# print('\n Using existing Owner...\n')
			break
		elif ui == '3':
			break
		elif ui == '00':
			exit(' Terminating program...')
		else:
			print('Invalid input...try again...')

	# print('here1')
	# pprint(sdAcc)
	# print('here2')
	# pprint(bdAcc)
	# print('here3')
	# pprint(dLead)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	# Seller Dictionary
	# if useExistingOwner is False:
	# 	sdAcc['ENTITY'], dPrint['Seller_Entity'] = 'None', 'None'
	# 	sdAcc['NAME'], dPrint['Seller_Person'] = 'None', 'None'
	# 	sdAcc['STREET'] = 'None'
	# 	sdAcc['CITY'] = 'None'
	# 	sdAcc['STATE'] = 'None'
	# 	sdAcc['ZIPCODE'] = 'None'
	# 	sdAcc['COUNTRY'] = 'None'
	# 	sdAcc['PHONE'] = 'None'
	# 	sdAcc['EMAIL'] = 'None'
	# 	dLead['Name'] = 'NeedDealName'


	# if dLead['City__c'] == '' and dTF['City__c'] != 'None':
	# 	dTF['City__c'] = row[20]
	if dLead['City__c'] != dTF['City__c']:
		dTF['City__c'], dPrint['CITY'] = dTF['City__c'], dTF['City__c']
	else:
		dPrint['CITY'] = 'None'

	# Classification
	dTF['Classification__c'], dPrint['Classification'] = dLead['Classification__c'], dLead['Classification__c']

	# Development Status
	dTF['Development_Status__c'] = dLead['Development_Status__c']

	dPrint['County'] = dTF['County__c']
	if dLead['Description__c'] != '' and dTF['Description__c'] != 'None':
		dTF['Description__c'] = '{0}\n{1}'.format(dLead['Description__c'], dTF['Description__c'])

	dTF['Location__c'] = dLead['Location__c']

	dTF['Longitude__c'] = dLead['Longitude__c']
	dTF['Latitude__c'] = dLead['Latitude__c']

	if dLead['Lot_Description__c'] != '' and dTF['Lot_Description__c'] != 'None':
		dTF['Lot_Description__c'] = '{0}\n{1}'.format(dLead['Lot_Description__c'], dTF['Lot_Description__c'])

	if dLead['Lots__c'] == 0 and dTF['Lots__c'] != 'None':
		dPrint['Lots'] = dTF['Lots__c']

	if dTF['Recorded_Instrument_Number__c'] != 'None':
		dPrint['RDN'] = dTF['Recorded_Instrument_Number__c']
	else:
		dTF['Recorded_Instrument_Number__c'], dPrint['RDN'] = '', 'None'

	if dTF['Sale_Date__c'] != 'None':
		# Remove Sale Date if it is in the future
		sDate = td.date_engine(dTF['Sale_Date__c'])
		if datetime.now() > datetime.strptime(sDate, '%Y-%m-%d'):
			dTF['Sale_Date__c'] = sDate
		else:
			dTF['Sale_Date__c'] = 'None'

	if dTF['Sale_Price__c'] != 'None':
		dTF['Sale_Price__c'] = (dTF['Sale_Price__c']).replace('$', '').replace(',', '')

	if dTF['Source__c'] == 'None':
		dTF['Source__c'] = 'LAO'

	if dTF['Source_ID__c'] != 'None':
		dPrint['Source_ID'] = dTF['Source_ID__c']
	else:
		dPrint['Source_ID'] = 'None'

	if dLead['Subdivision__c'] != '':
		dTF['Subdivision__c'] = dLead['Subdivision__c']

	if dLead['Zipcode__c'] != '':
		dTF['Zipcode__c'] = dLead['Zipcode__c']

	dPrint['Zoning'] = dTF['Zoning__c']

	# Add List Date
	if dTF['List_Date__c'] != 'None':
		dTF['List_Date__c'] = td.date_engine(dTF['List_Date__c'])
		dPrint['List_Date'] = dTF['List_Date__c']
	else:
		dPrint['List_Date'] = 'None'

	# Add List Price
	if dTF['List_Price__c'] != 'None':
		dTF['List_Price__c'], dPrint['List_Price'] = (dTF['List_Price__c']).replace('$', '').replace(',', ''), dTF['List_Price__c']
		if int(dTF['List_Price__c']) == 0:
			dTF['List_Price__c'] = 10000
			dPrint['List_Price'] = '$10,000'
	else:
		dPrint['List_Price'] = 'None'

	dPrint['Status'] = dTF['MLS Status']

	# Default Fields
	dTF['Id'] = dLead['Id']

	if dTF['Sale_Date__c'] == 'None' or dTF['Sale_Price__c'] == 'None':
		if dTF['MLS Status'] == 'Sold':
			dTF['OPR_Sent__c'] = '1965-01-11'
		else:
			dTF['OPR_Sent__c'] = '1964-09-11'
	else:
		dTF['OPR_Sent__c'] = '1965-01-11'

	dTF['RecordTypeID'] = '012a0000001ZSS8AAO' # Research Type
	dTF['type'] = 'lda_Opportunity__c'

	return dTF, sdAcc, sdAcc, bdAcc

# User to choose what to do with record
def choose_action_for_record(dTF, dLead):
	lao.print_function_name('script def choose_action_for_record')

	while 1:
		print('\n APN location copied to ArcMap...\n\n [S]kip For All Enternity\n [I]n Progress\n [Enter] to Process New Deal\n [Type in a PID]\n [00] Quit')
		ui = td.uInput('\n Select > ').upper()
		ui = ui.strip()
		if ui == 'S':
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			dLead = 'Skip'
			break
		elif ui == 'I':
			print('In progress will reasearch later...')
			dLead = 'Skip'
			break
		elif ui == '':
			print('Processing new Deal...')
			break
		# User input an existing PID
		elif len(ui) > 2:
			# Check if LAO Deal or non-existing PID number
			if bb.isLAODeal(service, ui) == 'Try Again':
				continue
			dPrint['PID'] = ui
			# Check if PID is to be split and split if true
			ui_split = td.uInput('\n Split this PID? [0/1] > ')
			if ui_split == '1':
				ui = bb.splitDeal(service, ui)
				dPrint['PID'] = ui
			# Write existing PID info to ld dictionary
			dLead = selectLeadRecordByPID(dPrint['PID'])
			# Check for Type as LAO Exclusive
			if dLead['Type__c'] == 'Exclusive LAO':
				td.warningMsg('\n ***WARNING***\n\n Deal Type is Exclusive LAO!')
				td.uInput('\n Continue...')
			# Check for if Deal is a Lead
			if dLead['StageName__c'] != 'Lead':
				td.warningMsg('\n ***WARNING***\n\n Deal Stage Name is {0}!'.format(dLead['StageName__c']))
				td.uInput('\n Continue...')
			break
		elif ui == '00':
			sys.exit(' Terminating program...')
		else:
			print('\nInvalid input...try again...')
	return dTF, dLead

# Add unknown Seller or Buyer
def unknownSellerBuyer(name):
	lao.print_function_name('script def unknownSellerBuyer')

	nameCaps = name.upper()
	if 'UNKNOWN' in nameCaps:
		ui = td.uInput('\n[Enter] to use Unknown or enter new name > ')
	else:
		return name
	if ui == '':
		if nameCaps == 'UNKNOWN IDAHO SELLER':
			return '0011300001cut4H'
		elif nameCaps == 'UNKNOWN RIVERSIDE':
			return 'Unknown Riverside'
	else:
		return ui

# Set the value of Buyer Acting As field
def buyerActingAs(dTF):
	lao.print_function_name('script def buyerActingAs')

	print('\n Buyer Acting As...\n')
	print(' 1) Homebuilder\n 2) Inv/Dev\n 3) Lot Banker\n 4) User')
	dTF['Buyer_Acting_As__c'] = 'None'
	while dTF['Buyer_Acting_As__c'] == 'None':
		ui = td.uInput('\nSelect > ')
		if ui == '1':
			dTF['Buyer_Acting_As__c'] = 'Homebuilder'
		elif ui == '2':
			dTF['Buyer_Acting_As__c'] = 'Inv/Dev'
		elif ui == '3':
			dTF['Buyer_Acting_As__c'] = 'Lot Banker'
		elif ui == '4':
			dTF['Buyer_Acting_As__c'] = 'User'
		else:
			td.warningMsg('\n Invalid input...try again...')

# Print the important info
def printinfo(dPrint, hiLight='None'):
	lao.print_function_name('script def printinfo')

	# print('{0}{1}{2}'.format(fg('yellow_2'), text, Style.reset))
	recordsleft = totalRecords - currentRecord

	td.banner('TF M1 AWS CSV Entry v02 Row: {0} : {1} : {2}'.format(totalRecords, currentRecord, recordsleft))

	if hiLight == 'start':
		td.colorText(' Status:   {0:30}  PID:   {1}'.format(dPrint['Status'], dPrint['PID']), 'YELLOW')
	else:
		print(' Status:   {0:30}  PID:   {1}'.format(dPrint['Status'], dPrint['PID']))
	print(' County:   {0:30}  City:  {1}\n'.format(dPrint['County'], dPrint['CITY']))
	if hiLight == 'acres':
		acresColor = Fore.yellow_2
		# td.colorText(' Acres:    {1}'.format(dPrint['Acres'], 'YELLOW'))
		print('{0} Acres:    {1:<30}{2}  Lead Par: {3}'.format(acresColor, dPrint['Acres'], Style.reset, dPrint['Lead_Parcel']))
	else:
		# print(' Acres:    {0}'.format(dPrint['Acres']))
		print(' Acres:    {0:<30}  Lead Par: {1}'.format(dPrint['Acres'], dPrint['Lead_Parcel']))
	# print(' Lead Par: {0:30}'.format(dPrint['Lead_Parcel']))
	print(' Parcles:  {0}\n'.format(dPrint['Parcels']))
	sellerColor = ''
	buyerColor = ''
	if hiLight == 'seller':
		sellerColor = Fore.yellow_2
	if hiLight == 'buyer':
		buyerColor = Fore.yellow_2
	print('{0} Seller    {1:30}{2}  {3}Buyer{4}'.format(sellerColor, '', Style.reset, buyerColor, Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPrint['Seller_Entity'], Style.reset, buyerColor, dPrint['Buyer_Entity'], Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPrint['Seller_Person'], Style.reset, buyerColor, dPrint['Buyer_Person'], Style.reset))
	menuColor = ''
	if hiLight == 'listingagent':
		menuColor = Fore.yellow_2
	print('{0}  Agnt {1:35}  {2}{3}'.format(menuColor,dPrint['ListAgent'], dPrint['SellAgent'], Style.reset))
	menuColor = ''
	if 'Beneficiary__c' in dPrint:
		if hiLight == 'beneficiary':
			print('{0}'.format(Fore.yellow_2))
		else:
			print('{0}'.format(Style.reset))
		print('Beneficiary')
		print('  {0}'.format(dPrint['Beneficiary__c']))
		print('{0}'.format(Style.reset))
	else:
		print('{0}'.format(Style.reset))
	print(' Lots:     {0}'.format(str(dPrint['Lots'])))
	if hiLight == 'classification':
		menuColor = Fore.yellow_2
	print('{0} Class:    {1}{2}'.format(menuColor, dPrint['Classification'], Style.reset))
	menuColor = ''
	print(' ')
	print(' Date:     {0:<30}  List Date:  {1}'.format(dPrint['Sale_Date'], dPrint['List_Date']))
	print(' Price:    {0:<30}  List Price: {1}'.format(td.currency_format_from_number(dPrint['Sale_Price']), td.currency_format_from_number(dPrint['List_Price'])))
	print(' ')
	print(' Location: {0}'.format(dPrint['Location']))
	print(' Sub Name: {0}'.format(dPrint['Subdivision']))
	if 'Longitude' in dPrint:
		print(' Lon Lat:  {0} {1}'.format(dPrint['Longitude'], dPrint['Latitude']))
	else:
		print(' Lon Lat: None')
	print(' SourceID: {0}'.format(dPrint['Source_ID']))
	print(' Rec Doc:  {0}'.format(dPrint['RDN']))
	td.colorText('_________________________________________________________________________\n', 'BLUE')

# Confirm Data (NOT USED NOT COMPLETED)
def confirmData(dTF, dPrint):
	lao.print_function_name('script def confirmData')

	recordsleft = totalRecords - currentRecord

	fields = 'Id, Name, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone'
	wc = ""
	qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	results = bb.sfquery(service, qs)
	# fields = 'Id, Name, FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone, Fax, PersonMobilePhone, PersonEmail'
	
	print(' Seller: {0}'.format(dPrint['Seller_Entity']))

# Select the record of the Source ID
def selectLeadRecordByPID(pid):
	lao.print_function_name('script def selectLeadRecordByPID')

	while 1:
		pidLoop = False
		# TerraForce Query
		fields = 'default'
		wc = "PID__c = '{}'".format(pid)
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		if results == []:
			while 1:
				print('\n Could not find PID {0}\n')
				ui = td.uInput(' Enter PID again or 00 to quit > ')
				if ui == '00':
					exit(' Terminating program...\n\n fin')
				elif ui == '':
					print('\n Invalid input...try again...')
				else:
					pid = ui
					pidLoop = True
					break
		if pidLoop is False:
			break

	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(results[0]['Id']))
	#lao.setActiveWindow('CSV to TF')
	return results[0]

# If no Sale Price or if the Source ID already exists then skip record
def skipRecord(dTF, dPrint):
	lao.print_function_name('script def skipRecord')

	# Check if there is a sale price otherwise skip record
	if dPrint['Sale_Price'] == 'None' and dTF['State__c'] != 'Idaho' and dTF['State__c'] != 'Texas':
		td.warningMsg('\n No Sale Price, writing to skip file...Continue')
		if dTF['Source_ID__c'] != '':
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
		sleep(1)
		return 'Skip'
	print(' Condition Nominal Sale Price Exists...')

	# Check if there is a sale date otherwise skip record
	if dPrint['Sale_Date'] == 'None' and dTF['State__c'] != 'Idaho':
		td.warningMsg('\n No Sale Date, writing to skip file...Continue...')
		if dTF['Source_ID__c'] != '':
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
		sleep(1)
		return 'Skip'
	print(' Condition Nominal Sale Date Exists...')

	# Check if record Source ID exists in Skip file
	if dTF['Source_ID__c'] != '':
		if lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'CHECK'):
			# No need to print warning
			# print('\n Source ID found in Skip file...moving on...')
			print('Record found in Skip File: {0}'.format(dTF['Source_ID__c']))
			return 'Skip'
	print(' Condition Nominal Source ID not in Skip file...')

	# Check if record already entered by searching TF Source ID
	if dTF['Source_ID__c'] != '':
		fields = 'Id'
		wc = "Source_ID__c LIKE '%{0}%' AND County__c = '{1}'".format(dTF['Source_ID__c'], dTF['County__c'])
		# TerraForce Query
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		if results != []:
			td.warningMsg('\n Source ID found in TF Record file...writing to skip file & moving on...')
			# Enter record in dont_select_me_again.txt
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			sleep(1)
			print(' Record found in TF by Source ID: {0}'.format(dTF['Source_ID__c']))
			return 'Skip'
	print(' Condition Nominal Source ID not in TerraForce record...')

	# Check if record already entered by Source ID
	if dTF['Recorded_Instrument_Number__c'] != '':
		fields = 'Id'
		wc = "Recorded_Instrument_Number__c = '{}'".format(dTF['Recorded_Instrument_Number__c'])
		# TerraForce Query
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
		if results != []:
			td.warningMsg('\n Recorded Instrument Number found in TF Record file...writing to skip file & moving on...')
			# Enter record in dont_select_me_again.txt
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			sleep(1)
			print(' Record found in TF by Record Instrument Nubmer: {0}'.format(dTF['Recorded_Instrument_Number__c']))
			return 'Skip'
	print(' Condition Nominal Recorded Instrument Number not in TerraForce record...')
	return {}

# Add a Note to the TF Record
def addNote(DID, title, body):
	lao.print_function_name('script def addNote')

	noted = {}
	noted['type'] = 'Note'
	noted['ParentId'] = DID
	noted['Title'] = title
	noted['Body'] = body
	results = bb.sfcreate(service, noted)
	if results[0]['success']:
		print('Note added successfully.\n')
	else:
		print('Note was not added...')
		print(results)
		sys.exit('Terminating program...')

# Check that Lead Parcel Exists and Add if Not
def leadParcelCheck(dTF):
	lao.print_function_name('script def leadParcelCheck')

	if not 'Lead_Parcel__c' in dTF:
		dTF['Lead_Parcel__c'] = 'None'
	if dTF['Lead_Parcel__c'] == '' or dTF['Lead_Parcel__c'] == 'None' or dTF['Lead_Parcel__c'] == []:
		if 'Parcels__c' in dTF:
			parSplit = dTF['Parcels__c'].split(', ')
			dTF['Lead_Parcel__c'] = parSplit[0]
	return dTF

# Remove unnecessary and 'None' keys from dTF
def clean_dTF(dTF):
	lao.print_function_name('script def clean_dTF')

	# Seller Dictionary
	del dTF['Seller Entity']
	del dTF['Seller Person']
	del dTF['Seller Street']
	del dTF['Seller City']
	del dTF['Seller State']
	del dTF['Seller Zip']
	del dTF['Seller Country']
	del dTF['Seller Phone']
	del dTF['Seller Email']

	# Buyer Dictionary
	del dTF['Buyer Entity']
	del dTF['Buyer Person']
	del dTF['Buyer Street']
	del dTF['Buyer City']
	del dTF['Buyer State']
	del dTF['Buyer Zip']
	del dTF['Buyer Country']
	del dTF['Buyer Phone']
	del dTF['Buyer Email']

	# Listing & Buyer Agents
	del dTF['List Entity']
	del dTF['List Agent']
	del dTF['List Agent Phone']
	del dTF['List Agent Email']
	del dTF['Buyer Agent Entity']
	del dTF['Buyer Agent']
	del dTF['Buyer Agent Phone']
	del dTF['Buyer Agent Email']

	# Delete other non-Terraforce fields
	del dTF['AltAPN A']
	del dTF['AltAPN B']
	del dTF['Deal Name']
	del dTF['Lender']
	del dTF['Market__c']
	del dTF['MLS Status']
	notes = dTF['Notes']
	del dTF['Notes']
	del dTF['Residence Y-N']

	# Remove 'None' values from dTF
	dTF = {key: value for key, value in dTF.items() if value != 'None'}
	# for (key, value) in dTF.items():
	# 	if value == 'None':
	# 		del dTF[key]

	return dTF, notes

# Create Deal Name
def create_deal_name(sdAcc, dTF):
	lao.print_function_name('script def create_deal_name')

	# Shorten Owner Name if longer than 50 characters (max Name length is 80)
	# if STXID != 'None' and len(STX) > 50:
	if sdAcc['EID'] != 'None' and len(sdAcc['ENTITY']) > 50:
		# owner_name = STX.split(' ')
		owner_name = sdAcc['ENTITY'].split(' ')
		name = ''
		for i in range(1, len(owner_name)):
			if len(name) < 50:
				name = '{0} {1}'.format(name, owner_name[i])
				print(name)
			else:
				break
		owner_name = name
	# elif STXID == 'None':
	elif sdAcc['EID'] == 'None':
		# owner_name = SPR
		owner_name = sdAcc['NAME']
	else:
		# owner_name = STX
		owner_name = sdAcc['ENTITY']

	if int(dTF['Acres__c']) < 5:
		if 'UNKNOWN' in sdAcc['ENTITY'].upper():
			dTF['Name'] = '{0} {1} {2:.1f} Ac'.format(dPrint['Lead_Parcel'], dPrint['County'], float(dTF['Acres__c']))
		elif sdAcc['EID'] != 'None':
			dTF['Name'] = '{0} {1:.1f} Ac'.format(owner_name, float(dTF['Acres__c']))
		elif sdAcc['NAME'] != 'None':
			dTF['Name'] = '{0} {1:.1f} Ac'.format(owner_name, float(dTF['Acres__c']))
		else:
			dTF['Name'] = '{0} {1} {2:.1f} Ac'.format(dPrint['Lead_Parcel'], dPrint['County'], float(dTF['Acres__c']))
	else:
		if 'UNKNOWN' in sdAcc['ENTITY'].upper():
			dTF['Name'] = '{0} {1} {2} Ac'.format(dPrint['Lead_Parcel'], dPrint['County'], int(dTF['Acres__c']))
		elif sdAcc['EID'] != 'None':
			dTF['Name'] = '{0} {1} Ac'.format(owner_name, int(dTF['Acres__c']))
		elif sdAcc['NAME'] != 'None':
			dTF['Name'] = '{0} {1} Ac'.format(owner_name, int(dTF['Acres__c']))
		else:
			dTF['Name'] = '{0} {1} {2} Ac'.format(dPrint['Lead_Parcel'], dPrint['County'], int(dTF['Acres__c']))
	return dTF

td.console_title('CSV to TF')
service = fun_login.TerraForce()

# Open CSV GUI to input into TF
extension = [('formated csv files', '_FORMATTED.csv'), ('all files', '.*')]
usercsvpath = f'{lao.getPath('comps')}ID_MLS_2025-04-03_FORMATTED.csv'
# usercsvpath = lao.guiFileOpen(lao.getPath('comps'), "Open User's CSV", extension)

# Create inFile dictionary
dFin = dicts.spreadsheet_to_dict(usercsvpath)

# Set entry progress variables
totalRecords = len(dFin)
currentRecord = 0

# Set source variable
dataSource = 'None'

isREDNewsLoggedIn = False

for line in dFin:
	dTF = dFin[line]

	# Count number of rows
	currentRecord += 1

	# Skip records w/o data
	if dTF['Acres__c'].upper() == 'SKIP':
		continue

	# Make Deal Dict, Seller Dict, Buyer Dict, Offer Dict, Printinfo Dict, Commission Dict
	dTF, sdAcc, bdAcc, dOffer, dPrint, dCommision = assignTFfieldsFromSpreadsheet(dTF)
	
	print('here1')
	pprint(dTF)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	

	# Create M1 Find Me file
	marketAbb, stateAbb = lao.get_market_abbreviation(dTF['Market__c'], dTF['County__c'])
	polyinlayer = '{0}Parcels{1}'.format(stateAbb, dTF['County__c'])
	fjson.create_ZoomToPolygon_json_file(fieldname='apn', polyId=dTF['Lead_Parcel__c'], polyinlayer=polyinlayer, lon=dTF['Longitude__c'], lat=dTF['Latitude__c'], market=dTF['Market__c'])


	# # Skip if Sale Price = 'None' or if Source ID exits
	# print('here4')
	# td.warningMsg('\n Not checking for skip record...')
	dLead = {}

	dLead = skipRecord(dTF, dPrint)
	if dLead == 'Skip':
		dLead = {}
		continue

	if dLead == {}:
		# Open and login to RED News
		if dTF['Source__c'] == 'RED News':
			if isREDNewsLoggedIn is False:
				td.banner('TF M1 AWS CSV Entry v02')
				openbrowser('https://realestatedaily-news.com/wp-login.php')
				td.warningMsg('\n Login to RED News website...\n\n Username: Craig K.\n Password: Harley692019!!')
				td.uInput('\n Continue... > ')
				isREDNewsLoggedIn = True
			else:
				openbrowser('https://realestatedaily-news.com/displaycomp/?ID={0}&NoComment='.format(dTF['Source_ID__c']))
			openbrowser('https://realestatedaily-news.com/displaycomp/?ID={0}&NoComment='.format(dTF['Source_ID__c']))
		elif dTF['Source__c'] == 'MLS':
			openbrowser(dTF['Source_ID__c'])
		elif dTF['Source__c'] == 'Reonomy':
			# print('here5')
			# td.warningMsg('\n NOT OPENING REONOMY...')
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
			openbrowser(dTF['Source_ID__c'])
		
		printinfo(dPrint, 'start')
		sleep(1)

		# User to choose what to do with the record
		dTF, dLead = choose_action_for_record(dTF, dLead)

	# User chooses to skip record
	if dLead == 'Skip':
		dLead = {}
		continue

	# Check if deal is closed and if so only update relevant fields
	closedDeal = False
	if dLead != {}:
		# Create M1 Zoom to Polygon json file
		fjson.create_ZoomToPolygon_json_file(fieldname='pid', polyId=dPrint['PID'], polyinlayer='OwnerIndex', lon=None, lat=None)

		printinfo(dPrint, 'sellerbuyer')
		
		dTF, sdAcc, sdAcc, bdAcc = assignTFfieldsFromLeadDeal(dTF, dLead, sdAcc, bdAcc)

		if 'Closed' in dLead['StageName__c']:
			closedDeal = True

	# Enter Seller
	if sdAcc != {} and closedDeal is False:
		printinfo(dPrint, 'seller')
		print('----> Seller: {0}'.format(sdAcc['ENTITY']))
		if sdAcc['ENTITY'] == 'None':
			print('\n **** No Seller Entity Listed ****\n\n')
			ui = td.uInput(' Type Entity or [Enter] for None > ')
			if len(ui) > 2:
				sdAcc['ENTITY'] = ui

		# Check if Buyer Entity and Person exists
		# if sdAcc['ENTITY'] != 'None' and sdAcc['EID'] != 'None' and sdAcc['NAME'] != 'None' and sdAcc['AID'] != 'None':
		# 	pass
		# else:
		if sdAcc['ENTITY'] != 'None':
			sdAcc = acc.find_create_account_entity(service, sdAcc)
			if sdAcc['EID'] == 'None':
				sdAcc['NAME'] = sdAcc['ENTITY']
				sdAcc['ENTITY'] = 'None'
				sdAcc['AID'] = 'None'
			# Check for TerraForce for Employees, Child Accounts and Existing Deals of ENTITY
			else:
				dTF['Owner_Entity__c'] = sdAcc['EID']
				sdAcc['NAME'], sdAcc['AID'] = acc.find_persons_of_entity(service, sdAcc['EID'])
		else:
			# STXID, SPRID = 'None', 'None'
			sdAcc['Owner_Entity__c'], sdAcc['AID'] = 'None', 'None'

		# Check if no person associated with Entity and sdAcc['NAME'] (Person) is not None:
		# I don't think this is necessary #################
		# if SPRID == 'None' and sdAcc['NAME'] != 'None':
		# 	SPR = sdAcc['NAME']

		# If no Employee or Child Account of Entity then create a Person Account
		if sdAcc['AID'] == 'None':
			temp1, temp2, sdAcc = acc.find_create_account_person(service, sdAcc)
			if sdAcc['AID'] != 'None':
				dTF['AccountId__c'] = sdAcc['AID']
		else:
			dTF['AccountId__c'] = sdAcc['AID']

	# Create Deal Name
	if dLead == {} or dLead['Name'] == 'NeedDealName':	# No need to create Deal name for existing Deal
		dTF = create_deal_name(sdAcc, dTF)

	# Enter Buyer
	if closedDeal is False and dPrint['Status'] == 'Sold':
		printinfo(dPrint, 'buyer')
		print('\n ----> Buyer: {0}'.format(bdAcc['ENTITY']))

		# If no Buyer Entity ask user if they want to enter one
		if bdAcc['ENTITY'] == 'None':
			td.warningMsg('\n **** No Buyer Entity Listed ****')
			ui = td.uInput('\n\n Type in Buyer Entity or [Enter] for None > ')
			if len(ui) > 0:
				bdAcc['ENTITY'] = ui
		
		# # Check if Buyer Entity and Person exists
		# if bdAcc['ENTITY'] != 'None' and bdAcc['EID'] != 'None' and bdAcc['NAME'] != 'None' and bdAcc['AID'] != 'None':
		# 	pass
		# else:
		# Check TerraForce for 
		if bdAcc['ENTITY'] != 'None':
			bdAcc = acc.find_create_account_entity(service, bdAcc)
			if bdAcc['EID'] == 'None':
				bdAcc['NAME'] = bdAcc['ENTITY']
				bdAcc['ENTITY'] = 'None'
			# Check for Employees or Child Accounts of Business
			elif dPrint['Status'] == 'Sold':
				dOffer['Buyer_Entity__c'] = bdAcc['EID']
				bdAcc['NAME'], bdAcc['AID'] = acc.find_persons_of_entity(service, bdAcc['EID'])
				dPrint['Buyer_Person'] = bdAcc['NAME']
			else:
				bdAcc['AID'] = 'None'
		else:
			bdAcc['AID'] = 'None'

		# If no Buyer Entity and no Account Person then ask user to enter Person
		noBuyer = False
		# if BPRID == 'None' and bdAcc['ENTITY'] == 'None' and dPrint['Status'] == 'Sold':
		if bdAcc['AID'] == 'None' and bdAcc['ENTITY'] == 'None' and dPrint['Status'] == 'Sold':
			ui = td.uInput('\n **** No Buyer Person Listed ****\n\n Type in Buyer Person or [Enter] for None > ')
			if len(ui) > 0:
				# bdAcc['Buyer_Person'] = ui
				dPrint['Buyer_Person'] = ui
				bdAcc['NAME'] = ui
			else:
				noBuyer = True

		# If no Employee or Child Account of Business then create a Person Account
		if noBuyer is False:
			# if BPRID == 'None':
			if bdAcc['AID'] == 'None':
				if dPrint['Buyer_Person'] != 'None':
					# BPR = dPrint['Buyer_Person']
					bdAcc['NAME'] = dPrint['Buyer_Person']
				temp1, temp2, bdAcc = acc.find_create_account_person(service, bdAcc)
				# if BPRID != 'None' and dPrint['Status'] == 'Sold':
				if bdAcc['AID'] != 'None' and dPrint['Status'] == 'Sold':
					# dOffer['Buyer__c'] = BPRID
					dOffer['Buyer__c'] = bdAcc['AID']
			elif dPrint['Status'] == 'Sold':
				# dOffer['Buyer__c'] = BPRID
				dOffer['Buyer__c'] = bdAcc['AID']

	# Enter Beneficiary
	if closedDeal is False and dPrint['Status'] == 'Sold' and 'Beneficiary__c' in dTF:
		benedAcc = dicts.get_blank_account_dict()
		benedAcc['ENTITY'] = dTF['Beneficiary__c']
		printinfo(dPrint, 'beneficiary')
		print('----> Beneficiary: {0}'.format(dTF['Beneficiary__c']))
		# BENEX, BENEXID, RTYID, business_dict = bb.findCreateAccountEntity(service, dTF['Beneficiary__c'])
		benedAcc = acc.find_create_account_entity(service, benedAcc)
		# if BENEXID == 'None':
		if benedAcc['EID'] == 'None':
			# BENEX, BENEXID, RTYID = bb.findCreateAccountPerson(service, dTF['Beneficiary__c'])
			temp1, temp2, benedAcc = acc.find_create_account_person(service, benedAcc)
		# if BENEXID == 'None':
		if benedAcc['EID'] == 'None' and benedAcc['AID'] == 'None':
			del dTF['Beneficiary__c']
			del dTF['Loan_Amount__c']
			if 'Loan_Date__c' in dTF:
				del dTF['Loan_Date__c']
		elif benedAcc['EID'] != 'None':
			dTF['Beneficiary__c'] = benedAcc['EID']
		elif benedAcc['AID'] != 'None':
			dTF['Beneficiary__c'] = benedAcc['AID']
		# else:
		# 	dTF['Beneficiary__c'] = BENEXID

	# Enter Listing Agent
	listagentd = {}
	if dTF['List Agent'] != 'None':
		agntdAcc = dicts.get_blank_account_dict()
		printinfo(dPrint, 'listingagent')
		print('----> Listing Agent')
		# AGENT, AGENTID, RTYID = bb.findCreateAccountPerson(service, dTF['List Agent'], PHONE=dTF['List Agent Phone'], EMAIL=dTF['List Agent Email'])
		temp1, temp2, agntdAcc = acc.find_create_account_person(service, agntdAcc)
		listagentd['type'] = 'lda_Commission__c'
		listagentd['Agent_Order__c'] = 0
		# listagentd['Agent__c'] = AGENTID
		listagentd['Agent__c'] = agntdAcc['AID']

	# Check that Acres has a value
	if 'Acres__c' in dTF:
		if dTF['Acres__c'] == 'None':
			printinfo(dPrint, 'acres')
			dTF['Acres__c'] = float(td.uInput('\n Enter Acres > '))
		if dTF['Acres__c'] == 0:
			printinfo(dPrint, 'acres')
			dTF['Acres__c'] = float(td.uInput('\n Enter Acres > '))

	# Check Location
	if not '&' in dTF['Location__c']:
		if 'Longitude__c' in dTF:
			if dTF['Longitude__c'] != 'None':
				dTF = mpy.get_intersection_from_lon_lat(dTF)
			else:
				dTF['Location__c'] = td.uInput('\n Enter Location > ')
		else:
			dTF['Location__c'] = td.uInput('\n Enter Location > ')
		dPrint['Location'] = dTF['Location__c']

	# Enter Classification
	printinfo(dPrint, 'classification')
	dTF, start_over = lao.select_from_list(dTF, 'Classification__c')
	dPrint['Classification'] = dTF['Classification__c']
	dTF, start_over = lao.select_from_list(dTF, 'Lot_Type__c')
	dTF, start_over = lao.select_from_list(dTF, 'Development_Status__c')
	# Get Buyer Acting As if a the Deal is a sale
	if dTF['Source__c'] == 'Reonomy':
		dTF, start_over = lao.select_from_list(dTF, 'Buyer_Acting_As__c')

	# Make sure Lead Parcel is populated
	dTF = leadParcelCheck(dTF)

	# Add Researcher OwnerId to record
	dTF['OwnerId'] = bb.createdByResearch(service)

	# Check if non-disclosure state and move Sale Price to Description if Yes
	if dOffer != {}:
		if lao.getCounties('IsDisclosure', '', dTF['County__c']) == 'No' and dTF['Source__c'] == 'Reonomy' and dTF['Sale_Price__c'] != 10000:
			salePriceFormatted = td.currency_format_from_number(dTF['Sale_Price__c'])
			pricePerAcre = float(float(dTF['Sale_Price__c']) / float(dTF['Acres__c']))
			pricePerAcre = td.currency_format_from_number(pricePerAcre)
			if 'Description__c' in dTF:
				dTF['Description__c'] = 'Reonomy Estimated Sale Price: {0}  {1} per acre\n{2}'.format(salePriceFormatted, pricePerAcre, dTF['Description__c'])
			else:
				dTF['Description__c'] = 'Reonomy Estimated Sale Price: {0}  {1} per acre\n'.format(salePriceFormatted, pricePerAcre)
			dTF['Sale_Price__c'] = 10000
			dOffer['Offer_Price__c'] = 10000

	printinfo(dPrint)

	# Remove unnecessary and 'None' keys from dTF
	dTF, notes = clean_dTF(dTF)

	# Create Records
	if dLead == {}: # Create a new record since ld (Lead Dict) is empty
		DID = bb.tf_create_3(service, dTF)
		if DID == 'Create Failed':
			td.warningMsg(' Deal was not created...\n')
			print(results)
			sys.exit('\nTerminating program...')
	else: # Update and existing Lead
		DID = bb.tf_update_3(service, dTF)

	# Create offer if dOffer is populated otherwise leave the record as Lead
	if dOffer != {} and closedDeal is False:
		dOffer['DealID__c'] = DID
		OID = bb.tf_create_3(service, dOffer)
		if OID == 'Create Failed':
			td.warningMsg(' Offer was not created...')
			print(results)
			sys.exit(' Terminating program...')

		# Close the Deal after offer is made
		close_dict = {'type': 'lda_Opportunity__c', 'id': DID, 'StageName__c': 'Closed Lost'}
		bb.tf_update_3(service, close_dict)

	# Create Commissions if they exist
	if listagentd != {}:
		listagentd['DealID__c'] = DID
		results = bb.tf_create_3(service, listagentd)
		if results == 'Create Failed':
			td.warningMsg('Listing Agent was not closed...')
			print(results)
			sys.exit(' Terminating program...')

	# Create Notes if they exist
	if notes != 'None':
		addNote(DID, 'Transaction Remarks', notes)

	# Open the newly created deal
	# TerraForce Query
	fields = 'default'
	wc = "Id = '{0}'".format(DID)
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	DID = results[0]['Id']
	PID = results[0]['PID__c']
	salePID = PID
	dPrint['PID'] = PID
	dPrint['Status'] = results[0]['StageName__c']
	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))

	# Enter Lot Details
	if dTF['Lot_Type__c'] != 'Raw Acreage':
		printinfo(dPrint, 'start')
		print(' PID: {0}'.format(PID))
		ui = td.uInput('\n Add Lot Details? [0/1/00] > ')
		if ui == '1':
			bb.deleteExistingLotDetails(service, DID)
			totalLots = bb.LotDetail(service, DID)
		elif ui == '00':
			exit('\n Terminating program...')

	printinfo(dPrint, 'start')
	print(' PID: {0}'.format(PID))

	# Confirm OwnerIndex Polygon is created and saved with PID
	td.warningMsg('\n Confirm OwnerIndex polygon is created and saved with PID.')
	td.uInput('\n Continue > ')
	# Create OPR Map
	opr_map_created = mpy.make_opr_map_api(service, salePID)

	# Don't create Leads for Idaho, UNKNOWN Buyer or Buyer Acting As User
	if dTF['State__c'] == 'Idaho' or dTF['Buyer_Acting_As__c'] == 'User':
		if dTF['State__c'] == 'Idaho':
			print('\n Leads are not required for Idaho comps...')
		elif dTF['Buyer_Acting_As__c'] == 'User':
			print('\n Buyer acting as User. No Lead required.')
		# elif 'UNKNOWN' in BTX.upper():
		# 	print('\n Unknown Buyer. No Lead created.')
	else:
		while 1:
			ui = td.uInput('\n Create Lead? [0/1] > ')
			if ui == '0':
				print('\n No Lead created.')
				break
			elif ui == '1':
				# Create Lead of Sale Deal
				leadPID = bb.tf_create_lead_of_sale_deal(service, PID=PID, root='None', DEALID='None')
				# Make OI polygon of Lead
				mpy.oi_make_from_pid(PID=PID, PIDnew=leadPID)
				break
			else:
				td.warningMsg('\n Invalid entry...try again...\n\n > ')

	ui = td.uInput('\n [Enter] to continue or [00] to quit > ')
	if ui == '00':
		exit('\n Terminating program...')

td.banner('TF M1 AWS CSV Entry v02')
print(' Entry for this spreadsheet complete...\n\n Fin')