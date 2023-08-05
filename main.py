from ib_insync import *
from algo_trader import constants
import pandas as pd

app = IB()
app.connect('127.0.0.1', 7497, 123)

#RequMest Market Data
app.reqMarketDataType(1)
# app.reqMktData(1, MES, '', False, False, [])

#CANDLEBARS SHOW BID PRICE
#useRTH = use Real Time Trading Hours

bars = app.reqHistoricalData(contract = constants.MES,
    endDateTime = '',durationStr = '1 D', barSizeSetting='1 min',
    whatToShow = 'BID', useRTH = 0, formatDate = 1, 
    keepUpToDate = True)
# save to CSV file

df = util.df(bars)
df.to_csv(constants.MES.symbol + '.csv', index=False)
print(df)
# convert to pandas dataframe (pandas needs to be installed):


