# Non-ESRI map functions


from datetime import datetime
import aws
import bb
from collections import Counter
import dicts
import fjson
import fun_login
import geopandas as gpd
from json import dump
import lao
import math
import os
import pandas as pd
from pprint import pprint
import requests
from shapely.geometry import Point
import fun_text_date as td
import time

def get_arcgis_token():
	"""Get authentication token for LAO ArcGIS REST API."""

	print('\n Getting ArcGIS token...')

	from dotenv import load_dotenv
	# Load environment variables from a .env file
	load_dotenv()

	# Get the value of an environment variable
	username = os.getenv('ARCGIS_USERNAME')
	password = os.getenv('ARCGIS_PASSWORD')

	url = "https://maps.landadvisors.com/portal/sharing/rest/generateToken"
	data = {
		"username": username,
		"password": password,
		"client": "referer",
		"referer": "https://maps.landadvisors.com",
		"f": "json"
	}
	response = requests.post(url, data=data)
	result = response.json()
	token = result.get("token")
	expires = result.get("expires")  # milliseconds since epoch
	# print(f' Token expires: {datetime.fromtimestamp(expires/1000)}')
	print(' Token acquired.\n')
	return token

def get_lead_layer_id(token, leadid):
	"""Extract state and county from leadid and look up the Lead layer ID from the API."""
	parts = leadid.split("_")
	state = parts[0].upper()
	county = parts[1].upper()
	lead_layer_name = f"{state}LEADS{county}"
	parcel_layer_name = f"{state}PARCELS{county}"
	
	# Query the FeatureServer to get all layers
	# url = "https://maps.landadvisors.com/arcgis/rest/services/Research_leads/FeatureServer"
	url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Leads/MapServer"
	params = {
		"f": "json",
		"token": token
	}
	response = requests.get(url, params=params)
	data = response.json()
	
	# Find the layer with matching name
	for layer in data.get("layers", []):
		if layer["name"].upper() == lead_layer_name:
			lead_layer_id = layer["id"]
	
	# Query the FeatureServer to get all layers
	url = "https://maps.landadvisors.com/arcgis/rest/services/Research_parcels/FeatureServer"
	params = {
		"f": "json",
		"token": token
	}
	response = requests.get(url, params=params)
	data = response.json()
	
	# Find the layer with matching name
	for layer in data.get("layers", []):
		if layer["name"].upper() == parcel_layer_name:
			parcel_layer_id = layer["id"]
	
	return lead_layer_id, parcel_layer_id

# Get Lead attributes by leadid from ArcGIS REST API
def get_lead_by_id(token, leadid, layer_id):
	lao.print_function_name(' mpy def get_lead_by_id')

	# base_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_leads/FeatureServer"
	base_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Leads/MapServer"
	url = f"{base_url}/{layer_id}/query"
	params = {
		"where": f"leadid='{leadid}'",
		"outFields": "*",
		"returnGeometry": "false",
		"f": "json",
		"token": token
	}
	# pprint(params)
	# print(url)
	response = requests.get(url, params=params)
	data = response.json()
	# Print data for debugging
	# print(f"\n Lead data for LeadID {leadid}:")
	# pprint(data)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	if data.get("features"):
		return data["features"][0]["attributes"]
	return None

def get_parcel_propertyids(token, parcels_str, parcel_layer_id):
	lao.print_function_name(' mpy def get_parcel_propertyids')
	"""Get propertyids for parcels from the Parcels layer.
	
	Args:
		token: ArcGIS auth token
		parcels_str: Comma-separated string of APNs from Lead's 'parcels' field
		parcel_layer_id: Layer ID for the appropriate county parcels layer
	
	Returns:
		List of propertyid values
	"""
	# Parse comma-separated APNs and clean whitespace
	apns = [apn.strip() for apn in parcels_str.split(",")]
	
	# Build IN clause for query
	apn_list = ",".join([f"'{apn}'" for apn in apns])
	where_clause = f"apn IN ({apn_list})"
	
	parcel_fields = dicts.get_parcel_fields_list()
	print('\n Parcel Fields list')
	print(parcel_fields)
	print(f'\n Parcel_layer_id: {parcel_layer_id}')
	print('\n')

	base_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_parcels/FeatureServer"
	url = f"{base_url}/{parcel_layer_id}/query"
	params = {
		"where": where_clause,
		"outFields": parcel_fields,
		"returnGeometry": "false",
		"f": "json",
		"token": token
	}
	pprint(params)
	response = requests.get(url, params=params)
	data = response.json()

	# pprint(data)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	
	lPropertyids = []
	lOwners = []
	subdiv = 'None'
	usedesc = 'None'
	zoning = 'None'
	if data.get("features"):
		for feature in data["features"]:
			pid = feature["attributes"].get("propertyid")
			if pid:
				lPropertyids.append(pid)
			owner = feature["attributes"].get("owner", "").upper()
			lOwners.append(owner)
			if subdiv == 'None':
				subdiv = feature["attributes"].get("subdiv", subdiv)
			if usedesc == 'None':
				usedesc = feature["attributes"].get("usedesc", usedesc)
			if zoning == 'None':
				zoning = feature["attributes"].get("zoning", zoning)
	
	# Determine the most common owner
	if lOwners:
		most_common_owner = Counter(lOwners).most_common(1)[0][0]
	else:
		most_common_owner = 'None'
	
	return lPropertyids, subdiv, usedesc, zoning, most_common_owner

