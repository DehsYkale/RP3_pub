#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Functions for creating and formatting Excle files with xlwings

import fun_text_date as td
import lao
import xlwings as xw
from pprint import pprint
from webs import get_L5_url

# Get the number of rows in a sheet
def getNumberRows(sht):
	for i in range(3, 100000):
		if sht.range('A{0}'.format(i)).value is None:
			return i-1

# Parse the Classification field of Deals object
def classParse(CLA):
	lCLA = CLA.split(';')
	lClassifications = []

	# Commercial properties
	if 'Office' in CLA and 'Retail' in lCLA:
		lClassifications = ['Commercial']
		lCLA.remove('Office')
		lCLA.remove('Retail')

	for classification in lCLA:

		# Classification exceptions to rename
		if classification == 'Multifamily':
			classification = 'Apartment Traditional'
		elif classification == 'Finished Lots':
			classification = 'Residential'
		elif classification == 'Homebuilder':
			classification = 'Residential'
		elif classification == 'High Density Residential':
			classification = 'High Den Res'
		elif classification == 'High Density Assisted Living':
			classification = 'Assisted Living'
		elif classification == 'Partially Improved Lots':
			classification = 'Residential'
		elif 'Golf' in classification:
			classification = 'Hospitality'
		elif classification == 'Single Family':
			classification = 'Residential'
		elif classification == 'Large Lot':
			classification = 'Residential'
		elif classification == 'Medium Density Residential':
			classification = 'High Den Res'
		elif classification == 'Platted and Engineered Lots':
			classification = 'Residential'
		
		# Write to classification list
		if lClassifications == []:
			lClassifications = [classification]
		elif not classification in lClassifications:
			lClassifications.append(classification)
		
	# Sort list and convert to string
	lClassifications.sort()
	STY = ', '.join(i for i in lClassifications)
	return STY	

# Build Hyperlinks for Excel cells
def buildHyperlink(sht, linkType, rowNo, colID, colTarget, market=None, lBrochures=None, L5RecType=''):

	# L5 Deal Link
	if linkType == 'L5':
		from webs import get_L5_url
		cell = sht.range('{0}{1}'.format(colID, rowNo))
		PID = cell.value
		cell = sht.range('{0}{1}'.format(colTarget, rowNo))
		hyperlink = get_L5_url(L5RecType, market, PID)
		cell.add_hyperlink(hyperlink, 'L5', 'Open in L5')

	# TerraForce Deal Link
	elif linkType == 'Deal':
		cell = sht.range('{0}{1}'.format(colID, rowNo))
		DID = cell.value
		cell = sht.range('{0}{1}'.format(colTarget, rowNo))
		hyperlink = 'https://landadvisors.my.salesforce.com/{0}'.format(DID)
		cell.add_hyperlink(hyperlink, 'TF', 'Open in TerraForce')

	# Account TF Link
	elif linkType == 'Account':
		cell = sht.range('{0}{1}'.format(colID, rowNo))
		AccountID = cell.value
		cell = sht.range('{0}{1}'.format(colTarget, rowNo))
		if cell.value != None and 'Unknown' not in cell.value:
			hyperlink = 'https://landadvisors.my.salesforce.com/{0}'.format(AccountID)
			cell.add_hyperlink(hyperlink, cell.value, 'Open TerraForce Record')
	
	# Top 100 Link
	elif linkType == 'Top100':
		# Populate only if there is a person
		personColumn = chr(ord(colTarget) - 1)
		cell = sht.range('{0}{1}'.format(personColumn, rowNo))
		if cell.value != None:
			cell = sht.range('{0}{1}'.format(colID, rowNo))
			AccountID = cell.value
			cell = sht.range('{0}{1}'.format(colTarget, rowNo))
			top100 = cell.value
			if top100 == None:
				hyperlink = 'https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}'.format(AccountID)
				cell.add_hyperlink(hyperlink, 'Add', 'Add to Top 100')
	
	# Brochure Link
	elif linkType == 'Brochure':
		cell = sht.range('{0}{1}'.format(colID, rowNo))
		PID = cell.value
		brochureName = '{0}_competitors_package.pdf'.format(PID)
		if brochureName in lBrochures:
			hyperlink = 'https://request-server.s3.amazonaws.com/listings/{0}'.format(brochureName)
			cell = sht.range('{0}{1}'.format(colTarget, rowNo))
			cell.add_hyperlink(hyperlink, 'B', 'Open Brochure')

