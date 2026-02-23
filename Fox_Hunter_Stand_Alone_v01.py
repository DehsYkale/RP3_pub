
import fun_text_date as td
import fun_fox_hunter as fh

td.banner('Fox Hunter Stand Alone v0.1')

company_name = td.uInput('\n Enter Company or Person Name [00] > ')
if company_name.strip() == '':
	exit('\n No name provided. Terminating program...')

address_full = td.uInput('\n Enter Full Company Address [00] > ')
if address_full.strip() == '':
	exit('\n No address provided. Terminating program...')

company_name = company_name.strip()
address_full = address_full.strip()

results = fh.main(company_name, address_full)

ui = td.uInput('\n Continue [00]... > ')
if ui == '00':
	exit('\n Terminating program...')

exit('\n fin')