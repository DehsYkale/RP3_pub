
from lao import uInput, getUserName, consoleWindowPosition
import fjson
from os import system, startfile
import socket

system('cls')
user = getUserName()

# Move the console window to the correct position
if user == 'blandis':
	consoleWindowPosition(position='Bill Marvelous Menu')

# Get the json file with the path to the Python script to launch
d = fjson.getJsonDict('C:/Users/Public/Public Mapfiles/python_script_to_launch.json')

# Determin the version of python to use
if 'RP3' in d['scriptPath']:
	pypath = 'C:/"Program Files"/Python312/python.exe'
else:
	pypath = 'C:/Python27/ArcGIS10.8/python.exe'

# Create the command line to launch the Python script
lauchCommandLine = '{0} "{1}"'.format(pypath, d['scriptPath'])

# Launch the Python script
system(lauchCommandLine)

print(' \n Python Script Shell v01')
uInput('\n [Enter] to close...')
