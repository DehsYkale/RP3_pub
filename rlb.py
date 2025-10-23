# python3

__author__ = 'blandis'
__project__ = 'rlb'

import csv
import datetime
import lao
from numpy import median
import fun_text_date as td
from pprint import pprint

# Get RLB csv and xlsx file and return dicts
def getRLBData():
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg(' Select latest RLB COE csv...')
	# Select COE and derive other file names from date
	rlbPath = lao.getPath('rlb')
	inCOE = lao.guiFileOpen(rlbPath, 'Select RLB COE CSV', [('.csv', 'RLB*COE*20*KEY*CLEANED.csv')])
	lao.banner('MO RLB Master Data Calculator')
	print(' Assembling data...please stand by...')
	# Get file data 20YY-MM from file name
	fileDate = inCOE.replace('{0}RLB COE '.format(rlbPath), '').replace(' KEY CLEANED.csv', '')
	inPermits = '{0}RLB Permits {1} KEY CLEANED.csv'.format(rlbPath, fileDate)
	inResale = '{0}RLB Resale {1}.csv'.format(rlbPath, fileDate)
	# inResale = lao.guiFileOpen(rlbPath, 'Select RLB Resale CSV', [('.csv', 'RLB Resale*.csv')])
	print('\n Building COE dict...')
	dCOE = lao.spreadsheetToDict(inCOE)
	print('\n Building Permits dict...')
	dPermits = lao.spreadsheetToDict(inPermits)
	print('\n Building Resale dict...')
	dResale = lao.spreadsheetToDict(inResale)

	# Make Builders Cleaned csv files returning cleaned dicts
	# dCOE, dPermits = cleanBuilderNames(dCOE, dPermits, inCOE, inPermits)

	return dCOE, dPermits, dResale, fileDate

# Clean the builder names and change product codes to readable
def cleanBuilderNames(dCOE, dPermits, inCOE, inPermits):
	# Set variables
	lDicts = [dCOE, dPermits]
	outCOE = inCOE.replace('.csv', ' BUILDERS CLEANED.csv')
	outPermits = inPermits.replace('.csv', ' BUILDERS CLEANED.csv')
	builderrenamefile = 'F:/Research Department/MIMO/zData/BuilderRenameDatabase_v01.csv'
	dRename = lao.spreadsheetToDict(builderrenamefile)
	
	isCOE = True
	for din in lDicts:
		if isCOE:
			outFile = outCOE
			isCOE = False
		else:
			outFile = outPermits
		lHeader = []
		for key in din[1].keys():
			lHeader.append(key)

		lao.check_if_file_is_open(outFile)
		with open(outFile, 'w') as f:
			fout = csv.writer(f)
			fout.writerow(lHeader)
			for row in din:
				if din[row]['PRODCODE'] == 'A':
					din[row]['PRODCODE'] = 'Attached'
				elif din[row]['PRODCODE'] == 'B':
					din[row]['PRODCODE'] = 'Detached'
				elif din[row]['PRODCODE'] == 'C':
					din[row]['PRODCODE'] = 'Adult'
				elif din[row]['PRODCODE'] == 'D':
					din[row]['PRODCODE'] = 'Custom'
				for rename in dRename:
					if din[row]['BUILDER'] == dRename[rename]['BUILDER']:
						din[row]['BUILDER'] =dRename[rename]['RENAME']
						break
				lLine = din[row].values()
				fout.writerow(lLine)
	# Create dicts from Builders Cleaned csv
	dCOE = lao.spreadsheetToDict(outCOE)
	dPermits = lao.spreadsheetToDict(outPermits)
	# lao.openFile(outCOE)
	# lao.openFile(outPermits)
	return dCOE, dPermits

