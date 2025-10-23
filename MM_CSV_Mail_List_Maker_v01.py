
# from amp import getMarketAbbreviation
import lao
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
from glob import glob
import os
import shutil
from pprint import pprint
import webs



# Make office list
def get_office_list():
	lOffice = []
	for row in dAgent:
		record = dAgent[row]
		# print(f'\n {row} : {record['Office']}')
		# if not record['Office'] in lOffice and not record['Office'] == '' and not record['Office'] == 'Reno'  and not record['Office'] == 'Scottsdale' and record['LAO'] == 'Yes' and not record['Office'] == 'JMP' and not record['Office'] == 'Yuma':
		if not record['Office'] in lOffice and not record['Office'] == '' and not record['Office'] == 'Scottsdale' and record['LAO'] == 'Yes' and not record['Office'] == 'Conservation' and not record['Office'] == 'JMP' and not record['Office'] == 'New York' and not record['Office'] == 'None' and not record['Office'] == 'Yuma':
			lOffice.append(record['Office'])
	lOffice.append('Jaxsonville')
	lOffice.append('Campbell')
	lOffice.append('Heglie')
	lOffice.append('McCarville')
	lOffice.append('Medical')
	lOffice.append('Schwab')
	lOffice.append('Vogel')
	lOffice.append('Wuertz')
	lOffice.append('Xander')
	lScottsaleAgents = ['Campbell',
						'Heglie',
						'McCarville',
						'Medical',
						'Schwab',
						'Vogel',
						'Wuertz',
						'Xander',
						'Scottsdale']
	
	return lOffice, lScottsaleAgents

# Get the MVPs based on Market/Advisor
def get_office_MVPs():
	print(f' Processing {office}...\n')
	wc = "Category__c INCLUDES ('Market Mailer') AND BillingStreet != '' AND (NOT (FirstName LIKE '%Deceased%')) AND (NOT (LastName LIKE '%Deceased%')) AND (NOT (PersonTitle LIKE '%Deceased%')) AND (Top100__c INCLUDES ("
	firstAgent = True
	for agent in dAgent:
		if office == 'Atlanta':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('David Moore') and Top100__c EXCLUDES ('Mike Ripley')"
			break
		elif office == 'Jacksonville':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('David Moore;Mike Ripley')"
			break
		if office == 'Orlando':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Mike Ripley') and Top100__c EXCLUDES ('David Moore')"
		elif office == 'Campbell': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Wesley Campbell') and Top100__c EXCLUDES ('Mike Schwab', 'Greg Vogel')"
			break
		elif office == 'Heglie': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Ben Heglie') and Top100__c EXCLUDES ('Mike Schwab')"
			break
		elif office == 'McCarville': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Kirk McCarville', 'Trey Davis')"
			break
		elif office == 'Medical': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Michele Pino', 'Michael Brinkley', 'Laurie Sandau') and Top100__c EXCLUDES ('Mike Schwab', 'Greg Vogel')"
			break
		elif office == 'Schwab': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Mike Schwab')"
			break
		elif office == 'Vogel': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Greg Vogel') and Top100__c EXCLUDES ('Ben Heglie', 'Mike Schwab')"
			break
		elif office == 'Wuertz': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Bobby Wuertz') and Top100__c EXCLUDES ('Ben Heglie', 'Kirk McCarville', 'Trey Davis')"
			break
		elif office == 'Xander': # and agent == 'Greg Vogel':
			wc = "Category__c INCLUDES ('Market Mailer') and (Top100__c INCLUDES ('Max Xander') and Top100__c EXCLUDES ('Mike Schwab', 'Greg Vogel')"
			break
		elif office == dAgent[agent]['Office'] and dAgent[agent]['Roll'] == 'Agent' and dAgent[agent]['LAO'] == 'Yes' and not '.' in agent:
			if firstAgent:
				wc = "{0}'{1}')".format(wc, agent)
				firstAgent = False
			else:
				wc = "{0} OR Top100__c INCLUDES ('{1}')".format(wc, agent)
	wc = '{0})'.format(wc)

	# TerraForce Query
	fields = 'default'
	results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
	return results

