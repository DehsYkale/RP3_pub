# AWS Functions

from fiona import remove
import fun_login
from json import dump, load
from lao import getUserName, convertState, warningMsg, uInput, sleep, print_function_name, openFile
import fun_text_date as td
from pprint import pprint
import subprocess
import boto3
from pathlib import Path
import mimetypes

# OPR MAPS ###########################################################################
# Upload OPR maps to AWS
def aws_upload_opr_maps(delete_files=False):
	from glob import glob
	from os import remove, path, makedirs, system
	print_function_name('aws def aws_upload_opr_maps')

	# Variables
	# oprMapFilePath = 'F:\\Research Department\\Code\\ASW_Upload\\Maps'
	# oprMapFilePath = 'C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Maps'
	oprMapFilePath = 'C:\\Users\\Public\\"Public Mapfiles"\\M1_Files\\AWS_OPR_Maps_Upload'
	# oprListingsFilePath = 'C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Listings'
	# oprListingsArchiveFilePath = 'F:\\Research Department\\scripts\\awsUpload\\Listings Archive'
	lMaps = glob('C:\\Users\\Public\\"Public Mapfiles"\\M1_Files\\AWS_OPR_Maps_Upload\\*.*')
	# lCompBrochures = glob('C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Listings\\*.pdf')

	# Copy Maps & Listing Brochures to AWS
	if not lMaps == []:
		# Upload the folder contents to AWS
		print('\n Uploading OPR maps...\n')
		system('aws s3 sync "{0}" s3://request-server/maps/ --acl public-read'.format(oprMapFilePath))
		print(' Upload complete...')
		if delete_files:
			print('\n Deleting maps...')
			for map in lMaps:
				try:
					remove(map)
				except WindowsError:
					pass

def opr_map_aws_delete(PID=None, file_type='Both', prefix_delete=None):
	import subprocess
	
	folder_aws = f's3://request-server/maps'
	creation_flags = subprocess.CREATE_NO_WINDOW

	# Bulk delete by prefix
	if prefix_delete:
		print(f'\n Deleting all PNG files starting with "{prefix_delete}"...')
		
		# Delete all PNG files matching the prefix
		subprocess.run(
			f'aws s3 rm {folder_aws}/ --recursive --exclude "*" --include "{prefix_delete}*.png" --only-show-errors',
			creationflags=creation_flags
		)
		print(f' Bulk deletion complete for prefix "{prefix_delete}"')
		return
	
	# Single PID deletion
	if not PID:
		print(' Error: Must provide either PID or prefix_delete parameter')
		return
	
	print(f'\n Deleting OPR maps for {PID}...')
	png_file = f'{PID}.png'
	jpg_file = f'{PID}.jpg'

	# Delete PNG file
	if file_type in ['Both', 'PNG']:
		subprocess.run(f'aws s3 rm {folder_aws}/{png_file} --only-show-errors', creationflags=creation_flags)
	
	# Delete JPG file
	if file_type in ['Both', 'JPG']:
		subprocess.run(f'aws s3 rm {folder_aws}/{jpg_file} --only-show-errors', creationflags=creation_flags)

	print(f' Deletion complete for {PID}')

def opr_map_aws_copy(PID, action='UP or DOWN'):

	import subprocess
	import os
	
	folder_aws = f's3://request-server/maps'
	folder_user = f'C:/Users/Public/"Public Mapfiles"/M1_Files'
	png_file = f'{PID}.png'
	jpg_file = f'{PID}.jpg'
	creation_flags = subprocess.CREATE_NO_WINDOW

	if action == 'DOWN':
		print('\n Downloading OPR map...')
		# subprocess.run(f'aws s3 cp {folder_aws}/{png_file} {folder_user}/{png_file} --only-show-errors')
		subprocess.run([
			'aws', 's3', 'cp',
			f'{folder_aws}/{png_file}',
			f'{folder_user}/{png_file}',
			'--only-show-errors',
			'--acl', 'public-read'
		], creationflags=creation_flags, check=True)
	elif action == 'UP':
		print('\n Uploading OPR maps...')
		# subprocess.run(f'aws s3 cp {folder_user}/{png_file} {folder_aws}/{png_file} --only-show-errors --acl public-read', creationflags=creation_flags, check=True)
		subprocess.run([
			'aws', 's3', 'cp',
			f'{folder_user}/{png_file}',
			f'{folder_aws}/{png_file}',
			'--only-show-errors',
			'--acl', 'public-read'
		], creationflags=creation_flags, check=True)
		# if os.path.exists(jpg_file_user):
		subprocess.run([
			'aws', 's3', 'cp',
			f'{folder_user}/{jpg_file}',
			f'{folder_aws}/{jpg_file}',
			'--only-show-errors',
			'--acl', 'public-read'
		], creationflags=creation_flags, check=True)
	# aws s3 sync "{0}" s3://request-server/maps/ --acl public-read