# Get dAcc and dTF from LeadId
def get_lead_info_dAcc_dTF_dicts(token, LeadId):
	lao.print_function_name(' mpy def get_lead_info_dAcc_dTF_dicts')

	start_time = time.time()

	# token = get_arcgis_token()

	lead_layer_id, parcel_layer_id = get_lead_layer_id(token, LeadId)
	print(f"\n Lead Layer ID: {lead_layer_id}")
	print(f" Parcel Layer ID: {parcel_layer_id}\n")

	dLeadInfo = get_lead_by_id(token, LeadId, lead_layer_id)
	# pprint(dLeadInfo)

	# Return empty dicts if no lead info found
	if not dLeadInfo:
		print('\n No Lead Info found...')
		return {}, {}, []	

	# Get propertyids from the parcels
	parcels_str = dLeadInfo.get("parcels")
	# print(f"\n Parcels: {parcels_str}")
	if parcels_str:
		print("\n Getting Parcel Property IDs...")
		lPropertyids, subdiv, usedesc, zoning, most_common_owner = get_parcel_propertyids(token, parcels_str, parcel_layer_id)
		# print(f"\n Property IDs: {lPropertyids}")

	# Create dAcc from dLeadInfo
	dAcc = dicts.get_blank_account_dict()
	dAcc['ENTITY'] = most_common_owner
	dAcc['STREET'] = dLeadInfo.get('mailstreet', '')
	dAcc['CITY'] = dLeadInfo.get('mailcity', '')
	dAcc['STATE'] = dLeadInfo.get('mailstate', '')
	dAcc['ZIP'] = dLeadInfo.get('mailzip', '')
	dAcc['ADDRESSFULL'] = f"{dAcc['STREET']}, {dAcc['CITY']}, {dAcc['STATE']} {dAcc['ZIP']}"
	dAcc['PHONE'] = dLeadInfo.get('phone', '')

	# Create dTF from dLeadInfo
	dTF = dicts.get_blank_tf_deal_dict()
	dTF['Acres__c'] = dLeadInfo.get('acres', '')
	dTF['Parcels__c'] = dLeadInfo.get('parcels', '')
	dTF['Lead_Parcel__c'] = dTF['Parcels__c'].split(',')[0]
	lstate_county = dLeadInfo.get('leadid', '').split('_')  # e.g., 'FL_Lake'
	dTF['State__c'] = lstate_county[0]
	dTF['County__c'] = lstate_county[1]
	dTF['Latitude__c'] = dLeadInfo.get('y', '')
	dTF['Longitude__c'] = dLeadInfo.get('x', '')
	dTF['Subdivision__c'] = subdiv
	dTF['Description__c'] = usedesc
	dTF['Zoning__c'] = zoning

	print(f"Completed in {time.time() - start_time:.2f} seconds.")
	
	return dAcc, dTF, lPropertyids

# Get list of Parcel PropertyIDs from list of APNs
def get_parcel_propertyid(lParcels, dTF=None):
	"""
	Given a list of parcel numbers, return a dictionary mapping each parcel number to its property ID.
	"""
	start_time = time.time()
	lParcel_PropertyID = []

	MarketAbb = dicts.get_counties('MarketAbb', ArcName=dTF['County__c'], State=dTF['State__c'])
	layer_name = f"{dTF['State__c']}Parcels{dTF['County__c']}"

	# Define cache path
	cache_dir = "F:/Research Department/maps/Parcels & Leads/GDF Caches"
	# cache_dir = "C:/TEMP"
	# os.makedirs(cache_dir, exist_ok=True)
	cache_path = f"{cache_dir}/{layer_name}.parquet"

	# Read from cache or source
	print(f'\n Getting parcel information from {layer_name}...')
	if os.path.exists(cache_path):
		# print(f" Reading from cache: {cache_path}...\n")
		gdf = pd.read_parquet(cache_path)
	else:
		print(f" Reading parcel layer: {layer_name}...\n")
		os.environ['OGR_ORGANIZE_POLYGONS'] = 'SKIP'
		gdb_path = f"C:/Users/Public/Public Mapfiles/Parcels/{MarketAbb}.gdb"
		gdf = gpd.read_file(gdb_path, layer=layer_name, ignore_geometry=True)
		
		# Save to cache for future runs
		# print(f" Saving cache: {cache_path}...\n")
		gdf.to_parquet(cache_path)

	# Filter for all APNs in the list
	print(f" Finding {len(lParcels)} parcels...\n")
	result = gdf[gdf['apn'].isin(lParcels)]

	# Map parcel numbers to property IDs
	zoning = 'None'
	subdivision = 'None'
	use_description = 'None'
	for _, row in result.iterrows():
		lParcel_PropertyID.append(row['propertyid'])
		# pprint(row)
		if dTF['Zoning__c'] == 'None' and  row['zoning'] != '':
			dTF['Zoning__c']  = row['zoning']
		if dTF['Subdivision__c'] == 'None' and  row['subdiv'] != '':
			dTF['Subdivision__c']  = row['subdiv'].title()
		if dTF['Description__c'] == 'None' and  row['usedesc'] != '':
			dTF['Description__c']  = row['usedesc']

	print(f"Completed in {time.time() - start_time:.2f} seconds.")
	if dTF:
		return lParcel_PropertyID, dTF
	else:
		return lParcel_PropertyID

