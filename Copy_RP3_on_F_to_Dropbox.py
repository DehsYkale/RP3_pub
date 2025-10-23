# Copies Python files in the RP3 folder from F: drive to C: drive for access by Kablewy

#!/usr/bin/env python3
"""
Copy RP3 Repository Script
Copies all files and folders from F:\\Research Department\\Code\\RP3 to C:\\Users\\blandis\\Dropbox\\Code\\RP3
"""

import os
import shutil
import sys
from pathlib import Path
import time
from datetime import datetime

def should_copy_file(source_file, dest_file):
	"""
	Determine if a file should be copied based on existence and modification time.
	Returns True if:
	- Destination file doesn't exist
	- Source file is newer than destination file
	"""
	if not dest_file.exists():
		return True, "NEW"
	
	try:
		source_mtime = source_file.stat().st_mtime
		dest_mtime = dest_file.stat().st_mtime
		
		if source_mtime > dest_mtime:
			return True, "UPDATED"
		else:
			return False, "SKIPPED"
	except Exception as e:
		# If we can't compare times, err on the side of caution and copy
		return True, f"ERROR_COMPARING: {e}"

def copy_rp3_repository():
	"""
Copy files and folders from F:\\Research Department\\Code\\RP3 to C:\\Users\\blandis\\Dropbox\\Code\\RP3
	Only copies files that don't exist in destination or are newer than existing files.
	"""
	# Define source and destination paths
	source_path = Path("F:\\Research Department\\Code\\RP3")
	destination_path = Path("C:\\Users\\blandis\\Dropbox\\Code\\RP3")

	# Check if source exists
	if not source_path.exists():
		print(f"ERROR: Source path does not exist: {source_path}")
		print("Please verify the path to your RP3 repository.")
		return False
	
	# Create destination directory if it doesn't exist
	try:
		destination_path.mkdir(parents=True, exist_ok=True)
		if not destination_path.exists():
			print(f"Created destination directory: {destination_path}")
		else:
			print(f"Using existing destination directory: {destination_path}")
	except Exception as e:
		print(f"ERROR: Could not create destination directory: {e}")
		return False
	
	# Copy files and track progress
	copied_files = 0
	updated_files = 0
	skipped_files = 0
	copied_dirs = 0
	errors = []
	
	print(f"\nStarting incremental copy from:")
	print(f"  Source: {source_path}")
	print(f"  Destination: {destination_path}")
	print("  Mode: Copy only new/updated files")
	print("-" * 50)
	
	try:
		# Walk through all files and directories in source
		for root, dirs, files in os.walk(source_path):
			# Calculate relative path from source
			rel_path = os.path.relpath(root, source_path)
			
			# Create corresponding directory structure in destination
			if rel_path != '.':
				dest_dir = destination_path / rel_path
			else:
				dest_dir = destination_path
			
			# Create directory if it doesn't exist
			try:
				if not dest_dir.exists():
					dest_dir.mkdir(parents=True, exist_ok=True)
					if rel_path != '.':
						copied_dirs += 1
						print(f"Created directory: {rel_path}")
			except Exception as e:
				error_msg = f"Failed to create directory {rel_path}: {e}"
				errors.append(error_msg)
				print(f"ERROR: {error_msg}")
				continue
			
			# Copy files that are new or updated
			for file in files:
				source_file = Path(root) / file
				dest_file = dest_dir / file
				
				# Check if file should be copied
				should_copy, reason = should_copy_file(source_file, dest_file)
				
				if should_copy:
					try:
						shutil.copy2(source_file, dest_file)
						
						if reason == "NEW":
							copied_files += 1
						elif reason == "UPDATED":
							updated_files += 1
						else:
							copied_files += 1  # For error cases
						
						# Show progress for every 10 operations
						total_operations = copied_files + updated_files
						if total_operations % 10 == 0 and total_operations > 0:
							print(f"Processed {total_operations} files ({copied_files} new, {updated_files} updated)...")
						
						# Show individual file progress for Python files
						if file.endswith('.py'):
							rel_file_path = os.path.relpath(source_file, source_path)
							source_time = datetime.fromtimestamp(source_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
							print(f"  {reason}: {rel_file_path} (modified: {source_time})")
							
					except Exception as e:
						error_msg = f"Failed to copy {source_file}: {e}"
						errors.append(error_msg)
						print(f"ERROR: {error_msg}")
				else:
					# File was skipped
					skipped_files += 1
					if file.endswith('.py') and skipped_files % 20 == 0:
						print(f"  Skipped {skipped_files} unchanged files...")
	
	except Exception as e:
		print(f"CRITICAL ERROR during copy operation: {e}")
		return False
	
	# Summary report
	print("\n" + "=" * 60)
	print("INCREMENTAL COPY OPERATION COMPLETE")
	print("=" * 60)
	print(f"New files copied: {copied_files}")
	print(f"Updated files copied: {updated_files}")
	print(f"Files skipped (unchanged): {skipped_files}")
	print(f"Directories created: {copied_dirs}")
	print(f"Total files processed: {copied_files + updated_files + skipped_files}")
	print(f"Errors encountered: {len(errors)}")
	
	if errors:
		print("\nERRORS:")
		for error in errors:
			print(f"  - {error}")
	
	# Show efficiency summary
	total_files = copied_files + updated_files + skipped_files
	if total_files > 0:
		efficiency = (skipped_files / total_files) * 100
		print(f"\nEfficiency: {efficiency:.1f}% of files were already up to date")
	
	# Verify some key files were copied
	print("\nVerifying key files...")
	key_files_to_check = [
		"lao.py",
		"fun_login.py", 
		"mc.py",
		"requirements.txt",
		"README.md"
	]
	
	for key_file in key_files_to_check:
		key_file_path = destination_path / key_file
		if key_file_path.exists():
			print(f"  ✓ Found: {key_file}")
		else:
			print(f"  - Missing: {key_file}")
	
	# Show directory structure summary
	print(f"\nDestination directory: {destination_path}")
	print(f"Total size: {get_directory_size(destination_path):.2f} MB")
	
	return len(errors) == 0

def get_directory_size(path):
	"""Calculate total size of directory in MB"""
	total_size = 0
	try:
		for dirpath, dirnames, filenames in os.walk(path):
			for filename in filenames:
				filepath = os.path.join(dirpath, filename)
				try:
					total_size += os.path.getsize(filepath)
				except (OSError, FileNotFoundError):
					pass
	except Exception:
		pass
	return total_size / (1024 * 1024)  # Convert bytes to MB

def main():
	"""Main function"""
	print("RP3 Repository Incremental Copy Script")
	print("=" * 40)
	
	# Show what the script will do
	print("\nThis script will:")
	print("• Copy NEW files from F:\\Research Department\\Code\\RP3 to C:\\RP3_on_C")
	print("• Update files that are NEWER in the source than destination")
	print("• Skip files that are already up-to-date in the destination")
	print("• Preserve file timestamps and permissions")
	
	# Confirm operation
	response = input("\nContinue with incremental copy? (y/N): ")
	if response.lower() not in ['y', 'yes']:
		print("Operation cancelled.")
		return
	
	# Record start time
	start_time = time.time()
	
	# Perform copy operation
	success = copy_rp3_repository()
	
	# Calculate elapsed time
	elapsed_time = time.time() - start_time
	
	print(f"\nOperation completed in {elapsed_time:.2f} seconds")
	
	if success:
		print("✓ Incremental copy operation completed successfully!")
		if copied_files + updated_files > 0:
			print(f"✓ {copied_files + updated_files} files were copied/updated")
		if skipped_files > 0:
			print(f"• {skipped_files} files were already up to date")
		print("\nNext steps:")
		print("1. Your updated files are now available at C:\\RP3_on_C")
		print("2. You can now give Claude access to analyze your latest code")
		print("3. Run this script regularly to keep your local copy synchronized")
	else:
		print("⚠ Copy operation completed with errors. Check the error messages above.")
	
	input("\nPress Enter to exit...")

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n\nOperation cancelled by user.")
	except Exception as e:
		print(f"\nUnexpected error: {e}")
		input("Press Enter to exit...")