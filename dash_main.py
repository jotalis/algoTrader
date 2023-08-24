from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
from algo_trader import constants
from algo_trader.studies import *
import plotly.graph_objects as go
from algo_trader.chart_helpers import *
import os
import dash_bootstrap_components as dbc

# Default Contract
df = None
contract = '' 
bar_size = ''

# Initialize Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Build Dash Layout
app.layout = dbc.Container(
    children = [
        dcc.Interval(id = 'graph_update', interval = 20000, n_intervals = 0),
        dcc.Interval(id = 'account_summary_update', interval = 5000, n_intervals = 0),
        dcc.Store(id='scroll-zoom-store', data=True),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("ACCOUNT SUMMARY", style = {'text-decoration' : 'underline'})),
                    dbc.CardBody([
                        html.H4("BALANCE:", className="card-text", ),
                        html.Strong(id = 'account_balance', className="card-text"),
                    ])
                ],
                color="#202A44",
                className = 'mt-3 mb-3 text-light',
                style = {'height': '48vh'}
                ),
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("OPEN POSITIONS", style = {'text-decoration' : 'underline'})),
                    dbc.CardBody([
                        html.P("$156,789", className="card-text"),
                        html.P("+12.5% from last week", className="card-text"),
                    ]),
                ],
                color="#202A44",
                className = 'mb-3 text-light',
                style = {'height': '48vh'}
                ),
            ],
            width = {'size': 2, 'order': 1}),
            
            dbc.Col([
                dbc.Card(
                [
                    dbc.CardHeader(
                        [
                        dcc.Dropdown(id = 'contract_dropdown',
                            options = list(constants.CONTRACTS.keys()),
                            value = 'MES',
                            clearable = False,
                            style = {"float": "left", "width": "10vw", "font-weight": "bold"}
                        ),
                        html.Div(
                            className = 'graph-top-right inline-block',
                            children = [
                                dcc.Dropdown(id = 'bar_size',
                                    options = constants.TIME_INTERVALS,
                                    clearable = False,
                                    value = '1 min',
                                    style = {"float": "right", "width": "10vw", "font-weight": "bold"}
                                ),
                            ],  
                        )]
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            id="graph_subplots",
                            config={'displayModeBar': False},
                            style={'height': '90vh'},
                        ),
                    ]),
                ],
                color="#202A44",
                className = 'mt-3 mb-3',
                style = {'height': '97vh'}
                ),
            ],
            width = {'size': 8, 'order': 2}),

            dbc.Col([
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("GRAPH DASHBOARD", style = {'text-decoration' : 'underline'})),
                    dbc.CardBody([
                        html.H4("Select Studies", className="card-text"),
                        dbc.Checklist(
                            id = "studies_checklist",
                            options = constants.STUDIES
                        ),
                    ])
                ],
                color="#202A44",
                className = 'mt-3 mb-3 text-light',
                style = {'height': '48vh'}
                ),
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("BOT DASHBOARD",  style = {'text-decoration' : 'underline'})),
                    dbc.CardBody([
                        html.Div(children = [                        
                            html.H4("SELECT STUDIES (2 MAX)"),
                            dbc.Checklist(
                                id = "bot_studies",
                                options = constants.STUDIES
                            ),
                        ]),
                        html.Div(
                            style = {'margin-top' : '15px'},
                            children = [
                            html.H4("RUN BOT (STATUS: STOPPED)", id = 'bot_status'),
                            # dbc.Button("STOP", color="danger", className="mb-3 mr-3", style = {'margin-right' : '15px' ,'width' :'5vw'}),
                            dbc.Button("START", n_clicks = 0, color="success", id = "run_bot_button" ,className="mr-3 mb-3", style = {'margin-right' : '15px' ,'width' :'7vw'})
                        ]),


                    ]),
                ],
                color="#202A44",
                className = 'mb-3 text-light',
                style = {'height': '48vh'}
                ),
            ],
            width = {'size': 2, 'order': 3}),
        ]),
    ],
    fluid = True,
    style = {'backgroundColor': '#182033'}
    
)

# ~~~Define app callbacks~~~
# Graph Callback
@app.callback(
    Output('graph_subplots', 'figure'), 
    [Input('contract_dropdown','value'),
     Input('bar_size', 'value'),
     Input('studies_checklist', 'value'),
     Input('graph_update', 'n_intervals')],
     State('graph_subplots', 'figure')
)
def update_graphs(new_contract, new_bar_size, new_studies, intervals, fig):
    global df, contract, bar_size
    
    # Contract or bar size changed
    if (new_contract != contract or new_bar_size != bar_size):    
        # Get last modification date of data file
        last_modified = os.path.getmtime('data/' + new_contract + '.csv')
        
        # Request new data
        with open("contract_request.txt", "w") as file:
            file.write(new_contract + '\n')
            file.write(new_bar_size)
        contract = new_contract
        bar_size = new_bar_size

        # Check if data file has been updated     
        while last_modified >= os.path.getmtime('data/' + new_contract + '.csv'):
            time.sleep(0.1)

    # Update figure
    df = pd.read_csv('data/' + new_contract + '.csv')
    fig = get_fig(df, new_studies)
    return fig

# Account Summary Callback
@app.callback(
    Output('account_balance', 'children'),
    Input('account_summary_update', 'n_intervals')
)
def update_account_summary(intervals):
    if os.path.exists("account_data.txt"):
        with open("account_data.txt", "r") as file:
            balance = file.readline().strip()
    return '$' + balance

# Bot Dashboard Callback
@app.callback(
    Output('run_bot_button', 'color'),
    Output('run_bot_button', 'children'),
    Output("bot_status", "children"),
    Output('bot_studies', 'options'),
    [Input("run_bot_button", "n_clicks"),
     Input('bot_studies', 'value'),],
    State('run_bot_button', 'color'),
    State('run_bot_button', 'children'),
    State("bot_status", "children"),
    prevent_initial_call=True
)
def update_bot_dashboard(n_clicks, value, button_color, button_text, status):
    options = constants.STUDIES
    is_odd_click = n_clicks % 2 == 1

    if (value and len(value) == 2) or is_odd_click:
        options = [
            {"label": option["label"], "value": option["value"], "disabled": option["value"] not in value}
            for option in constants.STUDIES
        ]

    button_color = 'warning' if is_odd_click else 'success'
    button_text = 'CANCEL' if is_odd_click else 'START'
    status = f'RUN BOT (STATUS: {"RUNNING" if is_odd_click else "STOPPED"})'

    return [button_color, button_text, status, options]

# Update scroll zoom
app.clientside_callback(
    """function(scrollZoomState) {return {'scrollZoom': true};}""",
    Output('graph_subplots', 'config'),
    Input('scroll-zoom-store', 'data')
)


app.run(debug = True)

