import pandas as pd
import mpy
import os
import sys
import time

def main():
	try:
		# Define the path to the Excel file
		excel_file = r"F:\Research Department\Projects\Advisors and Markets\Greenville Spartanburg\GSP Self-Storage.xlsx"
		
		# Check if file exists
		if not os.path.exists(excel_file):
			print(f"Error: File '{excel_file}' not found.")
			sys.exit(1)
		
		# Read the Excel file
		print(f"Reading Excel file: {excel_file}")
		df = pd.read_excel(excel_file)
		
		# Check for required columns
		required_columns = ["D-U-N-S® Number", "Address Line 1", "City", "State Or Province", "Postal Code"]
		for col in required_columns:
			if col not in df.columns:
				print(f"Error: Required column '{col}' not found in Excel file.")
				sys.exit(1)
		
		# Create a list to store the results
		results = []
		
		# Total number of locations to process
		total = len(df)
		print(f"Found {total} locations to process")
		
		# Process each location
		for index, row in df.iterrows():
			duns_number = row["D-U-N-S® Number"]
			address_line1 = str(row["Address Line 1"])
			city = str(row["City"])
			state = str(row["State Or Province"])
			postal_code = str(row["Postal Code"])
			
			# Format the address for geocoding
			full_address = f"{address_line1}, {city}, {state} {postal_code}"
			
			print(f"Processing {index+1}/{total}: {full_address}")
			
			try:
				# Get coordinates using the provided function
				lon, lat = mpy.get_lon_lat_from_address_or_intersection(full_address)
				print(f"  Coordinates found: {lon}, {lat}")
				
				# Add to results
				results.append({
					"DUNS_Number": duns_number,
					"Address": full_address,
					"Longitude": lon,
					"Latitude": lat
				})
				
				# Add a short delay to prevent hitting API rate limits
				time.sleep(0.5)
				
			except Exception as e:
				print(f"  Error getting coordinates for {full_address}: {str(e)}")
				# Add to results with empty coordinates
				results.append({
					"DUNS_Number": duns_number,
					"Address": full_address,
					"Longitude": "",
					"Latitude": ""
				})
		
		# Create a DataFrame from the results
		results_df = pd.DataFrame(results)
		
		# Save to CSV
		output_file = r"F:\Research Department\Projects\Advisors and Markets\Greenville Spartanburg\self_storage_coordinates.csv"
		results_df[["DUNS_Number", "Longitude", "Latitude"]].to_csv(output_file, index=False)
		
		print(f"\nCoordinates saved to {output_file}")
		print(f"Successfully processed {len(results)} locations")
		
	except Exception as e:
		print(f"An error occurred: {str(e)}")
		sys.exit(1)

if __name__ == "__main__":
	main()