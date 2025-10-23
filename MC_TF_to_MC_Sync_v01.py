# #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Syncs TF contacts with MC based on the agent
"""

import acc
import bb
import fun_login
import fun_text_date as td
import lao
import mc
from pprint import pprint

def verifyEmailFormat(email):
	"""
	Function that verifies that the string passed is a valid email address.
	Regex for email validation based on MailChimp limits:
	http://kb.mailchimp.com/accounts/management/international-characters-in-mailchimp
	:param email: The potential email address
	:type email: :py:class:`str`
	:return: Nothing
	"""
	import re
	if not re.match(r".+@.+\..+", email):
		raise ValueError('String passed is not a valid email address')
	return

def getEmailHash(email):
	"""
	The MD5 hash of the lowercase version of the list member's email.
	Used as subscriber_hash
	:param email: The member's email address
	:type member_email: :py:class:`str`
	:returns: The MD5 hash in hex
	:rtype: :py:class:`str`
	"""
	import hashlib
	verifyEmailFormat(email)
	email = email.lower().encode()
	m = hashlib.md5(email)
	return m.hexdigest()

# # Build dAcc, dMC and dTags for MC import
def buildDicts(dTFContactData):
	dAcc = acc.populatedAccFromTF(service, dAcc='None', dTFData=dTFContactData)
	dAcc['MCAUDID'] = listID
	dMC, dTags = mc.buildMCDicts(dAcc)
	return dAcc, dMC, dTags

# Determine MC Contacts to unsubscribe b/c they are not on the Tampa List
def unsubscribeFromMC(listID, dAudienceMembers, dTFContacts):
	lao.banner('MC TF to MC Sync v01')
	# Only unsubscribe Tampa contacts
	if listID == '7d74485d38':
		# lao.warningMsg('\n This is not Tampa. Are you sure you want to proceed with unsubscribing?')
		# print('\n 0) Do not unsubscribe')
		# print('\n 0) Unsubscribe')
		# ui = td.uInput('\n [0/1] > ')
		# if ui != '1':
		# 	return
		ui = td.uInput(' Unsubscribe MC Members if not in TF dict?\n\n [0/1] > ')
		if ui == '1':
			print '\n Unsubscribing...'
			for mcID in dAudienceMembers:
				mcEmail = dAudienceMembers[mcID]['email'].lower()
				mcStatus = dAudienceMembers[mcID]['status']

				# Skip unsubscribed Members
				if mcStatus == 'unsubscribed':
					continue
				# Skip LAO Members
				if 'landadvisors.com' in mcEmail:
					continue

				notInTF = True
				for dTFContactData in dTFContacts:
					tfEmail = dTFContactData['PersonEmail'].lower()
					if tfEmail == mcEmail:
						# print mcEmail
						notInTF = False
						break
				if notInTF:
					print '\n Unsubscribing: {0}'.format(mcEmail)
					# Build MailChimp unsubscribe dict
					dMC = {
						"status": 'unsubscribed',
						"email_address": mcEmail
						}
					mc.addUpdateMember(client, listID=listID, dMC=dMC, upDateOnly=True, dTags='None')
			td.uInput('\n Unsubscribes done...continue > ')

def getAgentsOfMaichimpList():
	lao.banner('MC TF to MC Sync v01')
	listname, listID = mc.selectList(client)
	dAgents = lao.getAgentDict()
	lAgentNames = []
	for agent in dAgents:
		if listID in dAgents[agent]['MC Aud ID'] and dAgents[agent]['Roll'] == 'Agent' and dAgents[agent]['LAO'] == 'Yes':
			lAgentNames.append(agent)
	# Make TF Include query string
	strInclude = ""
	for row in lAgentNames:
		if len(lAgentNames) == 1:
			strInclude = "{0}".format(row)
		elif strInclude == "":
			strInclude = "{0}".format(row)
		else:
			strInclude = "{0}', '{1}".format(strInclude, row)
	return listID, strInclude


client = fun_login.MailChimp()
service = fun_login.TerraForce()

listID, strInclude = getAgentsOfMaichimpList()

# dAgents = lao.getAgentDict()
# agentName = "'Nancy Surak', 'Mike Schwab'"
# Get the Audience ID from dAgents
# listID = dAgents[agentName]['MC Aud ID']
# Get MC Members from Agent's Audience
dAudienceMembers = mc.getListMembers(client, listID, cnt='get_all')
# Get TF Contacts with Agent in Category or MVP (Top100)
dTFContacts = bb.getAgentContactsDict(service, strInclude, withEmail=True)

# Determine MC Contacts to unsubscribe b/c they are not on the Tampa List
unsubscribeFromMC(listID, dAudienceMembers, dTFContacts)

lao.banner('MC TF to MC Sync v01')

# Cycle through TF Contacts and see if they are in MC
tfcount = 0
for dTFContactData in dTFContacts:
	tfcount += 1
	# Build dAcc, dMC and dTags
	dAcc, dMC, dTags = buildDicts(dTFContactData)
	
	tfEmail = dTFContactData['PersonEmail']
	inMC = False
	for mcID in dAudienceMembers:
		mcEmail = dAudienceMembers[mcID]['email']
		mcStatus = dAudienceMembers[mcID]['status']

		# dMem = mc.getMemberInfo(client, listID, mcEmail)
		# pprint(dMem)


		if tfEmail == mcEmail:
			if mcStatus == 'unsubscribed' or mcStatus == 'cleaned':
				inMC = 'Skip'
			else:
				inMC = True
			break

	# Skip if in MC as unsubscribed
	if inMC == 'Skip':
		continue
	# Update Member in MC with TF Contact data
	elif inMC:
		print ' Matched: {0}'.format(mcEmail)
		upDateOnly = True
	# Add new Member to MC
	if inMC is False:
		print ' New    : {0}'.format(mcEmail)
		upDateOnly = False
	print '{0} of {1}'.format(tfcount, len(dTFContacts))
	mc.addUpdateMember(client, listID=listID, dMC=dMC, upDateOnly=upDateOnly, dTags=dTags)

exit('\n Fin')





