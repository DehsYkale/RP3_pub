"""
Salesforce Account Creation/Update Script - Phase 1
Searches for matching companies in Salesforce and asks for user confirmation
"""

import json
import os

from pprint import pprint
import bb
import fun_login
from datetime import datetime
import fun_text_date as td

def load_json_file(file_path):
	"""Load the company data from JSON file"""
	with open(file_path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data

def search_company_by_name(service, company_name):
	"""Search Salesforce for companies matching the name"""
	# Clean the company name for search
	search_name = company_name.replace("'", "\\'")
	
	# Build WHERE clause for partial name match
	where_clause = f"Name LIKE '%{search_name}%' AND IsPersonAccount = false"
	
	# Query using bb.tf_query_3
	records = bb.tf_query_3(service, rec_type='Entity', where_clause=where_clause, limit=10, fields='default')
	
	return records

def search_company_by_address(service, street, city, state, postal_code):
	"""Search Salesforce for companies matching the address"""
	matches = []
	
	# Search by street and city
	if street and city:
		street_clean = street.replace("'", "\\'")
		city_clean = city.replace("'", "\\'")
		where_clause = f"BillingStreet LIKE '%{street_clean}%' AND BillingCity = '{city_clean}' AND IsPersonAccount = false"
		records = bb.tf_query_3(service, rec_type='Entity', where_clause=where_clause, limit=10, fields='default')
		matches.extend(records)
	
	# Search by postal code if no matches yet
	if not matches and postal_code:
		where_clause = f"BillingPostalCode = '{postal_code}' AND IsPersonAccount = false"
		records = bb.tf_query_3(service, rec_type='Entity', where_clause=where_clause, limit=10, fields='default')
		matches.extend(records)
	
	return matches

def display_company_comparison(json_company, sf_matches):
	"""Display the JSON company and potential Salesforce matches side by side"""
	print("\n" + "="*80)
	print("COMPANY FROM JSON FILE:")
	print("="*80)
	print(f"Name:           {json_company.get('Name', '')}")
	print(f"Address:        {json_company.get('BillingStreet', '')}")
	print(f"                {json_company.get('BillingCity', '')}, {json_company.get('BillingState', '')} {json_company.get('BillingPostalCode', '')}")
	print(f"Category:       {json_company.get('Category__c', '')}")
	print(f"Phone:          {json_company.get('Phone', '')}")
	print(f"Website:        {json_company.get('Website', '')}")
	print(f"Description:    {json_company.get('Description', '')[:100]}..." if json_company.get('Description') else "Description:    ")
	
	if sf_matches:
		print("\n" + "="*80)
		print(f"POTENTIAL MATCHES FOUND IN SALESFORCE ({len(sf_matches)}):")
		print("="*80)
		
		for i, match in enumerate(sf_matches, 1):
			print(f"\nMatch #{i}:")
			print(f"  ID:           {match.get('Id', '')}")
			print(f"  Name:         {match.get('Name', '')}")
			print(f"  Address:      {match.get('BillingStreet', '')}")
			print(f"                {match.get('BillingCity', '')}, {match.get('BillingState', '')} {match.get('BillingPostalCode', '')}")
			print(f"  Category:     {match.get('Category__c', '')}")
			print(f"  Phone:        {match.get('Phone', '')}")
			print(f"  Website:      {match.get('Website', '')}")
	else:
		print("\n" + "="*80)
		print("NO MATCHES FOUND IN SALESFORCE")
		print("="*80)

def get_user_confirmation(sf_matches):
	"""Ask user if any of the matches are the same company"""
	if not sf_matches:
		response = input("\nNo matches found. Should we create a new account? (y/n): ").strip().lower()
		return None if response == 'y' else False
	
	print("\n" + "-"*80)
	print("Are any of these matches the same company?")
	print("Enter the match number (1-{}) or [0] for none: ".format(len(sf_matches)), end='')
	
	while True:
		response = input().strip().lower()
		
		if response == '0':
			return None
		
		try:
			match_num = int(response)
			if 1 <= match_num <= len(sf_matches):
				return sf_matches[match_num - 1]
			else:
				print(f"Please enter a number between 1 and {len(sf_matches)}, or [0]: ", end='')
		except ValueError:
			print(f"Please enter a number between 1 and {len(sf_matches)}, or [0]: ", end='')

def process_company(service, json_data, company_type):
	"""Process the primary company from the JSON file"""
	dCompany = json_data['companies'][company_type]
	
	print("\n" + "#"*80)
	print(f"PROCESSING {company_type.upper()} COMPANY")
	print("#"*80)
	
	# Search by name first
	name_matches = search_company_by_name(service, dCompany['Name'])
	
	# Search by address
	address_matches = search_company_by_address(
		service,
		dCompany.get('BillingStreet', ''),
		dCompany.get('BillingCity', ''),
		dCompany.get('BillingState', ''),
		dCompany.get('BillingPostalCode', '')
	)
	
	# Combine matches and remove duplicates
	all_matches = []
	seen_ids = set()
	
	for match in name_matches + address_matches:
		if match['Id'] not in seen_ids:
			all_matches.append(match)
			seen_ids.add(match['Id'])
	
	# Display comparison
	display_company_comparison(dCompany, all_matches)
	
	# Get user confirmation
	selected_match = get_user_confirmation(all_matches)
	
	return {
		'company': dCompany,
		'match': selected_match,
		'match_type': 'existing' if selected_match else 'new'
	}

def update_match_record(service, dMatch):
	"""Update the matched Salesforce record with data from JSON company"""
	# Prepare update data
	AI_entity = dMatch['company']
	TF_entity = dMatch['match']

	dup = {}
	# Cycle through the TF entity fields and update from AI entity if not empty
	for row in TF_entity:
		# Skip attributes metadata and Description field
		if row == 'attributes':
			continue

		print(f'{row}: {TF_entity[row]}')

		# Update Description field by appending new info
		if row == 'Description':
			if AI_entity['Description'] != '':
				if TF_entity['Description'] != 'None':
					if AI_entity['Description'] not in TF_entity['Description']:
						dup['Description'] = TF_entity['Description'] + '\n\n' + AI_entity['Description']
				else:
					dup['Description'] = AI_entity['Description']

		# Check if field exists in AI entity and is not empty
		if TF_entity[row] == 'None':
			if row in AI_entity:
				if AI_entity[row] != '':
					dup[row] = AI_entity[row]

	print('here1')
	pprint(dup)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	
	# Update record in Salesforce
	if dup != {}:
		dup['Id'] = TF_entity['Id']
		dup['type'] = 'Account'
		# up_results = bb.tf_update_3(service, dup)
		up_results = bb.tf_update_with_duplicate_bypass(service, dup)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

def main():
	"""Main function for Phase 1"""

	# Load the JSON file
	file_path = "C:/Users/Public/Public Mapfiles/Contact_Files/Company_Search_Hartford Investments Llc_20251120_105114.json"
	# Check if file exists
	if not os.path.exists(file_path):
		print(f"Error: File not found at {file_path}")
		return
	
	# Load JSON data
	print(f"Loading data from: {file_path}")
	json_data = load_json_file(file_path)
	
	# Connect to Salesforce using fun_login
	service = fun_login.TerraForce()
	
	# Process primary company
	result = process_company(service, json_data, 'primary')

	
	print('here1')
	pprint(result)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	
	
	# Display summary
	print("\n" + "="*80)
	print("PHASE 1 COMPLETE")
	print("="*80)
	print(f"Company: {result['company']['Name']}")
	print(f"Action:  {'Update existing account' if result['match_type'] == 'existing' else 'Create new account'}")
	if result['match']:
		print(f"Match:   {result['match']['Name']} (ID: {result['match']['Id']})")
	print("="*80)

	update_match_record(service, result)

		# Process primary company
	result = process_company(service, json_data, 'parent_company')

	
	print('here1')
	pprint(result)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	
	
	# Display summary
	print("\n" + "="*80)
	print("PHASE 1 COMPLETE")
	print("="*80)
	print(f"Company: {result['company']['Name']}")
	print(f"Action:  {'Update existing account' if result['match_type'] == 'existing' else 'Create new account'}")
	if result['match']:
		print(f"Match:   {result['match']['Name']} (ID: {result['match']['Id']})")
	print("="*80)

	update_match_record(service, result)

if __name__ == "__main__":
	main()