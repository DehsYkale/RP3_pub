
import bb
import csv
import dicts
import fun_login
import fun_text_date as td
import lao
import mc
from pprint import pprint

# Get the list of audiences and their groups IDs
def make_master_group_list(d):

	# Get list of counties in PID format
	dCounties = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/LAO_Counties.xlsx')
	lPID_counties = []
	for i in dCounties:
		# tf_county = f"{dCounties[i]['State']}{dCounties[i]['ArcName']}"
		lPID_counties.append(f"{dCounties[i]['State']}{dCounties[i]['ArcName']}")

	# List of audiences to skip	
	lSkip = [
			'Market Insights Subscribers',
			'Land Sale Notification',
			'LAO Staff',
			'Thunderbird',
			'Events',
			'Captial'
			]
	
	with open('c:/TEMP/MC_Groups.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['Audience', 'Aud ID', 'Group', 'Grp ID'])

		for row in d['lists']:
			audience_name = row['name']

			if audience_name in lSkip:
				continue
			
			print(f'Audience: {audience_name}')
			audience_id = row['id']
			dGroups = mc.getListCampaignGroups(client, audience_id)
			for key, val in dGroups.items():
				# Skip Groups named after PIDS
				for pid_cnty in lPID_counties:
					if key == pid_cnty:
						break
				else:
					writer.writerow([audience_name, audience_id, key, val])

	lao.openFile('c:/TEMP/MC_Groups.csv')

# START PROGRAM ###############################################

client = fun_login.MailChimp()
service = fun_login.TerraForce()

# Make dict of Audience Names, IDs, Interests and Tags
d = mc.getListNameID(client)
print('Audience Names and IDs')
ldAudiences = d['lists']
pprint(ldAudiences)
make_master_group_list(d)
print()

	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')


	# dListMembers, listID = mc.get_audience_members(client, audience_id)

	# # dInterests = mc.getListInterestsDict(client, audience_id)
	# # pprint(dInterests)
	# # ui = td.uInput('\n Continue [00]... > ')
	# # if ui == '00':
	# # 	exit('\n Terminating program...')
	
	# dEmail_group = {}
	# for row in dListMembers:
	# 	# pprint(row) # Member ID
	# 	dMem = dListMembers[row]
	# 	email = dMem['email']
	# 	dEmail_group[email] = []
		
	# 	pprint(dMem)
	# 	print()
	# 	dMem_groups = dMem['interests']

	# 	for grp in dMem_groups:
	# 		print(grp)
	# 		print(dMem_groups[grp])
	# 		if dMem_groups[grp] is True:
	# 			for key, val in dGroups.items():
	# 				if grp == val:
	# 					print(f' Group: {key}')
	# 					print(f' ID: {val}')
	# 					dEmail_group[email].append(key)
	# 					break
	# 	pprint(dEmail_group)
	# 	ui = td.uInput('\n Continue [00]... > ')
	# 	if ui == '00':
	# 		exit('\n Terminating program...')