# Calculate Meidan Sale Price & Count for COE & Resale
# [Housing Sales] pink worksheet
def housingSales(dCOE, dResale, fileDate):
	lao.banner('MO RLB Master Data Calculator')
	print(' Calculating median sale prices and counts for COE & resale homes...')
	# Create Lists
	# PHX COE
	lCOE_PHX_count, lCOE_PHX_Sale_Price_Cur_Mo, lCOE_PHX_SqFt_Cur_Mo = [], [], []
	# PHX RESALE
	lRESALE_PHX_count, lRESALE_PHX_cur_mo, lRESALE_PHX_SqFt_Cur_Mo = [], [], []
	# PIN COE
	lCOE_PIN_count, lCOE_PIN_Sale_Price_Cur_Mo, lCOE_PIN_SqFt_Cur_Mo = [], [], []
	# PIN RESALE
	lRESALE_PIN_count, lRESALE_PIN_cur_mo, lRESALE_PIN_SqFt_Cur_Mo = [], [], []

	lfileDate = fileDate.split('-')
	year = lfileDate[0]
	month = lfileDate[1]
	dt_First_Of_Last_Month = datetime.datetime(int(lfileDate[0]), int(lfileDate[1]), 1)
	ui = td.uInput('\n Continue... > {0}'.format(dt_First_Of_Last_Month))
	if ui == '00':
		exit('\n Terminating program...')
	dt_jan_1_cur_yr = datetime.datetime(int(year), 1, 1)

	# COE -----------------------------------------------------------------------
	PHX_new_total_reveune = 0
	for row in dCOE:
		# Skip Pima County and Attached units
		if dCOE[row]['COUNTY'] == 'PIMA':  # Exclude Pima county
			continue
		# Exclude Attached homes
		# if dCOE[row]['PRODCODE'] == 'A' or dCOE[row]['PRODCODE'] == 'Attached':
		# 	continue

		# All PHX COE
		lCOE_PHX_count.append(int(dCOE[row]['SALEPRICE']))
		PHX_new_total_reveune = PHX_new_total_reveune + int(dCOE[row]['SALEPRICE'])
		dtsplt = dCOE[row]['DATE'].split('/')
		saledate = datetime.datetime(int(dtsplt[2]), int(dtsplt[0]), int(dtsplt[1]))
		
		# PHX Current Month Meidan Price list
		if saledate >= dt_First_Of_Last_Month:
			lCOE_PHX_Sale_Price_Cur_Mo.append(int(dCOE[row]['SALEPRICE']))
			# print(dCOE[row]['SQFT'])
			if dCOE[row]['SQFT'] != '':
				if int(dCOE[row]['SQFT']) > 0 :
					lCOE_PHX_SqFt_Cur_Mo.append(int(dCOE[row]['SQFT']))

		if dCOE[row]['COUNTY'] == 'PINAL':
			# All Pinal COE
			lCOE_PIN_count.append(int(dCOE[row]['SALEPRICE']))
			# Pinal Current Month Meidan Price list
			if saledate >= dt_First_Of_Last_Month:
				lCOE_PIN_Sale_Price_Cur_Mo.append(int(dCOE[row]['SALEPRICE']))
				if dCOE[row]['SQFT'] != '':
					lCOE_PIN_SqFt_Cur_Mo.append(int(dCOE[row]['SQFT']))

	# RESALE -----------------------------------------------------------------------
	for row in dResale:
		# Skip Pima County and Attached units
		if dResale[row]['COUNTY'] == 'PIMA':  # Exclude Pima county
			continue
		# Exclude Attached homes
		# if dResale[row]['PRODCODE'] == 'A' or dResale[row]['PRODCODE'] == 'Attached':
		# 	continue

		lRESALE_PHX_count.append(int(dResale[row]['SALEPRICE']))
		dtsplt = dResale[row]['DATE'].split('/')
		saledate = datetime.datetime(int(dtsplt[2]), int(dtsplt[0]), int(dtsplt[1]))
		
		# PHX Current Month Sale Price and Count
		if saledate >= dt_First_Of_Last_Month:
			if dResale[row]['SALEPRICE'] != '':
				lRESALE_PHX_cur_mo.append(int(dResale[row]['SALEPRICE']))
			if dResale[row]['SQFT'] != '':
				lRESALE_PHX_SqFt_Cur_Mo.append(int(dResale[row]['SQFT']))

		if dResale[row]['COUNTY'] == 'PINAL':
			# PIN All Resale
			lRESALE_PIN_count.append(int(dResale[row]['SALEPRICE']))
			# PIN Current Month Meidan Price list
			if saledate >= dt_First_Of_Last_Month:
				if dResale[row]['SALEPRICE'] != '':
					lRESALE_PIN_cur_mo.append(int(dResale[row]['SALEPRICE']))
				if dResale[row]['SQFT'] != '':
					lRESALE_PIN_SqFt_Cur_Mo.append(int(dResale[row]['SQFT']))
	
	dRLB = {}
	# PHX NEW
	dRLB['NEW_PHX_COUNT'] = len(lCOE_PHX_count)
	dRLB['NEW_PHX_MEDIAN_PRICE'] = round(median(lCOE_PHX_Sale_Price_Cur_Mo))
	dRLB['NEW_PHX_MEDIAN_SQFT'] = round(median(lCOE_PHX_SqFt_Cur_Mo))
	dRLB['NEW_PHX_PRICE_SQFT'] = round(dRLB['NEW_PHX_MEDIAN_PRICE'] / dRLB['NEW_PHX_MEDIAN_SQFT'])
	dRLB['NEW_PHX_TOTAL_REVEUE'] = round(PHX_new_total_reveune)
	dRLB['NEW_PHX_AVG_PRICE'] = dRLB['NEW_PHX_TOTAL_REVEUE'] / dRLB['NEW_PHX_COUNT']
	# PHX RESALE
	dRLB['RESALE_PHX_COUNT'] = len(lRESALE_PHX_count)
	dRLB['RESALE_PHX_MEDIAN_PRICE'] = round(median(lRESALE_PHX_cur_mo))
	dRLB['RESALE_PHX_MEDIAN_SQFT'] = round(median(lRESALE_PHX_SqFt_Cur_Mo))
	dRLB['RESALE_PHX_PRICE_SQFT'] = round(dRLB['RESALE_PHX_MEDIAN_PRICE'] / dRLB['RESALE_PHX_MEDIAN_SQFT'])
	
	dRLB['NEW_PIN_COUNT'] = len(lCOE_PIN_count)
	dRLB['NEW_PIN_MEDIAN_PRICE'] = round(median(lCOE_PIN_Sale_Price_Cur_Mo))
	dRLB['NEW_PIN_MEDIAN_SQFT'] = round(median(lCOE_PIN_SqFt_Cur_Mo))

	dRLB['RESALE_PIN_COUNT'] = len(lRESALE_PIN_count)
	dRLB['RESALE_PIN_MEDIAN_PRICE'] = round(median(lRESALE_PIN_cur_mo))

	return dRLB

