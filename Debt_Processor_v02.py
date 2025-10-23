
# Debt processor for Property Radar

import lao
# import amp
import csv
import dicts
import fun_text_date as td
from glob import glob
import gspread
from google.oauth2.service_account import Credentials
import os
import re
import shutil
from pprint import pprint
from zipfile import ZipFile

import geopandas as gpd
from shapely.geometry import Point

# Connect to the Google Sheet
def gs_connect():
	# Path to the service account credentials JSON file
	SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), 'workspaces-339922-bb678e67b28b.json')

	# The scopes required for Google Sheets API
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

	# Authenticate and construct the service
	credentials = Credentials.from_service_account_file(
		SERVICE_ACCOUNT_FILE, scopes=SCOPES)

	gc = gspread.authorize(credentials)

	# Open the Google Sheet using its name or ID
	spreadsheet_id = '1w88EfdoJXOGHLh0SlvBywQvPanGjMTmwf9B8boh_Uew'
	spreadsheet = gc.open_by_key(spreadsheet_id)

	return spreadsheet

# Create a list of list of the debt csv file
def get_debt_records_list():
	list_of_lists = []
	lHeader = 'None'
	for row in dMstr:
		if lHeader == 'None':
			lHeader = list(dMstr[row].keys())
			list_of_lists.append(lHeader)
		lValues = list(dMstr[row].values())
		list_of_lists.append(lValues)

	return list_of_lists

# Remove unwanted text line from Prop Rad csv.
def prop_rad_clean_csv(csv_path):
	with open(csv_path, 'r') as f:
		lines = f.readlines()
	with open(csv_path, 'w', newline='') as f:
		for line in lines:
			if 'The information contained' in line:
				break
			f.write(line)

def combine_duplicates(dDebt, src):
	unique_dicts = {}
	keys = dDup_keys[src]
	for key, value in dDebt.items():
		unique_key = tuple(value[k] for k in keys)
		if unique_key not in unique_dicts:
			unique_dicts[unique_key] = value
		else:
			initial_record = unique_dicts[unique_key]
			if src == 'PR':
				sum_acres = float(initial_record['Lot Acres']) + float(value.get('Lot Acres', 0))
				initial_record['Lot Acres'] = sum_acres
				initial_record['APN'] += ', ' + value.get('APN', '')
			elif src == 'RY':
				sum_acres = float(initial_record['lot_area']) + float(value.get('lot_area', 0))
				initial_record['lot_area'] = sum_acres
				initial_record['apn'] += ', ' + value.get('apn', '')
			elif src == 'MSTR':
				# Populate blank values if duplicate has value in the field
				lFields = ['Owner Entity', 'Owner Person', 'Mail Street', 'Mail City', 'Mail State', 'Mail Zip', 'Loan Maturity Date', 'Loan Purpose', 'Prop Type', 'Prop Subtype', 'Last Sale Date', 'Last Sale Amount']
				for fld in lFields:
					# print(fld)
					# print('{0}: {1}'.format(initial_record[fld], len(str(initial_record[fld]))))
					if len(str(initial_record[fld])) == 0 and len(str(value.get(fld))) > 0:
						initial_record['Source'] = 'PROPRAD REON'
						initial_record[fld] = value.get(fld)
					# unique_dicts[unique_key] = initial_record

	return unique_dicts

