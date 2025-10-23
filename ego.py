# EnformionGO functions


from datetime import datetime
import dicts
from dotenv import load_dotenv
import fun_text_date as td
import lao
from pprint import pprint
import json
import os
import requests
from typing import Dict, Any, List, Optional

# Load environment variables from a .env file
load_dotenv()

# EnformionGO api
def ego_api_post(api_url, headers, payload):

	try:
		# Make the API request
		response = requests.post(api_url, headers=headers, data=json.dumps(payload))

		# Check for a successful response (status code 200)
		if response.status_code == 200:
			# Parse the JSON response
			data = response.json()
			filepath = 'C:\\TEMP\\enformion_response.json'
			with open(filepath, 'w', encoding='utf-8') as f:
				json.dump(data, f, indent=4, ensure_ascii=False)
			# print("Contact Enrichment Result:")
			# print(json.dumps(data, indent=4))
			return data
			
		else:
			print(f"Error: {response.status_code} - {response.text}")

	except requests.exceptions.RequestException as e:
		print(f"An error occurred: {e}")

# Run EnformionGO Enrichment Search
def run_EnformionGO_enrichment_search(dAcc):
	# Construct the API URL
	api_url = "https://devapi.enformion.com/Contact/Enrich"

	# Get the request headers
	headers = get_ego_header(SEARCH_TYPE="DevAPIContactEnrich")

	# Get the payload for the enrichment search
	payload = get_ego_blank_person_payload()
	# Populate payload
	payload['FirstName'] = dAcc['NF']
	payload['LastName'] = dAcc['NL']
	if dAcc['STREET'] == 'None':
		payload['Address']['AddressLine1'] = ''
	else:
		payload['Address']['AddressLine1'] = dAcc['STREET']
	payload['Address']['AddressLine2'] = f'{dAcc['CITY']}, {dAcc['STATE']}'

	# Make the API request
	dEGO = ego_api_post(api_url, headers, payload)

	# If no strong matches and AddressLine1 (dAcc['STREET']) is not empty, set AddressLine1 to empty and try search again
	if dEGO.get('message', '') == 'No strong matches' and payload['Address']['AddressLine1'] != '':
		payload['Address']['AddressLine1'] = ''
		dEGO = ego_api_post(api_url, headers, payload)


	# Process the response
	dAcc = get_ego_enrichment_data(dEGO, dAcc)

	return dAcc

# Run EnformionGO Enrichment Search
def run_EnformionGO_entity_search(dAcc):
	# Construct the API URL
	api_url = "https://devapi.enformion.com/BusinessV2Search"

	# Get the request headers
	headers = get_ego_header(SEARCH_TYPE="BusinessV2")

	# Get the payload for the enrichment search
	payload = get_ego_blank_entity_payload()
	# Populate payload
	payload['BusinessName'] = dAcc['ENTITY']
	if dAcc['STREET'] == 'None':
		payload['AddressLine1'] = ''
	else:
		payload['AddressLine1'] = dAcc['STREET']
	
	if dAcc['CITY'] == 'None':
		dAcc['CITY'] = td.uInput('\n Enter City [00] > ').title()
		if dAcc['CITY'] == '00':
			exit('\n Terminating program...')
	if dAcc['STATE'] == 'None':
		dAcc['STATE'] = td.uInput('\n Enter State [00] > ').title()
		if dAcc['STATE'] == '00':
			exit('\n Terminating program...')
	payload['AddressLine2'] = f'{dAcc['CITY']}, {dAcc['STATE']}'

	# Make the API request
	dEGO = ego_api_post(api_url, headers, payload)

	# Process the response
	dAcc = get_ego_entity_data(dEGO, dAcc)

	return dAcc

# PAYLOADS & HEADERS #################################################################
def get_ego_blank_entity_payload():
	payload = {
		"BusinessName": "",
		"AddressLine1": "",
		"AddressLine2": ""
	}
	return payload

