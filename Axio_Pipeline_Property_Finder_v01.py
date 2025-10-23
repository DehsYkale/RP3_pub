

# Reads spreadsheet of AxioMetrics pipeline apartment projects and
#  helps locate them in L5 so the user can create a request to have the
#  property added to the Ownership layer

import csv
import lao
import os
from pprint import pprint
import pyperclip
import fun_text_date as td


# Make processed out file
def get_out_csv_file():
	outfilename = filename.replace('xlsx', '_PROCESSED.csv')
	if os.path.isfile(outfilename) is False:
		with open(outfilename, 'w', newline='') as f:
			fout = csv.writer(f)
			header = ['Processing Results',
					'Property Type',
					'Project Name',
					'Units',
					'Stories',
					'Developer',
					'Owner',
					'Street',
					'City',
					'State',
					'Zip Code',
					'Notes',
					'Lat',
					'Lon',
					'Axio ID']
			fout.writerow(header)
	return outfilename

def write_to_out_csv_file():
	lout = [processing_results,
		property_type,
		subdivision,
		units,
		stories,
		developer,
		owner,
		street,
		city,
		state,
		zipcode,
		notes,
		lat,
		lon,
		axioid]
	with open(outfilename, 'a', newline='') as f:
		fout = csv.writer(f)
		fout.writerow(lout)

def print_property_info():
	msgProperty_info = \
		f' Subdivison: {subdivision}\n' \
		f' Developer:  {developer}\n' \
		f' Units:      {units}\n' \
		f' Apt Type:   {property_type}\n' \
		f' Axio Notes: {notes}'
	print(msgProperty_info)
	return msgProperty_info

# td.warningMsg('help!!! HELLO')
# td.instrMsg('help!!! HELLO')
# exit()

filename = r'F:\Research Department\MIMO\zData\AxioMetrics\Pipeline\AUS_Axio_Pipeline_2023_08_22.xlsx'

# Make dict of Pipeline Projects
dPipeline_projects = lao.spreadsheetToDict(filename)
basefilename = os.path.basename(filename)
market = basefilename[:3]
record_count = len(dPipeline_projects)

# Get outfilename
outfilename = get_out_csv_file()

# Cycle through pipeline projects
counter = 1
for row in dPipeline_projects:
	
	d = dPipeline_projects[row]
	# pprint(d)
	
	lon = d['Longitude']
	lat = d['Latitude']
	lat_lon_for_L5 = '{0}, {1}'.format(lat, lon )
	subdivision = d['Property_N']
	developer = d['Developer']
	units = d['Total_Unit']
	property_type = d['Property01']
	stories = d['Stories']
	owner = d['Property_O']
	street = d['Address']
	city = d['City']
	state = d['State']
	zipcode = d['ZIP_Code']
	axioid = d['Property_I']
	notes = d['Property02']
	
	# Check if property is already done
	varSkip = f'{market}:{subdivision}:{developer}:{units}'
	if lao.SkipFile(varSkip, 'skipAxioPipeline', 'CHECK'):
		counter += 1
		continue

	print_property_info()

	pyperclip.copy(lat_lon_for_L5)

	# User to select action to take
	while 1:
		lao.banner('Axio Pipeline Property Finder v01')
		print(f'Record Count {counter} : {record_count}')
		msgProperty_info = print_property_info()
		print('\n Lat/Lon copied for L5...')
		msgInstructions = \
			'\n  1) Copy info for Request\n' \
			'  2) Skip/Not Relevant\n' \
			' 00) Quit'
		print(msgInstructions)

		ui = '\n Select > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			user_action = 'Copy info for request'
			break
		elif ui == '2':
			user_action = 'Skipped'
			break
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)
	
	# User Action
	if user_action == 'Copy info for request':
		msgRequest_notes = '\n Enter Request instuctions or [Enter] for none...\n > ')
		if msgRequest_notes == '':
			msgRequest_notes = 'None'
		msgProperty_info = f'\n\n AXIO PIPELINE PROPERTY\nRequest Instructions: {msgRequest_notes}\n\n{msgProperty_info}'
		pyperclip.copy(msgProperty_info)
		print('\n Property info copied...')
		ui = '\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		processing_results = 'Requested PID'
	elif user_action == 'Skipped':
		while 1:
			msgSkipped = \
				'  Enter Skip Reason\n\n' \
				'  1) Under Construction\n' \
				'  2) Construction Loan Found\n' \
				'  3) Could Not Determine Parcel\n' \
				'  4) LAO Deal\n' \
				'  5) Property Entered\n' \
				'  6) Other\n' \
				' 00) Quit'
			print(msgSkipped)
			ui = '\n Select > ')
			if ui == '00':
				exit('\n Terminating program...')
			elif ui == '1':
				processing_results = 'Under Construction'
				break
			elif ui == '2':
				processing_results = 'Construction Loan Found'
				break
			elif ui == '3':
				processing_results = 'Could Not Determine Parcel'
				break
			elif ui == '4':
				processing_results = 'LAO Deal'
				break
			elif ui == '5':
				processing_results = 'Property Entered'
				break
			elif ui == '6':
				processing_results = '\n Enter why property was skipped:\n >')
				if processing_results == '':
					processing_results = 'Other'
				break
			else:
				td.warningMsg('\n Invalid input...try again...')
				lao.sleep(2)

	# Write property info to csv and skip files
	write_to_out_csv_file()
	lao.SkipFile(varSkip, 'skipAxioPipeline', 'WRITE')
	counter += 1

	


		


# =HYPERLINK("https://maps.landadvisors.com/h5v/?viewer=austin.h5v&runWorkflow=ZoomTo&mapid=8&lyr=Recent%20Sales&qry=pid=%27TXBastrop238487%27#", "L5")