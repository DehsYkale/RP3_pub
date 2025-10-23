#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Creates a top subdivision csv for Market Overviews and Market Insights
import acc
print('\n Importing arcpy...')
import arcpy
from arcpy import env
import csv
from glob import glob
import how
import lao
import os.path
from pprint import pprint
import fun_text_date as td
import warnings
import xlrd
import xlwings as xw

def get_mimo_tnhc_market_lists():
	dMIMO_TNHC_Market_Lists = {'MIMO': {}, 'TNHC': {}, 'TNHC VDL':{}}

	csvTop_MPC_Starts_Closings_File_Temp = 'F:/Research Department/MIMO/Master Spreadsheet Data/Zonda Top MPCs Starts Closings All Markets.csv'
	csvTop_MPC_VDL_File_Temp = 'F:/Research Department/MIMO/Master Spreadsheet Data/Zonda Top MPCs VDL All Markets.csv'
	with open(csvTop_MPC_Starts_Closings_File_Temp, 'wb') as g:  # Clear past csv file
		outcsv = csv.writer(g)
	with open(csvTop_MPC_VDL_File_Temp, 'wb') as g:  # Clear past csv file
		outcsv = csv.writer(g)

	# All Markets
	dMIMO_TNHC_Market_Lists['MIMO']['infile'] = csvTop_MPC_Starts_Closings_File_Temp
	dMIMO_TNHC_Market_Lists['MIMO']['outFile'] = 'F:/Research Department/MIMO/Master Spreadsheet Data/Zonda Top MPCs MIMO Markets.xls'
	dMIMO_TNHC_Market_Lists['MIMO']['lMarkets'] = [
			'ATL',
			'AUS',
			'BOI',
			'CLT',
			'DFW',
			'HOU',
			'IEP',
			'JAX',
			'LVS',
			'NSH',
			'ORL',
			'PHX',
			'PRC',
			'RNO',
			'SAC',
			'SEA',
			'SLC',
			'SRQ',
			'TPA',
			'TUC']
	# TNHC Markets
	dMIMO_TNHC_Market_Lists['TNHC']['infile'] = csvTop_MPC_Starts_Closings_File_Temp
	dMIMO_TNHC_Market_Lists['TNHC']['outFile'] = 'F:/Research Department/MIMO/Master Spreadsheet Data/Zonda Top MPC TNHC Sales Closings Markets.xls'
	dMIMO_TNHC_Market_Lists['TNHC']['lMarkets'] = [
			'AUS',
			'CLT',
			'DFW',
			'HOU',
			'IEP',
			'NSH',
			'ORL',
			'PHX',
			'SAC',
			'SLC',
			'SEA']
	dMIMO_TNHC_Market_Lists['TNHC VDL']['infile'] = csvTop_MPC_VDL_File_Temp
	dMIMO_TNHC_Market_Lists['TNHC VDL']['outFile'] = 'F:/Research Department/MIMO/Master Spreadsheet Data/Zonda Top MPC VDL TNHC Markets.xls'
	dMIMO_TNHC_Market_Lists['TNHC VDL']['lMarkets'] = dMIMO_TNHC_Market_Lists['TNHC']['lMarkets']
	return dMIMO_TNHC_Market_Lists

def get_submarket_From_Lon_Lat(x, y):
	# # Create point from lon/lats and make dynamic feature class
	# Create point file
	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(x, y), sr)
	# Asigning new shapefile name to variable
	fLonLatPnt = "fc_temp_point_get_geo_info_lon_lat.shp"
	# Delete if point file already exists
	if os.path.exists('C:/Users/Public/Public Mapfiles/{0}'.format(fLonLatPnt)) is True:
		arcpy.Delete_management(fLonLatPnt)
	# Create point shape file
	arcpy.CopyFeatures_management(inFeaturesPoints, fLonLatPnt)
	arcpy.SelectLayerByLocation_management(lyrSubmarkets, "INTERSECT", fLonLatPnt)
	submarket_fields = ["submarket"]
	submarket_data = arcpy.da.SearchCursor(lyrSubmarkets, submarket_fields)

	# Get Submarket Name
	for row in submarket_data:
		submarket = row[0]
	try:
		return submarket
	except UnboundLocalError:
		pass
		# td.warningMsg('\n No submarket, getting county...')
	# Get county if no LAO submarket
	arcpy.SelectLayerByLocation_management(lyrCounties, "INTERSECT", fLonLatPnt)
	county_fields = ["county"]
	county_data = arcpy.da.SearchCursor(lyrCounties, county_fields)
	# Get the county
	for row in county_data:
		county = row[0]
	return county

