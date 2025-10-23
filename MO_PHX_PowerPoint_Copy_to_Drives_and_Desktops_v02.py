# Copy PHX MO PPTX & PDFs to drives & desktops

import lao
from pprint import pprint
from glob import glob
import os
import shutil
import fun_text_date as td

def copy_to_destination(outpath, copyPDF=False, destination='None'):
	lPHX_MO_files = glob('{0}PHX Market Overview 20*.*'.format(outpath))
	td.colorText(' Copying to {0}...'.format(destination), 'GREEN')
	# print(' Deleting existing files...')
	copyPPTX = True
	for fMO in lPHX_MO_files:
		td.colorText(' Deleting {0}...'.format(fMO), 'ORANGE')
		try:
			os.remove(fMO)
		except WindowsError:
			td.warningMsg(' Delete failed...\n {0} is open by another user...\n Copy not done.'.format(fMO))
			copyPPTX = False

	if copyPPTX:
		try:
			shutil.copyfile(inPPTX_full_path, '{0}{1}'.format(outpath, outPPTX_file_name))
		except IOError:
			td.warningMsg(' Failed to copy to {0}.'.format(destination))
		
		if copyPDF:
			try:
				shutil.copyfile(inPDF_full_path, '{0}{1}'.format(outpath, outPDF_file_name))
			except PermissionError:
				td.warningMsg(' Failed to copy PDF to {0}.'.format(destination))
		print(' Copy finished...\n')

lao.banner('MO Copy PHX PowerPoints to Drives and Desktops v02')
currentQtr = lao.getDateQuarter(lastquarter=True)
inPPTXpath = 'F:/Research Department/MIMO/PowerPoints/Phoenix/{0} Market Overview/'.format(currentQtr)
print(inPPTXpath)
inPPTX_full_path = lao.guiFileOpen(path=inPPTXpath, titlestring='Select MO PowerPoint file', extension=[('PowerPoint files', '.pptx'), ('all files', '.*')])
inPDF_full_path = inPPTX_full_path.replace('.pptx', '.pdf')
print(inPDF_full_path)

# Check if PDF file exists
if os.path.isfile(inPDF_full_path) is False:
	td.warningMsg('\n PFD file does not exists.  Make it and rerun program.')
	ui = td.uInput('\n Continue... > ')
	exit('\n Terminating program...')

outPPTX_file_name = os.path.basename(inPPTX_full_path)
outPDF_file_name = os.path.basename(inPDF_full_path)
outVision_path = '//vision-pc/c$/Users/landadvisor/Desktop/'
outBressan_path = '//training-pc/c$/Users/landadvisor/Desktop/'
outStarboard_path = '//starboard/c$/Users/landadvisor/Desktop/'
outBLDropbox_path = 'C:/Users/blandis/Dropbox/LAO/MarketOverviews/'
# outGVDesktop_path = '//GVOGELPC/Users/gvogel/Desktop/'
# outGVDropbox_path = '//192.168.1.65/Archive/User/0-Current Users/Greg Vogel/GVogel_Presentations/Phoenix Market Overviews (Dropboxed)/'
outPhoenixMarketOverview_path = 'F:/PhoenixMarketOverview/'

# Copy files
lao.banner('MO Copy PHX PowerPoints to Drives and Desktops v02')

copy_to_destination(outVision_path, copyPDF=False, destination='Vision')
copy_to_destination(outBressan_path, copyPDF=False, destination='Bressan')
copy_to_destination(outBressan_path, copyPDF=False, destination='Starboard')
# copy_to_destination(outGVDesktop_path, copyPDF=False, destination='GV Desktop')
copy_to_destination(outBLDropbox_path, copyPDF=True, destination='BL Dropbox')
# copy_to_destination(outGVDropbox_path, copyPDF=True, destination='GV Dropbox')
copy_to_destination(outPhoenixMarketOverview_path, copyPDF=True, destination='F:/PhoenixMarketOverview')

exit('\n Fin')


