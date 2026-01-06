import bb
import json
import fjson
import fun_login
import fun_text_date as td
from pprint import pprint


# Function to check if company name exists
def check_company_name_exists(service, company_name):
	"""Query TF to see if a company with this exact name exists"""
	where_clause = f"Name = '{company_name}'"
	results = bb.tf_query_3(service, 'Entity', where_clause, fields='default')

	if results and len(results) > 0:
		print(f" ✓ FOUND {len(results)} match(es) in Terraforce:")
		for idx, record in enumerate(results, 1):
			print(f"\n  Match #{idx}:")
			print(f"    Salesforce ID: {record.get('Id', 'None')}")
			print(f"    Name: {record.get('Name', 'None')}")
			print(f"    Category: {record.get('Category__c', 'None')}")
			print(f"    Address: {record.get('BillingStreet', 'None')}, {record.get('BillingCity', 'None')}, {record.get('BillingState', 'None')}")
			print(f"    Phone: {record.get('Phone', 'None')}")
	else:
		print(" ✗ NOT FOUND in Terraforce")
	return results

def check_address_exists(service, street, city, state, zip_code):
	"""Query TF to see if an address exists"""
	where_clause = (f"BillingStreet = '{street}' AND "
					f"BillingCity = '{city}' AND "
					f"BillingState = '{state}' AND "
					f"BillingPostalCode = '{zip_code}'")
	results = bb.tf_query_3(service, 'Entity', where_clause, fields='default')
	return results

td.banner('Fox Hunter json to TF v01')

# Load the JSON file
filepath = 'F:/Research Department/Code/Contact Files'
filename = 'Company_Search_TAVARES TWENTY-FIVE I LLC_20251229_114320.json'
fullpath = f'{filepath}/{filename}'

dFox = fjson.getJsonDict(fullpath)

for row in dFox:
	print(f'\n Row: {row}')
	pprint(dFox[row])
# exit()

# Get Terraforce connection
service = fun_login.TerraForce()

# Extract company names to check
primary_company = dFox['companies']['primary']['Name']
if dFox['companies']['parent_company'] is not None:
    parent_company = dFox['companies']['parent_company']['Name']
else:
    parent_company = 'None'

print(f"Checking Terraforce for:\n1. Primary: {primary_company}\n2. Parent: {parent_company}\n")

# Check primary company
print(f"=" * 60)
print(f" Checking Primary Company: {primary_company}")
print(f"=" * 60)
primary_results = check_company_name_exists(service, primary_company)

# Check parent company
print(f"\n{'=' * 60}")
print(f" Checking Parent Company: {parent_company}")
print(f"=" * 60)
parent_results = check_company_name_exists(service, parent_company) if parent_company != 'None' else []

# Summary
print(f"\n{'=' * 60}")
print(" SUMMARY")
print(f"{'=' * 60}")
print(f" Primary Company ({primary_company}): {'EXISTS' if primary_results else 'DOES NOT EXIST'}")
print(f" Parent Company ({parent_company}): {'EXISTS' if parent_results else 'DOES NOT EXIST'}")