#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import how
import fun_text_date as td
import lao
import rlb
from pprint import pprint
import pyperclip


lao.banner('PHX MPC Slide Calculator v02')

# Instructions
how.mo_phx_mpc_slide_calculator()

fPrice = lao.guiFileOpen(path='F:/Research Department/MIMO/zData/Zonda', titlestring='Zonda MPCs from L5', extension=[('csv files', '*MPCS CLEANED.csv')])
if not 'CLEANED' in fPrice:
	td.warningMsg('\n Opened the wrong file...')
	exit('\n Terminating program...')
fCSV_unsorted = 'C:/TEMP/RLB_MPCs_unsorted.csv'
fCSV_sorted = 'C:/TEMP/RLB_MPCs_sorted.csv'

# DO NOT REORDER
lMajorMPCs = [
	'Aloravita',
	'Vistancia',
	'North Copper Canyon',
	'Sun City Festival/Foothills',
	'Verrado/Victory',
	'Arroyo Seco',
	'Estrella Mtn Ranch/Cantamia',
	'Alamar',
	'Verde Trails',
	'Rancho El Dorado/Province',
	'Desert Ridge',
	'Eastmark/Encore',
	'Superstition Vistas',
	'Waterston',
	'Bella Vista Farms',
	'Tortosa',
		]

dOut = {}
index = 1
for row in lMajorMPCs:
	dOut[row] = {'COEs': 0, 'MINPRICE': 0, 'MAXPRICE': 0, 'PERMITS': 0, 'ORDER': index}
	index += 1

# dCOE = lao.spreadsheetToDict(fCOE)
# dPermits = lao.spreadsheetToDict(fPerm)
# Get RLB dicts, dResael and fileDate not used
dCOE, dPermits, dResale, fileDate = rlb.getRLBData()
dPrice = lao.spreadsheetToDict(fPrice, sheetname='None', capitalize_keys=True)

pprint(lMajorMPCs)
# for row in dPrice:
# 	pprint(dPrice[row])
# 	ui = td.uInput('\n Continue... > ')
# 	break
print

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
for price in dPrice:
	
	zondaMPC = dPrice[price]['MASTER_PLAN']
	# if zondaMPC == '':
	# 	continue
	# pprint(dPrice[price])
	# print(zondaMPC)
	# ui = td.uInput('\n Continue... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	if zondaMPC in lMajorMPCs:
		# print('here1')
		# ui = td.uInput('\n Continue... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		print(zondaMPC)
		if dPrice[price]['L12M_AVG_SALES'] == '' and zondaMPC == 'VERRADO/VICTORY':
			continue
		try:
			minprice = round(int(dPrice[price]['MINPRICE']), -3)
		except ValueError:
			minprice = dPrice[price]['MINPRICE']
		try:
			maxprice = round(int(dPrice[price]['MAXPRICE']), -3)
		except ValueError:
			maxprice = dPrice[price]['MAXPRICE']
		print(minprice, maxprice)
		print
		# if dOut.has_key(zondaMPC):
		# print('dOUT Min: {0}  dPrice Min: {1}'.format(dOut[zondaMPC]['MINPRICE'], minprice))
		# print('dOUT Max: {0}  dPrice Max: {1}'.format(dOut[zondaMPC]['MAXPRICE'], maxprice))
		if minprice != '':
			if dOut[zondaMPC]['MINPRICE'] == 0:
				dOut[zondaMPC]['MINPRICE'] = minprice
			elif dOut[zondaMPC]['MINPRICE'] > minprice:
				dOut[zondaMPC]['MINPRICE'] = minprice
		if maxprice != '':
			if dOut[zondaMPC]['MAXPRICE'] == 0:
				dOut[zondaMPC]['MAXPRICE'] = maxprice
			elif dOut[zondaMPC]['MAXPRICE'] < maxprice:
				dOut[zondaMPC]['MAXPRICE'] = maxprice

# Write to file
lData = []
with open(fCSV_unsorted, 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(['ORDER', 'MPC', 'PERMITS', 'COE', 'MINPRICE', 'MAXPRICE'])
	for row in dOut:
		maxprice = str(dOut[row]['MAXPRICE'])
		maxprice = maxprice[:-3]
		minprice = str(dOut[row]['MINPRICE'])
		minprice = minprice[:-3]
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
	outcsv.writerow(['ORDER', 'MPC', 'PERMITS', 'SALES', 'AVGPRICE'])
	for row in csv_sorted:
		outcsv.writerow(row)

		lao.banner('PHX MPC Slide Calculator v02')
		td.instrMsg(' Copy to Major Master Plan Community slide\n')
		clipboard_permits_sales_pricing = '{0} Permits  {1} Sales\r\nPricing: ${2}-${3}'.format(row[2], row[3], row[4], row[5])
		
		print('{0}\n'.format(row[1].title()))
		print(clipboard_permits_sales_pricing)
		pyperclip.copy(clipboard_permits_sales_pricing)
		print('\n Copied to clipboard.')
		# print('{0} Permits  {1} Sales'.format(row[2], row[3]))
		# print('Pricing: ${0}-${1}'.format(row[4], row[5]))
		lao.holdup()

lao.openFile(fCSV_sorted)

# # Sort by MPC
# with open(fCSV_unsorted, 'r') as unsorted, open(fCSV_sorted, 'w', newline='') as sorted:
# 	incsv = csv.reader(unsorted)
# 	outcsv = csv.writer(sorted)
# 	outcsv.writerow(['MPC', 'PERMITS', 'SALES', 'AVGPRICE'])
# 	csv_sorted = sorted(incsv, key=lambda x: x[0], reverse=False)
# 	for row in csv_sorted:
# 		outcsv.writerow(row)

# lao.openFile(fCSV_unsorted)



	
