# #!/usr/bin/env python
# -*- coding: utf-8 -*-


import acc
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
import lao
from pprint import pprint

service = fun_login.TerraForce()

dDomains = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/Domains Email Format v03.xlsx')
dALL_TF_Contacts = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/TF_All_Contacts_v01.csv')

lao.banner('Email Populator from Domains v03')
count = 0
for contact in dALL_TF_Contacts:
	
	dCon = dALL_TF_Contacts[contact]

	if dCon['EID'] == 'None':
		continue
	if dCon['Email'] != 'None':
		continue

	for domain in dDomains:
		
		dDom = dDomains[domain]
		# print('here1')
		# pprint(dDom)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
		if dDom['ENTITY TFID'] == 'None' or dDom['ENTITY TFID'] == '' or dDom['ENTITY TFID'] == None:
			continue
		if dCon['EID'][-3] == dDom['ENTITY TFID'][:-3]:
			
			print('\n  Name: {0}'.format(dCon['PersonName']))
			print(' Email: {0}'.format(dCon['Email']))
			print(' Email: {0}'.format(dCon['EntityName']))
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			break
	count += 1
	print(' Count: {0}'.format(count))
	




exit()
for row in dDomains:
	EID = dDomains[row]['Company ID']

	qs = "SELECT Id, Name, FirstName, MiddleName__c, LastName, BillingStreet, BillingCity, BillingState, Phone, PersonEmail FROM Account WHERE Company__c = '{0}' AND IsPersonAccount = TRUE".format(EID)
	dEmp = bb.sfquery(service, qs)

	dEMP = acc.findPersonsOfEntity(service, EID = EID, person = 'None', returnDict = True)
	pprint(dEMP)


	ui = td.uInput(' Continue [0/1] > ')
	if ui == '0':
		exit()

