
import bb
import dicts
import lao
from os import system, remove, path
from pprint import pprint
import sys
import fun_text_date as td

from time import sleep
from webbrowser import open as openbrowser


# Open URL in Chrome
def open_chrome(url, width=920, height=500, pos_x=0, pos_y=0):
	import subprocess

	window_size = f'--window-size={width},{height}'
	window_position = f'--window-position={pos_x},{pos_y}'
	subprocess.Popen(['start', 'chrome', url, '--new-window', window_size, window_position], shell=True)

	# # Path to the Chrome executable (adjust this path if Chrome is installed in a different location)
	# chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
	
	# # Check if Chrome is running
	# is_running = subprocess.call('tasklist /FI "IMAGENAME eq chrome.exe"', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0
	
	# # Arguments for window size and position
	# window_size = f'--window-size={width},{height}'
	# window_position = f'--window-position={pos_x},{pos_y}'
	
	# if is_running:
	# 	# Launch a new Chrome window with the URL, specified size, and position
	# 	subprocess.Popen([chrome_path, url, '--new-window', window_size, window_position], shell=False)
	# else:
	# 	# Launch Chrome with the URL in a new window (same command if not running)
	# 	subprocess.Popen([chrome_path, url, '--new-window', window_size, window_position], shell=False)



	# openbrowser(url)

# opens url in browser
def open_url(URL):
	from webbrowser import open as openbrowser
	openbrowser(URL)

# # Remove HTML tags
def removeHTMLTags(html):
	html = html.replace('</p>', '\n')
	html = html.replace('<br>', '\n')
	soup = BeautifulSoup(html, 'html.parser')
	txt = soup.get_text()
	return txt

def selenium_LAO_Data_Sites_Login(url, vid='None'):
	from selenium import webdriver
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.chrome.options import Options
	# from pickle import load
	from lao import getUserName
	user = getUserName()
	if url == 'MetroStudy':
		url = 'https://portal.metrostudy.com/#'
		uname = 'blandis@landadvisors.com'
		pw = 'wwynhq'
		uname_element_id = 'access_email'
		pw_element_id = 'access_password'
	if url == 'Vizzda':
		url = 'https://www2.vizzda.com/login'
		uname = '{0}@landadvisors.com'.format(user)
		if user == 'avidela':
			pw = 'Research2021!'
		elif user == 'lkane':
			pw = 'Research#1'
		else:
			uname = 'blandis@landadvisors.com'
			pw = '$cottsdale2013'
		uname_element_id = 'user-name'
		pw_element_id = 'Password'
	if 'reonomy' in url.lower():

		uname_element_id = '//*[@id="1-email"]'
		pw_element_id = '/html/body/div/div/div[2]/form/div/div/div/div/div[2]/div[2]/span/div/div/div/div/div/div/div/div/div[2]/div[3]/div[2]/div/div/input'

		if user == 'lkane':
			url = url.lower()
			uname = 'blandis@landadvisors.com'
			pw = 'ReonomyPassword!'
		elif user == 'avidela':
			url = url.lower()
			uname = 'avidela@landadvisors.com'
			pw = 'Research2021!'
			uname_element_id = 'email'
			pw_element_id = 'password'
		elif user == 'blandis':
			url = url.lower()
			uname = 'blandis@landadvisors.com'
			pw = 'ReonomyPassword!'
		else:
			url = url.lower()
			uname = 'egranger@landadvisors.com'
			pw = 'ReonomyPassword!'
	if url == 'RED News':
		url = 'https://realestatedaily-news.com/wp-login.php'
		uname = 'Craig K.'
		pw = 'Harley692019!!'
		uname_element_id = 'user_login'
		pw_element_id = 'user_pass'

	driver = getSeleniumDriver()

	driver.get(url)
	sleep(3)

	elem = driver.find_element(By.XPATH, uname_element_id)
	elem.clear()
	elem.send_keys(uname)

	elem = driver.find_element(By.XPATH, pw_element_id)
	elem.clear()
	elem.send_keys(pw)
	elem.send_keys(Keys.RETURN)
	sleep(3)

	if vid != 'None':
		print('\n Logged in...opening Vizzda record web page...\n')
		try:
			driver.get('https://www2.vizzda.com//detail/{0}'.format(vid))
			# driver.get(r'https://www2.vizzda.com/map#/event/{0}'.format(vid))
			print(' Sleeping for 6 seconds...')
			sleep(6)
		except:
			print('\n Still waiting for Vizzda...\n')
			ui = td.uInput('[Enter] to continue or 00 to quit > ')
			if ui.upper() == '00':
				sys.exit('Terminating program...')
	return driver

def moveBrowser(driver, location):
	
	while 1:
		if location == 'Bill Vizzda':
			sx, sy = 950, 1300
			lx, ly = 595, 400
			break

		if 'DF' in location:
			
			sx, sy = 1152, 854
			lx, ly = 1326, 864
			break
		sy, ly = 1160, 0
		if 'F' in location:
			sx = 1920
		else:
			sx = 960
		if 'A' in location:
			lx = -1920
		elif 'B' in location:
			lx = 0
		else:
			lx = 1920
		if 'R' in location:
			lx += 960
		break
	driver.set_window_size(sx, sy)
	driver.set_window_position(lx, ly)

