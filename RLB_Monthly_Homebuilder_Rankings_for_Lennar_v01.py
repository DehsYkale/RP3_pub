# Creates the Lennar Monthly Homebuilder Rankings

from datetime import datetime, timedelta
import fun_text_date as td
import lao
from os import startfile
import pandas as pd
from pprint import pprint


# Get date variables
def get_date_variables():
	# Get reference date (December 2024)
	current_date = td.get_last_day_of_previous_month()
	one_year_ago = current_date - timedelta(days=365)
	two_years_ago = current_date - timedelta(days=730)
	curr_ytd_start = datetime(current_date.year, 1, 1)
	prev_ytd_start = datetime(current_date.year - 1, 1, 1)
	prev_ytd_end = datetime(current_date.year - 1, current_date.month, current_date.day)
	# Get month name and year for column headers
	month_name = current_date.strftime("%b")
	year = current_date.year

	# print('here2')
	# print(f'current_date: {current_date}')
	# print(f'one_year_ago: {one_year_ago}')
	# print(f'two_years_ago: {two_years_ago}')
	# print(f'curr_ytd_start: {curr_ytd_start}')
	# print(f'prev_ytd_start: {prev_ytd_start}')
	# print(f'prev_ytd_end: {prev_ytd_end}')
	# print(f'month_name: {month_name}')
	# print(f'year: {year}')
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	return current_date, one_year_ago, two_years_ago, curr_ytd_start, prev_ytd_start, prev_ytd_end, month_name, year

# Get data frames
def get_data_frames():
	# Read the CSV files
	df_permits = pd.read_csv(permits_file)
	df_coe = pd.read_csv(coe_file)
	
	# Convert date columns to datetime 
	df_permits['PERMIT_DAT'] = pd.to_datetime(df_permits['PERMIT_DAT'])
	df_coe['DATE'] = pd.to_datetime(df_coe['DATE'])

	return df_permits, df_coe

# Get permit and COE totals
def get_permit_coe_totals(df_permits, df_coe):

	# Calculate total permits (including Misc Custom) for totals row
	total_prev_12mo_permits = len(df_permits[
		(df_permits['PERMIT_DAT'] >= prev_ytd_start) & 
		(df_permits['PERMIT_DAT'] <= prev_ytd_end) &
		(df_permits['COUNTY'] != 'PIMA')  # Still exclude PIMA
	])
	
	total_curr_12mo_permits = len(df_permits[
		(df_permits['PERMIT_DAT'] >= one_year_ago) &
		(df_permits['COUNTY'] != 'PIMA')  # Still exclude PIMA
	])
	
	total_growth = round(((total_curr_12mo_permits - total_prev_12mo_permits) / total_prev_12mo_permits * 100), 1)
	
	# Calculate totals
	# Calculate total YTD Permits and COE using totals including Misc Custom
	total_curr_ytd_starts = len(df_permits[
		(df_permits['PERMIT_DAT'] >= curr_ytd_start) & 
		(df_permits['PERMIT_DAT'] <= current_date) &
		(df_permits['COUNTY'] != 'PIMA')  # Still exclude PIMA
	])

	# Calculate total YTD Permits and COE using totals including Misc Custom
	total_12mo_coe = len(df_coe[
		(df_coe['DATE'] >= one_year_ago) &
		(df_coe['COUNTY'] != 'PIMA')  # Still exclude PIMA
	])

	# Ask user if they would like to use HBACA data totals
	while 1:
		td.banner('RLB Monthly Homebuilder Rankings for Lennar v01')
		ui = td.uInput('\n Use HBACA data for 12 month permit totals? [0/1/00] > ')
		if ui == '1':
			td.instrMsg('\n HBACA data is in the Phx MO xlsx file.\n    Opening folder in Windows File Explorer...')
			startfile(r'F:\Research Department\MIMO\Spreadsheets\Phoenix')
			ui_prev = td.uInput(f'\n Enter 12 Mo total permits for Last Year [00]> ')
			if ui_prev == '00':
				td.warningMsg('\n Using RBL permits.')
				ui = td.uInput('\n Continue [00]... > ')
				if ui == '00':
					exit('\n Terminating program...')
			else:
				ui_curr = td.uInput(f'\n Enter 12 Mo total permits for the Current Year [00]> ')
				if ui_curr == '00':
					td.warningMsg('\n Using RBL permits.')
					ui = td.uInput('\n Continue [00]... > ')
					if ui == '00':
						exit('\n Terminating program...')
				else:
					ui_ytd_curr = td.uInput(f'\n Enter YTD permits for the Current Year [00]> ')
					if ui_curr == '00':
						td.warningMsg('\n Using RBL permits.')
						ui = td.uInput('\n Continue [00]... > ')
						if ui == '00':
							exit('\n Terminating program...')
					else:
						total_prev_12mo_permits = int(ui_prev.replace(',', ''))
						total_curr_12mo_permits = int(ui_curr.replace(',', ''))
						total_curr_ytd_starts = int(ui_ytd_curr.replace(',', ''))
						break
		elif ui == '0':
			pass
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...using RBL permits.')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')



	# Print totals
	td.colorText(f' total prev year permits: {total_prev_12mo_permits}', 'GREEN')
	td.colorText(f' total curr year permits: {total_curr_12mo_permits}', 'GREEN')
	td.colorText(f' total ser_growth: {total_growth}', 'GREEN')
	print(f'\n total_12mo_coe: {total_12mo_coe}')

	return total_curr_ytd_starts, total_12mo_coe