def opr_map_aws_list_png():
	import subprocess
	import json
	import csv
	from datetime import datetime
	
	folder_aws = 's3://request-server/maps'
	output_file = r'C:\TEMP\aws_png_files.csv'
	
	print('\n Retrieving PNG file list from AWS...')
	creation_flags = subprocess.CREATE_NO_WINDOW
	
	# List all PNG files in the bucket
	result = subprocess.run(
		f'aws s3api list-objects-v2 --bucket request-server --prefix maps/ --query "Contents[?ends_with(Key, \'.png\')]" --output json',
		capture_output=True,
		text=True,
		creationflags=creation_flags
	)
	
	if result.returncode == 0:
		files = json.loads(result.stdout)
		
		if files:
			# Write to CSV
			with open(output_file, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(['Filename', 'Size_Bytes', 'Size_MB', 'Last_Modified', 'PID'])
				
				for file in files:
					filename = file['Key'].split('/')[-1]  # Get just the filename
					size_bytes = file['Size']
					size_mb = round(size_bytes / (1024**2), 2)
					last_modified = file['LastModified']
					pid = filename.replace('.png', '')  # Extract PID from filename
					
					writer.writerow([filename, size_bytes, size_mb, last_modified, pid])
			
			print(f' Found {len(files):,} PNG files')
			print(f' CSV file created: {output_file}')
			
			openFile(output_file)

			return len(files)
		else:
			print(' No PNG files found in bucket')
			return 0
	else:
		print(f' Error: {result.stderr}')
		return None
	
# FILE UTILITIES ###########################################################################
def check_bucket_usage(bucket='request-server', prefix='maps/'):
	import subprocess
	import json
	
	print(f'\n Checking bucket usage for {bucket}/{prefix}...')
	
	# Get bucket size and object count
	result = subprocess.run(
		f'aws s3api list-objects-v2 --bucket {bucket} --prefix {prefix} --query "[sum(Contents[].Size), length(Contents[])]" --output json',
		capture_output=True,
		text=True,
		creationflags=subprocess.CREATE_NO_WINDOW
	)
	
	if result.returncode == 0:
		data = json.loads(result.stdout)
		total_bytes = data[0] if data[0] else 0
		object_count = data[1] if data[1] else 0
		
		# Convert to human-readable format
		total_gb = total_bytes / (1024**3)
		total_mb = total_bytes / (1024**2)
		
		print(f' Total Objects: {object_count:,}')
		print(f' Total Size: {total_gb:.2f} GB ({total_mb:.2f} MB)')
		
		return {'bytes': total_bytes, 'objects': object_count, 'gb': total_gb}
	else:
		print(f' Error: {result.stderr}')
		return None

# Check if file exists on AWS
def aws_file_exists(filename, extention='jpg', verbose=False):
	import requests
	print_function_name('aws def aws_file_exists')

	file_exits = False
	# Check for pdf listing brochure
	if '.pdf' in filename:
		r = requests.get('https://request-server.s3.amazonaws.com/listings/{0}'.format(filename))
	# Check for jpg map
	else:
		r = requests.get(f'https://request-server.s3.amazonaws.com/maps/{filename}.{extention}')
	# Check results
	# print(r.status_code)
	if r.status_code == 200:
		file_exits = True
		if verbose:
			print(f'{filename} exists on AWS')
	else:
		if verbose:
			td.warningMsg(f'{filename} does not exist on AWS')
	# return results
	return file_exits

# Copies M1 json files to/from AWS to local drive
def get_m1_file_copy(action='UP or DOWN', user='None', getZoom=False):
	import subprocess
	if user == 'None':
		user = getUserName()
	folder_aws = f's3://research-datastore/{user}'
	folder_user = f'C:/Users/Public/"Public Mapfiles"/M1_Files'
	# folder_user = 'C:/TEMP/TEMP/'
	lUp = ['zoomToPolygon.json']
	lDown = ['ArcMakePIDFromParcelOwnerInfo.json', 'PIDOID.json']
	if action == 'UP':
		creation_flags = subprocess.CREATE_NO_WINDOW
		for file in lUp:
			subprocess.run(f'aws s3 cp {folder_user}/{file} {folder_aws}/{file} --only-show-errors', creationflags=creation_flags, check=True)
	elif action == 'DOWN':
		for file in lDown:
			subprocess.run(f'aws s3 cp {folder_aws}/{file} {folder_user}/{file} --only-show-errors')
	if getZoom:
		subprocess.run(f'aws s3 cp {folder_aws}/zoomToPolygon.json C:TEMP/TEMP/zoomToPolygon.json --only-show-errors')

# PID AND POLYGONS ###########################################################################
# Get blank Arc AWS dictionary
def get_Arc_AWS_dict():
	user, initials = getUserName(initials=True)
	j = {'action': 'None',
		'dateupdated': todayDate(dateformat='slash'),
		'initials': initials,
		'oid': 'None',
		'layername': '',
		'lid': 'None',
		'lon': 'None',
		'lat': 'None',
		'fieldname': 'None',
		'parcels': 'None',
		'pid': 'None',
		'pidnew': 'None',
		'propertyid': 'None',
		'user': user
		}
	return j

# Split PID Instructions
def split_PID_Instructions():
	from lao import banner, uInput, warningMsg
	banner('Lead to Sale AWS v01.108')
	msg = \
		' SPLIT INSTRUCTIONS' \
		'\n 1) Split the OwnerIndex polygon in ArcMap.' \
		'\n 2) Save the polygons.' \
		'\n 3) Select the polygon that sold.'
	print(msg)
	while 1:
		ui = uInput('\n\n   Has this been done [0/1/00] > ')
		if ui == '1':
			break
		# Write Fail text file to stop Power PID Producer in ArcMap
		elif ui == '0' or ui == '00':
			with open('C:/Users/Public/Public Mapfiles/Power PID Producer TF Record Results.txt', 'w') as f:
				f.write('Fail')
				exit()
		else:
			warningMsg('\n Invalid input...try again...')

# Read/Write/Clear PID and OID from/to json file
def read_Write_PID_OID(PID='Read', OID='Read'):
	jFile = 'C:/Users/Public/Public Mapfiles/M1_Files/PIDOID.json'
	# Read if PID is None
	if PID == 'Read':
		with open(jFile, 'rb') as f:
			d = load(f)
		return d['pid'], d['oid']
	elif PID == 'Clear':
		d = {}
		d['pid'] = 'None'
		d['oid'] = 'None'
		with open(jFile, 'wb') as f:
			dump(d, f)
	# Write PID and OID to json file
	else:
		# Check if OID needs to be looked up
		if PID != 'Read' and OID == 'Write':
			import mpy
			import subprocess
			OID = mpy.get_OID_from_PID(PID)
			OID = str(OID)
			print(f' OID: {OID}')
		# Write PID and OID to json file
		d = {}
		d['pid'] = PID
		d['oid'] = OID
		with open(jFile, 'w') as f:
			dump(d, f)
		# Upload to AWS
		user = getUserName()
		folder_aws = f's3://research-datastore/{user}'
		folder_user = f'C:/Users/Public/"Public Mapfiles"/M1_Files'
		lUp = ['zoomToPolygon.json', 'PIDOID.json']
		creation_flags = subprocess.CREATE_NO_WINDOW
		for file in lUp:
			subprocess.run(f'aws s3 cp {folder_user}/{file} {folder_aws}/{file} --only-show-errors', creationflags=creation_flags, check=True)
		return d

# Check if Ownership exists based on a Lead centroid
def Ownership_Exist():
	user, initials = getUserName(initials=True)

	j = {'action': 'Ownership Exist',
	'dateupdated': todayDate(dateformat='slash'),
	'initials': initials,
	'oid': 'None',
	'layername': 'Ownerships',
	'lid': 'None',
	'lon': 'None',
	'lat': 'None',
	'fieldName': 'apn',
	'parcels': 'None',
	'pid': 'None',
	'pidnew': 'None',
	'propertyid': 'None',
	'user': user
	}


	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'wb') as f:
		dump(j, f)

	run_Arc_AWS()

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'rb') as f:
		j = load(f)
	
	return j['pid']