def openMaricopaAffidavit(RecDocNumber, monitor = 'BL'):
	from lao import click
	from selenium import webdriver

	docnum = (RecDocNumber)[5:]
	docyear = (RecDocNumber)[:4]
	driver = getSeleniumDriver()
	# driver = webdriver.Chrome(executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe')
	driver.get(r'http://recorder.maricopa.gov/recdocdata/')
	moveBrowser(driver, monitor)
	elem = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_txtRecYear"]')
	elem.send_keys(docyear)
	elem = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_txtRecNum"]')
	elem.send_keys(docnum)
	elem.send_keys(Keys.RETURN)
	sleep(1)
	try:
		elem = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_radAff"]')
		elem.click()
		sleep(1)
	except:
		print('Moving on...')
	elem = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_lnkPages"]')
	elem.click()
	return driver

def openTFDID(DID, monitor = 'DF'):
	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))
	return 'None'

def open_pid_did(service, pid_did):

	dStateAbbr = dicts.get_state_abbriviations_dict()
	if pid_did[:2] in dStateAbbr.keys():
		# Get DID based on PID
		fields = 'default'
		wc = "PID__c = '{0}'".format(pid_did)
		results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	
		if results == []:
			# lao.warningMsg(f'\n No Deal found for PID {pid_did}.')
			# sleep(2)
			return False
		DID = results[0]['Id']
	else:
		DID = pid_did

	openbrowser('https://landadvisors.my.salesforce.com/{0}'.format(DID))

	return DID

# Open TF Account Record
def openTFAccId(ID):
	openbrowser('https://landadvisors.lightning.force.com/lightning/r/Account/{0}/view'.format(ID))
	
# Search for Owner Person in Arizona Corporation Commission Website and search
def openACC(ENTITY):
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	
	driver = getSeleniumDriver()
	# driver = webdriver.Chrome(executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe')
	driver.get('https://ecorp.azcc.gov/EntitySearch/Index')
	sleep(2)
	elem = driver.find_element_by_xpath('//*[@id="SearchCriteria.quickSearch.BusinessName"]')
	elem.send_keys(ENTITY)
	elem.send_keys(Keys.RETURN)
	return driver

def open_opr_map_in_browser(PID):
	# Open the OPR map in a browser
	openbrowser('https://request-server.s3.amazonaws.com/maps/{0}.jpg'.format(PID))

def open_listing_brochure_in_browser(PID):
	# Open the listing brochure in a browser
	openbrowser('https://request-server.s3.amazonaws.com/listings/{0}_competitors_package.pdf'.format(PID))

# Search company infomation resources for Entity contact
def getEntityContact(ENTITY, STATE='None', CITY='None'):
	from lao import uInput, warningMsg
	# from selenium import webdriver
	# from selenium.webdriver.common.keys import Keys
	from webbrowser import open as openbrowser

	# Clean Entity
	ENTITY = ENTITY.upper()
	ENTITY = ENTITY.replace(',', '').replace('.', '')
	ENTITY = ENTITY.replace('LLC', '').replace('INC', '')
	STATE = STATE.upper()
	driver = None
	openCorpName = True


	openCorpName = ENTITY.replace(' ', '+')
	url = 'https://opencorporates.com/companies?jurisdiction_code=&q={0}'.format(openCorpName)
	openbrowser(url)

# Opens Vizzda Report and returns driver
def openVizzdaReport(vid):
	from lao import click, getUserName
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.chrome.options import Options
	user = getUserName()
	td.uInput(user)
	# Open the Vizzda report page
	options = Options()
	#options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-certificate-errors-spki-list')
	options.add_argument("--disable-infobars")
	options.add_argument('--ignore-ssl-errors')
	# driver = webdriver.Chrome(executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', port=0, chrome_options=options)
	# if user == 'blandis':
	# 	driver = webdriver.firefox()
	# else:
	driver = getSeleniumDriver()
		# driver = webdriver.Chrome(chrome_options=options)
	driver.get(r'https://www2.vizzda.com/login')
	# moveBrowser(driver, 'BL')
	elem = driver.find_element_by_id('user-name')
	elem.send_keys('blandis@landadvisors.com')
	elem = driver.find_element_by_id('Password')
	elem.send_keys('$cottsdale2013')
	elem.send_keys(Keys.RETURN)
	sleep(3)

	click(1200,500)
	print('Logged in...opening Vizzda record web page...\n')
	try:
		driver.get('https://www2.vizzda.com//detail/{0}'.format(vid))
		# driver.get(r'https://www2.vizzda.com/map#/event/{0}'.format(vid))
		print(' Sleeping for 6 seconds...')
		sleep(6)
	except:
		print('\nStill waiting for Vizzda...\n')
		ui = td.uInput('[Enter] to continue or [00] Quit > ')
		if ui.upper() == 'Q' or ui == '00':
			sys.exit('Terminating program...')
	return driver

# Returns Vizzda html or just makes the user selected page come to the front
def vizzdaPage(driver, vizpage, returnhtml=True):
	from lao import warningMsg, uInput
	from selenium.common.exceptions import ElementClickInterceptedException
	dvizpage = {'Contacts': '4', 'History': '3', 'Parcels': '5', 'Summary': '1'}
	while 1:
		print('\n Loading {0} page...please stand by...'.format(vizpage))
		try:
			elem = driver.find_element_by_xpath('//*[@id="detail-tabs"]/li[{0}]/button'.format(dvizpage[vizpage]))
			elem.click()
			break
		except ElementClickInterceptedException as exception:
			warningMsg('\n Error, try scrolling to the top of the Vizzda page.')
			uInput('\n Continue...')
	if returnhtml:
		sleep(1)
		html = driver.page_source
		return html

# Scrape specific Contact HTML
def scrapeContacts(index, driver):
	# print('Scraping Contact Index {0} Data...\n'.format(index))
	# print('Scraping contacts...please stand by...\n')
	elem = driver.find_element_by_xpath('//*[@id="contacts-tab"]/div[1]/ul/li[{0}]'.format(index))
	elem.click()
	sleep(1)
	contact_html = driver.page_source
	return contact_html

