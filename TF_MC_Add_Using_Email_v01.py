# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# Adds contact to TF and MailChimp

import lao

import django
from django.template import Template, Context
from django.conf import settings
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

user = lao.getUserName()
import acc
import bb
import csv
import dicts
import fun_login
from glob import glob
import lao
import mc
import os
from pprint import pprint
import pyperclip
import fun_text_date as td


# Clear screen and print user input progress
def printUIInput(dAcc):
	lao.print_function_name('internal def printUIInput')

	lao.banner('TF MC Add Using Email v01')
	if isNewSubscriber:
		td.colorText('\n NEW SUBSCRIBER REQUEST\n', 'GREEN')
		td.warningMsg('TEST')

	msg = \
		' Entity              {0}\n' \
		' Contact Name        {1}\n\n' \
		' Phone               {2}\n\n' \
		' MC Audience         {3}\n' \
		' Email               {4}\n' \
		' Comments            {5}\n' \
		.format(
			dAcc['ENTITY'],
			dAcc['NAME'],
			dAcc['PHONE'],
			dAcc['MCAUDNAME'],
			dAcc['EMAIL'],
			dAcc['MCSUBMSG'])
	print(msg)
	# print('\n Email File   :       {0}\n'.format(emailfilename))

def is_email_in_TF(dAcc):
	lao.print_function_name('internal def is_email_in_TF')

	is_in_TF = False
	# TerraForce Query
	# wc = "PersonEmail = '{0}'".format(dAcc['EMAIL'])
	# results = bb.tfquery2(service, rec_type='Person', where_clause=wc, limit=None)
	# TerraForce Query
	fields = 'default'
	wc = "PersonEmail = '{0}'".format(dAcc['EMAIL'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	if results != []:
		r = results[0]
		dAcc['AID'] = r['Id']
		dAcc['NAME'] = r['Name']
		dAcc['NF'] = r['FirstName']
		dAcc['NL'] = r['LastName']
		if r['Company__c'] != '':
			dAcc['EID'] = r['Company__c']
			dAcc['ENTITY'] = r['Company__r']['Name']
		if r['Phone'] != '' and dAcc['PHONE'] == 'None':
			dAcc['PHONE'] = r['Phone']
		is_in_TF = True
		print('\n Email {0}, {1} found in TF...'.format(dAcc['EMAIL'], dAcc['NAME']))
		lao.sleep(4)
	return dAcc, is_in_TF

def dissectEmail(dAcc):
	lao.print_function_name('internal def dissectEmail')

	email = td.uInput('\n Enter Email [00] > ')
	if email == '00':
		exit('\n Terminating program...')
	email = email.strip()
	dAcc['EMAIL'] = email.lower()
	dAcc, is_in_TF = is_email_in_TF(dAcc)

	if is_in_TF is False:
		lEmail = email.split('@')

		# parce name
		if '.' in lEmail[0]:
			lTempName = lEmail[0].split('.')
			tempFirst = lTempName[0].title()
			tempLast = lTempName[1].title()
			print('\n Possible Name: {0} {1}'.format(tempFirst, tempLast))
		else:
			tempFirst = lEmail[0][:1].title()
			tempLast = lEmail[0][1:].title()
		msg = \
			'\n\n Name:   {0} {1}' \
			.format(
				tempFirst,
				tempLast)
		print(msg)
		msg = \
			'\n\n [Enter] to use this name' \
			'\n [Type] First name' \
			'\n [Type] Full name' \
			'\n\n 00) Quit'
		print(msg)
		ui = td.uInput('\n Input > ').title()
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '':
			name = '{0} {1}'.format(tempFirst, tempLast)
		elif ' ' in ui:
			name = ui
		else:
			name = '{0} {1}'.format(ui, tempLast)
		dAcc['NAME'] = name

		tempCompany = lEmail[1].split('.')
		tempCompany = tempCompany[0].title()
		pyperclip.copy(tempCompany)
		print('\n Possible Company: {0}'.format(tempCompany))
		msg = \
		'\n     1] to use this name' \
		'\n  Type] Company' \
		'\n Enter] for no Company' \
		'\n\n 00) Quit'
		print(msg)
		ui = td.uInput('\n Enter Company > ')
		if email == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			dAcc['ENTITY'] = tempCompany
		elif ui == '':
			dAcc['ENTITY'] = 'None'
		else:
			dAcc['ENTITY'] = ui
	
	return email, dAcc, is_in_TF

# Scape the information from the new subscriber email
def scrapeNewMCSubsciberEmails(dAcc):
	lao.print_function_name('internal def scrapeNewMCSubsciberEmails')

	while 1:
	# get list of new subscriber email text files
		lNewSubsEmailFiles = glob('F:/Research Department/MailChimp/New MC Subscribers/*.txt')
		# Return None if there are not new subscriber email text files
		if lNewSubsEmailFiles == []:
			return dAcc, 'None'
		
		# Scrape new subscriber email text files
		for emailfilename in lNewSubsEmailFiles:
			# Delete duplicates
			if ' - 1.txt' in emailfilename:
				os.remove(emailfilename)
				continue


			with open(emailfilename) as f:
				lines = f.readlines()
				for line in lines:
					if 'Email Address' in line:
						temp = line.replace('Email Address', '')
						temp = temp.strip()
						temp = temp.lower()
						dAcc['EMAIL'] = temp
					elif 'First Name' in line:
						temp = line.replace('First Name', '')
						temp = temp.strip()
						dAcc['NF'] = temp
					elif 'Last Name' in line:
						temp = line.replace('Last Name', '')
						temp = temp.strip()
						dAcc['NL'] = temp
					elif 'Company \t' in line:
						temp = line.replace('Company \t', '')
						temp = temp.strip()
						dAcc['ENTITY'] = temp
					elif 'Phone Number' in line:
						temp = line.replace('Phone Number', '')
						temp = temp.strip()
						if temp != '':
							dAcc['PHONE'] = temp
					elif 'Select Market(s) of Interest' in line:
						temp = line.replace('Select Market(s) of Interest', '')
						temp = temp.strip()
						dAcc['MIMARKETS'] = temp
					elif 'Comments ' in line:
						temp = line.replace('Comments', '')
						temp = temp.strip()
						dAcc['MCSUBMSG'] = temp
					elif 'Subscriber IP' in line:
						temp = line.replace('Subscriber IP', '')
						temp = temp.strip()
						dAcc['IP'] = temp
						break
				dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
				lao.banner('Add Contacts to TF & MC')
				# pprint(dAcc)
				if dAcc['EMAIL'] == '' or dAcc['EMAIL'] == 'None':
					# f.close()
					continue
				# ui = td.uInput('\n 00 quit > ')
				# if ui == '00':
				# 	exit('\n Terminating program...')
			# f.close()
			return dAcc, emailfilename

# Determine market the new subscriber wants MIs from
def getMIMarketFromNewSubsciberEmail(dAcc, lMIMarkets):
	lao.print_function_name('internal def getMIMarketFromNewSubsciberEmail')

	for mkt in lMIMarkets:
		# Greg only for Phoenix
		if mkt == 'AZ - Phoenix':
			dAcc['MCAUDID'] = '8c10515ac1'
			dAcc['MCAUDNAME'] = 'Greg Vogel'
			return dAcc
		else:			
			for row in dStaff:
				if dStaff[row]['Roll'] == 'Agent':
					if mkt in dStaff[row]['MC New Subscriber Market']:
					# if dStaff[row]['MC New Subscriber Market'] == mkt:
						dAcc['MCAUDID'] = dStaff[row]['MC Aud ID']
						dAcc['MCAUDNAME'] = dStaff[row]['MC Audience']
						return dAcc

# Append new contact to csv to send to Advisors
def appendToNewContactsCSV():
	lao.print_function_name('internal def appendToNewContactsCSV')

	fullname = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	lLine = [
			todaydate,
			dAcc['MCAUDNAME'],
			fullname,
			dAcc['ENTITY'],
			dAcc['PHONE'],
			dAcc['EMAIL']]
	while 1:
		try:
			with open(csvMC_New_Contacts_Added, 'ab') as f:
				fout = csv.writer(f)
				fout.writerow(lLine)
				break
		except:
			td.warningMsg('\n Close Excel file!')
			td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

# Build recipiants
def buildRecipiants(MIMarket, dStaff):
	lao.print_function_name('internal def buildRecipiants')

	OPRsender = 'Land Advisors {0} MailChimp Research <research@landadvisors.com>'.format(dAcc['MCAUDNAME'])

	# Build recipient email list
	recipient = []
	for agent in dStaff:
		emailAddress = '{0} <{1}@landadvisors.com>'.format(agent, dStaff[agent]['Email'])
		if MIMarket in dStaff[agent]['MC New Subscriber Market'] and not emailAddress in recipient:
			recipient.append(emailAddress)
	recipient.append('Bill Landis <blandis@landadvisors.com>')
	recipient.append('Michael Klingen <mklingen@landadvisors.com>')

	return recipient, OPRsender

# Build HTML Dict for email template
def build_html_dict():
	lao.print_function_name('internal def build_html_dict')

	address = '{0}, {1}, {2} {3}'.format(dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE'])
	urlName = 'https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view'.format(dAcc['AID'])
	urlEntity = 'https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view'.format(dAcc['EID'])
	if dAcc['MCSUBMSG'] == '':
		dAcc['MCSUBMSG'] = td.uInput('\n Copy/paste message from subsciber or [Enter] for none\n\n ----> ')
		if dAcc['MCSUBMSG'] == '':
			dAcc['MCSUBMSG'] = 'None'

	htmldict = {'TLT': 'Land Advisors Research Department',
				'NAME': dAcc['NAME'],
				'AID': dAcc['AID'],
				'URLNAME': urlName,
				'ENTITY': dAcc['ENTITY'],
				'EID': dAcc['EID'],
				'URLENTITY': urlEntity,
				'ADDRESS': address,
				'PHONE': dAcc['PHONE'],
				'EMAIL': dAcc['EMAIL'],
				'MSG': dAcc['MCSUBMSG']
				}
	return htmldict

# Build & Send email of new subscriber to agents
def build_send_new_subscriber_email():
	lao.print_function_name('internal def build_send_new_subscriber_email')
	
	# Temp recipiant Bill only
	# recipient = ['Bill Landis <blandis@landadvisors.com>']

	msg = MIMEMultipart('alternative')
	msg['Subject'] = 'New Subsciber Alert'
	msg['From'] = OPRsender
	msg['To'] = ','.join(recipient)
	msg['Date'] = formatdate(localtime=True)

	html = open('F:/Research Department/Code/RP3/templates/mc_new_subscriber_01.html', 'r').read()

	# assign Template
	t = Template(html)
	c = Context(htmldict)
	html = t.render(c)
	with open('C:/TEMP/MC_MI_NEW_SUBSCRIBER_OPR.html', 'w') as h:
		h.write(html)

	# create body of the message as plain text and html
	text = 'LAO New Market Insights Subscriber'
	# record MIME types of both parts
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html') # .encode('utf8'), 'html')

	msg.attach(part1)
	msg.attach(part2)
	print('\n Sending...')
	s = smtplib.SMTP('mx1.webville.net')
	s.sendmail(OPRsender, recipient, msg.as_string())
	s.quit()
	print('\n Pausing for 5 seconds...')
	lao.sleep(5)

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': 'F:/Research Department/Code/Research/templates'
	}
]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

client = fun_login.MailChimp()
service = fun_login.TerraForce()
dStaff = dicts.get_staff_dict()
todaydate = td.today_date('slash')
csvMC_New_Contacts_Added = 'F:/Research Department/MailChimp/MailChimp New Contacts Added.csv'

# Loop entry process until user quits
while 1:
	td.banner('TF MC Add Using Email v01')
	dAcc = dicts.get_blank_account_dict()
	# Skip this for direct entry
		# ui = td.uInput('\n Enter New Subscriber emails? [0/1/00] > ')
		# if ui == '00':
		# 		exit('\n Terminating program...')
		# elif ui == '1':
		# 	dAcc, emailfilename = scrapeNewMCSubsciberEmails(dAcc)
	
	
	if dAcc['EMAIL'] == 'None':
		isNewSubscriber = False
		printUIInput(dAcc)
		email, dAcc, is_in_TF = dissectEmail(dAcc)
		# User to enter Enity/Company
		printUIInput(dAcc)
		# # User to enter Contact Name
		dAcc = td.parse_person(dAcc)
		lMIMarkets = 'Manual Entry'
	else:
		is_in_TF = False
		isNewSubscriber = True
		# pprint(dAcc)
		# ui = td.uInput('\n Continue... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		lMIMarkets = dAcc['MIMARKETS'].split(', ')
		dAcc = getMIMarketFromNewSubsciberEmail(dAcc, lMIMarkets)
		if dAcc == None:
			td.warningMsg('\n Missing MC New Subscriber Market in lao_staff_data_v2.xlsx')
			print('\n List of Markets from new subscriber email')
			pprint(lMIMarkets)
			exit('\n Terminating program...')
	printUIInput(dAcc)

	# Check TF for Entity
	# if dAcc['ENTITY'] != 'None' and is_in_TF is False:
	if dAcc['ENTITY'] != 'None':
		dAcc = acc.find_create_account_entity(service, dAcc)
		printUIInput(dAcc)

	# if is_in_TF is False:
	tmp1, tmp2, dAcc = acc.find_create_account_person(service, dAcc)

	# Populate dAcc from TF
	dAcc = acc.populate_dAcc_from_tf(service, dAcc['AID'], dAcc=dAcc)

	# User to select MC Audience
	add_another = True
	while add_another is True:
		printUIInput(dAcc)
		ui = td.uInput(' Add {0} to MailChimp [0/1/00] > '.format(dAcc['NAME']))
		if ui == '0':
			add_another = False
		elif ui == '1':
			# User to select MC Audience
			printUIInput(dAcc)
			if dAcc['MCAUDID'] == 'None':
				dAcc['MCAUDNAME'], dAcc['MCAUDID'] = mc.select_audeince(client)
				lMIMarkets = [dAcc['MCAUDNAME'], 'Manual Entry']
			# User to select Campaign(s) from Audience
			printUIInput(dAcc)
			# pprint(dAcc)
			dAcc['MCLCAMPAIGNIDS'], isMarketInsightsSelected = mc.select_campaign_groups(client=client, listID=dAcc['MCAUDID'], listName=dAcc['MCAUDNAME'])
			dMC, dTags = dicts.get_mailchimp_add_update_dict(dAcc)
			mc.addUpdateMember(client, listID=dAcc['MCAUDID'], dMC=dMC, upDateOnly=False)
			# appendToNewContactsCSV()

			# Update TF Contact Category with Market Insights and Agents
			if isMarketInsightsSelected:
				dAccCat ={'type': 'Account', 'Id': dAcc['AID']}

				lAgents = ['Market Insights']
				for agent in dStaff:
					dA = dStaff[agent]
					if dAcc['MCAUDID'] in dA['MC Aud ID']:
						if dA['Roll'] == 'Agent' and dA['LAO'] == 'Yes':
							lAgents.append(agent)
				# pprint(lAgents)

				# TerraForce Query
				fields = 'default'
				wc = "Id = '{0}'".format(dAcc['AID'])
				results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

				updateContact = False
				# Trap if no Category
				if results[0]['Category__c'][0] == 'None':
					lCat = ['Market Insights']
				else:
					lCat = results[0]['Category__c'].split(';')
				# Add Advisors to Category
				for row in lAgents:
					if row not in lCat:
						lCat.append(row)
				if 'Market Insights' not in lCat:
					lCat.append('Market Insights')
				dAccCat['Category__c'] = ';'.join(lCat)
				
				# upResults = bb.sfupdate(service, dAccCat)
				upResults = bb.tf_update_3(service, dAccCat)

				# Build & Send email notification to agents
				printUIInput(dAcc)
				recipient, OPRsender = buildRecipiants(lMIMarkets[0], dStaff)
				print('\n Agents to Notify:')
				for recip in recipient:
					print('     {0}'.format(recip))
				ui = td.uInput('\n Send email notification to Agents [0/1/00] > ')
				if ui == '1':
					
					# recipient, OPRsender = buildRecipiants(dAcc['MCAUDNAME'], dStaff)
					
					htmldict = build_html_dict()
					build_send_new_subscriber_email()
					# break
				elif ui == '00':
					exit('\n Terminating program...')
				elif ui == '0':
					td.warningMsg('\n Email notification not sent...')

					td.uInput('\n Continue [00]... > ')
					if ui == '00':
						exit('\n Terminating program...')
					# break
				
		elif ui == '00':
			exit('\n Terminating program...')

		# Loop if more markets to add
		if	'Manual Entry' in lMIMarkets:
			lMIMarkets = ['Manual Entry']
			break
		elif len(lMIMarkets) > 1:
			del lMIMarkets[0]
			dAcc['MIMARKETS'] = lMIMarkets
			dAcc = getMIMarketFromNewSubsciberEmail(dAcc, lMIMarkets)
		# delete the new subscriber email text file and from MC New Subscriber Group
		elif len(lMIMarkets) == 1:
			while 1:
				ui = td.uInput('\n Delete New Subscriber notification text file [0/1/00] > ')
				if ui == '1':
					mc.deleteMember(client, dAcc['EMAIL'])
					os.remove(emailfilename)
					break
				elif ui == '00':
					exit('\n Terminating program...')
				elif ui == '0':
					td.warningMsg('\n New Subscriber notification text file not deleted...')
					td.uInput('\n Continue... > ')
					break
				else:
					td.warningMsg('\n Invalid input...try again...')
			break

	# # Add another contact?
	# while 1:
	# 	ui = td.uInput('\n Add another Contact [0/1] > ')
	# 	if ui == '0':
	# 		exit('\n Fin')
	# 	elif ui == '1':
	# 		break
	# 	else:
	# 		break
			

	

