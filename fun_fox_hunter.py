# Chat GPT AI Functions - Company & Contact Finder for Salesforce
# Version 0.7 - Two-part search: Company structure first, then contacts
# Fixes: Rate limiting, truncation issues, better error handling
# Uses comprehensive v02 prompts with full search strategy and verification steps

from anyio import Path
import ai
from datetime import datetime
import fun_text_date as td
import json
import os
from pprint import pprint
import time

from fun_fox_hunter_person_detection import (
	is_company, 
	parse_person_names, 
	create_person_only_result,
	detect_and_route
)


def load_company_structure_prompt(company_name, company_address, model):
	"""Load and format the AI prompt for company structure search."""

	with open('F:/Research Department/Code/Prompts/Fox_Hunter_Entity_AI_Prompt_v03.txt', 'r', encoding='utf-8') as file:
		prompt = file.read()
	
	prompt = prompt.replace('**[COMPANY_NAME]**', company_name).replace('**[COMPANY_ADDRESS]**', company_address)
	return prompt

def load_person_prompt(persons: list, address: str) -> str:
	"""Load and format the AI prompt for person contact enrichment."""
	with open('F:/Research Department/Code/Prompts/Find_Person_Contacts_AI_Prompt_v01.txt', 'r', encoding='utf-8') as file:
		prompt = file.read()
	
	# Build person list for the prompt
	person_list = []
	for idx, p in enumerate(persons, 1):
		name = f"{p['FirstName']} {p['MiddleName__c']} {p['LastName']}".replace("  ", " ").strip()
		person_list.append(f"{idx}. {name}")
	
	persons_text = "\n".join(person_list)
	prompt = prompt.replace('**[PERSON_LIST]**', persons_text)
	prompt = prompt.replace('**[PROPERTY_ADDRESS]**', address)
	
	return prompt

def load_contacts_prompt(companies_data):
	"""Load and format the AI prompt for contacts search based on discovered companies."""
	with open('F:/Research Department/Code/Prompts/Find_Contacts_AI_Prompt_v02.txt', 'r', encoding='utf-8') as file:
		prompt = file.read()
	
	# Build company list for the prompt
	company_list = []
	
	if 'primary' in companies_data:
		company_list.append(f"- {companies_data['primary']['Name']} ({companies_data['primary'].get('BillingCity', 'N/A')}, {companies_data['primary'].get('BillingState', 'N/A')})")
	
	if 'parent_company' in companies_data and companies_data['parent_company'] is not None:
		company_list.append(f"- {companies_data['parent_company']['Name']} ({companies_data['parent_company'].get('BillingCity', 'N/A')}, {companies_data['parent_company'].get('BillingState', 'N/A')}) - PARENT COMPANY")
	
	if 'subsidiaries' in companies_data:
		for sub in companies_data['subsidiaries']:
			company_list.append(f"- {sub['Name']} ({sub.get('BillingCity', 'N/A')}, {sub.get('BillingState', 'N/A')}) - Subsidiary")
	
	if 'affiliates' in companies_data:
		for aff in companies_data['affiliates']:
			company_list.append(f"- {aff['Name']} ({aff.get('BillingCity', 'N/A')}, {aff.get('BillingState', 'N/A')}) - Affiliate")
	
	companies_text = "\n".join(company_list)
	prompt = prompt.replace('**[COMPANY_LIST]**', companies_text)
	
	return prompt

def is_json_complete(json_str):
	"""Check if JSON string appears complete by counting braces."""
	if not json_str:
		return False
	
	open_braces = json_str.count('{')
	close_braces = json_str.count('}')
	open_brackets = json_str.count('[')
	close_brackets = json_str.count(']')
	
	# Check if all braces/brackets are balanced
	if open_braces != close_braces or open_brackets != close_brackets:
		return False
	
	# Check if it ends properly (should end with } or ])
	stripped = json_str.rstrip()
	if not stripped.endswith('}') and not stripped.endswith(']'):
		return False
	
	return True

