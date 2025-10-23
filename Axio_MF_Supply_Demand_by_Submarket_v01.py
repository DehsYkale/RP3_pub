# Create Supply Demand by Submarket

import lao
import bb
import csv
import dicts
import how
from pprint import pprint
import datetime
from glob import glob
import fun_text_date as td

td.banner('Axio MF Supply Demand by Submarket v01')
pathAxio = lao.getPath('axio')
filename = f'{pathAxio}AnnualMarketPerformance_PhoenixMesaScottsdaleAZ 2024Q2.xlsx'
dTemp = dicts.spreadsheet_to_dict(filename)
year = '2024'

# Create list of submarkets
lSubmarkets = []
for row in dTemp:
	r = dTemp[row]
	if r['Submarket'] == 'Market':
		continue
	elif r['Submarket'] not in lSubmarkets:
		lSubmarkets.append(r['Submarket'])

# Cycle through submarkets and get the New Supply and Demand data for each
lNew_supply_demand = [['Submarket', 'New Supply', 'Demand']]
for submarket in lSubmarkets:
	for row in dTemp:
		r = dTemp[row]
		if r['Submarket'] == submarket and r['Period'] == year:
			lNew_supply_demand.append([submarket,  r['Annual Supply'], r['Annual Demand']])
			break
# pprint(lNew_supply_demand)

# Create a new CSV file with the New Supply and Demand data
output_file = f'{pathAxio}PHX Market Supply Demand {year}.csv'
with open(output_file, mode='w', newline='') as file:
	writer = csv.writer(file)
	writer.writerows(lNew_supply_demand)
# Open the new CSV file
lao.openFile(output_file)
exit('\n Fin')