def parceAddress(address):
	from lao import zipCodeFindCityStateCountry, warningMsg, uInput
	addList = address.split()
	zipcode = addList[-1]
	if '-' in zipcode and len(zipcode) == 10:
		zipcode = zipcode[:5]
	if not zipcode.isdigit():
		while 1:
			print(address)
			street = (uInput('\n Manually enter Street > ')).upper()
			city = (uInput('\n Manually enter City > ')).upper()
			state = (uInput('\n Manually enter State > ')).upper()
			zipcode = (uInput('\n Manually enter Zipcode > ')).upper()
			print('\n\n Check Addres\n')
			print(' Street:  {0}'.format(street))
			print(' City:    {0}'.format(city))
			print(' State:   {0}'.format(state))
			print(' Zipcode: {0}'.format(zipcode))
			ui = uInput('\n Approve Address [0/1] > ')
			if ui == '1':
				break
			else:
				warningMsg('\n Try again...\n')
	else:
		city, state, country = zipCodeFindCityStateCountry(zipcode)
		street = (address.replace(city, '').replace(state, '').replace(zipcode, '')).strip()
	return street, city, state, zipcode

def printContactInfo(md, roll):
	for row in md:
		if roll in row:
			index = row.split('_')[1]
			rollname = row.split('_')[0]
			print(' Index   : {0}'.format(index))
			print(' Roll    : {0}'.format(rollname))
			print(' Name    : {0}'.format(md[row]['NAME']))
			if not 'Legal' in row:
				if 'STREET' in md[row]:
					print(' Address : {0}'.format(md[row]['STREET']))
				else:
					print(' Address :')
				# City, State Zip
				csz = ''
				if 'CITY' in md[row]:
					csz = '{0}, '.format(md[row]['CITY'])
				if 'STATE' in md[row]:
					csz = '{0} {1}'.format(csz, md[row]['STATE'])
				if 'ZIPCODE' in md[row]:
					csz = '{0} {1}'.format(csz, md[row]['ZIPCODE'])
				print('         : {0}'.format(csz))
				if 'PHONE' in md[row]:
					print(' Phone   : {0}'.format(md[row]['PHONE']))
				else:
					print(' Phone   :')
				if 'EMAIL' in md[row]:
					print(' Email   : {0}'.format(md[row]['EMAIL']))
				else:
					print(' Email   :')
			print('\n-----------------------\n')

def printTFPersonInfo(dperson, pid, entityname):
	print(' PID     : {0}'.format(pid))
	print(' Entity  : {0}\n\n'.format(entityname))
	print(' Person  : {0}'.format(dperson['Name']))
	print(' Address : {0}'.format(dperson['BillingStreet']))
	print('         : {0}, {1} {2}'.format(dperson['BillingCity'], dperson['BillingState'], dperson['BillingPostalCode']))
	print(' Phone   : {0}'.format(dperson['Phone']))
	print(' Email   : {0}'.format(dperson['PersonEmail']))
	print(' ========================================\n\n')

# Builds L5 URL fof specific market
def get_L5_url(LOT, MARKET, PID):

	dL5_URL_Vals = dicts.get_L5_url_dict()

	if LOT == 'P&Z':
		return 'https://maps.landadvisors.com/h5v/?viewer=phoenix.h5v&runWorkflow=ZoomTo&mapid=24&lyr=Ownerships&qry=propertyid=%27{0}%27'.format(PID)
	elif LOT == 'TOP100' or LOT == 'LISTING':
		return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&runWorkflow=ZoomTo&mapid={1}&lyr=Ownerships&qry=PropertyID=%27{2}%27#".format(dL5_URL_Vals[MARKET]['Name'], dL5_URL_Vals[MARKET]['Zoom'], PID)
	elif LOT == 'COMP':
		return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&runWorkflow=ZoomTo&mapid={1}&lyr=Recent%20Sales&qry=pid=%27{2}%27#".format(dL5_URL_Vals[MARKET]['Name'], dL5_URL_Vals[MARKET]['Zoom'], PID)
	elif LOT == 'PIR_Comp':
		return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&runWorkflow=ZoomTo&mapid={1}&lyr=Recent%20Sales&qry=pid=%27{2}%27#".format(dL5_URL_Vals[MARKET]['Name'], dL5_URL_Vals[MARKET]['Zoom'], PID)
	elif LOT == 'CENTER':
		# PID variable contains comma separated lon/lat
		lLL = PID.split(',')
		lon = lLL[0]
		lat = lLL[1]
		return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&center={1},{2},4326&scale=10000#".format(dL5_URL_Vals[MARKET]['Name'], lon, lat)
	else:
		return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&runWorkflow=ZoomTo&mapid={1}&lyr=Ownerships&qry=PropertyID=%27{2}%27#".format(dL5_URL_Vals[MARKET]['Name'], dL5_URL_Vals[MARKET]['Zoom'], PID)
		# return "https://maps.landadvisors.com/h5v/?viewer={0}.h5v&runWorkflow=ZoomTo&mapid={1}&lyr=Recent%20Sales&qry=PropertyID=%27{2}%27#".format(dL5_URL_Vals[MARKET]['Name'], dL5_URL_Vals[MARKET]['Zoom'], PID)

