#Python3

# Archive Comps files from Reonomy and CoStar

import fun_text_date as td
import lao
import os
import shutil
from datetime import datetime, timedelta

# Source folder containing files to check
source_folder = "F:\\Research Department\\scripts\\Projects\\Research\\data\\CompsFiles"

# Destination folder to move old files
dest_folder = "F:\\Research Department\\scripts\\Projects\\Research\\data\\CompsFiles\\Archive"

# Get the current date and time
current_time = datetime.now()

td.banner('CompsFiles Folder Archive Old Files v01')

# Loop through each file in the directory
for filename in os.listdir(source_folder):
	file_path = os.path.join(source_folder, filename)

	# Ensure that it's actually a file and not a directory
	if os.path.isfile(file_path):
		
		# Get the last modified date
		file_stat = os.stat(file_path)
		modified_time = datetime.fromtimestamp(file_stat.st_mtime)

		# Calculate the age of the file
		file_age = current_time - modified_time

		# If the file is older than 60 days, move it
		if file_age > timedelta(days=45):
			print(f"Moving file {filename} to archive")
			shutil.move(file_path, os.path.join(dest_folder, filename))
		
	# ui = td.uInput('\n Continue... > ')
	# if ui == '00':
	# 	exit('\n Terminating program...')
