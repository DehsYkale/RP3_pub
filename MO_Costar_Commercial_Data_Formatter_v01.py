# Formats CoStar commercial data exports for the Market Overviews

import lao
import fun_text_date as td
from pprint import pprint

def get_concept_name_dict():
	dConcept_name = {
		'Market Rent Growth 12 Mo': {'num_type': 'percentage', 'mo_label': 'Annual Rent Growth'},
		'Net Delivered SF 12 Mo': {'num_type': 'integer', 'mo_label': 'Delivered Sq. Ft.'},
		'Net Absorption SF 12 Mo': {'num_type': 'integer', 'mo_label': 'Absorption Sq. Ft.'},
		'Vacancy Rate': {'num_type': 'percentage', 'mo_label': 'Vacancy Rate'},
		'Under Construction Buildings': {'num_type': 'integer', 'mo_label': 'Properties'},
		'Under Construction SF': {'num_type': 'integer', 'mo_label': 'Construction Sq. Ft.'},
		'Inventory SF': {'num_type': 'integer', 'mo_label': 'Inventory Sq. Ft.'},
		'Market Asking Rent Growth 12 Mo': {'num_type': 'percentage', 'mo_label': 'Annual Rent Growth'},
		'Net Delivered Units 12 Mo': {'num_type': 'integer', 'mo_label': 'Delivered Units (12 mo)'},
		'Absorption Units 12 Mo': {'num_type': 'integer', 'mo_label': 'Absorption Units (12 mo)'},
		'Under Construction Units': {'num_type': 'integer', 'mo_label': 'Construction Units'},
		'Inventory Units': {'num_type': 'integer', 'mo_label': 'Inventory Units'},
		}
	return dConcept_name

cur_qtr = td.getDateQuarter()
cur_qtr_costar = '{0} {1} EST'.format(cur_qtr[:4], cur_qtr[4:])
lProperty_classes = ['Multifamily', 'Industrial', 'Retail', 'Office']

dConcept_name = get_concept_name_dict()

for prop_class in lProperty_classes:
	file_prop_class = f'F:\Research Department\MIMO\zData\CoStar\Commercial Market Reports/LAO Markets {prop_class} {cur_qtr}.xlsx'
	dSpreadsheet = lao.spreadsheetToDict(file_prop_class)
	print('-' * 40)

	# Check if cur_qtr_costar is EST
	if not cur_qtr_costar in dSpreadsheet[1]:
		cur_qtr_costar = '{0} {1}'.format(cur_qtr[:4], cur_qtr[4:])

	class_name, market = 'None', 'None'
	for mrkt_off in dSpreadsheet:
		r = dSpreadsheet[mrkt_off]

		if not r['Geography Name'] == 'Sarasota - FL' and not r['Geography Name'] == 'Tampa - FL':
			continue

		# pprint(r)
		if class_name != r['Property Class Name']:
			class_name = r['Property Class Name']
		if market != r['Geography Name']:
			market = r['Geography Name']
			print(f'\n {market} {class_name}')
		
		concept_name = r['Concept Name']
		# Used to calculate percentage of under construction sf
		if concept_name == 'Under Construction SF':
			construction_sf = '{0}'.format(r[cur_qtr_costar])
		# Used to calculate percentage of under construction sf
		if concept_name == 'Under Construction Units':
			construction_units = '{0}'.format(r[cur_qtr_costar])

		num_type = dConcept_name[concept_name]['num_type']
		mo_label = dConcept_name[concept_name]['mo_label']

		# Calculate percentage of under construction to existing sqft
		if concept_name == 'Inventory SF':
			inventroy_sf = '{0}'.format(r[cur_qtr_costar])
			construction_pct_of_inventory = float(int(construction_sf) / int(inventroy_sf))
			value = '{:.1%}'.format(construction_pct_of_inventory)
		elif concept_name == 'Inventory Units':
			inventroy_units = '{0}'.format(r[cur_qtr_costar])
			construction_pct_of_inventory = float(int(construction_units) / int(inventroy_units))
			value = '{:.1%}'.format(construction_pct_of_inventory)
		# Format percentage
		elif num_type == 'percentage':
			value = '{:.1%}'.format(r[cur_qtr_costar])
		# Format integer
		elif num_type == 'integer':
			# value = '{:,}'.format(r[cur_qtr_costar])
			value = td.format_number_to_k_m_b(r[cur_qtr_costar])
		
		print(f' {mo_label:25}: {value}')
	

lao.holdup()
