
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

def get_address_components(dAcc, entity=None, address=None):
	lao.print_function_name(' tfaf def get_address_components()')
	if address is None:
		if dAcc['ADDRESSFULL'] == 'None':
			dAcc['ADDRESSFULL'] = f"{dAcc['STREET']}, {dAcc['CITY']}, {dAcc['STATE']} {dAcc['ZIP']}"
		BillingStreet = dAcc['STREET']
		BillingCity = dAcc['CITY']
		BillingState = dAcc['STATE']
		BillingPostalCode = dAcc['ZIP']
		full_address = dAcc['ADDRESSFULL']
	else:
		full_address = address
		# Parse the Full Address
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
		print(f"\n Street Number: {street_number}")
		print(f" Street Name: {street_name}")
		print(f" Unit/Suite: {unit_suite}\n")
	
	return dAcc, BillingStreet, BillingCity, BillingState, BillingPostalCode, full_address, street_number, street_name, unit_suite

# Parse out BillingStreet into number, street name, unit/suite
def get_billingstreet_number_street_name_unit_suite(street_full):
	lao.print_function_name(' tfaf def get_billingstreet_number_street_name_unit_suite()')
	"""Extracts the street number and street name from a full billing street address."""

	# Remove any text before the first digit (street number)
	match = re.search(r'\d', street_full)
	try:
		if match.start() != 0:
			print(f" Initial street_full: {street_full}")
			print(match.start())
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

# Find best match woth address function
def find_best_entity_name_match_with_address(full_entity_name, results):
	lao.print_function_name(' tfaf def find_best_entity_name_match_with_address()')
	EID = 'None'
	for row in results:
		found_match = 'NO MATCH'

		full_entity_name_lower = full_entity_name.lower()
		tf_entity_name = str(row.get('Name'))
		tf_entity_name_lower = tf_entity_name.lower()
		lTF_entity_name_lower_shorting = tf_entity_name_lower.split()

		# Check for entity name match
		if full_entity_name_lower == tf_entity_name_lower:
			td.colorText(f' Exact {full_entity_name} match found.', 'GREEN')
			EID = row['Id']
			return EID
			# found_match = 'EXACT'
			# break

		# Check for entity name by shorting
		while 1:
			lTF_entity_name_lower_shorting = lTF_entity_name_lower_shorting[:-1]
			tf_entity_name_lower_shorted = ' '.join(lTF_entity_name_lower_shorting)
			if len(lTF_entity_name_lower_shorting) == 0:
				break
			if tf_entity_name_lower_shorted in full_entity_name_lower:
				td.colorText(f' Exact {full_entity_name} match found by shorting TF entity name.', 'GREEN')
				# print('here3')
				# pprint(row)
				EID = row['Id']
				print(f"\n EID: {EID}")
				return EID

		lTF_entity_name = full_entity_name_lower.split()
		if len(lTF_entity_name) >= 2:
			first_word = lTF_entity_name[0].lower()
			second_word = lTF_entity_name[1].lower()
			if first_word in tf_entity_name_lower and second_word in tf_entity_name_lower:
				td.colorText(f' Partial {full_entity_name} match found.', 'CYAN')
				EID = row.get('Id')
				return EID
			
		# Check for first word match but only if the entity name has two words
		if found_match == 'NO MATCH' and len(lTF_entity_name) == 2:
			first_word = lTF_entity_name[0].lower()
			if first_word in tf_entity_name_lower:
				td.colorText(f' First word of {full_entity_name} match found.', 'PURPLE')
				EID = row.get('Id')
				return EID

	return EID

# Find best match without address function
def find_best_entity_name_match_no_address(service, full_entity_name):
	lao.print_function_name(' tfaf def find_best_entity_name_match_no_address()')
	td.warningMsg(' No street number found in BillingStreet. Querying by entity name only.')
	EID = 'None'
	wc = (f" Name = '{full_entity_name}'")
	fields = 'Id'
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	# If no results, try partial name match
	if results == []:
		lFull_entity_name = full_entity_name.split()
		if len(lFull_entity_name) >= 2:
			first_word = lFull_entity_name[0].lower()
			second_word = lFull_entity_name[1].lower()
			fields = 'Id'
			wc = (f" Name LIKE '%{first_word}%' AND Name LIKE '%{second_word}%'")
			results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	if results == []:
		td.warningMsg(' No TerraForce Account Name or Address matches found for this entity name.')
		return EID
	
	EID = results[0]['Id']
	return EID

