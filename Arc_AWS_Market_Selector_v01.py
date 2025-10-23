
__author__ = 'blandis'

# import amp
# import bb
# import json
# import lao
import fun_login
from os import path
import arcpy

def getUserInput():
	if arcpy.GetParameterAsText(0) == 'true':
		return 'Albuquerque'
	elif arcpy.GetParameterAsText(1) == 'true':
		return 'Atlanta'
	elif arcpy.GetParameterAsText(2) == 'true':
		return 'Austin'
	elif arcpy.GetParameterAsText(3) == 'true':
		return 'Boise'
	elif arcpy.GetParameterAsText(4) == 'true':
		return 'Charlotte'
	elif arcpy.GetParameterAsText(5) == 'true':
		return 'DFW'
	elif arcpy.GetParameterAsText(6) == 'true':
		return 'Denver'
	elif arcpy.GetParameterAsText(7) == 'true':
		return 'Greenville'
	elif arcpy.GetParameterAsText(8) == 'true':
		return 'Houston'
	elif arcpy.GetParameterAsText(9) == 'true':
		return 'Huntsville'
	elif arcpy.GetParameterAsText(10) == 'true':
		return 'Jacksonville'
	elif arcpy.GetParameterAsText(11) == 'true':
		return 'Kansas City'
	elif arcpy.GetParameterAsText(12) == 'true':
		return 'Las Vegas'
	elif arcpy.GetParameterAsText(13) == 'true':
		return 'Nashville'
	elif arcpy.GetParameterAsText(14) == 'true':
		return 'Prescott'
	elif arcpy.GetParameterAsText(15) == 'true':
		return 'Orlando'
	elif arcpy.GetParameterAsText(16) == 'true':
		return 'Phoenix'
	elif arcpy.GetParameterAsText(17) == 'true':
		return 'Reno'
	elif arcpy.GetParameterAsText(18) == 'true':
		return 'Salt Lake City'
	elif arcpy.GetParameterAsText(19) == 'true':
		return 'Tampa'
	elif arcpy.GetParameterAsText(20) == 'true':
		return 'Tucson'
	elif arcpy.GetParameterAsText(21) == 'true':
		return 'Yuma'
	else:
		arcpy.AddError('\n No selection made.')

