from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
from algo_trader import constants
from algo_trader.studies import mrr
import plotly.graph_objects as go
from algo_trader.chart_helpers import *
from plotly.subplots import make_subplots
from dash import clientside_callback
# Default Contract
contract = '' 
bar_size = ''
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
        interval = 500,
        n_intervals = 0
    ),
    dcc.Store(id='scroll-zoom-store', data=True)
])

# Define app callbacks
@app.callback(
    Output('graph_subplots', 'figure'), 
    [Input(component_id='contract_dropdown', component_property= 'value'),
     Input(component_id='bar_size', component_property= 'value'),
     Input('graph_update', 'n_intervals')],
)

# Update Function
def display_graphs(new_contract, new_bar, intervals):
    global df, contract, bar_size
    # print(new_contract, new_bar, intervals)
    if new_contract != contract or new_bar != bar_size: # Contract Changed
        with open("contract_request.txt", "w") as file:
            file.write(new_contract + '\n')
            file.write(new_bar)
            file.close()
        contract = new_contract
        bar_size = new_bar

    df = pd.read_csv('data/' + new_contract + '.csv')
    fig = get_default_fig(df)
    
    # Add Studies
    get_mrr(fig, df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10)

    # Share last xaxis with all traces
    fig.update_traces(xaxis = 'x2')

    return fig

app.clientside_callback(
    """function(scrollZoomState) {return {'scrollZoom': true};}""",
    Output('graph_subplots', 'config'),
    Input('scroll-zoom-store', 'data')
)
app.run(debug=True)

