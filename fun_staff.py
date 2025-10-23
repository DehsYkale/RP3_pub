# Function that returns info from the staff db

import pandas as pd
from typing import Union, List, Dict

def load_staff_db(skip_former_employees=True) -> pd.DataFrame:
	"""
	Load the LAO staff database from an Excel file.
	
	Args:
		filepath: Path to the Excel file (default: 'LAO_Staff_Db_v03.xlsx')
		
	Returns:
		A pandas DataFrame containing the staff database
	"""
	filepath = r"F:\Research Department\Code\Databases\LAO_Staff_Db_v03.xlsx"

	# Load the Excel file
	df = pd.read_excel(filepath, sheet_name='staff')

	# Apply LAO filter if requested
	if skip_former_employees:
		df = df[df['LAO'] == 'Yes']
		
	return df

def staff_details(dict_key='Name') -> Dict[str, Dict[str, str]]:
	"""
	Return a dictionary of staff member details where Name is the key.
	
	Returns:
		A dictionary where:
			- Key is Name
			- Value is a dictionary containing Roll, Office, and marketAbb...
	"""
	df = load_staff_db()
	
	# Initialize the result dictionary
	dResults = {}
	
	# Include all columns as fields
	fields = df.columns.tolist()
	
	# For each person
	for _, row in df.iterrows():
		# Create sub-dictionary with required fields
		person_dict = {field: row[field] for field in fields}
		dResults[row[dict_key]] = person_dict
	
	return dResults