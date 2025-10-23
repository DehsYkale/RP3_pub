# Create a new PID from parcels

import acc
import aws
import bb
import dicts
import fjson
import fun_login
import fun_text_date as td
import lao
import mpy
from pprint import pprint
import webs


# Choose if record will be a Lead or a Sale
def menu_lead_or_sale(dTF):
	td.banner('Find Create Entity and Person')
	print(' Choose Record Type\n')
	print(' - Select Lead for Reonomy Comps, MVP or Competitor Listings')
	print(' - Select Sale for manually entering a sale.')
	print(' - Select OI Poly to make OwnerIndex polygon for an existing TF Deal.\n')
	print('  1) Lead')
	print('  2) Sale')
	print('  3) OI Poly')
	print(' 00) Quit')
	while 1:
		ui = td.uInput('\n Select > ')
		if ui == '1':
			dTF['StageName__c'] = 'Lead'
			break
		elif ui == '2':
			dTF['StageName__c'] = 'Closed Lost'
			break
		elif ui == '3':
			dTF['StageName__c'] = 'OI Poly'
			break
		elif ui == '00':
			exit('\n Terminating program...')
		else:
			td.warningMsg('\n Invalid input...try again...')
	return dTF

# Choose from list of parcel owners
def get_parcel_data():
	# Download ArcMakePIDFromParcelOwnerInfo json file from M1
	aws.get_m1_file_copy(action='DOWN')
	# Get json file with parcels/PID and other info
	filename_make_PID = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'
	dMake = fjson.getJsonDict(filename_make_PID)
	lUnique_owners = []
	
	td.banner('Find Create Entity and Person')
	onlyonerecord = True
	# dTF['PARCELPROPIDS'] = []
	lat_max, lat_min, lon_max, lon_min = 0, 100, -200, 0
	count_parcels, total_lat, total_lon = 0, 0, 0
	for indx in dMake:
		count_parcels += 1
		d = dMake[indx]
		# Only print uqniue owner records
		lInfo = [d['owner'], d['mailstreet'], d['mailcity'], d['mailstate'], d['mailzip']]
		if lInfo not in lUnique_owners:
			lUnique_owners.append(lInfo)
			print('\n****************************\n')
			print(' {0}'.format(indx))
			print(' {0}'.format(d['owner']))
			print(' {0}'.format(d['mailstreet']))
			print(' {0}, {1}  {2}'.format(d['mailcity'], d['mailstate'], d['mailzip']))

		# Add Acres to dAcc
		dTF['Acres__c'] = dTF['Acres__c'] + d['acres']
		# Add Parcel APNs
		if dTF['Parcels__c'] == 'None':
			dTF['Parcels__c'] = d['apn']
			dTF['Lead_Parcel__c'] = d['apn']
		else:
			dTF['Parcels__c'] = '{0}, {1}'.format(dTF['Parcels__c'], d['apn'])
		dPoly['PARCELPROPIDS'].append(d['propertyid'])
		# Add Zoning
		if dTF['Zoning__c'] == 'None':
			if d['zoning'] != '':
				dTF['zoning__c'] = d['zoning']
		else:
			if d['zoning'] != '':
				dTF['zoning__c'] = '{0}, {1}'.format(dTF['zoning__c'], d['zoning'])
		# Calculate centroid of all parcels
		total_lat = total_lat + d['lat']
		total_lon = total_lon + d['lon']

		if indx == 'Index 2':
			onlyonerecord = False

	# Calculate centroid of all parcels
	dTF['Latitude__c'] = total_lat / count_parcels
	dTF['Longitude__c'] = total_lon / count_parcels
	# Round Acres to 2 decimal places
	dTF['Acres__c'] = round(dTF['Acres__c'], 2)

	if onlyonerecord:
		ui_indx = 'Index 1'
	else:
		while 1:
			print('\n Select Entity/Person to use buy Index Number')
			ui_indx = 'Index {0}'.format(td.uInput('\n Enter number or [00] to quit > '))
			if ui_indx == 'Index 00':
				exit('\n Terminating program...')
			try:
				d = dMake[ui_indx]
				break
			except KeyError:
				td.warningMsg('\n Invalid input...try again...')
				lao.sleep(1)

	# 	print('\n Select Entity/Person to use buy Index Number')
	# 	ui_indx = 'Index {0}'.format(td.uInput('\n Enter number or [00] to quit > '))
	# 	if ui_indx == 'Index 00':
	# 		exit('\n Terminating program...')

	# d = dMake[ui_indx]
	dAcc['ENTITY'] = d['owner']
	if d['mailstreet']:
		dAcc['STREET']  = d['mailstreet'].strip()
		dAcc['STREET'] = td.titlecase_street(dAcc['STREET'])
	if d['mailcity']:
		dAcc['CITY']  = d['mailcity'].strip()
		dAcc['CITY'] = dAcc['CITY'].title()
	if d['mailstate']:
		dAcc['STATE']  = d['mailstate'].strip()
	if d['mailzip']:
		dAcc['ZIPCODE']  = d['mailzip'].strip()
	dAcc['SOURCE'] = 'Parcel'
	dTF['Source__c'] = 'LAO'

	return dAcc, dTF, dPoly

