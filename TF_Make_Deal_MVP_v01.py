# Open LLR and Make missing MVPs MPVs

import lao
import bb
import datetime
import fun_login
import fun_text_date as td
from pprint import pprint
from os import rename, remove
import shutil
import webs

def get_llr_dict():
	llr_path = 'F:/Research Department/Lot Comps Components/Archive/'
	llr_filename = lao.guiFileOpen(path=llr_path, titlestring='Select LLR File', extension=[('Excel files', '.xlsx'), ('all files', '.*')])
	dLLR = lao.spreadsheetToDict(llr_filename, sheetname='MVP Deals')
	return dLLR

lao.banner("Add Brochure to TF Deal Recored v01")
service = fun_login.TerraForce()
dLLR = get_llr_dict()

for row in dLLR:
	lao.banner("Make Deal MVP v01")
	dRec = dLLR[row]
	pprint(dRec)
	# Skip Deals with Brochures and older than 18 months
	if dRec[' 3'] != '--':
		continue
	elif is_more_than_18_months_old(dRec['List Date']):
			continue

	DID = dRec[' 2'].split(',')[0]
	DID = DID.replace('=HYPERLINK("https://landadvisors.my.salesforce.com/', '').replace('"', '')
	PID = bb.getPIDfromDID(service, DID)
	