# Make the json file for creating an OwernIndex poly on the service from Parcels
# Requires info to be passed using dd the TF data dict
def make_AWS_OwnerIndex_Poly_from_Parcels_dd(dd, runASW=True):
	print('\n RUNNING: make_AWS_OwnerIndex_Poly_from_Parcels_dd')
	
	user, initials = getUserName(initials=True)

	# Check if APNs are listed in Parcel__c and if not stop and warn the user.
	if dd['Parcels__c'] == None or dd['Parcels__c'] == '' or dd['Parcels__c'] == 'None':
		warningMsg(' No APNs given so cannot make a PID polygon.  It must be drawn manually.')
		ui = uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		return

	# Construct parcel layer name
	if len(dd['State__c']) > 2:
		stAbb = convertState(dd['State__c'])
	else:
		stAbb = dd['State__c']
	layername = '{0}Parcels{1}'.format(stAbb, dd['County__c'])

	j = {'action': 'Make New OI Poly from Parcels',
		'dateupdated': td.today_date(dateformat='slash'),
		'initials': initials,
		'oid': 'None',
		'layername': layername.upper(),
		'lid': 'None',
		'lon': 'None',
		'lat': 'None',
		'fieldName': 'apn',
		'parcels': dd['Parcels__c'],
		'pid': dd['PID__c'],
		'pidnew': 'None',
		'propertyid': 'None',
		'user': user
		}
	
	pprint(j)
	
	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'w') as f:
		dump(j, f, indent=4)

	if runASW:
		run_Arc_AWS()

