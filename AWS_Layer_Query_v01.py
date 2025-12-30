from arcgis.gis import GIS
from arcgis.features import FeatureLayer

def print_transfer_fields():
	# Print all field names
	print("Available fields:")
	for field in fl.properties.fields:
		print(f"  {field['name']} ({field['type']})")
	exit()

# Connect to your ArcGIS Online or Portal
user = 'blandis'
pwd = 'Logmeintoarcmap5!'

gis = GIS("https://maps.landadvisors.com/portal", user, pwd, verify_cert=True)

# URL to the FATransfers feature layer
transfers_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_View_Main/MapServer/7"  # Layer ID 7

fl = FeatureLayer(transfers_url, gis)

# First, let's see what format the date is in
test_query = fl.query(
	where="County = 'Canyon_ID'",
	out_fields="CurrentSaleRecordingDate, CurrentSaleTransactionId",
	return_geometry=False,
	result_record_count=5
)

print("Sample date formats:")
for f in test_query.features:
	print(f"  {f.attributes['CurrentSaleRecordingDate']}")
