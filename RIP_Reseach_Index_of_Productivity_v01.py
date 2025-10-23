# RIP Research Index of Productivity
# Caclulated the RIP for the Research Department staff

import bb
import csv
import dicts
import lao
import fun_login
import fun_text_date as td
from pprint import pprint
import webs

def make_dicts_and_lists(hours_in_period):
	dStaff_TF_Ids = dicts.get_staff_dict(dict_type='userid', skipFormerEmployees=False)
	dResearchers = dicts.get_staff_dict(dict_type='researchers')
	lResearcher_Ids = list(dResearchers.values())
	lResearcher_Ids = "','".join(lResearcher_Ids)
	lResearcher_names = list(dResearchers.keys())
	lResearcher_names = "','".join(lResearcher_names)
	dRIP = {}
	
	for researcher in dResearchers:
		dRIP[researcher] = {
			'Deals Created': 0,
			'Deals Edited': 0,
			'Entity Accounts Created': 0,
			'Entity Accounts Edited': 0,
			'Contact Accounts Created': 0,
			'Contact Accounts Edited': 0,
			'Comps Created': 0,
			'Listings Created': 0,
			'LAO Deals Edited': 0,
			'Requests Completed': 0,
			'OPRs Sent': 0,
			'Hours Worked': 0,
			'Hours in Period': hours_in_period,
			'Weighted Points': 0,
			'RIP Desk': 0,
			'RIP Worked': 0
		}
	
	# List of tasks to be used in the spreadsheet
	lTasks = list(dRIP['Bill Landis'].keys())
	
	# EOS Scrorecard dict
	dEOS = {
		'Requests Fullfilled': 0,
		'Requests Made': 0,
		'RIP Avg Researcher': 0,
		'RIP Team Total': 0,
		'Comps Entered': 0,
		'Listings Entered': 0,
		'Accounts Created': 0
	}
	# PTO
	dPTO = dicts.spreadsheet_to_dict(pto_file)
	return dRIP, lResearcher_Ids, dStaff_TF_Ids, lResearcher_names, lTasks, dPTO, dEOS

