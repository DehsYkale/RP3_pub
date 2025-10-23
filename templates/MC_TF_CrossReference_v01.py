#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Cross reference Excel list with TF to create new list with addresses

# Libraries
import fun_text_date as td
import sys
import smtplib
import lao
import bb
import xlwings as xw

service = bb.sfLogin()

dInFile = lao.spreadsheetToDict('C:/TEMP/members_Tampa_Market_Overview_4Q17_sent_Jun_19_2018.xlsx')

outFile = 'C:/TEMP/Tampa_Contacts_Addresses.xlsx'
wb = xw.Book()
sht = wb.sheets.active
sht.range('A1').value = ['Company', 'Name', 'Street', 'City', 'State', 'Zipcode', 'Email', 'Campaign', 'Agent']
count = 2
for row in dInFile:
	fields = 'Id, Name, Company__r.Name, BillingStreet, BillingCity, BillingState, BillingPostalCode'
	wc = "PersonEmail = '{0}'".format(dInFile[row]['Email Address'])
	qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
	results = bb.sfquery(service, qs)
	personname = '{0} {1}'.format(dInFile[row]['First Name'], dInFile[row]['Last Name'])
	lRow = []
	if results == []:
		lRow.append(dInFile[row]['Campaign'])
		lRow.append(personname)
		lRow.append('')
		lRow.append('')
		lRow.append('')
		lRow.append('')
		lRow.append(dInFile[row]['Email Address'])
		lRow.append(dInFile[row]['Campaign'])
		lRow.append(dInFile[row]['Agent'])
	else:
		if dInFile[row]['Company'] != '':
			lRow.append(dInFile[row]['Company'])
		elif results[0]['Company__r'] != '':
			lRow.append(results[0]['Company__r']['Name'])
		else:
			lRow.append('')
		lRow.append(results[0]['Name'])
		lRow.append(results[0]['BillingStreet'])
		lRow.append(results[0]['BillingCity'])
		lRow.append(results[0]['BillingState'])
		lRow.append(results[0]['BillingPostalCode'])
		lRow.append(dInFile[row]['Email Address'])
		lRow.append(dInFile[row]['Campaign'])
		lRow.append(dInFile[row]['Agent'])
	xCell = 'A{0}'.format(count)
	sht.range(xCell).value = lRow
	count += 1
	# td.uInput(results)