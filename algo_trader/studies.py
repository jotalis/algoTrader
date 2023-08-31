import talib, math, time
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from algo_trader import constants
"""
~~~FUNCTIONS~~~
void get_study(fig, row, df): 
    Adds study to figure

calc_study(df):
    Calculates study
    return [{
        'data_used_for_graphing' : data_used_for_graphing, -> For building figure traces    
        },
        {
        'last_signal': last_signal, -> For checking if a trade should be made
        }]
"""

# ~~~DMI~~~
def get_DMI(fig, row, df, timeperiod = 20):
    dmi_data = calc_DMI(df, timeperiod)
    posDI, negDI = dmi_data[0]['posDI'], dmi_data[0]['negDI']

    # Cut all plots to same num bars length
    posDI, negDI = posDI.tail(constants.NUM_BARS), negDI.tail(constants.NUM_BARS)    

    fig.add_trace(go.Scatter(x=posDI['date'],y=posDI['posDI'], name = "posDI", line={"color" : "#70DB93"}), row=row, col = 1)
    fig.add_trace(go.Scatter(x=negDI['date'],y=negDI['negDI'], name = "negDI", line={"color" : "#ff5349"}), row=row, col = 1)

def calc_DMI(df, timeperiod = 20):

    dates = df['date']
    high = np.array(df["high"])
    low = np.array(df["low"])
    close = np.array(df["close"])
    
    # Calculate DMI
    posDI = talib.PLUS_DI(high, low, close, timeperiod = timeperiod)
    negDI = talib.MINUS_DI(high, low, close, timeperiod = timeperiod)

    # Combine with date column 
    posDI_df = pd.DataFrame({'date': dates, 'posDI': posDI})
    negDI_df = pd.DataFrame({'date': dates, 'negDI': negDI})

    # Remove Nan values
    posDI_df = posDI_df.dropna(subset = ['posDI']).reset_index(drop=True)
    negDI_df = negDI_df.dropna(subset = ['negDI']).reset_index(drop=True)

    # Find indexes where lines cross  
    crosses = (np.where(np.diff(np.sign(posDI - negDI)) != 0)[0] + 1)
    directions= np.where(posDI[crosses] > negDI[crosses], True, False)

    # Get last signal
    last_signal = {
        "date" : dates[crosses[-1]],
        "order_action" : directions[-1],
    }

    return [{
        'posDI' : posDI_df,
        'negDI' : negDI_df
        },
        {
        'last_signal': last_signal,
        'crosses': crosses,
        'directions': directions
        }]

# ~~~HMA~~~
def get_HMA(fig, row, df, timeperiod = 14):
    hma_data = calc_HMA(df, timeperiod)
    hma_data = hma_data[0]['HMA']

    # Cut all plots to same num bars length
    hma_data = hma_data.tail(constants.NUM_BARS)

    fig.add_trace(go.Scatter(x= hma_data['date'], y=hma_data['HMA'], name = "HMA decreasing", showlegend = True, line={"color" : "#ff5349"}), row=row, col = 1)
    fig.add_trace(go.Scatter(x=hma_data['date'],y=hma_data['HMA'].where(hma_data['trends'] == 1), name = "HMA increasing", line={"color" : "#70DB93"}), row=row, col = 1)

