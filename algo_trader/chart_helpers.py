import plotly.graph_objects as go
from plotly.subplots import make_subplots
from algo_trader.studies.mrr import *

def get_default_fig(df):
    fig = make_subplots(rows = 2, cols = 1, shared_xaxes=True, vertical_spacing=0.01, y_title='Price',)
    fig.update_layout(plot_bgcolor="#FFF", hovermode = 'x unified',
                        xaxis1=dict(linecolor="#BCCCDC", showgrid=False),
                        xaxis2=dict(linecolor="#BCCCDC", showgrid=False), 
                        yaxis=dict(linecolor="#BCCCDC", showgrid=False), 
                        yaxis2=dict(linecolor="#BCCCDC", showgrid=False),
                        uirevision = 'The User is always right'
                        ) 
    
    fig.add_trace(get_candlebar(df),row = 1, col = 1)

    fig.update_xaxes(rangeslider_visible = False, showspikes = True, spikemode = 'across')
    
    return fig

def get_candlebar(df):
    candlebar = go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='candlestick',
        hoverlabel = dict(namelength = 0),
        )

    return candlebar
