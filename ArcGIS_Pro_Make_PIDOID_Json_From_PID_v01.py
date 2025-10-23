from arcgis import GIS
from arcgis.features import FeatureLayer
import logging
import time
import requests
from typing import Optional, Union, Dict, List
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def setup_logging():
	"""Setup logging configuration for the script."""
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(levelname)s - %(message)s',
		handlers=[
			logging.FileHandler('lao_pid_query.log'),
			logging.StreamHandler()
		]
	)

def check_server_status(base_url: str, timeout: int = 10) -> bool:
	"""
	Check if the ArcGIS server is responding.
	
	Args:
		base_url (str): Base URL of the ArcGIS server
		timeout (int): Timeout in seconds
		
	Returns:
		bool: True if server is responsive, False otherwise
	"""
	try:
		response = requests.get(f"{base_url}/rest/info", timeout=timeout)
		return response.status_code == 200
	except Exception as e:
		logging.warning(f"Server status check failed: {str(e)}")
		return False

def create_resilient_session() -> requests.Session:
	"""
	Create a requests session with retry strategy.
	
	Returns:
		requests.Session: Session with retry configuration
	"""
	session = requests.Session()
	
	# Define retry strategy
	retry_strategy = Retry(
		total=3,
		status_forcelist=[429, 500, 502, 503, 504],
		method_whitelist=["HEAD", "GET", "OPTIONS"],
		backoff_factor=1
	)
	
	adapter = HTTPAdapter(max_retries=retry_strategy)
	session.mount("http://", adapter)
	session.mount("https://", adapter)
	
	return session

def query_owner_index_by_pid(
	pid: str, 
	gis_connection: GIS = None, 
	username: str = None, 
	password: str = None, 
	portal_url: str = None,
	retry_count: int = 3,
	retry_delay: float = 2.0
) -> Optional[int]:
	"""
	Query the OwnerIndex Feature Class to retrieve the objectid for a given PID with enhanced error handling.
	
	Args:
		pid (str): The Property ID to search for
		gis_connection (GIS, optional): Existing GIS connection. If None, creates new connection.
		username (str, optional): Username for authentication
		password (str, optional): Password for authentication  
		portal_url (str, optional): Portal URL (defaults to ArcGIS Online)
		retry_count (int): Number of times to retry on failure
		retry_delay (float): Seconds to wait between retries
		
	Returns:
		Optional[int]: The objectid of the matching record, or None if not found
		
	Raises:
		Exception: If there's an error connecting to or querying the feature service after all retries
	"""
	
	# Feature Service URL and layer index
	feature_service_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer"
	layer_index = 0  # OwnerIndex is Feature Class 0
	layer_url = f"{feature_service_url}/{layer_index}"
	
	# Alternative portal URLs to try
	portal_urls = [
		"https://maps.landadvisors.com/portal" # Fallback to ArcGIS Online
	]
	
	if portal_url:
		portal_urls.insert(0, portal_url)  # Try user-specified URL first
	
	last_exception = None
	
	for attempt in range(retry_count):
		logging.info(f"Attempt {attempt + 1} of {retry_count} for PID '{pid}'")
		
		# Check server status before attempting connection
		server_base = "https://maps.landadvisors.com/arcgis"
		if not check_server_status(server_base):
			logging.warning(f"Server at {server_base} appears to be down. Attempt {attempt + 1}")
			if attempt < retry_count - 1:
				time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
				continue
			else:
				raise Exception("LAO ArcGIS server is not responding. Please contact LAO IT support.")
		
		for portal_attempt, current_portal_url in enumerate(portal_urls):
			try:
				# Create GIS connection if not provided
				if gis_connection is None:
					if username and password:
						logging.info(f"Attempting connection to {current_portal_url}")
						gis = GIS(current_portal_url, username, password)
					else:
						# Try anonymous connection
						gis = GIS()
				else:
					gis = gis_connection
				
				# Create FeatureLayer object
				owner_index_layer = FeatureLayer(layer_url, gis=gis)
				
				# Create the where clause to filter by PID
				where_clause = f"pid = '{pid}'"
				
				# Query the layer
				feature_set = owner_index_layer.query(
					where=where_clause,
					out_fields=["objectid", "pid"],
					return_geometry=False
				)
				
				# Check if any features were returned
				if feature_set.features and len(feature_set.features) > 0:
					# Get the first (and should be only) matching record
					feature = feature_set.features[0]
					# Try both lowercase and uppercase field names
					objectid = feature.attributes.get('OBJECTID') or feature.attributes.get('objectid')
					
					logging.info(f"Found record for PID '{pid}': ObjectID = {objectid}")
					return objectid
				else:
					logging.warning(f"No record found for PID '{pid}'")
					return None
				
			except Exception as e:
				error_msg = str(e)
				last_exception = e
				
				if 'token' in error_msg.lower() or 'authentication' in error_msg.lower():
					logging.error(f"Authentication failed for {current_portal_url}: {error_msg}")
					if portal_attempt == len(portal_urls) - 1:  # Last portal URL
						raise Exception(f"Authentication required: Please verify credentials for LAO feature service.")
				elif '500' in error_msg or 'server error' in error_msg.lower():
					logging.error(f"Server error on attempt {attempt + 1}: {error_msg}")
					break  # Try next attempt after delay
				else:
					logging.error(f"Connection failed to {current_portal_url}: {error_msg}")
					continue  # Try next portal URL
		
		# Wait before next attempt if not the last one
		if attempt < retry_count - 1:
			delay = retry_delay * (attempt + 1)
			logging.info(f"Waiting {delay} seconds before retry...")
			time.sleep(delay)
	
	# All attempts failed
	if last_exception:
		raise Exception(f"Failed to query OwnerIndex after {retry_count} attempts: {str(last_exception)}")
	else:
		raise Exception(f"Failed to query OwnerIndex after {retry_count} attempts: Unknown error")

