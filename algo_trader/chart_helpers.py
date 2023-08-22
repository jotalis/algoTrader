import plotly.graph_objects as go
from plotly.subplots import make_subplots
from algo_trader.studies import *

def get_fig(df, studies):
    row = 1
    num_studies = len(studies) if studies else 0
    fig = make_subplots(rows = 1 + num_studies, cols = 1, shared_xaxes=True, vertical_spacing=0.01)
    
    get_candlebar(fig, row, df)
    if studies:
        for row, study in enumerate(studies,2):
            if study == 'MRR': get_MRR(fig, row, df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = False)
            elif study == 'MRR-INV': get_MRR(fig, row, df, levelsPeriod=21, levelsUpPercent=89, levelsDownPercent=10, invert = True)
            elif study == 'DMI': get_DMI(fig, row, df)
            elif study == 'HMA': get_HMA(fig, row, df)
            fig.update_yaxes(row = row, col = 1, title = study, showgrid = False, linecolor="#FFF")
            fig.update_xaxes(row = row, col = 1, showgrid = False)

    fig.update_layout(plot_bgcolor="#263252", paper_bgcolor = "#263252", font = {"color" : "#FFF"}, hovermode = 'x unified', showlegend = False,
                        xaxis1=dict(showgrid=False), yaxis1=dict(linecolor="#FFF", showgrid=False), 
                        uirevision = 'The User is always right',
    )
    fig.update_traces(xaxis="x"+str(row))
    fig.update_xaxes(rangeslider_visible = False, showspikes = True, spikemode = 'across')
    return fig

def get_candlebar(fig, row, df):
    candlebar = go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='candlestick',
        hoverlabel = dict(namelength = 0),
        )
    fig.add_trace(candlebar, row = row, col = 1)
    fig.update_yaxes(row = row, col = 1, title = "CNDLBAR")
    return candlebar
