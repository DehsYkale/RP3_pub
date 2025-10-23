# Create Debt LLR

import bb
import csv
import dicts
import lao
import fun_login
import fun_text_date as td
import pandas as pd
from pprint import pprint
import xlwings as xw
import xxl

lao.banner('LLR Debt v01')
service = fun_login.TerraForce()
todaydate = td.today_date()


# TerraForce Query ##################################################
print('\n Querying TerraForce...')
fields = 'default'
wc = "Loan_Amount__c > 1 and Sale_Date__c > {0}".format('2019-01-01')
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=10, fields=fields)

lToExcelDebtList = []
print(msg := '\n Creating Debt List...')
for dLine in results:
	lLine = xxl.llr_debt_list_line_maker(dLine)
	lToExcelDebtList.append(lLine)

# Create Excel workbook #############################################
print('\n Creating Excel file...')
wb = xw.Book()

# Tax Delinquent Sheet ####################################################
print('\n Creating Tax Delinquent Sheet...')
folder_tax_delinquent = 'F:/Research Department/MIMO/zData/Debt/Tax Delinquent/'
header_tax_delinquent = dicts.get_tax_delinquent_header_list()
noCols_tax_delinquent_list = len(header_tax_delinquent)
file_name_td = 'LAO Markets Tax Delinquent Properties 2024-10-04.csv'
# Create list of lists from the csv file
dTax_delinquent = dicts.spreadsheet_to_dict(f'{folder_tax_delinquent}{file_name_td}')
lTax_delinquent = []
for row in dTax_delinquent:
	lLine = xxl.llr_debt_tax_delinquent_line_maker(dTax_delinquent[row])
	lTax_delinquent.append(lLine)
	
noRows_tax_delinquwent_list = len(lTax_delinquent) + 2
sht = xw.main.sheets.add('Tax Delinquent')
sht.range('A1').value = 'Tax Delinquent - 1 Year PLus - LAO Markets'
df = pd.DataFrame(lTax_delinquent, columns=header_tax_delinquent)  # Convert list of lists to a dataframe
df = df.sort_values(by=['State', 'Market']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.format_tax_delinquetn_sheet(wb, sht, noRows_tax_delinquwent_list, noCols_tax_delinquent_list)

# Write Debt Sheet ##################################################
print('\n Creating Debt Sheet...')
outFilePath = 'F:/Research Department/Lot Comps Components/'
header_debt_list = dicts.get_debt_header_list()
noCols_debt_list= len(header_debt_list)
noRowsDebtList = len(lToExcelDebtList) + 2
sht = xw.main.sheets.add('Debt')
sht.range('A1').value = 'Debt LAO Markets'
df = pd.DataFrame(lToExcelDebtList, columns=header_debt_list)  # Convert list of lists to a dataframe
df = df.sort_values(by=['Market', 'LAO Deal']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.formatDebtListSheet(wb, sht, noRowsDebtList, noCols_debt_list)
lao.sleep(2)

# Remove Sheet1, save and close ####################################
sht1 = wb.sheets['Sheet1']
sht1.delete()
outFile = '{0}Debt_LAO_Markets_Land_Lot_Report_{1}.xlsx'.format(outFilePath, todaydate)
wb.save(outFile)
# wb.close()
lao.sleep(5)
exit('\n Fin')


