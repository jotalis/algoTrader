from ib_insync import *
from algo_trader import constants
from algo_trader.ib_helpers import *
import pandas as pd
import os, pickle

# Default Contract
contract = ''
bar_size = ''
duration = '2 D'
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

        if requested_bar_size == '1 min': duration = "14400 S"
        elif requested_bar_size == '5 min': duration = "2 D"
        else: duration = '1 W'

        # Request data from IBKR
        bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
            endDateTime = '',durationStr = duration, barSizeSetting = requested_bar_size,
            whatToShow = 'BID', useRTH = rth, formatDate = 1, 
            keepUpToDate = True)

        # Save data up to current time 
        df = util.df(bars)
        df.loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)

    # Continously save new rows of incoming data
    try:
        bars_length, file_length = len(bars), len(pd.read_csv('data/' + requested_contract + '.csv'))
        if bars_length > file_length:
            util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].tail(bars_length-file_length).to_csv('data/' + requested_contract + '.csv',
                                        mode = 'a', index=False, header = False)
            check_trade(ib)
    except:
        pass

    # Check for new trade request
    if os.path.exists("trade_order.p"):

        # Create a new instance of IB-Insync for orders
        ib_orders = IB()
        ib_orders.connect('127.0.0.1', 7497, 1)
        
        # Get trade request details
        trade_order = pickle.load(open("trade_order.p", "rb"))
        os.remove("trade_order.p")
        order_action = trade_order['order_action']
        contract = constants.CONTRACTS[trade_order['contract']]
        amount = int(trade_order['amount'])
        
        print(type(contract))
        
        # Fill in missing contract details
        ib_orders.qualifyContracts(contract)
        
        # Place order
        order = MarketOrder(order_action, amount)
        ib_orders.placeOrder(contract, order)
        ib_orders.sleep(1)

        while order.orderStatus.status != 'Filled':
            ib_orders.sleep(0.05)

        print("Order Filled")

        ib_orders.disconnect()
        

    # Retrieve and send account data
    account_summary = ib.accountSummary()
    for x in account_summary:
        if x.tag == "CashBalance" and x.currency == "USD":
            with open("account_data.txt", "w") as file:
                file.write(x.value)

    