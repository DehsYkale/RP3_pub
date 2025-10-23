import arcpy
from glob import glob
import os
import json


def get_parcel_centroid(parcel_geometry):
	"""
	Calculate the centroid (lon, lat) of a parcel geometry.
	Returns longitude and latitude as floats.
	"""
	try:
		extent = parcel_geometry.extent
		lon = float((extent.XMax + extent.XMin) / 2)
		lat = float((extent.YMax + extent.YMin) / 2)
		return lon, lat
	except:
		return 0.0, 0.0

def write_parcel_owner_info_json():
	"""
	Write parcel owner information from selected parcels to a JSON file.
	This function extracts owner data from the selected parcel layer and writes it to 
	'C:/TEMP/ArcMakePIDFromParcelOwnerInfo.json' in the specified JSON format.
	"""
	
	# Ensure temp directory exists
	temp_dir = 'C:/Users/Public/Public Mapfiles/M1_Files'
	if not os.path.exists(temp_dir):
		os.makedirs(temp_dir)

	output_file = 'C:/Users/Public/Public Mapfiles/M1_Files/ArcMakePIDFromParcelOwnerInfo.json'

	try:
		# Check if parcel_lyr exists (should be created from selected parcels)
		if not arcpy.Exists("parcel_lyr"):
			arcpy.AddError("No parcel layer found. Please select parcels first.")
			return False
		
		# Check for mailaddress vs mailstreet field
		desc = arcpy.Describe("parcel_lyr")
		flds = desc.fields
		mail_address_field = False
		
		for fld in flds:
			if fld.name == 'mailaddress':
				mail_address_field = True
				break
		
		index = 0
		total_acres = 0.0
		parcel_dict = {}
		
		# Process each selected parcel
		for row in arcpy.SearchCursor("parcel_lyr"):
			index += 1
			
			# Get parcel centroid coordinates
			lon, lat = get_parcel_centroid(row.shape)
			
			# Process APN information
			apn = ""
			if hasattr(row, 'APN') and str(row.APN) != '' and str(row.APN).upper() != 'NONE':
				apn = str(row.APN)
			elif hasattr(row, 'ALTAPN') and str(row.ALTAPN) != '' and str(row.ALTAPN).upper() != 'NONE':
				apn = str(row.ALTAPN)
			
			# Get propertyid
			propertyid = ""
			if hasattr(row, 'propertyid'):
				propertyid = str(row.propertyid)
			
			# Get owner information
			owner = ""
			if hasattr(row, 'owner') and row.owner:
				owner = str(row.owner)
			
			# Get mail address information
			mailstreet = ""
			mailcity = ""
			mailstate = ""
			mailzip = ""
			
			try:
				# Handle mail address field variation
				if mail_address_field and hasattr(row, 'mailaddress') and row.mailaddress:
					address_lines = row.mailaddress.split('\n')
					if len(address_lines) > 0:
						mailstreet = address_lines[0]
				elif hasattr(row, 'mailstreet') and row.mailstreet:
					mailstreet = str(row.mailstreet)
				
				if hasattr(row, 'mailcity') and row.mailcity:
					mailcity = str(row.mailcity)
				if hasattr(row, 'mailstate') and row.mailstate:
					mailstate = str(row.mailstate)
				if hasattr(row, 'mailzip') and row.mailzip:
					mailzip = str(row.mailzip)
					
			except (AttributeError, TypeError):
				# Handle null values
				pass
			
			# Get zoning information
			zoning = ""
			if hasattr(row, 'zoning') and row.zoning:
				zoning = str(row.zoning)
			
			# Get acres
			acres = 0.0
			if hasattr(row, 'acres') and row.acres:
				acres = float(row.acres)
				total_acres += acres
			
			# Create parcel entry
			parcel_entry = {
				"propertyid": propertyid,
				"acres": acres,
				"apn": apn,
				"owner": owner,
				"mailstreet": mailstreet,
				"mailcity": mailcity,
				"mailstate": mailstate,
				"mailzip": mailzip,
				"zoning": zoning,
				"lon": lon,
				"lat": lat
			}
			
			# Add to dictionary with index key
			parcel_dict["Index {0}".format(index)] = parcel_entry
			
			arcpy.AddMessage('Processing parcel {0}: APN={1}, Owner={2}'.format(index, apn, owner))
		
		# Write JSON file
		with open(output_file, 'w') as f:
			json.dump(parcel_dict, f, indent=2)
		
		# Log summary information
		arcpy.AddMessage('\nParcel owner information written successfully as JSON!')
		arcpy.AddMessage('Total parcels processed: {0}'.format(index))
		arcpy.AddMessage('Total acres: {0}'.format(round(total_acres, 2)))
		arcpy.AddMessage('Output file: {0}'.format(output_file))
		
		# Try to copy to S3, but don't fail if it doesn't work
		try:
			copy_json_to_s3()
			arcpy.AddMessage('JSON file copied to S3 successfully.')
		except Exception as s3_error:
			arcpy.AddWarning('Warning: Could not copy to S3: {0}'.format(str(s3_error)))
			arcpy.AddMessage('JSON file was still created successfully locally.')

		return True
		
	except Exception as e:
		arcpy.AddError('Error writing parcel owner information: {0}'.format(str(e)))
		return False

