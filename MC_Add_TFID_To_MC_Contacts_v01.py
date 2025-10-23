# Add TFID to MailChimp Contacts

import fun_text_date as td
import lao
import acc
import bb
import fun_login
import mc
from pprint import pprint

client = fun_login.MailChimp()
service = fun_login.TerraForce()


lao.banner('MC Add TFID to MC Contacts v01')

print(' Downloading emails...\n')
dListMembers, listID = mc.get_audience_members(client, listID='None', cnt='get_all', off=0, includeInterests=True)
for mem_id in dListMembers:
	dEml = dListMembers[mem_id]
	pprint(dEml)
	ui = td.uInput('\n Continue... > ')
	if ui == '00':
		exit('\n Terminating program...')
	continue
	exit()
	# mc_email = dEml['email']
	# mc_status = dEml['status']
	# mc_first_name = dEml['firstName']
	# mc_last_name = dEml['lastName']
	# mc_company = dEml['company']
	# mc_tfid = dEml['tfid']

	dAcc = dicts.get_blank_account_dict()
	dAcc['EMAIL'] = dEml['email']
	mc_email = dEml['email']
	mc_click_rate = dEml['clickRate']
	mc_open_rate = dEml['openRate']
	dAcc['MCSTATUS'] = dEml['status']
	dAcc['NF'] = dEml['firstName']
	dAcc['NL'] = dEml['lastName']
	dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	dAcc['ENTITY'] = dEml['company']
	dAcc['AID'] = dEml['tfid']

	# Skip unsubscribed or cleaned
	if dAcc['MCSTATUS'] != 'subscribed':
		continue
	# Skip TFID already populated
	if dAcc['AID'] != '':
		continue
	
	# TerraForce Query
	fields = 'default'
	wc = "PersonEmail = '{0}'".format(dAcc['EMAIL'])
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

	if results != []:
		dAcc['AID'] = results[0]['Id']
		dMC = {"email_address": dAcc['EMAIL']}
		dMC["merge_fields"] = {"TFID": dAcc['AID']}
		print(dAcc['EMAIL'])
		print(dAcc['AID'])
		mc.addUpdateMember(client, listID, dMC, upDateOnly=True, dTags='None')
		# ui = td.uInput('\n Continue... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
	else:
		print('\n dAcc data')
		print(dAcc['EMAIL'])
		print(dAcc['NF'])
		print(dAcc['NL'])
		print(dAcc['ENTITY'])

		name, AID, dAcc = acc.find_create_account_person(service, dAcc)
		dMC = {"email_address": dAcc['EMAIL']}
		dMC["merge_fields"] = {"TFID": dAcc['AID']}
		print(dAcc['EMAIL'])
		print(dAcc['AID'])
		mc.addUpdateMember(client, listID, dMC, upDateOnly=True, dTags='None')
		ui = td.uInput('\n Continue... > ')
		if ui == '00':
			exit('\n Terminating program...')

# name, listID = mc.select_audeince(client)
# results = mc.getMemberInfo(client, listID, email)
# pprint(results)

