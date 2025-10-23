# Convert an Ownership to a Sale
# with an option to make a new Ownership

import acc
import bb
from colored import Fore, Back, Style
import cpypg
import dicts
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
from pprint import pprint
import webs

def get_pid():
	td.banner('PPP Ownership to Sale v01')
	jsonFile = 'C:/Users/Public/Public Mapfiles/M1_Files/zoomToPolygon.json'
	d = fjson.getJsonDict(jsonFile)
	PID = d['polyId']
	while 1:
		td.colorText(f'Zoom to Poly PID: {PID}', 'GREEN')
		print('\n  1) Use this PID')
		print('  2) Enter a new PID')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			return PID
		elif ui == '2':
			ui = td.uInput('\n Enter new PID > ')
			if len(ui) > 0:
				return ui
		elif len(ui) > 3:
			return ui
		elif ui == '00':
			exit('\n Terminating program...')
		td.warningMsg('\n Invalid selection...try again...\n')
		lao.sleep(1)

# Print the important info
def print_info(dPnt, hiLight='None'):
	# print('{0}{1}{2}'.format(Fore.yellow_2, text, Style.reset))

	td.banner('PPP Ownership to Sale v01')

	if hiLight == 'start':
		print('{0}'.format(Fore.yellow_2))
	print(' Status:   {0:30}  PID:   {1}'.format(dPnt['Status'], dPnt['PID']))
	print('{0}'.format(Style.reset))
	print(' County:   {0:30}  City:  {1}'.format(dPnt['County'], dPnt['CITY']))
	print('\n')
	menuColor = ''

	if hiLight == 'acres':
		# menuColor = Fore.yellow_2
		menuColor = Fore.yellow_2
	print('{0} Acres:    {1}{2}'.format(menuColor, dPnt['Acres'], Style.reset))
	menuColor = ''

	print(' Lead Par: {0:30}'.format(dPnt['Lead_Parcel']))
	print(' Parcels:  {0}\n'.format(dPnt['Parcels']))
	menuColor = ''
	sellerColor = ''
	buyerColor = ''
	if hiLight == 'seller':
		sellerColor = Fore.yellow_2
	if hiLight == 'buyer':
		buyerColor = Fore.yellow_2
	print('{0} Seller    {1:30}{2}  {3}Buyer{4}'.format(sellerColor, '', Style.reset, buyerColor, Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPnt['Seller_Entity'], Style.reset, buyerColor, dPnt['Buyer_Entity'], Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPnt['Seller_Person'], Style.reset, buyerColor, dPnt['Buyer_Person'], Style.reset))

	if hiLight == 'listingagent':
		menuColor = Fore.yellow_2
	print('{0}  Agnt {1:35}  {2}{3}'.format(menuColor,dPnt['ListAgent'], dPnt['SellAgent'], Style.reset))
	menuColor = ''

	if 'Beneficiary__c' in dPnt:
		if hiLight == 'beneficiary':
			print('{0}'.format(Fore.yellow_2))
		else:
			print('{0}'.format(Style.reset))
		print('Beneficiary')
		print('  {0}'.format(dPnt['Beneficiary__c']))
		print('{0}'.format(Style.reset))
	else:
		print('{0}'.format(Style.reset))
	
	print(' Lots:     {0}'.format(str(dPnt['Lots'])))
	
	if hiLight == 'classification':
		menuColor = Fore.yellow_2
	print('{0} Class:    {1}   Lot Type: {2}{3}'.format(menuColor, dPnt['Classification'], dPnt['Lot_Type'], Style.reset))
	menuColor = ''
	print
	if hiLight == 'sale_date':
		menuColor = Fore.yellow_2
	print('{0} Date:     {1}{2}'.format(menuColor, dPnt['Sale_Date'], Style.reset))
	menuColor = ''

	if hiLight == 'sale_price':
		menuColor = Fore.yellow_2
	print('{0} Price:    {1}{2}'.format(menuColor, td.currency_format_from_number(dPnt['Sale_Price']), Style.reset))
	menuColor = ''

	print(' Lst Date: {0}'.format(dPnt['List_Date']))
	print(' Lst Price:{0}'.format(td.currency_format_from_number(dPnt['List_Price'])))
	print('\n')
	print(' SourceID  {0}'.format(dPnt['Source_ID']))
	print(' RDN:      {0}'.format(dPnt['RDN']))
	print('\n')
	if 'Longitude' in dPnt:
		print(' Lon Lat:  {0} {1}'.format(dPnt['Longitude'], dPnt['Latitude']))
	else:
		print(' Lon Lat: None')

	if hiLight == 'location':
		menuColor = Fore.yellow_2
	print('{0} Location: {1}{2}'.format(menuColor, dPnt['Location'], Style.reset))
	menuColor = ''

	print(' Sub Name: {0}'.format(dPnt['Subdivision']))
	print('_________________________________________________________________________\n')

