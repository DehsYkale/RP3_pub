

# Import data from TF formated CSV (CSV_TF_Formater_v##.py) into TF


import acc
import bb
from bs4 import BeautifulSoup
import cpypg
from colored import Fore, Back, Style
from datetime import datetime
import dicts
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
from pprint import pprint
from time import sleep
from webbrowser import open as openbrowser
import webs

# Open Reonomy in browser and scrape Seller Buyer info
def openReonomy(dTF, dSlr, dByr, dPnt):
	driver = webs.selenium_LAO_Data_Sites_Login(dTF['Source_ID__c'])
	#lao.setActiveWindow('CSV to TF')

	sales_html = webs.getReonomyReportHTML(driver, 'Sales')
	soup = BeautifulSoup(sales_html, 'html.parser')
	divs = soup.find('div', {'class': 'ng-isolate-scope'})
	buyer = divs.find('span', {'once-text': 'sale.buyer1_buyer_name_borrower_name | lowercase'}).text
	seller = divs.find('span', {'once-text': 'sale.seller_name | lowercase'}).text

	# td.banner('CSV 2 TF - Reonomy Choose Buyer & Seller')
	print(' Sale Date: {0}  Sale Price: {1}\n'.format(dPnt['Sale_Date'], td.currency_format_from_number(dPnt['Sale_Price'])))
	print(' SPREADSHEET\n')
	print(' Seller-Owner{0:38}Buyer'.format(''))
	print('  {0:50}{1}'.format(dSlr['ENTITY'], dByr['ENTITY']))
	print('  {0:50}{1}'.format(dSlr['NAME'], dByr['NAME']))
	print('\nWEB PAGE\n')
	print(' 1) {0}\n'.format(seller.title())) # SELLER
	print(' 2) {0}\n'.format(buyer.title()))  # BUYER
	print(' 3) Neither\n')
	print('00) Skip')
	# click()
	while 1:
		ui = td.uInput('\n Which is the Seller? > ')

		# Spreadsheet Seller is the Seller
		if ui == '1':

			while 1:
				ui = td.uInput('\n Is {0} the...\n\n 1) Buyer\n 2) Same as Seller\n 3) Neither\n\n Select > '.format(dByr['ENTITY']))
				if ui == '1':
					break
				elif ui == '2' or ui == '3':
					dByr['ENTITY'], dPnt['Buyer_Entity'] = buyer.title(), buyer.title()
					dByr['NAME'], dPnt['Buyer_Person'] = 'None', 'None'
					dByr['STREET'] = 'None'
					dByr['CITY'] = 'None'
					dByr['STATE'] = 'None'
					dByr['ZIPCODE'] = 'None'
					dByr['COUNTRY'] = 'None'
					dByr['PHONE'] = 'None'
					dByr['Email'] = 'None'
					break
				else:
					print('\n Invalid entry...try again...')
			break
		# Spreadsheet Seller is the Buyer
		elif ui == '2':

			dSlr_Entiy, dPnt_SellerEntity = dByr['ENTITY'], dPnt['Buyer_Entity']
			dByr_Account, dPnt_SellerPersion = dByr['NAME'], dPnt['Buyer_Person']
			dSlr_Street, dSlr_City, dSlr_State, dSlr_Zip = dByr['STREET'], dByr['CITY'], dByr['STATE'], dByr['ZIPCODE']
			dSlr_County, dSlr_Phone, dSlr_Email = dByr['COUNTRY'], dByr['PHONE'], dByr['Email']
			# Buyer Dictionary
			dByr['ENTITY'], dPnt['Buyer_Entity'] = dSlr['ENTITY'], dPnt['Seller_Entity']
			dByr['NAME'], dPnt['Buyer_Person'] = dSlr['NAME'], dPnt['Seller_Person']
			dByr['STREET'], dByr['CITY'], dByr['STATE'], dByr['ZIPCODE'] = dSlr['STREET'], dSlr['CITY'], dSlr['STATE'], dSlr['ZIPCODE']
			dByr['COUNTRY'] = dSlr['COUNTRY']
			dByr['PHONE'] = dSlr['PHONE']
			dByr['Email'] = dSlr['EMAIL']


			ui = td.uInput('\n Is {0} the...\n\n 1) Seller\n 2) Same as Buyer\n 3) Neither\n\n Select > '.format(dSlr_Entiy))
			while 1:
				if ui == '1':
					# Seller Dictionary
					dSlr['ENTITY'], dPnt['Seller_Entity'] = dSlr_Entiy, dPnt_SellerEntity
					dSlr['NAME'], dPnt['Seller_Person'] = dByr_Account, dPnt_SellerPersion
					dSlr['STREET'] = dSlr_Street
					dSlr['CITY'] = dSlr_City
					dSlr['STATE'] = dSlr_State
					dSlr['ZIPCODE'] = dSlr_Zip
					dSlr['COUNTRY'] = dSlr_County
					dSlr['PHONE'] = dSlr_Phone
					dSlr['EMAIL'] = dSlr_Email
					break
				elif ui == '2' or ui == '3':
					dSlr['ENTITY'], dPnt['Seller_Entity'] = seller.title(), seller.title()
					dSlr['NAME'], dPnt['Seller_Person'] = 'None', 'None'
					dSlr['STREET'] = 'None'
					dSlr['CITY'] = 'None'
					dSlr['STATE'] = 'None'
					dSlr['ZIPCODE'] = 'None'
					dSlr['COUNTRY'] = 'None'
					dSlr['PHONE'] = 'None'
					dSlr['EMAIL'] = 'None'
					break
				else:
					print('\n Invalid entry...try again...')
			break

		elif ui == '3':
			dSlr['ENTITY'], dPnt['Seller_Entity'] = seller.title(), seller.title()
			dSlr['NAME'], dPnt['Seller_Person'] = 'None', 'None'
			dSlr['STREET'] = 'None'
			dSlr['CITY'] = 'None'
			dSlr['STATE'] = 'None'
			dSlr['ZIPCODE'] = 'None'
			dSlr['COUNTRY'] = 'None'
			dSlr['PHONE'] = 'None'
			dSlr['EMAIL'] = 'None'
			while 1:
				ui = td.uInput('\n Is {0} the Buyer? [0/1] > '.format(dByr['ENTITY']))
				if ui == '1':
					break
				elif ui == '0':
					dByr['ENTITY'], dPnt['Buyer_Entity'] = buyer.title(), buyer.title()
					dByr['NAME'], dPnt['Buyer_Person'] = 'None', 'None'
					dByr['STREET'] = 'None'
					dByr['CITY'] = 'None'
					dByr['STATE'] = 'None'
					dByr['ZIPCODE'] = 'None'
					dByr['COUNTRY'] = 'None'
					dByr['PHONE'] = 'None'
					dByr['Email'] = 'None'
					break
				else:
					print('\n Invalid input...try again...')
			break
		elif ui == '00':
			lao.lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			return 'Skip'
		else:
			print('\n Invalid input...try again...')

	divs = soup.find('div', {'class': 'col-xs-12 col-sm-6'})
	dds = divs.find_all('dd')
	dTF['Recorded_Instrument_Number__c'], dPnt['RDN'] = dds[3].text, dds[3].text


	openbrowser(dTF['Source_ID__c'])
	#lao.setActiveWindow('CSV to TF')

	return 'Dont Skip'

