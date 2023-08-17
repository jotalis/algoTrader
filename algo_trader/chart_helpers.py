import plotly.graph_objects as go
from plotly.subplots import make_subplots
from algo_trader.studies.mrr import *

def get_default_fig(df):
    fig = make_subplots(rows = 2, cols = 1, shared_xaxes=True, vertical_spacing=0.01, y_title='Price',)
    fig.add_trace(get_candlebar(df), row = 1, col = 1)
    fig.update_xaxes(rangeslider_visible = False)
    fig["layout"]["uirevision"] = "The User is always right"
    return fig

def get_candlebar(df):
    candlebar = go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],)
    return candlebar