def get_dTF_of_deal(service, PID):
	# Get the deal dictionary for the given PID
	dTF = dicts.get_blank_tf_deal_dict()
	dSlr = dicts.get_blank_account_dict()

	# Query the deal using the PID
	fields = 'default'
	wc = f"PID__c = '{PID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	dTF = results[0]  # Ownership query of PID results

	# Convert dict from ordered to regular	
	dTF = {k: v for k, v in dTF.items()}

	# pprint(dTF)
	# print('###############################################')
	# pprint(dTF['AccountId__r'])
	# print('###############################################')
	# print(dTF['AccountId__r'].get('FirstName'))
	# exit()

	# # Variables for seller
	# DID = dTF['Id']
	# PID = dTF['PID__c']

	# Remove keys that are not needed
	lRemove_keys = [
				'AccountId__r',
				'Accounts_Receivable__r',
				'attributes',
				'Beneficiary__r',
				'Commissions__r',
				'CreatedById',
				'CreatedDate',
				'Digitized__c',
				'LastModifiedById',
				'LastModifiedDate',
				'Offers__r',
				'Owner_Entity__r',
				'OwnerId',
				'Package_Information__r',
				'Parent_Opportunity__c',
				'Parent_Opportunity__r',
				'Price_Per_Acre__c',
				'Price_Per_Lot__c'
				'Report_Acres__c',
				'Request_Deal__r',
				'Research_Flag__c',
				'Verified_By__c',
				'Verified_By__c'
			 ]
	
	for k in lRemove_keys:
		if k in dTF:
			del dTF[k]
	dTF['type'] = 'lda_Opportunity__c'
	
	return dTF

