#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Updates MailChimp Contacts with info From TF change emails

import lao
import bb
import dicts
import fun_login
import mc
import fun_text_date as td
from glob import glob
from pprint import pprint
import shutil
from win32gui import GetForegroundWindow, MoveWindow

# Menu
def menu(select2):
	# Menu
	print('\n 11) Unsubscribe Old TF/MC Email')
	if select2:
		td.instrMsg('  2) Update/Replace Email in MailChimp')
	else:
		print('  2) Update/Replace Email in MailChimp')
	print('  3) Add to MailChimp')
	print('  4) Skip/Next')
	print(' 00) Quit')
	if noPossibleMatches:  # Auto add records without matches
		ui = '3'
	else:
		ui = td.uInput('\n Select > ')
	return ui

def unsubscribe():
	lao.consoleColor('BLUE')
	td.banner('TF Changed Emails to MC v03')
	td.warningMsg('\n UNSUBSCRIBE')
	print('\n TF Email Message Record Info')
	print(' {0}'.format(contactName))
	print(' {0}'.format(emailTF))
	td.colorText('\n Choose MC Contact', 'YELLOW')
	for i in dPossibleMatches:
		dPM = dPossibleMatches[i]
		print('\n {0}) {1} {2}'.format(i, dPM['firstName'], dPM['lastName']))
		print('    {0}'.format(dPM['company']))
		print('    {0}'.format(dPM['email']))
	print(' 00) Cancel unsubscribe')
	uiEmail = int(td.uInput('\n Select > '))
	if uiEmail == '00':
		td.warningMsg('\n Unsubscribe canceled...')
		return
	uiEmail = dPossibleMatches[uiEmail]['email']
	upDict = {'email_address': uiEmail, 'status': 'unsubscribed'}
	mc.addUpdateMember(client, audience_id, upDict, upDateOnly=True)

def updateReplace(select2):
	lao.consoleColor('BLUE')
	td.banner('TF Changed Emails to MC v03')
	print('\n Update/Replace')
	print('\n TF Email Message Record Info')
	print(' {0}'.format(contactName))
	print(' {0}'.format(emailTF))
	td.colorText('\n Choose MC Contact to Update', 'YELLOW')
	for i in dPossibleMatches:
		dPM = dPossibleMatches[i]
		if dPM['lastName'].upper() == lNameTF.upper() and dPM[
			'firstName'].upper() == fNameTF.upper():
			td.colorText('\n {0}) {1} {2}'.format(i, dPM['firstName'], dPM['lastName']), 'GREEN')
			select2 = True
		else:
			print('\n {0}) {1} {2}'.format(i, dPM['firstName'], dPM['lastName']))
			select2 = False
		print('    {0}'.format(dPM['company']))
		print('    {0}'.format(dPM['email']))
	ui = int(td.uInput('\n Select > '))
	uiEmail = dPossibleMatches[ui]['email']
	upDict = {'email_address': emailTF, 'status': 'subscribed', 'merge_fields': {'FNAME': fNameTF, 'LNAME': lNameTF}}
	uiCompany = td.uInput('\n Type company or [Enter] for none > ')
	upDict['merge_fields'] = {'COMPANY': uiCompany}
	client.lists.members.update(list_id=audience_id, subscriber_hash=uiEmail, data=upDict)
	print(f'\n MailChimp updated: {fNameTF} {lNameTF}   {emailTF}')
	print('\n Select [4] to continue to next Contact...')
	return select2

def addNewContact():
	# Make MC upDict
	upDict = {'email_address': emailTF, 'status': 'subscribed', 'merge_fields': {'FNAME': fNameTF, 'LNAME': lNameTF}}
	mc.addUpdateMember(client, audience_id, upDict)

def archiveFile(filename):
	filename_arch = filename.replace('TF_Changes_2\\', 'TF_Changes_2\\Arch\\')
	print('here1 Archiving')
	print(f'\n Archiving: {filename_arch}')
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	shutil.move(filename, filename_arch)

# Get the Agent's MC id and archive files created by Research (MC Aud ID = 'None')
def get_agent_MC_audience_member_list(lFiles):
	# Check if Agent or EA has made record changes
	audience_id, dAudience_members = None, None
	for filename in lFiles:
		if agent in filename:
			# Select only the first list if agent has more than one
			agent_mc_audience_id = dStaff[agent].split(',')
			audience_id = agent_mc_audience_id[0]
			print(f'\n Getting {agent} list members...')
			dAudience_members = mc.get_audience_members(client, audience_id, 'get_all', includeInterests=False)
			break
	
	return audience_id, dAudience_members

# Archive non-Agent/EA TF changes
def archive_non_agents_ea_changes():
	lIn_files = glob('F:/Research Department/scripts/Data/TF_Changes_2/*.txt')
	for filename in lIn_files:
		if not 'landadvisors.com' in filename:
			archiveFile(filename)
		# Check if Agent is a 'None' MC Aud ID
		for agent in dStaff:
			agent_mc_audience_id = dStaff[agent]
			# print(agent)
			# print(agent_mc_audience_id)
			if agent in filename:
				# Archive users that do not have an Audience
				if agent_mc_audience_id == 'None':
					archiveFile(filename)
					break
				# Skip Pino and Campbell for now
				elif agent == 'cpino' or agent == 'dcampbell':
					break

def get_tf_account_info(emailTF):
	strStart = line.find('.com') + 5
	AID = line[strStart:]
	print(AID)
	AID = AID.strip()
	AID = AID.replace('>', '')
	print(AID)
	# TerraForce Query
	fields = 'default'
	wc = f"PersonEmail = '{emailTF}'"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	pprint(results)
	for row in results:
		print(row)
		print(row['PersonEmail'])
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

