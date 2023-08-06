from ib_insync import *
from algo_trader import constants
import pandas as pd

requested_contract = 'ES'
ib = IB()
ib.connect('127.0.0.1', 7497, 0)

#RequMest Market Data
ib.reqMarketDataType(1)

#CANDLEBARS SHOW BID PRICE
#useRTH = use Real Time Trading Hours
bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
    endDateTime = '',durationStr = '1 D', barSizeSetting='5 mins',
    whatToShow = 'BID', useRTH = 0, formatDate = 1, 
    keepUpToDate = True)

#Converting to pandas dataframe
df = util.df(bars)

df = df.to_csv('data/' + requested_contract + '.csv', index=False)





