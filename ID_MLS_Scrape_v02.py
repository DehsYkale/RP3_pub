# Scrapes ID MLS data into TF compatible CSV file

from bs4 import BeautifulSoup
import csv
import dicts
import fun_text_date as td
import glob
import lao
import mpy
import webs
from pprint import pprint

def getData(style):
	"""
	Get data from div elements by their style attribute (positioning)
	Returns 'skip' if element not found
	"""
	try:
		element = soup.find('div', {'style': style})
		if element:
			text = element.get_text().strip()
			return text if text else 'skip'
		else:
			return 'skip'
	except AttributeError:
		return 'skip'

def getDataByContent(content_text):
	"""
	Find data by looking for div elements containing specific text
	Useful for finding associated values
	"""
	try:
		# Find div containing the label text
		label_div = soup.find('div', string=content_text)
		if not label_div:
			return 'skip'
		
		# Get the style attribute to determine positioning
		style = label_div.get('style', '')
		if not style:
			return 'skip'
		
		# Extract position values
		import re
		top_match = re.search(r'top:(\d+)px', style)
		left_match = re.search(r'left:(\d+)px', style)
		
		if not (top_match and left_match):
			return 'skip'
		
		top = int(top_match.group(1))
		left = int(left_match.group(1))
		
		# Look for data div at same top position but further right
		data_divs = soup.find_all('div', style=True)
		for div in data_divs:
			div_style = div.get('style', '')
			div_top_match = re.search(r'top:(\d+)px', div_style)
			div_left_match = re.search(r'left:(\d+)px', div_style)
			
			if div_top_match and div_left_match:
				div_top = int(div_top_match.group(1))
				div_left = int(div_left_match.group(1))
				
				# Same row, further right (data value)
				if div_top == top and div_left > left:
					text = div.get_text().strip()
					if text and text != content_text:
						return text
		
		return 'skip'
	except Exception as e:
		print(f"Error in getDataByContent for '{content_text}': {e}")
		return 'skip'

def debugParsing(soup_obj):
	"""
	Debug function to help identify what data is available in the HTML
	"""
	print("\n" + "="*80)
	print("DEBUG: Analyzing HTML structure for data elements")
	print("="*80)
	
	# Find all divs with class mls12 or mls13 (these contain the main data)
	data_divs = soup_obj.find_all('div', class_=['mls12', 'mls13'])
	
	print(f"Found {len(data_divs)} data elements:")
	for i, div in enumerate(data_divs[:15]):  # Show first 15
		style = div.get('style', '')
		text = div.get_text().strip()
		class_name = div.get('class', [''])
		print(f"{i+1:2d}. Class: {class_name[0]:5s} | Style: {style[:40]:<40s} | Text: '{text}'")
	
	print("\nLooking for key data patterns...")
	test_patterns = [
		('MLS Number', 'top:0px;left:350px'),
		('Price', 'top:0px;left:590px'),
		('Address', 'top:64px;left:350px'),
		('City', 'top:80px;left:350px'),
		('Acres', 'top:48px;left:590px'),
		('Agent', 'top:304px;left:330px'),
		('Office', 'top:320px;left:330px'),
	]
	
	for label, partial_style in test_patterns:
		matching_divs = soup_obj.find_all('div', style=lambda x: x and partial_style in x)
		if matching_divs:
			for div in matching_divs:
				text = div.get_text().strip()
				print(f"{label:12s}: {text}")
		else:
			print(f"{label:12s}: NOT FOUND")
	
	print("="*80)

