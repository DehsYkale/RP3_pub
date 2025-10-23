print(' Importing arcgis...')
import arcgis
from arcgis.gis import GIS
import arcgis.features
# from IPython.display import display
# from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureLayer
from arcgis.features import FeatureSet
from arcgis.geometry import Point
from arcgis.geoanalytics import manage_data
from importlib.machinery import SourceFileLoader
import fjson
from os import system
from pprint import pprint
import fun_text_date as td
import lao

# Clears the console and create a banner_internal based on agrument
def banner_internal(title='Arc AWS v02'):
	system('cls')
	print
	print('        '+('-' * (len(title)+4)))
	print(' ------|'+(' ' * (len(title)+4))+'|------')
	print('  \\    |  '+title+'  |    /')
	print('   \\   |'+ (' ' * (len(title)+4)) + '|   /')
	print('   /    '+ ('-' * (len(title)+4)) + '    \\')
	print('  /      )'+ (' ' * (len(title))) + '(      \\')
	print(' --------'+ (' ' * (len(title))) + '  --------')
	print

# Login to the AWS server
def loginAWS():
	from getpass import getuser
	import time
	d['user'] = getuser().lower()
	d['initials'] = d['user'][:2].upper()
	d['dateupdated'] = (time.strftime('%m/%d/%Y'))

	print('\n Loging into LAO portal...')
	
	d['user'] = 'blandis'
	pwd = 'Logmeintoarcmap5!'

	print
	print(' User:   {0}'.format(d['user']))
	print('  Pwd:   {0}'.format(pwd))
	print('  Int:   {0}'.format(d['initials']))
	print(' Date:   {0}'.format(d['dateupdated']))
	print
	gis = GIS("https://maps.landadvisors.com/portal", d['user'], pwd, verify_cert=True)

	print(' Login complete...')
	# # Check what you can access
	print(f"Your username: {gis.users.me.username}")
	print(f"Your role: {gis.users.me.role}")
	# exit()
	return gis

# Get the AWS services
def getServices(gis, serviceListName='Reserach'):
	# Service Lists (Research_Parcels, Research_Leads, Research_Edit_Main)
	titleName = 'title:{0}'.format(serviceListName)
	service_list = gis.content.search(serviceListName, item_type="Feature Layer")

	# 	# Print the contents of service_list
	# for i, item in enumerate(service_list):
	# 	print(f"Item {i+1}:")
	# 	print(f"\tTitle: {item.title}")
	# 	print(f"\tID: {item.id}")
	# 	print(f"\tType: {item.type}")
	# 	print(f"\tOwner: {item.owner}")
	# 	print(f"\tCreated: {item.created}")
	# 	print(f"\tURL: {item.url}")
	# 	print()
	# exit()
	return service_list

# Get the OwnerIndex Feature Layer
def get_OwnerIndex_Feature_Layer():
	# Make OwnerIndex FeatureLayer
	lyr_url = 'https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer/0'
	OwnerIndex = FeatureLayer(lyr_url)
	return OwnerIndex

# Get the Ownerships Feature Layer
def get_Ownerships_Feature_Layer():
	# Make Ownerships FeatureLayer
	lyr_url = 'https://maps.landadvisors.com/arcgis/rest/services/Research_View_Main/FeatureServer/2'
	Ownerships = FeatureLayer(lyr_url)
	return Ownerships

# Get the Parcels or Leads Feature Layer by Layer Name
def get_Feature_Layer(service_list, layername):
	# Get dict of Service Layers
	print('\n layername: {0}'.format(layername))
	from json import load
	if 'LEADS' in layername:
		lyrType = 'Leads'
	elif 'PARCELS' in layername:
		lyrType = 'Parcels'
	# jsonFile = 'F:/Research Department/Code/Research/data/AWS_{0}_Service_Layers.json'.format(lyrType)
	jsonFile = 'F:/Research Department/Code/Databases/AWS_{0}_Service_Layers.json'.format(lyrType)
	with open(jsonFile, 'rb') as f:
		dLayers = load(f)
	for row in dLayers['layers']:
		if layername.upper() == row['name'].upper():
			lyrID = row['id']
			print('\n Selected Layer: {0} : {1}'.format(row['name'], lyrID))
			break
	lyr_url = 'https://maps.landadvisors.com/arcgis/rest/services/Research_{0}/FeatureServer/{1}'.format(lyrType, lyrID)
	lyr = FeatureLayer(lyr_url)
	return lyr

