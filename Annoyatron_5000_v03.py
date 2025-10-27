# Annoyatron 5000 batch sends emails to LAO offices for MIMO updates

import lao
from pprint import pprint
import dicts
import django
from django.template import Template, Context
from django.conf import settings
import emailer
import fun_text_date as td
import smtplib
import warnings


# Send test email ###
def testing():
	while 1:
		td.banner('Annoyatron 5000 v03')
		print('  1) Send test emails')
		print('  2) Send to Advisors')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			print(f'\n Sending Test {annoy_sheetname} Emails')
			return True
		elif ui == '2':
			td.uInput('\n Sending to Advisors\n\n Continue... > ')
			return False
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')

# Select email notification type to send (MI, MO, MM Posters, MM Mail List, MM Letter)
def select_notification():
	annoy_sheetname = 'None'
	while annoy_sheetname == 'None':
		td.banner('Annoyatron 5000 v03')
		print('  1) MI - Market Insights')
		print('  2) MO - Market Overview')
		print('  3) MM - Cover Letter')
		print('  4) MM - Mail List')
		print('  5) MM - Posters')
		print('  6) MM - Notification')
		print(' 00] Quit')

		ui = td.uInput('\n Select Nofication to send out > ')
		if ui == '1':
			print('\n MI - Approval')
			annoy_sheetname = 'Market Insights'
			msg_sheetname = 'Market Insights Msg'
		elif ui == '2':
			print('\n MO - Market Overview')
			annoy_sheetname = 'Market Overview'
			msg_sheetname = 'Market Overview Msg'
		elif ui == '3':
			print('\n MM - Cover Letter')
			annoy_sheetname = 'Cover Letter'
			msg_sheetname = 'Cover Letter Msg'
		elif ui == '4':
			print('\n MM - Mail List')
			annoy_sheetname = 'Mail List'
			msg_sheetname = 'Mail List Msg'
		elif ui == '5':
			print('\n MM - Posters')
			annoy_sheetname = 'Posters'
			msg_sheetname = 'Poster Msg'
		elif ui == '6':
			print('\n MM - Notification')
			annoy_sheetname = 'Notification'
			msg_sheetname = 'Notification Msg'
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)

	dAnnoys = lao.spreadsheetToDict(fin, annoy_sheetname)

	sender = 'LAO Research <research@landadvisors.com>' # sender
	# Build Msgs dict
	dTemp = lao.spreadsheetToDict(fin, msg_sheetname)
	dMsgs = {}
	for tmp in dTemp:
		dMsgs[dTemp[tmp]['STATUS']] = {
			'SUBJECT': dTemp[tmp]['SUBJECT'],
			'MESSAGE': dTemp[tmp]['MESSAGE']}

	return dAnnoys, dMsgs, annoy_sheetname, sender

