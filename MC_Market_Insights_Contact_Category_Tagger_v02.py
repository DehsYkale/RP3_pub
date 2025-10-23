

import acc
# import amp
# import arcpy
import bb
import csv
import dicts
import fun_login
import lao
import os
import pandas as pd
from pprint import pprint
import fun_text_date as td
from webbrowser import open as openbrowser
import xlwings as xw
import xxl



def getTFContactsWithEmails():
	# Build email where clause and list of emails
	wcEmails = "'none@none.com'"
	lEmails = []
	for row in dMIContacts:
		if dMIContacts[row]['Market Insights'] == 'X':
			email = dMIContacts[row]['Email'].lower()
			# Build where clase for emails
			wcEmails = "{0}, '{1}'".format(wcEmails, email)
			# Build List of Emails
			lEmails.append(email)
	# TerraForce Query
	fields = 'default'
	wc = "PersonEmail IN ({0})".format(wcEmails)
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	return results, lEmails

# Clear screen and print user input progress
def printUIInput(dAcc):
	lao.banner('Contact TFMC Import')
	if lao.getUserName() == 'blandis':
		td.colorText(' [main def printUIInput]', 'YELLOW')
	msg = \
		' Record {0} of {1}\n\n' \
		' Entity             {2}\n' \
		' Contact Name       {3}\n\n' \
		' Address            {4}\n' \
		'                    {5}, {6} {7}\n\n' \
		' Phone              {8}\n' \
		' Mobile             {9}\n\n' \
		' MC Audience        {10}\n' \
		' Email              {11}\n' \
		' Category           {12}\n' \
		' ---------------------------------------------------------\n' \
	.format(
		rowCount,
		fileNoRows,
		dAcc['ENTITY'],
		dAcc['NAME'],
		dAcc['STREET'],
		dAcc['CITY'],
		dAcc['STATE'],
		dAcc['ZIPCODE'],
		dAcc['PHONE'],
		dAcc['MOBILE'],
		dAcc['MCAUDNAME'],
		dAcc['EMAIL'],
		dAcc['CATEGORY'])
	print(msg)

def findCreateTFContact():
	# Build contact dict to run Find/Create in TF
	dAcc = dicts.get_blank_account_dict()
	dAcc['NF'] = dMIContacts[row]['First Name']
	dAcc['NL'] = dMIContacts[row]['Last Name']
	try:
		dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	except UnicodeEncodeError:
		pprint(dMIContacts[row])
		exit()
	dAcc['EMAIL'] = dMIContacts[row]['Email']
	if dMIContacts[row]['Company'] == None:
		dAcc['ENTITY'] = 'None'
	else:
		dAcc['ENTITY'] = dMIContacts[row]['Company']
	# Skip adding Entity if not listed
	if dAcc['ENTITY'] != 'None':
		dAcc = acc.find_create_account_entity(service, dAcc)
	printUIInput(dAcc)
	NAME, AID, dAcc = acc.find_create_account_person(service, dAcc)
	return NAME, AID, dAcc

# def getMarketsAgentList(marketAbb):
# 	dAgentmarketAbbs = lao.getAgentDict('agentoffice')
# 	lMarketsAgents = []
# 	for agent in dAgentmarketAbbs:
# 		if marketAbb == dAgentmarketAbbs[agent]:
# 			lMarketsAgents.append(agent)
# 	return lMarketsAgents

def addMarketInsightsToCategory(AID, CATEGORY):
	dUpdate = {'type': 'Account', 'id': AID}
	print('\n PRE-CATEGORY:  {0}\n'.format(CATEGORY))
	if CATEGORY == 'None' or CATEGORY == '':
		# CATEGORY = []
		CATEGORY = ''
	
	# CATEGORY.append('Market Insights')
	CATEGORY = f'{CATEGORY};Market Insights'
	need_to_add_agent = True
	addThisAgent = 'None'
	# lMarketsAgents = getMarketsAgentList(marketAbb)
	# for agent in lMarketsAgents:
	for agent in dStaff:
		if dStaff[agent]['Roll'] == 'Agent':
			if mc_audience in dStaff[agent]['MC Audience']:
				if addThisAgent == 'None':
					addThisAgent = agent
				if agent in CATEGORY:
					need_to_add_agent = False
					break
	# Add agent to cateory if none for the market exists
	if need_to_add_agent:
		# CATEGORY.append(addThisAgent)
		CATEGORY = f'{CATEGORY};{addThisAgent}'
	print('POST-CATEGORY: {0}\n'.format(CATEGORY))
	dUpdate['Category__c'] = CATEGORY
	upResults = bb.tf_update_3(service, dUpdate)

def confirmRecord(AID):
	while 1:
		acc.printUIInput(dAcc)
		print(f'\n Record {rowCount} of {fileNoRows}')
		print('\n  1) Open TF Contact\n  2) Next Contact\n 00) Quit')
		ui = td.uInput('\n > ')
		if ui == '1':
			openbrowser('https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view'.format(AID))
		elif ui == '' or ui == '2':
			break
		elif ui == '00':
			exit('\n Fin')

lao.banner('Market Insights Contact Category Tagger v02')
# Set Variables
service = fun_login.TerraForce()
# inFile = 'F:/Research Department/MailChimp/MailChimp Admin Report Dallas - Ft Worth 2021-04-05.xlsx'
inFile = lao.guiFileOpen(path='F:/Research Department/MailChimp/', titlestring='Open MailChimp Admin Report', extension=[('Excel files', 'MailChimp*.xlsx'), ('all files', '.*')])

filename = os.path.basename(inFile)
mc_audience = filename.replace('MailChimp Admin Report ', '')[:-16]
dStaff = dicts.get_staff_dict()

# print('\n Market Abbreviations\n\n ALT  AUS  BOI  CLT  DFW  GSP  HOU  JAX  KCI  LSV  ORL   PHX  PIN  NSH  NAZ  SLC TPA  TUC\n')
# marketAbb = td.uInput('\n Enter 3 letter market abbreviation > ').upper()

dMIContacts = lao.spreadsheetToDict(inFile)

# Get dict of TF contacts from MC Admin Report MI list and a list of emails
dTFContacts, lEmails = getTFContactsWithEmails()
rowCount = 1
fileNoRows = len(lEmails)
# Cycle through emails from the MC Admin Report
for email in lEmails:
	lao.banner('Market Insights Contact Category Tagger v02')
	# print
	# print(email)
	email_in_TF = False
	# Search for email in TF query of contacts
	for row in dTFContacts:
		if email == row['PersonEmail'].lower():
			email_in_TF = True
			if 'Market Insights' in row['Category__c']:
				break
			else:
				# print(' found, but MI not in category...adding...\n')
				addMarketInsightsToCategory(row['Id'], row['Category__c'])
				email_in_TF = True
				# confirmRecord(row['Id'])
			break

	# If the email is not in TF then find/create contact
	if email_in_TF is False:
		for row in dMIContacts:
			if email == dMIContacts[row]['Email'].lower():
				NAME, AID, dAcc = findCreateTFContact()
				# pprint(dAcc)
				addMarketInsightsToCategory(AID, dAcc['CATEGORY'])
				break
		confirmRecord(AID)

	rowCount += 1



