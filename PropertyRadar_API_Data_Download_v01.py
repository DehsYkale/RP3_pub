# PropertyRadar data download using API

from collections import defaultdict
import csv
import dicts
import fun_acc_entity as fae
import fun_text_date as td
import json
import lao
import menus
import requests
from subprocess import Popen
from pprint import pprint
import pandas as pd

# # Select the market menu
# market = td.market_menu()

def get_proprad_api_fields():
	lao.print_function_name('Internal: get_proprad_api_fields')

	# proprad_api_fields = \
	# 	'Card,' \
	# 	'Map,' \
	# 	'Overview,' \
	# 	'APN,' \
	# 	'AssessorURL,' \
	# 	'County,' \
	# 	'FirstLenderOriginal,' \
	# 	'LenderAddress,' \
	# 	'LenderCityStZip,' \
	# 	'FirstAmount,' \
	# 	'FirstDate,' \
	# 	'FirstLoanType,' \
	# 	'FirstPurpose,' \
	# 	'FirstTermInYears,' \
	# 	'LastTransferSeller,' \
	# 	'LastTransferType,' \
	# 	'OwnerAddress,' \
	# 	'OwnerCity,' \
	# 	'OwnerState,' \
	# 	'OwnerZipFive,' \
	# 	'Subdivision,' \
	# 	'Zoning,' \
	# 	'-AVM,' \
	# 	'-AssessedValue,' \
	# 	'-AvailableEquity,' \
	# 	'-LotSize,' \
	# 	'-PType,' \
	# 	'-TotalLoanBalance,' \
	# 	'-isSameMailingOrExempt'
	
	proprad_api_fields = \
		'APN,' \
		'AVM,' \
		'County,' \
		'FirstAmount,' \
		'FirstDate,' \
		'FirstLenderOriginal,' \
		'FirstLoanType,' \
		'FirstPurpose,' \
		'FirstTermInYears,' \
		'LastTransferSeller,' \
		'LastTransferType,' \
		'LenderAddress,' \
		'LenderCityStZip,' \
		'LotSize,' \
		'Owner,' \
		'OwnerAddress,' \
		'OwnerCity,' \
		'OwnerState,' \
		'OwnerZipFive,' \
		'Subdivision,' \
		'RadarID,' \
		'Zoning' \
		
		# '-AssessedValue,' \
		# '-AvailableEquity,' \
		# '-PType,' \
		# '-TotalLoanBalance,' \
		# '-isSameMailingOrExempt'

	lProperty_fields = [
		'Address',
		'AdvancedPropertyType',
		'APN',
		'AssessorURL',
		'City',
		'County',
		'FirstAmount',
		'FirstDate',
		'FirstLenderOriginal',
		'FirstLoanType',
		'FirstPurpose',
		'FirstTermInYears',
		'inForeclosure',
		'isListedForSale',
		'LastTransferRecDate',
		'LastTransferSeller',
		'LastTransferType',
		'LastTransferValue',
		'Latitude',
		'Longitude',
		'LotSizeAcres',
		'Owner',
		'Owner2',
		'OwnerAddress',
		'OwnerCity',
		'OwnerState',
		'OwnerZipFive',
		'RadarID',
		'SqFt',
		'State',
		'Subdivision',
		'YearBuilt',
		'Zoning']
		# 		'Persons',
	lPerson_fields = [
			'Age',
			'Email',
			'FirstName',
			'LastName',
			'MailAddress',
			'Occupation',
			'OwnershipRole',
			'PersonType',
			'Phone',
			'PrimaryResidence',
			'isPrimaryContact']
	lEntity_fields = [
			'EntityName',
			'MailAddress',
			'OwnershipRole',
			'PersonType',
			'isPrimaryContact']


	return proprad_api_fields, lProperty_fields, lEntity_fields, lPerson_fields