def get_gpf_for_LAO_geoinfo(include_zip=True):
	lao.print_function_name(' mpy def get_gpf_for_LAO_geoinfo')

	# Load LAO Geo shapefile
	dGDF = {}
	shapefile_path = 'F:/Research Department/maps/LAO_Geo/LAO_Geo_1.shp'
	dGDF['LAO_geo'] = gpd.read_file(shapefile_path)

	# T/F search for zip codes in get_LAO_geoinfo
	dGDF['Zip'] = include_zip
	return dGDF

# Gets LAO Geo Info from lon/lat or dTF (State, County, Market, Submarket, City, Zipcode, Google Map link and L5 link)
def get_LAO_geoinfo(dTF='None', dGDF=False, lon=0, lat=0):
	# Get Lon/Lat from dTF if not None
	if dTF != 'None':
		lon = dTF['Longitude__c']
		lat = dTF['Latitude__c']
	else:
		# Build a blank dict for LAO Geo Info
		dLAO_geoinfo = {
				'arcname': 'None',
				'county_name': 'None',
				'market_full': 'None',
				'market_abb': 'None',
				'state_abb': 'None',
				'state_full': 'None',
				'submarket': 'None',
				'city': 'None',
				'zipcode': 'None',
				'google_map': 'None',
				'l5_map': 'None'}
		# Return blank dict if lon/lat is blank
		if lon == '' or lat == '':
			# td.warningMsg('\n Lon/Lat is blank...')
			return dLAO_geoinfo
	
	# Load LAO Geo shapefile
	if dGDF:  # dGDF provided
		gdf = dGDF['LAO_geo']
	else:     # dGDF not provided
		dGDF = get_gpf_for_LAO_geoinfo()
		gdf = dGDF['LAO_geo']

	# Create a Point object based on the given coordinates
	point = Point(lon, lat)

	# Check which geometry in the GeoDataFrame contains the point
	containing_county = gdf[gdf.contains(point)]

	# Check if the point is within a county
	if containing_county.empty:
		# td.warningMsg('\n The given coordinates do not fall within any county in the shapefile.')
		if dTF == 'None':
			dLAO_geoinfo['google_map'] = f'https://www.google.com/maps/@{lat},{lon},3000m/data=!3m1!1e3'
			dLAO_geoinfo['l5_map'] = 'None'
			return dLAO_geoinfo
		else:
			print(f' {lon}')
			print(f' {lat}')
			td.warningMsg('\n Lon/Lat is not within any LAO county in the shapefile...')
			td.warningMsg('\n Have Bill open F:/Research Department/maps/mxd/LAO_GEO_v01.mxd and check the coordinates.')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			return dTF
	
	# Assign values to the dictionary
	if dTF == 'None':
		# Assuming the shapefile has 'NAME' for county name and 'STATE_NAME' for state name
		dLAO_geoinfo['arcname'] = containing_county.iloc[0]['arcname']
		dLAO_geoinfo['county_name'] = containing_county.iloc[0]['county']
		dLAO_geoinfo['market_full'] = containing_county.iloc[0]['market']
		dLAO_geoinfo['market_abb'] = containing_county.iloc[0]['marketabb']
		dLAO_geoinfo['state_abb'] = containing_county.iloc[0]['state']
		dLAO_geoinfo['state_full'] = containing_county.iloc[0]['statefull']
		dLAO_geoinfo['submarket']  = containing_county.iloc[0]['submarket']
		dLAO_geoinfo['google_map'] = f'https://www.google.com/maps/@{lat},{lon},3000m/data=!3m1!1e3'
		# Create L5 link
		if dLAO_geoinfo['market_full'] == 'None' or dLAO_geoinfo['market_full'] == None:
			dLAO_geoinfo['l5_map'] = 'None'
		else:
			import webs
			dLAO_geoinfo['l5_map'] = webs.get_L5_url(LOT='CENTER', MARKET=dLAO_geoinfo['market_full'], PID=f'{lon},{lat}')

		stateabb = dLAO_geoinfo['state_abb']
		# return dLAO_geoinfo
	else:
		# Assuming the shapefile has 'NAME' for county name and 'STATE_NAME' for state name
		stateabb = containing_county.iloc[0]['state']
		dTF['State__c']  = containing_county.iloc[0]['statefull']
		dTF['County__c'] = containing_county.iloc[0]['arcname']
		dTF['Submarket__c']  = containing_county.iloc[0]['submarket']

	# if dGDF['Zip'] is true oad LAO ZipCode shapefile else return dLAO_geoinfo
	if dGDF['Zip']:
		shapefile_path = f'F:/Research Department/maps/LAO_Geo/LAO_Zip_{stateabb}.shp'
		gdf = gpd.read_file(shapefile_path)
	else:
		# Replace None values with 'None'
		for key in dLAO_geoinfo:
			if dLAO_geoinfo[key] == None:
				dLAO_geoinfo[key] = 'None'
		return dLAO_geoinfo
	
	# Check which geometry in the GeoDataFrame contains the point
	containing_county = gdf[gdf.contains(point)]

	# Check if the point is within a county
	if containing_county.empty:
		if dTF == 'None':
			dLAO_geoinfo['city'] = 'None'
			dLAO_geoinfo['zipcode'] = 'None'
			return dLAO_geoinfo
		else:
			return "The given coordinates do not fall within any county in the shapefile."
	
	# Get the city and zipcode
	if dTF == 'None':
		dLAO_geoinfo['city'] = containing_county.iloc[0]['PO_NAME']
		dLAO_geoinfo['zipcode'] = containing_county.iloc[0]['ZIP']
	else:
		dTF['City__c']  = containing_county.iloc[0]['PO_NAME']
		dTF['Zipcode__c'] = containing_county.iloc[0]['ZIP']

	# Return the dictionary	
	if dTF == 'None':
		# Replace None values with 'None'
		for key in dLAO_geoinfo:
			if dLAO_geoinfo[key] == None:
				dLAO_geoinfo[key] = 'None'
		return dLAO_geoinfo
	else:
		return dTF