# Make the json file for creating an OwernIndex poly on the service from Parcels
# Requires info to be passed using dd the TF data dict
def make_AWS_OwnerIndex_Poly_from_Parcel_PropertyIds(dd, lPropertyIds, runASW=True):
	print('\n RUNNING: make_AWS_OwnerIndex_Poly_from_Parcel_PropertyIds')
	user, initials = getUserName(initials=True)

	# Construct parcel layer name and county (stAbb_county)
	if len(dd['State__c']) > 2:
		stAbb = convertState(dd['State__c'])
	else:
		stAbb = dd['State__c']
	county = dd['County__c']
	layername = f'{stAbb}Parcels{county}'.upper()
	county = f'{stAbb}_{county}'

	j = {
		"action": "Make New OI Poly from Parcel PropertyIds",
		"county": county,
		"dateupdated": td.today_date(dateformat='slash'),
		"fieldName": "propertyid",
		"initials": initials,
		"layername": layername,
		"lat": "None",
		"lid": "None",
		"lon": "None",
		"oid": "None",
		"parcels": "None",
		"pid": dd['PID__c'],
		"pidnew": "None",
		"propertyid": lPropertyIds,
		"user": user
	}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'w') as f:
		dump(j, f)

	if runASW:
		run_Arc_AWS()

# Make the json file for creating an OwernIndex poly on the service from Parcels
def make_AWS_OwnerIndex_Poly_from_OwnerIndex_Poly(PID='None', PIDnew='None', runASW=True):
	print('\n RUNNING: make_AWS_OwnerIndex_Poly_from_OwnerIndex_Poly')
	user, initials = getUserName(initials=True)

	j = {'action': 'Make New OI Poly from OI poly',
		'dateupdated': td.date_engine(date='today', outformat='slash', informat='unknown'),
		'initials': initials,
		'oid': 'None',
		'layername': 'None',
		'lid': 'None',
		'lon': 'None',
		'lat': 'None',
		'fieldName': 'pid',
		'parcels': 'None',
		'pid': PID,
		'pidnew': PIDnew,
		'propertyid': 'None',
		'user': user
		}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'w') as f:
		dump(j, f)
	if runASW:
		run_Arc_AWS()