# get webpage html
def getHTML(url, driver='None'):
	from selenium import webdriver
	from selenium.webdriver.chrome.options import Options
	if driver == 'None':
		driver = getSeleniumDriver()
		# options = Options()
		# options.add_argument('--ignore-certificate-errors')
		# options.add_argument('--ignore-certificate-errors-spki-list')
		# options.add_argument("--disable-infobars")
		# options.add_argument('--ignore-ssl-errors')
		# driver = webdriver.Chrome('C:/Program Files/Google/Chrome/Application/chromedriver.exe')
		# driver = webdriver.Chrome(chrome_options=options)
	driver.get(url)
	try:
		driver.switch_to.frame('fraDetail')
	except:
		return 'No web page', '', driver
	sleep(2)
	# driver.switch_to_frame('fraDetail')
	# elem = driver.find_element_by_name('fraDetail')

	html = driver.page_source	
	url = driver.current_url
	return html, url, driver

# Open CoStar in browser
def openCoStar():
	driver = getSeleniumDriver()
	# options = webdriver.ChromeOptions()
	# options.add_argument('--ignore-certificate-errors')
	# options.add_argument('--ignore-certificate-errors-spki-list')
	# options.add_argument("--disable-infobars")
	# options.add_argument('--ignore-ssl-errors')
	# driver = webdriver.Chrome(chrome_options=options)
	# driver = webdriver.Chrome(executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe')
	# driver.get(r'https://gateway.costar.com/Login/?AuthStatus=-3&Request=http%3a%2f%2fgateway.costar.com%2fGateway%2fdefault.aspx')
	# driver.get('http://www.costar.com/')
	driver.get('https://gateway.costar.com/login')
	elem = driver.find_element_by_id('username')
	elem.send_keys('egranger')
	elem = driver.find_element_by_id('password')
	elem.send_keys('landadvisor')
	sleep(10)
	#td.uInput('Continue...')
	elem = driver.find_element_by_id('loginButton')
	elem.click()

	return driver, 'CoStar'

def getReonomyReportHTML(driver, ReonPage, returnhtml=True):
	dReonPage = {'Building & Lots': '1', 'Ownership': '2', 'Sales': '4'}
	print('\n Loading {0} page...please stand by...\n'.format(ReonPage))
	elem = driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[2]/ui-view/main/section/div/section/div/nav/ul/li[{0}]/a'.format(dReonPage[ReonPage]))
	elem.click()
	if returnhtml:
		sleep(1)
		html = driver.page_source
		return html

# Add Competitor Package/Brochure/Flyer to Deal
def addCompetitorPackage(service, DID='None', PID='None'):
	from bb import tf_create_3
	from lao import guiFileOpen, openURL
	from os import rename, remove
	dCP = {}
	dCP['type'] = 'lda_Opportunity__c'
	dCP['Id'] = DID
	filePath = 'F:/Research Department/scripts/awsListings/'
	newFileName = '{0}_competitors_package.pdf'.format(PID)
	file = guiFileOpen(filePath, 'Select PDF', [('PDF', '.pdf'), ('all files', '.*')])
	fileRenamed = '{0}{1}'.format(filePath, newFileName)
	rename(file, fileRenamed)

	print('\n Uploading file...')
	awsUpload(delete_files=True)
	print(' File uploading...')
	dpackage = {}
	dpackage['type'] = 'lda_Package_Information__c'
	dpackage['DealID__c'] = DID
	dpackage['Field_Content__c'] = 'https://request-server.s3.amazonaws.com/listings/{0}'.format(newFileName)
	dpackage['Field_Name__c'] = 'Competitor Package'
	dpackage['Field_Type__c'] = 'URL'
	print('\n Adding package info...')
	tf_create_3(service, dpackage)
	print('Package info added...')
	# openURL('http://requestsXXX.landadvisors.com/listings/{0}'.format(newFileName))

	remove(fileRenamed)

# Upload file to AWS
def awsUpload(delete_files=False):
	td.warningMsg("\n webs.awsUpload function is has been replace with aws.sync_opr_maps_comp_listings_folders_to_s3(delete_files=False)")
	exit('\n Terminating program...')
	# from glob import glob
	# from os import remove, path, makedirs
	# import shutil

	# # Make folder for uploads if they don't exist
	# folder_path = 'C:/Users/Public/Public Mapfiles/awsUpload'
	# if not path.exists(folder_path):
	# 	makedirs(folder_path)
	# 	subfolder_path = f'{folder_path}/Maps'
	# 	makedirs(subfolder_path)
	# 	subfolder_path = f'{folder_path}/Listings'
	# 	makedirs(subfolder_path)

	# # Variables
	# oprMapFilePath = 'C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Maps\\'
	# oprListingsFilePath = 'C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Listings\\'
	# oprListingsArchiveFilePath = 'F:\\Research Department\\Code\\AWS_Upload\\Listings Archive\\'
	# lMaps = glob('C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Maps\\*.*')
	# lCompBrochures = glob('C:\\Users\\Public\\Public Mapfiles\\awsUpload\\Listings\\*.pdf')
	# pprint(lCompBrochures)

	
	# # Copy Maps & Listing Brochures to AWS
	# if not lMaps == []:
	# 	print('\n Uploading to AWS Maps bucket...\n')
	# 	system('aws s3 sync "{0}" s3://request-server/maps/ --acl public-read'.format(oprMapFilePath))
	# 	print(' Upload complete...')
	# 	if delete_files:
	# 		print('\n Deleting source maps...')
	# 		for map in lMaps:
	# 			try:
	# 				remove(map)
	# 			except WindowsError:
	# 				pass
	# if not lCompBrochures == []:
	# 	print('\n Uploading to AWS Listings bucket...\n')
	# 	system('aws s3 sync "{0}" s3://request-server/listings/ --acl public-read'.format(oprListingsFilePath))
	# 	print(' Upload complete...')
	# 	if delete_files:
	# 		for pdf in lCompBrochures:
	# 			# Use full path and file name to move which will overwrite existing file in archive folder
	# 			pdffilename = path.basename(pdf)
	# 			fullpath = '{0}\\{1}'.format(oprListingsArchiveFilePath, pdffilename)
	# 			shutil.move(pdf, fullpath)

