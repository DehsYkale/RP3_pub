

import acc
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
import lao
from pprint import pprint
import xlwings as xw
import xxl
import pandas as pd

def get_Skip_Domains_List():
	td.banner('Email Domain Format Finder v03')
	ui = '\n Open Skip Domains spreadsheet to edit [0/1/00] > ')
	while 1:
		if ui == '0':
			break
		elif ui == '1':
			lao.openFile(fSkipDomains)
			'\n Continue... > ')
			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')
	
	print('\n Creating Skip Domains list...')
	dSkipDomains = lao.spreadsheetToDict(fSkipDomains)
	lSkipDomains = []
	for dsd in dSkipDomains:
		lSkipDomains.append(dSkipDomains[dsd]['SKIP DOMAINS'])
	print(' Skip Domains list created...')

	return lSkipDomains

# Make a csv of all TF contacts
def make_All_TF_Contacts_CSV():

	print('\n Getting contacts from TF...')
	# TerraForce Query
	fields = 'default'
	wc = 'IsPersonAccount = TRUE'
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

	# Write results to csv
	with open(fTF_All_Contacts, 'w', newline='') as f:
		fout = csv.writer(f)
		header = [
			'AID',
			'PersonName',
			'NF',
			'NM',
			'NL',
			'Email',
			'PersonStreet',
			'PersonCity',
			'PersonState',
			'PersonZipCode',
			'PersonPhone',
			'PersonMobile',
			'PersonHome',
			'EID',
			'EntityName',
			'EntityStreet',
			'EntityCity',
			'EntityState',
			'EntityZipCode',
			'EntityPhone']
		fout.writerow(header)
		for row in results:
			person_name = '{0} {1}'.format(row['FirstName'], row['LastName'], )
			if row['Company__c'] == 'None':
				EID = 'None'
				entity = 'None'
				entity_street = 'None'
				entity_city = 'None'
				entity_state = 'None'
				entity_zip = 'None'
				entity_phone = 'None'
			else:
				EID = row['Company__c']
				entity = row['Company__r']['Name']
				entity_street = row['Company__r']['BillingStreet']
				entity_city = row['Company__r']['BillingCity']
				entity_state = row['Company__r']['BillingState']
				entity_zip = row['Company__r']['BillingPostalCode']
				entity_phone = row['Company__r']['Phone']
			lContactInfo = [
				row['Id'],
				person_name,
				row['FirstName'],
				row['MiddleName__c'],
				row['LastName'], 
				row['PersonEmail'],
				row['BillingStreet'],
				row['BillingCity'],
				row['BillingState'],
				row['BillingPostalCode'],
				row['Phone'],
				row['PersonMobilePhone'],
				row['PersonHomePhone'],
				EID,
				entity,
				entity_street,
				entity_city,
				entity_state,
				entity_zip,
				entity_phone
			]
			# Change blank values to 'None'
			lout = []
			for val in lContactInfo:
				if val == '':
					val = 'None'
				lout.append(val)

			try:
				fout.writerow(lout)
			except UnicodeEncodeError:
				pass
			# 	print('\n UnicodeEncodeError')
			# 	print(row['Id'])
			# 	exit()
			# fout.writerow(lout)

	# lao.openFile(fTF_All_Contacts)

# Format Name
def name_formatter(name):
	name = name.strip()
	name = name.replace('"', "")
	name = name.replace('Ph.D', "")
	if name.isupper():
		name = name.title()
	return name

