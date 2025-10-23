# python3
# -*- coding: utf-8 -*-

print('\n Loading arcpy in "amp.py" main...')
# import arcpy
# from arcpy import env
import bb
from getpass import getuser
import fun_login
import lao
import os.path
from os import system
from sys import exit
import fun_text_date as td
from webbrowser import open as openbrowser
import geopandas as gpd
from shapely.geometry import Point


# List of parcel of LAO markets
def countyParcels(market='All'):
	if market == 'All':
		# return lao.getListResearchParcelLayerNames()
		return lao.getCounties('AllParcelsNames')
	if market == 'ID':
		return ['IDParcelsAda', 'IDParcelsCanyon', 'IDParcelsBoise']

# Create ArcMap Find Me file
def createArcMapFindMeFile(dd, idtype, showMessage=True):

	with open('C:/Users/Public/Public Mapfiles/find_me_pid_parcel.txt', 'w') as f:
		if idtype == 'PID':
			try:
				arcMapQuery = "pid in ('{0}')".format(dd['PID__c'])
			except TypeError:
				arcMapQuery = "pid in ('{0}')".format(dd)
		elif idtype == 'LEAD':
			arcMapQuery = "leadid in ('{0}')".format(dd)
		else:

			# Assign Lon Lat
			if 'Longitude__c' in dd:
				lon = dd['Longitude__c']
				lat = dd['Latitude__c']
			else:
				lon, lat = 'None', 'None'
			if lon == '':
				lon, lat = 'None', 'None'

			# Remove dashes from some counties
			dashCounties = ['Brazoria', 'Harris', 'Manatee', 'Polk', 'Yuma', 'SaltLake', 'Lake', 'Seminole']
			leadParcel = 'None'
			for dashCounty in dashCounties:
				if dashCounty == dd['County__c']:
					leadParcel = (dd['Lead_Parcel__c']).replace('-', '')
					break
			if leadParcel == 'None':
				leadParcel = dd['Lead_Parcel__c']

			# Add trailing 0 to Pima APNs
			if dd['County__c'] == 'Pima' and len(leadParcel) == 10:
				leadParcel = '{0}0'.format(leadParcel)

			# Check and remove Vizzda VPN virtual APN numbers
			if 'VPN-' in leadParcel:
				leadParcel = 'None'

			# Remove leading zero for Manatee
			if leadParcel[0] == '0' and dd['County__c'] == 'Manatee':
				leadParcel = leadParcel[1:]

			apnField = 'apn'

			# Write the ArcMap query
			state = lao.getCounties('State', '', dd['County__c'])
			if state == []:
				print("\n Did not find {0} county in creating find_me file.\n Add to county list csv.".format(dd['County__c']))
				exit('Terminating program...')
			arcMapQuery = "{0} in ('{1}'){2}Parcels{3}:{4}:{5}".format(apnField, leadParcel, state, dd['County__c'], lon, lat)
		if '(None)' in arcMapQuery:
			arcMapQuery = arcMapQuery.replace("(None)", "('None')")
		f.write(arcMapQuery)
		if showMessage:
			print('\n ArcMap Find Me file created...\n')

# Get MSA based on county
def getMSA(county, state):
	msa, L5Market = 'None', 'False'
	filepath = 'F:/Research Department/MIMO/zData/US MSA County List.xlsx'
	dMSA = lao.spreadsheetToDict(filepath)
	county = county.strip()
	msa = 'None'
	state = state.strip()
	for row in dMSA:
		d = dMSA[row]
		if (state in d['State'] or state == d['State Name']) and county in d['County']:
			msa = d['Market']
			L5Market = d['L5']
			return msa, L5Market
	return msa, L5Market

# Get City, County, Project, Submarket, OwnerIndex (Ownership), Zipcode info from Lon/Lat point
def get_Geo_Info_From_Lon_Lat(x, y, arcpy='None'):

	from bb import sfLogin
	if arcpy == 'None':
		print('\n Loading arcpy in amp.get_Geo_Info_From_Lon_Lat...')
		import arcpy
	from arcpy import env

	# service = sfLogin()
	service = fun_login.TerraForce()
	
	# user = lao.getUserName()
	# Set enviroment to write the lon/lat point shape file to
	env.workspace = "C:/Users/Public/Public Mapfiles"
	# Open mxd with the required layers on the Portal
	fMXD = 'F:/Research Department/maps/mxd/get_Geo_Info_From_Lon_Lat_No_Projects.mxd'
	mxd = arcpy.mapping.MapDocument(fMXD)
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

	# Assign layers to variables
	lyrCounties = arcpy.mapping.ListLayers(mxd, 'US_Counties', df)[0]
	lyrOwnerIndex = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	lyrProjects = arcpy.mapping.ListLayers(mxd, 'Projects', df)[0]
	lyrSubmarkets = arcpy.mapping.ListLayers(mxd, 'LAO_Submarkets', df)[0]
	lyrZipCodes = arcpy.mapping.ListLayers(mxd, 'ZipCodes', df)[0]

	# Create point from lon/lats and make dynamic feature class
	# Assign projection to variable
	sr = arcpy.SpatialReference("WGS 1984")
	# Create point file
	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(x, y), sr)
	# Asigning new shapefile name to variable
	fLonLatPnt = "fc_temp_point_get_geo_info_lon_lat.shp"
	# Delete if point file already exists
	if os.path.exists('C:/Users/Public/Public Mapfiles/{0}'.format(fLonLatPnt)) is True:
		arcpy.Delete_management(fLonLatPnt)
	# Create point shape file
	arcpy.CopyFeatures_management(inFeaturesPoints, fLonLatPnt)

	# select SubMarket polygon that intersects point
	arcpy.SelectLayerByLocation_management(lyrCounties, "INTERSECT", fLonLatPnt)
	arcpy.SelectLayerByLocation_management(lyrOwnerIndex, "INTERSECT", fLonLatPnt)
	arcpy.SelectLayerByLocation_management(lyrProjects, "INTERSECT", fLonLatPnt)
	arcpy.SelectLayerByLocation_management(lyrSubmarkets, "INTERSECT", fLonLatPnt)
	arcpy.SelectLayerByLocation_management(lyrZipCodes, "INTERSECT", fLonLatPnt)
	

	# Create list of requried fields
	county_fields = ["county"]
	county_data = arcpy.da.SearchCursor(lyrCounties, county_fields)
	ownerindex_fields = ["pid"]
	ownerindex_data = arcpy.da.SearchCursor(lyrOwnerIndex, ownerindex_fields)
	projects_fields = ["name", "symbol"]
	projects_data = arcpy.da.SearchCursor(lyrProjects, projects_fields)
	submarket_fields = ["submarket"]
	submarket_data = arcpy.da.SearchCursor(lyrSubmarkets, submarket_fields)
	zipcode_fields = ["PO_NAME", "STATE", "ZIP"]
	zipcode_data = arcpy.da.SearchCursor(lyrZipCodes, zipcode_fields)

	# Create Geo Info dict
	dGeoInfo = {
		'city': None,
		'competitor_listing': None,
		'county': None,
		'pid': None,
		'stagename': None,
		'state': None,
		'subdivision_name': None,
		'subdivision_status': None,
		'submarket': None,
		'zipcode': None
	}

	# Get the county
	for row in county_data:
		dGeoInfo['county'] = row[0]
		break

	# Get OwnerIndex/Ownerships PID, StageName, Competitor Listing
	results = arcpy.GetCount_management(lyrOwnerIndex)
	count = int(results.getOutput(0))
	# Query TF to check if Ownership exists
	if count != 0:
		for row in ownerindex_data:
			PID = row[0].strip()
			fields = 'Id, PID__c, StageName__c, RecordTypeId'
			wc = "PID__c = '{0}'".format(PID)
			qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
			results = bb.sfquery(service, qs)
			print(results)
			print(PID)
			if not 'Closed' in results[0]['StageName__c']:
				dGeoInfo['pid'] = PID
				dGeoInfo['stagename'] = results[0]['StageName__c']
				# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
				if results[0]['RecordTypeId'] == '012a0000001ZSS8AAO': # Research type
					dGeoInfo['competitor_listing'] = True
				else:
					dGeoInfo['competitor_listing'] = False
				break
		
	# Get Project Data
	results = arcpy.GetCount_management(lyrProjects)
	count = int(results.getOutput(0))
	if count != 0:
		for row in projects_data:
			dGeoInfo['subdivision_name'] = row[0]
			dGeoInfo['subdivision_status'] = row[1]

	# Get Submarket Name
	for row in submarket_data:
		dGeoInfo['submarket'] = row[0]

	# Get Zipcode & City
	for row in zipcode_data:
		dGeoInfo['city'] = row[0]
		dGeoInfo['state'] = row[1]
		dGeoInfo['zipcode'] = row[2]

	# delete the fc_temp.shp file
	arcpy.Delete_management(fLonLatPnt)

	return dGeoInfo

