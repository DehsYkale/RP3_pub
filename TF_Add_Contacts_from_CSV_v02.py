# Crosschecks Constant Contact List with TerraForce records.
# Updates Email Address in TF

import acc
import bb
import csv
import lao
import fun_login
from pprint import pprint
from os.path import exists
import fun_text_date as td

def getSkipFile():
	skipfile = 'F:/Research Department/Projects/Advisors and Markets/DFW/SKIP DFW Contacts 2023-09.txt'
	# Make skipfile if it does not exitst
	file_exists = exists(skipfile)
	if file_exists is False:
		with open(skipfile, 'w') as f:
			f.write('Heartman Contacts Skip File')
	return skipfile

# Poplate the dAcc dict
def populate_dAcc():
	# Get blank Account dict
	dAcc = dicts.get_blank_account_dict()

	# Populate Dict Keys if they exist
	# Person
	if 'FIRST NAME' in dCon.keys():
		dAcc['NF'] = dCon['FIRST NAME']
	if 'MIDDLE NAME' in dCon.keys():
		dAcc['NM'] = dCon['MIDDLE NAME']
	if 'LAST NAME' in dCon.keys():
		dAcc['NL'] = dCon['LAST NAME']
	if 'FIRST NAME' in dCon.keys() and 'LAST NAME' in dCon.keys():
		dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	# if dAcc['NAME'] == 'None' and 'NAME' in dCon.keys():
	# 	dAcc['NAME'] = dCon['NAME']
	# Company
	if 'COMPANY' in dCon.keys():
		dAcc['ENTITY'] = dCon['COMPANY']
		if dAcc['NAME'] == 'None' or dAcc == '':
			 dAcc['NAME'] = dCon['COMPANY']
	if 'ENTITY' in dCon.keys():
		if dAcc['ENTITY'] == 'None':
			dAcc['ENTITY'] = dCon['NAME']
	if 'DEPARTMENT' in dCon.keys():
		dAcc['DEPARTMENT'] = dCon['DEPARTMENT']
	if 'JOB TITLE' in dCon.keys():
		dAcc['TITLEPERSON'] = dCon['JOB TITLE']
	# Address
	# One cell Address
	if 'ADDRESS' in dCon.keys():
		dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'] = td.parce_single_line_address(dCon['ADDRESS'])
		# dAcc = addressFormater(dAcc)
		dAcc = td.address_formatter(dAcc)
	# Multi-cell Address
	if 'STREET' in dCon.keys():
		dAcc['STREET'] = dCon['STREET']
	if 'CITY' in dCon.keys():
		dAcc['CITY'] = dCon['CITY']
	if 'STATE' in dCon.keys():
		dAcc['STATE'] = dCon['STATE']
	if 'ZIPCODE' in dCon.keys():
		dAcc['ZIPCODE'] = dCon['ZIPCODE']
	dAcc = td.address_formatter(dAcc)
	# Phone & Email
	if 'PHONE' in dCon.keys():
		dAcc['PHONE'] = dCon['PHONE']
	if 'PHONEHOME' in dCon.keys():
		dAcc['PHONEHOME'] = dCon['HOME PHONE']
	if 'PHONE OTHER' in dCon.keys():
		dAcc['PHONEOTHER'] = dCon['PHONE OTHER']
	if 'FAX' in dCon.keys():
		dAcc['FAX'] = dCon['FAX']
	if 'MOBILE' in dCon.keys():
		dAcc['MOBILE'] = dCon['MOBILE']
	if 'EMAIL' in dCon.keys():
		dAcc['EMAIL'] = dCon['EMAIL']
	if 'WEBSITE' in dCon.keys():
		dAcc['WEBSITE'] = dCon['WEBSITE']
	if 'DESCRIPTION' in dCon.keys():
		dAcc['DESCRIPTION'] = dCon['DESCRIPTION']
	dAcc['MARKETMAILER'] = False
	dAcc['TOP100AGENT'] = 'None' # Logan Holz
	# Find Create Account Entity
	# pprint(dAcc)
	return dAcc