def query_owner_index_batch(
	pids: List[str], 
	gis_connection: GIS = None, 
	username: str = None, 
	password: str = None, 
	portal_url: str = None,
	batch_size: int = 50
) -> Dict[str, Optional[int]]:
	"""
	Query the OwnerIndex Feature Class for multiple PIDs at once with batch processing.
	
	Args:
		pids (List[str]): List of Property IDs to search for
		gis_connection (GIS, optional): Existing GIS connection. If None, creates new connection.
		username (str, optional): Username for authentication
		password (str, optional): Password for authentication
		portal_url (str, optional): Portal URL (defaults to ArcGIS Online)
		batch_size (int): Maximum number of PIDs to process in each batch
		
	Returns:
		Dict[str, Optional[int]]: Dictionary mapping PIDs to their objectids (None if not found)
	"""
	
	if not pids:
		return {}
	
	results = {}
	
	# Process PIDs in batches to avoid query size limits
	for i in range(0, len(pids), batch_size):
		batch_pids = pids[i:i + batch_size]
		logging.info(f"Processing batch {i//batch_size + 1}: PIDs {i+1} to {min(i+batch_size, len(pids))}")
		
		try:
			batch_results = _query_batch_internal(batch_pids, gis_connection, username, password, portal_url)
			results.update(batch_results)
		except Exception as e:
			logging.error(f"Batch processing failed for PIDs {i+1} to {min(i+batch_size, len(pids))}: {str(e)}")
			# Mark all PIDs in failed batch as None
			for pid in batch_pids:
				results[pid] = None
	
	return results

def _query_batch_internal(
	pids: List[str], 
	gis_connection: GIS = None, 
	username: str = None, 
	password: str = None, 
	portal_url: str = None
) -> Dict[str, Optional[int]]:
	"""Internal batch query function."""
	
	# Feature Service URL and layer index
	feature_service_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer"
	layer_index = 0
	layer_url = f"{feature_service_url}/{layer_index}"
	
	results = {}
	
	try:
		# Create GIS connection if not provided
		if gis_connection is None:
			if username and password:
				gis = create_authenticated_connection(portal_url, username, password)
			else:
				gis = GIS()
		else:
			gis = gis_connection
		
		# Create FeatureLayer object
		owner_index_layer = FeatureLayer(layer_url, gis=gis)
		
		# Initialize all PIDs as None (not found)
		for pid in pids:
			results[pid] = None
		
		# Create IN clause for multiple PIDs
		pid_list = "', '".join(pids)
		where_clause = f"pid IN ('{pid_list}')"
		
		# Query the layer for all matching records
		feature_set = owner_index_layer.query(
			where=where_clause,
			out_fields=["objectid", "pid"],
			return_geometry=False
		)
		
		# Process the results
		if feature_set.features:
			for feature in feature_set.features:
				found_pid = feature.attributes['pid']
				# Try both lowercase and uppercase field names
				objectid = feature.attributes.get('OBJECTID') or feature.attributes.get('objectid')
				results[found_pid] = objectid
				
		found_count = sum(1 for v in results.values() if v is not None)
		logging.info(f"Batch query completed for {len(pids)} PIDs. Found {found_count} matches.")
		
	except Exception as e:
		error_msg = str(e)
		if 'token' in error_msg.lower():
			logging.error("Authentication required for batch query.")
			raise Exception("Authentication required: Please provide valid credentials to access the LAO feature service.")
		else:
			logging.error(f"Error in batch query: {error_msg}")
			raise Exception(f"Failed to batch query OwnerIndex: {error_msg}")
	
	return results

