#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from subprocess import Popen
import fun_text_date as td
import lao
import csv
from time import sleep
from selenium import webdriver
import sys
from pprint import pprint
from webs import getSeleniumDriver

lao.banner('Employment by Industry Pct Change')

dMSAs = {'ABQ':
			  {'market': 'nm_albuquerque',
			   'region': 'southwest',
			   'msaNo': ''},
		  'ALT':
			  {'market': 'ga_atlanta',
			   'region': 'southeast',
			   'msaNo': ''},
		  'AUS':
			  {'market': 'tx_austin',
			   'region': 'southwest',
			   'msaNo': ''},
		  'BOI':
			  {'market': 'id_boisecity',
			   'region': 'west',
			   'msaNo': ''},
		  'CLT':
			  {'market': 'nc_charlotte',
			   'region': 'southeast',
			   'msaNo': ''},
		  'DEN':
			  {'market': 'co_denver',
			   'region': 'southwest',
			   'msaNo': ''},
		  'DFW':
			  {'market': 'tx_dallas',
			   'region': 'southwest',
			   'msaNo': ''},
		  'GSP':
			  {'market': 'sc_greenville',
			   'region': 'southeast',
			   'msaNo': ''},
		  'HNT':
			  {'market': 'al_huntsville',
			   'region': 'southeast',
			   'msaNo': ''},
		  'HOU':
			  {'market': 'tx_houston',
			   'region': 'southwest',
			   'msaNo': ''},
		  'JAX':
			  {'market': 'fl_jacksonville',
			   'region': 'southeast',
			   'msaNo': ''},
		  'KCI':
			  {'market': 'mo_kansascity',
			   'region': 'mountain-plains',
			   'msaNo': '1'},
		  'LVS':
			  {'market': 'nv_lasvegas',
			   'region': 'west',
			   'msaNo': ''},
		  'NAZF':
			  {'market': 'az_flagstaff',
			   'region': 'west',
			   'msaNo': ''},
		  'NAZP':
			  {'market': 'az_prescott',
			   'region': 'west',
			   'msaNo': ''},
		  'NSH':
			  {'market': 'tn_nashville',
			   'region': 'southeast',
			   'msaNo': ''},
		  'ORL':
			  {'market': 'fl_orlando',
			   'region': 'southeast',
			   'msaNo': ''},
		  'PHX':
			  {'market': 'az_phoenix',
			   'region': 'west',
			   'msaNo': '1'},
		  'RNO':
			  {'market': 'nv_reno',
			   'region': 'west',
			   'msaNo': ''},
          'SRQ':
			  {'market': 'fl_sarasota',
			   'region': 'southeast',
			   'msaNo': ''},
		  'TPA':
			  {'market': 'fl_tampa',
			   'region': 'southeast',
			   'msaNo': '1'},
		  'TUC':
			  {'market': 'az_tucson',
			   'region': 'west',
			   'msaNo': ''},
		  'UTAH':
			  {'market': 'ut_saltlakecity',
			   'region': 'mountain-plains',
			   'msaNo': ''},
		  }

lOrder = ['ABQ', 'ALT', 'AUS', 'BOI', 'CLT', 'DEN', 'DFW', 'GSP', 'HNT', 'HOU', 'JAX', 'KCI', 'LVS', 'NAZF', 'NAZP', 'NSH', 'ORL', 'PHX', 'RNO', 'SRQ', 'TPA', 'TUC', 'UTAH']
driver = getSeleniumDriver()
with open('C:/TEMP/BLS_MSA_Industries.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(['Place', 'Industry', 'Pct Change'])

	#for msa in dMSAs:
	for msa in lOrder:
		mktAbbrv = msa
		region = dMSAs[msa]['region']
		market = dMSAs[msa]['market']
		msaNo = dMSAs[msa]['msaNo']
		url = 'https://www.bls.gov/regions/{0}/{1}_msa.htm'.format(region, market)

		driver.get(url)
		sleep(3)
		emp_html = driver.page_source
		# td.uInput(msa)
		# continue

		soup = BeautifulSoup(emp_html, 'html.parser')
		table = soup.find('table', {'id': 'eag_{0}_msa{1}'.format(market, msaNo)})

		try:
			tbody = table.find(['tbody'])
		except AttributeError:
			td.warningMsg('\n Could not find the table tbody.\n\n Check if the table id needs msaNo to equal 1.\n\n Example: mo_kansascity_msa1')
			exit('\n Terminating program...')
		trs = tbody.find_all(['tr'])

		dIndustries = {}
		txtMiningConstructionTogether = 'ABQ AUS BOI CLT DFW GSP HNT KCI NAZF NAZP NSH SRQ UTAH'
		#if msa == 'ABQ' or msa == 'AUS' or msa == 'BOI' or msa == 'CLT' or msa == 'DFW' or msa == 'HNT' or msa == 'NAZF' or msa == 'NAZP' or msa == 'NSH' or msa == 'SRQ' or msa == 'UTAH':
		if msa in txtMiningConstructionTogether:
			lIndustry = ['Total', 'Mining, Logging, & Construction', 'Manufacturing', 'Trade, Transportation, & Utilities', 'Information', 'Financial Activities', 'Professional & Business Services', 'Education & Health Services', 'Leisure & Hospitality', 'Personal Services', 'Government']
		else:
			lIndustry = ['Total', 'Mining & Logging', 'Construction', 'Manufacturing', 'Trade, Transportation & Utilities', 'Information', 'Financial Activities', 'Professional & Business Services', 'Education & Health Services', 'Leisure & Hospitality', 'Personal Services', 'Government']
		
		i = 0
		for tr in trs:
			# print(tr)
			if tr.find(['th']).text == '12-month % change':
				if lIndustry[i] == 'Total':
					print('skip total')
					i += 1
					continue
				pctChange = tr.findAll(['td'])[6].text.replace('(p)', '').strip()
				# print('pctChange: {0}'.format(pctChange))
				if pctChange == '': # Last col is blank use next to last col
					pctChange = tr.findAll(['td'])[5].text.replace('(p)', '').strip()

				dIndustries[lIndustry[i]] = float(pctChange)
				i += 1
				# if i == 13:
				# 	break
				# td.uInput(dIndustries)
		print
		print(mktAbbrv)
		#for key, value in sorted(dIndustries.items(), key=lambda k, v: (v, k), reverse=True):
			print(f' {key} : {value}')
		for key, value in sorted(dIndustries.items(), key=lambda k, v: v[1], reverse=True):
			print(f' {key} : {value}')
			fout.writerow([mktAbbrv, key, value])
		# td.uInput('continue...')

driver.quit()

p = Popen('C:/TEMP/BLS_MSA_Industries.csv', shell=True)

print('\nCopy data into master spreadsheet...')
td.uInput('\nContinue...')