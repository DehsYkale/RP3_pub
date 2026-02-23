"""
USPS Address Validation Script
Validates addresses using the USPS Addresses API v3
"""

import requests
from dotenv import load_dotenv
import os

load_dotenv()

USPS_CUSTOMER_KEY = os.getenv("USPS_CUSTOMER_KEY")
USPS_CUSTOMER_SECRET = os.getenv("USPS_CUSTOMER_SECRET")

# Debug: Check if credentials loaded
print(f"Key loaded: {bool(USPS_CUSTOMER_KEY)} ({USPS_CUSTOMER_KEY[:8] if USPS_CUSTOMER_KEY else 'None'}...)")
print(f"Secret loaded: {bool(USPS_CUSTOMER_SECRET)} ({USPS_CUSTOMER_SECRET[:4] if USPS_CUSTOMER_SECRET else 'None'}...)")



def get_access_token():
	"""Get OAuth 2.0 access token from USPS"""
	auth_url = "https://api.usps.com/oauth2/v3/token"
	auth_data = {
		"grant_type": "client_credentials",
		"client_id": USPS_CUSTOMER_KEY,
		"client_secret": USPS_CUSTOMER_SECRET
	}
	response = requests.post(auth_url, data=auth_data)
	
	# Debug: print full response if token not found
	data = response.json()
	if "access_token" not in data:
		print(f"Auth failed. Status: {response.status_code}")
		print(f"Response: {data}")
		raise SystemExit("Failed to get access token")
	
	return data["access_token"]


def validate_address(token, street, secondary, city, state, zip_code):
	"""Validate an address using USPS API"""
	headers = {
		"Authorization": f"Bearer {token}",
		"Content-Type": "application/json"
	}
	
	params = {
		"streetAddress": street,
		"city": city,
		"state": state,
		"ZIPCode": zip_code
	}
	
	if secondary:
		params["secondaryAddress"] = secondary
	
	url = "https://api.usps.com/addresses/v3/address"
	response = requests.get(url, headers=headers, params=params)
	return response.json()


def main():
	print("USPS Address Validation")
	print("-" * 40)
	
	# Get address from user
	street = input("Street Address: ")
	secondary = input("Secondary Address (Suite, Apt, etc. - press Enter to skip): ")
	city = input("City: ")
	state = input("State (2-letter abbreviation): ")
	zip_code = input("ZIP Code: ")
	
	print("\nValidating address...")
	
	# Get token and validate
	token = get_access_token()
	result = validate_address(token, street, secondary, city, state, zip_code)
	
	print("\nUSPS Response:")
	print("-" * 40)
	
	# Pretty print the response
	import json
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