# Assign variables to dictionary
def create_Acc_Dict():
	# dAcc = acc.getBlankAccountDictionary()
	dAcc = dicts.get_blank_account_dict()

	dAcc['EID'] = row['EID']
	dAcc['ENTITY'] = row['EntityName']

	dAcc['AID'] = row['AID']
	dAcc['NF'] = name_formatter(row['NF'])
	dAcc['NM'] = name_formatter(row['NM'])
	dAcc['NL'] = name_formatter(row['NL'])
	dAcc['NFL'] = dAcc['NF'].lower()
	dAcc['NML'] = dAcc['NM'].lower()
	dAcc['NLL'] = dAcc['NL'].lower()
	dAcc['NFI'] = dAcc['NF'][:1].lower().strip()
	dAcc['NMI'] = dAcc['NM'][:1].lower().strip()
	dAcc['NLI'] = dAcc['NL'][:1].lower().strip()
	dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	dAcc['HYPERLINKPERSON'] = '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}", "{1}")'.format(dAcc['AID'], dAcc['NAME'])
	dAcc['EMAILUSERNAME'] = row['Email'].split('@')[0].lower().strip()
	try:
		dAcc['EMAILDOMAIN'] = row['Email'].split('@')[1].lower().strip()
	except IndexError:
		td.warningMsg(' An error occured writing the email domain...')
		print('\n Email: {0}\n'.format(row['Email']))
		pprint(row)
		exit()

	if dAcc['EID'] == 'None':
		dAcc['HYPERLINKENTITY']  = 'None'
	else:
		dAcc['HYPERLINKENTITY'] = '=HYPERLINK("https://landadvisors.my.salesforce.com/{0}", "{1}")'.format(dAcc['EID'], dAcc['ENTITY'])
	# pprint(dAcc)
	# exit()
	return dAcc

# Determine email name format
def get_emailFormat():
	
	emailFormat = 'None'
	# Example: William Scott Landis
	# wlandis
	if dAcc['EMAILUSERNAME'] == '{0}{1}'.format(dAcc['NFI'], dAcc['NLL']):
		# emailFormat = 'firstinitial_last'
		emailFormat = 'NFI_NL'

	# william
	elif dAcc['EMAILUSERNAME'] == '{0}'.format(dAcc['NFL']):
		# emailFormat = 'only_first'
		emailFormat = 'NF'
		
	# landis
	elif dAcc['EMAILUSERNAME'] == '{0}'.format(dAcc['NLL']):
		# emailFormat = 'only_last'
		emailFormat = 'NL'
		
	# william.landis
	elif dAcc['EMAILUSERNAME'] == '{0}.{1}'.format(dAcc['NFL'], dAcc['NLL']):
		# emailFormat = 'first_dot_last'
		emailFormat = 'NF_dot_NL'
		
	# w.landis
	elif dAcc['EMAILUSERNAME'] == '{0}.{1}'.format(dAcc['NFI'], dAcc['NLL']):
		# emailFormat = 'firstinitial_dot_last'
		emailFormat = 'NFI_dot_NL'
		
	# william_landis
	elif dAcc['EMAILUSERNAME'] == '{0}_{1}'.format(dAcc['NFL'], dAcc['NL']):
		# emailFormat = 'first_underscore_last'
		emailFormat = 'NF_underscore_NL'
		
	# williamlandis
	elif dAcc['EMAILUSERNAME'] == '{0}{1}'.format(dAcc['NFL'], dAcc['NLL']):
		# emailFormat = 'first_last'
		emailFormat = 'NF_NL'
		
	# williaml
	elif dAcc['EMAILUSERNAME'] == '{0}{1}'.format(dAcc['NFL'], dAcc['NLI']):
		# emailFormat = 'first_lastinitial'
		emailFormat = 'NF_NLI'
		
	# williamslandis
	elif dAcc['EMAILUSERNAME'] == '{0}{1}{2}'.format(dAcc['NFI'], dAcc['NMI'], dAcc['NLL']):
		# emailFormat = 'first_middleinitial_last'
		emailFormat = 'NF_NMI_NL'
		
	# williamsl
	elif dAcc['EMAILUSERNAME'] == '{0}{1}{2}'.format(dAcc['NFL'], dAcc['NMI'], dAcc['NLI']):
		# emailFormat = 'first_middleinitial_lastinitial'
		emailFormat = 'NF_NMI_NLI'
	
	# wl
	elif dAcc['EMAILUSERNAME'] == '{0}{1}'.format(dAcc['NFI'], dAcc['NLI']):
		# emailFormat = 'first_middleinitial_lastinitial'
		emailFormat = 'NFI_NLI'

	#w
	elif dAcc['EMAILUSERNAME'] == '{0}'.format(dAcc['NFI']):
		# emailFormat = 'first_middleinitial_lastinitial'
		emailFormat = 'NFI'
	
	return emailFormat

