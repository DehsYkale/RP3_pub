
import lao
import bb
from datetime import datetime, timedelta
import fun_login
import os
import pandas as pd
from pprint import pprint
import shutil
import subprocess
import fun_text_date as td
from webs import get_L5_url
import xlwings as xw
import xxl


# Archive old LLRs
def archive_old_llrs():

	archive_folder = 'F:/Research Department/Lot Comps Components/Archive'

	# Calculate the date threshold
	week_old_date = datetime.now() - timedelta(days=2)

	# Check each file in the folder
	for filename in os.listdir(outFilePath):
		file_path = os.path.join(outFilePath, filename)

		# Check if the file is an Excel file
		if filename.endswith('.xlsx') or filename.endswith('.xls'):
			# Get the creation date of the file
			creation_date = datetime.fromtimestamp(os.path.getctime(file_path))

			# Check if the file is more than a week old
			if creation_date < week_old_date:
				# Move the file to the archive folder
				destination_path = os.path.join(archive_folder, filename)
				try:
					shutil.move(file_path, destination_path)
				except PermissionError:
					pass
				print(' Moved {0} to the archive folder.'.format(filename))

# Select Market meue
def selectMarketMenu():
	index = 1
	lmenu = []
	lao.banner('LLR Maker v18 Menu')
	for market in lMarkets:
		lmenu.append(market)
		print(' {0:2}) {1}'.format(index, market))
		index += 1
	print(' {0:2}) All'.format(index))
	lmenu.append('All')
	print('\n 00) Quit')
	ui = int(td.uInput('\n Select List > ')) - 1
	if ui == -1:
		exit('\n Terminating program...')
	selection = lmenu[ui]
	return selection

# Build query
def build_tf_query():
	# Build TerraForce where clauses

	# WHERE CLAUSE
	# Basic criteria that all Sale Records need to meet (Sale price greater than $9999)
	wcMinSalePrice = "Sale_Price__c >= 10000"#

	# To capture the deals that Bill has reviewed but Escrow hasn't closed
	wcClosedDeals = "StageName__c LIKE 'Closed%'"

	# To remove Closed Deals on Covered Land
	wcCoveredLand = "Lot_Type__c <> 'Covered Land'"

	# To capture the LAO deals
	wcLAODeals = "StageName__c != 'Closed' AND StageName__c != 'Closed Lost' AND StageName__c != 'Lead' AND StageName__c != 'Cancelled' AND StageName__c != 'Top 100'"

	# To capture the Top100 deals
	wcTop100Deals = "StageName__c = 'Top 100'"

	# To capture the Stage Name Lead and Top100/MVP deals
	wcLeadDeals = "StageName__c != 'Closed' AND StageName__c != 'Closed Lost' AND StageName__c != 'Cancelled' AND StageName__c != 'Escrow'"

	# Only select Brokerage or Reserch Record Types
	# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	wcRecordType = "(RecordTypeId = '012a0000001ZSS5AAO' or RecordTypeId = '012a0000001ZSS8AAO')"
	wcRecordType_Brokerage = "RecordTypeId = '012a0000001ZSS5AAO'"
	wcRecordType_Research = "(RecordTypeId = '012a0000001ZSS8AAO')"

	# Date is filtered in script below because Excel and L5 have different criteria <- even though they are supposed to have different criteria, the older data is so bad that it shouldn't be included
	# SaleDateCutOff = lao.less84months()
	SaleDateCutOff = td.less_time_ago('MONTH', 84)
	wsDateFilter = 'Sale_Date__c > {0}'.format(SaleDateCutOff)
	# wsDateFilter = 'Sale_Date__c > {0}'.format('2000-01-01')

	# Confidential Records do not include OPR 1/1/1970
	wsDateConfidentialRecord = 'OPR_Sent__c != 1970-01-01'

	# Selected Market if any
	if selectedMarket == 'All':
		userSelectedMarket = False
		wcSelectedMarket = ''
	else:
		userSelectedMarket = True
		wcSelectedMarket = "Market__c = '{0}'".format(selectedMarket)

	# Create Comps where clause
	wcComps = "{0} AND {1} AND {2} AND {3} AND {4} AND {5}".format(wcRecordType, wcMinSalePrice, wcClosedDeals, wsDateFilter, wsDateConfidentialRecord, wcCoveredLand)
	if userSelectedMarket:
		wcComps = "{0} AND {1}".format(wcComps, wcSelectedMarket)

	# Create Competitor Listings where clause
	wcCompetitor_Listings = "StageName__c = 'Lead' AND  List_Date__c > {0} AND {1}".format(SaleDateCutOff,wcRecordType_Research)
	if userSelectedMarket:
		wcCompetitor_Listings = "{0} AND {1}".format(wcCompetitor_Listings, wcSelectedMarket)

	# Create LAO Deals where clause
	wcLAO_Deals = "{0} AND {1}".format(wcRecordType_Brokerage, wcLAODeals)
	if userSelectedMarket:
		wcLAO_Deals = "{0} AND {1}".format(wcLAO_Deals, wcSelectedMarket)

	# Create Top 100 Deals where clause
	wcTop100_Deals = "{0} AND {1}".format(wcRecordType_Brokerage, wcTop100Deals)
	if userSelectedMarket:
		wcTop100_Deals = "{0} AND {1}".format(wcTop100_Deals, wcSelectedMarket)
	
	# Create Lead Deals where clause
	wcLead_Deals = "{0} AND {1}".format(wcRecordType_Brokerage, wcLeadDeals)
	if userSelectedMarket:
		wcLead_Deals = "{0} AND {1}".format(wcLead_Deals, wcSelectedMarket)
	
	# return LLRQS_Comps, LLRQS_Competitor_Lisings, LLRQS_Top100_Deals, LLRQS_Lead_Deals
	return wcComps, wcCompetitor_Listings, wcLAO_Deals, wcTop100_Deals, wcLead_Deals