# The payload has the query criteria
def get_payload(state, lCounty_fips, payload_type='COMPS'):
	lao.print_function_name('Internal: get_payload')
	# payload_type = 'COMPS', 'LISTINGS' or 'DEBT'
	if payload_type == 'COMPS':
		payload = {
			"Criteria": [
				{"name": "State", "value": [state]},
				{"name": "County", "value": lCounty_fips},
				{"name": "LotSizeAcres", "value": [[.1,999999]]},
				{"name": "LastTransferValue", "value": [[100000, 999999999]]},
				{"name": "LastTransferRecDate", "value": ["Last 90 Days"]},
				{"name": "PropertyType", "value": [
					{"name": "PType",
					"value": ["LND"]}]}
			]}
	elif payload_type == 'LISTINGS':
		pass
	elif payload_type == 'DEBT':
		payload = {
			"Criteria": [
				{"name": "State", "value": ["state"]},
				{"name": "County", "value": [lCounty_fips]},
				{"name": "LotSizeAcres", "value": [[3,999999]]},
				{"name": "FirstAmount", "value": [[2000000, 999999999]]},
				{"name": "FirstDate", "value": ["from: 5/1/2025 to: 5/31/2025"]},
				{"name": "hasOwnerPhone", "value": [1]},
				{"name": "hasOwnerMobilePhone", "value": [1]},
				{"name": "hasOwnerEmail", "value": [1]},
				{"name": "PropertyType", "value": [
					{"name": "PType",
					"value": ["LND"]}]}
			]}

	return payload

# Get PropertyRada data returned as a list of dicts
def get_properties_data(state, lCounty_fips, query_type):
	lao.print_function_name('Internal: get_properties_data')
	# PR token bf51945436937af5f8c9cf906683f7fc05b67956
	if query_type == 'PROPERTIES':
		url = "https://api.propertyradar.com/v1/properties"

		# proprad_api_fields = 'RadarID, State, ZipFive, APN'
		# query = {
		# "Purchase": "1",
		# "Fields": proprad_api_fields,
		# "Limit": "3",
		# "Sort": "ZipFive",
		# "Start": "0"
		# }

		# Fields All, Overview, Card
		# proprad_api_fields = 'RadarID, State, ZipFive, APN, LastTransferSeller'
		proprad_api_fields = dicts.get_proprad_api_fields()

		query = {
		"Purchase": "1",
		"Fields": proprad_api_fields,
		"Limit": "500",
		"Sort": "ZipFive",
		"Start": "0"
		}


	payload = get_payload(state, lCounty_fips, payload_type='COMPS')

	headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer bf51945436937af5f8c9cf906683f7fc05b67956"
	}

	# Getting the property data from the PropertyRadar API
	print('\n Getting PropertyRadar data...please stand by...')

	response = requests.post(url, json=payload, headers=headers, params=query)

	data = response.json()

	return data['results']

# Get Persons data for a PropertyRadar property ID
def get_persons_data(radar_id):
	lao.print_function_name('Internal: get_persons_data')

	url = f"https://api.propertyradar.com/v1/properties/{radar_id}/persons"

	proprad_api_fields = 'FirstName, MiddleName, LastName, EntityName, MailAddress, Phone, Email'
	query = {
	"Purchase": "1",
	"Fields": proprad_api_fields
	}

	headers = {"Authorization": "Bearer bf51945436937af5f8c9cf906683f7fc05b67956"}

	response = requests.get(url, headers=headers, params=query)

	data = response.json()

	# Get Phone and Email if they exist
	ldProp_persons = data['results']

	# print('here24')
	# pprint(ldProp_persons)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	for person in ldProp_persons:
		if 'Phone' in person.keys():
			# Check if the phone has already been purchased
			if 'v1' in person['Phone'][0]['href']:
				td.warningMsg(' looking up phone')
				url = f"https://api.propertyradar.com/v1/persons/{person['PersonKey']}/Phone"

				query = {
					"Purchase": "1"
				}

				response = requests.post(url, headers=headers, params=query)

				data = response.json()
				
				# print('here20')
				# pprint(person['Phone'])
				# print('\nhere22\n')
				# pprint(data)
				# ui = td.uInput('\n Continue [00]... > ')
				# if ui == '00':
				# 	exit('\n Terminating program...')
				
				
				if 'results' in data:
					person['Phone'] = data['results'][0]['Phone']
				else:
					person['Phone'] = 'None'

		if 'Email' in person.keys():
			if 'v1' in person['Email'][0]['href']:
				td.warningMsg(' looing up email')
				url = f"https://api.propertyradar.com/v1/persons/{person['PersonKey']}/Email"

				query = {
					"Purchase": "1"
				}

				response = requests.post(url, headers=headers, params=query)

				data = response.json()

				# print('here21')
				# pprint(data['results'])
				# ui = td.uInput('\n Continue [00]... > ')
				# if ui == '00':
				# 	exit('\n Terminating program...')
				
				if 'results' in data:
					person['Email'] = data['results'][0]['Email']
				else:
					person['Email'] = 'None'

	return ldProp_persons