# Check if file exists on AWS
def awsFileExists(fileName):
	td.warningMsg("awsFileExists function is has been replace with aws.aws_file_exists(filename, extention='jpg', verbose=False")
	exit('\n Terminating program...')
	# import requests

	# if '.pdf' in fileName:
	# 	r = requests.get('https://request-server.s3.amazonaws.com/listings/{0}'.format(fileName))
	# else:
	# 	# r = requests.get('https://request-server.s3.amazonaws.com/maps/{0}.jpg'.format(fileName))
	# 	r = requests.get('https://request-server.s3.amazonaws.com/maps/{0}.png'.format(fileName))

	# if r.status_code == 200:
	# 	return True
	# else:
	# 	return False

#3 Get the Selenium driver and trap for old Chromedriver version
def getSeleniumDriver(win_width='None', win_height='None', pos_x='None', pos_y='None'):
	from lao import openURL, uInput
	from fun_text_date import warningMsg
	from selenium import webdriver
	from selenium.webdriver.chrome.service import Service
	from selenium.webdriver.chrome.options import Options
	from selenium.common.exceptions import SessionNotCreatedException

	# service = Service(r'F:\Research Department\Code\Chromedriver\Chrome1\chromedriver.exe')
	# service = Service(r'F:\Research Department\Code\Chromedriver\Chrome2\chromedriver.exe')
	options = Options()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-certificate-errors-spki-list')
	options.add_argument("--disable-infobars")
	options.add_argument('--ignore-ssl-errors')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# Set window size
	if win_width != 'None':
		options.add_argument('window-size={0},{1}'.format(win_width, win_height))
	# Open Chrome
	try:
		service = Service(r'F:\Research Department\Code\Chromedriver\Chrome1\chromedriver.exe')
		driver = webdriver.Chrome(service=service, options=options)
	except SessionNotCreatedException:
		warningMsg('\n Chrome1 failed...trying Chrome2...')
	try:
		service = Service(r'F:\Research Department\Code\Chromedriver\Chrome2\chromedriver.exe')
		driver = webdriver.Chrome(service=service, options=options)
	except SessionNotCreatedException:
		warningMsg('\n Chrome2 failed...trying Chrome2...')
		warningMsg('\n Chromedriver needs to be updated.')
		print(f'n MAKE BILL READ THIS MESSAGE!\n\n Copy the new version to:\n\n    F:/Research Department/Code/Chromedriver\n\n Download from https://googlechromelabs.github.io/chrome-for-testing/\n\n chromedriver-64.zip')
		# openURL('https://chromedriver.chromium.org/downloads')
		openURL('https://googlechromelabs.github.io/chrome-for-testing/')
		uInput('\n Continue... > ')
		exit('\n Terminating program...')
	# Set window position
	if pos_x != 'None':
		driver.set_window_position(pos_x, pos_y, windowHandle='current')
	return driver

# Validate email(s) and return good ones
def email_validation(lEmails, return_description=True):
	import requests
	import json

	# Emails must be a new line separated string. Check if list
	if isinstance(lEmails, list):
		if len(lEmails) == 1:
			emails = lEmails[0]
			is_single_email = True
		else:
			# Join list as line separated string
			emails = '\n'.join(lEmails)
			is_single_email = False
	else:
		emails = lEmails
		is_single_email = True
	
	# Validate single or batch
	if is_single_email:
		url = 'https://cfworker-lao-email-validation.landadvisors.workers.dev/single'
		
	else:
		url = 'https://cfworker-lao-email-validation.landadvisors.workers.dev/batch'
	
	headers = {'content-type': 'application/json'}
	body = {'email': emails}
	r = requests.post(url, headers=headers, json=body)
	dResults = json.loads(r.text)

	
	# print('here1')
	# pprint(dResults)
	# ui = td.uInput('\n Continue [00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	

	# Insert result into dictionary
	lEmails_sort, primary_email, str_tf_email_description = [], 'None', 'None'
	
	# Insufficient funds trap
	insufficient_balance = False
	if 'message' in dResults:
		if 'data' in dResults:
		# if 'Insufficient balance' in dResults:
			if dResults['data'][0]['message'] == 'Insufficient balance':
				insufficient_balance = True
		elif dResults['message'] is None:
			pass
		elif 'Insufficient balance' in dResults['message']:
			insufficient_balance = True
	if insufficient_balance:
		if is_single_email:
			primary_email = lEmails[0]
		else:
			str_tf_email_description = 'Possible Emails:'
			for row in lEmails:
				str_tf_email_description = '{0}\n {1}'.format(str_tf_email_description, row[0])
		return primary_email, str_tf_email_description

	# Return results if single email. May return None values if no good email found.
	if is_single_email:
		if dResults['result'] != 'undeliverable':
			primary_email = dResults['email']
		return primary_email, str_tf_email_description

	# Process multiple emails
	for row in dResults['data']:
		if row['result'] != 'undeliverable':
			intSendex = int(float(row['sendex']) * 100)
			lEmails_sort.append([row['email'], intSendex])
	
	# No Emails
	if lEmails_sort == []:
		return 'None', 'Possible Emails:'

	# If only one good email is found return it as the primary email and None Description
	if len(lEmails_sort) == 1:
		primary_email = lEmails_sort[0][0]
		return primary_email, str_tf_email_description

	# Determine best email primary email and a TF Description of the rest
	# Sort by sendex
	lEmails_sort.sort(key=lambda x: x[1], reverse=True)

	pprint(lEmails_sort)

	primary_email = lEmails_sort[0][0]
	str_tf_email_description = 'Possible Emails:'
	for row in lEmails_sort:
		str_tf_email_description = '{0}\n {1}'.format(str_tf_email_description, row[0])

	if return_description:
		return primary_email, str_tf_email_description
	else:
		return primary_email

