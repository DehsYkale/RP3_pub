# Calculates the land sales by sector for the Phx MO slide

import lao
import bb
import fun_login
from pprint import pprint
import fun_text_date as td

def get_sale_date_ranges():
	yrqtr = td.getDateQuarter(lastquarter=True)
	print(yrqtr)
	year_current = yrqtr[:4]
	year_last = int(year_current) - 1
	quarter = yrqtr[4:]
	print(year_current)
	print(year_last)
	print(quarter)
	if quarter == 'Q1':
		sale_date_start = f'{year_last}-04-01'
		sale_date_end = f'{year_current}-03-31'
	elif quarter == 'Q2':
		sale_date_start = f'{year_last}-07-01'
		sale_date_end = f'{year_current}-06-30'
	elif quarter == 'Q3':
		sale_date_start = f'{year_last}-11-01'
		sale_date_end = f'{year_current}-10-31'
	elif quarter == 'Q4':
		sale_date_start = f'{year_current}-01-01'
		sale_date_end = f'{year_current}-12-31'

	return sale_date_start, sale_date_end

service = fun_login.TerraForce()


lao.banner('MIMO Land Sales by Sector v04')

dSectors = {'Single Family': 0,
			'Multifamily': 0,
			'Industrial': 0,
			'Commercial': 0,
			'Ag Spec': 0,
			'Total': 0}
		
sale_date_start, sale_date_end = get_sale_date_ranges()

# TerraForce Query
fields = 'default'
# wc = "StageName__c LIKE 'Closed%' AND " \
# 	 "Sale_Date__c >= 2021-01-01 AND Sale_Price__c >= 10000 AND " \
# 	 "(County__c LIKE '%Maricopa%' OR County__c LIKE '%Pinal%') AND " \
# 	 "(RecordTypeId = '012a0000001ZSS5AAO' or RecordTypeId = '012a0000001ZSS8AAO')"

wc = "StageName__c LIKE 'Closed%' AND " \
	 "Sale_Date__c >= {0} AND Sale_Date__c <= {1} AND Sale_Price__c >= 10000 AND " \
	 "(County__c LIKE '%Maricopa%' OR County__c LIKE '%Pinal%') AND " \
	 "(RecordTypeId = '012a0000001ZSS5AAO' or RecordTypeId = '012a0000001ZSS8AAO')" \
	 .format(sale_date_start, sale_date_end)

results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=2, fields=fields)

for row in results:
	pprint(row)
	print(row['Classification__c'])
	print(row['Sale_Price__c'])
	exit()