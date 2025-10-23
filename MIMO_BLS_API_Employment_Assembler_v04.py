
import csv
from dotenv import load_dotenv
from os import system
import os
import dicts
import fun_staff as fstf
import fun_text_date as td
import json
import lao
from pprint import pprint
import requests

# Load environment variables from a .env file
load_dotenv()

# Get latest year-mo# by querying BLS API
def get_current_yr_mo():
	lSeriesid = ['LAUMT064014000000003']
		# Request the BLS api for employment data that returns json file
	headers = {'Content-type': 'application/json'}
	BLS_API_REGISTRATION_KEY = os.getenv("BLS_API_REGISTRATION_KEY")
	data = json.dumps({"seriesid": lSeriesid,
						"startyear":"2024", "endyear":"2040",
						"registrationkey": BLS_API_REGISTRATION_KEY})
	p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
	dGet_yr_mo = json.loads(p.text)
	for series in dGet_yr_mo['Results']['series']:

		for item in series['data']:
			cur_year = item['year']
			strCur_month = item['period']
			iCur_month = int(item['period'][1:])
			break  # Exit after first item to get the latest year and month
		break
	strLast_year = str(int(cur_year) - 1)
	strTwo_years_ago = str(int(cur_year) - 2)
	return cur_year, strCur_month , iCur_month, strLast_year, strTwo_years_ago  # Return year and month as strings and integer

# Get data from BLS API``
def get_bls_unemployment_rate_data(area_id):
	# Check if area is a state
	print(f'Area ID: {area_id}')
	print(f'Area ID (without last 4 chars): {area_id[-5:]}')
	if area_id[-5:] == '00000':
		seriesid = f"LASST{area_id}00000003"
	else:
		seriesid = f"LAUMT{area_id}00000003"
	lSeriesid = [seriesid]
		# Request the BLS api for employment data that returns json file
	headers = {'Content-type': 'application/json'}
	BLS_API_REGISTRATION_KEY = os.getenv("BLS_API_REGISTRATION_KEY")
	data = json.dumps({"seriesid": lSeriesid,
						"startyear":"2023", "endyear":"2025",
						"registrationkey": BLS_API_REGISTRATION_KEY})
	p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
	json_data = json.loads(p.text)
	return json_data

def get_bls_total_employment_data(area_id):
	# SM: State and Area Employment, Hours, and Earnings
	# U: Not Seasonally Adjusted (S: Seasonally Adjusted)
	# Super Sector: 00 (Total Nonfarm)
	# Industry: 000000 (Total Nonfarm)
	# Data Type: 01 (All Employees, in Thousands)
	BLS_API_REGISTRATION_KEY = os.getenv("BLS_API_REGISTRATION_KEY")
	seriesid = f"SMU{area_id}0000000001"
	lSeriesid = [seriesid]
	# Request the BLS api for employment data that returns json file
	headers = {'Content-type': 'application/json'}
	data = json.dumps({"seriesid": lSeriesid,
					"startyear":"2007", "endyear":"2025",
					"registrationkey": BLS_API_REGISTRATION_KEY})
	p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
	json_data = json.loads(p.text)
	return json_data

# Determine the state from the first 2 digits of area ID
def get_state_name_from_fips(area, dFIPS):
	
	dStateFIPS = dicts.get_state_2_digit_fips_dict()
	state_fips = dFIPS[area][:2]
	for key, value in dStateFIPS.items():
		if value == state_fips:
			return key
	print(' State not found for area:', area)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	return None