lao.banner('LLR Maker v18')

service = fun_login.TerraForce()
outFilePath = 'F:/Research Department/Lot Comps Components/'
todaydate = td.today_date()

# Set list of LAO Markets
lMarkets = lao.getCounties('Market')
selectedMarket = selectMarketMenu()

# Archive old LLRs
if selectedMarket == 'All':
	archive_old_llrs()

# Get list of brochures on aws
# cp stands for CompleteProcess
cpBrochures = subprocess.run('aws s3 ls s3://request-server/listings/ --output text', stdout = subprocess.PIPE, text=True)
# Convert CompletedProcess to text string
lBrochures = cpBrochures.stdout


# Get the where clauses
wcComps, wcCompetitor_Listings, wcLAO_Deals, wcTop100_Deals, wcLead_Deals = build_tf_query()

lao.banner('LLR Maker v18')

# TerraForce Query Comps
print(' Querying Comps...please stand by...')
fields = 'default'

wc = wcComps
results_Comps = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

# TerraForce Query Competitor Listings
print('\n Querying Competitor Listings...please stand by...')
fields = 'default'
wc = wcCompetitor_Listings
results_Competitor_Listings = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

# TerraForce Query LAO Deals
print('\n Querying LAO Deals...please stand by...')
fields = 'default'
wc = wcLAO_Deals
results_LAO_Deals = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

# TerraForce Query Top100/MVP
print('\n Querying Top 100 Deals...please stand by...')
fields = 'default'
wc = wcTop100_Deals
results_Top100_Deals = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

# TerraForce Query Leads
print('\n Querying Lead Deals...please stand by...')
fields = 'default'
wc = wcLead_Deals
results_Lead_Deals = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
print('\n Querying complete...')

# COMPS LLR SHEET
# Build the master dictionary by Market from TF
dMarketsComps = {}
dMarketsCompsCallList = {}
dMarketsCompetitorListings = {}
dMarketsCompsExternal = {}
dMarketsLAODeals = {}
dMarketsTop100Deals = {}
dMarketsLeadDeals = {}

lSkip_markets = ['Albuquerque', 'Huntsville', 'Raleigh', 'Yuma']