# Google & Email domain open browser
def open_google_email_domain_browser(dAcc):
	if dAcc['ISBROWSEROPEN'] == False:
		if dAcc['STREET'] == 'None':
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(dAcc['ENTITY']))
		else:
			lao.openbrowser('https://www.google.com.tr/search?q={0}+{1}+{2}+{3}+{4}'.format(dAcc['ENTITY'], dAcc['STREET'], dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))
		if dAcc['EMAIL'] != 'None':
			domain = dAcc['EMAIL'].split('@')
			domain = domain[1]
			lao.openbrowser('https://{0}'.format(dAcc['EMAIL']))
		dAcc['ISBROWSEROPEN'] = True
	return dAcc

# Connect to the Google Sheet
def gs_connect(sheet_name):
	from google.oauth2.service_account import Credentials
	import gspread
	import os
	# Path to the service account credentials JSON file
	SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), 'workspaces-339922-bb678e67b28b.json')

	# The scopes required for Google Sheets API
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

	# Authenticate and construct the service
	credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

	gc = gspread.authorize(credentials)

	# Open the Google Sheet using its name or ID
	if sheet_name == 'Foreclosure':
		spreadsheet_id = '1z7c8IyI8M9fNBu2pF1irMZmz-xXm9RhT-DH1g8_4h-k'
	elif sheet_name == 'Debt':
		spreadsheet_id = '1w88EfdoJXOGHLh0SlvBywQvPanGjMTmwf9B8boh_Uew'
	spreadsheet = gc.open_by_key(spreadsheet_id)

	return spreadsheet

# Update the Google Sheet
def update_gs(sheet_name, lData):
	from google.oauth2.service_account import Credentials
	import gspread
	import os

	# sheet_name = 'Foreclosure' or 'Debt'
	# lData is a list of lists to write to the Google Sheet

	# Connect to the Google Sheet
	# Path to the service account credentials JSON file
	SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), 'workspaces-339922-bb678e67b28b.json')

	# The scopes required for Google Sheets API
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

	# Authenticate and construct the service
	credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

	gc = gspread.authorize(credentials)

	# Open the Google Sheet using its name or ID
	if sheet_name == 'Foreclosure':
		spreadsheet_id = '1z7c8IyI8M9fNBu2pF1irMZmz-xXm9RhT-DH1g8_4h-k'
	elif sheet_name == 'Debt':
		spreadsheet_id = '1w88EfdoJXOGHLh0SlvBywQvPanGjMTmwf9B8boh_Uew'
	spreadsheet = gc.open_by_key(spreadsheet_id)

	# Select the worksheet by name or index. For example, by index:
	worksheet = spreadsheet.get_worksheet(0)  # 0 means the first worksheet
	# Write the records to Google Sheets
	worksheet.update(lData)

