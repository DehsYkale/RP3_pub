# Person vs Company Detection and Name Parsing for Parcel Owner Data
# Add these functions to fun_fox_hunter.py or import as a module

import re

# Corporate indicators - if any of these appear, it's likely a company
CORPORATE_INDICATORS = [
	'ADVISORS', 'ADVISOR',
	'ASSOCIATE', 'ASSOCIATES', 'ASSOCIATION', 'ASSOC',
	'CORP', 'CORPORATION',
	'LIMITED', 'LTD',
	'LLC', 'L.L.C.', 'L L C',
	'INC', 'INCORPORATED', 'INCORPORATION',	
	'LP', 'L.P.', 'LIMITED PARTNERSHIP',
	'LLP', 'L.L.P.',
	'PARTNERS', 'PARTNERSHIP',
	'TRUST', 'TRUSTEE', 'REVOCABLE', 'IRREVOCABLE', 'LIVING TRUST',
	'ESTATE', 'ESTATE OF',
	'COMPANY', 'COMPANIES', 'CO.',
	'ENTERPRISES', 'ENTERPRISE',
	'HOLDING', 'HOLDINGS',
	'PROPERTY', 'PROPERTIES',
	'INVESTMENTS', 'INVESTMENT',
	'VENTURE', 'VENTURES',
	'GROUP', 'GRP',
	'CAPITAL',
	'DEVELOPER', 'DEVELOPERS', 'DEVELOPMENT', 'DEV',
	'BUILDER', 'BUILDERS', 'BUILDING',
	'REALTY', 'REAL ESTATE',
	'MANAGEMENT', 'MGMT',
	'SERVICE', 'SERVICES',
	'SOLUTION', 'SOLUTIONS',
	'INTERNATIONAL', 'INTL',
	'NATIONAL',
	'GLOBAL',
	'BANK', 'BANKING',
	'CREDIT UNION',
	'CHURCH', 'MINISTRY', 'MINISTRIES',
	'FOUNDATION',
	'COUNTY', 'CITY OF', 'STATE OF', 'TOWN OF',
	'SCHOOL', 'DISTRICT',
	'HOMEOWNERS', 'HOA',
	'FAMILY LP', 'FAMILY LLC', 'FAMILY TRUST', 'TRUST'
	'SERIES', 'FUND',
]

# Patterns that indicate multiple persons
MULTI_PERSON_INDICATORS = [' & ', ' AND ', ' ET UX', ' ET VIR', ' ETAL', ' ET AL', '/']


def is_company(name: str) -> bool:
	"""
	Determine if the owner name is a company or person(s).
	
	Args:
		name: Owner name from parcel data (typically uppercase)
	
	Returns:
		True if likely a company, False if likely person(s)
	"""
	if not name:
		return False
	
	name_upper = name.upper().strip()
	
	# Check for corporate indicators
	for indicator in CORPORATE_INDICATORS:
		# Use word boundary matching to avoid false positives
		# e.g., "INCORPORATED" shouldn't match in "CORPORATED"
		pattern = r'\b' + re.escape(indicator) + r'\b'
		if re.search(pattern, name_upper):
			return True
	
	# Check for numbered entities (e.g., "123 MAIN STREET LLC" without the LLC)
	# Names that are primarily numbers/addresses are likely companies
	if re.match(r'^\d+\s+\w+\s+(ST|STREET|AVE|AVENUE|RD|ROAD|DR|DRIVE|BLVD|WAY|LN|LANE)', name_upper):
		return True
	
	# If none of the above, likely a person
	return False