def buildDict():
	"""
	Extract data from the MLS HTML structure
	Based on the actual HTML structure from the sample
	"""
	d = {}
	
	# Try to get key identifying information first
	d['sourceID'] = getData('top:0px;left:350px;width:175px;height:13px;')  # MLS # - Updated coordinates
	d['type'] = getData('top:32px;left:350px;width:175px;height:13px;')     # Type - Updated coordinates
	
	# Determine if we have a valid listing
	if d['sourceID'] == 'skip' or d['type'] == 'skip':
		print("Warning: Could not find MLS ID or Type, trying alternative methods...")
		# Try by content
		d['sourceID'] = getDataByContent('MLS #')
		d['type'] = getDataByContent('Type')
	
	# Basic property information - Updated coordinates based on actual HTML
	d['priceAsking'] = getData('top:0px;left:590px;width:145px;height:13px;')    # Asking Price
	d['mlsStatus'] = getData('top:16px;left:590px;width:175px;height:13px;')     # Status
	d['acres'] = getData('top:48px;left:590px;width:86px;height:13px;')          # # Acres
	d['street'] = getData('top:64px;left:350px;width:175px;height:13px;')        # Address
	d['city'] = getData('top:80px;left:350px;width:174px;height:13px;')          # City
	d['zipcode'] = getData('top:96px;left:350px;width:175px;height:13px;')       # Zip
	d['county'] = getData('top:432px;left:340px;width:255px;height:13px;')       # County
	
	# Description and remarks
	d['description'] = getData('top:125px;left:290px;width:471px;height:113px;') # REMARKS
	
	# Agent and listing information - Updated coordinates
	d['listAgent'] = getData('top:304px;left:330px;width:295px;height:12px;')    # List Agent - Phn
	d['listEntity'] = getData('top:320px;left:330px;width:283px;height:12px;')   # List Office - Phn
	d['listAgentEmail'] = getData('top:366px;left:330px;width:245px;height:12px;') # Agent Email
	
	# Property details
	d['leadParcel'] = getData('top:944px;left:47px;width:126px;height:13px;')    # Parcel #
	d['parcels'] = d['leadParcel']  # Default to same as lead parcel
	d['zoning'] = getData('top:416px;left:647px;width:114px;height:13px;')       # Zoning
	d['landUse'] = getData('top:560px;left:340px;width:391px;height:13px;')      # Land Use
	
	# Dates and prices
	d['pendingDate'] = getData('top:896px;left:665px;width:97px;height:12px;')   # Pending Date
	d['priceSold'] = getData('top:912px;left:665px;width:97px;height:12px;')     # Sold Price
	d['closingDate'] = getData('top:896px;left:500px;width:84px;height:12px;')   # Closing Date
	
	# Default values
	d['state'] = 'ID'
	d['source'] = 'Idaho_MLS'
	d['residence'] = 'No'  # Default for land listings
	
	# Handle missing data
	for key, value in d.items():
		if value == 'skip' or value == '':
			d[key] = 'None'
	
	return d

td.console_title('Idaho MLS')
# Get file names of Vizzda email text files.
# files = glob.glob('F:/Research Department/scripts/Data/Idaho_MLS/*.txt')
files = glob.glob('F:/Research Department/Data Entry/Idaho MLS/*.txt')

lhrefs = []
for file in files:
	with open(file) as f:
		for line in f:
			if 'Click Here' in line:
				start = line.find('<') + 1
				end = line.find('>')
				href = line[start:end]
				break
		# raw_input(href)
		lhrefs.append(href)

header = ['owner','acres', 'city', 'county', 'description', 'landUse', 'leadParcel', 'listingAgent', 'listAgentPhone', 'listAgentEmail', 'listEntity', 'listEntityPhone', 'parcels', 'pendingDate', 'priceAsking', 'priceSold', 'closingDate', 'source', 'sourceID', 'street', 'state', 'zipcode', 'zoning', 'mlslink', 'residence', 'mlsStatus']

