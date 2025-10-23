

import bb
from bs4 import BeautifulSoup
from subprocess import Popen
import codecs
import csv
import dicts
import lao
import fun_login
import fun_text_date as td
from os.path import exists
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import webs
from pprint import pprint

# Make daily Raw Comps csv if it does not exist
def make_Raw_Comps_CSV():
	csvRawCompsFileName = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/TUC RED News {0}.csv'.format(td.today_date())
	if exists(csvRawCompsFileName):
		print(' Comps file exists...')
	else:
		print(' Making comps file...')
		with open(csvRawCompsFileName, 'w', newline='') as f:
			fout = csv.writer(f)
			header = 'Seller Entity', 'Seller Person', 'Seller Street', 'Seller City', 'Seller State', 'Seller Zip', 'Seller Phone', 'Buyer Entity', 'Buyer Person', 'Buyer Street', 'Buyer City', 'Buyer State', 'Buyer Zip', 'Buyer Phone', 'Sale_Date__c', 'Description__c', 'Lead_Parcel__c', 'Sale_Price__c', 'Zoning__c', 'Longitude__c', 'Parcels__c', 'Recorded_Instrument_Number__c', 'Latitude__c', 'City__c', 'Subdivision__c', 'Source_ID__c', 'Acres__c', 'Lots__c', 'Source__c', 'State__c', 'County__c', 'Market__c'
			fout.writerow(header)
	return csvRawCompsFileName

# Check if record skipped already
def isRecordEnteredSkipped(SID):
	if lao.SkipFile(str(SID), 'Pima', 'CHECK'):
		return True
	# print('\n Checking for existing RED News record...\n')
	# qs = "SELECT Id, Source_Id__c FROM lda_Opportunity__c WHERE Source__c = 'RED News' and Source_Id__c LIKE '%{0}%'".format(SID)
	# results = bb.sfquery(service, qs)
	# TerraForce Query
	fields = 'default'
	wc = f"Source__c = 'RED News' and Source_Id__c LIKE '%{SID}%'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	if results != []:
		lao.SkipFile(str(SID), 'Pima', 'WRITE')
		return True
	# with open('{0}tucson_comps_raw_v03.csv'.format(lao.getPath('comps')), 'r') as f:
	# 	fin = csv.reader(f)
	# 	for row in fin:
	# 		if str(SID) == row[25]:
	# 			return True
	return False