# Make the json file for creating an OwernIndex poly on the service from Parcels
def make_AWS_OwnerIndex_Poly_from_Lead_Poly(PID, LID, runASW=True):
	print('\n RUNNING: make_AWS_OwnerIndex_Poly_from_Lead_Poly')
	user, initials = getUserName(initials=True)

	# Make layername from split of LID
	lLIDName = LID.split('_')
	# LID format may or may not include state
	# LID starts with state
	if len(lLIDName[0]) == 2:
		county = lLIDName[1]
		stateAbb = lLIDName[0]
	# LID does not start with state
	else:
		from lao import getCounties
		county = lLIDName[0]
		stateAbb = getCounties(returnList='State', market='None', ArcName=county, MarketAbb='None')
	layername = '{0}LEADS{1}'.format(stateAbb, county)
	
	j = {'action': 'Make New OI Poly from Lead poly',
		'dateupdated': todayDate(dateformat='slash'),
		'initials': initials,
		'oid': 'None',
		'layername': layername.upper(),
		'lid': LID,
		'lon': 'None',
		'lat': 'None',
		'fieldName': 'LeadId',
		'parcels': 'None',
		'pid': PID,
		'pidnew': 'None',
		'propertyid': 'None',
		'user': user
		}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'wb') as f:
		dump(j, f)
	if runASW:
		run_Arc_AWS()

# Make the json file for creating an OwernIndex poly on the service from Parcels
def make_AWS_Split_OwnerIndex_Update_Attributes_for_New_PID(OID, PID, runASW=True):
	print('\n RUNNING: make_AWS_Split_OwnerIndex_Update_Attributes_for_New_PID')
	user, initials = getUserName(initials=True)

	j = {'action': 'Split OwnerIndex Update Attributes for New PID',
		'dateupdated': todayDate(dateformat='slash'),
		'initials': initials,
		'oid': OID,
		'layername': 'None',
		'lid': 'None',
		'lon': 'None',
		'lat': 'None',
		'fieldName': 'objectid',
		'parcels': 'None',
		'pid': PID,
		'pidnew': 'None',
		'propertyid': 'None',
		'user': user
		}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'wb') as f:
		dump(j, f)
	if runASW:
		run_Arc_AWS()

# Make the json file for deleteing an OwernIndex poly on the service
def delete_AWS_OwnerIndex_Poly(arcpy, OID, runAWS=True):
	# print('\n RUNNING: delete_AWS_OwnerIndex_Poly')

	# Actions: Make New OI Poly from Parcels, Delete Poly
	user, initials = getUserName(initials=True)

	j = {'action': 'Delete OI Poly',
		'dateupdated': todayDate(dateformat='slash'),
		'initials': initials,
		'oid': OID,
		'layername': 'None',
		'lid': 'None',
		'lon': 'None',
		'lat': 'None',
		'fieldname': 'None',
		'parcels': 'None',
		'pid': 'None',
		'pidnew': 'None',
		'propertyid': 'None',
		'user': user
		}

	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'wb') as f:
		dump(j, f)
	sleep(1)
	if runAWS:
		run_Arc_AWS()

# Run Arc_AWS to add or delete poly from OwnerIndex
def run_Arc_AWS():
	from os import system
	user, initials = getUserName(initials=True)
	print(f'\n User: {user}  Initials: {initials}')
	print('\n Launching run_Arc_AWS...')
	if user =='blandis':
		# Do something specific for user 'blandis'
		pyPath = 'C:/"Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" "F:/Research Department/Code/RP3/Arc_AWS_v03.py"'
	else:
		pyPath = 'C:/"Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" "F:/Research Department/Code/RP3/Arc_AWS_v02.py"'
	# pyPath = 'C:/"Program Files/Python312/python.exe" "F:/Research Department/Code/RP3/aws.py"'
	system(pyPath)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