def calc_HMA(df, timeperiod = 14):
    dates = df['date']
    close = df['close']

    # Calculate HMA
    hma = (talib.WMA(2 * talib.WMA(close, timeperiod = timeperiod//2) - talib.WMA(close, timeperiod = timeperiod),int(math.sqrt(timeperiod))))
    
    # Determine trend (increasing / decreasing)
    diffs = np.diff(hma)
    diffs = np.insert(diffs, 0, 0)
    trends = np.where(diffs > 0, 1, -1)

    # Combine with date and trend columns and remove NaN values
    hma_df = pd.DataFrame({'date': dates, 'trends': trends, 'HMA': hma})
    hma_df = hma_df.dropna(subset = ['HMA']).reset_index(drop=True)

    # Get last signal
    last_signal = {
        'date' : dates.iloc[-1],
        'order_action' : trends[-1] == 1
    }
    return [{
        'HMA' : hma_df
        },
        {
        'last_signal': last_signal
        }]

# ~~~MRR~~~
def get_MRR(fig, row, df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    mrr_data = calc_MRR(df, averagePeriod, averagePrice, averageType, levelsPeriod, levelsUpPercent, levelsDownPercent, showSignals, invert)
    plots, up_cross, down_cross = mrr_data[0], mrr_data[1]['up_cross_signals']-(levelsPeriod+averagePeriod-2), mrr_data[1]['down_cross_signals']-(levelsPeriod+averagePeriod-2)

    # Cut all plots to same num bars length
    for x in plots: plots[x] = plots[x].tail(constants.NUM_BARS)
    up_cross, down_cross = up_cross[up_cross > plots['average'].index[0]], down_cross[down_cross > plots['average'].index[0]]

    # Plot average, level_up, level_down
    fig.add_traces([go.Scatter(x=plots[x]['date'],y=plots[x][averagePrice], name = x) for x in plots], rows=row, cols = 1)

    # Plot arrows
    annotations =   [
             dict(x=plots['average']['date'][idx], 
                y=plots['average'][averagePrice][idx],
                yref="y"+str(row), 
                text="BUY", showarrow=True, 
                font=dict(family="Courier New, monospace", size=16, color="#40826D"), 
                arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor="#009E60",
                ax=0, ay=-30,
                bordercolor="#c7c7c7", borderwidth=2, borderpad=1, bgcolor="#C1E1C1") for idx in up_cross 
                    ] + [
            dict(x=plots['average']['date'][idx], 
                y=plots['average'][averagePrice][idx],
                yref="y"+str(row), 
                text="SELL", showarrow=True, 
                font=dict(family="Courier New, monospace", size=16, color="#A40826"), 
                arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor="#FF3131",
                ax=0, ay=30,
                bordercolor="#c7c7c7", borderwidth=2, borderpad=1, bgcolor="#E1C1C1") for idx in down_cross 
                    ]
    fig.update_layout(annotations =  fig['layout']['annotations']+tuple(annotations))

def calc_MRR(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    
    # Get specified data of candlestick
    data = df[averagePrice]
    # Get Series of dates
    dates = df['date']
    
    # PLOT 1
    average = talib.SMA(data, timeperiod = averagePeriod) #Get moving average

    # Define averages
    rolling_min = average.rolling(levelsPeriod).min()
    rolling_max = average.rolling(levelsPeriod).max()

    # PLOT 2
    level_up = rolling_min + (rolling_max - rolling_min) * levelsUpPercent / 100 

    # PLOT 3
    level_down = rolling_min + (rolling_max - rolling_min) * levelsDownPercent / 100 

    # Convert to numpy arrays for vectorization
    average = average.to_numpy()
    level_up = level_up.to_numpy()
    level_down = level_down.to_numpy()

    # Concatenate with date column to make dataframes
    average_df = pd.DataFrame({'date': dates, averagePrice: average})
    level_up_df = pd.DataFrame({'date': dates, averagePrice: level_up})
    level_down_df = pd.DataFrame({'date': dates, averagePrice: level_down})

    # Remove NaN values from all plots and reset start index
    starting_index = levelsPeriod+averagePeriod-2
    average_df = average_df[starting_index:].reset_index(drop=True)
    level_up_df = level_up_df[starting_index:].reset_index(drop=True)
    level_down_df = level_down_df[starting_index:].reset_index(drop=True)

    # Add signals
    # Find indexes where lines cross  
    up_cross = (np.where(np.diff(np.sign(average - level_up)) != 0)[0] + 1)
    down_cross = (np.where(np.diff(np.sign(average - level_down)) != 0)[0] + 1)
    
    # Find order of cross direction and remove invalid cross signals
    if invert:
        up_directions = np.where(average[up_cross] < level_up[up_cross], True, False)
        down_directions = np.where(average[down_cross] > level_down[down_cross], True, False)
        up_cross_signals = down_cross[(down_directions & (down_cross > starting_index))]
        down_cross_signals = up_cross[(up_directions & (up_cross > starting_index))]

    else:
        up_directions = np.where(average[up_cross] > level_up[up_cross], True, False)
        down_directions = np.where(average[down_cross] < level_down[down_cross], True, False)
        up_cross_signals = up_cross[(up_directions & (up_cross > starting_index))]
        down_cross_signals = down_cross[(down_directions & (down_cross > starting_index))]

    # Get last signal
    last_signal = {
        'date' : dates[up_cross[-1]] if up_cross[-1] > down_cross[-1] else dates[down_cross[-1]],
        'order_action' : up_cross[-1] > down_cross[-1]
    }
    return [{
        'average' :average_df,
        'level_up': level_up_df,
        'level_down' :level_down_df
        },
        {
        'last_signal': last_signal,
        'up_cross_signals': up_cross_signals,
        'down_cross_signals': down_cross_signals
        }]