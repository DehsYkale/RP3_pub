


from pprint import pprint
import lao
import bb
import fun_login
import fun_text_date as td

import webs
from glob import glob
import subprocess
import os
import shutil

# Get list of brochures on aws
# cp stands for CompleteProcess
cpBrochures = subprocess.run('aws s3 ls s3://request-server/listings/ --output text', stdout = subprocess.PIPE, text=True)
# Convert CompletedProcess to text string
lBrochures = cpBrochures.stdout

lPackages = glob('F:/Research Department/scripts/awsUpload/Listings Archive/*.pdf')
for pkg in lPackages:
	filename = os.path.basename(pkg)
	# print(filename)
	# print(pkg)
	# print(webs.awsFileExists(filename))
	if filename in lBrochures:
		continue
	else:
		print(f' Missing: {filename}')
		destination_file = f'C:/Users/Public/Public Mapfiles/awsUpload/Listings/{filename}'
		print(pkg)
		print(destination_file)
		shutil.copy(pkg, destination_file)
		webs.awsUpload()
		os.remove(destination_file)
		lao.sleep(1)
		# ui = td.uInput('\n Continue... > ')
		# if ui == '00':
		# 	exit('\n Terminating program...')
# webs.awsUpload()


exit()