def run_Arc_AWS_play():
	from os import system
	pyPath = 'C:/"Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" "F:/Research Department/Code/Research/Arc_AWS_v01_play.py"'
	system(pyPath)

# Run script launched by an ArcMap script
def run_Arc_Subscript(fPythonScript):
	from os import system
	from lao import getPath

	# Write Results file to let ArcMap know if the subscript was successful
	with open('C:/Users/Public/Public Mapfiles/Power PID Producer TF Record Results.txt', 'w') as f:
		f.write('Fail')

	# Run the script
	system('{0}{0}'.format(getPath('pyEXE'), fPythonScript))

	# Read Results file to let ArcMap know if the subscript was successful
	with open('C:/Users/Public/Public Mapfiles/Power PID Producer TF Record Results.txt', 'r') as f:
		tf_record_results = f.readline()
	
	# If the fPythonScript failed exit the Arc script
	if tf_record_results == 'Fail':
		import arcpy
		arcpy.AddError('\n TF record not created, terminating program...\n')
		exit()

# Check age of ArcMakePIDFromParcelOwnerInfo.json
def was_file_modified_recently(file_to_check='Make PID from Parcels', seconds=90):
	from datetime import datetime, timedelta

	user = getUserName()
	if file_to_check == 'Make PID from Parcels':
		filename = 'ArcMakePIDFromParcelOwnerInfo.json'
	elif file_to_check == 'Zoom To Polygon':
		filename = 'zoomToPolygon.json'
	elif file_to_check == 'PIDOID':
		filename = 'PIDOID.json'

	try:
		result = subprocess.run(
			['aws', 's3', 'ls', f's3://research-datastore/{user}/'],
			capture_output=True,
			text=True,
			check=True
		)
		files = result.stdout.strip().split('\n')
		for file in files:
			if file:
				parts = file.split()
				if len(parts) >= 4:
					date = parts[0]
					time = parts[1]
					name = ' '.join(parts[3:])
					if name == filename:
						# Combine date and time
						file_datetime_str = f"{date} {time}"
						file_datetime = datetime.strptime(file_datetime_str, "%Y-%m-%d %H:%M:%S")
						current_time = datetime.now()
						time_difference = current_time - file_datetime
						# Return True if the file was modified recently
						return time_difference <= timedelta(seconds=seconds)

		return False  # File not found or older than specified time
	except subprocess.CalledProcessError as e:
		print(f"An error occurred: {e.stderr}")
		return False
	except Exception as e:
		print(f"An unexpected error occurred: {str(e)}")
		return False

# Upload Listings Brochure to AWS
def upload_listing_package_to_aws(service, PID):

	import bb
	import fun_login
	from lao import guiFileOpen
	from os import rename
	import shutil


	service = fun_login.TerraForce()
	DID = bb.getDIDfromPID(service, PID)

	# User to select Brochure
	package_path = 'F:/Research Department/CompListingBrochures/'
	package_filename = guiFileOpen(package_path, 'Select Brochure PDF', [('PDF', '.pdf'), ('all files', '.*')])
	try:
		package_new_fileName = '{0}_competitors_package.pdf'.format(PID)
		package_file_renamed = '{0}{1}'.format(package_path, package_new_fileName)
		rename(package_filename, package_file_renamed)
	except FileExistsError:
		td.warningMsg('\n A package with that name already exists.')
		ui = td.uInput('\n Continue [00]...')
		if ui == '00':
			exit('\n Terminating program...')

	# package_file_move_to = 'C:/Users/Public/Public Mapfiles/awsUpload/Listings/{0}'.format(package_new_fileName)
	# shutil.move(package_file_renamed, package_file_move_to)

	while 1:
		try:
			package_file_move_to = 'C:/Users/Public/Public Mapfiles/awsUpload/Listings/{0}'.format(package_new_fileName)
			shutil.move(package_file_renamed, package_file_move_to)
			break
		except:
			td.warningMsg('\n PDF is open in a viewer application like FoxIt Reader.\n\n Close the PDF viewer and try again.')
			ui = td.uInput('\n Continue [00]...')
			if ui == '00':
				exit('\n Terminating program...')

	# td.uInput('\n file moved to awsUpload\Listings Continue... > ')
	print('\n Uploading {0}'.format(package_new_fileName))
	sync_opr_maps_comp_listings_folders_to_s3(delete_files=True)

	# ASSIGN PACKAGE TO DEAL *******************************************************
	dpackage = {}
	dpackage['type'] = 'lda_Package_Information__c'
	dpackage['DealID__c'] = DID
	dpackage['Field_Content__c'] = 'https://request-server.s3.amazonaws.com/listings/{0}'.format(package_new_fileName)
	dpackage['Field_Name__c'] = 'Competitor Package'
	dpackage['Field_Type__c'] = 'URL'
	print('\n Adding package info...')
	bb.tf_create_3(service, dpackage)
	# Add competitor package link to TF Deal record
	dup = {
		'type': 'lda_Opportunity__c',
		'Id': DID,
		'Package__c': dpackage['Field_Content__c']
			}
	bb.tf_update_3(service, dup)
	print('Package info added...')
	# ******************************************************************************

	return package_new_fileName

