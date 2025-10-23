# python3

import aws
from lao import *
import bb
import dicts
import fjson
import fun_login
from os import startfile, system
import tkinter as tk
from tkinter import *
from tkinter import messagebox


# Get App name and file library
def getAppsData():
	# d = spreadsheetToDict('{0}GUI_PY3_Apps_Library_v01.xlsx'.format(getPath('pyData')))
	# d = dicts.spreadsheet_to_dict('F:/Research Department/Code/RP3/data/GUI_PY3_Apps_Library_v01.xlsx')
	d = dicts.spreadsheet_to_dict('F:/Research Department/Code/Databases/GUI_Apps_Db_PY3_v01.xlsx')
	lAppNames, lFolders, lExcel = [], [], []
	for row in d:
		if d[row]['Type'] == 'Map':
			continue
		elif d[row]['Type'] == 'Excel':
			lExcel.append(d[row]['Name'])
		elif d[row]['Type'] == 'Folder':
			lFolders.append(d[row]['Name'])
		elif user == 'blandis':
			lAppNames.append(d[row]['Name'])
		elif d[row]['User'] == 'All':
			lAppNames.append(d[row]['Name'])
	return d, lAppNames, lFolders, lExcel

# Move the window to the user's perfered location
def center_window(width=1000, height=200):
	# root.geometry('%dx%d+%d+%d' % (width, height, "X", "Y"))
	if user == 'blandis':
		screenwidth = root.winfo_screenwidth()
		screenheight = root.winfo_screenheight()
		# print(screenwidth)
		# print(screenheight)
		# exit()
		if screenwidth == 1920 and screenheight == 1080:
			bill_location = 'Home'
		elif screenwidth == 3840 and screenheight == 2160:
			bill_location = 'Bressan'
		else:
			bill_location = 'LAO'

		# LAO or Home Computer
		if bill_location == 'LAO':
			root.geometry('%dx%d+%d+%d' % (width, height, 3840, 1120))
			# root.geometry('%dx%d+%d+%d' % (width, height, 0, 0))
		elif bill_location == 'Home':
			root.geometry('%dx%d+%d+%d' % (width, height, 6, -82))
		elif bill_location == 'Bressan':
			root.geometry('%dx%d+%d+%d' % (width, height, 0, 0))
	elif user == 'avidela':
		root.geometry('%dx%d+%d+%d' % (width, height, 0, 0))
	elif user == 'lkane':
		# In office
		# root.geometry('%dx%d+%d+%d' % (width, height, 0, 1360))
		# Working from home
		root.geometry('%dx%d+%d+%d' % (width, height, 0, 0))
	# Interns
	elif user == 'zhahn':
		root.geometry('%dx%d+%d+%d' % (width, height, 1920, 970))
	else:
		root.geometry('%dx%d+%d+%d' % (width, height, 0, 0))