with open('{0}/ID_MLS_raw.csv'.format(lao.getPath('comps')), 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(header)
	driver = 'None'
	for href in lhrefs:
		print(href)
		html, url, driver = webs.getHTML(href, driver)

		if html == 'No web page':
			continue

		soup = BeautifulSoup(html, 'html.parser')
		
		# Add debugging to see what we're working with
		debugParsing(soup)

		d = buildDict()
		
		d['mlslink'] = url
		l = []

		# Clean Parcels
		if 'CALL' in d['leadParcel'].upper() or 'DETERMINED' in d['leadParcel'].upper() or 'ON FILE' in d['leadParcel'].upper():
			d['leadParcel'], d['parcels'] = '', ''
		if ',' in d['leadParcel']:
			d['parcels'] = d['leadParcel']
			par = d['leadParcel'].split(',')
			d['leadParcel'] = par[0]
		if d['parcels'] == '':
			d['parcels'] = d['leadParcel']
		elif d['parcels'] != d['leadParcel']:
			d['parcels'] = '{0}, {1}'.format(d['leadParcel'], d['parcels'])

		# Clean Listing Agent and Entity - Fixed logic with better error handling
		print('Parsing agent data:')
		print(f"Raw listAgent: {d['listAgent']}")
		print(f"Raw listEntity: {d['listEntity']}")
		
		# Initialize default values
		d['listAgentPhone'] = ''
		d['listEntityPhone'] = ''
		d['owner'] = 'None'  # Default owner since not in this layout
		
		# Parse List Agent (format: "Name - Contact Type: Phone")
		if d['listAgent'] and d['listAgent'] != 'None':
			if ' - Cell: ' in d['listAgent']:
				parts = d['listAgent'].split(' - Cell: ')
			elif ' - Voice: ' in d['listAgent']:
				parts = d['listAgent'].split(' - Voice: ')
			elif ' - Main: ' in d['listAgent']:
				parts = d['listAgent'].split(' - Main: ')
			else:
				parts = [d['listAgent'], '']  # No phone number format found
			
			if len(parts) >= 2:
				d['listAgent'] = parts[0].strip()
				d['listAgentPhone'] = parts[1].strip()
			else:
				d['listAgentPhone'] = ''
		
		# Parse List Entity (format: "Company - Contact Type: Phone")
		if d['listEntity'] and d['listEntity'] != 'None':
			if ' - Main: ' in d['listEntity']:
				parts = d['listEntity'].split(' - Main: ')
			elif ' - Voice: ' in d['listEntity']:
				parts = d['listEntity'].split(' - Voice: ')
			else:
				parts = [d['listEntity'], '']  # No phone number format found
			
			if len(parts) >= 2:
				d['listEntity'] = parts[0].strip()
				d['listEntityPhone'] = parts[1].strip()
			else:
				d['listEntityPhone'] = ''

		# Clean Prices
		d['priceAsking'] = d['priceAsking'].replace('$', '').replace(',', '')
		d['priceSold'] = d['priceSold'].replace('$', '').replace(',', '')

		# print('here2')
		# pprint(d)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		l = [
		d['owner'],
		d['acres'],
		d['city'],
		d['county'],
		d['description'],
		d['landUse'],
		d['leadParcel'],
		d['listAgent'],
		d['listAgentPhone'],
		d['listAgentEmail'],
		d['listEntity'],
		d['listEntityPhone'],
		d['parcels'],
		d['pendingDate'],
		d['priceAsking'],
		d['priceSold'],
		d['closingDate'],
		d['source'],
		d['sourceID'],
		d['street'],
		d['state'],
		d['zipcode'],
		d['zoning'],
		d['mlslink'],
		d['residence'],
		d['mlsStatus']
		]
		
		# print('here1')
		# pprint(l)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		
		fout.writerow(l)

f.close()
driver.quit()
# lao.openFile('{0}ID_MLS_raw.csv'.format(lao.getPath('comps')))

today = td.today_date()
inFile = '{0}ID_MLS_raw.csv'.format(lao.getPath('comps'))
outFile = '{0}'.format(inFile.replace('raw.csv', '{0}_FORMATTED.csv'.format(today)))
# fMSAs = 'F:\Research Department\scripts\Projects\Research\data\LAO_Markets_and_MSAs.csv'

dIDMLS = lao.spreadsheetToDict(inFile)
# dMSAs = lao.spreadsheetToDict(fMSAs)