# Build List of email recipients
def get_recipients(is_a_test):
	# # TEST TO BILL ONLY
	if is_a_test:
		recipient = ['Bill Landis <blandis@landadvisors.com>']
	else:
		if d['OFFICE'] == 'PHX' and annoy_sheetname == 'Posters':
			recipient = ['Greg Vogel <gvogel@landadvisors.com>', 'Bret Rinehart <brinehart@landadvisors.com>', 'Max Xander <mxander@landadvisors.com>', 'Michael Schwab Jr. <mjrschwab@landadvisors.com>', 'Trey Davis <tdavis@landadvisors.com>']
		elif d['OFFICE'] == 'CAM':
			recipient = ['Wesley Campbell <wcampbell@landadvisors.com>']
		elif d['OFFICE'] == 'JAX':
			recipient = ['Mike Ripley <mripley@landadvisors.com>', 'David Moore <dmoore@landadvisors.com>', 'Ashley Popowski <apopowski@landadvisors.com>']
		elif d['OFFICE'] == 'HEG':
			recipient = ['Ben Heglie <bheglie@landadvisors.com>']
		elif d['OFFICE'] == 'HNT':
			recipient = ['Wilson Higgins <whiggins@landadvisors.com>', 'Eric Deems <edeems@landadvisors.com>', 'George Schubert <gschubert@landadvisors.com', 'Kim Chinn <kchinn@landadvisors.com>']
		elif d['OFFICE'] == 'MCC':
			recipient = ['Kirk McCarville <mmccarville@landadvisors.com>', 'Trey Davis <tdavis@landadvisors.com>']
		elif d['OFFICE'] == 'MED':
			recipient = ['Michele Pino <mpino@landadvisors.com>', 'Michael Brinkley <mbrinkley@landadvisors.com>', 'Laurie Sandau <lsandau@landadvisors.com>']
		elif d['OFFICE'] == 'NAZ':
			recipient = ['Capri Barney <cbarney@landadvisors.com>']
		elif d['OFFICE'] == 'SCH':
			recipient = ['Mike Schwab <mschwab@landadvisors.com>', 'Michael Schwab Jr <mjrschwab@landadvisors.com>']
		elif d['OFFICE'] == 'SRQ':
			recipient = ['Nancy Surak <nsurak@landadvisors.com>']
		elif d['OFFICE'] == 'VOG':
			recipient = ['Greg Vogel <gvogel@landadvisors.com>', 'Jennifer Bittner <jbittner@landadvisors.com>', 'Danielle Kirchner <dkirchner@landadvisors.com>']
		elif d['OFFICE'] == 'WUE':
			recipient = ['Bobby Wuertz <bwuertz@landadvisors.com>', 'Logan Kane <lkane@landadvisors.com>']
		elif d['OFFICE'] == 'XAN':
			recipient = ['Max Xander <mxander@landadvisors.com>']
		else:
			recipient = []
			for agent in dStaff:
				# skipRolls = ['DA', 'Escrow', 'IT', 'Marketing', 'Capital', 'Mapping', 'Research', 'Intern', 'Conservation']
				# if dStaff[agent]['Roll'] in skipRolls or dStaff[agent]['LAO'] == 'No':
				# 	continue
				# Skip former employees
				if dStaff[agent]['LAO'] == 'No':
					continue
				# Send to Agents and EAs in the market
				if dStaff[agent]['Roll'] == 'Agent' or dStaff[agent]['Roll'] == 'EA':
					emailAddress = '{0} <{1}@landadvisors.com>'.format(agent, dStaff[agent]['Email'])
					if d['OFFICE'] in dStaff[agent]['marketAbb'] and not emailAddress in recipient:
						recipient.append(emailAddress)

		# Add Brian and/or Greg
		if add_Brian:
			recipient.append('Brian Rosener <brosener@landadvisors.com>')
		if add_Greg:
			recipient.append('Greg Vogel <gvogel@landadvisors.com>')

		# Add Bill
		recipient.append('Bill Landis <blandis@landadvisors.com>')
		recipient.append('Michael Klingen <mklingen@landadvisors.com>')

	
	return recipient

# Build the email
def build_email():
	# create body of the message as plain text and html
	annoyatron_template = open(r'F:\Research Department\Code\RP3\templates\annoyatron_5000_01.html', 'r').read()
	text = ''
	html = annoyatron_template

	# assign Template
	htmldict = make_html_dict()
	t = Template(html)
	c = Context(htmldict)
	html = t.render(c)
	with open('C:/TEMP/annoyatron.html', 'w', newline='') as h:
		h.write(html)

	subject = dMsgs[d['STATUS']]['SUBJECT']
	body = html
	sender_email = sender

	attach_file = False
	if annoy_sheetname == 'Market Insights':
		# # Attach Excel File
		print('\n Attaching Market Insights PDF to email...')
		filename = 'F:/Research Department/MIMO/Market Insights/{0}/PDFs/{0}_{1}.pdf'.format(yrqtr, d['OFFICE'])
		attach_file = True
	elif annoy_sheetname == 'Market Overview':
		# # Attach Excel File
		print('\n Attaching Market Overview PDF to email...')
		# filename = 'F:/Research Department/MIMO/PowerPoints/{0}/LAO_{1}_Market_Overview_{0}_v1.pdf'.format(yrqtr, d['OFFICE'])
		filename = 'F:/Research Department/MIMO/PowerPoints/{0}/LAO_{1}_Market_Overview_{0}.pdf'.format(yrqtr, d['OFFICE'])
		attach_file = True
	elif annoy_sheetname == 'Cover Letter':
		# # Attach Excel File
		print('\n Attaching Cover Letter Word doc to email...')
		filename = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Letters/2025/{0} 2025 Market Mailer Letter.docx'.format(d['OFFICE'])
		attach_file = True

	# Attach PDF
	attachments = None
	if attach_file:
		attachments = [filename]

	return subject, body, sender_email, attachments, htmldict

# Make html dict
def make_html_dict():

	htmldict = {
		'TYPE': d['TYPE'],
		'STATUS': d['STATUS'],
		'SALUTATION': d['SALUTATION'],
		'MESSAGE': dMsgs[d['STATUS']]['MESSAGE'],
		'OFFICE': d['OFFICE']}

	# Add TYPE specific fields to dict
	if d['TYPE'] == 'Posters':
		htmldict['PDFLINK'] = d['PDFLINK']
		htmldict['REVISIONLINK'] = d['REVISIONLINK']
		htmldict['RQLINK'] = d['RQLINK']
	elif d['TYPE'] == 'Mail List':
		htmldict['LISTLINK'] = d['LISTLINK']
		htmldict['NOMAILERLINK'] = d['NOMAILERLINK']
		# htmldict['NUMCONTACTS'] = int(d['NUMCONTACTS'])

	return htmldict