# Remove Lead, Parcel & Road layers and load same from selected Market
def loadMarketMasterMXDMarket(market='None', mxd=False, polyType='None', polyID='None', Lon='None', Lat='None', parcelLayerName='None', arcpy='None'):
	if arcpy == 'None':
		print('\n Loading arcpy in amp.loadMarketMasterMXDMarket...')
		import arcpy
	from bb import getLeadDealData
	from lao import getCounties

	# Set Variables
	lyrPath = 'F:/Research Department/maps/Layers/'
	foundAPN = True

	# User "CURRENT" mxd if one is not provided in argument
	if mxd is False:
		mxd = arcpy.mapping.MapDocument("CURRENT")
		clearSelection = False
	else:
		clearSelection = True

	df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
	mxdMarket = arcpy.mapping.ListLayers(mxd, "", df)[0].name
	targetGroupLayer = arcpy.mapping.ListLayers(mxd, 'ID', df)[0]

	# Clear OwnerIndex of selected PIDs/polygons
	OwnerIndexLayer = arcpy.mapping.ListLayers(mxd, "OwnerIndex", df)[0]
	arcpy.SelectLayerByAttribute_management(OwnerIndexLayer, "CLEAR_SELECTION")

	# If PID provided get the PID's market
	if polyType == 'PID':
		PID = polyID.strip()
		service = fun_login.TerraForce()
		
		market = getLeadDealData(service, PID, dealVar='Market')
		# No PID Exists error trap
		if market == 'No PID Exists':
			return 'No PID Exists'
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Get Market
	elif polyType == 'MARKET':
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Get LID Dictionary
	elif polyType == 'LID':
		LID = polyID.strip()
		dLID = getLIDDict(LID)
		market = dLID['market']
		county = dLID['county']
		marketAbb, stateAbb = getMarketAbbreviation(market, county)
	
	# Get APN Dictionary
	elif polyType == 'APN':
		APN = polyID.strip()
		APN = APN.replace('_split', '')
		if market == 'None' or market == None:
			market, ArcName = getMarketMasterMXDMarketFromLonLat(float(Lon), float(Lat), arcpy=arcpy)
		marketAbb, stateAbb = getMarketAbbreviation(market)
		if parcelLayerName == 'None' or not 'Parcels' in parcelLayerName:
			parcelLayerName = '{0}Parcels{1}'.format(stateAbb, ArcName)

	if polyType == 'LonLat':
		market, ArcName = getMarketMasterMXDMarketFromLonLat(float(Lon), float(Lat), arcpy=arcpy)
		marketAbb, stateAbb = getMarketAbbreviation(market)

	# Check if market is currently loaded
	if market == mxdMarket:
		loadNewMarket = False
	else:
		loadNewMarket = True
	
	# Remove Market Master TOC market label, Leads, Parcels & Roads
	if loadNewMarket:
		lMarkets = getCounties('Market')
		# Remove Market Label
		for mkt in lMarkets:
			try:
				removeLyr = arcpy.mapping.ListLayers(mxd, mkt, df)[0]
				arcpy.mapping.RemoveLayer(df, removeLyr)
				break
			except IndexError:
				continue
		
		# Remove Roads
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Roads', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
			arcpy.AddError('Roads failed to remove')
			pass
		# Remove Parcels
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Parcels', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
			pass
		# Remove Leads
		try:
			removeLyr = arcpy.mapping.ListLayers(mxd, 'Leads', df)[0]
			arcpy.mapping.RemoveLayer(df, removeLyr)
		except IndexError:
				pass
	
		# Add Parcels
		# arcpy.AddMessage(marketAbb)
		addLayer = arcpy.mapping.Layer('{0}{1}_Parcels.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
		# Add Leads. If clearSelection is not true the it is the OPR that is loading so don't load Leads layer.
		if clearSelection is not True:
			addLayer = arcpy.mapping.Layer('{0}{1}_Leads.lyr'.format(lyrPath, marketAbb))
			arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
		# Add Roads
		# if stateAbb == 'AL' or stateAbb == 'KY':
		# 	stateAbb = 'TN'
		# addLayer = arcpy.mapping.Layer('{0}{1}_Roads.lyr'.format(lyrPath, stateAbb))
		addLayer = arcpy.mapping.Layer('{0}{1}_Roads.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayer(df, addLayer, "TOP")
		# Add TOC Market Label
		addLayer = arcpy.mapping.Layer('{0}{1}_TOC_Label.lyr'.format(lyrPath, marketAbb))
		arcpy.mapping.AddLayer(df, addLayer, "TOP")
		# Zoom to LID if nessasary
		if polyType == 'LID':
			zoomToLID(arcpy, df, mxd, dLID, clearSelection=clearSelection)
	
	# Zoom to Market, PID or LID
	# First always zoom to the market defualt veiw
	zoomToLAOMarketBookmark(arcpy, df, mxd, market)
	# if polyType == 'MARKET':
	# 	zoomToLAOMarketBookmark(arcpy, df, mxd, market)
	if polyType == 'PID':
		zoomToPID(arcpy, df, mxd, PID, clearSelection=clearSelection)
	elif polyType == 'LID':
		zoomToLID(arcpy, df, mxd, dLID, clearSelection=False)
	elif polyType == 'APN':
		foundAPN = zoomToAPN(arcpy, df, mxd, APN, parcelLayerName, clearSelection=False)
		if foundAPN is False:
			if Lon == 'None':
				arcpy.AddError('\n Cannot find APN.')
			elif Lon != None:
				zoomToLonLat(arcpy, df, mxd, float(Lon), float(Lat))
	elif polyType == 'LonLat':
		zoomToLonLat(arcpy, df, mxd, float(Lon), float(Lat))

	arcpy.RefreshActiveView()
	del mxd

# Set Variables
market = getUserInput()
arcpy.AddMessage('\n Arc AWS Market Selector PY3')
arcpy.AddMessage('\n {0}'.format(market))

loadMarketMasterMXDMarket(market=market, mxd=False, polyType='MARKET')

exit()