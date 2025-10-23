
# EnformionGo

import acc
import ego
import dicts
import fjson
import fun_acc_entity as fae
import fun_text_date as td
import lao
import mpy
from pprint import pprint
import webs
import json
from typing import Dict, Any, List, Optional
import dicts  # Your dicts module with get_blank_account_dict()





def get_search_type():

	while 1:
		td.banner('People Search API')

		# Search Type menu
		print("\n Select Search Type:\n")
		print("  1) Person Contact Enrichment")
		print("  2) Person")
		print("  3) Entity/Company")
		print("  4) Property APN")
		print("  5) Teaser")
		print(" 00) Quit")

		ui = td.uInput('\n Select > ') 

		if ui == "1":
			SEARCH_TYPE = "DevAPIContactEnrich"
			api_url = "https://devapi.enformion.com/Contact/Enrich"
			payload = ego.get_ego_blank_person_payload()
			break
		elif ui == "2":
			SEARCH_TYPE = "Person"
			api_url = "https://devapi.enformion.com/PersonSearch"
			payload = ego.get_ego_blank_person_payload()
			break
		elif ui == "3":
			SEARCH_TYPE = "BusinessV2"
			api_url = "https://devapi.enformion.com/BusinessV2Search"
			payload = ego.get_ego_blank_entity_payload()
			break
		elif ui == "4":
			SEARCH_TYPE = "PropertyV2"
			api_url = "https://devapi.enformion.com/PropertyV2Search"
			payload = ego.get_ego_blank_property_payload()
			break
		elif ui == "5":
			SEARCH_TYPE = "Teaser"
			api_url = "https://devapi.enformion.com/PersonSearch"
			payload = ego.get_ego_blank_person_payload()
			break
		elif ui == "00":
			exit('\n Terminating program...')
		else:
			print("Invalid selection. Please try again.")

	headers = ego.get_ego_header(SEARCH_TYPE)

	return SEARCH_TYPE, api_url, payload, headers

def enter_person(dAcc, payload):
	print('\n Person')
	dAcc['NAME'] = td.uInput('\n Enter Person Full Name [00] > ')

	if dAcc['NAME'] == '00':
		exit('\n Terminating program...')

	dAcc = td.parse_person(dAcc)

	payload['FirstName'] = dAcc['NF']
	payload['LastName'] = dAcc['NL']

	dAcc['CITY'] = td.uInput('\n Enter City [00] > ').title()
	if dAcc['CITY'] == '00':
		exit('\n Terminating program...')
	
	dAcc['STATE'] = td.uInput('\n Enter State [00] > ').upper()
	if dAcc['STATE'] == '00':
		exit('\n Terminating program...')

	# Populate payload		
	if dAcc['STREET'] == 'None':
		payload['Address']['AddressLine1'] = ''
	else:
		payload['Address']['AddressLine1'] = dAcc['STREET']
	payload['Address']['AddressLine2'] = f'{dAcc['CITY']}, {dAcc['STATE']}'

	return dAcc, payload

def enter_entity(dAcc, payload):
	print('\n Entity/Company')
	dAcc['ENTITY'] = td.uInput('\n Enter Entity/Company Name [00] > ')

	if dAcc['ENTITY'] == '00':
		exit('\n Terminating program...')
	
	# Populate payload 
	payload['BusinessName'] = dAcc['ENTITY']

	dAcc['CITY'] = td.uInput('\n Enter City [00] > ').title()
	if dAcc['CITY'] == '00':
		exit('\n Terminating program...')

	dAcc['STATE'] = td.uInput('\n Enter State [00] > ').upper()
	if dAcc['STATE'] == '00':
		exit('\n Terminating program...')

	payload['AddressLine2'] = f'{dAcc['CITY']}, {dAcc['STATE']}'

	return dAcc, payload

