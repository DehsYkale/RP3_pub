import pandas as pd
from pyzipcode import ZipCodeDatabase



#Excel sheet to read
excel_file_path = 'C:\VS\Excel Workbooks\AutomationTest.xlsx'
df = pd.read_excel(excel_file_path, sheet_name='Sheet1')

#This seperates the Full Name into First, Middle, and Last. 
splitted = df['Name'].str.split()
df['First Name'] = splitted.str[0]
df['Last Name'] = splitted.str[-1]
df['Middle Name'] = splitted.str[1]
#This masks all middle names equal to last names
df['Middle Name'] = df['Middle Name'].mask(df['Last Name'].eq(df['Middle Name']))


#This splits the address into strings, and then assigns each string to a new column 
splitted = df['Location'].str.split()
df['zip_code'] = splitted.str[-1]
df['zip_code'] = pd.to_numeric(df['zip_code'], errors='coerce')
df.dropna(subset=['zip_code'], inplace=True)
df['zip_code'] = df['zip_code'].astype(int)


zcdb = ZipCodeDatabase()
df["State"] = df["zip_code"].map(lambda x: zcdb[x].state)
df["City"] = df["zip_code"].map(lambda x: zcdb[x].city)


df['Billing'] = df.query("City!='State'")["Location"]
df['Billing'] = df['Billing'].str.split('\n').str[0]




df.to_csv('C:\VS\Excel Workbooks\CleanedCRMImport.csv')
print(df) 