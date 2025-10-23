# Safe delete a PID from TerraForce and OwnerIndex polygon

__author__ = 'blandis'

import aws
import bb
import dicts
import fjson
import fun_login
import lao
import fun_text_date as td

# Check if the zoomToPolygon.json file was made recently
def is_pid_current():
	while 1:
		td.banner('M1 Safe PID Delete v01')
		is_recent = aws.was_file_modified_recently('Zoom To Polygon')
		if is_recent is False:
			td.warningMsg('\n GUI submitted PID was created more than 90 seconds.\n\n Confirm the PID in the GUI and click Submit.')
			print('\n OPTIONS:')
			print('\n [Enter] PID submitted, try again')
			print(' Type in a PID')
			print(' [00] Quit')
			ui = td.uInput('\n  > ')
			if ui == '00':
				exit('\n Terminating program...')
			elif ui == '':
				continue
			elif len(ui) > 5:
				PID = ui
				break
			else:
				td.warningMsg('\n Invalid input...try again.')
				lao.sleep(2)
		else:
			break

service = fun_login.TerraForce()
user, userInitials = lao.getUserName(initials=True)

is_pid_current()

# Read json file
dZoom_To_Polygon = fjson.getJsonDict('C:/Users/Public/Public Mapfiles/M1_Files/zoomToPolygon.json')
# Get PID & DID
PID = dZoom_To_Polygon['polyId']
DID = bb.getDIDfromPID(service, PID)
if DID == 'No PID Exists':
	exit('\n Terminating program...')

while 1:
	td.banner('M1 Safe PID Delete v01')
	print(' PID: {0}'.format(PID))
	print('\n  0) No')
	print('  1) Yes')
	print(' 00) Quit')
	ui = td.uInput('\n Delete PID? > ')
	if ui == '00':
		print('\n Delete PID canceled.')
		exit('\n Terminating program...')
	elif ui == '0':
		print('\n Delete PID canceled.')
		exit('\n Terminating program...')
	elif ui == '1':
		bb.safe_deal_delete(service, PID)
		exit('\n Fin')
	else:
		td.warningMsg('\n Invalid input...try again...')
		lao.sleep(2)


