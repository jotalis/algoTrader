import os, pickle
import pandas as pd
from algo_trader.studies import *
def cleanup_files():
    if os.path.exists("bot_running.p"): os.remove("bot_running.p")
    if os.path.exists("contract_request.p"): os.remove("contract_request.p")

def check_buy():
    if os.path.exists("bot_running.p"):
        bot_request = pickle.load(open("bot_running.p", "rb"))
        contract = bot_request['contract']
        bar_size = bot_request['bar_size']
        studies = bot_request['studies']
        df = pd.read_csv("data/" + contract + ".csv")
        current_index = len(df) - 1
        for study in studies:
            if study == 'DMI':  dmi = calc_DMI(df)
            if dmi[1]['crosses'][-1] == current_index:
                if dmi[1]['directions'][-1] == True:
                    print("BUY")
                else:
                    print("SELL")
            # if study == 'MRR': print(calc_MRR(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = False)[1]["up_cross_signals"])
            # elif study == 'MRR-INV': calc_MRR(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = True)
            # elif study == 'DMI': calc_DMI(df)
            # elif study == 'HMA': calc_HMA(df)
    

def create_order():
    pass