def find_and_create_parcel_layer():
	"""
	Find parcel layers in the map and create parcel_lyr from selected parcels.
	Looks specifically for layers with 'Parcels' in the name.
	A layer with less than 2000 features is considered to have selected parcels.
	Returns True if successful, False otherwise.
	"""
	try:
		mxd = arcpy.mapping.MapDocument("CURRENT")
		layers = arcpy.mapping.ListLayers(mxd)
		
		found_parcels = False
		
		for layer in layers:
			# Check if layer name contains 'Parcels'
			if 'Parcels' in layer.name:
				arcpy.AddMessage('Checking parcel layer: {0}'.format(layer.name))
				
				try:
					# Try to make feature layer and count features
					temp_layer_name = "temp_parcel_check"
					arcpy.MakeFeatureLayer_management(layer.name, temp_layer_name)
					count = int(arcpy.GetCount_management(temp_layer_name).getOutput(0))
					
					arcpy.AddMessage('Feature count in {0}: {1}'.format(layer.name, count))
					
					# If count is less than 2000, this layer has selected parcels
					if count < 2000:
						arcpy.AddMessage('Found {0} selected parcels in layer: {1}'.format(count, layer.name))
						
						# Delete temp layer and create parcel_lyr
						arcpy.Delete_management(temp_layer_name)
						arcpy.MakeFeatureLayer_management(layer.name, "parcel_lyr")
						found_parcels = True
						break
					else:
						arcpy.AddMessage('Layer {0} has {1} features (>= 2000), no parcels selected'.format(layer.name, count))
						arcpy.Delete_management(temp_layer_name)
						
				except Exception as e:
					arcpy.AddMessage('Could not process layer {0}: {1}'.format(layer.name, str(e)))
					if arcpy.Exists(temp_layer_name):
						arcpy.Delete_management(temp_layer_name)
					continue
		
		if not found_parcels:
			arcpy.AddMessage('No parcel layers found with selected features (count < 2000).')
		
		del mxd
		return found_parcels
		
	except Exception as e:
		arcpy.AddError('Error finding parcel layers: {0}'.format(str(e)))
		return False