def write_to_presorted_csv():
	
	# Create Presorted CSV		
	with open(csv_presort, 'w', newline='') as f:
		fout = csv.writer(f)
		fout.writerow(header)
		for row in results:
			# Verify Address and skip if invalid
			street = row['BillingStreet'].replace('\n', ', ')
			street = street.strip()
			city = row['BillingCity'].strip()
			state = row['BillingState'].strip()
			zipcode = row['BillingPostalCode'].strip()
			if street == 'None' or city == 'None' or state == 'None' or zipcode == 'None':
				td.warningMsg(f'\n City: {city}\n State: {state}\n Zip: {zipcode}')
				webs.openTFAccId(row['Id'])
				ui = td.uInput('\n Continue [00]... > ')
				if ui == '00':
					exit('\n Terminating program...')
			# Write contact to list
			lRow = []
			lRow.append(row['FirstName'])
			lRow.append(row['LastName'])
			try:
				lRow.append(row['Company__r']['Name'])
			except TypeError:
				lRow.append('')
			lRow.append(street)
			lRow.append(city)
			lRow.append(state)
			lRow.append(zipcode)
			lRow.append(MM_market)
			tf_url = '=HYPERLINK("https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view", "TF")'.format(row['Id'])
			lRow.append(tf_url)
			lRow.append('none')

			# Write row to Presorted CSV
			fout.writerow(lRow)
			# Write row to All MVPs CSV
			fAll_MVPs.writerow(lRow)
	
# Sort Presorted CSV and write to Sorted CSV
def sort_office_mm_csv():
	with open(csv_presort, 'r') as f, open(csv_sorted, 'w', newline='') as o:
		fin = csv.reader(f)
		fout = csv.writer(o)
		fout.writerow(next(fin))
		sorted1 = sorted(fin, key=lambda row: row[2])
		sorted2 = sorted(sorted1, key=lambda row: row[1])
		for row in sorted2:
			fout.writerow(row)
	os.remove(csv_presort)

lao.banner('Market Mailer CSV Mail List Maker v01')

service = fun_login.TerraForce()

dAgent = lao.getAgentDict(dict_type='full', version='v2')
fields = 'ID, Name, FirstName, LastName, Company__r.Name, BillingStreet, BillingCity, BillingState, BillingPostalCode'

# Get dict of Markets/Advisors
dMM_market = dicts.get_mm_market_dict()
# Get list of offices/Advisors (PHX)
lOffice, lScottsaleAgents, lRemove_Vogel, lSchwab_Only = dicts.get_lao_markets_mailer_lists()
# CSV with MM counts for all Markets/Adviosrs
csv_office_mailer_count = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Mailing Lists/Office Mailer Count.csv'
# CSV of all contacts
csv_all_mvps = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Mailing Lists/All MVPs.csv'
header = ['First Name', 'Last Name', 'Company', 'Street', 'City', 'State', 'ZipCode', 'Market', 'TFID URL', 'Letter ID']


with open(csv_all_mvps, 'w', newline='') as h:
	fAll_MVPs = csv.writer(h)
	fAll_MVPs.writerow(header)

	for office in lOffice:
		# if not office in lScottsaleAgents:
		# 	continue

		# Skip these offices
		if office == 'Casa Grande' or office == 'Seattle' or office == 'Agriculture' or office == 'Conservation':
			continue
			
		# Get marketAbb
		elif office in lScottsaleAgents:
			marketAbb = office[:3].upper()
		else: 
			marketAbb, stateAbb = td.get_market_abbreviation(office)

		# Set CSV file variables
		csv_presort = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Mailing Lists/{0} Mailing List.csv'.format(marketAbb)
		csv_sorted = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Mailing Lists/{0} Mailing List SORTED.csv'.format(marketAbb)

		# Get Market Mailer Market for Cover Letter
		MM_market = dMM_market[marketAbb]
		# Get the MVPs based on Market/Advisor from TF
		results = get_office_MVPs()
		# Write to Presorted, All MVPs CSVs and Office Mailer Count CSVs
		write_to_presorted_csv()
		# Sort CSV
		sort_office_mm_csv()

dAll_MVPs = lao.spreadsheetToDict(csv_all_mvps)
mail_list_folder = 'F:/Research Department/MIMO/Market Insights/Market Mailers/Mailing Lists/'
lMail_List_CSVs = glob('{0}*Mailing List SORTED.csv'.format(mail_list_folder))

csv_mailer_generic_filename = ('{0}GEN Mailing List.csv'.format(mail_list_folder))
lGeneric_Contact_TFIDs = []

