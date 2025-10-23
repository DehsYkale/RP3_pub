
# Make an export of all the emails for import into MailChimp

import bb
import csv
from os import system
import dicts
import fun_login
from json import dump
import lao
from pprint import pprint
import fun_text_date as td

def make_west_valley_email_list(service):
	print(' Processing West Valley Email List')
	lWest_Valley_submarkets = dicts.get_phoenix_west_valley_submarkets_list()
	# TerraForce Query
	print('\n Querying TerraForce...')
	fields = 'default'
	wc = "Market__c = 'Phoenix'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	print(' Query complete...')
	lWV_emails = [['First Name', 'Last Name', 'Entity', 'Email']]
	lEntered_emails = []

	for row in results:
		# pprint(row)
		if row['Submarket__c'] in lWest_Valley_submarkets:
			if row['AccountId__c'] != 'None':
				if row['AccountId__r']['PersonEmail'] != 'None':
					submarket = row['Submarket__c']
					name_first = row['AccountId__r']['FirstName']
					name_last = row['AccountId__r']['LastName']
					email = row['AccountId__r']['PersonEmail']
					if row['Owner_Entity__c'] == 'None':
						entity = 'None'
					else:
						entity = row['Owner_Entity__r']['Name']
					if email not in lEntered_emails:
						# print(f' {name_first} {name_last} - {email} - {submarket}')
						lWV_emails.append([name_first, name_last, entity, email])
						lEntered_emails.append(email)
	return lWV_emails

def make_entity_domain_email_list(service):
	print('\n Enter Entity/Company Domain')
	domain = td.uInput('\n Domain > ').strip()
	# TerraForce Query
	fields = 'default'
	wc = f"PersonEmail LIKE '%{domain}'"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	lEntity_emails = [['First Name', 'Last Name', 'Entity', 'Email']]
	lEntered_emails = []
	for row in results:
		name_first = row['FirstName']
		name_last = row['LastName']
		email = row['PersonEmail']
		if row['Company__c'] == 'None':
			entity = 'None'
		else:
			entity = row['Company__r']['Name']
		if email not in lEntered_emails:
			# print(f' {name_first} {name_last} - {email} - {submarket}')
			lEntity_emails.append([name_first, name_last, entity, email])
			lEntered_emails.append(email)
	return lEntity_emails



service = fun_login.TerraForce()

while 1:
	td.banner('TF Export Email List for MC Maker v01')
	print(' Create Email List Options')
	print('\n  1) West Valley')
	print('  2) Email Domain of a Enity/Company')
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '1':
		lEmails = make_west_valley_email_list(service)
	elif ui == '2':
		lEmails = make_entity_domain_email_list(service)
	elif ui == '00':
		exit('\n Terminating program...')



	with open('C:/TEMP/TF_emails_list.csv', 'w', newline='') as f:
		fout = csv.writer(f)
		try:
			fout.writerows(lEmails)
		except UnicodeEncodeError:
			print(lEmails)
			continue
	lao.openFile('C:/TEMP/TF_emails_list.csv')

	print('\n File created: C:/TEMP/TF_emails_list.csv')
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

exit(' Fin...')




