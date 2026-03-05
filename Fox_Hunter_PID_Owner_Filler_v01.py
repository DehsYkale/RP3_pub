
import acc
import bb
import dicts
import fox_hunter as fh
import fun_login
import fun_text_date as td
import lao
import os
from pprint import pprint


def check_contact_file_exists(entity_name):
	"""Check Contact Files folder for an existing Fox Hunter JSON for this entity."""
	folder_path = "F:/Research Department/Code/Contact Files"
	files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
	for file_name in files:
		if entity_name.upper() in file_name.upper():
			return file_name
	return False


# =============================================================================
# MAIN
# =============================================================================

td.banner('Fox Hunter PID Owner Filler v01')

service = fun_login.TerraForce()

PID = td.uInput('\n Enter PID [00] > ').strip()
if PID == '00' or PID == '':
	exit('\n Terminating program...')

# ------------------------------------------------------------------
# Query TF deal
# ------------------------------------------------------------------
print(f'\n Querying TerraForce for PID: {PID}...')
wc      = f"PID__c = '{PID}'"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields='default')

if not results:
	td.warningMsg(f'\n PID {PID} not found in TerraForce.')
	exit('\n Terminating program...')

deal = results[0]
DID  = deal['Id']

# ------------------------------------------------------------------
# Display current field values
# ------------------------------------------------------------------
entity_name   = deal['Owner_Entity__r']['Name']        if deal['Owner_Entity__c'] != 'None' else '(blank)'
entity_street = deal['Owner_Entity__r']['BillingStreet'] if deal['Owner_Entity__c'] != 'None' else 'None'
person_name   = deal['AccountId__r']['Name']           if deal['AccountId__c']    != 'None' else '(blank)'
person_street = deal['AccountId__r']['BillingStreet']  if deal['AccountId__c']    != 'None' else 'None'
person_city   = deal['AccountId__r']['BillingCity']    if deal['AccountId__c']    != 'None' else 'None'
person_state  = deal['AccountId__r']['BillingState']   if deal['AccountId__c']    != 'None' else 'None'
person_zip    = deal['AccountId__r']['BillingPostalCode'] if deal['AccountId__c'] != 'None' else 'None'

print(f'\n PID:          {PID}')
print(f' Owner Entity: {entity_name}')
print(f' Account Name: {person_name}')

# ------------------------------------------------------------------
# Determine which fields need filling
# ------------------------------------------------------------------
needs_entity = deal['Owner_Entity__c'] in ('None', '', None)
needs_person = deal['AccountId__c']    in ('None', '', None)

if not needs_entity and not needs_person:
	td.colorText('\n Both Owner Entity and Account Name are already populated. Nothing to do.', 'GREEN')
	exit('\n Fin...')

print('\n Fields to fill:')
if needs_entity:
	td.warningMsg('   - Owner Entity')
if needs_person:
	td.warningMsg('   - Account Name')

# ------------------------------------------------------------------
# Determine Fox Hunter search input:
#   1. Owner Entity if it has a billing address
#   2. Otherwise fall back to Account Name
# ------------------------------------------------------------------
fh_name    = 'None'
fh_address = 'None'

if deal['Owner_Entity__c'] != 'None' and entity_street not in ('None', '', None):
	# Owner Entity exists and has an address — use it
	fh_name    = entity_name
	fh_address = '{0}, {1}, {2} {3}'.format(
		entity_street,
		deal['Owner_Entity__r']['BillingCity'],
		deal['Owner_Entity__r']['BillingState'],
		deal['Owner_Entity__r']['BillingPostalCode'])
	print(f'\n Using Owner Entity as Fox Hunter input:')
	print(f'   Name:    {fh_name}')
	print(f'   Address: {fh_address}')

elif deal['AccountId__c'] != 'None':
	# No Owner Entity with address — fall back to Account Name
	fh_name    = person_name
	fh_address = '{0}, {1}, {2} {3}'.format(
		person_street, person_city, person_state, person_zip)
	print(f'\n No Owner Entity address found. Using Account Name as Fox Hunter input:')
	print(f'   Name:    {fh_name}')
	print(f'   Address: {fh_address}')

else:
	td.warningMsg('\n No Owner Entity address or Account Name found on this deal.')
	td.warningMsg(' Cannot determine Fox Hunter search input. Terminating.')
	exit('\n Terminating program...')

# Populate dAcc from Fox Hunter input
dAcc              = dicts.get_blank_account_dict()
dAcc['ENTITY']    = fh_name
dAcc['ADDRESSFULL'] = fh_address

# ------------------------------------------------------------------
# Run Fox Hunter (or use existing file)
# ------------------------------------------------------------------
print('\n Checking for existing Fox Hunter contact file...')
contact_json_file = check_contact_file_exists(dAcc['ENTITY'])

if contact_json_file:
	td.colorText(f'\n Existing Fox Hunter file found: {contact_json_file}', 'GREEN')
else:
	print(f'\n Running Fox Hunter for: {dAcc["ENTITY"]}...')
	contact_json_file = fh.create_ai_contacts_json(dAcc['ENTITY'], dAcc['ADDRESSFULL'])
	if contact_json_file:
		td.colorText(f'\n Fox Hunter complete. File: {contact_json_file}', 'GREEN')
	else:
		td.warningMsg('\n Fox Hunter did not produce a result file. Continuing with existing name only.')

ui = td.uInput('\n Continue to find/create TF accounts [00] > ')
if ui == '00':
	exit('\n Terminating program...')

# ------------------------------------------------------------------
# Find / Create accounts in TF
# ------------------------------------------------------------------
dUpdate = dicts.get_blank_deal_update_dict(DID)

if needs_entity:
	print('\n Finding / Creating Owner Entity in TerraForce...')
	dAcc = acc.find_create_account_entity(service, dAcc)
	if dAcc['EID'] != 'None':
		dUpdate['Owner_Entity__c'] = dAcc['EID']
		td.colorText(f'\n Owner Entity: {dAcc["ENTITY"]}  ({dAcc["EID"]})', 'GREEN')
	else:
		td.warningMsg('\n No Entity ID obtained — Owner Entity will not be updated.')

if needs_person:
	print('\n Finding / Creating Account Name in TerraForce...')
	_name, _aid, dAcc = acc.find_create_account_person(service, dAcc)
	if dAcc['AID'] != 'None':
		dUpdate['AccountId__c'] = dAcc['AID']
		td.colorText(f'\n Account Name: {dAcc["NAME"]}  ({dAcc["AID"]})', 'GREEN')
	else:
		td.warningMsg('\n No Account ID obtained — Account Name will not be updated.')

# ------------------------------------------------------------------
# Confirm and update
# ------------------------------------------------------------------
td.banner('Fox Hunter PID Owner Filler v01')
td.warningMsg(' CONFIRM UPDATE')
print(f'\n PID: {PID}')
if needs_entity:
	print(f' Owner Entity: {dAcc.get("ENTITY", "(not set)")}')
if needs_person:
	print(f' Account Name: {dAcc.get("NAME", "(not set)")}')

ui_confirm = td.uInput(f'\n Update PID {PID}? [1=Yes / 0=No / 00=Quit] > ')
if ui_confirm == '00':
	exit('\n Terminating program...')
elif ui_confirm == '1':
	results = bb.tf_update_3(service, dUpdate)
	td.colorText(f'\n PID {PID} updated successfully.', 'GREEN')
else:
	print('\n Update cancelled.')

exit('\n Fin...')
