

import dicts
import django
from django.template import Template, Context
from django.conf import settings
import emailer
import fun_text_date as td
import lao
import os
from pprint import pprint
from time import sleep


def buildRecipiants(OFFICE, dAgents, today):
	xlsxFile = '{0}_Land_Lot_Report_{1}.xlsx'.format(OFFICE, today)
	xlsxFileExternal = '{0}_EXTERNAL_Land_Lot_Report_{1}.xlsx'.format(OFFICE, today)

	if OFFICE == 'ABQ':
		OFFICE = 'Albuquerque'
	elif OFFICE == 'LasVegas':
		OFFICE = 'Las Vegas'
	elif OFFICE == 'Prescott':
		OFFICE = 'Northern Arizona'
	elif OFFICE == 'Phoenix':
		OFFICE = 'Scottsdale'
	elif OFFICE == 'SaltLakeCity':
		OFFICE = 'Salt Lake City'


	OPRsender = 'Land Advisors {0} Research <research@landadvisors.com>'.format(OFFICE)

	recipients = []

	for agent in dAgents:
		skipRolls = ['Capital', 'DA', 'Escrow', 'Event', 'Intern', 'Intern CON', 'Intern PHX', 'Intern TUC', 'IT', 'Mapping', 'Marketing', 'MC Group']
		
		# Skip non-essential roles, former LAO staff and Bill Landis
		if dAgents[agent]['Roll'] in skipRolls or dAgents[agent]['LAO'] == 'No' or agent == 'Bill Landis':
			continue
		emailAddress = '{0} <{1}@landadvisors.com>'.format(agent, dAgents[agent]['Email'])
		if OFFICE in dAgents[agent]['Markets'] and not emailAddress in recipients:
			recipients.append(emailAddress)
			
	cc_recipients = ['Bill Landis <blandis@landadvisors.com>']

	return recipients, cc_recipients, xlsxFile, xlsxFileExternal, OPRsender

lao.banner('Email LLR Reports v15')
while 1:
	ui = td.uInput('\n Send LLRs to Advisors [0/1/00] > ')
	if ui == '0' or ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		'\n Sending LLRs...'
		break
	else:
		td.warningMsg('\n Invalid input...try again...')

lFileNameOffice = ['Atlanta', 'Austin', 'Boise', 'Charlotte', 'DFW', 'Greenville', 'Houston', 'Jacksonville', 'Kansas City', 'Las Vegas', 'Prescott', 'Orlando', 'Nashville', 'Phoenix', 'Salt Lake City', 'Tampa', 'Tucson']

dAgents = dicts.get_staff_dict(dict_type='full')
today = td.today_date()
htmldict = {'TLT': 'Research Department'}

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': 'F:/Research Department/Code/Research/templates'
	}
]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

for office in lFileNameOffice:
	if office == 'Atlanta' or office == 'Austin':
		continue
	recipients, cc_recipients, xlsxFile, xlsxFileExternal, OPRsender = buildRecipiants(office, dAgents, today)

	subject = 'Weekly Land & Lot Report'
	sender_email = OPRsender
	# recipients = ','.join(recipient)
	# recipient = ['Bill Landis <blandis@landadvisors.com>']

	html = open('F:/Research Department/Code/Research/templates/llr_01.html', 'r').read()

	# assign Template
	t = Template(html)
	c = Context(htmldict)
	html = t.render(c)
	with open('C:/TEMP/LLR_OPR.html', 'w') as h:
		h.write(html)
	body = html

	# # Attach Excel File
	print('\n Attaching Excel file to email...')
	filename = 'F:/Research Department/Lot Comps Components/{0}'.format(xlsxFile)
	filename_x = 'F:/Research Department/Lot Comps Components/{0}'.format(xlsxFileExternal)

	# Check if xlsxFile exists
	if not os.path.exists(filename):
		td.warningMsg('\n Excel file not found: {0}'.format(filename))
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		continue
	
	print(f'\n {office}')
	print(f' Sender: {OPRsender}')
	print(' Recipients:')
	pprint(recipients)
	print(' CC:')
	pprint(cc_recipients)

	lAttachments = [filename]
	# Skip External file for Tampa
	if not office == 'Tampa':
		lAttachments.append(filename_x)

	print('\n Sending LLR to {0}...'.format(office))
	for row in recipients:
		print(' {0}'.format(row))
	emailer.send_email_ses(subject, body, sender_email, recipients=recipients, cc=cc_recipients, bcc=None, attachments=lAttachments)

	print('\n Pausing for 2 seconds...')
	sleep(2)

exit('\n Fin')