# Build list of dicts from the PropertyRadar API data
def build_dicts_from_api_data(lProp_results, market_name, lookup_phone_email=True):
	lao.print_function_name('Internal: build_dicts_from_api_data')

	# List of dicts to hold the TF to CSV data
	ldTF_2_CSV = []

	print('\n Getting person data...please stand by...')
	# Cycle through the PropertyRadar API results
	for dProperty in lProp_results:
		# Get blank dict for TF to CSV
		dTF_2_CSV = dicts.get_tf_csv_dict()

		# Populate the TF to CSV dict with PropertyRadar data
		for key, value in dProp_field_map.items():
			# If the key is in the PropertyRadar data dict
			if key in dProperty.keys():
				dTF_2_CSV[value] = dProperty[key]

		if lookup_phone_email:
			# Get Persons data
			ldPersons = get_persons_data(dTF_2_CSV['Source_ID__c'])

			if ldPersons != []:
				for dPrsn in ldPersons:
					if dPrsn['PersonType'] == 'Person':
						dTF_2_CSV['Buyer Person'] = f'{dPrsn["FirstName"]} {dPrsn["LastName"]}'
						# Check if phone exists and download it from the API
						if 'Phone' in dPrsn.keys():
							dTF_2_CSV['Buyer Phone'] = dPrsn['Phone'][0]['linktext']
						if 'Email' in dPrsn.keys():
							dTF_2_CSV['Buyer Email'] = dPrsn['Email'][0]['linktext']
		
		# Add values to standard fields in dict
		dTF_2_CSV['MLS Status'] = 'Sold'
		dTF_2_CSV['Source__c'] = 'PropertyRadar'
		# Add Lead_Parcel__c
		lead_parcel = dProperty['APN'].split(',')
		dTF_2_CSV['Lead_Parcel__c'] = lead_parcel[0]
		# Add market name
		dTF_2_CSV['Market__c'] = market_name

		# Add the dict to the list of dicts
		ldTF_2_CSV.append(dTF_2_CSV)

	return ldTF_2_CSV

# Prints a PropertyRadar list of lists
def print_lists():
	lao.print_function_name('Internal: print_lists')

	url = "https://api.propertyradar.com/v1/lists"
	# query = {
	#   "Fields": "ListID",
	#   "ListType": "dynamic",
	#   "isMonitored": "1",
	#   "ImportSource": "api",
	#   "ImportType": "property",
	#   "Limit": "1000",
	#   "Sort": "TotalCount",
	#   "Dir": "desc"
	# }
	query = {
		"Fields": "ListID,ListName,ListType,TotalCount",
		"Limit": "1000",
		"Sort": "TotalCount",
		"Dir": "desc"
		}

	headers = {"Authorization": "Bearer bf51945436937af5f8c9cf906683f7fc05b67956"}

	response = requests.get(url, headers=headers, params=query)

	data = response.json()
	pprint(data)


