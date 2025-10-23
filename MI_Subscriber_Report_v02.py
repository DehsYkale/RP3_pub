# Makes an Excel report of Market Insights subscribers

import bb
import datetime
import fun_login
import lao
import mc
import pandas as pd
from pprint import pprint
import fun_text_date as td
import xlwings as xw
import xxl
# from operator import itemgetter

# Select the MailChimp list to report on
def selectMCList():
	lmenu = []
	td.banner('MailChimp MI Subscriber Report v02 Select List')
	# Make list of MC Audiences
	for lst in dMCLists['lists']:
		listname = lst['name']
		if listname in skipLists:
			continue
		lmenu.append(listname)
	lmenu.sort()
	# Print menu
	index = 1
	for row in lmenu:
		print(' {0:2}) {1}'.format(index, row))
		index += 1
	print(' {0:2}) All'.format(index))
	lmenu.append('All')
	print('\n 00) Quit')
	# User select form menu
	ui = int(td.uInput('\n Select List > ')) - 1
	if ui < 1:
		exit('\n Terminating program...')
	selection = lmenu[ui]
	return selection

# Query MailChimp for campaign data
def assembleCampaignData():
	print('\n Getting Campaigns...')
	lCampaignsNoHeader = []
	lCampsInList = mc.getCampaignsInList(client, mcListID)

	# Cycle all through campaigns
	for CID in lCampsInList:
		dCampResults = mc.getCampReport(client, CID)
		campTitle = dCampResults['campaign_title']
		if campTitle == '':
			continue
		sendDate = (dCampResults['send_time'])
		hour = str(int(sendDate[11:13]) - 7)
		if int(hour) < 0:
			hour = 12 + int(hour)
		sendDate = '{0}{1}{2}'.format(sendDate[:11], hour, sendDate[13:19].replace('-', '0'))
		# print campTitle
		# print sendDate
		# print
		sendDateSimple = datetime.datetime.strptime(sendDate, '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y')
		sendDay = datetime.datetime.strptime(sendDate, '%Y-%m-%dT%H:%M:%S').strftime('%A')
		sendTime = datetime.datetime.strptime(sendDate, '%Y-%m-%dT%H:%M:%S').strftime('%I:%m%p')
		sendDate = datetime.datetime.strptime(sendDate, '%Y-%m-%dT%H:%M:%S').strftime('%a. %b %d, %Y %I:%m%p')
		totalSentTo = dCampResults['emails_sent']
		lTotalSentTo.append(totalSentTo)
		# totalSentTo = totalSentTo  - totalSentToLAO
		emailSubject = (dCampResults['subject_line'])
		clicksTotal = dCampResults['clicks']['clicks_total']
		clicksUniqueSubscribersTotal = dCampResults['clicks']['unique_subscriber_clicks']
		clickRate = '{0:0.2f}%'.format(float(dCampResults['clicks']['click_rate'] * 100))
		bounced = dCampResults['bounces']['hard_bounces'] + dCampResults['bounces']['soft_bounces']
		bounceRate = '{0:0.2f}%'.format(float(bounced) / totalSentTo * 100)
		opens = dCampResults['opens']['unique_opens']
		openRate = '{0:0.2f}%'.format(float(dCampResults['opens']['open_rate'] * 100))
		lOpenRate.append(float(dCampResults['opens']['open_rate']))
		notOpened = totalSentTo - opens
		unsubscribed = dCampResults['unsubscribed']

		lData = []
		lData.append(campTitle)
		lData.append(sendDateSimple)
		lData.append(sendDay)
		lData.append(sendTime)
		lData.append(totalSentTo)
		lData.append(unsubscribed)
		lData.append(opens)
		lData.append(openRate)
		lData.append(clicksTotal)
		lData.append(clickRate)
		lData.append(clicksUniqueSubscribersTotal)
		lData.append(bounced)
		lData.append(bounceRate)

		lCampaignsNoHeader.append(lData)
	return lCampaignsNoHeader