def buildSimpleHyperlink(linkType, dLine):

	# L5 Link
	if linkType == 'L5':
		# Populate LAO Market if missing
		if dLine['Market__c'] == 'None':
			dLine['Market__c'] = lao.get_market_from_county_state(dLine['County__c'], dLine['State__c'])
		if dLine['StageName__c'] == 'Closed' or dLine['StageName__c'] == 'Closed Lost':
			# td.uInput('comp')
			L5hyperlink = get_L5_url('COMP', dLine['Market__c'], dLine['PID__c'])
			return '=HYPERLINK("{0}", "L5")'.format(L5hyperlink)
		else:
			#td.uInput('ownership')
			L5hyperlink = get_L5_url('OWNERSHIPS', dLine['Market__c'], dLine['PID__c'])
			return '=HYPERLINK("{0}", "L5")'.format(L5hyperlink)
	
	# TF Hyperlink
	if linkType == 'TF':
		TFhyperlink = 'https://landadvisors.my.salesforce.com/{0}'.format(dLine['Id'])
		return '=HYPERLINK("{0}", "TF")'.format(TFhyperlink)

	# Top 100 Link
	if linkType == 'TOP100SELLER':
		tfid = dLine['AccountId__c']
		return '=HYPERLINK("https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}", "Add"'.format(tfid)
	if linkType == 'TOP100BUYER':
		tfid = dLine['Offers__r']['records'][0]['Buyer__r']['Id']
		return '=HYPERLINK("https://landadvisors.my.salesforce.com/apex/Top100Account?Id={0}", "Add"'.format(tfid)
	
	# Brochure Link
	elif linkType == 'BROCHURE':
		brochurehyperlink = 'https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(dLine['PID__c'])
		return '=HYPERLINK("{0}", "B"'.format(brochurehyperlink)

	# Research Request Email Link (R?)
	elif linkType == 'RESEARCH':
		return '=HYPERLINK("mailto:research@landadvisors.com?subject=Update Comp: {0}&body=Please describe the changes/corrections you would like to make to {0}","R?")'.format(dLine['PID__c'])
	
	# Google Map
	elif linkType == 'GOOGLE MAP':
		googlemaplink = 'https://www.google.com/maps/@{0},{1},3000m/data=!3m1!1e3'.format(dLine['Latitude__c'], dLine['Longitude__c'])
		return '=HYPERLINK("{0}", "GM")'.format(googlemaplink)

	# Account TF Link
	elif linkType == 'SELLERENTITY':
		if dLine['Owner_Entity__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['Owner_Entity__r']['Name']
			tfid = dLine['Owner_Entity__c']
	elif linkType == 'SELLERPERSON':
		if dLine['AccountId__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['AccountId__r']['Name']
			tfid = dLine['AccountId__c']
	elif linkType == 'BUYERENTITY':
		if dLine['Offers__r']['records'][0]['Buyer_Entity__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['Offers__r']['records'][0]['Buyer_Entity__r']['Name']
			tfid = dLine['Offers__r']['records'][0]['Buyer_Entity__r']['Id']
	elif linkType == 'BUYERPERSON':
		if dLine['Offers__r']['records'][0]['Buyer__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['Offers__r']['records'][0]['Buyer__r']['Name']
			tfid = dLine['Offers__r']['records'][0]['Buyer__r']['Id']
	elif linkType == 'BENEFICIARY':
		if dLine['Beneficiary__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['Beneficiary__r']['Name']
			tfid = dLine['Beneficiary__r']['Id']
	elif linkType == 'AGENT':
		if dLine['Commissions__r']['records'][0]['Agent__r'] == 'None':
			name = ''
			tfid = ''
		else:
			name = dLine['Commissions__r']['records'][0]['Agent__r']['Name']
			tfid = dLine['Commissions__r']['records'][0]['Agent__c']

	name = name.replace('"', '')
	return '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}", "{1}"'.format(tfid, name)

# Format spreadsheet as table
def formatSheetAsTable(wb, sht, noRows, noCols):
	tbl = sht.tables.add(sht.range((3,1),(noRows,noCols)), table_style_name='TableStyleMedium2')
	sht.range('A1').select()
	sht.autofit('c')
	active_window = wb.app.api.ActiveWindow
	active_window.FreezePanes = False
	active_window.SplitColumn = 0
	active_window.SplitRow = 3
	active_window.FreezePanes = True
	active_window.Zoom = 75

# Format Title
def formatTitle(sht, lastColumn, lastInfoLinkColumn='C'):
	titleRange = 'A1:{0}1'.format(lastColumn)
	sht.range(titleRange).color = (7, 79, 105) # Set title background color
	sht.range(titleRange).api.Font.ColorIndex = 2 # Set title font color to white
	sht.range(titleRange).api.Font.Bold = True # Set title font to bold

# Makes list for line in LLR excel file
def llrCompsLineMaker(dLine):

	# Determine Classficiation
	classification = classParse(dLine['Classification__c'])

	# If Sale Price is $10,000 set to $0
	salePrice = dLine['Sale_Price__c']
	pricePerAcre = dLine['Price_Per_Acre__c']
	if salePrice == 10000:
		salePrice = 0
		pricePerAcre = 0

	# Determine Buyer
	if dLine['Offers__r'] == 'None':
		td.uInput(dLine['PID__c'])
	if dLine['Offers__r']['records'][0]['Buyer_Entity__r'] == 'None':
		if dLine['Offers__r']['records'][0]['Buyer__r'] == 'None':
			buyer = ''
		else:
			buyer = dLine['Offers__r']['records'][0]['Buyer__r']['Name']
	else:
		buyer = dLine['Offers__r']['records'][0]['Buyer_Entity__r']['Name']

	try:	
		# Determine Seller
		if dLine['Owner_Entity__r'] == 'None':
			# print(dLine['PID__c'])
			seller = dLine['AccountId__r']['Name']
		else:
			seller = dLine['Owner_Entity__r']['Name']
	except TypeError:
		td.uInput('TypeError on seller for PID: {0}'.format(dLine['PID__c']))
		
		print('here1')
		pprint(dLine)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		
	
	# Determine Beneficiary & Loan Amount
	beneficiary, loanAmount = '', ''
	if dLine['Beneficiary__r'] != 'None':
		beneficiary = dLine['Beneficiary__r']['Name']
		loanAmount = dLine['Loan_Amount__c']

	# Determine and set Description (will be replaced if there are Lot Details)
	if dLine['Market__c'] == 'Phoenix' and not 'SAND' in dLine['Description__c'].upper():  # Phoenix never has a Description
			description = ''
	else:
		description = dLine['Description__c']
	
	# Determine if LAO Deal
	if dLine['StageName__c'] == 'Closed':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'
	
	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)
	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	if dLine['Lot_Details__r'] == 'None':
		# Create empty single line list
		lLine = []

		# Set Lot Detail Variables
		lotCount, lotWidth, lotDepth, lotPricePer, lotFFPrice = '', '', '', '', ''
		priceperparcel = salePrice

		# Create line list of values
		lLine.append(L5Link)
		lLine.append(TFLink)
		# lLine.append(requestResearch)
		lLine.append(dLine['PID__c'])
		lLine.append(dLine['Lot_Type__c'])
		lLine.append(classification)
		lLine.append(dLine['Submarket__c'])
		lLine.append(dLine['Buyer_Acting_As__c'])
		lLine.append(dLine['Subdivision__c'])
		lLine.append(dLine['Location__c'])
		lLine.append(dLine['City__c'])
		lLine.append(buyer)
		lLine.append(seller)
		lLine.append(dLine['Sale_Date__c'])
		lLine.append(salePrice)
		lLine.append(dLine['Report_Acres__c'])
		lLine.append(pricePerAcre)
		lLine.append(dLine['Lots__c'])
		lLine.append('0')
		lLine.append('0')
		lLine.append(dLine['Price_Per_Lot__c'])
		lLine.append(lotFFPrice)
		lLine.append(priceperparcel)
		lLine.append(description)
		lLine.append(beneficiary)
		lLine.append(loanAmount)
		lLine.append(LAODeal)

		# Remove 'None' values from lLine
		for i in range(len(lLine)):
			if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
				lLine[i] = '--'

		# Add lLine to lList_of_Lines even though there is only one Line
		lList_of_Lines.append(lLine)
		return lList_of_Lines

	#  If there are Lot Details each lot size requires its own line so
	#  cycle through the Lot Detail lot sizes
	for row in dLine['Lot_Details__r']['records']:
		# Create empty single line list
		lLine = []

		# If Sale Price is $10,000 set to $0
		salePrice = dLine['Sale_Price__c']
		pricePerAcre = dLine['Price_Per_Acre__c']
		if dLine['Price_Per_Lot__c'] == 'None':
			lotPricePer = ''
		else:
			lotPricePer = dLine['Price_Per_Lot__c']
		if dLine['Lot_Details__r'] != 'None':
			# Set Lot Detail Variables
			lotFFPrice = row['Price_per_Front_Foot__c']
			lotCount = row['Lot_Count__c']
			lotWidth = row['Lot_Width__c']
			lotDepth = row['Lot_Depth__c']
			pricePerParcel = row['Price_per_parcel__c']
			description = row['Name']
		else:
			lotFFPrice = ''
			lotCount = '0'
			lotWidth = '0'
			lotDepth = '0'
			pricePerParcel = dLine['Sale_Price__c']
			description = dLine['Description__c']
		if salePrice == 10000:
			salePrice = 0
			pricePerAcre = 0
			lotPricePer = ''
			lotFFPrice = ''
		
		pricePerParcel = row['Price_per_parcel__c']
		description = row['Name']

		# Create line list of values
		lLine.append(L5Link)
		lLine.append(TFLink)
		# lLine.append(requestResearch)
		lLine.append(dLine['PID__c'])
		lLine.append(dLine['Lot_Type__c'])
		lLine.append(classification)
		lLine.append(dLine['Submarket__c'])
		lLine.append(dLine['Buyer_Acting_As__c'])
		lLine.append(dLine['Subdivision__c'])
		lLine.append(dLine['Location__c'])
		lLine.append(dLine['City__c'])
		lLine.append(buyer)
		lLine.append(seller)
		lLine.append(dLine['Sale_Date__c'])
		lLine.append(dLine['Sale_Price__c'])
		lLine.append(dLine['Report_Acres__c'])
		lLine.append(dLine['Price_Per_Acre__c'])
		lLine.append(lotCount)
		lLine.append(lotWidth)
		lLine.append(lotDepth)
		lLine.append(lotPricePer)
		lLine.append(lotFFPrice)
		lLine.append(pricePerParcel)
		lLine.append(description)
		lLine.append(beneficiary)
		lLine.append(loanAmount)
		lLine.append(LAODeal)
		# lLine.append(dLine['Id'])
		
		# Remove 'None' values from lLine
		for i in range(len(lLine)):
			if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
				lLine[i] = '--'

		# Add lLine to lList_of_Lines even though there is only one Line
		lList_of_Lines.append(lLine)

	return lList_of_Lines

# Makes list for line in LLR excel file
def llrCompsCallListLineMaker(dLine):
	from pprint import pprint
	# pprint(dLine)

	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# If Sale Price is $10,000 set to $0
	salePrice = dLine['Sale_Price__c']
	pricePerAcre = dLine['Price_Per_Acre__c']
	lotPricePer = dLine['Price_Per_Lot__c']
	lotFFPrice = dLine['Weighted_Avg_Price_Per_FF__c']
	if salePrice == 10000:
		salePrice = 0
		pricePerAcre = 0
		lotPricePer = ''
		lotFFPrice = ''

	# Determine Buyer Entity
	if dLine['Offers__r'] == 'None':
		print('no offer!!')
		td.uInput(dLine['PID__c'])
	buyerEntityName = ''
	if dLine['Offers__r']['records'][0]['Buyer_Entity__r'] != 'None':
		buyerEntityName = buildSimpleHyperlink('BUYERENTITY', dLine)
	
	# Determine Buyer Person
	buyerPersonName, buyerPersonPhone, buyerPersonMobile, buyerPersonEmail, buyerPersonTop100 = '', '', '', '', ''
	if dLine['Offers__r']['records'][0]['Buyer__r'] != 'None':
		buyerPersonName = buildSimpleHyperlink('BUYERPERSON', dLine)
		buyerPersonPhone = dLine['Offers__r']['records'][0]['Buyer__r']['Phone']
		buyerPersonMobile = dLine['Offers__r']['records'][0]['Buyer__r']['PersonMobilePhone']
		buyerPersonEmail = dLine['Offers__r']['records'][0]['Buyer__r']['PersonEmail']
		# if dLine['Offers__r']['records'][0]['Buyer__r']['Top100__c'] != []:
		if dLine['Offers__r']['records'][0]['Buyer__r']['Top100__c'] != 'None':
			buyerPersonTop100 = 'MVP'
		else:
			buyerPersonTop100 = buildSimpleHyperlink('TOP100BUYER', dLine)
	
	# Determine Seller Entity
	sellerEntityName = ''
	if dLine['Owner_Entity__r'] != 'None':
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
	
	# Determine Seller Person
	sellerPersonName, sellerPersonPhone, sellerPersonMobile, sellerPersonEmail, sellerPersonTop100 = '', '', '', '', ''
	if dLine['AccountId__r'] != 'None':
		sellerPersonName = buildSimpleHyperlink('SELLERPERSON', dLine)
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = buildSimpleHyperlink('TOP100SELLER', dLine)
	
	# Determine Beneficiary & Loan Amount
	beneficiary, loanAmount = '', ''
	if dLine['Beneficiary__r'] != 'None':
		beneficiary = buildSimpleHyperlink('BENEFICIARY', dLine)
		loanAmount = dLine['Loan_Amount__c']		

	# Determine and set Dectiption (will be replaced if there are Lot Details)
	if dLine['Market__c'] == 'Phoenix' and not 'SAND' in dLine['Description__c'].upper():  # Phoenix never has a Description
			description = ''
	else:
		description = dLine['Description__c']
	
	# Determine if LAO Deal
	if dLine['StageName__c'] == 'Closed':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'
	
	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)
	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)
	# Request Research Email (R?)
	# requestResearch = buildSimpleHyperlink('RESEARCH', dLine)

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Buyer_Acting_As__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(buyerEntityName)
	lLine.append(buyerPersonName)
	lLine.append(buyerPersonTop100)
	lLine.append(buyerPersonPhone)
	lLine.append(buyerPersonMobile)
	lLine.append(buyerPersonEmail)
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(dLine['Sale_Date__c'])
	lLine.append(salePrice)
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(pricePerAcre)
	lLine.append(dLine['Lots__c'])
	lLine.append(lotPricePer)
	lLine.append(lotFFPrice)
	lLine.append(description)
	lLine.append(beneficiary)
	lLine.append(loanAmount)
	lLine.append(LAODeal)
	
	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Makes list for line in LLR External file
def llrCompsExternalLineMaker(dLine):

	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# If Sale Price is $10,000 set to $0
	salePrice = dLine['Sale_Price__c']
	pricePerAcre = dLine['Price_Per_Acre__c']
	if salePrice == 10000:
		salePrice = 0
		pricePerAcre = 0

	# Determine Seller
	if dLine['Owner_Entity__r'] == 'None':
		seller = dLine['AccountId__r']['Name']
	else:
		seller = dLine['Owner_Entity__r']['Name']
	
	# Determine and set Dectiption (will be replaced if there are Lot Details)
	if dLine['Market__c'] == 'Phoenix':  # Phoenix never has a Description
		description = ''
	else:
		description = dLine['Description__c']
	
	# Determine if LAO Deal
	if dLine['StageName__c'] == 'Closed':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'
	
	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	if dLine['Lot_Details__r'] == 'None':
		# Create empty single line list
		lLine = []

		# Set Lot Detail Variables
		lotCount, lotWidth, lotDepth, lotPricePer, lotFFPrice = '', '', '', '', ''
		pricePerParcel = salePrice
		# Create line list of values
		lLine.append(dLine['Lot_Type__c'])
		lLine.append(classification)
		lLine.append(dLine['Submarket__c'])
		lLine.append(dLine['Buyer_Acting_As__c'])
		lLine.append(dLine['Subdivision__c'])
		lLine.append(dLine['Location__c'])
		lLine.append(dLine['City__c'])
		lLine.append(seller)
		lLine.append(dLine['Sale_Date__c'])
		lLine.append(salePrice)
		lLine.append(dLine['Report_Acres__c'])
		lLine.append(pricePerAcre)
		lLine.append(lotCount)
		lLine.append(lotWidth)
		lLine.append(lotDepth)
		lLine.append(lotPricePer)
		lLine.append(lotFFPrice)
		lLine.append(pricePerParcel)
		lLine.append(description)

		# Remove 'None' values from lLine
		for i in range(len(lLine)):
			if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
				lLine[i] = '--'

		# Add lLine to lList_of_Lines even though there is only one Line
		lList_of_Lines.append(lLine)
		return lList_of_Lines

	#  If there are Lot Details each lot size requires its own line so
	#  cycle through the Lot Detail lot sizes
	for row in dLine['Lot_Details__r']['records']:
		lLine = []

		# If Sale Price is $10,000 set to $0
		salePrice = dLine['Sale_Price__c']
		pricePerAcre = dLine['Price_Per_Acre__c']
		if dLine['Price_Per_Lot__c'] == 'None':
			lotPricePer = ''
		else:
			lotPricePer = dLine['Price_Per_Lot__c']
		if dLine['Lot_Details__r'] != 'None':
			# Set Lot Detail Variables
			lotFFPrice = row['Price_per_Front_Foot__c']
			lotCount = row['Lot_Count__c']
			lotWidth = row['Lot_Width__c']
			lotDepth = row['Lot_Depth__c']
			pricePerParcel = row['Price_per_parcel__c']
			description = row['Name']
		else:
			lotFFPrice = ''
			lotCount = '0'
			lotWidth = '0'
			lotDepth = '0'
			pricePerParcel = dLine['Sale_Price__c']
			description = dLine['Description__c']
		if salePrice == 10000:
			salePrice = 0
			pricePerAcre = 0
			lotPricePer = ''
			lotFFPrice = ''

		# Create line list of values
		lLine.append(dLine['Lot_Type__c'])
		lLine.append(classification)
		lLine.append(dLine['Submarket__c'])
		lLine.append(dLine['Buyer_Acting_As__c'])
		lLine.append(dLine['Subdivision__c'])
		lLine.append(dLine['Location__c'])
		lLine.append(dLine['City__c'])
		lLine.append(seller)
		lLine.append(dLine['Sale_Date__c'])
		lLine.append(salePrice)
		lLine.append(dLine['Report_Acres__c'])
		lLine.append(pricePerAcre)
		lLine.append(lotCount)
		lLine.append(lotWidth)
		lLine.append(lotDepth)
		lLine.append(lotPricePer)
		lLine.append(lotFFPrice)
		lLine.append(pricePerParcel)
		lLine.append(description)
		
		# Remove 'None' values from lLine
		for i in range(len(lLine)):
			if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
				lLine[i] = '--'

		# Add lLine to lList_of_Lines even though there is only one Line
		lList_of_Lines.append(lLine)

	return lList_of_Lines

# Makes list for line in LLR excel file
def llrCompsCompetitorListingsLineMaker(dLine, lBrochures):

	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# Calculate Price per Acre
	try:
		if dLine['List_Price__c'] == 'None' or dLine['List_Price__c'] == 0 or dLine['Report_Acres__c'] == 0:
			priceperacre = ''
		else:
			priceperacre = dLine['List_Price__c'] / dLine['Report_Acres__c']
	except ZeroDivisionError:
		# pprint(dLine)
		print('\n Bad price per acre error\n\n')

	# Determine Seller Entity
	sellerEntityName = ''
	if dLine['Owner_Entity__r'] != 'None':
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
	
	# Determine Seller Person
	sellerPersonName, sellerPersonPhone, sellerPersonMobile, sellerPersonEmail, sellerPersonTop100 = '', '', '', '', ''
	if dLine['AccountId__r'] != 'None':
		sellerPersonName = buildSimpleHyperlink('SELLERPERSON', dLine)
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'

	# Determine Listing Agent Person
	agentEntityName, agentPersonName, agentPersonPhone, agentPersonEmail = '', '', '', ''
	if dLine['Commissions__r'] != 'None':
		agentPersonName = buildSimpleHyperlink('AGENT', dLine)
		agentPersonPhone = dLine['Commissions__r']['records'][0]['Agent__r']['Phone']
		agentPersonEmail = dLine['Commissions__r']['records'][0]['Agent__r']['PersonEmail']
		# if dLine['Commissions__r']['records'][0]['Agent__c'] != 'None':
		if dLine['Commissions__r']['records'][0]['Agent__r']['Company__r'] != 'None':
			agentEntityName = dLine['Commissions__r']['records'][0]['Agent__r']['Company__r']['Name']

	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)

	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Brochure Link
	brochurename = '{0}_competitors_package.pdf'.format(dLine['PID__c'])
	# pprint(lBrochures)
	if brochurename in lBrochures:
		brochureLink = buildSimpleHyperlink('BROCHURE', dLine)
	else:
		brochureLink = ''
	

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(brochureLink)
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(dLine['List_Price__c'])
	lLine.append(priceperacre)
	lLine.append(dLine['List_Date__c'])
	lLine.append(dLine['Listing_Expiration_Date__c'])
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(agentEntityName)
	lLine.append(agentPersonName)
	lLine.append(agentPersonPhone)
	lLine.append(agentPersonEmail)

	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Makes list for line in LLR excel file
def llrLAODealsLineMaker(dLine):
	from pprint import pprint
	from datetime import datetime
	
	# Determine Classficiation
	classification = classParse(dLine['Classification__c'])

	# Determine Seller Entity
	if dLine['Owner_Entity__r'] == 'None':
		sellerEntityName = ''
		sellerEntityId = ''
	else:
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
		sellerEntityId = dLine['Owner_Entity__c']
	
	# Determine Seller Person
	if dLine['AccountId__r'] == 'None':
		sellerPersonName = ''
		sellerPersonPhone = ''
		sellerPersonMobile = ''
		sellerPersonEmail = ''
		sellerPersonTop100 = ''
		sellerPersonId = ''
	else:
		sellerPersonName = buildSimpleHyperlink('SELLERPERSON', dLine)
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = ''
		sellerPersonId = dLine['AccountId__c']

	# # Convert Stage Top100 to MVP
	# if dLine['StageName__c'] == 'Top 100':
	# 	stage_name = 'MVP'
	# else:
	# 	stage_name = dLine['StageName__c']

	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)

	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Format Created Date  ZZZZ
	# createdDate = dLine['CreatedDate'].strftime('%m-%d-%Y')
	createdDate = datetime.strptime(dLine['CreatedDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m-%d-%Y')

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['StageName__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(createdDate)

	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Makes list for line in LLR excel file
def llrTop100DealsLineMaker(dLine):
	from pprint import pprint
	from datetime import datetime
	
	# Determine Classficiation
	classification = classParse(dLine['Classification__c'])

	# Determine Seller Entity
	if dLine['Owner_Entity__r'] == 'None':
		sellerEntityName = ''
		sellerEntityId = ''
	else:
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
		sellerEntityId = dLine['Owner_Entity__c']
	
	# Determine Seller Person
	if dLine['AccountId__r'] == 'None':
		sellerPersonName = ''
		sellerPersonStreet = ''
		sellerPersonCity = ''
		sellerPersonState = ''
		sellerPersonZipCode = ''
		sellerPersonPhone = ''
		sellerPersonMobile = ''
		sellerPersonEmail = ''
		sellerPersonTop100 = ''
		sellerPersonId = ''
	else:
		# pprint(dLine)
		sellerPersonName = dLine['AccountId__r']['Name']
		sellerPersonStreet = dLine['AccountId__r']['BillingStreet']
		sellerPersonCity = dLine['AccountId__r']['BillingCity']
		sellerPersonState = dLine['AccountId__r']['BillingState']
		sellerPersonZipCode = dLine['AccountId__r']['BillingPostalCode']
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = ''
		sellerPersonId = dLine['AccountId__c']

	# Convert Stage Top100 to MVP
	if dLine['StageName__c'] == 'Top 100':
		stage_name = 'MVP'
	else:
		stage_name = dLine['StageName__c']

	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)

	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Format Created Date  ZZZZ
	# createdDate = dLine['CreatedDate'].strftime('%m-%d-%Y')
	createdDate = datetime.strptime(dLine['CreatedDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m-%d-%Y')

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(dLine['PID__c'])
	lLine.append(stage_name)
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(dLine['Lots__c'])
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(sellerPersonStreet)
	lLine.append(sellerPersonCity)
	lLine.append(sellerPersonState)
	lLine.append(sellerPersonZipCode)
	lLine.append(createdDate)

	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Makes list for line in LLR excel file
def llrAllLeadDealsLineMaker(dLine):
	from pprint import pprint
	from datetime import datetime
	
	# Determine Classficiation
	classification = classParse(dLine['Classification__c'])

	# Determine Seller Entity
	if dLine['Owner_Entity__r'] == 'None':
		sellerEntityName = ''
		sellerEntityId = ''
	else:
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
		# sellerEntityName = dLine['Owner_Entity__r']['Name']
		sellerEntityId = dLine['Owner_Entity__c']
	
	# Determine Seller Person
	if dLine['AccountId__r'] == 'None':
		sellerPersonName = ''
		sellerPersonPhone = ''
		sellerPersonMobile = ''
		sellerPersonEmail = ''
		sellerPersonTop100 = ''
		sellerPersonId = ''
	else:
		sellerPersonName = buildSimpleHyperlink('SELLERPERSON', dLine)
		# sellerPersonName = dLine['AccountId__r']['Name']
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = ''
		sellerPersonId = dLine['AccountId__c']
	
	# Determine Beneficiary & Loan Amount
	beneficiary, loanAmount = '', ''
	if dLine['Beneficiary__r'] != 'None':
		beneficiary = buildSimpleHyperlink('BENEFICIARY', dLine)
		loanAmount = dLine['Loan_Amount__c']	

	# Convert Stage Top100 to MVP
	if dLine['StageName__c'] == 'Top 100':
		stage_name = 'MVP'
	else:
		stage_name = dLine['StageName__c']

	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)

	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Format Created Date
	# createdDate = dLine['CreatedDate'].strftime('%m-%d-%Y')
	createdDate = datetime.strptime(dLine['CreatedDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m-%d-%Y')

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(dLine['PID__c'])
	lLine.append(stage_name)
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(beneficiary)
	lLine.append(loanAmount)
	lLine.append(createdDate)
	
	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Makes list for line in LLR excel file
def llrOwnershipsLineMaker(dLine):

	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# Determine Seller Entity
	if dLine['Owner_Entity__r'] == 'None':
		sellerEntityName = ''
		sellerEntityId = ''
		sellerEntityNameLink = ''
	else:
		sellerEntityName = dLine['Owner_Entity__r']['Name']
		sellerEntityName = sellerEntityName.replace('"', '')
		sellerEntityId = dLine['Owner_Entity__r']['Id']
		sellerEntityNameLink = '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}", "{1}"'.format(sellerEntityId, sellerEntityName)

	# Determine Seller Person
	if dLine['AccountId__r'] == 'None':
		sellerPersonName = ''
		sellerPersonPhone = ''
		sellerPersonMobile = ''
		sellerPersonEmail = ''
		sellerPersonTop100 = ''
		sellerPersonId = ''
		sellerPersonNameLink = ''
	else:
		sellerPersonName = dLine['AccountId__r']['Name']
		sellerPersonName = sellerPersonName.replace('"', '')
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = ''
		sellerPersonId = dLine['AccountId__c']
		sellerPersonNameLink = '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}", "{1}"'.format(sellerPersonId, sellerPersonName)

	# Determine and set Description (will be replaced if there are Lot Details)
	if dLine['Market__c'] == 'Phoenix':  # Phoenix never has a Description
		description = ''
	else:
		description = dLine['Description__c']
	
	# Determine if LAO Deal
	if dLine['StageName__c'] != 'Lead':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'
	
	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)

	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	# lLine.append('L5')
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['StageName__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(dLine['Lots__c'])
	lLine.append(sellerEntityNameLink)
	lLine.append(sellerPersonNameLink)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)
	lLine.append(description)
	lLine.append(LAODeal)

	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)

	return lList_of_Lines