def formatSellerBuyer(aList, sellerbuyer):
	while 1:
		dataList = []
		lao.banner('Tucson RED Scrape v02')
		zipEntered = False
		count = -1
		# print aList
		# print len(aList)
		# print
		listCount = (len(aList) - 1)
		# if len(aList[listCount]) != 8:
		# 	del aList[listCount] Director of Land Acquisitions
		# 	listCount -= 1
		lReplace = ['Mr ', 'Mr.', 'Ms.' 'Mrs ', 'Mrs.', 'Director of Land Acquisitions', 'Dir. Land Acquisitions', 'Land Acquisitions', 'Land Acquisition', ' Desert Region', 'Dir. Land Acquisition', 'Land Acqusition', 'COO', 'CEO',  'Dir.', 'Owner', 'Tucson Acquisitions and Development -', ' /', 'Division  of Land', 'Division Vice  of Land', 'General Partner',  'Acquisitions', 'Director', 'Vice-President', 'President', 'Member', 'Manager', 'Divisional', 'Operations', 'Chief Real Estate', 'of Land']
		entityNameTooLong = False
		for row in aList:
			count += 1
			if count == 0 and len(row) > 50:
				entityNameTooLong = True
				entityName = row
			# Convert row to string if it's not already
			# if not isinstance(row, str):
			# 	row = str(row)
			# 	aList[count] = row
			# Remove non-ascii letters
			if isinstance(row, str):
				if all(ord(c) < 128 for c in row) is False:
					ascii = re.sub(r'[^\x00-\x7f]',r'', row)
					aList[count] = ascii
					row = ascii
			if count > 2:
				for replc in lReplace:
					if replc in row:
						row = row.replace(replc, '')
						aList[count] = row
				if aList[count][-4:] == 'Land':
					aList[count] = aList[count].replace('Land', '')
			print('{0})  {1}'.format(count, row))
		# Add Entity
		if entityNameTooLong:
			td.warningMsg('\n {0}\n\n Entity Name is too long...copy part of it and paste below...'.format(entityName))
		ui = td.uInput('\n Select Entity, type Name  or [Enter] for None > ')
		if ui == '':
			dataList.append('None')
		elif len(ui) > 2:
			dataList.append(ui)
		else:
			dataList.append(aList[(int(ui))])
		# Add Person
		ui = td.uInput('\n Select Person, type Name or [Enter] for None > ')
		if ui == '':
			dataList.append('None')
		elif len(ui) > 2:
			dataList.append(ui)
		else:
			dataList.append(aList[(int(ui))])
		# Add Street
		ui = td.uInput('\n Select Street 1, Type Street or [Enter] for None > ')
		if ui == '':
			dataList.append('None')
		elif len(ui) > 2:
			dataList.append(ui)
			ui = td.uInput(' Enter City > ')
			dataList.append(ui)
			ui = td.uInput(' Enter State (2 letter) > ')
			dataList.append(ui)
			ui = td.uInput(' Enter Zipcode > ')
			dataList.append(ui)
			zipEntered = True
		else:
			street1 = int(ui)
			street2 = (int(ui) + 1)
			if 'Suite' in aList[street2] or ' Flr' in aList[street2] or ' flr' in aList[street2] or ' Floor' in aList[street2] or ' floor' in aList[street2] or 'Ste.' in aList[street2] or 'Ste ' in aList[street2] or '#' in aList[street2]:
				dataList.append('{0} {1}'.format(aList[street1], aList[street2]))
			elif aList[street2] == '':
				dataList.append(aList[street1])
				street2 = street1 + 1
			elif aList[street2] == 'Tucson':
				dataList.append(aList[street1])
				street2 -= 1
			else:
				ui = td.uInput(' Select Street 2 or [Enter] for None > ')
				if ui == '':
					dataList.append(aList[street1])
					street2 = street1
				else:
					street2 = int(ui)
					dataList.append('{0} {1}'.format(aList[street1], aList[street2]))
		# Add City, State & Zip if exists
		if not zipEntered:
			iszip = street2 + 3
			if len(aList[iszip]) == 5:
				dataList.append(aList[(iszip - 2)])
				dataList.append(aList[(iszip - 1)])
				dataList.append(aList[iszip])
				# print('Found Zip Code...')
			else:
				td.warningMsg('\n Could not find Zip Code...\n')
				ui = td.uInput(' Select or Type City or [Enter] for None > ')
				if len(ui) == 1:
					dataList.append(aList[(int(ui))])
				elif ui == '':
					dataList.append('None')
				else:
					dataList.append(ui)
				ui = td.uInput(' Select or Type State or [Enter] for None > ')
				if len(ui) == 1:
					dataList.append(aList[(int(ui))])
				elif ui == '':
					dataList.append('None')
				else:
					dataList.append(ui)
				ui = td.uInput(' Select or Type Zip Code or [Enter] for None > ')
				if len(ui) == 1:
					dataList.append(aList[(int(ui))])
				elif ui == '':
					dataList.append('None')
				else:
					dataList.append(ui)
		
		# Add Phone Number if exists
		noPhone = True
		for row in aList:
			if len(row) == 12 and '.' in row:
				strTemp_number = row.replace('.', '')
				print(strTemp_number)
				if re.match('^[0-9]*$', strTemp_number):
					print('PHONE!')
					dataList.append(row)
					noPhone = False
					break
		if noPhone:
			print('NO PHONE!')
			dataList.append('None')

		print()
		print(' Entity:  {0}'.format(dataList[0]))
		print(' Person:  {0}'.format(dataList[1]))
		print(' Address: {0}'.format(dataList[2]))
		print(' City:    {0}'.format(dataList[3]))
		print(' State:   {0}'.format(dataList[4]))
		print(' ZipCode: {0}'.format(dataList[5]))
		print(' Phone:   {0}'.format(dataList[6]))
		ui = td.uInput('\n Is this correct? [0/1/00] > ')
		if ui == '1':
			return dataList
		elif ui == '00':
			exit('\n Terminating program...')

