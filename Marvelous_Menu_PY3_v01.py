#! python3


import bb
from lao import *
from os import system, environ
import shutil
import socket
import sys
import fun_text_date as td

def runApp(filename):
	system(filename)
	uInput('\n [Enter] to return to menu...')

def printMenu(menu):
	banner('                      The Marvelous Menu Code PY3 v01                         ')

	# Load MM database
	dMM = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/Marvelous_Menu_Db_PY3.xlsx')
	for row in dMM:
		d = dMM[row]
		title = d['Title']
		if menu == d['Menu']:
			if d['Index'] == 'None':
				if title == 'Blank Line':
					print()
				elif title == 'Dash Line':
					print(dashline)
				else:
					print(f' {title}')
			elif d['PY Version'] == 'None':
				idx = int(d['Index'])
				print(f' [{idx:2d}] {title}')
			elif d['PY Version'] == 'PY2':
				idx = int(d['Index'])
				print(f' [{idx:2d}] {title}')
			elif d['PY Version'] == 'PY3':
				idx = int(d['Index'])
				# print(f' [{idx:2d}] {title}')
				td.colorText(f' [{idx:2d}] {title}', 'CYAN')
			elif d['PY Version'] == 'AP3':
				idx = int(d['Index'])
				# print(f' [{idx:2d}] {title}')
				td.colorText(f' [{idx:2d}] {title}', 'GREEN')
	print(f'{dashline}\n [00] Quit')
	ui = uInput('\n Enter Selection > ')
	return ui

def getFileName(menu, index):
	# Exit program or return to Main menu
	if index == '00':
		if user in lFull_users and menu != 'Main':
			return 'Main', 'None'
		exit('\n Program terminated...')

	# Load MM database
	dMM = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/Marvelous_Menu_Db_PY3.xlsx')
	for row in dMM:
		d = dMM[row]
		# Skip 'None' index values
		if d['Index'] == 'None':
			continue
		elif menu == d['Menu'] and index == str(int(d['Index'])):
			return d['File'], d['PY Version']
			# Determine Python version and get appropriate path

	td.warningMsg('\n Invalid input...try again...')
	sleep(2)
	return 'None', 'None'

def build_path_filename():
	if py_version == 'PY2': # Python 2
		pypath = 'C:/Python27/ArcGIS10.8/python.exe "F:/Research Department/Code/Research/'
	elif py_version == 'PY3': # Python 3
		# pypath = 'C:/"Program Files"/Python312/python.exe F:/"Research Department"/scripts/Projects/RP3/'
		pypath = 'C:/"Program Files"/Python312/python.exe F:/"Research Department"/Code/RP3/'
	elif py_version == 'AP3': # ArcPy 3
		# pypath = 'C:/"Program Files"/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe F:/"Research Department"/scripts/Projects/RP3/'
		pypath = 'C:/"Program Files"/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe F:/"Research Department"/Code/RP3/'
	filename = f'{pypath}{python_script}'
	return filename

td.console_title('MM')
# Define Variables
user = getUserName()

TFpath = 'https://landadvisors.my.salesforce.com/'
llrpath = 'F:/scripts/'
dashline = '-' * 86

# Set menu based on user
lFull_users = ['blandis', 'avidela', 'mklingen']
if user in lFull_users:
	menu = 'Main'
else:
	menu = 'Comps'

while True:
	index = printMenu(menu)
	if index == '':
		continue
	# Select a menu item from the Main menu
	if int(index) <= 10 and menu == 'Main':
		menu, py_version = getFileName(menu, index)
		continue
	# Get the script name and which version of Python to run
	else:
		python_script, py_version = getFileName(menu, index)

	# Return to Main menu if 'Main' is returned
	if python_script == 'Main':
		menu = 'Main'
	elif python_script == 'None':
		continue
	# Run the selected script
	else:
		filename = build_path_filename()
		runApp(filename)

