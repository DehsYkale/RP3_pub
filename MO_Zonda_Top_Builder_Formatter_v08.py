
import acc
import bb
import csv
from glob import glob
import how
import lao
import operator
from pprint import pprint
from urllib.request import urlopen
import xlwings as xw
import warnings
from webbrowser import open as openbrowser
import fun_text_date as td

# Select report menu
def report_menu():
	how.zonda_top_builder_formater()
	
	while 1:
		lao.banner('Zonda Top Builder Formater v08')
		print('\n   1) Full List (for Max)')
		print('\n   2) COE Only (MIMO)')
		print('\n   3) TNHC Fields')
		print('\n   4) Private Builders Acitve (3+ Starts & Closings)')
		print('\n  00) Quit')
		ui = td.uInput('\n Select > ')
		if ui == '1':
			# isFullList = True
			list_type = 'FULL'
			headerData = ['Market', 'Builder', 'Type', 'Starts', 'Closings', 'Market Share', 'Closings Qtr', 'Future', 'VDL', 'Occupied', 'Fin Vac', 'U/C', 'Total Lots']
			outFileMasterFinal = '{0}Zonda Top Builders Full {1}.xlsx'.format(path_zonda_spreadsheet, yearQuarter)
			lSkip_Markets = []
			break
		elif ui == '2':
			# isFullList = False
			list_type = 'COE'
			headerData = ['Builder', 'Closings']
			outFileMasterFinal = '{0}Zonda Top Builders COE {1}.xlsx'.format(path_zonda_spreadsheet,yearQuarter)
			lSkip_Markets = ['IEP', 'PHX', 'SAC', 'SEA', 'TUC']
			break
		elif ui == '3':
			# isFullList = False
			list_type = 'TNHC'
			headerData = ['Builder', 'Type', 'Starts', 'Closings']
			outFileMasterFinal = '{0}Zonda Top Builders TNHC {1}.xlsx'.format(path_zonda_spreadsheet, yearQuarter)
			lSkip_Markets = ['ALT', 'BOI', 'JAX', 'LSV', 'PRC', 'RNO', 'SRQ', 'TPA', 'TUC']
			break
		elif ui == '4':
			# isFullList = False
			list_type = 'ACTIVE PRIVATE'
			headerData = ['Market', 'Builder', 'Type', 'Starts', 'Closings']
			outFileMasterFinal = '{0}Zonda Top Builders TNHC {1}.xlsx'.format(path_zonda_spreadsheet, yearQuarter)
			lSkip_Markets = ['ALT', 'BOI', 'JAX', 'LSV', 'PRC', 'RNO', 'SRQ', 'TPA', 'TUC']
			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')
			lao.sleep(2)

	# Clear data from temp csv
	with open(outFileMaster, 'w', newline='') as f:
		fout = csv.writer(f)

	return list_type, headerData, outFileMasterFinal, lSkip_Markets

# Find Duplicate Builders
def find_dup_builders():
	lDuplicates = []
	lTemp = []
	for hbData in lBuilders:
		if hbData['Builder'] in lTemp:
			lDuplicates.append(hbData['Builder'])
		else:
			lTemp.append(hbData['Builder'])
	return lDuplicates