client = fun_login.MailChimp()
service = fun_login.TerraForce()

# Load Agent Dict
# {[agent email name]: [MC Audience ID]}
dStaff = dicts.get_staff_dict('mcDict', skipFormerEmployees=False)

# Archive non-Agent/EA TF changes
archive_non_agents_ea_changes()

# Get list of files
lIn_files = glob('F:/Research Department/scripts/Data/TF_Changes_2/*.txt')

# Cycle through Agents and their Audence member lists
for agent in dStaff:
	# Skip EAs
	if agent == 'cpino' or agent == 'dcampbell':
		continue
	
	audience_id, dAudience_members = get_agent_MC_audience_member_list(lIn_files)

	# No TF changes made by this Agent/EA
	if audience_id is None:
		print(f'\n No TF record changes made by {agent}')
		lao.sleep(2)
		continue

	# Cycle throught files
	for filename in lIn_files:

		# Find agent's files
		if agent not in filename:
			continue

		lao.consoleColor('BLACK')
		td.banner('TF Changed Emails to MC v03')

		print('here2 Entering data')
		print(agent)
		# print(audience_id)
		print(filename)

		# Read the TF email msg file
		with open(filename, 'r') as f:
			lines = f.readlines()
		# Get contact name and email from TF email file
		emailTF = 'None'
		for line in lines:
			# print(line)
			# if 'https://landadvisors.my.salesforce.com' in line:
			# 	get_tf_account_info(line)
				
			if 'Name:' in line:
				contactName = line.strip('Name: ').strip()
				lcontactName = contactName.split(' ')
				fNameTF = lcontactName[0]
				lNameTF = 'None'
				if len(lcontactName) == 2:
					lNameTF = lcontactName[1]
				elif len(lcontactName) == 3:
					# Name has middle initial
					if len(lcontactName[1]) == 1:
						lNameTF = lcontactName[2]
					# Two word last name
					else:
						lNameTF = '{0} {1}'.format(lcontactName[1], lcontactName[2])
			if 'Email:' in line:
				emailTF = line.replace('Email: ', '').strip()
				print('here6 tf email')
				print(emailTF)
		
		# Archive files without email
		if emailTF == '' or emailTF == 'None':
			print('\n No email in change record...')
			lao.sleep(2)
			archiveFile(filename)
			continue
		
		# get_tf_account_info(emailTF)

		# See if Email Exists in dAudience_members
		mcEmailExists = False
		# Check if email (Member) exits in Agent's Audience
		for member in dAudience_members[0]:
			# pprint(dAudience_members)
			
			mcEmail = dAudience_members[0][member]['email']
			if emailTF == mcEmail:
				mcEmailExists = True
				break
		
		# Email exists in TF & MC
		# Move TF email msg to Arch(ive) folder
		if mcEmailExists:
			archiveFile(filename)

		# Add/Update new email or contact to MC
		else:
			td.banner('TF Changed Emails to MC v03')
			print('here7 Updating MC...')
			print(' {0}'.format(agent.upper()))
			print(' {0}'.format(filename))

			# Make list of possible matches of TF contact in MC based on last Name
			dPossibleMatches = {}
			index = 1
			for member in dAudience_members[0]:
				if dAudience_members[0][member]['lastName'].upper() == lNameTF.upper() and dAudience_members[0][member]['firstName'][:1].upper() == fNameTF[:1].upper() and dAudience_members[0][member]['status'] == 'subscribed':
					dSingleMem = dAudience_members[0][member]
					dPossibleMatches[index] = {'email': dSingleMem['email'], 'firstName': dSingleMem['firstName'], 'lastName': dSingleMem['lastName'], 'company': dSingleMem['company']}
					index += 1
			select2 = False
			if dPossibleMatches == {}:
				print('\n No Possible Matches')
				noPossibleMatches = True
			else:
				lao.consoleColor('BLUE')
				td.colorText('\n MC Records - Possible Matches', 'YELLOW')
				noPossibleMatches = False  # Auto add records without matches
				for i in dPossibleMatches:
					dPM = dPossibleMatches[i]
					if dPM['lastName'].upper() == lNameTF.upper() and dPM['firstName'].upper() == fNameTF.upper():
						td.colorText('\n {0}) {1} {2}'.format(i, dPM['firstName'], dPM['lastName']), 'YELLOW')
						select2 = True
					else:
						print('\n {0}) {1} {2}'.format(i, dPM['firstName'], dPM['lastName']))
						select2 = False
					print('    {0}'.format(dPM['company']))
					print('    {0}'.format(dPM['email']))
			# print agent_mc_audience_id
			while 1:
				print('\n TF Record')
				td.colorText('\n {0}'.format(contactName), 'CYAN')
				td.colorText(' {0}'.format(emailTF), 'CYAN')
				# Menu
				ui = menu(select2)
				select2 = False
				if ui == '11':  # Unsubscribe
					unsubscribe()
				elif ui == '2':  # Change Email but keep MC record
					select2 = updateReplace(select2)
				elif ui == '3':  # Add New
					addNewContact()
					break
				elif ui == '4':
					break
				elif ui == '00':
					exit()
				else:
					td.warningMsg('\n Invalid input...try again...')
			if ui == '1' or ui == '2':
				td.uInput('\n Continue...')
			lao.consoleColor('BLACK')
			archiveFile(filename)
			# print('\n Email exists?')
			# td.uInput(mcEmailExists)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
td.instrMsg('\n Fin')