# Returns intersection or address based on lon/lat
def get_intersection_from_lon_lat(dTF='None', lon=0, lat=0, askManually=True, findAddress=False):
	import requests
	from pprint import pprint

	lao.print_function_name('mpy def get_intersection_from_lon_lat')
	td.banner('Location Intersection')
	
	# ArcGIS API url
	url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?'

	# Set lontlat value
	if dTF != 'None':
		lonlat = '{0},{1}'.format(dTF['Longitude__c'], dTF['Latitude__c'])
	else:
		lonlat = '{0},{1}'.format(lon, lat)
	
	# Set params for address or intersection
	if findAddress:
		feature_types = 'StreetAddress'
	else:
		feature_types = 'StreetInt'
	# Request from api
	params = {'f': 'pjson', 'featureTypes': feature_types, 'location': lonlat}
	r = requests.get(url, params=params)

	if findAddress:
		try:
			location = r.json()['address']['Match_addr']
		except:
			location = 'None'
	else:
		try:
			location = r.json()['address']['Address']
		except:
			location = 'None'
	
	if dTF == 'None' and location != 'None':
		return location
	elif dTF != 'None' and location != 'None':
		dTF['Location__c'] = location
		return dTF

	if askManually:
		td.warningMsg('\n No intersection found...')
		ui = td.uInput('\n Manually enter intersection > ')
		if ui == '00':
			exit('\n Terminating program...')
		if ui == '':
			if isinstance(dTF, dict):
				dTF['Location__c'] = 'NF'
		else:
			dTF['Location__c'] = ui

	return dTF

# Get lon/lat from address or intersection
def get_lon_lat_from_address_or_intersection(address):
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

# Given a lon/lat return the bounding box coordinates for a given distance in miles
def get_bounding_box_coords(lat, lon, distance_miles=10):
	lao.print_function_name('mpy def get_bounding_box_coords')
	import math

	# Check if lat/lon are valid
	if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
		raise ValueError(" Invalid latitude or longitude values.")

	# Earth radius in miles
	R = 3960.0
	
	# Convert distance from miles to radians
	distance_rad = distance_miles / R
	
	# Make sure latitude is a float
	lat = float(lat)
	lon = float(lon)
	
	# Latitude in radians
	lat_rad = math.radians(lat)
	
	# Delta latitude in degrees
	delta_lat = math.degrees(distance_rad)
	
	# Delta longitude in degrees, adjusted by latitude
	delta_lon = math.degrees(distance_rad / math.cos(lat_rad))
	
	# Calculate new coordinates
	north_lat = lat + delta_lat
	south_lat = lat - delta_lat
	east_lon = lon + delta_lon
	west_lon = lon - delta_lon
	
	return {
		"north_lat": north_lat,
		"south_lat": south_lat,
		"east_lon": east_lon,
		"west_lon": west_lon
	}

# Choose from list of parcel owners
def get_parcel_data(dAcc, dTF):
	lao.print_function_name('[mpy def get_parcel_data]')
	import aws
	import fjson
	# Download ArcMakePIDFromParcelOwnerInfo json file from M1
	aws.get_m1_file_copy(action='DOWN')
	# Get json file with parcels/PID and other info
	filename_make_PID = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'
	dMake = fjson.getJsonDict(filename_make_PID)
	lUnique_owners = []
	lPropertyIds = []
	
	td.banner('Select Owner Entity and Person')
	onlyonerecord = True
	# dTF['PARCELPROPIDS'] = []
	lat_max, lat_min, lon_max, lon_min = 0, 100, -200, 0
	count_parcels, total_lat, total_lon = 0, 0, 0
	for indx in dMake:
		count_parcels += 1
		d = dMake[indx]
		# Only print uqniue owner records
		lInfo = [d['owner'], d['mailstreet'], d['mailcity'], d['mailstate'], d['mailzip']]
		if lInfo not in lUnique_owners:
			lUnique_owners.append(lInfo)
			print('\n****************************\n')
			print(' {0}'.format(indx))
			print(' {0}'.format(d['owner']))
			print(' {0}'.format(d['mailstreet']))
			print(' {0}, {1}  {2}'.format(d['mailcity'], d['mailstate'], d['mailzip']))

		# Add Acres to dAcc
		dTF['Acres__c'] = dTF['Acres__c'] + d['acres']
		# Add Parcel APNs
		if dTF['Parcels__c'] == 'None':
			dTF['Parcels__c'] = d['apn']
			dTF['Lead_Parcel__c'] = d['apn']
		else:
			dTF['Parcels__c'] = '{0}, {1}'.format(dTF['Parcels__c'], d['apn'])
		lPropertyIds.append(d['propertyid'])
		# Add Zoning
		if dTF['Zoning__c'] == 'None':
			if d['zoning'] != '':
				dTF['zoning__c'] = d['zoning']
		else:
			if d['zoning'] != '':
				dTF['zoning__c'] = '{0}, {1}'.format(dTF['zoning__c'], d['zoning'])
		# Calculate centroid of all parcels
		total_lat = total_lat + d['lat']
		total_lon = total_lon + d['lon']

		if indx == 'Index 2':
			onlyonerecord = False

	# Calculate centroid of all parcels
	dTF['Latitude__c'] = total_lat / count_parcels
	dTF['Longitude__c'] = total_lon / count_parcels
	# Round Acres to 2 decimal places
	dTF['Acres__c'] = round(dTF['Acres__c'], 2)

	if onlyonerecord:
		ui_indx = 'Index 1'
	else:
		print('\n Select Entity/Person to use buy Index Number')
		ui_indx = 'Index {0}'.format(td.uInput('\n Enter number or [00] to quit > '))
		if ui_indx == 'Index 00':
			exit('\n Terminating program...')

	# Get selected record
	d = dMake[ui_indx]
	dAcc['ENTITY'] = d['owner']
	if d['mailstreet']:
		dAcc['STREET']  = d['mailstreet'].strip()
		dAcc['STREET'] = td.titlecase_street(dAcc['STREET'])
	if d['mailcity']:
		dAcc['CITY']  = d['mailcity'].strip()
		dAcc['CITY'] = dAcc['CITY'].title()
	if d['mailstate']:
		dAcc['STATE']  = d['mailstate'].strip()
	if d['mailzip']:
		dAcc['ZIPCODE']  = d['mailzip'].strip()
	dAcc['SOURCE'] = 'Parcel'
	dTF['Source__c'] = 'LAO'

	# Get LAO Geo Info
	dTF = get_LAO_geoinfo(dTF)

	return dAcc, dTF, lPropertyIds

