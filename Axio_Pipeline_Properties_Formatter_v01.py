# Format AxioMetrics Pipeline Properties for LAO MF Spreadsheet

import csv
import dicts
import fun_text_date as td
import lao
import os
from pprint import pprint

def get_dicts():
	dMSA_LAO = {
		"Albuquerque, NM": "Albuquerque",
		"Santa Fe, NM": "Albuquerque",
		"Atlanta-Sandy Springs-Roswell, ": "Atlanta",
		"Savannah, ": "Atlanta",
		"Chattanooga, TN-GA": "Atlanta",
		"Calhoun, ": "Atlanta",
		"Gainesville,": "GA	Atlanta",
		"Jefferson, GA": "Atlanta",
		"LaGrange, GA": "Atlanta",
		"Austin-Round Rock, TX": "Austin",
		"Fredericksburg, TX": "Austin",
		"Killeen-Temple, TX": "Austin",
		"San Antonio-New Braunfels, ": "Austin",
		"Waco, TX": "Austin",
		"Boise City, ID": "Boise",
		"Coeur d'Alene, ID": "Boise",
		"Hailey, ": "Boise",
		"Idaho Falls, ID": "Boise",
		"Mountain Home, ID": "Boise",
		"Pocatello, ID": "Boise",
		"Albemarle, NC": "Charlotte",
		"Charlotte-Concord-Gastonia, NC-SC": "Charlotte",
		"Greensboro/Winston-Salem, NC": "Charlotte",
		"Hickory-Lenoir-Morganton, NC": "Charlotte",
		"Boulder, CO": "Denver",
		"Breckenridge, CO": "Denver",
		"Colorado Springs, CO": "Denver",
		"Denver-Aurora-Lakewood, CO": "Denver",
		"Fort Collins, ": "Denver",
		"Greeley, ": "Denver",
		"Pueblo, CO": "Denver",
		"Steamboat Springs, CO": "Denver",
		"Grand Junction, CO": "Denver",
		"Dallas-Plano-Irving, TX": "Dallas",
		"Fort Worth-Arlington, TX": "Dallas",
		"Gainesville, TX": "Dallas",
		"Sherman-Denison, TX": "Dallas",
		"Tyler, TX": "Dallas",
		"Asheville, NC": "Greenville",
		"Greenville/Spartanburg, ": "Greenville",
		"Seneca, SC": "Greenville",
		"Shelby, NC": "Charlotte",
		"College Station-Bryan, TX": "Houston",
		"Houston-The Woodlands-Sugar Land, TX": "Houston",
		"Brenham, TX": "Houston",
		"Brunswick, GA": "Jacksonville",
		"Deltona-Daytona Beach-Ormond Beach, FL": "Jacksonville",
		"Gainesville, ": "Jacksonville",
		"Jacksonville, FL": "Jacksonville",
		"Palatka, FL": "Jacksonville",
		"St. Marys, GA": "Jacksonville",
		"Kansas City, MO-KS": "Kansas City",
		"Lawrence, KS": "Kansas City",
		"Topeka, KS": "Kansas City",
		"Fernley, NV": "Las Vegas/Reno",
		"Las Vegas-Henderson-Paradise, NV": "Las Vegas/Reno",
		"Reno, ": "Las Vegas/Reno",
		"Clarksville, TN-KY": "Nashville",
		"Nashville-Davidson--Murfreesboro--Franklin, TN": "Nashville",
		"Deltona-Daytona Beach-Ormond Beach, ": "Orlando",
		"Lakeland-Winter Haven, FL": "Orlando",
		"Ocala, FL": "Orlando",
		"Orlando-Kissimmee-Sanford, FL": "Orlando",
		"Palm Bay-Melbourne-Titusville, FL": "Orlando",
		"Port St. Lucie/Sebastian/Vero Beach, FL": "Orlando",
		"Sebring, FL": "Orlando",
		"The Villages, FL": "Orlando",
		"Phoenix-Mesa-Scottsdale, AZ": "Phoenix",
		"Flagstaff, ": "Prescott",
		"Lake Havasu City-Kingman, AZ": "Prescott",
		"Prescott, AZ": "Prescott",
		"Raleigh/Durham, NC": "Raleigh-Durham",
		"Cape Coral-Fort Myers, ": "Tampa",
		"Homosassa Springs, FL": "Tampa",
		"Naples-Immokalee-Marco Island, FL": "Tampa",
		"North Port-Sarasota-Bradenton, ": "Tampa",
		"Tampa-St. Petersburg-Clearwater, ": "Tampa",
		"Tucson, AZ": "Tucson",
		"Logan, UT-ID": "Utah",
		"Provo-Orem, UT": "Utah",
		"Salt Lake City/Ogden/Clearfield, UT": "Utah"
	}

	dProp_status = {
		'Pre-Planned': '1 - Pre-Planned',
		'Planned': '2 - Planned',
		'Under Construction': '3 - Under Construction',
		'Under Construction/Lease-Up': '4 - Lease-Up'
	}

	dProp_structure = {
		'Duplex/Triplex/Quadplex': 'Duplex/Triplex/Quadplex',
		'Duplex/Triplex/Quadplex,Horizontal Apartment': 'Duplex/Triplex/Quadplex',
		'Duplex/Triplex/Quadplex,Townhome/Row Home': 'Duplex/Triplex/Quadplex',
		'Duplex/Triplex/Quadplex,Townhome/Row Home,Horizontal Apartment': 'Duplex/Triplex/Quadplex',
		'Garden': 'Garden',
		'Garden,Duplex/Triplex/Quadplex': 'Garden',
		'Garden,Duplex/Triplex/Quadplex,Townhome/Row Home': 'Garden',
		'Garden,Horizontal Apartment': 'Garden',
		'Garden,Modular': 'Garden',
		'Garden,Single Family': 'Garden',
		'Garden,Single Family,Duplex/Triplex/': 'Garden',
		'Garden,Single Family,Duplex/Triplex/Quadplex': 'Garden',
		'Garden,Single Family,Duplex/Triplex/Quadplex,Townhome/Row Home': 'Garden',
		'Garden,Single Family,Townhome/Row Home': 'Garden',
		'Garden,Tower': 'Garden',
		'Garden,Townhome/Row Home': 'Garden',
		'Garden,Townhome/Row Home,Horizontal Apartment': 'Garden',
		'Horizontal Apartment': 'BTR',
		'Horizontal Apartment': 'BTR',
		'Modular': 'Modular',
		'Modular,Single Family': 'Modular',
		'Podium': 'Podium',
		'Podium,Single Family': 'Podium',
		'Podium,Single Family,Duplex/Triplex/Quadplex': 'Podium',
		'Podium,Single Family,Townhome/Row Home': 'Podium',
		'Podium,Townhome/Row Home': 'Podium',
		'Single Family': 'BTR',
		'Single Family,Duplex/Triplex': 'BTR',
		'Single Family,Duplex/Triplex/Quadplex': 'BTR',
		'Single Family,Duplex/Triplex/Quadplex,Townhome/Row Home': 'BTR',
		'Single Family,Horizontal Apartment': 'BTR',
		'Single Family,Townhome/Row': 'BTR',
		'Single Family,Townhome/Row Home': 'BTR',
		'Tower': 'Tower',
		'Tower,Duplex/Triplex/Quadplex': 'Tower',
		'Tower,Single Family,Townhome/Row Home': 'Tower',
		'Tower,Townhome/Row Home': 'Tower',
		'Townhome/Row Home': 'BTR',
		'Townhome/Row Home,Horizontal Apartment': 'BTR',
		'Wrap': 'Wrap',
		'Wrap,Duplex/Triplex/Quadplex': 'Wrap',
		'Wrap,Single Family,Townhome/Row Home': 'Wrap',
		'Wrap,Townhome/Row Home': 'Wrap'
		}

	lLists = [[
		'Property ID',
		'Property Status',
		'Property Name',
		'Address',
		'City',
		'State',
		'ZIP Code',
		'Latitude',
		'Longitude',
		'Geography Code',
		'Market',
		'Submarket',
		'County',
		'Cnty State',
		'Construction Start Date',
		'Leasing Start Date',
		'First Move-In Date',
		'Construction Finish Date',
		'Year Built',
		'Property Owner',
		'Management Company',
		'Developer',
		'Architect',
		'General Contractor',
		'Total Units',
		'Stories',
		'Property Structure',
		'Last Update',
		'Property Notes']]

	return dMSA_LAO, dProp_status, dProp_structure, lLists

