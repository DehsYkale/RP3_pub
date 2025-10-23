# Updates an existing PID field with the selected parcels from M1

import aws
import bb
import dicts
import lao
import fun_login
import fun_text_date as td
import fjson
from pprint import pprint

td.banner('M1 Update PID with Selected Parcels v01')

service = fun_login.TerraForce()

# Make sure the use selected the parces in M1 withing the last 90 seconds
while 1:
	if not aws.was_file_modified_recently():
		td.warningMsg('\n M1 submitted parcels were created more than 90 seconds.\n\n Confirm the parcels in M1 and click Save Parcels.')
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	else:
		break


# Download the the M1 json file to local M1_Files folder
aws.get_m1_file_copy(action='DOWN')

filename_make_PID = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'
d = fjson.getJsonDict(filename_make_PID)

lParcels = []
for row in d:
	lParcels.append(d[row]['apn'])

lead_parcel = lParcels[0]
parcels = ', '.join(lParcels)

PID = td.uInput('\n Enter PID or [00] > ')
if PID == '' or PID == '00':
	exit('\n Terminating program...')

DID = bb.getDIDfromPID(service, PID)

dUpdate = dicts.get_blank_deal_update_dict(DID=DID)
dUpdate['Lead_Parcel__c'] = lead_parcel
dUpdate['Parcels__c'] = parcels

bb.tf_update_3(service, dUpdate)

ui = td.uInput('\n Continue... > ')
