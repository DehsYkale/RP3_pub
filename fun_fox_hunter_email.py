# fun_fox_hunter_email.py
# Fox Hunter Email - Contact Enrichment from Email Address
# Version 0.2
#
# INPUT:  first_name, last_name, email, entity_name (optional), address (optional)
# OUTPUT: combined_data dict matching fun_fox_hunter.py format
#
# Flow:
#   1. Extract email domain
#   2. Query TF for Person Account matching email → populate contact block with AID
#   3. If person found → resolve Entity via 3 paths (Company__c, ParentId, Deal)
#   4. If person NOT found → query TF Entity by domain (fallback)
#   5. Build AI prompt with all known data
#   6. Single AI call → enriched contact + company (fills gaps from TF)
#   7. Post-process (entity-as-contact filter, phone source fields)
#   8. Return combined_data dict with AID on contact and EID on company
#
# Changes v0.2:
#   - Added find_person_by_email()        → TF person lookup by email
#   - Added tf_person_to_contact_block()  → converts TF person → contact block w/ AID
#   - Added find_entity_for_person()      → resolves entity via Company__c / ParentId / Deal
#   - main() now runs person lookup first, entity fallback second
#   - assemble_combined_data() merges TF contact block with AI result
#   - search_metadata includes tf_person_resolved flag and entity_resolution_method

import ai
import bb
import fun_login
import fun_text_date as td
from fun_fox_hunter import filter_entity_as_contact, ensure_phone_source_fields
from datetime import datetime
import json
import os
from pprint import pprint
import re
import time

# =============================================================================
# Constants
# =============================================================================

PROMPT_PATH = 'F:/Research Department/Code/Prompts/Fox_Hunter_Email_AI_Prompt_v01.txt'
OUTPUT_DIR  = 'F:/Research Department/Code/Contact Files'

# Domains that carry no company identity signal
GENERIC_DOMAINS = {
	'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
	'aol.com', 'me.com', 'msn.com', 'live.com', 'comcast.net', 'att.net',
	'verizon.net', 'sbcglobal.net', 'cox.net', 'earthlink.net', 'protonmail.com',
	'mac.com', 'ymail.com', 'mail.com'
}

AI_MODEL = 'gpt-5.2'


# =============================================================================
# Domain Utilities
# =============================================================================

def extract_domain(email):
	"""
	Extract the domain portion from an email address.

	Args:
		email (str): Email address (e.g. 'john@acmehomes.com')

	Returns:
		str: Domain string lowercase (e.g. 'acmehomes.com'), or '' if invalid
	"""
	email = email.strip().lower()
	if '@' not in email:
		return ''
	parts = email.split('@')
	if len(parts) != 2 or not parts[1]:
		return ''
	return parts[1]


def is_generic_domain(domain):
	"""
	Return True if the domain is a generic personal email provider.

	Args:
		domain (str): Domain string (e.g. 'gmail.com')

	Returns:
		bool
	"""
	return domain.lower() in GENERIC_DOMAINS


# =============================================================================
# TF Person Lookup
# =============================================================================

def find_person_by_email(service, email):
	"""
	Query TerraForce for a Person Account matching the given email address.
	Returns the TF record dict or None.

	Args:
		service: TerraForce service object
		email (str): Email address to search

	Returns:
		dict or None: TF Person Account record, or None if not found
	"""
	if not email:
		return None

	wc = f"PersonEmail = '{email}' AND IsPersonAccount = true"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=1, fields='default')

	if not results:
		return None

	rec = results[0]
	print(f'\n ✅ TF person found [{email}]: {rec.get("FirstName", "")} {rec.get("LastName", "")} (AID: {rec.get("Id", "")})')
	return rec