# Create ArcMap Zoom to Polygon Json file
def create_zoomToPolygon_json_file(fieldname=None, polyId=None, polyinlayer=None, lon=None, lat=None, market=None):
	# fieldname: apn, pid (leadid not supported)
	# polyId: APN or PID (LeadID not supported)
	# polyinlayer: [ST]Parcels[County] (i.e. AZParalsPima)
	# lon: Longitude
	# lat: Latitude
	# market: LAO market name (i.e. Tucson, Phoenix, etc.)
	from aws import get_m1_file_copy
	import json
	import fun_text_date as td
	# lao.print_function_name('fjson def create_ZoomToPolygon_json_file')
	
	# Get market from apn polyinlayer
	if fieldname == 'apn' and polyinlayer != None and market == None:
		county = polyinlayer[9:]
		dCounty = lao.getCounties('FullDict')
		for row in dCounty:
			if county == dCounty[row]['ArcName']:
				market = dCounty[row]['Market']
				break
				
	# Add trailing zero to Tucson parcels if needed
	if market == 'Tucson' and fieldname == 'apn':
		if len(polyId) == 10:
			polyId = '{0}0'.format(polyId)

	# Make dict
	d = {}
	d['zoomquery'] = "{0} in ('{1}')".format(fieldname, polyId)
	d['fieldName'] = fieldname
	d['polyId'] = polyId
	d['layer'] = polyinlayer
	d['lon'] = lon
	d['lat'] = lat
	d['market'] = market

	# Save json file
	with open('C:/Users/Public/Public Mapfiles/zoomToPolygon.json', 'w') as f:
		json.dump(d, f)
	with open('C:/Users/Public/Public Mapfiles/M1_Files/zoomToPolygon.json', 'w') as f:
		json.dump(d, f, indent=4)

	get_m1_file_copy(action='UP')

# Check TF for Deal centroids within a certain distance of a lon/lat
def find_deals_in_extent(service, lon, lat, distance_feet=150):
	"""
	Find lda_Opportunity__c records within the specified distance of a point.
	
	Args:
		lon: Longitude in decimal degrees
		lat: Latitude in decimal degrees
		distance_feet: Distance to offset (default 150 feet)
	
	Returns:
		List of Deal records within the extent
	"""
	# Constants
	feet_per_degree_lat = 364567
	feet_per_degree_lon = 364567 * math.cos(math.radians(lat))
	
	# Calculate offsets in degrees
	lat_offset = distance_feet / feet_per_degree_lat
	lon_offset = distance_feet / feet_per_degree_lon
	
	min_lon = lon - lon_offset  # West
	min_lat = lat - lat_offset  # South
	max_lon = lon + lon_offset  # East
	max_lat = lat + lat_offset  # North
	
	# Build where clause
	where_clause = (
		f"Longitude__c >= {min_lon} AND Longitude__c <= {max_lon} "
		f"AND Latitude__c >= {min_lat} AND Latitude__c <= {max_lat}"
	)
		
	# Query for Deals
	results = bb.tf_query_3(service, 'Deal', where_clause)
	
	return results

# OWNERINDEX FUNCTIONS #####################################################################

# 	action values
#	"Make New OI Poly from Parcels" - Creates OI poly from APNs NEVER USED THIS
# 	"Make New OI Poly from Parcel PropertyIds" - Creates OI Poly from PropertyIds
# 	"Make New OI Poly from OI poly" - Creates OI based on PID.
#	      Used to create an Ownership after a closed deal is created
# 	"Delete OI Poly" - Deletes an OI poly

