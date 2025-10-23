# Instructions for LAO scripts

import fun_text_date as td

# AxioMetric MO_Axio_MF_Data_v## Instructions
def axio_intro():
	import lao
	import fun_text_date as td
	lao.banner('MO Axio MF Data')
	td.instrMsg(' INSTRUCTIONS\n\n')
	msg = \
		' 1) Open AxioMetrics website and login.\n' \
		' 2) Select Publications in top menu\n' \
		' 3) Select Market Supply and Demand Model\n' \
		' 4) Download each market individually and save\n' \
		'     Path:  F:/Research Department/MIMO/zData/AxioMetrics/\n' \
		'     Name:  [MRKT] Market Supply & Demand 20YYQ#.xlsx\n'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')


# AxioMetric MO_Axio_MF_Data_v## Instructions
def axio_exit():
	import lao
	import fun_text_date as td
	lao.banner('MO Axio MF Data')
	td.instrMsg('\n Copy to MIMO Spreadsheet\n')
	td.warningMsg('\n   Copy to spreadsheet')
	td.colorText('   Worksheet: MF (purple)', 'PURPLE')
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

def zonda_top_builder_formater():
	import lao
	import fun_text_date as td
	msg = \
		' INSTRUCTIONS\n' \
		' ---------------------------------------------\n' \
		' Download the Quaterly Activity by Builder PDF report for each market.\n' \
		'    Reports > Builder Analysis > Quaterly Activity by Builder\n\n' \
		' Save the PDF to: F:\Research Department\MIMO\zData\Metrostudy\n\n' \
		' Special Markets that require additional formatting:\n' \
		'    Inland Empire Counties (Southern California):\n' \
		'      San Bernardino, Riverside\n' \
		'    Sacramento MSA Counties (Northern California):\n' \
		'      El Dorado, Placer, Sacramento, Sutter, Yolo, Yuba\n'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')


def zonda_top_MPC_formater():
	import lao
	import fun_text_date as td
	msg = \
		' INSTRUCTIONS\n' \
		' ---------------------------------------------\n' \
		'\n 1) Go to Zonda > Housing Analysis > Select Market' \
		'\n 2) Set Builtout Same Quarter of Last Year' \
		'\n 3) Uncheck Future' \
		'\n 4) Click Update' \
		'\n 5) Select Reports > Survey Details > Current Activity and Profile' \
		'\n 6) Save Excel file to {0}' \
		'\n       File Name: [MKT]_subs_[YYYYQQ].csv'.format(lao.getPath('metstud')) 
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')


# Zonda MPC Name formatting instructions
def zonda_merger_merger():
	import lao
	import fun_text_date as td
	msg = \
		'\n 1) Open L5 to the market you want\n' \
		'\n 2) Go to Layers and turn on\n' \
		'      Homebuilder Data > ZondaProjects\n' \
		'\n 3) Zoom out to entire market\n' \
		'\n 4) Choose the Indetify > Rectangle tool\n' \
		'\n 5) Draw a selection box around all of the Zonda data\n' \
		'\n 6) Click the 3 dot next to the ZondaProjects selection in the left menu and Export to CSV\n' \
		'\n 7) Save csv to zData/Zonda folder\n\n'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')


# Data for Annual Sales per Active Subdiviion MO Maps
def zonda_active_sub_csv_builder_for_arcmap():
	import lao
	import fun_text_date as td
	lao.banner('MO Zonda Active Sub CSV Builder For ArcMap v01')
	msg = \
	' 1) Download/Export the MetroStudy > Housing Analysis for each market' \
	'\n    - Export Settings' \
	'\n      -------------------------------------------' \
	'\n      Built Out 4 quarter ago' \
	'\n      Uncheck Builtout' \
	'\n      Uncheck Future' \
	'\n      Click Update' \
	'\n\n 2) Run Report & Save' \
	'\n    - Save Settings' \
	'\n      -------------------------------------------' \
	'\n      Select Reports > Survey Details > Current Activity & Profile' \
	'\n      Save as XLS' \
	'\n      Save to folder F:/Research Department/MIMO/zData/Metrostudy/' \
	'\n      Save file as "[market]_subs_YYYYQ#.xls' \
	'\n\n 3) AcrMap open:' \
	'\n      F:/Research Department/map/MO LAHF MXDs/' \
	'\n        MO Blank for MS Active Sub Geo.mxd' \
	'\n\n 4) Display XY data:' \
	'\n      Add data to Layer (right click):' \
	'\n      F:/Research Department/maps/Active Subs/' \
	'\n        MS_Active_Subs.csv' \
	'\n      Display XY to add points based on lon lat.' \
	'\n      Export & overwrite new point file to:' \
	'\n        F:/Research Department/maps/Active Subs/'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

# Create csv of annual permits by MSA
def mo_census_permits_msa_extractor():
	import lao
	import fun_text_date as td
	lao.banner('MO Census Permits MSA Extractor v02')
	msg = \
	' This script extracts annual permits by MSA into a table based on csv files from' \
	'\n    the Census.  A new csv file needs to be created once the annual permits Excel' \
	'\n    file is published by the Census at:' \
	'\n    https://www.census.gov/construction/bps/msamonthly.html' \
	'\n    To the folder:' \
	'\n    F:/Research Department/MIMO/zData/Census Permits by MSA' \
	'\n\n    Years: 1995 - 2022'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')


# Get info for the MO PHX MPC Slide Calculator
def mo_phx_mpc_slide_calculator():
	import lao
	import fun_text_date as td
	lao.banner('MO Census Permits MSA Extractor v02')
	msg = \
	' This script extracts calculates the Permits, COE & Sale Price Range for major' \
	'\n Phoenix MPCs listed in the MO Major Master Plan Community slide.\n' \
	'\n    QUERY DATA' \
	'\n    1) Open L5 for Phoenix' \
	'\n    2) Turn on Homebuilder Data > ZondaProjects layer' \
	'\n    3) Select the Query button' \
	'\n    4) Set Data Source as ZondaProjects' \
	'\n    5) Set Map Area to All' \
	'\n    6) Set field to Sales Rate > 0' \
	'\n    7) Select Search' \
	'\n    8) Select the 4 Bar icon and select Export to CSV' \
	'\n    8) Save the CSV to:' \
	'\n       Folder:    F:/Research Department/zData/Zonda/' \
	'\n       File Name: Zonda L5 Major MPC Data YYYY-MM.csv\n' \
	'\n\n  RUN SCRIPTS' \
	'\n    1) Run MO Homebuilder MPC Merger Merger to clean/standardize the MPC names' \
	'\n    2) Run MO PHX MPC Slide Calculator to get the MPC info' \
	'\n    1) Copy info into the slide'
	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

# BLS data
def bls_data():
	import lao
	import fun_text_date as td
	td.banner('MIMO BLS API Employment Assembler v02')
	msg = \
	' This script extracts calculates BLS data for Employment and Unemployment LAO' \
	'\n markets.\n' \
	'\n    SOURCE REFERENCES' \
	'\n    BLS API Series ID Site' \
	'\n      Series IDs are the codes that identify the state and area (MSA) and data to pull' \
	'\n      https://www.bls.gov/help/hlpforma.htm#LA' \
	'\n' \
	'\n    BLS API INSTRUCTIONS' \
	'\n      https://www.bls.gov/developers/api_python.htm' \

	print(msg)
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