# Upload Map and Listing Brochure to AWS
def sync_opr_maps_comp_listings_folders_to_s3(delete_files=False):
	"""
	Sync local listings folder to S3 bucket.
	Syncs C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Listings\\ to s3://request-server/listings/
	"""
	
	# Configuration
	bucket_name = "request-server"
	l_local_folders = [
						r"C:\Users\Public\Public Mapfiles\awsUpload\maps",
						r"C:\Users\Public\Public Mapfiles\awsUpload\Listings"
					]

	l_s3_prefixes = [
						"maps/",
						"listings/"
					]

	# Initialize S3 client
	s3 = boto3.client('s3')

	# Loop through each local folder and corresponding S3 prefix
	for local_folder, s3_prefix in zip(l_local_folders, l_s3_prefixes):

		from os import path, remove
		import shutil
		# Convert to Path object
		local_path = Path(local_folder)


		print(f"\n Syncing folder: {local_folder} to s3://{bucket_name}/{s3_prefix}")

		# Walk through all files in the local folder
		for file_path in local_path.rglob('*'):
			if file_path.is_file():
				# Calculate relative path from the base folder
				relative_path = file_path.relative_to(local_path)

				# Create S3 key with forward slashes
				s3_key = s3_prefix + str(relative_path).replace('\\', '/')

				try:
					print(f" Uploading: {relative_path} -> {s3_key}")
					
					# Determine content type
					content_type, _ = mimetypes.guess_type(str(file_path))
					if content_type is None:
						content_type = 'application/octet-stream'
					
					# Set up ExtraArgs with ACL and proper headers
					extra_args = {
						'ACL': 'public-read',
						'ContentType': content_type,
						'ContentDisposition': 'inline'  # Force inline viewing instead of download
					}
					
					# Add ExtraArgs to set ACL to public-read and proper content headers
					s3.upload_file(
						str(file_path), 
						bucket_name, 
						s3_key,
						ExtraArgs=extra_args
					)
				except Exception as e:
					print(f" Failed to upload {relative_path}: {e}")
					delete_files = False  # Prevent deletion if any upload fails
			
			# Optionally delete local files after successful sync
			if delete_files:
					# Archive brochures pdfs to separate folder
					if s3_prefix == 'listings/':
						archive_path = 'F:\\Research Department\\Code\\AWS_Upload\\Listings Archive\\'
						try:
							pdf_file_name = path.basename(file_path)
							print(f"🗑️ Archiving: {pdf_file_name}")
							
							archive_file_path = '{0}\\{1}'.format(archive_path, pdf_file_name)
							shutil.move(file_path, archive_file_path)
						except Exception as e:
							td.warningMsg(f" Failed to archive {file_path}: {e}")
					elif s3_prefix == 'maps/':
						try:
							map_file_name = path.basename(file_path)
							print(f"🗑️ Deleting: {map_file_name}")
							remove(file_path)
						except Exception as e:
							td.warningMsg(f" Failed to delete {file_path}: {e}")

						

	print("\n Sync complete!")