def get_ego_blank_property_payload():
	"""
	Apn = null (optional, string) ... Assessor Parcel Number.
	BusinessName = null (optional, string) ... Business name.
	FirstName = null (optional, string) ... First name.
	MiddleName = null (optional, string) ... Middle name or middle initial.
	LastName = null (optional, string) ... Last name.
	AddressLine1 = null (optional, string) ... Address line 1 (house number, street, state, unit/suite/apt number).
	AddressLine2 = null (optional, string) ... Address line 2 (city,state,zip).
	TahoeId = null (optional, string)...Tahoe Id is a unique person ID attached to each person record.
	PoseidonIds = null (optional, string) poseidonid
	Ssn = null (optional, string)...Social security number (format: ###-##-####).

	"""
	payload = {
		"APN": "",
		"BusinessName": "",
		"FirstName": "",
		"LastName": "",
		"AddressLine1": "",
		"AddressLine2": ""
	}
	return payload

def get_ego_blank_person_payload():
	"""
	FirstName = null (optional, string).. First Name
	MiddleName = null (optional, string).. Middle name or middle initial
	LastName = null (optional, string)... Last name
	Dob = null (optional, string)..Date of birth (format: mm/dd/yyyy).
	Age = null (optional, int)...Age.
	Address.AddressLine1 = null (optional, string)..House number and street name or PO Box
	Address.AddressLine2 = null (optional, string)..State or City and State Or Zip
	Phone = null (optional, string)...Phone number (formats: ###-###-####, (###)###-####).
	Email = null (optional, string)..E-mail Address
	"""

	payload = {
		"FirstName": "",
		"LastName": "",
		"Email": "",
		"Phone": "",
		"Address": {
			"AddressLine1": "",
			"AddressLine2": ""
		},
		"FilterOptions": ["IncludeLatestRecordOnly"],
		"Page": 1,
		"ResultsPerPage": 10
	}
	return payload

# Construct the request headers
def get_ego_header(SEARCH_TYPE):

	# Get profile name and password from .env
	ACCESS_PROFILE_NAME = os.getenv("ACCESS_PROFILE_NAME")
	ACCESS_PROFILE_PASSWORD = os.getenv("ACCESS_PROFILE_PASSWORD")

	headers = {
		"accept": "application/json",
		"galaxy-ap-name": ACCESS_PROFILE_NAME,
		"galaxy-ap-password": ACCESS_PROFILE_PASSWORD,
		"galaxy-search-type": SEARCH_TYPE,
		"content-type": "application/json"
	}

	# pprint(headers)
	return headers