def strip_to_json(results):
	"""Extract JSON from AI response with improved error handling."""
	# Create output directory if it doesn't exist
	output_dir = Path('C:/Users/Public/Public Mapfiles/Contact_Files')
	
	try:
		# Extract the text field from the nested structure
		text_content = results['result']['content'][0]['text']
		
		# First parse the text content as JSON to get the response string
		response_data = json.loads(text_content)
		response_text = response_data['response']
		
		# Save raw response for debugging
		debug_file = output_dir / 'last_ai_response_raw.txt'
		with open(debug_file, 'w', encoding='utf-8') as f:
			f.write(response_text)
		print(f"📝 Raw response saved to: {debug_file}")
		
		# Try multiple extraction methods
		json_text = None
		
		# Method 1: Look for ```json markers
		start_marker = '```json\n'
		end_marker = '\n```'
		start_index = response_text.find(start_marker)
		
		if start_index != -1:
			end_index = response_text.find(end_marker, start_index + len(start_marker))
			if end_index != -1:
				json_text = response_text[start_index + len(start_marker):end_index]
				print("✓ Found JSON using ```json markers")
		
		# Method 2: Look for ```json without newline
		if not json_text:
			start_marker = '```json'
			start_index = response_text.find(start_marker)
			if start_index != -1:
				end_index = response_text.find('```', start_index + len(start_marker))
				if end_index != -1:
					json_text = response_text[start_index + len(start_marker):end_index].strip()
					print("✓ Found JSON using ```json markers (no newline)")
		
		# Method 3: Look for first { to last }
		if not json_text:
			first_brace = response_text.find('{')
			last_brace = response_text.rfind('}')
			if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
				json_text = response_text[first_brace:last_brace + 1]
				print("✓ Found JSON using brace matching")
		
		# Method 4: Try parsing the entire response as JSON
		if not json_text:
			try:
				extracted_data = json.loads(response_text)
				print("✓ Parsed entire response as JSON")
				# Save to output file
				output_file = output_dir / 'last_ai_response_extracted.json'
				with open(output_file, 'w', encoding='utf-8') as f:
					json.dump(extracted_data, f, indent='\t')
				print(f"📝 JSON data extracted and saved to: {output_file}")
				return extracted_data
			except json.JSONDecodeError:
				pass
		
			if not json_text:
				print("\n❌ ERROR: Could not find JSON in response")
				print(f"Response preview (first 500 chars):\n{response_text[:500]}")
				
				# NEW: Create minimal JSON structure when AI returns text instead of JSON
				print("\n⚠️  Attempting to create minimal structure from failed search...")
				minimal_structure = {
					"companies": {
						"primary": {
							"Name": company_name if 'company_name' in locals() else "Unknown",
							"BillingStreet": "",
							"BillingCity": "",
							"BillingState": "",
							"BillingPostalCode": "",
							"Category__c": "",
							"Description": f"AI search failed: {response_text[:200]}",
							"LinkedIn_Url__c": "",
							"Phone": "",
							"Website": "",
							"relationship": "primary_search_target",
							"relationship_description": "Original search target - no information found"
						},
						"parent_company": None,
						"subsidiaries": [],
						"affiliates": []
					},
					"search_metadata": {
						"search_date": datetime.now().strftime('%Y-%m-%d'),
						"sources_used": ["AI search attempted but no results found"],
						"confidence_level": "None",
						"corporate_structure_notes": "No corporate information could be located for this entity"
					}
				}
				return minimal_structure
		
		
		# Validate JSON completeness before parsing
		if not is_json_complete(json_text):
			print("\n⚠️  WARNING: JSON appears incomplete (unbalanced braces)")
			print(f"Open braces: {json_text.count('{')}, Close braces: {json_text.count('}')}")
			print(f"Open brackets: {json_text.count('[')}, Close brackets: {json_text.count(']')}")
			print("\nThis usually means the AI response was truncated.")
			print("The two-part search approach should prevent this.")
			return None
		
		# Parse the extracted JSON
		extracted_data = json.loads(json_text)
		
		# Save to output file
		output_file = output_dir / 'last_ai_response_extracted.json'
		with open(output_file, 'w', encoding='utf-8') as f:
			json.dump(extracted_data, f, indent='\t')
		
		print(f"✅ JSON data extracted and saved to: {output_file}")
		
		return extracted_data
		
	except KeyError as e:
		print(f"\n❌ ERROR: Unexpected response structure - missing key: {e}")
		print("Response structure:")
		pprint(results, depth=2)
		return None
	except json.JSONDecodeError as e:
		print(f"\n❌ ERROR: Invalid JSON format: {e}")
		if json_text:
			print(f"Attempted to parse:\n{json_text[:500]}")
		return None
	except Exception as e:
		print(f"\n❌ ERROR: Unexpected error in strip_to_json: {e}")
		import traceback
		traceback.print_exc()
		return None