def parse_person_names(name: str, address: str = "") -> list:
	"""
	Parse parcel owner name into individual person records.
	
	Common formats:
		- "STALNAKER RALPH T" → Single person
		- "SMITH JOHN & MARY" → Two people (couple)
		- "MATTERA CARMELA MATTERA VALENTE" → Two people (repeated last name)
		- "JONES ROBERT E JR" → Single person with suffix
		- "SMITH JOHN AND JANE SMITH" → Two people
	
	Args:
		name: Owner name from parcel data
		address: Property address (used for contact records)
	
	Returns:
		List of dicts with parsed name components
	"""
	if not name:
		return []
	
	name = name.strip().upper()
	persons = []
	
	# Check for multiple person indicators
	has_multiple = any(ind in name for ind in MULTI_PERSON_INDICATORS)
	
	if has_multiple:
		# Split on common separators
		# Replace various separators with a common one
		normalized = name
		for sep in [' & ', ' AND ', ' ET UX', ' ET VIR', '/']:
			normalized = normalized.replace(sep, '|SPLIT|')
		
		parts = [p.strip() for p in normalized.split('|SPLIT|') if p.strip()]
		
		# Handle "ETAL" or "ET AL" - just note it, don't try to parse
		parts = [p for p in parts if p not in ['ETAL', 'ET AL']]
		
		for part in parts:
			parsed = _parse_single_name(part, address)
			if parsed:
				persons.append(parsed)
		
		# Special case: "MATTERA CARMELA MATTERA VALENTE" (two people, same last name)
		# If we only got one person but the name has the last name repeated, try splitting
		if len(persons) == 1 and len(parts) == 1:
			words = name.split()
			if len(words) >= 4:
				# Check if first word appears again (repeated last name for couple)
				first_word = words[0]
				for i in range(2, len(words)):
					if words[i] == first_word:
						# Split into two people
						person1_words = words[:i]
						person2_words = words[i:]
						
						parsed1 = _parse_single_name(' '.join(person1_words), address)
						parsed2 = _parse_single_name(' '.join(person2_words), address)
						
						if parsed1 and parsed2:
							persons = [parsed1, parsed2]
						break
	else:
		# Single person
		parsed = _parse_single_name(name, address)
		if parsed:
			persons.append(parsed)
	
	return persons


def _parse_single_name(name: str, address: str = "") -> dict:
	"""
	Parse a single person's name from parcel format.
	
	Parcel format is typically: LASTNAME FIRSTNAME [MIDDLE] [SUFFIX]
	
	Args:
		name: Single person's name
		address: Property address
	
	Returns:
		Dict with name components or None if parsing fails
	"""
	if not name:
		return None
	
	# Common suffixes
	SUFFIXES = ['JR', 'JR.', 'SR', 'SR.', 'II', 'III', 'IV', 'V']
	
	words = name.strip().upper().split()
	
	if len(words) < 2:
		# Can't parse a single word
		return None
	
	# Check for and remove suffix
	suffix = ""
	if words[-1] in SUFFIXES:
		suffix = words.pop()
	
	if len(words) < 2:
		return None
	
	# Standard parcel format: LASTNAME FIRSTNAME [MIDDLE]
	last_name = words[0]
	first_name = words[1] if len(words) > 1 else ""
	middle_name = ""
	
	if len(words) > 2:
		# Everything after first name is middle name/initial
		middle_name = ' '.join(words[2:])
	
	# Title case the names
	last_name = last_name.title()
	first_name = first_name.title()
	middle_name = middle_name.title() if middle_name else ""
	
	# Add suffix back to last name if present
	if suffix:
		last_name = f"{last_name} {suffix}"
	
	# Parse address if provided
	billing_street = ""
	billing_city = ""
	billing_state = ""
	billing_zip = ""
	
	if address:
		addr_parts = parse_address(address)
		billing_street = addr_parts.get('street', '')
		billing_city = addr_parts.get('city', '')
		billing_state = addr_parts.get('state', '')
		billing_zip = addr_parts.get('zip', '')
	
	return {
		"FirstName": first_name,
		"MiddleName__c": middle_name,
		"LastName": last_name,
		"BillingStreet": billing_street,
		"BillingCity": billing_city,
		"BillingState": billing_state,
		"BillingPostalCode": billing_zip,
		"Category__c": "Land owner",
		"Company__c": "",
		"company_association": "",
		"Description": "Property owner identified from parcel records.",
		"LinkedIn_Url__c": "",
		"PersonEmail": "",
		"Phone": "",
		"PersonMobilePhone": "",
		"PersonTitle": "Property Owner",
		"priority_rank": 1,
		"_raw_name": name  # Keep original for reference
	}


