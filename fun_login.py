# Login to various LAO services

# ArcGIS Online login
def LAO_ArcGIS_portal():
	from arcgis.gis import GIS
	from dotenv import load_dotenv
	import os

	load_dotenv()
	username = os.getenv("ARCGIS_USERNAME")
	password = os.getenv("ARCGIS_PASSWORD")

	gis = GIS("https://maps.landadvisors.com/portal", username, password, verify_cert=False)
	return gis

# Crexi login
def crexi():
	import dicts
	import lao
	from selenium import webdriver
	from selenium.webdriver.common.by import By
	from selenium.webdriver.chrome.options import Options
	from webs import getSeleniumDriver
	import fun_text_date as td

	# Load LAO_Staff_Db_v03.xlsx into a dictionary with the Names as keys
	dStaff = dicts.get_staff_dict_2()
	# Get the user name of the operator
	# The username is used to find the password and token in the dStaff dictionary
	user = lao.getUserName()
	print(f'📡 Logging into Crexi as {user}...')
	# Cycle through the staff dictionary (dStaff) to find the user and get their password and token
	for person in dStaff:
		if user == dStaff[person]['Email']:
			password = dStaff[person]['Crexi Password']
			break

	options = Options()
	# Anti-bot blocking
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option("useAutomationExtension", False) 
	# Other options
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-certificate-errors-spki-list')
	options.add_argument("--disable-infobars")
	options.add_argument('--ignore-ssl-errors')
	driver = getSeleniumDriver()
	driver.get(r'https://www.crexi.com/')
	lao.sleep(5)

	loginFailed = True
	try:
		elem = driver.find_element(By.XPATH, '/html/body/crx-app/div/crx-home-page/crx-normal-page/div/crx-header/crx-header-content/div/div/crx-logged-out-header/button')
		loginFailed = False
	except:
		print(' failed 1')
		ui = lao.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		lao.sleep(1)
	if loginFailed:
		td.warningMsg('\n Crexi login failed...call Bill.')
		exit(' Crexi login failed')

	elem.click()
	lao.sleep(1)
	# Sign Up or Log In form button
	try:
		elem = driver.find_element(By.XPATH, '//*[@id="mat-mdc-dialog-title-0"]/div/button[2]')
		elem.click()
		lao.sleep(1)
	except:
		print(' Sign Up or Log In form button click failed')
		ui = lao.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	# Enter user's Email 
	try:
		elem = driver.find_element(By.XPATH, '//*[@id="auto-group-3"]/crx-auto-ctrl[1]/cui-form-field/div/div/div/crx-ctrl-switch/crx-ctrl-input/input')
		elem.send_keys('{0}@landadvisors.com'.format(user))
		lao.sleep(1)
	except:
		print(' Enter user Email failed')
		ui = lao.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	# Enter user's Password
	try:
		elem = driver.find_element(By.XPATH, '//*[@id="auto-group-3"]/crx-auto-ctrl[2]/cui-form-field/div/div/div/crx-ctrl-switch/crx-ctrl-input/input')
		elem.send_keys(password)
		lao.sleep(1)
	except:
		print(' Enter user Password failed')
		ui = lao.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	# Log In button
	button_click_failed = False
	try:
		# elem = driver.find_element(By.XPATH, '//*[@id="login-form"]/button')
		elem = driver.find_element(By.XPATH, '//*[@id="mat-mdc-dialog-1"]/div/div/ng-component/div[2]/button[1]')
		elem.click()
	except:
		print(' Log In button click failed 1')
		button_click_failed = True
		ui = lao.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	if button_click_failed:
		try:
			elem = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/button[1]')
			elem.click()
		except:
			td.warningMsg('Log In button click failed 2')
			ui = lao.uInput('\n Continue [00]... > ')
			if ui == '00':
				exit('\n Terminating program...')

	print('\n Crexi login successful...')

	return driver

# Create MC Client 
def MailChimp():
	import lao
	import dicts
	from mailchimp3 import MailChimp

	# Load LAO_Staff_Db_v03.xlsx into a dictionary with the Names as keys
	dStaff = dicts.get_staff_dict_2()
	user = lao.getUserName(initials=False)
	print(f'📡 Logging into MailChimp as {user}...')
	# Cycle through the staff dictionary (dStaff) to find the user and get their password and token
	for person in dStaff:
		if user == dStaff[person]['Email']:
			if user == 'blandis':
				username = 'Deh5Ykael'
			else:
				username = f'{user}@landadvisors.com'
			token = dStaff[person]['MC Token']
			break
	
	print(f' MailChimp username: {username}')
	print(f' MailChimp token: {token}')
	client = MailChimp(token, username)

	return client

# RED News login
def RED_News():
	from lao import sleep
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.keys import Keys
	from webs import getSeleniumDriver
	from dotenv import load_dotenv
	import os

	load_dotenv()
	username = os.getenv("RED_NEWS_USERNAME")
	password = os.getenv("RED_NEWS_PASSWORD")

	print('📡 Logging into RED News...')
	driver = getSeleniumDriver()
	driver.get(r'https://realestatedaily-news.com/wp-login.php')
	# //*[@id="user_login"]
	# exit()
	sleep(2)
	elem = driver.find_element(By.ID, "user_login")
	elem.send_keys(username)
	elem = driver.find_element(By.ID,'user_pass')
	elem.send_keys(password)
	elem.send_keys(Keys.RETURN)
	sleep(2)
	return driver

# Login to LAO SalesForce account, Returns service
def TerraForce():  #SalesForceService
	import lao
	import dicts
	from simple_salesforce import Salesforce

	# Load LAO_Staff_Db_v03.xlsx into a dictionary with the Names as keys
	dStaff = dicts.get_staff_dict_2()
	# Get the user name of the operator
	# The username is used to find the password and token in the dStaff dictionary
	user = lao.getUserName()
	print(f'📡 Logging into Terraforce as {user}...')
	# Cycle through the staff dictionary (dStaff) to find the user and get their password and token
	for person in dStaff:
		if user == dStaff[person]['Email']:
			username = f'{user}@landadvisors.com'
			password = dStaff[person]['SF Password']
			token = dStaff[person]['SF Token']
			break
	# print(f' User: {username}\n Password: {password} \nToken: {token}')
	# Login to SalesForce using the simple_salesforce library
	service = Salesforce(username, password, token)
	return service
# Login to RED News



