# python3

import lao
import fun_text_date as td
import shutil
from os import remove
from glob import glob

zfiles = lao.unzipPinal()
if zfiles == 'Not the email with the link.':
	td.warningMsg(' Not the email with the link.')
	lao.sleep(3)
else:
	my_arch = 'F:/Research Department/Code/RP3/data/Dailies/Pinal/ArchZips'
	for zfile in zfiles:
		my_zip = zfile
		shutil.move(my_zip, my_arch)
	print('\n Renaming TIFF files...')
	lao.renamePinalTIFFs()

# Remove all text files

email_files = glob(r'F:\Research Department\PiRec\*.txt')
for file in email_files:
	print(f' Removing {file}...')
	ui = td.uInput('\n Continue [00]... > ')
	if ui == '00':
		exit('\n Terminating program...')
	remove(file)
exit()