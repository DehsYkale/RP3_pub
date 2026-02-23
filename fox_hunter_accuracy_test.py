# Fox Hunter Accuracy Test
# Reads TF contact export, runs fun_fox_hunter.main() for each Owner Entity,
# and writes results to a comparison CSV for accuracy analysis.
# v02 - 2025-02-16 - Added Phone Source and Mobile Source columns

import csv
import fun_fox_hunter
import fun_text_date as td
import time
import traceback


SOURCE_FILE = r'F:\Research Department\Code\Contact Files\Fox Hunter Contact Test v01.csv'
RESULTS_FILE = r'F:\Research Department\Code\Contact Files\Fox Hunter Contact Test Results v08.csv'

FIELDNAMES = [
	'Source',
	'Owner Entity Type',
	'Deal: Deal Name',55
	'PID',
	'Account Name: Account Contact Name',
	'Owner Entity',
	'Account Name: Billing Street',
	'Account Name: Billing City',
	'Account Name: Billing State/Province',
	'Account Name: Billing Zip/Postal Code',
	'Account Name: Phone',
	'Phone Source',
	'Account Name: Mobile',
	'Mobile Source',
	'Account Name: Email',
	'Account Name: Website',
	'Account Name: LinkedIn Url',
	'Account Name: Category',
]


def assemble_address(row):
	"""Build a single address string from CSV address fields."""
	parts = [
		row.get('Account Name: Billing Street', '').strip(),
		row.get('Account Name: Billing City', '').strip(),
		row.get('Account Name: Billing State/Province', '').strip(),
		row.get('Account Name: Billing Zip/Postal Code', '').strip(),
	]
	# Format as "Street, City, ST Zip"
	street = parts[0]
	city = parts[1]
	state = parts[2]
	zipcode = parts[3]
	
	city_state_zip = f"{city}, {state} {zipcode}".strip()
	if street and city_state_zip:
		return f"{street}, {city_state_zip}"
	return street or city_state_zip


def blank_row(deal_name, pid):
	"""Return a dict with shared fields populated, rest blank."""
	return {f: '' for f in FIELDNAMES} | {
		'Deal: Deal Name': deal_name,
		'PID': pid,
	}


def entity_row(company_dict, entity_type, deal_name, pid):
	"""Build a CSV row for a company/entity result from Fox Hunter."""
	row = blank_row(deal_name, pid)
	row['Source'] = 'FH'
	row['Owner Entity Type'] = entity_type
	row['Owner Entity'] = company_dict.get('Name', '')
	row['Account Name: Billing Street'] = company_dict.get('BillingStreet', '')
	row['Account Name: Billing City'] = company_dict.get('BillingCity', '')
	row['Account Name: Billing State/Province'] = company_dict.get('BillingState', '')
	row['Account Name: Billing Zip/Postal Code'] = company_dict.get('BillingPostalCode', '')
	row['Account Name: Phone'] = company_dict.get('Phone', '')
	row['Phone Source'] = ''
	row['Mobile Source'] = ''
	row['Account Name: Website'] = company_dict.get('Website', '')
	row['Account Name: Category'] = company_dict.get('Category__c', '')
	# Account Name, Mobile, Email left blank for entities
	return row


def contact_row(contact_dict, deal_name, pid):
	"""Build a CSV row for a person/contact result from Fox Hunter."""
	row = blank_row(deal_name, pid)
	row['Source'] = 'FH'
	
	# Build full name
	first = contact_dict.get('FirstName', '')
	middle = contact_dict.get('MiddleName__c', '')
	last = contact_dict.get('LastName', '')
	full_name = f"{first} {middle} {last}".replace('  ', ' ').strip()
	
	row['Account Name: Account Contact Name'] = full_name
	row['Owner Entity'] = contact_dict.get('Company__c', '')
	row['Account Name: Billing Street'] = contact_dict.get('BillingStreet', '')
	row['Account Name: Billing City'] = contact_dict.get('BillingCity', '')
	row['Account Name: Billing State/Province'] = contact_dict.get('BillingState', '')
	row['Account Name: Billing Zip/Postal Code'] = contact_dict.get('BillingPostalCode', '')
	row['Account Name: Phone'] = contact_dict.get('Phone', '')
	row['Phone Source'] = contact_dict.get('PhoneSource', '')
	row['Account Name: Mobile'] = contact_dict.get('PersonMobilePhone', '')
	row['Mobile Source'] = contact_dict.get('MobileSource', '')
	row['Account Name: Email'] = contact_dict.get('PersonEmail', '')
	row['Account Name: Website'] = ''
	row['Account Name: LinkedIn Url'] = contact_dict.get('LinkedIn_Url__c', '')
	row['Account Name: Category'] = contact_dict.get('Category__c', '')
	return row


