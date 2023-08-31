import os, pickle
import pandas as pd
from algo_trader.studies import *

def cleanup_files():
    if os.path.exists("bot_running.p"): os.remove("bot_running.p")
    if os.path.exists("contract_request.p"): os.remove("contract_request.p")
    if os.path.exists("trade_order.p"): os.remove("trade_order.p")
    if os.path.exists("account_data.txt"): os.remove("account_data.txt")

def make_trade_order(order_action, contract, amount):
    trade_order = {
        'order_action': order_action,
        'contract': contract,
        'amount': amount
    }
    pickle.dump(trade_order, open("trade_order.p", "wb"))
    
    return trade_order

def check_trade(ib):
    
    # Whether the bot should make a trade
    trade = False

    if os.path.exists("bot_running.p"):
        bot_request = pickle.load(open("bot_running.p", "rb"))
        contract = bot_request['contract']
        studies = bot_request['studies']

        df = pd.read_csv("data/" + contract + ".csv")

        if len(studies) == 1:
            study = studies[0]
            if study == 'DMI': data = calc_DMI(df)
            # TODO: Add logic for other studies
            # elif study == 'MRR': data = calc_MRR(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = False)
            # elif study == 'MRR-INV': data = calc_MRR(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = True)
            # elif study == 'HMA': data = calc_HMA(df)

            signal = data[1]['last_signal']
            if signal['date'] == df['date'].iloc[-1]:
                trade = True
                if signal['order_action']: order_action = 'BUY'
                else: order_action = 'SELL'
        else:            
            pass
            # TODO: Add logic for multiple studies

        # Create trade order to send to ib_main
        positions = sum([v.position for v in ib.positions() if v.contract.symbol == contract])
        if trade and ((positions >= 1 and order_action == 'SELL') or (positions <= -1 and order_action == 'BUY') or positions == 0):
            make_trade_order(order_action, contract, abs(positions)+ 1)
            
    return trade
