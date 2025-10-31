# src/email_utils.py
from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import ClientError
import fun_text_date as td
import lao
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)  # Only show warnings and errors

def create_mime_message(sender, destination, subject, body, attachments):
	lao.print_function_name('emailer def create_mime_message')
	"""
	Create a MIME message with attachments
	
	Args:
		sender (str): Formatted sender string
		destination (dict): Dictionary with ToAddresses, CcAddresses, BccAddresses
		subject (str): Email subject
		body (str): HTML body content
		attachments (str or list): Path(s) to attachment file(s)
	
	Returns:
		MIMEMultipart: MIME message object
	"""
	# Create MIME container
	msg = MIMEMultipart('mixed')
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = ', '.join(destination.get('ToAddresses', []))
	
	if destination.get('CcAddresses'):
		msg['Cc'] = ', '.join(destination['CcAddresses'])
	
	# Create body part
	msg_body = MIMEMultipart('alternative')
	
	# Add HTML body
	html_part = MIMEText(body, 'html', 'utf-8')
	msg_body.attach(html_part)
	
	# Add text version (strip HTML tags for simple text version)
	import re
	text_content = re.sub('<[^<]+?>', '', body)
	text_part = MIMEText(text_content, 'plain', 'utf-8')
	msg_body.attach(text_part)
	
	msg.attach(msg_body)
	
	# Handle attachments
	if isinstance(attachments, str):
		attachments = [attachments]
	
	for file_path in attachments:
		if not os.path.isfile(file_path):
			logger.warning(f"Attachment file not found: {file_path}")
			continue
		
		# Get file name
		file_name = os.path.basename(file_path)
		
		# Determine MIME type based on file extension
		if file_path.lower().endswith(('.xlsx', '.xls')):
			# Excel files
			with open(file_path, 'rb') as f:
				attach = MIMEApplication(f.read(), _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
				attach.add_header('Content-Disposition', 'attachment', filename=file_name)
				msg.attach(attach)
		elif file_path.lower().endswith('.csv'):
			# CSV files
			with open(file_path, 'rb') as f:
				attach = MIMEApplication(f.read(), _subtype='csv')
				attach.add_header('Content-Disposition', 'attachment', filename=file_name)
				msg.attach(attach)
		elif file_path.lower().endswith('.pdf'):
			# PDF files
			with open(file_path, 'rb') as f:
				attach = MIMEApplication(f.read(), _subtype='pdf')
				attach.add_header('Content-Disposition', 'attachment', filename=file_name)
				msg.attach(attach)
		else:
			# Generic binary attachment
			with open(file_path, 'rb') as f:
				attach = MIMEBase('application', 'octet-stream')
				attach.set_payload(f.read())
				encoders.encode_base64(attach)
				attach.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
				msg.attach(attach)
		
		# logger.info(f"Attached file: {file_name}")
	
	return msg

def send_email_ses(subject, body, sender_email, recipients=None, cc=None, bcc=None, attachments=None):
	lao.print_function_name('emailer def send_email_ses')
	"""
	Send an email using AWS SES with optional attachments
	
	Args:
		subject (str): Email subject line
		body (str): HTML body content
		recipients (str or list): Single recipient email or list of recipient emails
		cc (str or list, optional): CC recipient(s)
		bcc (str or list, optional): BCC recipient(s)
		attachments (str or list, optional): Path(s) to file(s) to attach
		sender_email (str): Sender email (must be verified in SES)

	
	Returns:
		dict: Response from SES or error information
	"""
	# Get credentials from environment variables
	# FIX: Use environment variable NAMES, not the actual values
	aws_access_key_id = os.getenv('SES_ACCESS_KEY')  # Changed from the actual key
	aws_secret_access_key = os.getenv('SES_SECRET_ACCESS_KEY')  # Changed from the actual secret
	aws_region = os.getenv('SES_REGION', 'us-east-1')  # Default to us-east-1
	
	if not all([aws_access_key_id, aws_secret_access_key]):
		error_msg = "AWS credentials not found in environment variables"
		logger.error(error_msg)
		return {"error": error_msg}
	
	# print(verify_email_identity(sender_email))

	try:
		# Create SES client
		client = boto3.client(
			'ses',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			region_name=aws_region
		)
		
		# Prepare destination with multiple recipients support
		destination = {}
		
		# Handle TO recipients (can be string or list)
		if recipients:
			if isinstance(recipients, str):
				destination['ToAddresses'] = [recipients]
			elif isinstance(recipients, list):
				destination['ToAddresses'] = recipients
			else:
				error_msg = "Recipients must be a string or list of email addresses"
				logger.error(error_msg)
				return {"error": error_msg}
		
		# Handle CC recipients (can be string or list)
		if cc:
			if isinstance(cc, str):
				destination['CcAddresses'] = [cc]
			elif isinstance(cc, list):
				destination['CcAddresses'] = cc
		
		# Handle BCC recipients (can be string or list)
		if bcc:
			if isinstance(bcc, str):
				destination['BccAddresses'] = [bcc]
			elif isinstance(bcc, list):
				destination['BccAddresses'] = bcc
		
		# Format sender with display name
		source = sender_email
		
		# Check if we have attachments
		if attachments:
			# Use MIME for emails with attachments
			msg = create_mime_message(
				source, destination, subject, body, attachments
			)
			
			# Send raw email
			response = client.send_raw_email(
				Source=source,
				Destinations=(
					destination.get('ToAddresses', []) +
					destination.get('CcAddresses', []) +
					destination.get('BccAddresses', [])
				),
				RawMessage={'Data': msg.as_string()}
			)
		else:
			# Send regular email without attachments
			response = client.send_email(
				Destination=destination,
				Message={
					'Body': {
						'Html': {
							'Charset': "UTF-8", 
							'Data': body
						},
						'Text': {
							'Charset': "UTF-8",
							'Data': body  # You might want to strip HTML for text version
						}
					},
					'Subject': {
						'Charset': "UTF-8", 
						'Data': subject
					}
				},
				Source=source
			)
		
		# logger.info(f"Email sent successfully! Message ID: {response['MessageId']}")
		td.colorText(f"\n Email sent successfully!", 'GREEN')
		return {"success": True, "message_id": response['MessageId']}
		
	except ClientError as e:
		error_code = e.response['Error']['Code']
		error_message = e.response['Error']['Message']
		# logger.error(f"SES Error ({error_code}): {error_message}")
		# return {"error": f"{error_code}: {error_message}"}
	except Exception as e:
		logger.error(f"Unexpected error: {str(e)}")
		return {"error": f"Unexpected error: {str(e)}"}

def verify_email_identity(email_address):
	lao.print_function_name('emailer def verify_email_identity')
	"""
	Verify an email identity in SES (required before sending)
	
	Args:
		email_address (str): Email address to verify
	
	Returns:
		dict: Verification response or error
	"""
	aws_access_key_id = os.getenv('SES_ACCESS_KEY')  # Fixed
	aws_secret_access_key = os.getenv('SES_SECRET_ACCESS_KEY')  # Fixed
	aws_region = os.getenv('SES_REGION', 'us-east-1')
	
	try:
		client = boto3.client(
			'ses',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			region_name=aws_region
		)
		
		response = client.verify_email_identity(EmailAddress=email_address)
		logger.info(f"Verification email sent to: {email_address}")
		return {"success": True, "message": f"Verification email sent to {email_address}"}
		
	except ClientError as e:
		error_message = e.response['Error']['Message']
		logger.error(f"Verification failed: {error_message}")
		return {"error": error_message}

def check_sending_quota():
	lao.print_function_name('emailer def check_sending_quota')
	"""
	Check SES sending quota and usage
	
	Returns:
		dict: Quota information or error
	"""
	aws_access_key_id = os.getenv('SES_ACCESS_KEY')  # Fixed
	aws_secret_access_key = os.getenv('SES_SECRET_ACCESS_KEY')  # Fixed
	aws_region = os.getenv('SES_REGION', 'us-east-1')
	
	try:
		client = boto3.client(
			'ses',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			region_name=aws_region
		)
		
		quota = client.get_send_quota()
		statistics = client.get_send_statistics()
		
		return {
			"max_24_hour": quota['Max24HourSend'],
			"max_send_rate": quota['MaxSendRate'],
			"sent_last_24_hours": quota['SentLast24Hours'],
			"send_statistics": statistics['SendDataPoints']
		}
		
	except ClientError as e:
		return {"error": e.response['Error']['Message']}