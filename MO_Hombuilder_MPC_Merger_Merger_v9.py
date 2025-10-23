
#! python3

# Merges RL Brown builder names from COE & Permit Exports

import lao
import csv
import dicts
import fun_text_date as td
from glob import glob
import how
import mpy
from pprint import pprint
import shutil

import xlwings as xw
import xxl


# Make No Name Found List csv
def make_no_name_found_csv():
	fRLB_No_Name = '{0}RLB No Name Found List.csv'.format(lao.getPath('rlb'))
	with open(fRLB_No_Name, 'w', newline='') as f:
		fTemp = csv.writer(f)
		fTemp.writerow(['BUILDER', 'UPPER'])
	return fRLB_No_Name

# Choose RLB or Zonda file
def chooseSourceFile():
	while 1:
		lao.banner('Homebuilder & MPC Merger Merger v09 (RLB Zonda MetroStudy)')
		# Choose RLB or Zonda to format
		msg = \
			 ' Choose source\n\n' \
			 ' 1) RL Brown Homebuilders & MPC (COE & Permits)\n\n' \
			 ' 2) Zonda MPCs from L5 download\n\n' \
			 ' 3) MetroStudy Homebuilders\n\n' \
			 ' 00) Quit'
		print(msg)
		ui = td.uInput('\n > ')
		lao.banner('Homebuilder & MPC Merger Merger v09 RL BROWN')
		if ui == '1':
			infile = lao.guiFileOpen(path=lao.getPath('rlb'), titlestring='RLB COE or Permits', extension=[('COE Files', 'RLB*COE*20*.csv'), ('Permit Files', 'RLB*Permits*20*.csv'), ('csv files', '.csv'), ('all files', '.*')])
			outfile = infile.replace('.csv', ' KEY CLEANED.csv')
			if 'COE' in infile.upper():
				dataSource = 'RLB COE'
			else:
				dataSource = 'RLB PERMITS'
			file_cant_find = 'C:/TEMP/file_cant_find.csv'
			return infile, outfile, dataSource #, file_cant_find
		elif ui == '2':
			lao.banner('Homebuilder & MPC Merger Merger v09 ZONDA')
			how.zonda_merger_merger()
			infile = lao.guiFileOpen(lao.getPath('zonda'))
			outfile = infile.replace('.csv', ' MPCS CLEANED.csv')
			dataSource = 'Zonda'
			return infile, outfile, dataSource
		elif ui == '3':
			lao.banner('Homebuilder & MPC Merger Merger v09 METROSTUDY')
			dataSource = 'MetroStudy'
			return 'None', 'None', dataSource
		elif ui == '00':
			exit('\n Fin')
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)

def cleanName(txt):
	txt = txt.strip()
	txt = txt.upper()
	return txt