def getCitySubMarketZipCountyFromLonLat(service, x, y, wd, pd):
	
	print('\n Loading arcpy in amp.getCitySubMarketZipCountyFromLonLat...')
	import arcpy
	user = lao.getUserName()
	# Set enviroment to write the lon/lat point shape file to
	env.workspace = "C:/Users/Public/Public Mapfiles"
	# Open mxd with the required layers on the Portal
	mxd = arcpy.mapping.MapDocument('F:/Research Department/maps/mxd/getCitySubMarketZipCountyFromLonLat.mxd')
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

	# Assign layers to variables
	lyrCounties = arcpy.mapping.ListLayers(mxd, 'US_Counties', df)[0]
	lyrOwnerIndex = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	lyrProjects = arcpy.mapping.ListLayers(mxd, 'Projects', df)[0]
	lyrSubmarkets = arcpy.mapping.ListLayers(mxd, 'LAO_Submarkets', df)[0]
	lyrZipCodes = arcpy.mapping.ListLayers(mxd, 'ZipCodes', df)[0]

	# Create point from lon/lats and make dynamic feature class
	# Assign projection to variable
	sr = arcpy.SpatialReference("WGS 1984")
	# Create point file
	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(x, y), sr)

	# Asigning new shapefile name to variable
	in_shp = "fc_temp_point_getData1.shp"
	# Delete if point file already exists
	if os.path.exists('C:/Users/Public/Public Mapfiles/fc_temp_point_getData1.shp') is True:
		arcpy.Delete_management(in_shp)
	# Create point shape file
	arcpy.CopyFeatures_management(inFeaturesPoints, in_shp)

	# select SubMarket polygon that intersects point
	arcpy.SelectLayerByLocation_management(lyrCounties, "INTERSECT", in_shp)
	arcpy.SelectLayerByLocation_management(lyrOwnerIndex, "INTERSECT", in_shp)
	arcpy.SelectLayerByLocation_management(lyrProjects, "INTERSECT", in_shp)
	arcpy.SelectLayerByLocation_management(lyrSubmarkets, "INTERSECT", in_shp)
	arcpy.SelectLayerByLocation_management(lyrZipCodes, "INTERSECT", in_shp)

	# Create list of requried fields
	county_fields = ["county"]
	county_data = arcpy.da.SearchCursor(lyrCounties, county_fields)
	ownerindex_fields = ["pid"]
	ownerindex_data = arcpy.da.SearchCursor(lyrOwnerIndex, ownerindex_fields)
	projects_fields = ["name"]
	projects_data = arcpy.da.SearchCursor(lyrProjects, projects_fields)
	submarket_fields = ["submarket"]
	submarket_data = arcpy.da.SearchCursor(lyrSubmarkets, submarket_fields)
	zipcode_fields = ["ZIP", "PO_NAME"]
	zipcode_data = arcpy.da.SearchCursor(lyrZipCodes, zipcode_fields)

	# Get County Name
	for row in county_data:
		county = row[0]
		break
	# Get OwnerIndex/Ownerships Data
	results = arcpy.GetCount_management(lyrOwnerIndex)
	count = int(results.getOutput(0))
	if count != 0:
		wd['PID__c'] = None
		for row in ownerindex_data:
			print(row[0])
			PID = row[0]
			fields = 'Id, PID__c, StageName__c'
			wc = "PID__c = '{0}'".format(PID)
			qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
			results = bb.sfquery(service, qs)
			if results[0]['StageName__c'] == 'Lead' or results[0]['StageName__c'] == 'Top 100':
				wd['PID__c'] = row[0]
				break
	else:
		wd['PID__c'] = None
	# Get Project Data
	results = arcpy.GetCount_management(lyrProjects)
	count = int(results.getOutput(0))
	if count != 0:
		for row in projects_data:
			subdivision = row[0]
	else:
		subdivision = ' '

	# Get Submarket Name
	for row in submarket_data:
		submarket = row[0]
	# Get Zipcode & City
	for row in zipcode_data:
		city = row[1]
		zipcode = row[0]

	# Get Parcel Data

	if county == 'Maricopa':
		inFeaturesParcels = "LAO.gdb/AZParcelsMaricopa"
		pd['State'] = 'Arizona'
		parcels_fields = ["apn", "owner", "mailstreet", "mailcity", "mailstate", "mailzip"]
	elif county == 'Pinal':
		inFeaturesParcels = "LAO.gdb/AZParcelsPinal"
		pd['State'] = 'Arizona'
		parcels_fields = ["apn", "Owner", "MailStreet", "MailCity", "Mail", "mailzip"]
	arcpy.MakeFeatureLayer_management(inFeaturesParcels, "parcels_lyr")
	arcpy.SelectLayerByLocation_management("parcels_lyr", "INTERSECT", in_shp)
	parcels_fields = ["apn", "owner", "mailstreet", "mailcity", "mailstate", "mailzip"]
	with arcpy.da.SearchCursor("parcels_lyr", parcels_fields) as cursor:
		try:
			for row in cursor:
				pd['apn'] = row[0]
				pd['owner'] = row[1]
				pd['mailstreet'] = row[2]
				pd['mailcity'] = row[3]
				pd['mailstate'] = row[4]
				pd['mailzip'] = row[5]
			else:
				pd['apn'] = None
				pd['owner'] = None
				pd['mailstreet'] = None
				pd['mailcity'] = None
				pd['mailstate'] = None
				pd['mailzip'] = None
		except RuntimeError:
			print('PID/Parcel Find Failed ****************************************************')
			pd['apn'] = None
			pd['owner'] = None
			pd['mailstreet'] = None
			pd['mailcity'] = None
			pd['mailstate'] = None
			pd['mailzip'] = None

	# delete the fc_temp.shp file
	arcpy.Delete_management(in_shp)
	arcpy.Delete_management("parcels_lyr")

	return city, county, subdivision, submarket, zipcode, wd, pd

def getCitySubMarketZipFromLonLat(x, y, includesubmarkets=True, cityfieldname='name'):

	print('\n Loading arcpy in amp.getCitySubMarketZipFromLonLat...')
	import arcpy
	submarket = ''

	# set workspace
	env.workspace = "C:/Users/Public/Public Mapfiles"

	# assign geodatabases to variables
	inFeaturesCity = "LAO.gdb/Cities_LAO"
	inFeaturesZip = "LAO.gdb/ZipCodes"
	if includesubmarkets:
		inFeaturesSubMarket = "LAO.gdb/LAOSUBMARKETS"


	# make dynamic feature classes
	arcpy.MakeFeatureLayer_management(inFeaturesCity, "city_lyr")
	arcpy.MakeFeatureLayer_management(inFeaturesZip, "zipcodes_lyr")
	if includesubmarkets:
		arcpy.MakeFeatureLayer_management(inFeaturesSubMarket, "submarkets_lyr")

	# create point from lon/lats and make dynamic feature class
	# assign projection to variable
	sr = arcpy.SpatialReference("WGS 1984")
	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(x, y), sr)

	# assing new shapefile name to variable
	in_shp = "fc_temp_point_getData2.shp"
	if os.path.exists('C:/Users/Public/Public Mapfiles/fc_temp_point_getData2.shp') is True:
		arcpy.Delete_management(in_shp)
	arcpy.CopyFeatures_management(inFeaturesPoints, in_shp)

	# select polygon that intersects point
	arcpy.SelectLayerByLocation_management("city_lyr", "INTERSECT", in_shp)
	if includesubmarkets:
		arcpy.SelectLayerByLocation_management("submarkets_lyr", "INTERSECT", in_shp)
	arcpy.SelectLayerByLocation_management("zipcodes_lyr", "INTERSECT", in_shp)

	# copy selected SubMarket into a list
	city_fields = [cityfieldname]
	city_data = arcpy.da.SearchCursor("city_lyr", city_fields)
	zipcode_fields = ["ZIP", "PO_NAME"]
	zipcode_data = arcpy.da.SearchCursor("zipcodes_lyr", zipcode_fields)
	if includesubmarkets:
		submarket_fields = ["submarket"]
		submarket_data = arcpy.da.SearchCursor("submarkets_lyr", submarket_fields)

	city = 'None'

	results = arcpy.GetCount_management("city_lyr")
	count = int(results.getOutput(0))
	if count > 0:
		for row in city_data:
			city = row[0]

	if includesubmarkets:
		try:
			for row in submarket_data:
				submarket = row[0]
		except TypeError:
			submarket = ''
	else:
		submarket = ''

	for row in zipcode_data:
		if city == 'None':
			city = row[1]
		zipcode = row[0]

	# delete the fc_temp.shp file
	arcpy.Delete_management(in_shp)
	arcpy.Delete_management("zipcodes_lyr")
	arcpy.Delete_management("city_lyr")
	if includesubmarkets:
		arcpy.Delete_management("submarkets_lyr")

	return city, submarket, zipcode

def getSelectParcelFromAPN(service, apn, county, PID, date, initials):
	from arcpy import Exists
	from arcpy import Delete_management
	from arcpy import MakeFeatureLayer_management
	from arcpy import SelectLayerByAttribute_management
	from arcpy import Describe
	from arcpy import CreateFeatureclass_management
	from arcpy import Append_management
	from arcpy import UpdateCursor

	sfdriver = 'None'

	# set workspace
	env.workspace = "C:/Users/Public/Public Mapfiles"

	# ASSIGN GEODATABASES TO VARIABLES
	# temp file to hold selected parcel
	fc_temp_parcel = "LAO.gdb/temp_parcel"
	# Check if fc_temp_parcel.shp exists and if so delete it
	if Exists(fc_temp_parcel) is True:
		Delete_management(fc_temp_parcel)

	# destination file for new PIDs
	fc_out_Listings = "LAO.gdb/ID_Listings"
	# input parcel layer based on county
	if county == 'Ada':
		fc_in_Parcels = "LAO.gdb/IDparcelsAda"
		whereclause = '"PARCEL" = ' + "'" + apn + "'"
	elif county == 'Canyon':
		fc_in_Parcels = "LAO.gdb/IDParcelsCanyon"
		whereclause = '"APN" = ' + "'" + apn + "'"
	elif county == 'Maricopa':
		fc_in_Parcels = "LAO.gdb/AZParcelsMaricopa"

	# Check if feature layer (parcel_lyr) exists and if so delete it
	if Exists("parcel_lyr") is True:
		Delete_management("parcel_lyr")
	# make dynamic feature class of input parcel layer
	MakeFeatureLayer_management(fc_in_Parcels, "parcel_lyr")

	# select input parcel based on APN
	SelectLayerByAttribute_management("parcel_lyr", "NEW_SELECTION", whereclause)

	# create fc_temp_parcel file to hold selected parcel (parcle_lyr)
	out_path = "C:/Users/Public/Public Mapfiles/LAO.gdb"
	out_name = "temp_parcel"
	geometry_type = "POLYGON"
	template = fc_out_Listings
	spatial_reference = Describe(fc_out_Listings).spatialReference
	has_m = "DISABLED"
	has_z = "DISABLED"
	CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)

	# append selected parcel to fc_temp_parcel file
	Append_management("parcel_lyr", fc_temp_parcel, "NO_TEST")

	# assign PID values to fc_temp_parcel file
	cursor = UpdateCursor(fc_temp_parcel)
	for row in cursor:
		row.setValue("pid", PID)
		row.setValue("dateupdated", date)
		row.setValue("initials", initials)
		cursor.updateRow(row)
	del row
	del cursor
	print('fc_temp_parcel updated')
	# Append selected parcel to ID_Listings shapefile
	Append_management(fc_temp_parcel, fc_out_Listings, "TEST", "", "")
	print('fc_out_Listings updated')

