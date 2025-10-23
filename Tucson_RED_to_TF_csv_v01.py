# Format Tucson RED News spreadsheet to for TF AWS CSV Entry

import bb
import csv
import dicts
import fun_text_date as td
import lao
import os
from pprint import pprint
from datetime import datetime

td.banner('Tucson RED News to TF CSV v01')
inPath = 'F:/Research Department/scripts/Projects/Research/data/CompsFiles/'
inFile = lao.guiFileOpen(path=inPath, titlestring='Tucson RED News CSV File', extension=[('RED News files', '*Tucson* *TUC*.csv'), ('csv files', '.csv'), ('txt files', '.txt'), ('Excel files', '.xlsx'), ('all files', '.*')])
outFile = inFile.replace('.csv', '')
outFile = '{0}_FORMATTED.csv'.format(outFile)
dComps = lao.spreadsheetToDict(inFile)

with open(outFile, 'w', newline='') as f:
	fout = csv.writer(f)
	fout.writerow(dicts.get_tf_csv_header())
	for row in dComps:
		# VARIABLES ################################################################
		r= dComps[row]
		lRow = []
		# date = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(r['Sale Date']) - 2)
		# date = date.strftime("%m/%d/%Y")
		# exit()
		lRow.append(r['Seller Entity'])  # Seller Entity
		lRow.append(r['Seller Person'])  # Seller Person
		lRow.append(r['Seller Street'])  # Seller Street
		lRow.append(r['Seller City'])  # Seller City
		lRow.append(r['Seller State'])  # Seller State
		lRow.append(r['Seller Zip'])  # Seller Zip
		lRow.append('None')  # Seller Country
		lRow.append(r['Seller Phone'])  # Seller Phone
		lRow.append('None')  # Seller Email
		lRow.append(r['Buyer Entity'])  # Buyer Entity
		lRow.append(r['Buyer Person'])  # Buyer Person
		lRow.append(r['Buyer Street'])  # Buyer Street
		lRow.append(r['Buyer City'])  # Buyer City
		lRow.append(r['Buyer State'])  # Buyer State
		lRow.append(r['Buyer Zip'])  # Buyer Zip
		lRow.append('None')  # Buyer Country
		lRow.append(r['Buyer Phone'])  # Buyer Phone
		lRow.append('None')  # Buyer Email
		lRow.append(r['Acres'])  # Acres__c
		lRow.append('None')  # Buyer_Acting_As__c
		lRow.append(r['City'])  # City__c
		lRow.append('None')  # Classification__c
		lRow.append('USA')  # Country__c
		lRow.append('Pima')  # County
		lRow.append(r['Type'])  # Description__c
		lRow.append('None')  # General_Plan__c
		lRow.append('None')  # Keyword_Group__c
		lRow.append(r['Latitude'])  # Latitude__c
		lRow.append(r['Lead Parcel'])  # Lead_Parcel__c
		lRow.append('None')  # Legal_Description__c
		lRow.append('None')  # Location__c
		lRow.append(r['Longitude'])  # Longitude__c
		lRow.append('None')  # Lot_Description__c
		lRow.append('None')  # Lot_Type__c
		lRow.append(r['Lots'])  # Lots__c
		lRow.append('Tucson')  # Market__c
		lRow.append('None')  # Deal Name
		lRow.append(r['Parcels'])  # Parcels__c
		lRow.append(r['Rec Doc'])  # Record_Instrument_Number__c
		lRow.append(r['Sale Date']) # Sale Date
		lRow.append(r['Sale Price'])  # Sale_Price__c
		lRow.append('RED News')  # Source__c
		lRow.append(r['Source ID'])  # Source_ID__c
		lRow.append('Arizona')  # State__c
		lRow.append(r['Subdivision'])  # Subdivision__c
		lRow.append('None')  # Submarket__c
		lRow.append('None')  # Zipcode__c
		lRow.append('None')  # Zoning__c
		lRow.append('None')  # List_Date__c
		lRow.append('None')  # List_Price__c
		lRow.append('None')  # List Entity
		lRow.append('None')  # List Agent
		lRow.append('None')  # List Agent Phone
		lRow.append('None')  # List Agent Email
		lRow.append('None')  # Alt APN A
		lRow.append('None')  # Alt APN B
		lRow.append('None')  # PID__c
		lRow.append('None')  # Residence Y-N
		lRow.append('None')  # Terms__c
		lRow.append('None')  # Recorded_Doc_URL__c
		lRow.append('None')  # Notes
		lRow.append('None')  # Lender
		lRow.append('None')  # Loan_Amount__c
		lRow.append('None')  # Loan_Date__c
		lRow.append('None')  # Buyer Agent Entity
		lRow.append('None')  # Buyer Agent
		lRow.append('None')  # Buyer Agent Phone
		lRow.append('None')  # Buyer Agent Email
		lRow.append('Sold')  # MSL Status

		fout.writerow(lRow)
lao.openFile(outFile)
exit()