def enter_property(dAcc, payload):
	# APN
	apn = td.uInput('\n Enter APN [00] > ')
	if apn == '00':
		exit('\n Terminating program...')
	payload['APN'] = apn

	# Business Name
	dAcc['ENTITY'] = td.uInput('\n Enter Entity/Company Name [00] > ')
	if dAcc['ENTITY'] == '00':
		exit('\n Terminating program...')
	elif dAcc['ENTITY'] == '':
		payload['BusinessName'] = ''
	else:
		payload['BusinessName'] = dAcc['ENTITY']

	# Person
	dAcc['NAME'] = td.uInput('\n Enter Person [00] > ')
	if dAcc['NAME'] == '00':
		exit('\n Terminating program...')
	if dAcc['NAME'] == '':
		payload['FirstName'] = ''
		payload['LastName'] = ''
	else:
		dAcc = td.parse_person(dAcc)
		payload['FirstName'] = dAcc['NF']
		payload['LastName'] = dAcc['NL']

	# Address
	street = td.uInput('\n Enter Street [00] > ')
	if street == '00':
		exit('\n Terminating program...')
	if street == '':
		payload['AddressLine1'] = ''
	else:
		payload['AddressLine1'] = street

	city_state = td.uInput('\n Enter City & State [00] > ')
	if city_state == '00':
		exit('\n Terminating program...')
	elif city_state == '':
		payload['AddressLine2'] = ''
	else:
		city_state = city_state.replace(",", "")
		lcity_state = city_state.split(' ')
		if len(lcity_state) == 2:
			city = lcity_state[0].strip()
			state = lcity_state[1].strip()
			payload['AddressLine2'] = f'{city}, {state}'
		else:
			payload['AddressLine2'] = ''

	# else:
	# 	street, city, state, zipcode = td.parce_single_line_address(full_address)
	# 	payload['Address']['AddressLine1'] = street
	# 	payload['Address']['AddressLine2'] = f'{city}, {state} {zipcode}'

	return dAcc, payload

while 1:
	td.banner('People Search API v01')


	# print('here10')
	# # pprint(dEGO['counts'])
	# # pprint(dEGO, depth=3)
	# for row in dEGO['persons']:
	# 	pprint(row)
	# 	ui = td.uInput('\n Continue [00]... > ')
	# 	if ui == '00':
	# 		exit('\n Terminating program...')
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')


	# dAcc, dTF, dPoly = mpy.get_parcel_data()

	# dAcc, is_entity = fun_acc_entity.is_entity(dAcc)


	dAcc = dicts.get_blank_account_dict()

	SEARCH_TYPE, api_url, payload, headers = get_search_type()


	if SEARCH_TYPE == "DevAPIContactEnrich":
		dAcc, payload = enter_person(dAcc, payload)
	elif SEARCH_TYPE == "Person":
		dAcc, payload = enter_person(dAcc, payload)
	if SEARCH_TYPE == "BusinessV2":
		dAcc, payload = enter_entity(dAcc, payload)
	elif SEARCH_TYPE == "PropertyV2":
		dAcc, payload = enter_property(dAcc, payload)
	elif SEARCH_TYPE == "Teaser":
		dAcc, payload = enter_person(dAcc, payload)

	# print('here6')
	# print('\n PAYLOAD')
	# pprint(payload)
	# print('\n HEADERS')
	# pprint(headers)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	dEGO = ego.ego_api_post(api_url, headers, payload)


	print('here20')
	print('\n dEGO RESPONSE')
	pprint(dEGO)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

	if SEARCH_TYPE == "DevAPIContactEnrich":
		dAcc = ego.get_ego_enrichment_data(dEGO, dAcc)
	elif SEARCH_TYPE == "BusinessV2":
		# Method 1: Interactive selection
		print("Method 1: Interactive Selection")
		dAcc = ego.get_ego_entity_data(dEGO, dAcc)
		print(f"\nSelected Entity: {dAcc['ENTITY']}")
		print(f"Phone: {dAcc['PHONE']}")
		print(f"Address: {dAcc['ADDRESSFULL']}")

	pprint(dAcc)
	ui = td.uInput('\n Enter another or [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
# print('here7')
# pprint(dAcc)
# ui = td.uInput('\n Continue [00]... > ')
# if ui == '00':
# 	exit('\n Terminating program...')

