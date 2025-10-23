
import acc
import aws
import datetime
import bb
import dicts
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
import os
from pprint import pprint

import re

# Check if the files were made recently
def check_if_files_current():
	is_recent = False
	while is_recent is False:
		td.banner('M1 Deal Updater v01')
		is_recent = aws.was_file_modified_recently()
		if is_recent is False:
			td.warningMsg('\n Selected parcels are not current.\n\n Click Save Parcels in M1 and Continue.')
			ui = td.uInput('\n Continue [00] > ')
			if ui == '00':
				exit('\n Terminating program...')

# Get the user who is logged in
def get_creator_modifier(dOwnShp_results):
	# Get the record creator, owner and last modifier
	for staff in dStaff:
		if dStaff[staff]['UserID'] in dOwnShp_results['CreatedById']:
			rec_creator = '{0} ({1})'.format(staff, dStaff[staff]['Roll'])
		if dStaff[staff]['UserID'] in dOwnShp_results['OwnerId']:
			rec_owner = '{0} ({1})'.format(staff, dStaff[staff]['Roll'])
		if dStaff[staff]['UserID'] in dOwnShp_results['LastModifiedById']:
			rec_modifier = '{0} ({1})'.format(staff, dStaff[staff]['Roll'])
			
	return rec_creator, rec_owner, rec_modifier

# Address comparison function
def compare_addresses(addr1, addr2):
	# Define a regex pattern to match starting digits
	pattern = r'^\d+'
	
	# Use regex to find the starting digits
	match1 = re.match(pattern, addr1)
	match2 = re.match(pattern, addr2)
	
	# Check if both addresses start with digits
	if match1 and match2:
		# Extract the digits
		digits1 = match1.group()
		digits2 = match2.group()
		
		# Compare the digits
		return digits1 == digits2
	else:
		# If either address doesn't start with digits, return False
		return False

# Check if the deal has been modified or is unchanged (Steve Simpson (IT), Ethan Granger (Research), Julio Mejia (IT)
def check_for_unchanged_deals(rec_creator, rec_owner, rec_modifier):
	# Check if the deal has been modified
	bCreator, bOwner, bModifier = False, False, False
	if rec_creator == 'Steve Simpson (IT)':
		bCreator = True
	if rec_owner == 'Steve Simpson (IT)' or rec_owner == 'Ethan Granger (Research)':
		bOwner = True
	if rec_modifier == 'Ethan Granger (Research)' or rec_modifier == 'Julio Mejia (IT)':
		bModifier = True
	if bCreator and bOwner and bModifier:
		return True
	else:
		return False

# Compare the owner names and highlight the match
def compare_deal_owner_names(dOwnShp_vals, Par_name):
	# Compare the owner names
	if dOwnShp_vals['entity'] == Par_name:
		return 'Entity Match'
	elif dOwnShp_vals['person'] == Par_name:
		return 'Person Match'
	else:
		return 'No Match'

# Print the information
def print_info():

	# Get the record creator, owner and last modifier
	rec_creator, rec_owner, rec_modifier = get_creator_modifier(dOwnShp_results)
	rec_created_date = td.date_engine(dOwnShp_results['CreatedDate'], 'dash', 'iso')
	rec_modified_date = td.date_engine(dOwnShp_results['LastModifiedDate'], 'dash', 'iso')

	td.banner('M1 Deal Updater v01')
	# Check if streets or owner names match and if the deal has been modified
	do_streets_match = compare_addresses(dOwnShp_vals['street'], Par_street)
	is_deal_unchanged = check_for_unchanged_deals(rec_creator, rec_owner, rec_modifier)
	deal_owner_name_match = compare_deal_owner_names(dOwnShp_vals, Par_name)

	if is_deal_unchanged:
		td.colorText((f'\n PID:      {PID:40}  UNCHANGED'), 'YELLOW')
	else:
		td.colorText(f'\n PID:      {PID:40}  MODIFIED', 'CYAN')

	print(f' Creator:  {rec_creator:40}  {rec_created_date}')
	print(f' Modifier: {rec_modifier:40}  {rec_modified_date}')
	print(f' Owner:    {rec_owner:40}')

	title1, title2 = 'OWNERSHIP', 'PARCEL'
	print(f'\n           {title1:40}  {title2}')
	if deal_owner_name_match == 'Entity Match':
		td.colorText(f' Name:     {dOwnShp_vals['entity'][:35]:40}  {Par_name[:35]}', 'GREEN')
	else:
		print(f' Name:     {dOwnShp_vals['entity'][:35]:40}  {Par_name[:35]}')
	if deal_owner_name_match == 'Person Match':
		td.colorText(f' Person:   {dOwnShp_vals['person'][:35]:40}  {Par_name[:35]}', 'GREEN')
	else:
		print(f' Person:   {dOwnShp_vals['person'][:35]:40}  {Par_name[:35]}\n')
	if do_streets_match:
		td.colorText(f' Street:   {dOwnShp_vals['street'][:35]:40}  {Par_street[:35]}', 'GREEN')
	else:
		td.colorText(f' Street:   {dOwnShp_vals['street'][:35]:40}  {Par_street[:35]}', 'YELLOW')
	print(f' Phone:    {dOwnShp_vals['phone'][:35]:40}')
	print(f' Email:    {dOwnShp_vals['email'][:35]:40}')