# Process text box contents
def buttonSubmit():
	# Update button to show processing
	btnSubmit.config(text='Stand By', bg='yellow', fg='black')
	root.update()  # Force GUI update
	service = fun_login.TerraForce()
	market = menuMarketsDefault.get()
	textValue1 = txtbox_PID_LID_APN.get()
	textValue1 = textValue1.strip()
	if 'PID_LeadID_APN_Gmap_Co_Person' in textValue1 or textValue1 == '':
		messagebox.showerror('ERROR', 'Invalid entry...\n\nEnter a\n\nPID,\nLead ID\nParcel APN\nGoogle Map Link\nLon Lat\nCompany Name\nPerson\n\nin the text box.')
	
	# VIZZDA: Check if Vizzda ID and open Vizzda record
	elif market == 'Vizzda':
		textValue1 = bb.openVizzdaReturnPID(service, textValue1)
		if textValue1 == 'None':
			messagebox.showerror('ERROR', 'Vizzda ID not found.')
			return
	
		#  https://www.google.com/maps/@33.5006434,-111.9403254,6204m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI1MDYyMy4wIKXMDSoASAFQAw%3D%3D

	# GOOGLE MAPS: Create Zoom to Polygon json file from Google Maps url
	elif 'google.com' in textValue1:
		# Extract longitude and latitude from url
		lat = str(textValue1.split('@')[1].split(',')[0].strip())
		lon = str(textValue1.split('@')[1].split(',')[1].strip())
		fjson.create_ZoomToPolygon_json_file(fieldname=None, polyId=None, polyinlayer=None, lon=lon, lat=lat, market=market)

	# LEAD: Check if Lead ID (LID) and create Zoom to Polygon json file
	elif '_' in textValue1:
		LID = textValue1
		dLID = getLIDDict(LID)
		fjson.create_ZoomToPolygon_json_file(fieldname='leadid', polyId=LID, polyinlayer=dLID['leadLayerName'], lon=None, lat=None)
		return
	
	# Enter Enity or Person into TF
	elif ' ' in textValue1 and textValue1[:1] != '-' and not textValue1[:2].isdigit():
		scriptPath = 'F:/Research Department/Code/RP3/TF_Contact_Entry_v01.py'
		# Create json file with the contact name
		fjson.create_tf_contact_entry_file(textValue1)
		fjson.createScriptToLauchFile(scriptPath)
		startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')
		
	# PID: Check if PID and create Zoom to Polygon json file and open PID in browser
	elif textValue1[:2] in lStatesAbb:
		PID = textValue1
		DID = bb.openTFPID(service, PID)
		if DID == 'None':
			messagebox.showerror('ERROR', 'PID not found.')
		else:
			# Create Zoom to Polygon json file for PID
			fjson.create_ZoomToPolygon_json_file(fieldname='pid', polyId=PID, polyinlayer='OwnerIndex', lon=None, lat=None, market=None)
			# Create PIDOID json file
			aws.read_Write_PID_OID(PID=PID, OID='Write')
	
	# LON/LAT: Copied from TF
	elif 'Latitude' in textValue1:
		corrdinates = textValue1.replace('Longitude', '')
		corrdinates = corrdinates.split('Latitude')
		lon = corrdinates[0].strip()
		lat = corrdinates[1].strip()
		fjson.create_ZoomToPolygon_json_file(fieldname=None, polyId=None, polyinlayer=None, lon=lon, lat=lat, market=market)
		
	# LON/LAT: Create zoom to Polygon json file for longitude and latitude
	elif textValue1[0] == '-' and textValue1[1].isdigit():
		corrdinates = textValue1.split()
		lon = corrdinates[0].strip()
		lat = corrdinates[1].strip()
		fjson.create_ZoomToPolygon_json_file(fieldname=None, polyId=None, polyinlayer=None, lon=lon, lat=lat, market=market)
	
	

	
	# APN: Else textvalue1 is an APN and create Zoom to Polygon json file
	else:
		county = menuCountiesDefault.get()
		market = menuMarketsDefault.get()
		
		if market == 'Market' or market == 'Vizzda':
			messagebox.showerror('ERROR', 'Market not selected.')
			return
		elif county == 'County':
			messagebox.showerror('ERROR', 'County not selected.')
			return
		dCounties = getCounties('FullDict')
		for row in dCounties:
			if county == dCounties[row]['ArcName'] and market == dCounties[row]['Market']:
				polyinlayer = '{0}Parcels{1}'.format(dCounties[row]['State'], county)
				break
		# Format APN
		APN = txtbox_PID_LID_APN.get()
		APN = APN.strip()
		APN = APN.upper()
		# Make Zoom to Polygon json file
		fjson.create_ZoomToPolygon_json_file(fieldname='apn', polyId=APN, polyinlayer=polyinlayer, lon=None, lat=None, market=market)
	# Reset Submit button
	btnSubmit.config(text='Submit', bg='black', fg='cyan')
	root.update()  # Force GUI update