# Makes list for line in LLR excel file
def llrDeedsOfTrustLineMaker(dLine):
	
	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# Determine Buyer Entity
	if dLine['Offers__r'] == 'None':
		td.warningMsg('no offer!!')
		print(dLine['PID__c'])
		lao.holdup()
	if dLine['Offers__r']['records'][0]['Buyer_Entity__r'] == 'None':
		buyerEntityName = ''
		buyerEntityId = ''
	else:
		buyerEntityName = dLine['Offers__r']['records'][0]['Buyer_Entity__r']['Name']
		buyerEntityId = dLine['Offers__r']['records'][0]['Buyer_Entity__r']['Id']
	
	# Determine Buyer Person
	if dLine['Offers__r']['records'][0]['Buyer__r'] == 'None':
		buyerPersonName = ''
		buyerPersonPhone = ''
		buyerPersonMobile = ''
		buyerPersonEmail = ''
		buyerPersonTop100 = ''
		buyerPersonId = ''
	else:
		buyerPersonName = dLine['Offers__r']['records'][0]['Buyer__r']['Name']
		buyerPersonPhone = dLine['Offers__r']['records'][0]['Buyer__r']['Phone']
		buyerPersonMobile = dLine['Offers__r']['records'][0]['Buyer__r']['PersonMobilePhone']
		buyerPersonEmail = dLine['Offers__r']['records'][0]['Buyer__r']['PersonEmail']
		if dLine['Offers__r']['records'][0]['Buyer__r']['Top100__c'] != 'None':
			buyerPersonTop100 = 'MVP'
		else:
			buyerPersonTop100 = ''
		buyerPersonId = dLine['Offers__r']['records'][0]['Buyer__r']['Id']

	# Determine Beneficiary
	if dLine['Beneficiary__r'] == 'None':
		beneficiaryName = ''
		beneficiaryId = ''
	else:
		beneficiaryName = dLine['Beneficiary__r']['Name']
		beneficiaryId = dLine['Beneficiary__r']['Id']

	# Determine Beneficiary Person
	if dLine['Beneficiary_Contact__r'] == 'None':
		beneficiaryContactName = ''
		beneficiaryContactPhone = ''
		beneficiaryContactMobile = ''
		beneficiaryContactEmail = ''
		beneficiaryContactTop100 = ''
		beneficiaryContactId = ''
	else:
		beneficiaryContactName = dLine['Beneficiary_Contact__r']['Name']
		beneficiaryContactPhone = dLine['Beneficiary_Contact__r']['Phone']
		beneficiaryContactMobile = dLine['Beneficiary_Contact__r']['PersonMobilePhone']
		beneficiaryContactEmail = dLine['Beneficiary_Contact__r']['PersonEmail']
		if dLine['Beneficiary_Contact__r']['Top100__c'] != []:
			beneficiaryContactTop100 = 'Top100'
		else:
			beneficiaryContactTop100 = ''
		beneficiaryContactId = dLine['Beneficiary_Contact__r']['Id']

	# Determine if LAO Deal
	if dLine['StageName__c'] == 'Closed':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'

	# Request Research Email (R?)
	# requestResearch = '=HYPERLINK("mailto:research@landadvisors.com?subject=Update Comp: {0}&body=Please describe the changes/corrections you would like to make to {0}","R?")'.format(dLine['PID__c'])

	# Set empty "List of Lines" and individual "Line" list variables
	lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append('L5')
	lLine.append('TF')
	# lLine.append(requestResearch)
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['StageName__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Sale_Date__c'])
	lLine.append(dLine['Sale_Price__c'])
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(dLine['Encumbrance_Rating__c'])
	lLine.append(dLine['Loan_Amount__c'])
	lLine.append(dLine['Credit_Bid_Amount__c'])
	lLine.append(buyerEntityName)
	lLine.append(buyerPersonName)
	lLine.append(buyerPersonTop100)
	lLine.append(buyerPersonPhone)
	lLine.append(buyerPersonMobile)
	lLine.append(buyerPersonEmail)
	lLine.append(beneficiaryName)
	lLine.append(beneficiaryContactName)
	lLine.append(beneficiaryContactTop100)
	lLine.append(beneficiaryContactPhone)
	lLine.append(beneficiaryContactMobile)
	lLine.append(beneficiaryContactEmail)
	lLine.append(LAODeal)
	lLine.append(dLine['Id'])
	lLine.append(buyerEntityId)
	lLine.append(buyerPersonId)
	lLine.append(beneficiaryId)
	lLine.append(beneficiaryContactId)

	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'
	
	# Add lLine to lList_of_Lines even though there is only one Line
	lList_of_Lines.append(lLine)
	return lList_of_Lines

