# Run Fox Hunter on a property owner with an address

import fun_fox_hunter as fh
import fun_text_date as td


td.banner('Fox Hunter Contact Finder V01')

print(' Enter a Property Owner/Company or [1] for test case [00]...')

company = td.uInput('\n Enter Property Owner/Company > ')

if company == '1':
	company = 'Espos Resturant LLC'
	address = '3863 W CHANDLER BLVD , CHANDLER, AZ 85226'
elif company == '00':
	exit('\n Terminating program...')
else:
	address = td.uInput('\n Enter full Property Address > ')

print('\n Running Fox Hunter Contact Finder AI on:')
print(f'   Company: {company}')
print(f'   Address: {address}\n')
results = fh.main(company, address)

exit('\n Fin')