td.console_title('RED News')
td.banner('Tucson RED Scrape v02')

service = fun_login.TerraForce()

driver = fun_login.RED_News()
csvRawCompsFileName = make_Raw_Comps_CSV()

filepath = '{0}RED News Last Record Checked.txt'.format(lao.getPath('comps'))
with open(filepath, 'r') as f:
	SID = (f.read()).strip()
	SID = int(SID)

# The list of dicts to be written to the final CSV file
ldTF_2_CSV = []

while 1:
	# Check if record already entered
	if isRecordEnteredSkipped(SID):
		SID += 1
		with open(filepath, 'w', newline='') as f:
			f.write('{0}\n'.format(SID))
		continue

	print('RED Id: {0}'.format(SID))
	print(' Opening web page...')
	driver.get(r'https://realestatedaily-news.com/displaycomp/?ID={0}&NoComment='.format(SID))
	lao.sleep(1)
	html = driver.page_source

	soup = BeautifulSoup(html, 'html.parser')

	dd = {}

	# Scrape Name
	h1 = soup.find('h1')
	try:
		dd['Name'] = h1.text
		numberFails = 0
	except AttributeError:
		print('Blank record...')
		# driver.quit()
		try:
			numberFails += 1
		except NameError:
			numberFails = 1
		if numberFails == 5:
			print('\n\n5 blank records in a row...')
			driver.quit()
			break
			# sys.exit('\nFin')
		SID += 1
		continue

	# Scrape data that can be obtained through looping through the html
	isLand = False
	for tr in soup.find_all('tr')[1:]:
		tds = tr.find_all('td')
		if tds == []:
			continue
		# print
		# print tds
		if 'Sale Price:' in tds[0]:
			dd['Sale_Price__c'] = int((tds[1].text).replace('$', '').replace(',', ''))
		elif 'Property Type:' in tds[0]:
			propertyType = (tds[1].text).strip()
			print(propertyType)
			if 'Land' in propertyType:
				isLand = True
		elif 'Sale Date:' in tds[0]:
			dd['Sale_Date__c'] = td.date_engine(tds[1].text)
		elif "Recorder's Doc#" in tds[0]:
			dd['Recorded_Instrument_Number__c'] = tds[1].text
		elif 'RED Comp#:' in tds[0]:
			dd['Source_ID__c'] = tds[1].text
		elif 'Land Area:' in tds[0]:
			try:
				print(tds[1].text)
				lAcres = (tds[1].text).split(' ')
				# dd['Acres__c'] =  float((((tds[1].text).split('/'))[0]).replace(',', ''))
				dd['Acres__c'] = float(lAcres[0].replace(',', ''))
			except ValueError:
				dd['Acres__c'] = 0
		elif 'Units:' in tds[0]:
			dd['Lots__c'] = int(tds[1].text)
		elif 'Subdivision:' in tds[0]:
			dd['Subdivision__c'] = (tds[1].text).strip()
		elif len(tds) >= 4:
			if 'Subdivision:' in tds[2]:
				dd['Subdivision__c'] = (tds[3].text).strip()
			elif 'Latitude:' in tds[0]:
				try:
					dd['Latitude__c'], dd['Longitude__c'] = float(tds[1].text), float(tds[3].text)
				except ValueError:
					td.warningMsg('\n No Lon/Lat for Record, setting to Tucson aircraft boneyard.')
					td.uInput('\n Continue...')
					dd['Latitude__c'], dd['Longitude__c'] = 32.153, -110.827
	if isLand and dd['Sale_Price__c'] >= 100000:
		lao.banner('Tucson RED  Scrape v02')
		ui = td.uInput('Enter this record? [0/1/00] > ')
		if ui == '0':
			lao.SkipFile(str(SID), 'Pima', 'WRITE')
			SID += 1
			with open(filepath, 'w', newline='') as f:
				f.write('{0}\n'.format(SID))
			continue
		elif ui == '00':
			exit('\n Terminating program...')
	else:
		if isLand:
			print('Sale Price is ${0} less than $100K'.format(dd['Sale_Price__c']))
		else:
			print('Not a Land Deal')
		SID += 1
		# with open(filepath, 'w', newline='') as f:
		# 	f.write('{0}\n'.format(SID))
		continue

	# Print page
	# print('\n Printing page...')
	# driver.execute_script('window.print();')
	# exit()

	# Check if data was entered for specified fields and set to 'None' if not.
	if not 'Subdivision__c' in dd:
		dd['Subdivision__c'] = 'None'
	if not 'Lots__c' in dd:
		dd['Lots__c'] = 'None'
	if not 'Recorded_Instrument_Number__c' in dd:
		dd['Recorded_Instrument_Number__c'] = 'None'

	# pprint(dd)
	# td.uInput('\n Continue... > ')

	# Scrape data in the Seller and Buyer table
	process = False
	sellerList, buyerList, stopcount = [], [], 0
	# Find all table rows 'tr'
	for tr in soup.find_all('tr')[1:]:
		# Find all table data 'td' (cells/columns) in table row 'tr'
		tds = tr.find_all('td')
		# Skip empty tds
		if tds == []:
			continue
		print
		# Set process flag to True if the table contains 'Seller'
		if 'Seller:' in tds[0]:
			process = True
		if len(tds) > 2:
			if 'Listing' in tds[0] or 'Selling' in tds[2] or stopcount == 3:
				break
		if len(tds) > 2:
			if u'\xa0' in tds[0] and  u'\xa0' in tds[1] and u'\xa0' in tds[2] and u'\xa0' in tds[3]:
				stopcount += 1
				continue
			elif stopcount == 1:
				stopcount = 0
		if process:
			# print(len(tds))
			# raw_input(tds)
			if len(tds) == 1:
				pass
			elif u'\xa0' in tds[1].text:
				titlelist = ['Facility Management', 'Managing Member', 'Vice President', 'General Partner', 'Acquisitions', 'Member', 'member', 'Vice President', 'Director', 'Dir. Land', 'CEO', 'CFO', 'CIO', 'Manager', 'President', 'Principal', 'Officer', 'VP', ',', 'Trustee', 'Divisional', "'"]
				lSellerName = (tds[1].text).split(u'\xa0')
				lBuyerName = (tds[3].text).split(u'\xa0')
				for s in lSellerName:
					if s == u'Mr.' or s == u'Ms.' or s == u'Mrs.':
						continue
					if s != '':
						for title in titlelist:
							s = s.replace(title, '')
						sellerList.append(s)
				for s in lBuyerName:
					if s == u'Mr.' or s == u'Ms.' or s == u'Mrs.':
						continue
					if s != '':
						for title in titlelist:
							s = s.replace(title, '')
						buyerList.append(s)
			else:
				try:
					sellerList.append(((tds[1].text).replace(',', '').replace('c/o ', ''))) #.encode('utf8'))
					buyerList.append(((tds[3].text).replace(',', '').replace('c/o ', ''))) #.encode('utf8'))
				except IndexError:
					break
					print('fuck error')
					# print tds
					exit()

	process, leadParcel = False, False
	for tr in soup.find_all('tr')[1:]:
		tds = tr.find_all('td')
		if tds == []:
			continue
		if u'1.\xa0' in tds[0]:
			process, leadParcel = True, True
		elif u'\xa0' in tds[0] and process is True:
			break
		if process:
			if leadParcel:
				try:
					dd['Lead_Parcel__c'] = tds[1].text
					dd['Parcels__c'] = tds[1].text
					dd['City__c'] = tds[3].text
					if dd['City__c'] == 'County':
						dd['City__c'] = 'Tucson'
					if dd['City__c'] == 'OroValley':
						dd['City__c'] = 'Oro Valley'
					dd['Zoning__c'] = tds[4].text
					leadParcel = False
				except IndexError:
					dd['Lead_Parcel__c'] = 'None'
					dd['Parcels__c'] = 'None'
					dd['City__c'] = 'None'
					dd['Zoning__c'] = 'None'
					break
			else:
				dd['Parcels__c'] = '{0}, {1}'.format(dd['Parcels__c'], tds[1].text)

	# Check if City and Zoning have values and if not set to 'None'
	if dd['Zoning__c'] == u'\xa0':
		dd['Zoning__c'] = 'None'
	if dd['City__c'] == u'\xa0':
		dd['City__c'] = 'None'


	# Process Seller Buyer Info
	# lao.click(1500, 700)
	dataList = formatSellerBuyer(sellerList, 'Seller')
	dataList.extend(formatSellerBuyer(buyerList, 'Buyer'))

	# Add scraped data to csv row dataList
	try:
		dataList.append(dd['Sale_Date__c'])
	except KeyError:
		ui = td.uInput('Missing Sale Date, please enter [MMDDYY] > ')
		dd['Sale_Date__c'] = lao.dateFormat(ui, 'TF', 'eight')
		dataList.append(dd['Sale_Date__c'])
	dataList.append(dd['Name'])
	dataList.append(dd['Lead_Parcel__c'])
	dataList.append(dd['Sale_Price__c'])
	dataList.append(dd['Zoning__c'])
	try:
		dataList.append(dd['Longitude__c'])
	except KeyError:
		dataList.append('')
	dataList.append(dd['Parcels__c'])
	dataList.append(dd['Recorded_Instrument_Number__c'])
	try:
		dataList.append(dd['Latitude__c'])
	except KeyError:
		dataList.append('')
	dataList.append(dd['City__c'])
	dataList.append(dd['Subdivision__c'])
	dataList.append(dd['Source_ID__c'])
	dataList.append(dd['Acres__c'])
	dataList.append(dd['Lots__c'])
	dataList.extend(['RED News', 'Arizona', 'Pima', 'Tucson'])

	# with open('F:/Research Department/scripts/Projects/Research/data/CompsFiles/tucson_comps_raw_v03.csv', 'a') as f:
	with open(csvRawCompsFileName, 'a', newline='') as f:
		fout = csv.writer(f)
		fout.writerow(dataList)

	SID += 1
	# with open(filepath, 'w', newline='') as f:
	# 	f.write('{0}\n'.format(SID))

	lao.banner('Tucson RED  Scrape v02')

