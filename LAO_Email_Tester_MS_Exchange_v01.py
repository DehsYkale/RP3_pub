

import fun_text_date as td
import emailer

td.banner('LAO Email Tester MS Exchange v01')

subject = "Excel Attachment Evil Test Email from Bill Through AWS SES"
body = """
<html>
<body>
<h1>Hello, this is a test email with an Excel attachment!</h1>
<p>This email is sent using AWS SES.</p>
</body>
</html>
"""

print(' Select email sender')
print('\n  1) LAO Research <research@landadvisors.com>')
print('\n  2) Bill Landis <blandis@landadvisors.com>')
ui = td.uInput('\n Select > ')
if ui == '1':
	sender_email = "LAO Research <research@landadvisors.com>"
elif ui == '2':
	sender_email = "Bill Landis <blandis@landadvisors.com>"

# sender_email = "LAO Research <research@landadvisors.com>"
# sender_email = "Bill Landis <blandis@landadvisors.com>"
recipients = ['Bill Landis <blandis@landadvisors.com>']

filename = 'F:/Research Department/Lot Comps Components/DFW_Land_Lot_Report_2025-09-07.xlsx'
attachments = [filename]

emailer.send_email_ses(subject, body, sender_email, recipients=recipients, cc=None, bcc=None, attachments=attachments)