def create_authenticated_connection(portal_url: str = None, username: str = None, password: str = None) -> GIS:
	"""
	Create an authenticated GIS connection with multiple fallback options.
	
	Args:
		portal_url (str, optional): URL of your ArcGIS Portal or ArcGIS Online
		username (str, optional): Username for authentication
		password (str, optional): Password for authentication
		
	Returns:
		GIS: Authenticated GIS connection object
	"""
	
	portal_urls = []
	
	if portal_url:
		portal_urls.append(portal_url)
	
	# Add LAO-specific URLs
	portal_urls.extend([
				"https://maps.landadvisors.com/portal" # Fallback to ArcGIS Online
				])
	
	last_error = None
	
	for url in portal_urls:
		try:
			if username and password:
				gis = GIS(url, username, password)
				logging.info(f"Successfully connected to {url} as {username}")
				return gis
			else:
				gis = GIS(url)
				logging.info(f"Successfully connected to {url} (anonymous)")
				return gis
				
		except Exception as e:
			last_error = e
			logging.warning(f"Failed to connect to {url}: {str(e)}")
			continue
	
	raise Exception(f"Failed to establish connection to any portal. Last error: {str(last_error)}")

def test_server_connectivity():
	"""Test connectivity to LAO servers and report status."""
	
	setup_logging()
	
	servers_to_test = [
		"https://maps.landadvisors.com/portal"]
	
	print("=== LAO Server Connectivity Test ===")
	
	for server in servers_to_test:
		print(f"\nTesting {server}...")
		if check_server_status(server):
			print(f"✓ {server} is responding")
		else:
			print(f"✗ {server} is not responding or experiencing issues")
	
	print("\n=== Direct REST API Test ===")
	feature_service_url = "https://maps.landadvisors.com/arcgis/rest/services/Research_Edit_Main/FeatureServer"
	
	try:
		response = requests.get(f"{feature_service_url}?f=json", timeout=10)
		if response.status_code == 200:
			print(f"✓ Feature service is accessible")
			print(f"Response: {response.json().get('serviceDescription', 'No description')}")
		else:
			print(f"✗ Feature service returned status code: {response.status_code}")
	except Exception as e:
		print(f"✗ Feature service test failed: {str(e)}")

def test_with_fallback_methods():
	"""Test PID query using multiple fallback methods."""
	
	setup_logging()
	
	# Test credentials from the original script
	USERNAME = 'blandis'
	PASSWORD = 'Logmeintoarcmap5!'
	TEST_PID = "AZMA74771"
	
	print("=== LAO PID Query Test with Fallbacks ===")
	print(f"Testing PID: {TEST_PID}")
	print("Note: This will try multiple connection methods and servers.")
	print()
	
	try:
		# Method 1: Enhanced query with retries
		print("Method 1: Enhanced query with retry logic...")
		objectid = query_owner_index_by_pid(
			pid=TEST_PID,
			username=USERNAME,
			password=PASSWORD,
			retry_count=2,
			retry_delay=1.0
		)
		
		if objectid:
			print(f"✓ Success! PID '{TEST_PID}' has ObjectID = {objectid}")
			return True
		else:
			print(f"✗ No record found for PID '{TEST_PID}'")
			
	except Exception as e:
		print(f"✗ Enhanced query failed: {str(e)}")
		print("This suggests the LAO ArcGIS server is experiencing issues.")
		print()
		print("Recommended actions:")
		print("1. Contact LAO IT support about server issues")
		print("2. Try again later when server is stable")
		print("3. Verify your credentials are still valid")
		print("4. Check if there are alternative ways to access the data")
		return False
	
	return True

if __name__ == "__main__":
	# First test server connectivity
	test_server_connectivity()
	print("\n" + "="*50 + "\n")
	
	# Then test the PID query with fallbacks
	test_with_fallback_methods()