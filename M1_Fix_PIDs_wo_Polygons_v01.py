import bb
import csv
import dicts
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
import os
from pprint import pprint
import webs
from symbols import SUCCESS, ERROR, INFO, WARNING

def find_matches(dTF):
	# TerraForce Query
	fields = 'default'
	wc = "PID__c <> '{0}' and Lead_Parcel__c = '{1}' and County__c = '{2}'".format(dTF['PID__c'], dTF['Lead_Parcel__c'], dTF['County__c'])
	if dTF['Owner_Entity__c'] != 'None':
		wc = "{0} and Owner_Entity__c = '{1}'".format(wc, dTF['Owner_Entity__c'])
	if dTF['AccountId__c'] != 'None':
		wc = "{0} and AccountId__c = '{1}'".format(wc, dTF['AccountId__c'])
	
	match_results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	if len(match_results) > 1:
		print(f'\n Found matches for {dTF["PID__c"]}')
		for match in match_results:
			print(f' Match PID: {match["PID__c"]}\n Parcel: {match["Lead_Parcel__c"]}\n Created: {match["CreatedDate"]}\n')
	else:
		print(f'\n No matches found for {dTF["PID__c"]}\n')

td.banner('M1 Fix PIDs without Polygons v01')
service = fun_login.TerraForce()
gis = fun_login.LAO_ArcGIS_portal()
today_date = td.today_date(include_time=True)
dStateAbbr = dicts.get_state_abbriviations_dict()

# TerraForce Query
fields = 'default'
wc = f"Market__c = '' and CreatedDate >= 2023-01-01T00:00:00Z and (NOT PID__c LIKE '%MarketingGroup%') and RecordTypeId <> '01213000001CFArAAO'"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

with open(r'C:\TEMP\Missing OI Poly.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow([ 'Has Poly','PID', 'Market', 'Created Date', 'State', 'County', 'Parcels'])
	for row in results:

		td.banner('M1 Fix PIDs without Polygons v01')
		
		# Get state abbreviation
		for key, value in dStateAbbr.items():
			if value == row.get('State__c'):
				state_abbr = key
				break

		# Check if OI poly exists
		if mpy.get_OID_from_PID(row.get('PID__c'), gis=gis) is None:
			writer.writerow(['No', row.get('PID__c'), row.get('Market__c'), row.get('CreatedDate'), state_abbr, row.get('County__c'), row.get('Parcels__c')])
						
			# Make ArcMap parcel layer name
			polyinlayer = f'{state_abbr}Parcels{row.get("County__c")}'
			polyId = row.get('Parcels__c').split(',')[0].strip()

			# Make Zoom to Polygon Json file
			fjson.create_ZoomToPolygon_json_file(fieldname='apn', polyId=polyId, polyinlayer=polyinlayer, lon=row.get('Longitude__c'), lat=row.get('Latitude__c'), market=None)

			# Open PID in TerraForce
			webs.open_pid_did(service, row.get('PID__c'))

			print(f'\n PID:     {row.get("PID__c")}')
			print(f' Deal:    {row.get("Name")}')
			print(f' APNs:    {row.get("Parcels__c")}')
			print(f' Acres:   {row.get("Acres__c")}')
			print(f' Created: {row.get("CreatedDate")}\n')

			EID = 'None'
			AID = 'None'
			if (row.get("Owner_Entity__c") != 'None'):
				EID = row.get("Owner_Entity__c")
				print(f' Entity: {row.get("Owner_Entity__r", {}).get("Name")}')
			if (row.get("AccountId__c") != 'None'):
				AID = row.get("AccountId__c")
				print(f' Person: {row.get("AccountId__r", {}).get("Name")}')
			
			find_matches(row)

			print(f'\n Options:\n')
			print('  [Enter] Continue to next')
			print('  1) Safe PID Delete')
			print(' 00) Quit')
			ui = td.uInput('\n Select > ')
			if ui == '00':
				exit('\n Terminating program...')
			elif ui == '1':
				# Create Zoom to Polygon Json file
				fjson.create_ZoomToPolygon_json_file(fieldname='pid', polyId=row.get('PID__c'), polyinlayer='OwnerIndex', lon=row.get('Longitude__c'), lat=row.get('Latitude__c'), market=None)
				os.system('python "F:/Research Department/Code/RP3/M1_Safe_PID_Delete_v01.py"')
		else:
			writer.writerow(['Yes', row.get('PID__c'), row.get('Market__c'), row.get('CreatedDate'), state_abbr, row.get('County__c'), row.get('Parcels__c')])

lao.openFile(r'C:\TEMP\Missing OI Poly.csv')

exit(' Fin...')