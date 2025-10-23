#!/usr/bin/env python3
"""
RSVP PID Lookup - Production Version (FIXED)
Final script that processes all 520 RSVP attendees with real Salesforce integration

To use this script:
1. Ensure the WVW2025_RSVP.xlsx file is in C:/TEMP/
2. Run this script from an environment with access to the Salesforce query tools
3. Results will be saved to C:/TEMP/RSVP_PIDs_Complete.csv

Author: Research Department, Land Advisors Organization  
Date: September 2025
"""

import bb
import fun_login
import pandas as pd
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import OrderedDict

service = fun_login.TerraForce()


class RSVPPIDProcessor:
	"""Production processor that uses actual Salesforce API calls"""
	
	def __init__(self, input_file: str, output_file: str):
		self.input_file = input_file
		self.output_file = output_file
		self.results = []
		self.start_time = datetime.now()
		
		# Statistics
		self.stats = {
			'people_found': 0,
			'companies_found': 0,
			'records_with_pids': 0,
			'total_pids': 0,
			'processing_errors': 0,
			'duplicate_people': 0,
			'api_calls': 0
		}
	
	def convert_ordered_dict(self, data):
		"""Convert OrderedDict to regular dict recursively"""
		if isinstance(data, OrderedDict):
			return {k: self.convert_ordered_dict(v) for k, v in data.items()}
		elif isinstance(data, list):
			return [self.convert_ordered_dict(item) for item in data]
		else:
			return data
	
	def search_person(self, first_name: str, last_name: str) -> Tuple[Optional[Dict], List[Dict]]:
		"""Search for a person in Salesforce Accounts"""
		try:
			# Clean names for query
			first_clean = first_name.replace("'", "\\'").strip()
			last_clean = last_name.replace("'", "\\'").strip()
			
			# TerraForce Query
			fields = 'default'
			wc = "FirstName = '{}' AND LastName = '{}'".format(first_clean, last_clean)
			self.stats['api_calls'] += 1
			results = bb.tf_query_3(service, rec_type='Person', where_clause=wc, limit=None, fields=fields)
			
			# Handle the results structure - bb.tf_query_3 returns a list of OrderedDict directly
			records = []
			if results and isinstance(results, list):
				# Convert OrderedDict objects to regular dicts
				records = [self.convert_ordered_dict(record) for record in results]
				
				if records and len(records) > 0:
					if len(records) > 1:
						self.stats['duplicate_people'] += 1
					return records[0], records
			
			return None, []
				
		except Exception as e:
			print(f"Error searching for {first_name} {last_name}: {str(e)}")
			print(f"Results type: {type(results)} - First item: {results[0] if results else 'None'}")
			return None, []
	
	def get_company_info(self, company_id: str) -> Optional[Dict]:
		"""Get company information from Account record"""
		try:
			if not company_id:
				return None
			
			# TerraForce Query for Entity
			fields = 'default'
			wc = "Id = '{}'".format(company_id)
			self.stats['api_calls'] += 1
			results = bb.tf_query_3(service, rec_type='Entity', where_clause=wc, limit=None, fields=fields)
			
			if results and isinstance(results, list) and len(results) > 0:
				return self.convert_ordered_dict(results[0])
			
			return None
			
		except Exception as e:
			print(f"Error getting company {company_id}: {str(e)}")
			return None
	
	def find_properties(self, person_id: str, company_id: str = None) -> List[Dict]:
		"""Find properties associated with person and/or company"""
		try:
			where_conditions = []
			
			# Search by person
			if person_id:
				where_conditions.append("AccountId__c = '{}'".format(person_id))
			
			# Search by company
			if company_id:
				where_conditions.append("Owner_Entity__c = '{}'".format(company_id))
			
			if not where_conditions:
				return []
			
			where_clause = " OR ".join(where_conditions)
			
			# TerraForce Query for Deals
			fields = 'default'
			self.stats['api_calls'] += 1
			results = bb.tf_query_3(service, rec_type='Deal', where_clause=where_clause, limit=100, fields=fields)
			
			if results and isinstance(results, list):
				return [self.convert_ordered_dict(record) for record in results]
			
			return []

		except Exception as e:
			print(f"Error finding properties: {str(e)}")
			return []
	
	def process_person(self, row: pd.Series, index: int) -> Dict:
		"""Process a single person from the RSVP list"""
		first_name = str(row['First Name']).strip()
		last_name = str(row['Last Name']).strip()
		email = str(row['Email']).strip()
		
		print(f"Processing {index + 1:3d}/520: {first_name} {last_name}")
		
		# Initialize result
		result = {
			'First Name': first_name,
			'Last Name': last_name,
			'Email': email,
			'Companies': '',
			'PIDs': ''
		}
		
		try:
			# Step 1: Search for person in Salesforce
			person_record, all_records = self.search_person(first_name, last_name)
			
			if not person_record:
				print(f"  ✗ Not found in Salesforce")
				return result
			
			self.stats['people_found'] += 1
			print(f"  ✓ Found person: {person_record.get('Id', 'Unknown')}")
			
			companies = []
			all_properties = []
			
			# Step 2: Process each person record (handle duplicates)
			for record in all_records:
				person_id = record.get('Id')
				company_id = record.get('Company__c')
				
				# Step 3: Get company information if exists
				if company_id:
					company_info = self.get_company_info(company_id)
					if company_info and company_info.get('Name'):
						company_name = company_info['Name']
						if company_name not in companies:
							companies.append(company_name)
							print(f"  ✓ Found company: {company_name}")
				
				# Step 4: Find properties
				properties = self.find_properties(person_id, company_id)
				all_properties.extend(properties)
			
			# Update company statistics
			if companies:
				self.stats['companies_found'] += 1
			
			# Step 5: Extract and process PIDs
			pids = []
			for prop in all_properties:
				pid = prop.get('PID__c')
				if pid and pid not in pids:
					pids.append(pid)
			
			# Sort PIDs for consistent output
			pids.sort()
			
			if pids:
				self.stats['records_with_pids'] += 1
				self.stats['total_pids'] += len(pids)
				print(f"  ✓ Found {len(pids)} properties")
			
			# Update result
			result['Companies'] = '; '.join(companies)
			result['PIDs'] = '; '.join(pids)
			
		except Exception as e:
			print(f"  ✗ Error: {str(e)}")
			self.stats['processing_errors'] += 1
		
		return result
	
	def load_data(self) -> pd.DataFrame:
		"""Load the RSVP Excel file"""
		try:
			print(f"Loading data from: {self.input_file}")
			df = pd.read_excel(self.input_file)
			print(f"Loaded {len(df)} records")
			
			# Validate required columns
			required_cols = ['First Name', 'Last Name', 'Email']
			missing_cols = [col for col in required_cols if col not in df.columns]
			if missing_cols:
				raise ValueError(f"Missing required columns: {missing_cols}")
			
			return df
			
		except Exception as e:
			print(f"Error loading data: {str(e)}")
			raise
	
	def save_results(self, df: pd.DataFrame):
		"""Save all results and statistics"""
		try:
			# Main results
			df.to_csv(self.output_file, index=False)
			print(f"\n✓ Results saved to: {self.output_file}")
			
			# High-value records (with PIDs)
			high_value = df[df['PIDs'] != '']
			if len(high_value) > 0:
				hv_file = self.output_file.replace('.csv', '_high_value.csv')
				high_value.to_csv(hv_file, index=False)
				print(f"✓ High-value records: {hv_file}")
			
			# Statistics file
			stats_file = self.output_file.replace('.csv', '_statistics.txt')
			self.save_statistics(stats_file, df)
			print(f"✓ Statistics: {stats_file}")
			
		except Exception as e:
			print(f"Error saving results: {str(e)}")
			raise
	
	def save_statistics(self, stats_file: str, df: pd.DataFrame):
		"""Save detailed processing statistics"""
		total = len(df)
		elapsed = datetime.now() - self.start_time
		
		with open(stats_file, 'w') as f:
			f.write("RSVP PID Lookup Processing Report\n")
			f.write("=" * 60 + "\n\n")
			
			f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
			f.write(f"Input File: {self.input_file}\n")
			f.write(f"Output File: {self.output_file}\n")
			f.write(f"Processing Time: {str(elapsed).split('.')[0]}\n\n")
			
			f.write("SUMMARY STATISTICS:\n")
			f.write(f"Total Records: {total:,}\n")
			f.write(f"People Found: {self.stats['people_found']:,} ({self.stats['people_found']/total*100:.1f}%)\n")
			f.write(f"With Companies: {self.stats['companies_found']:,} ({self.stats['companies_found']/total*100:.1f}%)\n")
			f.write(f"With PIDs: {self.stats['records_with_pids']:,} ({self.stats['records_with_pids']/total*100:.1f}%)\n")
			f.write(f"Total PIDs: {self.stats['total_pids']:,}\n")
			f.write(f"Avg PIDs per Record: {self.stats['total_pids']/max(self.stats['records_with_pids'],1):.1f}\n")
			f.write(f"API Calls Made: {self.stats['api_calls']:,}\n")
			f.write(f"Processing Errors: {self.stats['processing_errors']:,}\n")
			f.write(f"Duplicate Records: {self.stats['duplicate_people']:,}\n")
			
			# Company breakdown
			if self.stats['records_with_pids'] > 0:
				f.write("\nTOP COMPANIES BY PID COUNT:\n")
				company_pids = {}
				for _, row in df[df['PIDs'] != ''].iterrows():
					companies = row['Companies'].split('; ') if row['Companies'] else []
					pid_count = len(row['PIDs'].split('; ')) if row['PIDs'] else 0
					for company in companies:
						if company.strip():
							company_pids[company.strip()] = company_pids.get(company.strip(), 0) + pid_count
				
				for company, count in sorted(company_pids.items(), key=lambda x: x[1], reverse=True)[:15]:
					f.write(f"  {company}: {count} PIDs\n")
	
	def run(self) -> bool:
		"""Main processing function"""
		try:
			print("RSVP PID Lookup Processor - Production Version (FIXED)")
			print("=" * 60)
			
			# Load data
			df = self.load_data()
			total_records = len(df)
			
			print(f"\nStarting processing of {total_records} records...")
			print("Estimated time: 30-45 minutes")
			print("Press Ctrl+C to interrupt and save partial results")
			print("-" * 60)
			
			# Process each record
			for index, row in df.iterrows():
				try:
					result = self.process_person(row, index)
					self.results.append(result)
					
					# Progress updates every 25 records
					if (index + 1) % 25 == 0:
						self.log_progress(index + 1, total_records)
					
					# Rate limiting - small delay between API calls
					time.sleep(0.15)  # 150ms delay
					
				except KeyboardInterrupt:
					print(f"\n⚠ Processing interrupted at record {index + 1}")
					break
				except Exception as e:
					print(f"  ✗ Unexpected error: {str(e)}")
					# Add empty result to maintain alignment
					empty_result = {
						'First Name': str(row['First Name']).strip(),
						'Last Name': str(row['Last Name']).strip(),
						'Email': str(row['Email']).strip(),
						'Companies': '',
						'PIDs': ''
					}
					self.results.append(empty_result)
			
			# Create final results DataFrame
			results_df = pd.DataFrame(self.results)
			
			# Save all results
			self.save_results(results_df)
			
			# Display final report
			self.display_final_report(results_df)
			
			return True
			
		except Exception as e:
			print(f"Fatal error: {str(e)}")
			return False
	
	def log_progress(self, current: int, total: int):
		"""Log processing progress"""
		percent = (current / total) * 100
		elapsed = datetime.now() - self.start_time
		rate = current / elapsed.total_seconds() * 60 if elapsed.total_seconds() > 0 else 0
		
		print(f"Progress: {current:3d}/{total} ({percent:5.1f}%) | "
			  f"Rate: {rate:.1f}/min | "
			  f"Found: {self.stats['people_found']} people, {self.stats['total_pids']} PIDs")
	
	def display_final_report(self, df: pd.DataFrame):
		"""Display final processing report"""
		total = len(df)
		with_pids = len(df[df['PIDs'] != ''])
		elapsed = datetime.now() - self.start_time
		
		print("\n" + "="*70)
		print("FINAL PROCESSING REPORT")
		print("="*70)
		print(f"Records Processed: {total:,}")
		print(f"People Found: {self.stats['people_found']:,} ({self.stats['people_found']/total*100:.1f}%)")
		print(f"Companies Found: {self.stats['companies_found']:,} ({self.stats['companies_found']/total*100:.1f}%)")
		print(f"Records with PIDs: {with_pids:,} ({with_pids/total*100:.1f}%)")
		print(f"Total PIDs Found: {self.stats['total_pids']:,}")
		print(f"Processing Time: {str(elapsed).split('.')[0]}")
		print(f"API Calls Made: {self.stats['api_calls']:,}")
		
		if with_pids > 0:
			print(f"\nTop records by PID count:")
			top_records = df[df['PIDs'] != ''].copy()
			top_records['PID_Count'] = top_records['PIDs'].apply(lambda x: len(x.split('; ')) if x else 0)
			top_records = top_records.nlargest(5, 'PID_Count')
			
			for _, row in top_records.iterrows():
				print(f"  {row['First Name']} {row['Last Name']} ({row['Companies']}): {row['PID_Count']} PIDs")
		
		print("="*70)
		print(f"\nResults saved to: {self.output_file}")


def main():
	"""Main function"""
	# Configuration
	input_file = "C:/TEMP/WVW2025_RSVP.xlsx"
	output_file = "C:/TEMP/RSVP_PIDs_Complete.csv"
	
	# Validate input file
	if not os.path.exists(input_file):
		print(f"ERROR: Input file not found: {input_file}")
		print("\nPlease ensure:")
		print("1. The Excel file is saved in C:/TEMP/")
		print("2. The filename is exactly: WVW2025_RSVP.xlsx")
		print("3. The file contains columns: Name, Email, First Name, Last Name")
		return False
	
	# Create and run processor
	processor = RSVPPIDProcessor(input_file, output_file)
	success = processor.run()
	
	if success:
		print("\n🎉 RSVP PID lookup completed successfully!")
		print(f"Check your results in: {output_file}")
	else:
		print("\n❌ Processing encountered errors. Check the logs above.")
	
	return success


if __name__ == "__main__":
	main()