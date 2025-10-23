# Opens and OPR map in a browser based on user input of PID

import lao
import fun_text_date as td
import webs

while 1:
	td.banner('Open OPR Map in Browser v01')
	# Get PID from user
	PID = td.uInput("Enter PID or [00] > ")
	if PID == '00':
		break
	elif PID == '':
		td.warningMsg('PID cannot be blank')
		lao.sleep(2)
		continue
	PID = PID.strip()
	
	print('\n Open...')
	print('\n  1) OPR Map')
	print('  2) Listing Brochure')
	print('  3) Both')
	print(' 00) Quit')
	ui = td.uInput('\n Select > ')
	if ui == '1':
		webs.open_opr_map_in_browser(PID)
	elif ui == '2':
		webs.open_listing_brochure_in_browser(PID)
	elif ui == '3':
		webs.open_opr_map_in_browser(PID)
		webs.open_listing_brochure_in_browser(PID)
	elif ui == '00':
		break
	else:
		td.warningMsg('Invalid selection')
		lao.sleep(2)

exit('\n Fin')