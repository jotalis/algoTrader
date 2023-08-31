from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
from algo_trader import constants
from algo_trader.studies import *
import plotly.graph_objects as go
from algo_trader.dash_helpers import *
import os, datetime, pickle
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
                        html.Strong(children = "", id = 'account_balance', className="card-text"),
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
                    dbc.CardHeader([
                        html.Div(
                            children = [
                                dcc.Dropdown(id = 'contract_dropdown',
                                    options = list(constants.CONTRACTS.keys()),
                                    value = 'MES',
                                    clearable = False,
                                    style = {"float": "left", "width": "10vw", "font-weight": "bold"}
                                ),
                            ]
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
                            options = constants.STUDIES,
                            value=[],
                        ),
                    ])
                ],
                color="#202A44",
                className = 'mt-3 mb-3 text-light',
                style = {'height': '38vh'}
                ),
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("BOT DASHBOARD",  style = {'text-decoration' : 'underline'})),
                    dbc.CardBody([
                        html.Div(children = [                        
                            html.H4("SELECT STUDIES (2 MAX)"),
                            dbc.Checklist(
                                id = "bot_studies",
                                options = constants.STUDIES,
                                value=[],
                            ),
                        ]),
                        html.Div(
                            style = {'margin-top' : '15px'},
                            children = [
                            html.H4("BOT STATUS: STOPPED", id = 'bot_status'),

                            dbc.Button("START", n_clicks = 0, color="success", id = "run_bot_button" ,className="mr-3 mb-3", style = {'margin-right' : '15px' ,'width' :'7vw'}),
                            dbc.Alert(
                                "Please select atleast one study",
                                id="bot-erorr-alert",
                                is_open=False,
                                color = 'danger',
                                duration=3000,
                            ),
                        ]),                       
                        html.Div(
                            style = {'margin-top' : '15px'},
                            
                            children = [
                                html.H4("BOT CONSOLE", id = 'bot_console'),
                                dbc.Card([
                                    dbc.CardBody(
                                        id = "bot_log",
                                        children = []
                                    )
                                ],
                                color = "dark",
                                style = {'height': '25vh', "overflow-y": "scroll", "flex-direction": "column-reverse"},
                                className = 'mb-3 text-light',
                                )
                            ]
                        )

                    ]),
                ],
                color="#202A44",
                className = 'mb-3 text-light',
                style = {'height': '58vh',}
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
     Input('graph_update', 'n_intervals'),
     Input('graph_subplots', 'relayoutData'),],
     State('graph_subplots', 'figure')
)
def update_graphs(new_contract, new_bar_size, new_studies, intervals, relayout_data, fig):
    global df, contract, bar_size

    # Contract or bar size changed
    if (new_contract != contract or new_bar_size != bar_size):    
        # Get last modification date of data file
        last_modified = time.time()
        if os.path.exists('data/' + new_contract + '.csv'):
            last_modified = os.path.getmtime('data/' + new_contract + '.csv')
        
        
        # Request new data
        new_request = {
            'contract': new_contract,
            'bar_size': new_bar_size
        }
        pickle.dump(new_request, open("contract_request.p", "wb"))
        contract = new_contract
        bar_size = new_bar_size

        # Check if data file has been updated     
        while last_modified >= os.path.getmtime('data/' + new_contract + '.csv'):
            time.sleep(0.1)

    # Update figure
    while not os.path.exists('data/' + new_contract + '.csv'):
        time.sleep(0.1)

    df = pd.read_csv('data/' + new_contract + '.csv')    
    fig = get_fig((df.tail(constants.NUM_BARS + 100)).reset_index(drop=True), new_studies)

    # Update xaxis number
    axis = str(len(new_studies)+1) if new_studies else '' 
    
    # Set default axis range
    xaxis_range = [0, constants.NUM_BARS]

    # Set figure axis range if graph is zoomed 
    if relayout_data and 'xaxis' + axis +'.range[0]' in relayout_data and 'xaxis' + axis +'.range[1]' in relayout_data:
        x_min = max(relayout_data['xaxis' + axis +'.range[0]'], 0)
        x_max = min(relayout_data['xaxis' + axis +'.range[1]'], constants.NUM_BARS)
        xaxis_range = [x_min, x_max]
    
    # Update figure xaxis range
    fig['layout']['xaxis'+ axis]['range'] = xaxis_range

    # Update figure dragmode
    if list(fig['layout']['xaxis'+ axis]['range']) != [0, constants.NUM_BARS]: fig['layout']['dragmode'] = 'pan'
    else: fig['layout']['dragmode'] = 'zoom'

    return fig