def tf_person_to_contact_block(tf_record):
	"""
	Convert a TF Person Account record into the contact block format used in combined_data.
	Populates AID with the TF record Id.

	Args:
		tf_record (dict): Raw TF Person Account record

	Returns:
		dict: contact block with AID populated
	"""
	return {
		'FirstName':            tf_record.get('FirstName', ''),
		'MiddleName__c':        tf_record.get('MiddleName__c', ''),
		'LastName':             tf_record.get('LastName', ''),
		'PersonEmail':          tf_record.get('PersonEmail', ''),
		'PersonTitle':          tf_record.get('PersonTitle', ''),
		'Phone':                tf_record.get('Phone', ''),
		'PhoneSource':          'terraforce' if tf_record.get('Phone') else 'none',
		'PersonMobilePhone':    tf_record.get('PersonMobilePhone', ''),
		'MobileSource':         'terraforce' if tf_record.get('PersonMobilePhone') else 'none',
		'BillingStreet':        tf_record.get('BillingStreet', ''),
		'BillingCity':          tf_record.get('BillingCity', ''),
		'BillingState':         tf_record.get('BillingState', ''),
		'BillingPostalCode':    tf_record.get('BillingPostalCode', ''),
		'Category__c':          tf_record.get('Category__c', ''),
		'LinkedIn_Url__c':      tf_record.get('LinkedIn_Url__c', ''),
		'Description':          tf_record.get('Description', ''),
		'Company__c':           '',		# Populated after entity resolution (Company__c may be a SF ID)
		'AID':                  tf_record.get('Id', ''),		# TF Person Account ID
		'source':               'terraforce',
		'priority_rank':        1,
		'enrichment_attempted': True,
		'enrichment_source':    'terraforce'
	}


# =============================================================================
# Entity Resolution from Person (3-path)
# =============================================================================

def find_entity_for_person(service, tf_person_record):
	"""
	Given a TF Person Account record, attempt to resolve the associated Entity
	(company) via three paths in priority order:

		1. Company__c field populated → query Entity by Id (if SF ID) or by Name
		2. Person is a child account (ParentId) → query that Entity directly
		3. Person appears as AccountId__c on a Deal that has Owner_Entity__c set

	Args:
		service: TerraForce service object
		tf_person_record (dict): TF Person Account record

	Returns:
		tuple: (entity_record or None, resolution_method str or None)
	"""
	person_id   = tf_person_record.get('Id', '')
	person_name = f'{tf_person_record.get("FirstName", "")} {tf_person_record.get("LastName", "")}'.strip()

	# --- Path 1: Company__c field ---
	# Company__c may be a Salesforce record ID (15/18 chars, alphanumeric)
	# or a plain name string depending on how the field was set.
	company_val = tf_person_record.get('Company__c', '')
	if company_val:
		sf_id_pattern = re.compile(r'^[a-zA-Z0-9]{15}([a-zA-Z0-9]{3})?$')
		if sf_id_pattern.match(company_val):
			# It's a SF record ID — query directly by Id
			wc = f"Id = '{company_val}' AND IsPersonAccount = false"
		else:
			# It's a plain name string
			wc = f"Name = '{company_val}' AND IsPersonAccount = false"
		results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=1, fields='default')
		if results:
			print(f'\n ✅ Entity via Company__c: {results[0]["Name"]} (EID: {results[0]["Id"]})')
			return results[0], 'Company__c field'

	# --- Path 2: Child account (ParentId) ---
	parent_id = tf_person_record.get('ParentId', '')
	if parent_id:
		wc = f"Id = '{parent_id}' AND IsPersonAccount = false"
		results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=1, fields='default')
		if results:
			print(f'\n ✅ Entity via ParentId: {results[0]["Name"]} (EID: {results[0]["Id"]})')
			return results[0], 'child account (ParentId)'

	# --- Path 3: Deal where AccountId__c = person AND Owner_Entity__c is set ---
	if person_id:
		wc = f"AccountId__c = '{person_id}' AND Owner_Entity__c != null"
		deals = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=1, fields='default')
		if deals:
			entity_id = deals[0].get('Owner_Entity__c', '')
			if entity_id:
				wc2 = f"Id = '{entity_id}' AND IsPersonAccount = false"
				results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc2, limit=1, fields='default')
				if results:
					print(f'\n ✅ Entity via Deal Owner_Entity__c: {results[0]["Name"]} (EID: {results[0]["Id"]})')
					return results[0], 'Deal Owner_Entity__c'

	print(f'\n ℹ️  No entity found for [{person_name}] via any path')
	return None, None


# =============================================================================
# TF Entity Domain Lookup (fallback when person not found)
# =============================================================================