lao.banner('LLR Maker v18')
for mkt in lMarkets:
	# Create only the user selected market unless 'All'
	if selectedMarket == 'All':
		pass
	elif mkt != selectedMarket:
		continue
	elif mkt == 'Prescott' and selectedMarket == 'All':
		continue
	
	if mkt in lSkip_markets:
		continue
	print('\n Building Comps List of Lists dictionary...')
	# Create the list of lines (lToExcelComps) that will be used to create the Excel spreadsheet
	lToExcelComps = []
	#   Add header to the lToExcelComps
	headerComps = [' ', ' ', 'PID', 'Lot Type', 'Classification', 'Submarket', 'Buyer Acting As', 'Subdivision', 'Location', 'City', 'Buyer', 'Seller', 'Sale Date', 'Sale Price', 'Acres', '$/Ac', 'Lot Count', 'Lot Width', 'Lot Depth', '$/Lot', '$/FF', '$/Parcel', 'Description', 'Beneficiary', 'Loan Amount', 'LAO Deal']
	noColsComps = len(headerComps)
	# lToExcelComps.append(headerComps)

	lToExcelCompsCallList = []
	#   Add header to the lToExcelCompsCallList
	headerCompsCallList = [' ', ' ', 'PID', 'Lot Type', 'Classification', 'Submarket', 'Buyer Acting As', 'Subdivision', 'Location', 'City', 'Buyer Enity', 'Buyer Person', 'MVP Byr', 'Phone Byr', 'Mobile Byr', 'Email Byr', 'Seller Entity', 'Seller Person', 'MVP Slr', 'Phone Slr', 'Mobile Slr', 'Email Slr', 'Sale Date', 'Sale Price', 'Acres', '$/Ac', 'Lot Count', '$/Lot', '$/FF', 'Description', 'Beneficiary', 'Loan Amount', 'LAO Deal']
	noColsCompsCallList = len(headerCompsCallList)
	# lToExcelCompsCallList.append(headerCompsCallList)

	lToExcelCompsExternal = []
	#   Add header to the lToExcelComps
	headerCompsExternal = ['Lot Type', 'Classification', 'Submarket', 'Buyer Acting As', 'Subdivision', 'Location', 'City', 'Seller', 'Sale Date', 'Sale Price', 'Acres', '$/Ac', 'Lot Count', 'Lot Width', 'Lot Depth', '$/Lot', '$/FF', '$/Parcel', 'Description']
	noColsCompsExternal = len(headerCompsExternal)

	# Cycle through TF query Comps results
	for row in results_Comps:
		# SKIP RECORD CONDITIONS
		# Not the current Market
		if row['Market__c'] != mkt:
			continue
		# Not a Sale
		if not 'Closed' in row['StageName__c']:
			continue
		# Sale less than $10K
		if row['Sale_Price__c'] < 10000:
			continue
		# Create the line(s) from each single (row) from result

		lList_of_Lines_Comps = xxl.llrCompsLineMaker(row)
		lList_of_Lines_Comps_Call_List = xxl.llrCompsCallListLineMaker(row)
		lList_of_Lines_Comps_External = xxl.llrCompsExternalLineMaker(row)

		# Add the new lines to lToExcelComps list
		for single_line in lList_of_Lines_Comps:
			lToExcelComps.append(single_line)
		for single_line in lList_of_Lines_Comps_Call_List:
			lToExcelCompsCallList.append(single_line)
		for single_line in lList_of_Lines_Comps_External:
			lToExcelCompsExternal.append(single_line)

	dMarketsComps[mkt] = lToExcelComps
	dMarketsCompsCallList[mkt] = lToExcelCompsCallList
	dMarketsCompsExternal[mkt] = lToExcelCompsExternal
	
	print('\n Building Competitor Listings List of Lists dictionary...')
	lToExcelCompetitorListings = []
	# Add headder to the lToExcelCompetitorListings
	headerCompetitorListings = [' ', ' ', ' ', 'PID', 'Lot Type', 'Classification', 'Submarket', 'Subdivision', 'City', 'Acres', 'List Price','$/Ac', 'List Date', 'List Expriation', 'Seller Entity', 'Seller Person', 'MVP', 'Phone', 'Mobile', 'Email', 'Listing Enity', 'Listing Agent', 'Agent Phone', 'Agent Email']
	noColCompetitorListings = len(headerCompetitorListings)
	# Cycle through TF querty results Competitor Listings
	for row in results_Competitor_Listings:
		# SKIP RECORD CONDITIONS
		# Not the current Market
		if row['Market__c'] != mkt:
			continue

		# Create the line(s) from each single (row) from result
		lList_of_Lines_Competitor_Listings = xxl.llrCompsCompetitorListingsLineMaker(row, lBrochures)

		# Add the new lines to lToExcelComps list
		for single_line in lList_of_Lines_Competitor_Listings:
			lToExcelCompetitorListings.append(single_line)
	dMarketsCompetitorListings[mkt] = lToExcelCompetitorListings

	print('\n Building LAO Deals List of Lists dictionary...')
	lToExcelLAODeals = []
	# Add headder to the lToExcelLAODeals
	headerLAOProperties = [' ', ' ', 'PID', 'Stage', 'Lot Type', 'Classification', 'Submarket', 'Subdivision', 'Location', 'City', 'Acres', 'Seller Entity', 'Seller Person', 'MVP', 'Phone', 'Mobile', 'Email', 'PID Created']
	noColLAODeals= len(headerLAOProperties)
	# Cycle through TF querty results Top 100
	for row in results_LAO_Deals:
		# Not the current Market
		if row['Market__c'] != mkt:
			continue
		# Create the line(s) from each single (row) from result
		lList_of_Lines_LAO_Deals = xxl.llrLAODealsLineMaker(row)
		# Add the new lines to lToExcelLAODeals list
		for single_line in lList_of_Lines_LAO_Deals:
			lToExcelLAODeals.append(single_line)
	dMarketsLAODeals[mkt] = lToExcelLAODeals

	print('\n Building Top 100 (MVP) Deals List of Lists dictionary...')
	lToExcelTop100Deals = []
	# Add headder to the lToExcelTop100Deals
	headerTop100Properties = [' ', ' ', 'PID', 'Stage', 'Lot Type', 'Classification', 'Submarket', 'Subdivision', 'Location', 'City', 'Acres', 'Lot Count', 'Seller Entity', 'Seller Person', 'MVP', 'Phone', 'Mobile', 'Email', 'Billing Street', 'Billing City', 'Billing State', 'Billing Zip', 'PID Created']
	noColTop100Deals= len(headerTop100Properties)
	# Cycle through TF querty results Top 100
	for row in results_Top100_Deals:
		# Not the current Market
		if row['Market__c'] != mkt:
			continue
		# Create the line(s) from each single (row) from result
		lList_of_Lines_Top100_Deals = xxl.llrTop100DealsLineMaker(row)
		# Add the new lines to lToExcelTop100Deals list
		for single_line in lList_of_Lines_Top100_Deals:
			lToExcelTop100Deals.append(single_line)
	dMarketsTop100Deals[mkt] = lToExcelTop100Deals

	print('\n Building Lead Deals List of Lists dictionary...')
	lToExcelLeadDeals = []
	# Add headder to the lToExcelLeadDeals
	headerLeadProperties = [' ', ' ', 'PID', 'Stage', 'Lot Type', 'Classification', 'Submarket', 'Subdivision', 'Location', 'City', 'Acres', 'Seller Entity', 'Seller Person', 'MVP', 'Phone', 'Mobile', 'Email', 'Beneficiary', 'Loan Amount', 'PID Created']
	noColLeadDeals= len(headerLeadProperties)
	# Cycle through TF querty results Leads
	for row in results_Lead_Deals:
		# Not the current Market
		if row['Market__c'] != mkt:
			continue
		# Create the line(s) from each single (row) from result
		lList_of_Lines_Lead_Deals = xxl.llrAllLeadDealsLineMaker(row)
		# Add the new lines to lToExcelLeadDeals list
		for single_line in lList_of_Lines_Lead_Deals:
			lToExcelLeadDeals.append(single_line)
	dMarketsLeadDeals[mkt] = lToExcelLeadDeals
	