# Find/Create Account in TF
def findCreateAccount(dAcc):
	# Find Create Seller/Owner Entity if not already in Ownership record
	dAcc = acc.find_create_account_entity(service, dAcc)
	# If not Seller/Owner Entity the set Seller/Owner Person variable to None
	if dAcc['AID'] == 'None':
		acc.find_persons_of_entity(service, dAcc)

	return dAcc

# Populate Buyer/Seller dict for Sale Deals
def populate_dBS_for_sale(dAcc):
	td.banner('Find Create Entity and Person (PPP v02)')

	# Get blank Buyer/Seller dict
	dBS = dicts.get_blank_buyer_seller_dict()

	# Buyer/Seller menu
	print(' {0}'.format(dAcc['ENTITY']))
	print(' {0}'.format(dAcc['NAME']))
	print(' {0}'.format(dAcc['STREET']))
	print(' {0}, {1}, {2}\n'.format(dAcc['CITY'], dAcc['STATE'], dAcc['ZIPCODE']))
	print('\n Is this the Buyer or the Seller?')
	print('\n 1) Buyer')
	print(' 2) Seller')
	while 1:
		ui = td.uInput('\n Select > ')
		if ui == '1':
			print('\n You chose the BUYER:')
			print(f' Entity: {dAcc['ENTITY']}')
			print(f' Person: {dAcc['NAME']}')
			dBS['BUYERENTITYID'] = dAcc['EID']
			dBS['BUYERENTITYNAME'] =  dAcc['ENTITY']
			dBS['BUYERPERSONID']  = dAcc['AID']
			dBS['BUYERPERSONNAME']  = dAcc['NAME']
			break
		elif ui == '2':
			print('\n You chose the SELLER:')
			print(f' Entity: {dAcc['ENTITY']}')
			print(f' Person: {dAcc['NAME']}')
			dBS['SELLERENTITYID'] = dAcc['EID']
			dBS['SELLERENTITYNAME'] = dAcc['ENTITY']
			dBS['SELLERPERSPNID'] = dAcc['AID']
			dBS['SELLERPERSONNAME'] = dAcc['NAME']
			break
		else:
			td.warningMsg('\n Invalid input...try again...')

	
	td.banner('Find Create Entity and Person (PPP v02)')
	dAcc = dicts.get_blank_account_dict()
	# Enter Buyer
	is_buyer_seller = 'SELLER'
	if dBS['BUYERENTITYID'] == 'None' and dBS['BUYERPERSONNAME'] == 'None':
		is_buyer_seller = 'BUYER'
		dAcc['ENTITY'] = td.uInput(f' Enter {is_buyer_seller} Entity or Person [00] > ')
		if dAcc['ENTITY'] == '00':
			exit('\n Terminating program...')
		
	# Enter Buyer/Seller Entity/Person
	dAcc = acc.find_create_account_entity(service, dAcc)
	temp1, temp2, dAcc = acc.find_create_account_person(service, dAcc)

	# Assign Buyer/Seller Entity/Person to dict
	if is_buyer_seller == 'BUYER':
		dBS['BUYERENTITYID'] = dAcc['EID']
		dBS['BUYERENTITYNAME'] =  dAcc['ENTITY']
		dBS['BUYERPERSONID']  = dAcc['AID']
		dBS['BUYERPERSONNAME']  = dAcc['NAME']
	else:
		dBS['SELLERENTITYID'] = dAcc['EID']
		dBS['SELLERENTITYNAME'] = dAcc['ENTITY']
		dBS['SELLERPERSPNID'] = dAcc['AID']
		dBS['SELLERPERSONNAME'] = dAcc['NAME']
	
	return dBS

# Make Offer dict
def make_offer(dBS, dTF):

	dOffer = {}
	dOffer['type'] = 'lda_Offer__c'
	# dOffer['DealID__c'] = DID

	if dTF['Sale_Date__c'] == 'None':
		print('\n Enter Sale Date')
		dTF['Sale_Date__c'] = td.make_tf_date()
	dOffer['Offer_Date__c'] = dTF['Sale_Date__c']
	dOffer['Date_Accepted__c'] = dTF['Sale_Date__c']
	dOffer['Offer_Status__c'] = 'Accepted'
	if dTF['Sale_Price__c'] == 0:
		dTF['Sale_Price__c'] = float(td.uInput(' Enter Sale Price (no punctuation) > '))
	dOffer['Offer_Price__c'] = dTF['Sale_Price__c']
	if dBS['BUYERENTITYID'] != 'None':
		dOffer['Buyer_Entity__c'] = dBS['BUYERENTITYID']
	if dBS['BUYERPERSONID'] != 'None':
		dOffer['Buyer__c'] = dBS['BUYERPERSONID']

	return dOffer

