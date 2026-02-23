import fun_login
import fun_text_date as td
import bb

def main():
	# Get user input
	old_advisor = td.uInput('\n  Enter the Advisor name to REMOVE:  > ').strip()
	new_advisor = td.uInput('\n  Enter the Advisor name to ADD (replacement):  > ').strip()
	confirm_each_edit = td.uInput('\n  Confirm each edit? [0/1/00] > ')
	if confirm_each_edit == '00':
		print("Terminated by user.")
		return
	elif confirm_each_edit == '1':
		confirm_each_edit = True
	else:
		confirm_each_edit = False
	
	if not old_advisor or not new_advisor:
		print("Both names are required.")
		return
	
	# Login to TerraForce
	service = fun_login.TerraForce()
	
	# Query Accounts where Top100__c contains the old advisor name
	where_clause = f"Top100__c INCLUDES ('{old_advisor}')"
	
	print(f"\nSearching for Accounts with '{old_advisor}' in Top100__c...")
	results = bb.tf_query_3(service, 'Person', where_clause)
	
	if not results:
		print(f"No records found with '{old_advisor}' in Top100__c.")
		return
	
	print(f"\nFound {len(results)} record(s).\n")
	
	# Process each record
	for record in results:
		record_id = record['Id']
		name = record['Name']
		current_top100 = record.get('Top100__c', '') or ''
		
		# Parse current advisors (semicolon-delimited multipicklist)
		current_list = [a.strip() for a in current_top100.split(';') if a.strip()]
		
		# Build new list
		new_list = []
		for advisor in current_list:
			if old_advisor.lower() not in advisor.lower():
				new_list.append(advisor)
		
		# Add new advisor if not already present
		new_advisor_exists = any(new_advisor.lower() in a.lower() for a in new_list)
		if not new_advisor_exists:
			new_list.append(new_advisor)
		
		new_top100 = ';'.join(new_list)
		
		# Display changes
		print("=" * 60)
		print(f"Account: {name}")
		print(f"ID: {record_id}")
		print(f"\nCURRENT Top100__c:")
		for i, adv in enumerate(current_list, 1):
			print(f"  {i}. {adv}")
		print(f"\nPROPOSED Top100__c:")
		for i, adv in enumerate(new_list, 1):
			print(f"  {i}. {adv}")
		
		if new_advisor_exists:
			print(f"\n  (Note: '{new_advisor}' already exists, only removing '{old_advisor}')")
		
		# Confirm
		if confirm_each_edit:
			choice = input("\nUpdate this record? [0/1/00]: ").strip()
		else:
			choice = '1'
		
		if choice == '00':
			print("Terminated by user.")
			return
		elif choice == '1':
			dup = {'Id': record_id, 'Top100__c': new_top100, 'type': 'Account'}
			bb.tf_update_3(service, dup)
			print(f"✓ Updated {name}")
		else:
			print(f"Skipped {name}")
		
		print()
	
	print("Done.")

if __name__ == "__main__":
	main()