# Get the Enrichment data into dAcc
def get_ego_enrichment_data(dEGO, dAcc):

	# Confirm data was found else return dAcc
	if dEGO.get('message', '') == 'No strong matches':
		td.warningMsg('No strong matches found in EnformionGO API.')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		return dAcc
	
	d_person = dEGO.get('person', {})

	# Addresses
	if dAcc['STREET'] == 'None':
		# Gets the most recent address based on last reported date
		d_addresses = d_person.get('addresses', [])
		if d_addresses:
			# Sort by lastReportedDate to get most recent
			try:
				d_current_address = max(d_addresses, key=lambda x: datetime.strptime(x.get('lastReportedDate', '1/1/1900'), '%m/%d/%Y'))

				dAcc['STREET'] = d_current_address.get('street', 'None')    # 7855 S River Pkwy
				dAcc['CITY'] = d_current_address.get('city', 'None')        # Tempe
				dAcc['STATE'] = d_current_address.get('state', 'None')      # AZ
				dAcc['ZIPCODE'] = d_current_address.get('zip', 'None')      # 85284
				
				# Full address for ADDRESSFULL
				address_parts = [
					d_current_address.get('street', ''),
					d_current_address.get('unit', ''),
					d_current_address.get('city', ''),
					d_current_address.get('state', ''),
					d_current_address.get('zip', '')
				]
				full_address = ', '.join(filter(None, address_parts))
				dAcc['ADDRESSFULL'] = full_address if full_address else 'None' 
			except (ValueError, TypeError):
				# Handle date parsing errors
				d_current_address = d_addresses[0]  # Just use first address if date parsing fails
				dAcc['STREET'] = d_current_address.get('street', 'None')
				dAcc['CITY'] = d_current_address.get('city', 'None')
				dAcc['STATE'] = d_current_address.get('state', 'None')
				dAcc['ZIPCODE'] = d_current_address.get('zip', 'None')
				dAcc['ADDRESSFULL'] = 'None'
	
	
	# Phones
	# Process phone numbers - primary phone (480) 883-8987, mobile (480) 225-3805
	d_phones = d_person.get('phones', [])
	d_connected_phones = []  # Initialize outside try block
	d_mobile_phones = []     # Initialize outside try block
	
	if d_phones:
		try:
			if dAcc['PHONE'] == 'None' or len(dAcc['PHONE']) < 10:
				# Get primary phone (most recent connected landline or any phone)
				# Only return connected phones
				d_connected_phones = [p for p in d_phones if p.get('isConnected', False)]
				if d_connected_phones:
					primary_phone = max(d_connected_phones, key=lambda x: datetime.strptime(x.get('lastReportedDate', '1/1/1900'), '%m/%d/%Y'))
					dAcc['PHONE'] = primary_phone.get('number', 'None')  # (480) 883-8987
			
			if dAcc['MOBILE'] == 'None':
				# Get mobile numbers specifically
				# Only return connected phones
				d_mobile_phones = [p for p in d_phones if p.get('type') == 'mobile' and p.get('isConnected', False)]
				if d_mobile_phones:
					primary_mobile = max(d_mobile_phones, key=lambda x: datetime.strptime(x.get('lastReportedDate', '1/1/1900'), '%m/%d/%Y'))
					dAcc['MOBILE'] = primary_mobile.get('number', 'None')  # (480) 225-3805
		except (ValueError, TypeError):
			# Handle date parsing errors - just use first available
			d_connected_phones = [p for p in d_phones if p.get('isConnected', False)]
			d_mobile_phones = [p for p in d_phones if p.get('type') == 'mobile' and p.get('isConnected', False)]
			
			for phone in d_connected_phones:
				if dAcc['PHONE'] == 'None':
					dAcc['PHONE'] = phone.get('number', 'None')
					break
			for phone in d_mobile_phones:
				if dAcc['MOBILE'] == 'None':
					dAcc['MOBILE'] = phone.get('number', 'None')
					break
		
		# Create Note Title and Content (now that variables are guaranteed to be defined)
		if d_connected_phones or d_mobile_phones:
			dAcc['NOTETITLE'] = 'Additional Phone Numbers'
			dAcc['NOTECONTENT'] = ''  # Initialize note content
			for item in d_connected_phones:
				dAcc['NOTECONTENT'] = dAcc.get('NOTECONTENT', '') + f"{item.get('number', 'None')} - Landline\n"
			for item in d_mobile_phones:
				dAcc['NOTECONTENT'] = dAcc.get('NOTECONTENT', '') + f"{item.get('number', 'None')} - Mobile\n"

	# Process emails - use first email since none are validated
	d_emails = d_person.get('emails', [])
	if d_emails:
		# Get primary email (validated if available, otherwise first email)
		d_validated_emails = [e for e in d_emails if e.get('isValidated', False)]
		if d_validated_emails:
			# Create Note Title
			if dAcc['NOTETITLE'] == 'Additional Phone Numbers':
				dAcc['NOTETITLE'] = 'Additional Phone Numbers and Emails'
			else:
				dAcc['NOTETITLE'] = 'Additional Email Addresses'

			for item in d_validated_emails:
				if dAcc['EMAIL'] == 'None':
					dAcc['EMAIL'] = item.get('email', 'None')
				# Create Note Content
				dAcc['NOTECONTENT'] = dAcc.get('NOTECONTENT', '') + f"{item.get('email', 'None')}\n"

	
	# print('here5')
	# pprint(dEGO)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	# pprint(dAcc)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	return dAcc

