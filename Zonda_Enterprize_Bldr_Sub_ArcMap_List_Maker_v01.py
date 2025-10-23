# Creates a list of top builders for LAO markets for the MI and MO

import csv
import dicts
import lao
import fun_text_date as td
import os
import pandas as pd
from pprint import pprint

# FUNCTIONS #########################################################################################
# Change '' to 0 in Starts and Closings
def change_empty_to_zero(dData):
	for row in dData:
		if 'Projects' in fin:
			if dData[row]['Annual Starts'] == '':
				dData[row]['Annual Starts'] = 0
			if dData[row]['Annual Closings'] == '':
				dData[row]['Annual Closings'] = 0
		elif 'Subdivisions' in fin:
			if dData[row]['Annual Starts'] == '':
				dData[row]['Annual Starts'] = 0
			if dData[row]['Annual Closings'] == '':
				dData[row]['Annual Closings'] = 0
			if dData[row]['Vacant Developed Lots'] == '':
				dData[row]['Vacant Developed Lots'] = 0
			if dData[row]['VDL Months Of Supply'] == '':
				dData[row]['VDL Months Of Supply'] = 0
		else:
			print('Error: wrong data type in change_empty_to_zero function!')
			exit()

	return dData

# Make dict of total Starts and Closings for each builder
def make_dict_of_homebuilder_starts_closings(dProjects):
	# Create dict to aggregate builder metrics
	dHB = {}

	for row in dProjects:
		# Builder not in dict, add it
		if dProjects[row]['Builder'] not in dHB:
			dHB[dProjects[row]['Builder']] = {'Starts': int(dProjects[row]['Annual Starts']), 'Closings': int(dProjects[row]['Annual Closings'])}
		# Builder in dict, add to it
		else:
			dHB[dProjects[row]['Builder']]['Starts'] += int(dProjects[row]['Annual Starts'])
			dHB[dProjects[row]['Builder']]['Closings'] += int(dProjects[row]['Annual Closings'])

	return dHB

# Build list of top builders bu COE for csv
def build_list_of_top_builders_by_COE(dHB, market):
	lHB_by_coe = []
	for builder in dHB:
		lHB_by_coe.append([builder, dHB[builder]['Closings']])
	# Sort list by COE
	lHB_by_coe.sort(key=lambda x: x[1], reverse=True)
	# Retrun only the top 20 builders
	lHB_by_coe = lHB_by_coe[:30]
	return lHB_by_coe

# Build the csv file of top builders by COE for each market
def build_csv_of_top_builders_by_COE(dLAO_markets_hb, hb_top_csv_file):
	# List of markets to exclude
	excluded_markets = ['IEP', 'PHX', 'PRC', 'SAC', 'SEA', 'TUC']

	# Create a filtered dictionary excluding the specified markets
	filtered_markets_hb = {market: data for market, data in dLAO_markets_hb.items()
						if market not in excluded_markets}

	# Create a DataFrame from each market
	market_dfs = []
	for market, data in filtered_markets_hb.items():
		df = pd.DataFrame(data, columns=["Builder", "COE"])
		df.rename(columns={"Builder": f"[{market}] Builder", "COE": f"COE"}, inplace=True)
		market_dfs.append(df)

	# Concatenate the DataFrames side by side (align by row index)
	final_df = pd.concat(market_dfs, axis=1)

	# Save to CSV
	while 1:
		try:
			final_df.to_csv(hb_top_csv_file, index=False)
		except PermissionError:
			td.warningMsg('\n Close the file to continue...')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
		break

