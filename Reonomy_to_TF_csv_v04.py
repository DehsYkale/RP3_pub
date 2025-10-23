# Converts Reonomy zip file export to TerraForce csv entry file.

import lao
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
import mpy
from os import path
from pprint import pprint
from shutil import copyfileobj
from zipfile import ZipFile
# from amp import getIntersection

# Unzip the Reonomy export file
def unzipFile():
	from zipfile import ZipFile
	zipFile = lao.guiFileOpen('{0}'.format(lao.getPath('comps')), 'Select Reonomy Zip File', extension=[('zip files', '.zip')])
	csvName = path.basename(zipFile).replace('.zip', '')
	my_dir = lao.getPath('comps')
	my_zip = zipFile

	
	with ZipFile(my_zip) as zip_file:
		for member in zip_file.namelist():
			
			if 'contacts.csv' in member:
				# contact_or_property = 'contacts.csv'
				contact_or_property = member
			else:
				# contact_or_property = 'properties.csv'
				contact_or_property = member
			# filename = path.basename('{0} {1}'.format(csvName, contact_or_property))
			filename = path.basename('{0}'.format(contact_or_property))

			# skip directories
			if not filename:
				continue

			# copy file (taken from zipfile's extract)
			source = zip_file.open(member)
			# target = file(path.join(my_dir, filename), "wb")
			target = open(path.join(my_dir, filename), "wb")
			with source, target:
				copyfileobj(source, target)

	# Determine market based on 3 letter abbriviation if exists
	market3LetterAbbriviation = csvName[:3]
	market = lao.getCounties('MarketAbb', MarketAbb=market3LetterAbbriviation)

	return csvName, market