# Find best Person match woth address function
def find_best_person_name_match_with_address(first_name, last_name, results):
	lao.print_function_name(' tfaf def find_best_person_name_match_with_address()')
	AID = 'None'
	for row in results:
		found_match = 'NO MATCH'

		full_first_name_lower = first_name.lower()
		full_last_name_lower = last_name.lower()
		tf_full_first_name = str(row.get('FirstName'))
		tf_full_last_name = str(row.get('LastName'))
		tf_full_first_name_lower = tf_full_first_name.lower()
		tf_full_last_name_lower = tf_full_last_name.lower()

		# print(full_first_name_lower, full_last_name_lower)
		# print(tf_full_first_name_lower, tf_full_last_name_lower)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		# Check for Person name match
		if full_first_name_lower == tf_full_first_name_lower and full_last_name_lower == tf_full_last_name_lower:
			td.colorText(f' Exact {first_name} {last_name} match found.', 'GREEN')
			AID = row['Id']
			return AID
			# found_match = 'EXACT'
			# break

		# Check for Person name by first name initial and last name
		first_initial_matches_counter = 0
		if len(full_first_name_lower) > 0:
			first_name_initial = full_first_name_lower[0]
			if first_name_initial == tf_full_first_name_lower[0] and full_last_name_lower == tf_full_last_name_lower:
				td.colorText(f' Exact {first_name_initial}. {last_name} match found.', 'GREEN')
				AID = row['Id']
				td.warningMsg('\n Match found by first name initial and last name.')
				print(f'Source: {full_first_name_lower}, {full_last_name_lower}')
				print(f'TF: {tf_full_first_name_lower}, {tf_full_last_name_lower}')
				ui = td.uInput('\n Continue [00]... > ')
				if ui == '00':
					exit('\n Terminating program...')
				return AID

	return AID

def main(service, dAcc, account_type=None, entity=None, address=None):
	lao.print_function_name(' tfaf def main()')
	"""Get TerraForce Account ID (EID) based on Account dict info."""

	# Assign entity and address if not provided
	if account_type == 'Entity':
		if entity is None:
			entity = dAcc['ENTITY']
			full_entity_name = entity
	elif account_type == 'Person':
		first_name = dAcc['NF']
		last_name = dAcc['NL']
	
	# Getting address components ##########################################
	dAcc, BillingStreet, BillingCity, BillingState, BillingPostalCode, full_address, street_number, street_name, unit_suite = get_address_components(dAcc, entity, address)

	# Entity Account Type Handling ########################################
	# Handle records that do not have an address number by querying with the entity name only
	if account_type == 'Entity':
		if street_number is None:
			found_match = find_best_entity_name_match_no_address(service, full_entity_name)


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

		# If still no results try with entity name
		# The function will handle exact, partial, and first word matches
		# If no results, function will return EID as 'None'
		if results == []:
			td.warningMsg(' No TerraForce Account matches found for this address.')
			EID = find_best_entity_name_match_no_address(service, full_entity_name)
			return EID

		
		# Find best match
		EID = find_best_entity_name_match_with_address(full_entity_name, results)
		dAcc['EID'] = EID
		return EID

	if account_type == 'Person':
		# TODO: Handle records that do not have an address number by querying with the person name only
		if street_number is None:
			found_match = find_best_person_name_match_no_address(service, first_name, last_name)
			td.warningMsg(' No street number found in BillingStreet. Querying by person name only.')
			exit()

		# TerraForce Query for Address Match
		fields = 'default'
		results = []
		# Query using street number and street name only
		if not unit_suite is None:
			wc = (f" BillingStreet LIKE '{street_number}%' AND BillingStreet LIKE '%{street_name}%' AND BillingStreet LIKE '%{unit_suite}%' AND BillingState = '{BillingState}' AND BillingPostalCode LIKE '{BillingPostalCode}%'")
			results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
		
		# If no results, try without unit_suite
		if results == []:
			# Query without unit_suite
			wc = (f" BillingStreet LIKE '{street_number}%' AND BillingStreet LIKE '%{street_name}%' AND BillingState = '{BillingState}' AND BillingPostalCode LIKE '{BillingPostalCode}%'")
			results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

		# If still no results try with entity name
		# The function will handle exact, partial, and first word matches
		# If no results, function will return EID as 'None'
		# if results == []:
		# 	td.warningMsg(' No TerraForce Account matches found for this address.')
		# 	AID = find_best_person_name_match_no_address(service, first_name, last_name)
		# 	return AID

		
		# print('here1')
		# pprint(results)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		

		
		# Find best match
		AID = find_best_person_name_match_with_address(first_name, last_name, results)
		dAcc['AID'] = AID
		return AID






