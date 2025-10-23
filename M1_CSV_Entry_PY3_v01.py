# Enter CSVs into TF & L6/M1 from Reonomy, Crexi, Costar, PropertyRadar, BCI

import bb
from colored import Fore, Back, Style
from datetime import datetime
import dicts
import fun_text_date as td
import fun_login
import lao
import mpy
import pandas as pd
from pprint import pprint
import os
import webs

# Get the field mapping dictionary for the CSV file
def get_field_mapping_dict():

	dFM = {
		'TF': {
			'Acres__c': 'Acres__c',
			'City__c': 'City__c',
			'Classification__c': 'Classification__c',
			'Country__c': 'Country__c',
			'County__c': 'County__c',
			'Description__c': 'Description__c',
			'Latitude__c': 'Latitude__c',
			'Lead_Parcel__c': 'Lead_Parcel__c',
			'List_Date__c': 'List_Date__c',
			'List_Price__c': 'List_Price__c',
			'Loan_Amount__c': 'Loan_Amount__c',
			'Loan_Date__c': 'Loan_Date__c',
			'Location__c': 'Location__c',
			'Longitude__c': 'Longitude__c',
			'Lot_Type__c': 'Lot_Type__c',
			'Lots__c': 'Lots__c',
			'Market__c': 'Market__c',
			'MLS Status': 'StageName__c',  # MLS Status is used for StageName__c if 'Sold' changed to 'Closed Lost'
			'Deal Name': 'Deal Name',
			'Parcels__c': 'Parcels__c',
			'PID__c': 'PID__c',
			'Recorded_Instrument_Number__c': 'Recorded_Instrument_Number__c',
			'Sale_Date__c': 'Sale_Date__c',
			'Sale_Price__c': 'Sale_Price__c',
			'Source_ID__c': 'Source_ID__c',
			'Source__c': 'Source__c',
			'State__c': 'State__c',
			'Subdivision__c': 'Subdivision__c',
			'Submarket__c': 'Submarket__c',
			'Zipcode__c': 'Zipcode__c',
			'Zoning__c': 'Zoning__c'
		},
		'Seller': {
			'Seller City': 'CITY',
			'Seller Email': 'EMAIL',
			'Seller Entity': 'ENTITY',	# Company
			'Seller Person': 'NAME',		# Person Name
			'Seller Phone': 'PHONE',
			'Source__c': 'SOURCE',		# Source of the date (i.e. parcel, TPS, DnB...)
			'Seller State': 'STATE',
			'Seller Street': 'STREET',
			'Seller Zip': 'ZIPCODE'
		},
		'Buyer': {
			'Buyer City': 'CITY',
			'Buyer Email': 'EMAIL',
			'Buyer Entity': 'ENTITY',	# Company
			'Buyer Person': 'NAME',		# Person Name
			'Buyer Phone': 'PHONE',
			'Source__c': 'SOURCE',		# Source of the date (i.e. parcel, TPS, DnB...)
			'Buyer State': 'STATE',
			'Buyer Street': 'STREET',
			'Buyer Zip': 'ZIPCODE'
		},
		'List Agent': {
			'List Agent Email': 'EMAIL',
			'List Entity': 'ENTITY',	# Company
			'List Agent': 'NAME',		# Person Name
			'List Agent Phone': 'PHONE',
			'Source__c': 'SOURCE'		# Source of the date (i.e. parcel, TPS, DnB...)
		},
		'Buyer Agent': {
			'Buyer Agent Email': 'EMAIL',
			'Buyer Agent Entity': 'ENTITY',	# Company
			'Buyer Agent': 'NAME',			# Person Name
			'Buyer Agent Phone': 'PHONE',
			'Source__c': 'SOURCE',			# Source of the date (i.e. parcel, TPS, DnB...)
		},
		'Lender': {
			'Lender': 'ENTITY',				# Company
			'Source__c': 'SOURCE'			# Source of the date (i.e. parcel, TPS, DnB...)
		}
	}

	return dFM

