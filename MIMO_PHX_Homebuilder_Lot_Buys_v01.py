# Calaculates the number of lots Homebuilders buy annually and for the last 12 months.

import lao
lao.banner('PHX Homebuilder Lot Buys v01')

import bb
import fun_login
import fun_text_date as td
from pprint import pprint

def get_hb_lot_buy_records():
	
	print(' Querying Terraforce...')
	# Build Lot Types, Classifications and BAA
	lot_types = "'Finished Lots', 'Initial Lot Option', 'Lot Option Built Out', 'Partially Improved', 'Platted and Engineered'"
	classification = "'Build For Rent (platted)', 'High Den Res', 'Residential', 'Master Planned Community', 'Medium Density Residential'"
	buyer_acting_as = "Homebuilder"

	# Build where clause
	# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
	# "RecordTypeId = '012a0000001ZSS5AAO' " \
	# 	"AND " \
	# 		"Lot_Type__c IN ({0}) " \
	# 	"AND " \
	wc = "Sale_Price__c >= 10000 " \
		"AND " \
		"StageName__c LIKE 'Closed%' " \
		"AND " \
		"Sale_Date__c >= 2017-01-01 " \
		"AND " \
		"OPR_Sent__c != 1970-01-01 " \
		"AND " \
		"County__c IN ('Maricopa', 'Pinal')" \
		"AND " \
		"Classification__c INCLUDES ({0}) " \
		"AND " \
		"Buyer_Acting_As__c = '{1}'" \
		.format(classification, buyer_acting_as)
		
	# TerraForce Query
	fields = 'default'
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	return results

# Get the date range of the current quarter
def get_current_qtr_date_range():
	yr = cur_qtr[:4]
	yr_last = int(yr) - 1
	qtr = cur_qtr[4:]
	if qtr == 'Q1':
		yr_start = f'{yr_last}-04-01'
		yr_end = f'{yr}-03-31'	
	elif qtr == 'Q2':
		yr_start = f'{yr_last}-07-01'
		yr_end = f'{yr}-06-30'
	elif qtr == 'Q3':
		yr_start = f'{yr_last}-10-01'
		yr_end = f'{yr}-09-30'
	elif qtr == 'Q4':
		yr_start = f'{yr}-01-01'
		yr_end = f'{yr}-12-31'
		
	return yr_start, yr_end

service = fun_login.TerraForce()

cur_qtr = td.getDateQuarter()
yr_current = int(cur_qtr[:4])
yr_range_last = yr_current + 1

results = get_hb_lot_buy_records()



dLots = {}
# Cycle through years
for yr in range(2017, yr_range_last):
	# print(yr)
	# print(yr_current)
	if yr == yr_current:
		print('here1')
		yr_start, yr_end = get_current_qtr_date_range()
	else:
		yr_start = f'{yr}-01-01'
		yr_end = f'{yr}-12-31'
	# print(yr)
	# Add year to dLots dict
	dLots[yr] = 0

	# Cycle through TF query results
	count = 0
	for row in results:
		# pprint(row)
		

		sale_date = row['Sale_Date__c']
		# Filter by Year
		if sale_date >= yr_start and sale_date <= yr_end:
			count += 1

			# print(row['PID__c'])
			# print(row['Lot_Type__c'])
			# print(row['Classification__c'])
			# print(count)
			# Create Lot Details Dict
			try:
				dLot_details = row['Lot_Details__r']['records']
				lot_details_exist = True
			except TypeError:
				# print(row['PID__c'])
				dLots[yr] = dLots[yr] + row['Lots__c']
				lot_details_exist = False
			
			if lot_details_exist:
				for rec in dLot_details:
					dLots[yr] = dLots[yr] + rec['Lot_Count__c']
	# print('here1')
	# break

for k, v in dLots.items():
    print(k, v)
