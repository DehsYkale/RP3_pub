#Python3

# Creates a spreadsheet of state and MSA change in employment using the BLS API for MIMO

import csv
import fun_text_date as td
import how
import lao
import json
import requests
from subprocess import Popen
from pprint import pprint

# Get state/msa seriesid list for api request and make a dict
#   of seriesid: MSA for reference printing
def get_market_seriesid():
	file_seriesid = 'F:/Research Department/Code/RP3/data/BLS_MSA_Employment_State_MSA_Series_IDs.xlsx'
	dSeriesID = lao.spreadsheetToDict(file_seriesid)
	lSeriesid_employed = []
	lSeriesid_unemployment_rate = []
	dSeriesid_employed = {}
	dSeriesid_unemployment_rate = {}
	for row in dSeriesID:
		state_msa = dSeriesID[row]['MSA']
		seriesid_employed = '{0}{1}'.format(dSeriesID[row]['GEOGRAPHY ID'], dSeriesID[row]['TOTAL EMPLOYED'])
		lSeriesid_employed.append(seriesid_employed)
		seriesid_unemployment_rate = '{0}{1}'.format(dSeriesID[row]['GEOGRAPHY ID'], dSeriesID[row]['UNEMPLOYMENT RATE'])
		lSeriesid_unemployment_rate.append(seriesid_unemployment_rate)
		
		dSeriesid_employed[seriesid_employed] = state_msa
		dSeriesid_unemployment_rate[seriesid_unemployment_rate] = state_msa
	
	dBig = {'State MSA': state_msa,
			'lEMPLOYED': lSeriesid_employed,
			'dEMPLOYED': dSeriesid_employed,
			'lUNEMP RATE': lSeriesid_unemployment_rate,
			'dUNEMP RATE': dSeriesid_unemployment_rate}
	
	return dBig

# Get data from BLS API
def get_bls_data(seriesid):
	lSeriesid = [seriesid]
	# Request the BLS api for employment data that returns json file
	headers = {'Content-type': 'application/json'}
	# data = json.dumps({"seriesid": lSeriesid,
	# 					"startyear":"2005", "endyear":"2024", 
	# 					"registrationkey":"2dcfec57a7104fa78745ed4eec9e07d4"})
	data = json.dumps({"seriesid": lSeriesid,
						"startyear":"2009", "endyear":"2025",
						"registrationkey":"ee8dfd59d30741419ad211bb958d539d"})
	p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
	json_data = json.loads(p.text)
	return json_data

# Print the BLS API resources for data and the seriesid
how.bls_data()

td.banner('MIMO BLS API Employment Assembler v02')
# Get the seriesid list and seriesid:msa dict
dBig = get_market_seriesid()
# pprint(dSeriesid_employed)
lMaster = []

# Determine if it is the 4th quarter
current_qtr = td.getDateQuarter()

if 'Q4' in current_qtr:
	is_4th_quarter = True
else:
	is_4th_quarter = False


