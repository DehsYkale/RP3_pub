
import bb
import dicts
import fox_hunter as fh
import fjson
import fun_login
import fun_text_date as td
import json
import lao
import mpy
import os
from pprint import pprint
import json
import geopandas as gpd
import os
import time
import pandas as pd
from pprint import pprint

def get_lead_parcel_info_populate_dTF(dTF):

	start_time = time.time()
	# lAPN = ['181927010000002500', '181927010000002501', '181927010000002602', '181927010000002600']
	lAPN = dTF['Parcels__c'].split(',')
	county = dTF['County__c']
	state = dTF['State__c']
	MarketAbb = dicts.get_counties('MarketAbb', ArcName=county, State=state)
	layer_name = f"{state}Parcels{county}"

	# Read the parcel layer
	print('\n Getting parcel information for Lead')
	print(f"\n Reading parcel layer: {layer_name}...\n")
	os.environ['OGR_ORGANIZE_POLYGONS'] = 'SKIP'
	gdb_path = f"C:/Users/Public/Public Mapfiles/Parcels/{MarketAbb}.gdb"
	gdf = gpd.read_file(gdb_path, layer=layer_name, ignore_geometry=True)

	# Filter for all APNs in the list
	print(f" Finding {len(lAPN)} parcels...\n")
	result = gdf[gdf['apn'].isin(lAPN)]

	# Create nested dictionary with selected fields
	print(" Writing parcel information to dictionary...\n")
	fields = ['apn', 'saleprice', 'saledate', 'zoning', 'propertyid', 'subdiv', 
			'usedesc', 'owner', 'mailstreet', 'mailcity', 'mailstate', 'mailzip', 
			'acres', 'x', 'y', 'mtg1lender', 'mtg1type', 'mtg1recdt', 'mtg1amt', 
			'sellr1name', 'buyr1name']

	def clean_value(val):
		if val is None:
			return 'None'
		if val is pd.NaT:  # Add this line
			return 'None'
		if isinstance(val, float) and pd.isna(val):
			return 'None'
		if isinstance(val, pd.Timestamp) and pd.isna(val):
			return 'None'
		if isinstance(val, str) and val.strip() == '':
			return 'None'
		return val

	dParcels = {
		row['apn']: {k: clean_value(v) for k, v in row[fields].to_dict().items()}
		for _, row in result.iterrows()
	}

	print(f" Found {len(dParcels)} of {len(lAPN)} parcels\n")
	pprint(dParcels)

	elapsed_time = time.time() - start_time
	print(f"\n Execution time: {elapsed_time:.2f} seconds")

	# Populate dTF with parcel information
	lPropertyIds = []
	for row in dParcels:
		d = dParcels[row]
		if dTF['Sale_Date__c'] == 'None' and d['saledate'] != 'None':
			dTF['Sale_Date__c'] = d['saledate']
		if dTF['Sale_Price__c'] == 'None' and d['saleprice'] != 'None':
			dTF['Sale_Price__c'] = d['saleprice']
		if dTF['Subdivision__c'] == 'None' and d['subdiv'] != 'None':
			dTF['Subdivision__c'] = d['subdiv']
		if dTF['Zoning__c'] == 'None' and d['zoning'] != 'None':
			dTF['Zoning__c'] = d['zoning']
		if d['propertyid'] != 'None':
			lPropertyIds.append(d['propertyid'])
	
	return dTF, lPropertyIds


# Check if Fox Hunter contact file exists
def contact_file_exists(search_string):
	"""
	Searches JSON file names in F:\Research Department\Code\Contact Files for a given string.
	Returns True if any JSON file name contains the string, False otherwise.
	"""
	folder_path = "F:/Research Department/Code/Contact Files"
	files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
	
	for file_name in files:
		if search_string.upper() in file_name.upper():
			return file_name
	
	return False

td.banner('TF Request Auto OwnerShip Generator v01')

# Get nested dictionary of Research Requests
print('\n Getting new Research Requests from TerraForce...')
# dRequests = bb.get_new_research_requests_nested_dict()

dRequests = {'RQ-105794':
				{'Approver__c': '0051300000Brlk1AAB',
				'Approver__r_Name': 'Nancy Surak',
				'CreatedDate': '2025-12-17T18:08:55.000+0000',
				'DID': 'None',
				'Description__c': 'Please add Lead FL_Pasco_572f2a to Terraforce and create an outline in the Ownerships layer.this is a future project - = very early FUTURE project called - Axiom/Sierra Farms aka Festival Parkplease add it to my regional map',
				'LID': 'FL_Pasco_572f2a',
				'MapTitle__c': 'L5 Lead Research FL_Pasco_572f2a',
				'Office__c': 'Tampa',
				'PID': 'None',
				'Parcel_Layer': 'None',
				'Parcels__c': 'None',
				'RecordTypeId': '0124X000001dVG6QAM',
				'Request_Id': 'a0QUT00000RsN4y2AF',
				'Request_Name': 'RQ-105794',
				'Request_Type': 'Lead Research',
				'Status__c': 'New'}
			}

# Cycle through each Research Requests
for row in dRequests:

	if dRequests[row]['Request_Type'] == 'Lead Research':

		print(row)
		pprint(dRequests[row])
		print('\n -------------------------\n')

		# Build dAcc and dTF dictionaries for the Lead
		dAcc, dTF = mpy.get_lead_info_dAcc_dTF_dicts(dRequests[row]['LID'])

		print('\n -------------------------\n')
		pprint(dAcc)
		print('\n -------------------------\n')

		dTF, lPropertyIds = get_lead_parcel_info_populate_dTF(dTF)
		pprint(dTF)
		print('\n -------------------------\n')

		# Check if Fox Hunter contact file exists
		contact_json_file = contact_file_exists(dAcc['ENTITY'])

		if contact_json_file == False:
			contacts_json_file = fh.create_ai_contacts_json(dAcc['ENTITY'], f"{dAcc['ADDRESSFULL']}")
			print(f" Created contact file for {dAcc['ENTITY']}")
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

		# Load json file
		print(contact_json_file)
		contact_file_path = os.path.join("F:/Research Department/Code/Contact Files", contact_json_file)
		with open(contact_file_path, 'r') as file:
			contact_data = json.load(file)
		pprint(contact_data)
		print('\n -------------------------\n')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

exit('\n Fin...')

# mpy.oi_make_from_parcel_propertyid(dTF='None', lPropertyIds='None')