# Libraries
import accounts
import aws
import apn
import bb
import fun_login
import fun_text_date as td
import fjson
import lao
from os import system
import webs
from pprint import pprint

# Check if record is LAO Exclusive, has Offer or is not Stage Lead, Draft, Top100
def is_TF_Record_Ok_to_Edit(dd, DID):
	if dd['Type__c'] == 'Exclusive LAO':
		td.warningMsg('\n Type is Exclusive LAO which prevents editing!\n\n Stop or change Type to blank.')
		webs.openTFDID(DID)
		while 1:
			ui = td.uInput('\n [Enter] to continue or [00] to quit > ')
			if ui == '':
				break
			elif ui == '00':
				exit()
			else:
				td.warningMsg('\n Invalid input...try again...')
	
	# Check for Existing Offers
	if dd['Offers__r'] != '':
		webs.openTFDID(DID)
		td.warningMsg('\n Accepted Offer Exists!\n\n Terminating program...')
		td.uInput('\n Continue... > ')
		exit()
	
	# Check that Stage is not greater than Draft or Top100
	if dd['StageName__c'] == 'Lead' or dd['StageName__c'] == 'Top 100' or dd['StageName__c'] == 'Draft':
		pass
	else:
		webs.openTFDID(DID)
		td.warningMsg('\n Stage Name is not a Lead, Top100 or Draft!')
		td.uInput('\n Continue...')
		exit('\n Terminating program...')

# START PROGRAM *****************************************************************
td.banner('TF AWS Lead To Sale v01')

service = fun_login.TerraForce()

# Check if PID in text file from ArcMap
try:
	PID, OID = aws.read_Write_PID_OID(PID='Read', OID='Read')
except IOError:
	PID, OID = 'None', 'None'


# Ask User to enter PID if not given by ArcMap
if PID == 'None':
	PID = td.uInput('\n Enter PID > ')

# Get TF record data
DID = bb.getDIDfromPID(service, PID)
dd = bb.get_All_Deal_Info(service, DID)

# Cannot edit EXclusive LAO so ask user to change or quit
# Cannot edit if there are existing Offers so quit
# Cannot edit if StageName is not Lead, Draft or Top100 so quit
is_TF_Record_Ok_to_Edit(dd, DID)

# Create Update Dict
dUpdate = {}
dUpdate['Id'] = DID
dUpdate['type'] = 'lda_Opportunity__c'

# SPLIT ************************************************************************
# Check if PID is to be split and split/make new Lead in TF if true
td.banner('TF AWS Lead To Sale v01')
while 1:
	ui_split = td.uInput('\n Split this PID? [0/1/00] > ')
	if ui_split == '1':
		aws.split_PID_Instructions() # Confirm user split the PID before proceding
		PID = bb.splitDeal(service, PID)
		DID = bb.getDIDfromPID(service, PID)
		# Assign new Lead PID attributest to polygon
		aws.make_AWS_Split_OwnerIndex_Update_Attributes_for_New_PID(OID, PID, runASW=True)
		# Color cmd window blue
		system('color 2f') # green with white letters
		break
	elif ui_split == '0':
		break
	elif ui_split == '00':
		exit()
	else:
		td.warningMsg('\n Invalid input...try again...')
# *****************************************************************************

# OWNER INFO ******************************************************************
# Print Existing Owner/Seller
td.banner('TF AWS Lead To Sale v01')
if dd['Owner_Entity__r'] == '':
	td.warningMsg('\n Owner Entity: None')
else:
	print('\n Owner Entity: {0}'.format(dd['Owner_Entity__r']['Name']))
if dd['AccountId__r'] == '':
	td.warningMsg(' Owner Person: None')
else:
	print(' Owner Person: {0}'.format(dd['AccountId__r']['Name']))

# Check if user wants to keep existing owner
print(' PID: {0}'.format(PID))
while 1:
	ui = td.uInput('\n Use existing Owner/Seller? [0/1] > ')
	if ui == '0' or ui == '1':
		break
	else:
		td.warningMsg('\n Invalid input...try again...')

# Use existing Owner/Seller
if ui == '1':
	print(' Using existing Owner/Seller data...')
	if dd['Owner_Entity__r'] != '':
		STX = dd['Owner_Entity__r']['Name']
	else:
		STX = 'None'
	if dd['AccountId__r'] == '':
		SPR, SPRID, RTYID = bb.findCreateAccountPerson(service, COMPANY=STX)
	else:
		SPR = dd['AccountId__r']['Name']
# Enter new Owner/Seller
elif ui == '0':
	STX, STXID, RTYID, business_dict = bb.findCreateAccountEntity(service)
	if STXID == 'None':
		SPR = STX
		STX = 'None'
		SPRID = 'None'
	# Check for Employees or Child Accounts of Business
	else:
		dUpdate['Owner_Entity__c'] = STXID
		SPR, SPRID, RTYID = bb.findPersonsOfEntity(service, STXID)

	# If no Employee or Child Account of Business then create a Person Account
	if SPRID == 'None':
		SPR, SPRID, RTYID = bb.findCreateAccountPerson(service, SPR)
	if SPR != 'None':
		dUpdate['AccountId__c'] = SPRID
	print('STX: ' + STX + '   SPR: ' + SPR)
# *******************************************************************************