# Create GENERIC mailer list (Contacts with multiple Advisors as MVP)
with open(csv_mailer_generic_filename, 'w', newline='') as g, open(csv_office_mailer_count, 'w', newline='') as c:
	fCount = csv.writer(c)
	fCount.writerow(['Office', 'Mailers'])
	fout_gen = csv.writer(g)
	fout_gen.writerow(header)

	i_generic_letter_id = 1
	count_generic = 1
	# Clycle through MARKET/ADVISOR mail list CSVs
	for ml in lMail_List_CSVs:

		# Count MARKET/ADVISOR
		count_market_advisors = 1

		# Get market abbrivation from file name
		filename = os.path.basename(ml)
		marketAbb = filename[:3]

		# Create GENERIC mailer list and individual MARKET/ADVISOR mailer lists
		ml_out_file_name = ml.replace('SORTED', 'CLEANED')
		with open(ml_out_file_name, 'w', newline='') as f:
			fout_mkt = csv.writer(f)
			fout_mkt.writerow(header)
		
			# Make MARKET/ADVISOR mail list SORTED dict
			dOffice_MM_List = lao.spreadsheetToDict(ml)

			i_market_letter_id = 1
			# Cycle through mail list rows (omml)
			for omml in dOffice_MM_List:
				lGeneric_Offices = []
				omml_url = dOffice_MM_List[omml]['TFID URL']

				for amvp in dAll_MVPs:
					amvp_url = dAll_MVPs[amvp]['TFID URL']
					# Add Office(s) to contact record
					if amvp_url == omml_url:
						lGeneric_Offices.append(dAll_MVPs[amvp]['Market'])
						
				# Skip generic if only one office
				if len(lGeneric_Offices) > 1:
					# Skip Jacksonville if agents are David Moore and Mike Ripley
					if 'Jacksonville' in lGeneric_Offices:
						if 'David Moore' in lGeneric_Offices and 'Mike Ripley' in lGeneric_Offices:
							continue

					# Remove Vogel
					if 'Vogel' in lGeneric_Offices:
						# print(lGeneric_Offices)
						for scottsdale_agent in lRemove_Vogel:
							if scottsdale_agent in lGeneric_Offices:
								lGeneric_Offices.remove('Vogel')
								break
				
					# Schawb Only remove other Arizona agents
					if 'Schwab' in lGeneric_Offices:
						# print(lGeneric_Offices)
						for arizona_agent in lSchwab_Only:
							if arizona_agent in lGeneric_Offices:
								lGeneric_Offices.remove(arizona_agent)
				
				# Create out list to write to cleaned file
				strGeneric_Offices = ', '.join(lGeneric_Offices)
				lout = [dOffice_MM_List[omml]['First Name'],
						dOffice_MM_List[omml]['Last Name'],
						dOffice_MM_List[omml]['Company'],
						dOffice_MM_List[omml]['Street'],
						dOffice_MM_List[omml]['City'],
						dOffice_MM_List[omml]['State'],
						str(dOffice_MM_List[omml]['ZipCode']),
						strGeneric_Offices,
						omml_url]
				
				# WRITE TO FINAL CSVS #######################################################
				# Write to single MARKET/ADVISOR CSV
				if len(lGeneric_Offices) == 1:
					# Add letter id
					letter_id = '{0} {1:03d}'.format(marketAbb, i_market_letter_id)
					lout.append(letter_id)
					fout_mkt.writerow(lout)
					i_market_letter_id += 1
					count_market_advisors += 1
				elif omml_url in lGeneric_Contact_TFIDs:
					continue
				# Writer to GENERIC CSV
				else:
					# Add letter id
					letter_id = '{0} {1:03d}'.format('GEN', i_generic_letter_id)
					lout.append(letter_id)
					fout_gen.writerow(lout)
					lGeneric_Contact_TFIDs.append(omml_url)
					i_generic_letter_id += 1
					count_generic += 1
				############################################################################
		
		# Write row to Office Mailer Count CSV
		fCount.writerow([marketAbb, count_generic])
		
		os.remove(ml)
		# Copy Market/Advisor CSV to local driver for mail merge
		print(f'\n Copying {marketAbb} to OneDrive...')
		csv_mm_on_c_drive = 'C:/Users/blandis/OneDrive/Documents/My Data Sources/{0} Mailing List.csv'.format(marketAbb)
		shutil.copy2(ml_out_file_name, csv_mm_on_c_drive)
	
	fCount.writerow(['GEN', count_market_advisors])

# Copy Generic CSV to local driver for mail merge
csv_mm_on_c_drive = 'C:/Users/blandis/OneDrive/Documents/My Data Sources/{0} Mailing List.csv'.format('GEN')
shutil.copy2(csv_mailer_generic_filename, csv_mm_on_c_drive)

exit('\n Fin\n')