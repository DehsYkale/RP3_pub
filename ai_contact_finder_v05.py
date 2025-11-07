# Chat GPT AI Functions - Company & Contact Finder for Salesforce
# Version 0.5 - Cleaner JSON extraction using strip_to_json
# Fixed: Strips HTML comments and text before JSON object

from anyio import Path
import ai
from datetime import datetime
import fun_text_date as td
import json
from pprint import pprint


def load_ai_prompt(company_name, company_address):
	"""Load and format the AI prompt with company information."""
	with open('F:/Research Department/Code/Databases/Find_Company_Owner_AI_Prompt_v04.txt', 'r', encoding='utf-8') as file:
		prompt = file.read()
	
	prompt = prompt.replace('**[COMPANY_NAME]**', company_name).replace('**[COMPANY_ADDRESS]**', company_address)
	return prompt

def strip_to_json(results):
	# Create output directory if it doesn't exist
	output_dir = Path('C:/Users/Public/Public Mapfiles/M1_Files')

	# Extract the text field from the nested structure
	text_content = results['result']['content'][0]['text']

	# First parse the text content as JSON to get the response string
	response_data = json.loads(text_content)
	response_text = response_data['response']

	# Find the JSON content between ```json and ```
	start_marker = '```json\n'
	end_marker = '\n```'

	start_index = response_text.find(start_marker)
	end_index = response_text.find(end_marker, start_index + len(start_marker))

	json_text = response_text[start_index + len(start_marker):end_index]

	# Parse the extracted JSON
	extracted_data = json.loads(json_text)

	# Save to output file
	output_file = output_dir / 'Ashton_Gray_Development_contacts_SCRIPT.json'
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(extracted_data, f, indent='\t')

	print(f"JSON data extracted and saved to: {output_file}")


	print('here1')
	pprint(extracted_data)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	
	return extracted_data

def run_ai_company_search(company_name, company_address):
	"""
	Run AI search for company and contact information.
	
	Args:
		company_name (str): Name of the company to search
		company_address (str): Address of the company
		
	Returns:
		dict: Structured company and contact data ready for Salesforce
	"""
	prompt = load_ai_prompt(company_name, company_address)
	
	payload = {
		"jsonrpc": "2.0",
		"id": 3,
		"method": "tools/call",
		"params": {
			"name": "process_chat",
			"arguments": {
				"model": "claude-sonnet-4-5-20250929",
				"messages": [
					{
						"role": "system",
						"content": "You are more than a helpful assistant. You are a highly capable AI productivity partner with access to a powerful suite of tools to run tasks and actions on behalf of the user. You MUST return ONLY valid JSON responses with no explanatory text before or after. The response must be parseable by Python's json.loads() function."
					},
					{
						"role": "user",
						"content": prompt
					}
				],
				"tools": [
					"web_search",
					"web_search_with_summary",
					"enformion_enrich_contact",
					"enformion_business_search",
					"parallel_search",
					"url_context_query"				
				]
			}
		}
	}
	
	print('\n' + '='*80)
	print(f' Running Kablewy AI request for: {company_name}')
	print('='*80 + '\n')
	
	try:
		results = ai.ask_kablewy_ai(payload)

		# Strip everything before the JSON object
		dContact_info = strip_to_json(results)

		return dContact_info

	except Exception as e:
		print(f"\n❌ Error during AI request: {e}")
		import traceback
		traceback.print_exc()
		return None

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
	
	# Check company fields
	if 'company' not in data:
		missing.append("company object")
	else:
		for field in required_company_fields:
			if field not in data['company'] or not data['company'][field]:
				missing.append(f"company.{field}")
	
	# Check contacts
	if 'contacts' not in data or not data['contacts']:
		missing.append("contacts array (no contacts found)")
	else:
		for idx, contact in enumerate(data['contacts']):
			for field in required_person_fields:
				if field not in contact or not contact[field]:
					missing.append(f"contacts[{idx}].{field}")
	
	return len(missing) == 0, missing