# Build Buyer & Seller dictionaries
def buildBuyerSellerDicts():
	# Start Buyer (bd) and Seller (sd) dictionaries
	bd = {}
	sd = {}

	# Loop through Contacts dictionary
	for contRow in dContacts:

		cont = dContacts[contRow]
		contID = cont['reonomy_property_id']

		if contID == propID:
			if propBuyer.lower() == cont['contact_name'].lower():
				bd['Person'] = cont['contact_name']
				bd['Entity'] = cont['contact_company_name']
				bd['Street'] = cont['contact_address_1_line_1']
				bd['City'] = cont['contact_address_1_city']
				bd['State'] = cont['contact_address_1_state'].upper()
				bd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif propBuyer.lower() == cont['contact_company_name'].lower():
				bd['Person'] = cont['contact_name']
				bd['Entity'] = cont['contact_company_name']
				bd['Street'] = cont['contact_address_1_line_1']
				bd['City'] = cont['contact_address_1_city']
				bd['State'] = cont['contact_address_1_state'].upper()
				bd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif propBuyer.lower() == cont['reported_owner_name'].lower():
				bd['Person'] = ''
				bd['Entity'] = cont['reported_owner_name']
				bd['Street'] = cont['reported_mailing_address_line_1']
				bd['City'] = cont['reported_mailing_address_city']
				bd['State'] = cont['reported_mailing_address_state'].upper()
				bd['ZipCode'] = cont['reported_mailing_address_postal_code']
				break

			if propSeller.lower() == cont['contact_name'].lower():
				sd['Person'] = cont['contact_name']
				sd['Entity'] = cont['contact_company_name']
				sd['Street'] = cont['contact_address_1_line_1']
				sd['City'] = cont['contact_address_1_city']
				sd['State'] = cont['contact_address_1_state'].upper()
				sd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif propSeller.lower() == cont['contact_company_name'].lower():
				sd['Person'] = cont['contact_name']
				sd['Entity'] = cont['contact_company_name']
				sd['Street'] = cont['contact_address_1_line_1']
				sd['City'] = cont['contact_address_1_city']
				sd['State'] = cont['contact_address_1_state'].upper()
				sd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif propSeller.lower() == cont['reported_owner_name'].lower():
				sd['Person'] = ''
				sd['Entity'] = cont['reported_owner_name']
				sd['Street'] = cont['reported_mailing_address_line_1']
				sd['City'] = cont['reported_mailing_address_city']
				sd['State'] = cont['reported_mailing_address_state'].upper()
				sd['ZipCode'] = cont['reported_mailing_address_postal_code']
				break

			# Split Names
			lpropBuyer = propBuyer.split(' ')
			lpropSeller = propSeller.split(' ')
			if lpropBuyer[0].lower() in cont['contact_name'].lower() and lpropBuyer[1].lower() in cont[
				'contact_name'].lower():
				bd['Person'] = cont['contact_name']
				bd['Entity'] = cont['contact_company_name']
				bd['Street'] = cont['contact_address_1_line_1']
				bd['City'] = cont['contact_address_1_city']
				bd['State'] = cont['contact_address_1_state'].upper()
				bd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif lpropBuyer[0].lower() in cont['contact_company_name'].lower() and lpropBuyer[1].lower() in cont[
				'contact_company_name'].lower():
				bd['Person'] = cont['contact_name']
				bd['Entity'] = cont['contact_company_name']
				bd['Street'] = cont['contact_address_1_line_1']
				bd['City'] = cont['contact_address_1_city']
				bd['State'] = cont['contact_address_1_state'].upper()
				bd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif lpropBuyer[0].lower() in cont['reported_owner_name'].lower() and lpropBuyer[1].lower() in cont[
				'reported_owner_name'].lower():
				bd['Person'] = ''
				bd['Entity'] = cont['reported_owner_name']
				bd['Street'] = cont['reported_mailing_address_line_1']
				bd['City'] = cont['reported_mailing_address_city']
				bd['State'] = cont['reported_mailing_address_state'].upper()
				bd['ZipCode'] = cont['reported_mailing_address_postal_code']
				break
			elif lpropSeller[0].lower() in cont['contact_name'].lower() and lpropSeller[1].lower() in cont[
				'contact_name'].lower():
				sd['Person'] = cont['contact_name']
				sd['Entity'] = cont['contact_company_name']
				sd['Street'] = cont['contact_address_1_line_1']
				sd['City'] = cont['contact_address_1_city']
				sd['State'] = cont['contact_address_1_state'].upper()
				sd['ZipCode'] = cont['contact_address_1_postal_code']
				break
			elif len([lpropSeller]) >= 2:
				if lpropSeller[0].lower() in cont['contact_company_name'].lower() and lpropSeller[1].lower() in cont['contact_company_name'].lower():
					sd['Person'] = cont['contact_name']
					sd['Entity'] = cont['contact_company_name']
					sd['Street'] = cont['contact_address_1_line_1']
					sd['City'] = cont['contact_address_1_city']
					sd['State'] = cont['contact_address_1_state'].upper()
					sd['ZipCode'] = cont['contact_address_1_postal_code']
					break
				elif lpropSeller[0].lower() in cont['reported_owner_name'].lower() and lpropSeller[1].lower() in cont[
					'reported_owner_name'].lower():
					sd['Person'] = ''
					sd['Entity'] = cont['reported_owner_name']
					sd['Street'] = cont['reported_mailing_address_line_1']
					sd['City'] = cont['reported_mailing_address_city']
					sd['State'] = cont['reported_mailing_address_state'].upper()
					sd['ZipCode'] = cont['reported_mailing_address_postal_code']
					break

	if sd == {}:
		sd['Person'] = 'None'
		sd['Entity'] = propSeller
		sd['Street'] = 'None'
		sd['City'] = 'None'
		sd['State'] = 'None'
		sd['ZipCode'] = 'None'
	if bd == {}:
		bd['Person'] = 'None'
		bd['Entity'] = propBuyer
		bd['Street'] = 'None'
		bd['City'] = 'None'
		bd['State'] = 'None'
		bd['ZipCode'] = 'None'

	return bd, sd

