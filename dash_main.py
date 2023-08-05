from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from algo_trader import constants
import plotly.graph_objects as go

df = pd.read_csv('data/MES.csv')

app = Dash(__name__)

app.layout = html.Div([
    dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider', 
                  'value': 'slider'}],
        value=['slider']
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"), 
    Input("toggle-rangeslider", "value"))
def display_candlestick(value):
    fig = go.Figure(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    ))

    fig.update_layout(
        xaxis_rangeslider_visible='slider' in value
    )
    return fig

app.run(debug=True)