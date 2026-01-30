
import bb
import csv
import lao
from os import system
import dicts
import fun_login
import fun_staff as fstf
import fun_text_date as td
from pprint import pprint
import re
from datetime import datetime


def get_billingstreet_number_street_name_unit_suite(street_full):
	"""Extracts the street number and street name from a full billing street address."""

	# Remove any text before the first digit (street number)
	match = re.search(r'\d', street_full)
	try:
		if match.start() != 0:
			print(f" Initial street_full: {street_full}")
			print(match.start())
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
			street_full = street_full[match.start()-1:]
	except Exception as e:
		print(f"Error processing street_full: {street_full} - {e}")
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		return None, None, None

	# Remove commas and periods and extra spaces
	street_full = street_full.replace(',', ' ').replace('.', ' ')
	# Clean up extra spaces
	street_full = re.sub(r'\s+', ' ', street_full).strip()
	# Split by '#' to handle unit numbers
	if '#' in street_full:
		parts = street_full.split('#')
		street_full = parts[0].strip()
		unit_suite = parts[1].strip() if len(parts) > 1 else None
	else:
		# Remove unit designators (e.g., Apt, Suite, Unit, #) but capture the unit number
		lUnit_designators = dicts.get_unit_suite_designators_list()
		pattern = r'\b(?:' + '|'.join(lUnit_designators) + r')\.?\s*(\S+(?:\s+\d\S*)?)'
		# Extract unit_suite number before removal
		match = re.search(pattern, street_full.strip(), flags=re.IGNORECASE)
		unit_suite = match.group(1) if match else None
	# Remove the unit designator and number from the address
		street_full = re.sub(pattern, '', street_full.strip(), flags=re.IGNORECASE)

	# Remove predirectional (e.g., N, S, E, W, NW, NE, SW, SE)
	street_full = re.sub(r'^(\d+)\s+(N|S|E|W|NW|NE|SW|SE)\s+', r'\1 ', street_full.strip(), flags=re.IGNORECASE)
	# Remove postdirectional (e.g., N, S, E, W, NW, NE, SW, SE)
	street_full = re.sub(r'\s+(N|S|E|W|NW|NE|SW|SE)$', '', street_full.strip(), flags=re.IGNORECASE)
	# print(f" After predirectional removal: {street_full}")

	# Remove street suffix if present
	last_word = street_full.split()[-1].upper()
	dStreet_suffixes = dicts.get_street_suffixes_dict()
	if last_word in dStreet_suffixes:
		# Remove street suffix
		street_full = ' '.join(street_full.split()[:-1])
		# 
		# print(f" Removed suffix: {last_word}")
	# print(f" After suffix removal: {street_full}")



	# Extract street number and name
	match = re.match(r'(\d+)\s+(.*)', street_full)
	if match:
		street_number = match.group(1)
		street_name = match.group(2)
		return street_number, street_name, unit_suite
	else:
		return None, None, None

