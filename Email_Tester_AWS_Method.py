# src/email_utils.py
from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import ClientError
import logging
import emailer


# Example usage
if __name__ == "__main__":
	# Test the email function
	subject = "Test Email from LAO Research Department"
	body = """
	<html>
		<body>
			<h2>Land Advisors Organization</h2>
			<p>This is a test email from the Research Department.</p>
			<p>If you received this email, your configuration is working correctly.</p>
		</body>
	</html>
	"""
	sender_email = "research@landadvisors.com"
	recipients = [
		"blandis@landadvisors.com",
	]
	
	# Send the test email
#  result = send_email_ses(subject, body, recipient)
	result = emailer.send_email_ses(subject, body, sender_email, recipients, cc=None, bcc=None, attachments=None)

	if result.get("success"):
		print(f"✅ Email sent successfully! Message ID: {result['message_id']}")
	else:
		print(f"❌ Failed to send email: {result['error']}")