def copy_json_to_s3():
	"""
	Copies M1 json files to AWS S3. 
	Compatible with Python 2.7 (ArcMap 10.8) with full AWS CLI path detection.
	"""
	import subprocess
	import sys
	import os
	from getpass import getuser
	
	user = getuser().lower()
	folder_aws = 's3://research-datastore/{0}'.format(user)
	folder_user = 'C:/Users/Public/Public Mapfiles/M1_Files'
	file = 'ArcMakePIDFromParcelOwnerInfo.json'
	local_file_path = os.path.join(folder_user, file)

	# Check if local file exists first
	if not os.path.exists(local_file_path):
		raise Exception('Local JSON file not found: {0}'.format(local_file_path))

	# Handle subprocess creation flags for Python 2.7
	creation_flags = 0
	if sys.platform == "win32":
		try:
			# Use the numeric value for CREATE_NO_WINDOW (0x08000000)
			creation_flags = 0x08000000
		except:
			creation_flags = 0

	# Try to find AWS CLI executable in common locations
	aws_paths = [
		'aws',  # Try from PATH first
		'C:/Program Files/Amazon/AWSCLIV2/aws.exe',
		'C:/Program Files/Amazon/AWSCLI/aws.exe',
		'C:/Program Files (x86)/Amazon/AWSCLIV2/aws.exe',
		'C:/Program Files (x86)/Amazon/AWSCLI/aws.exe',
		'C:/Users/{0}/AppData/Local/Programs/Python/Python312/Scripts/aws.exe'.format(os.environ.get('USERNAME', '')),
		'C:/Python27/Scripts/aws.exe',
		'C:/Python312/Scripts/aws.exe'
	]
	
	aws_cmd = None
	for aws_path in aws_paths:
		try:
			# Test if this AWS path works
			test_cmd = '"{0}" --version'.format(aws_path) if ' ' in aws_path else '{0} --version'.format(aws_path)
			
			with open(os.devnull, 'w') as devnull:
				if sys.platform == "win32" and creation_flags:
					result = subprocess.call(test_cmd, creationflags=creation_flags, shell=True, 
										   stdout=devnull, stderr=devnull)
				else:
					result = subprocess.call(test_cmd, shell=True, 
										   stdout=devnull, stderr=devnull)
			
			if result == 0:
				aws_cmd = aws_path
				break
				
		except Exception:
			continue
	
	if not aws_cmd:
		raise Exception('AWS CLI not found. Checked common installation paths.')

	try:
		# Construct the S3 copy command with proper quoting
		if ' ' in aws_cmd:
			cmd = '"{0}" s3 cp "{1}" {2}/{3} --only-show-errors'.format(aws_cmd, local_file_path, folder_aws, file)
		else:
			cmd = '{0} s3 cp "{1}" {2}/{3} --only-show-errors'.format(aws_cmd, local_file_path, folder_aws, file)
		
		# Execute the command
		if sys.platform == "win32" and creation_flags:
			result = subprocess.call(cmd, creationflags=creation_flags, shell=True)
		else:
			result = subprocess.call(cmd, shell=True)
		
		# Check return code (0 = success)
		if result != 0:
			raise Exception('AWS S3 copy failed (return code: {0}). Check credentials and bucket permissions.'.format(result))
			
	except Exception as e:
		raise Exception('S3 upload error: {0}'.format(str(e)))

def main():
	"""
	Main function to execute the parcel owner information writing process.
	"""
	arcpy.AddMessage('Starting parcel owner information extraction...')
	
	# Clean up any existing parcel_lyr
	if arcpy.Exists("parcel_lyr"):
		arcpy.Delete_management("parcel_lyr")
	
	# Find and create parcel layer from selected parcels
	if not find_and_create_parcel_layer():
		arcpy.AddError('No parcel layers with selected features found.')
		arcpy.AddError('Please select parcels in a parcel layer before running this script.')
		return
	
	# Check if we have selected parcels
	try:
		count = int(arcpy.GetCount_management("parcel_lyr").getOutput(0))
		arcpy.AddMessage('Processing {0} selected parcels'.format(count))
		
		if count == 0:
			arcpy.AddError('No parcels selected. Please select parcels before running this script.')
			return
		
		# Write the parcel information
		success = write_parcel_owner_info_json()
		
		if success:
			arcpy.AddMessage('Process completed successfully!')
		else:
			arcpy.AddError('Process failed. Check error messages above.')
			
	except Exception as e:
		arcpy.AddError('Error: {0}'.format(str(e)))
		arcpy.AddError('Make sure parcels are selected in a parcel layer.')
	
	finally:
		# Clean up
		if arcpy.Exists("parcel_lyr"):
			arcpy.Delete_management("parcel_lyr")

	arcpy.AddMessage('Launching Power PID Producer Python script...')
	pypath = 'C:/"Program Files"/Python312/python.exe'
	py_script = 'F:/Research Department/Code/RP3/M1_Power_PID_Producer_v02.py'

	# Create the command line to launch the Python script
	lauchCommandLine = '{0} "{1}"'.format(pypath, py_script)

	# Launch the Python script
	os.system(lauchCommandLine)

if __name__ == "__main__":
	main()