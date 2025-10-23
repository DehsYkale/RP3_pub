# Scrapes Census Permit data for last 12 months for LAO markets
# totals Single Family and MultiFamily permits

import csv
import datetime
import fun_text_date as td
from subprocess import Popen
import urllib
import lao
from urllib.request import urlopen
from urllib.error import HTTPError
import xlrd
from pprint import pprint
import fun_text_date as td

def makeMSADict():
	return {'Albuquerque': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Atlanta-Sandy Springs': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Austin-Round Rock': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Boise City': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Charlotte-Concord': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Dallas-Fort Worth': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Denver-Aurora': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Flagstaff': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Greenville-Anderson': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Houston': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Huntsville': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Jacksonville': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Kansas City': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Las Vegas': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Nashville': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Ogden': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Orlando': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Phoenix': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Prescott': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Provo-Orem': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Reno': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Riverside':{'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Sacramento': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Salt Lake City': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Sarasota': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Seattle': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Spartanburg': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Tampa-St. Petersburg': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		'Tucson': {'sfrpre': 0, 'sfr': 0, 'mf': 0}}
		# }
		# 'Miami-Fort Lauderdale': {'sfrpre': 0, 'sfr': 0, 'mf': 0}}

		# 'Charleston-North Charleston': {'sfr': 0, 'mf': 0},
		# 'Columbia, SC': {'sfr': 0, 'mf': 0},
		# 
		# 'Durham-Chapel Hill': {'sfr': 0, 'mf': 0},
		# 'Greensboro-High Point': {'sfr': 0, 'mf': 0},
		# 'Greenville-Anderson-Mauldin': {'sfr': 0, 'mf': 0},
		# 'Kansas City': {'sfrpre': 0, 'sfr': 0, 'mf': 0}}
		# 'Los Angeles-Long Beach-Anaheim': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		# 'Myrtle Beach-Conway-North Myrtle Beach': {'sfr': 0, 'mf': 0}}
		# 'Portland-Vancouver-Hillsboro': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		# 'Sacramento--Roseville--Arden-Arcade': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		# 'San Diego-Carlsbad': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		# 'San Francisco-Oakland-Hayward': {'sfrpre': 0, 'sfr': 0, 'mf': 0},
		# 'Winston-Salem': {'sfr': 0, 'mf': 0},

def get_starting_yearMonth_and_lastmonth():

	print('\n Getting the staring yearMonth and last month...')
	today = datetime.date.today()
	first = today.replace(day=1)
	lastmonth = first - datetime.timedelta(days=1)
	yearMonth = lastmonth.strftime('%Y%m')
	# xlsurl = 'https://www.census.gov/construction/bps/xls/msamonthly_{0}.xls'.format(yearMonth)
	xlsurl = 'https://www.census.gov/construction/bps/xls/cbsamonthly_{0}.xls'.format(yearMonth)
	# print(yearMonth)
	# Check if current month or previous month
	try:
		urllib.request.urlretrieve(xlsurl, 'C:/TEMP/permitsTemp.xls')
	except HTTPError:
		td.warningMsg('*** No data for current year/month {0}, starting with previous month. ***\n'.format(yearMonth))
		first = lastmonth.replace(day=1)
		lastmonth = first - datetime.timedelta(days=1)
		yearMonth = lastmonth.strftime('%Y%m')

	print(f' Starting yearMonth: {yearMonth}')
	print(f' Last month: {lastmonth}\n')
	return yearMonth, lastmonth

# Get the Census permits data from the XLS files
def get_census_permits_dict():

	# Check if permits XLS file exists on F drive
	file_name = f'{permits_xls_folder}cbsamonthly_{yearMonth}.xls'
	file_exists = lao.does_file_exists(file_name)
	# If not download the file
	if file_exists is False:
	# Format changed for 2024
		xlsurl = 'https://www.census.gov/construction/bps/xls/cbsamonthly_{0}.xls'.format(yearMonth)
		# urllib.request.urlretrieve(xlsurl, 'C:/TEMP/permitsTemp.xls')
		urllib.request.urlretrieve(xlsurl, file_name)

	xl_wb = xlrd.open_workbook(file_name)
	xl_sheet = xl_wb.sheet_by_index(0)
	# Format changed for 2024
	# if '2024' in yearMonth:
	# 	colcount = 9
	# else:
	# 	colcount = 8
	colcount = 9
	header = []
	for i in range(2, colcount):
		header.append(xl_sheet.cell_value(7, i))
	index = 0
	dSht = {}
	for row_idx in range(9, xl_sheet.nrows):
		index += 1
		dSht[index] = {}
		for i in range(0, 7):
			dSht[index][header[i].upper()] = xl_sheet.cell_value(row_idx, i+2)

	return dSht

