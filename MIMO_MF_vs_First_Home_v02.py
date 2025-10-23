# Create table of AxioMetrics deliveries vs new homes under $350K

import lao
lao.banner('MIMO MF vs First Time Home v01')
import datetime
from pprint import pprint
import fun_text_date as td

today = td.today_date('slash')
print(today)
lToday = today.split('/')
today_year = int(lToday[2])
today_month = int(lToday[0])
today_day = int(lToday[0])
last_year_year = today_year - 1
# RL Brown updates on the 15 so factor that into the month
if today_day < 15:
	last_year_mo = today_month - 1
else:
	last_year_mo = today_month
last_12_mo_date = datetime.datetime(last_year_year, last_year_mo, 1)
print(last_12_mo_date)


dYears = {
	'2019': 0,
	'2020': 0,
	'2021': 0,
	'2022': 0,
	'2023': 0,
	'Last 12 Mo': 0
}

infile_COE = 'F:/Research Department/MIMO/zData/RL Brown/RLB COE Master Database.csv'
dRLB_COE = lao.spreadsheetToDict(infile_COE)

for row in dRLB_COE:
	line = dRLB_COE[row]

	if line['PRODCODE'] == 'Adult':
		continue

	# Sale Price below $350K
	if int(line['SALEPRICE']) > 350000:
		continue
	
	if line['COUNTY'] == 'PIMA':
		continue
	
	sale_date = td.convert_to_datetime(line['DATE'])
	sale_date_year = sale_date.strftime('%Y')

	for yr in dYears:
		if yr == 'Last 12 Mo':
			if sale_date > last_12_mo_date:
				dYears['Last 12 Mo'] = dYears['Last 12 Mo'] + 1
				break
		elif sale_date_year == yr:
			dYears[yr] = dYears[yr] + 1
			break

print(' Starter Home Sales (less than $350K)\n')
print(' 2019:       {0}'.format(dYears['2019']))
print(' 2020:       {0}'.format(dYears['2020']))
print(' 2021:       {0}'.format(dYears['2021']))
print(' 2022:       {0}'.format(dYears['2022']))
print(' 2023:       {0}'.format(dYears['2023']))
print(' Last 12 Mo: {0}'.format(dYears['Last 12 Mo']))

exit()

