
import aws
import csv
import lao
import fjson
import fun_text_date as td
import mpy
from pprint import pprint

def get_pid_dic():
	dPIDs = {
		'Central Mesa': 'AZMS00951',
		'Pinal County': 'AZPL00791',
		'Tucson': 'AZPima272351',
		'Yuma': 'AZYuma176688',
		'Las Vegas': 'NVClark213452',
		'Flagstaff': 'AZCoconino266576',
		'Prescott': 'AZYV00889',
		'Boise': 'IDAda258278',
		'Salt Lake City': 'UTSaltLake191467',
		'Denver': 'CODenver266504',
		'Kansas City': 'KSJohnson251505',
		'Nashville': 'TNDavidson245524',
		'Huntsville': 'ALMadison259599',
		'Atlanta': 'GADeKalb221403',
		'Charlotte': 'NCMecklenburg208715',
		'Greenville': 'SCGreenville207647',
		'DFW': 'TXDallas277334',
		'Austin': 'TXTR00599',
		'Houston': 'TXBrazoria191191',
		'Jacksonville': 'FLDuval225180',
		'Orlando': 'FLOrange266701',
		'Tampa': 'FLHillsborough188596'}
	
	return dPIDs

def timer():
	import time
	start_time = time.time()
	print(' Timer started...')
	ui = td.uInput('\n [Enter] to stop [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	else:
		print(' Timer stopped...')
		elapsed_time = round(time.time() - start_time)  # Round to nearest whole second
		
		return elapsed_time

def view_json_file(filename, file_location='local'):
	td.banner('M1 JSON File Viewer v01')
	
	if file_location == 'local':
		print(f'\n File location: {M1_folder_local}')
		d = fjson.getJsonDict(f'{M1_folder_local}/{filename}')
	elif file_location == 'network':
		print(f'\n File location: {M1_folder_network}')
		d = fjson.getJsonDict(f'{M1_folder_network}/{filename}')
	
	print(f' Viewing {filename}...\n')
	pprint(d)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

def test_zoom_to_poly(dPIDs):
	td.banner('M1 Zoom To Poly Test')
	print(' Testing Zoom to Polygon...\n')

	today_date = td.today_date(dateformat='slash', include_time=False)

	with open(M1_display_log, 'a', newline='') as f:
		fout = csv.writer(f)
	
		for market in dPIDs:
			PID = dPIDs[market]
			mpy.create_zoomToPolygon_json_file(fieldname='pid', polyId=PID, polyinlayer='OwnerIndex', lon=None, lat=None, market=None)
			print(f'\n Market: {market}')
			print(f' PID:    {PID}')
			elapsed_time = timer()
			print(f' Elapsed time: {elapsed_time} seconds')

			comment = td.uInput('\n Enter comment [00]... > ')
			if comment == '00':
				lao.openFile(M1_display_log)
				exit('\n Terminating program...')

			fout.writerow([today_date, market, PID, elapsed_time, comment])
			
			

M1_folder_local = r'C:\Users\Public\Public Mapfiles\M1_Files'
M1_folder_network = r'F:\Research Department\Code\M1 Json Files'
M1_display_log = r'F:\Research Department\Code\Databases\M1 Display Time Log.csv'
dPIDs = get_pid_dic()

while 1:
	td.banner('M1 JSON File Viewer v01')
	# User choose input file
	print('\n View JSON Files')
	print('  1) Zoom to Polygon')
	print('  2) Arc Map PID from Parcel OwnerInfo')
	print('  3) PID OID')
	print('  4) M1 Params Local C Drive')
	print('  5) M1 Params Network F Drive')

	print('\n M1 Testing')
	print('  6) Test Zoom to Poly')
	print(' 00) Quit')

	ui = td.uInput('\n Select > ')

	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		view_json_file('zoomToPolygon.json')
	elif ui == '2':
		aws.get_m1_file_copy(action='DOWN')
		view_json_file('ArcMakePIDFromParcelOwnerInfo.json')
	elif ui == '3':
		aws.get_m1_file_copy(action='DOWN')
		view_json_file('PIDOID.json')
	elif ui == '4':
		view_json_file('m1_params.json', 'local')
	elif ui == '5':
		view_json_file('m1_params_blandis.json', 'network')
	elif ui == '6':
		test_zoom_to_poly(dPIDs)
		

	