# Get RLB data
def getRLBData(rec):
	# Change RLB Product codes to words
	if rec['PRODCODE'].strip() == 'A':
		rec['PRODCODE'] = 'Attached'
	elif rec['PRODCODE'].strip() == 'B':
		rec['PRODCODE'] = 'Detached'
	elif rec['PRODCODE'].strip() == 'C':
		rec['PRODCODE'] = 'Adult'
	elif rec['PRODCODE'].strip() == 'D':
		rec['PRODCODE'] = 'Custom'
	
	# Trap non-negative longitude values
	float_lon = float(rec['LONGITUDE'])
	if float_lon > 0:
		rec['LONGITUDE'] = str(float_lon * -1)
	# if float(rec['LONGITUDE']) > 0:
	# 	rec['LONGITUDE'] = str(float(rec['LONGITUDE'] * -1))

	# Rename Builders
	rlbBuilderName = cleanName(rec['BUILDER'])
	didNotFindRename = True
	for rename in dBuilderRename:
		db_rename_formatted = cleanName(dBuilderRename[rename]['BUILDER'])
		if rlbBuilderName == db_rename_formatted:
			rec['BUILDER'] = dBuilderRename[rename]['RENAME']
			didNotFindRename = False
			break
	
	if didNotFindRename:
		rlbBuilderNameTitle = rlbBuilderName.title()
		rlbBuilderNameTitle = rlbBuilderNameTitle.replace('Llc', '')
		rlbBuilderNameTitle = rlbBuilderNameTitle.replace('Development', 'Dev') 
		with open(fRLB_No_Name, 'a', newline='') as fnoname:
			fout = csv.writer(fnoname)
			fout.writerow([rlbBuilderName, rlbBuilderNameTitle])

	# Rename MPCs basd on MASTERPLAN field
	rlb_MPC_name = rec['MASTPLAN']
	try:
		rlb_sub_name = rec['SUBDIVISION']
		sub_key = 'SUBDIVISION'
	except KeyError:
		rlb_sub_name = rec['SUBDIVISIN']
		sub_key = 'SUBDIVISIN'
	
	not_replaced = True
	for row in dMPC_Rename:
		# Assign db MPC name to variable
		db_MPC_name = dMPC_Rename[row]['MPC']
		db_MPC_rename = dMPC_Rename[row]['RENAME']

		# Check if rlb MPC name matches db MPC name and replace if True
		if rlb_MPC_name == db_MPC_name:
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		# Else check if rlb sub name matches db MPC name and replace if True
		elif db_MPC_name == rlb_sub_name:
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		# Check if rlb MPC name matches db MPC name and replace if True
		elif rlb_MPC_name.upper() == db_MPC_name.upper():
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		# Else check if rlb sub name matches db MPC name and replace if True
		elif db_MPC_name.upper() in rlb_sub_name.upper():
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		elif db_MPC_name.upper() in rlb_sub_name.upper():
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		elif db_MPC_rename.upper() in rlb_sub_name.upper():
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break
		elif db_MPC_rename.upper() in rlb_sub_name.upper():
			rec['MASTPLAN'] = dMPC_Rename[row]['RENAME']
			not_replaced = False
			break

	lLine = list(rec.values())
	# Add KEYID
	if 'COE' in infile:
		lDate = rec['DATE'].split('/')
		mo = lDate[0].rjust(2, '0')
		day = lDate[1].rjust(2, '0')
		yr = lDate[2]
		keyid = 'KEY-{0}-{1}-{2}-{3}-{4}'.format(rec['ADDRESS'], rec['PARTYPE'], mo, day, yr)
	elif 'Permits' in infile:
		lDate = rec['PERMIT DATE'].split('/')
		mo = lDate[0].rjust(2, '0')
		day = lDate[1].rjust(2, '0')
		yr = lDate[2]
		keyid = 'KEY-{0}-{1}-{2}-{3}-{4}'.format(rec['ADDRESS'], rec['PERMIT NUM'], mo, day, yr)
	lLine.append(keyid)
	return lLine

# Get Zonda data
def getZondaData(rec):
	# Rename MPCs
	# pprint(rec)
	
	zonda_MPC_Name = rec['master_plan'].strip()
	zonda_Project_Name = rec['project_name'].strip()

	
	# zonda_MPC_Name = zonda_MPC_Name.upper()
	# if zonda_MPC_Name != '':
	print(' START')
	print(' Zonda MPC Name: {0}'.format(zonda_MPC_Name))
	# if zonda_MPC_Name == 'Sonoran Foothills':
	# 	print( ' Sonoran Foothills ZONDA')
	# Cycle through MPC database
	for rename in dMPC_Rename:
		foundit = False
		db_MPC_Name = dMPC_Rename[rename]['MPC'].strip()
		db_MPC_Rename = dMPC_Rename[rename]['RENAME'].strip()
		# Check db MPC to Zonda Project
		# Check db MPC to Zonda MPC
		if db_MPC_Name == zonda_MPC_Name:
			rec['master_plan'] = db_MPC_Rename
			break
		# Check db MPC to Zonda MPC Upper
		elif db_MPC_Name == zonda_MPC_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break
		# Check db MPC to Zonda MPC Upper
		elif db_MPC_Name.upper() == zonda_MPC_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break
		elif db_MPC_Name in zonda_Project_Name:
			rec['master_plan'] = db_MPC_Rename
			break
		# Check db MPC to Zonda Project Upper
		elif db_MPC_Name in zonda_Project_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break
		# Check db MPC to Zonda Project Upper
		elif db_MPC_Name.upper() in zonda_Project_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break
		elif db_MPC_Rename.upper() in zonda_MPC_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break
		elif db_MPC_Rename.upper() in zonda_Project_Name.upper():
			rec['master_plan'] = db_MPC_Rename
			break

	lLine = rec.values()
	return lLine