def verifyParcelsExist(parcel_list):
	print('\n Loading arcpy in amp.verifyParcelsExist...')
	import arcpy
	# set workspace
	env.workspace = "C:/Users/Public/Public Mapfiles"

	# assign geodatabases to variables
	inf_parcels = r"LAO.gdb\AZParcelsMaricopa"

	# make dynamic feature classes
	arcpy.MakeFeatureLayer_management(inf_parcels, "parcel_lyr")

	# Make where_clause
	pl = ','.join("'{0}'".format(x) for x in parcel_list)
	wc = "apn in (" + pl + ")"

	# Select the parcels
	arcpy.SelectLayerByAttribute_management("parcel_lyr","NEW_SELECTION", wc)

	# Assign selected parcels to variable rows
	rows = arcpy.SearchCursor('parcel_lyr', fields="apn")

	# Make the parcel list to return
	selection_list = []
	for row in rows:
		selection_list.append(row.getValue("apn"))

	missing_parcel_list = []
	for val in parcel_list:
		if val not in selection_list:
			missing_parcel_list.append(val)
	if len(missing_parcel_list) > 0:
		# print '%d missing parcels...\n%s' % (len(missing_parcel_list), ', '.join("{0}".format(x) for x in missing_parcel_list))
		print('{0} missing parcels...\n{1}'.format(len(missing_parcel_list), ', '.join("{0}".format(x) for x in missing_parcel_list)))
	else:
		print('All parcels selected...')
	return missing_parcel_list

	arcpy.Delete_management('parcel_lyr')

def updateOwnershipsSaleMap():
	from os import system
	from arcpy import Delete_management
	from arcpy import FeatureClassToGeodatabase_conversion

	# td.uInput('WARNING - CLOSING ARCMAP!\n\nContinue...')
	system('taskkill /f /im ArcMap.exe')
	print('\ArcMap closed...')

	env.workspace = "C:/Users/Public/Public Mapfiles/LAO.gdb"
	Delete_management("ownerships")
	print('Ownerships deleted...')
	Delete_management("salemap")
	print('SaleMap deleted...')

	arcversion = '8'
	env.workspace = "C:/Users/{0}/AppData/Roaming/ESRI/Desktop10.{1}/ArcCatalog/spatialdb10{1}_vectors_arcadmin.sde".format(getuser().lower(), arcversion)
	laogdb = "C:/Users/Public/Public Mapfiles/LAO.gdb"
	copy_fcs = ["vectors.arcadmin.ownerships", "vectors.arcadmin.salemap"]
	FeatureClassToGeodatabase_conversion(copy_fcs, laogdb)

def confirmPIDdigitized(PID):
	print('\n Loading arcpy in amp.confirmPIDdigitized...')
	import arcpy
	env.workspace = "C:/Users/Public/Public Mapfiles"
	oi_area = 'C:/Users/Public/Public Mapfiles/oi_lyr_area.shp'
	if os.path.isfile(oi_area):
		arcpy.Delete_management(oi_area)
	148

	if arcpy.Exists("oi_lyr_area_fl"):
		arcpy.Delete_management("oi_lyr_area_fl")
	# inf_oi = r'C:/Users/blandis/mapfiles/LAO.gdb/OWNERINDEX'
	arcversion = '8'
	inf_oi = 'C:/Users/{0}/AppData/Roaming/ESRI/Desktop10.{1}/ArcCatalog/spatialdb10{1}_vectors_arcadmin.sde/vectors.arcadmin.OWNERINDEX'.format(getuser().lower(), arcversion)

	arcpy.MakeFeatureLayer_management(inf_oi, "oi_lyr").format(getuser().lower())
	wc = "pid in ('" + PID + "')"
	arcpy.SelectLayerByAttribute_management("oi_lyr","NEW_SELECTION", wc)
	result = arcpy.GetCount_management("oi_lyr")
	count = int(result.getOutput(0))
	acres = 0
	if count == 1:
		arcpy.CalculateAreas_stats("oi_lyr", "oi_lyr_area")
		arcpy.MakeFeatureLayer_management(oi_area, "oi_lyr_area_fl")
		fcSearch = arcpy.SearchCursor("oi_lyr_area_fl")
		for row in fcSearch:
			sqmeters = row.getValue("F_AREA")
			acres = sqmeters/4046.86 # Sq meters in an acre
			break
	arcpy.Delete_management(oi_area)
	arcpy.Delete_management("oi_lyr")
	if arcpy.Exists("oi_lyr_area_fl"):
		arcpy.Delete_management("oi_lyr_area_fl")
	return count, acres

def stripTags(html):
	writeit = False
	text = ''
	for c in html:
		if c == '<':
			writeit = False
		if c == '>':
			writeit = True
			continue
		if writeit is True:
			text = '%s%s' % (text, c)
	return text

def streetTypeValue(type):
	if type == 'motorway':
		return 5
	elif type == 'primary':
		return 4
	elif type == 'secondary':
		return 3
	elif type == 'tertiary':
		return 2
	elif type == 'residential':
		return 1
	else:
		return -5

def locationIntersection(lat, lon, YCenter, XCenter):
	from urllib.request import urlopen
	url = 'http://api.geonames.org/findNearestIntersectionOSM?lat=%s&lng=%s&username=laoblandis' % (lat, lon)
	txt = urlopen(url)

	street1 = 'None'
	for row in txt:
		if '<street1>' in row:
			street1 = (stripTags(row)).strip()
		elif '<street2>' in row:
			street2 = (stripTags(row)).strip()
		elif '<highway1>' in row:
			highway1 = (stripTags(row)).strip()
			hwyval1 = streetTypeValue(highway1)
		elif '<highway2>' in row:
			highway2 = (stripTags(row)).strip()
			hwyval2 = streetTypeValue(highway2)
		elif '<distance>' in row:
			distance = float((stripTags(row)).strip())
		elif '<lat>' in row:
			latitude = float(stripTags(row))
		elif '<lng>' in row:
			longitude = float(stripTags(row))

	if street1 == 'None':
		return ['None', '', '', 0, 0]

	if YCenter > latitude:
		latdirection = 'N'
	else:
		latdirection = 'S'
	if XCenter < longitude:
		londirection = 'W'
	else:
		londirection = 'E'

	if distance < 0.3:
		bearing = '%s%sC' % (latdirection, londirection)
	else:
		bearing = '%s%s of' % (latdirection, londirection)

	hwyval = hwyval1 + hwyval2

	location = '%s %s & %s' % (bearing, street1, street2)
	l = [location, highway1, highway2, distance, hwyval]
	return l

# Select parcels with centroid in PID
def selectParcelsInPID(mxd, PID):
	from arcpy import AddMessage
	from arcpy import mapping
	from arcpy import SelectLayerByAttribute_management
	from arcpy import MakeFeatureLayer_management
	from arcpy import SearchCursor
	from arcpy import SelectLayerByLocation_management
	from arcpy import GetCount_management
	from arcpy import Delete_management


	AddMessage('\n Selecting parcels from PID...')

	# Clear any existing selections
	df = mapping.ListDataFrames(mxd, "Layers") [0]
	# ClearLayers = lao.getListResearchParcelLayerNames()
	ClearLayers = lao.getCounties('AllParcelsNames')
	ClearLayers.append('OwnerIndex')
	ClearLayers.append('US_Counties')

	for polyLayerClear in ClearLayers:
		for lyr in mapping.ListLayers(mxd, "", df):
			if lyr == polyLayerClear:
				AddMessage(polyLayerClear)
				clearlyr = mapping.ListLayers(mxd, polyLayerClear, df)[0]
				SelectLayerByAttribute_management(clearlyr, "CLEAR_SELECTION")
				break
	AddMessage(' Layers cleared...')

	# Select OwnerIndex polygon based on user entered PID
	MakeFeatureLayer_management('OwnerIndex', "oi_lyr")
	wc = "PID in ('{0}')".format(PID)
	SelectLayerByAttribute_management("oi_lyr","NEW_SELECTION", wc)
	for row in SearchCursor("oi_lyr"):
		selectedPID = row.pid
		# AddMessage(' Selected PID is %s...' % selectedPID)
	AddMessage(' OwnerIndex polygon %s selected...' % PID)

	# Determine county
	MakeFeatureLayer_management('US_Counties', "counties")
	# system('taskkill /f /im ArcGISCacheMgr.exe')
	# system('taskkill /f /im ArcGISConnection.exe')
	SelectLayerByLocation_management("counties","INTERSECT","oi_lyr","#","NEW_SELECTION")
	for row in SearchCursor("counties"):
		county_name = row.county
		state_abb_name = row.state
		# Get rid of spaces in county name
		county_name = county_name.replace(' ', '')
		AddMessage(' County: {0}'.format(county_name))
		lCounties = lao.getCounties('AllCounties ArcName')
		if not county_name in lCounties:
			continue

		# Create Parcel FC and get the Owner field name in the Parcel layer to use to remove HOAs, NAP and Null parcels
		owner_field_name = setParcelLayerToQuery(county_name, state_abb_name)
		AddMessage(' Selected County Owner Field is {0}...'.format(owner_field_name))
		# Select the parcels within the PID
		parcel_count = int(GetCount_management("parcel_lyr").getOutput(0))
		AddMessage(' Pre-Query Parcel Count = {0} '.format(parcel_count))
		SelectLayerByLocation_management("parcel_lyr","HAVE_THEIR_CENTER_IN","oi_lyr","#","NEW_SELECTION")

		# Remove HOAs, NAP and Null parcels
		remove_list = ['COMMUNITY ALLIANCE', 'COMMUNITY ASSOC', 'HOMEOWNERS ASSOC', ' HOA', 'HOMEOWNERS ASSN', 'COMMUNITY MASTER ASSOC', 'TOWN SQUARE ASSOC']
		wc = '"apn" LIKE \'%NAP%\' OR "apn" IS NULL OR "apn" LIKE \'%--%\' OR '
		for row_remove in remove_list:
			wc = '{0}"{1}" LIKE \'%{2}%\' OR '.format(wc, owner_field_name, row_remove)
		wc = wc[:-4]
		try:
			SelectLayerByAttribute_management("parcel_lyr", "REMOVE_FROM_SELECTION", wc)
		except:
			pass
		parcel_count = int(GetCount_management("parcel_lyr").getOutput(0))
		AddMessage(' Post-Query Parcel Count = {0} '.format(parcel_count))

		# Delete parcel_lyr FC if no records selected
		if parcel_count == 0:
			Delete_management("parcel_lyr")
		else:
			break

	return parcel_count