# Get top subdivisions ranked by Annual Starts, aggregating same-named subdivisions
def get_top_subdivisions_by_starts(dSubdivisions, list_type):

	# Create dict to aggregate subdivision metrics
	dSubdiv_totals = {}
	
	for row in dSubdivisions:
		# Add ArcMap fields if list_type is 'arcmap'
		if list_type == 'arcmap':
			subdivision = dSubdivisions[row]['Subdivision']
			annual_starts = int(dSubdivisions[row]['Annual Starts'])
			annual_closings = int(dSubdivisions[row]['Annual Closings'])
			product_type = dSubdivisions[row]['Product Style']
			lon = float(dSubdivisions[row]['Longitude'])
			lat = float(dSubdivisions[row]['Latitude'])
			invvdl = int(dSubdivisions[row]['Vacant Developed Lots'])
			invfut = int(dSubdivisions[row]['Future Lots'])
		# Add top subdivision fields if list_type is 'topsubs'
		elif list_type == 'topsubs':
			subdivision = dSubdivisions[row]['Community']
			annual_starts = int(dSubdivisions[row]['Annual Starts'])
			annual_closings = int(dSubdivisions[row]['Annual Closings'])
		
		if subdivision == '-N/C':
			continue
		# Skip if no starts
		if annual_starts == 0 and annual_closings == 0:
			continue
			
		# Add or update subdivision totals
		if subdivision in dSubdiv_totals:
			dSubdiv_totals[subdivision]['AnnStarts'] += annual_starts
			dSubdiv_totals[subdivision]['AnnClos'] += annual_closings
			# Update Arcmap totals if list_type is 'arcmap'
			if list_type == 'arcmap':
				dSubdiv_totals[subdivision]['InvVDL'] += invvdl
				dSubdiv_totals[subdivision]['InvFut'] += invfut
		else:
			if list_type == 'arcmap':
				dSubdiv_totals[subdivision] = {
					'Market': market,
					'ProdType': product_type,
					'Lon': lon,
					'Lat': lat,
					'AnnStarts': annual_starts,
					'AnnClos': annual_closings,
					'InvVDL': invvdl,
					'InvFut': invfut
				}
			elif list_type == 'topsubs':
				dSubdiv_totals[subdivision] = {
					'AnnStarts': annual_starts,
					'AnnClos': annual_closings
				}
	
	# Remove subdivisions with less than 3 starts or 3 closings
	dSubdiv_totals = {subdiv: metrics for subdiv, metrics in dSubdiv_totals.items() if metrics['AnnStarts'] >= 5 or metrics['AnnClos'] >= 5}

	# Convert to list for ArcMap csv
	if list_type == 'arcmap':
		lSubdivisions_for_arcmap = [
			[subdiv, metrics['Market'], metrics['ProdType'], metrics['Lon'], metrics['Lat'],  metrics['AnnStarts'], metrics['AnnClos'], metrics['InvVDL'], metrics['InvFut']]
			for subdiv, metrics in dSubdiv_totals.items()
		]
		return lSubdivisions_for_arcmap

		# Convert to list format for table
	elif list_type == 'topsubs':
		lSubdivisions = [
			[subdiv, metrics['AnnStarts'], metrics['AnnClos']]
			for subdiv, metrics in dSubdiv_totals.items()
		]
	
		# Sort by Annual Starts descending
		lSubdivisions.sort(key=lambda x: x[1], reverse=True)
		
		# Return top N
		return lSubdivisions[:30]

# Creates CSV with Annual Starts and Closings by subdivision for each market
def build_csv_of_subdivisions_by_starts(dLAO_markets_subs, subs_top_csv_file):
	# Create a DataFrame from each market
	market_dfs = []
	for market, data in dLAO_markets_subs.items():
		df = pd.DataFrame(data, columns=["Subdivision", "Starts", "Closings"])
		df.rename(columns={"Subdivision": f"[{market}] Subdivision", "Starts": f"Starts", "COE": f"COE"}, inplace=True)
		market_dfs.append(df)

	# Combine all market data
	final_df = pd.concat(market_dfs, axis=1)
	
	# Save to CSV
	while 1:
		try:
			final_df.to_csv(subs_top_csv_file, index=False)
			break
		except PermissionError:
			td.warningMsg('\n Close the file to continue...')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

# PROGRAM STARTS HERE ###############################################################################

td.banner('Zonda Enterprize Buldr Sub Arcmap List Maker v01')

# Get year and quarter
year_qtr = td.getDateQuarter()
# Get dict of homebuilder rename
hb_rename_file = '{0}BuilderRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
dHB_rename = dicts.spreadsheet_to_dict(hb_rename_file)
# Get dict of MPC rename
mpc_rename_file = '{0}MPCRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
dSubs_rename = lao.spreadsheetToDict(mpc_rename_file)
# CSV top buidlers by COE file name
hb_top_csv_file = r'C:\TEMP\homebuilders_by_market.csv'
# CSV top subdivisions by starts file name
subs_top_csv_file = r'C:\TEMP\subdivisions_by_market.csv'
# ArcMap subdivisions file name
sub_arcmap_filename = f'F:/Research Department/maps/Active Subs/Zonda_Active_Subs_{year_qtr}.csv'
# Get list of LAO markets
lMarkets = dicts.get_zonda_markets_list()
# Zonda paths
zonda_path = 'F:/Research Department/MIMO/zData/Zonda/MIMO/'
projects_table_name = f'Projects-Table {year_qtr}.csv'
subdivisions_table_name = f'Subdivisions-Table {year_qtr}.csv'
# LAO markets dictionary
dLAO_markets_hb = {}
dLAO_markets_subs = {}
# List of al subdivisions for ArcMap
lAll_subs_for_arcmap = []