td.banner('AxioMetrics Pipeline Properties Formatter v01')

# Get dicts
dMSA_LAO, dProp_status, dProp_structure, lLists = get_dicts()
filepath = 'F:/Research Department/MIMO/zData/AxioMetrics/Pipeline/'
# User to select file
filename = lao.guiFileOpen(path=filepath, titlestring='Open Axio Pipeline File', extension=[('Excel files', '.xlsx'), ('all files', '.*')])
dAxio = dicts.spreadsheet_to_dict(filename, sheetname='Pipeline Project Details')

# Loop through dAxio and build lLists
for row in dAxio:
	# Determine LAO market
	msa = dAxio[row]['Market']
	if msa in dMSA_LAO:
		market = dMSA_LAO[dAxio[row]['Market']]
	else:
		market = 'Not Defined'
	
	# Build County State
	cnty_state = f"{dAxio[row]['County']} {dAxio[row]['State']}"
	# Format Property Status and Structure
	prop_status = dProp_status[dAxio[row]['Property Status']]
	prop_structure = dProp_structure[dAxio[row]['Property Structure']]

	date_con_start = td.date_engine(dAxio[row]['Construction Start Date'], outformat='ddmmyyyy', informat='datetime')
	date_lease_start = td.date_engine(dAxio[row]['Leasing Start Date'], outformat='ddmmyyyy', informat='datetime')
	date_first_move_in = td.date_engine(dAxio[row]['First Move-In Date'], outformat='ddmmyyyy', informat='datetime')
	date_con_finish = td.date_engine(dAxio[row]['Construction Finish Date'], outformat='ddmmyyyy', informat='datetime')
	date_last_update = td.date_engine(dAxio[row]['Last Update'], outformat='ddmmyyyy', informat='datetime')

	# Build list of data
	ltemp = [dAxio[row]['Property ID'],
		  	prop_status,
			dAxio[row]['Property Name'],
			dAxio[row]['Address'],
			dAxio[row]['City'],
			dAxio[row]['State'],
			dAxio[row]['ZIP Code'],
			dAxio[row]['Latitude'],
			dAxio[row]['Longitude'],
			dAxio[row]['Geography Code'],
			market,
			dAxio[row]['Submarket'],
			dAxio[row]['County'],
			cnty_state,
			date_con_start,
			date_lease_start,
			date_first_move_in,
			date_con_finish,
			dAxio[row]['Year Built'],
			dAxio[row]['Property Owner'],
			dAxio[row]['Management Company'],
			dAxio[row]['Developer'],
			dAxio[row]['Architect'],
			dAxio[row]['General Contractor'],
			dAxio[row]['Total Units'],
			dAxio[row]['Stories'],
			prop_structure,
			date_last_update,
			dAxio[row]['Property Notes']]
	lLists.append(ltemp)

# Write lLists to csv
filename_formatted = os.path.basename(filename).replace('.xlsx', '_Formatted.csv')
filepathname_formatted = f'{filepath}{filename_formatted}'
with open(filepathname_formatted, 'w', newline='', encoding='utf-8') as f:
	fout = csv.writer(f)
	fout.writerows(lLists)
lao.openFile(filepathname_formatted)

exit('\n Fin...')