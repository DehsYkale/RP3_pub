import lao
import csv
from glob import glob
import how
from pprint import pprint

# Add data fields to the dSubData dict for a market
def buildDict(dSubData, market):
	dSubData[market] = {
		'5-10': 0,
		'11-49': 0,
		'50-1000': 0,
		'Built Out': 0,
		'Total': 0
	}
	return dSubData

# Add Starts, Built Out and Total Subs to market
def addData(dSubData, market, r):
	# Total Subs in market
	dSubData[market]['Total'] = dSubData[market]['Total'] + 1
	# Total Annual Closings by number of Closings
	if r['AnnClosings'] >= 5 and r['AnnClosings'] <= 10:
		dSubData[market]['5-10'] = dSubData[market]['5-10'] + 1
	elif r['AnnClosings'] <= 49:
		dSubData[market]['11-49'] = dSubData[market]['11-49'] + 1
	elif r['AnnClosings'] >= 50:
		dSubData[market]['50-1000'] = dSubData[market]['50-1000'] + 1
	# Built Out Count
	# vacant_lots_in_sub = r['VDLInv'] + r['Future']
	vacant_lots_in_sub = r['VDLInv (VDL)'] + r['FutureUnits (Fut)']
	if r['AnnClosings'] >= vacant_lots_in_sub:
		dSubData[market]['Built Out'] = dSubData[market]['Built Out'] + 1
	
	return dSubData

how.zonda_active_sub_csv_builder_for_arcmap()

pathMetroStudy = 'F:/Research Department/MIMO/zData/Metrostudy/'
yrqtr = lao.getDateQuarter(lastquarter=True)
fMS_Active_Subs = 'F:/Research Department/maps/Active Subs/MS_Active_Subs_{0}.csv'.format(yrqtr)
fMS_Annual_Sales_per_Sub = 'F:/Research Department//maps/Active Subs/MS_Annual_Sales_per_Sub_{0}.csv'.format(yrqtr)
# inXLSXfiles = glob('{0}MS_*_{1}.xlsx'.format(pathMetroStudy, yrqtr))
inXLSXfiles = glob('{0}*subs_{1}.xls'.format(pathMetroStudy, yrqtr))
# print(yrqtr)
# pprint(inXLSXfiles)
# exit()

dSubData = {}
lMarkets = []
lSkip_markets = ['IEP', 'SAC', 'SEA']

with open(fMS_Active_Subs, 'w', newline='') as f:
	fout = csv.writer(f)
	# Header
	fout.writerow(['Market', 'SubID', 'ProdType', 'BuiltOut', 'AnnStarts', 'AnnClos', 'InvVDL', 'InvFut', 'Lon', 'Lat'])

	for xls in inXLSXfiles:
		# skip open temp files
		if '$' in xls:
			continue
		# Get market from file name
		# market = xls[48:51]
		market = xls[45:48]
		if market in lSkip_markets:
			continue
		# print(xls)
		# print(market)
		# Add data fields to the dSubData dict for a market
		dSubData = buildDict(dSubData, market)
		if market != 'DFW':
				lMarkets.append(market)
		print(market)
		# pprint(dSubData)
		# exit()
		dTemp = lao.spreadsheetToDict(xls)
		for row in dTemp:
			r = dTemp[row]
			if r == {}:
				break
			if (r['BuiltoutQtr'] == 'Active'  or r['BuiltoutQtr'] == '') and r['AnnClosings'] >= 5:
				# pprint(r)
				lWrite = []
				lWrite.append(market)
				lWrite.append(r['SubID'])
				lWrite.append(r['ProductType'])
				lWrite.append(r['BuiltoutQtr'])
				lWrite.append(r['AnnStarts'])
				lWrite.append(r['AnnClosings'])
				# lWrite.append(r['VDLInv'])
				lWrite.append(r['VDLInv (VDL)'])
				# lWrite.append(r['Future'])
				lWrite.append(r['FutureUnits (Fut)'])
				# lWrite.append(r['Longitude'])
				# lWrite.append(r['Latitude'])
				lWrite.append(r['Lon'])
				lWrite.append(r['Lat'])
				fout.writerow(lWrite)

				# Add Starts, Built Out and Total Subs to market
				if market != 'DFW':
					dSubData = addData(dSubData, market, r)
		# pprint(dSubData)

# Make Annual Sales per Active Subdivision csv
with open(fMS_Annual_Sales_per_Sub, 'w', newline='') as f:
	fout = csv.writer(f)
	# Header
	fout.writerow(['Market', 'CurSubCount', 'Sort'])
	sort_count = 1
	for mkt in lMarkets:
		cnt1 = dSubData[mkt]['5-10']
		cnt2 = dSubData[mkt]['11-49']
		cnt3 = dSubData[mkt]['50-1000']
		bltout = dSubData[mkt]['Built Out']
		tot = dSubData[mkt]['Total']
		cur_sub_count = '({0}):({1}):({2}):({3}):{4}'.format(cnt1, cnt2, cnt3, bltout, tot)
		for i in range(1, 3):
			sort_lable = 'CurSub {0:02d}'.format(sort_count)
			fout.writerow([mkt, cur_sub_count, sort_lable])
			sort_count += 1
		if mkt == 'ATL':
			sort_count += 1
			sort_lable = 'CurSub {0:02d}'.format(sort_count)
			fout.writerow([mkt, cur_sub_count, sort_lable])


lao.openFile(fMS_Active_Subs)
lao.openFile(fMS_Annual_Sales_per_Sub)
exit()





