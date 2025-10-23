#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import dicts
import how
import fun_text_date as td
import lao
import rlb
from pprint import pprint
import pyperclip


lao.banner('PHX MPC Slide Calculator v03')

# Instructions
how.mo_phx_mpc_slide_calculator()

# Get year and quarter
year_qtr = td.getDateQuarter()

# Get file paths
fPrice = f'F:/Research Department/MIMO/zData/Zonda/MIMO/PHX Subdivisions-Table {year_qtr}.csv'

fCSV_unsorted = 'C:/TEMP/RLB_MPCs_unsorted.csv'
fCSV_sorted = 'C:/TEMP/RLB_MPCs_sorted.csv'



# DO NOT REORDER
lMajorMPCs = [
	'Aloravita',
	'Vistancia',
	'Asante',
	'North Copper Canyon',
	'Sun City Festival/Foothills',
	'Sterling Grove',
	'Allen Ranches',
	'Verrado/Victory',
	'Arroyo Seco',
	'Estrella Mtn Ranch/Cantamia',
	'Alamar',
	'Amarillo Creek',
	'Rancho El Dorado/Province',
	'Tortosa',
	'Desert Ridge',
	'Eastmark/Encore',
	'Superstition Vistas',
	'Waterston',
	'Bella Vista Farms']

dOut = {}
index = 1
for row in lMajorMPCs:
	dOut[row] = {'COEs': 0, 'Price Min': 350, 'Price Max': 0, 'PERMITS': 0, 'ORDER': index}
	index += 1

# Get RLB dicts, dResael and fileDate not used
dCOE, dPermits, dResale, fileDate = rlb.getRLBData()
dPrice = lao.spreadsheetToDict(fPrice)
# Standardize MPC names
# Get dict of MPC rename
mpc_rename_file = '{0}MPCRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
dSubs_rename = lao.spreadsheetToDict(mpc_rename_file)
market = 'PHX'
print('Standardizing Zonda MPC names...')
dPrice = td.standarize_hb_and_sub_names(fPrice, dPrice, dSubs_rename, market)

# print('here1')
# pprint(dPrice)
# for row in dPrice:
# 	pprint(dPrice[row])
# 	ui = td.uInput('\n Continue... > ')
# 	break
# print

# Build COE
for coe in dCOE:
	rlbMPC = dCOE[coe]['MASTPLAN']
	# Skip MPCs not in lMajorMPCs list
	if not rlbMPC in lMajorMPCs:
		continue

	# If the MPC has already been added to dOut
	#if dOut.has_key(dCOE[coe]['MASTPLAN']):
	if dCOE[coe]['MASTPLAN'] in dOut:
		dOut[rlbMPC]['COEs'] = dOut[rlbMPC]['COEs'] + 1
	# Else add the MPC to dOut
	else:
		dOut[rlbMPC] = {'COEs': 1, 'SALEVOL': saleprice, 'AVGPRICE': 0, 'PERMITS': 0}

# Build Permits
for perm in dPermits:
	rlbMPC = dPermits[perm]['MASTPLAN']
	if not rlbMPC in lMajorMPCs:
		continue
	dOut[rlbMPC]['PERMITS'] = dOut[rlbMPC]['PERMITS'] + 1

# Build Price Range
for row in dPrice:
	
	# zonda_mpc = dPrice[row]['MASTER_PLAN']
	zonda_mpc = dPrice[row]['Community']
	# if zonda_mpc == '':
	# 	continue
	# pprint(dPrice[price])
	# print(zonda_mpc)
	# ui = td.uInput('\n Continue... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	if zonda_mpc in lMajorMPCs:
		# print('here1')
		# ui = td.uInput('\n Continue... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		# if dPrice[row]['L12M_AVG_SALES'] == '' and zonda_mpc == 'VERRADO/VICTORY':
		if dPrice[row]['Annual Closings'] == '' and zonda_mpc == 'VERRADO/VICTORY':
			continue

		try:
			minprice = int(round(float(dPrice[row]['Price Min']) / 1000))
		except ValueError:
			minprice = dPrice[row]['Price Min']
		try:
			maxprice = int(round(float(dPrice[row]['Price Max']) / 1000))
		except ValueError:
			maxprice = dPrice[row]['Price Max']

		if minprice != '':
			if dOut[zonda_mpc]['Price Min'] == 350 and minprice > 350:
				dOut[zonda_mpc]['Price Min'] = minprice
			elif dOut[zonda_mpc]['Price Min'] > minprice and minprice > 350:
				dOut[zonda_mpc]['Price Min'] = minprice
		if maxprice != '':
			if dOut[zonda_mpc]['Price Max'] == 0:
				dOut[zonda_mpc]['Price Max'] = maxprice
			elif dOut[zonda_mpc]['Price Max'] < maxprice:
				dOut[zonda_mpc]['Price Max'] = maxprice

# Write to file
lData = []
with open(fCSV_unsorted, 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(['ORDER', 'MPC', 'Permits', 'COE', 'Price Min', 'Price Max'])
	for row in dOut:
		maxprice = str(dOut[row]['Price Max'])
		num = int(maxprice)
		maxprice = f"{num:,}" if num >= 1000 else str(num)
		minprice = str(dOut[row]['Price Min'])
		num = int(minprice)
		minprice = f"{num:,}" if num >= 1000 else str(num)
		lRow = []
		lRow.append(dOut[row]['ORDER'])
		lRow.append(row)
		lRow.append(dOut[row]['PERMITS'])
		lRow.append(dOut[row]['COEs'])
		lRow.append(minprice)
		lRow.append(maxprice)
		fout.writerow(lRow)
		lData.append(lRow)

# Sort by MPC order
csv_sorted = sorted(lData, key=lambda x: x[0], reverse=False)

with open(fCSV_sorted, 'w', newline='') as sorted:
	outcsv = csv.writer(sorted)
	outcsv.writerow(['Order', 'MPC', 'Permits', 'SALES', 'AvgPrice'])
	for row in csv_sorted:
		outcsv.writerow(row)

		lao.banner('PHX MPC Slide Calculator v03')
		td.instrMsg(' Copy to Major Master Plan Community slide\n')
		clipboard_permits_sales_pricing = '{0} Permits  {1} Sales\r\nPricing: ${2}-${3}'.format(row[2], row[3], row[4], row[5])
		
		print('{0}\n'.format(row[1].title()))
		print(clipboard_permits_sales_pricing)
		pyperclip.copy(clipboard_permits_sales_pricing)
		print('\n Copied to clipboard.')
		lao.holdup()

lao.openFile(fCSV_sorted)





	