# Populate Buyer/Seller dict for Lead Deals
def populate_dBS_for_lead(dAcc):
	dBS['BUYERENTITYID'] = 'None'
	dBS['BUYERENTITYNAME'] =  'None'
	dBS['BUYERPERSONID']  = 'None'
	dBS['BUYERPERSONNAME']  = 'None'
	dBS['SELLERENTITYID'] = dAcc['EID']
	dBS['SELLERENTITYNAME'] = dAcc['ENTITY']
	dBS['SELLERPERSPNID'] = dAcc['AID']
	dBS['SELLERPERSONNAME'] = dAcc['NAME']
	return dBS

# Make Deal Name
def make_deal_name():
	# Make Deal Name based on Location and Acres
	if '&' in dTF['Location__c']:
	# if dTF['Location__c'] != 'None':
		if len(dTF['Location__c']) > 50:
			location = dTF['Location__c'].split(' ')
			name = location[0]
			for i in range(1, len(location)):
				if len(name) < 50:
					name = '{0} {1}'.format(name, location[i])
				else:
					break
		else:
			name = dTF['Location__c']
		dTF['Name'] = '{0} {1} Ac'.format(name, int(dTF['Acres__c']))

	# Name based on Entity Name and Acres if exists
	elif dTF['SELLERENTITYNAME'] != 'None':
		if len(dTF['SELLERENTITYNAME']) > 50:
			ownerName = dTF['SELLERENTITYNAME'].split(' ')
			name = ownerName[0]
			for i in range(1, len(ownerName)):
				if len(name) < 50:
					name = '{0} {1}'.format(name, ownerName[i])
				else:
					break
		else:
			name = dTF['SELLERENTITYNAME']
		dTF['Name'] = '{0} {1} Ac'.format(name, int(dTF['Acres__c']))
	# Name based on Person Name and Acres
	else:
		if len(dTF['SELLERPERSONNAME']) > 50:
			ownerName = dTF['SELLERPERSONNAME'].split(' ')
			name = ownerName[0]
			for i in range(1, len(ownerName)):
				if len(name) < 50:
					name = '{0} {1}'.format(name, ownerName[i])
				else:
					break
		else:
			name = dTF['SELLERPERSONNAME']
		dTF['Name'] = '{0} {1} Ac'.format(name, int(dTF['Acres__c']))

	return dTF

