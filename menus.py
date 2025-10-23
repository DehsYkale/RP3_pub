# Univeral menus

import fun_text_date as td
import lao
import pandas as pd
from pprint import pprint

def lao_markets(mkt_format='AIRPORTCODE'):
	lao.print_function_name('def menus lao_markets')

	county_file = 'F:/Research Department/Code/Databases/LAO_Counties.xlsx'

	# Read the Excel file
	df = pd.read_excel(county_file, sheet_name='LAO_Counties')

	# Get unique market combinations and sort by Market name
	unique_markets = df[['Market', 'MarketAbb']].drop_duplicates().sort_values('Market')
	
	# Convert to list of tuples
	market_list = [(row['Market'], row['MarketAbb']) for _, row in unique_markets.iterrows()]

	while 1:
		print("Select a market:\n")
		for i, (market_abb, market_name) in enumerate(market_list, 1):
			print(f"{i:2d}) {market_name} - {market_abb}")
		print('00) Quit')
	

		ui = td.uInput('\n Select Market > ')
		if ui == '00':
			exit('\n Terminating program...')
		else:
			ui = int(ui)
		
		if ui < 1 or ui > len(market_list):
			td.warningMsg('\n Invalid selection, try again...\n')
			lao.sleep(2)
		selected_market = market_list[ui - 1]
		if mkt_format == 'AIRPORTCODE':
			return selected_market[1]
		elif mkt_format == 'MARKETNAME':
			return selected_market[0]
		# Return both market name [0] and airport code [1]
		elif mkt_format == 'BOTH':
			return selected_market[0], selected_market[1]
