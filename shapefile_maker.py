import shapefile
from shapely.geometry import Point, LineString, Polygon
import os

def create_sample_shapefile(output_dir=None):
	"""
	Creates a sample ESRI shapefile with points, lines, and polygons
	representing property data for Land Advisors Organization
	"""
	
	# Set output directory
	if output_dir:
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		output_path = os.path.join(output_dir, 'sample_properties')
	else:
		output_path = 'sample_properties'
	
	print(f"Creating shapefile at: {os.path.abspath(output_path)}")
	
	# Create a new shapefile writer
	w = shapefile.Writer(output_path, shapeType=shapefile.POLYGON)
	
	# Define the fields (attributes) for the shapefile
	w.field('PID', 'C', size=20)  # Property ID
	w.field('DEAL_NAME', 'C', size=100)  # Deal Name
	w.field('ACRES', 'N', decimal=2)  # Acres
	w.field('SALE_PRICE', 'N', decimal=2)  # Sale Price
	w.field('COUNTY', 'C', size=50)  # County
	w.field('STATE', 'C', size=2)  # State
	w.field('CLASSIFIC', 'C', size=50)  # Classification
	w.field('LOT_TYPE', 'C', size=50)  # Lot Type
	w.field('STAGE_NAME', 'C', size=50)  # Stage Name
	w.field('MARKET', 'C', size=50)  # Market
	
	# Sample property polygons (coordinates in longitude, latitude)
	properties = [
		{
			'coords': [
				(-122.4194, 37.7749),
				(-122.4094, 37.7749),
				(-122.4094, 37.7849),
				(-122.4194, 37.7849),
				(-122.4194, 37.7749)  # Close the polygon
			],
			'attributes': {
				'PID': 'CA-SF-001',
				'DEAL_NAME': 'Downtown SF Development',
				'ACRES': 5.25,
				'SALE_PRICE': 2500000.00,
				'COUNTY': 'San Francisco',
				'STATE': 'CA',
				'CLASSIFIC': 'Residential',
				'LOT_TYPE': 'Raw Acreage',
				'STAGE_NAME': 'Signed Listing',
				'MARKET': 'San Francisco Bay Area'
			}
		},
		{
			'coords': [
				(-122.3994, 37.7949),
				(-122.3894, 37.7949),
				(-122.3894, 37.8049),
				(-122.3994, 37.8049),
				(-122.3994, 37.7949)
			],
			'attributes': {
				'PID': 'CA-SF-002',
				'DEAL_NAME': 'North Bay Apartments',
				'ACRES': 12.75,
				'SALE_PRICE': 8750000.00,
				'COUNTY': 'San Francisco',
				'STATE': 'CA',
				'CLASSIFIC': 'Apartment Traditional',
				'LOT_TYPE': 'Platted and Engineered',
				'STAGE_NAME': 'Escrow',
				'MARKET': 'San Francisco Bay Area'
			}
		},
		{
			'coords': [
				(-122.3794, 37.7649),
				(-122.3694, 37.7649),
				(-122.3694, 37.7749),
				(-122.3794, 37.7749),
				(-122.3794, 37.7649)
			],
			'attributes': {
				'PID': 'CA-SF-003',
				'DEAL_NAME': 'Mission District Retail',
				'ACRES': 3.50,
				'SALE_PRICE': 1850000.00,
				'COUNTY': 'San Francisco',
				'STATE': 'CA',
				'CLASSIFIC': 'Retail',
				'LOT_TYPE': 'Covered Land',
				'STAGE_NAME': 'Closed',
				'MARKET': 'San Francisco Bay Area'
			}
		}
	]
	
	# Add each property to the shapefile
	for prop in properties:
		# Create polygon geometry
		w.poly([prop['coords']])
		
		# Add attribute record
		w.record(
			prop['attributes']['PID'],
			prop['attributes']['DEAL_NAME'],
			prop['attributes']['ACRES'],
			prop['attributes']['SALE_PRICE'],
			prop['attributes']['COUNTY'],
			prop['attributes']['STATE'],
			prop['attributes']['CLASSIFIC'],
			prop['attributes']['LOT_TYPE'],
			prop['attributes']['STAGE_NAME'],
			prop['attributes']['MARKET']
		)
	
	# Close the shapefile writer
	w.close()
	
	print("Shapefile created successfully!")
	print("Files created:")
	print(f"- {output_path}.shp (geometry)")
	print(f"- {output_path}.shx (index)")
	print(f"- {output_path}.dbf (attributes)")
	
	return output_path

