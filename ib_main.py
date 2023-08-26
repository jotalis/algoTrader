from ib_insync import *
from algo_trader import constants
from algo_trader.ib_helpers import *
import pandas as pd
import os, pickle

# Default Contract
contract = ''
bar_size = ''
duration = '1 D'
rth = False

# Initialize IB-Insync
ib = IB()
ib.connect('127.0.0.1', 7497, 0)

# Give time to connect to TWS
while not ib.isConnected():
    ib.sleep(0.01)
print("Connected to TWS")

# Cleanup files in directory
cleanup_files()

while True:
    # Updates IB-Insync loop
    ib.sleep(0.1)
    
    # Check for new contract request
    if os.path.exists("contract_request.p"):
        request = pickle.load(open("contract_request.p", "rb"))
        requested_contract = request['contract']
        requested_bar_size = request['bar_size']
        os.remove("contract_request.p")
        
        if type(constants.CONTRACTS[requested_contract]) == Future: ib.reqMarketDataType(1); rth = False # Use live market data for futures
        else: ib.reqMarketDataType(3); rth = True # Use delayed and real time trading hour data for stocks

        # Request data from IBKR
        bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
            endDateTime = '',durationStr = duration, barSizeSetting = requested_bar_size,
            whatToShow = 'BID', useRTH = rth, formatDate = 1, 
            keepUpToDate = True)
        
        # Save data up to current time 
        df = util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)

    # Continously save new rows of incoming data
    try:
        file_length = len(pd.read_csv('data/' + requested_contract + '.csv'))
        bars_length = len(bars)
        if bars_length > file_length:
            util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].tail(bars_length-file_length).to_csv('data/' + requested_contract + '.csv',
                                        mode = 'a', index=False, header = False)
            #check_buy()
    except:
        pass
    check_buy()
    

    # Retrieve and send account data
    account_summary = ib.accountSummary()
    for x in account_summary:
        if x.tag == "CashBalance" and x.currency == "USD":
            with open("account_data.txt", "w") as file:
                file.write(x.value)

    