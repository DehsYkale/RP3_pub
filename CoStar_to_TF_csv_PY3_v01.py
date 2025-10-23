#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dicts
import fun_text_date as td
import lao
# from amp import getIntersection
import mpy
import csv
from pprint import pprint


lao.banner('CoStar to TF CSV v01')

inFilePath = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/'
inFile = lao.guiFileOpen(inFilePath, titlestring='Open Costar CSV', extension=[('csv files', '.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])

# inFile = 'F:/Research Department/Projects/Advisors and Markets/Houston/Fort Bend 50 Ac Comps CoStar.csv'
outFile = '{0}'.format(inFile.replace('.csv', '_FORMATTED.csv'))
fMSAs = 'F:/Research Department/scripts/Projects/Research/data/LAO_Markets_and_MSAs.csv'

dCoStar = dicts.spreadsheet_to_dict(inFile)
dMSAs = dicts.spreadsheet_to_dict(fMSAs)

noOfRecs = len(dCoStar)
count = 0
with open(outFile, 'w', newline='') as f:
	fout = csv.writer(f)
	# Write file header
	fout.writerow(dicts.get_tf_csv_header())
	for rec in dCoStar:
		count += 1
		print('\n Rec {0} of {1}'.format(count, noOfRecs))
		r = dCoStar[rec]

		# Skip if Sale Status is not Sold
		if r['Sale Status'] != 'Sold':
			continue

		# Get Intersection from lon/lat
		# location = getIntersection(r['Longitude'], r['Latitude'], False)
		location = mpy.get_intersection_from_lon_lat(dTF='None', lon=r['Longitude'], lat=r['Latitude'], askManually=False, findAddress=False)
		if location == 'None':
			location = r['Property Address']
		# print('here1')
		# Get LAO Market or MSA
		market = 'None'
		for msa in dMSAs:
			m = dMSAs[msa]
			if r['Property County'] in  m['County'] and r['Property State'] in m['State Abbr']:
				if m['LAO Market'] == '':
					market = m['CBSA Title']
					break
				else:
					market = m['LAO Market']
					break
		# print('here2')
		lRow = []
		lRow.append(r['Seller (True) Company'])  # Seller Enity 0
		lRow.append(r['Seller (True) Contact'])  # Seller Person 1
		lRow.append(r['Seller (True) Address'])  # Seller Street 2
		lRow.append(r['Seller (True) City'])  # Seller City 3
		lRow.append(r['Seller (True) State'])  # Seller State 4
		if r['Seller (True) Zip Code'] == '':
			lRow.append('None') # Seller Zip 5
		else:
			lRow.append(r['Seller (True) Zip Code'][6:11]) # Seller Zip 5
		lRow.append('None')  # Seller Country 6
		if r['Seller (True) Phone'] == '':
			lRow.append('None') # Seller Phone 7
		else:
			lRow.append(td.phoneFormat(r['Seller (True) Phone']) ) # Seller Phone 7
		lRow.append('None')  # Seller Email 8
		lRow.append(r['Buyer (True) Company'])  # Buyer Entity 9
		lRow.append(r['Buyer Contact'])  # Buyer Person 10
		lRow.append(r['Buyer (True) Address'])  # Buyer Street 11
		lRow.append(r['Buyer (True) City'])  # Buyer City 12
		lRow.append(r['Buyer (True) State'])  # Buyer State 13
		if r['Buyer (True) Zip Code'] == '':
			lRow.append('None') # Buyer Zip 14
		else:
			lRow.append(r['Buyer (True) Zip Code'][6:11]) # Buyer Zip 14
		lRow.append('None')  # Buyer Country 15
		if r['Buyer (True) Phone'] == '':
			lRow.append('None') # Buyer Phone 16
		else:
			lRow.append(td.phoneFormat(r['Buyer (True) Phone']) ) # Buyer Phone 16
		lRow.append('None')  # Buyer Email 17
		lRow.append(r['Land Area AC'])  # Acres 18
		lRow.append('None')  # Buyer Acting As 19
		lRow.append(r['Property City'])  # City 20
		lRow.append(r['Proposed Use'])  # Classification 21
		lRow.append('USA')  # Country 22
		lRow.append(r['Property County'].replace(' ', '').replace('.', ''))  # County 23
		lRow.append('None')  # Description 24
		lRow.append('None')  # General Plan 25
		lRow.append('None')  # Keyword Group 26
		lRow.append(r['Latitude'])  # Latitude 27
		lRow.append(r['Parcel Number 1 (Min)'])  # Lead Parcels 28
		lRow.append('None')  # Legal Description 29
		lRow.append(location)  # Location 30
		lRow.append(r['Longitude'])  # Longitude 31
		lRow.append('None')  # Lot Description 32
		lRow.append('None')  # Lot Type 33
		lRow.append('None')  # Lots 34
		lRow.append(market)  # Market 35
		lRow.append('None')  # Deal Name 36
		lRow.append(r['Parcel Number 2 (Max)'])  # Parcels 37
		lRow.append('None')  # Record Doc ID 38
		lRow.append(td.date_engine(r['Sale Date'], informat='CoStar'))  # Sale Date 39
		lRow.append(r['Sale Price'])  # Sale Price 40
		lRow.append('CoStar')  # Source 41
		lRow.append(r['Comp ID'])  # Source ID 42
		if len(r['Property State']) == 2:
			state = lao.convertState(r['Property State'])
			lRow.append(state)  # State 43
		else:
			lRow.append(r['Property State'])  # State 43
		lRow.append('None')  # Subdivision 44
		lRow.append('None')  # Submarket 45
		if r['Property Zip Code'] == '':
			lRow.append('None') # Zip Code 46
		else:
			lRow.append(r['Property Zip Code'][6:11]) # Zip Code 46
		lRow.append(r['Zoning'])  # Zoning 47
		lRow.append('None')  # List Date 48
		lRow.append('None')  # List Price 49
		lRow.append(r['Listing Broker Company'])  # List Entity 50
		lRow.append('None') # List Agent 51
		# if r['Listing Broker Agent First Name'] == '':
		# 	lRow.append('None') # List Agent 51
		# else:
		# 	listingAgent = '{0} {1}'.format(r['Listing Broker Agent First Name'], r['Listing Broker Agent Last Name'])
		# 	lRow.append(listingAgent)  # List Agent 51
		lRow.append(r['Listing Broker Phone'])  # List Agent Phone 52
		lRow.append('None')  # List Agent Email 53
		lRow.append('None')  # Alt APN A 54
		lRow.append('None')  # Alt APN B 55
		lRow.append('None')  # PID 56
		lRow.append('None')  # Residence Y-N 57
		lRow.append('None')  # Terms 58
		lRow.append('None')  # Rec Doc URL 59
		lRow.append(r['Transaction Notes'])  # Notes A 60
		lRow.append(r['First Trust Deed Lender'])  # Lender 61
		lRow.append(r['First Trust Deed Balance'])  # Loan Amount 62
		lRow.append('None')  # Loan Date 63
		lRow.append(r['Buyers Broker Company'])  # Buyer Agent Entity 64
		lRow.append('None') # Buyer Agent 65
		# if r['Buyers Broker Agent First Name'] == '':
		# 	lRow.append('None') # Buyer Agent 65
		# else:
		# 	buyerAgent = '{0} {1}'.format(r['Buyers Broker Agent First Name'], r['Buyers Broker Agent Last Name'])
		# 	lRow.append(buyerAgent) # Buyer Agent 65
		if r['Buyers Broker Phone'] == '':
			lRow.append('None') # Buyer Agent Phone 66
		else:
			lRow.append(td.phoneFormat(r['Listing Broker Phone']) ) # Buyer Agent Phone 66
		lRow.append('None')  # Buyer Agent Email 67
		lRow.append('Sold')  # MSL Status 68
		# print('here3')
		# Replace Blanks with None
		for n, i in enumerate(lRow):
			if i == '':
				lRow[n] = 'None'
		# print('here4')
		fout.writerow(lRow)

lao.openFile(outFile)