def getLIDDict(LID):
	from lao import getCounties

	leadCounty = LID.split('_')
	lid_state = leadCounty[0]
	lid_county = leadCounty[1]

	dCounties = getCounties('FullDict')
	for row in dCounties:
		dSelectedCounty = dCounties[row]
		if lid_state == dCounties[row]['State']:
			if lid_county == dCounties[row]['ArcName']:
				break

	d = {'LID': LID}
	d['county'] = dSelectedCounty['ArcName']
	d['marketAbb'] = dSelectedCounty['MarketAbb']
	d['stateAbb'] = dSelectedCounty['State']
	d['market'] = dSelectedCounty['Market']
	d['leadLayerName'] = dSelectedCounty['ParcelsName'].replace('Parcels', 'Leads')
	return d

def openInBrowser(app):
	market = menuMarketsDefault.get()
	txtValue = txtbox_PID_LID_APN.get().strip()
	# service = sfLogin()
	service = fun_login.TerraForce()
	
	if app.strip() == 'L5':
		if txtValue[:2] in lStatesAbb: # txtValue is a PID
			market = getLeadDealData(service, txtValue, dealVar='Market')
			stageName = getLeadDealData(service, txtValue, dealVar='StageName')
			if 'Closed' in stageName:
				LOT = 'COMP'
			else:
				LOT = 'TOP100'
			url = get_L5_url(LOT, market, txtValue)
		else:
			url = getDictValue(dApps, 'Name', market, 'File')
	elif app.strip() == 'Google Maps':
		if txtValue[:2] in lStatesAbb: # txtValue is a PID
			lon, lat = getLeadDealData(service, txtValue, dealVar='LonLat')
			url = 'https://www.google.com/maps/@{0},{1},3000m/data=!3m1!1e3'.format(lat, lon)
		else:
			url = getDictValue(dApps, 'Name', market, 'Path')
	else:
		url = getDictValue(dApps, 'Name', app, 'Path')
	openbrowser(url)

def appsChanged(*args):
	app = menuAppsDefault.get()
	appType = getDictValue(dApps, 'Name', app, 'Type')
	root.after(100, lambda: menuAppsDefault.set('Apps'))

	# Open URLs in browser
	if appType == 'Map' or appType == 'Web':
		openInBrowser(app)
	elif app == 'ArcMap':
		startfile('C:/Program Files (x86)/ArcGIS/Desktop10.8/bin/ArcMap.exe')
	elif app == '< Close GUI v05 >':
		quit()
	else:
		dAppValues = getDictValue(dApps, 'Name', app, 'All')
		
		# Validate that we got application details. Prevents looping error
		if dAppValues is None:
			return
	
		if dAppValues['Type'] == 'Title':
			pass
		else:
			scriptPath = '{0}{1}'.format(dAppValues['Path'], dAppValues['File'])
			fjson.createScriptToLauchFile(scriptPath)
			startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')
	

# Launch Mar Menu
def buttonMarvMenu():
	scriptPath = 'F:/Research Department/Code/RP3/Marvelous_Menu_PY3_v01.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Launch Power PID Producer
def buttonPowerPIDProducer():
	scriptPath = 'F:/Research Department/Code/RP3/M1_Power_PID_Producer_v02.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Launch Ownership to Sale
def buttonOwnershipToSale():
	scriptPath = 'F:/Research Department/Code/RP3/M1_PPP_Ownership_to_Sale_v01.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Launch Deal Updater
def buttonOwershipUpdater():
	scriptPath = 'F:/Research Department/Code/RP3/M1_Deal_Updater_v02.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Launch Safe PID Delete
def buttonSafePIDDelete():
	scriptPath = 'F:/Research Department/Code/RP3/M1_Safe_PID_Delete_v01.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Launch CSV to TF
def buttonCSV2TF():
	scriptPath = 'F:/Research Department/Code/RP3/TF_AWS_CSV_Entry_PY3_v02.py'
	fjson.createScriptToLauchFile(scriptPath)
	startfile('F:/Research Department/Code/RP3/python_script_shell_v01.py')

