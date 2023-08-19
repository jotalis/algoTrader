import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash_extensions import Scroll

import plotly.subplots as sp
import plotly.graph_objs as go

app = dash.Dash(__name__)

# Create example subplots
fig = sp.make_subplots(rows=2, cols=1)
trace1 = go.Scatter(x=[1, 2, 3], y=[3, 2, 1])
trace2 = go.Scatter(x=[1, 2, 3], y=[1, 2, 3])
fig.add_trace(trace1, row=1, col=1)
fig.add_trace(trace2, row=2, col=1)

app.layout = html.Div([
    dcc.Store(id='scroll-zoom-store', data=True),
    Scroll(dcc.Graph(figure=fig, id='subplot-fig'))
])

@app.callback(
    Output('scroll-zoom-store', 'data'),
    Input('subplot-fig', 'relayoutData'),
    prevent_initial_call=True
)
def toggle_scroll_zooming(relayout_data):
    return not relayout_data.get('xaxis.fixedrange', False)

@app.callback(
    Output('subplot-fig', 'config'),
    Input('scroll-zoom-store', 'data'),
    prevent_initial_call=True
)
def update_subplot_config(scroll_zoom_state):
    return {'scrollZoom': scroll_zoom_state}

if __name__ == '__main__':
    app.run_server(debug=True)