# Set the Feature Layer to the parcel name and owner field name
def setParcelLayerToQuery(county_name, state_abb_name):
	from arcpy import AddError
	from arcpy import AddMessage
	from arcpy import MakeFeatureLayer_management

	parcel_layer_name = '{0}Parcels{1}'.format(state_abb_name, county_name)
	parcelDict = lao.getCounties('ArcParcelLayers')

	for row in parcelDict:
		if county_name == 'Lake': # Lake FL vs SaltLake UT
			MakeFeatureLayer_management('FLParcelsLake', "parcel_lyr")
			owner_field_name = parcelDict['FLParcelsLake']
			return owner_field_name
		if parcel_layer_name in row:
			MakeFeatureLayer_management(row, "parcel_lyr")
			owner_field_name = parcelDict[row]
			AddMessage(' Feature Layer created...')
			return owner_field_name

	AddMessage(' County is %s...' % county_name)
	AddError(' Could not find {0} in list: amp > setParcelLayerToQuery County/Owner field list'.format(county_name))
	exit()

# Retruns intersection or address based on lon/lat
def getIntersection(lon, lat, askManually=True, findAddress=False):
	import requests
	import sys
	from pprint import pprint
	# Set text to utf-8
	reload(sys)
	sys.setdefaultencoding('utf-8')

	if findAddress:
		lonlat = '{0},{1}'.format(lon, lat)
		url = 'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?'
		params = {'f': 'pjson', 'featureTypes': 'StreetAddress', 'location': lonlat}
		r = requests.get(url, params=params)
		try:
			return r.json()['address']['Match_addr']
		except:
			return 'None'

	# Try GeoNames first
	# url = 'http://api.geonames.org/findNearestIntersectionOSMJSON?'
	# params = {'lat': lat, 'lng': lon, 'username': 'laoblandis'}
	# try:
	# 	r = requests.get(url, params=params)
	# 	results = '{0} & {1}'.format(r.json()['intersection']['street1'], r.json()['intersection']['street2'])
	# 	return results
	# except:
	# 	pass
	# Try ArcGIS
	lonlat = '{0},{1}'.format(lon, lat)
	url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?'
	params = {'f': 'pjson', 'featureTypes': 'StreetInt', 'location': lonlat}
	r = requests.get(url, params=params)
	try:
		return r.json()['address']['Address']
	except:
		pass

	if askManually:
		td.warningMsg(' No intersection found...')
		ui = td.uInput('\n Manually enter intersection > ')
		if ui == '':
			return '.'
		else:
			return ui
	return 'None'

def getLonLatFromAddressIntersection(address):
	import requests
	import re
	# Remove all non-alphanumeric characters except spaces
	address = re.sub(r'([^\s\w]|_)+', '', address)
	address = address.replace('  ', '%20')
	address = address.replace(' ', '%20')
	req = requests.get('https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=pjson&outFields=Addr_type&forStorage=false&SingleLine={}'.format(address))
	lon = req.json()['candidates'][0]['location']['x']
	lat = req.json()['candidates'][0]['location']['y']
	return lon, lat

def getPIDCentriodLonLat(PID):
	print('\n Loading arcpy in amp.getPIDCentriodLonLat...')
	import arcpy
	env.workspace = "C:/Users/Public/Public Mapfiles"
	if arcpy.Exists("oi_lyr"):
		arcpy.Delete_management("oi_lyr")
	
	arcversion = '8'
	inf_oi = 'C:/Users/{0}/AppData/Roaming/ESRI/Desktop10.{1}\ArcCatalog/spatialdb10{1}_vectors_arcadmin.sde/vectors.arcadmin.OWNERINDEX'.format(getuser().lower(), arcversion)
	arcpy.MakeFeatureLayer_management(inf_oi, "oi_lyr")
	wc = "pid in ('{0}')".format(PID)
	arcpy.SelectLayerByAttribute_management("oi_lyr","NEW_SELECTION", wc)
	for row in arcpy.SearchCursor("oi_lyr"):
		geom = row.shape
		ext = geom.extent
		break
	lon = float((ext.XMax + ext.XMin) / 2)
	lat = float((ext.YMax + ext.YMin) / 2)
	arcpy.Delete_management("oi_lyr")
	return lon, lat

def getPIDLocation(PID, service=False):
	lon, lat = getPIDCentriodLonLat(PID)
	location = getIntersection(lon, lat)
	if location == '':
		return ''
	elif service:
		DID = bb.getDIDfromPID(service, PID)
		upD = {'type': 'lda_Opportunity__c',
			   'Id': DID,
			   'Location__c': location}
		bb.tf_update_3(service, upD)
	else:
		return location

def pidExists(PID):
	from arcpy import Exists
	from arcpy import Delete_management
	from arcpy import MakeFeatureLayer_management
	from arcpy import SelectLayerByAttribute_management
	from arcpy import GetCount_management

	env.workspace = "C:/Users/Public/Public Mapfiles"
	if Exists("oi_lyr"):
		Delete_management("oi_lyr")
	arcversion = '8'
	inf_oi = 'C:/Users/{0}/AppData/Roaming/ESRI/Desktop10.{0}/ArcCatalog/spatialdb10{1}_vectors_arcadmin.sde/vectors.arcadmin.OWNERINDEX'.format(
		getuser().lower(), arcversion)
	MakeFeatureLayer_management(inf_oi, "oi_lyr")
	wc = "pid in ('{0}')".format(PID)
	SelectLayerByAttribute_management("oi_lyr", "NEW_SELECTION", wc)
	count = GetCount_management("oi_lyr")
	count = int(count[0])
	if count == 1:
		return True
	elif count == 0:
		print('\n No polygons found with PID {0}.\n May need to save OwnerIndex in ArcMap...'.format(PID))
		return False
	else:
		print('\nFound multiple polygons with PID {0}'.format(PID))
		return False

def makeNewOwnerIndexLeadJsonFile(action, salePID=None, leadPID=None, islotoption=False):
	import json
	# import lao

	user = lao.getUserName().lower()
	initials = user[:2].upper()
	d = {}
	d['action'] = action
	d['islotoption'] = islotoption
	d['salePID'] = salePID
	d['leadPID'] = leadPID
	d['initials'] = initials
	d['dateupdated'] = td.today_date('slash')

	with open('C:/TEMP/make_lead_pid_data.json', 'w') as f:
		json.dump(d, f)

def makeNewOwnerIndexLeadJsonFile2(action, salePID=None, leadPID=None, islotoption=False):

	import json
	from datetime import datetime
	# import lao

	user = lao.getUserName().lower()
	initials = user[:2].upper()
	d = {}
	d['action'] = action
	d['islotoption'] = islotoption
	d['salePID'] = salePID
	d['leadPID'] = leadPID
	d['initials'] = initials
	d['dateupdated'] = td.today_date('slash')

	now = datetime.now()
	timeNowString = now.strftime('%m_%d_%H_%M_%S')

	jsonFile = 'C:/TEMP/make_lead_pid_data_{0}.json'.format(timeNowString)
	with open(jsonFile, 'w') as f:
		json.dump(d, f)

def makeNewOwnerIndexLeadJsonFile3(action, salePID=None, leadPID=None, islotoption=False, polyIndex=0):
	import json
	from datetime import datetime

	now = datetime.now()
	timeNowString = now.strftime('%m_%d_%H_%M_%S')

	user = lao.getUserName().lower()
	initials = user[:2].upper()
	d = {}
	d['action'] = action
	d['islotoption'] = islotoption
	d['salePID'] = salePID
	d['leadPID'] = leadPID
	d['initials'] = initials
	d['dateupdated'] = td.today_date('slash')
	d['polyIndex'] = polyIndex

	jsonFile = 'C:/TEMP/make_lead_pid_data_{0}.json'.format(timeNowString)
	with open(jsonFile, 'w') as f:
		json.dump(d, f)

# Get and make an sequencial index number to attach to temp Arc FCs
def getPolyIndex():
	import json
	import os.path
	from os import path

	polyIndexFile = 'C:/TEMP/polyIndex.json'
	# If polyIndex.json file exits, open it, get polyIndex number, write new file
	#   with +1 added to old polyIndex
	if path.exists(polyIndexFile):
		with open(polyIndexFile, 'r') as f:
			d = json.load(f)
			polyIndex = d['polyIndex']
		# Cycle back to 1 if the polyIndex number is greater than 98
		if polyIndex > 499:
			newpolyIndex = 1
		else:
			newpolyIndex = polyIndex + 1
		d = {'polyIndex': newpolyIndex}
		with open(polyIndexFile, 'w') as f:
			json.dump(d, f)
	# Create the polyIndex.json file if it does not exist
	else:
		polyIndex = 1
		d = {'polyIndex': 2}
		with open(polyIndexFile, 'w') as f:
			json.dump(d, f)
	
	return polyIndex