# Get the datafram of the csv
def get_df():
	# Define the path to the CSV file
	csv_folder = r"F:\Research Department\scripts\Projects\Research\data\CompsFiles"
	csv_filename = "ATL Comps 1 040725_FORMATTED.csv"
	csv_path = os.path.join(csv_folder, csv_filename)

	# Load the CSV file into pandas DataFrame
	# Using cp1252 encoding as specified in the document metadata
	df = pd.read_csv(csv_path, encoding='cp1252')

	# Check if DataFrame is empty
	if df.empty:
		print("Error: CSV file is empty")
		return None
		
	print(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")

	# Get the number of rows in the DataFrame
	df_row_count = len(df)

	return df, df_row_count

# Get the TF deal dictionary and populate it with the first row of data from the CSV
def get_dTF(df, indx, field_mapping):
	"""
	Load the CSV file into pandas, create a blank TF deal dictionary,
	and populate it with the first line of data from the CSV.
	"""

	# Create a blank TF deal dictionary
	dTF = dicts.get_blank_tf_deal_dict()
	
	# Populate the dictionary with the first row data
	dTF = populate_dict(df, indx, dTF, field_mapping)
	
	# Set default record type to Research for imported data
	dTF['RecordTypeID'] = '012a0000001ZSS8AAO' # Research Type
	dTF['type'] = 'lda_Opportunity__c'
	dTF['Verified__c'] = True

	# Set Acres__c to 0 if not provided
	if dTF['Acres__c'] == 'None':
		dTF['Acres__c'] = 0.0
	# Set country to 'USA' if not provided
	if dTF['Country__c'] == 'None':
		dTF['Country__c'] = 'USA'
	# Format county name
	if dTF['County__c'] == 'None':
		td.warningMsg('\n No County listed in data! Terminating program...')
		exit()
	else:
		dTF['County__c'] = dTF['County__c'].replace(' ', '')  # Remove spaces from county name
	# Format lon/lat
	# if dTF['Latitude__c'] != 'None':
	# 	dTF['Longitude__c'], dTF['Latitude__c'] = (dTF['Longitude__c']).strip(), (dTF['Latitude__c']).strip()
	# Format List Date
	if dTF['List_Date__c'] != 'None':
		dTF['List_Date__c'] = td.date_engine(dTF['List_Date__c'])
	# Format List Price
	# if dTF['List_Price__c'] != 'None':
	# 	dTF['List_Price__c'] = (dTF['List_Price__c']).replace('$', '').replace(',', '')
	# Format lots
	if dTF['Lots__c'] != 'None':
		dTF['Lots__c'] = int(dTF['Lots__c'])
	# Format Sale Date
	if dTF['Sale_Date__c'] != 'None':
		sDate = td.date_engine(dTF['Sale_Date__c'])
		if datetime.now() > datetime.strptime(sDate, '%Y-%m-%d'):
			dTF['Sale_Date__c']= td.date_engine(dTF['Sale_Date__c'])
	# Format Sale Price
	if dTF['Sale_Price__c'] != 'None':
		dTF['Sale_Price__c'] = 10000
	else:
		dTF['Sale_Price__c'] = (dTF['Sale_Price__c']).replace('$', '').replace(',', '')
	# Format Source
	if dTF['Source__c'] == 'None':
		dTF['Source__c'] = 'LAO'
	# Add state if missing
	if dTF['State__c'] == 'None':
		dTF['STATE'] = lao.get_state_of_market(dTF['Market__c'], dTF['County__c'])
	# Format state
	if len(dTF['State__c']) == 2:
		dTF['State__c'] = td.convert_state(dTF['State__c'])
	# Set Stage Name to Closed Lost for imported sales
	if dTF['StageName__c'] == 'Sold':
		dTF['StageName__c'] = 'Closed Lost'
	elif dTF['StageName__c'] in ['Acitve', 'Pending', 'Back on Market']:
		dTF['StageName__c'] = 'Lead'
	else:
		dTF['StageName__c'] = 'Closed Lost'
	# Set OPR Send date
	if dTF['Sale_Date__c'] == 'None' or dTF['Sale_Price__c'] == 'None':
		if dTF['MLS Status'] == 'Sold':
			dTF['OPR_Sent__c'] = '1965-01-11'
		else:
			dTF['OPR_Sent__c'] = '1964-09-11'
	else:
		dTF['OPR_Sent__c'] = '1965-01-11'

	print("Successfully created and populated TF deal dictionary")
	
	return dTF

# Get Account dicts for Seller, Buyer, Agent, and Lender
def get_account_dicts(df, indx, dFM):
	"""
	Load the CSV file into pandas, create a blank TF deal dictionary,
	and populate it with the first line of data from the CSV.
	"""

	# Create a blank Account dicts
	dSeller = dicts.get_blank_account_dict()
	dBuyer = dicts.get_blank_account_dict()
	dAgent_list = dicts.get_blank_account_dict()
	dAgent_buyer = dicts.get_blank_account_dict()
	dLender = dicts.get_blank_account_dict()
	
	# Populate the dictionary with the first row data
	dSeller = populate_dict(df, indx, dSeller, dFM['Seller'])
	dBuyer = populate_dict(df, indx, dBuyer, dFM['Buyer'])
	dAgent_list = populate_dict(df, indx, dAgent_list, dFM['List Agent'])
	dAgent_buyer = populate_dict(df, indx, dAgent_buyer, dFM['Buyer Agent'])
	dLender = populate_dict(df, indx, dLender, dFM['Lender'])
	
	return dSeller, dBuyer, dAgent_list, dAgent_buyer, dLender

# Poulate the dictionary based on the field mapping
def populate_dict(df, indx, dDict, field_mapping):

	# Get the first row of data
	first_row = df.iloc[indx]

	# Populate the dictionary with the first row data
	for csv_field, tf_field in field_mapping.items():
		if csv_field in first_row:
			# Handle different data types appropriately
			if pd.notna(first_row[csv_field]):
				dDict[tf_field] = first_row[csv_field]

	return dDict

# Get the dPrint dictionaries for console output
def get_dPrint(dTF, dSeller, dBuyer, dAgent_list, dAgent_buyer, dLender):

	dPrint = {
		'Acres': dTF['Acres__c'],
		'Beneficiary': dLender['ENTITY'],
		'Buyer_Agent': dAgent_buyer['NAME'],
		'Buyer_Entity': dBuyer['ENTITY'],
		'Buyer_Person': dBuyer['NAME'],
		'City': dTF['City__c'],
		'Classification': dTF['Classification__c'],
		'County': dTF['County__c'],
		'Latitude': dTF['Latitude__c'],
		'Lead_Parcel': dTF['Lead_Parcel__c'],
		'List_Agent': dAgent_list['NAME'],
		'List_Date': dTF['List_Date__c'],
		'List_Price': dTF['List_Price__c'],
		'Location': dTF['Location__c'],
		'Longitude': dTF['Longitude__c'],
		'Lots': dTF['Lots__c'],
		'Parcels': dTF['Parcels__c'],
		'PID': dTF['PID__c'],
		'RDN': dTF['Recorded_Instrument_Number__c'],
		'StageName': dTF['StageName__c'],
		'Sale_Date': dTF['Sale_Date__c'],
		'Sale_Price': dTF['Sale_Price__c'],
		'Seller_Entity': dSeller['ENTITY'],
		'Seller_Person': dSeller['NAME'],
		'Source_ID': dTF['Source_ID__c'],
		'Subdivision': dTF['Subdivision__c'],
		'Zoning': dTF['Zoning__c'],
	}

	return dPrint

# Print the important info
def printinfo(dPrint, df_row_count, indx, hiLight='None'):

	# Print the banner with progress info
	recordsleft = df_row_count - indx
	td.banner('M1 CSV Entry PY3 v01 Row: {0} : {1} : {2}'.format(df_row_count, indx, recordsleft))

	if hiLight == 'Start':
		td.color_on_off('YELLOW')
	print(' Status:   {0:30}  PID:   {1}'.format(dPrint['StageName'], dPrint['PID']))
	td.color_on_off('OFF')
	print(' County:   {0:30}  City:  {1}'.format(dPrint['County'], dPrint['City']))
	print('\n')
	print(' Lead Par: {0:30}'.format(dPrint['Lead_Parcel']))
	print(' Parcles:  {0}'.format(dPrint['Parcels']))
	print()
	menuColor = ''
	sellerColor = ''
	buyerColor = ''
	if hiLight == 'seller':
		sellerColor = Fore.yellow_2
	if hiLight == 'buyer':
		buyerColor = Fore.yellow_2
	print('{0} Seller    {1:30}{2}  {3}Buyer{4}'.format(sellerColor, '', Style.reset, buyerColor, Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPrint['Seller_Entity'], Style.reset, buyerColor, dPrint['Buyer_Entity'], Style.reset))
	print('{0}  {1:40}{2}  {3}{4}{5}'.format(sellerColor, dPrint['Seller_Person'], Style.reset, buyerColor, dPrint['Buyer_Person'], Style.reset))
	if hiLight == 'listingagent':
		menuColor = Fore.yellow_2
	print('{0}  Agnt {1:35}  {2}{3}'.format(menuColor,dPrint['List_Agent'], dPrint['Buyer_Agent'], Style.reset))
	menuColor = ''
	if 'Beneficiary' in dPrint:
		if hiLight == 'beneficiary':
			print('{0}'.format(Fore.yellow_2))
		else:
			print('{0}'.format(Style.reset))
		print('Beneficiary')
		print('  {0}'.format(dPrint['Beneficiary']))
		print('{0}'.format(Style.reset))
	else:
		print('{0}'.format(Style.reset))
	menuColor = ''
	if hiLight == 'acres':
		menuColor = Fore.yellow_2
	print('{0} Acres:    {1}{2}'.format(menuColor, dPrint['Acres'], Style.reset))
	print(' Lots:     {0}'.format(str(dPrint['Lots'])))
	if hiLight == 'classification':
		menuColor = Fore.yellow_2
	print('{0} Class:    {1}{2}'.format(menuColor, dPrint['Classification'], Style.reset))
	menuColor = ''
	print
	print(' Date:     {0}'.format(dPrint['Sale_Date']))
	print(' Price:    {0}'.format(td.currency_format_from_number(dPrint['Sale_Price'])))
	print(' Lst Date: {0}'.format(dPrint['List_Date']))
	print(' Lst Price:{0}'.format(td.currency_format_from_number(dPrint['List_Price'])))
	print('\n')
	print(' SourceID  {0}'.format(dPrint['Source_ID']))
	print(' RDN:      {0}'.format(dPrint['RDN']))
	print('\n')
	if 'Longitude' in dPrint:
		print(' Lon Lat:  {0} {1}'.format(dPrint['Longitude'], dPrint['Latitude']))
	else:
		print(' Lon Lat: None')
	print(' Location: {0}'.format(dPrint['Location']))
	print(' Sub Name: {0}'.format(dPrint['Subdivision']))
	print('_________________________________________________________________________\n')

# Create the zoomToPolygon json file
def create_zoomToPolygon(dTF):
	# Field name is the parcel layer name
	state = td.convert_state(dTF['State__c'])
	county = dTF['County__c'].title()
	polyinlayer = f'{state}Parcels{county}'
	mpy.create_zoomToPolygon_json_file(fieldname='apn', polyId=dTF['Lead_Parcel__c'], polyinlayer=polyinlayer, lon=dTF['Longitude__c'], lat=dTF['Latitude__c'], market=dTF['Market__c'])

# User Options
def user_options_menu():

	td.colorText('\n Zoom to Polygon ready...', 'GREEN')
	# Display the user options menu
	print('\n\n')
	print(' User Options Menu')
	print(' 1) Enter PID')
	print(' 2) Enter TF deal dictionary')
	print(' 3) Enter Account dictionaries')
	print(' 4) Enter ZoomToPolygon json file')
	print(' 5. Exit program')
	print('\n')

	# Get user input
	user_input = input(' Select an option: ')
	if user_input == '1':
		get_df()
	elif user_input == '2':
		get_dTF()
	elif user_input == '3':
		get_account_dicts()
	elif user_input == '4':
		create_zoomToPolygon()
	elif user_input == '5':
		exit()


td.banner('M1 CSV Entry PY3 v01')

# Get the DataFrame from the CSV file
df, df_row_count = get_df()

# Get the field mapping dictionary
dFM = get_field_mapping_dict()

# get the TF deal dictionary and populate it with the first row of data from the CSV
for indx in range(0, df_row_count):

	# Get the TF deal dictionary
	dTF = get_dTF(df, indx, dFM['TF'])
	# Get Account dicts for Seller, Buyer, Agent, and Lender
	dSeller, dBuyer, dAgent_list, dAgent_buyer, dLender = get_account_dicts(df, indx, dFM)
	# Get the dPrint dictionaries for console output
	dPrint = get_dPrint(dTF, dSeller, dBuyer, dAgent_list, dAgent_buyer, dLender)

	# Create the zoomToPolygon json file
	create_zoomToPolygon(dTF)
	# Print the important info
	printinfo(dPrint, df_row_count, indx, hiLight='Start')
	# Open Reonomy record
	driver = webs.selenium_LAO_Data_Sites_Login(dTF['Source_ID__c'])
	

	

	



