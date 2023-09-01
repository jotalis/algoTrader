from ib_insync import *
from algo_trader import constants
from algo_trader.ib_helpers import *
import pandas as pd
import os, pickle
from datetime import datetime


# Default Contract
contract = ''
bar_size = ''
duration = '2 D'
rth = False
file_length = 0
client_id = 1
account_data = {}
# Initialize IB-Insync
ib = IB()
ib.connect('127.0.0.1', 7497, 0)

# Give time to connect to TWS
while not ib.isConnected():
    ib.sleep(0.01)
print("Connected to IB")

# Cleanup files in directory
cleanup_files()

while True:
    try: 
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
            file_length = len(bars)
            df = util.df(bars)
            df.loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)
            
        try:
            # Continously save new rows of incoming data
            bars_length = len(bars)
            
            if bars_length > file_length:
                last_bar = util.df(bars).loc[:,['date', 'open', 'high', 'low', 'close']].tail(bars_length-file_length)
                last_bar.to_csv('data/' + requested_contract + '.csv', mode = 'a', index=False, header = False)

                file_length = bars_length
                
                if os.path.exists("bot_running.p"): check_trade(ib); write_to_console(str(datetime.now().strftime("%H:%M:%S")) + ": CHECKED TRADE")
        except:
            pass

        # Check for new trade request
        if os.path.exists("trade_order.p"):

            # Create a new instance of IB-Insync for orders
            ib_orders = IB()
            ib_orders.connect('127.0.0.1', 7497, client_id)
            client_id += 1
            
            # Get trade request details
            trade_order = pickle.load(open("trade_order.p", "rb"))
            os.remove("trade_order.p")
            order_action = trade_order['order_action']
            contract = constants.CONTRACTS[trade_order['contract']]
            quantity = int(trade_order['amount'])

            
            # Fill in missing contract details
            ib_orders.qualifyContracts(contract)
            
            # Place order
            order = MarketOrder(order_action, quantity)
            trade = ib_orders.placeOrder(contract, order)
            ib_orders.sleep(3)
            fill_price = trade.orderStatus.avgFillPrice
            
            # Communicate data to dash
            write_to_console(str(datetime.now().strftime("%H:%M:%S")) + ": " + order_action + " ORDER FILLED FOR " + trade_order['contract'] + " AT $" + str(fill_price))
            # order_data = {
            #     'date': str(datetime.now().strftime("%H:%M:%S")),
            #     'contract': trade_order['contract'],
            #     'quantity': quantity,
            #     'order_action': order_action,
            #     'fill_price': fill_price
            # }
            # account_data.get('orders', {})[str(datetime.now().strftime("%H:%M:%S"))] = order_data
            order_data = {
                'date': str(datetime.now().strftime("%m/%d %H:%M")),
                'contract': trade_order['contract'],
                'quantity': quantity,
                'action': order_action,
                'fill px': fill_price
            }
            account_data['positions'] = [account_data.get(column, []).append(order_data[column]) for column in constants.POSITION_TABLE_COLUMNS]
            
            ib_orders.disconnect() 

        # Retrieve and send account data
        account_summary = ib.accountSummary()
        for x in account_summary:
            if x.tag == "CashBalance" and x.currency == "USD":
                account_data['balance'] = x.value
                pickle.dump(account_data, open('account_data.p', 'wb'))
        current_time = datetime.now()
        if current_time.hour == 13 and current_time.minute == 59 and current_time.second == 55:

            time.sleep(30)
            ib.disconnect()
            ib.connect('127.0.0.1', 7497, client_id)
            client_id += 1
            # Request data from IBKR
            bars = ib.reqHistoricalData(contract = constants.CONTRACTS[requested_contract],
                endDateTime = '',durationStr = duration, barSizeSetting = requested_bar_size,
                whatToShow = 'BID', useRTH = rth, formatDate = 1, 
                keepUpToDate = True)

            # Save data up to current time 
            file_length = len(bars)
            df = util.df(bars)
            df.loc[:,['date', 'open', 'high', 'low', 'close']].to_csv('data/' + requested_contract + '.csv', index=False)

    except Exception as e:
        print(e)
        pass