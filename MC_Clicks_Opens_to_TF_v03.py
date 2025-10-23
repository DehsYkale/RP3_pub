# Check if Contacts with Opens and Clicks are in TF and add them if they are not.

import acc
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
import lao
import mc
import sys
import datetime
from pprint import pprint
import time
from os import system
import webs

# Get a dict of contacts sent the eblast that clicked or opened that are not in TF
def get_contacts_missing_from_TF():
	lMC_emails = []
	# Lower case all emails
	for row in dSentTo:
		# print(dSentTo[row]['Email'])
		email_lower = dSentTo[row]['Email'].lower()
		lMC_emails.append(email_lower)

	email_count = 1
	lMC_emails_subset = []
	lTF_emails = []
	last_email = False
	# Cycle through the MC emails sent
	print('\n Checking TF for missing emails...')
	for index, email in enumerate(lMC_emails):
		# Check if last email in list
		lMC_emails_subset.append(email)
		if index == len(lMC_emails) - 1:
			last_email = True
		if email_count > 50 or last_email is True:
			# Query TF to find MC emails. Max query can be 4,000 characters.
			fields = 'default'
			wc = "PersonEmail IN ('{}')".format("','".join(lMC_emails_subset))
			results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
			for row in results:
				tf_email_lower = row['PersonEmail'].lower()
				if not tf_email_lower in lTF_emails:
					lTF_emails.append(tf_email_lower)
			email_count = 1
			lMC_emails_subset = []
		else:
			email_count += 1

	lTF_missing_contacts_email = []
	for mc_email in lMC_emails:
		if not mc_email in lTF_emails:
			lTF_missing_contacts_email.append(mc_email)

	print('\n Making dictionary of contacts not in TF that clicked or opened the eblast.')
	print(' Please stand by...')
	dAdd_to_TF = {}
	for missing_email in lTF_missing_contacts_email:
		# Only add contacts to TF that have opened or clicked on the campaign
		action = mc.getCampaignActions(client, CID, missing_email)
		if action == 'CLICKED': # Skipping OPENED for now or action == 'OPENED':
			for row in dSentTo:
				# Get the contact's name and company and add it to the dict dAdd_to_TF
				if dSentTo[row]['Email'] == missing_email:
					if dSentTo[row]['Name'] != 'No Name Listed':
						name_mc = dSentTo[row]['Name']
						name_mc = name_mc.split(',')
						name_last = name_mc[0].strip()
						name_first = name_mc[1].strip()
						name_full = '{0} {1}'.format(name_first, name_last)
						company = 'None'
						if dSentTo[row]['Company'] != '':
							company = dSentTo[row]['Company']

						dAdd_to_TF[missing_email] = {'FirstName': name_first, 'LastName': name_last, 'FullName': name_full, 'Company': company}

	return dAdd_to_TF

td.console_title('MC_Clicks_Open_to_TF_v03')
td.banner('MC Click & Open to TF v03')

service = fun_login.TerraForce()
client = fun_login.MailChimp()

while 1:
	td.banner('MC Click & Open to TF v03')
	# lao.consoleColor('YELLOW')

	campName, CID, listID, agentEmail, agent, mcCamps = mc.selectCampaign(client, 'MailClickOpen', mcCamps='None')
	# lao.consoleColor('YELLOW')
	lAgent = [agent]

	td.banner('MC Click & Open to TF v03')

	fix_broken_records = True
	if fix_broken_records is True:
		###################################################################
		dSentTo = mc.getReportSentTo(client, CID)
		dFixThem = get_contacts_missing_from_TF()
		num_FixThem_records = len(dFixThem)
		counter = 1

		for contact in dFixThem:
			td.banner('MC Click & Open to TF v03')
			print(f' {counter} : {num_FixThem_records}\n')
			dAcc = dicts.get_blank_account_dict()

			dAcc['NAME'] = dFixThem[contact]['FullName']
			dAcc['NF'] = dFixThem[contact]['FirstName']
			dAcc['NL'] = dFixThem[contact]['LastName']
			dAcc['ENTITY'] = dFixThem[contact]['Company']
			dAcc['EMAIL'] = contact
			# Skip missing Names
			if dAcc['NF'] == 'None' or dAcc['NL'] == 'None' or dAcc['NF'] == '' or dAcc['NL'] == '':
				counter += 1
				continue
			
			# Skip emails from some broakerage firms
			lSkip_domains = ['leearizona.com', 'lee-associates.com', 'cushwake.com', 'marcusmillichap.com']
			for dom in lSkip_domains:
				if dom in dAcc['EMAIL']:
					continue
			
			print(f'\n Agent: {agent}')
			print('\n Contact Info')
			print('-' * 50)
			print(' Name: {NAME}\n Entity: {ENTITY}\n Email: {EMAIL}'.format(**dAcc))

			# Ask user if they want to enter and Entity
			if dAcc['ENTITY'] == 'None':
				td.warningMsg('\n No Entity listed...')
				ui = td.uInput('\n Type Entity, [00] or [Enter] for None > ')
				if ui == '00':
					exit('\n Terminating program...')
				elif ui != '':
					dAcc['ENTITY'] = ui

			if dAcc['ENTITY'] != 'None':
				dAcc = acc.find_create_account_entity(service, dAcc)

			name, AID, dAcc = acc.find_create_account_person(service, dAcc)

			# User wants to skip record
			if name == 'None' and AID == 'None' and dAcc == 'None':
				counter += 1
				continue
				
			while 1:
				ui = td.uInput('\n [Enter] to Continue, [1] to open TF or [00] to quit... > ')
				if ui == '00':
					exit('\n Terminating program...')
				elif ui == '1':
					webs.openTFAccId(AID)
				else:
					break
			
			counter += 1
	
	lao.consoleColor('RED')
	ui = td.uInput('\n Process complete...\n\n[Enter] to do more or [00] to quit > ')
	if ui == '00':
		lao.consoleColor('BLACK')
		exit('\n Terminating program...')
	# Enter the Campaign Name into the skip file
	lao.SkipFile(campName, 'skipMailClickOpen', 'WRITE')
	# lao.consoleColor('YELLOW')

print('\n fin')
exit()



