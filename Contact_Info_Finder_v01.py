import lao
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import csv
import re
import fun_text_date as td

def extract_contact_info(url):
	# Send a GET request to the URL
	response = requests.get(url)
	
	# Parse HTML content
	soup = BeautifulSoup(response.content, 'html.parser')
	
	# Initialize lists to store contact information
	names = []
	addresses = []
	phone_numbers = []
	emails = []
	
	# Find all elements that might contain contact information
	contact_elements = soup.find_all(['p', 'a', 'span', 'div'])
	
	# Iterate over each element and extract contact information
	for element in contact_elements:
		text = element.get_text()
		print(text)
		
		# Regular expressions to find emails and phone numbers
		email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
		phone_pattern = r'\b(?:\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
		
		# Extract names, addresses, phone numbers, and emails
		names.extend(re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text))
		addresses.extend(re.findall(r'\b\d{1,5}\s\w+\s\w+\b', text))
		phone_numbers.extend(re.findall(phone_pattern, text))
		emails.extend(re.findall(email_pattern, text))
		pprint(names)
		pprint(emails)
		ui = td.uInput('\n Continue [00]... > ')
		if ui == '00':
			exit('\n Terminating program...')
	
	# Remove duplicates
	names = list(set(names))
	addresses = list(set(addresses))
	phone_numbers = list(set(phone_numbers))
	emails = list(set(emails))
	
	return names, addresses, phone_numbers, emails

def save_to_csv(data, filename='C:/TEMP/contact_info.csv'):
	with open(filename, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['Name', 'Address', 'Phone Number', 'Email'])
		writer.writerows(data)
	lao.openFile(filename)

def main():
	url = input("Enter the homepage URL of the website: ")
	if 'https' not in url:
		url = 'https://' + url
	names, addresses, phone_numbers, emails = extract_contact_info(url)
	contact_info = list(zip(names, addresses, phone_numbers, emails))
	save_to_csv(contact_info)
	print("Contact information saved to contact_info.csv")

if __name__ == "__main__":
	main()