def combine_multi_parcel_sales(property_data):
	"""
	Combines multi-parcel sales into single records.
	
	Multi-parcel sales are identified by matching:
	- LastTransferRecDate
	- LastTransferValue  
	- Owner
	
	When combining records:
	- APN values are combined into a comma-separated list
	- LotSizeAcres values are summed
	- All other fields remain unchanged (using the first record's values)
	
	Args:
		property_data: List of property records from PropertyRadar API
		
	Returns:
		List of property records with multi-parcel sales combined
	"""
	
	# Group records by the key fields that indicate a multi-parcel sale
	grouped_sales = defaultdict(list)
	
	for record in property_data:
		# Create a key from the fields that should match for multi-parcel sales
		# Handle cases where any of these fields might be None or missing
		transfer_date = record.get('LastTransferRecDate', '')
		transfer_value = record.get('LastTransferValue', '')
		owner = record.get('Owner', '')
		
		# Only group records that have all three key fields
		if transfer_date and transfer_value and owner:
			key = (transfer_date, transfer_value, owner)
			grouped_sales[key].append(record)
		else:
			# If any key field is missing, treat as single parcel
			grouped_sales[('single', len(grouped_sales), record.get('RadarID', ''))].append(record)
	
	combined_records = []
	
	for sale_group in grouped_sales.values():
		if len(sale_group) == 1:
			# Single parcel sale - add as-is
			combined_records.append(sale_group[0])
		else:
			# Multi-parcel sale - combine the records
			base_record = sale_group[0].copy()  # Start with first record
			
			# Combine APNs into comma-separated list
			apns = []
			total_acres = 0
			
			for record in sale_group:
				# Add APN if it exists and isn't already in the list
				apn = record.get('APN', '')
				if apn and apn not in apns:
					apns.append(apn)
				
				# Sum the lot sizes
				lot_size = record.get('LotSizeAcres', 0)
				if lot_size:
					total_acres += lot_size
			
			# Update the base record with combined values
			base_record['APN'] = ', '.join(apns)
			base_record['LotSizeAcres'] = round(total_acres, 2)  # Round to 2 decimal places
			
			combined_records.append(base_record)
	
	return combined_records

def filter_by_acreage(property_data, min_acres=2.0, min_value=1000000):
	"""
	Remove single parcel sales records that are less than the specified minimum acres.
	Remove all records where LastTransferValue is less than the minimum value.
	Multi-parcel sales (identified by comma-separated APNs) are kept regardless of acreage but still subject to value filter.
	
	Args:
		property_data: List of property records from PropertyRadar API
		min_acres: Minimum acreage threshold for single parcel sales (default: 2.0)
		min_value: Minimum transfer value for all sales (default: 1,000,000)
		
	Returns:
		List of property records with small single parcel sales and low-value sales filtered out
	"""
	
	filtered_records = []
	
	for record in property_data:
		# Check if this is a multi-parcel sale (comma in APN indicates combined parcels)
		is_multi_parcel = ',' in record.get('APN', '')
		
		# Get lot size and transfer value, default to 0 if missing
		lot_size = record.get('LotSizeAcres', 0)
		transfer_value = record.get('LastTransferValue', 0)
		
		# Apply acreage filter only to single parcel sales
		# Keep the record if:
		# 1. It's a multi-parcel sale (keep regardless of acreage), OR
		# 2. It's a single parcel sale that meets the minimum acreage requirement
		if is_multi_parcel:
			filtered_records.append(record)
		
		elif lot_size >= min_acres and transfer_value >= min_value:
			filtered_records.append(record)

	
	return filtered_records

def print_multi_parcel_stats(original_count, combined_data):
	"""
	Print statistics about multi-parcel sales found and combined.
	
	Args:
		original_count: Number of original records before combining
		combined_data: List of combined property records
	"""
	print(f"\n--- Multi-Parcel Sales Summary ---")
	print(f"Original records: {original_count}")
	print(f"Combined records: {len(combined_data)}")
	print(f"Multi-parcel sales identified: {original_count - len(combined_data)}")
	
	# Count and display multi-parcel sales
	multi_parcel_count = 0
	for record in combined_data:
		if ',' in record.get('APN', ''):
			multi_parcel_count += 1
			apn_count = len(record.get('APN', '').split(','))
			print(f"  • {record.get('Owner', 'Unknown')} - {apn_count} parcels - "
				  f"{record.get('LotSizeAcres', 0)} acres - ${record.get('LastTransferValue', 0):,}")
	
	print(f"Total multi-parcel sales: {multi_parcel_count}")

