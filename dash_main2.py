from dash import Dash, html, dcc, Output, Input, State
import plotly.express as px
import pandas as pd
from algo_trader import constants
from algo_trader.algorithms import mrr
import plotly.graph_objects as go
from algo_trader import chart_helpers
from plotly import subplots
app = Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id = 'dropdown',
            options = list(constants.CONTRACTS.keys()),
            value = 'MES'           
        )
    ]),
    html.Div( className = 'div-right-panel', children = [
    html.Div( children =[    html.Div(
        id = "charts",
        className = "row",
        children = [chart_helpers.chart_div("MES"), chart_helpers.chart_div("TSLA") ]
    ) ]),
    dcc.Interval(
        id = 'graph-update',
        interval = 5000,
        n_intervals=0

    )
     
     
     
    ])
])




df = pd.read_csv('data/MES.csv', index_col = 'date', parse_dates =True)
a = df['close']
print(a)
df = a.resample('30T').ohlc()

print(df)
fig = subplots.make_subplots(
    rows=1,
    shared_xaxes=True,
    shared_yaxes=True,
    cols=1,
    print_grid=False,
    vertical_spacing=0.12,
)
fig.append_trace(df, 1, 1)

# Define app callbacks
# @app.callback(
#     Output('candlestick_graph', 'figure'),
#     Output('algo_graph', 'figure'), 
#     [Input(component_id='dropdown', component_property= 'value'),
#      Input('graph-update', 'n_intervals')],

# )
# # Update Function
# def display_graphs(value, intervals):
#     global df, candlestick_df, algo_df, contract
#     print(intervals)
#     df = pd.read_csv('data/' + value + '.csv')

#     candlestick_df = df
#     algo_df = mrr.get_mrr(df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10)
    
#     # Update candlestick graph
#     candlestick_graph = go.Figure(go.Candlestick(
#         x=candlestick_df['date'],
#         open=candlestick_df['open'],
#         high=candlestick_df['high'],
#         low=candlestick_df['low'],
#         close=candlestick_df['close']
#     ))
#     candlestick_graph.update_layout(xaxis_rangeslider_visible=False)
#     candlestick_graph.update_layout(transition_duration=500)
#     candlestick_graph.update_xaxes(type = 'category')
#     # Update algo graph
#     algo_graph = go.Figure(data = [go.Scatter(x=algo_df[x]['date'],y=algo_df[x]['close'], name = x, showlegend = False) for x in algo_df]) 
#     algo_graph.update_layout(xaxis_rangeslider_visible=False)

#     if value != contract: # Contract Changed
#         print("contract changed")
#         contract = value
#         with open("contract_request.txt", "w") as file:
#             file.write(value)
#             file.close()

#     return [candlestick_graph, algo_graph]

app.run(debug=True)