# Calculate home sales counts by price range
# [RLB Housing $ Range] pink WS
def homePriceRanges(dCOE, dResale):

	lao.banner('MO RLB Master Data Calculator')
	outfilename = 'C:/TEMP/RLB_Home_Price_Range.csv'
	print(' RLB New & Existing Home Sales by Price Range')
	ui = td.uInput('\n West Valley only? [0/1] > ')

	# West Valley Zipcodes
	lWestValleyZips = ['85009', '85017', '85019', '85027', '85029', '85031', '85033', '85035', '85037', '85041', '85043', '85045', '85048', '85051', '85053', '85083', '85085', '85086', '85087', '85301', '85302', '85303', '85304', '85305', '85306', '85307', '85308', '85309', '85310', '85322', '85323', '85326', '85335', '85338', '85339', '85340', '85342', '85343', '85345', '85351', '85353', '85354', '85355', '85361', '85363', '85373', '85374', '85375', '85378', '85379', '85381', '85382', '85383', '85387', '85388', '85390', '85392', '85395', '85396']
	# NEW HOMES
	cnt350N, cnt450N, cnt550N, cnt650N, cnt750N, cnt999N = 0, 0, 0, 0, 0, 0

	for row in dCOE:
		# West Valley Filter
		if ui == '1':
			if not dCOE[row]['ZIP'] in lWestValleyZips:
				continue
		if dCOE[row]['SALEPRICE'] == '':
			continue
		if dCOE[row]['COUNTY'].upper() == 'PIMA':
			continue
		if dCOE[row]['PRODCODE'].strip() == 'A' or dCOE[row]['PRODCODE'].strip() == 'Attached':
			continue
		if int(dCOE[row]['SALEPRICE']) < 350000:
			cnt350N +=1
		elif int(dCOE[row]['SALEPRICE']) < 450000:
			cnt450N +=1
		elif int(dCOE[row]['SALEPRICE']) < 550000:
			cnt550N +=1
		elif int(dCOE[row]['SALEPRICE']) < 650000:
			cnt650N +=1
		elif int(dCOE[row]['SALEPRICE']) < 750000:
			cnt750N +=1
		elif int(dCOE[row]['SALEPRICE']) < 100000000:
			cnt999N +=1

	# RESALE HOMES
	cnt350R, cnt450R, cnt550R, cnt650R, cnt750R, cnt999R = 0, 0, 0, 0, 0, 0

	for row in dResale:
		# West Valley Filter
		if ui == '1':
			if not dResale[row]['ZIP'] in lWestValleyZips:
				continue
		# Skip no sale price and Pima county records		if dResale[row]['SALEPRICE'] == '':
			continue
		if dResale[row]['COUNTY'].upper() == 'PIMA':
			continue
		if dResale[row]['PRODCODE'].strip() == 'A' or dResale[row]['PRODCODE'].strip() == 'Attached':
			continue

		if int(dResale[row]['SALEPRICE']) < 350000:
			cnt350R +=1
		elif int(dResale[row]['SALEPRICE']) < 450000:
			cnt450R +=1
		elif int(dResale[row]['SALEPRICE']) < 550000:
			cnt550R +=1
		elif int(dResale[row]['SALEPRICE']) < 650000:
			cnt650R +=1
		elif int(dResale[row]['SALEPRICE']) < 750000:
			cnt750R +=1
		elif int(dResale[row]['SALEPRICE']) < 100000000:
			cnt999R +=1

	lao.check_if_file_is_open(outfilename)
	with open(outfilename, 'w', newline='') as f:
		fout = csv.writer(f)
		fout.writerow(['RLB HOUSING $ RANGE (pink)'])
		fout.writerow([''])
		fout.writerow(['NEW HOMES'])
		fout.writerow(['Range', 'Count'])
		fout.writerow(['< $350K', cnt350N])
		fout.writerow(['$350K-$450K', cnt450N])
		fout.writerow(['$450K-$550K',cnt550N])
		fout.writerow(['$550K-$650K',cnt650N])
		fout.writerow(['$650K-$750K',cnt750N])
		fout.writerow(['> $750K',cnt999N])
		fout.writerow([''])
		fout.writerow(['RESALE HOMES'])
		fout.writerow(['Range', 'Count'])
		fout.writerow(['< $350K', cnt350R])
		fout.writerow(['$359K-$450K', cnt450R])
		fout.writerow(['$450K-$550K', cnt550R])
		fout.writerow(['$550K-$650K', cnt650R])
		fout.writerow(['$650K-$750K', cnt750R])
		fout.writerow(['> $750K', cnt999R])

	lao.openFile(outfilename)
	
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Copy to PHX MO Spreadsheet\n')
	print('   RLB New & Existing Home Sales by Price Range')
	td.colorText('   Worksheet: RLB Housing $ Range (pink)', 'PINK')
	lao.holdup()