def create_point_shapefile():
	"""
	Creates a point shapefile for property locations
	"""
	w = shapefile.Writer('property_points', shapeType=shapefile.POINT)
	
	# Define fields
	w.field('PID', 'C', size=20)
	w.field('DEAL_NAME', 'C', size=100)
	w.field('ACRES', 'N', decimal=2)
	w.field('COUNTY', 'C', size=50)
	w.field('STATE', 'C', size=2)
	
	# Sample points
	points = [
		(-122.4194, 37.7749, 'CA-SF-001', 'Downtown SF Development', 5.25, 'San Francisco', 'CA'),
		(-122.3994, 37.7949, 'CA-SF-002', 'North Bay Apartments', 12.75, 'San Francisco', 'CA'),
		(-122.3794, 37.7649, 'CA-SF-003', 'Mission District Retail', 3.50, 'San Francisco', 'CA')
	]
	
	for lon, lat, pid, name, acres, county, state in points:
		w.point(lon, lat)
		w.record(pid, name, acres, county, state)
	
	w.close()
	print("Point shapefile created successfully!")

def create_line_shapefile():
	"""
	Creates a line shapefile for property boundaries or roads
	"""
	w = shapefile.Writer('property_lines', shapeType=shapefile.POLYLINE)
	
	# Define fields
	w.field('LINE_ID', 'C', size=20)
	w.field('LINE_TYPE', 'C', size=50)
	w.field('LENGTH_FT', 'N', decimal=2)
	
	# Sample lines
	lines = [
		{
			'coords': [(-122.4194, 37.7749), (-122.4094, 37.7749)],
			'id': 'LINE001',
			'type': 'Property Boundary',
			'length': 850.5
		},
		{
			'coords': [(-122.4094, 37.7749), (-122.4094, 37.7849)],
			'id': 'LINE002',
			'type': 'Property Boundary',
			'length': 1110.2
		}
	]
	
	for line in lines:
		w.line([line['coords']])
		w.record(line['id'], line['type'], line['length'])
	
	w.close()
	print("Line shapefile created successfully!")

def read_shapefile(filename):
	"""
	Reads and displays information from a shapefile
	"""
	try:
		sf = shapefile.Reader(filename)
		
		print(f"\nShapefile: {filename}")
		print(f"Shape Type: {sf.shapeType}")
		print(f"Number of shapes: {len(sf.shapes())}")
		print(f"Bounding box: {sf.bbox}")
		
		# Display field information
		print("\nFields:")
		for field in sf.fields[1:]:  # Skip deletion flag field
			print(f"  {field[0]}: {field[1]} ({field[2]}.{field[3]})")
		
		# Display first few records
		print("\nFirst 3 records:")
		for i, record in enumerate(sf.records()[:3]):
			print(f"  Record {i+1}: {record}")
			
	except Exception as e:
		print(f"Error reading shapefile: {e}")

if __name__ == "__main__":
	# Install required packages first:
	# pip install pyshp shapely
	
	print("Creating sample shapefiles...")
	print(f"Current working directory: {os.getcwd()}")
	
	# Option 1: Save to current directory (default)
	create_sample_shapefile()
	
	# Option 2: Save to specific directory
	create_sample_shapefile("C:/Users/Public/Public MapFiles")  # Windows
	# create_sample_shapefile("/Users/username/GIS_Data")  # Mac
	# create_sample_shapefile("./output")  # Relative path
	
	create_point_shapefile()   # Points
	create_line_shapefile()    # Lines
	
	# Read back the created shapefiles
	print("\n" + "="*50)
	print("Reading created shapefiles:")
	read_shapefile("sample_properties")