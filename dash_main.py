from dash import Dash, html, dcc, Output, Input, State
import plotly.express as px
import pandas as pd
from algo_trader import constants
from algo_trader.studies import mrr
import plotly.graph_objects as go
from algo_trader.chart_helpers import *
from plotly.subplots import make_subplots
# Default Contract
contract = 'MES' 
with open("contract_request.txt", "w") as file:
    file.write(contract)
    file.close()

# Initialize Dash App
app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id = 'contract_dropdown',
            options = list(constants.CONTRACTS.keys()),
            value = 'MES'           
        ),
    ]),

    html.Div([
        dcc.Dropdown(id = 'bar_size',
            options = constants.TIME_INTERVALS,
            value = '5 mins'       
        ),
        
    ]),


    dcc.Graph(
        id="graph_subplots",
        config={'displayModeBar': False},
        style={'height': '1000px'},
        className = 'chart-graph', 
    ),
    dcc.Interval(
        id = 'graph_update',
        interval = 5000,
        n_intervals = 0
    ),
])

# Define app callbacks
@app.callback(
    Output('graph_subplots', 'figure'), 
    [Input(component_id='contract_dropdown', component_property= 'value'),
     Input(component_id='bar_size', component_property= 'value'),
     Input('graph_update', 'n_intervals')],
     

)
# Update Function
def display_graphs(value, bar_size, intervals):
    global df, candlestick_df, algo_df, contract

    if value != contract: # Contract Changed
        with open("contract_request.txt", "w") as file:
            file.write(value + '\n')
            file.write(bar_size)
            file.close()
        contract = value

    df = pd.read_csv('data/' + value + '.csv')
    fig = get_default_fig(df)
    
    return fig

app.run(debug=True)