# Make new OwnerIndex poly from Parcels
def make_OwnerIndex_Poly_from_Parcels(d):
	# Service List (Research_Parcels, Research_Leads, Research_Edit_Main)
	print('\n Getting Service List from Research_Parcels to query...')
	service_list = getServices(gis, serviceListName='Research_Parcels')
	
	lParcels = d['parcels'].split(', ')  # fieldValueList must be a list
	if len(lParcels) == 0:
		td.warningMsg('\n NO APNs IN SELECTED PARCELS')
		td.uInput('\n  No OwnerIndex polygon created.\n\n Quitting Arc_AWS_v02 script.\n [Enter] to quit.')
		exit('\n Program termintated...')
	fieldName = d['fieldName'] # Usually APN
	layername = d['layername']

	# Handle Cheatham county spaces in APN
	lTNParcelLayers = ['TNPARCELSBEDFORD', 'TNPARCELSCHEATHAM', 'TNPARCELSDICKSON',  'TNPARCELSHICKMAN', 'TNPARCELSLOUDON',  'TNPARCELSMARSHALL',  'TNPARCELSROBERTSON', 'TNPARCELSSUMNER', 'TNPARCELSWILSON']
	for tnParcelLayer in lTNParcelLayers:
		if tnParcelLayer in layername:
			lTemp = []
			for row in lParcels:
				row = row.replace(' ','')
				if len(row) == 11:
					lTemp.append('{0}    {1}'.format(row[:6], row[6:]))
				else:
					lTemp.append('{0} {1} {2}'.format(row[:7], row[7:8], row[8:]))
			lParcels = lTemp
	if 'TNPARCELSMONTGOMERY' in layername:
		fieldname = 'propertyid'
	if 'TNPARCELSMAURY' in layername:
		fieldname = 'altapn'
	if 'TNPARCELSRUTHERFORD' in layername:
		lTemp = []
		for row in lParcels:
			row = row.replace(' ','')
			if len(row) == 8:
				lTemp.append('{0}    {1}'.format(row[:3], row[3:]))
			else:
				lTemp.append('{0} {1} {2}'.format(row[:4], row[4:5], row[5:]))
		lParcels = lTemp
	if 'TNPARCELSWILLIAMSON' in layername:
		lTemp = []
		for row in lParcels:
			row = row.replace(' ','')
			if len(row) == 8:
				lTemp.append('{0}    {1}'.format(row[:3], row[3:]))
			else:
				lTemp.append('{0} {1} {2}'.format(row[:4], row[4:5], row[5:]))
		lParcels = lTemp

	# Get Parcel Layer Feature based on layer name
	print('\n Getting parcel Feature Layer to query...')
	queryLyr = get_Feature_Layer(service_list, layername)

	# Query selected parcels
	print('\n Querying parcels by APN')
	print('   Parcels: {0}'.format(lParcels))
	print('   LayerID: {0}'.format(layername))
	query_result = queryFeatures(queryLyr, fieldName, fieldValueList=lParcels)

	# Disolve if more than 1 parcel
	if len(lParcels) >= 2:
		print('\n Disolving parcels into one poly...')
		# Dissolve takes a feature_collection so convert
		query_result = disolveParcels(query_result)

	# Append (may be more than one feature)
	print('\n Appending to OwnerIndex (Make OwnerIndex from Parcels)')
	# print(query_result)
	update_result = OwnerIndex.edit_features(adds=query_result)

	# Add Attributes to newly created OwnerIndex
	update_result = addAttributes(update_result)