def get_ego_entity_data(dEGO, dAcc):
	"""
	Allow user to select a company and populate dAcc dictionary with its data.
	
	Args:
		enformion_response: The JSON response from EnformionGO API
		company_index: Index of company to select (if known)
		company_name: Name of company to search for (if known)
		interactive: If True, prompts user for selection
	
	Returns:
		Populated dAcc dictionary for selected company
	"""
	# Get list of companies
	companies = display_company_list(dEGO)

	# Return dAcc if no companies found
	if companies == []:
		return dAcc
	
	selected_index = None
	
	
	# If interactive mode and no selection yet, prompt user
	while selected_index is None:
		try:
			ui = td.uInput(f"\n Enter company number [00] > ")
			if ui.strip() == '00':
				exit('\n Terminating program...')
			elif ui.strip() == '99':
				td.warningMsg("\n No company selected...")
				lao.sleep(1)
				return dAcc
			selected_index = int(ui)
			if not (0 <= selected_index < len(companies)):
				td.warningMsg(f"\n Please enter a number between 0 and {len(companies)-1}")
				selected_index = None
		except ValueError:
			td.warningMsg("\n Please enter a valid number...")

	# If still no selection, use first company
	if selected_index is None:
		selected_index = 0
		td.warningMsg(f"\n Defaulting to first company: {companies[0]['company_name']}")

	# Get the selected company's data
	selected_company = companies[selected_index]
	business_record = dEGO['businessV2Records'][selected_company['record_index']]

	# Extract filing based on type
	if selected_company['filing_type'] == 'usCorp':
		filings = business_record['usCorpFilings']
	else:
		filings = business_record['newBusinessFilings']
	
	# Find the specific filing (in case there are multiple)
	target_filing = None
	for filing in filings:
		if selected_company['filing_type'] == 'usCorp':
			if filing.get('name') == selected_company['company_name']:
				target_filing = filing
				break
		else:
			if filing.get('company') == selected_company['company_name']:
				target_filing = filing
				break
	
	if not target_filing:
		target_filing = filings[0]  # Default to first if exact match not found
	
	# Create a temporary response with just this filing
	temp_response = {
		'businessV2Records': [{
			'usCorpFilings': [target_filing] if selected_company['filing_type'] == 'usCorp' else [],
			'newBusinessFilings': [target_filing] if selected_company['filing_type'] == 'newBusiness' else []
		}]
	}
	
	# Use existing populate function
	dAcc = populate_dacc_from_enformion(temp_response, dAcc)
	return dAcc

def display_company_list(enformion_response: Dict[str, Any]) -> List[Dict[str, Any]]:
	"""
	Display a list of companies from EnformionGO response for user selection.
	
	Args:
		enformion_response: The JSON response from EnformionGO API
	
	Returns:
		List of company information dictionaries
	"""
	companies = []
	
	if not enformion_response.get('businessV2Records'):
		td.warningMsg("\n No business records found in response from EnformionGO")
		lao.sleep(2)
		return companies
	
	for idx, business_record in enumerate(enformion_response['businessV2Records']):
		# Check for usCorpFilings
		if business_record.get('usCorpFilings'):
			for filing in business_record['usCorpFilings']:
				# Get address for usCorp filing
				full_address = 'N/A'
				if filing.get('corpMainAddresses'):
					addr = filing['corpMainAddresses'][0]
					full_address = addr.get('fullAddress', 'N/A')
				
				company_info = {
					'index': len(companies),
					'record_index': idx,
					'filing_type': 'usCorp',
					'company_name': filing.get('name', 'Unknown'),
					'state': filing.get('stateCode', 'N/A'),
					'status': filing.get('corpStatus', 'Unknown'),
					'filing_date': filing.get('filingDate', 'N/A'),
					'entity_type': filing.get('corpType', 'N/A'),
					'full_address': full_address
				}
				companies.append(company_info)
		
		# Check for newBusinessFilings
		if business_record.get('newBusinessFilings'):
			for filing in business_record['newBusinessFilings']:
				# Get state and address from addresses if available
				state = 'N/A'
				full_address = 'N/A'
				if filing.get('addresses'):
					state = filing['addresses'][0].get('state', 'N/A')
					# Look for business address first, then mail address
					for addr in filing['addresses']:
						if addr.get('addressTypeDesc') == 'BUSINESS ADDRESS':
							full_address = addr.get('fullAddress', 'N/A')
							break
					# If no business address, use mail address
					if full_address == 'N/A':
						for addr in filing['addresses']:
							if addr.get('addressTypeDesc') == 'MAIL ADDRESS':
								full_address = addr.get('fullAddress', 'N/A')
								break
					# If still no address, use first available
					if full_address == 'N/A' and filing['addresses']:
						full_address = filing['addresses'][0].get('fullAddress', 'N/A')
				
				# Get filing date from history
				filing_date = 'N/A'
				for date_entry in filing.get('filingHistoryDates', []):
					if date_entry.get('dateTypeDesc') == 'SOURCE FILING DATE':
						filing_date = date_entry.get('date', 'N/A')
						break
				
				company_info = {
					'index': len(companies),
					'record_index': idx,
					'filing_type': 'newBusiness',
					'company_name': filing.get('company', 'Unknown'),
					'state': state,
					'status': filing.get('statusDesc', 'Unknown'),
					'filing_date': filing_date,
					'entity_type': filing.get('legalBusinessDescription', 'N/A'),
					'full_address': full_address
				}
				companies.append(company_info)
	
	# Display companies
	print("\n" + "="*80)
	print(" COMPANIES FOUND IN ENFORMION SEARCH RESULTS")
	print("="*80)
	
	for comp in companies:
		
		print('here6')
		pprint(comp)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		
		print(f"\n  {comp['index']}) {comp['company_name']}")
		print(f"    State:   {comp['state']}")
		print(f"    Address: {comp['full_address']}")
		# print(f"    Type: {comp['entity_type']}")
		print(f"    Status:  {comp['status']}")
		# print(f"    Filing Date: {comp['filing_date']}")
	
	print('\n 99) No match listed, continue')
	print('\n 00) Quit')

	print("\n" + "="*80)
	
	return companies