# Make a new OI poly from a list of parcel propertyid(s)
def oi_make_from_parcel_propertyid(dTF='None', lPropertyIds='None'):

	print('\n Creating OwnerIndex Poly...')
	# Construct parcel layer name and county (stAbb_county)
	if len(dTF['State__c']) > 2:
		stAbb = lao.convertState(dTF['State__c'])
	else:
		stAbb = dTF['State__c']
	county = dTF['County__c']
	layername = f'{stAbb}Parcels{county}'.upper()
	county = f'{stAbb}_{county}'
	
	# Get the dictionary of M1 parameters (user, initials and date is included in the dictionary)
	m1_params = dicts.get_blank_m1_params_dict()
	# Assign the parameters to the dictionary
	m1_params["action"] = "Make New OI Poly from Parcel PropertyIds"
	m1_params["county"] = county
	m1_params["fieldName"] = "propertyid"
	m1_params["layername"] = layername
	m1_params["pid"] = dTF['PID__c']
	m1_params["propertyid"] = lPropertyIds

	# Save the dictionary to a json file
	# M1 folder
	with open('C:/Users/Public/Public Mapfiles/M1_Files/m1_params.json', 'w') as f:
		dump(m1_params, f)
	# ArcGIS folder
	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'w') as f:
		dump(m1_params, f)
	# M1 Json files folder
	username = lao.getUserName()
	with open(f'F:/Research Department/Code/M1 Json Files/m1_params_{username}.json', 'w') as f:
		dump(m1_params, f)
	# Make the OI Poly
	oi_result = oi_post(m1_params)
	td.colorText('\n OI Poly created...', 'GREEN')
	return oi_result

# Make a new OI poly from a PID
def oi_make_from_pid(PID='None', PIDnew='None'):
	user, initials = lao.getUserName(initials=True)
	today_date = td.today_date(dateformat='slash')
	# Get the dictionary of M1 parameters (user, initials and date is included in the dictionary)
	m1_params = dicts.get_blank_m1_params_dict()
	# Assign the parameters to the dictionary
	m1_params["action"] = "Make New OI Poly from OI poly"
	m1_params["fieldName"] = "pid"
	m1_params["pid"] = PID
	m1_params["pidnew"] = PIDnew
	
	# Make the OI Poly
	oi_result = oi_post(m1_params)
	return oi_result

# Delete an OI poly
def oi_delete_poly(PID):
	print('\n Deleting OwnerIndex Poly...')
	# Get the TerraForce service
	# service = fun_login.TerraForce()
	# Get the dictionary of M1 parameters (user, initials and date is included in the dictionary)
	m1_params = dicts.get_blank_m1_params_dict()
	# Assign the parameters to the dictionary
	m1_params["action"] = "Delete OI Poly"
	m1_params["pid"] = PID
	m1_params["fieldName"] = "pid"
	m1_params["layername"] = "OwnerIndex"
	# Delete the OI Poly
	oi_result = oi_post(m1_params)
	if oi_result:
		td.colorText('\n OwnerIndex Poly deleted...', 'GREEN')
		lao.sleep(2)
		return True
	else:
		td.colorText('\n OI Poly not deleted...', 'YELLOW')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		return False