# Write to CSV file
def write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name):
	with open(filepath_results, mode='a', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow([found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name])

	# Find best match

# Find best match function
def find_best_entity_name_match_with_address(full_entity_name, results):
	for row in results:
		found_match = 'NO MATCH'

		full_entity_name_lower = full_entity_name.lower()
		tf_entity_name = str(row.get('Name'))
		tf_entity_name_lower = tf_entity_name.lower()
		lTF_entity_name_lower_shorting = tf_entity_name_lower.split()

		# Check for entity name match
		if full_entity_name_lower == tf_entity_name_lower:
			td.colorText(f' Exact {full_entity_name} match found {counter}', 'GREEN')
			found_match = 'EXACT'
			write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name)
			break

		# Check for entity name by shorting
		while 1:
			lTF_entity_name_lower_shorting = lTF_entity_name_lower_shorting[:-1]
			tf_entity_name_lower_shorted = ' '.join(lTF_entity_name_lower_shorting)
			if len(lTF_entity_name_lower_shorting) == 0:
				break
			if tf_entity_name_lower_shorted in full_entity_name_lower:
				td.colorText(f' Exact {full_entity_name} match found by shorting TF entity name {counter}.', 'GREEN')
				found_match = 'EXACT BY SHORTING'
				write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name)
				break
		if found_match == 'EXACT BY SHORTING':
			break

		lTF_entity_name = full_entity_name_lower.split()
		if len(lTF_entity_name) >= 2:
			first_word = lTF_entity_name[0].lower()
			second_word = lTF_entity_name[1].lower()
			if first_word in tf_entity_name_lower and second_word in tf_entity_name_lower:
				td.colorText(f' Partial {full_entity_name} match found {counter}.', 'CYAN')
				found_match = 'FIRST TWO WORDS'
				write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name)
				break
		if found_match == 'NO MATCH':
			first_word = lTF_entity_name[0].lower()
			if first_word in tf_entity_name_lower:
				td.colorText(f' First word of {full_entity_name} match found {counter}.', 'PURPLE')
				found_match = 'FIRST WORD'
				write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, tf_entity_name)
				break

		# No match found after checking all results
		if found_match == 'NO MATCH':
			td.warningMsg(f' No {full_entity_name} match found among TerraForce address matches.')
			write_to_csv(found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, 'NO TF ENTITY NAME MATCH')
			print('\n Entity :', row.get('Name'))
			print(' BillingStreet :', row.get('BillingStreet'))
			print(' BillingCity :', row.get('BillingCity'))
			print(' BillingState :', row.get('BillingState'))
			print(' BillingPostalCode :', row.get('BillingPostalCode'))
			print(f"\n Street Number: {street_number}")
			print(f" Street Name: {street_name}")
			print(f" Unit/Suite: {unit_suite}\n")

	return found_match