# Caclulate number of Active Adult Permits
# [Actv Adult Permits] purple WS
def activeAdultPermits(dPermits, dRLB):
	count = 0
	for row in dPermits:
		if dPermits[row]['COUNTY'] == 'PIMA':
			continue 
		if dPermits[row]['PRODCODE'] == 'C' or dPermits[row]['PRODCODE'] == 'Adult':
			count += 1
	
	dRLB['NEW_PHX_ACTV_ADULT_PERMITS'] = count
	return dRLB

# Build dict of Builder, Sales Volume and Homes Sold
def make_builder_salesvolume_homessold_avgprice(dCOE):
	lao.banner('MO RLB Master Data Calculator')
	# Build dHB dict
	print('\n Making HB dict...')
	dHB = {}
	for row in dCOE:
		# Skip Pima county
		if dCOE[row]['COUNTY'] == 'PIMA':
			continue
		builder = dCOE[row]['BUILDER']
		homesaleprice = int(dCOE[row]['SALEPRICE'])
		
		# Calculate total sales volume & homes sold
		if builder in dHB.keys():
			salesvolume = homesaleprice + dHB[builder]['SALESVOLUME']
			homessold = dHB[builder]['HOMESSOLD'] + 1
			dHB[builder]['SALESVOLUME'] = salesvolume
			dHB[builder]['HOMESSOLD'] = homessold
		else:
			dHB[builder] = {'SALESVOLUME': homesaleprice, 'HOMESSOLD': 1}

	# Calculate Average Sale Price
	for builder in dHB:
		avgsaleprice = dHB[builder]['SALESVOLUME'] / dHB[builder]['HOMESSOLD']
		dHB[builder]['AVGSALEPRICE'] = int(round(avgsaleprice))

	# Make Top COE list
	print('\n Making COE list...')
	lHBCOE = []
	for builder in dHB:
		if builder == 'Misc Custom':
			continue
		homessold = dHB[builder]['HOMESSOLD']
		lHBCOE.append([builder, homessold])
	# Sort by Homes Sold
	lHBCOE.sort(key=lambda x: x[1], reverse=True)
	lHBCOE = lHBCOE[:40]

	# Make HB by Avg Home Price
	print('\n Making Avg Home Price list...')
	lHBAvgPriceUnits = []
	for builder in dHB:
		if builder == 'Misc Custom':
			continue
		homessold = dHB[builder]['HOMESSOLD']
		avgsaleprice = dHB[builder]['AVGSALEPRICE']
		strAvgSalePrice = str(avgsaleprice)
		strAvgSalePrice = '${0}'.format(strAvgSalePrice[:-3])
		strAvgPriceUnits = '{0}K : {1:,} units'.format(strAvgSalePrice, homessold)
		lHBAvgPriceUnits.append([builder, avgsaleprice, strAvgPriceUnits, homessold])
	# Sort by Homes Sold
	lHBAvgPriceUnits.sort(key=lambda x: x[3], reverse=True)
	lHBAvgPriceUnits = lHBAvgPriceUnits[:40]
	lHBAvgPriceUnits.sort(key=lambda x: x[1], reverse=False)

	# Make HB Sales Volume list
	lHBRevenue = []
	
	for builder in dHB:
		if builder == 'Misc Custom':
			continue
		hbrevenue = dHB[builder]['SALESVOLUME']
		lHBRevenue.append([builder, hbrevenue])
	# Sort by Sales Volume
	lHBRevenue.sort(key=lambda x: x[1], reverse=True)
	lHBRevenue = lHBRevenue[:40]

	return lHBCOE, lHBAvgPriceUnits, lHBRevenue