def run_company_structure_search(company_name, company_address, model):
	"""
	Part 1: Search for company structure only.
	
	Args:
		company_name (str): Name of the company to search
		company_address (str): Address of the company
		model (str): AI model to use for the search
		
	Returns:
		dict: Company structure data (primary, parent, subsidiaries, affiliates)
	"""
	prompt = load_company_structure_prompt(company_name, company_address, model)
	
	payload = {
		"jsonrpc": "2.0",
		"id": 3,
		"method": "tools/call",
		"params": {
			"name": "process_chat",
			"arguments": {
				"model": model,
				"max_tokens": 32000,  # Increased for comprehensive company structure research
				"messages": [
					{
						"role": "system",
						"content": "You are a business research assistant. Return ONLY valid JSON with company structure information. CRITICAL: Even if you cannot find any information about the company, you MUST return the JSON structure with null/empty values as specified in the prompt. Never return explanatory text without JSON. No explanatory text before or after the JSON. Keep descriptions concise (under 300 characters)."
					},
					{
						"role": "user",
						"content": prompt
					}
				],
				"tools": [
					"web_search",
					"web_search_with_summary",
					"enformion_business_search",
					"parallel_search",
					"url_context_query"
				]
			}
		}
	}
	
	print('\n' + '='*80)
	print(f' PART 1: Finding company structure for: {company_name}')
	print('='*80 + '\n')
	
	ai_start_time = time.time()
	
	try:
		results = ai.ask_kablewy_ai(payload)
		ai_duration = time.time() - ai_start_time
		
		companies_data = strip_to_json(results)
		
		print(f"\n{'='*80}")
		print(f"⏱️  Part 1 Duration: {ai_duration:.2f} seconds ({ai_duration/60:.2f} minutes)")
		print('='*80 + '\n')
		
		return companies_data
		
	except Exception as e:
		ai_duration = time.time() - ai_start_time
		print(f"\n❌ Error during Part 1 (after {ai_duration:.2f} seconds): {e}")
		import traceback
		traceback.print_exc()
		return None

def run_contacts_search(companies_data, model):
	"""
	Part 2: Search for contacts based on discovered companies.
	
	Args:
		companies_data (dict): Company structure from Part 1
		
	Returns:
		list or dict: Contact data
	"""
	prompt = load_contacts_prompt(companies_data)
	
	payload = {
		"jsonrpc": "2.0",
		"id": 4,
		"method": "tools/call",
		"params": {
			"name": "process_chat",
			"arguments": {
				"model": model,
				"max_tokens": 32000,  # Increased for comprehensive contact research
				"messages": [
					{
						"role": "system",
						"content": "You are a business research assistant. Return ONLY valid JSON with contact information. No explanatory text. Include top 5-8 most important contacts only. Keep descriptions concise (under 200 characters each)."
					},
					{
						"role": "user",
						"content": prompt
					}
				],
				"tools": [
					"web_search",
					"enformion_enrich_contact",
					"enformion_business_search",
					"parallel_search",
					"url_context_query"
				]
			}
		}
	}
	
	print('\n' + '='*80)
	print(f' PART 2: Finding contacts for discovered companies')
	print('='*80 + '\n')
	
	# Wait 30 seconds between requests to avoid rate limiting
	print("⏳ Waiting 30 seconds before Part 2 to avoid rate limits...")
	time.sleep(30)
	print("▶️  Starting Part 2 now...")
	
	ai_start_time = time.time()
	
	try:
		results = ai.ask_kablewy_ai(payload)
		ai_duration = time.time() - ai_start_time
		
		contacts_data = strip_to_json(results)
		
		print(f"\n{'='*80}")
		print(f"⏱️  Part 2 Duration: {ai_duration:.2f} seconds ({ai_duration/60:.2f} minutes)")
		print('='*80 + '\n')
		
		return contacts_data
		
	except Exception as e:
		ai_duration = time.time() - ai_start_time
		print(f"\n❌ Error during Part 2 (after {ai_duration:.2f} seconds): {e}")
		import traceback
		traceback.print_exc()
		return None

