#Python3

# Takes two dictionaries one the user created dAcc
#   and the other the current TF contact info
#   dict and finds differences and asks the user if
#   they want to update the TF record

import acc
import bb
import fun_text_date as td
import lao
from pprint import pprint
import re


def update_contact(service, dAcc, dTFCon):
	
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_contact]', 'YELLOW')
	
	# Set the intial variable values in dAcc from dTFCon and get the update dict (dup)
	dAcc, dTFCon, dup = set_dAcc_variable_values(dAcc, dTFCon)
	# Update the address
	dAcc, dTFCon, dup = update_address(dAcc, dTFCon, dup)
	# Add Phone numbers
	dAcc, dTFCon, dup = update_phone(dAcc, dTFCon, dup)
	# Update Entity/company
	dAcc, dTFCon, dup = update_entity(dAcc, dTFCon, dup)
	# Update Category
	dAcc, dTFCon, dup = update_category(dAcc, dTFCon, dup)
	# Update Email
	dAcc, dTFCon, dup = update_email(dAcc, dTFCon, dup)
	
	# Update changes to TF
	if dAcc['UPDATERECORD'] is True:
		bb.tf_update_3(service, dup)
		dAcc['UPDATERECORD'] = False
	
	return dAcc

# Set the intial variable values in dAcc from dTFCon
def set_dAcc_variable_values(dAcc, dTFCon):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def set_dAcc_variable_values]', 'YELLOW')
	# Set dict None values to 'None'
	dAcc = acc.dict_blank_fields_to_none(dAcc)
	dTFCon = acc.dict_blank_fields_to_none(dTFCon)

	# Set dAcc ariables
	dAcc['UPDATERECORD'] = False
	dAcc['NF'] = dTFCon['FirstName']
	dAcc['NL'] = dTFCon['LastName']
	dAcc['NAME'] = '{0} {1}'.format(dAcc['NF'], dAcc['NL'])
	dAcc['AID'] = dTFCon['Id']
	print('\n {0} selected...Updating existing account...'.format(dAcc['NAME'] ))
	dTFCon['ValidEmail'] = ''

	# Create the update dict
	dup = {'type': 'Account', 'id': dAcc['AID']}

	return dAcc, dTFCon, dup

# Update the address
def update_address(dAcc, dTFCon, dup):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_address]', 'YELLOW')
	# Add address if none
	if dTFCon['BillingStreet'] == 'None':
		if dAcc['STREET'] != 'None':
			STREET = td.titlecase_street(dAcc['STREET'])
			dup['BillingStreet'] = STREET
			dup['BillingCity'] = dAcc['CITY'].title()
			dup['BillingState'] = dAcc['STATE']
			dAcc['STATEOFORIGIN'] = dAcc['STATE']
			dup['BillingPostalCode'] = dAcc['ZIPCODE']
			dAcc['UPDATERECORD'] = True
		# No Billing Address so ask user to enter one if available
		else:
			td.warningMsg('\n Contact is missing an address...')
			dAcc = acc.get_missing_address(dAcc, search_for='Person Address')

	# Address Mismatch allow user to update
	if dAcc['STREET'] != 'None':
		update_account = False
		mismatch_street = False
		mismatch_city = False
		mismatch_state = False
		mismatch_zipcode = False
		lStreet = dAcc['STREET'].split(' ')
		if not lStreet[0].upper() in dTFCon['BillingStreet'].upper():
			update_account = True
			mismatch_street = True
		# if not lStreet[1].upper() in dTFCon['BillingStreet'].upper():
		# 	update_account = True
		# 	mismatch_street = True
		if dAcc['CITY'] != 'None' and dTFCon['BillingCity'].upper() != dAcc['CITY'].upper():
			update_account = True
			mismatch_city = True
		if dAcc['STATE'] != 'None' and dTFCon['BillingState'].upper() != dAcc['STATE'].upper():
			update_account = True
			mismatch_state = True
		if dAcc['ZIPCODE'] != 'None' and str(dTFCon['BillingPostalCode']) != str(dAcc['ZIPCODE']):
			update_account = True
			mismatch_zipcode = True
		
		# Mismatches found as user to update
		if update_account:
			td.warningMsg('\n POSSIBLE ADDRESS MISMATCH\n')
			msg = \
				' ADDRESS IN TF      {0}\n' \
				'                    {1}, {2} {3}\n\n' \
				' UPDATE ADDRESS     {4}\n' \
				'                    {5}, {6} {7}\n' \
			.format(
				dTFCon['BillingStreet'],
				dTFCon['BillingCity'],
				dTFCon['BillingState'],
				dTFCon['BillingPostalCode'],
				dAcc['STREET'],
				dAcc['CITY'],
				dAcc['STATE'],
				dAcc['ZIPCODE'])
			print(msg)

			# Update Address ask user
			if mismatch_street:
				ui = td.uInput('\n Update Address in TF [0/1/00] > ')
				if ui == '1':
					STREET = td.titlecase_street(dAcc['STREET'])
					dup['BillingStreet'] = STREET
					dup['BillingCity'] = dAcc['CITY'].title()
					dup['BillingState'] = dAcc['STATE']
					dup['BillingPostalCode'] = dAcc['ZIPCODE']
					print('\n Address updated...\n')
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n Address not updated.')
				mismatch_city = False
				mismatch_state = False
				mismatch_zipcode = False
			if mismatch_city:
				ui = td.uInput('\n Update CITY in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingCity'] = dAcc['CITY'].title()
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n City not updated.')
			if mismatch_state:
				ui = td.uInput('\n Update STATE in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingState'] = dAcc['STATE']
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n State not updated.')
			if mismatch_zipcode:
				ui = td.uInput('\n Update ZIP CODE in TF [0/1/00] > ')
				if ui == '1':
					dup['BillingPostalCode'] = dAcc['ZIPCODE']
					dAcc['UPDATERECORD'] = True
				elif ui == '00':
					exit('\n Terminating program...')
				else:
					td.warningMsg('\n Zip Code not updated.')
	
	return dAcc, dTFCon, dup