def find_entity_by_domain(service, domain):
	"""
	Query TerraForce for Entity accounts whose Website field contains the domain.
	Returns the best matching TF record or None.

	Strategy:
		- Query Website LIKE '%domain%'
		- If 1 result  → return it (high confidence)
		- If 2+ results → return the one whose Website most closely matches
		  the domain (shortest Website string = most specific match)
		- If 0 results → return None

	Args:
		service: TerraForce service object from fun_login.TerraForce()
		domain (str): Email domain (e.g. 'acmehomes.com')

	Returns:
		dict or None: TF Entity record dict, or None if no match
	"""
	if not domain or is_generic_domain(domain):
		return None

	wc = f"Website LIKE '%{domain}%' AND IsPersonAccount = false"
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields='default')

	if not results:
		return None

	if len(results) == 1:
		print(f'\n ✅ TF entity found via domain [{domain}]: {results[0]["Name"]}')
		return results[0]

	# Multiple matches — pick the one with the shortest (most specific) Website
	def website_specificity(rec):
		w = rec.get('Website', '') or ''
		return len(w)

	best = min(results, key=website_specificity)
	print(f'\n ✅ TF entity found via domain [{domain}] ({len(results)} matches, using best): {best["Name"]}')
	return best


def tf_record_to_company_block(tf_record):
	"""
	Convert a TF Entity query result dict into the company block format
	used in combined_data. Populates EID with the TF record Id.

	Args:
		tf_record (dict): Raw TF Entity record

	Returns:
		dict: company block with EID populated
	"""
	return {
		'Name':                  tf_record.get('Name', ''),
		'BillingStreet':         tf_record.get('BillingStreet', ''),
		'BillingCity':           tf_record.get('BillingCity', ''),
		'BillingState':          tf_record.get('BillingState', ''),
		'BillingPostalCode':     tf_record.get('BillingPostalCode', ''),
		'Phone':                 tf_record.get('Phone', ''),
		'Website':               tf_record.get('Website', ''),
		'LinkedIn_Url__c':       tf_record.get('LinkedIn_Url__c', ''),
		'Category__c':           tf_record.get('Category__c', ''),
		'Description':           tf_record.get('Description', ''),
		'EID':                   tf_record.get('Id', ''),		# TF Entity Account ID
		'domain_match_confidence': 'high',
		'domain_match_notes':    'Matched via Website field in TerraForce',
		'source':                'terraforce'
	}


# =============================================================================
# Prompt Builder
# =============================================================================

def build_prompt(first_name, last_name, email, entity_name, address, domain, tf_entity_found):
	"""
	Load the AI prompt template and inject all known data.

	Args:
		first_name (str)
		last_name (str)
		email (str)
		entity_name (str): Company name or 'None'
		address (str): Property/context address or 'None'
		domain (str): Extracted email domain
		tf_entity_found (bool): True if TF already resolved the entity

	Returns:
		str: Formatted prompt ready for AI call
	"""
	with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
		prompt = f.read()

	# Build entity block for prompt
	if tf_entity_found:
		entity_block = (
			f'Company Name: {entity_name}\n'
			f'NOTE: This company was already found in TerraForce via email domain match. '
			f'Focus enrichment on the PERSON only (phone, address, LinkedIn, category). '
			f'You do NOT need to research the company — it is already resolved.'
		)
	elif entity_name and entity_name != 'None':
		entity_block = f'Company Name: {entity_name}'
	else:
		entity_block = 'No company name provided — infer from email domain if possible.'

	prompt = prompt.replace('**[FIRST_NAME]**',    first_name)
	prompt = prompt.replace('**[LAST_NAME]**',     last_name)
	prompt = prompt.replace('**[EMAIL]**',         email)
	prompt = prompt.replace('**[ENTITY_BLOCK]**',  entity_block)
	prompt = prompt.replace('**[EMAIL_DOMAIN]**',  domain if domain else 'unknown')
	prompt = prompt.replace('**[ADDRESS]**',       address if address and address != 'None' else 'Not provided')

	return prompt


# =============================================================================
# JSON Extraction (reuses Fox Hunter pattern)
# =============================================================================