def run_person_enrichment(persons: list, address: str, model: str):
	"""
	Enrich contact information for individual property owner(s).
	
	Args:
		persons: List of parsed person dicts from parse_person_names()
		address: Property address
		model: AI model to use
		
	Returns:
		dict: Enriched contact data in standard format
	"""
	prompt = load_person_prompt(persons, address)
	
	payload = {
		"jsonrpc": "2.0",
		"id": 5,
		"method": "tools/call",
		"params": {
			"name": "process_chat",
			"arguments": {
				"model": model,
				"max_tokens": 16000,  # Smaller than company search - less data expected
				"messages": [
					{
						"role": "system",
						"content": "You are a contact research assistant. Return ONLY valid JSON with person contact information. No explanatory text. Keep descriptions concise (under 200 characters each)."
					},
					{
						"role": "user",
						"content": prompt
					}
				],
				"tools": [
					"web_search",
					"enformion_enrich_contact",
					"parallel_search",
					"url_context_query"
				]
			}
		}
	}
	
	print('\n' + '='*80)
	print(f' PERSON ENRICHMENT: Finding contact info for property owner(s)')
	print('='*80 + '\n')
	
	ai_start_time = time.time()
	
	try:
		results = ai.ask_kablewy_ai(payload)
		ai_duration = time.time() - ai_start_time
		
		enriched_data = strip_to_json(results)
		
		print(f"\n{'='*80}")
		print(f"⏱️  Person Enrichment Duration: {ai_duration:.2f} seconds ({ai_duration/60:.2f} minutes)")
		print('='*80 + '\n')
		
		return enriched_data
		
	except Exception as e:
		ai_duration = time.time() - ai_start_time
		print(f"\n❌ Error during person enrichment (after {ai_duration:.2f} seconds): {e}")
		import traceback
		traceback.print_exc()
		return None
	
def combine_results(companies_data, contacts_data):
	"""
	Combine company structure and contacts into final format.
	
	Args:
		companies_data (dict): From Part 1
		contacts_data (dict or list): From Part 2
		
	Returns:
		dict: Combined data in expected format
	"""
	combined = {
		"companies": companies_data,
		"contacts": contacts_data if isinstance(contacts_data, list) else contacts_data.get('contacts', []),
		"search_metadata": {
			"search_date": datetime.now().strftime('%Y-%m-%d'),
			"search_method": "two_part_search",
			"confidence_level": "high",
			"notes": "Company structure and contacts searched separately for better reliability"
		}
	}
	
	# Merge metadata if it exists in either result
	if isinstance(companies_data, dict) and 'search_metadata' in companies_data:
		combined['search_metadata'].update(companies_data['search_metadata'])
	
	if isinstance(contacts_data, dict) and 'search_metadata' in contacts_data:
		combined['search_metadata'].update(contacts_data['search_metadata'])
	
	return combined

def validate_sf_data(data):
	"""
	Validate that required Salesforce fields are present.
	
	Args:
		data (dict): Parsed company/contact data
		
	Returns:
		tuple: (is_valid, missing_fields)
	"""
	if not data:
		return False, ["No data provided"]
	
	required_company_fields = ['Name', 'BillingStreet', 'BillingCity', 'BillingState', 'BillingPostalCode']
	required_person_fields = ['FirstName', 'LastName', 'PersonTitle']
	
	missing = []
	
	# Check companies structure (new format)
	if 'companies' in data:
		companies = data['companies']
		
		# Check primary company (skip if None - indicates person owner, not company)
		if 'primary' in companies and companies['primary'] is not None:
			for field in required_company_fields:
				if field not in companies['primary'] or not companies['primary'][field]:
					missing.append(f"companies.primary.{field}")
		# If primary is None, this is a person owner - company fields not required
	else:
		# Check legacy company structure
		if 'company' not in data:
			missing.append("company object")
		else:
			for field in required_company_fields:
				if field not in data['company'] or not data['company'][field]:
					missing.append(f"company.{field}")
	
	# Check contacts
	if 'contacts' not in data or not data['contacts']:
		missing.append("contacts array (should contain at least one contact)")
	else:
		for idx, contact in enumerate(data['contacts']):
			for field in required_person_fields:
				if field not in contact or not contact[field]:
					missing.append(f"contacts[{idx}].{field}")
	
	return len(missing) == 0, missing