def print_summary(data):
	"""Print a formatted summary of the search results."""
	if not data:
		print("\n❌ No data returned from search")
		return
	
	print("\n" + "="*80)
	print("COMPANY INFORMATION")
	print("="*80)
	
	company = data.get('company', {})
	print(f"Name:        {company.get('Name', 'N/A')}")
	print(f"Address:     {company.get('BillingStreet', 'N/A')}")
	print(f"             {company.get('BillingCity', 'N/A')}, {company.get('BillingState', 'N/A')} {company.get('BillingPostalCode', 'N/A')}")
	print(f"Phone:       {company.get('Phone', 'N/A')}")
	print(f"Website:     {company.get('Website', 'N/A')}")
	print(f"LinkedIn:    {company.get('LinkedIn_Url__c', 'N/A')}")
	print(f"Category:    {company.get('Category__c', 'N/A')}")
	
	desc = company.get('Description', 'N/A')
	if desc and desc != 'N/A' and len(desc) > 100:
		print(f"Description: {desc[:100]}...")
	else:
		print(f"Description: {desc}")
	
	contacts = data.get('contacts', [])
	print(f"\n{'='*80}")
	print(f"CONTACTS FOUND: {len(contacts)}")
	print("="*80)
	
	for idx, contact in enumerate(contacts, 1):
		full_name = f"{contact.get('FirstName', '')} {contact.get('MiddleName__c', '')} {contact.get('LastName', '')}".strip()
		print(f"\n[{idx}] {full_name}")
		print(f"    Title:       {contact.get('PersonTitle', 'N/A')}")
		print(f"    Email:       {contact.get('PersonEmail', 'N/A')}")
		print(f"    Phone:       {contact.get('Phone', 'N/A')}")
		print(f"    Mobile:      {contact.get('PersonMobilePhone', 'N/A')}")
		print(f"    LinkedIn:    {contact.get('LinkedIn_Url__c', 'N/A')}")
		
		desc = contact.get('Description', 'N/A')
		if desc and desc != 'N/A' and len(desc) > 80:
			print(f"    Description: {desc[:80]}...")
		else:
			print(f"    Description: {desc}")
		
		print(f"    Priority:    {contact.get('priority_rank', 'N/A')}")
	
	metadata = data.get('search_metadata', {})
	print(f"\n{'='*80}")
	print("SEARCH METADATA")
	print("="*80)
	print(f"Confidence:  {metadata.get('confidence_level', 'N/A')}")
	print(f"Sources:     {', '.join(metadata.get('sources_used', ['N/A']))}")
	if metadata.get('notes'):
		print(f"Notes:       {metadata['notes']}")
	print("="*80 + "\n")

def save_results_to_file(data, company_name):
	"""Save results to a JSON file for later use."""
	if not data:
		return None
	
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
	filename = f"C:/Users/Public/Public MapFiles/M1_Files/Company_Search_{safe_name}_{timestamp}.json"
	
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
		print(f"✅ Results saved to: {filename}")
		return filename
	except Exception as e:
		print(f"❌ Error saving file: {e}")
		return None

def main(company, address):
	"""Main execution function."""
	
	# Run the search
	dContact_info = run_ai_company_search(company, address)
	
	if dContact_info:
		# Validate the data
		is_valid, missing = validate_sf_data(dContact_info)
		
		if not is_valid:
			print("\n⚠️  WARNING: Missing required Salesforce fields:")
			for field in missing:
				print(f"   - {field}")
			print()
		else:
			print("\n✅ All required Salesforce fields are present\n")
		
		# Print summary
		print_summary(dContact_info)
		
		# Save to file
		save_results_to_file(dContact_info, company)

		# Return the structured data for further processing
		return dContact_info
	else:
		print("\n❌ Search failed or returned no results")
		return None

if __name__ == "__main__":
	# Example search
	company = "Ashton Gray Development"
	address = "101 Parklane Blvd Ste 102, Sugar Land, TX 77478"

	ui = td.uInput('\n Company Name... > ')
	if ui.strip() != '':
		company = ui
		address = td.uInput('\n Company Address... > ')
		if address.strip() == '':
			exit('\n No address provided. Terminating program...')
	
	print(f"\n Searching for company: {company}\n Address: {address}\n")

	# Run the search
	dContact_info = main(company, address)
	
	# If you want to see the raw JSON structure:
	# pprint(dContact_info, width=120)

# TODO: Add function to actually create/update Salesforce Account records using the structured data
# TODO: Add batch processing capability for multiple companies
# TODO: Add error handling for duplicate detection in Salesforce

