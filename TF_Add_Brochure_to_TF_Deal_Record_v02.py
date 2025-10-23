# Add competitor listing brochure to a TF Deal record based on the PID

import aws
import lao
import bb
import fun_login
import fun_text_date as td
from pprint import pprint
from os import rename, remove
import shutil
import webs

def get_llr_dict():
	llr_path = 'F:/Research Department/Lot Comps Components/'
	llr_filename = lao.guiFileOpen(path=llr_path, titlestring='Select LLR File', extension=[('Excel files', '.xlsx'), ('all files', '.*')])
	dLLR = lao.spreadsheetToDict(llr_filename, sheetname='Competitor Listings')
	return dLLR



lao.banner("Add Brochure to TF Deal Recored v02")
service = fun_login.TerraForce()
brochure_path = 'F:/Research Department/CompListingBrochures/'


# ADD PACKAGE  *****************************************************************
# Add Competitors Package
while 1:
	
	# Cycle through records

	lao.banner("Add Brochure to TF Deal Recored v02")

	PID = td.uInput('\n Enter PID [00] > ')
	if PID == '00':
		exit('\n Terminating program...')

	PID = PID.strip()
	DID = bb.getDIDfromPID(service, PID)


	# Open Crexi listing page
	# TerraForce Query
	fields = 'default'
	wc = f"Id = '{DID}'"
	results = bb.tf_query_3(service, rec_type='Deal', where_clause=wc, limit=None, fields=fields)
	# TerraForce Query
	fields = 'default'
	wc = f"DealID__c = '{DID}'"
	package_results = bb.tf_query_3(service, rec_type='Package', where_clause=wc, limit=None, fields=fields)
	# pprint(package_results)
	if package_results != []:

		print('\n No Package found for PID {0}...'.format(PID))
		pprint(package_results)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
		continue
		
	# User to select Brochure
	brochure_filename = lao.guiFileOpen(brochure_path, 'Select Brochure PDF', [('PDF', '.pdf'), ('all files', '.*')])
	brochure_new_fileName = '{0}_competitors_package.pdf'.format(PID)
	brochure_file_renamed = '{0}{1}'.format(brochure_path, brochure_new_fileName)
	# td.uInput('\n File renamed Continue... > ')
	while 1:
		try:
			rename(brochure_filename, brochure_file_renamed)
			brochure_file_move_to = 'C:/Users/Public/Public Mapfiles/awsUpload/Listing/{0}'.format(brochure_new_fileName)
			shutil.move(brochure_file_renamed, brochure_file_move_to)
			break
		except:
			td.warningMsg('\n PDF is open in a viewer application like FoxIt Reader.\n\n Close the PDF viewer and try again.')
			ui = td.uInput('\n Continue [00]...')
			if ui == '00':
				exit('\n Terminating program...')

	# td.uInput('\n file moved to awsUpload\Listings Continue... > ')
	print('\n Uploading {0}'.format(brochure_new_fileName))
	# webs.awsUpload(delete_files=True)
	aws.sync_opr_maps_comp_listings_folders_to_s3(delete_files=False)
	print(' File uploaded...')
	# td.uInput('\n did file upload Continue... > ')
	dpackage = {}
	dpackage['type'] = 'lda_Package_Information__c'
	dpackage['DealID__c'] = DID
	dpackage['Field_Content__c'] = 'https://request-server.s3.amazonaws.com/listings/{0}'.format(brochure_new_fileName)
	dpackage['Field_Name__c'] = 'Competitor Package'
	dpackage['Field_Type__c'] = 'URL'
	print('\n Adding package info...')
	bb.tf_create_3(service, dpackage)
	# Add competitor package link to TF Deal record
	dup = {
		'type': 'lda_Opportunity__c',
		'Id': DID,
		'Package__c': dpackage['Field_Content__c']
			}
	bb.tf_update_3(service, dup)
	print('Package info added...')
	lao.openURL('https://request-server.s3.amazonaws.com/listings/{0}'.format(brochure_new_fileName))
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')

# ******************************************************************************
