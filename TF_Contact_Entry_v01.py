
import acc
import cpypg
import dicts
import fjson
import fun_login
from json import dump
import lao
import mc
from pprint import pprint
import fun_text_date as td
import webs

# User to open TF record(s)
def open_tf_record():
	AID = dAcc['AID']
	EID = dAcc['EID']
	print(f'\n Open the record in TerraForce?')
	if AID != 'None' and EID != 'None':
		print(f'\n  1) {dAcc['ENTITY']}')
		print(f'  2) {dAcc['NAME']}')
		print('  3) Both')
		print('  4) Continue to add to MailChimp')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			webs.openTFDID(EID)
		elif ui == '2':
			webs.openTFDID(AID)
		elif ui == '3':
			webs.openTFDID(EID)
			webs.openTFDID(AID)
		elif ui == '4' or ui == '':
			return
		elif ui == '00':
			exit('\n Fin...')
	if dAcc['EID'] != 'None' and dAcc['AID'] == 'None':
		print(f'\n  1) {dAcc['ENTITY']}')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			webs.openTFDID(EID)
		else:
			exit('\n Fin...')
	if dAcc['EID'] == 'None' and dAcc['AID'] != 'None':
		print(f'\n  1) {dAcc['NAME']}')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			webs.openTFDID(AID)
		else:
			exit('\n Fin...')

td.banner('TF Contact Entry v01')

# Variables
service = fun_login.TerraForce()
dAcc = dicts.get_blank_account_dict()
user = lao.getUserName()

# Check if json file with the contact's name exists
name_file = 'C:/Users/Public/Public Mapfiles/M1_Files/tf_contact_entry.json'
if lao.does_file_exists(name_file):
	d = fjson.getJsonDict(name_file)
	dAcc['ENTITY'] = d['name']
	# Delete the file
	lao.delete_file(name_file)
# User to enter a contact name
else:
	ui = td.uInput(' Type Person or Company or [Enter] for None > ')
	if len(ui) > 2:
		dAcc['ENTITY'] = ui
	elif ui == '' or ui.upper() == 'NONE':
		dAcc['ENTITY'] = 'None'

# pprint(dAcc['ENTITY'])
# exit()

if dAcc['ENTITY'] != 'None':
	dAcc = acc.find_create_account_entity(service, dAcc)

find_person = True
if dAcc['ENTITY'] != 'None' and dAcc['NAME'] == 'None':
	print(f'\n Would you like find or enter a Person for {dAcc['ENTITY']}?')
	print('\n  1) Yes')
	print('  2) No')
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '1' or ui == '':
		ui = td.uInput('\n Enter a Person or [Enter] for None > ')
		if ui == '':
			dAcc['NAME'] = 'None'
		else:
			dAcc['NAME'] = ui
	elif ui == '2':
		dAcc['NAME'] = 'None'
		find_person = False
		AID = 'None'
	# else:
	# 	exit('\n Terminating program...')

if find_person:
	Name, AID, dAcc = acc.find_create_account_person(service, dAcc)

# Add to a Market Mailer List
if AID != 'None' and dAcc['STREET'] != 'None':
	ui = td.uInput(f'\n Add {dAcc['NAME']} to Market Mailer [0/1] > ')
	if ui == '1':
		acc.make_person_mvp_and_market_mailer(service, AID=AID, didpid='None', make_market_mailer=True)

# User to open TF record(s)
open_tf_record()

# User to add the contact to MailChimp
if user == 'blandis' or user == 'mklingen':
	if AID != 'None' and dAcc['EMAIL'] != 'None':
		ui = td.uInput(f'\n Add {dAcc['NAME']} to MailChimp [0/1/00] > ')
		if ui == '1':
			client = fun_login.MailChimp()
			mc.add_tf_person_to_mc(service, client, AID)

exit('\n Fin...')