# Opens folder
def foldersChanged(*args):
	folder = menuFoldersDefault.get()
	root.after(100, lambda: menuFoldersDefault.set('Folders'))
	folderPathName = getDictValue(dApps, 'Name', folder, 'Path')
	# Validate that we got application details
	if folderPathName is None:
		return
	# excelFileName = getDictValue(dApps, 'Name', folder, 'File')
	# appType = getDictValue(dApps, 'Name', folder, 'Type')
	startfile(folderPathName)

# Opens Excel database files (GUI, Counties, Staff)
def excelChanged(*args):
	folder = menuExcelDefault.get()
	root.after(100, lambda: menuExcelDefault.set('Excel'))
	folderPathName = getDictValue(dApps, 'Name', folder, 'Path')
	# Validate that we got application details
	if folderPathName is None:
		return
	excelFileName = getDictValue(dApps, 'Name', folder, 'File')
	# appType = getDictValue(dApps, 'Name', folder, 'Type')
	startfile('{0}{1}'.format(folderPathName, excelFileName))

def quit():
	exit()

# Changes the County tk.OptionMenu to list the counties for that Market
def marketChanged(*args):
	market = menuMarketsDefault.get()
	lCounties = getCounties('Counties', market)
	menuCountiesDefault.set('County')
	menuCounties = tk.OptionMenu(root, menuCountiesDefault, *lCounties)
	menuCounties.config(width=12, bg='black', fg='cyan')
	menuCounties['menu'].config(bg='black', fg='cyan')
	menuCounties['highlightthickness'] = 0
	menuCounties.grid(row=0, column=2, padx=(0, 0), pady=3)
	# return lCounties

def buttonTest():
	service = fun_login.TerraForce()
	market = menuMarketsDefault.get()
	textValue1 = txtbox_PID_LID_APN.get()
	textValue1 = textValue1.strip()
	messagebox.showinfo('Test1', '{0} : {1}'.format(market, textValue1))
	if 'Enter' in textValue1 or textValue1 == '':
		messagebox.showerror('ERROR', 'Invalid entry...\n\nEnter a PID, LID or APN in the text box.')
	elif market == 'Vizzda':
		messagebox.showinfo('Test2', '{0} : {1}'.format(market, textValue1))
		textValue1 = bb.openVizzdaReturnPID(service, textValue1)
		if textValue1 == 'None':
			messagebox.showerror('ERROR', 'Vizzda ID not found.')
			return
	# Check if LID
	elif '_' in textValue1:
		LID = textValue1
		dLID = getLIDDict(LID)
		fjson.create_ZoomToPolygon_json_file(fieldname='leadid', polyId=LID, polyinlayer=dLID['leadLayerName'], lon=None, lat=None)
		return
	messagebox.showerror('ERROR', 'buttonTest')

# START #############################################
user = getUserName()

dApps, lAppNames, lFolders, lExcel = getAppsData()
lCounties = getCounties('AllCounties ArcName')
lMarkets = getCounties('Market')
lMarkets.append('Vizzda')
lStatesAbb = getCounties('StateAbb')

root = tk.Tk()  # Blank window
root.overrideredirect(1)
root.configure(background='black')
if user == 'blandis':
	center_window(1025, 33)
else:
	center_window(820, 33)
root.wm_attributes("-topmost", 1)
txtbox_text_var = tk.StringVar()

# Apps dropdown list
menuAppsDefault = tk.StringVar(root)
menuAppsDefault.set('Apps')
menuAppsDefault.trace_add('write', appsChanged)
menuApps = tk.OptionMenu(root, menuAppsDefault, *lAppNames)
menuApps.config(width=6, bg='black', fg='white')
menuApps['menu'].config(bg='black', fg='white')
menuApps['highlightthickness'] = 0
menuApps.grid(row=0, column=0, padx=(3, 0), pady=3)

# APN Market dropdown list
menuMarketsDefault = tk.StringVar(root)
menuMarketsDefault.set('Market')
menuMarketsDefault.trace_add('write', marketChanged) # Update Counties list
menuMarkets = tk.OptionMenu(root, menuMarketsDefault, *lMarkets)
menuMarkets.config(width=12, bg='black', fg='cyan')
menuMarkets['menu'].config(bg='black', fg='cyan')
menuMarkets['highlightthickness'] = 0
menuMarkets.grid(row=0, column=1, padx=(0, 0), pady=3)