# Update Category
def update_category(dAcc, dTFCon, dup):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_category]', 'YELLOW')
	if 'CATEGORY' in dAcc.keys():
		if dAcc['CATEGORY'] != 'None':
			# dAcc['UPDATERECORD'] = True
			# Create a list of dAcc Categories
			if ';' in dAcc['CATEGORY']:
				lCategory_dAcc = dAcc['CATEGORY'].split(';')
			else:
				lCategory_dAcc = [dAcc['CATEGORY']]
			
			# Assign dTFCon Categories to a string variable
			if dTFCon['Category__c'] == 'None':
				# lCategory_dTFCon = []
				str_category = 'None'
			else:
				str_category = dTFCon['Category__c']

			# Write Categories to dup
			# dup['Category__c'] = ';'.join(lCategory_dAcc)
			for cat in lCategory_dAcc:
				if not cat in str_category:
					if str_category == 'None':
						str_category = cat
						dAcc['UPDATERECORD'] = True
					else:
						str_category = f'{str_category};{cat}'
						dAcc['UPDATERECORD'] = True

			if dAcc['UPDATERECORD'] is True:
				dup['Category__c'] = str_category

			# if lCategory_dTFCon != []:
			# 	for cat in lCategory_dTFCon:
			# 		if not cat in dup['Category__c']:
			# 			dup['Category__c'] = '{0};{1}'.format(dup['Category__c'], cat)
	
	return dAcc, dTFCon, dup

# Add Phone, Mobile, Home Phone if blank
def update_phone(dAcc, dTFCon, dup):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_phone]', 'YELLOW')
	# Add Mobile
	if dTFCon['PersonMobilePhone'] == 'None' and dAcc['MOBILE'] != 'None':
		dAcc['MOBILE'] = td.phoneFormat(dAcc['MOBILE'])
		dup['PersonMobilePhone'] = dAcc['MOBILE']
		dAcc['UPDATERECORD'] = True

	# Add Home Phone
	try:
		if dTFCon['PersonHomePhone'] == 'None' and dAcc['PHONEHOME'] != 'None':
			dAcc['PHONEHOME'] = td.phoneFormat(dAcc['PHONEHOME'])
			dup['PersonHomePhone'] = dAcc['PHONEHOME']
			dAcc['UPDATERECORD'] = True
	except KeyError:
		pass

	# Add Phone if None
	if dTFCon['Phone'] == 'None' and dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
		dup['Phone'] = dAcc['PHONE']
		dAcc['UPDATERECORD'] = True

	# Add Phone to 'Other Phone' if different from number already entered
	elif dTFCon['Phone'] != 'None' and dAcc['PHONE'] != 'None' and dAcc['PHONE'] != 'Skip':
		# Remove punctuation just leaving digits
		tfPhone = re.sub("[^0-9]", "", dTFCon['Phone'])
		uiPhone = re.sub("[^0-9]", "", dAcc['PHONE'])
		if tfPhone != uiPhone:
			dAcc['PHONE'] = td.phoneFormat(dAcc['PHONE'])
			dup['PersonOtherPhone'] = dAcc['PHONE']
			dAcc['UPDATERECORD'] = True
	
	# Give user option to add Phone if none exists
	elif dTFCon['Phone'] == 'None' and dAcc['PHONE'] == 'None' and dTFCon['PersonMobilePhone'] == 'None' and dAcc['MOBILE'] == 'None':
		# dAcc = enterPhoneNumber(dAcc)
		dAcc = acc.get_missing_phone(dAcc, search_for='Person Phone')
		if dAcc['PHONE'] != 'None' or dAcc['PHONE'] != 'Skip':
			dup['Phone'] = dAcc['PHONE']
			dAcc['UPDATERECORD'] = True
	
	return dAcc, dTFCon, dup