# Assign rows into a list and write to the Raw csv
def buildRawCSV(bd, sd, prop):
	lRow = []
	lRow.append(sd['Entity'])  # Seller Entity 0
	lRow.append(sd['Person'])  # Seller Person 1
	lRow.append(sd['Street'])  # Seller Street 2
	lRow.append(sd['City'])  # Seller City 3
	lRow.append(sd['State'].upper())  # Seller State4
	lRow.append(sd['ZipCode'])  # Seller Zip 5
	lRow.append('None')  # Seller Country 6
	lRow.append('None')  # Seller Phone 7
	lRow.append('None')  # Seller Email 8
	lRow.append(bd['Entity'])  # Buyer Entity 9
	lRow.append(bd['Person'])  # Buyer Person 10
	lRow.append(bd['Street'])  # Buyer Street 11
	lRow.append(bd['City'])  # Buyer City 12
	lRow.append(bd['State'].upper())  # Buyer State 13
	lRow.append(bd['ZipCode'])  # Buyer Zip 14
	lRow.append('None')  # Buyer Country 15
	lRow.append('None')  # Buyer Phone 16
	lRow.append('None')  # Buyer Email 17
	lRow.append(acres)  # Acres 18
	lRow.append('None')  # Buyer Acting As 19
	lRow.append(prop['address_city'])  # City 20
	# lRow.append(prop['asset_category'])  # Classification 21
	lRow.append('None')  # Classification 21
	lRow.append('USA')  # Country 22
	lRow.append(county)  # County 23
	lRow.append('None')  # Description 24
	lRow.append('None')  # General Plan 25
	lRow.append('None')  # Keyword Group 26
	lRow.append(prop['latitude'])  # Latitude 27
	lRow.append(prop['apn'])  # Lead Parcels 28
	lRow.append('None')  # Legal Description 29
	lRow.append(location)  # Location 30
	lRow.append(prop['longitude'])  # Longitude 31
	lRow.append('None')  # Lot Description 32
	lRow.append('None')  # Lot Type 33
	lRow.append('None')  # Lots 34
	if market == 'USA':  # GV National Whale Sales
		lRow.append(prop['address_city'])
	else:
		lRow.append(market)  # Market 35
	lRow.append('None')  # Deal Name 36
	lRow.append(prop['apn'])  # Parcels 37
	lRow.append(prop['sale_document_id'])  # Record Doc ID 38
	lRow.append(prop['sale_recorded_date'])  # Sale Date 39
	lRow.append(salePrice)  # Sale Price 40
	lRow.append('Reonomy')  # Source 41
	lRow.append(sourceID)  # Source ID 42
	if len(prop['address_state']) == 2:
		state = lao.convertState(prop['address_state'].upper())
		lRow.append(state)  # State 43
	else:
		lRow.append(prop['address_state'])  # State 43
	lRow.append('None')  # Subdivision 44
	lRow.append('None')  # Submarket 45
	lRow.append(prop['address_postal_code'])  # Zip Code 46
	lRow.append(prop['zoning'].upper())  # Zoning 47
	lRow.append('None')  # List Date 48
	lRow.append('None')  # List Price 49
	lRow.append('None')  # List Entity 50
	lRow.append('None')  # List Agent 51
	lRow.append('None')  # List Agent Phone 52
	lRow.append('None')  # List Agent Email 53
	lRow.append('None')  # Alt APN A 54
	lRow.append('None')  # Alt APN B 55
	lRow.append('None')  # PID 56
	lRow.append('None')  # Residence Y-N 57
	lRow.append('None')  # Terms 58
	lRow.append('None')  # Rec Doc URL 59
	lRow.append('None')  # Notes A 60
	# lRow.append(prop['mortgage_lender_name'])  # Lender 61
	lRow.append(prop['mortgage_standardized_name'])  # Lender 61
	lRow.append(prop['mortgage_amount'])  # Loan Amount 62
	lRow.append(prop['mortgage_recorded_date'])  # Loan Date 63
	lRow.append('None')  # Buyer Agent Entity 64
	lRow.append('None')  # Buyer Agent 65
	lRow.append('None')  # Buyer Agent Phone 66
	lRow.append('None')  # Buyer Agent Email 67
	lRow.append('Sold')  # MSL Status 68

	for i in range(0, len(lRow)):
		if lRow[i] == '' or lRow[i] == 'NONE':
			lRow[i] = 'None'

	fout.writerow(lRow)