# Format Sheet - Comps Deals
def formatCompsSheet(mkt, wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,14),(noRows,14)).number_format='$#,##0' # Sale Price
	sht.range((4,16),(noRows,16)).number_format='$#,##0' # $/Ac
	sht.range((4,20),(noRows,22)).number_format='$#,##0' # $/Lot, $/FF
	sht.range((4,25),(noRows,25)).number_format='$#,##0' # Loan Amount

	# Format Title
	formatTitle(sht, 'Z', 'C')
	# Format Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	# Format Rows & Columns
	sht.range('A3:AA{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set first 3 colums to 2.7
	sht.range('C:E').column_width = 25 # Set PID, Lot Type, Classification
	sht.range('F:G').column_width = 20 # Set Submarket, BAA
	sht.range('H:I').column_width = 35 # Set Subdivision & Location
	sht.range('K:L').column_width = 40 # Set Buyer, Seller
	sht.range('M:V').column_width = 13 # Sale Date to $/Parcel
	sht.range('W:W').column_width = 25 # Set Description

# Format Sheet - Comps Call List Deals
def formatCompsCallListSheet(mkt, wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,24),(noRows,24)).number_format='$#,##0' # Sale Price
	sht.range((4,26),(noRows,26)).number_format='$#,##0' # $/Ac
	sht.range((4,28),(noRows,29)).number_format='$#,##0' # $/Lot
	sht.range((4,32),(noRows,32)).number_format='$#,##0' # Loan Amount

	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AG{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set frist 3 columns to 2.7
	sht.range('C:E').column_width = 25 # Set PID Lot Type Classification
	sht.range('F:G').column_width = 20 # Set Submarket, BAA
	sht.range('H:I').column_width = 35 # Set Subdivision & Location
	sht.range('K:K').column_width = 40 # Set Buyer Entity
	sht.range('L:L').column_width = 30 # Set Buyer Person
	sht.range('M:M').column_width = 10 # Set MVP Top 100
	sht.range('N:O').column_width = 15 # Set Phone & Mobile
	sht.range('P:P').column_width = 20 # Set Email
	sht.range('Q:Q').column_width = 40 # Set Seller Entity
	sht.range('R:R').column_width = 30 # Set Seller Person
	sht.range('S:S').column_width = 10 # Set MVP Top 100
	sht.range('T:U').column_width = 15 # Set Phone & Mobile
	sht.range('V:V').column_width = 20 # Set Email
	sht.range('X:AC').column_width = 13 # Sale Price to $/FF
	sht.range('AD:AD').column_width = 25 # Set Description

	# Remove TF Id columns from sheet
	sht.range('AI:AM').api.Delete()

	# Format Title
	formatTitle(sht, 'AG', 'C')

# Format Sheet - Competitor Listings Deals
def formatCompetitorListingsSheet(mkt, wb, sht, noRows, noCols, lBrochures):
	from webs import get_L5_url

	# Format Currency coloumns
	sht.range((4,11),(noRows,12)).number_format='$#,##0' # List Price & $/Ac


	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AB{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:C').column_width = 2.7 # Set first four columns to 2.7
	sht.range('D:F').column_width = 25 # Set PID Lot Type Classification
	sht.range('I:I').column_width = 35 # Set Subdivision Column to 35
	sht.range('K:N').column_width = 13 # Sale Price to List X Date
	sht.range('O:P').column_width = 40 # Set Seller & Person
	sht.range('Q:Q').column_width = 10 # Set MVP Top 100
	sht.range('R:S').column_width = 15 # Set Phone & Mobile
	sht.range('T:T').column_width = 20 # Set Email
	sht.range('U:U').column_width = 40 # Set Listing Entity
	sht.range('V:V').column_width = 30 # Set Seller & Person
	sht.range('W:W').column_width = 15 # Set Phone
	sht.range('X:X').column_width = 20 # Set Email

	# Format Title
	formatTitle(sht, 'X', 'D')

# Format Sheet - Top 100/MVP Deals
def formatLAODealsSheet(mkt, wb, sht, noRows, noCols):
	# Sort by Submarket then Type
	# sht.range((4,1),(noRows,noCols)).api.Sort(Key1=sht.range('E4').api, Order1=1, Key2=sht.range('H4').api, Order2=1)

	# Format Currency coloumns
	sht.range((4,12),(noRows,13)).number_format='$#,##0' # List Price & $/Ac

	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AB{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set first four columns to 2.7
	sht.range('C:F').column_width = 25 # Set PID, Stage, Lot Type, Classification
	sht.range('H:I').column_width = 35 # Set Subdivision & Location
	sht.range('M:N').column_width = 35 # Set Seller & Person
	sht.range('N:N').column_width = 10 # Set MVP Top 100
	sht.range('O:P').column_width = 15 # Set Phone & Mobile
	sht.range('Q:Q').column_width = 30 # Set Email
	sht.range('Q:Q').column_width = 15 # Set Created Date

	# Format Title
	formatTitle(sht, 'R', 'C')

# Format Sheet - Top 100/MVP Deals
def formatTop100DealsSheet(mkt, wb, sht, noRows, noCols):
	# Sort by Submarket then Type
	# sht.range((4,1),(noRows,noCols)).api.Sort(Key1=sht.range('E4').api, Order1=1, Key2=sht.range('H4').api, Order2=1)

	# Format Currency coloumns
	sht.range((4,12),(noRows,13)).number_format='#,##0' # List Price & $/Ac

	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AB{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set first four columns to 2.7
	sht.range('C:C').column_width = 25 # Set PID
	sht.range('D:D').column_width = 9 # Set StageName (MVP)
	sht.range('E:G').column_width = 25 # Set PID, Stage, Lot Type, Classification
	sht.range('H:I').column_width = 35 # Set Subdivision & Location
	sht.range('M:N').column_width = 35 # Set Seller & Person
	sht.range('N:N').column_width = 10 # Set MVP Top 100
	sht.range('O:P').column_width = 15 # Set Phone & Mobile
	sht.range('Q:Q').column_width = 30 # Set Email
	#sht.range('Q:Q').column_width =  # Set Created Date

	# Format Title
	formatTitle(sht, 'V', 'C')

def formatOwnershipsSheet(mkt, wb, sht, noRows, noCols):
	import lao

	# Format Currency coloumns
	sht.range((4,19),(noRows,19)).number_format='$#,##0' # Sale Price

	# Format Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:X{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set first two columns to 2.7
	sht.range('C:F').column_width = 25 # Set PID, Stage, Lot Type, Classification 
	sht.range('H:I').column_width = 35 # Set Subdivision & Location
	sht.range('L:M').column_width = 35 # Set Seller Entity & Seller
	sht.range('N:N').column_width = 10 # Set MVP Top 100
	sht.range('O:P').column_width = 15 # Set Phone & Mobile
	sht.range('Q:Q').column_width = 20 # Set Email


	# # Remove TF Id columns from sheet
	# sht.range('V:X').api.Delete()

	# Format Title
	formatTitle(sht, 'T', 'C')

# Format Sheet - Comps External
def formatCompsExternalSheet(mkt, wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,10),(noRows,10)).number_format='$#,##0'
	sht.range((4,12),(noRows,12)).number_format='$#,##0'
	sht.range((4,21),(noRows,23)).number_format='$#,##0'
	sht.range((4,26),(noRows,26)).number_format='$#,##0'


	# Format Title
	formatTitle(sht, 'S', 'C')
	# Format Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:S{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:D').column_width = 25 # Set PID & Location Column to 35
	sht.range('E:F').column_width = 35 # Set Subdivision & Location Column to 35
	sht.range('H:H').column_width = 35 # Set Buyer & Seller Columns to 50
	sht.range('J:L').column_width = 14 # Set Price, Acres, $/Ac
	sht.range('S:S').column_width = 25 # Set Description column to 50

# Makes list for line in LLR excel file
def llr_debt_list_line_maker(dLine):
	from pprint import pprint
	# pprint(dLine)

	# Error trap if Market is Georgia
	if dLine['Market__c'] == 'Georgia':
		dLine['Market__c'] = 'Atlanta'
	if dLine['Market__c'] == 'Chattanooga':
		dLine['Market__c'] = 'Atlanta'
	if dLine['Market__c'] == 'Knoxville':
		dLine['Market__c'] = 'Nashville'
	if dLine['Market__c'] == 'North Carolina':
		dLine['Market__c'] = 'Charlotte'

	# Determint Classficiation
	classification = classParse(dLine['Classification__c'])

	# If Sale Price is $10,000 set to $0
	salePrice = dLine['Sale_Price__c']
	pricePerAcre = dLine['Price_Per_Acre__c']
	lotPricePer = dLine['Price_Per_Lot__c']
	lotFFPrice = dLine['Weighted_Avg_Price_Per_FF__c']
	if salePrice == 10000:
		salePrice = 0
		pricePerAcre = 0
		lotPricePer = ''
		lotFFPrice = ''

	# Determine Buyer Entity
	# if dLine['Offers__r'] == 'None':
	# 	print('no offer!!')
	# 	td.uInput(dLine['PID__c'])
	# Offer values are not always present
	buyerEntityName, buyerPersonName, buyerPersonPhone, buyerPersonMobile, buyerPersonEmail, buyerPersonTop100 = '', '', '', '', '', ''
	if dLine['Offers__r'] != 'None':
		if dLine['Offers__r']['records'][0]['Buyer_Entity__r'] != 'None':
			buyerEntityName = buildSimpleHyperlink('BUYERENTITY', dLine)
			# Determine Buyer Person
		if dLine['Offers__r']['records'][0]['Buyer__r'] != 'None':
			buyerPersonName = buildSimpleHyperlink('BUYERPERSON', dLine)
			buyerPersonPhone = dLine['Offers__r']['records'][0]['Buyer__r']['Phone']
			buyerPersonMobile = dLine['Offers__r']['records'][0]['Buyer__r']['PersonMobilePhone']
			buyerPersonEmail = dLine['Offers__r']['records'][0]['Buyer__r']['PersonEmail']
			# if dLine['Offers__r']['records'][0]['Buyer__r']['Top100__c'] != []:
			if dLine['Offers__r']['records'][0]['Buyer__r']['Top100__c'] != 'None':
				buyerPersonTop100 = 'MVP'
			else:
				buyerPersonTop100 = buildSimpleHyperlink('TOP100BUYER', dLine)
	
	# Determine Seller Entity
	sellerEntityName = ''
	if dLine['Owner_Entity__r'] != 'None':
		sellerEntityName = buildSimpleHyperlink('SELLERENTITY', dLine)
	
	# Determine Seller Person
	sellerPersonName, sellerPersonPhone, sellerPersonMobile, sellerPersonEmail, sellerPersonTop100 = '', '', '', '', ''
	if dLine['AccountId__r'] != 'None':
		sellerPersonName = buildSimpleHyperlink('SELLERPERSON', dLine)
		sellerPersonPhone = dLine['AccountId__r']['Phone']
		sellerPersonMobile = dLine['AccountId__r']['PersonMobilePhone']
		sellerPersonEmail = dLine['AccountId__r']['PersonEmail']
		if dLine['AccountId__r']['Top100__c'] != 'None':
			sellerPersonTop100 = 'MVP'
		else:
			sellerPersonTop100 = buildSimpleHyperlink('TOP100SELLER', dLine)
	
	# Determine Beneficiary & Loan Amount
	beneficiary, loanAmount = '', ''
	if dLine['Beneficiary__r'] != 'None':
		# Standarize Lender Name
		dLine['Beneficiary__r']['Name'] = td.standarize_lender_names(dLine['Beneficiary__r']['Name'])
		beneficiary = buildSimpleHyperlink('BENEFICIARY', dLine)
	loanAmount = dLine['Loan_Amount__c']		

	# Determine and set Dectiption (will be replaced if there are Lot Details)
	if dLine['Market__c'] == 'Phoenix' and not 'SAND' in dLine['Description__c'].upper():  # Phoenix never has a Description
			description = ''
	else:
		description = dLine['Description__c']
	
	# Determine if LAO Deal
	if dLine['StageName__c'] == 'Closed':
		LAODeal = 'TRUE'
	else:
		LAODeal = 'FALSE'
	
	# L5 Link
	L5Link = buildSimpleHyperlink('L5', dLine)
	# TF Hyperlink
	TFLink = buildSimpleHyperlink('TF', dLine)
	# Request Research Email (R?)
	# requestResearch = buildSimpleHyperlink('RESEARCH', dLine)

	# Set empty "List of Lines" and individual "Line" list variables
	# lList_of_Lines = []

	# Determine Lot Details
	#   If there are no Lot Details then there will only be one line
	#   for the record
	lLine = []

	# Create line list of values
	lLine.append(L5Link)
	lLine.append(TFLink)
	lLine.append(LAODeal)
	lLine.append(dLine['Market__c'])
	lLine.append(dLine['StageName__c'])
	lLine.append(dLine['PID__c'])
	lLine.append(dLine['Lot_Type__c'])
	lLine.append(classification)
	lLine.append(dLine['Buyer_Acting_As__c'])
	lLine.append(dLine['Sale_Date__c'])
	lLine.append(salePrice)
	lLine.append(loanAmount)
	lLine.append(dLine['Report_Acres__c'])
	lLine.append(pricePerAcre)
	lLine.append(dLine['Lots__c'])
	lLine.append(lotPricePer)
	lLine.append(lotFFPrice)
	lLine.append(beneficiary)
	lLine.append(buyerPersonTop100)
	lLine.append(buyerEntityName)
	lLine.append(buyerPersonName)
	lLine.append(buyerPersonPhone)
	lLine.append(buyerPersonMobile)
	lLine.append(buyerPersonEmail)
	lLine.append(sellerPersonTop100)
	lLine.append(sellerEntityName)
	lLine.append(sellerPersonName)
	lLine.append(sellerPersonPhone)
	lLine.append(sellerPersonMobile)
	lLine.append(sellerPersonEmail)	
	lLine.append(dLine['City__c'])
	lLine.append(dLine['Submarket__c'])
	lLine.append(dLine['Subdivision__c'])
	lLine.append(dLine['Location__c'])
	lLine.append(description)
		
	# Remove 'None' values from lLine
	for i in range(len(lLine)):
		if lLine[i] == 'None' or lLine[i] == '' or lLine[i] == '.':
			lLine[i] = '--'

	return lLine

# Makes line for Debt LLR Tax Delinquent worksheet
def llr_debt_tax_delinquent_line_maker(dLine):
	from pprint import pprint

	# Create line list of values
	lLine = []
	lLine.append(dLine['Map']),
	lLine.append(dLine['State']),
	lLine.append(dLine['LAO Market']),
	lLine.append(dLine['County']),
	lLine.append(dLine['LAO Submarket']),
	lLine.append(dLine['City']),
	lLine.append(dLine['APN']),
	lLine.append(dLine['Lot Acres']),
	lLine.append(dLine['Zoning']),
	lLine.append(dLine['Tax Delinquent $']),
	lLine.append(dLine['Purchase Date']),
	lLine.append(dLine['Purchase Amt']),
	lLine.append(dLine['Owner']),
	lLine.append(dLine['Primary Name']),
	lLine.append(dLine['Mail Address']),
	lLine.append(dLine['Mail City']),
	lLine.append(dLine['Mail State']),
	lLine.append(dLine['Mail ZIP']),
	lLine.append(dLine['Primary Phone1']),
	lLine.append(dLine['Primary Mobile Phone1']),
	lLine.append(dLine['Primary Email1']),
	lLine.append(dLine['1st Orig Lender']),
	lLine.append(dLine['1st Amount']),
	lLine.append(dLine['1st Rec Date']),
	lLine.append(dLine['1st Purpose']),
	lLine.append(dLine['Foreclosure?']),
	lLine.append(dLine['FCL Doc Type']),
	lLine.append(dLine['FCL Rec Date']),
	lLine.append(dLine['FCL Stage']),
	lLine.append(dLine['Default Date']),
	lLine.append(dLine['Default Amt'])

	return lLine

# Makes line for Debt LLR Foreclosure worksheet
def llr_debt_foreclosure_line_maker(dLine):
	from pprint import pprint
	
	# Create line list of values
	lLine = []
	lLine.append(dLine['Map']),
	lLine.append(dLine['State']),
	lLine.append(dLine['LAO Market']),
	lLine.append(dLine['County']),
	lLine.append(dLine['LAO Submarket']),
	lLine.append(dLine['City']),
	lLine.append(dLine['Acres']),
	lLine.append(dLine['Zoning']),
	lLine.append(dLine['FCL Doc Type']),
	lLine.append(dLine['FCL Rec Date']),
	lLine.append(dLine['FCL Stage']),
	lLine.append(dLine['Default Date']),
	lLine.append(dLine['Default Amount']),
	lLine.append(dLine['Owner Entity']),
	lLine.append(dLine['Owner Person']),
	lLine.append(dLine['Mail Street']),
	lLine.append(dLine['Mail City']),
	lLine.append(dLine['Mail Address']),
	lLine.append(dLine['Mail Zip']),
	lLine.append(dLine['Phone']),
	lLine.append(dLine['Mobile']),
	lLine.append(dLine['Email']),
	lLine.append(dLine['Lender']),
	lLine.append(dLine['Loan Amount']),
	lLine.append(dLine['Loan Date']),
	lLine.append(dLine['Loan Purpose']),
	lLine.append(dLine['Prop Type']),
	lLine.append(dLine['Prop Subtype']),
	lLine.append(dLine['Loan Maturity Date']),
	lLine.append(dLine['Last Sale Date']),
	lLine.append(dLine['Last Sale Amount']),
	lLine.append(dLine['APN']),
	lLine.append(dLine['Source']),
	lLine.append(dLine['Source ID']),
	lLine.append(dLine['Latitude']),
	lLine.append(dLine['Longitude'])

	return lLine

# Format Sheet - Debt List Deals
def format_tax_delinquent_sheet(wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,10),(noRows,10)).number_format='$#,##0' # Tax Delinquent $
	sht.range((4,12),(noRows,12)).number_format='$#,##0' # Purchase Amt
	sht.range((4,23),(noRows,23)).number_format='$#,##0' # 1st Amount
	sht.range((4,31),(noRows,31)).number_format='$#,##0' # Default Amt

	# Format Text columns
	sht.range((4,6),(noRows,6)).number_format='@' # APN

	# Format center text in cells
	sht.range((4,1),(noRows,1)).api.HorizontalAlignment = -4108 # Center
	sht.range((4,2),(noRows,2)).api.HorizontalAlignment = -4108 # Center

	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AE{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 9 # Set frist 2 columns to 9

	# Format Title
	formatTitle(sht, 'AE', 'C')

# Format Sheet - Debt List Deals
def format_foreclosure_sheet(wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,13),(noRows,13)).number_format='$#,##0' # Tax Delinquent $
	sht.range((4,24),(noRows,24)).number_format='$#,##0' # 1st Amount
	sht.range((4,31),(noRows,31)).number_format='$#,##0' # Default Amt

	# Format Text columns
	sht.range((4,32),(noRows,32)).number_format='@' # APN

	# Format column width
	sht.range('A:B').column_width = 8.0 # Set first 2 columns to 8
	sht.range('AG:AH').column_width = 13.0 # Set colums to 13

	# Format center text in cells
	sht.range((4,1),(noRows,1)).api.HorizontalAlignment = -4108 # Center
	sht.range((4,2),(noRows,2)).api.HorizontalAlignment = -4108 # Center

	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AJ{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	# sht.range('A:B').column_width = 9 # Set frist 2 columns to 9

	# Format Title
	formatTitle(sht, 'AJ', 'C')

# Format Sheet - Debt List Deals
def formatDebtListSheet(wb, sht, noRows, noCols):

	# Format Currency coloumns
	sht.range((4,11),(noRows,11)).number_format='$#,##0' # Sale Price
	sht.range((4,12),(noRows,12)).number_format='$#,##0' # Loan Amount
	sht.range((4,14),(noRows,14)).number_format='$#,##0' # $/Ac
	sht.range((4,16),(noRows,16)).number_format='$#,##0' # $/Lot
	sht.range((4,17),(noRows,17)).number_format='$#,##0' # $/FF
	
	# Format as Table
	formatSheetAsTable(wb, sht, noRows, noCols)

	sht.range('A3:AI{0}'.format(noRows)).row_height = 16 # Set all rows to 16
	sht.range('A:B').column_width = 2.7 # Set frist 2 columns to 2.7
	sht.range('F:I').column_width = 25 # Set PID Lot Type Classification Submarket
	sht.range('K:Q').column_width = 13 # Sale Price to $/FF
	sht.range('R:R').column_width = 40 # Beneficiary
	sht.range('S:S').column_width = 10 # Set MVP Top 100
	sht.range('T:T').column_width = 40 # Set Buyer Entity
	sht.range('U:U').column_width = 30 # Set Buyer Person
	sht.range('V:W').column_width = 15 # Set Phone & Mobile
	sht.range('X:X').column_width = 20 # Set Email
	sht.range('Y:Y').column_width = 10 # Set MVP Top 100
	sht.range('Z:Z').column_width = 40 # Set Seller Entity
	sht.range('AA:AA').column_width = 30 # Set Seller Person
	sht.range('AB:AC').column_width = 15 # Set Phone & Mobile
	sht.range('AD:AD').column_width = 20 # Set Email

	# sht.range('S:T').column_width = 20 # Set Submarket, BAA
	# sht.range('J:K').column_width = 35 # Set Subdivision & Location	
	# sht.range('AF:AF').column_width = 25 # Set Description
	
	# Remove TF Id columns from sheet
	# sht.range('AI:AM').api.Delete()

	# Format Title
	formatTitle(sht, 'AI', 'C')

def mailchimp_admin_list_formatter(lIn, header):
	from operator import itemgetter

	if header == 'Stats':
		lHeader = ['First Name', 'Last Name', 'Company', 'Email', 'Email App', 'Stars', 'Click Rate', 'Open Rate', 'Status']
	elif header == 'BouncedUnsub':
		lHeader = ['First Name', 'Last Name', 'Company', 'Email', 'Email App', 'Status', 'Date Removed', 'Unsub Reason']
	elif header == 'Campaigns':
		lHeader = ['Campaign', 'Date', 'Day', 'Time', 'Total Sent', 'Unsubscribed', 'Total Open', 'Open Rate', 'Total Clicks', 'Click Rate', 'Sub Clicks', 'Total Bounces', 'Bounce Rate']
	else:
		lHeader = header

	if header == 'Campaigns':
		lSorted = sorted(lIn, key=itemgetter(0))
		lout = lSorted
	else:
		lSorted = sorted(lIn, key=itemgetter(1))
		lHasName, lNoName = [], []
		for row in lSorted:
			if row[1] == '':
				lNoName.append(row)
			else:
				lHasName.append(row)

		lout = lHasName
		lout.extend(lNoName)
	num_rows = len(lout) + 1
	return lout, lHeader, num_rows

# Format MailChimpEblast Admin Report
def mailchimp_admin_report_formatter(wb, sht, cols, rows=0, group=False):
	from xlwings import constants

	column_letter = ''
	cols_temp = cols
	while cols_temp > 0:
		cols_temp, remainder = divmod(cols_temp - 1, 26)
		column_letter = chr(65 + remainder) + column_letter
	
	# Vertical format for Group Membership
	if group:
		sht.range('E3:{0}3'.format(column_letter)).api.Orientation = -90
		sht.range('E3:{0}3'.format(column_letter)).api.VerticalAlignment = constants.VAlign.xlVAlignTop
		sht.range('E4:{0}{1}'.format(column_letter, rows)).api.HorizontalAlignment = constants.HAlign.xlHAlignCenter
		# sht.range('E3:S3').api.ColumnWidth = 3

	sht.range('A1').api.Font.Bold = True
	sht.range('A3:{0}3'.format(column_letter)).api.Font.Bold = True

	sht.range('A3').select()
	rows = rows + 2
	tbl = sht.tables.add(sht.range((3,1), (rows, cols)), table_style_name='TableStyleMedium2')
	sht.range('A1').select()
	sht.autofit('c')
	active_window = wb.app.api.ActiveWindow
	active_window.FreezePanes = False
	active_window.SplitColumn = 0
	active_window.SplitRow = 3
	active_window.FreezePanes = True