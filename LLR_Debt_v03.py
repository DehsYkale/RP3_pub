# Create Debt LLR

import bb
import csv
from datetime import datetime
import dicts
from glob import glob
import lao
import fun_login
import fun_text_date as td
import mpy
import os
import pandas as pd
from pprint import pprint
import xlwings as xw
import webs
import xxl

def tax_delinquent_processor():
	# Get the current date in the format YYYY-MM-DD
	current_date = datetime.now().strftime('%Y-%m-%d')
	
	# Initialize a list to hold dataframes
	dataframes = []
	
	# Loop through the files in the folder
	file_pattern = os.path.join(folder_tax_delinquent, '*TD*.csv')
	lTax_delinquent_files = glob(file_pattern)
	for file_name in lTax_delinquent_files:
		# Read each CSV file and append to the list
		df = pd.read_csv(file_name)
		dataframes.append(df)
	
	# Concatenate all dataframes
	combined_df = pd.concat(dataframes, ignore_index=True)

	# Remove all rows that start with The information contained
	combined_df = combined_df[~combined_df['APN'].str.startswith('The information contained')]
	# Convert the combined dataframe to a dictionary of dictionaries
	dTD = combined_df.to_dict(orient='index')

	# Cycle through the df and run the fuction mpy.get_LAO_geoinfo using the longitute and latitude
	dGDF = mpy.get_gpf_for_LAO_geoinfo(include_zip=False)
	# Create a list of the keys in the dTD dictionary
	lTD_keys = list(dTD[0].keys())
	# Add 3 values to lTD_keys
	lTD_keys.extend(['LAO Market', 'LAO Submarket', 'Map'])
	lTD = [lTD_keys]
	# lTD = []
	for row in dTD:
		# Get dLAO_geoinfo dictionary
		lat = dTD[row]['Latitude']
		lon = dTD[row]['Longitude']
		dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', dGDF=dGDF, lon=lon, lat=lat)

		# Create a list of values for each row
		lLine = []
		for key in lTD_keys:
			# Title case fields
			if key in ['City', 'County', 'Mail City']:
				txt = dTD[row][key].title()
				if txt == 'Unknown':
					txt = ''
				lLine.append(txt)
			# Lower case fields
			elif key == 'Email':
				txt = dTD[row][key].lower()
				lLine.append(txt)
			# Format Owner and 1st Orig Lender fields
			elif key in ['Owner', 'Primary Name', '1st Orig Lender']:
				txt = dTD[row][key]
				# Trap for float values
				if isinstance(txt, float):
					txt = ''
				else:
					txt = td.format_entity_names(txt)
				lLine.append(txt)
			# If Owner and Primary Name are the same, add a blank value for Primary Name
			elif key in ['Primary Name']:
				if dTD[row]['Owner'] == dTD[row]['Primary Name']:
					lLine.append('')
				else:
					txt = dTD[row][key]
					# Trap for float values
					if isinstance(txt, float):
						txt = ''
					else:
						txt = td.format_entity_names(txt)
					lLine.append(txt)
			# Add LAO_geoinfo values
			elif key == 'LAO Market':
				lLine.append(dLAO_geoinfo['market_full'])
			elif key == 'LAO Submarket':
				lLine.append(dLAO_geoinfo['submarket'])
			elif key == 'Map':
				map_link = ''
				if dLAO_geoinfo['l5_map'] != 'None':
					map_link = f'=HYPERLINK("{dLAO_geoinfo["l5_map"]}", "L5")'
				elif dLAO_geoinfo['google_map'] != 'None':
					map_link = f'=HYPERLINK("{dLAO_geoinfo["google_map"]}", "GM")'
				lLine.append(map_link)
			else:
				# # Remove float values
				if isinstance(dTD[row][key], float):
					txt = ''
					lLine.append(txt)
				else:
					lLine.append(dTD[row][key])
		lTD.append(lLine)

	# Write lFCL to csv
	output_file = f"LAO Markets Tax Delinquent {current_date}.csv"
	output_file = f'{folder_tax_delinquent}{output_file}'
	with open(output_file, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(lTD)

	return output_file


def foreclosure_processor():
	# Get Foreclosure Processor Dicts
	dGDF = mpy.get_gpf_for_LAO_geoinfo(include_zip=False)
	dFCL_fields, dFCL_doc_type, dFCL_stage = dicts.get_foreclosure_processor_dicts()
	dPR = dicts.spreadsheet_to_dict(f'{filename_pr}')
	dRY = dicts.spreadsheet_to_dict(f'{filename_ry}')
	lFCL_dicts = [dPR, dRY]
	lTitle_case = ['City', 'County', 'Mail City']


	# Create list of lists for dFCL_fields
	# Make a list of dFCL_fields keys for csv header
	lFCL_fields = []
	for key in dFCL_fields:
		lFCL_fields.append(key)
	lFCL = [lFCL_fields]
	# Make Google Sheet Foreclosure Properties list
	lFCL_fields_no_map = lFCL_fields
	del lFCL_fields_no_map[0]
	lFCL_no_map = [lFCL_fields_no_map]

	# Cycle through dPR and add to lFCL
	dict_processing = 'PR'
	for dict in lFCL_dicts:
		# print(dict_processing)
		# for row in dPR:
		for row in dict:
			# dict_row = dPR[row]
			dict_row = dict[row]
			# pprint(dict_row)
			if dict_processing == 'PR':
				# Get LAO market and submarket
				dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', dGDF=dGDF, lon=dict_row['Longitude'], lat=dict_row['Latitude'])
			elif dict_processing == 'RY':
				dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', dGDF=dGDF, lon=dict_row['longitude'], lat=dict_row['latitude'])
			
			lLine = []
			for l5_fld in lFCL_fields:
				# if l5_fld == 'Map':
				# 	break
				dict_fld = dFCL_fields[l5_fld][dict_processing]
				# Formatting for fields
				if dict_fld == 'None':
					lLine.append('')
				# Fields to be added
				# LAO Market
				elif dict_fld == 'LAO Market':
					lao_market = dLAO_geoinfo['market_full'].replace('None', '')
					lLine.append(lao_market)
				elif dict_fld == 'LAO Submarket':
					lLine.append(dLAO_geoinfo['submarket'].replace('None', ''))
				elif dict_fld == 'PropertyRadar':
					lLine.append('PropertyRadar')
				elif dict_fld == 'Reonomy':
					lLine.append('Reonomy')

				# Formatted fields #################################
				# Acres - Reonomy
				elif dict_processing == 'RY' and  l5_fld == 'Acres':
					acres = float(dict_row[dict_fld])/43560
					acres = round(acres, 2)
					lLine.append(acres)
				# Title case
				elif l5_fld in lTitle_case:
					txt = dict_row[dict_fld].title()
					lLine.append(txt)
				# Lower case
				elif l5_fld == 'Email':
					txt = dict_row[dict_fld].lower()
					lLine.append(txt)
				# Convert to string
				elif l5_fld == 'APN' or l5_fld == 'Zip':
					txt = str(dict_row[dict_fld])
					lLine.append(txt)
				# Entity names
				elif l5_fld == 'Owner Entity' or l5_fld == 'Lender':
					owner_entity = dict_row[dict_fld]
					txt = dict_row[dict_fld].title()
					txt = td.format_entity_names(txt)
					lLine.append(txt)
				# Owner Person is same as Owner Entity
				elif l5_fld == 'Owner Person':
					if dict_row[dict_fld] == owner_entity:
						lLine.append('')
					else:
						txt = dict_row[dict_fld].title()
						lLine.append(txt)
				# Street
				elif l5_fld == 'Mail Street':
					dAcc = {'STREET': dict_row[dict_fld]}
					dAcc = td.address_formatter(dAcc)
					lLine.append(dAcc['STREET'])
				# Format Property Radar doc type from abbreviation
				elif dict_processing == 'PR' and l5_fld == 'FCL Doc Type':
					lLine.append(dFCL_doc_type[dict_row[dict_fld]])
				elif dict_fld == 'flc_stage':
					stage = dict_row['preforeclosure_doc_type'].upper()
					lLine.append(dFCL_stage[stage])
				elif l5_fld == 'Map':
					map_link = ''
					if dLAO_geoinfo['l5_map'] != 'None':
						map_link = f'=HYPERLINK("{dLAO_geoinfo["l5_map"]}", "L5")'
					elif dLAO_geoinfo['google_map'] != 'None':
						map_link = f'=HYPERLINK("{dLAO_geoinfo["google_map"]}", "GM")'
					lLine.append(map_link)
				else:
					lLine.append(dict_row[dict_fld])
			lFCL.append(lLine)
			lLine_no_map = lLine
			# Remove the Map field for the Google Sheet Foreclosure Properties list
			del lLine_no_map[0]
			lFCL_no_map.append(lLine_no_map)
		dict_processing = 'RY'

	# Write lFCL to csv
	output_file = f'{path_fcl}TEMP US Foreclosures.csv'
	with open(output_file, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(lFCL)
	

	
	return path_fcl, lFCL_fields, lFCL_no_map

# START PROGRAM ##################################################
lao.banner('LLR Debt v03')
service = fun_login.TerraForce()
todaydate = td.today_date()

# Select foreclosure files
path_fcl = 'F:/Research Department/MIMO/zData/Debt/Foreclosure/'
# filename_pr = lao.guiFileOpen(path=path_fcl, titlestring='Open Property Radar File', extension=[('csv files', 'Property*.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])
# filename_ry = lao.guiFileOpen(path=path_fcl, titlestring='Open Reonomy Foreclosures File', extension=[('csv files', 'Reonomy*.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])
# Select Tax Delinquent file
# folder_tax_delinquent = 'F:/Research Department/MIMO/zData/Debt/Tax Delinquent/'
# file_name_td = lao.guiFileOpen(path=folder_tax_delinquent, titlestring='Open Tax Delinquent File', extension=[('csv files', 'LAO Markets Tax Delinquent*.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])
filename_pr = f'{path_fcl}Property Radar US Foreclosures 2024-10-11.csv'
filename_ry = f'{path_fcl}Reonomy US Foreclosures 2024-10-12_properties.csv'
# file_name_td = f'{folder_tax_delinquent}LAO Markets Tax Delinquent 2024-10-16.csv'

# TerraForce Query ##################################################
print('\n Querying TerraForce...')
fields = 'default'
wc = "Loan_Amount__c > 1 and Sale_Date__c > {0}".format('2019-01-01')
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=10, fields=fields)

lToExcelDebtList = []
print(msg := '\n Creating Debt List...')
for dLine in results:
	lLine = xxl.llr_debt_list_line_maker(dLine)
	lToExcelDebtList.append(lLine)

# Create Excel workbook #############################################
print('\n Creating Excel file...')
wb = xw.Book()

# Tax Delinquent Sheet ####################################################
print('\n Creating Tax Delinquent Sheet...')
folder_tax_delinquent = 'F:/Research Department/MIMO/zData/Debt/Tax Delinquent/'
file_name_td = tax_delinquent_processor()
header_tax_delinquent = dicts.get_tax_delinquent_header_list()
noCols_tax_delinquent_list = len(header_tax_delinquent)
# Create list of lists from the csv file
dTax_delinquent = dicts.spreadsheet_to_dict(f'{file_name_td}')
lTax_delinquent = []
for row in dTax_delinquent:
	lLine = xxl.llr_debt_tax_delinquent_line_maker(dTax_delinquent[row])
	lTax_delinquent.append(lLine)
	
noRows_tax_delinquwent_list = len(lTax_delinquent) + 2
sht = xw.main.sheets.add('Tax Delinquent')
sht.range('A1').value = 'Tax Delinquent - 1 Year PLus - LAO Markets'
df = pd.DataFrame(lTax_delinquent, columns=header_tax_delinquent)  # Convert list of lists to a dataframe
df = df.sort_values(by=['State', 'LAO Market']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.format_tax_delinquent_sheet(wb, sht, noRows_tax_delinquwent_list, noCols_tax_delinquent_list)

# Foreclosures Sheet ####################################################
print('\n Creating Foreclosures Sheet...')

path_fcl, header_foreclosure, lFCL_no_map = foreclosure_processor()
noCols_foreclosure_list = len(header_foreclosure)
dFCL = dicts.spreadsheet_to_dict(f'{path_fcl}TEMP US Foreclosures.csv')
lForeclosures = []
for row in dFCL:
	lLine = xxl.llr_debt_foreclosure_line_maker(dFCL[row])
	lForeclosures.append(lLine)

noRows_foreclosure_list = len(lForeclosures) + 2
sht = xw.main.sheets.add('Foreclosures')
sht.range('A1').value = 'US Land Foreclosures'
df = pd.DataFrame(lForeclosures, columns=header_foreclosure)  # Convert list of lists to a dataframe
df = df.sort_values(by=['State', 'LAO Market']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.format_foreclosure_sheet(wb, sht, noRows_foreclosure_list, noCols_foreclosure_list)
# Write lFCL_no_map to Google Sheet Foreclosure Properties
print('\n Updating Google Sheet...')
webs.update_gs(sheet_name='Foreclosure', lData=lFCL_no_map)

# Write Debt Sheet ##################################################
print('\n Creating Debt Sheet...')
outFilePath = 'F:/Research Department/Lot Comps Components/'
header_debt_list = dicts.get_debt_header_list()
noCols_debt_list= len(header_debt_list)
noRowsDebtList = len(lToExcelDebtList) + 2
sht = xw.main.sheets.add('Debt')
sht.range('A1').value = 'Debt LAO Markets'
df = pd.DataFrame(lToExcelDebtList, columns=header_debt_list)  # Convert list of lists to a dataframe
df = df.sort_values(by=['Market', 'LAO Deal']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.formatDebtListSheet(wb, sht, noRowsDebtList, noCols_debt_list)
lao.sleep(1)

# Remove Sheet1, save and close ####################################
sht1 = wb.sheets['Sheet1']
sht1.delete()
outFile = '{0}Debt_LAO_Markets_Land_Lot_Report_{1}.xlsx'.format(outFilePath, todaydate)
wb.save(outFile)
# wb.close()
lao.sleep(5)
exit('\n Fin')


