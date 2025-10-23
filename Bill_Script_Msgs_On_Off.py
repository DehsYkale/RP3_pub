# Turns Banner and Fuction messages on and off for Bill script testing

import fun_text_date as td
from json import dump
import fjson
import lao
from pprint import pprint

# Read the bill script messages on off json file
def read_bill_script_msgs_on_off(msg_type='Dict'):
	from json import load
	# lao.print_function_name('fjson def readBillScriptMsgsOnOffJsonFile')
	json_file = '{0}bill_script_msgs_on_off.json'.format(lao.getPath('py3Data'))
	with open(json_file, 'r') as f:
		dMsgs = load(f)
	if msg_type == 'Banner':
		return dMsgs['Banner']
	elif msg_type == 'Functions':
		return dMsgs['Functions']
	elif msg_type == 'Dict':
		return dMsgs

json_file = '{0}bill_script_msgs_on_off.json'.format(lao.getPath('py3Data'))


while 1:
	td.banner('Bill Script Msgs On Off')

	# Read the json file
	# with open(json_file, 'r') as f:
	# 	dMsgs = load(f)
	dMsgs = fjson.read_bill_script_msgs_on_off(msg_type='Dict')
	

	if dMsgs['Banner'] == 'On':
		td.colorText("  1) Banner don't clear screen is On", 'GREEN')
	else:
		print("  1) Banner don't clear screen is Off")

	if dMsgs['Functions'] == 'On':
		td.colorText('  2) Function printing is On', 'GREEN')
	else:
		print('  2) Function printing is Off')
	print(' 00) Quit')

	ui = td.uInput('\n Select > ')
	if ui == '00':
		exit('\n Terminating program...')
	elif ui == '1':
		if dMsgs['Banner'] == 'On':
			dMsgs['Banner'] = 'Off'
		else:
			dMsgs['Banner'] = 'On'
	elif ui == '2':
		if dMsgs['Functions'] == 'On':
			dMsgs['Functions'] = 'Off'
		else:
			dMsgs['Functions'] = 'On'
	
	lao.print_function_name('Bill Script Msgs On Off')
	
	# Write the json file
	with open(json_file, 'w') as f:
		dump(dMsgs, f)