def print_summary(data, company_name):
	"""
	Print a formatted summary of the search results.
	
	Args:
		data (dict): The complete search results
		company_name (str): Original company name searched
	"""
	output_lines = []
	
	output_lines.append("\n" + "="*80)
	output_lines.append(f"SEARCH RESULTS FOR: {company_name}")
	output_lines.append("="*80)
	
	# Display Company Structure (new format)
	if 'companies' in data:
		companies = data['companies']
		
		# Display Primary Company
		if 'primary' in companies and companies['primary'] is not None:
			primary = companies['primary']
			output_lines.append("\n\nPRIMARY COMPANY (Search Target):")
			output_lines.append("-" * 80)
			output_lines.append(f"Name:        {primary.get('Name', 'N/A')}")
			output_lines.append(f"Address:     {primary.get('BillingStreet', 'N/A')}")
			output_lines.append(f"             {primary.get('BillingCity', 'N/A')}, {primary.get('BillingState', 'N/A')} {primary.get('BillingPostalCode', 'N/A')}")
			output_lines.append(f"Phone:       {primary.get('Phone', 'N/A')}")
			output_lines.append(f"Website:     {primary.get('Website', 'N/A')}")
			output_lines.append(f"LinkedIn:    {primary.get('LinkedIn_Url__c', 'N/A')}")
			output_lines.append(f"Category:    {primary.get('Category__c', 'N/A')}")
			
			if primary.get('relationship_description'):
				output_lines.append(f"Relationship: {primary.get('relationship_description')}")
			
			desc = primary.get('Description', 'N/A')
			if desc and desc != 'N/A':
				output_lines.append(f"Description: {desc}")
		
		# Display Parent Company
		if 'parent_company' in companies and companies['parent_company']:
			parent = companies['parent_company']
			output_lines.append("\n\nPARENT COMPANY:")
			output_lines.append("-" * 80)
			output_lines.append(f"Name:        {parent.get('Name', 'N/A')}")
			output_lines.append(f"Address:     {parent.get('BillingStreet', 'N/A')}")
			output_lines.append(f"             {parent.get('BillingCity', 'N/A')}, {parent.get('BillingState', 'N/A')} {parent.get('BillingPostalCode', 'N/A')}")
			output_lines.append(f"Phone:       {parent.get('Phone', 'N/A')}")
			output_lines.append(f"Website:     {parent.get('Website', 'N/A')}")
			output_lines.append(f"LinkedIn:    {parent.get('LinkedIn_Url__c', 'N/A')}")
			output_lines.append(f"Category:    {parent.get('Category__c', 'N/A')}")
			
			if parent.get('ownership_percentage'):
				output_lines.append(f"Ownership:   {parent.get('ownership_percentage')}")
			
			if parent.get('relationship_description'):
				output_lines.append(f"Relationship: {parent.get('relationship_description')}")
			
			desc = parent.get('Description', 'N/A')
			if desc and desc != 'N/A':
				output_lines.append(f"Description: {desc}")
		
		# Display Subsidiaries
		if 'subsidiaries' in companies and companies['subsidiaries']:
			output_lines.append(f"\n\nSUBSIDIARIES ({len(companies['subsidiaries'])}):")
			output_lines.append("-" * 80)
			for idx, sub in enumerate(companies['subsidiaries'], 1):
				output_lines.append(f"\n[{idx}] {sub.get('Name', 'N/A')}")
				output_lines.append(f"    Address:      {sub.get('BillingStreet', 'N/A')}")
				output_lines.append(f"                  {sub.get('BillingCity', 'N/A')}, {sub.get('BillingState', 'N/A')} {sub.get('BillingPostalCode', 'N/A')}")
				output_lines.append(f"    Phone:        {sub.get('Phone', 'N/A')}")
				output_lines.append(f"    Website:      {sub.get('Website', 'N/A')}")
				output_lines.append(f"    Category:     {sub.get('Category__c', 'N/A')}")
				
				if sub.get('ownership_percentage'):
					output_lines.append(f"    Ownership:    {sub.get('ownership_percentage')}")
				
				if sub.get('relationship_description'):
					output_lines.append(f"    Relationship: {sub.get('relationship_description')}")
				
				desc = sub.get('Description', 'N/A')
				if desc and desc != 'N/A':
					output_lines.append(f"    Description:  {desc}")
		
		# Display Affiliates
		if 'affiliates' in companies and companies['affiliates']:
			output_lines.append(f"\n\nAFFILIATED COMPANIES ({len(companies['affiliates'])}):")
			output_lines.append("-" * 80)
			for idx, aff in enumerate(companies['affiliates'], 1):
				output_lines.append(f"\n[{idx}] {aff.get('Name', 'N/A')}")
				output_lines.append(f"    Address:      {aff.get('BillingStreet', 'N/A')}")
				output_lines.append(f"                  {aff.get('BillingCity', 'N/A')}, {aff.get('BillingState', 'N/A')} {aff.get('BillingPostalCode', 'N/A')}")
				output_lines.append(f"    Phone:        {aff.get('Phone', 'N/A')}")
				output_lines.append(f"    Website:      {aff.get('Website', 'N/A')}")
				output_lines.append(f"    Category:     {aff.get('Category__c', 'N/A')}")
				
				if aff.get('relationship_description'):
					output_lines.append(f"    Relationship: {aff.get('relationship_description')}")
				
				desc = aff.get('Description', 'N/A')
				if desc and desc != 'N/A':
					output_lines.append(f"    Description:  {desc}")
	
	# Handle legacy single company structure for backwards compatibility
	elif 'company' in data:
		company = data.get('company', {})
		output_lines.append("\nCOMPANY INFORMATION:")
		output_lines.append("-" * 80)
		output_lines.append(f"Name:        {company.get('Name', 'N/A')}")
		output_lines.append(f"Address:     {company.get('BillingStreet', 'N/A')}")
		output_lines.append(f"             {company.get('BillingCity', 'N/A')}, {company.get('BillingState', 'N/A')} {company.get('BillingPostalCode', 'N/A')}")
		output_lines.append(f"Phone:       {company.get('Phone', 'N/A')}")
		output_lines.append(f"Website:     {company.get('Website', 'N/A')}")
		output_lines.append(f"LinkedIn:    {company.get('LinkedIn_Url__c', 'N/A')}")
		output_lines.append(f"Category:    {company.get('Category__c', 'N/A')}")
		
		desc = company.get('Description', 'N/A')
		if desc and desc != 'N/A':
			output_lines.append(f"Description: {desc}")
	
	# Display Contacts
	contacts = data.get('contacts', [])
	output_lines.append(f"\n\n{'='*80}")
	output_lines.append(f"CONTACTS FOUND: {len(contacts)}")
	output_lines.append("="*80)
	
	for idx, contact in enumerate(contacts, 1):
		full_name = f"{contact.get('FirstName', '')} {contact.get('MiddleName__c', '')} {contact.get('LastName', '')}".strip()
		output_lines.append(f"\n[{idx}] {full_name}")
		output_lines.append(f"    Title:           {contact.get('PersonTitle', 'N/A')}")
		output_lines.append(f"    Company:         {contact.get('Company__c', 'N/A')}")
		
		if contact.get('company_association'):
			output_lines.append(f"    Association:     {contact.get('company_association')}")
		
		output_lines.append(f"    Email:           {contact.get('PersonEmail', 'N/A')}")
		output_lines.append(f"    Phone:           {contact.get('Phone', 'N/A')}")
		output_lines.append(f"    Mobile:          {contact.get('PersonMobilePhone', 'N/A')}")
		output_lines.append(f"    LinkedIn:        {contact.get('LinkedIn_Url__c', 'N/A')}")
		
		desc = contact.get('Description', 'N/A')
		if desc and desc != 'N/A':
			output_lines.append(f"    Description:     {desc}")
		
		output_lines.append(f"    Priority Rank:   {contact.get('priority_rank', 'N/A')}")
	
	# Display Search Metadata
	metadata = data.get('search_metadata', {})
	output_lines.append(f"\n\n{'='*80}")
	output_lines.append("SEARCH METADATA")
	output_lines.append("="*80)
	output_lines.append(f"Search Date:  {metadata.get('search_date', 'N/A')}")
	output_lines.append(f"Search Method: {metadata.get('search_method', 'N/A')}")
	output_lines.append(f"Confidence:   {metadata.get('confidence_level', 'N/A')}")
	
	sources = metadata.get('sources_used', [])
	if sources:
		output_lines.append(f"Sources:      {sources[0]}")
		for source in sources[1:]:
			output_lines.append(f"              {source}")
	else:
		output_lines.append(f"Sources:      N/A")
	
	if metadata.get('corporate_structure_notes'):
		output_lines.append(f"\nCorporate Structure Notes:")
		output_lines.append(f"{metadata['corporate_structure_notes']}")
	
	if metadata.get('notes'):
		output_lines.append(f"\nAdditional Notes:")
		output_lines.append(f"{metadata['notes']}")
	
	output_lines.append("="*80 + "\n")
	
	# Join all lines into single output string
	output = "\n".join(output_lines)
	
	# Print to console
	print(output)
	
	# Save to file
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
	filename = f"C:/Users/Public/Public MapFiles/Contact_Files/Company_Search_{safe_name}_{timestamp}_Print_Summary.txt"
	
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			f.write(output)
		print(f"✅ Print summary saved to: {filename}")
	except Exception as e:
		print(f"❌ Error saving print summary file: {e}")