# Populate dAcc from TerraForce data (dAcc['AID'] must have a value)
def populate_dAcc_from_tf(service, dAcc='None', PID='None'):
	# Check if existing dAcc dictionary exisits
	if dAcc == 'None':
		dAcc = dicts.get_blank_account_dict()
	
	# Check if PID exists and get AID and EID from TF Deal
	if PID != 'None':
		# TerraForce Query
		wc = "PID__c = '{PID}'".format(PID=PID)
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None)
		if results:
			d = results[0]
			dAcc['AID'] = d['AccountId__c']
			dAcc['EID'] = d['Owner_Entity__c']
		else:
			td.warningMsg(f"\n No Deal found for PID: {PID}")
			return dAcc

	# Check if EID exists and populate dAcc info if it does
	if dAcc['EID'] != 'None':
		# TerraForce Query
		wc = "Id = '{EID}'".format(**dAcc)
		results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None)
		if results:
			d = results[0]
			dAcc['ENTITY'] = d['Name']
			dAcc['CATEGORY'] = d['Category__c']
			dAcc['CITY'] = d['BillingCity']
			dAcc['DESCRIPTION'] = d['Description']
			dAcc['PHONE'] = d['Phone']
			dAcc['STATE'] = td.make_title_case(d['BillingState'])
			dAcc['STREET'] = td.titlecase_street(d['BillingStreet'])
			dAcc['ZIPCODE'] = d['BillingPostalCode']
		else:
			td.warningMsg(f"\n No Entity found for EID: {dAcc['EID']}")
			return dAcc

	# Check if AID exists
	if dAcc['AID'] != 'None':
		# TerraForce Query
		wc = "Id = '{AID}'".format(**dAcc)
		results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
		d = results[0]
		# Populate dAcc fields with TF data
		dAcc['AID'] = d['Id']
		dAcc['CATEGORY'] = d['Category__c']
		dAcc['CCID'] = d['CC_ID__c']
		if dAcc['CITY'] == 'None':
			dAcc['CITY'] = d['BillingCity']
		dAcc['DESCRIPTION'] = d['Description']
		if d['Company__c'] != 'None':
			dAcc['EID'] = d['Company__c']		# Entity ID
			dAcc['ENTITY'] = d['Company__r']['Name']
		if '@' in d['PersonEmail']:
			dAcc['EMAIL'] = d['PersonEmail'].lower()
		dAcc['EMAILOPTOUT'] = d['PersonHasOptedOutOfEmail']
				# Company
		dAcc['MOBILE'] = d['PersonMobilePhone']
		dAcc['NAME'] = d['Name']			# Person Name
		dAcc['NF'] = d['FirstName']			# First Name
		dAcc['NM'] = d['MiddleName__c']			# Middle Name
		dAcc['NL'] = d['LastName']			# Last Name
		if d['Phone'] != 'None':
			dAcc['PHONE'] = d['Phone']
		dAcc['PHONEHOME'] = d['PersonHomePhone']
		if dAcc['STATE'] == 'None':
			dAcc['STATE'] = td.make_title_case(d['BillingState'])
		if dAcc['STREET'] == 'None':
			dAcc['STREET'] = td.titlecase_street(d['BillingStreet'])
		dAcc['TITLEPERSON'] = td.make_title_case(d['PersonTitle'])
		try:
			dAcc['TOP100AGENT'] = d['Top100__c']
		except KeyError:
			pass
		dAcc['ZIPCODE'] = d['BillingPostalCode']
	
	dAcc = td.address_formatter(dAcc)
	return dAcc

# Populate the dPnt dictionary from the TerraForce Deal and Seller
def populate_dPnt(dTF, dSlr):
	dPnt = {}

	# Seller Dictionary
	dPnt['Seller_Entity'] = dSlr['ENTITY']
	dPnt['Seller_Person'] = dSlr['NAME']

	# Buyer Dictionary
	dPnt['Buyer_Entity'] = 'None'
	dPnt['Buyer_Person'] = 'None'

	# Beneficiary Dictionary
	dPnt['Beneficiary__c'] = 'None'

	# Assign TF Fields
	if dTF['Acres__c'] == 'None':
		dPnt['Acres'] = 0
	else:
		dPnt['Acres'] = float(dTF['Acres__c'])
	dPnt['CITY'] = dTF['City__c']
	dPnt['Classification'] = dTF['Classification__c']
	dPnt['County'] = dTF['County__c']
	dPnt['Latitude'] = (dTF['Latitude__c'])
	dPnt['Lead_Parcel'] = (dTF['Lead_Parcel__c']).strip(' ')
	dPnt['Location'] = dTF['Location__c']
	dPnt['Longitude'] = (dTF['Longitude__c'])
	dPnt['Lot_Type'] = dTF['Lot_Type__c']
	dPnt['Lots'] = int(dTF['Lots__c'])
	dPnt['Parcels'] = dTF['Parcels__c']
	dPnt['PID'] = dTF['PID__c']
	dPnt['RDN'] = dTF['Recorded_Instrument_Number__c']
	dPnt['Sale_Date'] = 'None'
	dPnt['Sale_Price'] = 'None'
	dPnt['Source_ID'] = dTF['Source_ID__c']
	dPnt['Subdivision'] = dTF['Subdivision__c']
	dPnt['Zoning'] = dTF['Zoning__c']
	dPnt['List_Date'] = 'None'
	dPnt['List_Price'] = 'None'
	dPnt['Status'] = 'Sold'
	dPnt['ListEntity'] = 'None'
	dPnt['ListAgent'] = 'None'
	dPnt['SellAgent'] = 'None'
	dPnt['Beneficiary__c'] = 'None'
	dPnt['Status'] = 'Sold'

	return dPnt