def parse_address(address: str) -> dict:
	"""
	Parse an address string into components.
	
	Args:
		address: Full address string (e.g., "123 Main St, Marianna, FL 32446")
	
	Returns:
		Dict with street, city, state, zip
	"""
	result = {'street': '', 'city': '', 'state': '', 'zip': ''}
	
	if not address:
		return result
	
	# Try to extract ZIP code (5 digits or 5+4)
	zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
	if zip_match:
		result['zip'] = zip_match.group(1)
		address = address[:zip_match.start()] + address[zip_match.end():]
	
	# Try to extract state (2-letter code)
	state_match = re.search(r'\b([A-Z]{2})\b', address.upper())
	if state_match:
		# Verify it's a valid state code
		valid_states = [
			'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA',
			'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
			'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT',
			'VA','WA','WV','WI','WY','DC'
		]
		if state_match.group(1).upper() in valid_states:
			result['state'] = state_match.group(1).upper()
			address = address[:state_match.start()] + address[state_match.end():]
	
	# Split remaining by comma
	parts = [p.strip() for p in address.split(',') if p.strip()]
	
	if len(parts) >= 2:
		result['street'] = parts[0]
		result['city'] = parts[1].strip()
	elif len(parts) == 1:
		result['street'] = parts[0]
	
	return result


def create_person_only_result(persons: list, address: str, search_date: str) -> dict:
	"""
	Create the full JSON result structure for person owners (no company).
	
	Args:
		persons: List of parsed person dicts from parse_person_names()
		address: Original address provided
		search_date: Date of search (YYYY-MM-DD format)
	
	Returns:
		Dict matching the expected output format with null companies
	"""
	return {
		"companies": {
			"primary": None,
			"parent_company": None,
			"subsidiaries": [],
			"affiliates": []
		},
		"contacts": persons,
		"search_metadata": {
			"search_date": search_date,
			"sources_used": ["Parcel owner data"],
			"confidence_level": "Medium",
			"corporate_structure_notes": "Owner identified as individual person(s), not a company entity.",
			"total_contacts_found": len(persons),
			"notes": "Names parsed from parcel records. Contact enrichment recommended."
		}
	}


# =============================================================================
# INTEGRATION WITH MAIN WORKFLOW
# =============================================================================

def detect_and_route(owner_name: str, address: str, model: str = None):
	"""
	Main entry point - detects person vs company and routes accordingly.
	
	Args:
		owner_name: Owner name from parcel data
		address: Property address
		model: AI model for company searches (not needed for person-only)
	
	Returns:
		Tuple: (is_person, initial_data)
			- is_person: True if owner is person(s), False if company
			- initial_data: For persons, returns parsed data ready to enrich
			              For companies, returns None (proceed with normal flow)
	"""
	from datetime import datetime
	
	if is_company(owner_name):
		return False, None
	else:
		# Parse person names
		persons = parse_person_names(owner_name, address)
		search_date = datetime.now().strftime('%Y-%m-%d')
		initial_data = create_person_only_result(persons, address, search_date)
		return True, initial_data


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
	# Test cases
	test_cases = [
		# Person names
		("STALNAKER RALPH T", "123 Main St, Marianna, FL 32446"),
		("MATTERA CARMELA MATTERA VALENTE", "456 Oak Ave, Tampa, FL 33601"),
		("SMITH JOHN & MARY", "789 Pine Rd, Orlando, FL 32801"),
		("JONES ROBERT E JR", "321 Elm St, Jacksonville, FL 32099"),
		("WILLIAMS JAMES AND SARAH WILLIAMS", "555 Maple Dr, Miami, FL 33101"),
		("JOHNSON MICHAEL ET UX", "777 Cedar Ln, Gainesville, FL 32601"),
		
		# Company names
		("SMITH HOLDINGS LLC", "100 Corporate Blvd, Tampa, FL 33602"),
		("ABC DEVELOPMENT CORP", "200 Business Park, Orlando, FL 32802"),
		("JONES FAMILY TRUST", "300 Trust Way, Miami, FL 33102"),
		("FIRST NATIONAL BANK", "400 Bank St, Jacksonville, FL 32100"),
		("WALMART INC", "500 Retail Rd, Fort Myers, FL 33901"),
		("FARM CREDIT OF NORTHWEST FLORIDA ACA", "5052 Highway 90 East, Marianna, FL 32446"),
	]
	
	print("=" * 80)
	print("PERSON VS COMPANY DETECTION TESTS")
	print("=" * 80)
	
	for name, address in test_cases:
		is_person, data = detect_and_route(name, address)
		
		if is_person:
			print(f"\n✓ PERSON: {name}")
			for p in data['contacts']:
				print(f"   → {p['FirstName']} {p['MiddleName__c']} {p['LastName']}".replace("  ", " "))
		else:
			print(f"\n✗ COMPANY: {name}")
			print(f"   → Route to company structure search")
	
	print("\n" + "=" * 80)