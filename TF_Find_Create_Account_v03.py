# Find/Create Account in TF

# import acc1 as acc
import acc
import bb
import cpypg
import fun_login
import fun_text_date as td
import lao
from pprint import pprint
from webbrowser import open as openbrowser
import webs

def findCreateAccount_old(STX, street, city, state, zipcode):
	# Find Create Seller/Owner Entity if not already in Ownership record
	STX, STXID, RTYID, business_dict = bb.findCreateAccountEntity(service, NAME=STX, CITY=city, STATE=state, URL='None', STREET=street, ZIPCODE=zipcode, PHONE='None')
	# If not Seller/Owner Entity the set Seller/Owner Person variable to None
	if STXID == 'None':
		SPR, STX, SPRID = STX, 'None', 'None'
	# Else check if Seller/Owner Person is already associated with Seller/Owner Entity
	else:
		SPR, SPRID, RTYID = bb.findPersonsOfEntity(service, STXID)
	if SPRID == 'None' and STXID != 'None':
		driver = webs.getEntityContact(STX, state)
		if driver != None:
			driver.quit()

	# If Seller/Owner Person not established then find/create it
	if SPRID == 'None':
		SPR, SPRID, RTY = bb.findCreateAccountPerson(service, NAME=SPR, CITY=city, STATE=state, URL='None',STREET=street, ZIPCODE=zipcode, PHONE='None', EMAIL='None', EID=STXID, MOBILE='None', AGENT='None', COMPANY=STX)

	return STXID, SPRID, STX, SPR

def findCreateAccount(dAcc):
	# Find Create Seller/Owner Entity if not already in Ownership record
	dAcc = acc.find_create_account_entity(service, dAcc)
	# If not Seller/Owner Entity the set Seller/Owner Person variable to None
	if dAcc['AID'] == 'None':
		acc.find_persons_of_entity(service, dAcc)

	return dAcc

lao.consoleArcMapSizeColor()
td.console_title('TF Find Create Account v02')

service = fun_login.TerraForce()

# Choose if record will be a Lead or a Sale
td.banner('Find Create Entity and Person')
print(' Choose Record Type')
print('\n - Select Lead for Reonomy Comps, MVP or Competitor Listings')
print(' - Select Sale for manually entering a sale.')
print('\n  1) Lead')
print('  2) Sale')
print(' 00) Quit')
while 1:
	ui = td.uInput('\n Select > ')
	if ui == '1':
		recordType = 'Lead'
		break
	elif ui == '2':
		recordType = 'Sale'
		break
	elif ui == '00':
		with open('C:/TEMP/ArcMakePIDFromParcelOwnerInfo.txt', 'w') as f:
			f.write('Quit')
		exit()
	else:
		td.warningMsg('\n Invalid input...try again...')

# Choose from list of parcel owners
td.banner('Find Create Entity and Person')
index = 0
with open('C:/TEMP/ArcMakePIDFromParcelOwnerInfo.txt', 'r') as f:
	eof = (f.readline()).strip()
	onlyonerecord = True
	while eof != 'EoF':
		print('\n****************************\n')
		print(eof)
		print((f.readline()).strip())
		print((f.readline()).strip())
		print((f.readline()).strip())
		print((f.readline()).strip())
		print((f.readline()).strip())
		eof = (f.readline()).strip()
		if 'Index' in eof:
			onlyonerecord = False
		
	f.seek(0)
	if onlyonerecord:
		ui = 'Index 1'
	else:
		ui = 'Index {0}'.format(td.uInput('\n Select Entity/Person to use buy Index Number > '))

	while 1:
		dAcc = dicts.get_blank_account_dict()
		print('\n {0}\n'.format(ui))
		if ui == (f.readline()).strip():
			dAcc['ENTITY'] = (f.readline()).strip()
			dAcc['STREET']  = (f.readline()).strip()
			dAcc['STREET'] = td.titlecase_street(dAcc['STREET'])
			dAcc['CITY']  = (f.readline()).strip()
			dAcc['CITY'] = dAcc['CITY'].title()
			dAcc['STATE']  = (f.readline()).strip()
			dAcc['ZIPCODE']  = (f.readline()).strip()
			dAcc['SOURCE'] = 'Parcel'
			break

td.banner('Find Create Entity and Person')


# Find Create Seller/Owner Entity if not already in Ownership record
dAcc = acc.find_create_account_entity(service, dAcc)
temp1, temp2, dAcc = acc.find_create_account_person(service, dAcc)