# Assign TF Field Values to a new Record
def assignTFfieldsFromSpreadsheet(dTF):
	
	# Deal Dict, Seller Dict, Buyer Dict, Offer Dict, Print Dict, Commission Dict
	dSlr = dicts.get_blank_account_dict()
	dByr = dicts.get_blank_account_dict()
	dBen = dicts.get_blank_account_dict()
	dOfr, dPnt, dComm = {}, {}, {}

	# Seller Dictionary
	dSlr['ENTITY'], dPnt['Seller_Entity'] = dTF['Seller Entity'], dTF['Seller Entity']
	dSlr['NAME'], dPnt['Seller_Person'] = dTF['Seller Person'], dTF['Seller Person']
	dSlr['STREET'] = dTF['Seller Street']
	dSlr['CITY'] = dTF['Seller City']
	dSlr['STATE'] = dTF['Seller State']
	dSlr['ZIPCODE'] = dTF['Seller Zip']
	dSlr['COUNTRY'] = dTF['Seller Country']
	dSlr['PHONE'] = dTF['Seller Phone']
	dSlr['EMAIL'] = dTF['Seller Email']

	# Buyer Dictionary
	dByr['ENTITY'], dPnt['Buyer_Entity'] = dTF['Buyer Entity'], dTF['Buyer Entity']
	dByr['NAME'], dPnt['Buyer_Person'] = dTF['Buyer Person'], dTF['Buyer Person']
	dByr['STREET'] = dTF['Buyer Street']
	dByr['CITY'] = dTF['Buyer City']
	dByr['STATE'] = dTF['Buyer State']
	dByr['ZIPCODE'] = dTF['Buyer Zip']
	dByr['COUNTRY'] = dTF['Buyer Country']
	dByr['PHONE'] = dTF['Buyer Phone']
	dByr['EMAIL'] = dTF['Buyer Email']

	# Beneficiary Dictionary
	dBen['ENTITY'], dPnt['Beneficiary__c'] = dTF['Lender'], dTF['Lender']

	# Assign TF Fields
	if dTF['Acres__c'] == 'None':
		dTF['Acres__c'], dPnt['Acres'] = 0, 0
	else:
		dTF['Acres__c'], dPnt['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])
	if dTF['City__c'] == 'None':
		dPnt['CITY'] = 'None'
	else:
		dPnt['CITY'] = dTF['City__c']
	dPnt['Classification'] = dTF['Classification__c']
	if dTF['Country__c'] == 'None':
		dTF['Country__c'] = 'United States'
	if dTF['County__c'] == 'None':
		td.warningMsg('\n No County listed in data! Terminating program...')
		exit()
	else:
		dTF['County__c'] = dTF['County__c'].replace(' ', '')  # Remove spaces from county name
		dPnt['County'] = dTF['County__c']
	if dTF['Latitude__c'] != 'None':
		dTF['Latitude__c'], dPnt['Latitude'] = (dTF['Latitude__c']).strip(), (dTF['Latitude__c']).strip()
	else:
		dPnt['Latitude'] = 'None'
	dTF['Lead_Parcel__c'], dPnt['Lead_Parcel'] = (dTF['Lead_Parcel__c']).strip(' '), (dTF['Lead_Parcel__c']).strip(' ')
	dPnt['Location'] = dTF['Location__c']
	if dTF['Longitude__c'] == 'None':
		dPnt['Longitude'] = 'None'
	else:
		dTF['Longitude__c'], dPnt['Longitude'] = (dTF['Longitude__c']).strip(), (dTF['Longitude__c']).strip()
	if dTF['Lots__c'] == 'None':
		dPnt['Lots'] = 'None'
	else:
		dTF['Lots__c'], dPnt['Lots'] = int(dTF['Lots__c']), int(dTF['Lots__c'])
	dPnt['Parcels'] = dTF['Parcels__c']
	dPnt['PID'] = 'New'
	if dTF['Recorded_Instrument_Number__c'] == 'None':
		dPnt['RDN'] = 'None'
	else:
		dPnt['RDN'] = dTF['Recorded_Instrument_Number__c']
	if dTF['Sale_Date__c'] != 'None': # and dTF['Sale_Price__c'] != 'None':
		sDate = td.date_engine(dTF['Sale_Date__c'])
		if datetime.now() > datetime.strptime(sDate, '%Y-%m-%d'):
			dTF['Sale_Date__c'], dPnt['Sale_Date'] = td.date_engine(dTF['Sale_Date__c']), td.date_engine(dTF['Sale_Date__c'])
			# row[39] = 'None'
		else:
			dPnt['Sale_Date'] = 'None'
	else:
		dPnt['Sale_Date'] = 'None'
	if dTF['Sale_Price__c'] == 'None':
		dTF['Sale_Price__c'], dPnt['Sale_Price'] = '10000', 'None'
	else:
		salePrice = (dTF['Sale_Price__c']).replace('$', '').replace(',', '')
		dTF['Sale_Price__c'], dPnt['Sale_Price'] = salePrice, salePrice
	if dTF['Source__c'] == 'None':
		dTF['Source__c'] = 'LAO'
	dPnt['Source_ID'] = dTF['Source_ID__c']
	if dTF['State__c'] == 'None':
		dTF['STATE'] = lao.get_state_of_market(dTF['Market__c'], dTF['County__c'])
	if len(dTF['State__c']) == 2:
		dTF['State__c'] = td.convert_state(dTF['State__c'])
	dPnt['Subdivision'] = dTF['Subdivision__c']
	dPnt['Zoning'] = dTF['Zoning__c']
	if dTF['List_Date__c'] == 'None':
		dPnt['List_Date'] = 'None'
	else:
		dTF['List_Date__c'] = td.date_engine(dTF['List_Date__c'])
		dPnt['List_Date'] = dTF['List_Date__c']
	if dTF['List_Price__c'] == 'None':
		dPnt['List_Price'] = 'None'
	else:
		dPnt['List_Price'] = dTF['List_Price__c']
		dTF['List_Price__c'] = (dTF['List_Price__c']).replace('$', '').replace(',', '')
		if int(dTF['List_Price__c']) == 0:
			dTF['List_Price__c'] = 10000
			dPnt['List_Price'] = '$10,000'
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

	dPnt['Status'] = dTF['MLS Status']

	# Offer Dictionary
	if dTF['Sale_Date__c'] != 'None' and dTF['Sale_Price__c'] != 'None' and dPnt['Status'] == 'Sold':
		dOfr['type'] = 'lda_Offer__c'
		dOfr['Offer_Price__c'] = dTF['Sale_Price__c']
		dOfr['Offer_Date__c'] = dTF['Sale_Date__c']
		dOfr['Offer_Status__c'] = 'Accepted'
		dOfr['Date_Accepted__c'] = dTF['Sale_Date__c']
	# Listing and Selling Agents
	dPnt['ListEntity'] = dTF['List Entity']
	dPnt['ListAgent'] = dTF['List Agent']
	dPnt['SellAgent'] = dTF['Buyer Agent']
	# Commission Listing Agent Dict
	dComm['Agent'] = dTF['List Agent']
	dComm['AgentPhone'] = dTF['List Agent Phone']
	dComm['AgentEmail'] = dTF['List Agent Email']
	# Mortgage/Deed of Trust Info
	if dTF['Lender'] != 'None' and dTF['Loan_Amount__c'] != 'None':
		dTF['Beneficiary__c'], dPnt['Beneficiary__c'] = dTF['Lender'], dTF['Lender']
		dTF['Loan_Amount__c'] = dTF['Loan_Amount__c'].replace('$', '').replace(',', '')
		if dTF['Loan_Date__c'] != 'None':
			dTF['Loan_Date__c'] = td.date_engine(dTF['Loan_Date__c'])
	else:
		del dTF['Loan_Amount__c']
		del dTF['Loan_Date__c']

	return dTF, dSlr, dByr, dBen, dOfr, dPnt, dComm

# Assign TF Field Values to an existing Lead
def assignTFfieldsFromLeadDeal(dTF, dLead):

	# Check if Acres is different from TF record
	if float(dLead['Acres__c']) >= 0 and dTF['Acres__c'] == 'None':
		skipping = 0
	elif float(dLead['Acres__c']) != float(dTF['Acres__c']):
		printinfo(dPnt, 'acres')
		print(' Choose Acres value:\n\n  1) {0:15}{1}\n  2) {2:15}{3}\n  Or Type in Acres\n\n 00) Quit'.format('TerraForce', dLead['Acres__c'], dTF['Source__c'], dTF['Acres__c']))
		ui = td.uInput('\n Select or Type > ')
		if ui == '2':
			dTF['Acres__c'], dPnt['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])
		elif ui == '1' or ui == '':
			dTF['Acres__c'], dPnt['Acres'] = float(dLead['Acres__c']), float(dLead['Acres__c'])
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			dTF['Acres__c'], dPnt['Acres'] = float(ui), float(ui)
	else:
		dTF['Acres__c'], dPnt['Acres'] = float(dTF['Acres__c']), float(dTF['Acres__c'])

	# Use existing owner
	dSlr = {}
	printinfo(dPnt, 'seller')
	print(' Existing Owner\n')
	
	if dLead['Owner_Entity__r'] != 'None':
		print(' Entity: {0}\n'.format(dLead['Owner_Entity__r']['Name']))
	else:
		print(' Entity: None')
	if dLead['AccountId__r'] != 'None':
		print(' Person: {0}\n'.format(dLead['AccountId__r']['Name']))
	else:
		print(' Person: None')
	# click()
	while 1:
		ui = td.uInput('\n Use existing Owner? [0/1] > ')
		if ui == '0':
			useExistingOwner = False
			break
		elif ui == '1':
			useExistingOwner = True
			print('\n Using existing Owner...\n')
			break
		else:
			print('Invalid input...try again...')

	# Seller Dictionary
	if useExistingOwner is False:
		dSlr = dicts.get_blank_account_dict()
		dLead['Name'] = 'NeedDealName'


	# if dLead['City__c'] == 'None' and dTF['City__c'] != 'None':
	# 	dTF['City__c'] = row[20]
	if dLead['City__c'] != dTF['City__c']:
		dTF['City__c'], dPnt['CITY'] = dTF['City__c'], dTF['City__c']
	else:
		dPnt['CITY'] = 'None'

	dTF['Classification__c'], dPnt['Classification'] = dLead['Classification__c'], dLead['Classification__c']

	dPnt['County'] = dTF['County__c']
	if dLead['Description__c'] != 'None' and dTF['Description__c'] != 'None':
		dTF['Description__c'] = '{0}\n{1}'.format(dLead['Description__c'], dTF['Description__c'])

	dTF['Location__c'] = dLead['Location__c']

	dTF['Longitude__c'] = dLead['Longitude__c']
	dTF['Latitude__c'] = dLead['Latitude__c']

	if dLead['Lot_Description__c'] != 'None' and dTF['Lot_Description__c'] != 'None':
		dTF['Lot_Description__c'] = '{0}\n{1}'.format(dLead['Lot_Description__c'], dTF['Lot_Description__c'])

	if dLead['Lots__c'] == 0 and dTF['Lots__c'] != 'None':
		dPnt['Lots'] = dTF['Lots__c']

	if dTF['Recorded_Instrument_Number__c'] != 'None':
		dPnt['RDN'] = dTF['Recorded_Instrument_Number__c']
	else:
		dTF['Recorded_Instrument_Number__c'], dPnt['RDN'] = '', 'None'

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
		dPnt['Source_ID'] = dTF['Source_ID__c']
	else:
		dPnt['Source_ID'] = 'None'

	if dLead['Subdivision__c'] != 'None':
		dTF['Subdivision__c'] = dLead['Subdivision__c']

	if dLead['Zipcode__c'] != 'None':
		dTF['Zipcode__c'] = dLead['Zipcode__c']

	dPnt['Zoning'] = dTF['Zoning__c']

	# Add List Date
	if dTF['List_Date__c'] != 'None':
		dTF['List_Date__c'] = td.date_engine(dTF['List_Date__c'])
		dPnt['List_Date'] = dTF['List_Date__c']
	else:
		dPnt['List_Date'] = 'None'

	# Add List Price
	if dTF['List_Price__c'] != 'None':
		dTF['List_Price__c'], dPnt['List_Price'] = (dTF['List_Price__c']).replace('$', '').replace(',', ''), dTF['List_Price__c']
		if int(dTF['List_Price__c']) == 0:
			dTF['List_Price__c'] = 10000
			dPnt['List_Price'] = '$10,000'
	else:
		dPnt['List_Price'] = 'None'

	dPnt['Status'] = dTF['MLS Status']

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

	return dTF, dSlr

# Set the value of Buyer Acting As field
def buyerActingAs(dTF):
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
def printinfo(dPnt, hiLight='None'):
	# print('{0}{1}{2}'.format(Fore.yellow_2, text, Style.reset))
	recordsleft = totalRecords - currentRecord

	td.banner('TF AWS CSV Entry PY3 v02 Row: {0} : {1} : {2}'.format(totalRecords, currentRecord, recordsleft))

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
	print(' Lead Par: {0:30}'.format(dPnt['Lead_Parcel']))
	print(' Parcles:  {0}'.format(dPnt['Parcels']))
	print
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
	print('{0} Class:    {1}{2}'.format(menuColor, dPnt['Classification'], Style.reset))
	menuColor = ''
	print
	print(' Date:     {0}'.format(dPnt['Sale_Date']))
	print(' Price:    {0}'.format(td.currency_format_from_number(dPnt['Sale_Price'])))
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
	print(' Location: {0}'.format(dPnt['Location']))
	print(' Sub Name: {0}'.format(dPnt['Subdivision']))
	print('_________________________________________________________________________\n')

# Select the record of the Source ID
def selectLeadRecordByPID(pid):
	while 1:
		pidLoop = False
		wc = "PID__c = '{}'".format(pid)
		# results = bb.querySF(service, fields, wc)
		results = bb.tf_query_3(service, 'Deal', wc)
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

	# if open_lead_in_browser:
	# 	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(results[0]['Id']))

	return results[0]

# If no Sale Price or if the Source ID already exists then skip record
def skipRecord(dTF, dPnt):
	# Check if there is a sale price otherwise skip record
	if dPnt['Sale_Price'] == 'None' and dTF['State__c'] != 'Idaho' and dTF['State__c'] != 'Texas':
		td.warningMsg('\n No Sale Price, writing to skip file...Continue')
		if dTF['Source_ID__c'] != 'None':
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
		sleep(1)
		return 'Skip'
	print(' Condition Nominal Sale Price Exists...')

	# Check if there is a sale date otherwise skip record
	if dPnt['Sale_Date'] == 'None' and dTF['State__c'] != 'Idaho':
		td.warningMsg('\n No Sale Date, writing to skip file...Continue...')
		if dTF['Source_ID__c'] != 'None':
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
		sleep(1)
		return 'Skip'
	print(' Condition Nominal Sale Date Exists...')

	# Check if record Source ID exists in Skip file
	if dTF['Source_ID__c'] != 'None':
		if lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'CHECK'):
			# No need to print warning
			# print('\n Source ID found in Skip file...moving on...'
			print('Record found in Skip File: {0}'.format(dTF['Source_ID__c']))
			return 'Skip'
	print(' Condition Nominal Source ID not in Skip file...')

	# Check if record already entered by searching TF Source ID
	# print('here3'
	if dTF['Source_ID__c'] != 'None':
		fields = 'Id'
		wc = "Source_ID__c LIKE '%{0}%' AND County__c = '{1}'".format(dTF['Source_ID__c'], dTF['County__c'])
		# results = bb.querySF(service, fields, wc)
		results = bb.tf_query_3(service, 'Deal', wc, fields=fields)
		if results != []:
			td.warningMsg('\n Source ID found in TF Record file...writing to skip file & moving on...')
			# Enter record in dont_select_me_again.txt
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			sleep(1)
			print(' Record found in TF by Source ID: {0}'.format(dTF['Source_ID__c']))
			return 'Skip'
	print(' Condition Nominal Source ID not in TerraForce record...')

	# Check if record already entered by Source ID
	if dTF['Recorded_Instrument_Number__c'] != 'None':
		fields = 'Id'
		wc = "Recorded_Instrument_Number__c = '{}'".format(dTF['Recorded_Instrument_Number__c'])
		# results = bb.querySF(service, fields, wc)
		results = bb.tf_query_3(service, 'Deal', wc, fields=fields)
		if results != []:
			td.warningMsg('\n Recorded Instrument Number found in TF Record file...writing to skip file & moving on...')
			# Enter record in dont_select_me_again.txt
			lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
			sleep(1)
			print(' Record found in TF by Record Instrument Nubmer: {0}'.format(dTF['Recorded_Instrument_Number__c']))
			return 'Skip'
	print(' Condition Nominal Recorded Instrument Number not in TerraForce record...')
	return {}

# Check if a PID already exists for this Lead Parcel
#   and make the Zoom To Polygon JSON file
def check_for_existing_pid(dTF, dPnt):

	# Check for existing Ownership
	# TerraForce Query
	fields = 'Id, PID__c'
	wc = "Lead_Parcel__c LIKE '%{0}%' AND County__c = '{1}' AND (NOT (StageName__c LIKE 'Closed%'))".format(dTF['Lead_Parcel__c'], dTF['County__c'])
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	
	if results != []:
		dTF['PID__c'] = results[0]['PID__c']
		dTF['Id'] = results[0]['Id']
		dPnt['PID'] = results[0]['PID__c']
		# Create ArcMap Find Me file
		fjson.create_ZoomToPolygon_json_file(fieldname='pid', polyId=dPnt['PID'], polyinlayer='OwnerIndex', lon=None, lat=None)
		# Open TerraForce Deal in browser
		webs.open_pid_did(service, dTF['Id'])
	else:
		# Create M1/ArcMap Zoom To Polygon JSON file
		# Get Market Abbreviation and State Abbreviation
		marketAbb, stateAbb = lao.get_market_abbreviation(dTF['Market__c'], dTF['County__c'])
		# Build poygon layer name
		polyinlayer = '{0}Parcels{1}'.format(stateAbb, dTF['County__c'])
		# Create the json file
		fjson.create_ZoomToPolygon_json_file(fieldname='apn', polyId=dTF['Lead_Parcel__c'], polyinlayer=polyinlayer, lon=dTF['Longitude__c'], lat=dTF['Latitude__c'], market=dTF['Market__c'])
	
	return dTF, dPnt

# Open the Source ID in a browser
def open_source_comp_in_browser(dTF, isREDNewsLoggedIn):
	# RED NEWS
	if dTF['Source__c'] == 'RED News':
		# Check if logged into Red News
		if isREDNewsLoggedIn is False:
			td.banner('TF AWS CSV Entry PY3 v02')
			openbrowser('https://realestatedaily-news.com/wp-login.php')
			td.warningMsg('\n Login to RED News website...\n\n Username: Craig K.\n Password: ftGV#sEthp9#dP0v')
			td.uInput('\n Continue... > ')
			isREDNewsLoggedIn = True
		# Open the RED News Comp
		openbrowser('https://realestatedaily-news.com/displaycomp/?ID={0}&NoComment='.format(dTF['Source_ID__c']))
		return True
	# Idaho MLS
	elif dTF['Source__c'] == 'MLS':
		openbrowser(dTF['Source_ID__c'])
	# REONOMY
	elif dTF['Source__c'] == 'Reonomy':
		openbrowser(dTF['Source_ID__c'])
	# Print the deal info
	printinfo(dPnt, 'start')
	sleep(1)

# Add a Note to the TF Record
def addNote(DID, title, body):
	noted = {}
	noted['type'] = 'Note'
	noted['ParentId'] = DID
	noted['Title'] = title
	noted['Body'] = body
	# results = bb.sfcreate(service, noted)
	results = bb.tf_create_3(service, noted)
	if results[0]['success']:
		print('Note added successfully.\n')
	else:
		print('Note was not added...')
		print(results)
		exit('Terminating program...')

# Check that Lead Parcel Exists and Add if Not
def leadParcelCheck(dTF):
	# Ensure Lead_Parcel__c exists in the dictionary
	if 'Lead_Parcel__c' not in dTF:
		dTF['Lead_Parcel__c'] = 'None'
	
	# Check if Lead_Parcel__c is None, empty, or the string 'None'
	if dTF['Lead_Parcel__c'] == 'None' or dTF['Lead_Parcel__c'] == '' or dTF['Lead_Parcel__c'] is None:
		# If Parcels__c exists, use the first parcel from it
		if 'Parcels__c' in dTF and dTF['Parcels__c'] != 'None':
			parSplit = dTF['Parcels__c'].split(', ')
			dTF['Lead_Parcel__c'] = parSplit[0].strip()
		else:
			dTF['Lead_Parcel__c'] = 'None'
	else:
		# If Lead_Parcel__c has a value, split it and take the first part
		# This handles cases where multiple parcels might be in the field
		parcel_parts = str(dTF['Lead_Parcel__c']).split()
		dTF['Lead_Parcel__c'] = parcel_parts[0].strip()
	
	return dTF

# Remove unnecessary and 'None' keys from dTF
def clean_dTF(dTF):
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
	keys_to_delete = [key for key, value in dTF.items() if value == 'None']
	for key in keys_to_delete:
		del dTF[key]

	return dTF, notes

##############################################################################
# START OF THE PROGRAM
##############################################################################

td.banner('TF AWS CSV Entry PY3 v02')
td.console_title('CSV to TF PY3')

# Login to TerraForce
service = fun_login.TerraForce()
# Set Red News logged in variable
isREDNewsLoggedIn = True

# Open CSV GUI to input into TF
extension = [('formated csv files', '_FORMATTED.csv'), ('all files', '.*')]
comps_listing_filename = lao.guiFileOpen(lao.getPath('comps'), "Open Comps or Listing CSV", extension)

# Create inFile dictionary
dFin = dicts.spreadsheet_to_dict(comps_listing_filename)

# Set entry progress variables
totalRecords = len(dFin)
currentRecord = 0

# Set source variable
data_source = dFin[1]['Source__c']


for line in dFin:

	dTF = dFin[line]

	# Skip records with no County
	if dTF['County__c'] == 'None' or dTF['County__c'] == '':
		continue

	# Count number of rows
	currentRecord += 1

	# Skip records w/o data
	if dTF['Acres__c'].upper() == 'SKIP':
		continue

	# Make TF Deal Dict, Seller Dict, Buyer Dict, Benificary Dict, Offer Dict, Printinfo Dict, Commission Dict
	dTF, dSlr, dByr, dBen, dOfr, dPnt, dComm = assignTFfieldsFromSpreadsheet(dTF)

	# Skip if Sale Price = 'None' or if Source ID exits in Skip file or TF
	dLead = skipRecord(dTF, dPnt)
	if dLead == 'Skip':
		dLead = {}
		continue

	td.banner('TF AWS CSV Entry PY3 v02')

	# Check if a PID already exists for this Lead Parcel
	#   and make the Zoom To Polygon JSON file
	dTF, dPnt = check_for_existing_pid(dTF, dPnt)

	if dLead == {}:
		
		# Open the Source Comp in browser
		isREDNewsLoggedIn = open_source_comp_in_browser(dTF, isREDNewsLoggedIn)

		# User to choose what to do with the record
		while 1:
			print('\n Zoom to Polygon file created for M1/ArcMap...\n')
			print(' DEAL ENTRY OPTIONS:\n')
			print('  [Type in an existing PID]')
			print('  [1] Create a new PID')
			print('  [2] Process Deal Later (go to next record)')
			print('  [3] Skip Deal for All Enternity')
			# If existing PID is not found then ask user if they want to use it
			if dPnt['PID'] != 'None' and dPnt['PID'] != 'New':
				td.colorText(' [4] Use Existing PID: {0}'.format(dPnt['PID']), 'GREEN')
			print(' [00] Quit')
			ui = td.uInput('\n Select > ').upper()
			ui = ui.strip()
			if ui == '1':
				print('Processing new Deal...')
				break
			elif ui == '2':
				print('In progress will reasearch later...')
				dLead = 'Skip'
				break
			elif ui == '3':
				dLead = 'Skip For All Enternity'
				break			
			# User input an existing PID
			elif len(ui) > 2 or ui == '4':
				if ui == '4':
					if dPnt['PID'] == 'None' or dPnt['PID'] == 'New':
						print('\n No existing PID found...try again...')
						sleep(1)
						continue
					# Use existing PID
					ui = dPnt['PID']
				else:
					dPnt['PID'] = ui.strip()
					pid_did = webs.open_pid_did(service, dPnt['PID'])
					if pid_did is False:
						print('\n Could not find PID {0}...try again...'.format(dPnt['PID']))
						sleep(1)
						continue
				# Check if LAO Deal or non-existing PID number
				# if bb.isLAODeal(service, ui) == 'Try Again':
				# 	continue
				# Write existing PID info to dLead dictionary
				dLead = selectLeadRecordByPID(dPnt['PID'])

				# Check for Type as LAO Exclusive
				if dLead['Type__c'] == 'Exclusive LAO':
					td.warningMsg('\n ***WARNING***\n\n Deal Type is Exclusive LAO!')
					td.instrMsg(f'\n If {dLead["PID__c"]} is no longer an LAO Deal then change the Type to "-None-" in TerraForce.\n If you are not sure then do not change the Type.\n')
					print('  [1] Continue entering Deal')
					print('  [2] Process Deal Later (go to next record)')
					print('  [3] Skip Deal for All Enternity')
					print(' [00] Quit program')
					ui = td.uInput('\n Select > ')
					if ui == '00':
						exit(' Terminating program...')
					elif ui == '1':
						print('Continuing to enter Deal...')
					elif ui == '2':
						print('Skipping Deal...')
						dLead = 'Skip'
						break
					if ui == '3':
						dLead = 'Skip For All Enternity'
						break

				# Check for if Deal is a Lead
				if dLead['StageName__c'] != 'Lead':
					td.warningMsg('\n ***WARNING***\n\n Deal Stage Name is {0}!'.format(dLead['StageName__c']))
					td.instrMsg(f'\n Check with the Advisor or Escrow if {dLead['PID__c']} is still a LAO Deal.\n\n Escrow will need to change the Stage Name to "Lead" if it is no longer a LAO Deal.\n')
					print('  [1] Process Deal Later (go to next record)')
					print('  [2] Skip Deal for All Enternity')
					print('  [00] Quit program')
					ui = td.uInput('\n Select > ')
					if ui == '00':
						exit(' Terminating program...')
					elif ui == '1':
						print('Skipping Deal...')
						dLead = 'Skip'
						break
					elif ui == '2':
						dLead = 'Skip For All Enternity'
					break
				
				# Check if PID is to be split and split if true
				ui_split = td.uInput('\n Split this PID? [0/1/00] > ')
				if ui_split == '1':
					dLead['PID__c'], dLead['Id'] = bb.splitDeal(service, ui)
					dPnt['PID'] = dLead['PID__c']
				elif ui_split == '00':
					exit(' Terminating program...')

				break

			elif ui == '00':
				exit(' Terminating program...')
			else:
				print('\nInvalid input...try again...')

	# If user selected to skip record then continue to next record
	if dLead == 'Skip':
		dLead = {}
		continue
	elif dLead == 'Skip For All Enternity':
		print('\n\n Skipping record for all enternity...')
		lao.SkipFile(dTF['Source_ID__c'], dTF['County__c'], 'WRITE')
		sleep(1)
		dLead = {}
		continue

	# Check if deal is closed and if so only update relevant fields
	closedDeal = False
	if dLead != {}:
		# Create ArcMap Find Me file
		fjson.create_ZoomToPolygon_json_file(fieldname='pid', polyId=dPnt['PID'], polyinlayer='OwnerIndex', lon=None, lat=None)

		printinfo(dPnt, 'sellerbuyer')

		dTF, dSlr = assignTFfieldsFromLeadDeal(dTF, dLead)

		if 'Closed' in dLead['StageName__c']:
			closedDeal = True

	# Enter Seller
	if dSlr!= {} and closedDeal is False:
		printinfo(dPnt, 'seller')
		print('----> Seller: {0}'.format(dSlr['ENTITY']))

		# If no Seller Entity and no Account Person then ask user to enter Person
		if dSlr['ENTITY'] == 'None' and dSlr['NAME'] == 'None':
			td.warningMsg('\n**** No Seller Entity or Person Listed ****')
			ui = td.uInput('\n\n Type in Seller Entity or Person or [Enter] for None > ')
			if len(ui) > 0:
				dSlr['ENTITY'] = ui
			else:
				dSlr['ENTITY'] = 'Unknown Seller'


		# Find or Create Seller Entity
		if dSlr['ENTITY'] != 'None':
			dSlr = acc.find_create_account_entity(service, dSlr)

		# User to choose if they want to enter a Person for the Entity
		if dSlr['ENTITY'] != 'None' and dSlr['NAME'] == 'None':
			print(f'\n Would you like to enter a Person for {dSlr['ENTITY']}?')
			print('\n  1) Yes')
			print('  2) No')
			print(' 00) Quit')
			ui = td.uInput('\n Select > ')
			if ui == '1' or ui == '':
				ui = td.uInput('\n Enter a Person or [Enter] for None > ')
				if ui == '':
					dSlr['NAME'] = 'None'
				else:
					dSlr['NAME'] = ui
			elif ui == '2':
				dSlr['NAME'] = 'None'
			elif ui == '00':
				exit(' Terminating program...')
		
		# Find or Create Seller Person
		Name, AID, dSlr = acc.find_create_account_person(service, dSlr)

		# # Give user the option to make final changes to the contact
		# dSlr = cpypg.info_print_final_confirm(dSlr)

	# Create Deal Name
	if dLead == {} or dLead['Name'] == 'NeedDealName':	# No need to create Deal name for existing Deal
		
		# Set ownerName as Entity or Person or UNKNOWN
		if dSlr['EID'] != 'None':
			ownerName = dSlr['ENTITY']
		elif dSlr['AID'] != 'None':
			ownerName = dSlr['NAME']
		else:
			ownerName = 'UNKNOWN'

		# Shorten Owner Name if longer than 50 characters (max Name length is 80)
		# if dSlr['EID'] != 'None' and len(dSlr['NAME']) > 50:
		if len(ownerName) > 50:
			# STX = dSlr['NAME']
			lownerName = ownerName.split(' ')
			name = ''
			for i in range(1, len(lownerName)):
				if len(name) < 50:
					name = '{0} {1}'.format(name, lownerName[i])
					print(name)
				else:
					break
			ownerName = name
		
		if int(dTF['Acres__c']) < 100:
			if 'UNKNOWN' in ownerName.upper():
				dTF['Name'] = '{0} {1} {2:.1f} Ac'.format(dPnt['Lead_Parcel'], dPnt['County'], float(dTF['Acres__c']))
			else:
				dTF['Name'] = '{0} {1:.1f} Ac'.format(ownerName, float(dTF['Acres__c']))
		else:
			if 'UNKNOWN' in ownerName.upper():
				dTF['Name'] = '{0} {1} {2:.0f} Ac'.format(dPnt['Lead_Parcel'], dPnt['County'], int(dTF['Acres__c']))
			else:
				dTF['Name'] = '{0} {1:.0f} Ac'.format(ownerName, int(dTF['Acres__c']))


	# Enter Buyer
	if closedDeal is False and dPnt['Status'] == 'Sold':
		printinfo(dPnt, 'buyer')
		print(f'\n ----> Buyer: {dByr['ENTITY']}')

		# If no Buyer Entity ask user if they want to enter one
		if dByr['ENTITY'] == 'None':
			td.warningMsg('\n**** No Buyer Entity Listed ****')
			ui = td.uInput('\n\n Type in Buyer Entity or [Enter] for None > ')
			if len(ui) > 0:
				dByr['ENTITY'] = ui

		BTX = 'None'
		# Check TerraForce for 
		if dByr['ENTITY'] != 'None':
			dByr = acc.find_create_account_entity(service, dByr)
			
			# if BTXID == 'None':
			if dByr['EID'] == 'None':
				# BPR = BTX
				# BTX = 'None'
				# BPRID = 'None'
				dByr['NAME'] = dByr['ENTITY']
				dByr['ENTITY'] = 'None'
			# Check for Employees or Child Accounts of Business
			elif dPnt['Status'] == 'Sold':
				# dOfr['Buyer_Entity__c'] = BTXID
				dOfr['Buyer_Entity__c'] = dByr['EID']
				# BPR, BPRID, RTYID = bb.findPersonsOfEntity(service, BTXID)
				dByr['NAME'], dByr['AID'] = acc.find_persons_of_entity(service, dByr['EID'])
			else:
				# BPRID == 'None'
				dByr['AID'] = 'None'
		else:
			# BPRID = 'None'
			dByr['AID'] = 'None'

		# If no Buyer Entity and no Account Person then ask user to enter Person
		noBuyer = False
		# if BPRID == 'None' and dByr['ENTITY'] == 'None' and dPnt['Status'] == 'Sold':
		if dByr['AID'] == 'None' and dByr['ENTITY'] == 'None' and dPnt['Status'] == 'Sold':
			ui = td.uInput('\n **** No Buyer Person Listed ****\n\n Type in Buyer Person or [Enter] for None > ')
			if len(ui) > 0:
				# dByr['Buyer_Person'] = ui
				dByr['NAME'] = ui
			else:
				noBuyer = True
		# If no Employee or Child Account of Business then create a Person Account
		if noBuyer is False:
			# if BPRID == 'None':
			if dByr['AID'] == 'None':
				if dPnt['Buyer_Person'] != 'None':
					# BPR = dPnt['Buyer_Person']
					dByr['NAME'] = dPnt['Buyer_Person']
				# dFindCreatePerson = acc.buildAccountDictionary(dByr)
				# BPR, BPRID, RTY = acc.findCreateAccountPerson(service, dFindCreatePerson)
				dByr['NAME'], dByr['AID'], dByr = acc.find_create_account_person(service, dByr)
				# if BPRID != 'None' and dPnt['Status'] == 'Sold':
				if dByr['AID'] != 'None' and dPnt['Status'] == 'Sold':
					# dOfr['Buyer__c'] = BPRID
					dOfr['Buyer__c'] = dByr['AID']
			elif dPnt['Status'] == 'Sold':
				# dOfr['Buyer__c'] = BPRID
				dOfr['Buyer__c'] = dByr['AID']

	
	# Enter Beneficiary
	if closedDeal is False and dPnt['Status'] == 'Sold' and 'Beneficiary__c' in dTF:
		printinfo(dPnt, 'beneficiary')
		print('----> Beneficiary: {0}'.format(dTF['Beneficiary__c']))
		# BENEX, BENEXID, RTYID, business_dict = bb.findCreateAccountEntity(service, dTF['Beneficiary__c'])
		dBen = acc.find_create_account_entity(service, dBen)
		# if BENEXID == 'None':
		if dBen['EID'] == 'None':
			# BENEX, BENEXID, RTYID = bb.findCreateAccountPerson(service, dTF['Beneficiary__c'])
			dBen['NAME'], dBen['AID'] = acc.find_persons_of_entity(service, dBen['EID'])
		# if BENEXID == 'None':
		if dBen['EID'] == 'None' and dBen['AID'] == 'None':
			del dTF['Beneficiary__c']
			del dTF['Loan_Amount__c']
			if 'Loan_Date__c' in dTF:
				del dTF['Loan_Date__c']
		elif dBen['EID'] != 'None':
			dTF['Beneficiary__c'] = dBen['EID']
		elif dBen['AID'] != 'None':
			dTF['Beneficiary__c'] = dBen['AID']

	# Enter Listing Agent
	listagentd = {}
	if dTF['List Agent'] != 'None':
		printinfo(dPnt, 'listingagent')
		print('----> Listing Agent')
		AGENT, AGENTID, RTYID = bb.findCreateAccountPerson(service, dTF['List Agent'], PHONE=dTF['List Agent Phone'], EMAIL=dTF['List Agent Email'])
		listagentd['type'] = 'lda_Commission__c'
		listagentd['Agent__c'] = AGENTID
		listagentd['Agent_Order__c'] = 0

	# Check that Acres has a value
	if 'Acres__c' in dTF:
		if dTF['Acres__c'] == 'None':
			printinfo(dPnt, 'acres')
			dTF['Acres__c'] = float(td.uInput('\n Enter Acres > '))
		if dTF['Acres__c'] == 0:
			printinfo(dPnt, 'acres')
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

	# Enter Classification, Lot Type, Buyer Acting As
	while 1:
		printinfo(dPnt, 'classification')
		if dLead == {}:
			dTF, startover = lao.select_from_list(dTF, 'Classification__c')
		elif dLead['Classification__c'] == []:
			dTF, startover = lao.select_from_list(dTF, 'Classification__c')
		else:
			# dTF['Classification__c'] = chooseClassification(dLead['Classification__c'])
			dTF, startover = lao.select_from_list(dTF, 'Classification__c')
		if startover:
			continue

		# User to enter Lot Type (TTY) and Classification(s) (CLASS)
		dTF, startover = lao.select_from_list(dTF, 'Lot_Type__c')
		if startover:
			continue

		if dPnt['Sale_Date'] != 'None':
			dTF, startover = lao.select_from_list(dTF, 'Buyer_Acting_As__c')
		if startover:
			continue

		break

	# Make sure Lead Parcel is populated
	dTF = leadParcelCheck(dTF)

	# Add Researcher OwnerId to record
	dTF['OwnerId'] = bb.createdByResearch(service)

	# Check if non-disclosure state and move Sale Price to Description if Yes
	if dOfr != {}:
		if lao.getCounties('IsDisclosure', '', dTF['County__c']) == 'No' and dTF['Source__c'] == 'Reonomy' and dTF['Sale_Price__c'] != 10000:
			salePriceFormatted = td.currency_format_from_number(dTF['Sale_Price__c'])
			pricePerAcre = float(float(dTF['Sale_Price__c']) / float(dTF['Acres__c']))
			pricePerAcre = td.currency_format_from_number(pricePerAcre)
			if 'Description__c' in dTF:
				dTF['Description__c'] = 'Reonomy Estimated Sale Price: {0}  {1} per acre\n{2}'.format(salePriceFormatted, pricePerAcre, dTF['Description__c'])
			else:
				dTF['Description__c'] = 'Reonomy Estimated Sale Price: {0}  {1} per acre\n'.format(salePriceFormatted, pricePerAcre)
			dTF['Sale_Price__c'] = 10000
			dOfr['Offer_Price__c'] = 10000

	printinfo(dPnt)

	# Remove unnecessary and 'None' keys from dTF
	dTF, notes = clean_dTF(dTF)

	# Create Records
	# CREATE NEW RECORD since dLead (Lead Dict) is empty ###########################################
	if dLead == {}: 
		DID = bb.tf_create_3(service, dTF)
		if DID == 'Create Failed':
			td.warningMsg(' Deal was not created...')
			exit(' Terminating program...')
		else:
			print('\n Deal created successfully...\n')
	# Update existing Lead
	else: 
		DID = bb.tf_update_3(service, dTF)
		if DID == 'Update Failed':
			td.warningMsg(' Deal was not updated...\n')
			exit('\n Terminating program...')
		else:
			print('\n Deal updated successfully.\n')

	# CREATE OFFER if dOfr is populated otherwise leave the record as Lead ########################
	if dOfr != {} and closedDeal is False:
		dOfr['DealID__c'] = DID
		Offer_ID = bb.tf_create_3(service, dOfr)
		if Offer_ID == 'Create Failed':
			td.warningMsg(' Offer was not created...')
			exit(' Terminating program...')
		else:
			print('\n Offer created successfully...\n')

		# Close the Deal after offer is made
		close_dict = {'type': 'lda_Opportunity__c', 'id': DID, 'StageName__c': 'Closed Lost'}
		# results = bb.sfupdate(service, close_dict)
		DID = bb.tf_update_3(service, close_dict)
		if DID == 'Update Failed':
			td.warningMsg(' Deal was not closed...\n')
			exit('\n Terminating program...')
		else:
			print('\n Deal closed successfully.\n')

	# CREATE COMMISSIONS if they exist #########################################################
	if listagentd != {}:
		listagentd['DealID__c'] = DID
		Commission_ID = bb.tf_create_3(service, listagentd)
		if Commission_ID == 'Create Failed':
			td.warningMsg(' Commission was not created...')
			exit(' Terminating program...')
		else:
			print('\n Deal Commission successfully...\n')
		# results = bb.tf_create_3(service, listagentd)
		# if results[0]['success']:
		# 	print('\n Deal closed successfully.\n')
		# else:
		# 	td.warningMsg('Listing Agent was not closed...')
		# 	print(results)
		# 	exit(' Terminating program...')

	# Create Notes if they exist
	if notes != 'None':
		addNote(DID, 'Transaction Remarks', notes)

	# Open the newly created deal
	# qs = "SELECT Id, PID__c, StageName__c FROM lda_Opportunity__c WHERE Id = '{0}'".format(DID)
	# results = bb.sfquery(service, qs)
	# TerraForce Query
	fields = 'default'
	wc = f"Id = '{DID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	DID = results[0]['Id']
	PID = results[0]['PID__c']
	salePID = PID
	dPnt['PID'] = PID
	dPnt['Status'] = results[0]['StageName__c']
	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))

	# Enter Lot Details
	if dTF['Lot_Type__c'] != 'Raw Acreage':
		printinfo(dPnt, 'start')
		print(' PID: {0}'.format(PID))
		ui = td.uInput('\n Add Lot Details? [0/1] > ')
		if ui == '1':
			bb.deleteExistingLotDetails(service, DID)
			totalLots = bb.LotDetail(service, DID)

	printinfo(dPnt, 'start')
	print(' PID: {0}'.format(PID))

	# Confirm OwnerIndex Polygon is created and saved with PID
	td.warningMsg('\n Confirm OwnerIndex polygon is created and saved with PID.')
	td.uInput('\n Continue > ')

	# CREATE LEAD FROM SALE DEAL ##########################################################
	# Don't create Leads for Idaho, Tucson, UNKNOWN Buyer or Buyer Acting As User
	if dTF['State__c'] == 'Idaho' or dTF['Buyer_Acting_As__c'] == 'User' or 'UNKNOWN' in BTX.upper():
		if dTF['State__c'] == 'Idaho':
			print('\n Leads are not required for Idaho comps...')
		elif dTF['County__c'] == 'Pima':
			print('\n Leads are not required for Tucson comps...')
		elif dTF['Buyer_Acting_As__c'] == 'User':
			print('\n Buyer acting as User. No Lead required.')
		elif 'UNKNOWN' in BTX.upper():
			print('\n Unknown Buyer. No Lead created.')
	else:
		while 1:
			ui = td.uInput('\n Create Lead? [0/1] > ')
			if ui == '0':
				print('\n No Lead created.')
				break
			elif ui == '1':
				leadPID = bb.tf_create_lead_of_sale_deal(service, PID)
				break
			else:
				td.warningMsg('\n Invalid entry...try again...\n\n > ')

	ui = td.uInput('\n [Enter] to continue or [00] to quit > ')
	if ui == '00':
		exit('\n Terminating program...')

td.banner('TF AWS CSV Entry PY3 v02')
print(' Entry for this spreadsheet complete...\n\n Fin')