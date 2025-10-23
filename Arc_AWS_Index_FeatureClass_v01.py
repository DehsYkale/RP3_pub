import arcpy

arcpy.env.workspace = r'C:\Users\Public\Public Mapfiles\Parcels.gdb'

fclist = arcpy.ListFeatureClasses()
for fc in fclist:
	print(fc)
	arcpy.management.AddIndex(fc, ['apn', 'altapn', 'owner', 'mailstreet', 'acres', 'saledate', 'saleprice'], 'SearchIndex', 'NON_UNIQUE', 'NON_ASCENDING')
