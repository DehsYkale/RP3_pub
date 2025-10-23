import lao
import bb
import csv
import dicts
import how
from pprint import pprint
import datetime
from glob import glob
import fun_text_date as td

how.axio_intro()
lao.banner('MO Axio MF Data v03')
pathAxio = lao.getPath('axio')
yrqtr = lao.getDateQuarter(lastquarter=True)
inXLSXfiles = glob('{0}*{1}.xlsx'.format(pathAxio, yrqtr))
yrCurrent = yrqtr[:4]
qtrCurrent = yrqtr[-1:]
yrqtrCurrent = '{0}Q{1}'.format(yrqtr[-1:], yrqtr[2:4])
print(f' Year: {yrCurrent}\n Qtr:  {qtrCurrent}\n YrQt: {yrqtrCurrent}\n')

dMaster = {}

for xls in inXLSXfiles:

	# skip open temp files
	if '$' in xls:
		continue

	# Get market from file name
	market = xls[46:49]
	print('\n {0}'.format(market))
	dMaster[market] = {}
	dTemp = dicts.spreadsheet_to_dict(xls)
	# Build Axio dict with yr qtr as primary key
	dAxio = {}
	for row in dTemp:
		r = dTemp[row]
		try:
			if r['Submarket'] == 'Market':
				dAxio[r['Quarterly']] = r
		except KeyError:
			pprint(r)
			exit()

	for i in range(14, 26): # 2014 to 2024
		# i = str(i)
		year = f'20{i}'
		# Get last 4 quarters
		# If not 4th quarter of current year
		if year == yrCurrent and qtrCurrent != '4':
			absorption = dAxio[yrqtrCurrent]['Demand (Qtrly Sum)']
			deliveries = dAxio[yrqtrCurrent]['New Supply (Qtrly Sum)']
			occupancy = '{0}%'.format(dAxio[yrqtrCurrent]['Occupancy'] * 100)
			rentgrowth = '{0}%'.format(dAxio[yrqtrCurrent]['Annual Avg Effective Rent Growth'] * 100)
		# If 4th quarter
		else:
			rYrQtr4 = f'4Q{i}'
			absorption = dAxio[rYrQtr4]['Demand (Qtrly Sum)']
			deliveries = dAxio[rYrQtr4]['New Supply (Qtrly Sum)']
			occupancy = '{0}%'.format(dAxio[rYrQtr4]['Occupancy'] * 100)
			rentgrowth = '{0}%'.format(dAxio[rYrQtr4]['Annual Avg Effective Rent Growth'] * 100)
		
		if year == yrCurrent and qtrCurrent != '4':
			dMaster[market]['Last 12 Mo'] = [absorption, deliveries, occupancy, rentgrowth]
			# if qtrCurrent == '1':
			# 	td.warningMsg(' Have Bill change MO_Axio_MF_Data_v03.py to include Last 12 Mo')
			# 	ui = td.uInput('\n Continue [00]... > ')
			# 	if ui == '00':
			# 		exit('\n Terminating program...')
		else:
			dMaster[market][year] = [absorption, deliveries, occupancy, rentgrowth]

	# pprint(dMaster)

# Create Market Header
lMarkets, lhdrMarket, lhrdFields, l2014, l2015, l2016, l2017, l2018, l2019, l2020, l2021, l2022, l2023, l2024, lLast12Mo = [], ['Market'], ['Year'], ['2014'], ['2015'], ['2016'], ['2017'], ['2018'], ['2019'], ['2020'], ['2021'], ['2022'], ['2023'], ['2024'], ['Last 12 Mo']

for row in dMaster:
	lMarkets.append(row)
lMarkets.sort()
for mkt in lMarkets:
	lhdrMarket.extend([mkt, '', '', ''])
	lhrdFields.extend(['Absorption', 'Deliveries', 'Occupancy', 'Rent Growth'])
	l2014.extend(dMaster[mkt]['2014'])
	l2015.extend(dMaster[mkt]['2015'])
	l2016.extend(dMaster[mkt]['2016'])
	l2017.extend(dMaster[mkt]['2017'])
	l2018.extend(dMaster[mkt]['2018'])
	l2019.extend(dMaster[mkt]['2019'])
	l2020.extend(dMaster[mkt]['2020'])
	l2021.extend(dMaster[mkt]['2021'])
	l2022.extend(dMaster[mkt]['2022'])
	l2023.extend(dMaster[mkt]['2023'])
	l2024.extend(dMaster[mkt]['2024'])
	lLast12Mo.extend(dMaster[mkt]['Last 12 Mo'])

# Create CSV
outfilename = '{0}Axio LAO Markets {1}.csv'.format(pathAxio, yrqtr)
lao.check_if_file_is_open(outfilename)
with open(outfilename, 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(lhdrMarket)
	fout.writerow(lhrdFields)
	fout.writerow(l2014)
	fout.writerow(l2015)
	fout.writerow(l2016)
	fout.writerow(l2017)
	fout.writerow(l2018)
	fout.writerow(l2019)
	fout.writerow(l2020)
	fout.writerow(l2021)
	fout.writerow(l2022)
	fout.writerow(l2023)
	fout.writerow(l2024)
	fout.writerow(lLast12Mo)

lao.openFile(outfilename)

# Instructions
how.axio_exit()

exit(' Fin')


