#Formats the exported QTR_All_Data TF report for the Quarterly Review

# Import Libraries
import bb
import csv
import dicts
import fun_login
import lao
import os
import operator
from pprint import pprint
import sys
import fun_text_date as td

#Set Quarter using Date (DTE)
def setQuarterDate(date):
	YR = date[:4]
	MO = int(date[5:7])
	# print(YR)
	# print(MO)
	# exit()
	# YR = date.strftime('%Y')
	# MO = int(date.strftime('%m'))
	if MO <= 3:
		if '2010' in YR:
			return '2010 Q1'
		elif '2011' in YR:
			return '2011 Q1'
		elif '2012' in YR:
			return '2012 Q1'
		elif '2013' in YR:
			return '2013 Q1'
		elif '2014' in YR:
			return '2014 Q1'
		elif '2015' in YR:
			return '2015 Q1'
		elif '2016' in YR:
			return '2016 Q1'
		elif '2017' in YR:
			return '2017 Q1'
		elif '2018' in YR:
			return '2018 Q1'
		elif '2019' in YR:
			return '2019 Q1'
		elif '2020' in YR:
			return '2020 Q1'
		elif '2021' in YR:
			return '2021 Q1'
		elif '2022' in YR:
			return '2022 Q1'
		elif '2023' in YR:
			return '2023 Q1'
		elif '2024' in YR:
			return '2024 Q1'
		elif '2025' in YR:
			return '2025 Q1'
	elif 4 <= MO <= 6:
		if '2010' in YR:
			return '2010 Q2'
		elif '2011' in YR:
			return '2011 Q2'
		elif '2012' in YR:
			return '2012 Q2'
		elif '2013' in YR:
			return '2013 Q2'
		elif '2014' in YR:
			return '2014 Q2'
		elif '2015' in YR:
			return '2015 Q2'
		elif '2016' in YR:
			return '2016 Q2'
		elif '2017' in YR:
			return '2017 Q2'
		elif '2018' in YR:
			return '2018 Q2'
		elif '2019' in YR:
			return '2019 Q2'
		elif '2020' in YR:
			return '2020 Q2'
		elif '2021' in YR:
			return '2021 Q2'
		elif '2022' in YR:
			return '2022 Q2'
		elif '2023' in YR:
			return '2023 Q2'
		elif '2024' in YR:
			return '2024 Q2'
		elif '2025' in YR:
			return '2025 Q2'
	elif 7 <= MO <= 9:
		if '2010' in YR:
			return '2010 Q3'
		elif '2011' in YR:
			return '2011 Q3'
		elif '2012' in YR:
			return '2012 Q3'
		elif '2013' in YR:
			return '2013 Q3'
		elif '2014' in YR:
			return '2014 Q3'
		elif '2015' in YR:
			return '2015 Q3'
		elif '2016' in YR:
			return '2016 Q3'
		elif '2017' in YR:
			return '2017 Q3'
		elif '2018' in YR:
			return '2018 Q3'
		elif '2019' in YR:
			return '2019 Q3'
		elif '2020' in YR:
			return '2020 Q3'
		elif '2021' in YR:
			return '2021 Q3'
		elif '2022' in YR:
			return '2022 Q3'
		elif '2023' in YR:
			return '2023 Q3'
		elif '2024' in YR:
			return '2024 Q3'
		elif '2025' in YR:
			return '2025 Q3'
	elif 10 <= MO <= 12:
		if '2010' in YR:
			return '2010 Q4'
		elif '2011' in YR:
			return '2011 Q4'
		elif '2012' in YR:
			return '2012 Q4'
		elif '2013' in YR:
			return '2013 Q4'
		elif '2014' in YR:
			return '2014 Q4'
		elif '2015' in YR:
			return '2015 Q4'
		elif '2016' in YR:
			return '2016 Q4'
		elif '2017' in YR:
			return '2017 Q4'
		elif '2018' in YR:
			return '2018 Q4'
		elif '2019' in YR:
			return '2019 Q4'
		elif '2020' in YR:
			return '2020 Q4'
		elif '2021' in YR:
			return '2021 Q4'
		elif '2022' in YR:
			return '2022 Q4'
		elif '2023' in YR:
			return '2023 Q4'
		elif '2024' in YR:
			return '2024 Q4'
		elif '2025' in YR:
			return '2025 Q4'