# Update Cateory with Market Insights & Advisors
def update_category():
	print('\n Updating Category...')
	update_cat = False
	if dAcc['CATEGORY'] == 'None':
		dAcc['CATEGORY'] = 'Market Insights;Landry Burdine;Austin Reilly'
		update_cat = True
	else:
		lCategory = ['Market Insights, Landry Burdine, Austin Reilly']
		for cat in lCategory:
			if cat in dAcc['CATEGORY']:
				continue
			else:
				dAcc['CATEGORY'] = '{0},{1}'.format(dAcc['CATEGORY'], cat)
				update_cat = True
	
	if update_cat:
		dup = {'type': 'Account',
				'Id': AID,
				'Category__c': dAcc['CATEGORY']}
		bb.tf_update_3(service, dup)

service = fun_login.TerraForce()
inSpreadsheet = 'F:/Research Department/Projects/Advisors and Markets/DFW/DFW Eblast List Update 2023-09-11.xlsx'
dContacts = lao.spreadsheetToDict(inSpreadsheet, sheetname='Add to MI List')
skipfile = getSkipFile()

for row in dContacts:
	lao.banner('TF Add Contacts from CSV v02')
	dCon = dContacts[row]

	# Populate dAcc dict
	dAcc = populate_dAcc()

	# See if Contact already entered
	if lao.SkipFile(dAcc['EMAIL'], '', 'CHECK', usefile=skipfile):
		continue

	# Find Create Entity Account
	print(dAcc['ENTITY'])
	if dAcc['ENTITY'] != 'None' and dAcc['ENTITY'] != '' and dAcc['ENTITY'] != None:
		td.colorText(' Person: {0}'.format(dAcc['NAME']), 'ORANGE')
		print('\n Enter Business...')
		dAcc = acc.find_create_account_entity(service, dAcc)
	# Print Entity Info
	if dAcc['ENTITY'] != 'None':
		print('\n ENTITY ENTERED\n')
		print(' {0}\n {1}\n {2}, {3} {4}\n'.format(dAcc['ENTITY'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))

	# Find Create Person Account
	print('\n Enter Person...')
	contactName, AID, dAcc = acc.find_create_account_person(service, dAcc)

	# Update Cateory with Market Insights & Advisors
	update_category()

	print('\n Contact entered...')
	ui = td.uInput('\n [Enter] to confirm or [00] to quit > ')
	if ui == '00':
		exit('\n Terminating program...')

	lao.SkipFile(dAcc['EMAIL'], '', 'WRITE', usefile=skipfile)
	

	


	# Update Category
	# fields = 'Id, Category__c'
	# wc = "Id = '{0}'".format(AID)
	# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	# results = bb.sfquery(service, qs)
	# dup = results[0]
	# updateRec = False
	# if not 'Bret Rinehart' in dup['Category__c']:
	# 	dup['Category__c'].append('Bret Rinehart')
	# 	updateRec = True
	# if not 'Developer List A' in dup['Category__c']:
	# 	dup['Category__c'].append('Developer List A')
	# 	updateRec = True
	# pprint(dup)
	# td.uInput('\n Continue... > ')
	# if updateRec:
	# 	bb.sfupdate(service, dup)
	# lao.SkipFile(dAcc['NAME'], '', 'WRITE', usefile=skipfile)


	# Add to Market Mailer
	# if contactName != '':
	# 	fields = 'Id, Category__c, Top100__c'
	# 	wc = "Id = '{0}'".format(AID)
	# 	qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	# 	results = bb.sfquery(service, qs)
	# 	updateAccount = False
	# 	CAT = results[0]['Category__c']
	# 	if not dAcc['CATEGORY'] in CAT:
	# 		CAT.append(dAcc['CATEGORY'])
	# 		updateAccount = True
	# 	TOP100 = results[0]['Top100__c']
	# 	if not dAcc['TOP100AGENT'] in TOP100:
	# 		TOP100.append(dAcc['TOP100AGENT'])
	# 		updateAccount = True
	# 	if updateAccount:
	# 		dUpdate = {'type': 'Account', 'Id': AID, 'Category__c': CAT, 'Top100__c': TOP100}
	# 		upresults = bb.sfupdate(service, dUpdate, 'Account')
	# exit('\n Fin')

exit('\nFin')
	