def add_lao_market_to_dict():
	print(' Adding LAO Markets & Submarkets...')
	for row in dMstr:
		lon = dMstr[row]['Longitude']
		lat = dMstr[row]['Latitude']
		
		# Blank coordinates
		if lon == '':
			continue

		point = Point(lon, lat)

		# Check which geometry in the GeoDataFrame contains the point
		# print(' Finding county...')
		containing_county = gdf[gdf.contains(point)]

		dLAO_geo = {}
		if containing_county.empty:
			# print("The given coordinates do not fall within any county in the shapefile.")
			dMstr[row]['LAO Market'] = ''
			dMstr[row]['LAO Submarket'] = ''
		else:
			# Assuming the shapefile has 'NAME' for county name and 'STATE_NAME' for state name
			dLAO_geo['state_abb'] = containing_county.iloc[0]['state']
			# dLAO_geo['state_full'] = containing_county.iloc[0]['statefull']
			dLAO_geo['county_name'] = containing_county.iloc[0]['county']
			dLAO_geo['market_full'] = containing_county.iloc[0]['market']
			dLAO_geo['market_abb'] = containing_county.iloc[0]['marketabb']
			dLAO_geo['arcname'] = containing_county.iloc[0]['arcname']
			dLAO_geo['submarket'] = containing_county.iloc[0]['submarket']

			# Upper case LAO Markets & Submarkets
			# if dLAO_geo['market_full'] is None:
			# 	dMstr[row]['LAO Market'] = dLAO_geo['market_full']
			# 	if dLAO_geo['submarket'] is None:
			# 		dMstr[row]['LAO Submarket'] = dLAO_geo['submarket']
			# 	else:
			# 		dMstr[row]['LAO Submarket'] = dLAO_geo['submarket'].upper()
			if dLAO_geo['market_full'] is None:
				dMstr[row]['LAO Market'] = None
				dMstr[row]['LAO Submarket'] = None
			else:
				dMstr[row]['LAO Market'] = dLAO_geo['market_full'].upper()
				dMstr[row]['LAO Submarket'] = dLAO_geo['submarket'].upper()
			# ui = '\n Continue... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
		
	return dMstr

def build_master_dict(dDebt, src, key_index, data_type):
	dt = data_type[:1].upper()
	for row in dDebt:
		d = dDebt[row]

		# Create record key
		i_str = '{:03d}'.format(key_index)
		i_key = f'{src}{dt}{i_str}'
		dMstr[i_key] = {}

		for dFlds in dDebt_fields:
			# Populate no corrisponding data field
			if dDebt_fields[dFlds][src] == '':
				if src == 'VZ':
					if dFlds == 'Foreclosure':
						dMstr[i_key][dFlds] = '0'
					elif dFlds == 'FCL Doc Type':
						dMstr[i_key][dFlds] = 'NOT IN FCL'
					elif dFlds == 'FCL Stage':
						dMstr[i_key][dFlds] = 'NOT IN FCL'
					else:
						dMstr[i_key][dFlds] = ''
				else:
					dMstr[i_key][dFlds] = ''

			# Populate Source field
			elif dFlds == 'Source':
				if src == 'PR':
					dMstr[i_key][dFlds] = 'PROPERTY RADAR'
				elif src == 'RY':
					dMstr[i_key][dFlds] = 'REONOMY'
				elif src == 'VZ':
					dMstr[i_key][dFlds] = 'VIZZDA'

			# Populate Forclosure field if Reonomy or Vizzda
			elif dFlds == 'Foreclosure' and src == 'RY':
				csv_src_field = dDebt_fields[dFlds][src]
				if d[csv_src_field] == '':
					dMstr[i_key][dFlds] = '0'
				else:
					dMstr[i_key][dFlds] = '1'
				# Add not a foreclosure to Vizzda Records
			

			# Populate PR FCL Doc Type with full doc name
			elif dFlds == 'FCL Doc Type' and src == 'PR' and d[dFlds] != '':
				flc_doc_type = d[dFlds]
				dMstr[i_key]['FCL Doc Type'] = dFCL_doc_type[flc_doc_type]

			
			
			# Populate Vizzda FCL Doc and Statge
			elif dFlds == 'FCL Doc Type' and src == 'VZ':
				dMstr[i_key][dFlds] = 'NOT IN FCL'
			elif dFlds == 'FCL Stage' and src == 'VZ':
				dMstr[i_key][dFlds] = 'NOT IN FCL'

			# Populate dMstr fields
			else:
				csv_src_field = dDebt_fields[dFlds][src]
				dMstr[i_key][dFlds] = d[csv_src_field]
			
		key_index += 1

	return dMstr, key_index

# Process the raw debt data from Property Radar, Reonomy
def process_raw_debt_data(dMstr, src, data_type='debt'):
	# Build raw csv file path
	if data_type == 'debt':
		if src == 'PR':
			lFiles = glob(f'{debt_folder}Property Radar/*.csv')
		elif src == 'RY':
			unzip_Reonomy_files()
			lFiles = glob(f'{debt_folder}Reonomy/*_properties.csv')
		elif src == 'VZ':
			lFiles = glob(f'{debt_folder}Vizzda/Vizzda*.xlsx')
	elif data_type == 'foreclosure':
		if src == 'PR':
			lFiles = glob(f'{debt_folder}Foreclosure/Property Radar*.csv')
		elif src == 'RY':
			lFiles = glob(f'{debt_folder}Foreclosure/Reonomy*.csv')

	key_index = 1
	for csv_path in lFiles:
		basefilename = os.path.basename(csv_path)
		print(basefilename)

		# Remove unwanted text line from Prop Rad csv.
		if src == 'PR':
			prop_rad_clean_csv(csv_path)
		# Make dict from csv
		dDebt = lao.spreadsheetToDict(csv_path)
		# Remove duplcates
		unique_debts = combine_duplicates(dDebt, src)
		dDebt = unique_debts
		# Add to Master dict
		dMstr, key_index = build_master_dict(dDebt, src, key_index, data_type)

	return dMstr

