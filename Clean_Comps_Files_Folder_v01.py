import fun_text_date as td
import os
import shutil
import time

td.banner('Clean Comps & Listins Files Folders v01')


# Define the age threshold in seconds (5 weeks)
five_weeks_in_seconds = 5 * 7 * 24 * 60 * 60  # 5 weeks

# Get the current time
current_time = time.time()

# Iterate through the Comps files in the source directory
print('\n Archiving Comps Files...')
# Define source and destination directories
source_dir = r"F:\Research Department\scripts\Projects\Research\data\CompsFiles"
archive_dir = r"F:\Research Department\scripts\Projects\Research\data\CompsFiles\Archive"
for filename in os.listdir(source_dir):
	file_path = os.path.join(source_dir, filename)

	# Check if it's a file and has the correct extension
	if os.path.isfile(file_path) and (filename.endswith('.zip') or filename.endswith('.csv')):
		# Get the file's last modification time
		file_age = current_time - os.path.getmtime(file_path)

		# Check if the file is older than 5 weeks
		if file_age > five_weeks_in_seconds:
			# Move the file to the archive directory
			shutil.move(file_path, os.path.join(archive_dir, filename))
			print(f"Moved: {filename} to {archive_dir}")
		else:
			print(f"File {filename} is not older than 5 weeks.")

print('\n Archiving Comps Files...')
# Define source and destination directories
source_dir = r"F:\Research Department\Listings"
archive_dir = r"F:\Research Department\Listings\Archive"

# Iterate through the Listings files in the source directory
for filename in os.listdir(source_dir):
	file_path = os.path.join(source_dir, filename)

	# Check if it's a file and has the correct extension
	if os.path.isfile(file_path) and (filename.endswith('.xls') or (filename.endswith('.xlsx'))):
		# Get the file's last modification time
		file_age = current_time - os.path.getmtime(file_path)

		# Check if the file is older than 5 weeks
		if file_age > five_weeks_in_seconds:
			# Move the file to the archive directory
			shutil.move(file_path, os.path.join(archive_dir, filename))
			print(f"Moved: {filename} to {archive_dir}")
		else:
			print(f"File {filename} is not older than 5 weeks.")

exit('\n Fin...')