def buildPresortedCSV(r):
	lRow = []
	lRow.append(r['Seller Entity']),
	lRow.append(r['Seller Person']),
	lRow.append(r['Seller Street']),
	lRow.append(r['Seller City']),
	lRow.append(r['Seller State']),
	lRow.append(r['Seller Zip']),
	lRow.append(r['Seller Country']),
	lRow.append(r['Seller Phone']),
	lRow.append(r['Seller Email']),
	lRow.append(r['Buyer Entity']),
	lRow.append(r['Buyer Person']),
	lRow.append(r['Buyer Street']),
	lRow.append(r['Buyer City']),
	lRow.append(r['Buyer State']),
	lRow.append(r['Buyer Zip']),
	lRow.append(r['Buyer Country']),
	lRow.append(r['Buyer Phone']),
	lRow.append(r['Buyer Email']),
	lRow.append(r['Acres__c']),
	lRow.append(r['Buyer_Acting_As__c']),
	lRow.append(r['City__c']),
	lRow.append(r['Classification__c']),
	lRow.append(r['Country__c']),
	lRow.append(r['County__c']),
	lRow.append(r['Description__c']),
	lRow.append(r['General_Plan__c']),
	lRow.append(r['Keyword_Group__c']),
	lRow.append(r['Latitude__c']),
	lRow.append(r['Lead_Parcel__c']),
	lRow.append(r['Legal_Description__c']),
	lRow.append(r['Location__c']),
	lRow.append(r['Longitude__c']),
	lRow.append(r['Lot_Description__c']),
	lRow.append(r['Lot_Type__c']),
	lRow.append(r['Lots__c']),
	lRow.append(r['Market__c']),
	lRow.append(r['Deal Name']),
	lRow.append(r['Parcels__c']),
	lRow.append(r['Recorded_Instrument_Number__c']),
	lRow.append(r['Sale_Date__c']),
	lRow.append(r['Sale_Price__c']),
	lRow.append(r['Source__c']),
	lRow.append(r['Source_ID__c']),
	lRow.append(r['State__c']),
	lRow.append(r['Subdivision__c']),
	lRow.append(r['Submarket__c']),
	lRow.append(r['Zipcode__c']),
	lRow.append(r['Zoning__c']),
	lRow.append(r['List_Date__c']),
	lRow.append(r['List_Price__c']),
	lRow.append(r['List Entity']),
	lRow.append(r['List Agent']),
	lRow.append(r['List Agent Phone']),
	lRow.append(r['List Agent Email']),
	lRow.append(r['AltAPN A']),
	lRow.append(r['AltAPN B']),
	lRow.append(r['PID__c']),
	lRow.append(r['Residence Y-N']),
	lRow.append(r['Terms__c']),
	lRow.append(r['Recorded_Doc_URL__c']),
	lRow.append(r['Notes']),
	lRow.append(r['Lender']),
	lRow.append(r['Loan_Amount__c']),
	lRow.append(r['Loan_Date__c']),
	lRow.append(r['Buyer Agent Entity']),
	lRow.append(r['Buyer Agent']),
	lRow.append(r['Buyer Agent Phone']),
	lRow.append(r['Buyer Agent Email']),
	lRow.append(r['MLS Status'])

	fout.writerow(lRow)

# Print the Buyer & Seller info
def printBuyerSellerInfo(cont):
	print('propSeller: {0}').format(propSeller)
	print('propBuyer:  {0}').format(propBuyer)
	print
	print('Contact Person: {0})'.format(cont['contact_name']))
	print('Contact Entity: {0})'.format(cont['contact_company_name']))
	print('Reported Owner: {0})'.format(cont['reported_owner_name']))
	print

# Skip Homebuilder to Individual Sales
def isHomebuilderToIndividual(service, r):
	# Skip if Buyer is a Company
	if lao.coTF(r['Buyer Entity']):
		return False
	homebuilder = r['Seller Entity'].split(' ')
	fields = 'default'
	wc = f"Category__c INCLUDES ('Buyer Homebuilder') AND Name LIKE '{homebuilder[0]} %' AND isPersonAccount = False"
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
	if results != []:
		return True
	else:
		return False

# -----------START PROGRAM--------------------------------------------------------------

td.console_title('Reonomy')
td.banner('Reonomy to TF CSV v04')
# Clean comps and listings folders
lao.clean_comps_listings_files_folders()
# Connect to TerraForce
service = fun_login.TerraForce()
lLAOCounties = lao.getCounties('AllCounties County Name')
# pprint(lLAOCounties)
# exit()

# Open the Reonomy Zip File
csvName, market = unzipFile()

# Select market if undetermined from zip file name
if market is None:
	market = lao.selectMarket(includeUSA=True)

# Create dictionaries of the two Reonomy csv files
filename_contacts = '{0}{1}_contacts.csv'.format(lao.getPath('comps'), csvName)
filename_properties = '{0}{1}_properties.csv'.format(lao.getPath('comps'), csvName)
dContacts = dicts.spreadsheet_to_dict(filename_contacts)
dProperties = dicts.spreadsheet_to_dict(filename_properties)

lao.banner('Reonomy to TF CSV v04')

