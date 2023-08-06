from ib_insync import *

CONTRACTS = {
    'MES': Future(symbol='MES', lastTradeDateOrContractMonth='202309', exchange='CME', currency='USD'),
    'ES': Future(symbol='ES', lastTradeDateOrContractMonth='202309', exchange='CME', currency='USD'),
    'TSLA': Stock('TSLA', 'SMART', 'USD'),
}