# Process MetroStudy Homebuilders
def processMetroStudyHomebuilders():
	# Read xlsx into list lSheet
	curqtr = lao.getDateQuarter(lastquarter=True)
	#curqtr = '2022Q3'
	inFiles = glob('F:/Research Department/MIMO/zData/Metrostudy/*builders{0}.xls'.format(curqtr))
	with open('C:/TEMP/TempNotInHBDict.csv', 'w', newline='') as f:
		fout = csv.writer(f)
		openfile = False
		for file in inFiles:

			print
			print(file)
			
			hbNotInHBDict = True
			wb = xw.Book(file)
			outfile = file.replace('.xls', ' BUILDERS CLEANED.xls')
			sht = wb.sheets('BA_RankXBuilder')
			noRows = xxl.getNumberRows(sht)
			# Cycle through the MetroStudy sheet
			for i in range(3, noRows):
				msBuilderName = cleanName(sht.range('C{0}'.format(i)).value)
				for rename in dBuilderRename:
					db_rename_formatted = cleanName(dBuilderRename[rename]['BUILDER'])
					if msBuilderName == db_rename_formatted:
						sht.range('C{0}'.format(i)).value = dBuilderRename[rename]['RENAME']
						hbNotInHBDict = False
						break
				if hbNotInHBDict:
					fout.writerow([file, msBuilderName])
					openfile = True
			wb.save(outfile)
			wb.close()
	if openfile:
		lao.openFile('C:/TEMP/TempNotInHBDict.csv')

# Make RLB KEYID List
def make_KeyID_List():
	dtemp = dicts.spreadsheet_to_dict(csvRLB)
	print('\n Building Master file KeyId list...')
	lKeyID = []
	for row in dtemp:
		lKeyID.append(dtemp[row]['KEYID'])
	return lKeyID

# Make COE or Permit Fields List
def make_COE_Permit_Field_List(dataSource):
	if dataSource == 'RLB COE':
		lin = [
			d['ADDRESS'],
			d['AREA'],
			d['BUILDER'],
			d['CITY'],
			d['COUNTY'],
			d['DATE'],
			d['INTENDUSE'],
			d['LATITUDE'],
			d['LONGITUDE'],
			d['LOT'],
			d['LOTSIZE'],
			d['LOTWIDTH'],
			d['MASTPLAN'],
			d['METHODFIN'],
			d['MORTGAGECO'],
			d['OURSUBDIV'],
			d['PARTYPE'],
			d['PRISQFT'],
			d['PRODCODE'],
			d['SALEPRICE'],
			d['SQFT'],
			d['STATE'],
			d['SUBDIVISIN'],
			d['SUBID'],
			d['ZIP'],
			d['KEYID'],
			submarket]
	elif dataSource == 'RLB PERMITS':
		lin = [
			d['ADDRESS'],
			d['AREA'],
			d['BUILDER'],
			d['CITY'],
			d['COUNTY'],
			d['LATITUDE'],
			d['LIVESQFT'],
			d['LONGITUDE'],
			d['LOT'],
			d['MASTPLAN'],
			d['PERMIT DATE'],
			d['PERMIT NUM'],
			d['PERMITSQFT'],
			d['PRODCODE'],
			d['STATE'],
			d['SUBDIVISION'],
			d['SUBID'],
			d['ZIP'],
			d['KEYID'],
			submarket]
	return lin


