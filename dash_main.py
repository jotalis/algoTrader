from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
from algo_trader import constants
from algo_trader.studies import *
import plotly.graph_objects as go
from algo_trader.chart_helpers import *
import os
import dash_bootstrap_components as dbc

# Default Contract
df = ''
contract = '' 
bar_size = ''

# Initialize Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Build Dash Layout
app.layout = dbc.Container(
    children = [
        dcc.Interval(id = 'graph_update', interval = 20000, n_intervals = 0),
        dcc.Store(id='scroll-zoom-store', data=True),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("ACCOUNT SUMMARY", className="card-text")),
                    dbc.CardBody([
                        html.P("$156,789", className="card-text"),
                        html.P("+12.5% from last week", className="card-text"),
                    ])
                ],
                color="#202A44",
                className = 'mt-3 mb-3 text-light',
                style = {'height': '48vh'}
                ),
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("OPEN POSITIONS", className="card-text")),
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
                    dbc.CardHeader(html.H2("BOT DASHBOARD", className="card-text")),
                    dbc.CardBody([
                        html.H5("Select Studies", className="card-text"),
                        dbc.Checklist(
                            id = "studies_checklist",
                            options = [
                                {"label": html.Span("MRR", style={"font-size": 15, "padding-left": 5}), "value": "MRR"},
                                {"label": html.Span("MRR-INV", style={"font-size": 15, "padding-left": 5}), "value": "MRR-INV"},
                                {"label": html.Span("DMI", style={"font-size": 15, "padding-left": 5}), "value": "DMI"},
                                {"label": html.Span("HMA", style={"font-size": 15, "padding-left": 5}), "value": "HMA"},
                            ]
                        ),
                    ])
                ],
                color="#202A44",
                className = 'mt-3 mb-3 text-light',
                style = {'height': '48vh'}
                ),
                dbc.Card(
                [
                    dbc.CardHeader(html.H2("Bot Console")),
                    dbc.CardBody([
                        html.P("$156,789"),
                        html.P("+12.5% from last week", className="card-text"),
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

# Define app callbacks
@app.callback(
    Output('graph_subplots', 'figure'), 
    [Input('contract_dropdown','value'),
     Input('bar_size', 'value'),
     Input('studies_checklist', 'value'),
     Input('graph_update', 'n_intervals')],
     State('graph_subplots', 'figure')
)

# Update Function
def display_graphs(new_contract, new_bar_size, new_studies, intervals, fig):
    global df, contract, bar_size
    
    # Contract or bar size changed
    if (new_contract != contract or new_bar_size != bar_size):    
        # Get last modification date of data file
        last_modified = os.path.getmtime('data/' + new_contract + '.csv')
        
        # Request new data
        with open("contract_request.txt", "w") as file:
            file.write(new_contract + '\n')
            file.write(new_bar_size)
            file.close()
        contract = new_contract
        bar_size = new_bar_size

        # Check if data file has been updated     
        while last_modified >= os.path.getmtime('data/' + new_contract + '.csv'):
            time.sleep(0.1)

    # Update figure
    df = pd.read_csv('data/' + new_contract + '.csv')
    fig = get_fig(df, new_studies)
    return fig

# Update scroll zoom
app.clientside_callback(
    """function(scrollZoomState) {return {'scrollZoom': true};}""",
    Output('graph_subplots', 'config'),
    Input('scroll-zoom-store', 'data')
)

app.run(debug = True)