def makeLeadForClosedDeal(service, salePID, leadPID):
	import aws
	print('\n ------------------------------------------------------------------')
	print('\n Sale PID: {0}'.format(salePID))
	print(' Lead PID: {0}'.format(leadPID))
	print('\n Creating new polygon for Lead...')
	# Check if Stage Name is Closed
	fields = 'Id, PID__c, StageName__c'
	wc = "PID__c = '{0}'".format(salePID)
	qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
	results = bb.sfquery(service, qs)
	if not 'Closed' in results[0]['StageName__c']:
		td.warningMsg(' Not a Closed Sale...Lead {0} not created...continue...'.format(leadPID))
		return
	PID = results[0]['PID__c']

	aws.make_AWS_OwnerIndex_Poly_from_OwnerIndex_Poly(PID=salePID, PIDnew=leadPID, runASW=True)
	return

# Deletes the local copy of FileCabinet.gdb to reduce file size on local disk
def deleteFileCabinetGDB():
	from arcpy import Exists, Delete_management, CreateFileGDB_management
	if Exists('C:/Users/Public/Public Mapfiles/FileCabinet.gdb'):
		try:
			Delete_management('C:/Users/Public/Public Mapfiles/FileCabinet.gdb')
			CreateFileGDB_management('C:/Users/Public/Public Mapfiles/', 'FileCabinet.gdb')
		except arcpy.ExecuteError:
			print('\n FileCabinet.gdb not deleted...')

# Get the market that Market Master MXD is working in by the Group Layer name
def getMarketMasterMXDMarket(arcpy='None'):
	if arcpy == 'None':
		print('\n Loading arcpy in amp.getMarketMasterMXDMarket...')
		import arcpy
	mxd = arcpy.mapping.MapDocument("CURRENT")
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	# The first layer will be the market name
	market = arcpy.mapping.ListLayers(mxd, "", df)[0].name
	return market

# Get the Market from lon lat coords
def getMarketMasterMXDMarketFromLonLat(x, y, arcpy='None'):
	if arcpy == 'None':
		print('\n Loading arcpy in amp.getMarketMasterMXDMarketFromLonLat...')
		import arcpy
	from arcpy import env
	import os
	env.workspace = "C:/Users/Public/Public Mapfiles"

	# assign geodatabases to variables
	inFeaturesCounty = r"LAO.gdb\US_Counties"
	# make dynamic feature classes
	if arcpy.Exists("county_lyr"):
			arcpy.Delete_management("county_lyr")
	arcpy.MakeFeatureLayer_management(inFeaturesCounty, "county_lyr")

	# create point from lon/lats and make dynamic feature class
	# assign projection to variable
	sr = arcpy.SpatialReference("WGS 1984")

	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(x, y), sr)

	# asigning new shapefile name to variable
	in_shp = "fc_temp_point_getData1.shp"
	if os.path.exists('C:/Users/Public/Public Mapfiles/fc_temp_point_getData1.shp') is True:
		arcpy.Delete_management(in_shp)
	arcpy.CopyFeatures_management(inFeaturesPoints, in_shp)

	# select SubMarket polygon that intersects point
	arcpy.SelectLayerByLocation_management("county_lyr", "INTERSECT", in_shp)

	# copy selected SubMarket into a list
	county_fields = ["county"]
	county_data = arcpy.da.SearchCursor("county_lyr", county_fields)

		# Get County Name
	for row in county_data:
		county = row[0]
		break

	dCounties = lao.getCounties('FullDict')
	
	for row in dCounties:
		if county == dCounties[row]['County']:
			return dCounties[row]['Market'], dCounties[row]['ArcName']

def zoomToMarket(arcpy, df, lon, lat, mxd):
	from os import path
	# create point from lon/lats and make dynamic feature class
	# assign projection to variable
	prjPath = 'F:/Research Department/maps/Projections/'
	prjWGS84File = '{0}GCS_WGS_1984.prj'.format(prjPath)
	sr = arcpy.SpatialReference(prjWGS84File)

	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(lon, lat), sr)

	# assing new shapefile name to variable
	in_shp = "C:/Users/Public/Public Mapfiles/fc_temp_point_zoom.shp"
	if path.exists('C:/Users/Public/Public Mapfiles//fc_temp_point_zoom.shp') is True:
		arcpy.Delete_management(in_shp)
	arcpy.CopyFeatures_management(inFeaturesPoints, in_shp)

	templyr = arcpy.mapping.Layer(in_shp)
	arcpy.mapping.AddLayer(df, templyr)
	lyr = arcpy.mapping.ListLayers(mxd, 'fc_temp_point_zoom', df)[0]
	whereclause = '"FID" = 0'
	arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
	df.zoomToSelectedFeatures()
	df.scale = 200000.00
	arcpy.mapping.RemoveLayer(df, lyr)
	arcpy.Delete_management(in_shp)

# Zoom to LAO market using Market Master map bookmark
def zoomToLAOMarketBookmark(arcpy, df, mxd, market):
	for bkmk in arcpy.mapping.ListBookmarks(mxd, "", df):
		if market == bkmk.name:
			arcpy.AddMessage(bkmk.name)
			df.extent = bkmk.extent
			break

# Zoom to OwnerIndex PID
def zoomToPID(arcpy, df, mxd, PID, clearSelection=False):
	lyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
	whereclause = "pid in ('{0}')".format(PID)
	arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
	count = int(arcpy.GetCount_management(lyr).getOutput(0))
	if count == 0:
		arcpy.AddError('\n PID {0} is not in OwnerIndex.\n\n Program terminated...\n\n'.format(PID))
	else:
		# df.zoomToSelectedFeatures()
		df.extent = lyr.getSelectedExtent()
		if df.scale < 4000.00:
				df.scale = 6000.00
		else:
			df.scale = df.scale * 1.5
		if clearSelection:
			arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

# Zoom to Lead Layer LeadId (LID)
def zoomToLID(arcpy, df, mxd, dLID, clearSelection=False):
	# Make Leads layer group visable
	lyrLeads = arcpy.mapping.ListLayers(mxd, "Leads", df)[0]
	lyrLeads.visible = True

	arcpy.AddMessage('\n dLID dictionary: {0}'.format(dLID))
	arcpy.AddMessage('   LID:           {0}'.format(dLID['LID']))
	arcpy.AddMessage('   marketAbb:     {0}'.format(dLID['marketAbb']))
	arcpy.AddMessage('   stateAbb:      {0}'.format(dLID['stateAbb']))
	arcpy.AddMessage('   leadLayerName: {0}'.format(dLID['leadLayerName']))
	arcpy.AddMessage('   county:        {0}'.format(dLID['county']))
	arcpy.AddMessage('   market:        {0}'.format(dLID['market']))
	arcpy.AddMessage('   county:        {0}'.format(dLID['county']))
	
	lyr = arcpy.mapping.ListLayers(mxd, dLID['leadLayerName'], df)[0]
	whereclause = "leadid in ('{0}')".format(dLID['LID'])
	arcpy.AddMessage('\n   whereclause:   {0}\n'.format(whereclause))
	arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
	count = int(arcpy.GetCount_management(lyr).getOutput(0))

	if count == 0:
		arcpy.AddError('\n Lead {0} does not exist.\n\n Program terminated...\n\n'.format(dLID['leadLayerName']))
	else:
		# df.zoomToSelectedFeatures()
		df.extent = lyr.getSelectedExtent()
		# arcpy.AddMessage(df.scale)
		if df.scale < 4000.00:
				df.scale = 6000.00
		else:
			df.scale = df.scale * 1.5
		if clearSelection:
			arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

# Zoom to APN
def zoomToAPN(arcpy, df, mxd, APN, parcelLayerName, clearSelection=False):
	arcpy.AddMessage(APN)
	arcpy.AddMessage(parcelLayerName)
	lyr = arcpy.mapping.ListLayers(mxd, parcelLayerName, df)[0]
	whereclause = "apn in ('{0}')".format(APN)
	arcpy.AddMessage(whereclause)
	try:
		arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
	except arcpy.ExecuteError:
		arcpy.AddMessage('\n APN: {0} does not exist in {1}'.format(APN, parcelLayerName))
	count = int(arcpy.GetCount_management(lyr).getOutput(0))
	# arcpy.AddMessage(' Count: {0}'.format(count))
	if count == 0:
		whereclause = "altapn in ('{0}')".format(APN)
		arcpy.AddMessage(whereclause)
		try:
			arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
			count = int(arcpy.GetCount_management(lyr).getOutput(0))
		except:
			arcpy.AddMessage('\n altAPN: {0} does not exist in {1}'.format(APN, parcelLayerName))
			count = 0
	if count == 0:
		# Remove hyphens and try APN again
		if '-' in APN:
			APNstrip = APN.replace('-', '')
			whereclause = "apn in ('{0}')".format(APNstrip)
			arcpy.AddMessage('\n Removing hyphens from APN {0}\n and trying to locate...')
			try:
				arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
				count = int(arcpy.GetCount_management(lyr).getOutput(0))
			except:
				arcpy.AddMessage("\n Removing hyphens didn't work...")
				count = 0
	if count == 0:
		# arcpy.AddMessage("\n Could not find APN to zoom to...\n")
		arcpy.AddError("\n Could not find APN to zoom to...\n")
		return False
	arcpy.AddMessage("\n Zooming to APN...\n")
	# df.zoomToSelectedFeatures()
	df.extent = lyr.getSelectedExtent()
	if df.scale < 4000.00:
			df.scale = 6000.00
	else:
		df.scale = df.scale * 1.5
	if clearSelection:
		arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
	return True

def zoomToLonLat(arcpy, df, mxd, lon, lat):
	from os import path
	from lao import sleep
	arcpy.AddMessage("\n Zooming to Lon/Lat {0}  {1} \n".format(lon, lat))
	# create point from lon/lats and make dynamic feature class
	# assign projection to variable
	sr = arcpy.SpatialReference("WGS 1984")

	inFeaturesPoints = arcpy.PointGeometry(arcpy.Point(lon, lat), sr)
	# arcpy.AddMessage('{0} : {1}'.format(lon, lat))

	# assing new shapefile name to variable
	in_shp = "C:/Users/Public/Public Mapfiles/fc_temp_point_zoom.shp"
	if path.exists('C:/Users/Public/Public Mapfiles//fc_temp_point_zoom.shp') is True:
		arcpy.Delete_management(in_shp)
	arcpy.CopyFeatures_management(inFeaturesPoints, in_shp)

	templyr = arcpy.mapping.Layer(in_shp)
	arcpy.mapping.AddLayer(df, templyr)
	lyr = arcpy.mapping.ListLayers(mxd, 'fc_temp_point_zoom', df)[0]
	whereclause = '"FID" = 0'
	arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
	# exit()
	sleep(2)
	df.zoomToSelectedFeatures()
	df.scale = 4000.00
	arcpy.mapping.RemoveLayer(df, lyr)
	arcpy.RefreshActiveView()
	# arcpy.Delete_management(in_shp)