def save_results_to_file(data, company_name):
	"""Save results to a JSON file for later use."""
	if not data:
		return None
	
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
	filename = f"F:/Research Department/Code/Contact Files/Company_Search_{safe_name}_{timestamp}.json"
	
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
		print(f"✅ Results saved to: {filename}")
		return filename
	except Exception as e:
		print(f"❌ Error saving file: {e}")
		return None

def check_if_company_file_exists(company_name):
	"""
	Search for the most recent file matching a company name and return its contents.
	
	Args:
		company_name: Company name to search for in filename
	
	Returns:
		Tuple: (file_path, json_contents) or (None, None) if not found
	"""
	folder_path = r"F:\Research Department\Code\Contact Files"
	safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
	matches = []
	
	for filename in os.listdir(folder_path):
		if safe_name.upper() in filename.upper() and filename.endswith('.json'):
			matches.append(filename)
	
	if not matches:
		return None
	
	# Sort by date/time in filename (YYYYMMDD_HHMMSS) - most recent last
	matches.sort(key=lambda x: x.split('_')[-2] + x.split('_')[-1].replace('.json', ''))
	most_recent = matches[-1]
	
	file_path = os.path.join(folder_path, most_recent)
	
	with open(file_path, 'r', encoding='utf-8') as f:
		contents = json.load(f)
	
	return contents