# OI Poly create an OwnerIndex polygon for an existing TF Deal
def make_oi_poly_for_existing_tf_deal():
	td.banner('Make OwnerIndex polygon for existing TF Deal')
	
	# User to enter PID
	dTF['PID__c'] = td.uInput('\n Enter PID > ')
	dTF['PID__c'] = dTF['PID__c'].strip()
	# TerraForce Query
	fields = 'default'
	wc = f"PID__c = '{dTF['PID__c']}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	dTF['State__c'] = results[0]['State__c']
	dTF['County__c'] = results[0]['County__c']

	# Download ArcMakePIDFromParcelOwnerInfo json file from M1
	aws.get_m1_file_copy(action='DOWN')
	# Get json file with parcels/PID and other info
	filename_make_PID = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'
	dMake = fjson.getJsonDict(filename_make_PID)
	# Add Parcel APNs
	for indx in dMake:
		dPoly['PARCELPROPIDS'].append(dMake[indx]['propertyid'])
	
	ui = td.uInput('\n Make OwnerIndex polygon [0/1/00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		is_oi_poly_made = mpy.oi_make_from_parcel_propertyid(dTF, dPoly['PARCELPROPIDS'])
		if mpy.get_OID_from_PID(dTF['PID__c']) is None:
			td.colorText('\n TELL Bill M1_Power_PID_Producer_v02.py failed at def make_oi_polygon.\n\nPID poly {0} not produced!\n Make it manually.'.format(dTF['PID__c']), 'YELLOW')
			ui = td.uInput('\n Continue > ')
	
# Make Ownership from Sale record
# Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
def create_ownership_from_sale(dTF, dBS, dPoly):
	print('\n Create Ownership from Sale Record')
	dTF['AccountId__c'] = dBS['BUYERPERSONID']
	dTF['Owner_Entity__c'] = dBS['BUYERENTITYID']
	dTF['RecordTypeID'] = '012a0000001ZSS5AAO'
	dTF['StageName__c'] = 'Lead'
	dTF['type'] = 'lda_Opportunity__c'
	dTF['Parent_Opportunity__c'] = dTF['Id']

	del dTF['Buyer_Acting_As__c']
	del dTF['Id']
	del dTF['PID__c']
	del dTF['Sale_Date__c']
	del dTF['Sale_Price__c']

	dTF['Id'] = bb.tf_create_3(service, dTF)
	dTF['PID__c'] = bb.getPIDfromDID(service, dTF['Id'])

	make_oi_polygon(dTF, dPoly)

def make_oi_polygon(dTF, dPoly):
	is_oi_poly_made = mpy.oi_make_from_parcel_propertyid(dTF, dPoly['PARCELPROPIDS'])

	if mpy.get_OID_from_PID(dTF['PID__c']) is None:
		td.colorText('\n TELL Bill M1_Power_PID_Producer_v02.py failed at def make_oi_polygon.\n\nPID poly {0} not produced!\n Make it manually.'.format(dTF['PID__c']), 'YELLOW')
		ui = td.uInput('\n Continue > ')

# START OF PROGRAM ########################################################

user = lao.getUserName()

td.console_title('PPP Parcel to Ownership v01')

# Move the console window to the correct position
if user == 'blandis':
	lao.consoleWindowPosition(position='Bill Marvelous Menu')

service = fun_login.TerraForce()

while 1:
	dAcc = dicts.get_blank_account_dict()
	dBS = dicts.get_blank_buyer_seller_dict()
	dPoly = {'PARCELPROPIDS': []}
	dTF = dicts.get_blank_tf_deal_dict()
	dTF = menu_lead_or_sale(dTF)

	# IO Poly 
	if dTF['StageName__c'] == 'OI Poly':
		make_oi_poly_for_existing_tf_deal()
		exit()

	dAcc, dTF, dPoly = get_parcel_data()

	# Find Create Seller/Owner Entity if not already in Ownership record
	td.banner('Find Create Entity and Person (PPP v02)')
	dAcc = acc.find_create_account_entity(service, dAcc)
	temp1, temp2, dAcc = acc.find_create_account_person(service, dAcc)

	# Populate Buyer/Seller dict based on Lead or Sale
	is_sale_record = False
	if dTF['StageName__c'] == 'Lead':
		dBS = populate_dBS_for_lead(dAcc)
	# Is Sale record so populate Buyer/Seller dict
	elif dTF['StageName__c'] == 'Closed Lost':
		dBS = populate_dBS_for_sale(dAcc)
		dOffer = make_offer(dBS, dTF)
		is_sale_record = True
		dTF['StageName__c'] = 'Lead'

	# Add Owner Entity and AccountID to record
	dTF['Owner_Entity__c'] = dBS['SELLERENTITYID']
	dTF['AccountId__c'] = dBS['SELLERPERSPNID']

	# Add Classification, Lot Type, Lots, Development Status and Buyer Acting As
	dTF = bb.populate_deal_details(dTF, is_sale_record)

	# Add City, County, Market, Submarket, State & Zip Code based on Lon/Lat
	print('\n Getting LAO Geo Info...')
	dTF = mpy.get_LAO_geoinfo(dTF=dTF)

	# Get Location intersection
	print(' Getting Location intersection...')
	dTF = mpy.get_intersection_from_lon_lat(dTF)

	# Make Deal Name based on Seller Entity or Person
	print(' Making Deal Name...')
	dTF = make_deal_name()

	# Add Researcher OwnerId to record
	print(' Getting Researcher OwnerId...')
	dTF['OwnerId'] = bb.createdByResearch(service)

	td.banner('PPP Parcel to Ownership v01')

	# Make Ownership TF Deal Record
	print('\n Making Ownership TF Deal Record...')
	dTF['Id'] = bb.tf_create_3(service, dTF)

	dTF['PID__c'] = bb.getPIDfromDID(service, dTF['Id'])
				
	# Make Offer record if Sale
	if is_sale_record:
		print('\n Making Offer and converting Ownership to Sale record...')
		dOffer['DealID__c'] = dTF['Id']
		OID = bb.tf_create_3(service, dOffer)
		dUP = dicts.get_lead_to_closed_lost_dict(dTF['Id'])
		bb.tf_update_3(service, dUP)

	# Open the new TF Deal record in TerraForce
	webs.openTFDID(dTF['Id'])

	# ui = td.uInput('\n Make OwnerIndex polygon [0/1/00]... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
	# elif ui == '1':
	make_oi_polygon(dTF, dPoly)

	# Make Ownership from Sale record
	if is_sale_record:
		ui = td.uInput('\n Create a new Ownership of the Sale [0/1/00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			create_ownership_from_sale(dTF, dBS, dPoly)
		else:
			print('\n No Ownership created.')
			ui = td.uInput('\n Continue > ')


	ui = td.uInput('\n Finished... > ')

	exit()