# Set Region based on Submarket
def setSubmarket(sub, URL, DTE, LTY):
	sub = sub.upper()
	if 'ANTHEM' == sub:
		return 'NORTHEAST'
	elif 'APACHE JUNCTION' == sub:
		return 'SOUTHEAST'
	elif 'AVONDALE' == sub:
		return 'SOUTHWEST'
	elif 'AVONDALE-TOLLESON' == sub:
		return 'SOUTHWEST'
	elif 'CASA GRANDE' == sub:
		return 'PINAL COUNTY'
	elif 'CENTRAL' == sub:
		return 'NORTHEAST'
	elif 'COOLIDGE' == sub:
		return 'PINAL COUNTY'
	elif 'EAST BUCKEYE' == sub:
		return 'SOUTHWEST'
	elif 'ELOY' == sub:
		return 'PINAL COUNTY'
	elif 'ESTRELLA' == sub:
		return 'SOUTHWEST'
	elif 'FLORENCE' == sub:
		return 'PINAL COUNTY'
	elif 'GILBERT' == sub:
		return 'SOUTHEAST'
	elif 'GLENDALE' == sub:
		return 'NORTHWEST'
	elif 'GOODYEAR' == sub:
		return 'NORTHWEST'
	elif 'LAKE PLEASANT' == sub:
		return 'NORTHWEST'
	elif 'LAVEEN' == sub:
		return 'SOUTHWEST'
	elif 'MARICOPA' == sub:
		return 'PINAL COUNTY'
	elif 'MESA' == sub:
		return 'SOUTHEAST'
	elif 'MESA GILBERT' == sub:
		return 'SOUTHEAST'
	elif 'NORTH BUCKEYE' == sub:
		return 'SOUTHEAST'
	elif 'NORTH CENTRAL' == sub:
		return 'NORTHEAST'
	elif 'NORTH CHANDLER' == sub:
		return 'SOUTHEAST'
	elif 'NORTH GOODYEAR' == sub:
		return 'NORTHWEST'
	elif 'NORTH I17' == sub:
		return 'NORTHWEST'
	elif 'NORTH PEORIA' == sub:
		return 'NORTHWEST'
	elif 'NORTH PHOENIX' == sub:
		return 'NORTHEAST'
	elif 'NORTH PHOENIX SCOTTSDALE' == sub:
		return 'NORTHEAST'
	elif 'NORTH SURPRISE' == sub:
		return 'NORTHWEST'
	elif 'NORTHEAST' == sub:
		return 'NORTHEAST'
	elif 'NORTHWEST' == sub:
		return 'NORTHWEST'
	elif 'NORTHWEST MARICOPA COUNTY' == sub:
		return 'NORTHWEST'
	elif 'PECOS' == sub:
		return 'SOUTHEAST'
	elif 'PINAL EAST' == sub:
		return 'PINAL COUNTY'
	elif 'PINAL NORTH' == sub:
		return 'PINAL COUNTY'
	elif 'PINAL SOUTH' == sub:
		return 'PINAL COUNTY'
	elif 'PINAL WEST' == sub:
		return 'PINAL COUNTY'
	elif 'QUEEN CREEK' == sub:
		return 'SOUTHEAST'
	elif 'RAINBOW VALLEY' == sub:
		return 'SOUTHWEST'
	elif 'SHEA' == sub:
		return 'NORTHEAST'
	elif 'SOUTH CHANDLER' == sub:
		return 'SOUTHEAST'
	elif 'SOUTH MOUNTAIN' == sub:
		return 'SOUTHWEST'
	elif 'SOUTH PEORIA' == sub:
		return 'NORTHWEST'
	elif 'SOUTH SCOTTSDALE' == sub:
		return 'NORTHEAST'
	elif 'SOUTH SURPRISE' == sub:
		return 'NORTHWEST'
	elif 'SOUTHEAST MESA' == sub:
		return 'SOUTHEAST'
	elif 'SOUTHWEST' == sub:
		return 'SOUTHWEST'
	elif 'SOUTHWEST EAST' == sub:
		return 'SOUTHWEST'
	elif 'SOUTHWEST WEST' == sub:
		return 'SOUTHWEST'
	elif 'SUN CITIES' == sub:
		return 'NORTHWEST'
	elif 'TEMPE' == sub:
		return 'SOUTHEAST'
	elif 'TEMPE CHANDLER' == sub:
		return 'SOUTHEAST'
	elif 'TONOPAH' == sub:
		return 'SOUTHWEST'
	elif 'VERRADO' == sub:
		return 'SOUTHWEST'
	elif 'WEST BUCKEYE' == sub:
		return 'SOUTHWEST'
	elif 'WEST PHOENIX TOLLESON' == sub:
		return 'SOUTHWEST'
	elif 'WEST SURPRISE' == sub:
		return 'NORTHWEST'
	elif 'WITTMANN' == sub:
		return 'NORTHWEST'
	else:
		# missingField('SUBMARKET', URL, DTE, LTY)
		return ''