def main(owner_name: str, address: str):
	"""
	Main execution function with person vs company detection.
	
	Args:
		owner_name: Owner name from parcel data (could be person or company)
		address: Property address
		
	Returns:
		dict: Combined company/contact data in standard format
	"""
	
	# Check if already researched
	combined_data = check_if_company_file_exists(owner_name)
	if combined_data:
		print(f"\n✅ Existing data found for '{owner_name}'")
		return combined_data
	
	model = "gpt-5.2"
	# model = "gemini-3-pro-preview"
	# model = "gemini-2.5-flash"
	# model = "claude-sonnet-4-5-20250929"
	# PART 1: Get company structure

	print(f"\n🔍 Analyzing owner: {owner_name}")
	
	if is_company(owner_name):
		print(f"   → Detected as COMPANY - proceeding with corporate structure search")
		
		# Original two-part company flow
		# PART 1: Get company structure
		print("\n🔍 Starting two-part search process...")
		companies_data = run_company_structure_search(owner_name, address, model)
		
		if not companies_data:
			print("\n❌ Part 1 failed - cannot continue to Part 2")
			return None
		
		print("\n✅ Part 1 complete - Company structure found")
		
		# Show what was found
		if 'companies' in companies_data:
			comp_obj = companies_data['companies']
		else:
			comp_obj = companies_data
		
		print(f"\nCompanies discovered:")
		if 'primary' in comp_obj:
			print(f"  • Primary: {comp_obj['primary'].get('Name', 'N/A')}")
		if 'parent_company' in comp_obj and comp_obj['parent_company'] is not None:
			print(f"  • Parent: {comp_obj['parent_company'].get('Name', 'N/A')}")
		if 'subsidiaries' in comp_obj:
			print(f"  • Subsidiaries: {len(comp_obj['subsidiaries'])}")
		if 'affiliates' in comp_obj:
			print(f"  • Affiliates: {len(comp_obj['affiliates'])}")
		
		# PART 2: Get contacts for all discovered companies
		contacts_data = run_contacts_search(
			comp_obj if 'companies' not in companies_data else companies_data['companies'], 
			model
		)
		
		if not contacts_data:
			print("\n⚠️  Part 2 failed - but we have company structure")
			combined_data = {
				"companies": comp_obj, 
				"contacts": [], 
				"search_metadata": {
					"partial_results": True,
					"search_date": datetime.now().strftime('%Y-%m-%d'),
					"notes": "Part 2 (contacts) failed but company structure is available"
				}
			}
		else:
			print("\n✅ Part 2 complete - Contacts found")
			
			if 'companies' in companies_data:
				combined_data = companies_data
				combined_data['contacts'] = contacts_data if isinstance(contacts_data, list) else contacts_data.get('contacts', [])
				if isinstance(contacts_data, dict) and 'search_metadata' in contacts_data:
					if 'search_metadata' not in combined_data:
						combined_data['search_metadata'] = {}
					combined_data['search_metadata'].update(contacts_data['search_metadata'])
			else:
				combined_data = combine_results(comp_obj, contacts_data)
	
	else:
		# =======================================================================
		# NEW: Handle person owner(s)
		# =======================================================================
		print(f"   → Detected as PERSON - proceeding with contact enrichment")
		
		# Parse person names from parcel format
		persons = parse_person_names(owner_name, address)
		
		if not persons:
			print(f"\n❌ Could not parse person name: {owner_name}")
			return None
		
		print(f"\n👤 Parsed {len(persons)} person(s):")
		for p in persons:
			name = f"{p['FirstName']} {p['MiddleName__c']} {p['LastName']}".replace("  ", " ").strip()
			print(f"   • {name}")
		
		# Create initial structure with parsed names
		search_date = datetime.now().strftime('%Y-%m-%d')
		initial_data = create_person_only_result(persons, address, search_date)
		
		# Enrich contact information via AI
		enriched_data = run_person_enrichment(persons, address, model)
		
		if enriched_data and 'contacts' in enriched_data:
			combined_data = enriched_data
			print(f"\n✅ Contact enrichment complete - {len(enriched_data.get('contacts', []))} contact(s) found")
		else:
			# Use initial parsed data if enrichment fails
			print("\n⚠️  Contact enrichment failed - using parsed names only")
			combined_data = initial_data
			combined_data['search_metadata']['notes'] = "AI enrichment failed. Names parsed from parcel records only."
	
	# ==========================================================================
	# Common processing for both paths
	# ==========================================================================
	
	# Validate the combined data
	is_valid, missing = validate_sf_data(combined_data)
	
	if not is_valid:
		print("\n⚠️  WARNING: Missing required Salesforce fields:")
		for field in missing:
			print(f"   - {field}")
		print()
	else:
		print("\n✅ All required Salesforce fields are present\n")
	
	# Print summary
	print_summary(combined_data, owner_name)
	
	# Save to file
	save_results_to_file(combined_data, owner_name)
	
	return combined_data


# =============================================================================
# QUICK REFERENCE: Detection Logic
# =============================================================================
#
# COMPANY INDICATORS (routes to company search):
#   - LLC, INC, CORP, LTD, LP, LLP
#   - TRUST, ESTATE, FOUNDATION
#   - COMPANY, ENTERPRISES, HOLDINGS
#   - PROPERTIES, INVESTMENTS, DEVELOPMENT
#   - BANK, CREDIT UNION
#   - CHURCH, SCHOOL, GOVERNMENT entities
#   - Any numbered address entity (e.g., "123 MAIN ST HOLDINGS")
#
# PERSON PATTERNS (routes to person enrichment):
#   - LASTNAME FIRSTNAME [MIDDLE]
#   - LASTNAME FIRSTNAME & FIRSTNAME (couples)
#   - LASTNAME FIRSTNAME LASTNAME FIRSTNAME (couples with repeated last name)
#   - Names with ET UX, ET VIR, ET AL (spouse/family indicators)
#
# =============================================================================