def filter_permits_coe(df_permits, df_coe):
	# Now filter out Misc Custom for builder rankings
	df_permits = df_permits[
		(df_permits['BUILDER'] != 'Misc Custom') & 
		(df_permits['COUNTY'] != 'PIMA')
	]
	df_coe = df_coe[
		(df_coe['BUILDER'] != 'Misc Custom') & 
		(df_coe['COUNTY'] != 'PIMA')
	]
	return df_permits, df_coe

def create_builder_rankings(df_permits, df_coe):

	# Calculate last 12 months permits by builder
	ser_current_12_mo_permits = df_permits[
		df_permits['PERMIT_DAT'] >= one_year_ago
	].groupby('BUILDER').size()
	
	# Calculate YTD permits by builder (i.e. Jan 1 2024 to Dec 31 2024)
	ser_ytd_permits = df_permits[
		(df_permits['PERMIT_DAT'] >= curr_ytd_start) & 
		(df_permits['PERMIT_DAT'] <= current_date)
	].groupby('BUILDER').size()
	
	# Calculate last 12 months closings by builder
	ser_l12m_closings = df_coe[
		df_coe['DATE'] >= one_year_ago
	].groupby('BUILDER').size()
	
	# Calculate previous year's permits for YOY growth (Jan 1 2023 to Dec 31 2023)
	# .size() returns a Series with the number of permits for each builder
	ser_prev_12_mo_permits = df_permits[
		(df_permits['PERMIT_DAT'] >= two_years_ago) & 
		(df_permits['PERMIT_DAT'] <= one_year_ago)
	].groupby('BUILDER').size()
	
	# Create final dataframe with dynamic column names
	df_hb_rankings = pd.DataFrame({
		'Last 12 Mo Housing Starts': ser_current_12_mo_permits,
		f'YTD Starts {month_name} {year}': ser_ytd_permits,
		'Last 12 Mo Closings': ser_l12m_closings
	})
	
	# Fill NaN values with 0
	df_hb_rankings = df_hb_rankings.fillna(0)
	
	# Calculate market shares of YTD Starts
	df_hb_rankings[f'Share of YTD Starts {month_name} {year}'] = (df_hb_rankings[f'YTD Starts {month_name} {year}'] / total_curr_ytd_starts * 100).round(1).astype(str) + '%'

	# Calculate market shares of L12M Closings
	df_hb_rankings['Share of Closings'] = (df_hb_rankings['Last 12 Mo Closings'] / total_12mo_coe * 100).round(1).astype(str) + '%'
	
	# Calculate YOY growth in permits/starts
	# First align the data
	ser_prev_12_mo_permits = ser_prev_12_mo_permits.reindex(df_hb_rankings.index).fillna(0)
	current_permits = df_hb_rankings['Last 12 Mo Housing Starts']
	
	# Calculate YTD growth rate of each builder
	ser_growth = pd.Series(index=df_hb_rankings.index)
	for builder in df_hb_rankings.index:
		prev = ser_prev_12_mo_permits[builder]
		curr = current_permits[builder]

		# print('here1')
		# print(f'builder: {builder} prev: {prev} curr: {curr}')
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		if prev == 0:
			ser_growth[builder] = float('inf') if curr > 0 else 0
		else:
			ser_growth[builder] = ((curr - prev) / prev)
	
	# Add growth calculation to dataframe as new column
	df_hb_rankings['YOY Starts Growth'] = ser_growth
	df_hb_rankings['YOY Starts Growth'] = (df_hb_rankings['YOY Starts Growth'] * 100).round(1).astype(str) + '%'
	
	# Sort by Last 12 Mo Housing Starts and keep only top 10
	df_hb_rankings = df_hb_rankings.sort_values('Last 12 Mo Housing Starts', ascending=False)
	df_hb_rankings = df_hb_rankings.head(10)
	df_hb_rankings.insert(0, 'Rank', range(1, 11))
	
	# Format numbers as strings with commas, handling NaN values
	def format_number(x):
		if pd.isna(x) or x == 0:
			return "0"
		return f"{int(x):,}"
	
	df_hb_rankings['Last 12 Mo Housing Starts'] = df_hb_rankings['Last 12 Mo Housing Starts'].apply(format_number)
	df_hb_rankings[f'YTD Starts {month_name} {year}'] = df_hb_rankings[f'YTD Starts {month_name} {year}'].apply(format_number)
	df_hb_rankings['Last 12 Mo Closings'] = df_hb_rankings['Last 12 Mo Closings'].apply(format_number)
	
	return df_hb_rankings

