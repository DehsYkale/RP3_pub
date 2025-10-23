
import csv
import fun_text_date as td
import how
import lao
import sys


# Instructions
how.mo_census_permits_msa_extractor()

datapath = 'F:/Research Department/MIMO/zData/Permits/Census Permits by County/'
dStateFIPS = {'AK':'02','AL':'01','AR':'05','AS':'60','AZ':'04','CA':'06','CO':'08','CT':'09','DC':'11','DE':'10','FL':'12','GA':'13','GU':'66','HI':'15','IA':'19','ID':'16','IL':'17','IN':'18','KS':'20','KY':'21','LA':'22','MA':'25','MD':'24','ME':'23','MI':'26','MN':'27','MO':'29','MS':'28','MT':'30','NC':'37','ND':'38','NE':'31','NH':'33','NJ':'34','NM':'35','NV':'32','NY':'36','OH':'39','OK':'40','OR':'41','PA':'42','PR':'72','RI':'44','SC':'45','SD':'46','TN':'47','TX':'48','UT':'49','VA':'51','VI':'78','VT':'50','WA':'53','WI':'55','WV':'54','WY':'56'}

# User to enter MSA name
ui = td.uInput('\n Enter 2 Letter State Name > ')
state = ui.strip()
state = state.upper()

MSA = td.uInput('\n\n Enter MSA (Partial name ok) > ')
MSA = MSA.strip()
MSA = MSA.upper()
no_chars_msa = len(MSA)
# print(MSA)
# print(no_chars_msa)
# exit()

outFile = 'F:/Research Department/MIMO/zData/Permits/Census Permits by MSA/{0} Permits.csv'.format(MSA)
with open(outFile, 'w', newline='') as g:
	fout = csv.writer(g)
	

	print_msa = True
	for year in range(1995, 2025):
		inFile = 'F:/Research Department/MIMO/zData/Permits/Census Permits by MSA/{0} Permits MSA FORMATTED.csv'.format(year)


		with open(inFile, 'r', newline='') as f:
			fin = csv.reader(f)
			# fin.next()
			next(fin)

			# Cycle through rows to find state then county			
			for row in fin:
				# Skip if state not in row[0]
				if not state in row[0]:
					continue
				# if MSA in row[0].upper():
				full_msa = row[0].upper()
				if MSA == full_msa[0:no_chars_msa]:
					# Print the name of the selected MSA for user to verify
					if print_msa:
						td.colorText(row[0], 'GREEN')
						fout.writerow([row[0], '', '', ''])
						header = ['YEAR', 'SFR', 'MF', 'TOTAL', 'MSA']
						fout.writerow(header)
						print_msa = False
					SFR = int(row[2])
					MF = int(row[3]) + int(row[4]) + int(row[5])
					TOTAL = SFR + MF
					fout.writerow([year, SFR, MF, TOTAL, row[0]])
					break

lao.openFile(outFile)