noOfRecs = len(dIDMLS)
count = 0
with open(outFile, 'w', newline='') as f:
	fout = csv.writer(f)
	# Write file header
	fout.writerow(dicts.get_tf_csv_header())
	for rec in dIDMLS:
		count += 1
		print(f'\n Rec {count} of {noOfRecs}')
		r = dIDMLS[rec]

		# Replace blank values with None
		for i in r:
			if r[i] == '':
				r[i] = 'None'

		# Skip records
		owner = r['owner']
		if 'skip' in owner or 'Cancelled' in r['mlsStatus']:
			continue

		# Clean misc owner text and blanks
		lNone = 'ON FILE CLA OF RECORD'
		if owner.upper() in lNone:
			owner = 'None'

		# Format Location
		d['location'] = '{0} {1} {2}'.format(r['street'], r['state'], r['zipcode'])
		d['longitude'], d['latitude'] = mpy.get_lon_lat_from_address_or_intersection(d['location'])

		lRow = []
		lRow.append(owner)  # Seller Enity 0
		lRow.append('None')  # Seller Person 1
		lRow.append('None')  # Seller Street 2
		lRow.append('None')  # Seller City 3
		lRow.append('None')  # Seller State 4
		lRow.append('None') # Seller Zip 5
		lRow.append('None')  # Seller Country 6
		lRow.append('None') # Seller Phone 7
		lRow.append('None')  # Seller Email 8
		lRow.append('None')  # Buyer Entity 9
		lRow.append('None')  # Buyer Person 10
		lRow.append('None')  # Buyer Street 11
		lRow.append('None')  # Buyer City 12
		lRow.append('None')  # Buyer State 13
		lRow.append('None') # Buyer Zip 14
		lRow.append('None')  # Buyer Country 15
		lRow.append('None') # Buyer Phone 16
		lRow.append('None')  # Buyer Email 17
		lRow.append(r['acres'])  # Acres 18
		lRow.append('None')  # Buyer Acting As 19
		lRow.append(r['city'])  # City 20
		lRow.append(r['landUse'])  # Classification 21
		lRow.append('USA')  # Country 22
		lRow.append(r['county'])  # County 23
		lRow.append(r['description'])  # Description 24
		lRow.append('None')  # General Plan 25
		lRow.append('None')  # Keyword Group 26
		lRow.append(d['latitude'])  # Latitude 27
		lRow.append(r['leadParcel'])  # Lead Parcels 28
		lRow.append('None')  # Legal Description 29
		lRow.append(d['location'])  # Location 30
		lRow.append(d['longitude'])  # Longitude 31
		lRow.append('None')  # Lot Description 32
		lRow.append('None')  # Lot Type 33
		lRow.append('None')  # Lots 34
		lRow.append('Boise')  # Market 35
		lRow.append('None')  # Deal Name 36
		lRow.append(r['parcels'])  # Parcels 37
		lRow.append('None')  # Record Doc ID 38
		if r['closingDate'] == 'None':
			lRow.append('None')  # Sale Date 39
		else:
			# lRow.append(lao.dateFormat(r['closingDate'], informat='slash'))  # Sale Date 39
			lRow.append(td.date_engine(r['closingDate'], outformat='TF', informat='slash'))  # Sale Date 39
		if r['priceSold'] == 'None':
			lRow.append(10000)
		else:
			lRow.append(r['priceSold'])  # Sale Price 40
		lRow.append('MLS')  # Source 41
		lRow.append(r['mlslink'])  # Source ID 42
		lRow.append('Idaho')  # State 43
		lRow.append('None')  # Subdivision 44
		lRow.append('None')  # Submarket 45
		lRow.append(r['zipcode']) # Zip Code 46
		lRow.append(r['zoning'])  # Zoning 47
		lRow.append('None')  # List Date 48
		lRow.append(r['priceAsking'])  # List Price 49
		lRow.append(r['listEntity'])  # List Entity 50
		lRow.append(r['listingAgent']) # List Agent 51
		lRow.append(r['listAgentPhone'])  # List Agent Phone 52
		lRow.append(r['listAgentEmail'])  # List Agent Email 53
		lRow.append('None')  # Alt APN A 54
		lRow.append('None')  # Alt APN B 55
		lRow.append('None')  # PID 56
		lRow.append(r['residence'])  # Residence Y-N 57
		lRow.append('None')  # Terms 58
		lRow.append('None')  # Rec Doc URL 59
		lRow.append('None')  # Notes A 60
		lRow.append('None')  # Lender 61
		lRow.append('None')  # Loan Amount 62
		lRow.append('None')  # Loan Date 63
		lRow.append('None')  # Buyer Agent Entity 64
		lRow.append('None') # Buyer Agent 65
		lRow.append('None') # Buyer Agent Phone 66
		lRow.append('None')  # Buyer Agent Email 67
		lRow.append(r['mlsStatus'])  # MLS Status 68

		# Replace Blanks with None
		for n, i in enumerate(lRow):
			if i == '':
				lRow[n] = 'None'

		fout.writerow(lRow)

lao.openFile(outFile)