# Reset the Verified field to False for the PID
# Must be done before updating the Deal bc it needs to be False to update
def reset_verified(DID):
	dVerified_off = {
		'type': 'lda_Opportunity__c',
		'Verified__c': False,
		'Id': DID
	}
	results = bb.tf_update_3(service, dVerified_off)

# Build teh dUpdate dictionary
def build_dUpdate_dict(dTF, dAcc, dUpdate):
	dUpdate['Acres__c'] = dTF['Acres__c']
	dUpdate['City__c'] = dTF['City__c']
	dUpdate['County__c'] = dTF['County__c']
	dUpdate['Latitude__c'] = dTF['Latitude__c']
	dUpdate['Longitude__c'] = dTF['Longitude__c']
	dUpdate['Lead_Parcel__c'] = dTF['Lead_Parcel__c']
	dUpdate['Parcels__c'] = dTF['Parcels__c']
	dUpdate['State__c'] = dTF['State__c']
	dUpdate['Zipcode__c'] = dTF['Zipcode__c']
	if dTF['Zoning__c'] != 'None':
		dUpdate['Zoning__c'] = dTF['Zoning__c']
	return dUpdate

# Main Program

td.banner('M1 Deal Updater v02')

service = fun_login.TerraForce()
user = lao.getUserName()

# Check if the files were made recently
check_if_files_current()

# Set up the dictionaries
dStaff = dicts.get_staff_dict(dict_type='full', skipFormerEmployees=False)
dAcc = dicts.get_blank_account_dict()
dBS = dicts.get_blank_buyer_seller_dict()
dTF = dicts.get_blank_tf_deal_dict()
dOwnShp_vals = dicts.get_m1_deal_updater_owner_dict() # Ownership values dict
dZoom_To_Polygon = fjson.getJsonDict('C:/Users/Public/Public Mapfiles/M1_Files/zoomToPolygon.json')

# Get PID & DID
PID, dTF['PID__c'] = dZoom_To_Polygon['polyId'], dZoom_To_Polygon['polyId']
DID = bb.getDIDfromPID(service, PID)
dUpdate = dicts.get_blank_deal_update_dict(DID)
# Get the parcel data and have user choose the parcel to use')
dAcc, dTF, lPropertyIds = mpy.get_parcel_data(dAcc, dTF)

# Add dTF values to dUpdate
dUpdate['Acres__c'] = dTF['Acres__c']
dUpdate['City__c'] = dTF['City__c']
dUpdate['County__c'] = dTF['County__c']
dUpdate['Latitude__c'] = dTF['Latitude__c']
dUpdate['Longitude__c'] = dTF['Longitude__c']
dUpdate['Lead_Parcel__c'] = dTF['Lead_Parcel__c']
dUpdate['Parcels__c'] = dTF['Parcels__c']
dUpdate['State__c'] = dTF['State__c']
dUpdate['Zipcode__c'] = dTF['Zipcode__c']
if dTF['Zoning__c'] != 'None':
	dUpdate['Zoning__c'] = dTF['Zoning__c']


# TerraForce Query
fields = 'default'
wc = f"PID__c = '{PID}'"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
dOwnShp_results = results[0] # Ownership query of PID results

# Check if the PID is a sale and exit if it is
if dOwnShp_results['StageName__c'] != 'Lead':
	td.warningMsg(f'\n PID {PID} is a Sale and cannot be updated.\n\n Terminating program...')
	ui = td.uInput('\n Continue > ')
	exit()

# Assign Ownership Entity Info (OS)
if dOwnShp_results['Owner_Entity__c'] != 'None':
	# pprint(dOwnShp_results['Owner_Entity__r'])
	dOwnShp_vals['entity'] = dOwnShp_results['Owner_Entity__r']['Name']
	dOwnShp_vals['street'] = dOwnShp_results['Owner_Entity__r']['BillingStreet']
	dOwnShp_vals['phone'] = dOwnShp_results['Owner_Entity__r']['Phone']