def unzip_Reonomy_files():
	print('here1')
	reonomy_folder = f'{debt_folder}Reonomy/'
	lFiles = glob(f'{reonomy_folder}*.zip')
	# Loop through all files in the specified folder
	# zip_path = os.path.join(root, file)  # Full path to the zip file
	
	for zip_path in lFiles:
	# Open the zip file
		with ZipFile(zip_path, 'r') as zip_ref:
			# Get the list of all files inside the zip
			for zip_file in zip_ref.namelist():
				# Check if the file name contains 'properties.csv'
				if 'properties.csv' in zip_file:
					# Construct the target path in the same folder as the zip file
					destination_path = f'{debt_folder}Reonomy/{os.path.basename(zip_file)}'
					# Extract the 'properties.csv' file to the same folder as the zip file
					with zip_ref.open(zip_file) as source_file, open(destination_path, 'wb') as target_file:
						shutil.copyfileobj(source_file, target_file)

# Update the Google Sheet
def update_gs():
	# Connect to the Google Sheet
	spreadsheet = gs_connect()
	# Create a list of list of the debt csv file
	lDebt = get_debt_records_list()
	# Select the worksheet by name or index. For example, by index:
	worksheet = spreadsheet.get_worksheet(0)  # 0 means the first worksheet
	# Write the records to Google Sheets
	worksheet.update(lDebt)

# Parce Vizzda string
def parce_string(txt, dPatterns):

	# Check if loan is in the txt by $
	if '$' not in txt:
		return ''
	if 'no debt recorded' in txt:
		return 'no debt'

	
	# Cycle through patterns
	pattern_found = False
	for pattern in dPatterns:
		# Check if pattern is in the txt string
		if pattern in txt:
			# print(txt)
			# print(pattern)
			pattern_found = True
			match = (re.search(pattern, txt))
			# Find currency that falls before the pattern
			if dPatterns[pattern] == 'backward':
				start_index = (match.start())
				txt_end_index = -1
				step = -1
			elif dPatterns[pattern] == 'forward':
				start_index = (match.end())
				txt_end_index = len(txt)
				step = 1
			break

	

	if pattern_found:
		# print(f'match: {match}')
		# print(f'start_index: {start_index}')
		# print(f'txt_end_index: {txt_end_index}')
		# print('txt to parce: {0}'.format(txt[start_index:txt_end_index]))
		# Find $ for the starting point to parce
		for i in range(start_index, txt_end_index, step):
			if txt[i] == '$':
				start_index = i
				txt_end_index = len(txt)
				break
		# Find space ' ' for the ending point to parce
		for i in range(start_index, txt_end_index, 1):
			if txt[i] == ' ':
				end_index = i
				break

		# Format the currency	
		strParced = txt[start_index: end_index]
		# print(strParced)
		# Loan Amount formated as millions like $123m
		if strParced[-1] == 'm':
			strParced = strParced.replace('$', '').replace(',', '.').replace('m', '')
			float_temp = float(strParced)
			# print(f'float_temp: {float_temp}')
			strParced = float_temp * 1000000
			# print(f'strParced: {strParced}')
		else:
			strParced = strParced.replace('$', '').replace(',', '').replace('in', '')
		return strParced
	else:
		return ''
	
