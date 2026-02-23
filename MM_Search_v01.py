#! python3

import pandas as pd
import fun_text_date as td
from os import system

def search_menu_db(search_term):
	"""Search the Marvelous Menu database for matching titles"""
	# Load the database
	db_path = 'F:/Research Department/Code/Databases/Marvelous_Menu_Db_PY3.xlsx'
	df = pd.read_excel(db_path)
	
	# Filter out rows where Title is NaN or special formatting rows
	df = df[df['Title'].notna()]
	df = df[~df['Title'].isin(['Blank Line', 'Dash Line'])]
	
	# Filter out rows without a File (can't launch these)
	df = df[df['File'].notna()]
	
	# Search for matches (case-insensitive)
	mask = df['Title'].str.lower().str.contains(search_term.lower(), na=False)
	results = df[mask].reset_index(drop=True)
	
	return results

def display_results(results):
	"""Display search results in formatted output"""
	if len(results) == 0:
		td.warningMsg('\n No matching scripts found.')
		return
	
	print(f'\n Found {len(results)} matching script(s):\n')
	print(f' {"#":<4} {"Menu":<12} {"Index":<8} {"Title":<50} {"File"}')
	print('-' * 130)
	
	for i, row in results.iterrows():
		menu = str(row['Menu']) if pd.notna(row['Menu']) else ''
		index = str(int(row['Index'])) if pd.notna(row['Index']) else '-'
		title = str(row['Title']) if pd.notna(row['Title']) else ''
		file = str(row['File']) if pd.notna(row['File']) else ''
		
		# Truncate title if too long
		if len(title) > 48:
			title = title[:45] + '...'
		
		print(f' {i+1:<4} {menu:<12} {index:<8} {title:<50} {file}')

def build_path_filename(py_version, python_script):
	"""Build the full command path based on Python version"""
	if py_version == 'PY2':
		pypath = 'C:/Python27/ArcGIS10.8/python.exe "F:/Research Department/Code/Research/'
		filename = f'{pypath}{python_script}"'
	elif py_version == 'PY3':
		pypath = 'C:/"Program Files"/Python312/python.exe F:/"Research Department"/Code/RP3/'
		filename = f'{pypath}{python_script}'
	elif py_version == 'AP3':
		pypath = 'C:/"Program Files"/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe F:/"Research Department"/Code/RP3/'
		filename = f'{pypath}{python_script}'
	else:
		filename = None
	return filename

def launch_script(results, selection):
	"""Launch the selected script"""
	try:
		idx = int(selection) - 1
		if idx < 0 or idx >= len(results):
			td.warningMsg('\n Invalid selection.')
			return False
		
		row = results.iloc[idx]
		py_version = row['PY Version'] if pd.notna(row['PY Version']) else None
		python_script = row['File'] if pd.notna(row['File']) else None
		
		if not py_version or not python_script:
			td.warningMsg('\n Cannot launch - missing version or file info.')
			return False
		
		filename = build_path_filename(py_version, python_script)
		if not filename:
			td.warningMsg(f'\n Unknown Python version: {py_version}')
			return False
		
		print(f'\n Launching: {row["Title"]}')
		print(f' Command: {filename}\n')
		system(filename)
		td.uInput('\n [Enter] to return to search...')
		return True
		
	except ValueError:
		td.warningMsg('\n Invalid input - enter a number.')
		return False

def main():
	td.console_title('MM Search')
	
	while True:
		td.banner('                      Marvelous Menu Search Tool                              ')
		
		search_term = td.uInput('\n Enter search term (or 00 to quit) > ')
		
		if search_term == '00':
			print('\n Program terminated...')
			break
		
		if search_term == '':
			td.warningMsg('\n Please enter a search term.')
			continue
		
		results = search_menu_db(search_term)
		display_results(results)
		
		if len(results) == 0:
			continue
		
		# Allow user to select and launch a script
		while True:
			print(f'\n [1-{len(results)}] Launch script | [0] New search | [00] Quit')
			selection = td.uInput(' > ')
			
			if selection == '00':
				print('\n Program terminated...')
				return
			
			if selection == '0' or selection == '':
				break  # Return to search
			
			launch_script(results, selection)
			break  # Return to search after launch

if __name__ == '__main__':
	main()