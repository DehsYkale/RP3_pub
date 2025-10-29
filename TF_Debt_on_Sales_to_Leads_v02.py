# Copies Loan data on Sale Deals to Leads - Batch Update Version

import bb
import lao
import dicts
import fun_login
import fun_text_date as td
from pprint import pprint

import webs

lao.banner('TF Debt on Sales to Leads v02 - Batch Update')

service = fun_login.TerraForce()

def clean_update_dict(update_dict):
	"""
	Remove metadata fields that bulk API doesn't accept, None values, and "None" strings
	
	Args:
		update_dict: Dictionary with update fields
	
	Returns:
		Cleaned dictionary with only valid update fields and non-None values
	"""
	# Fields to remove (metadata fields that bulk API rejects)
	fields_to_remove = ['type', 'attributes', 'Type']
	
	# Remove metadata fields, None values, AND "None" strings
	cleaned = {k: v for k, v in update_dict.items() 
			   if k not in fields_to_remove and v is not None and v != "None"}
	return cleaned

def batch_update_deals(service, updates, batch_size=200):
	"""
	Batch update TerraForce deals
	
	Args:
		service: TerraForce service connection
		updates: List of update dictionaries with 'Id' field
		batch_size: Number of records per batch (default 200)
	
	Returns:
		Tuple of (successful_count, failed_records)
	"""
	successful = 0
	failed = []
	total = len(updates)
	
	print(f'\n Batch updating {total} records...')
	
	# Clean all update dictionaries
	cleaned_updates = [clean_update_dict(upd) for upd in updates]
	
	# Process in batches
	for i in range(0, total, batch_size):
		batch = cleaned_updates[i:i + batch_size]
		batch_num = (i // batch_size) + 1
		total_batches = (total + batch_size - 1) // batch_size
		
		print(f' Processing batch {batch_num} of {total_batches} ({len(batch)} records)...')
		
		try:
			# Use bulk API for batch updates
			result = service.bulk.lda_Opportunity__c.update(batch)
			
			# Check results
			for idx, res in enumerate(result):
				if res['success']:
					successful += 1
				else:
					failed.append({
						'record': batch[idx],
						'errors': res['errors']
					})
		except Exception as e:
			print(f' Batch update error: {e}')
			failed.extend([{'record': rec, 'errors': str(e)} for rec in batch])
	
	return successful, failed

lao.banner('TF Debt on Sales to Leads v02 - Batch Update')

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

	record_count = len(results)
	
	if record_count == 0:
		print('\n No records found matching criteria.')
		continue

	if update_type == 'Missing Loan date':
		print(f'\n Found {record_count} Sale Deals with missing Loan Dates')
		print(' Preparing batch update...')
		
		updates = []
		counter = 1
		for row in results:
			dup = dicts.get_blank_deal_update_dict(row['Id'])
			dup['Loan_Date__c'] = row['Sale_Date__c']
			del dup['OwnerId']
			
			updates.append(dup)
			
			# PID = bb.getPIDfromDID(service, row['Id'])
			# print(f' {PID} {counter} - {record_count}')
			print(f' {counter} - {record_count}')
			counter += 1
		
		# Execute batch update
		successful, failed = batch_update_deals(service, updates)
		
		print(f'\n Update Summary:')
		print(f'  Total records: {record_count}')
		print(f'  Successful: {successful}')
		print(f'  Failed: {len(failed)}')
		
		if failed:
			print('\n Failed Updates:')
			for fail in failed:
				print(f"  Record ID: {fail['record']['Id']}")
				print(f"  Errors: {fail['errors']}\n")

	elif update_type == 'Leads missing Debt info from Sales':
		print(f'\n Found {record_count} Leads with missing Debt info')
		print(' Preparing batch update...')
		
		updates = []
		counter, cnt100 = 1, 1
		for row in results:
			dup = dicts.get_blank_deal_update_dict(row['Id'])
			dup['Beneficiary__c'] = row['Parent_Opportunity__r']['Beneficiary__c']
			dup['Beneficiary_Contact__c'] = row['Parent_Opportunity__r']['Beneficiary_Contact__c']
			dup['Encumbrance_Rating__c'] = row['Parent_Opportunity__r']['Encumbrance_Rating__c']
			dup['Credit_Bid_Amount__c'] = row['Parent_Opportunity__r']['Credit_Bid_Amount__c']
			dup['Loan_Amount__c'] = row['Parent_Opportunity__r']['Loan_Amount__c']
			dup['Loan_Date__c'] = row['Parent_Opportunity__r']['Loan_Date__c']
			del dup['OwnerId']
			
			updates.append(dup)

			# PID = bb.getPIDfromDID(service, row['Id'])
			# print(f' {PID} {counter} - {record_count}')
			if cnt100 == 100:
				print(f' {counter} - {record_count}')
				cnt100 = 0
			counter += 1
			cnt100 += 1
		
		# Execute batch update
		successful, failed = batch_update_deals(service, updates)
		
		print(f'\n Update Summary:')
		print(f'  Total records: {record_count}')
		print(f'  Successful: {successful}')
		print(f'  Failed: {len(failed)}')
		
		if failed:
			print('\n Failed Updates:')
			for fail in failed:
				print(f"  Record ID: {fail['record']['Id']}")
				print(f"  Errors: {fail['errors']}\n")