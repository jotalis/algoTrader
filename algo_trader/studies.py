import talib, math
import pandas as pd
import plotly.graph_objects as go
import numpy as np


# ~~~HMA~~~
def get_DMI(fig, row, df, timeperiod = 20):
    dmi_data = calc_DMI(df, timeperiod)
    posDI, negDI = dmi_data [0]['posDI'], dmi_data[0]['negDI']
    
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

    return [{
        'posDI' : posDI_df,
        'negDI' : negDI_df
        }]

# ~~~DMI~~~
def get_HMA(fig, row, df, timeperiod = 14):
    
    hma_data = calc_HMA(df, timeperiod)
    hma_data = hma_data[0]['HMA']
    hma_increasing = hma_data.loc[hma_data['trends'] == 1]
    hma_decreasing = hma_data.loc[hma_data['trends'] == -1]
    fig.add_trace(go.Scatter(x= hma_data['date'], y=hma_data['HMA'], name = "HMA decreasing", showlegend = True, line={"color" : "#ff5349"}), row=row, col = 1)
    fig.add_trace(go.Scatter(x=hma_data['date'],y=hma_data['HMA'].where(hma_data['trends'] == 1), name = "HMA increasing", line={"color" : "#70DB93"}), row=row, col = 1)
    # fig.add_trace(go.Scatter(x= hma_data['date'], y=hma_data['HMA'].where(hma_data['trends'] == -1), name = "HMA decreasing", line={"color" : "#ff5349"}), row=row, col = 1)


def calc_HMA(df, timeperiod = 14):
    dates = df['date']
    close = df['close']

    # Calculate HMA
    hma = (talib.WMA(2 * talib.WMA(close, timeperiod = timeperiod//2) - talib.WMA(close, timeperiod = timeperiod),int(math.sqrt(timeperiod))))
    
    # Determine trend (increasing / decreasing)
    # print(len(hma))
    diffs = np.diff(hma)
    diffs = np.insert(diffs, 0, 0)
    # print("diffs", len(diffs))
    trends = np.where(diffs > 0, 1, -1)


    # Combine with date and trend columns and remove NaN values
    
    hma_df = pd.DataFrame({'date': dates, 'trends': trends, 'HMA': hma})
    hma_df = hma_df.dropna(subset = ['HMA']).reset_index(drop=True)

    return [{
        'HMA' : hma_df
        }]

# ~~~MRR~~~
def get_MRR(fig, row, df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    mrr_data = calc_MRR(df, averagePeriod, averagePrice, averageType, levelsPeriod, levelsUpPercent, levelsDownPercent, showSignals, invert)
    plots, up_cross, down_cross = mrr_data[0], mrr_data[1]['up_cross_signals'], mrr_data[1]['down_cross_signals']

    # Plot average, level_up, level_down
    fig.add_traces([go.Scatter(x=plots[x]['date'],y=plots[x]['close'], name = x) for x in plots], rows=row, cols = 1)
    
    # Plot arrows
    for idx in up_cross:
        fig.add_annotation(
                x=df['date'][idx],
                y=plots['average']['close'][idx-(levelsPeriod+averagePeriod-2)],
                yref="y"+str(row), text="UP",
                showarrow=True,
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="#40826D"
                    ),
                arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor="#009E60",
                ax=0, ay=-30,
                bordercolor="#c7c7c7", borderwidth=2, borderpad=1, bgcolor="#C1E1C1"
            )
    for idx in down_cross:
        fig.add_annotation(
                x=df['date'][idx],
                y=plots['average']['close'][idx-(levelsPeriod+averagePeriod-2)], yref="y"+str(row), text="DOWN",

                showarrow=True,
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="#A40826"
                    ),
                arrowhead=2, arrowsize=1, arrowwidth=3, arrowcolor="#FF3131",
                ax = 0, ay=30,
                bordercolor="#c7c7c7", borderwidth=2, borderpad=1, bgcolor="#E1C1C1"
            )


def calc_MRR(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    
    # Get specified data of candlestick
    data = df[averagePrice]
    # Get Series of dates
    dates = df['date']
    
    # PLOT 1
    average = talib.SMA(data, timeperiod = averagePeriod) #Get moving average
    average = average.rename(averagePrice) #Convert to series with label 'averagePrice'

    # Define averages
    rolling_min = average.rolling(levelsPeriod).min()
    rolling_max = average.rolling(levelsPeriod).max()

    # PLOT 2
    level_up = rolling_min + (rolling_max - rolling_min) * levelsUpPercent / 100 
    # PLOT 3
    level_down = rolling_min + (rolling_max - rolling_min) * levelsDownPercent / 100 
    
    # Concatenate with date column to make dataframes
    average_df = pd.concat([dates, average], axis=1) 
    level_up_df = pd.concat([dates, level_up], axis=1)
    level_down_df = pd.concat([dates, level_down], axis=1)

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
        up_directions = np.where(average[up_cross] < level_up[up_cross], 1, 0)
        down_directions = np.where(average[down_cross] > level_down[down_cross], 1, 0)
        down_cross_signals = [up_cross[i] for i, x in enumerate(up_directions) if x and up_cross[i] > starting_index]
        up_cross_signals = [down_cross[i] for i, x in enumerate(down_directions) if x and down_cross[i] > starting_index]
    else:
        up_directions = np.where(average[up_cross] > level_up[up_cross], 1, 0)
        down_directions = np.where(average[down_cross] < level_down[down_cross], 1, 0)
        up_cross_signals = [up_cross[i] for i, x in enumerate(up_directions) if x and up_cross[i] > starting_index]
        down_cross_signals = [down_cross[i] for i, x in enumerate(down_directions) if x and down_cross[i] > starting_index]

    return [{
        'average' :average_df,
        'level_up': level_up_df,
        'level_down' :level_down_df
        },
        {
        'up_cross_signals': up_cross_signals,
        'down_cross_signals': down_cross_signals
        }]