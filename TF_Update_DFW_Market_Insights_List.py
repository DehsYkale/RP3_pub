



import os
import json
import requests
from pprint import pprint
import lao
import bb
import fun_login
from exchangelib import Credentials, Account, DELEGATE
import mc 

service = fun_login.TerraForce()
client = fun_login.MailChimp()
audience_id = '444f159575'
lAdvisors = dicts.get_staff_dict('namesonly')
lDFW_advisors = ['Austin Reilly', 'Landry Burdine', 'Josh Watson']
fin = 'F:/Research Department/Projects/Advisors and Markets/DFW/DFW Eblast List Update 2023-09-11.xlsx'
dEmails = lao.spreadsheetToDict(fin, sheetname='Add to MI List')
for row in dEmails:
	# pprint(dEmails[row])
	email = dEmails[row]['Email']
	print(email)
	# TerraForce Query
	fields = 'default'
	# wc = "PersonEmail = '{0}' and Category__c INCLUDES ('Austin Reilly', 'Landry Burdine', 'Josh Watson')".format(email)
	wc = "PersonEmail = '{0}'".format(email)
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

	# Continue if no record returned
	if results == []:
		print(' No email or DFW Advisor in TF')
		continue
	# pprint(results)

	# Get update dict
	dup = bb.get_update_dict(results=results, id='None', account_type='None')

	# Check if email is bounced in MC, archive if not
	status = mc.getMemberStatus(client, email, listID=audience_id, override=False)
	print(status)
	if status == 'bounced':
		print(' Bounced email')
		dup['PersonEmail'] = None
	elif status == 'unsubscribed':
		print(' Unsubscribed')
		pass
	else:
		print(' Archiving account in MC DFW Audience')
		mc.archive_member(client, email, audience_id=audience_id)

	# Make a list of Category__c
	lCategory = results[0]['Category__c'].split(';')

	# Remove DFW Advisors
	for advisor in lDFW_advisors:
		try:
			lCategory.remove(advisor)
		except ValueError:
			continue

	# Check if other Advisors are in the Category
	is_other_agents = False
	for advisor in lAdvisors:
		# print(advisor)
		if advisor in lCategory:
			is_other_agents = True
			break

	# Update TF
	if is_other_agents:
		category = ';'.join(lCategory)
		dup['Category__c'] = category
		pprint(dup)
		print(' Update account removing DFW Advisors')
		bb.tf_update_3(service, dup)
	else:
		category = 'None'
		print(' Deleting account, no Advisors')
		delete_results = bb.tf_delete_3(service, results[0]['Id'], results[0]['attributes']['type'])

		# Remove DFW Advisors from Categor it delete failed
		if delete_results == 'Delete Failed':
			try:
				lCategory.remove('Market Insights')
			except ValueError:
				pass
			if lCategory == []:
				dup['Category__c'] = None 
			else:
				category = ';'.join(lCategory)
				dup['Category__c'] = category
				print(' Update account removing DFW Advisors')
				bb.tf_update_3(service, dup)
				
	# print(lCategory)
	# print(category)

	


	


exit()