lao.banner('MO Census Permits Last 12 Months v02')
fTemp_permits = 'C:/TEMP/permitsTemp.xls'
permits_xls_folder = 'F:/Research Department/MIMO/zData/Permits/Census Permits by MSA/Monthly/'
yearMonth, lastmonth = get_starting_yearMonth_and_lastmonth()

dMSAs = makeMSADict()

for i in range(1, 25):  # 12 Months
	print(yearMonth)
	if int(yearMonth) > 201910:
		dPermits = get_census_permits_dict()
		for permit in dPermits:
			p = dPermits[permit]
			for msa in dMSAs:
				if msa in p['NAME']:
					sfr = int(p['1 UNIT'])
					mf = int(p['2 UNITS']) + int(p['3 AND 4 UNITS']) + int(p['5 UNITS OR MORE'])

					if i <= 12:  # Last 12 Months
						dMSAs[msa]['sfr'] = dMSAs[msa]['sfr'] + sfr
						dMSAs[msa]['mf'] = dMSAs[msa]['mf'] + mf
					else: # Previous 12 Months
						dMSAs[msa]['sfrpre'] = dMSAs[msa]['sfrpre'] + sfr
	else:
		urlCensus_permits = 'F:/Research Department/MIMO/zData/Permits/Census Permits by MSA/tb3u{0}.txt'.format(yearMonth)
		with open(urlCensus_permits, 'r') as f:
			Lines = f.readlines()
		lao.sleep(1)  # Wait for page to load
		for line in Lines:
			for msa in dMSAs:
				print(msa)
				if msa in line:
					if 'Houston' in msa:
						start = len(msa.split()) + 5
					else:
						start = len(msa.split()) + 4
					# Deal with two line entries in text file
					data = line.split()
					sfr = int(data[start])
					mf = int(data[start+1]) + int(data[start+2]) + int(data[start+3]) + int(data[start+4])
					if i < 13:
						dMSAs[msa]['sfr'] = dMSAs[msa]['sfr'] + sfr
						dMSAs[msa]['mf'] = dMSAs[msa]['mf'] + mf
					else:
						dMSAs[msa]['sfrpre'] = dMSAs[msa]['sfrpre'] + sfr
	first = lastmonth.replace(day=1)
	lastmonth = first - datetime.timedelta(days=1)
	yearMonth = lastmonth.strftime('%Y%m')

print('\n')

# Writer to CSV
with open('C:/TEMP/PermitsLAOMarketsLast12MoUNSORTED.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	# Salt Lake City area MSAs
	lSLC_msa = ['Provo-Orem', 'Ogden', 'Salt Lake City']
	# Salt Lake City variables
	slc_sfr, slc_mf, slc_sfrpre = 0, 0, 0
	# Cycle through MSAs and write to CSV
	for msa in dMSAs:
		# Check if MSA is in Salt Lake City area
		if msa in lSLC_msa:
			slc_sfr = slc_sfr + dMSAs[msa]['sfr']
			slc_mf = slc_mf + dMSAs[msa]['mf']
			slc_sfrpre = slc_sfrpre + dMSAs[msa]['sfrpre']
		else:
			fout.writerow([msa, dMSAs[msa]['sfrpre'], dMSAs[msa]['sfr'], dMSAs[msa]['mf']])

	# Write Salt Lake City totals
	fout.writerow(['Salt Lake City', slc_sfrpre, slc_sfr, slc_mf])

# Sort
with open('C:/TEMP/PermitsLAOMarketsLast12MoUNSORTED.csv', 'r') as f:
	fin = csv.reader(f)
	sortedlist = sorted(fin, key=lambda row: row[0])

# Final csv with PHX and TUC at the end
with open('C:/TEMP/PermitsLAOMarketsLast12Mo.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(['Market', 'Previous Year SFR', 'Single Family', 'MultiFamily'])
	for row in sortedlist:
		if row[0] == 'Phoenix':
			rowPHX = row
		elif row[0] == 'Tucson':
			rowTUC = row
		else:
			fout.writerow(row)
	fout.writerow(['', '', '', ''])
	fout.writerow(rowPHX)
	fout.writerow(rowTUC)


# Open in Excel
p = Popen('C:/TEMP/PermitsLAOMarketsLast12Mo.csv', shell=True)

exit('\n Fin')