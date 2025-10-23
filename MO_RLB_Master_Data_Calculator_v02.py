#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Calcualte all data from RL Brown


import lao
import rlb
import fun_text_date as td
from pprint import pprint

# Print Data to be copied to MO Spreadsheet and MO PowerPoint
def printDataForMOSpreadsheet():
	lao.banner('MO RLB Master Data Calculator')
	# PHX XLSX PERMITS HBACA
	td.warningMsg('\n   Permits  : Update from HBACA')
	td.instrMsg('\n    1. Open latest HBACA spreadsheet located at: ')
	td.instrMsg('\n          F:/BRinehart/News-Reports/HBACA')
	td.instrMsg('\n    2. Copy permits by Market for last 3 months into columns')
	td.colorText('         Worksheet: HBACA Permits (purple)', 'PURPLE')
	lao.holdup()
	td.instrMsg('\n    3. Adjust "YTD" sum range for last year and this year for Apache Junction')
	td.instrMsg('\n         a) Copy down for cells of all cities')
	lao.holdup()
	td.instrMsg('\n    4. Adjust "12 Mo" sum range for last year and this year for Apache Junction')
	td.instrMsg('\n         a) Copy down for cells of all cities')
	lao.holdup()
	td.instrMsg('\n    5. Confirm "12 Mo Current Year" total is populated/matches value in Top HB Permits WS')
	td.colorText('         Worksheet: Top HB Permits (red)', 'RED')
	print('         Cell: row "Total Permits" L:38')
	lao.holdup()

	# PHX XLSX ACTIVE ADULT PERMITS
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Copy to PHX MO Spreadsheet\n')
	td.warningMsg('   Total Permits  : {0:.0f}'.format(dRLB['NEW_PHX_ACTV_ADULT_PERMITS']))
	td.colorText('   Worksheet: Actv Adult Permits (purple)', 'PURPLE')
	print('   Cell: Row "Last 12 Mo" column B')
	lao.holdup()
	td.instrMsg('\n Copy to PHX MO PowerPoint\n')
	td.warningMsg('   Copy Actv Adult Permits chart to slide')
	print('   Slide: Active Adult Community Permits')
	lao.holdup()
	td.warningMsg('\n   Update percentage of Active Adult Permits in right side box with "Pct Adult" value from WS')
	print('   Slide: Active Adult Community Permits')
	lao.holdup()

	# PHX XLSX HOUSING SALES
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Copy to PHX MO Spreadsheet\n')
	td.warningMsg('\n   $ Resale  : {0:.0f}'.format(dRLB['RESALE_PHX_MEDIAN_PRICE']))
	td.warningMsg('   $ New     : {0:.0f}'.format(dRLB['NEW_PHX_MEDIAN_PRICE']))
	td.warningMsg('   # Resale  : {0:.0f}'.format(dRLB['RESALE_PHX_COUNT']))
	td.warningMsg('   # New     : {0:.0f}'.format(dRLB['NEW_PHX_COUNT']))
	td.colorText('   Worksheet: Housing Sales (pink)', 'PINK')
	print('   Cell: row "Last 12" columns B to E')
	lao.holdup()
	td.instrMsg('\n Copy to PHX MO PowerPoint\n')
	td.warningMsg('   Copy Housing Sales chart to slide')
	print('   Slide: New & Resale Home Sales & Median Prices')
	lao.holdup()

	# PHX PPTX RESALE MEDIAN PRICE, SIZE, $/SQFT, $ VOLUME
	td.instrMsg('\n Copy data right side boxes of the MO PowerPoint\n')
	print('   Slide: New & Resale Home Sales & Median Prices')
	td.warningMsg('\n   Resale Homes Box (yellow green)')
	print('   Median Price:      {0:,.0f}'.format(dRLB['RESALE_PHX_MEDIAN_PRICE']))
	print('   Median Size:       {0:,.0f}'.format(dRLB['RESALE_PHX_MEDIAN_SQFT']))
	print('   $/SqFt:            {0:.0f}'.format(dRLB['RESALE_PHX_PRICE_SQFT']))
	print('   12 Mo Volume:      {0:,.0f}'.format(dRLB['RESALE_PHX_COUNT'] ))
	lao.holdup()

	print('\n   Slide: New & Resale Home Sales & Median Prices')
	td.warningMsg('   New Homes Box on right (LAO blue)')
	print('   Median Price:           {0:,.0f}'.format(dRLB['NEW_PHX_MEDIAN_PRICE']))
	print('   Median Size:            {0:,.0f}'.format(dRLB['NEW_PHX_MEDIAN_SQFT']))
	print('   Median New Home $/SqFt: {0:.0f}'.format(dRLB['NEW_PHX_PRICE_SQFT'] ))
	print('   Total Sales           : {0:,.0f}'.format(dRLB['NEW_PHX_COUNT'] ))
	lao.holdup()

	# PHX XLSX TOTAL NEW HOME SALES
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Confirm Total COE number in Top HB COE WS\n')
	td.warningMsg('\n   Total Sales  : {0:.0f}'.format(dRLB['NEW_PHX_COUNT']))
	td.colorText('   Worksheet: Top HB COE (red)', 'RED')
	print('   Cell: Total COE F:36')
	lao.holdup()

	# PHX XLSX TOTAL NEW HOME SALES
	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg('\n Copy to PHX MO Spreadsheet\n')
	td.warningMsg('\n   Total Sales  : {0:.0f}'.format(dRLB['NEW_PHX_TOTAL_REVEUE']))
	td.warningMsg('   Avg Price    : {0:.0f}'.format(dRLB['NEW_PHX_AVG_PRICE']))
	td.colorText('   Worksheet: Top HB Avg Hm Price (red)', 'RED')
	print('   Cell: Total COE F:4 & F:5')
	lao.holdup()

	lao.banner('MO RLB Master Data Calculator')
	td.instrMsg(' Copy to Market Insights spreadsheet for PIN')
	print('\n Pinal County COE Home Price & Count')
	print('   Pinal Resale Median Price:  {0:,.0f}'.format(dRLB['RESALE_PIN_MEDIAN_PRICE']))
	print('   Pinal COE Median Price:     {0:,.0f}'.format(dRLB['NEW_PIN_MEDIAN_PRICE']))
	print('   Pinal Resale Count:         {0:,.0f}'.format(dRLB['RESALE_PIN_COUNT']))
	print('   Pinal COE Count:            {0:,.0f}'.format(dRLB['NEW_PIN_COUNT'] ))
	lao.holdup()