# Write list to Excel Sheet
# write_to_Excel(lMembersGroup, lMembersGroupHeader, colsGroups, 'Group Membership', 'Group Membership')
def write_to_Excel(lin, header, num_cols, sheet_name, sheet_title):
	lout, lHeader, num_rows = xxl.mailchimp_admin_list_formatter(lin, header)
	sht = xw.main.sheets.add(sheet_name)
	df = pd.DataFrame(lout, columns=lHeader)  # Convert list of lists to a dataframe
	sht.range('A1').value = sheet_title
	sht.range('A3').options(index=False, header=True).value = df

	# Vertical format for Group Membership
	if header == 'Group Membership':
		group = True
	else:
		group = False

	# Add Hyperlink to Campaigns
	if header == 'Campaigns':
		rowsCampaigns = len(lCampaignsNoHeader) + 4
		for i in range(4, rowsCampaigns):
			cell = sht.range('A{0}'.format(i))
			cellValue = cell.value
			cellValueNoSpaces = cellValue.replace(' ', '')
			hyperlink = 'https://request-server.s3.amazonaws.com/maps/{0}.html'.format(cellValueNoSpaces)
			cell.add_hyperlink(hyperlink, cellValue, 'Click to open Eblast')

	xxl.mailchimp_admin_report_formatter(wb, sht, num_cols, rows=num_rows, group=group)
# pp = PrettyPrinter(indent=4)
service = fun_login.TerraForce()
client = fun_login.MailChimp()
outFilePath = 'F:/Research Department/MailChimp/'
todaydate = td.today_date()
skipLists = 'Capital, Events, Land Advisors Organization Test List, Land Sale Notification, LAO Staff, Market Insights Subscribers, New Mexico, Prop 479, Resort Solutions, Schwab Personal, Thunderbird, Tony Lang, Water'

# Dict of MC Lists
dMCLists = mc.getListNameID(client)

# Select list from menu
useThisList = selectMCList()