# Is the Account the Owner or the Buyer
if recordType == 'Sale':
	td.banner('Find Create Entity and Person')
	print(' {0}'.format(nameEntity))
	print(' {0}'.format(street))
	print(' {0}, {1}, {2}\n'.format(city, state, zipcode))
	print('\n Is this the Buyer or the Seller?')
	print('\n 1) Buyer')
	print(' 2) Seller')
	while 1:
		ui = td.uInput('\n Select > ')
		if ui == '1':
			print('\n You chose {0}, {1} as the Buyer...'.format(nameEntity, namePerson))
			idBuyerEntity = dAcc['EID']
			idBuyerPerson = dAcc['AID']
			nameBuyerEnity = dAcc['ENTITY']
			nameBuyerPerson = dAcc['NAME']
			# idBuyerEntity = idEntity
			# idBuyerPerson = idPerson
			# nameBuyerEnity = nameEntity
			# nameBuyerPerson = namePerson
			break
		elif ui == '2':
			print('\n You chose {0}, {1} as the Seller...'.format(nameEntity, namePerson))
			idBuyerEntity = 'None'
			idBuyerPerson = 'None'
			nameBuyerEnity = 'None'
			nameBuyerPerson = 'None'
			idSellerEntity = dAcc['EID']
			idSellerPerson = dAcc['AID']
			nameSellerEnity = dAcc['ENTITY']
			nameSellerPerson = dAcc['NAME']
			# idSellerEntity = idEntity
			# idSellerPerson = idPerson
			# nameSellerEnity = nameEntity
			# nameSellerPerson = namePerson
			break
		else:
			td.warningMsg('\n Invalid input...try again...')
else:
	idBuyerEntity = 'None'
	idBuyerPerson = 'None'
	nameBuyerEnity = 'None'
	nameBuyerPerson = 'None'
	idSellerEntity = dAcc['EID']
	idSellerPerson = dAcc['AID']
	nameSellerEnity = dAcc['ENTITY']
	nameSellerPerson = dAcc['NAME']
	# idSellerEntity = idEntity
	# idSellerPerson = idPerson
	# nameSellerEnity = nameEntity
	# nameSellerPerson = namePerson

# If entering Sale record have user enter the Buyer or Seller
if recordType == 'Sale':
	dAcc = dicts.get_blank_account_dict()
	td.banner('Find Create Entity and Person')
	# Enter Buyer
	if idBuyerEntity == 'None':
		dAcc['NAME'] = td.uInput(' Enter Buyer > ')
		dAcc = cpypg.start_cpypg(dAcc)
		# idBuyerEntity, idBuyerPerson, nameBuyerEnity, nameBuyerPerson = findCreateAccount(ui, 'None', 'None', 'None', 'None')
		idBuyerEntity = dAcc['EID']
		idBuyerPerson = dAcc['AID']
		nameBuyerEnity = dAcc['ENTITY']
		nameBuyerPerson = dAcc['NAME']
	# or Enter Seller
	else:
		dAcc['NAME'] = td.uInput(' Enter Seller > ')
		dAcc = cpypg.start_cpypg(dAcc)
		# idSellerEntity, idSellerPerson, nameSellerEnity, nameSellerPerson = findCreateAccount(ui, 'None', 'None', 'None', 'None')
		idSellerEntity = dAcc['EID']
		idSellerPerson = dAcc['AID']
		nameSellerEnity = dAcc['ENTITY']
		nameSellerPerson = dAcc['NAME']

# Write Owner Entity and AccountID to text file
with open('C:/TEMP/ArcMakePIDFromParcelOwnerInfo.txt', 'w') as f:
	# f.write('{0}\n{1}\n{2}\n{3}\n{4}\n'.format(STXID, SPRID, STX, SPR, accountRoll))
	f.write('Buyer\n')
	f.write('{0}\n'.format(idBuyerEntity))
	f.write('{0}\n'.format(idBuyerPerson))
	f.write('{0}\n'.format(nameBuyerEnity))
	f.write('{0}\n'.format(nameBuyerPerson))
	f.write('Seller\n')
	f.write('{0}\n'.format(idSellerEntity))
	f.write('{0}\n'.format(idSellerPerson))
	f.write('{0}\n'.format(nameSellerEnity))
	f.write('{0}\n'.format(nameSellerPerson))
