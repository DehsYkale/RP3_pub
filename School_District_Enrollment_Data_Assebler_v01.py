import csv
import dicts
from json import dump
import lao
from pprint import pprint
import fun_text_date as td


dDistricts = {}
lYears = ['2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']
year = 2020
for file_name_years in lYears:
	dtemp = dicts.spreadsheet_to_dict(f'F:/Research Department/MIMO/zData/Schools/AZ School Enrollment {file_name_years}.xlsx')
	for row in dtemp:
		# Trap * for enrollment total
		if dtemp[row]['Total'] == '*':
			dtemp[row]['Total'] = 0
		# Get district name
		district_name = dtemp[row]['LEA Name']
		if district_name in dDistricts:
			if year in dDistricts[district_name]:
				dDistricts[district_name][year] = dDistricts[district_name][year] + int(dtemp[row]['Total'])
			else:
				dDistricts[district_name][year] = int(dtemp[row]['Total'])
		else:
			dDistricts[dtemp[row]['LEA Name']] = {year: int(dtemp[row]['Total'])}
	year += 1

# Remove districts if missing enrollment data for any year
lRemove = []
for district in dDistricts:
	if len(dDistricts[district]) < 5:
		lRemove.append(district)
for district in lRemove:
	del dDistricts[district]

# Calculate percentage change 2020 to 2024
for district in dDistricts:
	# Skip districts with no 2020 enrollment or 2023 enrollment
	if dDistricts[district][2020] == 0 or dDistricts[district][2024] == 0:
		dDistricts[district]['Pct Chng 2020-2024'] = 0
	else:
		dDistricts[district]['Pct Chng 2020-2024'] = round((dDistricts[district][2024] - dDistricts[district][2020]) / dDistricts[district][2020], 2)
# pprint(dDistricts)

# Write dDistricts to csv file
lMaster = [['District', '2020', '2021', '2022', '2023', '2024', 'Pct Chng 2020-2024']]

for district in dDistricts:
	lLine = [district]
	for year in range(2020, 2025):		
		if year in dDistricts[district]:
			lLine.append(dDistricts[district][year])
		else:
			lLine.append('')
	if 'Pct Chng 2020-2024' in dDistricts[district]:
		lLine.append(dDistricts[district]['Pct Chng 2020-2024'])
	else:
		lLine.append('')
	lMaster.append(lLine)

with open('F:/Research Department/MIMO/zData/Schools/District Enrollment 2020-2024.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerows(lMaster)
lao.openFile('F:/Research Department/MIMO/zData/Schools/District Enrollment 2020-2024.csv')
exit('\n Fin...')