# Make new OwnerIndex poly from Parcels
def make_OwnerIndex_Poly_from_Parcel_ProperyIds(d):
	# Service Lits (Research_Parcels, Research_Leads, Research_Edit_Main)
	print(' Getting Service List from Research_Parcels to query...')
	service_list = getServices(gis, serviceListName='Research_Parcels')
	
	# lParcels = d['parcels'].split(', ')  # fieldValueList must be a list
	fieldName = d['fieldName'] # Usually APN
	layername = d['layername']
	lPropertyIds = d['propertyid']

	# Get Parcel Layer Feature based on layer name
	print(' Getting parcel Feature Layer to query...')
	queryLyr = get_Feature_Layer(service_list, layername)

	# Query selected parcels
	print('\n Querying parcels by properyid')
	print('   LayerID:     {0}'.format(layername))
	print('   Field Name:  {0}'.format(fieldName))
	print('   PropertyIds: {0}'.format(lPropertyIds))
	
	# Query the parcels by propertyid in the list lPropertyIds
	query_result = queryFeatures(queryLyr, fieldName, fieldValueList=lPropertyIds)

	# Check if any parcels were selected
	if len(query_result) == 0:
		print('\n WARNING: No parcels selected for the Property IDs.')
		input('\n Continue...')
		exit()

	# Disolve if more than 1 parcel
	if len(query_result) >= 2:
		print('\n Disolving parcels into one poly...')
		# Dissolve takes a feature_collection so convert
		query_result = disolveParcels(query_result)

	# Append the polygon to OwnnerIndex (may be more than one feature)
	print('\n Appending to OwnerIndex (Make OwnerIndex Poly from Parcel Property IDs)')
	update_result = OwnerIndex.edit_features(adds=query_result)

	# Add Attributes to newly created OwnerIndex
	update_result = addAttributes(update_result)

	# input('\n Continue...')

# Make new OwnerIndex poly from Parcels
def make_OwnerIndex_Poly_from_Lead(d):
	
	# Service Lits (Research_Parcels, Research_Leads, Research_Edit_Main)
	print('\n Getting Service List from Research_Leads to query...')
	service_list = getServices(gis, serviceListName='Research_Leads')
	
	lLeads = d['lid'].split(', ')  # fieldValueList must be a list
	fieldName = d['fieldName'] # Usually LeadId
	layername = d['layername']

	# Get Parcel Layer Feature based on layer name
	print('\n Getting Leads Feature Layer to query...')
	queryLyr = get_Feature_Layer(service_list, layername)

	# Query selected parcels
	print('\n Querying Leads by LeadId')
	query_result = queryFeatures(queryLyr, fieldName, fieldValueList=lLeads)

	# Append (may be more than one feature)
	print('\n Appending Lead to OwnerIndex')
	update_result = OwnerIndex.edit_features(adds=query_result)

	# Add Attributes to newly created OwnerIndex
	update_result = addAttributes(update_result)

# Returns feature collection and extent
def queryFeatures(queryLyr, fieldName, fieldValueList):

	# query the features
	query_result = queryLyr.query(where="{} IN ('{}')".format(fieldName, "','".join(fieldValueList)), return_extent_only=False)


	return query_result

# Disolve multiple parcels into one poly
def disolveParcels(query_result):
	feature_collection = arcgis.features.FeatureCollection.from_featureset(query_result)
	dissolved_query_result = arcgis.features.analysis.dissolve_boundaries(feature_collection, summary_fields=["acres Sum"], multi_part_features=True)
	dissolved_feature_set = dissolved_query_result.query()
	return dissolved_feature_set

