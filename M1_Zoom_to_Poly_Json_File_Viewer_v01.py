# Views the Zoom to Poly Json file scripts

from datetime import datetime
import fjson
import lao
import fun_text_date as td
import os
from pprint import pprint

def print_dic_elements(d, title):
	print(f'\n {title} : {mod_datetime}')
	print('-' * 40)
	for key in d:
		print(f' {key:<20}: {d[key]}')
	print('-' * 40)


user = lao.getUserName()
td.banner('M1 Zoom to Poly Json File Viewer')
# Public Mapfiles path
path = lao.getPath('m1_files')

# Json files in the Public Mapfiles M1_Files folder
dJson_files = {
		'Zoom to Polygon': 'zoomToPolygon.json',
		'PIDOID': 'PIDOID.json',
		'M1 Parameters': 'M1_params.json',
		'Arc Make PID From Parcel Ownerinfo': 'ArcMakePIDFromParcelOwnerInfo.json'		
}

for key in dJson_files:
	file_path = f'{path}{dJson_files[key]}'
	dZoom_to_Poly = fjson.getJsonDict(file_path)
	mod_time = os.path.getmtime(file_path)
	mod_datetime = datetime.fromtimestamp(mod_time)
	print_dic_elements(dZoom_to_Poly, key)