from ib_insync import *
from dash import html
CONTRACTS = {
    'MES': Future(symbol='MES', lastTradeDateOrContractMonth='202309', exchange='CME', currency='USD'),
    'ES': Future(symbol='ES', lastTradeDateOrContractMonth='202309', exchange='CME', currency='USD'),
    'TSLA': Stock('TSLA', 'SMART', 'USD'),
}

TIME_INTERVALS = [
    '1 min',
    '5 mins',
    '15 mins',
    '30 mins',
]

STUDIES = [
    {"label": html.Span("MRR", style={"font-size": 15, "padding-left": 5}), "value": "MRR"},
    {"label": html.Span("MRR-INV", style={"font-size": 15, "padding-left": 5}), "value": "MRR-INV"},
    {"label": html.Span("DMI", style={"font-size": 15, "padding-left": 5}), "value": "DMI"},
    {"label": html.Span("HMA", style={"font-size": 15, "padding-left": 5}), "value": "HMA"},
]

ADD_OPTIONS = [

    {"label": html.Span("EARLY EXIT", style={"font-size": 15, "padding-left": 5}), "value": "EARLY EXIT"},
]

POSITION_TABLE_COLUMNS = ['DATE', 'TKR', 'ACTN', '#', '$']

NUM_BARS = 150
