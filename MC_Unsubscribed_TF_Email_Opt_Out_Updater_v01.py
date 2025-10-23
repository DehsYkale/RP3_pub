# Updates TF Email Opt Out field with Mailchimp Unsubscribes

import bb
import fun_login
import fun_text_date as td
import lao
import mc
from pprint import pprint


def get_skip_lists():
	lSkipLists = ['All LAO Contacts',
	'Land Advisors Contacts',
	'Land Sale Notification',
	'Market Insights Subscribers',
	'Phoenix LAHF Final Send Day of',
	'LAO Staff',
	'Schwab Personal',
	'a list with just Ethan in it',
	'Brent - Multifamily',
	'New Mexico',
	'Events',
	'Resort Solutions',
	'Tony Lang',
	'Zach Hartman for US Congress']

	return lSkipLists

def selectMCList():
	index = 1
	lmenu = []
	lao.banner('MailChimp Admin Report v04 Select List')
	for lst in dMCLists['lists']:
		listname = lst['name']
		if listname in lSkipLists:
			continue
		lmenu.append(listname)
		print(' {0:2}) {1}'.format(index, listname))
		index += 1
	print(' {0:2}) All'.format(index))
	lmenu.append('All')
	ui = int(td.uInput('\n Select List > ')) - 1
	selection = lmenu[ui]
	return selection


service = fun_login.TerraForce()
client = fun_login.MailChimp()
lSkipLists = get_skip_lists()
# Dict of MC Lists
dMCLists = mc.getListNameID(client)
# Select list from menu
useThisList = selectMCList()

# # Cycle throught lists
for l in dMCLists['lists']:
	mcListName = l['name']

	if mcListName in lSkipLists:
		# print('\n Skipped: {0}'.format(mcListName))
		continue
	if useThisList == 'All':
		td.warningMsg('\n Cannot use All')
		exit('\n Terminating program...')
	if mcListName != useThisList:
		continue
	
	lao.banner('MC Unsubscribe TF Email Opt Out Updater v01')
	print(f' MC Audience: {useThisList}')
	
	# print(mcListName)
	mcListID = l['id']

	print('\n Getting list members...')
	dListMembers = mc.get_audience_members(client, mcListID, 'get_all', 0, True)

	lMembersBouncedUnsub = []

	# Cycle through members
	for member in dListMembers:
		# Set variable values
		fname = dListMembers[member]['firstName']
		lname = dListMembers[member]['lastName']
		company = dListMembers[member]['company']
		email = dListMembers[member]['email']
		status = dListMembers[member]['status']
		unsubReason = dListMembers[member]['unsubscribe_reason']
		unsubReason = unsubReason.replace('N/A (', '').replace(')', '')
		lastChange = dListMembers[member]['last_changed']
		lastChange = lastChange[:10]

		# lBouncedUnsub = []

		# lBouncedUnsub.extend([fname, lname, company, email])
		dBouncedUnsub = {'FirstName': fname,
						'LastName': lname,
						'Company': company,
						'Email': email,
						'Audience': mcListName,
						'Reason': unsubReason}

		if status == 'subscribed':
			continue
		elif 'landadvisors.com' in email:
			continue
		elif status == 'cleaned':
			dBouncedUnsub['Status'] = 'Bounced'
			dBouncedUnsub['LastChange'] = lastChange
			dBouncedUnsub['Reason'] = 'n/a'

		else:
			dBouncedUnsub['Status'] = 'Unsubscribed'
			dBouncedUnsub['LastChange'] = lastChange
			dBouncedUnsub['Reason'] = unsubReason
		lMembersBouncedUnsub.append(dBouncedUnsub)

# pprint(lMembersBouncedUnsub)

for member in lMembersBouncedUnsub:
	pprint(member)
	print(' ')
	# TerraForce Query
	fields = 'default'
	wc = "PersonEmail = '{0}'".format(member['Email'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	if results != []:
		for row in results:
			AID = row['Id']
			# Skip if Email Opt out is alread true
			if 'Email Status:' in row['Description']:
				break
			if 'Bad Email:' in row['Description']:
				break

			# Write Email Status to Description
			if row['Description'] == 'None':
				description = 'Email Status: {0} from MailChimp Audience {1}'.format(member['Status'], member['Audience'])
			else:
				description = '{0}\nEmail Status: {1} from MailChimp Audience {2}'.format(row['Description'], member['Status'], member['Audience'])
			
			# Add bad email if bounced or reason if unsubscribed
			if member['Status'] == 'Bounced':
				description = '{0}\nBad Email: {1}'.format(description, member['Email'])
			elif member['Status'] == 'Unsubscribed':
				description = '{0}\nEmail: {1}\nReason Unsubscribed: {2}'.format(description, member['Email'], member['Reason'])
		
			dup = {'type': 'Account',
					'Id': AID,
					'Description': description,
					'PersonHasOptedOutOfEmail': True}
			
			bb.tf_update_3(service, dup)



