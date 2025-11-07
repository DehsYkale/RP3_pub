# Chat GPT AI Functions

from dotenv import load_dotenv
import json
import lao
import pyperclip
import requests
import os
from openai import OpenAI
from pprint import pprint

def get_ai_message(role_system=None, role_user=None):

	# Vizzda debt role system
	if role_system == 'VIZZDA':
		role_system = {"role": "system", "content": "You are a real estate expert skilled in collecting specific real estate information from provided blocks of text. The blocks are separateded by '::'. The first part of the block in is brackes which is the block ID. The information you collect includes 6 elements.  Return the resulsts as a json file as a dictionary of dictionaries readable by python json.loads function.  Use the block ID as key for each dictionary.  If an element cannont be determined incldue the key as a blank value. The elements are the following: the date of the transaction which will be the only date formated text in the block (key name 'Loan Date'), the amount of the sale (key name 'Last Sale Amount'), the company that purchased the real estate (key name 'Owner Entity'), the person to contact at the company or who is assoicated with the company (key name 'Owner Person'), if there is a loan the loan amount (key name 'Loan Amount') and the lender (key name 'Lender')."}
	elif role_system == 'COMPANY WITH ADDRESS':
		#role_system = {"role": "system", "content": "You are an expert researcher who is skilled at locating a company and finding information about the company.  You will be provided with a company name and address. You will need to find the company website and locate the contact information for the company.  The contact information will include the company address, phone number, website, persons and email addresses.  Return the results as a json file as a dictionary of dictionaries readable by python json.loads function.  Use the company name as key for each dictionary.  If the information cannot be found include the key as a blank value."}
		role_system = {"role": "system", "content": "You are an expert researcher who is skilled at locating a company and finding information about the company.  You will be provided with a company name and address. Do they have a website, phone number, associated persons and associated emails? Return the results as a json file as a dictionary of dictionaries readable by python json.loads function.  Use the company name as key for each dictionary.  If the information cannot be found include the key as a blank value."}
	elif role_system is not None:
		role_system = {"role": "system", "content": role_system}
	
	if role_user is not None:
		role_user = {"role": "user", "content": role_user}
	
	# Builded the message
	if role_system is not None and role_user is not None:
		message = [role_system, role_user]
	elif role_system is not None and role_user is None:
		message = [role_system]
	elif role_system is None and role_user is not None:
		message = [role_user]
	
	return message


def copy_ai_prompt_to_clipboard(dAcc):
	"""
	Reads the AI prompt text file and copies its content to the clipboard.
	
	Returns:
		bool: True if successful, False if an error occurred
	"""
	file_path = r"F:\Research Department\Code\Databases\Find Company Owner AI Prompt v01.txt"
	
	try:
		# Check if file exists
		if not os.path.exists(file_path):
			print(f"Error: File not found at {file_path}")
			return False
		
		# Read the file content
		with open(file_path, 'r', encoding='utf-8') as file:
			content = file.read()
		
		# Copy to clipboard
		pyperclip.copy(content)
		
		print(f"Successfully copied AI prompt to clipboard!")
		print(f"Content length: {len(content)} characters")
		
		return True
		
	except FileNotFoundError:
		print(f"Error: File not found at {file_path}")
		return False
	except PermissionError:
		print(f"Error: Permission denied accessing {file_path}")
		return False
	except UnicodeDecodeError:
		print("Error: Unable to decode file. Trying with different encoding...")
		try:
			with open(file_path, 'r', encoding='latin-1') as file:
				content = file.read()
			pyperclip.copy(content)
			print("Successfully copied AI prompt to clipboard using latin-1 encoding!")
			return True
		except Exception as e:
			print(f"Error reading file with alternate encoding: {e}")
			return False
	except Exception as e:
		print(f"Unexpected error: {e}")
		return False

# Ask Kablewy AI
def ask_kablewy_ai(payload):
	load_dotenv()
	ORG_ID = os.getenv("KABLEWY_ORG_ID")
	USER_ID = os.getenv("KABLEWY_USER_ID")
	API_KEY = os.getenv("KABLEWY_API_KEY")
	BASE = f"https://kablewy.ai/v1/mcp-jsonrpc/{ORG_ID}/users/{USER_ID}"
 
	headers = {
	"Authorization": f"Bearer {API_KEY}",
	"Content-Type": "application/json",
	"Accept": "application/json"
	}
	resp = requests.post(f"{BASE}/mcp/jsonrpc", headers=headers, json=payload)
	resp.raise_for_status()
	return resp.json()