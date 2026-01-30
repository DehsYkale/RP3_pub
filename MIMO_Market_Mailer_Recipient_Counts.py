
import fun_text_date as td
import bb
import dicts

td.banner('MIMO Market Mailer Recipient Counts')

lMarkets = dicts.get_lao_markets_list(abbreviation=False)
for market in lMarkets:
	print(f"Processing market: {market}")
	# where_clause = f"Market_Mailer_Market__c = '{market}'"
	# count = bb.tf_count_3(fun_login.TerraForce(), 'Person', where_clause)
	# print(f"{market}: {count} recipients")