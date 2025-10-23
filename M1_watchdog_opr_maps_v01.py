# Monitors 

import fun_text_date as td
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

def upload_map(filename):
	"""
	Placeholder function to simulate uploading a map.
	Actual implementation will depend on the details of the upload process.
	"""
	print(f"Uploading {filename}")

class MapFileHandler(FileSystemEventHandler):
	def on_created(self, event):
		# Checking if the created file is a JSON file
		if event.is_directory:
			return
		if event.src_path.endswith('.json'):
			upload_map(event.src_path)

def monitor_folder(path):
	"""
	Monitor the specified folder for new JSON files and upload them.
	"""
	event_handler = MapFileHandler()
	observer = Observer()
	observer.schedule(event_handler, path, recursive=False)
	observer.start()
	try:
		while True:
			# Run indefinitely
			pass
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

td.banner('M1 Watchdog OPR Maps v01')
monitor_folder(r"F:\Research Department\Code\AWS_Upload\Maps")

