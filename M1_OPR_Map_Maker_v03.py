# Make OPR Maps based on PID

import aws
import bb
import csv
import fun_login
import fjson
import json
import fun_text_date as td
import lao
import mpy
from pprint import pprint
import subprocess
import webs

# Update OPR Maps based on date range
def batch_map_update():
	# Get date range
	date_start = td.uInput('\n Enter start date > ')
	date_end = td.uInput('\n Enter end date or [Enter] for today > ')
	date_start = td.date_engine(date_start)
	if date_end == '':
		date_end = td.today_date()
	else:
		date_end = td.date_engine(date_end)
	print(f'\n Start date: {date_start}\n End date: {date_end}')

	print('\n Create OPR Maps for:\n')
	print('  1) Closed Deals')
	print('  2) Leads')
	print(' 00) Quit')
	stage = td.uInput('\n Select > ').upper()

	if stage == '00':
		exit('\n Terminating program...')
	elif stage == '1':
		print('\n Querying TerraForce for Closed Deals...')
		# TerraForce Query
		fields = 'default'
		wc = f"StageName__c LIKE 'Closed%' and (NOT PID__c LIKE 'none%') and Sale_Date__c > {date_start} and Sale_Date__c <= {date_end}"
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	elif stage == '2':
	# TerraForce Query
		print('\n Querying TerraForce for Leads...')
		fields = 'default'
		wc = f"Market__c != '' and CreatedDate >= {date_start}T00:00:00Z and CreatedDate <= {date_end}T00:00:00Z and (NOT PID__c LIKE '%MarketingGroup%') and (NOT PID__c LIKE 'none%') and RecordTypeId <> '01213000001CFArAAO' and (StageName__c = 'Lead' or StageName__c = 'Top100' or StageName__c LIKE '%Lisingg%')"
		# print(f'\n Where Clause: {wc}\n')
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	number_of_deals = len(results)
	
	# Get existing OPR Maps
	print('\n Loading existing OPR Maps in AWS bucket...')
	existing_maps = subprocess.run(f'aws s3 ls s3://request-server/maps/ --output text', stdout = subprocess.PIPE, text=True)
	# pprint(existing_maps.stdout)
	# exit()

	# Cycle throug results to create PID list
	counter = 1
	for result in results:
		PID = result['PID__c']
		print(PID)
		# Check the AWS folder
		# if aws.aws_file_exists(PID, extention='jpg', verbose=True):
		# 	continue
		if PID in existing_maps.stdout:
			print(PID)
			counter += 1
			# print(f'\n OPR Map for {PID} already exists in AWS bucket. Skipping...')
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
			continue
		# Make OPR Map
		print(f'\n {counter} of {number_of_deals} - {PID}...')
		opr_map_created = mpy.make_opr_map_api(service, PID, pause_it=False)
		if opr_map_created:
			print('\n')
		counter += 1
	exit()

td.banner('M1 OPR Map Maker v03')

service = fun_login.TerraForce()

lPIDs = []
while 1:
	td.banner('M1 OPR Map Maker v03')

	# Display PIDs entered
	if lPIDs != []:
		pids_entered = ', '.join(lPIDs)
		print(f'\n PIDs entered: {pids_entered}')
	# User to enter PIDs
	print('\n CREATE OPRs')
	print('\n Enter 1 or more PIDs to make OPR Map(s).\n')
	print('  1) Make the OPR Map(s)')
	print('  2) Batch Update by PID Date Range')	
	print('\n UTILITIES\n')
	print('  3) Open OPR Map in Browser')
	print('  4) Check for existing OPR Map in AWS')
	print('  5) Check AWS Bucket Usage')
	print('\n DELETE MAPS\n')
	print('  6) Delete OPR Map from AWS')
	print('  7) Bulk Delete PNG OPR Maps')
	print('\n 00) to quit')
	PID = td.uInput('\n Enter PID > ')
	if PID == '00':
		exit('\n Terminating program...')
	# Create OPR Maps
	if PID == '1':
		for PID in lPIDs:
			opr_map_created = mpy.make_opr_map_api(service, PID)
			if opr_map_created:
				lao.sleep(1)
		lPIDs = []
	# Batch Update by PID Date Range
	elif PID == '2':
		batch_map_update()
	# Open OPR Map in Browser
	elif PID == '3':
		if lPIDs != []:
			for PID in lPIDs:
				webs.open_opr_map_in_browser(PID=PID)
			lPIDs = []
		else:
			PID = td.uInput('\n Enter PID to open OPR Map > ')
			webs.open_opr_map_in_browser(PID=PID)
	# Check for existing OPR Map in AWS
	elif PID == '4':
		if lPIDs != []:
			for PID in lPIDs:
				result = aws.aws_file_exists(PID, extention='jpg', verbose=False)
				print(f' PID: {PID} - OPR Map exists in AWS: {result}')
			lPIDs = []
		else:
			PID = td.uInput('\n Enter PID to check for OPR Map > ')
			result = aws.aws_file_exists(PID, extention='jpg', verbose=False)
			print(f' PID: {PID} - OPR Map exists in AWS: {result}')
		lPIDs = []
	elif PID == '5':
		batch_map_update()
		lPIDs = []
	# Delete OPR Maps from AWS
	elif PID == '6':
		looping = True
		while looping:
			PID = td.uInput('\n Enter PID to delete OPR Map > ')
			if PID == '':
				td.warningMsg('PID cannot be blank')
				lao.sleep(2)
				continue
			print(f'\n Confirm Deletion of OPR Map for {PID}\n')
			print('  1) Yes')
			print('  2) No')
			print(' 00) Quit')
			ui = td.uInput('\n Select > ')
			if ui == '1':
				aws.opr_map_aws_delete(PID)
				looping = False
			elif ui == '2':
				print('\n Deletion cancelled...')
				lao.sleep(1)
				looping = False
			elif ui == '00':
				exit('\n Terminating program...')
			else:
				td.warningMsg('\n Invalid selection...try again...')
				lao.sleep(1)
		if ui == '00':
			exit('\n Terminating program...')
	# Bulk Delete PNG OPR Maps
	elif PID == '7':
		prefix_delete = td.uInput('\n Enter PNG file name prefix (e.g. AZMar) > ')
		if prefix_delete == '':
			td.warningMsg('PID cannot be blank')
			lao.sleep(2)
			continue
		print(f'\n Confirm Deletion of OPR Maps starting with {prefix_delete}\n')
		print('  1) Yes')
		print('  2) No')
		print(' 00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			aws.opr_map_aws_delete(PID=None, file_type='PNG', prefix_delete=prefix_delete)
			break
		elif ui == '2':
			print('\n Deletion cancelled...')
			lao.sleep(1)
			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid selection...try again...')
			lao.sleep(1)
	# Add PID to list
	else:
		lPIDs.append(PID)
		