# Make Homebuilder Permits dict
def make_builder_permits(dPermits):
	print('\n Making Permits dict...')
	dHB = {}
	for row in dPermits:
		# Skip Pima county
		if dPermits[row]['COUNTY'] == 'PIMA':
			continue
		builder = dPermits[row]['BUILDER']
		# Calculate total sales volume & homes sold
		if builder in dHB.keys():
			dHB[builder] += 1
		else:
			dHB[builder] = 1
	
	# Make Top Permit list
	print('\n Making Permits list...')
	lHBPermits = []
	for builder in dHB:
		# Skip Misc Custom and Attached units
		if builder == 'Misc Custom':
			continue
		# if dHB[builder]['PRODCODE'] == 'Attached':
		# 	continue
		# homessold = dHB[builder]['HOMESSOLD']
		lHBPermits.append([builder, dHB[builder]])
	# Sort by Homes Sold
	lHBPermits.sort(key=lambda x: x[1], reverse=True)
	lHBPermits = lHBPermits[:40]
	return lHBPermits

# Make list of Builder Active Subs
def make_builder_acitve_subs(dCOE, dPermits):
	print('\n Making HB Active Subs dict...')
	dSubs = {}
	# Process COEs
	for row in dCOE:
		# Skip Pima County and Attached units
		if dCOE[row]['COUNTY'] == 'PIMA':  # Exclude Pima county
			continue
		builder = dCOE[row]['BUILDER']
		subid = dCOE[row]['SUBID']
		# Skip Misc Custom and Attached units
		if builder == 'Misc Custom':
			continue
		# Calculate total sales volume & homes sold
		if builder in dSubs.keys():
			if subid in dSubs[builder]:
				continue
			else:
				dSubs[builder].append(subid)
		else:
			dSubs[builder] = [subid]

	# Process Permits
	for row in dPermits:
		# Skip Pima County and Attached units
		if dPermits[row]['COUNTY'] == 'PIMA':  # Exclude Pima county
			continue
		builder = dPermits[row]['BUILDER']
		subid = dPermits[row]['SUBID']
		# Skip Misc Custom
		if builder == 'Misc Custom':
			continue
		# Calculate total sales volume & homes sold
		if builder in dSubs.keys():
			if subid in dSubs[builder]:
				continue
			else:
				dSubs[builder].append(subid)
		else:
			dSubs[builder] = [subid]

	print('\n Making HB Active Subs list...')
	lHBActiveSubs = []
	for builder in dSubs:
		total_subs = len(dSubs[builder])
		lHBActiveSubs.append([builder, total_subs])
	# Sort by number of Subs
	lHBActiveSubs.sort(key=lambda x: x[1], reverse=True)
	lHBActiveSubs = lHBActiveSubs[:40]

	return lHBActiveSubs