# Check if Ownership exits based on Lead's lon/lat & return PID in json file
def Ownership_Exist():

	print('\n Checking if Ownership exists...')
	# ******************************************************************************
	# Variables
	LeadCentroid = 'C:/Users/Public/Public Mapfiles/lead_centroid.shp'
	OwnershipPIDField = ['propertyid']
	# Get Ownerships Feature Layer
	lyr_url = 'https://maps.landadvisors.com/arcgis/rest/services/Research_View_Main/FeatureServer/80'
	Ownerships = FeatureLayer(lyr_url)
	# ******************************************************************************

	# ******************************************************************************
	# select polygon that intersects Lead centroid
	arcpy.SelectLayerByLocation_management(Ownerships, "INTERSECT", LeadCentroid)
	# Determine if any Ownerships were selected
	resultsOwnerships = arcpy.da.SearchCursor(Ownerships, OwnershipPIDField)
	results = arcpy.GetCount_management(resultsOwnerships)
	OwnershipCount = int(results.getOutput(0))

	if OwnershipCount > 0:
		for row in resultsOwnerships:
			OwnershipPID = row[0]
			print(' Ownership exists ({0})...'.format(OwnershipPID))
			input('\n Continue...')
			break
	else:
		exit()
	# ******************************************************************************
	
	# ******************************************************************************
	# Write query results to json file
	j = {'action': 'Query Ownerships',
	'dateupdated': 'None',
	'initials': 'None',
	'oid': 'None',
	'layername': 'Ownerships',
	'lid': 'None',
	'fieldName': 'apn',
	'parcels': 'None',
	'pid': OwnershipPID,
	'pidnew': 'None'
	}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'wb') as f:
		dump(j, f)
	# ******************************************************************************
	input('\n Continue...')
	exit()

def get_ownerindex_from_lon_lat(lon=-82.463073, lat=28.238743, spatial_reference=4326):
	lyr_url = 'https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer/0'
	# Get the feature layer
	feature_layer = FeatureLayer(lyr_url)
	print('here2')
	# # Construct a point geometry from the provided longitude and latitude
	# point_geometry = {
	# 	"x": lon,
	# 	"y": lat,
	# 	"spatialReference": {"wkid": spatial_reference}
	# }
	point_geometry = Point({
		"x": lon,
		"y": lat,
		"spatialReference": {"wkid": spatial_reference}
	})
	# Use the buffer method to create a small buffer around the point to account for any slight discrepancies between the provided coordinates and the actual polygon vertices
	buffer_distance = 0.001  # Adjust as needed
	buffer_geometry = {
		"x": lon,
		"y": lat,
		"distance": buffer_distance,
		"units": "esriSRUnit_Meter",
		"spatialReference": {"wkid": spatial_reference},
		"geometryType": "esriGeometryPoint"
	}

	# Query the feature layer to find intersecting polygons
	query_result = feature_layer.query(geometry=point_geometry.within)
	# query_result = feature_layer.query(geometry_filter=buffer_geometry, return_geometry=True, max_allowable_offset=0.1, out_fields="pid")

	num_polygons_selected = len(query_result.features)  # Determine the number of polygons selected
	print(num_polygons_selected)
	if query_result.features:
		# Assuming only one feature will intersect, retrieve the first feature
		intersecting_feature = query_result.features[0]
		# Get the value of the 'PID' attribute
		PID = intersecting_feature.attributes['pid']
		print(PID)
		print('here4')
		intersecting_feature = query_result.features[1]
		PID = intersecting_feature.attributes['pid']
		print(PID)
	else:
		PID = None

	print(PID)
	input('\n Continue...')

	return PID

# Add Attributes to OwnerIndex
def addAttributes(update_result):
	# Append (may be more than one feature)
	print('\n Adding data to fields')
	oidList = []
	for result in update_result['addResults']:
		if result['success']:
			oidList.append(result['objectId'])
	# print(update_result)
	# print(oidList)
	# Update - handles multiple appends
	try:
		oi_selection = OwnerIndex.query(where="objectId IN ({})".format(','.join(str(v) for v in oidList)))
	except:
		print('\n WARNING: Tell Bill the Parcel and Leads json files need to be updated.')
		print(' They are located at https://maps.landadvisors.com/arcgis/rest/services/Research_Parcels/FeatureServer')
		print(' The json file is F:\Research Department\scripts\Projects\Research\data\AWS_Leads_Service_Layers.json')
		input('\n DO NOT CLOSE UNTIL YOU TELL BILL')
		exit('\n Terminating program...')
	print('\n Adding attributes:')
	if d['pidnew'] == 'None':
		print('\n   PID: {0}'.format(d['pid']))
	else:
		print('\n   PID: {0}'.format(d['pidnew']))
	print('\n   Initials: {0}'.format(d['initials']))
	print('\n   PID: {0}'.format(d['dateupdated']))
	for oid in oi_selection.features:
		if d['pidnew'] == 'None':
			oid.attributes['pid'] = d['pid']
		else:
			oid.attributes['pid'] = d['pidnew']
		oid.attributes['Initials'] = d['initials']
		oid.attributes['dateupdated'] = d['dateupdated']
		update_result = OwnerIndex.edit_features(updates=[oid])
	return update_result