# Update Entity/company
def update_entity(dAcc, dTFCon, dup):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_entity]', 'YELLOW')
	# Update Company
	if dAcc['EID'] != 'None' and dTFCon['Company__c'] == 'None':
		dup['Company__c'] = dAcc['EID']
		dAcc['UPDATERECORD'] = True
	elif dAcc['ENTITY'] != 'None' and dTFCon['Company__c'] == 'None':
		import fun_login
		service = fun_login.TerraForce()
		dAcc = acc.find_create_account_entity(service, dAcc)
		dup['Company__c'] = dAcc['EID']
		dAcc['UPDATERECORD'] = True
	# Mismatched companies
	elif dAcc['ENTITY'] != 'None' and dTFCon['Company__c'] != 'None':
		if dAcc['EID'] != dTFCon['Company__c']:
			td.warningMsg('\n POSSIBLE COMPANY MISMATCH\n')
			msg = \
				' COMPANY IN TF     {0}\n\n' \
				' UPDATE COMPANY    {1}\n' \
			.format(
				dTFCon['Company__r']['Name'],
				dAcc['ENTITY'])
			print(msg)
			ui = td.uInput('\n Update company in TF [0/1/00] > ')
			if ui == '1':
				dup['Company__c'] = dAcc['EID']
				dAcc['UPDATERECORD'] = True
			elif ui == '00':
				exit('\n Terminating program...')
	
	return dAcc, dTFCon, dup

# Update Email
def update_email(dAcc, dTFCon, dup):
	if lao.getUserName() == 'blandis':
		td.colorText(' [fun_update_contact def update_email]', 'YELLOW')
	if dAcc['EMAIL'] != 'None':
		# Add Email to Account if blank
		if dTFCon['PersonEmail'] == 'None':  # Add Email to Account
			dup['PersonEmail'] = dAcc['EMAIL']
			dAcc['UPDATERECORD'] = True
		elif dTFCon['PersonEmail'].lower() != dAcc['EMAIL'].lower():
			print('\n Email in TF: {0}'.format(dTFCon['PersonEmail'].lower()))
			print(' New Email  : {0}'.format(dAcc['EMAIL'].lower()))
			uin = td.uInput('\n Update Email Address? [0/1/00] > ')
			if uin == '1':
				if dTFCon['PersonEmail'].lower() in dTFCon['Description']:
					pass
				elif dTFCon['Description'] == 'None':
					dAcc['DESCRIPTION'] = 'Possible email: {0}'.format(dTFCon['PersonEmail'].lower())
				elif uin == '00':
					exit('\n Terminating program...')
				else:
					dAcc['DESCRIPTION'] = '{0}\r\nPossible email: {0}'.format(dTFCon['Description'], dTFCon['PersonEmail'].lower())
				dup['PersonEmail'] = dAcc['EMAIL']
				dup['Description'] = dAcc['DESCRIPTION']
				dAcc['UPDATERECORD'] = True
	elif dAcc['EMAIL'] == 'None' and dTFCon['PersonEmail'] == 'None':
		while 1:
			uin = td.uInput('\n Add Email Address or [Enter] for none > ')
			if uin == '':
				break
			elif '@' not in uin:
				td.warningMsg('\n Improperly formatted email address...try again...')
			else:
				dAcc['EMAIL'] = uin
				dup['PersonEmail'] = dAcc['EMAIL']
				dAcc['UPDATERECORD'] = True
				break
	
	return dAcc, dTFCon, dup