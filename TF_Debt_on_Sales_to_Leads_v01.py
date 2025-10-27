# Copies Loan data on Sale Deals to Leads

import bb
import lao
import dicts
import fun_login
import fun_text_date as td
from pprint import pprint

import webs

lao.banner('TF Debt on Sales to Leads v01')

service = fun_login.TerraForce()

lao.banner('TF Debt on Sales to Leads v01')

while 1:
	print(' Menu')
	print('  1) Update Close PIDs without Loan Date')
	print('  2) Update Leads without Debt with Sales with Debt')
	print('  00) Quit')
	ui = td.uInput('\n Select an option > ')

	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		wc = "StageName__c LIKE '%Closed%' AND Sale_Date__c != null AND Loan_Amount__c != null AND Loan_Date__c = null"
		update_type = 'Missing Loan date'
	# TerraForce Query
	elif ui == '2':
		wc = "StageName__c = 'Lead' AND (Loan_Amount__c = null or Loan_Date__c = null) AND Parent_Opportunity__c != null AND Parent_Opportunity__r.Loan_Amount__c != null"
		update_type = 'Leads missing Debt info from Sales'

	fields = 'default'
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	if update_type == 'Missing Loan date':
		record_count = len(results)
		print (' \n Updating missing Loan Dates on {0} Sale Deals...'.format(record_count))
		counter = 1
		for row in results:
			dup = dicts.get_blank_deal_update_dict(row['Id'])
			dup['Loan_Date__c'] = row['Sale_Date__c']
			del dup['OwnerId']

			PID = bb.getPIDfromDID(service, row['Id'])
			print(f' {PID} {counter} - {record_count}')
			# pprint(dup)

			bb.tf_update_3(service, dup)
			# webs.open_pid_did(service, PID)
			counter += 1

	elif update_type == 'Leads missing Debt info from Sales':
		record_count = len(results)
		print (' \n Updating missing Debt info on {0} Leads from their Sales...'.format(record_count))
		counter = 1
		for row in results:
			dup = dicts.get_blank_deal_update_dict(row['Id'])
			dup['Beneficiary__c'] = row['Parent_Opportunity__r']['Beneficiary__c']
			dup['Beneficiary_Contact__c'] = row['Parent_Opportunity__r']['Beneficiary_Contact__c']
			dup['Encumbrance_Rating__c'] = row['Parent_Opportunity__r']['Encumbrance_Rating__c']
			dup['Credit_Bid_Amount__c'] = row['Parent_Opportunity__r']['Credit_Bid_Amount__c']
			dup['Loan_Amount__c'] = row['Parent_Opportunity__r']['Loan_Amount__c']
			dup['Loan_Date__c'] = row['Parent_Opportunity__r']['Loan_Date__c']
			del dup['OwnerId']

			PID = bb.getPIDfromDID(service, row['Id'])
			print(f' {PID} {counter} - {record_count}')
			# pprint(dup)

			bb.tf_update_3(service, dup)
			# webs.open_pid_did(service, PID)
			counter += 1

