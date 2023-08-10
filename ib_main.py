from ib_insync import *
from algo_trader import constants
import pandas as pd
import os


# Callback function
def on_new_bar(bars, hasNewBar):
    print("is this begin called")
    if hasNewBar:
        util.df(bars).tail(1).to_csv('data/' + requested_contract + '.csv',
                                    mode = 'a', index=False, header = False)

# Default Contract
requested_contract = 'MES'

ib = IB()
ib.connect('127.0.0.1', 7497, 0)

# Give time to connect to TWS
while not ib.isConnected():
    ib.sleep(0.01)
print("Connected to TWS")

# Request Real Time Market Data
ib.reqMarketDataType(3)

# Request candlebar data
# useRTH = use Real Time Trading Hours
bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
    endDateTime = '',durationStr = '1 D', barSizeSetting='5 mins',
    whatToShow = 'BID', useRTH = 1, formatDate = 1, 
    keepUpToDate = True)

# Save to corresponding csv file
df = util.df(bars).to_csv('data/' + requested_contract + '.csv', index=False)

# Update calls callback function
bars.updateEvent+= on_new_bar

while True:

    # Updates IB-Insync loop
    ib.sleep(0.03)

    # Check for new contract request
    if os.path.exists("contract_request.txt"):
        with open("contract_request.txt", "r") as file:
            requested_contract = file.read()
            print(requested_contract)
            file.close()
        os.remove("contract_request.txt")

    if requested_contract != bars.contract.symbol:

        bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
            endDateTime = '',durationStr = '2 D', barSizeSetting='15 mins',
            whatToShow = 'BID', useRTH = 1, formatDate = 1, 
            keepUpToDate = True)
        df = util.df(bars).to_csv('data/' + requested_contract + '.csv', index=False)

