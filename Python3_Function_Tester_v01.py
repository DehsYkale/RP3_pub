#!/C/Program\ Files/Python312/python.exe

import fun_text_date as td
td.banner('Python3 Function Tester v01')
print(' Importing Libraries...')

import acc
import aws
import bb
import cpypg
import dicts
import fjson
import fun_acc_entity as fae
import fun_login
import fun_update_contact
import how
import lao
import mc
import mpy
import rlb
import webs
import xxl

import re
import subprocess

td.colorText(' Libraries Imported successfully...', 'GREEN')

user = lao.getUserName().lower()
print(f'\n User: {user}')

print('\n Logging into Salesforce...')
service = fun_login.TerraForce()
print(' Login successful...')

print('\n Testing ASW, listing bucket files...\n')
bucket_files = subprocess.run(
		['aws', 's3', 'ls', f's3://research-datastore/{user}/'],
		capture_output=True,
		text=True,
		check=True
	)
text = bucket_files.stdout
print(text)
td.colorText(' AWS test successful...', 'GREEN')