# Sum Duplicate Builder data values
def sum_dup_builders():
	iBuilders = []
	lBuildersDuplicates = []
	for builder in lDuplicates:
		starts, closings, closings_qtr, total_lots, future, vdl, under_contstruction, finished_vacant, occupied = 0, 0, 0, 0, 0, 0, 0, 0, 0
		for rec in lBuilders:
			# Build the data
			if rec['Builder'] == builder:
				# if isFullList:
				if list_type == 'FULL':
					starts = starts + rec['Starts']
					# Calculate Market Share of Starts
					market_share = round(float(starts) / float(total_starts) * 100, 1)
					market_share = '{0}%'.format(market_share)
					type_public_private = rec['Type']
					closings = closings + rec['Closings']
					closings_qtr = closings_qtr + rec['Closings Qtr']
					total_lots = total_lots + rec['Total Lots']
					future = future + rec['Future']
					vdl = starts + rec['VDL']
					under_contstruction = starts + rec['U/C']
					finished_vacant = starts + rec['Fin Vac']
					occupied = starts + rec['Occupied']
				elif list_type == 'COE':
					closings = closings + rec['Closings']
				elif list_type == 'TNHC':
					starts = starts + rec['Starts']
					closings = closings + rec['Closings']
					type_public_private = rec['Type']
				elif list_type == 'ACTIVE PRIVATE':
					starts = starts + rec['Starts']
					closings = closings + rec['Closings']
					type_public_private = rec['Type']

		# Add data to duplcates list
		# if isFullList:
		if list_type == 'FULL':
			lBuildersDuplicates.append({
				'Market': market,
				'Builder': builder,
				'Type': type_public_private,
				'Starts': starts,
				'Closings': closings,
				'Market Share': market_share,
				'Closings Qtr': closings_qtr,
				'Total Lots': total_lots,
				'Future': future,
				'VDL': vdl,
				'U/C': under_contstruction,
				'Fin Vac': finished_vacant,
				'Occupied': occupied})
		elif list_type == 'COE':
			lBuildersDuplicates.append({
				'Builder': builder,
				'Closings': closings})
		elif list_type == 'TNHC':
			lBuildersDuplicates.append({
				'Builder': builder,
				'Type': type_public_private,
				'Starts': starts,
				'Closings': closings})
		elif list_type == 'ACTIVE PRIVATE':
			lBuildersDuplicates.append({
				'Market': market,
				'Builder': builder,
				'Type': type_public_private,
				'Starts': starts,
				'Closings': closings})
		
		# Add data to list
		i = 0
		for rec in lBuilders:
			if rec['Builder'] == builder:
				#if isFullList:
				if list_type == 'FULL':
					lBuilders[i]['Market'] = market
					lBuilders[i]['Builder'] = '{0} DUP'.format(builder)
					lBuilders[i]['Type'] = 'NONE'
					lBuilders[i]['Starts'] = 1
					lBuilders[i]['Closings'] = 1
					lBuilders[i]['Market Share'] = 1
					lBuilders[i]['Closings Qtr'] = 1
					lBuilders[i]['Total Lots'] = 1
					lBuilders[i]['Future'] = 1
					lBuilders[i]['VDL'] = 1
					lBuilders[i]['U/C'] = 1
					lBuilders[i]['Fin Vac'] = 1
					lBuilders[i]['Occupied'] = 1
				elif list_type == 'COE':
					lBuilders[i]['Builder'] = '{0} DUP'.format(builder)
					lBuilders[i]['Closings'] = 1
				elif list_type == 'TNHC':
					lBuilders[i]['Builder'] = '{0} DUP'.format(builder)
					lBuilders[i]['Type'] = 'NONE'
					lBuilders[i]['Starts'] = 1
					lBuilders[i]['Closings'] = 1
				elif list_type == 'ACTIVE PRIVATE':
					lBuilders[i]['Market'] = market
					lBuilders[i]['Builder'] = '{0} DUP'.format(builder)
					lBuilders[i]['Type'] = 'NONE'
					lBuilders[i]['Starts'] = 1
					lBuilders[i]['Closings'] = 1

			i += 1
	lBuilders.extend(lBuildersDuplicates)
	return lBuilders

# Get Lots Under Development values by Builder
# def lots_under_dev():


lao.banner('Zonda Top Builder Formater v08')
warnings.filterwarnings('ignore')
renameFile = '{0}BuilderRenameDatabase_v01.xlsx'.format(lao.getPath('zdata'))
dHB = lao.spreadsheetToDict(renameFile)
yearQuarter = lao.getDateQuarter(lastquarter=True)
inFiles = glob('{0}*_Qtrly_Activity_Builder_{1}.pdf'.format(lao.getPath('metstud'), yearQuarter))
path_zonda_spreadsheet = 'F:/Research Department/MIMO/Spreadsheets/Master Spreadsheet Data/Zonda/'
outFileMaster = '{0}Zonda Top Builders Temp.csv'.format(path_zonda_spreadsheet)

list_type, headerData, outFileMasterFinal, lSkip_Markets = report_menu()