def populate_dacc_from_enformion(dEGO: Dict[str, Any],
								 dAcc: Dict[str, Any], 
								 target_officer: Optional[str] = None,
								 use_entity_address: bool = True) -> Dict[str, Any]:
	"""
	Populate a dAcc dictionary with data from EnformionGO API response.
	Handles both usCorpFilings and newBusinessFilings response types.
	
	Args:
		enformion_response: The JSON response from EnformionGO API
		target_officer: Optional specific officer name/title to extract (if None, uses first officer)
		use_entity_address: If True, uses entity address; if False, uses registered agent address
	
	Returns:
		Populated dAcc dictionary
	"""
	# # Get blank dAcc dictionary
	# dAcc = dicts.get_blank_account_dict()
	
	# Check if we have valid response data
	if not dEGO.get('businessV2Records'):
		td.warningMsg("No business records found in response from EnformionGO")
		lao.sleep(2)
		return dAcc
	
	# Get the first business record
	business_record = dEGO['businessV2Records'][0]
	
	# Determine which type of filing we have and extract data accordingly
	filing = None
	filing_type = None
	
	# Check for US Corp filings first
	if business_record.get('usCorpFilings') and len(business_record['usCorpFilings']) > 0:
		filing = business_record['usCorpFilings'][0]
		filing_type = 'usCorp'
	# Check for new business filings
	elif business_record.get('newBusinessFilings') and len(business_record['newBusinessFilings']) > 0:
		filing = business_record['newBusinessFilings'][0]
		filing_type = 'newBusiness'
	else:
		print("No filings found")
		return dAcc
	
	# Populate Entity Information based on filing type
	if filing_type == 'usCorp':
		dAcc['ENTITY'] = filing.get('name', 'None')
		dAcc['EID'] = filing.get('corpFileKey', 'None')
		dAcc['SOURCE_ID'] = filing.get('registryNumber', filing.get('corpFileKey', 'None'))
		dAcc['STATE'] = filing.get('stateCode', 'None')
		dAcc['STATEOFORIGIN'] = filing.get('incorporationState', filing.get('stateCode', 'None'))
		
		# Get officers and addresses from usCorp structure
		officers = filing.get('officers', [])
		entity_addresses = filing.get('corpMainAddresses', [])
		
	elif filing_type == 'newBusiness':
		dAcc['ENTITY'] = filing.get('company', 'None')
		dAcc['EID'] = filing.get('businessId', 'None')
		dAcc['SOURCE_ID'] = filing.get('data', {}).get('filingNumber', str(filing.get('businessId', 'None')))
		
		# Get contacts (officers) and addresses from newBusiness structure
		contacts = filing.get('contacts', [])
		addresses = filing.get('addresses', [])
		phones = filing.get('phones', [])
		
		# Extract state from addresses if available
		if addresses:
			dAcc['STATE'] = addresses[0].get('state', 'None')
			dAcc['STATEOFORIGIN'] = addresses[0].get('state', 'None')
		
		# Handle phone numbers for entity
		if phones and len(phones) > 0:
			phone_number = phones[0].get('phoneNumber', 'None')
			dAcc['PHONE'] = phone_number
			dAcc['PHONEENTITY'] = phone_number
		
		# Convert contacts to officers format for consistent processing
		officers = []
		for contact in contacts:
			officer = {
				'title': contact.get('officerTitleDesc', ''),
				'name': contact.get('name', {}),
				'address': None
			}
			
			# Find corresponding address for this contact
			contact_type_id = contact.get('contactTypeId')
			for addr in addresses:
				if addr.get('addressTypeId') == contact_type_id:
					officer['address'] = addr
					break
			
			officers.append(officer)
		
		# Use business address as entity address
		entity_addresses = [addr for addr in addresses if addr.get('addressTypeDesc') == 'BUSINESS ADDRESS']
		if not entity_addresses:
			entity_addresses = [addr for addr in addresses if addr.get('addressTypeDesc') == 'MAIL ADDRESS']
	
	dAcc['SOURCE'] = 'EnformionGO'
	
	# Process Officers/Contacts to find contact person
	selected_officer = None
	
	for officer in officers:
		# Get title based on filing type
		if filing_type == 'usCorp':
			title = officer.get('title', '').upper()
		else:
			title = officer.get('title', '').upper()
		
		# Skip registered agents for contact person
		if 'AGENT' in title and 'REGISTERED' in title:
			continue
		
		# If target_officer specified, look for match
		if target_officer:
			if filing_type == 'usCorp':
				officer_name = officer.get('name', {}).get('nameRaw', '')
			else:
				name_dict = officer.get('name', {})
				officer_name = name_dict.get('fullName', '')
			
			if target_officer.upper() in officer_name.upper() or target_officer.upper() in title:
				selected_officer = officer
				break
		# Otherwise, prioritize managers/members/directors
		elif not selected_officer:
			if any(role in title for role in ['MANAGER', 'MEMBER', 'DIRECTOR', 'PRESIDENT', 'CEO', 'ORGANIZER']):
				selected_officer = officer
	
	# If no officer selected yet, use first non-agent officer
	if not selected_officer:
		for officer in officers:
			title = officer.get('title', '').upper() if filing_type == 'usCorp' else officer.get('title', '').upper()
			if 'AGENT' not in title or 'REGISTERED' not in title:
				selected_officer = officer
				break
	
	# Extract person information from selected officer
	if selected_officer:
		if filing_type == 'usCorp':
			name_data = selected_officer.get('name', {})
			name_raw = name_data.get('nameRaw', '')
			
			# Check if this is a company acting as officer
			if any(corp_indicator in name_raw.upper() for corp_indicator in ['LLC', 'INC', 'CORP', 'COMPANY', 'LP', 'LTD', 'LLLP', ' PC']):
				# This is a company, not a person - don't populate person fields
				dAcc['NAME'] = 'None'
				dAcc['NF'] = 'None'
				dAcc['NM'] = 'None'
				dAcc['NL'] = 'None'
			else:
				# This appears to be a person
				dAcc['NAME'] = name_raw
				dAcc['NF'] = name_data.get('nameFirst', 'None')
				dAcc['NM'] = name_data.get('nameMiddle', 'None')
				dAcc['NL'] = name_data.get('nameLast', 'None')
				dAcc['TITLEPERSON'] = selected_officer.get('title', 'None')
		else:
			# newBusiness format
			name_data = selected_officer.get('name', {})
			full_name = name_data.get('fullName', '')
			
			# Check if this is a company
			if any(corp_indicator in full_name.upper() for corp_indicator in ['LLC', 'INC', 'CORP', 'COMPANY', 'LP', 'LTD', 'LLLP', ' PC']):
				dAcc['NAME'] = 'None'
				dAcc['NF'] = 'None'
				dAcc['NM'] = 'None'
				dAcc['NL'] = 'None'
			else:
				dAcc['NAME'] = full_name
				dAcc['NF'] = name_data.get('firstName', 'None')
				dAcc['NM'] = name_data.get('middleInit', 'None')
				dAcc['NL'] = name_data.get('lastName', 'None')
				dAcc['TITLEPERSON'] = selected_officer.get('title', 'None')
	
	# Get entity address
	entity_address = None
	
	if use_entity_address and entity_addresses:
		entity_address = entity_addresses[0]
	elif selected_officer and selected_officer.get('address'):
		entity_address = selected_officer['address']
	else:
		# Look for any officer with an address
		for officer in officers:
			if officer.get('address'):
				entity_address = officer['address']
				break
		# If still no address, try any address from newBusiness filing
		if not entity_address and filing_type == 'newBusiness' and addresses:
			entity_address = addresses[0]
	
	# Populate address fields
	if entity_address:
		# Build full address
		address_parts = []
		
		# Add house number and street
		if entity_address.get('houseNumber'):
			address_parts.append(entity_address['houseNumber'])
		if entity_address.get('streetPreDirection'):
			address_parts.append(entity_address['streetPreDirection'])
		if entity_address.get('streetName'):
			address_parts.append(entity_address['streetName'])
		if entity_address.get('streetPostDirection'):
			address_parts.append(entity_address['streetPostDirection'])
		
		# Add unit if present
		unit_parts = []
		if entity_address.get('unitType'):
			unit_parts.append(entity_address['unitType'])
		if entity_address.get('unit'):
			unit_parts.append(entity_address['unit'])
		
		street_address = ' '.join(address_parts)
		if unit_parts:
			street_address += ', ' + ' '.join(unit_parts)
		
		dAcc['STREET'] = street_address if street_address else entity_address.get('addressLine1', 'None')
		dAcc['CITY'] = entity_address.get('city', 'None')
		dAcc['STATE'] = entity_address.get('state', dAcc['STATE'])  # Use existing state if not in address
		dAcc['ZIPCODE'] = entity_address.get('zip', 'None')
		dAcc['COUNTRY'] = entity_address.get('country', 'USA')  # Default to USA if not specified
		
		# Build full address
		full_address = f"{dAcc['STREET']}, {dAcc['CITY']}, {dAcc['STATE']} {dAcc['ZIPCODE']}"
		dAcc['ADDRESSFULL'] = full_address
	
	# Add filing dates and status to description
	if filing_type == 'usCorp':
		dAcc['DESCRIPTION'] = f"Status: {filing.get('corpStatus', 'Unknown')} as of {filing.get('corpStatusDate', 'Unknown')}"
		if filing.get('filingDate'):
			dAcc['DESCRIPTION'] += f" | Filed: {filing['filingDate']}"
		if filing.get('corpType'):
			dAcc['DESCRIPTION'] += f" | Type: {filing['corpType']}"
	else:
		# newBusiness format
		status_desc = filing.get('statusDesc', 'Unknown')
		dAcc['DESCRIPTION'] = f"Status: {status_desc}"
		
		# Get filing dates from history
		filing_dates = filing.get('filingHistoryDates', [])
		for date_entry in filing_dates:
			if date_entry.get('dateTypeDesc') == 'SOURCE FILING DATE':
				dAcc['DESCRIPTION'] += f" | Filed: {date_entry.get('date', 'Unknown')}"
				break
		
		legal_desc = filing.get('legalBusinessDescription', '')
		if legal_desc:
			dAcc['DESCRIPTION'] += f" | Type: {legal_desc}"
	
	# Note: User will need to fill in the CATEGORY field
	
	return dAcc
