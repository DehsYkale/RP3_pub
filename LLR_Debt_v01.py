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
outFilePath = 'F:/Research Department/Lot Comps Components/'
todaydate = td.today_date()
headerDebtList = dicts.get_debt_header_list()
noColsDebtList= len(headerDebtList)

# TerraForce Query ##################################################
print('\n Querying TerraForce...')
fields = 'default'
wc = "Loan_Amount__c > 1 and Sale_Date__c > {0}".format('2019-01-01')
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

lToExcelDebtList = []
print(msg := '\n Creating Debt List...')
for dLine in results:
	lLine = xxl.llr_debt_list_line_maker(dLine)
	lToExcelDebtList.append(lLine)

# Write Debt Sheet ##################################################
print(msg := '\n Creating Excel file...')
wb = xw.Book()
noRowsDebtList = len(lToExcelDebtList) + 2
sht = xw.main.sheets.add('Debt')
sht.range('A1').value = 'Debt LAO Markets'
df = pd.DataFrame(lToExcelDebtList, columns=headerDebtList)  # Convert list of lists to a dataframe
df = df.sort_values(by=['Market', 'LAO Deal']) # Sort
sht.range('A3').options(index=False, header=True).value = df
xxl.formatDebtListSheet(wb, sht, noRowsDebtList, noColsDebtList)
lao.sleep(2)

# Remove Sheet1, save and close ####################################
sht1 = wb.sheets['Sheet1']
sht1.delete()
outFile = '{0}Debt_LAO_Markets_Land_Lot_Report_{1}.xlsx'.format(outFilePath, todaydate)
wb.save(outFile)
# wb.close()
lao.sleep(5)
exit('\n Fin')


