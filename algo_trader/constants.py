from ibapi.contract import Contract
from ib_insync import *
#CONTRACTS
# MES = Contract()
# MES.symbol = 'MES'
# MES.secType = 'FUT'
# MES.exchange = 'CME'
# MES.currency = 'USD'
# MES.lastTradeDateOrContractMonth  = '202309'
MES = Future(symbol='MES', lastTradeDateOrContractMonth='202309', exchange='CME', currency='USD')

ES = Contract()
ES.symbol = 'ES'
ES.secType = 'FUT'
ES.exchange = 'CME'
ES.currency = 'USD'
ES.lastTradeDateOrContractMonth  = '20230915'