def extract_fh_rows(result, deal_name, pid):
	"""
	Parse fun_fox_hunter result dict into a list of CSV row dicts.
	Entities first (Primary, Parent, Subsidiary, Affiliate), then contacts.
	"""
	rows = []
	if not result:
		return rows
	
	# --- Companies / Entities ---
	companies = result.get('companies', {})
	if companies:
		# Primary
		primary = companies.get('primary')
		if primary and isinstance(primary, dict):
			rows.append(entity_row(primary, 'Primary', deal_name, pid))
		
		# Parent
		parent = companies.get('parent_company')
		if parent and isinstance(parent, dict):
			rows.append(entity_row(parent, 'Parent', deal_name, pid))
		
		# Subsidiaries
		for sub in companies.get('subsidiaries', []):
			if sub and isinstance(sub, dict):
				rows.append(entity_row(sub, 'Subsidiary', deal_name, pid))
		
		# Affiliates
		for aff in companies.get('affiliates', []):
			if aff and isinstance(aff, dict):
				rows.append(entity_row(aff, 'Affiliate', deal_name, pid))
	
	# --- Contacts / Persons ---
	for contact in result.get('contacts', []):
		if contact and isinstance(contact, dict):
			rows.append(contact_row(contact, deal_name, pid))
	
	return rows


def main(limit=None):
	# Read source CSV
	with open(SOURCE_FILE, 'r', encoding='latin-1') as f:
		reader = csv.DictReader(f)
		source_rows = list(reader)
	
	if limit:
		source_rows = source_rows[:limit]
	
	total = len(source_rows)
	print(f"\n{'='*60}")
	print(f"  FOX HUNTER ACCURACY TEST (v08)")
	print(f"  Source rows: {total}")
	print(f"  Phone/Mobile source tracking: ENABLED")
	print(f"{'='*60}\n")
	
	# Track unique Owner Entities to avoid duplicate API calls
	cache = {}  # owner_entity+address -> result
	
	# Open results file for writing
	with open(RESULTS_FILE, 'w', newline='', encoding='utf-8-sig') as f:
		writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
		writer.writeheader()
		
		for idx, src in enumerate(source_rows, 1):
			owner_entity = src.get('Owner Entity', '').strip()
			deal_name = src.get('Deal: Deal Name', '')
			pid = src.get('PID', '')
			address = assemble_address(src)
			
			print(f"\n[{idx}/{total}] {owner_entity}")
			print(f"         PID: {pid}")
			print(f"         Addr: {address}")
			
			# Write the TF source row first (add blank source columns)
			tf_row = {f: src.get(f, '') for f in FIELDNAMES}
			tf_row['Phone Source'] = 'TF'
			tf_row['Mobile Source'] = 'TF'
			writer.writerow(tf_row)
			
			# Check cache
			cache_key = f"{owner_entity.upper()}|{address.upper()}"
			if cache_key in cache:
				print(f"         ⚡ Using cached result")
				fh_result = cache[cache_key]
			else:
				# Run Fox Hunter
				try:
					fh_result = fun_fox_hunter.main(owner_entity, address, enrich_contacts=True)
					cache[cache_key] = fh_result
				except Exception as e:
					if '502' in str(e):
						print(f"         ⚠️  502 Server Error - retrying in 30 seconds...")
						time.sleep(30)
						try:
							fh_result = fun_fox_hunter.main(owner_entity, address, enrich_contacts=True)
							cache[cache_key] = fh_result
						except Exception as e2:
							print(f"         ❌ Retry failed: {e2}")
							fh_result = None
							cache[cache_key] = None
					else:
						print(f"         ❌ ERROR: {e}")
						traceback.print_exc()
						fh_result = None
						cache[cache_key] = None
				
				# Rate limit pause between API calls
				time.sleep(2)
			
			# Write FH result rows
			if fh_result:
				fh_rows = extract_fh_rows(fh_result, deal_name, pid)
				for fh_row in fh_rows:
					writer.writerow(fh_row)
				print(f"         ✅ {len(fh_rows)} FH rows written")
			else:
				print(f"         ⚠️  No FH results")
			
			# Flush periodically so partial results are saved
			if idx % 5 == 0:
				f.flush()
	
	print(f"\n{'='*60}")
	print(f"  COMPLETE - Results saved to:")
	print(f"  {RESULTS_FILE}")
	print(f"{'='*60}\n")


if __name__ == '__main__':
	ui = td.uInput('\n Run Fox Hunter Accuracy Test? [0/1/00] > ')
	if ui == '1':
		limit_ui = td.uInput('\n Limit number of records? [0=No/1=Yes] > ')
		if limit_ui == '1':
			count_ui = td.uInput('\n How many records to run? > ').strip()
			try:
				record_limit = int(count_ui)
			except ValueError:
				print('Invalid number. Cancelled.')
				record_limit = None
			if record_limit:
				print(f'\n Running first {record_limit} records...')
				main(limit=record_limit)
		else:
			print('\n Running all records...')
			main()
	elif ui == '00':
		print('Terminated.')
	else:
		print('Cancelled.')