# Open website in browser
def open_contact_websites(dAcc, website):
	lao.print_function_name(f'webs def open_contact_websites: website={website}')

	# Domain from email
	if website == 'Domain' or website == '40':  # text will be Entity name
		if dAcc['EMAIL'] != 'None':
			domain = dAcc['EMAIL'].split('@')
			domain = domain[1]
			lao.openbrowser('https://{0}'.format(dAcc['EMAIL']))
		else:
			td.warningMsg('\n No email given...')
			sleep(3)
	if website == 'TerraForce' or website == '41':
		import pyperclip
		if dAcc['EMAIL'] != 'None':
			domain = dAcc['EMAIL'].split('@')
			domain = domain[1]
			pyperclip.copy(domain)
			lao.openbrowser('https://landadvisors.lightning.force.com/lightning/page/home')
		else:
			td.warningMsg('\n No email given...')
			sleep(3)

	# Google Enity Name & Adedress
	elif website == 'Google Contact Name & Address' or website == '10':
		if dAcc['ENTITY'] != 'None':
			name_address = dAcc['ENTITY'].replace(' ', '%20')
			if dAcc['STREET'] != '10':
				street = dAcc['STREET'].replace(' ', '%20')
				city = dAcc['CITY'].replace(' ', '%20')
				state = dAcc['STATE'].replace(' ', '%20')
				zipcode = dAcc['ZIPCODE'].replace(' ', '%20')
				name_address = f'{name_address}%20{street}%20{city}%20{state}%20{zipcode}'
				# print(f'\n Name & Address: {name_address}')
				lao.openbrowser(f'https://www.google.com.tr/search?q={name_address}')
			else:
				td.warningMsg('\n Entity Address is "None", seaching Google for Entity/Person only.\n')
				lao.openbrowser(f'https://www.google.com.tr/search?q={name_address}')
				lao.sleep(3)
				
		else:
			td.warningMsg('\n Entity name is "None", select a different option.\n')

	# Google Enity Name
	elif website == 'Google Contact Name' or website == '11':
		if dAcc['ENTITY'] != 'None':
			entity = dAcc['ENTITY'].replace(' ', '%20')
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(entity))
		else:
			td.warningMsg('\n Entity name is "None", select a different option.\n')


	# Google Person Name & Address
	elif website == 'Google Contact Name & Address' or website == '12':
		if dAcc['NAME'] != 'None':
			name_address = dAcc['NAME'].replace(' ', '%20')
			if dAcc['STREET'] != 'None':
				street = dAcc['STREET'].replace(' ', '%20')
				city = dAcc['CITY'].replace(' ', '%20')
				state = dAcc['STATE'].replace(' ', '%20')
				zipcode = dAcc['ZIPCODE'].replace(' ', '%20')
				name_address = f'{name_address}%20{street}%20{city}%20{state}%20{zipcode}'
				# print(f'\n Name & Address: {name_address}')
				lao.openbrowser(f'https://www.google.com.tr/search?q={name_address}')
			else:
				td.warningMsg('\n Person Address is "None", select a different option.\n')
		else:
			td.warningMsg('\n Person name is "None", select a different option.\n')
		
		# Google Person Name
	elif website == 'Google Contact Name' or website == '13':
		if dAcc['NAME'] != 'None':
			entity = dAcc['NAME'].replace(' ', '%20')
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(entity))
		else:
			td.warningMsg('\n Person name is "None", select a different option.\n')

	# Google Address
	elif website == 'Google Address' or website == '14':
		if dAcc['STREET'] != 'None':
			address = f'{dAcc["STREET"]} {dAcc["CITY"]} {dAcc["STATE"]} {dAcc["ZIPCODE"]}'
			address = address.replace(' ', '%20')
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(address))
		else:
			td.warningMsg('\n Address is "None", select a different option.\n')

	# Google Contact Email
	elif website == 'Google Email' or website == '15':
		if dAcc['EMAIL'] != 'None':
			entity = dAcc['EMAIL']
			lao.openbrowser('https://www.google.com.tr/search?q={0}'.format(entity))
		else:
			td.warningMsg('\n Email is "None", select a different option.\n')

	# Arizona Corporation Commission
	elif website == 'Arizona Corporation Commission' or website == '20':  # text will be Entity name
		# Paste Entity into clipboard
		if dAcc['ENTITY'] != 'None':
			import pyperclip
			pyperclip.copy(dAcc['ENTITY'])
		lao.openbrowser('https://ecorp.azcc.gov/EntitySearch/Index/')

	# Dunn & Bradstreet Hoovers subscription
	elif website == 'Dunn & Bradstreet Hoovers' or website == '21':  # text will be Entity name
		if dAcc['ENTITY'] != 'None':
			entity = dAcc['ENTITY'].replace(' ', '%20')
			lao.openbrowser('https://app.dnbhoovers.com/search/results/company?q={0}'.format(entity))
		else:
			dAcc['ENTITY'] = td.uInput('\n Type Entity name or [Enter] for none > ')
			if dAcc['ENTITY'] == '':
				dAcc['ENTITY'] = 'None'
				lao.openbrowser('https://app.dnbhoovers.com/')
			else:
				entity = dAcc['ENTITY'].replace(' ', '%20')
				lao.openbrowser('https://app.dnbhoovers.com/search/results/company?q={0}'.format(entity))

	# Fast People Search
	elif website == 'FastPeopleSearch' or website == '22':
		if dAcc['NAME'] != 'None':
			if dAcc['CITY'] == 'None':
				dAcc['CITY'] = td.uInput('\n Enter City > ')
			if dAcc['STATE'] == 'None':
				dAcc['STATE'] = td.uInput('\n Enter 2 Letter State > ')
			dAcc = td.parse_person(dAcc, ask_name_arragement_possiblities=False)
			if 'NM' in dAcc:
				if dAcc['NM'] == '':
					fps_name = '{0}-{1}'.format(dAcc['NF'], dAcc['NL'])
				else:
					fps_name = '{0}-{1}-{2}'.format(dAcc['NF'], dAcc['NM'], dAcc['NL'])
			else:
				dAcc['NM'] = ''
				fps_name = '{0}-{1}'.format(dAcc['NF'], dAcc['NL'])
			lao.openbrowser('https://www.fastpeoplesearch.com/name/{0}_{1}-{2}'.format(fps_name.lower(), dAcc['CITY'].lower(), dAcc['STATE'].lower()))
		else:
			lao.openbrowser('https://www.fastpeoplesearch.com/')

	# Sunbiz
	elif website == 'Sunbiz' or website == '23':
		if dAcc['ENTITY'] != 'None':
			entity = dAcc['ENTITY'].upper()
			EntityName = entity.replace(' ', '%20')
			searchNameOrder = entity.replace(' ', '')
			lao.openbrowser('https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults/EntityName/{0}/Page1?searchNameOrder{1}'.format(EntityName, searchNameOrder))
		else:
			lao.openbrowser('https://search.sunbiz.org/Inquiry/CorporationSearch/ByName')

	# OpenCorporates
	elif website == 'OpenCorporates' or website == '24':
		if dAcc['ENTITY'] != 'None':
			entity = dAcc['ENTITY'].replace(' ', '+')
			lao.openbrowser('https://opencorporates.com/companies/country/us?q={0}'.format(entity))
		else:
			lao.openbrowser('https://opencorporates.com/')

	# Real Yellow Pages
	elif website == 'Yellow Pages' or website == '25':
		if dAcc['ENTITY'] != 'None':
			entity = dAcc['ENTITY'].replace(' ', '+')
			lao.openbrowser('https://www.yellowpages.com/search?search_terms={0}'.format(entity))
		else:
			lao.openbrowser('https://www.yellowpages.com/')

	# TruePeopleSearch Name
	elif website == 'TruePeopleSearch' or website == 'TruePeopleSearch Name' or website == '30':
		if dAcc['NAME'] != 'None':
			# print('here1')
			dAcc = td.parse_person(dAcc, ask_name_arragement_possiblities=False)
			# if dAcc.has_key('NM'):
			if 'NM' in dAcc:
				if dAcc['NM'] == '':
					tps_name = '{0}%20{1}'.format(dAcc['NF'], dAcc['NL'])
				else:
					tps_name = '{0}%20{1}%20{2}'.format(dAcc['NF'], dAcc['NM'], dAcc['NL'])
			else:
				dAcc['NM'] = ''
				tps_name = '{0}%20{1}'.format(dAcc['NF'], dAcc['NL'])
			# User to enter City and State if missing
			if dAcc['CITY'] == 'None':
				td.colorText('\n TruePeopleSearch requires City and State', 'CYAN')
				ui = td.uInput('\n Type City or [Enter] for none > ')
				if ui == '00':
					exit('\n Terminating program...')
				elif ui == '':
					pass
				else:
					dAcc['CITY'] = ui.title()
					ui = td.uInput('\n Type 2 letter State or [Enter] for none > ')
					if ui == '00':
						exit('\n Terminating program...')
					elif ui == '':
						pass
					else:
						dAcc['STATE'] = ui.upper()
			if dAcc['CITY'] != 'None' and dAcc['STATE'] != 'None':
				city_no_space = dAcc['CITY'].replace(' ', '%20')
				lao.openbrowser('https://www.truepeoplesearch.com/results?name={0}&citystatezip={1},%20{2}'.format(tps_name, city_no_space, dAcc['STATE']))
			else:
				lao.openbrowser('https://www.truepeoplesearch.com/')
		else:
			lao.openbrowser('https://www.truepeoplesearch.com/')

	# TruePeopleSearch Address
	elif website == 'TruePeopleSearch Address' or website == '31':
		if dAcc['STREET'] != 'None':
			street = dAcc['STREET'].replace(' ', '%20')
			city_no_space = dAcc['CITY'].replace(' ', '%20')
			city_state = '{0},%20{1}'.format(city_no_space, dAcc['STATE'])
			lao.openbrowser(f'https://www.truepeoplesearch.com/resultaddress?streetaddress={street}&citystatezip={city_state}')
		else:
			lao.openbrowser('https://www.truepeoplesearch.com/')
	
	# USA People Search Name
	elif website == 'USA-People-Search' or website == '32':
		if dAcc['NAME'] != 'None':

			if dAcc['CITY'] == 'None':
				dAcc['CITY'] = td.uInput('\n Enter City > ')
			if dAcc['STATE'] == 'None':
				dAcc['STATE'] = td.uInput('\n Enter 2 Letter State > ')

			dAcc = td.parse_person(dAcc, ask_name_arragement_possiblities=False)
			if 'NM' in dAcc:
				if dAcc['NM'] == '':
					usaps_name = '{0}-{1}'.format(dAcc['NF'], dAcc['NL'])
				else:
					usaps_name = '{0}-{1}-{2}'.format(dAcc['NF'], dAcc['NM'], dAcc['NL'])
			else:
				dAcc['NM'] = ''
				usaps_name = '{0}-{1}'.format(dAcc['NF'], dAcc['NL'])
			lao.openbrowser('https://www.usa-people-search.com/name/{0}/{1}-{2}'.format(usaps_name.lower(), dAcc['CITY'].lower(), dAcc['STATE'].lower()))
		else:
			lao.openbrowser('https://www.usa-people-search.com/')
	
	# EnformionGO API
	elif website == 'EnformionGO Enhanced' or website == '34':
		import ego

		if dAcc['NAME'] != 'None':

			if dAcc['CITY'] == 'None':
				dAcc['CITY'] = td.uInput('\n Enter City > ')
				dAcc['CITY'] = dAcc['CITY'].title()
			if dAcc['STATE'] == 'None':
				while 1:
					dAcc['STATE'] = td.uInput('\n Enter 2 Letter State > ')
					if len(dAcc['STATE']) == 2:
						dAcc['STATE'] = dAcc['STATE'].upper()
						break
					else:
						td.warningMsg('\n State must be 2 letters')

			dAcc = td.parse_person(dAcc, ask_name_arragement_possiblities=False)

			dAcc = ego.run_EnformionGO_enrichment_search(dAcc)

	elif website == 'EnformionGO Entity' or website == '35':
		import ego

		if dAcc['ENTITY'] == 'None':
			td.warningMsg('\n Entity name is "None", select a different option.\n')
		else:
			if dAcc['CITY'] == 'None':
				dAcc['CITY'] = td.uInput('\n Enter City > ')
				dAcc['CITY'] = dAcc['CITY'].title()
			if dAcc['STATE'] == 'None':
				while 1:
					dAcc['STATE'] = td.uInput('\n Enter 2 Letter State > ')
					if len(dAcc['STATE']) == 2:
						dAcc['STATE'] = dAcc['STATE'].upper()
						break
					else:
						td.warningMsg('\n State must be 2 letters')

			dAcc = ego.run_EnformionGO_entity_search(dAcc)
	# AI
	elif website == 'AI Prompt' or website == '50':
		import pyperclip

		file_path = r"F:\Research Department\Code\Databases\Find Company Owner AI Prompt v01.txt"
			# Read the file content
		with open(file_path, 'r', encoding='utf-8') as file:
			content = file.read()
			
			# Add Entity and Address to the prompt
		content = content.replace('**[COMPANY_NAME]**', dAcc['ENTITY'])

		if dAcc['STREET'] != 'None':
			
			content = content.replace('**[COMPANY_ADDRESS]**', f"{dAcc['STREET']}, {dAcc['CITY']}, {dAcc['STATE']} {dAcc['ZIPCODE']}")

			# Copy to clipboard
		pyperclip.copy(content)
			
		print(f"Successfully copied AI prompt to clipboard!")


	
	return dAcc