# Build the LLR for each Market
for mkt in dMarketsComps:
	# if mkt == 'Nashville':
	# 	continue
	print('\n Building {0} market report...'.format(mkt))
	# Create only the user selected market unless 'All'
	if selectedMarket == 'All':
		pass
	elif mkt != selectedMarket:
		continue
	# if mkt == 'Raleigh' or mkt == 'Atlanta' or mkt == 'Albuquerque' or mkt == 'Yuma':
	if mkt == 'Raleigh' or mkt == 'Albuquerque' or mkt == 'Yuma':
		continue
	
	wb = xw.Book()

	# Write Lead Deals Sheet #############################################
	print(' Writing Lead Deals sheet...')
	lToExcelLeadDeals = dMarketsLeadDeals[mkt]
	noRowsLeadDeals = len(lToExcelLeadDeals) + 2
	sht = xw.main.sheets.add('Ownerships')
	df = pd.DataFrame(lToExcelLeadDeals, columns=headerLeadProperties)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort by Submarket, Classification
	sht.range('A1').value = '{0} Ownerships'.format(mkt)
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatOwnershipsSheet(mkt, wb, sht, noRowsLeadDeals, noColLeadDeals)
	lao.sleep(2)
	
	# Write Top 100 Deals Sheet ##########################################
	print(' Writing MVP Deals sheet...')
	lToExcelTop100Deals = dMarketsTop100Deals[mkt]
	with open('C:/TEMP/{0}.txt'.format(mkt), 'w') as ftxt:
		for element in lToExcelTop100Deals:
			ftxt.write('{0}\n'.format(element))
	noRowsTop100Deals = len(lToExcelTop100Deals) + 2
	sht = xw.main.sheets.add('MVP Deals')
	df = pd.DataFrame(lToExcelTop100Deals, columns=headerTop100Properties)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A1').value = '{0} MVP Deals'.format(mkt)
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatTop100DealsSheet(mkt, wb, sht, noRowsTop100Deals, noColTop100Deals)
	lao.sleep(2)

	# Write LAO Deals Sheet ##########################################
	print(' Writing LAO Deals sheet...')
	lToExcelLAODeals = dMarketsLAODeals[mkt]
	with open('C:/TEMP/{0}.txt'.format(mkt), 'w') as ftxt:
		for element in lToExcelLAODeals:
			ftxt.write('{0}\n'.format(element))
	noRowsLAODeals = len(lToExcelLAODeals) + 2
	sht = xw.main.sheets.add('Active LAO Deals')
	df = pd.DataFrame(lToExcelLAODeals, columns=headerLAOProperties)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A1').value = '{0} Active LAO Deals'.format(mkt)
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatLAODealsSheet(mkt, wb, sht, noRowsLAODeals, noColLAODeals)
	lao.sleep(2)

	# Write Competitor Listings Sheet ##################################################
	print(' Writing Listings Deals sheet...')
	lToExcelCompetitorListings = dMarketsCompetitorListings[mkt]
	noRowsCompetitorListings = len(lToExcelCompetitorListings) + 2
	sht = xw.main.sheets.add('Competitor Listings')
	sht.range('A1').value = '{0} Competitor Listings'.format(mkt)
	df = pd.DataFrame(lToExcelCompetitorListings, columns=headerCompetitorListings)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatCompetitorListingsSheet(mkt, wb, sht, noRowsCompetitorListings, noColCompetitorListings, lBrochures)
	lao.sleep(2)

	# Write Comps Call List Sheet ##################################################
	print(' Writing Comps Call List sheet...')
	lToExcelCompsCallList = dMarketsCompsCallList[mkt]
	noRowsCompsCallList = len(lToExcelCompsCallList) + 2
	sht = xw.main.sheets.add('Comps Call Sheet')
	sht.range('A1').value = '{0} Comps Call Sheet'.format(mkt)
	df = pd.DataFrame(lToExcelCompsCallList, columns=headerCompsCallList)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatCompsCallListSheet(mkt, wb, sht, noRowsCompsCallList, noColsCompsCallList)
	lao.sleep(2)
	
	# Write Comps Sheet ##################################################
	print(' Writing Comps sheet...')
	lToExcelComps = dMarketsComps[mkt]
	noRowsComps = len(lToExcelComps) + 2
	sht = xw.main.sheets.add('Comps')
	sht.range('A1').value = '{0} Comps'.format(mkt)
	df = pd.DataFrame(lToExcelComps, columns=headerComps)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatCompsSheet(mkt, wb, sht, noRowsComps, noColsComps)
	lao.sleep(2)

	# Remove Sheet1, save and close
	sht1 = wb.sheets['Sheet1']
	sht1.delete()
	outFile = '{0}{1}_Land_Lot_Report_{2}.xlsx'.format(outFilePath, mkt, todaydate)
	wb.save(outFile)
	if selectedMarket == 'All':
		wb.close()
	lao.sleep(5)

	# External LLR ##################################################
	print(' Writing External Comps sheet...')
	lToExcelCompsExternal = dMarketsCompsExternal[mkt]
	noColsCompsExternal = len(lToExcelCompsExternal) + 2
	wb = xw.Book()
	sht = xw.main.sheets.add('LAO Land & Lot Report')
	sht.range('A1').value = '{0} Comps'.format(mkt)
	df = pd.DataFrame(lToExcelCompsExternal, columns=headerCompsExternal)  # Convert list of lists to a dataframe
	df = df.sort_values(by=['Classification', 'Submarket']) # Sort
	sht.range('A3').options(index=False, header=True).value = df
	xxl.formatCompsExternalSheet(mkt, wb, sht, noRowsComps, noColsCompsExternal)

	# Remove Sheet1, save and close
	sht1 = wb.sheets['Sheet1']
	sht1.delete()
	outFile = '{0}{1}_EXTERNAL_Land_Lot_Report_{2}.xlsx'.format(outFilePath, mkt, todaydate)
	wb.save(outFile)
	wb.close()
	lao.sleep(5)

exit('\n Fin')




	

