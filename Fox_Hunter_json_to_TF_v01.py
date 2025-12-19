import json
import fun_login
import bb

# Load the JSON file
json_path = "C:/Users/Public/Public Mapfiles/Contact_Files/Company_Search_Hartford Investments Llc_20251120_105114.json"

with open(json_path, 'r') as f:
	data = json.load(f)

# Get Terraforce connection
service = fun_login.TerraForce()

# Extract company names to check
primary_company = data['companies']['primary']['Name']
parent_company = data['companies']['parent_company']['Name']

print(f"Checking Terraforce for:\n1. Primary: {primary_company}\n2. Parent: {parent_company}\n")

# Function to check if company exists
def check_company_exists(service, company_name):
	"""Query TF to see if a company with this exact name exists"""
	where_clause = f"Name = '{company_name}'"
	results = bb.tf_query_3(service, 'Entity', where_clause, fields='default')
	return results

# Check primary company
print(f"=" * 60)
print(f"Checking Primary Company: {primary_company}")
print(f"=" * 60)
primary_results = check_company_exists(service, primary_company)

if primary_results and len(primary_results) > 0:
	print(f"✓ FOUND {len(primary_results)} match(es) in Terraforce:")
	for idx, record in enumerate(primary_results, 1):
		print(f"\n  Match #{idx}:")
		print(f"    Salesforce ID: {record.get('Id', 'N/A')}")
		print(f"    Name: {record.get('Name', 'N/A')}")
		print(f"    Category: {record.get('Category__c', 'N/A')}")
		print(f"    Address: {record.get('BillingStreet', 'N/A')}, {record.get('BillingCity', 'N/A')}, {record.get('BillingState', 'N/A')}")
		print(f"    Phone: {record.get('Phone', 'N/A')}")
else:
	print("✗ NOT FOUND in Terraforce")

# Check parent company
print(f"\n{'=' * 60}")
print(f"Checking Parent Company: {parent_company}")
print(f"=" * 60)
parent_results = check_company_exists(service, parent_company)

if parent_results and len(parent_results) > 0:
	print(f"✓ FOUND {len(parent_results)} match(es) in Terraforce:")
	for idx, record in enumerate(parent_results, 1):
		print(f"\n  Match #{idx}:")
		print(f"    Salesforce ID: {record.get('Id', 'N/A')}")
		print(f"    Name: {record.get('Name', 'N/A')}")
		print(f"    Category: {record.get('Category__c', 'N/A')}")
		print(f"    Address: {record.get('BillingStreet', 'N/A')}, {record.get('BillingCity', 'N/A')}, {record.get('BillingState', 'N/A')}")
		print(f"    Phone: {record.get('Phone', 'N/A')}")
else:
	print("✗ NOT FOUND in Terraforce")

# Summary
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
print(f"Primary Company ({primary_company}): {'EXISTS' if primary_results else 'DOES NOT EXIST'}")
print(f"Parent Company ({parent_company}): {'EXISTS' if parent_results else 'DOES NOT EXIST'}")