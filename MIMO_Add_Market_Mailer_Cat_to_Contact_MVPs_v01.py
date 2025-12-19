# Add "Market Mailer" to Contact Category of MVPs

import bb
import dicts
import fun_login
import fun_text_date as td
import lao
from pprint import pprint

td.banner('MIMO Add Market Mailer Cat to Contact MVPs')
service = fun_login.TerraForce()

advisor_name = 'Zach Hartman'
dAdvisor = dicts.get_staff_dict_2()
advisor_id = dAdvisor[advisor_name]['Id']

# TerraForce Query
fields = 'default'
wc = f"Top100__c INCLUDES ('{advisor_name}') AND Category__c EXCLUDES ('Market Mailer')"
results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
# pprint(results)

# Add "Market Mailer" to Contact Category of MVPs
for rec in results:
	contact_id = rec['Id']
	contact_name = rec['Name']
	
	
	print(f' Processing Contact: {contact_name} (ID: {contact_id})')

	dUpdate = {
		'type': 'Account',
		'Id': contact_id
	}

	if rec['Category__c'] == 'None':
		# Set Category to "Market Mailer" if no other categories exist
		dUpdate['Category__c'] = 'Market Mailer;Zach Hartman'
	elif 'Zach Hartman' in rec['Category__c']:
		# Append "Market Mailer" if Zach Hartman exist
		dUpdate['Category__c'] = f"{rec['Category__c']};Market Mailer"
	else:
		# Set Category to "Market Mailer" if categories exist but not Zach Hartman
		dUpdate['Category__c'] = f"{rec['Category__c']};Market Mailer;Zach Hartman"
	
	# pprint(dUpdate)

	bb.tf_update_3(service, dUpdate)