# APN County dropdown list
menuCountiesDefault = tk.StringVar(root)
menuCountiesDefault.set('County')
menuCounties = tk.OptionMenu(root, menuCountiesDefault, *lCounties)
menuCounties.config(width=12, bg='black', fg='cyan')
menuCounties['menu'].config(bg='black', fg='cyan')
menuCounties['highlightthickness'] = 0
menuCounties.grid(row=0, column=2, padx=(0, 0), pady=3)

# Textbox
txtbox_PID_LID_APN = tk.Entry(root)
txtbox_PID_LID_APN.insert(tk.END, 'PID_LeadID_APN_Gmap_Co_Person')
txtbox_PID_LID_APN.config(width=30, bg='black', fg='cyan')
txtbox_PID_LID_APN.grid(row=0, column=3, padx=5, pady=2)

# Submit button
btnSubmit = tk.Button(root, text='Submit', width=9, bg='black', fg='cyan', command=buttonSubmit)
btnSubmit.config(width=6)
btnSubmit.grid(row=0, column=4, padx=3, pady=2)

# Power PID Producer Button
btnPPP = tk.Button(root, text='PPP', width=5, bg='black', fg='green2', command=buttonPowerPIDProducer)
btnPPP.config(width=5)
btnPPP.grid(row=0, column=5, padx=3, pady=3)

# Ownership 2 Sale Button
btnO2S = tk.Button(root, text='O2S', width=5, bg='black', fg='orange', command=buttonOwnershipToSale)
btnO2S.config(width=5)
btnO2S.grid(row=0, column=6, padx=3, pady=3)

# Deal Updater Button
btnUpdater = tk.Button(root, text='UP', width=5, bg='black', fg='gold', command=buttonOwershipUpdater)
btnUpdater.config(width=5)
btnUpdater.grid(row=0, column=7, padx=3, pady=3)

# Safe PID Delete Button
btnPIDDelete = tk.Button(root, text='DEL', width=5, bg='black', fg='red', command=buttonSafePIDDelete)
btnPIDDelete.config(width=5)
btnPIDDelete.grid(row=0, column=8, padx=3, pady=3)

# Safe PID Delete Button
btnPIDDelete = tk.Button(root, text='CSV2TF', width=5, bg='black', fg='white', command=buttonCSV2TF)
btnPIDDelete.config(width=5)
btnPIDDelete.grid(row=0, column=9, padx=3, pady=3)


# Folders dropdown list
if user == 'blandis':
	
	# Marvelous Menu Button
	btnMarvMenue = tk.Button(root, text='MM', width=5, bg='black', fg='MediumOrchid1', command=buttonMarvMenu)
	btnMarvMenue.config(width=5)
	btnMarvMenue.grid(row=0, column=10, padx=3, pady=3)

	# Excel dropdown list
	menuExcelDefault = tk.StringVar(root)
	menuExcelDefault.set('Excel')
	menuExcelDefault.trace_add('write', excelChanged)
	menuFolders = tk.OptionMenu(root, menuExcelDefault, *lExcel)
	menuFolders.config(width=5, bg='black', fg='white')
	menuFolders['menu'].config(bg='black', fg='white')
	menuFolders['highlightthickness'] = 0
	menuFolders.grid(row=0, column=11, padx=(0, 0), pady=3)

	# Folder dropdown list
	menuFoldersDefault = tk.StringVar(root)
	menuFoldersDefault.set('Folders')
	menuFoldersDefault.trace_add('write', foldersChanged)
	menuFolders = tk.OptionMenu(root, menuFoldersDefault, *lFolders)
	menuFolders.config(width=7, bg='black', fg='white')
	menuFolders['menu'].config(bg='black', fg='white')
	menuFolders['highlightthickness'] = 0
	menuFolders.grid(row=0, column=12, padx=(0, 0), pady=3)

# Start the GUI event loop
root.mainloop()