#Set Lot Type
def set_lot_type(lotType, URL, DTE, LTY):
	if 'Finished Lots' in lotType:
		return 'FINISHED LOT'
	elif 'Lot Option' in lotType:
		return 'FINISHED LOT'
	elif 'Platted' in lotType:
		return 'PI/P&E'
	elif 'Part' in lotType:
		return 'PI/P&E'
	elif 'Raw Acreage' in lotType:
		return 'ACREAGE'
	elif 'Developed' in lotType:
		return 'ACREAGE'
	elif 'MultiFamily' in lotType:
		return 'MULTIFAMILY'
	elif 'Covered Land' in lotType:
		return 'COVERED LAND'
	else:
		LTY = 'Missing'
		# missingField('LOT TYPE', URL, DTE, LTY)
		return ''

# Set Deal Classification
def set_classification(cls, URL, DTE, LTY):
	dClass = dicts.get_phx_raw_data_deal_classification_dict()

	lClass = cls.split(';')
	if len(lClass) == 2:
		if lClass[0] == 'Office' and lClass[1] == 'Retail':
			return 'COMMERCIAL'
		
		

	if len(lClass) > 1:
		# APARTMENT
		if 'Agricultural' in lClass and 'Speculative' in lClass:
			return 'AGRICULTURAL'
		
		# APARTMENT
		elif 'High Density Residential' in lClass and 'Apartment' in lClass:
			return 'APARTMENT'
		elif 'High Density Residential' in lClass and 'Apartment Horizontal' in lClass:
			return 'APARTMENT'
		
		# COMMERCIAL
		elif 'Industrial' in lClass and ('Retail' in lClass or 'Office' in lClass):
					return 'COMMERCIAL'
		elif 'Office' in lClass and 'Retail' in lClass and 'Mixed-Use' in lClass:
					return 'COMMERCIAL'
		elif 'Office' in lClass and 'Retail' in lClass and 'Storage' in lClass:
				return 'COMMERCIAL'
		elif len(lClass) == 2 and 'Office' in lClass and 'Storage' in lClass:
			return 'COMMERCIAL'
		elif 'Medical' in lClass and 'Mixed-Use' in lClass:
			return 'COMMERCIAL'
		elif len(lClass) == 2 and 'Retail' in lClass and 'School' in lClass:
			return 'COMMERCIAL'
		elif len(lClass) == 2 and 'Retail' in lClass and 'Speculative' in lClass:
			return 'COMMERCIAL'

		# INDUSTRIAL
		elif 'Agricultural' in lClass and 'Industrial' in lClass:
			return 'INDUSTRIAL'
		elif len(lClass) == 2 and 'Speculative' in lClass and 'Industrial' in lClass:
			return 'INDUSTRIAL'
		elif len(lClass) == 2 and 'Other' in lClass and 'Industrial' in lClass:
			return 'INDUSTRIAL'
		
		# RESIDENTIAL
		elif 'Agricultural' in lClass and 'Residential' in lClass:
			return 'RESIDENTIAL'
		elif 'Speculative' in lClass and 'Residential' in lClass:
			return 'RESIDENTIAL'
		elif 'Master Planned Community' in lClass:
			return 'RESIDENTIAL'
		elif len(lClass) == 2 and 'Single Family' in lClass and 'Speculative' in lClass:
			return 'RESIDENTIAL'
				
		# MIXED USE
		elif ('Office' in lClass or 'Retail' in lClass) and ('High Density Residential' in lClass or 'Residential' in lClass or 'Apartment Traditional' in lClass or 'Apartment Horizontal' in lClass):
			return 'MIXED USE'
		elif ('Office' in lClass or 'Retail' in lClass) and 'Mixed-Use' in lClass:
			return 'MIXED USE'

		
		# else:
		# 	assigned_class = '**NONE**'
		# 	for row in dClass:
		# 		if row in cls:
		# 			assigned_class = dClass[row]
		# 	with open('C:/TEMP/class.txt', 'a') as f:
		# 		cats = ', '.join(lClass)
		# 		f.write(f'{cats} > {assigned_class}\n')
	

	for row in dClass:
		if row in cls:
			return dClass[row]

	with open('C:/TEMP/class.txt', 'a') as f:
		f.write(f'{cls} > MISSING\n')
	return 'MISSING'