# Delete polygons from AWS
def deleteFeatures(OID):
	del_results = OwnerIndex.delete_features(where = "objectId IN ({0})".format(OID))


if __name__ == '__main__':

	# Color cmd window blue
	system('color 1f') # blue with white letters

	banner_internal()

	# Get parcel list from json file
	d = fjson.getJsonDict('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json')
	# Login to service and get token
	gis = loginAWS()

	# Get OwnerIndex Feature Layer based on service url
	print('\n Getting OwnerIndex Feature Layer to query...')
	OwnerIndex = get_OwnerIndex_Feature_Layer()

	

	# CREATE FROM PARCELS **************************************************
	if d['action'] == 'Make New OI Poly from Parcels':
		make_OwnerIndex_Poly_from_Parcels(d)
	# **********************************************************************

	# CREATE FROM PARCELS **************************************************
	if d['action'] == 'Make New OI Poly from Parcel PropertyIds':
		make_OwnerIndex_Poly_from_Parcel_ProperyIds(d)
	# **********************************************************************

	# CREATE FROM OWNERINDEX PID ***************************************************
	# Create new OwnerIndex poly from existing OwnerIndex poly
	if d['action'] == 'Make New OI Poly from OI poly':
		fieldName = d['fieldName']
		PID = d['pid'].split() # fieldValueList must be a list
		# Query selected OI poly
		print('\n Querying OwnerIndex by OID')
		query_result = queryFeatures(OwnerIndex, fieldName=fieldName, fieldValueList=PID)
		print('\n Appending to OwnerIndex (__main__ Create from OwnerIndex PID)')
		update_result = OwnerIndex.edit_features(adds=query_result)
		# Add Attributes to new OwnerIndex Poly
		update_result = addAttributes(update_result)
	# **********************************************************************

	# CREATE FROM LEAD ***************************************************
	# Create new OwnerIndex poly from Lead poly
	if d['action'] == 'Make New OI Poly from Lead poly':
		make_OwnerIndex_Poly_from_Lead(d)
	# **********************************************************************

	# UPDATE ATTRIBUTES ****************************************************
	# Update the Attributes of a Split PID
	if d['action'] == 'Split OwnerIndex Update Attributes for New PID':
		print('\n Updating attributes of split PID...')
		# query the features
		oi_selection = OwnerIndex.query(where="{} IN ('{}')".format(d['fieldName'], d['oid']), return_extent_only=False)
		for oid in oi_selection.features:
			oid.attributes['pid'] = d['pid']
			oid.attributes['initials'] = d['initials']
			oid.attributes['dateupdated'] = d['dateupdated']
			update_result = OwnerIndex.edit_features(updates=[oid])
			print
			print(update_result)

	# QUERY  OWNERSHIPS ****************************************************
	# Create new OwnerIndex poly from Lead poly
	if d['action'] == 'Ownership Exist':
		Ownership_Exist()
	# **********************************************************************

	# # GET LAYER JSON FILES**************************************************
	# # Create new OwnerIndex poly from Lead poly
	# if d['action'] == 'Get Feature Layer json files':
	# 	get_Feature_Layer_json_Files()
	# # **********************************************************************

	# DELETE ***************************************************************
	# Delete exiting OwnerIndex poly
	elif d['action'] == 'Delete OI Poly':
		print('\n Deleting OwnerIndex polygon...')
		deleteFeatures(d['oid'])
	# **********************************************************************
	
	# input('\n Fin...continue...')


	exit()
