

import acc
import bb
import datetime
import dicts
import fun_login
import fun_text_date as td
import fun_tf_account_finder as tfaf
import fun_fox_hunter as fh
import geopandas as gpd
import lao
import mpy
import os
import pandas as pd
from pprint import pprint
import webs


# Get Enitity ID (EID)
def get_entity_EID(service, dAcc):
	#####################################################
	# Check TF for existing Entity
	fh_results = 'None'
	EID = tfaf.main(service, dAcc, account_type='Entity')
	if EID != 'None':
		td.colorText(f' TerraForce Entity already exists with EID: {EID}', 'YELLOW')
	else:
		######################################################
		entity = dAcc['ENTITY']
		address = f"{dAcc['STREET']}, {dAcc['CITY']}, {dAcc['STATE']} {dAcc['ZIP']}"
		print(f'\n Owner: {entity}')
		print(f' Address: {address}')

		# Use Fox Hunter to get Entity and Contact details
		fh_results = fh.main(entity, address)

		if make_fox_hunter_file_only:
			td.warningMsg('\n No existing TerraForce Entity found. MADE FOX HUNTER FILE ONLY...')
			# If making Fox Hunter file only, return 'None' for EID
			EID = 'None'
			return EID, fh_results
		
		# Check if Fox Hunter found any companies
		if fh_results['companies']['primary'] is None:
			td.warningMsg('\n Fox Hunter did not find any companies for this owner.')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			return EID, fh_results

		# Add/Remove fields to match TerraForce Account object
		dAcc_fh_entity_primary = fh_results['companies']['primary']
		dAcc_fh_entity_primary['type'] = 'Account'
		del dAcc_fh_entity_primary['relationship_description']
		del dAcc_fh_entity_primary['relationship']
		# Add Created by Fox Hunter to Description
		if len(dAcc_fh_entity_primary['Description']) > 0:
			dAcc_fh_entity_primary['Description'] = dAcc_fh_entity_primary['Description'] + f'\nCreated by Fox Hunter on {datetime.date.today().isoformat()}'
		else:
			dAcc_fh_entity_primary['Description'] = f'Created by Fox Hunter on {datetime.date.today().isoformat()}'
		# TODO: Add routine to create Parent Enitity if it does exists

		# Create a temporary dAcc to check for existing Entity again
		dAcc_temp = dicts.get_blank_account_dict()
		dAcc_temp['ENTITY'] = dAcc_fh_entity_primary['Name']
		dAcc_temp['STREET'] = dAcc_fh_entity_primary['BillingStreet']
		dAcc_temp['CITY'] = dAcc_fh_entity_primary['BillingCity']
		dAcc_temp['STATE'] = dAcc_fh_entity_primary['BillingState']
		dAcc_temp['ZIP'] = dAcc_fh_entity_primary['BillingPostalCode']
		# Check for existing Entity again with updated dAcc
		EID = tfaf.main(service, dAcc_temp, account_type='Entity')
		if EID == 'None':
			print('\n Creating TerraForce Account...')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			EID = bb.tf_create_3(service, dAcc_fh_entity_primary)
			print(f'\n Created TerraForce Account with EID: {EID}')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

	return EID, fh_results

# Get Person ID (AID)
def get_person_AID(service, dAcc, EID, fh_results):

	lContacts = fh_results['contacts']
	# TODO: Handle if there are no contacts found
	for dAcc_person_primary in lContacts:
		print('\n Contact:')
		# pprint(dAcc_person_primary)
		if dAcc_person_primary['priority_rank'] == 1:
			dAcc_temp = dicts.get_blank_account_dict()
			dAcc_temp['NF'] = dAcc_person_primary['FirstName']
			dAcc_temp['NL'] = dAcc_person_primary['LastName']
			dAcc_temp['STREET'] = dAcc_person_primary['BillingStreet']
			dAcc_temp['CITY'] = dAcc_person_primary['BillingCity']
			dAcc_temp['STATE'] = dAcc_person_primary['BillingState']
			dAcc_temp['ZIP'] = dAcc_person_primary['BillingPostalCode']
			# Check for existing Entity again with updated dAcc
			AID = tfaf.main(service, dAcc_temp, account_type='Person')
			break
	if AID == 'None':
		print('\n Creating TerraForce Person Account...')
	
		if EID != 'None':
			dAcc_person_primary['Company__c'] = EID
		dAcc_person_primary['type'] = 'Account'
		del dAcc_person_primary['company_association']
		del dAcc_person_primary['priority_rank']
		# Add Created by Fox Hunter to Description
		if len(dAcc_person_primary['Description']) > 0:
			dAcc_person_primary['Description'] = dAcc_person_primary['Description'] + f'\nCreated by Fox Hunter on {datetime.date.today().isoformat()}'
		else:
			dAcc_person_primary['Description'] = f'Created by Fox Hunter on {datetime.date.today().isoformat()}'
		
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		AID = bb.tf_create_3(service, dAcc_person_primary)
		print(f'\n Created TerraForce Contact with AID: {AID}')
	
	return AID


td.banner('AI L5 Lead Spreadsheet Ownership Maker v01')

