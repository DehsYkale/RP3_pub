#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from subprocess import Popen
import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

def banner(text):
	"""Display a banner message"""
	print('\n' + '=' * 60)
	print(f'  {text}')
	print('=' * 60 + '\n')

def get_selenium_driver():
	"""Get a Selenium WebDriver instance"""
	options = Options()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-certificate-errors-spki-list')
	options.add_argument("--disable-infobars")
	options.add_argument('--ignore-ssl-errors')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	
	try:
		driver = webdriver.Chrome(options=options)
		return driver
	except Exception as e:
		print(f"\nError starting Chrome: {e}")
		print("\nPlease ensure Chrome and ChromeDriver are installed")
		sys.exit(1)

banner('Employment by Industry Pct Change')

dMSAs = {
	'ABQ': {'market': 'nm_albuquerque', 'region': 'southwest', 'msaNo': ''},
	'ALT': {'market': 'ga_atlanta', 'region': 'southeast', 'msaNo': ''},
	'AUS': {'market': 'tx_austin', 'region': 'southwest', 'msaNo': ''},
	'BOI': {'market': 'id_boisecity', 'region': 'west', 'msaNo': ''},
	'CLT': {'market': 'nc_charlotte', 'region': 'southeast', 'msaNo': ''},
	'DEN': {'market': 'co_denver', 'region': 'mountain-plains', 'msaNo': '1'},
	'DFW': {'market': 'tx_dallas', 'region': 'southwest', 'msaNo': ''},
	'GSP': {'market': 'sc_greenville', 'region': 'southeast', 'msaNo': ''},
	'HNT': {'market': 'al_huntsville', 'region': 'southeast', 'msaNo': ''},
	'HOU': {'market': 'tx_houston', 'region': 'southwest', 'msaNo': ''},
	'JAX': {'market': 'fl_jacksonville', 'region': 'southeast', 'msaNo': ''},
	'KCI': {'market': 'mo_kansascity', 'region': 'mountain-plains', 'msaNo': '1'},
	'LVS': {'market': 'nv_lasvegas', 'region': 'west', 'msaNo': ''},
	'NAZF': {'market': 'az_flagstaff', 'region': 'west', 'msaNo': ''},
	'NAZP': {'market': 'az_prescott', 'region': 'west', 'msaNo': ''},
	'NSH': {'market': 'tn_nashville', 'region': 'southeast', 'msaNo': ''},
	'ORL': {'market': 'fl_orlando', 'region': 'southeast', 'msaNo': ''},
	'PHX': {'market': 'az_phoenix', 'region': 'west', 'msaNo': '1'},
	'RNO': {'market': 'nv_reno', 'region': 'west', 'msaNo': ''},
	'SRQ': {'market': 'fl_sarasota', 'region': 'southeast', 'msaNo': ''},
	'TPA': {'market': 'fl_tampa', 'region': 'southeast', 'msaNo': '1'},
	'TUC': {'market': 'az_tucson', 'region': 'west', 'msaNo': ''},
	'UTAH': {'market': 'ut_saltlakecity', 'region': 'mountain-plains', 'msaNo': ''},
}

lOrder = ['ABQ', 'ALT', 'AUS', 'BOI', 'CLT', 'DEN', 'DFW', 'GSP', 'HNT', 'HOU', 
          'JAX', 'KCI', 'LVS', 'NAZF', 'NAZP', 'NSH', 'ORL', 'PHX', 'RNO', 
          'SRQ', 'TPA', 'TUC', 'UTAH']

driver = get_selenium_driver()

with open(r'C:\Downloaded Files\BLS_MSA_Industries.csv', 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(['Place', 'Industry', 'Pct Change'])

	for msa in lOrder:
		mktAbbrv = msa
		region = dMSAs[msa]['region']
		market = dMSAs[msa]['market']
		msaNo = dMSAs[msa]['msaNo']
		url = f'https://www.bls.gov/regions/{region}/{market}_msa.htm'

		print(f'\nProcessing {msa}...')
		driver.get(url)
		sleep(3)
		emp_html = driver.page_source

		soup = BeautifulSoup(emp_html, 'html.parser')
		table = soup.find('table', {'id': f'eag_{market}_msa{msaNo}'})

		try:
			tbody = table.find('tbody')
		except AttributeError:
			print(f'\nERROR: Could not find table for {msa}')
			print('Check if the table id needs msaNo to equal 1')
			print(f'Example: {market}_msa1')
			continue
			
		trs = tbody.find_all('tr')

		dIndustries = {}
		txtMiningConstructionTogether = 'ABQ AUS BOI CLT DEN DFW GSP HNT KCI NAZF NAZP NSH SRQ UTAH'
		
		if msa in txtMiningConstructionTogether:
			lIndustry = ['Total', 'Mining, Logging, & Construction', 'Manufacturing', 
			            'Trade, Transportation, & Utilities', 'Information', 
			            'Financial Activities', 'Professional & Business Services', 
			            'Education & Health Services', 'Leisure & Hospitality', 
			            'Personal Services', 'Government']
		else:
			lIndustry = ['Total', 'Mining & Logging', 'Construction', 'Manufacturing', 
			            'Trade, Transportation & Utilities', 'Information', 
			            'Financial Activities', 'Professional & Business Services', 
			            'Education & Health Services', 'Leisure & Hospitality', 
			            'Personal Services', 'Government']
		
		i = 0
		for tr in trs:
			th = tr.find('th')
			if th and th.text == '12-month % change':
				# Check if we've gone past the end of the industry list
				if i >= len(lIndustry):
					break
					
				if lIndustry[i] == 'Total':
					print('  Skipping total')
					i += 1
					continue
				
				tds = tr.findAll('td')
				# Try column 6 first (index 6)
				pctChange = tds[6].text.replace('(p)', '').strip() if len(tds) > 6 else ''
				
				# If column 6 is blank, use column 5
				if pctChange == '':
					pctChange = tds[5].text.replace('(p)', '').strip() if len(tds) > 5 else ''

				if pctChange:
					dIndustries[lIndustry[i]] = float(pctChange)
				i += 1

		print(f'\n{mktAbbrv} Results:')
		for key, value in sorted(dIndustries.items(), key=lambda item: item[1], reverse=True):
			print(f'  {key}: {value}')
			fout.writerow([mktAbbrv, key, value])

driver.quit()

print('\n' + '='*60)
print('Data saved to: C:\\Downloaded Files\\BLS_MSA_Industries.csv')
print('='*60)

# Open the output file
try:
	p = Popen(r'C:\Downloaded Files\BLS_MSA_Industries.csv', shell=True)
	print('\nOpening CSV file...')
except Exception as e:
	print(f'Could not open file: {e}')

print('\nScript complete!')