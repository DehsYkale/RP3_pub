

import ai
import bb
import fun_login
import dicts
import fun_fox_hunter as fh
import fun_text_date as td
import fun_tf_account_finder as tfaf
import lao
import mpy
from pprint import pprint
import datetime

# Check for existing Ownership base on lon/lat of Lead
def existing_ownership_exists(service, lon, lat):
	lao.print_function_name(' internal - existing_ownership_exists')

	deals = mpy.find_deals_in_extent(service, lon, lat)
	print(f"\n Found {len(deals)} deal(s) within 150 feet of the point:")
	if len(deals) > 0:
		for deal in deals:
			print(f"  PID: {deal.get('PID__c')} | Name: {deal.get('Name')} | Acres: {deal.get('Acres__c')}")

		# 	# Updateing OPR_Sent__c field to 1994-10-01
		# 	dup = {'Id': deal.get('Id'), 'OPR_Sent__c': '1994-10-01', 'type': 'lda_Opportunity__c'}
		# 	bb.tf_update_3(service, dup)
		# 	print(f"  Updated OPR_Sent__c field for Deal ID: {deal.get('Id')}")

		# TODO: Add Ownership to the spreadsheet
		return True
	return False

# Get Person ID (AID)
def get_person_AID(service, dAcc, EID, fh_results):
	lao.print_function_name(' internal - get_person_AID')

	lContacts = fh_results['contacts']
	AID_primary = 'None'
	# TODO: Handle if there are no contacts found
	for dPerson in lContacts:
		print('\n Contact:')
		# pprint(dPerson)
		dAcc_temp = dicts.get_blank_account_dict()
		dAcc_temp['NF'] = dPerson['FirstName']
		dAcc_temp['NL'] = dPerson['LastName']
		dAcc_temp['STREET'] = dPerson['BillingStreet']
		dAcc_temp['CITY'] = dPerson['BillingCity']
		dAcc_temp['STATE'] = dPerson['BillingState']
		dAcc_temp['ZIP'] = dPerson['BillingPostalCode']
		dAcc_temp['PHONE'] = dPerson['Phone']
		dAcc_temp['MOBILE'] = dPerson['PersonMobilePhone']
		dAcc_temp['EMAIL'] = dPerson['PersonEmail']

		
		print('here7')
		pprint(dAcc_temp)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		

		# Check for existing Entity again with updated dAcc
		AID = tfaf.main(service, dAcc_temp, account_type='Person')
		print('here1')
		print(f"Found AID: {AID} for contact {dPerson['FirstName']} {dPerson['LastName']}")
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
			
		# No existing Person found in TF, create new Person
		if AID == 'None':
			print('\n Creating TerraForce Person Account...')
		
			# Delete unnecessary fields from fh_results contact dict before creating TF Person Account
			for key in ('company_association', 'priority_rank', 'enrichment_attempted', 'enrichment_source', 'PhoneSource', 'MobileSource'):
				dPerson.pop(key, None)

			dPerson['type'] = 'Account'
			if EID != 'None':
				dPerson['Company__c'] = EID

			# Add Created by Fox Hunter to Description
			if len(dPerson['Description']) > 0:
				dPerson['Description'] = dPerson['Description'] + f'\nCreated by Fox Hunter on {datetime.date.today().isoformat()}'
			else:
				dPerson['Description'] = f'Created by Fox Hunter on {datetime.date.today().isoformat()}'
			
			# Format the Person Name and address
			dPerson['FirstName'] = dPerson['FirstName'].title()
			dPerson['MiddleName__c'] = dPerson['MiddleName__c'].title()
			dPerson['LastName'] = dPerson['LastName'].title()
			dPerson = td.address_formatter(dPerson)

			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			AID = bb.tf_create_3(service, dPerson)
			print(f'\n Created TerraForce Contact with AID: {AID}')
		else:
			print(f'\n Found existing TerraForce Contact with AID: {AID}')
		
		if AID_primary == 'None':
			AID_primary = AID
	
	return AID_primary

td.banner('FH Contact Maker Leads Parcels PIDs v01')

# Login to TerraForce and get ESRI token
service = fun_login.TerraForce()
token = mpy.get_arcgis_token()

lStatesAbb = lao.getCounties('StateAbb')
county, state, apn, PID, LeadId = 'None', 'None', 'None', 'None', 'None'

td.banner('FH Contact Maker Leads Parcels PIDs v01')

# User enters either Lead ID, APN with State and County, or PID to create contact from. The program will determine the source type based on the format of the input and then query for the necessary information to create the contact in TerraForce.
while 1:
	ui = td.uInput(' Enter Lead, APN or PID [00] > ')

	if '_' in ui:
		LeadId = ui
		source_type = 'Lead'
		break
	elif ui[:2] in lStatesAbb:
		PID = ui
		source_type = 'PID'
		break
	elif ui == '00':
		exit('\n Terminating program...')
	else:
		apn = ui
		state = td.uInput(' Enter State abbreviation (e.g. FL) [00] > ')
		if state == '00':
			exit('\n Terminating program...')
		county = td.uInput(' Enter County name (e.g. Lake) [00] > ')
		if county == '00':
			exit('\n Terminating program...')
		source_type = 'Parcel'
		break

# Source type can be Lead, Parcel or PID. This will determine how we query for the initial information and how we create the dAcc, dTF and lPropertyids structures.

if source_type == 'Parcel':
	# Parcel source info
	dAcc, dTF, lPropertyids = mpy.get_parcel_info_dAcc_dTF_dicts(token, apn, state, county)
elif source_type == 'Lead':
	# Lead source info
	dAcc, dTF, lPropertyids = mpy.get_lead_info_dAcc_dTF_dicts(token, LeadId)
elif source_type == 'PID':
	exit()
	# PID source info
	# dAcc, dTF, lPropertyids = mpy.get_pid_info_dAcc_dTF_dicts(token, LeadId)


# # Check for existing Ownership base on lon/lat of Lead (TF lon/lat fields are text, so we need to convert them to numeric first)
# results = existing_ownership_exists(service, dTF['Longitude__c'], dTF['Latitude__c'])
# print(f"Existing ownership exists: d{results}")

# if results:
# 	print("\n Ownership already exists for this lead. No further action needed.")
# 	exit()


# print('\n dAcc #########################################################')
# pprint(dAcc)
# print('\n dTF ##########################################################')
# pprint(dTF)
# print('\n lPropertyids ################################################')
# pprint(lPropertyids)

# print('\n Next Up fh.get_entity_EID() #####################################')
# ui = td.uInput('\n Continue [00]... > ')
# if ui == '00':
# 	exit('\n Terminating program...')

dAcc['EID'], fh_results = fh.get_entity_EID(service, dAcc)

dAcc['AID'] = get_person_AID(service, dAcc, dAcc['EID'], fh_results)

print(f'\n dAcc EID {dAcc["EID"]}')
print(f'\n dAcc AID {dAcc["AID"]}')

exit()