# # Cycle throught lists
for l in dMCLists['lists']:
	mcListName = l['name']
	# print mcListName
	if mcListName in skipLists:
		continue
	if useThisList == 'All':
		pass
	elif mcListName != useThisList:
		continue
	lao.banner('Market Insights Subscriber Report - {0}'.format(mcListName))
	outFile = '{0}Market Insights Subscriber Report {1} {2}.xlsx'.format(outFilePath, mcListName, todaydate)

	mcListID = l['id']

	lTotalSentTo = []
	lOpenRate = []

	lCampaignsNoHeader = assembleCampaignData()

	print('\n Getting list members...')
	dListMembers, listID = mc.get_audience_members(client, mcListID, 'get_all', 0, True)

	# for member in dListMembers:
	# 	pprint(dListMembers[member])
	# 	break
	# 	ui = td.uInput('\n Continue... > ')
	# 	if ui == '00':
	# 		exit('\n Terminating program...')

	# Make lists for sheets
	lMembersStats, lMembersBouncedUnsub, lMembersGroup = [], [], []
	lMembersGroupHeader = ['First Name', 'Last Name', 'Company', 'Email']

	dListCampaignGroups = mc.getListCampaignGroups(client, mcListID)
	lCampaignGroups = []
	
	for group in dListCampaignGroups:
		if group != 'Market Insights':
				continue
		lCampaignGroups.append(group)
	lCampaignGroups.sort()
	lMembersGroupHeader.extend(lCampaignGroups)
	lMembersGroupHeader.append('Tag')
	# lMembersGroup = [lMembersGroupHeader]

	# Cycle through members
	for member in dListMembers:
		# pprint(dListMembers[member])
		
		# Set variable values
		fname = dListMembers[member]['firstName']
		lname = dListMembers[member]['lastName']
		company = dListMembers[member]['company']
		email = dListMembers[member]['email']
		stars = dListMembers[member]['memberRating']
		status = dListMembers[member]['status']
		unsubReason = dListMembers[member]['unsubscribe_reason']
		unsubReason = unsubReason.replace('N/A (', '').replace(')', '')
		emailClient = dListMembers[member]['email_client']
		lastChange = dListMembers[member]['last_changed']
		lastChange = lastChange[:10]
		dInterests = dListMembers[member]['interests']
		clickRate = '{0:0.2f}%'.format(float(dListMembers[member]['clickRate'] * 100))
		openRate = '{0:0.2f}%'.format(float(dListMembers[member]['openRate'] * 100))
		# Add Tags
		lTags = []
		if dListMembers[member]['tags'] == []:
			lTags = []
		else:
			for row in dListMembers[member]['tags']:
				lTags.append(row['name'])

		# Make sheet row list
		lStat, lBouncedUnsub, lGroup = [], [], []

		lStat.extend([fname, lname, company, email, emailClient])
		lBouncedUnsub.extend([fname, lname, company, email, emailClient])
		lGroup.extend([fname, lname, company, email])

		if status == 'subscribed':  # Subscribed Contacts
			lStat.extend([stars, clickRate, openRate, status])
			lMembersStats.append(lStat)
		else: # Bounced & Unsubscribed Contacts
			if status == 'cleaned':
				lBouncedUnsub.append('bounced')
				lBouncedUnsub.append(lastChange)
				lBouncedUnsub.append('n/a')
			else:
				lBouncedUnsub.append(status)
				lBouncedUnsub.append(lastChange)
				lBouncedUnsub.append(unsubReason)
			lMembersBouncedUnsub.append(lBouncedUnsub)

		# Make Group Membership
		if status == 'subscribed':
			for group in lCampaignGroups:
				if group != 'Market Insights':
					continue
				for row in dListCampaignGroups:
					if row == group:
						id = dListCampaignGroups[row]
						break
				if dInterests[id] == True:
					lGroup.append('YES')
				else:
					lGroup.append('NO')
			# Tags
			isMITagged = 'NO'
			for tag in lTags:
				if tag == 'Market Insights':
					isMITagged = 'YES'
					break
			lGroup.append(isMITagged)
			# print(lGroup)
			lMembersGroup.append(lGroup)

	# Make pages based on subscriber activity
	lClickersNoHeader, lOpenersNoHeader, lIgnorersNoHeader = [], [], []
	for row in lMembersStats:
		if row[6] != '0.00%':
			lClickersNoHeader.append(row)
		elif row[7] != '0.00%':
			lOpenersNoHeader.append(row)
		else:
			lIgnorersNoHeader.append(row)

	colsGroups = len(lMembersGroupHeader)
	rowsGroups = len(lMembersGroup)

	
	# lMembersGroup = mc.adminReportListFormatter(lMembersGroup, lMembersGroupHeader)
	lMembersGroup, lHeader, num_rows = xxl.mailchimp_admin_list_formatter(lMembersGroup, lMembersGroupHeader)
	# Write to spreadsheet
	wb = xw.Book()

	write_to_Excel(lMembersGroup, lMembersGroupHeader, colsGroups, 'Market Insights', 'Market Insights')
	# sht = xw.main.sheets.add('Market Insights')
	# sht.range('A1').value = 'Market Insights Subscribers'
	# sht.range('A3').value = lMembersGroup
	# # mc.adminReportPageFormatter(wb, sht, colsGroups, rowsGroups, group=True)
	# xxl.mailchimp_admin_report_formatter(wb, sht, colsGroups, rowsGroups, group=True)

	sht1 = wb.sheets['Sheet1']
	sht1.delete()
	print(outFile)
	wb.save(outFile)

	# Open spreadsheet if only one market is selected
	if useThisList == 'All':
		wb.close()
print(' Fin')

# print(' Adding sheet: Group Members')
# write_to_Excel(lMembersGroup, lMembersGroupHeader, colsGroups, 'Group Membership', 'Group Membership')