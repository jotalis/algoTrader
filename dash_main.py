from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
from algo_trader import constants
import plotly.graph_objects as go


contract = 'MES' #Default Contract
df = pd.read_csv('data/' + contract + '.csv')

#Initial Graphs
candlebar = go.Figure(go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
))
algo_graph = px.line(df, x='date', y='close')

#Create App
app = Dash(__name__)
app.layout = html.Div([
    html.Div([

        dcc.Dropdown(id = 'dropdown',
            options = list(constants.CONTRACTS.keys()),
            value = 'MES'           
        )
    ]),
    html.Div([
        dcc.Graph(id="candlebar"),
        dcc.Graph(id="algo_graph"),
    ]),
    html.Pre(id='relayout-data')
])

@app.callback(
    Output('candlebar', 'figure'),
    Output('algo_graph', 'figure'), 
    [Input(component_id='dropdown', component_property= 'value'),
     Input('algo_graph', 'relayoutData')],
     [State('candlebar', 'figure'),
      State('algo_graph', 'figure')]
)
def display_graphs(value, relayoutData, candlebar, algo_graph):
    global df, contract
    if relayoutData == None or value != contract:
        df = pd.read_csv('data/' + value + '.csv')
        contract = value
        candlebar = go.Figure(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ))
        candlebar.update_layout(
            xaxis_rangeslider_visible=False
        )
        algo_graph = px.line(df, x='date', y='close')
        algo_graph.update_layout(
            xaxis_rangeslider_visible=True
        )
    
        return [candlebar, algo_graph] 
    
    elif 'xaxis.range' in relayoutData:
        
        xmin = relayoutData["xaxis.range"][0]
        xmax = relayoutData["xaxis.range"][1]
        dff = df[df['date'].between(xmin, xmax)]
        candlebar = go.Figure(go.Candlestick(
            x=dff['date'],
            open=dff['open'],
            high=dff['high'],
            low=dff['low'],
            close=dff['close']
        ))
        candlebar.update_layout(
            xaxis_rangeslider_visible=False
        )
        # algo_graph = px.line(df, x='date', y='close')

    return [candlebar, algo_graph]

app.run(debug=True)