# BUYER INFO ********************************************************************
# Get Buyer BTX, BTXID
td.banner('TF AWS Lead To Sale v01')
print(' PID: {0}'.format(PID))
print('\n\n BUYER')
BTX, BTXID, RTYID, business_dict = bb.findCreateAccountEntity(service)
if BTXID == 'None':
	BPR = BTX
	BTX = 'None'
	BPRID = 'None'
	print(BPR)
else:  # Check for Employees or Child Accounts of Business
	BPR, BPRID, RTYID = bb.findPersonsOfEntity(service, BTXID)
if BPRID == 'None':  # If no Employee or Child Account of Business then create a Person Account
	BPR, BPRID, RTYID = bb.findCreateAccountPerson(service, BPR)
# *******************************************************************************

# SALE PRICE & DATE *************************************************************
td.banner('TF AWS Lead To Sale v01')
print(' PID: {0}'.format(PID))
# User input Sale Price
dd['Sale_Price__c'] = apn.makeSalePrice()

# User input Sale Date
dd['Sale_Date__c'] = apn.makeSaleDate()
# *******************************************************************************

# SUBDIVISION ******************************************************************
td.banner('TF AWS Lead To Sale v01')
print(' PID: {0}'.format(PID))
# User input Subdivision
if 'Subdivision__c' in dd:
	if dd['Subdivision__c'] == '':
		ui = (td.uInput('\n Type Subdivision or [ENTER] to leave blank. > ')).upper()
		if ui != '':
			dUpdate['Subdivision__c'] = ui
	else:
		print('Subdivision: {0}'.format(dd['Subdivision__c']))
		ui = td.uInput('\n [Enter] to use existing Subdivision or type new > ')
		if ui != '':
			dUpdate['Subdivision__c'] = ui
# *******************************************************************************

# CLASSIFICATION, LOT TYPE, LOTS ************************************************
td.banner('TF AWS Lead To Sale v01')
print(' PID: {0}'.format(PID))
# User input Classification
dUpdate['Classification__c'] = lao.chooseClassification(dd['Classification__c'])

# User input Lot Type
dUpdate['Lot_Type__c'] = lao.chooseLotType(dUpdate['Classification__c'])

# User input Lots
if lao.askForNumberOfLots(dUpdate['Classification__c']):
	print('\n Current Lots: {0}'.format(dd['Lots__c']))
	ui = td.uInput('\n Type number of Lots or [ENTER] to accept exiting number. > ')
	if ui != '':
		dUpdate['Lots__c'] = int(ui)
# *******************************************************************************

# BUYER ACTING AS ***************************************************************
# User Input Buyer Acting As
dUpdate['Buyer_Acting_As__c'] = lao.chooseBuyerActingAs()
# *******************************************************************************

# FORMAT SALE PRICE, DATE AND ADD OWNERID, OPR SENT *****************************
td.banner('TF AWS Lead To Sale v01')
print(' PID: {0}'.format(PID))
# Format Sale Price for SalesForce
dUpdate['Sale_Price__c'] = dd['Sale_Price__c'].replace('$', '').replace(',', '')
# Format Sale Date for SalesForce
dUpdate['Sale_Date__c'] = bb.formatDateToSF(dd['Sale_Date__c'])
# Add Researcher OwnerId to record
dUpdate['OwnerId'] = bb.createdByResearch(service)
dUpdate['OPR_Sent__c'] = '1965-01-11T00:00:00+00:00'
# *******************************************************************************

# DEAL TO RESEARCH TYPE *********************************************************
# # Set Deal to Research Type
# # Brokerage: 012a0000001ZSS5AAO Research: 012a0000001ZSS8AAO
bb.changeDealTypeToReserach(service, DID)
# Update Deal
results = bb.sfupdate(service, dUpdate)
# *******************************************************************************

# OFFER *************************************************************************
# Add Offer to Deal
dOffer = {'type': 'lda_Offer__c', 'DealID__c': DID, 'Offer_Price__c': dUpdate['Sale_Price__c'], 'Offer_Date__c': dUpdate['Sale_Date__c'], 'Date_Accepted__c': dUpdate['Sale_Date__c'], 'Offer_Status__c': 'Accepted'}
# Add Owner Person to object if BTX != BPR
if BPRID != 'None':
	dOffer['Buyer__c'] = BPRID
# Add Owner Entity to object if BTX != BPR
if BTX != 'None':
	dOffer['Buyer_Entity__c'] = BTXID
results = bb.sfcreate(service, dOffer)
if results[0]['success']:
	print('\n Offer created successfully...')
else:
	print('Offer was not created...')
	print(results)
	exit('Terminating program...')
# ******************************************************************************

# Close the Deal after offer is made
dup = {'type': 'lda_Opportunity__c', 'id': DID, 'StageName__c': 'Closed Lost', 'Sale_Date__c': dUpdate['Sale_Date__c'], 'Sale_Price__c': dUpdate['Sale_Price__c']}
results = service.update(dup)

# Write record created results file
with open('C:/Users/Public/Public Mapfiles/Power PID Producer TF Record Results.txt', 'w') as f:
	f.write('Success')

# Create new Lead
if not 'Option' in dUpdate['Lot_Type__c']:
	while 1:
		ui = td.uInput('\n Create Lead? [0/1] > ')
		if ui == '1':
			leadPID = bb.sfgeneratelead(service, DEALID=DID)
			print('\n TF Lead created, making polygon...')
			aws.make_AWS_OwnerIndex_Poly_from_OwnerIndex_Poly(PID, PIDnew=leadPID, runASW=True)
			break
		elif ui == '0':
			break
		else:
			td.warningMsg('\n Invalid input...try again...')


