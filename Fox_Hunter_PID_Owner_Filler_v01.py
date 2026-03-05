
import bb
import dicts
import fjson
import fox_hunter as fh
import fun_login
import fun_text_date as td
import json
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


def is_blank(val):
	return val in ('None', '', None)


def select_fh_contact(contacts, person_name):
	"""Display FH contacts and have user select one to apply to the Account Name record."""
	print('\n Fox Hunter Contacts Found:')
	print(' [ 0] Skip — do not update Account Name contact info')
	for i, c in enumerate(contacts, 1):
		name  = f"{c.get('FirstName', '')} {c.get('LastName', '')}".strip()
		phone = c.get('Phone', 'None')
		email = c.get('PersonEmail', 'None')
		print(f' [{i:>2}] {name:30.30}  Ph: {phone:20.20}  Email: {email}')

	while 1:
		ui = td.uInput(f'\n Select contact to use for Account Name [{person_name}] [0-{len(contacts)}/00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		try:
			idx = int(ui)
		except ValueError:
			td.warningMsg(' Enter a number.')
			continue
		if 0 <= idx <= len(contacts):
			break
		td.warningMsg(' Invalid selection.')

	return contacts[idx - 1] if idx > 0 else None


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
# Collect current field values from linked records
# ------------------------------------------------------------------
has_entity = not is_blank(deal['Owner_Entity__c'])
has_person = not is_blank(deal['AccountId__c'])

entity_name   = deal['Owner_Entity__r']['Name']           if has_entity else 'None'
entity_street = deal['Owner_Entity__r']['BillingStreet']  if has_entity else 'None'
entity_city   = deal['Owner_Entity__r']['BillingCity']    if has_entity else 'None'
entity_state  = deal['Owner_Entity__r']['BillingState']   if has_entity else 'None'
entity_zip    = deal['Owner_Entity__r']['BillingPostalCode'] if has_entity else 'None'
entity_phone  = deal['Owner_Entity__r']['Phone']          if has_entity else 'None'

person_name   = deal['AccountId__r']['Name']              if has_person else 'None'
person_phone  = deal['AccountId__r']['Phone']             if has_person else 'None'
person_mobile = deal['AccountId__r']['PersonMobilePhone'] if has_person else 'None'
person_email  = deal['AccountId__r']['PersonEmail']       if has_person else 'None'

EID = deal['Owner_Entity__c'] if has_entity else 'None'
AID = deal['AccountId__c']    if has_person else 'None'

# ------------------------------------------------------------------
# Display current state
# ------------------------------------------------------------------
print(f'\n PID: {PID}')
print(f'\n {"OWNER ENTITY":25} {entity_name}')
print(f'   {"Phone:":23} {entity_phone}')
print(f'\n {"ACCOUNT NAME:":25} {person_name}')
print(f'   {"Phone:":23} {person_phone}')
print(f'   {"Mobile:":23} {person_mobile}')
print(f'   {"Email:":23} {person_email}')

# ------------------------------------------------------------------
# Determine which fields need filling
# ------------------------------------------------------------------
needs_entity_phone  = has_entity and is_blank(entity_phone)
needs_person_phone  = has_person and is_blank(person_phone)
needs_person_mobile = has_person and is_blank(person_mobile)
needs_person_email  = has_person and is_blank(person_email)

if not any([needs_entity_phone, needs_person_phone, needs_person_mobile, needs_person_email]):
	td.colorText('\n All phone/email fields are already populated. Nothing to do.', 'GREEN')
	exit('\n Fin...')

print('\n Fields to fill:')
if needs_entity_phone:
	td.warningMsg('   - Owner Entity Phone')
if needs_person_phone:
	td.warningMsg('   - Account Name Phone')
if needs_person_mobile:
	td.warningMsg('   - Account Name Mobile')
if needs_person_email:
	td.warningMsg('   - Account Name Email')

# ------------------------------------------------------------------
# Determine Fox Hunter search input:
#   1. Owner Entity if it has a billing address
#   2. Otherwise fall back to Account Name
# ------------------------------------------------------------------
if has_entity and not is_blank(entity_street):
	fh_name    = entity_name
	fh_address = f'{entity_street}, {entity_city}, {entity_state} {entity_zip}'
	print(f'\n Using Owner Entity as Fox Hunter input:')
elif has_person:
	person_street = deal['AccountId__r']['BillingStreet']
	person_city2  = deal['AccountId__r']['BillingCity']
	person_state2 = deal['AccountId__r']['BillingState']
	person_zip2   = deal['AccountId__r']['BillingPostalCode']
	fh_name    = person_name
	fh_address = f'{person_street}, {person_city2}, {person_state2} {person_zip2}'
	print(f'\n No Owner Entity address. Using Account Name as Fox Hunter input:')
else:
	td.warningMsg('\n No Owner Entity or Account Name found on this deal. Cannot run Fox Hunter.')
	exit('\n Terminating program...')

print(f'   Name:    {fh_name}')
print(f'   Address: {fh_address}')

# ------------------------------------------------------------------
# Run Fox Hunter (or load existing file)
# ------------------------------------------------------------------
print('\n Checking for existing Fox Hunter contact file...')
contact_json_file = check_contact_file_exists(fh_name)

if contact_json_file:
	td.colorText(f'\n Existing Fox Hunter file found: {contact_json_file}', 'GREEN')
else:
	print(f'\n Running Fox Hunter for: {fh_name}...')
	contact_json_file = fh.create_ai_contacts_json(fh_name, fh_address)
	if contact_json_file:
		td.colorText(f'\n Fox Hunter complete. File: {contact_json_file}', 'GREEN')
	else:
		td.warningMsg('\n Fox Hunter did not produce a result file.')
		exit('\n Terminating program...')

# ------------------------------------------------------------------
# Load FH JSON and extract data
# ------------------------------------------------------------------
contact_file_path = os.path.join('F:/Research Department/Code/Contact Files', contact_json_file)
dFox = fjson.getJsonDict(contact_file_path)

fh_entity_phone  = 'None'
fh_person_phone  = 'None'
fh_person_mobile = 'None'
fh_person_email  = 'None'

# Entity phone from primary company
if 'companies' in dFox and 'primary' in dFox['companies']:
	fh_entity_phone = dFox['companies']['primary'].get('Phone', 'None') or 'None'

# Person data — let user select from FH contacts
fh_contacts = dFox.get('contacts', [])

selected_contact = None
if has_person and any([needs_person_phone, needs_person_mobile, needs_person_email]):
	if fh_contacts:
		selected_contact = select_fh_contact(fh_contacts, person_name)
		if selected_contact:
			fh_person_phone  = selected_contact.get('Phone', 'None') or 'None'
			fh_person_mobile = selected_contact.get('PersonMobilePhone', 'None') or 'None'
			fh_person_email  = selected_contact.get('PersonEmail', 'None') or 'None'
	else:
		td.warningMsg('\n No contacts found in Fox Hunter results.')

# ------------------------------------------------------------------
# Confirm and apply updates
# ------------------------------------------------------------------
td.banner('Fox Hunter PID Owner Filler v01')
td.warningMsg(' CONFIRM UPDATES')
print(f'\n PID: {PID}\n')

dEntityUpdate = {'type': 'Account', 'Id': EID}
dPersonUpdate = {'type': 'Account', 'Id': AID}
do_entity_update = False
do_person_update = False

# Owner Entity phone
if needs_entity_phone:
	if not is_blank(fh_entity_phone):
		print(f' Owner Entity Phone:   {fh_entity_phone}')
		ui = td.uInput(' Apply to Owner Entity? [1=Yes / 0=No / 00=Quit] > ')
		if ui == '00':
			exit('\n Terminating program...')
		if ui == '1':
			dEntityUpdate['Phone'] = fh_entity_phone
			do_entity_update = True
	else:
		td.warningMsg(' Owner Entity Phone: No phone found in Fox Hunter results.')

# Account Name phone
if needs_person_phone:
	if not is_blank(fh_person_phone):
		print(f'\n Account Name Phone:   {fh_person_phone}')
		ui = td.uInput(' Apply to Account Name? [1=Yes / 0=No / 00=Quit] > ')
		if ui == '00':
			exit('\n Terminating program...')
		if ui == '1':
			dPersonUpdate['Phone'] = fh_person_phone
			do_person_update = True
	else:
		td.warningMsg(' Account Name Phone: No phone found in Fox Hunter results.')

# Account Name mobile
if needs_person_mobile:
	if not is_blank(fh_person_mobile):
		print(f'\n Account Name Mobile:  {fh_person_mobile}')
		ui = td.uInput(' Apply to Account Name? [1=Yes / 0=No / 00=Quit] > ')
		if ui == '00':
			exit('\n Terminating program...')
		if ui == '1':
			dPersonUpdate['PersonMobilePhone'] = fh_person_mobile
			do_person_update = True
	else:
		td.warningMsg(' Account Name Mobile: No mobile found in Fox Hunter results.')

# Account Name email
if needs_person_email:
	if not is_blank(fh_person_email):
		print(f'\n Account Name Email:   {fh_person_email}')
		ui = td.uInput(' Apply to Account Name? [1=Yes / 0=No / 00=Quit] > ')
		if ui == '00':
			exit('\n Terminating program...')
		if ui == '1':
			dPersonUpdate['PersonEmail'] = fh_person_email
			do_person_update = True
	else:
		td.warningMsg(' Account Name Email: No email found in Fox Hunter results.')

# ------------------------------------------------------------------
# Write updates to TF
# ------------------------------------------------------------------
if do_entity_update:
	bb.tf_update_3(service, dEntityUpdate)
	td.colorText(f'\n Owner Entity ({entity_name}) updated.', 'GREEN')

if do_person_update:
	bb.tf_update_3(service, dPersonUpdate)
	td.colorText(f'\n Account Name ({person_name}) updated.', 'GREEN')

if not do_entity_update and not do_person_update:
	print('\n No updates applied.')

exit('\n Fin...')