# Check if EID, Domain and Email Format alread exits
def domainExists():
	# Skip 'None' Email Format
	domain_exists = False
	if ladd_to_lin[0] == 'None':
		return True
	for dom in dEntered_Domains:
		dDom = dEntered_Domains[dom]
		
		# if dDom['EID'] in ladd_to_lin:
		# 	return True, 
		if dDom['DOMAIN'] in ladd_to_lin:
			if dDom['EMAILFORMAT'] in ladd_to_lin:
				domain_exists = True
	return domain_exists

service = fun_login.TerraForce()
fSkipDomains = 'F:/Research Department/Code/Databases/Skip Domains.xlsx'
lSkipDomains = get_Skip_Domains_List()
wb = xw.Book('F:/Research Department/Code/Databases/Domains Email Format v03.xlsx')
sht = wb.sheets('Domains')
nextrownum = xxl.getNumberRows(sht) + 1
fTF_All_Contacts = 'F:/Research Department/Code/Databases/TF_All_Contacts_v01.csv'

while 1:
	td.banner('Email Domain Format Finder v03')
	ui = '\n Make CSV of all TF contacts [0/1/00] > ')
	if ui == '0':
		print(' Using existing csv...')
		break
	elif ui == '1':
		make_All_TF_Contacts_CSV()
		print(' Fresh csv created...\n')
		ui = '\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		break
	elif ui == '00':
		exit('\n Terminating program...')
	else:
		td.warningMsg('\n Invalid input...try agian...')
		lao.sleep(2)


dTF_All_Contacts = dicts.spreadsheet_to_dict(fTF_All_Contacts)

# Create in list for Excel file with header titles
lin = [['EMAIL FORMAT', 'EMAILUSERNAME', 'DOMAIN', 'NF', 'NM', 'NL', 'NAME', 'ENITY', 'PERSON TFID', 'ENTITY TFID']]

# Cycle through contacts
dEntered_Domains = {0:{'EID': 'XXX', 'DOMAIN': 'XXX', 'EMAILFORMAT': 'XXX'}}
count = 1
print('\n Building domain spreadsheet...')
for contact in dTF_All_Contacts:
	row = dTF_All_Contacts[contact]
	print(row['Email'])
	if row['Email'] == 'None' or row['Email'] == '':
		continue
	# Skip if domain is in Skip Domains
	skipDom = False
	for domain in lSkipDomains:
		if domain in row['Email']:
			skipDom = True
			break
	if skipDom:
		continue

	# Variable dictionary
	dAcc = create_Acc_Dict()

	# Determine email name format
	dAcc['EMAILFORMAT'] = get_emailFormat()

	# Make list to add to lin
	ladd_to_lin = [dAcc['EMAILFORMAT'], dAcc['EMAILUSERNAME'], dAcc['EMAILDOMAIN'], dAcc['NF'], dAcc['NM'], dAcc['NL'], dAcc['HYPERLINKPERSON'], dAcc['HYPERLINKENTITY'],  dAcc['AID'], dAcc['EID']]

	# Skip if there is no match to the email name or if domain and email format exists
	if domainExists():
		continue

	lin.append(ladd_to_lin)
	
	# Add to dictionary
	dEntered_Domains[count] = {
		'EID': dAcc['EID'],
		'DOMAIN': dAcc['EMAILDOMAIN'],
		'EMAILFORMAT': dAcc['EMAILFORMAT']
	}
	count += 1

	# lIn.append([dVar['entityDom'], emailFormat, dVar['emailName'], dVar['firstname'], dVar['lastname'], dVar['company'], dVar['companyID']])

df = pd.DataFrame(lin)
sht.range('A1').options(index=False, header=False).value = df
	# print emailName
	# print firstname
	# print lastname
	# print firstinitial
	# print entityDom
	# print emailFormat
	# # pprint(row)
	# print
	# print
	# exit()