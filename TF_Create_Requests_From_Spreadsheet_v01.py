
# Create Requests from a spreadsheet
import bb
import dicts
import fun_login
import fun_text_date as td
import lao
import mpy
from pprint import pprint
import webs


def delete_request(service):

	while 1:
		print(' Delete Request')
		ui = td.uInput('\n Enter Request Name (RQ-######) [00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui[:3] != 'RQ-':
			td.warningMsg('\n Invalid Request Name format. Please use RQ-###### format.')
			lao.sleep(1)
		else:
			request_name = ui
			break

	# # TerraForce Query
	fields = 'default'
	wc = f"Name = '{request_name}'"
	results = bb.tf_query_3(service, rec_type='Request', where_clause=wc, limit=None, fields=fields)

	print('here1')
	pprint(results)
	request_id = results[0]['Id']
	print(f'Request ID: {request_id}')
	td.banner('TF Delete Request')
	print(f'\n Request Name: {request_name}')
	print(f' Approver: {results[0]["Approver__r"]["Name"]}')
	print(f'\n Description:\n{results[0]["Description__c"]}')
	while 1:
		print(f'\n Delete Request {request_name}?')
		print('\n  1) Yes')
		print('  2) No')
		print('  00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			print(f'Deleting Request {request_name}...')
			results = bb.tf_delete_3(service, request_id, 'lda_Request__c')
			break
		elif ui == '2':
			print(f'Not deleting Request {request_name}...')
			ui = td.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

# Select the Request approver
def select_approver():
	td.banner('TF Create Request From Spreadsheet v01')
	while 1:

		ui = td.uInput('\n Enter Approver Name (First Last) [00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		
		dStaff = dicts.get_staff_dict()
		try:
			approver = dStaff[ui]['UserID']
		except KeyError:
			td.warningMsg(f'\n Approver {ui} not found.')
			lao.sleep(1)
			continue
		print(f'Approver: {ui} ({approver})')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		return approver


def create_requests_from_spreadsheet(service):
	# filename = lao.guiFileOpen(path='F:/Research Department/Projects/Advisors and Markets', titlestring='Make Requests from Spreadsheet', extension=[('Excel files', '.xlsx'), ('csv files', '.csv'),  ('all files', '.*')])
	filename = r'F:\Research Department\Projects\Advisors and Markets\Greenville Spartanburg\Whit TR-Taylors-NGreer 10.08.2025.xlsx'
	dComps = dicts.spreadsheet_to_dict(filename)

	# Fields to include in description
	# Is the spreadshee from L5
	if "geometry" in dComps[1]:

		# Get the approver
		approver = select_approver()
		is_first_request = True

		for row in dComps:
			dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', dGDF=False, lon=dComps[row]['x'], lat=dComps[row]['y'])


			layer = f'{dLAO_geoinfo["state_abb"]}Parcels{dLAO_geoinfo["arcname"]}'
			apn = dComps[row]['apn']

			strDescription = f'Please add Parcel {layer} {apn} to Terraforce and create an outline in the Ownerships layer.'
			
			# Create Request object
			dRequest = {
				'Approver__c': approver,
				'Description__c': strDescription,
				'MapTitle__c': f'L5 Parcel to Research {layer} {apn}',
				'Property_Description_Method__c': 'State, County, and Parcel',
				'RecordTypeId': '0124X000001dVG6QAM',
				'Status__c': 'New',
				'type': 'lda_Request__c'
			}
			# Create Request record
			rq_results = bb.tf_create_3(service, dRequest)

			# Check the first request
			if is_first_request:
				is_first_request = False
				print('\n Checking first Request...\n')
				webs.open_chrome(f'https://landadvisors.lightning.force.com/lightning/r/lda_Request__c/{rq_results}/view')
				ui = td.uInput('\n Continue [00]... > ')
				if ui == '00':
					exit('\n Terminating program...')

	else:
		exit()
		lFields = ['APN', 'County', 'Notes', 'Type', 'Subdivision', 'Acres', 'Sale Price', 'Sale Date', 'Found in L5', 'MLS #']

		for row in dComps:
			pprint(dComps[row])
			strDescription = '-- PROPERTY INFO --'
			for field in lFields:
				if field == 'County':
					strDescription = f"{strDescription}\n{field:15}{'Twin Falls'}"
				else:
					strDescription = f"{strDescription}\n{field:15}{dComps[row][field]}"

		# print(f'{strDescription}')
		# print('-' * 20)
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

		# Create Request object
		dRequest = {
			'Approver__c': '005UT0000067kDx', # Julie Noris
			'Description__c': strDescription,
			'MapTitle__c': 'Twin Falls County Comp',
			'Property_Description_Method__c': 'State, County, and Parcel',
			'RecordTypeId': '0124X000001dVG6QAM',
			'Status__c': 'New',
			'type': 'lda_Request__c'
		}
		# Create Request record
		rq_results = bb.tf_create_3(service, dRequest)
		
		# print('\n Checking first Request...\n')
		# pprint(rq_results)
		# webs.open_chrome(f'https://landadvisors.lightning.force.com/lightning/r/lda_Request__c/{rq_results}/view')
		# ui = td.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')


service = fun_login.TerraForce()

while 1:

	td.banner('TF Create Requests From Spreadsheet v01')

	print(' OPTIONS')
	print('\n  1) Create Requests from Spreadsheet')
	print('  2) Delete a Request')
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '1':
		create_requests_from_spreadsheet(service)
	elif ui == '2':
		delete_request(service)
	elif ui == '00':
		exit('\n Terminating program...')


	