lBuilders_not_in_rename_db = [['Builder', 'Closings']]
is_active_private_header_written = False
for fpdf in inFiles:
	market = fpdf[45:48]

	# Skip markets in lSkip_Markets
	if market in lSkip_Markets:
		continue

	# Make headers
	if list_type == 'FULL':
		headerMarket = ['Market', market, yearQuarter, '', '', '', '', '', '', '']
	elif list_type == 'COE':
		headerMarket = ['Market', market]
	elif list_type == 'TNHC':
		headerMarket = ['Market', market, yearQuarter, '']
	elif list_type == 'ACTIVE PRIVATE':
		headerMarket = ['Active Private', yearQuarter, '', '', '']
	print('\n Market: {0}'.format(market))

	# Open pdf file
	pdfFileObj, pdfReader, intPages = td.open_pdf(fpdf)

	lBuilders = []
	# Read builder data from pdf
	print(' Reading {0} PDF...'.format(market))
	lBuilderData = td.read_pdf_data_metrostudy_builders(pdfReader, intPages)

	# Get total Starts
	print(' Calculating Total Starts...')
	row_num = 0
	total_starts = 0
	for row in lBuilderData:
		if row == 'Starts':
			builder = lBuilderData[row_num - 1]
			
			for i in range(row_num + 1, row_num + 10):
				if '$' in lBuilderData[i] or '-' in lBuilderData[i]:
					# if lBuilderData[i - 1] = 'Starts' then the first quareter numbers are negative
					# so continue until a $ is found
					if lBuilderData[i - 1] == 'Starts':
						continue
					starts = td.txt_to_int(lBuilderData[i - 1])
					if starts == 'Error':
						td.warningMsg('Starts val error...')
						print(' Market: {0}'.format(market))
						print(' Builder: {0}'.format(builder))
						print(' Val: {0}'.format(lBuilderData[i - 1]))
					total_starts = total_starts + starts
					break
		row_num += 1

	print(' Calculating all data...')
	row_num = 0
	for row in lBuilderData:
		# Starts
		if row == 'Starts':
			builder = lBuilderData[row_num - 1]
			for i in range(row_num + 1, row_num + 10):
				# if lBuilderData[i - 1] = 'Starts' then the first quareter numbers are negative
				# so continue until a $ is found
				if lBuilderData[i - 1] == 'Starts':
					continue
				if '$' in lBuilderData[i] or '-' in lBuilderData[i]:
					starts = td.txt_to_int(lBuilderData[i - 1])
					break
		# Closings
		elif row == 'Closings':
			for i in range(row_num + 1, row_num + 10):
				if 'section' in lBuilderData[i]:
					closings = td.txt_to_int(lBuilderData[i - 1])
					closings_qtr = td.txt_to_int(lBuilderData[i - 2])
					break
		# VDL
		elif row == 'VDL Inv':
			try:
				total_lots = td.txt_to_int(lBuilderData[row_num - 1])
				total_lots = td.txt_to_int(total_lots)
			except ValueError:
				td.warningMsg('error')
				exit('\n Terminating program...')
			future = td.txt_to_int(lBuilderData[row_num - 2])
			vdl = td.txt_to_int(lBuilderData[row_num - 3])
			under_contstruction = td.txt_to_int(lBuilderData[row_num - 4])
			finished_vacant = td.txt_to_int(lBuilderData[row_num - 5])
			occupied = td.txt_to_int(lBuilderData[row_num - 7])

			# Skip non-acitive subdivisions
			if starts > 0 and closings > 0:
				# Skip unknown a total
				if not builder == 'Unknown/Multiple' and not builder == 'Totals':

					# Clean builder names based on hb rename database spreadsheet
					builder, type_public_private, not_in_builder_rename_list = td.standarize_builder_names(builder, dHB_Rename=dHB, market=market)

					# If builder not in the rename db the add it to the missing list
					if not_in_builder_rename_list:
						# if not builder in lBuilders_not_in_rename_db:
						lBuilders_not_in_rename_db.append([builder, closings])

					# Calculate Market Share of Starts
					market_share = round(float(starts) / float(total_starts) * 100, 1)
					market_share = '{0}%'.format(market_share)
					# Full List: append all data
					if list_type == 'FULL':
						lBuilders.append({
							'Market': market,
							'Builder': builder,
							'Type': type_public_private,
							'Starts': starts,
							'Closings': closings,
							'Market Share': market_share,
							'Closings Qtr': closings_qtr,
							'Total Lots': total_lots,
							'Future': future,
							'VDL': vdl,
							'U/C': under_contstruction,
							'Fin Vac': finished_vacant,
							'Occupied': occupied
							})
					# COE List: append COE data
					elif list_type == 'COE':
						lBuilders.append({
							'Builder': builder,
							'Closings': closings
							})
					# TNHC List: append TNHC data
					elif list_type == 'TNHC':
						lBuilders.append({
							'Builder': builder,
							'Type': type_public_private,
							'Starts': starts,
							'Closings': closings
						})
					# TNHC List: append ACTIVE PRIVATE data
					elif list_type == 'ACTIVE PRIVATE':
						lBuilders.append({
							'Market': market,
							'Builder': builder,
							'Type': type_public_private,
							'Starts': starts,
							'Closings': closings
						})
		row_num += 1


	# Find duplicate builders\
	print(' Finding duplicate builders...')
	lDuplicates = find_dup_builders()
	# Sub data of duplicate builders
	print(' Summing data of duplicate builders...')
	lBuilders = sum_dup_builders()

	# lBuilders = lots_under_dev()

	outFileTemp = 'C:/TEMP/pdftest.csv'
	outFileSorted = 'C:/TEMP/pdftest_sorted.csv'

	
	with open(outFileTemp, 'w', newline='') as f:
		fout = csv.DictWriter(f, fieldnames = headerData)
		fout.writeheader()
		fout.writerows(lBuilders)

	# Sort the temp csv
	print(' Sorting the results...')
	with open(outFileTemp, 'r') as f, open(outFileMaster, 'a', newline='') as g:
		incsv = csv.reader(f)
		outcsv = csv.writer(g)
		next(incsv)
		# sorted_csv = sorted(incsv, key=lambda x: float(x[2]), reverse=True)
		# if isFullList:
		if list_type == 'FULL':  # Sort Starts high to low column 3
			sorted_csv = sorted(incsv, key=lambda x: float(x[3]), reverse=True)
		elif list_type == 'COE':  # Sort Closings high to low column 1
			sorted_csv = sorted(incsv, key=lambda x: float(x[1]), reverse=True)
		elif list_type == 'TNHC':  # Sort Starts high to low column 3
			sorted_csv = sorted(incsv, key=lambda x: float(x[3]), reverse=True)
		elif list_type == 'ACTIVE PRIVATE':  # Sort Starts high to low column 3
			sorted_csv = sorted(incsv, key=lambda x: float(x[4]), reverse=True)

		# Write Headers: ACTIVE PRIVATE
		if list_type == 'ACTIVE PRIVATE' or list_type == 'FULL':
			if is_active_private_header_written == False:
				print(' Writing ACTIVE PRIVATE headers...')
				# outcsv.writerow(headerMarket)
				outcsv.writerow(headerData)
				is_active_private_header_written = True
		# Write Headers: FULL, COE or TNHC
		else:
			print(' Writing FULL, COE or TNHC headers...')
			outcsv.writerow(headerMarket)
			outcsv.writerow(headerData)

		# Write Top 30 Builders
		i = 0
		print(f' Writing {market}...')
		for row in sorted_csv:
			# Write ACTIVE PRIVATE data
			if list_type == 'ACTIVE PRIVATE':
				if 'DUP' in row[0] or 'Public' in row[2]:
					continue
				# Write if more than 3 starts and 3 closings
				if int(row[3]) >= 3 and int(row[4]) >= 3:
					outcsv.writerow(row)
			elif list_type == 'FULL':
				if 'DUP' in row[0]:
					continue
				# Write if more than 5 VDLs
				elif int(row[8]) >= 5:
					outcsv.writerow(row)
			# Write FULL, COE, TNHC data
			else:
				i += 1
				if i <= 30:
					outcsv.writerow(row)
				# Add None to markets with less than 30 builders
				# if i != 30:
				# 	for i in range(i, 20):
				# 		outcsv.writerow(['None', 0])
		print(' Finished writing...')
		# for row in sorted_csv:
		# 	outcsv.writerow(row)


	# closing the pdf file object
	pdfFileObj.close()
	# print('here1')
	# break

# If ACTIVE PRIVATE open csv and end script
if list_type == 'ACTIVE PRIVATE' or list_type == 'FULL':
	lao.openFile(outFileMaster)
	exit('\n Fin')

# Write to Master CSV (not final temp file)
with open(outFileMaster, 'r') as f:
	incsv = csv.reader(f)
	wb = xw.Book()
	sht = wb.sheets['Sheet1']

	c = 1 # Column
	r = 1 # Row
	isFirst = True
	for row in incsv:
		if row[0] == 'Market':
			if isFirst:
				sht.range(r, c).value = row
				isFirst = False
			else:
				# if isFullList:
				if list_type == 'FULL':
					c = c + 12
				elif list_type == 'COE':
					c = c + 2
				elif list_type == 'TNHC':
					c = c + 4
				elif list_type == 'ACTIVE PRIVATE':
					c = c + 5
				r = 1
				sht.range(r, c).value = row
		else:
			sht.range(r, c).value = row
		r += 1

with open('C:/TEMP/lBuilders_not_in_rename_db.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	for row in lBuilders_not_in_rename_db:
		fout.writerow(row)

lao.openFile('C:/TEMP/lBuilders_not_in_rename_db.csv')

wb.save(outFileMasterFinal)


exit('\n Fin')
