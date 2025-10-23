import lao
import fun_text_date as td

# Create ArcMap Zoom to Polygon Json file
def create_ZoomToPolygon_json_file(fieldname=None, polyId=None, polyinlayer=None, lon=None, lat=None, market=None):
	from aws import get_m1_file_copy
	import json
	import fun_text_date as td
	# lao.print_function_name('fjson def create_ZoomToPolygon_json_file')
	
	# Get market from apn polyinlayer
	if fieldname == 'apn' and polyinlayer != None and market == None:
		county = polyinlayer[9:]
		dCounty = lao.getCounties('FullDict')
		for row in dCounty:
			if county == dCounty[row]['ArcName']:
				market = dCounty[row]['Market']
				break
				
	# Add trailing zero to Tucson parcels if needed
	if market == 'Tucson' and fieldname == 'apn':
		if len(polyId) == 10:
			polyId = '{0}0'.format(polyId)

	# Make dict
	d = {}
	d['zoomquery'] = "{0} in ('{1}')".format(fieldname, polyId)
	d['fieldName'] = fieldname
	d['polyId'] = polyId
	d['layer'] = polyinlayer
	d['lon'] = lon
	d['lat'] = lat
	d['market'] = market

	# Save json file
	with open('C:/Users/Public/Public Mapfiles/zoomToPolygon.json', 'w') as f:
		json.dump(d, f)
	with open('C:/Users/Public/Public Mapfiles/M1_Files/zoomToPolygon.json', 'w') as f:
		json.dump(d, f, indent=4)

	get_m1_file_copy(action='UP')

# Create new OwnerIndex or Lead json file version 3
def make_new_OwnerIndex_Lead_json_file(action, salePID=None, leadPID=None, islotoption=False, polyIndex=0):
	import json
	from ftime import dateTimeNowString
	# lao.print_function_name('fjson def create_opr_map_json_file')

	user = lao.getUserName().lower()
	initials = user[:2].upper()
	d = {}
	d['action'] = action
	d['islotoption'] = islotoption
	d['salePID'] = salePID
	d['leadPID'] = leadPID
	d['initials'] = initials
	d['dateupdated'] = td.today_date(dateformat='slash', include_time=False)
	d['polyIndex'] = polyIndex

	jsonFile = 'C:/TEMP/make_lead_pid_data_{0}.json'.format(dateTimeNowString('jsonFileExtention'))
	with open(jsonFile, 'w') as f:
		json.dump(d, f)

# Create json file for OPR Maps
def create_opr_map_json_file(PID=None, save_folder='global'):
	from json import dump
	from amp import getMarketAbbreviation
	from bb import sfLogin, getLeadDealData
	import fun_login
	# lao.print_function_name('fjson def create_opr_map_json_file')

	user = lao.getUserName().lower()
	
	# Get PID from user if none given from Marv Menu
	if PID == None:
		from lao import uInput
		PID = uInput('\n\n Enter PID for OPR Map > ')
		
	service = fun_login.TerraForce()
	
	market = getLeadDealData(service, PID, dealVar='Market')
	
	marketAbb, stateAbb = getMarketAbbreviation(market)

	d = {}
	d['PID'] = PID
	d['market'] = market
	d['marketAbb'] = marketAbb
	d['stateAbb'] = stateAbb
	
	if save_folder == 'global':
		jsonFile = 'F:/Research Department/Code/AWS_Upload/OPR Maps/OPRMap_{0}.json'.format(PID)
	elif save_folder == 'local':
		jsonFile = 'C:/Users/Public/Public Mapfiles/OPRMap_{0}.json'.format(PID)

	with open(jsonFile, 'w') as f:
		dump(d, f)

def createScriptToLauchFile(scriptPath, arguements='None'):
	from json import dump
	# lao.print_function_name('fjson def createScriptToLauchFile')
	d = {'scriptPath': scriptPath,
	  	'arguements': arguements}
	jsonFile = 'C:/Users/Public/Public Mapfiles/python_script_to_launch.json'
	with open(jsonFile, 'w') as f:
		dump(d, f)

def create_tf_contact_entry_file(name):
	from json import dump
	# lao.print_function_name('fjson def createScriptToLauchFile')
	d = {'name': name}
	jsonFile = 'C:/Users/Public/Public Mapfiles/M1_Files/tf_contact_entry.json'
	with open(jsonFile, 'w') as f:
		dump(d, f)

# Saves a dict as a json file
def getJsonDict(jsonFile):
	from json import load
	# lao.print_function_name('fjson def getJsonDict')
	with open(jsonFile, 'r') as g:
		d = load(g)
	return d