todaydate = td.today_date()

# Loop until user quits
lMPC_cant_Find = []

while 1:
	# Set Variables
	infile, outfile, dataSource = chooseSourceFile()
	fRLB_No_Name = make_no_name_found_csv()
	file_builder_rename_db = '{0}BuilderRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
	file_MPC_rename_db = 'F:/Research Department/MIMO/zData/MPCRenameDatabase_v01.xlsx'

	# Create dicts of infile, Builder names and MPC names
	dBuilderRename = dicts.spreadsheet_to_dict(file_builder_rename_db)
	dMPC_Rename = dicts.spreadsheet_to_dict(file_MPC_rename_db)
	# MetroStudy
	if dataSource == 'MetroStudy':
		processMetroStudyHomebuilders()
	# RL Brown & Zonda
	else:
		din = dicts.spreadsheet_to_dict(infile)
		lHeader = []
		for key in din[1].keys():
			lHeader.append(key)
		if 'RLB' in dataSource:
			lHeader.append('KEYID')

		lao.check_if_file_is_open(outfile)
		with open(outfile, 'w', newline='') as f:
			fout = csv.writer(f)
			fout.writerow(lHeader)
			print('\n Cleaning {0} data...'.format(dataSource))
			# Cycle through din records
			for row in din:
				rec = din[row]
				if 'RLB' in dataSource:
					lLine = getRLBData(rec)
				elif dataSource == 'Zonda':
					lLine = getZondaData(rec)
				fout.writerow(lLine)
		
		ui = td.uInput('\n Formatting complete...\n\n Open CSV [0/1/00] > ')
		if ui == '1':
			pprint(lMPC_cant_Find)
			lao.openFile(outfile)
			# lao.openFile(fRLB_No_Name)
			# lao.openFile(file_cant_find)
		elif ui == '00':
			exit('\n Terminating program...')
		
		# Add to Master CSV
		if 'RLB' in dataSource:
			ui = td.uInput('\n Add CSV to RLB Master CSV [0/1/00] > ')
			if ui == '00':
				exit('\n Terminating program...')
			if ui == '1':
				# Make backup of the Master csv
				if dataSource == 'RLB COE':
					csvRLB = '{0}RLB COE Master Database.csv'.format(lao.getPath('rlb'))
					# Make backup of existing file
					csvBackup = csvRLB.replace('.csv', ' {0}.csv'.format(todaydate))
					shutil.copy(csvRLB, csvBackup)
				elif dataSource == 'RLB PERMITS':
					csvRLB = '{0}RLB Permits Master Database.csv'.format(lao.getPath('rlb'))
					csvBackup = csvRLB.replace('.csv', ' {0}.csv'.format(todaydate))
					shutil.copy(csvRLB, csvBackup)
				din = dicts.spreadsheet_to_dict(outfile)

				lKeyID = make_KeyID_List()
				print('\n Adding new data to Master file...')
				with open(csvRLB, 'a', newline='') as f:
					fout = csv.writer(f)
					# Write din to Master CSV
					count = 1
					din_len = len(din)
					for row in din:
						d = din[row]
						if d['KEYID'] in lKeyID:
							continue
						# Get LAO Submarket
						dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', lon=d['LONGITUDE'], lat=d['LATITUDE'])
						submarket = dLAO_geoinfo['submarket']
						# Get Field values
						lin = make_COE_Permit_Field_List(dataSource)
						# Write to Master csv
						fout.writerow(lin)
						print(f' {count} of {din_len} : {d["KEYID"]} added...')
						lKeyID.append(d['KEYID'])
						count += 1
		

		
		
		