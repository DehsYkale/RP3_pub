import boto3
import csv
from datetime import datetime
import fun_text_date as td
import os
from pprint import pprint

def list_aws_buckets_to_csv():
	"""
	Lists files in LAO AWS S3 buckets (request-server/maps and request-server/listings)
	and saves the listings to CSV files in C:\\TEMP
	"""
	try:
		# Initialize S3 client
		s3_client = boto3.client('s3')
		
		# Ensure C:\TEMP directory exists
		temp_dir = 'C:\\TEMP'
		if not os.path.exists(temp_dir):
			os.makedirs(temp_dir)
		
		# Define bucket and prefixes
		bucket_name = 'request-server'
		ui = td.uInput('\n Create Map CSV, Listings CSV or Both [1/2/3/00] > ')
		if ui == '00':
			exit('\n Terminating program...')
		elif ui == '1':
			prefixes = {
				'maps': 'maps/'
			}
		elif ui == '2':
			prefixes = {
				'listings': 'listings/'
			}
		elif ui == '3':
			prefixes = {
				'maps': 'maps/',
				'listings': 'listings/'
			}

		timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		
		for folder_type, prefix in prefixes.items():
			print(f'\nListing files in {bucket_name}/{prefix}...')
			
			# List objects with pagination
			paginator = s3_client.get_paginator('list_objects_v2')
			page_iterator = paginator.paginate(
				Bucket=bucket_name,
				Prefix=prefix
			)
			
			files_data = []
			file_count = 0
			
			for page in page_iterator:
				if 'Contents' in page:
					for obj in page['Contents']:
						# Skip the folder itself
						if obj['Key'] != prefix:
							file_info = {
								'Filename': os.path.basename(obj['Key']),
								'Full_Path': obj['Key'],
								'Size_Bytes': obj['Size'],
								'Size_MB': round(obj['Size'] / 1024 / 1024, 2),
								'Last_Modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
								'ETag': obj['ETag'].strip('"'),
								'Storage_Class': obj.get('StorageClass', 'STANDARD')
							}
							files_data.append(file_info)
							file_count += 1
			
			# Save to CSV
			csv_filename = f'{temp_dir}\\aws_{folder_type}_listing_{timestamp}.csv'
			
			if files_data:
				with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
					fieldnames = ['Filename', 'Full_Path', 'Size_Bytes', 'Size_MB', 'Last_Modified', 'ETag', 'Storage_Class']
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					
					writer.writeheader()
					writer.writerows(files_data)
				
				print(f'✓ {file_count} files listed and saved to: {csv_filename}')
				
				# Print summary
				total_size_mb = sum(file['Size_MB'] for file in files_data)
				print(f'  Total files: {file_count}')
				print(f'  Total size: {total_size_mb:.2f} MB')
				
			else:
				print(f'  No files found in {bucket_name}/{prefix}')
				# Create empty CSV with headers
				with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
					fieldnames = ['Filename', 'Full_Path', 'Size_Bytes', 'Size_MB', 'Last_Modified', 'ETag', 'Storage_Class']
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					writer.writeheader()
				print(f'✓ Empty listing saved to: {csv_filename}')
		
		print('\n✓ AWS bucket listing complete!')
		
	except Exception as e:
		print(f'❌ Error listing AWS buckets: {str(e)}')
		return False
	
	return True

def list_specific_bucket_folder(bucket_name, prefix='', save_to_csv=True):
	"""
	Lists files in a specific bucket/folder combination
	
	Args:
		bucket_name (str): Name of the S3 bucket
		prefix (str): Folder prefix (e.g., 'maps/', 'listings/')
		save_to_csv (bool): Whether to save results to CSV
	
	Returns:
		list: List of file information dictionaries
	"""
	try:
		s3_client = boto3.client('s3')
		
		print(f'\nListing files in {bucket_name}/{prefix}...')
		
		paginator = s3_client.get_paginator('list_objects_v2')
		page_iterator = paginator.paginate(
			Bucket=bucket_name,
			Prefix=prefix
		)
		
		files_data = []
		
		for page in page_iterator:
			if 'Contents' in page:
				for obj in page['Contents']:
					# Skip the folder itself
					if obj['Key'] != prefix:
						file_info = {
							'Filename': os.path.basename(obj['Key']),
							'Full_Path': obj['Key'],
							'Size_Bytes': obj['Size'],
							'Size_MB': round(obj['Size'] / 1024 / 1024, 2),
							'Last_Modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
							'ETag': obj['ETag'].strip('"'),
							'Storage_Class': obj.get('StorageClass', 'STANDARD')
						}
						files_data.append(file_info)
		
		if save_to_csv and files_data:
			temp_dir = 'C:\\TEMP'
			if not os.path.exists(temp_dir):
				os.makedirs(temp_dir)
				
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			folder_name = prefix.replace('/', '_').strip('_') or 'root'
			csv_filename = f'{temp_dir}\\aws_{bucket_name}_{folder_name}_{timestamp}.csv'
			
			with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
				fieldnames = ['Filename', 'Full_Path', 'Size_Bytes', 'Size_MB', 'Last_Modified', 'ETag', 'Storage_Class']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(files_data)
			
			print(f'✓ {len(files_data)} files saved to: {csv_filename}')
		
		return files_data
		
	except Exception as e:
		print(f'❌ Error listing bucket {bucket_name}/{prefix}: {str(e)}')
		return []

if __name__ == '__main__':
	# Run the main listing function
	list_aws_buckets_to_csv()