# Build the CSV file name based on the market and date
lTF_2_CSV_fields = dicts.get_tf_csv_header()
# ldTF_2_CSV = dicts.spreadsheet_to_dict('C:/TEMP/TUC RED News 2025-06-11.csv')
ldTF_2_CSV = dicts.spreadsheet_to_dict(csvRawCompsFileName)

csv_file_path = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/'
# csv_file_path = 'C:/TEMP/'
csv_file_name = f'Red_News_{td.today_date()}_FORMATTED.csv'
filename = f'{csv_file_path}{csv_file_name}'

# Open the CSV file for writing
with open(filename, mode='w', newline='') as f:
	fout = csv.writer(f)

	# Write the header row
	fout.writerow(lTF_2_CSV_fields)

	# Cycle through the list of dicts and write each row based on the lTF_2_CSV_fields
	for i in ldTF_2_CSV:
		rec = ldTF_2_CSV[i]
		pprint(rec)
		row = []
		for fld in lTF_2_CSV_fields:
			if fld in rec:
				row.append(rec[fld])
			else:
				row.append('None')
		fout.writerow(row)
lao.openFile(filename)

# outFile = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/tucson_comps_v03_FORMATTED.csv'
# dict = lao.spreadsheetToDict(csvRawCompsFileName)
# with open(outFile, 'w', newline='') as f:
# 	fout = csv.writer(f)
# 	fout.writerow(lao.headerTFCSV())
# 	for row in dict:
# 		r= dict[row]
# 		lRow = []
# 		lRow.append(r['Seller Entity 00'])  # Seller Entity
# 		lRow.append(r['Seller Person 01'])  # Seller Person
# 		lRow.append(r['Seller Address 02'])  # Seller Street
# 		lRow.append(r['Seller City 03'])  # Seller City
# 		lRow.append(lao.convertState(r['Seller State 04']))  # Seller State
# 		lRow.append(r['Seller Zip 05'])  # Seller Zip
# 		lRow.append('None')  # Seller Country
# 		lRow.append('Seller Phone 06')  # Seller Phone
# 		lRow.append('None')  # Seller Email
# 		lRow.append(r['Buyer Entity 07'])  # Buyer Entity
# 		lRow.append(r['Buyer Person 08'])  # Buyer Person
# 		lRow.append(r['Buyer Street 09'])  # Buyer Street
# 		lRow.append(r['Buyer City 10'])  # Buyer City
# 		lRow.append(lao.convertState(r['Buyer State 11']))  # Buyer State
# 		lRow.append(r['Buyer Zip 12'])  # Buyer Zip
# 		lRow.append('None')  # Buyer Country
# 		lRow.append(r['Buyer Phone 13'])  # Buyer Phone
# 		lRow.append('None')  # Buyer Email
# 		lRow.append(r['Acres 26'])  # Acres__c
# 		lRow.append('None')  # Buyer_Acting_As__c
# 		lRow.append(r['City 23'])  # City__c
# 		lRow.append('None')  # Classification__c
# 		lRow.append('USA')  # Country__c
# 		lRow.append(r['County 30'])  # County
# 		lRow.append('None')  # Description__c
# 		lRow.append('None')  # General_Plan__c
# 		lRow.append('None')  # Keyword_Group__c
# 		lRow.append(r['Latitude 22'])  # Latitude__c
# 		lParcels = r['Parcels 20'].split(', ')
# 		lRow.append(lParcels[0])  # Lead_Parcel__c
# 		lRow.append('None')  # Legal_Description__c
# 		lRow.append('None')  # Location__c
# 		lRow.append(r['Longitude 19'])  # Longitude__c
# 		lRow.append('None')  # Lot_Description__c
# 		lRow.append('None')  # Lot_Type__c
# 		lRow.append(r['Lots 27'])  # Lots__c
# 		lRow.append('Tucson')  # Market__c
# 		lRow.append('None')  # Deal Name
# 		lRow.append(r['Parcels 20'])  # Parcels__c
# 		lRow.append(r['Rec Doc 21'])  # Record_Instrument_Number__c
# 		lao.dateFormat(r['Sale Date 14'])
# 		lRow.append(lao.dateFormat(r['Sale Date 14']))  # Sale_Date__c
# 		lRow.append(r['Sale Price 17'])  # Sale_Price__c
# 		lRow.append('RED News')  # Source__c
# 		lRow.append(r['Source ID 25'])  # Source_ID__c
# 		lRow.append('Arizona')  # State__c
# 		lRow.append(r['Subdivision 24'])  # Subdivision__c
# 		lRow.append('None')  # Submarket__c
# 		lRow.append('None')  # Zipcode__c
# 		lRow.append(r['Zoning 18'].upper())  # Zoning__c
# 		lRow.append('None')  # List_Date__c
# 		lRow.append('None')  # List_Price__c
# 		lRow.append('None')  # List Entity
# 		lRow.append('None')  # List Agent
# 		lRow.append('None')  # List Agent Phone
# 		lRow.append('None')  # List Agent Email
# 		lRow.append('None')  # Alt APN A
# 		lRow.append('None')  # Alt APN B
# 		lRow.append('None')  # PID__c
# 		lRow.append('None')  # Residence Y-N
# 		lRow.append('None')  # Terms__c
# 		lRow.append('None')  # Recorded_Doc_URL__c
# 		lRow.append('None')  # Notes
# 		lRow.append('None')  # Lender
# 		lRow.append('None')  # Loan_Amount__c
# 		lRow.append('None')  # Loan_Date__c
# 		lRow.append('None')  # Buyer Agent Entity
# 		lRow.append('None')  # Buyer Agent
# 		lRow.append('None')  # Buyer Agent Phone
# 		lRow.append('None')  # Buyer Agent Email
# 		lRow.append('Sold')  # MSL Status

# 		fout.writerow(lRow)

# lao.openFile(outFile)

sys.exit('\n Fin...')
