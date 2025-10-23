# Prints as list of the Marvelous Menu python script files

import fun_text_date as td
import lao
from os import startfile

def printmenu():
	while 1:
		lao.banner('Marvelous Menu Script File List PY3')
		print('  1) Main\n\n  2) Comps\n\n  3) MailChimp\n\n  4) MIMO\n\n  5) Data\n\n 6) Open Excel file of scripts\n\n 00) Quit')
		ui = td.uInput('\n Select a Category > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			cat = 'Main'
			break
		elif ui == '2':
			cat = 'Comps'
			break
		elif ui == '3':
			cat = 'MailChimp'
			break
		elif ui == '4':
			cat = 'MIMO'
			break
		elif ui == '5':
			cat = 'Data'
			break
		elif ui == '6':
			print('\n Opening Excel File...')
			startfile('F:/Research Department/Code/Databases/Marvelous_Menu_Db_PY3.xlsx')
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)
	return cat

dScripts = lao.spreadsheetToDict('F:/Research Department/Code/Databases/Marvelous_Menu_Db_PY3.xlsx')

while 1:
	cat = printmenu()
	print(cat)
	lao.banner('Marvelous Menu Script File List PY3')
	print(' {0:2}   {1:50} {2}'.format('Index', 'Title', 'File'))
	for script in dScripts:
		row = dScripts[script]
		if row['Menu'] == cat:
			if row['Index'] == 'None':
				if row['Title'] == 'Dash Line':
					print
					print(' {0}'.format('-'*100))
				continue
			print('\n {0:2}   {1:50} {2}'.format(int(row['Index']), row['Title'], row['File']))

	lao.holdup()