# Assign Ownership Person Info (OS)
if dOwnShp_results['AccountId__c'] != 'None':
	dOwnShp_vals['person'] = dOwnShp_results['AccountId__r']['Name']
	dOwnShp_vals['email'] = dOwnShp_results['AccountId__r']['PersonEmail']
	if dOwnShp_vals['street'] == 'None':
		dOwnShp_vals['street'] = dOwnShp_results['AccountId__r']['BillingStreet']
	if dOwnShp_vals['phone'] == 'None':
		dOwnShp_vals['phone'] = dOwnShp_results['AccountId__r']['Phone']

# Assign Parcel Info (Par)
Par_name = dAcc['ENTITY']
Par_street = dAcc['STREET']

td.banner('M1 Deal Updater v02')

# Assign Clasification if None
if dOwnShp_results['Classification__c'] != 'None':
	print(f' Classification: {dOwnShp_results['Classification__c']}')
	ui = td.uInput('\n Update Classification? [0/1/00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		dOwnShp_results['Classification__c'] = 'None'
	else:
		print(f"\n Keeping Classification: {dOwnShp_results['Classification__c']}")

if dOwnShp_results['Classification__c'] == 'None':
	# Reset Lot Type to None
	dTF['Lot_Type__c'] = 'None'
	dTF, startover = lao.select_from_list(dTF, 'Classification__c')
	dTF, startover = lao.select_from_list(dTF, 'Lot_Type__c')
	dUpdate['Classification__c'] = dTF['Classification__c']
	dUpdate['Lot_Type__c'] = dTF['Lot_Type__c']

# Assign Lot Type if None
if dOwnShp_results['Lot_Type__c'] == 'None' and dUpdate['Lot_Type__c'] == 'None':
	dTF, startover = lao.select_from_list(dTF, 'Lot_Type__c')
	dUpdate['Lot_Type__c'] = dTF['Lot_Type__c']


# Get Location if it is None or '.'
if dOwnShp_results['Location__c'] == '.' or dOwnShp_results['Location__c'] == 'None':
	dTF = mpy.get_intersection_from_lon_lat(dTF)
	dUpdate['Location__c'] = dTF['Location__c']

print('here1')
pprint(dTF)
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')

# Update the Deal Owner

# Print the information
update_poly = True
print_info()

print('\n  1) Owner is Correct')
print('  2) Update the Owner')
print('  3) Skip Owner Update')
print(' 00) Quit')
ui = td.uInput('\n Select > ')
if ui == '00':
	exit('\n Terminating program...')
elif ui == '1':
	# pprint(dUpdate)
	reset_verified(DID)
	results = bb.tf_update_3(service, dUpdate)
	td.colorText(f'\n PID {PID} verified...', 'GREEN')
	# ui = td.uInput('\n Continue... > ')
elif ui == '2':
	print('\n Updating Owner...')

	# Add/Get Entity and Person IDs
	dAcc = acc.find_create_account_entity(service, dAcc)
	temp1, temp2, dAcc = acc.find_create_account_person(service, dAcc)

	# Confirm the update
	td.banner('M1 Deal Updater v01')
	td.warningMsg(' COMFIRM UPDATE')
	title1, title2 = 'UPDATED OWNER', 'EXISTING OWNER'
	print(f'\n        {title1:40}  {title2}')
	print(f'Name:   {dAcc['ENTITY']:40}  {dOwnShp_vals['entity']}')
	print(f'Person: {dAcc['NAME']:40}  {dOwnShp_vals['person']}')
	ui_confirm = td.uInput(f'\n Update PID {PID} [0/1/00] > ')
	if ui_confirm == '00':
		exit('\n Terminating program...')
	elif ui_confirm == '1':
		# Update the Deal Owner
		dUpdate['Owner_Entity__c'] = dAcc['EID']
		dUpdate['AccountId__c'] = dAcc['AID']
		reset_verified(DID)
		
		results = bb.tf_update_3(service, dUpdate)
		td.colorText(f'\n PID {PID} updated...', 'GREEN')
	else:
		print('\n Skipping Owner Update...')
		ui = td.uInput('\n Continue... > ')
		update_poly = False
else:
	print('\n Skipping Owner Update...')
	ui = td.uInput('\n Continue... > ')
	update_poly = False

# Update the OwnerIndex Poly
if update_poly:
	# Delete the existing OwnerIndex Poly
	delete_poly_results = mpy.oi_delete_poly(PID)
	# Create the new OwnerIndex Poly
	if delete_poly_results:
		dUpdate['PID__c'] = PID
		mpy.oi_make_from_parcel_propertyid(dUpdate, lPropertyIds)