# Standarize fields in Master dictionary
def standardize_dMstr_fields(dMstr):
	# Remove records without a lon/lat
	# Make temp dict to hold values need to skip
	dTemp = {}
	for row in dMstr:
		
		if dMstr[row]['Latitude'] == '':
			continue
		else:
			dTemp[row] = dMstr[row]
	dMstr = dTemp

	# Clean County names
	for row in dMstr:

		# Populate non-Foreclosure FCL Doc Type with Not in Foreclosure
		if dMstr[row]['Foreclosure'] == '0':
			dMstr[row]['FCL Doc Type'] = 'NOT IN FCL'
			dMstr[row]['FCL Stage'] = 'NOT IN FCL'
		else:
			if dMstr[row]['FCL Doc Type'] == '':
				dMstr[row]['FCL Doc Type'] = 'UNKNOWN'
				dMstr[row]['FCL Stage'] = 'PREFORECLOSURE'

		# Clean County names
		if dMstr[row]['Source'] == 'VIZZDA':
			if dMstr[row]['County'] == 1:
				dMstr[row]['County'] = 'MARICOPA'
			elif dMstr[row]['County'] == 3:
				dMstr[row]['County'] = 'PINAL'
		else:
			dMstr[row]['County'] = dMstr[row]['County'].replace(' County', '').upper()

		# Upper case fields
		lFields = ['County', 'Owner Entity', 'Owner Person', 'Mail Street', 'Mail City', 'Lender', 'Loan Purpose', 'Prop Type', 'Prop Subtype', 'FCL Stage', 'FCL Doc Type']
		for fld in lFields:
			# Convert null fields to ''
			if dMstr[row][fld] == None:
				dMstr[row][fld] = ''
			else:
				dMstr[row][fld] = dMstr[row][fld].upper()
		
		# Populate Reonomy FCL Stage field based on FCL Doc Type
		if dMstr[row]['Source'] == 'REONOMY':
			if dMstr[row]['FCL Stage'] == '':
				dMstr[row]['FCL Stage'] = dFCL_stage[dMstr[row]['FCL Doc Type']]


		# Vizzda extract info from Property Description & Notes
		if dMstr[row]['Source'] == 'VIZZDA':
			# Zoning
			txt = dMstr[row]['Zoning']
			pattern = re.compile(r'\bzoned\s+(\w+(?:-\w+)?)\b', re.IGNORECASE)
			match = re.search(pattern, txt)
			if match:
				# Extract the next word after 'zoned'
				dMstr[row]['Zoning'] = match.group(1)
			else:
				dMstr[row]['Zoning'] = ''
			
			# Convert datetime to string
			dMstr[row]['Last Sale Date'] = str(td.convert_datetime_to_readable(dMstr[row]['Last Sale Date'], separator='-'))
			dMstr[row]['Loan Date'] = str(td.convert_datetime_to_readable(dMstr[row]['Loan Date'], separator='-'))
			# print(dMstr[row]['Source'])
			# print(dMstr[row]['Loan Date'])
			# ui = '\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')

			# Loan Amount
			txt = dMstr[row]['Loan Amount']
			dMstr[row]['Loan Amount'] = parce_string(txt, dViz_patterns)
			# Loan Purpose
			txt = dMstr[row]['Loan Purpose'].upper()
			if 'CONSTRUCTION' in txt:
				dMstr[row]['Loan Purpose'] = 'CONSTRUCTION'
			elif 'SELLER-CARRIE' in txt or 'SELLER-CARRY' in txt:
				dMstr[row]['Loan Purpose'] = 'SELLER-CARRIED'
			else:
				dMstr[row]['Loan Purpose'] = 'PURCHASE MONEY'
			
			# Mail Street (address is in one field so split)
			mail_street = dMstr[row]['Mail Street']
			if mail_street != '':
				match = re.search(r' (\d{5})\b', mail_street)
				mail_street = mail_street[:match.end()]
				street, city, state, zipcode = td.parce_single_line_address(mail_street)
				dMstr[row]['Mail Street'] = street
				dMstr[row]['Mail City'] = city
				dMstr[row]['Mail State'] = state
				dMstr[row]['Mail Zip'] = zipcode
				
				# ui = '\n Continue [00]... > ')
				# if ui == '00':
				# 	exit('\n Terminating program...')


		# 'Loan Amount': {'PR': '1st Amount', 'RY': 'mortgage_amount', 'VZ': 'Notes'},
		# 'Loan Purpose': {'PR': '1st Purpose', 'RY': '', 'VZ': 'Notes'},

		# Convert currency to integer
		lFields = ['Loan Amount', 'Last Sale Amount']
		for fld in lFields:
			if dMstr[row][fld] != '':
				if dMstr[row]['Source'] == 'PROPERTY RADAR':
					dMstr[row][fld] = int(dMstr[row][fld])
				elif dMstr[row]['Source'] == 'REONOMY':
					strClean = dMstr[row][fld]
					strClean = strClean.replace('$', '')
					strClean = int(float(strClean))
					dMstr[row][fld] = int(strClean)
		
		# Convert sqft to acres
		if dMstr[row]['Acres'] == None:
			dMstr[row]['Acres'] = 0
		elif dMstr[row]['Source'] == 'PROPERTY RADAR':
			acres = dMstr[row]['Acres']
		elif dMstr[row]['Source'] == 'REONOMY':
			sqft = dMstr[row]['Acres']
			acres = float(sqft) / 43560
		if dMstr[row]['Source'] == 'VIZZDA':
			acres = dMstr[row]['Acres']
		dMstr[row]['Acres'] = float(acres)

	# Delete listed records from dMstr dict
	keys_to_remove = []
	for key in dMstr:
		if dMstr[key]['Loan Amount'] == 'no debt':
			keys_to_remove.append(key)
	for key in keys_to_remove:
		del dMstr[key]
		

	return dMstr