# Make OPR Map
def make_opr_map_api(service, PID, pause_it=True):
	import requests
	import aws
	import os
	from PIL import Image
	# import webs
	lao.print_function_name('mpy def make_opr_map_api')

	print(f'\n Creating OPR Map of {PID}...')

	# CHECK IF PID EXISTS IN TERRA FORCE ################################################
	# TerraForce Query
	fields = 'default'
	wc = f"PID__c = '{PID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# Check if the PID was found in TF
	if results == []:
		td.warningMsg(f'\n OPR map not created because the PID {PID} was not found in TerraForce.')
		if pause_it:
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
		return 'PID not found'
	#######################################################################################
	
	# Construct parcel layer name (stAbb_county)
	if len(results[0]['State__c']) > 2:
		stAbb = lao.convertState(results[0]['State__c'])
	else:
		stAbb = results[0]['State__c']
	parcel_layer = f'{stAbb}_{results[0]['County__c']}'

	# Make the API call to create the OPR map
	lao.print_function_name('mpy def make_opr_map_api - Making map API Call Loop')
	attempts_counter = 0
	while 1:
		is_map_created = False
		if attempts_counter < 2:
			url = f'https://m1.landadvisors.com/api/ownerindex-static/{parcel_layer}?pid={PID}'
			r = requests.get(url)
			# Check if the PNG map was created
			if aws.aws_file_exists(PID, extention='png', verbose=False):
				# print(f'\n OPR Map PNG Created: {PID}')
				is_map_created = True
				break
			else:
				attempts_counter += 1
				continue
		
		# Check if the map was created
		if is_map_created is False:
			td.warningMsg(f'\n OPR Map Not Created: {PID}')
			if pause_it:
				td.warningMsg('\n Confirm that PID {PID} has a polygon in the OwnerIndex layer.', colorama=True)
				# print('\n API Response: {0}'.format(r.text))
				print('\n Options:')
				print('  1) Retry creating OPR Map')
				print('  2) Continue without creating OPR Map')
				print(' 00) Quit')
				ui = td.uInput('\n Enter option > ')
				if ui == '1':
					attempts_counter = 0
					continue
				elif ui == '2':
					return False
				elif ui == '00':
					exit('\n Terminating program...')
			else:
				return False

	# Set variables
	img_path = 'C:/Users/Public/Public Mapfiles/M1_Files/'
	img_png = f'{img_path}{PID}.png'
	img_jpg = img_png.replace('.png', '.jpg')
	size = (600, 600)

	# Download the OPR map
	while 1:
		aws.opr_map_aws_copy(PID, action='DOWN')
		# print(f'\n Downloaded OPR Map PNG: {PID}')
		# Confirm OPR map png was downloaded
		if os.path.exists(img_png):
			break
		else:
			aws.opr_map_aws_copy(PID, action='DOWN')

		if not os.path.exists(img_png):
			td.warningMsg(f'\n OPR Map Not Created: {PID}')
			if pause_it:
				td.warningMsg('\n Confirm that PID {PID} has a polygon in the OwnerIndex layer.', colorama=True)
				print('\n Options:')
				print('  1) Retry creating OPR Map')
				print('  2) Continue without creating OPR Map')
				print(' 00) Quit')
				ui = td.uInput('\n Enter option > ')
				if ui == '1':
					attempts_counter = 0
					continue
				elif ui == '2':
					return False
				elif ui == '00':
					exit('\n Terminating program...')
			else:
				return False
		else:
			break
		
	# Resize to 600 x 600 and create jpg copy
	"""
	Converts a PNG image to JPG format.
	
	:param png_path: Path to the input PNG file.
	:param jpg_path: Path to the output JPG file.
	:param quality: Quality setting for the output JPG (default: 85).
	"""
	# Open the PNG image
	# print(f'\n Resizing OPR Map: {PID}...')
	with Image.open(img_png) as img:
		# Resize the image
		resized_img = img.resize(size, Image.LANCZOS)
		# Save the image, overwriting the original file
		resized_img.save(img_png, 'PNG')

	# Make the jpg copy
	#print(f'\n Creating JPG copy of OPR Map: {PID}...')
	with Image.open(img_png) as img:
		# Convert to RGB (PNG can have transparency, but JPG does not support it)
		rgb_img = img.convert('RGB')
		# Save the image in JPG format
		rgb_img.save(img_jpg, 'JPEG', quality=85)

	# Check if PID has a child Deal in TerraForce
	# TerraForce Query
	fields = 'Id, Acres__c'
	wc = f"PID__c = '{PID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	DID = results[0]['Id']
	acres = results[0]['Acres__c']
	if acres == 'None':
		results = []
	else:
		# TerraForce Query
		fields = 'Id, Name, PID__c, Parent_Opportunity__c'
		wc = f"Parent_Opportunity__c = '{DID}' and Acres__c = {acres} and (NOT PID__c LIKE '%MarketingGroup%') and (NOT PID__c LIKE 'none%') and (RecordTypeId = '012a0000001ZSS8AAO' or RecordTypeId = '012a0000001ZSS5AAO') and (StageName__c = 'Lead' or StageName__c = 'Top100' or StageName__c LIKE '%Lisingg%')"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	# Create a copy of the OPR map for the child Deal
	if len(results) == 1:
		print(f'\n Creating OPR Map copy for child Deal: {results[0]['PID__c']}...')
		PID_child = results[0]['PID__c']
		img_jpg_child = img_jpg.replace(f'{PID}.jpg', f'{PID_child}.jpg')
		# Copy the jpg file
		if os.path.exists(img_jpg):
			from shutil import copyfile
			copyfile(img_jpg, img_jpg_child)
			lao.sleep(1)

		
		# Upload the jpg copy for the child Deal
		aws.opr_map_aws_copy(PID_child, action='UP')

		# Delete the jpg copy for the child Deal
		if aws.aws_file_exists(PID_child, extention='jpg', verbose=True):
			os.remove(img_jpg_child)
	
	# Upload the jpg copy
	# print(f'\n Uploading OPR Map to AWS: {PID}...')
	aws.opr_map_aws_copy(PID, action='UP')


	if aws.aws_file_exists(PID, extention='jpg', verbose=True):
		# Delete the png and jpg files
		if os.path.exists(img_png):
			os.remove(img_png)
		if os.path.exists(img_jpg):
			os.remove(img_jpg)
		td.colorText(' OPR Map JPG Created', 'GREEN', colorama=True)
		return 'Success'
	else:
		td.colorText(' OPR Map JPG Not Created', 'RED', colorama=True)
		return 'Fail'

# Post OwnderIndex Request to AWS
def oi_post(m1_params):
	import requests
	lao.print_function_name('mpy def oi_post')

	username = lao.getUserName()

	action = m1_params["action"]
	# Define the URL for the POST request
	url = 'https://m1.landadvisors.com/api/ownerindex-action'
	# Make the POST request with the parameters
	r = requests.post(url, json=m1_params)
	if r.status_code == 200:
		# print(r.status_code)
		td.colorText(f'\n {action} successful using M1 API.', 'GREEN')
		return True
	else:
		# Action failed
		# If action is "Make New OI Poly from Parcel PropertyIds" and the response is "OwnerIndex polygon not found"
		print(f'\n {action} failed using M1 API.')
		print(f' Trying ArcGIS...')
		print(f'\n {r.text}')
		if username == 'blandis':
			print('\n Here10 mpy.py')
			pprint(m1_params)
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

		# Try createing OwnerIndex poly using ArcGIS
		
		lResearchers = ['blandis', 'tjacobson', 'avidela', 'lcoxworth', 'lsweetser', 'mwifler', 'ccox', 'mklingen']
		if username in lResearchers:
			from aws import run_Arc_AWS
			run_Arc_AWS()
			return True
		else:
			print('here3 mpy.py')
			print(f'\n Writing m1_params.json to F:/Research Department/Code/M1 Json Files/m1_params_{username}.json\n')
			
			pprint(m1_params)

			with open(f'F:/Research Department/Code/M1 Json Files/m1_params_{username}.json', 'w') as f:
				dump(m1_params, f)


			return True