def save_dict_to_json_file(data, filepath=None):
	from json import dump

	if filepath is None:
		jsonfile = 'C:/TEMP/temp.json'
	else:
		jsonfile = filepath

	with open(jsonfile, 'w', encoding='utf-8') as f:
		dump(data, f, indent=4, ensure_ascii=False)

# Get and make an sequencial index number to attach to temp Arc FCs
def getPolyIndex():
	import json
	from os import path
	# lao.print_function_name('fjson def getJsonDict')

	# polyIndexFile = 'C:/TEMP/polyIndex.json'
	polyIndexFile = lao.getPath('mapfiles')
	# If polyIndex.json file exits, open it, get polyIndex number, write new file
	#   with +1 added to old polyIndex
	if path.exists(polyIndexFile):
		with open(polyIndexFile, 'r') as f:
			d = json.load(f)
			polyIndex = d['polyIndex']

		# Cycle back to 1 if the polyIndex number is greater than 98
		if polyIndex > 499:
			newpolyIndex = 1
		else:
			newpolyIndex = polyIndex + 1
		d = {'polyIndex': newpolyIndex}
		with open(polyIndexFile, 'w') as f:
			json.dump(d, f)
	# Create the polyIndex.json file if it does not exist
	else:
		polyIndex = 1
		d = {'polyIndex': 2}
		with open(polyIndexFile, 'w') as f:
			json.dump(d, f)
	
	return polyIndex

# Make the json file for creating a PID on the service
def makeNewOIPolyJsonFile(layername='None', parcels='None', PID='None', action='Make New OI Poly from Parcels', parcelfield='apn', runASW=True):
	# Actions: Make New OI Poly from Parcels, Delete Poly
	from json import dump
	# lao.print_function_name('fjson def makeNewOIPolyJsonFile')

	user, initials = lao.getUserName(initials=True)
	j = {'action': action,
		'dateupdated': td.today_date(dateformat='slash', include_time=False),
		'initials': initials,
		'layername': layername.upper(),
		'parcelfield': parcelfield,
		'parcels': parcels,
		'pid': PID
		}
	with open('C:/Users/Public/Public Mapfiles/Arc_Make_OwnerIndex_Parms.json', 'w') as f:
		dump(j, f)
	if runASW:
		from os import system
		system('C:/Users/blandis/AppData/Local/Programs/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe "F:/Research Department/Code/Research/Arc_AWS_v01.py"')

# Read the bill script messages on off json file
def read_bill_script_msgs_on_off(msg_type='Dict'):
	from json import load

	if lao.getUserName() != 'blandis':
		return 'Off'
	json_file = '{0}bill_script_msgs_on_off.json'.format(lao.getPath('py3Data'))
	with open(json_file, 'r') as f:
		dMsgs = load(f)
	if msg_type == 'Banner':
		return dMsgs['Banner']
	elif msg_type == 'Functions':
		return dMsgs['Functions']
	elif msg_type == 'Dict':
		return dMsgs

# Make a json file of jpeg files in the AWS OPR Maps folder
def make_aws_opr_maps_jpeg_file_list():
	import json
	from datetime import datetime
	import boto3
	from botocore import UNSIGNED
	from botocore.config import Config


	"""
	Creates a JSON file inventory of all JPEG files in s3://request-server/maps/
	"""
	# Initialize S3 client
	s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
	
	bucket = 'request-server'
	prefix = 'maps/'
	
	print(f"Listing objects from s3://{bucket}/{prefix}...")
	
	# List all objects with pagination
	paginator = s3.get_paginator('list_objects_v2')
	pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
	
	jpeg_files = []
	total_objects = 0
	
	for page in pages:
		if 'Contents' not in page:
			continue
			
		for obj in page['Contents']:
			total_objects += 1
			key = obj.get('Key', '')
			
			# Filter for JPEG files
			if key.lower().endswith(('.jpg', '.jpeg')):
				jpeg_files.append({
					'key': key,
					'size': obj.get('Size'),
					'last_modified': obj.get('LastModified').isoformat() if obj.get('LastModified') else None,
					'etag': obj.get('ETag', '').strip('"')
				})
	
	print(f"Total objects scanned: {total_objects}")
	print(f"JPEG files found: {len(jpeg_files)}")
	
	# Create inventory structure
	inventory = {
		'bucket': bucket,
		'prefix': prefix,
		'generated': datetime.now().isoformat(),
		'total_objects_scanned': total_objects,
		'total_jpegs': len(jpeg_files),
		'files': jpeg_files
	}
	
	# Write to JSON file
	output_file = r'F:\Research Department\Code\Databases\maps_jpeg_inventory.json'
	with open(output_file, 'w') as f:
		json.dump(inventory, f, indent='\t')
	
	print(f"\nCreated {output_file}")
	return output_file