# Top Subdivisions loop through markets
print(' Building Top Subdivisions by Annual Starts')
for market in lMarkets:

	# Input file name
	fin = f'{zonda_path}{market} {subdivisions_table_name}'
	# Check if the file exists
	if not os.path.exists(fin):
		td.warningMsg(f' Zonda Subdivision file for {market} does not exist!')
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		continue

	# Make dicts of subdivisions and rename dict
	dSubdivisions = dicts.spreadsheet_to_dict(fin)

	# Change '' to 0 in Starts and Closings
	dSubdivisions = change_empty_to_zero(dSubdivisions)

	# Get all subdivisions for ArcMap
	lSubdivisions_for_arcmap = get_top_subdivisions_by_starts(dSubdivisions, list_type='arcmap')
	# Add to all subdivisions for ArcMap list
	lAll_subs_for_arcmap.extend(lSubdivisions_for_arcmap)

	# Standarize/clean subdivision names
	dSubdivisions = td.standarize_hb_and_sub_names(fin, dSubdivisions, dSubs_rename, market)

	# Get top subdivisions ranked by Annual Starts
	lSubs_by_starts = get_top_subdivisions_by_starts(dSubdivisions, list_type='topsubs')
	# Add to market subdivision dict
	dLAO_markets_subs[market] = lSubs_by_starts
	
# MIMO SPREADSHEET: Build the csv file of top subdivisions by starts for each market
build_csv_of_subdivisions_by_starts(dLAO_markets_subs, subs_top_csv_file)
lao.openFile(subs_top_csv_file)
print("File 'subdivisions_by_market.csv' has been created!")

# ACRMAP: Build the csv file of all subdivisions for ArcMap
print('\n Building Top Homebuilders by Annual Closings')
with open(sub_arcmap_filename, 'w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['Market', 'SubName', 'ProdType', 'Lon', 'Lat', 'AnnStarts', 'AnnClos', 'InvVDL', 'InvFut'])
	writer.writerows(lAll_subs_for_arcmap)

lao.openFile(sub_arcmap_filename)

# Top Homebuilders loop through markets
print('\n Building Top Homebuilders by Annual Closings')
for market in lMarkets:
	# Input Zonda file name
	fin = f'{zonda_path}{market} {projects_table_name}'
	
	# Check if the file exists
	if not os.path.exists(fin):
		td.warningMsg(f' Zonda Project file for {market} does not exist!')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		continue

	# Make dicts of projects and rename dict
	dProjects = dicts.spreadsheet_to_dict(fin)
	
	# Standarize/clean homebuilder names
	dProjects = td.standarize_hb_and_sub_names(fin, dProjects, dHB_rename, market)

	# Change '' to 0 in Starts and Closings
	dProjects = change_empty_to_zero(dProjects)

	# Make dict of total Starts and Closings for each builder
	dHB = make_dict_of_homebuilder_starts_closings(dProjects)

	if market == 'HOU':
		with open('C:/TEMP/hb.csv', 'w', newline='') as f:
			fout = csv.writer(f)
			fout.writerow(['Builder', 'Annual Starts', 'Annual Closings'])
			for row in dHB:
				fout.writerow([row, dHB[row]['Starts'], dHB[row]['Closings']])
		lao.openFile('C:/TEMP/hb.csv')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

	# Build list of top builders by COE for csv
	lHB_by_coe = build_list_of_top_builders_by_COE(dHB, market)
	dLAO_markets_hb[market] = lHB_by_coe

# Build the csv file of top builders by COE for each market
build_csv_of_top_builders_by_COE(dLAO_markets_hb, hb_top_csv_file)

# Open the csv file
td.banner('Zonda Enterprize Buldr Sub Arcmap List Maker v01')
print(" File 'homebuilders_by_market.csv' has been created!")
lao.openFile(hb_top_csv_file)
exit('\n Fin')

	
	

	