## MAKE LOT SALES BY QUATER DATA FOR CHART
def getOpportunityFields():
	fields = \
		"Id,  " \
		"Name,  " \
		"Acres__c,  " \
		"Buyer_Acting_As__c,  " \
		"City__c,  " \
		"Classification__c,  " \
		"Country__c,  " \
		"County__c,  " \
		"Description__c,  " \
		"General_Plan__c,  " \
		"Latitude__c,  " \
		"Lead_Parcel__c,  " \
		"Legal_Description__c,  " \
		"Location__c,  " \
		"Longitude__c,  " \
		"Lot_Description__c,  " \
		"Lot_Type__c,  " \
		"Lots__c,  " \
		"Market__c,  " \
		"Parcels__c,  " \
		"PID__c,  " \
		"Recorded_Instrument_Number__c,  " \
		"Sale_Date__c,  " \
		"Sale_Price__c,  " \
		"Source__c,  " \
		"Source_ID__c,  " \
		"StageName__c,  " \
		"State__c,  " \
		"Subdivision__c,  " \
		"Submarket__c,  " \
		"Type__c,  " \
		"Zipcode__c,  " \
		"Zoning__c,  " \
		"Owner_Entity__c,  " \
		"Owner_Entity__r.Id,  " \
		"Owner_Entity__r.Name,  " \
		"Owner_Entity__r.BillingStreet,  " \
		"Owner_Entity__r.BillingCity,  " \
		"Owner_Entity__r.BillingState, " \
		"Owner_Entity__r.BillingPostalCode, " \
		"Owner_Entity__r.BillingCountry, " \
		"Owner_Entity__r.Phone,  " \
		"AccountId__c,  " \
		"AccountId__r.Id,  " \
		"AccountId__r.Name,  " \
		"AccountId__r.FirstName,  " \
		"AccountId__r.MiddleName__c,  " \
		"AccountId__r.LastName,  " \
		"AccountId__r.BillingStreet,  " \
		"AccountId__r.BillingCity,  " \
		"AccountId__r.BillingState,  " \
		"AccountId__r.BillingPostalCode,  " \
		"AccountId__r.BillingCountry,  " \
		"AccountId__r.Phone,  " \
		"AccountId__r.PersonEmail, " \
		"(Select  " \
		"Id,  " \
		"Name,  " \
		"Buyer_Entity__c,  " \
		"Buyer_Entity__r.Id, " \
		"Buyer_Entity__r.Name, " \
		"Buyer_Entity__r.BillingStreet,  " \
		"Buyer_Entity__r.BillingCity,  " \
		"Buyer_Entity__r.BillingState,  " \
		"Buyer_Entity__r.BillingPostalCode,  " \
		"Buyer_Entity__r.BillingCountry,  " \
		"Buyer_Entity__r.Phone,   " \
		"Buyer__c,  " \
		"Buyer__r.Id,  " \
		"Buyer__r.Name,  " \
		"Buyer__r.FirstName,  " \
		"Buyer__r.MiddleName__c,  " \
		"Buyer__r.LastName,  " \
		"Buyer__r.BillingStreet,  " \
		"Buyer__r.BillingCity,  " \
		"Buyer__r.BillingState,  " \
		"Buyer__r.BillingPostalCode,  " \
		"Buyer__r.BillingCountry,  " \
		"Buyer__r.Phone,  " \
		"Buyer__r.PersonEmail,  " \
		"Offer_Date__c,  " \
		"Offer_Price__c,  " \
		"Offer_Status__c  " \
		"From Offers__r WHERE Offer_Status__c = 'Accepted')," \
		"(Select " \
		"Name, " \
		"Lot_Count__c, " \
		"Lot_Width__c, " \
		"Lot_Depth__c, " \
		"Price_per_parcel__c, " \
		"Price_per_Front_Foot__c, " \
		"Price_per_Lot__c " \
		"From Lot_Details__r WHERE RecordTypeID != '012a0000001ZSieAAG')"

	return fields

service = bb.sfLogin()

fields = getOpportunityFields()
wc = \
	"StageName__c LIKE 'Closed%' AND " \
	"(Lot_Type__c = 'Finished Lots' OR Lot_Type__c = 'Initial Lot Option' OR Lot_Type__c = 'Lot Option Built Out') AND " \
	"Lots__c > 0 AND " \
	"Sale_Date__c >= 2017-01-01 AND Sale_Price__c >= 10001 AND " \
	"(County__c LIKE '%Maricopa%' OR County__c LIKE '%Pinal%') AND " \
	"(RecordTypeId = '012a0000001ZSS5AAO' or RecordTypeId = '012a0000001ZSS8AAO') LIMIT 5"
qs = "SELECT {0} FROM lda_Opportunity__c WHERE {1}".format(fields, wc)
results = bb.sfquery(service, qs)

with open('C:/TEMP/Fin Lots.csv', 'wb') as f:
	fout = csv.writer(f)
	fout.writerow(['PID', 'Classification', 'Sale Date', 'Sale Price', 'Lot Details Name', 'Lots', 'Width', 'Depth', 'Price per Lot', 'Price per Parcel'])
	for row in results:
		Lot_Details_Name, Lot_Width, Lot_Depth, Lot_Count, Price_per_Parcel, Price_per_Lot = 'None', 0, 0, 0, 0, 0
		# pprint(row)
		PID = row['PID__c']
		Classification = row['Classification__c']
		Sale_Date = row['Sale_Date__c']
		Sale_Price = row['Sale_Price__c']
		for rowLots in row['Lot_Details__r']:
			Lot_Details_Name = rowLots['Name']
			Lots = rowLots['Lot_Count__c']
			Lot_Width = rowLots['Lot_Width__c']
			Lot_Depth = rowLots['Lot_Depth__c']
			Lot_Count = rowLots['Lot_Count__c']
			Price_per_Parcel = rowLots['Price_per_parcel__c']
			Price_per_Lot = rowLots['Price_per_Lot__c']
			# pprint(rowLots)
			fout.writerow([PID, Classification, Sale_Date, Sale_Price, Lot_Details_Name, Lot_Count, Lot_Width, Lot_Depth, Price_per_Lot, Price_per_Parcel])

lao.openFile('C:/TEMP/Fin Lots.csv')

exit()


