import pandas as pd
import numpy as np
from datetime import datetime

def enhance_activtrak_data(input_file):
	"""
	Enhance ActivTrak data with time span calculations between first and last activity
	
	Args:
		input_file (str): Path to the original ActivTrak Excel file
	
	Returns:
		Enhanced Excel file with additional time span columns
	"""
	
	# Read the original Excel file
	print(f"Reading file: {input_file}")
	df = pd.read_excel(input_file)
	
	# Display basic info about the data
	print(f"Total records: {len(df)}")
	print(f"Columns: {list(df.columns)}")
	
	# Convert datetime columns
	df['First Activity'] = pd.to_datetime(df['First Activity'], errors='coerce')
	df['Last Activity'] = pd.to_datetime(df['Last Activity'], errors='coerce')
	df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
	
	# Calculate time span between first and last activity
	def calculate_time_span(row):
		"""Calculate minutes between first and last activity"""
		if pd.notna(row['First Activity']) and pd.notna(row['Last Activity']):
			time_diff = row['Last Activity'] - row['First Activity']
			return time_diff.total_seconds() / 60  # Return minutes
		return None
	
	def format_minutes_to_hhmm(minutes):
		"""Convert minutes to H:MM format"""
		if pd.isna(minutes) or minutes is None:
			return None
		hours = int(minutes // 60)
		mins = int(minutes % 60)
		return f"{hours}:{mins:02d}"
	
	def minutes_to_decimal_hours(minutes):
		"""Convert minutes to decimal hours"""
		if pd.isna(minutes) or minutes is None:
			return None
		return round(minutes / 60, 2)
	
	# Apply time span calculations
	print("Calculating time spans...")
	df['Total Time Span (minutes)'] = df.apply(calculate_time_span, axis=1)
	df['Total Time Span (h:mm)'] = df['Total Time Span (minutes)'].apply(format_minutes_to_hhmm)
	df['Total Time Span (decimal hours)'] = df['Total Time Span (minutes)'].apply(minutes_to_decimal_hours)
	
	# Add analysis flags for HR review
	df['Less than 8 hours span'] = df['Total Time Span (minutes)'] < 480
	df['8+ hours span'] = df['Total Time Span (minutes)'] >= 480
	df['More than 10 hours span'] = df['Total Time Span (minutes)'] > 600
	
	# Calculate difference between time span and recorded work time
	# Note: Work Time appears to be in seconds based on the sample data
	def calculate_span_vs_work_difference(row):
		"""Calculate difference between time span and actual work time"""
		if pd.notna(row['Total Time Span (minutes)']) and pd.notna(row['Work Time']):
			work_time_minutes = row['Work Time'] / 60  # Convert seconds to minutes
			return row['Total Time Span (minutes)'] - work_time_minutes
		return None
	
	df['Time Span vs Work Time Diff (min)'] = df.apply(calculate_span_vs_work_difference, axis=1)
	
	# Reorder columns for better presentation
	column_order = [
		'Date', 'User', 
		'First Activity', 'Last Activity',
		'Total Time Span (h:mm)', 'Total Time Span (decimal hours)', 'Total Time Span (minutes)',
		'Work Time', 'Work Time (h:mm:ss)',
		'Time Span vs Work Time Diff (min)',
		'Less than 8 hours span', '8+ hours span', 'More than 10 hours span'
	]
	
	# Only include columns that exist in the data
	available_columns = [col for col in column_order if col in df.columns]
	df_enhanced = df[available_columns]
	
	# Generate statistics
	active_records = df_enhanced.dropna(subset=['Total Time Span (minutes)'])
	
	print(f"\nAnalysis Results:")
	print(f"Records with activity data: {len(active_records)} out of {len(df_enhanced)}")
	
	if len(active_records) > 0:
		avg_span = active_records['Total Time Span (minutes)'].mean() / 60
		max_span = active_records['Total Time Span (minutes)'].max() / 60
		min_span = active_records['Total Time Span (minutes)'].min() / 60
		
		short_days = len(active_records[active_records['Less than 8 hours span'] == True])
		long_days = len(active_records[active_records['More than 10 hours span'] == True])
		
		print(f"Average time span: {avg_span:.2f} hours")
		print(f"Maximum time span: {max_span:.2f} hours")  
		print(f"Minimum time span: {min_span:.2f} hours")
		print(f"Records with < 8 hour span: {short_days} ({short_days/len(active_records)*100:.1f}%)")
		print(f"Records with > 10 hour span: {long_days} ({long_days/len(active_records)*100:.1f}%)")
	
	# Save enhanced file
	output_filename = input_file.replace('.xlsx', '_Enhanced.xlsx')
	
	with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
		# Write main data
		df_enhanced.to_excel(writer, sheet_name='Enhanced Data', index=False)
		
		# Create summary sheet
		if len(active_records) > 0:
			summary_data = [
				['Metric', 'Value'],
				['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
				['', ''],
				['Total Records', len(df_enhanced)],
				['Records with Activity', len(active_records)],
				['Records without Activity', len(df_enhanced) - len(active_records)],
				['', ''],
				['Average Time Span (hours)', f"{avg_span:.2f}"],
				['Maximum Time Span (hours)', f"{max_span:.2f}"],
				['Minimum Time Span (hours)', f"{min_span:.2f}"],
				['', ''],
				['Records < 8 hours span', short_days],
				['Records >= 8 hours span', len(active_records) - short_days],
				['Records > 10 hours span', long_days],
				['', ''],
				['% of active days < 8 hours', f"{short_days/len(active_records)*100:.1f}%"],
				['% of active days >= 8 hours', f"{(len(active_records) - short_days)/len(active_records)*100:.1f}%"],
				['% of active days > 10 hours', f"{long_days/len(active_records)*100:.1f}%"],
				['', ''],
				['Notes:', ''],
				['- Total Time Span = Last Activity - First Activity', ''],
				['- Includes breaks, lunch, meetings away from desk', ''],
				['- Different from Work Time which tracks active usage', '']
			]
			
			summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
			summary_df.to_excel(writer, sheet_name='Summary', index=False)
		
		# Format the Excel file
		workbook = writer.book
		worksheet = writer.sheets['Enhanced Data']
		
		# Header format
		header_format = workbook.add_format({
			'bold': True,
			'text_wrap': True,
			'valign': 'top',
			'fg_color': '#D7E4BC',
			'border': 1
		})
		
		# Apply header formatting
		for col_num, value in enumerate(df_enhanced.columns.values):
			worksheet.write(0, col_num, value, header_format)
		
		# Set column widths
		worksheet.set_column('A:A', 12)  # Date
		worksheet.set_column('B:B', 15)  # User  
		worksheet.set_column('C:D', 20)  # Activity times
		worksheet.set_column('E:E', 18)  # Time span h:mm
		worksheet.set_column('F:G', 22)  # Decimal hours and minutes
		worksheet.set_column('H:I', 18)  # Work time columns
		worksheet.set_column('J:M', 20)  # Analysis flags
		
		# Add conditional formatting for flags
		red_format = workbook.add_format({'bg_color': '#FFC7CE'})
		green_format = workbook.add_format({'bg_color': '#C6EFCE'})
		
		# Highlight short days in red
		short_col = df_enhanced.columns.get_loc('Less than 8 hours span') if 'Less than 8 hours span' in df_enhanced.columns else None
		if short_col is not None:
			worksheet.conditional_format(1, short_col, len(df_enhanced), short_col, 
										{'type': 'cell', 'criteria': '==', 'value': 'TRUE', 'format': red_format})
	
	print(f"\nEnhanced file saved as: {output_filename}")
	return output_filename

# Usage example:
if __name__ == "__main__":
	# Replace with your actual file path
	input_file = "F:\\Research Department\\Lessons Learned\\Staff Evaluations\\ActivTrak Working Hours 2025_08_15 13_45_33.xlsx"
	enhanced_file = enhance_activtrak_data(input_file)
	print(f"\nProcess completed. Enhanced file: {enhanced_file}")