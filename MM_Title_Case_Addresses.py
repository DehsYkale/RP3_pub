
import bb
import lao
from pprint import pprint
import fun_login
import fun_text_date as td


# Titlecase Street Address String
def titlecase_street(street):
	if street.isupper():
		if 'PO BOX' in street:
			street = street.replace('PO BOX', 'PO Box')
		elif 'P O BOX' in street:
			street= street.replace('P O BOX', 'PO Box ')
		elif 'P.O. BOX' in street:
			street= street.replace('P.O. BOX', 'PO Box ')
		elif street[:4] == 'BOX ':
			street = street.replace('BOX ', 'PO Box ')
		else:
			street = ' '.join([i.title() if i.isalpha() else i.lower() for i in street.split()]) # titlecases everything but ordinals (ie. 3RD to 3rd)
		if ' Sr ' in street:
			street = street.replace(' Sr ', ' SR ')
		if ' Cr ' in street:
			street = street.replace(' Cr ', ' CR ')
		if ' Fm ' in street:
			street = street.replace(' Fm ', ' FM ')
		if ' u.s. ' in street:
			street = street.replace(' u.s. ', ' U.S. ')
	return street

service = fun_login.TerraForce()



# fields = 'Id, BillingStreet, BillingCity, BillingState, BillingPostalCode, Name, Category__c, TOP100__c'
# wc = "BillingStreet != '' AND Category__c INCLUDES ('Market Mailer') AND IsPersonAccount = TRUE AND TOP100__c != NULL"
# qs = "SELECT {0} FROM Account WHERE {1}".format(fields, wc)
# results = bb.sfquery(service, qs)

# TerraForce Query
fields = 'default'
wc = "BillingStreet != '' AND Category__c INCLUDES ('Market Mailer') AND TOP100__c != NULL"
results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
# pprint(results)
# print

count = len(results)
counter = 1
for row in results:
	
	updateAddress = False
	dup = {'type': 'Account',
		'Id': row['Id']}
	if row['BillingStreet'].isupper():
		lstreet_split = row['BillingStreet'].split(' ')
		# Filter out SLC addresses (e.g. 400 N 500 W)
		for part in lstreet_split:
			print(part)
			try:
				int(part)
			except ValueError:
				# print('False')
				if len(part) > 1:
					updateAddress = True
					break
			# else:
			# 	print('True')
			# ui = lao.uInput('\n Continue... > ')
		if updateAddress:
			dup['BillingStreet'] = titlecase_street(row['BillingStreet'])
			# dup['BillingStreet'] = 
		
	if row['BillingCity'].isupper():
		dup['BillingCity'] = row['BillingCity'].title()
		updateAddress = True

	if updateAddress:
		print('\n {0} of {1}'.format(counter, count))
		print(' Dirty: {0}'.format(row['BillingStreet']))
		print(' Clean: {0}'.format(dup['BillingStreet']))
		upResults = bb.sfupdate(service, dup, quit_if_fail='Pause')
		# webs.openTFDID(row['Id'])
		# ui = lao.uInput('\n Continue [00]... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')

	counter += 1


# Titlecase Street Address String
# def titlecase_street(street):
# 	if street.isupper():
# 		if 'PO BOX' in street:
# 			street = street.replace('PO BOX', 'PO Box')
# 		elif 'P.O. BOX' in street:
# 			street= street.replace('P.O. BOX', 'PO Box ')
# 		elif street[:4] == 'BOX ':
# 			street = street.replace('BOX ', 'PO Box ')
# 		else:
# 			street = street.title()
# 	return street
# 	title_Case_BillingStreet




