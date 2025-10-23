# Copies Loan data on Sale Deals to Leads

import lao
import bb
import dicts
import fun_login
from pprint import pprint

lao.banner('TF Debt on Sales to Leads v01')

service = fun_login.TerraForce()

# TerraForce Query
fields = 'default'
wc = "StageName__c = 'Lead' AND Loan_Amount__c = null AND Parent_Opportunity__c != null AND Parent_Opportunity__r.Loan_Amount__c != null"
results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)

for row in results:
	dup = dicts.get_blank_deal_update_dict(row['Id'])
	dup['Beneficiary__c'] = row['Parent_Opportunity__r']['Beneficiary__c']
	dup['Beneficiary_Contact__c'] = row['Parent_Opportunity__r']['Beneficiary_Contact__c']
	dup['Encumbrance_Rating__c'] = row['Parent_Opportunity__r']['Encumbrance_Rating__c']
	dup['Credit_Bid_Amount__c'] = row['Parent_Opportunity__r']['Credit_Bid_Amount__c']
	dup['Loan_Amount__c'] = row['Parent_Opportunity__r']['Loan_Amount__c']
	del dup['OwnerId']

	print(bb.getPIDfromDID(service, row['Id']))
	# pprint(dup)

	bb.tf_update_3(service, dup)