# Reorder Columns
def reorder_columns(rankings):
	rankings = rankings.reindex(columns=[
	'Last 12 Mo Housing Starts',
	f'YTD Starts {month_name} {year}',
	f'Share of YTD Starts {month_name} {year}',
	'YOY Starts Growth',
	'Last 12 Mo Closings',
	'Share of Closings'
])
	return rankings
	
# Usage
if __name__ == "__main__":

	td.banner('RLB Monthly Homebuilder Rankings for Lennar v01')
	# Set file paths
	rlb_folder = lao.getPath('rlb')
	permits_file = f"{rlb_folder}RLB Permits Master Database.csv"
	coe_file = f"{rlb_folder}RLB COE Master Database.csv"
	
	# Get date variables
	current_date, one_year_ago, two_years_ago, curr_ytd_start, prev_ytd_start, prev_ytd_end, month_name, year = get_date_variables()

	# Get data frames
	df_permits, df_coe = get_data_frames()

	# Get permit and COE totals (do first before filtering out Misc Custom builders)
	total_curr_ytd_starts, total_12mo_coe = get_permit_coe_totals(df_permits, df_coe)

	# Filter out Misc Custom for builder rankings
	df_permits, df_coe = filter_permits_coe(df_permits, df_coe)

	# Create builder rankings
	rankings = create_builder_rankings(df_permits, df_coe)
	
	# Reorder columns
	rankings = reorder_columns(rankings)

	# Export to CSV
	output_file = r"C:\TEMP\Builder_Rankings.csv"
	hb_ranking_file = r"F:\Research Department\Projects\Advisors and Markets\Ryan Semro\Homebuilder Ranking by Starts for Lennar.xlsx"
	while 1:
		try:
			rankings.to_csv(output_file, index=True, index_label='Builder')
			break
		except PermissionError:
				td.warningMsg('\n The file is open...close it and press [Enter] or [00]')
				ui = td.uInput('\n  > ')
				if ui == '00':
					exit('\n Terminating program...')
	print(f"\n Rankings have been saved to: {output_file}")
	
	# Open the files
	lao.openFile(hb_ranking_file)
	lao.openFile(output_file)