def print_acreage_filter_stats(before_count, after_data, min_acres, min_value):
	"""
	Print statistics about records filtered by acreage and value.
	
	Args:
		before_count: Number of records before filtering
		after_data: List of property records after filtering
		min_acres: Minimum acreage threshold used
		min_value: Minimum transfer value threshold used
	"""
	after_count = len(after_data)
	removed_count = before_count - after_count
	
	print(f"\n--- Acreage & Value Filter Summary ---")
	print(f"Records before filtering: {before_count}")
	print(f"Records after filtering: {after_count}")
	print(f"Records removed: {removed_count}")
	print(f"  • Small single parcels (< {min_acres} acres) and/or")
	print(f"  • Low value sales (< ${min_value:,})")
	
	# Count multi-parcel vs single parcel sales in final results
	multi_parcel_count = 0
	single_parcel_count = 0
	
	for record in after_data:
		if ',' in record.get('APN', ''):
			multi_parcel_count += 1
		else:
			single_parcel_count += 1
	
	print(f"Final results: {multi_parcel_count} multi-parcel sales, {single_parcel_count} single parcel sales")
	
	# Show value range of remaining records
	if after_data:
		values = [record.get('LastTransferValue', 0) for record in after_data]
		min_remaining_value = min(values)
		max_remaining_value = max(values)
		print(f"Value range: ${min_remaining_value:,} - ${max_remaining_value:,}")

# Main program starts here
td.banner('PropertyRadar API Data Download v01')

# Get the property fields mapping to the csv fields
dProp_field_map = dicts.get_proprad_to_tf_csv_field_map_dict()

# LAO Markets menu can return the market abbreviation (AIRPORTCODE) or market name (MARKETNAME)
market_name, market_abb = menus.lao_markets(mkt_format='BOTH')
print(f'\n Selected Market: {market_name}')

# Get the county and state from the market abbreviation
state, lCounty_fips = dicts.get_county_fips_codes(market_abb)

# Get text string of api fields and a list of the fields for making the csv
proprad_api_fields, lProperty_fields, lEntity_fields, lPerson_fields = get_proprad_api_fields()

# PR query results as a list of dicts
lProp_results = get_properties_data(state, lCounty_fips, 'PROPERTIES')

# Store original count for statistics
original_count = len(lProp_results)

# Step 1: Combine multi-parcel sales
print('\n Combining multi-parcel sales...')
lProp_results = combine_multi_parcel_sales(lProp_results)
print_multi_parcel_stats(original_count, lProp_results)

# Step 2: Filter out small single parcel sales (< 2 acres) and low-value sales (< $1M)
print('\n Filtering out small single parcel sales and low-value sales...')
before_filter_count = len(lProp_results)
lProp_results = filter_by_acreage(lProp_results, min_acres=2.0, min_value=1000000)
print_acreage_filter_stats(before_filter_count, lProp_results, 2.0, 1000000)


ldTF_2_CSV = build_dicts_from_api_data(lProp_results, market_name, lookup_phone_email=False)

# Get list of TF to CSV fields
lTF_2_CSV_fields = dicts.get_tf_csv_header()

# Build the CSV file name based on the market and date
csv_file_path = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/'
csv_file_name = f'{market_abb} PropRad Comps {td.today_date()}_FORMATTED.csv'
filename = f'{csv_file_path}{csv_file_name}'

# Open the CSV file for writing
with open(filename, mode='w', newline='') as f:
	fout = csv.writer(f)

	# Write the header row
	fout.writerow(lTF_2_CSV_fields)

	# Cycle through the list of dicts and write each row based on the lTF_2_CSV_fields
	for rec in ldTF_2_CSV:
		row = []
		for fld in lTF_2_CSV_fields:
			row.append(rec[fld])
		fout.writerow(row)

lao.openFile(filename)


