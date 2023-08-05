from ib_insync import *
from algo_trader import constants

ib = IB()
ib.connect('127.0.0.1', 7497, 0)

#RequMest Market Data
ib.reqMarketDataType(1)

print(ib.accountSummary())
#CANDLEBARS SHOW BID PRICE
#useRTH = use Real Time Trading Hours
bars = ib.reqHistoricalData(contract = constants.CONTRACTS['MES'],
    endDateTime = '',durationStr = '1 D', barSizeSetting='1 min',
    whatToShow = 'BID', useRTH = 0, formatDate = 1, 
    keepUpToDate = True)

#Converting to pandas dataframe
df = util.df(bars)