def find_best_entity_name_match_no_address(full_entity_name):
	td.warningMsg(' No street number found in BillingStreet. Querying by entity name only.')
	wc = (f" Name = '{full_entity_name}'")
	fields = 'default'
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
	# If no results, try partial name match
	if results == []:
		lFull_entity_name = full_entity_name.split()
		if len(lFull_entity_name) >= 2:
			first_word = lFull_entity_name[0].lower()
			second_word = lFull_entity_name[1].lower()
			wc = (f" Name LIKE '%{first_word}%' AND Name LIKE '%{second_word}%'")
			results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	if results == []:
		td.warningMsg(' No TerraForce Account Name or Address matches found for this entity name.')
		# Write no match to CSV
		with open(filepath_results, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow(['NO TF ENTITY NAME MATCH', full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, 'NO TF ENTITY NAME MATCH'])
			return 'NO TF ENTITY NAME MATCH'
	else:
		with open(filepath_results, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			td.colorText(f' Name match found for {full_entity_name} without address.', 'GREEN')
			writer.writerow(['NAME MATCH ONLY NO ADDRESS MATCH', full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, 'NO TF ENTITY NAME MATCH'])
			return 'NAME MATCH ONLY NO ADDRESS MATCH'

	

# PROGRAM STARTS HERE ################################################
service = fun_login.TerraForce()

td.banner('TF Power Account Finder')
td.console_title('TF Power Account Finder')

# Make results CSV file
filepath_results = 'C:/TEMP/address samples RESULTS.csv'
with open(filepath_results, mode='w', newline='', encoding='utf-8') as file:
	writer = csv.writer(file)
	writer.writerow(['Name Match', 'Entity', 'Billing Street', 'Billing City', 'Billing State', 'Billing Postal Code', 'TF Entity Name'])

# Process a single Enity and address entered manually
full_entity_name = td.uInput('\n Enter Full Entity Name... > ')
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')
elif full_entity_name == '':
	filepath_source = 'C:/TEMP/address samples.csv'
	dAddresses = dicts.spreadsheet_to_dict(filepath_source)
	print_street_parse = False
else:
	full_address = td.uInput('\n Enter Full Address... > ')
	lAddress = td.parse_single_line_address(full_address)
	BillingStreet = lAddress[0]
	BillingCity = lAddress[1]
	BillingState = lAddress[2]
	BillingPostalCode = lAddress[3]
	print(f"\n BillingStreet: {BillingStreet}")
	print(f" BillingCity: {BillingCity}")
	print(f" BillingState: {BillingState}")
	print(f" BillingPostalCode: {BillingPostalCode}")
	dAddresses = {}
	dAddresses[1] = {'Account Contact Name': full_entity_name, 'Billing Street': BillingStreet, 'Billing City': BillingCity, 'Billing State/Province': BillingState, 'Billing Zip/Postal Code': BillingPostalCode}
	print_street_parse = True

counter = 0
counter_max = 500
for row_address in dAddresses:
	r = dAddresses[row_address]
	full_entity_name = r['Account Contact Name']
	if full_entity_name == '':
		continue
	full_address = f"{r['Billing Street']}, {r['Billing City']} {r['Billing State/Province']} {r['Billing Zip/Postal Code']}"

	# Parse the Full Address
	# print(full_address)
	lAddress = td.parse_single_line_address(full_address)
	BillingStreet = lAddress[0]
	BillingCity = lAddress[1]
	BillingState = lAddress[2]
	BillingPostalCode = lAddress[3]

	# Standardize BillingStreet format & get components
	BillingStreet = td.billingstreet_standarize_format(BillingStreet)

	# Handle PO Boxes
	if 'PO BOX' in BillingStreet.upper():
		BillingStreet_upper = BillingStreet.upper()
		street_number = BillingStreet_upper.replace('PO BOX ', '')
		street_name = 'PO BOX'
		unit_suite = None
	# Extract street number, name, and unit/suite
	else:
		street_number, street_name, unit_suite = get_billingstreet_number_street_name_unit_suite(BillingStreet)
	
	# Handle records that do not have an address number by querying with the entity name only
	if street_number is None:
		found_match = find_best_entity_name_match_no_address(full_entity_name)
		counter += 1
		if counter == counter_max:
			break
		continue

	if print_street_parse:
		print(f"\n Street Number: {street_number}")
		print(f" Street Name: {street_name}")
		print(f" Unit/Suite: {unit_suite}\n")

	# TerraForce Query for Address Match
	fields = 'default'
	results = []
	# Query using street number and street name only
	if not unit_suite is None:
		wc = (f" BillingStreet LIKE '{street_number}%' AND BillingStreet LIKE '%{street_name}%' AND BillingStreet LIKE '%{unit_suite}%' AND BillingState = '{BillingState}' AND BillingPostalCode LIKE '{BillingPostalCode}%'")
		results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
	
	# If no results, try without unit_suite
	if results == []:
		# Query without unit_suite
		wc = (f" BillingStreet LIKE '{street_number}%' AND BillingStreet LIKE '%{street_name}%' AND BillingState = '{BillingState}' AND BillingPostalCode LIKE '{BillingPostalCode}%'")
		results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	if results == []:
		td.warningMsg(' No TerraForce Account matches found for this address.')
		found_match = find_best_entity_name_match_no_address(full_entity_name)
		# Write no match to CSV
		with open(filepath_results, mode='a', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow([found_match, full_entity_name, BillingStreet, BillingCity, BillingState, BillingPostalCode, 'NO TF ADDRESS MATCH'])
		continue
	
	# Find best match
	found_match = find_best_entity_name_match_with_address(full_entity_name, results)



	counter += 1
	if counter == counter_max:
		break
	# Prompt to continue or open results file
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	lao.openFile(filepath_results)
	# 	exit('\n Terminating program...')

lao.openFile(filepath_results)

exit()