# Make Fox Hunter file only
while 1:
	ui = td.uInput('\n Make Fox Hunter file only? [0/1/00] > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		make_fox_hunter_file_only = True
		break
	elif ui == '0':
		make_fox_hunter_file_only = False
		break
	else:
		print('\n Invalid input...try again...')
		lao.sleep(1)

# Connect to Terraforce
service = fun_login.TerraForce()

# Load L5 Leads spreadsheet
dL5_Leads = dicts.spreadsheet_to_dict('C:/TEMP/Export (5).xlsx')

for row in dL5_Leads:
	r = dL5_Leads[row]
	leadid = r['leadid']
	print(f'\n Lead ID: {leadid}')

	# Check for existing Deals within 150 feet of Lead location
	lon = float(r['x'])
	lat = float(r['y'])
	deals = mpy.find_deals_in_extent(service, lon, lat)
	print(f"Found {len(deals)} deal(s) within 150 feet of the point:")
	if len(deals) > 0:
		for deal in deals:
			print(f"  PID: {deal.get('PID__c')} | Name: {deal.get('Name')} | Acres: {deal.get('Acres__c')}")
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
		# TODO: Add Ownership to the spreadsheet
		continue

	# Get Lead Info dicts
	dAcc, dTF, lParcel_PropertyID = mpy.get_lead_info_dAcc_dTF_dicts(leadid)
	if dAcc == {} and dTF == {}:
		continue
	print(lParcel_PropertyID)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	# pprint(dAcc)
	# print()
	# pprint(dTF)

		# Get Entity ID (EID)
	EID, fh_results = get_entity_EID(service, dAcc)
	# TODO: Handle if EID is 'None'
	# TODO: Handler Person contact if EID is not 'None' and fh_results is 'None'
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	
	# If making Fox Hunter file only, skip the rest
	if make_fox_hunter_file_only:
		continue

	# TODO Deal with Parcel__c field where the length is greater than 256 characters which means that it is truncated and not a list of all parcels.
	if len(dTF['Parcels__c']) >= 256:
		td.warningMsg('\n Lead Parcel__c field is too long and may be truncated.')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	
	# # Get Parcel propertyids
	# lParcels = dTF['Parcels__c'].split(',')
	# lParcel_PropertyID, dTF = mpy.get_parcel_propertyid(lParcels, dTF)

	# Find contact of an existing Entity
	AID = 'None'
	if EID != 'None' and fh_results == 'None':
		td.warningMsg('\n Existing Entity found but no Fox Hunter data available to find Contact.')
		dEmployees = acc.find_persons_of_entity(service, EID = EID, person = 'None', returnDict = True)
		print('\n Employees/Persons found for Entity in TF:')
		pprint(dEmployees)
		for emp in dEmployees:
			print(f"  Name: {emp['FirstName']} {emp['LastName']} | AID: {emp['Id']}")
			AID = emp['Id']
			# break
		# 
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

	# Get Person ID (AID)
	if AID == 'None':
		AID = get_person_AID(service, dAcc, EID, fh_results)

	# Add EID and AID to dTF
	dTF['Owner_Entity__c'] = EID
	dTF['AccountId__c'] = AID
	# dTF['OPR_Sent__c'] = datetime.date(1994, 10, 1)
	dTF['OPR_Sent__c'] = '1994-10-01'
	if len(dTF['State__c']) < 3:
		dTF['State__c'] = lao.convertState(dTF['State__c'])
	dTF = mpy.get_intersection_from_lon_lat(dTF=dTF, lon=0, lat=0, askManually=False, findAddress=False)
	# Deal Name
	if dTF['Subdivision__c'] != '':
		dTF['Name'] = f'{dTF["Subdivision__c"]} {dTF["Acres__c"]:.1f} Ac'
	if dTF['Location__c'] != '':
		dTF['Name'] = f'{dTF["Location__c"]} {dTF["Acres__c"]:.1f} Ac'
	elif dTF['Owner_Entity__c'] != '':
		dTF['Name'] = f'{dTF["Owner_Entity__r"]["Name"][:60]} {dTF["Acres__c"]:.1f} Ac'
	else:
		if dAcc['ENTITY'] != 'None' and dAcc['ENTITY'] != '':
			dTF['Name'] = f'{dAcc["ENTITY"][:60]} {dTF["Acres__c"]:.1f} Ac'
		else:
			dTF['Name'] = f'{dAcc["NF"]} {dAcc["NL"]} {dTF["Acres__c"]:.1f} Ac'
	# Add Created by Fox Hunter to Deal Description
	if len(dTF['Description__c']) > 0:
		dTF['Description__c'] = dTF['Description__c'] + f'\nCreated by Fox Hunter on {datetime.date.today().isoformat()}'
	else:
		dTF['Description__c'] = f'Created by Fox Hunter on {datetime.date.today().isoformat()}'
	
	print('here2')
	print(f' LeadID: {leadid}')
	print(' ### dTF with added Ownership fields ### ')
	pprint(dTF)
	print('\n Pause here to inspect dTF with added Ownership fields...')
	ui = td.uInput('\n Continue to create PID [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	
	# Create TF Deal record ###############################################
	DID = bb.tf_create_3(service, dTF)
	dTF['Id'] = DID
	dTF['PID__c'] = bb.getPIDfromDID(service, DID)

	webs.open_pid_did(service, DID)
	print(f'\n Created TerraForce Deal with DealID: {DID} and PID: {dTF["PID__c"]}')
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

	# Create Ownership polygon ###########################################
	mpy.oi_make_from_parcel_propertyid(dTF, lParcel_PropertyID)
	print(f'\n Created Ownership polygon from list of parcels')
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
exit()

