from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
from algo_trader import constants
import plotly.graph_objects as go

contract = 'MES'
df = pd.read_csv('data/' + contract + '.csv')

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





# def display_relayout_data(relayoutData):
#     if relayoutData != None and 'xaxis.range[0]' in relayoutData:
#         y_lower, y_upper = zoom(df, relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]'])
#         print(filtered_df)

#     # print("xaxis changed")
#     print(relayoutData)
    # if relayoutData != None and 'autosize' not in relayoutData:
    #     if 'xaxis.range' in relayoutData:
    #         df = zoom(df, relayoutData['xaxis.range'][0], relayoutData['xaxis.range'][1])
    #         x_upper = 
    #     elif 'xaxis.range[0]' in relayoutData:
    #         x_lower = relayoutData['xaxis.range[0]']
    #         x_upper = relayoutData['xaxis.range[1]']
    #     filtered_df = df[df['date'].between(x_lower, x_upper)]
    #     print(filtered_df)

        # in_view = df[(df['date'] >= x_lower):x_range1]


    # if relayoutData!= None and len(relayoutData) == 1 and "xaxis.range" in relayoutData:
    #     in_view = df.loc[relayoutData['xaxis.range'][0]:relayoutData['xaxis.range'][0]]
    #     print(in_view)
    #     print([in_view['close'].min() - 10, in_view['high'].max() + 10])
    # elif relayoutData != None and len(relayoutData) == 2:
    #     in_view = df.loc[relayoutData['xaxis.range[0]']:relayoutData['xaxis.range[1]']]
    #     print(in_view)
    #     print([in_view['close'].min() - 10, in_view['high'].max() + 10])
    # return None

candlebar = go.Figure(go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
))
algo_graph = px.line(df, x='date', y='close')

@app.callback(
    Output('candlebar', 'figure'),
    Output('algo_graph', 'figure'), 
    [Input(component_id='dropdown', component_property= 'value'),
     Input('algo_graph', 'relayoutData')],
     [State('candlebar', 'figure'),
      State('algo_graph', 'figure')],
    #  prevent_initial_call=True
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
        # dff['distance']=dff.split_d.cumsum()
        # algo_graph = px.line(df, x='date', y='close')

    

    return [candlebar, algo_graph]

# @app.callback(
#     Output("candlebar", "figure"),
#     Output("algo_graph", "figure"), 
    
# )
# def display_graphs(relayoutData):
    
#     candlebar = go.Figure(go.Candlestick(
#         x=df['date'],
#         open=df['open'],
#         high=df['high'],    
#         low=df['low'],
#         close=df['close']
#     ))

#     #Retrieve Range of X-Axis
#     if relayoutData != None and 'xaxis.range[0]' in relayoutData:
#         a = df[df['date'].between(relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]'])]
#         print(a)
#         # y_lower, y_upper = zoom(df, relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]'])
#         # candlebar.update_layout(yaxis={'range': [y_lower, y_upper]})


#     return [candlebar, algo_graph]

# def zoom(df, lower, upper):
#     df = df[df['date'].between(lower, upper)]
#     print(df)

app.run(debug=True)