# Open the raw csv to write data to
with open('{0}{1}_RAW.csv'.format(lao.getPath('comps'), csvName), 'w', newline='') as f:
	fout = csv.writer(f)

	# Write file header
	fout.writerow(dicts.get_tf_csv_header())

	# count = 0
	print('\n Processing...merging Reonomy Properties & Contacts files...please stand by...')

	# Loop through the Reonomy property dictionary to attach contact entities & names
	for propRow in dProperties:

		# Assign row to variable
		prop = dProperties[propRow]

		# Skip sales that are not 100%
		# if prop['sale_percent_transferred'] != '':
		# 	continue

		propID = prop['reonomy_id']
		# Filter out bad Reonomy IDs that are too long to be right
		if len(propID) > 50:
			continue
		propURL = 'https://app.reonomy.com/parcels/{0}'.format(propID)
		propSeller = prop['sale_seller_name']
		propBuyer = prop['sale_buyer_name']

		# Build the Buyer & Seller dictionaries
		bd, sd = buildBuyerSellerDicts()

		# Calculations
		# Skip records without a lot area
		if prop['lot_area'] == '':
			continue
		acres =  float(prop['lot_area']) / 43560
		acres = '{0:.2f}'.format(acres)
		county = prop['county'].replace(' County', '')
		# Skip Counties that are not LAO Counties
		if not county in lLAOCounties:
			continue
		# location = getIntersection(prop['longitude'], prop['latitude'], False)
		location = mpy.get_intersection_from_lon_lat(dTF='None', lon=prop['longitude'], lat=prop['latitude'], askManually=False, findAddress=False)
		sourceID = 'https://app.reonomy.com/parcels/{0}'.format(prop['reonomy_id'])
		salePrice = prop['sale_amount'].replace('$', '').replace(',','')
		if salePrice == '':
			salePrice = 'None'
		else:
			salePrice = int(float(salePrice))

		# Build the Raw CSV file
		buildRawCSV(bd, sd, prop)



# Process Muti-Parcel Sales
print('\n Processing...merging multi-parcel sales...please stand by...')
dRaws = lao.spreadsheetToDict('{0}{1}_RAW.csv'.format(lao.getPath('comps'), csvName))
dFormats = {}
firstLine = True
for raw in dRaws:
	lao.banner('Reonomy to TF CSV v04')
	# Assign row(raw) to variable
	rLine = dRaws[raw]
	# Skip the header (first line)
	if firstLine:
		dFormats['1'] = rLine
		firstLine = False
	else:
		lenFormat = len(dFormats)
		newLine = True
		for i in range(1, lenFormat + 1):
			i = str(i)
			fLine = dFormats[i]
			if rLine['Seller Entity'] == fLine['Seller Entity']\
					and rLine['Buyer Entity'] == fLine['Buyer Entity']\
					and rLine['Sale_Date__c'] == fLine['Sale_Date__c']\
					and rLine['Sale_Price__c'] == fLine['Sale_Price__c']:
				sumAcres = float(rLine['Acres__c']) + float(fLine['Acres__c'])
				dFormats[i]['Acres__c'] = sumAcres
				newLine = False
				break
			elif rLine['Sale_Date__c'] == fLine['Sale_Date__c']\
					and rLine['Sale_Price__c'] == fLine['Sale_Price__c']:
				print(' Seller')
				print(' Raw      : {0}'.format(rLine['Seller Entity']))
				print(' Formatted: {0}\n'.format(fLine['Seller Entity']))
				print(' Buyer')
				print(' Raw      : {0}'.format(rLine['Buyer Entity']))
				print(' Formatted: {0}'.format(fLine['Buyer Entity']))
				while 1:
					ui = td.uInput('\n Seller/Buyer match? [0/1/00] > ')
					if ui == '1':
						sumAcres = float(rLine['Acres__c']) + float(fLine['Acres__c'])
						dFormats[i]['Acres__c'] = sumAcres
						newLine = False
						break
					elif ui == '0':
						break
					elif ui == '00':
						exit('\n Terminating program...')
					else:
						lao.warningMsg(' Invalid input...try again...')
				break
		if newLine:
			i = str(lenFormat + 1)
			dFormats[i] = rLine

print('\n Processing...removing Homebuilder to Individual sales...please stand by...')

with open('{0}{1}_PRESORTED.csv'.format(lao.getPath('comps'), csvName), 'w', newline='') as f:
	fout = csv.writer(f)
	# Write file header
	fout.writerow(dicts.get_tf_csv_header())

	for frmt in dFormats:
		r = dFormats[frmt]

		# Skip Homebuilder to Individual Buyer Sales
		if isHomebuilderToIndividual(service, r):
			continue

		# Write the row (r) to the Presorted CSV file
		buildPresortedCSV(r)


with open('{0}{1}_PRESORTED.csv'.format(lao.getPath('comps'), csvName), 'r') as f, open('{0}{1}_FORMATTED.csv'.format(lao.getPath('comps'), csvName), 'w', newline='') as g:
	incsv = csv.reader(f)
	# header = incsv.next()
	header = next(incsv)
	outcsv = csv.writer(g)
	sortedcsv = sorted(incsv, key=lambda x: x[20], reverse=False)
	outcsv.writerow(header)
	for row in sortedcsv:
		outcsv.writerow(row)

lao.openFile('{0}{1}_FORMATTED.csv'.format(lao.getPath('comps'), csvName))

print('\n Fin')