for seriesid in dBig['lEMPLOYED']:
	# seriesid = 'LAUMT494162000000005'
	json_data = get_bls_data(seriesid)

	
	# print('here1')
	# pprint(json_data)
	# print(seriesid)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	

	# Loop through state and msa seriesid's
	for series in json_data['Results']['series']:
		lAnnual_employment = []
		seriesId = series['seriesID']
		# state_msa = dSeriesid_employed[seriesId]
		state_msa = dBig['dEMPLOYED'][seriesId]
		print(f'\nhere8 state_msa {state_msa}')
		if state_msa == 'Prescott':
			
			print('here10')
			pprint(series)
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			


		# Create dict of state/market total employed for each month 2005 to present
		dEmployed = {}
		for item in series['data']:
			year = item['year']
			period = item['period']
			year_period = f'{year}-{period}'
			persons_employed = item['value']

			if 'M01' <= period <= 'M12':
				dEmployed[year_period] = int(persons_employed)

		# pprint(dEmployed)

		# CALCULATE ANNUAL AVERAGE EMPLOYMENT ##############################################
		# Calculate annual aververage employment change for each year
		#   breaking at the last dict vaule and then calculationg last 12 months
		end_of_dict = False
		for year in range(2011, 2026):
			employment_change_sum = 0
			for month in range(1, 13):
				year_month_current = f'{year}-M{month:02}'
				year_month_last= f'{year-1}-M{month:02}'

				if year == 2020:
					if month == 12:
						employed_dec_2019 = dEmployed[year_month_current]

				# Check if current year month is a key in the dict
				#   If true add the difference from current year and last year to the
				#	change sum.  If false then assign year and month to the year end variables
				if year_month_current in dEmployed:
					employment_change_diff = dEmployed[year_month_current] - dEmployed[year_month_last]
					employment_change_sum = employment_change_sum + employment_change_diff
				# Create end of year/month variables and get total employed
				else:

					year_end_of_dict = year
					last_year_end_of_dict = year - 1
					month_end_of_dict = month - 1

					# Catch end of dict for 4th quarter
					if month_end_of_dict == 0:
						year_end_of_dict = year - 1
						last_year_end_of_dict = year - 2
						month_end_of_dict = 12
						
					end_of_dict = True
					print('here7 end of dict')
					print(f' year_end_of_dict: {year_end_of_dict}')
					print(f' last_year_end_of_dict: {last_year_end_of_dict}')
					print(f' month_end_of_dict: {month_end_of_dict}')

					year_month_current = f'{year_end_of_dict}-M{month_end_of_dict:02}'
					year_month_last = f'{last_year_end_of_dict}-M{month_end_of_dict:02}'
					print('here2')
					print(f' Cur: {year_month_current}   Last: {year_month_last}')

					total_employed_current_year = dEmployed[year_month_current]
					total_employed_last_year = dEmployed[year_month_last]

					break
			# Break at the end of the dict
			if end_of_dict:
				break

			# Calculate the last 12 month average
			lAnnual_employment.append(int(employment_change_sum / 12))

		if is_4th_quarter:
			print('here5 4th quarter')
			# Get the year. Since this runs in Jan subtract 1 from the year
			today_date = td.today_date()
			year = int(today_date[0:4]) - 1

			month_end_of_dict = 12
			year_end_of_dict = year
			last_year_end_of_dict = year - 1

			year_month_current = f'{year}-M12'
			year_month_last= f'{year-1}-M12'
			
			total_employed_current_year = dEmployed[year_month_current]
			total_employed_last_year = dEmployed[year_month_last]
		
		# CALCULATE LAST 12 MONTHS #########################################################
		# If end_of_dict is true calculate the last 12 months
		# 	otherwise it will skip this loop for 4th quarter data
		if end_of_dict:

			month_count = month_end_of_dict
			employment_change_sum = 0
			last_employment_change_sum = 0
			percentage_change_yoy_sum = 0
			while 1:
				# Sum change in employment for current year last 12 months
				year_month_current = f'{year_end_of_dict}-M{month_count:02}'
				year_month_last= f'{year_end_of_dict - 1}-M{month_count:02}'
				employment_change_diff = dEmployed[year_month_current] - dEmployed[year_month_last]
				employment_change_sum = employment_change_sum + employment_change_diff

				# Sum change in employment for the previous year last 12 months
				last_year_month_current = f'{last_year_end_of_dict}-M{month_count:02}'
				last_year_month_last= f'{last_year_end_of_dict - 1}-M{month_count:02}'
				last_employment_change_diff = dEmployed[last_year_month_current] - dEmployed[last_year_month_last]
				last_employment_change_sum = last_employment_change_sum + last_employment_change_diff

				# Sum percentage change YoY for every month over the last 12 months
				pct_change = (float(dEmployed[year_month_current]) - float(dEmployed[year_month_last])) / float(dEmployed[year_month_last])
				percentage_change_yoy_sum = percentage_change_yoy_sum + pct_change
				# print(percentage_change_yoy_sum)

				month_count -= 1
				# Change month to 12 (Dec) and year to privious year
				if month_count == 0:
					# Break if 4th quarter month = 12
					if month_end_of_dict == 12:
						break
					month_count = 12
					year_end_of_dict = year_end_of_dict - 1
					last_year_end_of_dict = last_year_end_of_dict - 1
				# End loop when the month_count value equals the month_end_of_dict value
				elif month_count == month_end_of_dict:
					break

			# Add average annual employment current and last to list
			current_employment_change_average = int(employment_change_sum / 12)
			last_employment_change_average = int(last_employment_change_sum / 12)
			# percent_change_current_year_last_year = ((current_employment_change_average - last_employment_change_average) / last_employment_change_average) * 100
			percent_change_current_year_last_year = (percentage_change_yoy_sum / 12) * 100
			percent_change_current_year_last_year = str(round(percent_change_current_year_last_year, 2))
			
			
			lAnnual_employment.append(current_employment_change_average)
			lAnnual_employment.append(percent_change_current_year_last_year)

			print(state_msa)
			print(f' current_employment_change_average:     {current_employment_change_average}')
			print(f' last_employment_change_average:        {last_employment_change_average}')
			print(f' percent_change_current_year_last_year: {percent_change_current_year_last_year}')

		else:
			month_end_of_dict = 12
			year_end_of_dict = year
			last_year_end_of_dict = year - 1

		# UNEMPLOYMENT RATE ###############################################################
		# Get unemployment rate for this year and last year
		dic = dBig['dUNEMP RATE']
		for key, value in dic.items():
			if state_msa == value:
				seriesid_unemployment_rate = key
				break
		
		json_data = get_bls_data(seriesid_unemployment_rate)
		dic = json_data['Results']['series'][0]['data']

		
		# print('here6')
		# pprint(dic)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		

		month = f'M{month_end_of_dict:02}'

		if month == 'M12':
			year_end_of_dict = year
			last_year_end_of_dict = year - 1
		else:
			year_end_of_dict += 1
			last_year_end_of_dict += 1

		for row in dic:

			
			# print('here3')
			# pprint(row)
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
			

			if row['year'] == str(year_end_of_dict) and row['period'] == f'M{month_end_of_dict:02}':
				unemployment_rate_current = row['value']
			elif row['year'] == str(last_year_end_of_dict) and row['period'] == f'M{month_end_of_dict:02}':
				unemployment_rate_last_year = row['value']
		
		# Add unemployment to list
		lAnnual_employment.append(unemployment_rate_last_year)
		lAnnual_employment.append(unemployment_rate_current)
		# Add total employment to list
		lAnnual_employment.append(total_employed_last_year)
		lAnnual_employment.append(total_employed_current_year)
		# Add Dec 2019 Employment
		lAnnual_employment.append(employed_dec_2019)
		

		print(f' unemployment_rate_last_year: {unemployment_rate_last_year}')
		print(f' unemployment_rate_current: {unemployment_rate_current}')
		print(f' total_employed_last_year: {total_employed_last_year}')
		print(f' unemployment_rate_total_employed_current_yearlast_year: {total_employed_current_year}')
		print(f' employed_dec_2019:{employed_dec_2019}')

		# Add
		# exit(' Exit')
		# Add lAnnual employment data to master list of dicts
		lMaster.append({state_msa: lAnnual_employment})

# pprint(lMaster)
# exit(' Exit')

# Write resutls to csv file
with open('C:/TEMP/MSA_Employment_Change.csv', 'w', newline='') as g:
	fout = csv.writer(g)
	header = ['State-MSA']       # row 0-1
	for i in range(2011, 2026):     # row 2-15
		header.append(str(i))
	# header.append('Last 12 Mo')     # row 16
	header.append('Annualized Monthly Pct Chg Emp Growth Loss')       # row 17
	header.append('Unemp Rate Last Yr')  # row 18
	header.append('Unemp Rate Current')  # row 19
	header.append('Total Emplyd Last Yr') # row 20
	header.append('Total Emplyd Current') # row 21
	header.append('Emplyd Dec 2019') # row 21
	fout.writerow(header)

	for row in lMaster:
		state_msa = list(row.keys())[0]
		lout = [state_msa]
		lout.extend(row[state_msa])
		fout.writerow(lout)
		# Instert total line for Greenville & Spartanburg
		if state_msa == 'Spartanburg' or state_msa == 'Yuma':
			fout.writerow([''])
	
p = Popen('C:/TEMP/MSA_Employment_Change.csv', shell=True)

exit(' Exit...')