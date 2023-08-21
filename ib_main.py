from ib_insync import *
from algo_trader import constants
import pandas as pd
import os
import time

# Callback function
def on_new_bar(bars, hasNewBar):
    if hasNewBar:
        util.df(bars).tail(1).loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv',
                                    mode = 'a', index=False, header = False)

# Default Contract
requested_contract = 'MES'
duration = '1 D'
bar_size = '1 min'
rth = False

ib = IB()
ib.connect('127.0.0.1', 7497, 0)

# Give time to connect to TWS
while not ib.isConnected():
    ib.sleep(0.01)
print("Connected to TWS")

# Request Real Time Market Data (1 = live, 3 = delayed)
ib.reqMarketDataType(1) 

bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
    endDateTime = '',durationStr =  duration, barSizeSetting= bar_size,
    whatToShow = 'BID', useRTH = rth, formatDate = 1, 
    keepUpToDate = True)
# Save to corresponding csv file
df = util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)

# Update calls callback function
bars.updateEvent+= on_new_bar

while True:
    # Updates IB-Insync loop
    ib.sleep(0.01)
    # Check for new contract request
    if os.path.exists("contract_request.txt"):
        with open("contract_request.txt", "r") as file:
            requested_contract = file.readline().strip()
            bar_size = file.readline().strip()
            file.close()
        os.remove("contract_request.txt")

    if requested_contract != bars.contract.symbol or bar_size != bars.barSizeSetting:
        if type(constants.CONTRACTS[requested_contract]) == Future: ib.reqMarketDataType(1); rth = False
        else: ib.reqMarketDataType(3); rth = True
        bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
            endDateTime = '',durationStr = duration, barSizeSetting = bar_size,
            whatToShow = 'BID', useRTH = rth, formatDate = 1, 
            keepUpToDate = True)
        try:
            df = util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)
        except:
            df = None
