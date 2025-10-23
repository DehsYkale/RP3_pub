# Check Market Mailer addresses against Anchor addresses

import lao
import dicts
import fun_text_date as td
from pprint import pprint
import webs

anchor_filename = r'F:\Research Department\MIMO\zData\Anchor Contact Standardization\13025_LAND_ADVISORS_NET_MAIL_FINAL.CSV'
# market_mailer_filename = r'F:\Research Department\MIMO\Market Insights\Market Mailers\Mailing Lists\AUS Mailing List CLEANED.csv'
fin_folder = r'F:\Research Department\MIMO\Market Insights\Market Mailers\Mailing Lists'

dAnchor_temp = dicts.spreadsheet_to_dict(anchor_filename)
# Build Anchor dictionary
dAnchor = {}
for row in dAnchor_temp:
	d = dAnchor_temp[row]
	dAnchor[d['Account Contact ID']] = {
		'Anchor Street': d['FNL_ADDR1'],
		'Anchor Street2': d['FNL_ADDR2'],
		'Anchor City': d['FNL_CITY'],
		'Anchor State': d['FNL_STATE'],
		'Anchor Zip': d['FNL_ZIP'],
		'Anchor Moved': d['NCO_ACTION'], # Possible Move AK
		'Anchor Zip Correction': d['STD_ZCAC'], # Zip Code Correction Code AU
		'Anchor Deliverable': d['ANC_DINDEX'], # ANC/DPV Deliverability Index AT
		'Anchor Deceased': d['DEC_MTCHS'], # Deceased Match AV
		'Anchor Match Code': d['LIST_NUM'] # List Number did it match Y
	}

while 1:
	td.banner('MM Address Anchor Check v01')
	market_mailer_filename = lao.guiFileOpen(path=fin_folder, titlestring='MM', extension=[('csv files', '.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])



	dMM = dicts.spreadsheet_to_dict(market_mailer_filename)

	for row in dMM:
		dline = dMM[row]
		lTemp = dline['TFID URL'].split('/')
		AID = lTemp[6][:-3]
		print(f'\n TFID: {AID}')
		# try:
		# 	pprint(dAnchor[AID])
		# except KeyError:
		# 	print(f'\n {AID} not found in Anchor file...')
			# webs.openTFDID(AID)
			# ui = td.uInput('\n Continue [00]... > ')
			# if ui == '00':
			# 	exit('\n Terminating program...')
			# continue
		try:
			if int(dAnchor[AID]['Anchor Match Code']) == 100:
				continue
		except KeyError:
			print(f'\n {AID} not found in Anchor file...')
			continue
		td.warningMsg(f'\n {AID} has a match code of {dAnchor[AID]['Anchor Match Code']}...')
		webs.openTFDID(AID)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')

	ui = td.uInput('\n Do another or quit [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')