def strip_to_json(results):
	"""
	Extract JSON from AI response using multiple fallback methods.
	Mirrors fun_fox_hunter.strip_to_json pattern.

	Args:
		results (dict): Raw AI response from ai.ask_kablewy_ai()

	Returns:
		dict or None: Parsed JSON dict, or None on failure
	"""
	try:
		text_content  = results['result']['content'][0]['text']
		response_data = json.loads(text_content)
		response_text = response_data['response']

		# Save raw response for debugging
		debug_path = os.path.join(OUTPUT_DIR, 'last_email_ai_response_raw.txt')
		with open(debug_path, 'w', encoding='utf-8') as f:
			f.write(response_text)
		print(f' 📝 Raw response saved: {debug_path}')

		json_text = None

		# Method 1: ```json with newline
		m = re.search(r'```json\n(.*?)```', response_text, re.DOTALL)
		if m:
			json_text = m.group(1)
			print(' ✓ JSON found via ```json markers')

		# Method 2: ```json without newline
		if not json_text:
			m = re.search(r'```json(.*?)```', response_text, re.DOTALL)
			if m:
				json_text = m.group(1).strip()
				print(' ✓ JSON found via ```json markers (no newline)')

		# Method 3: First { to last }
		if not json_text:
			first = response_text.find('{')
			last  = response_text.rfind('}')
			if first != -1 and last > first:
				json_text = response_text[first:last + 1]
				print(' ✓ JSON found via brace matching')

		# Method 4: Try entire response
		if not json_text:
			try:
				data = json.loads(response_text)
				print(' ✓ Entire response parsed as JSON')
				return data
			except json.JSONDecodeError:
				pass

		if not json_text:
			print(f'\n ❌ Could not extract JSON from response')
			print(f' Preview: {response_text[:300]}')
			return None

		data = json.loads(json_text)

		# Save extracted JSON for debugging
		extracted_path = os.path.join(OUTPUT_DIR, 'last_email_ai_response_extracted.json')
		with open(extracted_path, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent='\t')
		print(f' ✅ JSON extracted and saved: {extracted_path}')

		return data

	except KeyError as e:
		print(f'\n ❌ Unexpected response structure — missing key: {e}')
		return None
	except json.JSONDecodeError as e:
		print(f'\n ❌ Invalid JSON: {e}')
		return None
	except Exception as e:
		print(f'\n ❌ Unexpected error in strip_to_json: {e}')
		import traceback
		traceback.print_exc()
		return None


# =============================================================================
# AI Enrichment Call
# =============================================================================

def run_email_enrichment(first_name, last_name, email, entity_name, address, domain, tf_entity_found):
	"""
	Execute the single AI enrichment call for a known person + email.

	Args:
		first_name (str)
		last_name (str)
		email (str)
		entity_name (str)
		address (str)
		domain (str)
		tf_entity_found (bool)

	Returns:
		dict or None: Parsed AI result with 'contacts' and 'company' keys
	"""
	prompt = build_prompt(first_name, last_name, email, entity_name, address, domain, tf_entity_found)

	payload = {
		'jsonrpc': '2.0',
		'id': 6,
		'method': 'tools/call',
		'params': {
			'name': 'process_chat',
			'arguments': {
				'model': AI_MODEL,
				'max_tokens': 8000,
				'messages': [
					{
						'role': 'system',
						'content': (
							'You are a contact research assistant. A land broker needs to call this person '
							'or send them a letter about a land transaction. Return ONLY valid JSON. '
							'Run enformion_enrich_contact for the person — phone number and mailing address '
							'are the most important fields. For every phone and mobile number, include '
							'PhoneSource and MobileSource. Keep descriptions under 200 characters. '
							'No text before or after the JSON.'
						)
					},
					{
						'role': 'user',
						'content': prompt
					}
				],
				'tools': [
					'web_search',
					'enformion_enrich_contact',
					'enformion_business_search',
					'url_context_query'
				]
			}
		}
	}

	print(f'\n{"="*70}')
	print(f' EMAIL ENRICHMENT: {first_name} {last_name} | {email}')
	print(f'{"="*70}\n')

	start = time.time()
	try:
		results  = ai.ask_kablewy_ai(payload)
		duration = time.time() - start
		print(f'\n ⏱️  AI call duration: {duration:.1f}s')
		return strip_to_json(results)
	except Exception as e:
		duration = time.time() - start
		print(f'\n ❌ AI call failed after {duration:.1f}s: {e}')
		import traceback
		traceback.print_exc()
		return None


# =============================================================================
# File Cache
# =============================================================================

