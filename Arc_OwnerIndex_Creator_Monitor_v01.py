# Monitor a folder for JSON files with 'm1_params_' in the filename.
# When found, print a message, wait 5 seconds, then delete the file.

import fun_text_date as td
import glob
import os
import time

def monitor_folder(folder_path):
	"""
		Args:
		folder_path (str): Path to the folder to monitor
	"""
	td.banner('Arc OwnerIndex Creator Monitor v01')

	print(f"Monitoring folder: {folder_path}")
	print("Press Ctrl+C to stop the script")
	
	try:
		while True:
			# Search for JSON files with 'm1_params_' in the name
			file_pattern = os.path.join(folder_path, "*m1_params_*.json")
			matching_files = glob.glob(file_pattern)
			
			for file_path in matching_files:
				file_name = os.path.basename(file_path)
				print(f"Found JSON file: {file_name}")
				
				# Pause for 5 seconds
				print(f"Waiting 5 seconds before deleting...")
				time.sleep(5)
				
				# Delete the file
				os.remove(file_path)
				print(f"Deleted file: {file_name}")
			
			# Check every second for new files
			time.sleep(5)
			
	except KeyboardInterrupt:
		print("\nScript stopped by user")

if __name__ == "__main__":
	# Folder path to monitor
	folder_to_monitor = r"F:\Research Department\Code\M1 Json Files"
	
	# Ensure the folder exists
	if not os.path.isdir(folder_to_monitor):
		print(f"Error: The folder '{folder_to_monitor}' does not exist.")
		exit(1)
	
	# Start monitoring
	monitor_folder(folder_to_monitor)