def get_deals_created(dRIP):
	print('Getting Deals Created...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"CreatedById IN ('{lResearcher_Ids}') AND CreatedDate >= {start} AND CreatedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	for row in results:
		owner_name = dStaff_TF_Ids[row['OwnerId'][:-3]]
		created_by_name = dStaff_TF_Ids[row['CreatedById'][:-3]]
		dRIP[created_by_name]['Deals Created'] += 1
	return dRIP

def get_deals_edited(dRIP):
	print('Getting Deals Edited...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"LastModifiedById IN ('{lResearcher_Ids}') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	# Deals Edited
	for row in results:
		last_modified_by_name = dStaff_TF_Ids[row['LastModifiedById'][:-3]]
		dRIP[last_modified_by_name]['Deals Edited'] += 1
	
	return dRIP

def get_lao_deals_edited(dRIP):
	print('Getting LAO Deals Edited...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"LastModifiedById IN ('{lResearcher_Ids}') AND StageName__c IN ('Closed', 'Trusted Listing', 'Signed Listing', 'Draft', 'Escrow') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	for row in results:
		last_modified_by_name = dStaff_TF_Ids[row['LastModifiedById'][:-3]]
		dRIP[last_modified_by_name]['LAO Deals Edited'] += 1
	
	return dRIP

def get_entity_accounts_created(dRIP):
	print('Getting Entity Accounts Created...')
	if dRIP is False:
		start = td.date_engine(date_start_1w, 'tf_query', 'six')
		end = td.date_engine(date_end_1w, 'tf_query', 'six')
	else:
		start = td.date_engine(date_start_4w, 'tf_query', 'six')
		end = td.date_engine(date_end_4w, 'tf_query', 'six')
		
	# TerraForce Query
	wc = f"CreatedByID IN ('{lResearcher_Ids}') AND CreatedDate >= {start} AND CreatedDate <= {end} AND IsPersonAccount = False"
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	if dRIP is False:
		return len(results)	
	else:
		for row in results:
			created_by_name = dStaff_TF_Ids[row['CreatedById'][:-3]]
			dRIP[created_by_name]['Entity Accounts Created'] += 1
		
		return dRIP

def get_entity_accounts_edited(dRIP):
	print('Getting Entity Accounts edited...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"LastModifiedById IN ('{lResearcher_Ids}') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end} AND IsPersonAccount = False"
	results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)

	# Deals Edited
	missing_user = []
	for row in results:
		try:
			created_by_name = dStaff_TF_Ids[row['CreatedById'][:-3]]
		except KeyError:
			if row['CreatedById'][:-3] not in missing_user:
				missing_user.append(row['CreatedById'][:-3])
				print(row['CreatedById'][:-3])
				webs.openTFAccId(row['CreatedById'][:-3])
			continue
		last_modified__by_name = dStaff_TF_Ids[row['LastModifiedById'][:-3]]
		if created_by_name != last_modified__by_name:
			dRIP[last_modified__by_name]['Entity Accounts Edited'] += 1
	
	return dRIP

def get_contact_accounts_created(dRIP):
	print('Getting Contact Accounts Created...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"CreatedByID IN ('{lResearcher_Ids}') AND CreatedDate >= {start} AND CreatedDate <= {end} AND IsPersonAccount = True"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	for row in results:
		created_by_name = dStaff_TF_Ids[row['CreatedById'][:-3]]
		dRIP[created_by_name]['Contact Accounts Created'] += 1
	return dRIP

def get_contact_accounts_edited(dRIP):
	print('Getting Contact Accounts Edited...')
	start = td.date_engine(date_start_4w, 'tf_query', 'six')
	end = td.date_engine(date_end_4w, 'tf_query', 'six')

	# TerraForce Query
	wc = f"LastModifiedById IN ('{lResearcher_Ids}') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end} AND IsPersonAccount = True"
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)

	if dRIP is False:
		return len(results)	
	else:
		missing_user = []

		for row in results:
			try:
				created_by_name = dStaff_TF_Ids[row['CreatedById'][:-3]]
			except KeyError:
				if row['CreatedById'][:-3] not in missing_user:
					missing_user.append(row['CreatedById'][:-3])
					td.warningMsg(f'User not found in the LAO_Staff_Db: {row["CreatedById"][:-3]}')
					td.warningMsg(f'Opening TerraForce Account: {row["CreatedById"][:-3]}')
					print(row['CreatedById'][:-3])
					webs.openTFAccId(row['CreatedById'][:-3])
				continue
			last_modified__by_name = dStaff_TF_Ids[row['LastModifiedById'][:-3]]
			if created_by_name != last_modified__by_name:
				dRIP[last_modified__by_name]['Contact Accounts Edited'] += 1
	
	return dRIP

def get_comps_created(dRIP):
	print('Getting Comps Created...')
	if dRIP is False:
		start = td.date_engine(date_start_1w, 'tf_query', 'six')
		end = td.date_engine(date_end_1w, 'tf_query', 'six')
	else:
		start = td.date_engine(date_start_4w, 'tf_query', 'six')
		end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"OwnerId IN ('{lResearcher_Ids}') AND StageName__c IN ('Closed', 'Closed Lost') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	# Comps Created
	if dRIP is False:
		return len(results)
	else:
		for row in results:
			owner_name = dStaff_TF_Ids[row['OwnerId'][:-3]]
			dRIP[owner_name]['Comps Created'] += 1
		
		return dRIP

def get_listings_created(dRIP):
	print('Getting Listings Created...')
	if dRIP is False:
		start = td.date_engine(date_start_1w, 'tf_query', 'six')
		end = td.date_engine(date_end_1w, 'tf_query', 'six')
	else:
		start = td.date_engine(date_start_4w, 'tf_query', 'six')
		end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"OwnerId IN ('{lResearcher_Ids}') AND RecordTypeId = '012a0000001ZSS8AAO' AND LastModifiedDate >= {start} AND LastModifiedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	# Listings Created
	if dRIP is False:
		return len(results)
	else:
		for row in results:
			owner_name = dStaff_TF_Ids[row['OwnerId'][:-3]]
			dRIP[owner_name]['Listings Created'] += 1
		
		return dRIP

def get_oprs_sent(dRIP):
	print('Getting OPRs Sent...')
	start = td.date_engine(date_start_4w, 'TF', 'six')
	end = td.date_engine(date_end_4w, 'TF', 'six')
	# TerraForce Query
	wc = f"OwnerId IN ('{lResearcher_Ids}') AND OPR_Sent__c >= {start} AND OPR_Sent__c <= {end}"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

	for row in results:
		owner_name = dStaff_TF_Ids[row['OwnerId'][:-3]]
		dRIP[owner_name]['OPRs Sent'] += 1
	return dRIP

def get_requests_made():
	print('Getting Requests Made...')
	start = td.date_engine(date_start_1w, 'tf_query', 'six')
	end = td.date_engine(date_end_1w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"CreatedDate >= {start} AND CreatedDate <= {end} AND Record_Type_Name__c = 'Research'"
	results = bb.tf_query_3(service, rec_type='Request', where_clause=wc, limit=None, fields=fields)

	requests_made = len(results)
	
	return requests_made

def get_requests_completed(dRIP):
	print('Getting Requests Completed...')
	if dRIP is False:
		start = td.date_engine(date_start_1w, 'tf_query', 'six')
		end = td.date_engine(date_end_1w, 'tf_query', 'six')
	else:
		start = td.date_engine(date_start_4w, 'tf_query', 'six')
		end = td.date_engine(date_end_4w, 'tf_query', 'six')
	# TerraForce Query
	wc = f"Assigned_Mapper__c IN ('{lResearcher_Ids}') AND LastModifiedDate >= {start} AND LastModifiedDate <= {end}"
	results = bb.tf_query_3(service, rec_type='Request', where_clause=wc, limit=None, fields=fields)

	# Requests Completed
	if dRIP is False:
		return len(results)
	else:
		for row in results:
			
			# Check if Assigned Mapper is in the list of researchers
			assigned_mapper_name = row['Assigned_Mapper__r']['Name']
			assigned_mapper_name = assigned_mapper_name.replace('Micah', 'Mica')
			dRIP[assigned_mapper_name]['Requests Completed'] += 1

		
		return dRIP

def research_pto(dRIP, dPTO):
	start = td.date_engine(date_start_4w, 'datetime.datetime', 'six')
	end = td.date_engine(date_end_4w, 'datetime.datetime', 'six')

	dPTO_in_period = {
		'Alec Videla': 0,
		'Bill Landis': 0,
		'Mike Wifler': 0,
		'Connor Cox': 0,
		'Michael Klingen': 0,
		'Taylor Jacobson': 0
		}
	
	for researcher in dPTO_in_period:
		for row in dPTO:
			r = dPTO[row]
			if researcher == r['Employee']:
				if start <= r['Date'] <= end:
					dPTO_in_period[researcher] = dPTO_in_period[researcher] + r['Hours']
	for researcher in dRIP:
		dRIP[researcher]['Hours Worked'] = dRIP[researcher]['Hours in Period'] - dPTO_in_period[researcher]
	
	return dRIP

def calculate_rip(dRIP):
	print('Calculating RIP...')
	weighted_points = 0
	for researcher in dRIP:
		weighted_points = dRIP[researcher]['Deals Created'] * 4
		weighted_points = weighted_points + (dRIP[researcher]['Deals Edited'] * 3)
		weighted_points = weighted_points + (dRIP[researcher]['Entity Accounts Created'] * 2)
		weighted_points = weighted_points + (dRIP[researcher]['Entity Accounts Edited'] * 2)
		weighted_points = weighted_points + (dRIP[researcher]['Contact Accounts Created'] * 2)
		weighted_points = weighted_points + (dRIP[researcher]['Contact Accounts Edited'] * 2)
		weighted_points = weighted_points + (dRIP[researcher]['Comps Created'] * 5)
		weighted_points = weighted_points + (dRIP[researcher]['Listings Created'] * 5)
		weighted_points = weighted_points + (dRIP[researcher]['LAO Deals Edited'] * 3)
		weighted_points = weighted_points + (dRIP[researcher]['Requests Completed'] * 3)
		weighted_points = weighted_points + (dRIP[researcher]['OPRs Sent'] * 2)
		dRIP[researcher]['Weighted Points'] = weighted_points
		dRIP[researcher]['RIP Desk'] = round(weighted_points / dRIP[researcher]['Hours in Period'], 1)
		dRIP[researcher]['RIP Worked'] = round(weighted_points / dRIP[researcher]['Hours Worked'], 1)
	return dRIP

def make_spreadsheet(dRIP, dEOS):
	print('Making Spreadsheet...')
	filename = r'F:\Research Department\Lessons Learned\Staff Evaluations\RIP Team Weekly Temp.csv'
	while 1:
		try:
			with open(filename, 'w', newline='') as f:
				fout = csv.writer(f)

				# Team Totals
				# header determines the order of the columns in the spreadsheet
				header = ['Task', 'Alec Videla', 'Bill Landis', 'Connor Cox', 'Mike Wifler', 'Michael Klingen', 'Taylor Jacobson', 'Team Avg', 'Team Total']
				fout.writerow(header)

				for task in lTasks:
					total_points = 0
					row = [task]
					# Index for researcher names in header
					for i in range(1, 6):
						row.append(dRIP[header[i]][task])
						total_points = total_points + dRIP[header[i]][task]
					# Team Average: Total points divided by 6 researchers
					row.append(round(float(total_points / 6), 1))
					# Total points
					row.append(total_points)
					
					fout.writerow(row)
					# EOS Scorecard
					if task == 'RIP Worked':
						dEOS['RIP Team Total'] = total_points

				# Team Averages
				# Add blank line between Full team and researcher averages
				fout.writerow([])
				# header determines the order of the columns in the spreadsheet
				header = ['Task',  'Connor Cox', 'Mike Wifler', 'Taylor Jacobson', 'Rschr Avg', 'Rschr Total']
				fout.writerow(header)

				for task in lTasks:
					total_points = 0
					row = [task]
					# Index for researcher names in header
					for i in range(1, 3):
						row.append(dRIP[header[i]][task])
						total_points = total_points + dRIP[header[i]][task]
					# Researcher Average: Total points divided by 4 researchers
					row.append(round(float(total_points / 4), 1))
					# Total points
					row.append(total_points)
					
					fout.writerow(row)
					# EOS Scorecard
					if task == 'RIP Worked':
						dEOS['RIP Avg Researcher'] = round(float(total_points / 4), 1)
			break
		# Capture if file is open
		except PermissionError:
			td.warningMsg('\n File is open...close and press [Enter] or [00]')
			ui = td.uInput('\n  > ')
			if ui == '00':
				exit('\n Terminating program...')
	lao.openFile(filename)
	return dEOS

service = fun_login.TerraForce()

td.banner('RIP Research Index of Productivity v01')

rip_file = r'F:\Research Department\Lessons Learned\Staff Evaluations\RIP_v01.xlsx'
pto_file = r'F:\Research Department\Lessons Learned\Staff Evaluations\Staff_PTO.xlsx'
lao.openFile(rip_file)
lao.openFile(pto_file)
ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')


while 1:
	td.banner('RIP Research Index of Productivity v01')
	
	# User to enter start date and function will return the end date
	strDate = td.uInput('Enter END DATE (MMDDYY) [00]: ')
	if strDate == '00':
		exit('\n Terminating program...')
	date_start_4w, date_end_4w = td.weeks_difference(strDate=strDate, no_weeks=4, is_start=False)
	date_start_1w, date_end_1w = td.weeks_difference(strDate=strDate, no_weeks=1, is_start=False)
	ytd_start, ytd_end = td.weeks_difference(strDate=strDate, no_weeks=52, is_start=False)

	hours_in_period = td.uInput('\n Enter Hours in Period [160] > ')
	hours_in_period = int(hours_in_period)

	dRIP, lResearcher_Ids, dStaff_TF_Ids, lResearcher_names, lTasks, dPTO, dEOS = make_dicts_and_lists(hours_in_period)

	print()
	fields = 'default'
	
	dRIP = get_requests_completed(dRIP)
	dRIP = get_contact_accounts_created(dRIP)
	dRIP = get_contact_accounts_edited(dRIP)
	dRIP = get_entity_accounts_created(dRIP)
	dRIP = get_entity_accounts_edited(dRIP)
	dRIP = get_lao_deals_edited(dRIP)
	dRIP = get_listings_created(dRIP)
	dRIP = get_comps_created(dRIP)
	dRIP = get_deals_edited(dRIP)
	dRIP = get_deals_created(dRIP)
	dRIP = get_oprs_sent(dRIP)
	dRIP = research_pto(dRIP, dPTO)
	dRIP = calculate_rip(dRIP)

	# pprint(dRIP)

	dEOS = make_spreadsheet(dRIP, dEOS)

	# Make EOS Scorecard
	dEOS['Entities Created'] = get_entity_accounts_created(dRIP=False)
	dEOS['Persons Created'] = get_entity_accounts_created(dRIP=False)
	dEOS['Accounts Created'] = dEOS['Entities Created'] + dEOS['Persons Created']
	dEOS['Comps Entered'] = get_comps_created(dRIP=False)
	dEOS['Listings Entered'] = get_listings_created(dRIP=False)
	dEOS['Requests Fullfilled'] = get_requests_completed(dRIP=False)
	dEOS['Requests Made'] = get_requests_made()
	dEOS['Requests Over Under'] = dEOS['Requests Made'] - dEOS['Requests Fullfilled']

	td.banner('RIP Research Index of Productivity v01')
	# pprint(dEOS)
	print(f'Date Range: {date_start_4w, date_end_4w}')
	print(f'RIP Avg Researcher (mo): {dEOS['RIP Avg Researcher']}')
	print(f'Comps Entered (w):       {dEOS['Comps Entered']}')
	print(f'Listings Entered (w):    {dEOS['Listings Entered']}')
	print(f'Accounts Created (w):    {dEOS['Accounts Created']}')
	print(f'Requests Over/Under (w):  {dEOS['Requests Over Under']}')

	ui = td.uInput('\n [Enter] to run another report [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
