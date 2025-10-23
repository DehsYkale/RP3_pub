# Create MVP Contacts based on the owner person of MVP Deals

import acc
import csv
import bb
import dicts
import fun_login
import fun_text_date as td
import lao
from pprint import pprint

service = fun_login.TerraForce()

# User to select Market
dStaff = dicts.get_staff_dict()

# lDo_not_update_markets = ['CLT', 'DFW', 'TPA', 'HOU', 'PHX', 'SLC', 'TUC']
lDo_not_update_markets = []

while 1:
	td.banner('Make MVP Deal Contact MVP v02')
	market_abb = td.uInput('\n Enter 3 letter Market abbreviation [00] > ').upper()
	if len(market_abb) != 3:
		td.warningMsg('\n Invalid input...try again...')
		lao.sleep(2)
	elif market_abb in lDo_not_update_markets:
		td.warningMsg(f'\n {market_abb} in do not send list!')
		exit('\n Terminating program...')
		# Get full market name
		for row in dStaff:
			if dStaff[row]['marketAbb'] == market_abb:
				market = dStaff[row]['TFmarket']
				break
	elif market_abb == '00':
		exit('\n Terminating program...')
	else:
		# Make list of lists
		break

# Get list of PIDs to skip
lSkip_pids = []
while 1:
	ui = td.uInput('\n Do you have a skip PID list? [0/1/00] > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '0':
		break
	elif ui == '1':
		skip_pids_filename = lao.guiFileOpen(path='F:/Research Department/MIMO/Market Insights/Market Mailers/MVP Deals/', titlestring='Select List of PIDs CSV', extension=[('csv files', '.csv'), ('all files', '.*')])
		with open(skip_pids_filename, 'r') as f:
			csv_reader = csv.reader(f)
			for row in csv_reader:
				if row:  # Skip empty rows
					lSkip_pids.append(row[0])  # Add first column value
		break
	else:
		td.warningMsg('\n Invalid input...try again...')

lAgents = []
for row in dStaff:
	if dStaff[row]['marketAbb'] == market_abb and dStaff[row]['Roll'] == 'Agent':
		market = dStaff[row]['Markets']
		lAgents.append(row)

# Print Market and Agents
print(market)
print(lAgents)

# Select Market from Agents in multiple markets
if 'Nashville' in market:
	market = 'Nashville'
if ',' in market:
	lMarkets = market.split(',')
	print('\n Select Market\n')
	count = 1
	for mkt in lMarkets:
		print(f'  {count}) {mkt}')
		count += 1
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '00':
		exit('\n Terminating program...')
	else:
		market = lMarkets[int(ui)-1]

# Include Escrow and listings?
while 1:
	ui = td.uInput('\n Include Escrow and Listing Deals [0/1/00] > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '0':
		wc = "Market__c = '{0}' AND StageName__c = 'Top 100'".format(market)
		break
	elif ui == '1':
		wc = "Market__c = '{0}' AND StageName__c IN ('Escrow', 'Signed Listing', 'Trusted Listing', 'Top 100')".format(market)
		break

# TerraForce Query
fields = 'default'
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

for row in results:
	dAcc = dicts.get_blank_account_dict()
	dAcc['AID'] = row['AccountId__c']
	if dAcc['AID'] == 'None':
		continue
	# Skip Deals without Person contact
	dAcc = acc.populate_dAcc_from_tf(service, dAcc['AID'], dAcc=dAcc)

	# Add PID, Deal Name and Deal ID (DID) to dAcc
	dAcc['PID'] = row['PID__c']
	dAcc['DID'] = row['Id']
	dAcc['Deal Name'] = row['Name']

	# Skip PIDs in skip list
	if dAcc['PID'] in lSkip_pids:
		td.warningMsg(f'\n Skipping PID: {dAcc["PID"]}...')
		continue

	# Check if one of the agents or Greg Vogel in the market is already in the TOP100AGENT field
	for agent in lAgents:
		# Skip if the agent is already in the TOP100AGENT field or if Greg Vogel is in the TOP100AGENT field
		if agent in dAcc['TOP100AGENT'] or 'Greg Vogel' in dAcc['TOP100AGENT']:
			update_top100 = False
			break
		else:
			update_top100 = True
	if update_top100 is False:
		continue

	# Remove Rick Bressan from TOP100AGENT if it exists
	if dAcc['TOP100AGENT'] == 'Rick Bressan':
		dAcc['TOP100AGENT'] = dAcc['TOP100AGENT'].replace('Rick Bressan;', '')
		dAcc['TOP100AGENT'] = dAcc['TOP100AGENT'].replace('Rick Bressan', 'None')
	if dAcc['TOP100AGENT'] == 'Ashley Bishop':
		dAcc['TOP100AGENT'] = dAcc['TOP100AGENT'].replace('Ashley Bishop;', '')
		dAcc['TOP100AGENT'] = dAcc['TOP100AGENT'].replace('Ashley Bishop', 'None')
	# Remove Ben Jenkins from CATEGORY if it exists
	if 'Ben Jenkins' in dAcc['CATEGORY']:
		dAcc['CATEGORY'] = dAcc['CATEGORY'].replace('Ben Jenkins;', '')
		dAcc['CATEGORY'] = dAcc['CATEGORY'].replace('Ben Jenkins', 'None')
	if 'Ashley Bishop' in dAcc['CATEGORY']:
		dAcc['CATEGORY'] = dAcc['CATEGORY'].replace('Ashley Bishop;', '')
		dAcc['CATEGORY'] = dAcc['CATEGORY'].replace('Ashley Bishop', 'None')

	# Check if MVP (Top 100) exists and if None add Advisor, if other Advisors exist
	# add the market's Advisor(s) or if market's Advisor already exists continue.
	for agent in lAgents:		
		# Add agent or skip if agent is already in TOP100AGENT
		if dAcc['TOP100AGENT'] == 'None':
			dAcc['TOP100AGENT'] = agent
			update_top100 = True
		elif agent in dAcc['TOP100AGENT']:
			update_top100 = False
		else:
			dAcc['TOP100AGENT'] = '{0};{1}'.format(dAcc['TOP100AGENT'], agent)
			update_top100 = True
	
	# Check if CATEGORY is None or Market Mailer, if None add Market Mailer, if Market Mailer exists continue
	if dAcc['CATEGORY'] == 'None':
		dAcc['CATEGORY'] = 'Market Mailer'
		update_category = True
	elif 'Market Mailer' in dAcc['CATEGORY']:
		update_category = False
	else:
		dAcc['CATEGORY'] = '{0};Market Mailer'.format(dAcc['CATEGORY'])
		update_category = True
	
	# print(f"\n PID: {dAcc['PID']}")
	# print(f" AID {dAcc['AID']}")
	# print(f" TOP 100: {dAcc['TOP100AGENT']}")
	# print(f" Category: {dAcc['CATEGORY']}")

	# print('\n here1')
	# pprint(dAcc)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')

	# Update Account
	dup = {'type': 'Account', 'id': dAcc['AID']}
	if update_top100:
		dup['Top100__c'] = dAcc['TOP100AGENT']
	if update_category:
		dup['Category__c'] = dAcc['CATEGORY']

	if update_top100 is True or update_category is True:
		try:
			bb.tf_update_3(service, dup)
		except:
			print('here1')
			pprint(dAcc)
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')
			
	

