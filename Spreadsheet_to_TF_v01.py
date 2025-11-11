# Imporat a spreadsheet of contacts into Terraforce

import acc
import bb
import dicts
import fun_login
import fun_text_date as td
from pprint import pprint
import webs

td.banner('Spreadsheet to Terraforce Import v01')

service = fun_login.TerraForce()

filename = 'F:/Research Department/Projects/Advisors and Markets/Kansas City/City_Planners_2025-11-11.xlsx'
dContacts = dicts.spreadsheet_to_dict(filename)

for row in dContacts:
	dAcc = dicts.get_blank_account_dict()
	dAcc['NF'] = dContacts[row].get('First Name', '')
	dAcc['NL'] = dContacts[row].get('Last Name', '')
	dAcc['NAME'] = f"{dAcc['NF']} {dAcc['NL']}"
	dAcc['ENTITY'] = dContacts[row].get('Company', '')
	dAcc['EMAIL'] = dContacts[row].get('Email', '')

	pprint(dAcc)

	dAcc = acc.find_create_account_entity(service, dAcc)
	dAcc = acc.find_create_account_person(service, dAcc)

	acc.print_dAcc_info(dAcc)

	webs.openTFAccId(dAcc['EID'])
	webs.openTFAccId(dAcc['AID'])

	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')