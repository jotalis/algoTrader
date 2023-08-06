from dash import Dash, html, dcc, Output, Input, State
import plotly.express as px
import pandas as pd
from algo_trader import constants
from algo_trader.algorithms import mrr
import plotly.graph_objects as go

# Default Contract
contract = 'MES' 

# Default Dataframes
df = pd.read_csv('data/' + contract + '.csv')
candlestick_df = df
algo_df = mrr.get_mrr(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10)

# Default Graphs
candlestick_graph = go.Figure(go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
))
algo_graph = go.Figure(data = [go.Scatter(x=algo_df[x]['date'],y=algo_df[x]['close'], name = x, showlegend = False) for x in algo_df]) 

# Initialize Dash App
app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id = 'dropdown',
            options = list(constants.CONTRACTS.keys()),
            value = 'MES'           
        )
    ]),
    dcc.Graph(
        id="candlestick_graph",
        figure=candlestick_graph,
        config={'displayModeBar': False},
        style={'height': '750px'}  # Set the height for algo_graph
    ),
    dcc.Graph(
        id="algo_graph",
        figure=algo_graph,
        config={'displayModeBar': False},
        style={'height': '750px'}  # Set the height for algo_graph
    ),
    # html.Div([
    #     dcc.Graph(id="candlestick_graph"),
    #     dcc.Graph(id="algo_graph"), 
    # ] , style={'display': 'flex', 'flexDirection': 'column'}),
])


# Define app callbacks
@app.callback(
    Output('candlestick_graph', 'figure'),
    Output('algo_graph', 'figure'), 
    [Input(component_id='dropdown', component_property= 'value'),
     Input('algo_graph', 'relayoutData')],
     [State('candlestick_graph', 'figure'),
      State('algo_graph', 'figure')]
)
# Update Function
def display_graphs(value, relayoutData, candlestick_graph, algo_graph):
    global df ,candlestick_df, algo_df, contract

    if relayoutData == None or value != contract: # Contract Changed
        df = pd.read_csv('data/' + value + '.csv')
        algo_df = mrr.get_mrr(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10)
        
        # Update candlestick graph
        candlestick_graph = go.Figure(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ))
        candlestick_graph.update_layout(xaxis_rangeslider_visible=False)
        
        # Update algo graph
        algo_graph = go.Figure(data = [go.Scatter(x=algo_df[x]['date'],y=algo_df[x]['close'], name = x, showlegend = False) for x in algo_df]) 
        algo_graph.update_layout(xaxis_rangeslider_visible=True)

        # Update current contract
        contract = value
         
        return [candlestick_graph, algo_graph] 

    else: # Relay event callback

        # Get min max of changed graph
        xmin, xmax = algo_graph['layout']['xaxis']['range']
        candlestick_xbound = candlestick_df[candlestick_df['date'].between(xmin, xmax)]

        # Update candlestick graph
        candlestick_graph = go.Figure(go.Candlestick(
            x=candlestick_xbound['date'],
            open=candlestick_xbound['open'],
            high=candlestick_xbound['high'],
            low=candlestick_xbound['low'],
            close=candlestick_xbound['close']
        ))
        candlestick_graph.update_layout(xaxis_rangeslider_visible=False)

        # Update algo graph
        # Set min max of algo graph
        # TODO: fix algo_graph ymin and ymax
        algo_graph['layout']['yaxis']['range'] = [df['close'].min()-10, df['close'].max()+10]
        algo_graph['layout']['yaxis']['autorange'] = False

    return [candlestick_graph, algo_graph]

app.run(debug=True)