# Calculate employment data for each for area for each year through last year
def calc_avg_annual_employment_change(lSingle_area):
	for year in range(2008, int(cur_year)):
		yr_last = year - 1
		sum_emp_change = 0

		# Cycle through each month of the year and total the employment change for the year
		for mo in range(1, 13):
			str_month = f'M{mo:02d}'
			key_yr_mo_last = f"{yr_last}-{str_month}"
			key_yr_mo_current = f"{year}-{str_month}"
			# Sum the employment change for each month
			sum_emp_change = (dCalc[key_yr_mo_current] - dCalc[key_yr_mo_last]) + sum_emp_change

			# Print to check the math
			# print(f'Year: {year}, Month: {str_month}, Employment Current: {dCalc[key_yr_mo_current]}, Employment Last: {dCalc[key_yr_mo_last]}, Change: {dCalc[key_yr_mo_current] - dCalc[key_yr_mo_last]}')

		# Calculate the average monthly employment change for the year
		avg_emp_change = int(float(sum_emp_change / 12))
		# Print to check the math
		# print(f'Year: {year}, Sum Change: {sum_emp_change}')
		print(f'Year: {year}, Avg. Monthly Employment Change: {avg_emp_change}')

		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		lSingle_area.append(avg_emp_change)

	return lSingle_area

# Calulate the last 12 months of employment change
def calc_avg_annual_employment_change_for_last_12_months(lSingle_area):
	
	sum_emp_change = 0
	rolling_month = iCur_month
	rolling_year = int(cur_year)
	rolling_year_last = int(cur_year) - 1
	while 1:
		str_month = f'M{rolling_month:02d}'
		key_yr_mo_current = f"{rolling_year}-{str_month}"
		key_yr_mo_last = f"{rolling_year_last}-{str_month}"
		# Sum employment
		sum_emp_change = (dCalc[key_yr_mo_current] - dCalc[key_yr_mo_last]) + sum_emp_change

		# If month is 01 (January), roll back to December of previous year
		rolling_month -= 1
		if rolling_month == 0:
			rolling_month = 12
			rolling_year -= 1
		# If rolling month equals current month, break the loop
		elif rolling_month == iCur_month:
			break

	# Calculate the average monthly employment change for the last 12 months
	percent_avg_emp_change = int(float(sum_emp_change / 12))
	print(f'Last 12 Months Avg. Monthly Employment Change: {percent_avg_emp_change}')
	lSingle_area.append(percent_avg_emp_change)
	return lSingle_area

# Calulate the last 12 months of employment change
def calc_percentage_change_in_annual_employment_for_last_12_months(lSingle_area):
	
	sum_pct_change = 0
	rolling_month = iCur_month
	rolling_year = int(cur_year)
	rolling_year_last = int(cur_year) - 1

	while 1:
		str_month = f'M{rolling_month:02d}'
		key_yr_mo_current = f"{rolling_year}-{str_month}"
		key_yr_mo_last = f"{rolling_year_last}-{str_month}"
		# Calculate the percentage change in employment for the last 12 months
		cur_value = dCalc[key_yr_mo_current]
		last_value = dCalc[key_yr_mo_last]
		pct_change = (((cur_value - last_value) / last_value) * 100)
		sum_pct_change = sum_pct_change + pct_change

		# If month is 01 (January), roll back to December of previous year
		rolling_month -= 1
		if rolling_month == 0:
			rolling_month = 12
			rolling_year -= 1
			rolling_year_last -= 1
		# If rolling month equals current month, break the loop
		elif rolling_month == iCur_month:
			break

	# Calculate the average monthly employment change for the last 12 months
	avg_pct_change = float(sum_pct_change / 12)
	print(f'Sum Pct Change: {sum_pct_change:.1f}%')
	print(f'Last 12 Months Avg. Monthly Employment Change: {avg_pct_change:.1f}%')
	# Add the average percentage change to the output list
	lSingle_area.append(f'{avg_pct_change:.1f}')
	return lSingle_area

td.banner('MIMO BLS API Employment Assembler v04')

# Assign various dictionaries, variables, and lists
dFIPS = dicts.get_state_cbsa_fips_dict()
lAreas = dicts.get_lao_employment_data_area_markets_list()
cur_year, strCur_month , iCur_month, strLast_year, strTwo_years_ago = get_current_yr_mo()
lOutput = [['']]
BLS_API_REGISTRATION_KEY = os.getenv("BLS_API_REGISTRATION_KEY")


