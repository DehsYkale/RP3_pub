#!/usr/bin/env python3
"""
AWS File Delete CLI v01
Script to delete files from LAO AWS S3 buckets using AWS CLI commands
Based on file extension routing similar to existing LAO AWS functions
- JPG/PNG files are deleted from the maps bucket  
- PDF files are deleted from the listing bucket

Author: Research Department - Land Advisors Organization
"""

import fun_text_date as td
import subprocess
import os
from pathlib import Path

def check_aws_cli():
	"""Check if AWS CLI is available"""
	try:
		subprocess.run(['aws', '--version'], 
					   capture_output=True, 
					   check=True)
		return True
	except (subprocess.CalledProcessError, FileNotFoundError):
		return False

def file_exists_on_s3(bucket, key):
	"""
	Check if file exists on S3 using AWS CLI
	
	Args:
		bucket (str): S3 bucket name
		key (str): S3 object key (path)
	
	Returns:
		bool: True if file exists, False otherwise
	"""
	try:
		result = subprocess.run(
			['aws', 's3', 'ls', f's3://{bucket}/{key}'],
			capture_output=True,
			text=True,
			check=True
		)
		return len(result.stdout.strip()) > 0
	except subprocess.CalledProcessError:
		return False

def delete_file_from_s3_cli(filename):
	"""
	Delete file from appropriate S3 bucket using AWS CLI
	
	Args:
		filename (str): Name of file to delete
	"""
	# Extract file extension
	file_extension = Path(filename).suffix.lower()
	
	# Determine bucket and folder based on file extension
	if file_extension in ['.jpg', '.jpeg', '.png']:
		bucket_name = 'request-server'
		folder_path = 'maps/'
		file_type = 'map image'
	elif file_extension == '.pdf':
		bucket_name = 'request-server'
		folder_path = 'listings/'
		file_type = 'listing brochure'
	else:
		td.warningMsg(f"\n Unsupported file extension: {file_extension}")
		print(" Supported extensions: .jpg, .jpeg, .png, .pdf")
		return False
	
	# Construct full S3 path
	s3_path = f"s3://{bucket_name}/{folder_path}{filename}"
	
	# Check if file exists
	print(f" Checking if file exists: {filename}")
	if not file_exists_on_s3(bucket_name, f"{folder_path}{filename}"):
		td.warningMsg(f"\n File not found: {filename}")
		print(f"   Bucket: {bucket_name}")
		print(f"   Path: {folder_path}{filename}")
		return False
	
	# File exists, proceed with deletion
	print(f"\n 📁 Found {file_type}: {filename}")
	print(f"   Bucket: {bucket_name}")
	print(f"   Path: {folder_path}{filename}")
	
	# Confirm deletion
	confirm = td.uInput(f"\n  Confirm deletion of {filename}? (0/1/00): ").strip().lower()
	if confirm == '00':
		exit('\n 👋 Terminating program...')
	elif confirm == '0':
		print("❌ Deletion cancelled")
		return False
	
	try:
		# Delete the file using AWS CLI
		print(f"\n🗑️  Deleting {filename}...")
		result = subprocess.run(
			['aws', 's3', 'rm', s3_path],
			capture_output=True,
			text=True,
			check=True
		)
		
		print(f"✅ Successfully deleted: {filename}")
		if result.stdout:
			print(f"   AWS Response: {result.stdout.strip()}")
		return True
		
	except subprocess.CalledProcessError as e:
		print(f"❌ Error deleting file: {e}")
		if e.stderr:
			print(f"   Error details: {e.stderr}")
		return False

def list_files_in_bucket(bucket, prefix, limit=10):
	"""
	List recent files in bucket for reference
	
	Args:
		bucket (str): S3 bucket name
		prefix (str): Folder prefix
		limit (int): Maximum number of files to show
	"""
	try:
		result = subprocess.run(
			['aws', 's3', 'ls', f's3://{bucket}/{prefix}', '--human-readable'],
			capture_output=True,
			text=True,
			check=True
		)
		
		if result.stdout:
			files = result.stdout.strip().split('\n')[:limit]
			print(f"\nRecent files in {bucket}/{prefix}:")
			for file in files:
				if file:
					parts = file.split()
					if len(parts) >= 4:
						filename = parts[-1]
						size = parts[2]
						print(f"  • {filename} ({size})")
		else:
			print(f"\nNo files found in {bucket}/{prefix}")
			
	except subprocess.CalledProcessError:
		print(f"\nCould not list files in {bucket}/{prefix}")

def show_help():
	"""Display help information"""

	print("\n💡 Commands:")
	print("  • Enter just the filename (e.g., 'CA001234.jpg')")
	print("      • File extension determines which bucket to check")
	print("  • Type 'list maps' or 'list pdfs' to see recent files")
	print("  • Type 'help' to see this message")
	print("  • Type 00 to exit")

def main():
	"""Main function to handle user interface"""
	
	
	# Check AWS CLI availability
	if not check_aws_cli():
		td.warningMsg("\n AWS CLI not found or not configured")
		print(" Please install AWS CLI and configure credentials")
		return
	
	print("✅ AWS CLI detected and ready")
	show_help()
	
	while True:
		try:
			td.banner("AWS Delete File from Bucket v01")
			print("=" * 60)
			print("🗂️  AWS File Delete Tool - Land Advisors Organization")
			print("=" * 60)
			show_help()
			print("\n" + "─" * 50)
			ui = td.uInput(" Enter filename (or command) [00]: ").strip()
			
			
			# Handle empty input
			if not ui:
				print("Please enter a filename or command")
				continue
			
			if ui == '00':
				exit('\n 👋 Terminating program...')

			# Handle special commands
			if ui.lower() in ['help', 'h', '?']:
				show_help()
				continue
			elif ui.lower() in ['list maps', 'maps']:
				list_files_in_bucket('request-server', 'maps/')
				continue
			elif ui.lower() in ['list pdfs', 'pdfs', 'listings']:
				list_files_in_bucket('request-server', 'listings/')
				continue
			elif ui.lower() in ['exit', 'quit', 'q']:
				break
			
			# Treat as filename to delete
			success = delete_file_from_s3_cli(ui)
			
			if success:
				print(f" ✅ Operation completed successfully")
			else:
				print(f" ❌ Operation failed or was cancelled")
				
		except KeyboardInterrupt:
			print("\n\n 👋 Exiting...")
			break
		except Exception as e:
			print(f"\n ❌ Unexpected error: {e}")
			continue
	
	print("Goodbye! 👋")

if __name__ == "__main__":
	main()