# Set Buyer Category
# AGRICULTURE, BANKS, COMMERCIAL, HOME BUILDER, INVESTOR, LAND BANK, MULTIFAMILY, OTHER
def set_buyer_type(cat, baa, URL, DTE, LTY):
	if baa == 'Homebuilder':
		return 'HOME BUILDER'
	elif baa == 'Inv/Dev':
		return 'INVESTOR'
	elif baa == 'Lot Banker':
		return 'LAND BANK'
	elif baa == 'User':
		return 'USER'
	elif any('Agricultural' in s for s in cat):
		return 'AGRICULTURE'
	elif any('Attorney' in s for s in cat):
		return 'OTHER'
	elif any('uilder' in s for s in cat):	# Homebuliders and Builders thus 'uilder'
		return 'HOME BUILDER'
	elif any('Commercial' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Dairy' in s for s in cat):
		return 'AGRICULTURE'
	elif any('Developer' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Hotel' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Industrial' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Multifamily' in s for s in cat):
		return 'APARTMENT'
	elif any('Apartment' in s for s in cat):
		return 'APARTMENT'
	elif any('Non-Profit' in s for s in cat):
		return 'OTHER'
	elif any('Office' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Other' in s for s in cat):
		return 'OTHER'
	elif any('Person' in s for s in cat):
		return 'INVESTOR'
	elif any('Retail' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Government' in s for s in cat):
		return 'OTHER'
	elif any('Lot Investor' in s for s in cat):
		return 'LAND BANK'
	elif any('Land Banker' in s for s in cat):
		return 'LAND BANK'
	elif any('Investor' in s for s in cat):
		return 'INVESTOR'
	elif any('Lender' in s for s in cat):
		return 'BANKS'
	elif any('Medical' in s for s in cat):
		return 'OTHER'
	elif any('Retail' in s for s in cat):
		return 'COMMERCIAL'
	elif any('Schools' in s for s in cat):
		return 'OTHER'
	elif any('Utility' in s for s in cat):
		return 'OTHER'
	else:
		# missingField('CATEGORY', URL, DTE, LTY)
		return ''

# Write missing fields to
def missingField(field, URL, date, LTY):
	YR = date.strftime('%Y')


# Terraforce Login
# service = bb.sfLogin()
service = fun_login.TerraForce()

lao.banner('MO Raw Data v04')

print(' Querying TerraForce for Phoenix Land Deals...please stand by.\n')
# TerraForce Query
fields = 'default'
wc = "StageName__c LIKE 'Closed%' AND " \
	 "Sale_Date__c >= 2018-01-01 AND Sale_Price__c >= 10000 AND " \
	 "(County__c LIKE '%Maricopa%' OR County__c LIKE '%Pinal%') AND " \
	 "(RecordTypeId = '012a0000001ZSS5AAO' or RecordTypeId = '012a0000001ZSS8AAO')"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

#[Date:0, Region:1, Lot Type:2, Classification:3, Category:4, $:5, Lots:6, Acres:7]

# Open the CSV to write records to
print('\n Starting data collection...')
# yearQtr = ('Folder Location:\nEnter Year & Quarter (YYYYQ# (2015Q4)) > ')).upper()
yearQtr = lao.getDateQuarter()
# filepath = 'F:/Research Department/MIMO/PowerPoints/Phoenix/{0} Market Overview/'.format(yearQtr)
filepath = 'F:/Research Department/MIMO/Spreadsheets/Phoenix/{0}/'.format(yearQtr)
with open('{0}MO_Raw_Data_{1}_unsorted.csv'.format(filepath, yearQtr), 'w', newline='') as f:
	QTROUT = csv.writer(f)
	c = 0	# counter set to zero

	# Create Deal record List
	deal = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

	for row in results:
		# pprint(row)
		# Skip large Pinal Grazing Lease Deal
		if row['PID__c'] == 'AZPinal209108':
			continue
		DID = row['Id']
		DNM = row['Name']
		PID = row['PID__c']
		URL = '=HYPERLINK("https://landadvisors.my.salesforce.com/%s", "%s")' % (DID, DNM)
		SUB = row['Submarket__c']
		PRC = row['Sale_Price__c']
		DTE = row['Sale_Date__c']
		LOT = row['Lots__c']
		LTY = row['Lot_Type__c']
		CLS = row['Classification__c']
		ACR = row['Acres__c']
		BAA = row['Buyer_Acting_As__c']
		print(DID)
		if ACR == 0 or ACR == '':
			# missingField('ACRES', URL, DTE, LTY)
			PPA = 0
		elif PRC == 0:
			# missingField('PRICE', URL, DTE, LTY)
			PPA = 0
		else:
			PPA = PRC / ACR
		# Set the Buyer Entity Category.
		# If Buyer is a Person then set Category to Investor
		if row['Offers__r']['records'][0]['Buyer_Entity__r'] != 'None':
			CAT = row['Offers__r']['records'][0]['Buyer_Entity__r']['Category__c']
		else:
			CAT = ['Investor']

		# Count the records
		c += 1
		print(c)

		# Assign Quarter Date
		deal[0] = setQuarterDate(DTE)

		# Assign Region
		deal[1] = setSubmarket(SUB, URL, DTE, LTY)

		# Assign Lot Type
		deal[2] = set_lot_type(LTY, URL, DTE, LTY)

		# Assign Classification
		deal[3] = set_classification(CLS, URL, DTE, LTY)

		# Assign Buyer Type
		deal[4] = set_buyer_type(CAT, BAA, URL, DTE, LTY)

		# Assign Price, Lot Count, Acres & Price per Acre
		deal[5] = float(PRC)
		deal[6] = LOT
		deal[7] = float(ACR)
		deal[8] = float(PPA)
		deal[9] = '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}","{1}")'.format(DID, PID)

		# Write record to the QTR_Review.csv
		QTROUT.writerow(deal)

# Sort the CSV
with open('{0}MO_Raw_Data_{1}_unsorted.csv'.format(filepath, yearQtr), 'r') as f, open('{0}MO_Raw_Data_{1}_sorted.csv'.format(filepath, yearQtr), 'w', newline='') as g:
	fin = csv.reader(f)
	fout = csv.writer(g)
	sortedcsv = sorted(fin, key=operator.itemgetter(0))
	header = ['Sale Qtr', 'Region', 'Lot Type', 'Classification', 'Category', 'Sale Price', 'Lots', 'Acres', '$/Acre', 'TF Link']
	fout.writerow(header)
	for row in sortedcsv:
		fout.writerow(row)

# open the QTR_Review.csv
os.startfile('{0}MO_Raw_Data_{1}_sorted.csv'.format(filepath, yearQtr))
lao.banner('MO Raw Data Builder')
td.instrMsg('1) Open the QTR Review 20##-Q# Graphs & Summaries.xlsx file')
td.instrMsg('   (F:\\Research Department\\Transfer Data\\Review\\QTR Review 20##-Q# Graphs & Summaries.xlsx\n')
td.instrMsg('2) Copy contents of QTR_Review.csv and Paste it into the "Raw Data" sheet of QTR Review 20##-Q# Graphs & Summaries.xlsx\nOverwriting existing 2017 and newer records.')

exit('\n fin')
