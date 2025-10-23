#! python3


import bb
import dicts
from lao import *
from os import system, environ
import shutil
import socket
import sys

def runApp(filename):
	print(pypath)
	
	system('{0}{1}'.format(pypath, filename))
	uInput('\n [Enter] to return to menu...')

def printMenu(menu):
	banner('                      The Marvelous Menu AWS v01                         ')
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
			else:
				idx = int(d['Index'])
				print(f' [{idx:2d}] {title}')
	print(f'{dashline}\n [00] Quit')
	ui = uInput('\n Enter Selection > ')
	return ui

def getFileName(menu, index):
	if index == '00':
		if user == 'blandis' and menu != 'Main':
			return 'Main'
		exit('\n Program terminated...')
	for row in dMM:
		d = dMM[row]
		if d['Index'] == 'None':
			continue
		elif menu == d['Menu'] and index == str(int(d['Index'])):
			return d['File']
	warningMsg('\n Invalid input...try again...')
	sleep(2)
	return 'None'

# Define Variables
user = getUserName()
pypath = 'C:/"Program Files"/Python312/python.exe F:/"Research Department"/scripts/Projects/RP3/'
TFpath = 'https://landadvisors.my.salesforce.com/'
llrpath = 'F:/scripts/'
dMM = dicts.spreadsheet_to_dict('F:/Research Department/Code/RP3/Marvelous_Menu_Db_PY3.xlsx')
dashline = '-' * 86
if user == 'blandis' or user == 'avidela':
	menu = 'Main'
else:
	menu = 'Comps'

# Move terminal window for Bill
if user == 'blandis':
	consoleWindowPosition(position='Bill Marvelous Menu')

while True:
	index = printMenu(menu)
	if int(index) <= 3 and menu == 'Main':
		menu = getFileName(menu, index)
		continue
	else:
		filename = getFileName(menu, index)
	if filename == 'Main':
		menu = 'Main'
	elif filename == 'None':
		continue
	else:
		runApp(filename)