# Account Summary Callback
@app.callback(
    Output('account_balance', 'children'),
    Input('account_summary_update', 'n_intervals'),
    State('account_balance', 'children'),
)
def update_account_summary(intervals, balance):
    if os.path.exists("account_data.txt"):
        with open("account_data.txt", "r") as file:
            balance = file.readline().strip()
    return '$' + balance

# Bot Dashboard Callback
prev_clicks, bot_running = 0, False
@app.callback(
    Output('run_bot_button', 'color'),
    Output('run_bot_button', 'children'),
    Output("bot_status", "children"),
    Output('bot_studies', 'options'),
    Output("bot-erorr-alert", "is_open"),
    Output("contract_dropdown", "disabled"),
    Output("bar_size", "disabled"),
    Output("bot_log", "children"),
    [Input("run_bot_button", "n_clicks"),
     Input('bot_studies', 'value'),],
    State('run_bot_button', 'color'),
    State('run_bot_button', 'children'),
    State('bot_studies', 'options'),
    State("bot_status", "children"),
    State('contract_dropdown','value'),
    State('bar_size', 'value'),
    State("contract_dropdown", "disabled"),
    State("bot_log", "children"),
    prevent_initial_call=True
)
def update_bot_dashboard(n_clicks, selected_studies, button_color, button_text, options, status, contract, bar_size, dropdowns_disabled, bot_log):
    global prev_clicks, bot_running
    clicked = n_clicks > prev_clicks
    error_is_open = False
    if selected_studies:
        # Start/Stop bot
        if clicked:
            bot_running = not bot_running
            if bot_running:
                # Disable dropdowns if bot is running
                dropdowns_disabled = True
                # Update bot log
                bot_log.append(html.H6("> " + str(datetime.datetime.now().strftime("%H:%M:%S")) + ": Bot started with contract " + contract + " and bar size " + bar_size + " and studies " + str(selected_studies)))
                # bot_log.append(html.H6("> Current Time: " + ))
                # Create bot run request and send configurations to ib_main
                auto_trade_config = {
                    'contract': contract,
                    'bar_size': bar_size,
                    'studies': selected_studies
                }
                pickle.dump(auto_trade_config, open("bot_running.p", "wb"))

            else:
                # Enable dropdowns if bot is stopped
                dropdowns_disabled = False
                # Update bot log
                bot_log.append(html.H6("> " + str(datetime.datetime.now().strftime("%H:%M:%S")) + ": Bot stopped"))
                # Delete bot run request
                os.remove("bot_running.p")

        # Disable all studies if bot is running OR disable non-selected studies if max studies selected
        options = [
            {"label": option["label"], "value": option["value"], "disabled": (bot_running and option["value"]) or (len(selected_studies) == 2 and option["value"] not in selected_studies)}
            for option in options
        ]
    else:
        # Alert user to select atleast one study
        error_is_open = True
    # Update button
    button_color = 'warning' if bot_running else 'success'; 
    button_text = 'CANCEL' if bot_running else 'START'
    status = f'BOT STATUS: {"RUNNING" if bot_running else "STOPPED"}'
    prev_clicks = n_clicks
    
    return [button_color, button_text, status, options, error_is_open, dropdowns_disabled, dropdowns_disabled, bot_log]

app.run(debug = True)