lao.banner('MO RLB Master Data Calculator')

# Assemble dicts
dCOE, dPermits, dResale, fileDate = rlb.getRLBData()

# Assemble RLB dict
dRLB = rlb.housingSales(dCOE, dResale, fileDate)

# Add Active Adult Permits to RLB dict
dRLB = rlb.activeAdultPermits(dPermits, dRLB)

# Print the data to be entered into the PHX MO Spreadsheet
printDataForMOSpreadsheet()

# Make Home Price Range csv
rlb.homePriceRanges(dCOE, dResale)

# Make New Home Count, Avg Price/Units & HB Revenue lists for csv
lHBCOE, lHBAvgPriceUnits, lHBRevenue = rlb.make_builder_salesvolume_homessold_avgprice(dCOE)

# Make Permits list for csv
lHBPermits = rlb.make_builder_permits(dPermits)

# Make Active Subdivisions by HB list for csv
lHBActiveSubs = rlb.make_builder_acitve_subs(dCOE, dPermits)

# Create csv of data for PHX MO Spreadsheet
rlb.make_hb_results_csv(lHBPermits, lHBCOE, lHBAvgPriceUnits, lHBRevenue, lHBActiveSubs)

lao.banner('MO RLB Master Data Calculator')
exit('\n Fin') 