def get_contact_info(service, dContact, dPnt, contact_type):
	
	print_info(dPnt, contact_type)

	# If no Seller Entity and no Account Person then ask user to enter Person
	if dContact['ENTITY'] == 'None' and dContact['NAME'] == 'None':
		td.warningMsg(f'\n**** No {contact_type.title()} Entity or Person Listed ****')
		ui = td.uInput(f'\n\n Type in {contact_type.title()} Entity or Person or [Enter] for None [00] to Quit > ')
		if len(ui) > 0:
			dContact['ENTITY'] = ui
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			dContact['ENTITY'] = 'None'
	
	# Find or Create Seller Entity
	if dContact['ENTITY'] != 'None':
		dContact = acc.find_create_account_entity(service, dContact)

	# User to choose if they want to enter a Person for the Entity

	find_person = True
	if dContact['ENTITY'] != 'None' and dContact['NAME'] == 'None':
		print(f'\n Would you like to enter a Person for {dContact['ENTITY']}?')
		while 1:
			print('\n  1) Yes')
			print('  2) No')
			print(' 00) Quit')
			ui = td.uInput('\n Select > ')
			if ui == '1':
				ui = td.uInput('\n Enter a Person or [Enter] for None > ')
				if ui == '':
					dContact['NAME'] = 'None'
					find_person = False
				else:
					dContact['NAME'] = ui
				break
			elif ui == '2':
				dContact['NAME'] = 'None'
				find_person = False
				break
			elif ui == '00':
				exit(' Terminating program...')
			else:
				td.warningMsg('\n Invalid selection...try again...\n')
				lao.sleep(1)
				continue

	# Find or Create Seller Person
	if find_person:
		Name, AID, dContact = acc.find_create_account_person(service, dContact)

	# Update dPrnt with Seller info
	if contact_type == 'seller':
		dPnt['Seller_Entity'] = dContact['ENTITY']
		dPnt['Seller_Person'] = dContact['NAME']
	elif contact_type == 'buyer':
		dPnt['Buyer_Entity'] = dContact['ENTITY']
		dPnt['Buyer_Person'] = dContact['NAME']
	elif contact_type == 'beneficiary':
		if dContact['ENTITY'] != 'None':
			dPnt['Beneficiary__c'] = dContact['ENTITY']
		elif dContact['NAME'] != 'None':
			dPnt['Beneficiary__c'] = dContact['NAME']
		else:
			dPnt['Beneficiary__c'] = 'None'


	return dContact, dPnt

# Make Offer dict
def make_offer(dByr, dTF, dPnt):

	dOffer = {}
	dOffer['type'] = 'lda_Offer__c'
	dOffer['DealID__c'] = dTF['Id']
	dOffer['Offer_Status__c'] = 'Accepted'

	print_info(dPnt, 'sale_date')
	print('\n Enter Sale Date')
	dTF['Sale_Date__c'] = td.make_tf_date()
	dPnt['Sale_Date'] = dTF['Sale_Date__c']

	dOffer['Offer_Date__c'] = dTF['Sale_Date__c']
	dOffer['Date_Accepted__c'] = dTF['Sale_Date__c']
	
	print_info(dPnt, 'sale_price')
	ui = td.uInput('\n  Enter Sale Price > ')
	dTF['Sale_Price__c'] = float(ui.replace(',', '').replace('$', ''))
	dPnt['Sale_Price'] = dTF['Sale_Price__c']

	dOffer['Offer_Price__c'] = dTF['Sale_Price__c']
	if dByr['EID'] != 'None':
		dOffer['Buyer_Entity__c'] = dByr['EID']
	if dByr['AID'] != 'None':
		dOffer['Buyer__c'] = dByr['AID']

	return dOffer, dTF, dPnt

