#! python3

import lao
lao.banner('Py3 Working')

import colored
import acc
import bb
import fun_login
import fun_text_date as td
import sys
from pprint import pprint
import webs
import tkinter as tk
from tkinter import messagebox
# import arcgis
# from arcgis.gis import GIS
# exit()








# def show_message_box():
#     message = textbox.get("1.0", "end-1c")  # Get the contents of the text box
#     messagebox.showinfo("Message", message)  # Open a message box with the contents

# # Create the main window
# window = tk.Tk()
# window.title("Text Box Message")

# # Create a text box
# textbox = tk.Entry(window, height=10, width=30)
# textbox.pack()

# # Create a button
# button = tk.Button(window, text="Show Message", command=show_message_box)
# button.pack()

# # Start the Tkinter event loop
# window.mainloop()


# exit()

service = fun_login.TerraForce()
dCounties = lao.getCounties('FullDict')
# TerraForce Query
fields = 'default'
wc = "Market__c = ''"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=1, fields=fields)
for row in results:
	print(row['PID__c'])
	DID = row['Id']
	pid_no_digits = ''.join([i for i in row['PID__c'] if not i.isdigit()])
	tf_state = pid_no_digits[:2]
	tf_county = pid_no_digits[2:]
	print(tf_state)
	print(tf_county)

	for rec in dCounties:
		lao_state = dCounties[rec]['State']
		lao_county = dCounties[rec]['ArcName']
		market = dCounties[rec]['Market']
		if tf_state == lao_state and tf_county == lao_county:
			print(market)
			dup = {'type': 'lda_Opportunity__c',
					'Id': DID,
					'Market__c': market}
			bb.tf_update_3(service, dup)

			exit()




exit()



lao.banner('MC Click & Open to TF v02')
campName = 'AZMaricopa251511_RQ-68560_06292023'
service = fun_login.TerraForce()
dFixThem = lao.spreadsheetToDict('C:/TEMP/MC LOG {0}.csv'.format(campName))
for contact in dFixThem:
	lao.banner('MC Click & Open to TF v02')
	dAcc = dicts.get_blank_account_dict()

	dAcc['NAME'] = '{0} {1}'.format(dFixThem[contact]['FirstName'], dFixThem[contact]['LastName'])
	dAcc['NF'] = dFixThem[contact]['FirstName']
	dAcc['NL'] = dFixThem[contact]['LastName']
	dAcc['ENTITY'] = dFixThem[contact]['Company']
	dAcc['PHONE'] = dFixThem[contact]['Phone']
	dAcc['EMAIL'] = dFixThem[contact]['Email']
	
	print('\n Contact Info')
	print('\n Name: {NAME}\n Entity: {ENTITY}\n Email: {EMAIL}'.format(**dAcc))

	if dAcc['ENTITY'] != 'None':
		dAcc = acc.find_create_account_entity(service, dAcc)

	name, AID, dAcc = acc.find_create_account_person(service, dAcc)
	ui = td.uInput('\n [Enter] to Continue, [1] to open TF or [00] to quit... > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		webs.openTFAccId(AID)

exit()


service = fun_login.TerraForce()

# TerraForce Query
# wc = "Name = 'Bill Landis'"
#wc = "PersonEmail = 'cpino@landadvisors.com' and PersonTitle != 'Program Manager'"
email = 'cpino@landadvisors.com'
wc = "PersonEmail = '{0}' and PersonTitle != 'Program Manager'".format(email)
results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None)
# print(results)
# pprint(results[0])
# exit()
print(' ###############################################################')
print('\n {Id}\n {Name}, {PersonEmail}'.format(**row))
print(' ###############################################################')
print('\n\n\n')
# driver = fun_login.L5()

# print(sys.version)
# lao.print_py_3_string('This is working!!!')