def getMarketAbbreviation(market, county='None'):
	from lao import getCounties
	
	# Temp fix
	if market == 'Georgia':
		return 'Altanta', 'GA'
	elif market == 'Knoxville':
		return 'Nashville', 'TN'


	dCounties = getCounties('FullDict')
	marketAbb = 'None'
	county = county.replace(' ', '').replace('.', '')

	for row in dCounties:
		if county != 'None':
			if market.upper() == dCounties[row]['Market'].upper():
				print(market)
				print(county)
				print(dCounties[row]['County'])
				print
				if county.upper() == dCounties[row]['County'].upper() or county.upper() == dCounties[row]['ArcName'].upper():
					marketAbb = dCounties[row]['MarketAbb']
					stateAbb = dCounties[row]['State']
					break
		else:
			if market.upper() == dCounties[row]['Market'].upper():
				marketAbb = dCounties[row]['MarketAbb']
				stateAbb = dCounties[row]['State']
				break
	# Error check
	if marketAbb == 'None':
		td.warningMsg('\n Could not determine marketAbb...')
		print('\n Market: {0}'.format(market))
		print(' County: {0}'.format(county))
		td.warningMsg('\n Terminating program...')
		lao.holdup()
		exit()

	return marketAbb, stateAbb

# Get LID Dictionary
def getLIDDict(LID):
	from lao import getCounties

	leadCounty = LID.split('_')
	# Remove State
	if len(leadCounty[0]) == 2:
		stateAbb = leadCounty[0]
		del leadCounty[0]
	dCounties = getCounties('FullDict')
	
	for row in dCounties:
		if leadCounty[0] == dCounties[row]['ArcName'] and stateAbb == dCounties[row]['State']:
			selectedCounty = dCounties[row]
			# if dCounties[row]['LeadDate'] == 'NA':
			# 	selectedCounty = dCounties[row]
			# 	break
			# elif leadCounty[2] in dCounties[row]['LeadDate']:
			# 	selectedCounty = dCounties[row]
			# 	break

	d = {'LID': LID}
	d['county'] = selectedCounty['ArcName']
	d['marketAbb'] = selectedCounty['MarketAbb']
	d['stateAbb'] = selectedCounty['State']
	d['market'] = selectedCounty['Market']
	d['leadLayerName'] = selectedCounty['ParcelsName'].replace('Parcels', 'Leads')

	return d

# Get marketAbb, stateAbb and market from LAO Lead Layer by Lead ID
def getLIDMarket(LID):
	from lao import getCounties

	leadCounty = LID.split('_')
	county = leadCounty[0]
	dCounties = getCounties('FullDict')
	for row in dCounties:
		if county == dCounties[row]['ArcName']:
			marketAbb = dCounties[row]['MarketAbb']
			stateAbb = dCounties[row]['State']
			market = dCounties[row]['Market']
			break
	return marketAbb, stateAbb, market, county