lOutput = [['State', 'Area', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', 'Last12Mo', 'Annualized Monthly Pct Chg Emp Growth Loss', 'Unemp Rate Last Year', 'Unemp Rate Current', 'Total Emplyd Last Yr', 'Total Emplyd Current Yr']]

print(f'Current Year: {cur_year}, Current Month: {iCur_month}')

# Limit the number of areas to process
limit_counter = 0
for area in lAreas:

	# Determine the state from the first 2 digits of area ID
	state_name = get_state_name_from_fips(area, dFIPS)
	print(f'\nState: {state_name}')
	print(f'Area:  {area}')

	# Get nonfarm employment data
	dTotal_nonfarm_emp = get_bls_total_employment_data(dFIPS[area])
	for series in dTotal_nonfarm_emp['Results']['series']:
		
		seriesId = series['seriesID']
		print(f'Series ID: {seriesId}')
		print(f'State: {state_name}')
		print(f'Area:   {area}')
		print('Monthly Total Employment Data:')

		# Populate dCalc total nonfarm employment for each month
		dCalc = {}
		for item in series['data']:
			yr_period = f"{item['year']}-{item['period']}"
			dCalc[yr_period] = int(float(item['value']) * 1000)  # Convert to total employment

		##################################################################
		# Calculate year-over-year change for each year 2008 to last year
		# lSingle_area is a list of employment values for the area
		lSingle_area = [state_name, area]
		lSingle_area = calc_avg_annual_employment_change(lSingle_area)
		
		
		##################################################################
		# Calulate the last 12 months of employment change
		lSingle_area = calc_avg_annual_employment_change_for_last_12_months(lSingle_area)

		##############################################################
		# Calulate the last 12 months percentage employment change
		# Annualized Monthly Pct Chg Emp Growth Loss
		lSingle_area = calc_percentage_change_in_annual_employment_for_last_12_months(lSingle_area)


	##################################################################
	# Get the unemployment rate data
	dUnemp_rate = get_bls_unemployment_rate_data(dFIPS[area])
	for series in dUnemp_rate['Results']['series']:
		seriesId = series['seriesID']
		print('Monthly Unemployment Rate Data:')
		for item in series['data']:
			if item['year'] == cur_year and item['period'] == strCur_month:
				print(f"  Year: {item['year']}, Month: {item['period']}, Value: {item['value']}%")
				# Add the unemployment rate to the output list
				unemp_rate_current = item['value']
			elif item['year'] == strLast_year and item['period'] == strCur_month:
				print(f"  Year: {item['year']}, Month: {item['period']}, Value: {item['value']}%")
				unemp_rate_last_year = item['value']


		lSingle_area.append(unemp_rate_last_year)
		lSingle_area.append(unemp_rate_current)

	##################################################################
	# Get total employment for the current & last year and current month
	yr_last = int(cur_year) - 1
	last_year_current_month = f'{yr_last}-M{iCur_month:02d}'
	current_year_current_month = f'{cur_year}-M{iCur_month:02d}'
	last_year_month_total_employment = dCalc[last_year_current_month]
	current_year_month_total_employment = dCalc[current_year_current_month]
	lSingle_area.append(last_year_month_total_employment)
	lSingle_area.append(current_year_month_total_employment)

	lOutput.append(lSingle_area)
	
	if limit_counter == 100:
		print('\n\n Limit of 100 areas reached, exiting...')
		break
	limit_counter += 1
	
	# print('here3')
	# pprint(lOutput)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

# Write output to csv file
with open(r'C:\TEMP\M1 Employment Data.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	for row in lOutput:
		fout.writerow(row)
		# Write blank line after Spartansburg, SC and Salt Lake City, UT
		if row[1] == 'Spartanburg' or row[1] == 'Salt Lake City-Murray':
			fout.writerow([])

lao.openFile(r'C:\TEMP\M1 Employment Data.csv')