
import aws
import fun_text_date as td
import lao
import os
from pprint import pprint
import shutil

lao.banner('Upload Maps Listings Packages to AWS v01')

fup = lao.guiFileOpen(path='C:/TEMP', titlestring='Select File to Upload', extension=[('jpg files', '.jpg'), ('pdf files', '.pdf'),  ('png files', '.png'), ('all files', '.*')])

filename = os.path.basename(fup)

lMap_file_types = ['.jpg', '.png', '.jpeg']

for file_type in lMap_file_types:
	if file_type in filename.lower():
		file_path = f'C:/Users/Public/Public Mapfiles/awsUpload/Maps/{filename}'
if '.pdf' in filename.lower():
	file_path = f'C:/Users/Public/Public Mapfiles/awsUpload/Listing/{filename}'

shutil.copyfile(fup, file_path)

lao.sleep(2)

ui = td.uInput('\n Delete local files after upload? [0/1/00] > ')
if ui == '00':
	exit('\n Terminating program...')
elif ui == '1':
	delete_files = True
else:
	delete_files = False

aws.sync_opr_maps_comp_listings_folders_to_s3(delete_files=delete_files)