# Make CSV of New Home permits, coe, avg price units and revenue
def make_hb_results_csv(lHBPermits, lHBCOE, lHBAvgPriceUnits, lHBRevenue, lHBActiveSubs):
	import csv
	lMaster = []
	index = 0
	outfilename = '{0}HB Data.csv'.format(lao.getPath('rlb'))
	lao.check_if_file_is_open(outfilename)
	with open(outfilename, 'w', newline='') as f:
		fout = csv.writer(f)
		fout.writerow(['Top HB Permits', '', '', 'Top HB COE', '', '', 'Top HB Avg Hm Price', '', '', '', 'Top HB Revenue', '', '', 'Top HB Num Subs'])
		fout.writerow(['Homebuilder', '12 Month Permits', '', 'Homebuilder', '12 Month COE', '', 'Homebuilder', 'Avg Price', '$ & Units', '', 'Homebuilder', 'Revenue', '', 'Homebuilder', 'No Subs'])
		for i in range(0, 40):
			lprm = lHBPermits[i]
			lcoe = lHBCOE[i]
			lppu = lHBAvgPriceUnits[i][:-1]
			lrev = lHBRevenue[i]
			lsub = lHBActiveSubs[i]
			ltemp = lprm + [''] + lcoe + [''] + lppu + [''] + lrev + [''] + lsub
			fout.writerow(ltemp)
	lao.openFile(outfilename)

	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Copy to PHX MO Spreadsheet\n')
	print('   RLB Permits, COE, Avg Home rice, Revenue & Num Subs')
	td.colorText('   Worksheet: Top HB Permits (red)', 'RED')
	td.colorText('   Worksheet: Top HB COE (red)', 'RED')
	td.colorText('   Worksheet: Top HB Avg Hm Price (red)', 'RED')
	td.colorText('   Worksheet: Top HB Revenue (red)', 'RED')
	td.colorText('   Worksheet: Top HB Num Subs (red)', 'RED')
	lao.holdup()

		
