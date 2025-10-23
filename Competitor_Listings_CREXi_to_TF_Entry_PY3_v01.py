# Cycles through CREXi Excel file for competitor listings


# cls
# print('\n Loading arcpy TF_AWS_Make_Competitor_Listing_v01 main...')
import bb
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
import xlrd
import webs

# Clean comps and listings folders
lao.clean_comps_listings_files_folders()

service = fun_login.TerraForce()

td.banner('CREXi Competitor Listings TF Entry PY3 v01')
# Make Crexi Dictionary
filename = lao.guiFileOpen('F:/Research Department/Listings/', 'Open CREXi Excel XLS File', [('xls files', '.xls')])
xl_wb = xlrd.open_workbook(filename)
xl_sheet = xl_wb.sheet_by_index(0)
colcount = len(xl_sheet.row(0))
header = []
for i in range(0, colcount):
	header.append(xl_sheet.cell_value(0, i))
header.append('Link')
index = 0
dSht = {}
link = None

for row_idx in range(1, xl_sheet.nrows):
	index += 1
	dSht[index] = {}
	for i in range(0, colcount):
		dSht[index][header[i].upper()] = xl_sheet.cell_value(row_idx, i)
		if link is None:
			link = xl_sheet.hyperlink_map.get((row_idx, i))
	dSht[index]['Link'] = link.url_or_path
	link = None

# driver = fun_login.crexi()

for row in dSht:
	td.banner('CREXi Competitor Listings TF Entry PY3 v01')
	r = dSht[row]
	# Check if Link in Skip File
	if lao.SkipFile(r['Link'], 'skipListings', 'CHECK'):
		continue
	# TerraForce Query
	fields = 'default'
	wc = "Source_ID__c = '{0}'".format(r['Link'])
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	if results == []:
		print('\n Enter Record...\n')
	else:
		lao.SkipFile(r['Link'], 'skipListings', 'WRITE')
		continue

	# ascii codec error
	print(r['ADDRESS'])
	address = '{0}, {1}, {2} {3}'.format(r['ADDRESS'], r['CITY'], r['STATE'], int(r['ZIP']))
	propName = r['PROPERTY NAME']
	price = r['ASKING PRICE']
	print('\n Name: {0}'.format(propName))
	print('       {0}'.format(address))
	print(' Price: {0}'.format(price))
	lon, lat = mpy.get_lon_lat_from_address_or_intersection(address)
	print(' Lon: {0}'.format(lon))
	print(' Lat: {0}'.format(lat))

	fjson.create_ZoomToPolygon_json_file(fieldname='LonLat', polyId=None, polyinlayer=None, lon=lon, lat=lat)
	print('\n ArcMap Find Me File written...')

	# driver.get(r['Link'])
	webs.open_chrome(r['Link'])
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	while 1:
		ui = td.uInput('\n Copy to Skip File [0/1] > ')
		if ui == '1':
			lao.SkipFile(r['Link'], 'skipListings', 'WRITE')
			break
		elif ui == '0':
			break
		else:
			lao.warningMsg('\n Invalid input...try again...')
