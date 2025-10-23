
import arcpy


lyr = arcpy.mapping.ListLayers(mxd, 'OwnerIndex', df)[0]
arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
whereclause = "initials is null"
arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereclause)
count = int(arcpy.GetCount_management(lyr).getOutput(0))
print('Count =', count)
# pid_exists = True
# if count == 0:
# 	arcpy.AddError('\n PID {0} is not in OwnerIndex.\n\n Program terminated...\n\n'.format(PID))
# 	pid_exists = False
# else:
# 	# Get County name from PID
# 	county = ''.join([i for i in PID[2:] if not i.isdigit()])
# 	# Turn off all parcel layers excpt the needed county
# 	set_parcel_layers_visibility(arcpy, df, mxd, county)
# 	# df.zoomToSelectedFeatures()
# 	df.extent = lyr.getSelectedExtent()
# 	if df.scale < 4000.00:
# 			df.scale = 6000.00
# 	else:
# 		df.scale = df.scale * 1.5
# 	if clearSelection:
# 		arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
# return pid_exists