warnings.filterwarnings("ignore")
lao.banner('Zonda Top MPC Formatter v05')
# Instructions
how.zonda_top_MPC_formater()

# Include column for Number of Builders
while 1:
	print( '\n  Select type of MPC data\n')
	print( '  1) MIMO')
	print( '  2) TNHC')
	print( ' 00) Quit')
	ui = td.uInput('\n  > ')
	if ui == '1':
		include_number_of_builders = False
		break
	elif ui == '2':
		include_number_of_builders = True
		break
	elif ui == '00':
		if ui == '00':
			exit('\n Terminating program...')
	else:
		td.warningMsg('\n Invalid input...try again...')
		lao.sleep(2)

if include_number_of_builders:
	# ArcMap Variables
	print('\n Loading Submarket MXD...')
	env.workspace = "C:/Users/Public/Public Mapfiles"
	fMXD = 'F:/Research Department/maps/mxd/get_Geo_Info_From_Lon_Lat_No_Projects.mxd'
	mxd = arcpy.mapping.MapDocument(fMXD)
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	lyrSubmarkets = arcpy.mapping.ListLayers(mxd, 'LAO_Submarkets', df)[0]
	lyrCounties = arcpy.mapping.ListLayers(mxd, 'US_Counties', df)[0]
	sr = arcpy.SpatialReference("WGS 1984")
	print('\n Submarket MXD loaded...')

# List and File Variables
dMIMO_TNHC_Market_Lists = get_mimo_tnhc_market_lists()
renameFile = '{0}MPCRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
dMPC_Rename = lao.spreadsheetToDict(renameFile) 
inFiles = glob('{0}*subs_20*.xls'.format(lao.getPath('metstud')))

csv_MPC_starts_closings = 'C:/TEMP/Zonda_MPC_Starts_Closings_Rank_Temp.csv'
csv_MPC_VDL = 'C:/TEMP/Zonda_MPC_VDL_Rank_Temp.csv'