# Print info
def print_info():
	td.banner('Annoyatron 5000 v03')
	print(' SENT MARKETS: {0}'.format(','.join(lSentMarkets)))
	print('\n EMAIL TYPE: {0}'.format(htmldict['TYPE']))
	td.warningMsg('\n OFFICE:     {0}'.format(htmldict['OFFICE']))
	print(' STATUS:     {0}'.format(htmldict['STATUS']))
	print('\n Recipients')
	for rec in recipients:
		print('   {0}'.format(rec))
	print('\n SUBJECT: {0}'.format(dMsgs[d['STATUS']]['SUBJECT']))
	print('\n MESSAGE: {0}'.format(htmldict['MESSAGE']))

# Ask user if they want to pause after each send to office
def pause_after_each_send():
	while 1:
		ui = td.uInput('\n Pause after each send [0/1/00] > ')
		if ui == '0':
			return False
		elif ui == '1':
			return True
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')

# Add Brian and/or Greg to recipients
def add_Brian_Greg_to_recipients():
	print('\n Add Brian and/or Greg to recipients')
	print('\n  0) Do not add Brian or Greg')
	print('  1) Add Brian')
	print('  2) Add Greg')
	print('  3) Add Brian & Greg')
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '0':
		add_Brian = False
		add_Greg = False
	elif ui == '1':
		add_Brian = True
		add_Greg = False
	elif ui == '2':
		add_Brian = False
		add_Greg = True
	elif ui == '3':
		add_Brian = True
		add_Greg = True
	elif ui == '00':
		exit('\n Terminating program...')

	return add_Brian, add_Greg

# Send email
def send_email(sender, recipient, msg):
	print('\n Sending email...')
	s = smtplib.SMTP('mx1.webville.net')
	s.sendmail(sender, recipient, msg.as_string())
	s.quit()
	print('\n Email sent...')
	return True

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Set up Django templates
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': 'F:/Research Department/Code/RP3/templates'
	}]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

# Variables & Dicts
yrqtr = lao.getDateQuarter(lastquarter=True, two_qrts_ago=False)
# dStaff = lao.getAgentDict(dict_type='full', version='v2')
dStaff = dicts.get_staff_dict_2()
# fin = 'F:/Research Department/MIMO/Advisor Annoyatron Database.xlsx'
fin = 'F:/Research Department/Code/Databases/Annoyatron_Db_v01.xlsx'
dAnnoys, dMsgs, annoy_sheetname, sender = select_notification()
is_a_test = testing()
if is_a_test:
	pauseit, add_Brian, add_Greg = True, False, False
else:
	pauseit = pause_after_each_send()
	add_Brian, add_Greg = add_Brian_Greg_to_recipients()


lSentMarkets = []
for annoy in dAnnoys:
	d = dAnnoys[annoy]
	# pprint(d)

	# Reached end of Annoyatron spreadsheet so exit()
	if d['ACTION'] == None:
		break

	d['TYPE'] = annoy_sheetname
	td.banner('Annoyatron 5000 v03')

	# Skip Do not Send
	lDo_not_send = ['Eblast Sent', 'Approved Send to Printer']

	if d['ACTION'].upper() == 'DO NOT SEND' or d['STATUS'] in lDo_not_send:
		lSentMarkets.append(d['OFFICE'])
		continue

	print('\n STATUS: {0}'.format(d['STATUS'] ))
	recipients = get_recipients(is_a_test)
	# sender, msg, htmldict = build_email()
	subject, body, sender_email, attachments, htmldict = build_email()

	if pauseit:
		while 1:
			print_info()
			ui = td.uInput('\n Send {0} [0/1/00] > '.format(d['OFFICE']))
			if ui == '1':
				emailer.send_email_ses(subject, body, sender_email, recipients, cc=None, bcc=None, attachments=attachments)
				break
			elif ui == '0':
				print(' {0} not sent...'.format(d['OFFICE']))
				break
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				td.warningMsg('\n Invalid input...try again...')
				lao.sleep(2)
	else:
		print_info()
		emailer.send_email_ses(subject, body, sender_email, recipients, cc=None, bcc=None, attachments=attachments)
		lao.sleep(1)
	# Append market to sent list
	lSentMarkets.append(d['OFFICE'])

	if pauseit:
		lao.holdup()

exit('\n Fin')