# Get the parcel data from M1 or ArcMap ArcMakePIDFromParcelOwnerInfo.json file
def get_parcel_data():
	dAcc = dicts.get_blank_account_dict()
	dTF = dicts.get_blank_tf_deal_dict()
	dPoly = {'PARCELPROPIDS': []}
	# Download ArcMakePIDFromParcelOwnerInfo json file from M1
	aws.get_m1_file_copy(action='DOWN')
	# Get json file with parcels/PID and other info
	filename_make_PID = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'
	dMake = fjson.getJsonDict(filename_make_PID)
	lUnique_owners = []
	
	td.banner('Find Create Entity and Person')
	onlyonerecord = True
	# dTF['PARCELPROPIDS'] = []
	lat_max, lat_min, lon_max, lon_min = 0, 100, -200, 0
	count_parcels, total_lat, total_lon = 0, 0, 0
	for indx in dMake:
		count_parcels += 1
		d = dMake[indx]
		# Only print uqniue owner records
		lInfo = [d['owner'], d['mailstreet'], d['mailcity'], d['mailstate'], d['mailzip']]
		if lInfo not in lUnique_owners:
			lUnique_owners.append(lInfo)
			print('\n****************************\n')
			print(' {0}'.format(indx))
			print(' {0}'.format(d['owner']))
			print(' {0}'.format(d['mailstreet']))
			print(' {0}, {1}  {2}'.format(d['mailcity'], d['mailstate'], d['mailzip']))

		# Add Acres to dAcc
		dTF['Acres__c'] = dTF['Acres__c'] + d['acres']
		# Add Parcel APNs
		if dTF['Parcels__c'] == 'None':
			dTF['Parcels__c'] = d['apn']
			dTF['Lead_Parcel__c'] = d['apn']
		else:
			dTF['Parcels__c'] = '{0}, {1}'.format(dTF['Parcels__c'], d['apn'])
		dPoly['PARCELPROPIDS'].append(d['propertyid'])
		# Add Zoning
		if dTF['Zoning__c'] == 'None':
			if d['zoning'] != '':
				dTF['zoning__c'] = d['zoning']
		else:
			if d['zoning'] != '':
				dTF['zoning__c'] = '{0}, {1}'.format(dTF['zoning__c'], d['zoning'])
		# Calculate centroid of all parcels
		total_lat = total_lat + d['lat']
		total_lon = total_lon + d['lon']

		if indx == 'Index 2':
			onlyonerecord = False

	# Calculate centroid of all parcels
	dTF['Latitude__c'] = total_lat / count_parcels
	dTF['Longitude__c'] = total_lon / count_parcels
	# Round Acres to 2 decimal places
	dTF['Acres__c'] = round(dTF['Acres__c'], 2)

	if onlyonerecord:
		ui_indx = 'Index 1'
	else:
		while 1:
			print('\n Select Entity/Person to use buy Index Number')
			ui_indx = 'Index {0}'.format(td.uInput('\n Enter number or [00] to quit > '))
			if ui_indx == 'Index 00':
				exit('\n Terminating program...')
			try:
				d = dMake[ui_indx]
				break
			except KeyError:
				td.warningMsg('\n Invalid input...try again...')
				lao.sleep(1)

	# 	print('\n Select Entity/Person to use buy Index Number')
	# 	ui_indx = 'Index {0}'.format(td.uInput('\n Enter number or [00] to quit > '))
	# 	if ui_indx == 'Index 00':
	# 		exit('\n Terminating program...')

	# d = dMake[ui_indx]
	dAcc['ENTITY'] = d['owner']
	if d['mailstreet']:
		dAcc['STREET']  = d['mailstreet'].strip()
		dAcc['STREET'] = td.titlecase_street(dAcc['STREET'])
	if d['mailcity']:
		dAcc['CITY']  = d['mailcity'].strip()
		dAcc['CITY'] = dAcc['CITY'].title()
	if d['mailstate']:
		dAcc['STATE']  = d['mailstate'].strip()
	if d['mailzip']:
		dAcc['ZIPCODE']  = d['mailzip'].strip()
	dAcc['SOURCE'] = 'Parcel'
	dTF['Source__c'] = 'LAO'

	return dAcc, dTF, dPoly

# Get the ObjectID from OwnerIndex layer based on PID
def get_OID_from_PID(PID, gis='None'):
	from arcgis.features import FeatureLayer
	import fun_login
	# Login to LAO ArcGIS Portal
	if gis == 'None':
		gis = fun_login.LAO_ArcGIS_portal()

	# Feature Service URL and layer index
	feature_service_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer"
	layer_index = 0  # OwnerIndex is Feature Class 0
	layer_url = f"{feature_service_url}/{layer_index}"

	# Create FeatureLayer object
	owner_index_layer = FeatureLayer(layer_url, gis=gis)
	
	# Create the where clause to filter by PID
	where_clause = "pid = '{0}'".format(PID)
	
	# Query the layer
	feature_set = owner_index_layer.query(
		where=where_clause,
		out_fields=["objectid", "pid"],
		return_geometry=False
	)

	# Check if any features were returned
	if feature_set.features and len(feature_set.features) > 0:
		# Get the first (and should be only) matching record
		feature = feature_set.features[0]
		# Try both lowercase and uppercase field names
		objectid = feature.attributes.get('OBJECTID') or feature.attributes.get('objectid')
		
		print(f" Found record for PID '{PID}': ObjectID = {objectid}")
		return objectid
	else:
		td.warningMsg(f" No polygon found for OwnerIndex layer with PID '{PID}'")
		return None

# END OF FILE ##############################################################################