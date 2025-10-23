# Scrapes Zonda (MetroStudy) spreadsheets for Annual Starts, Closings and VDL

import lao
import csv
from glob import glob
import fun_text_date as td
import os.path
from pprint import pprint



def get_avg_home_pricing(market):
	pdfFileObj, pdf_objcet, intPages = td.open_pdf(f'F:/Research Department/MIMO/zData/Metrostudy/{market}_Qtrly_Plan_Sum_Builder_{year_qtr}.pdf')
	# pdfFileObj, pdf_objcet, intPages = td.open_pdf(f'F:/Research Department/MIMO/zData/Metrostudy/DEN_Qtrly_Plan_Sum_Builder_2023Q4.pdf')

	intLastPage = intPages-1
	pageObj = pdf_objcet.pages[intLastPage]

	# extracting text from page
	pageText = pageObj.extract_text()
	lPageText = pageText.split('\n')
	lMarket_avg_home_pricing = []
	index_start = lPageText.index('Averages')+4
	for val in range(index_start, index_start+12, 3):
		avg_home_price = lPageText[val].replace('$', '').replace(',', '')
		price_per_sf = lPageText[val+2].replace('$', '')
		lMarket_avg_home_pricing.append([avg_home_price, price_per_sf])

	return lMarket_avg_home_pricing

lao.banner('Zonda Starts Closings VDL Formatter v01')

year_qtr = td.getDateQuarter(lastquarter=True)
print(f' Calculating for quarter: {year_qtr}')
# Calculate start_scraping_date
yr = int(year_qtr[2:4]) - 1
qtr = int(year_qtr[-1]) + 1
if qtr == 5:
	qtr = 1
	yr = yr + 1
start_scraping_date = f'{qtr}Q{yr}'

# Check for missing MetroStudy reports
lao.metrostudy_reports_exist(year_qtr)

# Get list of Zonda Historical Housing Activity files
lHistoriacl_Housing_Activity_Files = glob('F:/Research Department/MIMO/zData/Metrostudy/*_HistoricalHousingActivity_{0}.xls'.format(year_qtr))
# pprint(lHistoriacl_Housing_Activity_Files)

# Create temp file for data
header = ['Quarter', 'Annual Starts', 'Annual Close', 'Vacant Dev Lots', 'MO Supply', 'Avg Price', 'Price per SF']
with open('C:\TEMP\Zonda_HistoricalHousingActivity_Data.csv', 'w', newline='') as f:
	fout = csv.writer(f)

	for filename in lHistoriacl_Housing_Activity_Files:
		market = filename[45:48]
		print('here1')
		print(filename)
		print(market)
		# Get average home pricing
		lMarket_avg_home_pricing = get_avg_home_pricing(market)
		# pprint(lMarket_avg_home_pricing)
		# exit()
		
		# if market != 'SAC' and market != 'IEP':
		# 	continue
		market_header = [market, '', '', '', '', '', '']
		print(market)

		# filepathname = 'F:/Research Department/MIMO/zData/Metrostudy/IEP_HistoricalHousingActivity_2023Q2.xls'

		dZonda = lao.spreadsheetToDict(filename)

		fout.writerow(market_header)
		fout.writerow(header)
		start_scraping = False
		count_home_pricing_list = 0
		for row in dZonda:
			dLine = dZonda[row]
			
			if dLine == {}:
				continue
			# if dLine['Quarter'] == '2Q23':
			if dLine['Quarter'] == start_scraping_date:
				start_scraping = True

			if start_scraping:
				# Assign home pricing variables
				AvgHomePrice = lMarket_avg_home_pricing[count_home_pricing_list][0]
				PricePerSF = lMarket_avg_home_pricing[count_home_pricing_list][1]
				lRow = []
				# Exceptions for PHX & TUC
				if market == 'PHX' or market == 'TUC':
					lRow.append(dLine['Quarter'])
					lRow.append('Use RLB')
					lRow.append('Use RLB')
					lRow.append(dLine['VDLInv (VDL)'])
					lRow.append(dLine['VDLMos'])
					lRow.append('Use RLB')
					lRow.append('Use RLB')
				else:
					lRow.append(dLine['Quarter'])
					lRow.append(dLine['AnnStarts'])
					lRow.append(dLine['AnnClosings'])
					lRow.append(dLine['VDLInv (VDL)'])
					lRow.append(dLine['VDLMos'])
					lRow.append(AvgHomePrice)
					lRow.append(PricePerSF)
				fout.writerow(lRow)
				count_home_pricing_list += 1

lao.openFile('C:\TEMP\Zonda_HistoricalHousingActivity_Data.csv')