# Add AI processed Vizzda notes
def add_Vizzda_notes():
	print('\n Adding Vizzda Notes...')
	filename = 'F:/Research Department/MIMO/zData/Debt/Vizzda/dViz_master.csv'
	dV_notes = {}
	with open(filename, 'r') as f:
		fin = csv.reader(f)
		headers = next(fin)
		for row in fin:
			key = row[0]
			dV_notes[key] = dict(zip(headers, row))
	for key in dV_notes:
		for row in dMstr:
			if dMstr[row]['Source'] == 'VIZZDA':
				if dMstr[row]['Source ID'] == int(key):
					dMstr[row]['Lender'] = dV_notes[key]['Lender']
					dMstr[row]['Last Sale Date'] = dV_notes[key]['Loan Date']
					dMstr[row]['Loan Date'] = dV_notes[key]['Loan Date']
	return dMstr


td.banner('Debt Processor v02')

# Run the Python 3 AWS Script Arc_AWS_v01
# from os import system

# pyPath = 'C:/"Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" "F:/Research Department/Code/Research/Arc_AWS_v01.py"'
# os.system(pyPath)
# exit()
# Get dicts of Property Radar (PR) and Reonomy (RY) fields and keys
dDebt_fields, dDup_keys, dSources, dViz_patterns, dFCL_doc_type, dFCL_stage = dicts.get_debt_processor_dicts()
dMstr = {} # Master dict
debt_folder = 'F:/Research Department/MIMO/zData/Debt/'
today_date = td.today_date()

# Process data
ui = 'None'
for dSrc in dSources:
	if ui != '3':
		ui = '\n Process {0} [0/1/00/All[3]] > '.format(dSrc)
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1' or ui == '3' or ui == 'All':
		dMstr = process_raw_debt_data(dMstr, dSources[dSrc]['src'], dSources[dSrc]['data_type'],)

# Standarize fields in Master dictionary
print('\n Standardizing dMstr...')
dMstr = standardize_dMstr_fields(dMstr)

# # Add LAO markets
print('\n Loading shp file...')
shapefile_path = 'F:/Research Department/maps/LAO_Geo_1.shp'
gdf = gpd.read_file(shapefile_path)
dMstr = add_lao_market_to_dict()

# Add AI processed Notes from Vizzda
dMstr = add_Vizzda_notes()

# Combine duplicates
dMstr = combine_duplicates(dMstr, 'MSTR')

# Write to csv
ui = td.uInput('\n Write to csv [0/1/00] > ')
if ui == '00':
	exit('\n Terminating program...')
elif ui == '1':
	out_csv = f'{debt_folder}LAO Markets Debt {today_date}.csv'
	lao.dict_to_csv(dMstr, out_csv)

# Update Google Sheet
ui = td.uInput('\n Write to Google Sheet [0/1/00] > ')
if ui == '00':
	exit('\n Terminating program...')
elif ui == '1':
	update_gs()

exit(' Fin')

# # Select the worksheet by name or index. For example, by index:
# worksheet = spreadsheet.get_worksheet(0)  # 0 means the first worksheet

# # Update a single cell
# worksheet.update('A1', [['Hello, world!']])

# # Update multiple cells
# worksheet.update('A2:B2', [['Hello', 'world!']])

# worksheet.update('A3', [['Hello', 'world!']])