for xlsfile in inFiles:
	market = xlsfile[45:]
	marketAbb = market[:3]

	if not 'PRC' in market:
		continue

	print('\n Processing {0}...'.format(marketAbb))

	book = xlrd.open_workbook(xlsfile)
	rowCount = book.sheet_by_index(0).nrows
	worksheet = book.sheet_by_index(0)

	dSubs = {}
	lSubs = []
	mktTotalStarts, mktTotalClosings, mktTotalVDL = 0, 0, 0

	# Read rows in MetroStudy subdivision file and write to dSub
	for i in range(1, rowCount):

		# Subdivison is a Community (MPC)
		subdivision = worksheet.row_values(i)[3]
		# Subdivison is not a Community (MPC)
		if subdivision == 'Undefined':
			subdivision = worksheet.row_values(i)[2]
		subdivision = td.standarize_MPC_names(subdivision, dMPC_Rename)
		# Catch UTF-8 characters
		subdivision = subdivision.encode('utf-8')
		starts = float(worksheet.row_values(i)[16])
		closings = float(worksheet.row_values(i)[17])
		vdl = float(worksheet.row_values(i)[25])
		lon = worksheet.row_values(i)[36]
		lon = float(lon.strip())
		lat = worksheet.row_values(i)[35]
		lat = float(lat.strip())

		# Skip Builtout
		if 'Builtout' in worksheet.row_values(i)[6]:
			mktTotalStarts = mktTotalStarts + starts
			mktTotalClosings = mktTotalClosings + closings
			mktTotalVDL = mktTotalVDL + vdl
			continue

		# Add Starts & Closings to Subdivions already found in Excel file
		if subdivision in dSubs:
			dSubs[subdivision]['Starts'] = dSubs[subdivision]['Starts'] + starts
			dSubs[subdivision]['Closings'] = dSubs[subdivision]['Closings'] + closings
			dSubs[subdivision]['VDL'] = dSubs[subdivision]['VDL'] + vdl
			mktTotalStarts = mktTotalStarts + starts
			mktTotalClosings = mktTotalClosings + closings
			mktTotalVDL = mktTotalVDL + vdl
		# Add Starts & Closings to first instance of Subdivion
		else:
			dSubs[subdivision] = {'Starts': starts, 'Closings': closings, 'VDL': vdl, 'Lon': lon, 'Lat': lat}
			mktTotalStarts = starts
			mktTotalClosings = closings
			mktTotalVDL = vdl
	
	# Write dSubs to csv for Starts & Closings
	with open(csv_MPC_starts_closings, 'wb') as f:
		fout = csv.writer(f)
		for sub in dSubs:
			if include_number_of_builders:  # TNHC
				fout.writerow([sub, '', dSubs[sub]['Starts'], dSubs[sub]['Closings'], dSubs[sub]['Lon'], dSubs[sub]['Lat']])
			else:
				fout.writerow([sub, dSubs[sub]['Starts'], dSubs[sub]['Closings'], dSubs[sub]['Lon'], dSubs[sub]['Lat']])
	
	# Write dSubs to csv
	with open(csv_MPC_VDL, 'wb') as f:
		fout = csv.writer(f)
		for sub in dSubs:
			fout.writerow([sub, dSubs[sub]['VDL'], dSubs[sub]['Lon'], dSubs[sub]['Lat']])

	# Sort subs by number of Closings for MIMO and Starts for TNHC
	with open(csv_MPC_starts_closings, 'rb') as f, open(dMIMO_TNHC_Market_Lists['TNHC']['infile'], 'ab') as g:
		incsv = csv.reader(f)
		outcsv = csv.writer(g)
		if include_number_of_builders:  # TNHC
			outcsv.writerow(['Market', marketAbb, '', '', ''])
			outcsv.writerow(['Subdivision', 'Number of Builders', 'Annual Starts', 'Annual Closings', 'Submarket'])
			sorted_csv = sorted(incsv, key=lambda x: float(x[2]), reverse=True)
		else:  # MIMO
			outcsv.writerow(['Market', marketAbb, ''])
			outcsv.writerow(['Subdivision', 'Annual Starts', 'Annual Closings'])
			sorted_csv = sorted(incsv, key=lambda x: float(x[1]), reverse=True)
		
		i = 0
		for row in sorted_csv:
			i += 1
			if i <= 20:  # Limit to top 30 subs
				if include_number_of_builders:  # TNHC
					lon, lat = row[4], row[5]  # Get submarket from lon lat
					del row[-1]
					del row[-1]
					submarket = get_submarket_From_Lon_Lat(lon, lat)
					row.append(submarket)
				else:  # MIMO
					del row[-1]
					del row[-1]
				outcsv.writerow(row)
				

	if include_number_of_builders:    # TNHC
		# Sort subs by number of VDL
		with open(csv_MPC_VDL, 'rb') as f, open(dMIMO_TNHC_Market_Lists['TNHC VDL']['infile'], 'ab') as g:
			incsv = csv.reader(f)
			outcsv = csv.writer(g)
			outcsv.writerow(['Market', marketAbb, ''])
			outcsv.writerow(['Subdivision', 'VDL', 'Submarket'])
			sorted_csv = sorted(incsv, key=lambda x: float(x[1]), reverse=True)
			i = 0
			for row in sorted_csv:
				i += 1
				if i <= 20:  # Limit to top 30 subs
					lon, lat = row[2], row[3]  # Get submarket from lon lat
					del row[-1]
					del row[-1]
					submarket = get_submarket_From_Lon_Lat(lon, lat)
					row.append(submarket)
					outcsv.writerow(row)

# Write to Master CSV (not final temp file)
for sprdsht in dMIMO_TNHC_Market_Lists:
	lMarkets = dMIMO_TNHC_Market_Lists[sprdsht]['lMarkets']

	if include_number_of_builders:  # TNHC
		if sprdsht == 'MIMO':
			continue
	elif include_number_of_builders is False:  # MIMO
		if not sprdsht == 'MIMO':
			continue
			
	csv_inFile = dMIMO_TNHC_Market_Lists[sprdsht]['infile']
	xls_outFile = dMIMO_TNHC_Market_Lists[sprdsht]['outFile']
	# columns = dMIMO_TNHC_Market_Lists[sprdsht]['Columns']
	with open(csv_inFile, 'rb') as f:
		incsv = csv.reader(f)
		wb = xw.Book()
		sht = wb.sheets['Sheet1']

		c = 1 # Column
		r = 1 # Row
		isFirst = True
		print('\n Writing {0} Excel spreadsheet...\n'.format(sprdsht))
		for row in incsv:
			# print(row)
			if row[0] == 'Market':
				if row[1] in lMarkets:
					print(row[1]) # Market
					writeit = True
					if isFirst:
						# Set number of columns
						columns = len(row)
						isFirst = False
					else:
						c = c + columns
						r = 1
						sht.range(r, c).value = row
				else:
					writeit = False
			if writeit:
				sht.range(r, c).value = row
				r += 1

	wb.save(xls_outFile)

# lao.openFile(csvTop_MPC_Starts_Closings_File_Temp)