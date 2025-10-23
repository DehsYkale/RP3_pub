# Combines multiple CSV files into a single CSV file for the tax delinquent properties project.

from datetime import datetime
import fun_text_date as td
from glob import glob
import lao
import mpy
import os
import pandas as pd
from pprint import pprint



def combine_csv_files(folder_path):
	# Get the current date in the format YYYY-MM-DD
	current_date = datetime.now().strftime('%Y-%m-%d')
	
	# Initialize a list to hold dataframes
	dataframes = []
	
	# Loop through the files in the folder
	file_pattern = os.path.join(folder_path, '*TD*.csv')
	lTax_delinquent_files = glob(file_pattern)
	for file_name in lTax_delinquent_files:
		# Read each CSV file and append to the list
		df = pd.read_csv(file_name)
		dataframes.append(df)
	
	# Concatenate all dataframes
	combined_df = pd.concat(dataframes, ignore_index=True)

	# Remove all rows that start with The information contained
	combined_df = combined_df[~combined_df['APN'].str.startswith('The information contained')]

	# Cycle through the df and run the fuction mpy.get_LAO_geoinfo using the longitute and latitude
	for index, row in combined_df.iterrows():
		# pprint(row)
		lat = row['Latitude']
		lon = row['Longitude']
		dLAO_geoinfo = mpy.get_LAO_geoinfo(dTF='None', lon=lon, lat=lat)
		# Add the city, market_abb, and submarket from dLAO_geoinfo to the df
		combined_df.at[index, 'City'] = dLAO_geoinfo['city']
		combined_df.at[index, 'Market'] = dLAO_geoinfo['market_abb']
		combined_df.at[index, 'Submarket'] = dLAO_geoinfo['submarket']

	# Define the output filename with the current date
	output_file = f"LAO Markets Tax Delinquent {current_date}.csv"
	output_path = os.path.join(folder_path, output_file)
	
	# Save the combined dataframe to a CSV file
	combined_df.to_csv(output_path, index=False)

	# Create a list of lists from the combined dataframe
	lCombined = combined_df.values.tolist()
	pprint(lCombined)

	print(f"Combined CSV saved as {output_file}")

	lao.openFile(output_path)

td.banner('Tax Delinquent Properties v01')
# Example usage
combine_csv_files(r'F:\Research Department\MIMO\zData\Debt\Tax Delinquent')