# Get Beneficiary and Loan amount
def get_beneficiary_and_loan_amount(service, dTF, dPnt):
	# BENEFICIARY #################################################
	dBen = dicts.get_blank_account_dict()
	# If no Beneficiary in dTF then ask user to enter Beneficiary
	if dTF['Beneficiary__c'] == 'None':
		print_info(dPnt, 'beneficiary')
		print('\n BENEFICIARY')
		print('\n [Enter] for None\n [00] to Quit')
		ui = td.uInput('\n Type Beneficiary Entity or Person > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui != '':
			dBen['ENTITY'] = ui
		else:
			dPnt['Beneficiary__c'] = 'None'
			dTF['Beneficiary__c'] = 'None'
	else:
		dBen = acc.populate_dAcc_from_tf(service, dTF['Beneficiary__c'], dAcc=dBen)
	# If Beneficiary exists in dTF then get Beneficiary info
	if dBen['ENTITY'] != 'None':
		dBen, dPnt = get_contact_info(service, dBen, dPnt, 'beneficiary')
		dTF['Beneficiary__c'] = dBen['EID']
	
	# LOAN AMOUNT & DATE ##########################################
	if dTF['Beneficiary__c'] != 'None':
		print('\n  LOAN AMOUNT & DATE')
		print('\n [Enter] for None\n [00] to Quit')
		ui = td.uInput('\n  Type Loan Amount > ')

		if ui == '00':
			exit('\n Terminating program...')
		elif ui != '':
			ui = ui.replace(',', '').replace('$', '')
			dTF['Loan_Amount__c'] = float(ui)
			print('\n  Enter Loan Date')
			dTF['Loan_Date__c'] = td.make_tf_date()
		else:
			dTF['Loan_Amount__c'] = 0

	return dTF, dPnt

# Create Ownership of Sale
def create_ownership_of_sale(service, PID):
	td.banner('PPP Ownership to Sale v01')
	print(f' Create Lead\Ownership of Sale for PID: {PID} ?')
	while 1:
		print('\n  1) Yes')
		print('  2) No')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			break
		elif ui == '2':
			return
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid selection...try again...\n')
			continue

	PIDnew = bb.tf_create_lead_of_sale_deal(service, PID=PID, DEALID='None')


def main():
	# Login to SalesForce
	service = fun_login.TerraForce()

	PID = get_pid()

	td.banner('PPP Ownership to Sale v01')

	# Get the Deal TF Dictionary
	dTF = get_dTF_of_deal(service, PID)

	# Get the TF Deal's Contact Dictionary
	dContact = populate_dAcc_from_tf(service, dAcc='None', PID=PID)
	# pprint(dTF)
	# pprint(dSlr)
	dPnt = populate_dPnt(dTF, dContact)

	# TF CONTACT ##################################################
	# Enter Contact info from TerraForce Deal
	dContact, dPnt = get_contact_info(service, dContact, dPnt, 'seller')

	# SELLER OR BUYER #############################################
	# Ask user if this is the seller or buyer
	while 1:
		print('\n Is this the Seller or Buyer?\n')
		print('  1) Seller')
		print('  2) Buyer')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')

		# dTF containts the Seller
		if ui == '1':
			dSlr = dContact
			print(f'\n Seller Entity: {dSlr["ENTITY"]}')
			print(f' Seller Person: {dSlr["NAME"]}')
			# Enter Buyer
			dByr = dicts.get_blank_account_dict()
			dByr, dPnt = get_contact_info(service, dByr, dPnt, 'buyer')
			break
		# dTF containts the Buyer
		elif ui == '2':
			dByr = dContact

			# Update dPnt info
			dPnt['Buyer_Entity'] = dByr['ENTITY']
			dPnt['Buyer_Person'] = dByr['NAME']
			dPnt['Seller_Entity'] = 'None'
			dPnt['Seller_Person'] = 'None'
			
			print(f'\n Buyer Entity: {dByr["ENTITY"]}')
			print(f' Buyer Person: {dByr["NAME"]}')
			# Enter Seller
			dSlr = dicts.get_blank_account_dict()
			dSlr, dPnt = get_contact_info(service, dSlr, dPnt, 'seller')

			# Update dTF with Seller info
			dTF['AccountId__c'] = dSlr['AID']
			dTF['Owner_Entity__c'] = dSlr['EID']

			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid selection...try again...\n')

	# OFFER ########################################################
	dOffer, dTF, dPnt = make_offer(dByr, dTF, dPnt)

	# BENEFICIARY #################################################
	dTF, dPnt = get_beneficiary_and_loan_amount(service, dTF, dPnt)


	# ACRES ########################################################
	print_info(dPnt, 'acres')
	ui = td.uInput('\n [Enter] to keep acres or type in new value > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui != '':
		dPnt['Acres'] = float(ui)
		dTF['Acres__c'] = dPnt['Acres']

	# CLASSIFICATION LOT TYPE, LOTS, BUYER ACTING AS ###############
	# Populate Deal Details
	print_info(dPnt, 'classification')
	dTF = bb.populate_deal_details(dTF, True)

	# LOCATION #####################################################
	if not '&' in dTF['Location__c']:
		print_info(dPnt, 'location')
		print(' Getting Location intersection...')
		dTF = mpy.get_intersection_from_lon_lat(dTF)
	
	# RESEARCHER & RECORDTYPEID ####################################
	# Add Researcher OwnerId to record
	print(' Getting Researcher OwnerId...')
	dTF['OwnerId'] = bb.createdByResearch(service)
	# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	dTF['RecordTypeId'] = '012a0000001ZSS8AAO'  # Research RecordTypeId
	dTF['StageName__c'] = 'Closed Lost'  # StageName for Research
	dTF['OPR_Sent__c'] = td.send_opr(dTF['Sale_Date__c'])

	# CLEAR UNWRITABLE FIELDS ##################################
	# Remove fields that are not writable from dTF
	Remove_keys = ['Market__c', 'Report_Acres__c', 'Lot_Price_Rollup__c', 'City_Planner__r', 'Price_Per_Lot__c', 'Weighted_Avg_Price_Per_FF__c', 'Zoning_Applicant__r']
	for key in Remove_keys:
		if key in dTF:
			del dTF[key]


	# CONVERT OWNERSHIP TO SALE ####################################
	print_info(dPnt, 'None')
	while 1:
		print(' Create Sale from Ownership?')
		print('  1) Yes')
		print('  2) No')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			# Create the Offer record
			OID = bb.tf_create_3(service, dOffer)
			if OID == 'Create Failed':
				td.warningMsg(f'\n Failed to make the Offer record\n\n {dTF["PID__c"]} not converted to Sale...')
				ui = td.uInput('\n Continue... > ')
				exit('\n Terminating program...')
			# Covert Ownership to Sale
			DID = bb.tf_update_3(service, dTF)
			if DID == 'Create Failed':
				td.warningMsg(f'\n Failed to make the Sale record\n\n {dTF["PID__c"]} not converted to Sale...')
				ui = td.uInput('\n Continue... > ')
				exit('\n Terminating program...')
			webs.openTFDID(DID)
			td.colorText(' Ownership converted to Sale...', 'GREEN')
			break
		elif ui == '2':
			td.warningMsg('\n Ownership not converted to Sale...')
			break
		else:
			print(' Invalid selection...try again...')

	# MAKE OWNERSHIP OF SALE ########################################
	create_ownership_of_sale(service, dTF)

	# print('here3')
	# ui = td.uInput('\n Print dTF and dOffer [Enter] [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	# pprint(dTF)
	# print('\n################################################\n')
	# pprint(dOffer)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

if __name__ == "__main__":
	main()