def check_if_email_file_exists(email):
	"""
	Check for a previously saved result file for this email address.
	Returns parsed JSON if found, None otherwise.

	Args:
		email (str): Email address used as filename key

	Returns:
		dict or None
	"""
	safe_email = email.replace('@', '_at_').replace('.', '_')
	matches    = []

	try:
		for filename in os.listdir(OUTPUT_DIR):
			if safe_email.upper() in filename.upper() and filename.endswith('.json'):
				matches.append(filename)
	except FileNotFoundError:
		return None

	if not matches:
		return None

	matches.sort()
	most_recent = matches[-1]
	file_path   = os.path.join(OUTPUT_DIR, most_recent)

	with open(file_path, 'r', encoding='utf-8') as f:
		return json.load(f)


def save_results_to_file(data, email):
	"""
	Save combined_data dict to a JSON file keyed on email address.

	Args:
		data (dict): combined_data
		email (str): Email address

	Returns:
		str or None: File path saved, or None on error
	"""
	if not data:
		return None

	timestamp  = datetime.now().strftime('%Y%m%d_%H%M%S')
	safe_email = email.replace('@', '_at_').replace('.', '_')
	filename   = f'Email_Search_{safe_email}_{timestamp}.json'
	file_path  = os.path.join(OUTPUT_DIR, filename)

	try:
		with open(file_path, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
		print(f' ✅ Results saved: {file_path}')
		return file_path
	except Exception as e:
		print(f' ❌ Error saving file: {e}')
		return None


# =============================================================================
# Result Assembly
# =============================================================================

def assemble_combined_data(ai_result, tf_entity_record, domain, entity_name,
                           tf_contact_block=None, entity_resolution_method=None):
	"""
	Build the combined_data dict from AI result, optional TF entity record,
	and optional TF contact block.

	Priority rules:
		- Contact: TF record is authoritative (AID populated). AI fills blank fields.
		- Company: TF entity is authoritative (EID populated). AI fills blank fields.
		  If no TF entity, AI company block is used with EID = ''.

	Args:
		ai_result (dict):             Parsed AI response with 'contacts' and 'company' keys
		tf_entity_record (dict|None): TF Entity record from find_entity_by_domain() or find_entity_for_person()
		domain (str):                 Email domain
		entity_name (str):            Input entity name or 'None'
		tf_contact_block (dict|None): TF Person record converted via tf_person_to_contact_block()
		entity_resolution_method (str|None): How entity was found (for metadata)

	Returns:
		dict: combined_data with keys:
			'companies'       → Fox Hunter company structure (EID on primary)
			'contacts'        → list of enriched contact dicts (AID on index 0)
			'search_metadata' → provenance info
	"""
	contacts   = ai_result.get('contacts', [])
	ai_company = ai_result.get('company')
	metadata   = ai_result.get('search_metadata', {})

	# --- Contact block: TF is authoritative, AI fills gaps ---
	if tf_contact_block:
		if contacts:
			ai_contact = contacts[0]
			# Fill blank TF fields from AI result
			for field in ('Phone', 'PersonMobilePhone', 'BillingStreet', 'BillingCity',
			              'BillingState', 'BillingPostalCode', 'PersonTitle',
			              'LinkedIn_Url__c', 'Category__c', 'Description'):
				if not tf_contact_block.get(field) and ai_contact.get(field):
					tf_contact_block[field] = ai_contact[field]
					# Update source flags when AI provides the value
					if field == 'Phone':
						tf_contact_block['PhoneSource'] = 'ai'
					elif field == 'PersonMobilePhone':
						tf_contact_block['MobileSource'] = 'ai'
			# Replace index 0 with the TF-authoritative block; keep any additional AI contacts
			contacts = [tf_contact_block] + contacts[1:]
		else:
			contacts = [tf_contact_block]

	# --- Company block: TF is authoritative, AI fills gaps ---
	if tf_entity_record:
		company_block = tf_record_to_company_block(tf_entity_record)
		if ai_company:
			for field in ('Phone', 'Website', 'LinkedIn_Url__c', 'Description'):
				if not company_block.get(field) and ai_company.get(field):
					company_block[field] = ai_company[field]
	elif ai_company:
		company_block       = ai_company
		company_block['EID'] = ''		# No TF entity found yet
	else:
		company_block = None

	# Inject company name into contact Company__c if contact is missing it
	if company_block and contacts:
		for contact in contacts:
			if not contact.get('Company__c') and company_block.get('Name'):
				contact['Company__c'] = company_block['Name']

	# --- Build companies structure matching Fox Hunter format ---
	if company_block:
		companies = {
			'primary': {
				'Name':                    company_block.get('Name', ''),
				'BillingStreet':           company_block.get('BillingStreet', ''),
				'BillingCity':             company_block.get('BillingCity', ''),
				'BillingState':            company_block.get('BillingState', ''),
				'BillingPostalCode':       company_block.get('BillingPostalCode', ''),
				'Phone':                   company_block.get('Phone', ''),
				'Website':                 company_block.get('Website', ''),
				'LinkedIn_Url__c':         company_block.get('LinkedIn_Url__c', ''),
				'Category__c':             company_block.get('Category__c', ''),
				'Description':             company_block.get('Description', ''),
				'EID':                     company_block.get('EID', ''),
				'domain_match_confidence': company_block.get('domain_match_confidence', 'none'),
				'domain_match_notes':      company_block.get('domain_match_notes', ''),
				'source':                  company_block.get('source', 'ai'),
				'relationship':            'primary_search_target'
			},
			'parent_company': None,
			'subsidiaries':   [],
			'affiliates':     []
		}
	else:
		companies = {
			'primary':        None,
			'parent_company': None,
			'subsidiaries':   [],
			'affiliates':     []
		}

	# --- Build final metadata ---
	search_metadata = {
		'search_date':              datetime.now().strftime('%Y-%m-%d'),
		'search_method':            'email_enrichment',
		'email_domain':             domain,
		'domain_is_generic':        is_generic_domain(domain) if domain else True,
		'tf_person_resolved':       tf_contact_block is not None,
		'tf_entity_resolved':       tf_entity_record is not None,
		'entity_resolution_method': entity_resolution_method,
		'company_found':            company_block is not None,
		'sources_used':             metadata.get('sources_used', []),
		'notes':                    metadata.get('notes', '')
	}

	return {
		'companies':       companies,
		'contacts':        contacts,
		'search_metadata': search_metadata
	}


# =============================================================================
# Summary Printer
# =============================================================================

def print_summary(combined_data, email):
	"""Print a readable summary of enrichment results to console."""

	lines = []
	lines.append(f'\n{"="*70}')
	lines.append(f' EMAIL ENRICHMENT RESULTS: {email}')
	lines.append(f'{"="*70}')

	meta = combined_data.get('search_metadata', {})
	lines.append(f' Domain:               {meta.get("email_domain", "N/A")}')
	lines.append(f' Generic domain:       {meta.get("domain_is_generic", "N/A")}')
	lines.append(f' TF person found:      {meta.get("tf_person_resolved", False)}')
	lines.append(f' TF entity found:      {meta.get("tf_entity_resolved", False)}')
	lines.append(f' Entity via:           {meta.get("entity_resolution_method", "N/A")}')
	lines.append(f' Company found:        {meta.get("company_found", False)}')

	companies = combined_data.get('companies', {})
	primary   = companies.get('primary')
	if primary:
		lines.append(f'\n COMPANY:')
		lines.append(f'   Name:       {primary.get("Name", "N/A")}')
		lines.append(f'   Address:    {primary.get("BillingStreet", "N/A")}')
		lines.append(f'               {primary.get("BillingCity", "")}, {primary.get("BillingState", "")} {primary.get("BillingPostalCode", "")}')
		lines.append(f'   EID:        {primary.get("EID", "N/A")}')
		lines.append(f'   Source:     {primary.get("source", "N/A")} (confidence: {primary.get("domain_match_confidence", "N/A")})')

	contacts = combined_data.get('contacts', [])
	lines.append(f'\n CONTACTS: {len(contacts)}')
	for idx, c in enumerate(contacts, 1):
		name       = f'{c.get("FirstName", "")} {c.get("MiddleName__c", "")} {c.get("LastName", "")}'.strip()
		phone_src  = c.get('PhoneSource', '')
		mobile_src = c.get('MobileSource', '')
		lines.append(f'\n [{idx}] {name}')
		lines.append(f'     AID:     {c.get("AID", "N/A")}')
		lines.append(f'     Title:   {c.get("PersonTitle", "N/A")}')
		lines.append(f'     Company: {c.get("Company__c", "N/A")}')
		lines.append(f'     Phone:   {c.get("Phone", "N/A")}  [{phone_src}]')
		lines.append(f'     Mobile:  {c.get("PersonMobilePhone", "N/A")}  [{mobile_src}]')
		lines.append(f'     Address: {c.get("BillingStreet", "N/A")}')
		lines.append(f'              {c.get("BillingCity", "")}, {c.get("BillingState", "")} {c.get("BillingPostalCode", "")}')
		lines.append(f'     Email:   {c.get("PersonEmail", "N/A")}')
		lines.append(f'     LinkedIn:{c.get("LinkedIn_Url__c", "N/A")}')
		lines.append(f'     Category:{c.get("Category__c", "N/A")}')

	lines.append(f'\n{"="*70}\n')
	print('\n'.join(lines))


# =============================================================================
# Main Entry Point
# =============================================================================

def main(service, first_name, last_name, email, entity_name='None', address='None'):
	"""
	Main entry point for email-based contact enrichment.

	Replaces acc.find_create_account_entity + acc.find_create_account_person
	for the MC_Clicks_Opens_to_TF workflow.

	Args:
		service:           TerraForce service object. If None, all TF lookups are skipped.
		first_name (str):  Person's first name
		last_name (str):   Person's last name
		email (str):       Person's email address (confirmed from MailChimp)
		entity_name (str): Company name if known, else 'None'
		address (str):     Property/context address for enrichment hint, else 'None'

	Returns:
		dict: combined_data with keys:
			'companies'       → Fox Hunter company structure dict
			                    primary['EID'] = TF Entity Account Id ('' if not found)
			'contacts'        → list of enriched contact dicts
			                    contacts[0]['AID'] = TF Person Account Id ('' if not found)
			'search_metadata' → search provenance info

	Lookup flow:
		1. TF person lookup by email           → populates contact block + AID
		2. Entity resolution from person (×3)  → Company__c / ParentId / Deal
		3. Fallback: TF entity by domain       → only if person not found in TF
		4. AI enrichment                       → fills gaps, skips company if TF resolved it
	"""
	total_start = time.time()

	# --- Cache check ---
	cached = check_if_email_file_exists(email)
	if cached:
		print(f'\n ✅ Cached result found for {email}')
		print_summary(cached, email)
		return cached

	# --- Extract domain ---
	domain  = extract_domain(email)
	generic = is_generic_domain(domain) if domain else True
	print(f'\n 📧 Email: {email}')
	print(f'    Domain: {domain}  ({"generic" if generic else "business"})')

	# --- Step 1a: TF person lookup by email (primary path) ---
	tf_person_record          = None
	tf_contact_block          = None
	tf_entity_record          = None
	tf_entity_found           = False
	tf_person_found           = False
	resolved_entity_name      = entity_name
	entity_resolution_method  = None

	if service:
		tf_person_record = find_person_by_email(service, email)
		if tf_person_record:
			tf_person_found  = True
			tf_contact_block = tf_person_to_contact_block(tf_person_record)

			# Step 1b: Resolve entity from person via 3 paths
			print(f'\n 🔍 Searching for associated entity...')
			tf_entity_record, entity_resolution_method = find_entity_for_person(service, tf_person_record)
			if tf_entity_record:
				tf_entity_found      = True
				resolved_entity_name = tf_entity_record.get('Name', entity_name)
				print(f'\n ✅ Entity resolved via [{entity_resolution_method}]: {resolved_entity_name}')

	# --- Step 1c: Fallback — TF entity by domain (only if person not found) ---
	if service and not tf_person_found and domain and not generic:
		tf_entity_record = find_entity_by_domain(service, domain)
		if tf_entity_record:
			tf_entity_found          = True
			resolved_entity_name     = tf_entity_record.get('Name', entity_name)
			entity_resolution_method = 'domain match'
			print(f'\n ✅ Entity resolved via domain match: {resolved_entity_name}')
		else:
			print(f'\n ℹ️  No TF entity found for domain [{domain}] — AI will search')

	elif not service:
		print(f'\n ℹ️  No TF service provided — skipping all TF lookups')

	# --- Step 2: AI enrichment ---
	ai_result = run_email_enrichment(
		first_name, last_name, email,
		resolved_entity_name, address,
		domain, tf_entity_found
	)

	# --- Step 3: Assemble combined_data ---
	if ai_result:
		contacts = ai_result.get('contacts', [])

		# Post-processing: filter entity-as-contact, ensure phone sources
		filter_companies = {}
		if tf_entity_record:
			filter_companies['primary'] = {'Name': tf_entity_record.get('Name', '')}
		elif resolved_entity_name and resolved_entity_name != 'None':
			filter_companies['primary'] = {'Name': resolved_entity_name}

		contacts, filtered_count = filter_entity_as_contact(contacts, filter_companies)
		if filtered_count:
			print(f'\n 🔧 Entity-as-contact filter removed {filtered_count} record(s)')

		contacts = ensure_phone_source_fields(contacts)
		ai_result['contacts'] = contacts

		combined_data = assemble_combined_data(
			ai_result, tf_entity_record, domain, resolved_entity_name,
			tf_contact_block, entity_resolution_method
		)
		combined_data['search_metadata']['entity_contacts_filtered'] = filtered_count

	else:
		# AI failed — return minimal structure with what we know from TF
		print('\n ⚠️  AI enrichment failed — returning minimal structure')

		company_block = tf_record_to_company_block(tf_entity_record) if tf_entity_record else None

		# Build minimal contact from TF person (if found) or raw inputs
		if tf_contact_block:
			minimal_contact = tf_contact_block
		else:
			minimal_contact = {
				'FirstName':            first_name,
				'MiddleName__c':        '',
				'LastName':             last_name,
				'PersonEmail':          email,
				'Company__c':           resolved_entity_name if resolved_entity_name != 'None' else '',
				'Phone':                '',
				'PhoneSource':          'none',
				'PersonMobilePhone':    '',
				'MobileSource':         'none',
				'BillingStreet':        '',
				'BillingCity':          '',
				'BillingState':         '',
				'BillingPostalCode':    '',
				'PersonTitle':          '',
				'Category__c':          '',
				'LinkedIn_Url__c':      '',
				'Description':          '',
				'AID':                  '',
				'priority_rank':        1,
				'enrichment_attempted': False,
				'enrichment_source':    'none'
			}

		combined_data = {
			'companies': {
				'primary': {
					**({
						'Name':                    company_block.get('Name', ''),
						'BillingStreet':           company_block.get('BillingStreet', ''),
						'BillingCity':             company_block.get('BillingCity', ''),
						'BillingState':            company_block.get('BillingState', ''),
						'BillingPostalCode':       company_block.get('BillingPostalCode', ''),
						'Phone':                   company_block.get('Phone', ''),
						'Website':                 company_block.get('Website', ''),
						'LinkedIn_Url__c':         company_block.get('LinkedIn_Url__c', ''),
						'Category__c':             company_block.get('Category__c', ''),
						'Description':             company_block.get('Description', ''),
						'EID':                     company_block.get('EID', ''),
						'domain_match_confidence': company_block.get('domain_match_confidence', 'none'),
						'domain_match_notes':      company_block.get('domain_match_notes', ''),
						'source':                  company_block.get('source', 'none'),
						'relationship':            'primary_search_target'
					} if company_block else {
						'Name': resolved_entity_name if resolved_entity_name != 'None' else '',
						'EID':  '',
						'source': 'none'
					})
				},
				'parent_company': None,
				'subsidiaries':   [],
				'affiliates':     []
			},
			'contacts': [minimal_contact],
			'search_metadata': {
				'search_date':              datetime.now().strftime('%Y-%m-%d'),
				'search_method':            'email_enrichment',
				'email_domain':             domain,
				'domain_is_generic':        generic,
				'tf_person_resolved':       tf_person_found,
				'tf_entity_resolved':       tf_entity_found,
				'entity_resolution_method': entity_resolution_method,
				'company_found':            company_block is not None,
				'notes':                    'AI enrichment failed. Minimal structure returned.',
				'entity_contacts_filtered': 0
			}
		}

	# --- Summary and save ---
	print_summary(combined_data, email)
	save_results_to_file(combined_data, email)

	total_duration = time.time() - total_start
	print(f'\n ⏱️  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)\n')

	return combined_data