# Remove Lead, Parcel & Road layers and load same from selected Market
def loadMarketMasterMXDMarket(market='None', mxd=False, polyType='None', polyID='None', Lon='None', Lat='None', parcelLayerName='None', arcpy='None'):
	if arcpy == 'None':
		print('\n Loading arcpy in amp.loadMarketMasterMXDMarket...')
		import arcpy
	from bb import getLeadDealData
	import fun_login
	from lao import getCounties

	# Set Variables
	lyrPath = 'F:/Research Department/maps/Layers/'
	foundAPN = True

	# User "CURRENT" mxd if one is not provided in argument
	if mxd is False:
		mxd = arcpy.mapping.MapDocument("CURRENT")
		clearSelection = False
	else:
		clearSelection = True

	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	mxdMarket = arcpy.mapping.ListLayers(mxd, "", df)[0].name
	targetGroupLayer = arcpy.mapping.ListLayers(mxd, 'ID', df)[0]

	# Clear OwnerIndex of selected PIDs/polygons
	OwnerIndexLayer = arcpy.mapping.ListLayers(mxd, "OwnerIndex", df)[0]
	arcpy.SelectLayerByAttribute_management(OwnerIndexLayer, "CLEAR_SELECTION")

	# If PID provided get the PID's market
	if polyType == 'PID':
		PID = polyID.strip()
		service = fun_login.TerraForce()
		market = getLeadDealData(service, PID, dealVar='Market')
		# No PID Exists error trap
		if market == 'No PID Exists':
			return 'No PID Exists'
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Get Market
	elif polyType == 'MARKET':
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Get LID Dictionary
	elif polyType == 'LID':
		LID = polyID.strip()
		dLID = getLIDDict(LID)
		market = dLID['market']
		county = dLID['county']
		marketAbb, stateAbb = getMarketAbbreviation(market, county)
	
	# Get APN Dictionary
	elif polyType == 'APN':
		APN = polyID.strip()
		APN = APN.replace('_split', '')
		if market == 'None' or market == None:
			market, ArcName = getMarketMasterMXDMarketFromLonLat(float(Lon), float(Lat), arcpy=arcpy)
		marketAbb, stateAbb = getMarketAbbreviation(market)
		if parcelLayerName == 'None' or not 'Parcels' in parcelLayerName:
			parcelLayerName = '{0}Parcels{1}'.format(stateAbb, ArcName)

	if polyType == 'LonLat':
		market, ArcName = getMarketMasterMXDMarketFromLonLat(float(Lon), float(Lat), arcpy=arcpy)
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Check if market is currently loaded
	if market == mxdMarket:
		loadNewMarket = False
	else:
		loadNewMarket = True
	
	# Remove Market Master TOC market label, Leads, Parcels & Roads
	if loadNewMarket:
		lMarkets = getCounties('Market')
		# Remove Market Label
		for mkt in lMarkets:
			try:
				removeLyr = arcpy.mapping.ListLayers(mxd, mkt, df)[0]
				arcpy.mapping.RemoveLayer(df, removeLyr)
				break
			except IndexError:
				continue
		
		# Remove Roads
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Roads', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
			arcpy.AddError('Roads failed to remove')
			pass
		# Remove Parcels
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Parcels', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
			pass
		# Remove Leads
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Leads', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
				pass
	
		# Add Parcels
		# arcpy.AddMessage(marketAbb)
		addLayer = arcpy.mapping.Layer('{0}{1}_Parcels.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
		# Add Leads. If clearSelection is not true the it is the OPR that is loading so don't load Leads layer.
		if clearSelection is not True:
			addLayer = arcpy.mapping.Layer('{0}{1}_Leads.lyr'.format(lyrPath, marketAbb))
			arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
		# Add Roads
		# if stateAbb == 'AL' or stateAbb == 'KY':
		# 	stateAbb = 'TN'
		# addLayer = arcpy.mapping.Layer('{0}{1}_Roads.lyr'.format(lyrPath, stateAbb))
		addLayer = arcpy.mapping.Layer('{0}{1}_Roads.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayer(df, addLayer, "TOP")
		# Add TOC Market Label
		addLayer = arcpy.mapping.Layer('{0}{1}_TOC_Label.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayer(df, addLayer, "TOP")
		# Zoom to LID if nessasary
		if polyType == 'LID':
			zoomToLID(arcpy, df, mxd, dLID, clearSelection=clearSelection)
	
	# Zoom to Market, PID or LID
	# First always zoom to the market defualt veiw
	zoomToLAOMarketBookmark(arcpy, df, mxd, market)
	# if polyType == 'MARKET':
	# 	zoomToLAOMarketBookmark(arcpy, df, mxd, market)
	if polyType == 'PID':
		zoomToPID(arcpy, df, mxd, PID, clearSelection=clearSelection)
	elif polyType == 'LID':
		zoomToLID(arcpy, df, mxd, dLID, clearSelection=False)
	elif polyType == 'APN':
		foundAPN = zoomToAPN(arcpy, df, mxd, APN, parcelLayerName, clearSelection=False)
		if foundAPN is False:
			if Lon == 'None':
				arcpy.AddError('\n Cannot find APN.')
			elif Lon != None:
				zoomToLonLat(arcpy, df, mxd, float(Lon), float(Lat))
	elif polyType == 'LonLat':
		zoomToLonLat(arcpy, df, mxd, float(Lon), float(Lat))

	arcpy.RefreshActiveView()
	del mxd

# Make an OPR jpg map from of a PID
def createOPRMap(PID, mxdPath='None'):
	print(' Loading arcpy amp.createOPRMap...')
	import arcpy
	from webs import awsUpload

	mxdOPRMapMaker = 'F:/Research Department/maps/mxd/AWS OPR Map Maker v01.mxd'
	# if mxdPath == 'None':
	# 	mxdOPRMapMaker = 'F:/Research Department/maps/mxd/Research OPR Map Maker v01.mxd'
	# else:
	# 	mxdOPRMapMaker = 'F:/Research Department/maps/mxd/AWS OPR Map Maker v01.mxd'
	oiHighlightPath = "C:/TEMP/OPRPropertyPolygon.shp"
	lyrHighlight = 'F:/Research Department/maps/Layers/OwnerIndexHighlight.lyr'
	mxd = arcpy.mapping.MapDocument(mxdOPRMapMaker)
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

	# Remove Parcels Layer
	removeLyr = arcpy.mapping.ListLayers(mxd, 'Parcels', df)[0]
	arcpy.mapping.RemoveLayer(df, removeLyr)

	# Turn off OwernIndex and Projects layers
	turnoffLyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	turnoffLyr.visible = False
	turnoffLyr = arcpy.mapping.ListLayers(mxd, 'Projects', df)[0]
	turnoffLyr.visible = False

	while 1:
		print('\n Making OPR map...')
		loadMarketMasterMXDMarket(market='None', mxd=mxd, polyType='PID', polyID=PID, Lon='None', Lat='None')

		# Select PID from OwnerIndex FeatureLayer
		if arcpy.Exists(oiHighlightPath):
				arcpy.Delete_management(oiHighlightPath)

		oi_lyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
		arcpy.SelectLayerByAttribute_management(oi_lyr, "CLEAR_SELECTION")
		wc = "pid in ('{0}')".format(PID)
		arcpy.SelectLayerByAttribute_management(oi_lyr, "NEW_SELECTION", wc)


		print('\n OwnerIndex selected: {0}\n'.format(PID))
		# Zoom to scale of Highlight PID and surrounding area
		df.extent = oi_lyr.getSelectedExtent()
		df.extent = oi_lyr.getSelectedExtent()
		if df.scale < 5000:
			df.scale = 10000
		else:
			df.scale = df.scale * 1.5
		arcpy.RefreshActiveView()

		# Check if one PID is selected
		results = arcpy.GetCount_management(oi_lyr)
		count = int(results.getOutput(0))
		print(' {0} PIDs selected'.format(count))
		if count == 0:
			lao.consoleColor('RED')
			td.warningMsg('\n No PID selected!\n\n Make sure {0} is saved in the OwnerIndex layer.'.format(PID))
			td.uInput('\n Continue > ')
			return True
		elif count > 2:
			td.warningMsg('\n There are {0} OwnerIndex polygons with the PID {1}!\n\n Fix OwnerIndex so only one polygon is PID {1}.'.format(count, PID))
			lao.holdup()
		else:
			break
	
	# Copy selected PID to temp Highlight 
	print(' Copying shapefile to local drive...this takes a minute...')
	arcpy.CopyFeatures_management(oi_lyr, oiHighlightPath)
	# Clear selection of OwnerIndex
	arcpy.SelectLayerByAttribute_management(oi_lyr, "CLEAR_SELECTION")
	# Add PID Highlight as layer to mxd
	print(' Highlighting PID')
	highlight = arcpy.mapping.Layer(oiHighlightPath)
	# highlight = arcpy.mapping.Layer(memHighlight)
	arcpy.mapping.AddLayer(df, highlight)
	# Make the Highlighted PID layer Blue
	lyrNewHighlight = arcpy.mapping.ListLayers(mxd, "OPRPropertyPolygon", df)[0]
	lyrHighlightSymbology = arcpy.mapping.Layer(lyrHighlight)
	arcpy.mapping.UpdateLayer(df, lyrNewHighlight, lyrHighlightSymbology)
	print(' PID highlighted...')
	
	print(' Exporting {0} as jpeg map...'.format(PID))
	jpgFileName = 'F:/Research Department/scripts/awsUpload/Maps/{0}.jpg'.format(PID)	
	arcpy.mapping.ExportToJPEG(mxd, jpgFileName)

	# Export map as jpeg and copy to FTP then delete (remove) the jpeg map
	print(' Copying {0} to AWS...'.format(PID))
	awsUpload(True)
	arcpy.Delete_management(oiHighlightPath)
	del mxd
	print(' OPR map created...')
	return

# Check if OwnerIndex PID exists
def isOwnerIndexPIDExist(PID, arcpy=None, checkingOPR=False):

	from lao import warningMsg, uInput
	if arcpy == None:
		print('\n Loading arcpy in amp.isOwnerIndexPIDExist...')
		import arcpy
	oprMessage = True
	mxdOPRMapMaker = 'F:/Research Department/maps/mxd/Research OwnerIndex Only v01.mxd'
	mxd = arcpy.mapping.MapDocument(mxdOPRMapMaker)
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	oi_lyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	wc = "pid in ('{0}')".format(PID)
	# arcpy.SelectLayerByAttribute_management(oi_lyr, "CLEAR_SELECTION")
	arcpy.SelectLayerByAttribute_management(oi_lyr, "NEW_SELECTION", wc)
	results = arcpy.GetCount_management(oi_lyr)
	count = int(results.getOutput(0))
	if count == 0:
		if checkingOPR:
			oprMessage = 'Missing map JPEG. No OwnerIndex polygon with PID {0}<br>'.format(PID)
		else:
			warningMsg('\n No PID selected!\n\n Make sure {0} is saved in the OwnerIndex layer.'.format(PID))
			uInput('\n Continue > ')
	elif count > 1:
		if checkingOPR:
			oprMessage = 'Missing map JPEG. There are {0} OwnerIndex polygons with PID {1}<br>'.format(count, PID)
		else:
			warningMsg('\nThere are {0} OwnerIndex polygons with the PID {1}!\n\n Fix OwnerIndex so only one polygon is PID {1}.'.format(count, PID))
			uInput('\n Continue > ')
	del mxd
	if checkingOPR:
		return oprMessage

# Create a Lead from a Closed Deal 108 to 103
def makeLeadForClosedDeal108To103(service, salePID, leadPID):
	import aws
	print('\n ------------------------------------------------------------------')
	print('\n Sale PID: {0}'.format(salePID))
	print(' Lead PID: {0}'.format(leadPID))
	print('\n Creating new polygon for Lead...')

	# Check if Stage Name is Closed
	if not 'Closed' in bb.getStageName(service, salePID):
		arcpy.AddError('\n Not a Closed Sale...Lead {0} not created...continue...'.format(leadPID))
		exit()

	aws.make_AWS_OwnerIndex_Poly_from_OwnerIndex_Poly(PID=salePID, PIDnew=leadPID, runASW=True)
	return

# Return dict of OwnerIndex, Ownership or SaleMap fields or all 3
def getOIFieldDicts(layername='None'):
	dOIFields = {
		'pid': ['TEXT', 50],
		'initials': ['TEXT', 10],
		'dateupdated': ['DATE'],
		'lon': ['DOUBLE'],
		'lat': ['DOUBLE'],
		'state': ['TEXT', 5],
		'county': ['TEXT', 50],
		'id': ['LONG'],
		}
	if layername.upper() == 'OWNERINDEX':
		return dOIFields
	
	dOwnFields = {
		'propertyid': ['TEXT', 50],
		'acres': ['DOUBLE'],
		'owner': ['TEXT', 255],
		'ownerentity': ['TEXT', 255],
		'mobile' : ['TEXT', 255],
		'phone' : ['TEXT', 255],
		'entityphone' : ['TEXT', 255],
		'email' : ['TEXT', 255],
		'entitywebsite' : ['TEXT', 255],
		'fax' : ['TEXT', 255],
		'entityaddress' : ['TEXT', 255],
		'location' : ['TEXT', 255],
		'lots' : ['LONG', 255],
		'lot_description' : ['TEXT', 1073741822],
		'classification' : ['TEXT', 255],
		'general_plan' : ['TEXT', 255],
		'zoning' : ['TEXT', 255],
		'notes' : ['TEXT', 1073741822],
		'billingaddress' : ['TEXT', 255],
		'shippingaddress' : ['TEXT', 255],
		'otheraddress' : ['TEXT', 255],
		'ownerid' : ['TEXT', 25],
		'ownerentid' : ['TEXT', 25],
		'sfid' : ['TEXT', 25],
		'dealname' : ['TEXT', 100],
		'recordtype' : ['TEXT', 25],
		'keyword' : ['TEXT', 100],
		'stage' : ['TEXT', 25],
		'accttop100url' : ['TEXT', 255],
		'accttop100phrase' : ['TEXT', 25],
		'accttop100list' : ['TEXT', 255],
		'lot_type' : ['TEXT', 50],
		'agents' : ['TEXT', 255],
		'DAREmailString' : ['TEXT', 255]
		}
	if layername.upper() == 'OWNERSHIPS':
		return dOwnFields

	dSMapFields = {
		'propertyid': ['TEXT', 50],
		'dealname' : ['TEXT', 255],
		'acres': ['DOUBLE'],
		'seller' : ['TEXT', 255],
		'sellerphone' : ['TEXT', 255],
		'selleremail' : ['TEXT', 255],
		'sellermobile' : ['TEXT', 255],
		'sellerhomephone' : ['TEXT', 255],
		'sellerentity' : ['TEXT', 255],
		'sellerentityphone' : ['TEXT', 255],
		'buyer' : ['TEXT', 255],
		'buyerentity' : ['TEXT', 255],
		'buyerentityphone' : ['TEXT', 255],
		'buyerentitywebsite' : ['TEXT', 255],
		'buyercontactphone' : ['TEXT', 255],
		'buyercontactmobile' : ['TEXT', 255],
		'buyercontacthomephone' : ['TEXT', 255],
		'buyercontactemail' : ['TEXT', 255],
		'classification' : ['TEXT', 255],
		'submarket' : ['TEXT', 50],
		'subdivision' : ['TEXT', 100],
		'lotcount' : ['LONG'],
		'lots' : ['LONG'],
		'lottype' : ['TEXT', 50],
		'lotdetails' : ['TEXT', 1073741822],
		'saledate' : ['DATE'],
		'saleprice' : ['DOUBLE'],
		'priceperac' : ['DOUBLE'],
		'priceperlot' : ['DOUBLE'],
		'priceperft' : ['DOUBLE'],
		'comments' : ['TEXT', 1073741822],
		'location' : ['TEXT', 255],
		'city' : ['TEXT', 255],
		'keyword' : ['TEXT', 255],
		'type' : ['TEXT', 255],
		'recordtype' : ['TEXT', 100],
		'redid' : ['TEXT', 255],
		'stage' : ['TEXT', 255],
		'saleyear' : ['SHORT'],
		'dealid' : ['TEXT', 50],
		'sellerid' : ['TEXT', 50],
		'sellerentid' : ['TEXT', 50],
		'buyerid' : ['TEXT', 50],
		'buyerentid' : ['TEXT', 50],
		'priceperff' : ['DOUBLE']
		}
	if layername.upper() == 'SALEMAP':
		return dSMapFields
	
	return dOIFields, dOwnFields, dSMapFields

# Delete existing FeatureClass fields except for ArcMap default fields
def deleteFeatureClassFields(fc, layername='Unknown'):
	from arcpy import AddMessage, DeleteField_management
	# Delete Parcel Fields
	arcpy.AddMessage('\n Deleting fields from new polygon for {0}...'.format(layername))
	lArcFieldName = ['OBJECTID', 'OBJECTID_1', 'shape', 'shape_Length', 'shape_Area', 'FID', 'Shape']
	for f in arcpy.ListFields(fc):
		if not f.name in lArcFieldName:
			arcpy.DeleteField_management(fc, f.name)
	arcpy.AddMessage(' Fields deleted...')

# Add fields for layername (OwnerIndex, Ownerships or SaleMap)
def addFeatureClassFields(fc, layername):
	from arcpy import AddMessage, AddField_management
	# Delete existing fields except for ArcMap default fields
	deleteFeatureClassFields(fc, layername)
	dFields = getOIFieldDicts(layername)
	# Add the fileds to the layer
	arcpy.AddMessage('\n Adding fields to new polygon for {0}...'.format(layername))
	for fld in dFields:
		fieldname = dFields[fld][0] 
		if fieldname == 'TEXT':
			fieldlength = dFields[fld][1]
			arcpy.AddField_management(fc, fld, fieldname, fieldlength)
		else:
			arcpy.AddField_management(fc, fld, fieldname)
	arcpy.AddMessage(' Fields added...')

# Add attributes to OwnerIndex, Ownerships or SaleMap FeatureClass
def addFeatureClassAttributes(fc, layername, PID):
	import time
	arcpy.AddMessage(' Adding attributes to new polygon for {0}...'.format(layername))
	user, initials = lao.getUserName(initials=True)
	today_date = (time.strftime('%m/%d/%Y'))
	if layername.upper() == 'OWNERINDEX':
		cur = arcpy.UpdateCursor(fc)
		for row in cur:
			row.pid = PID
			row.initials = initials
			row.dateupdated = today_date
			cur.updateRow(row)
	elif layername.upper() == 'OWNERSHIPS':
		cur = arcpy.UpdateCursor(fc)
		for row in cur:
			row.propertyid = PID
			cur.updateRow(row)
	elif layername.upper() == 'SALEMAP':
		cur = arcpy.UpdateCursor(fc)
		for row in cur:
			row.propertyid = PID
			cur.updateRow(row)
	arcpy.AddMessage(' Attributes added...')

def appendFeatureClass108To103(fc_source, fc_desination):
	from arcpy import AddMessage, Append_management
	try:
		AddMessage('\n Appending...')
		Append_management(fc_source, fc_desination, "TEST")
	except arcpy.ExecuteError:
		AddMessage('\n First write attempt failed... trying again...')
		Append_management(fc_source, fc_desination, "TEST")
	AddMessage(' Write completed successfuly...\n')

# Get the layer name from the Lead ID (LID)
def getLeadLayerName(LID):
	# Remove State if it exitsts
	lCounties = LID.split('_')
	if len(lCounties[0]) == 2:
		stateAbb = lCounties[0]
		del lCounties[0]
	# underscorelocation = LID.find('_', 1)
	# county = LID[:underscorelocation]
	county = lCounties[0]
	dCounties = lao.getCounties('FullDict')
	for i in dCounties:
		if county == dCounties[i]['ArcName'] and stateAbb == dCounties[i]['State']:
			leadlayer = dCounties[i]['ParcelsName']
			leadlayer = leadlayer.replace('Parcels', 'Leads')
			state = dCounties[i]['StateFull']
	return leadlayer, state, county

# Get dict of Lead and dAcc values
def getLeadDictionary(LID, dAcc='None'):
	print(' Loading arcpy amp.getLeadDictionary...')
	import arcpy
	import amp
	import acc
	from pprint import pprint
	print(LID)
	dLead = {'ACRES':'None',
		'COUNTY':'None',
		'LAT':'None',
		'LEADLAYER': 'None',
		'LEADPARCEL': 'None',
		'LID': LID,
		'LON':'None',
		'MAILADDRESS':'None',
		'MAILCITY':'None',
		'MAILSTATE':'None',
		'MAILZIP':'None',
		'OWNER':'None',
		'PARCELS':'None',
		'STATE':'None'}
	
	# Get the leadlayer, state and county
	dLead['LEADLAYER'], dLead['STATE'], dLead['COUNTY'] = amp.getLeadLayerName(LID)
	print(dLead['LEADLAYER'], dLead['STATE'], dLead['COUNTY'] )
	fc_Leads = 'C:/Users/Public/Public Mapfiles/LAO.gdb/{0}'.format(dLead['LEADLAYER'])

	# Clear cache
	arcpy.ClearWorkspaceCache_management()

	# Delete existing leads_layer and make fresh one
	if arcpy.Exists("leads_lyr"):
		arcpy.Delete_management("leads_lyr")
	arcpy.MakeFeatureLayer_management(fc_Leads, "leads_lyr")

	# Select the Lead from the leads_lyr fc
	wc = "leadId in ('" + LID + "')"
	arcpy.SelectLayerByAttribute_management("leads_lyr", "NEW_SELECTION", wc)

	# Set the cursor
	cur = arcpy.SearchCursor("leads_lyr")

	# Populate the dLead dict
	for row in cur:
		dLead['ACRES'] = '{:.2f}'.format(round(row.getValue('Acres'), 2))
		dLead['LAT'] = row.getValue('y')
		dLead['LON'] = row.getValue('x')
		try:
			dLead['MAILSTREET'] = row.getValue('mailstreet')
		except:
			dLead['MAILSTREET'] = row.getValue('mailaddress')
		dLead['MAILCITY'] = row.getValue('MailCity')
		dLead['MAILSTATE'] = row.getValue('MailState')
		dLead['MAILZIP'] = row.getValue('MailZip')[:5]
		dLead['OWNER'] = row.getValue('Owner')
		dLead['PARCELS'] = row.getValue('parcels')
		dLead['PARCELS'] = dLead['PARCELS'].replace(' ', '')
		dLead['LEADPARCEL'] = dLead['PARCELS'].split(',')[0]

	# Populate dAcc if exists
	if dAcc != 'None':
		dAcc['ENTITY'] = dLead['OWNER']
		dAcc['STREET'] = dLead['MAILSTREET']
		dAcc['CITY'] = dLead['MAILCITY']
		dAcc['STATE'] = dLead['MAILSTATE']
		dAcc['ZIPCODE'] = dLead['MAILZIP']
		dAcc = td.address_formatter(dAcc)
		return dLead, dAcc
	else:
		return dLead

# Get OID from DID or PID
def get_OID_From_PIDDID(piddid):
	# if arcpy == 'None':
	print(' Loading arcpy amp.get_OID_From_PIDDID...')
	import arcpy
	fMXD = 'F:/Research Department/maps/mxd/Ownerships Only.mxd'
	mxd = arcpy.mapping.MapDocument(fMXD)
	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	pid_or_did = bb.isDIDorPID(piddid)
	if pid_or_did == 'DID':
		PID = bb.getPIDfromDID(piddid)
	else:
		PID = piddid
	oi_lyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
	whereclause = "pid in ('{0}')".format(PID)
	arcpy.SelectLayerByAttribute_management(oi_lyr, "NEW_SELECTION", whereclause)
	pid_fields = ['objectid']
	for row in arcpy.da.SearchCursor(oi_lyr, pid_fields):
		OID = row[0]
	del mxd
	return OID

# OLD FUNCTIONS -----------------------------------------------------------------------------
def lookupMaricopaParcels(dd): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def lookupMaricopaParcels() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()
def lookupPinalParcels(dd): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def lookupPinalParcels() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()
def lookupIdahoParcels(dd): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def lookupIdahoParcels() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()
def lookupPhoneNumbers(dd): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def lookupPhoneNumbers() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()
def getCounty(PID): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def getCounty() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def getSelectPIDFromLonLat(service, x, y): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def getSelectPIDFromLonLat() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def makeTFAccountFromAPN(service, APN = 'None'): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def makeTFAccountFromAPN() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

# Make OPR Maps set TOC
def OPRmaps(): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
		td.warningMsg('amp.def OPRmaps() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
		exit()

def ZoomToPoly(): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def ZoomToPoly() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def getSelectPIDorParcelFromLonLat(service, x, y): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def getSelectPIDorParcelFromLonLat() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def getParcelsInPID(PID, dd, county_name): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def getParcelsInPID() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def deletePIDpoylgon(PID, isLotOption=False): # CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED
	td.warningMsg('amp.def getParcelsInPID() CHECK SCRIPTS/PROJECTS/LIBRARY BACKUP FOLDER IF NEEDED')
	exit()

def get_LAO_geoinfo(lon, lat):
	# Load the shapefile
	print('\n Loading shp file...')
	shapefile_path = 'F:/Research Department/LAO_Geo_1.shp'
	gdf = gpd.read_file(shapefile_path)

	# Create a Point object based on the given coordinates
	point = Point(lon, lat)

	# Check which geometry in the GeoDataFrame contains the point
	print(' Finding county...')
	containing_county = gdf[gdf.contains(point)]

	if containing_county.empty:
		return "The given coordinates do not fall within any county in the shapefile."

	# Assuming the shapefile has 'NAME' for county name and 'STATE_NAME' for state name
	dLAO_geoinfo = {}
	dLAO_geoinfo['state_abb'] = containing_county.iloc[0]['state']
	# dLAO_geoinfo['state_full'] = containing_county.iloc[0]['statefull']
	dLAO_geoinfo['county_name'] = containing_county.iloc[0]['county']
	dLAO_geoinfo['market_full'] = containing_county.iloc[0]['market']
	dLAO_geoinfo['market_abb'] = containing_county.iloc[0]['marketabb']
	dLAO_geoinfo['arcname'] = containing_county.iloc[0]['arcname']

	return dLAO_geoinfo