import talib
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def get_mrr(fig, row, df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    mrr_data = calc_mrr(df, averagePeriod, averagePrice, averageType, levelsPeriod, levelsUpPercent, levelsDownPercent, showSignals, invert)
    plots, up_cross, down_cross = mrr_data[0], mrr_data[1]['up_cross_signals'], mrr_data[1]['down_cross_signals']

    # Plot average, level_up, level_down
    fig.add_traces([go.Scatter(x=plots[x]['date'],y=plots[x]['close'], name = x, showlegend = True) for x in plots], rows=row, cols = 1)
    
    # Ensure all graphs share the same x axis
    fig.update_traces(xaxis = "x" + str(row))

    # Plot arrows
    for idx in up_cross:
        fig.add_annotation(
                x=df['date'][idx],
                y=plots['average']['close'][idx-(levelsPeriod+averagePeriod-2)],
                xref="x"+str(row), yref="y"+str(row), text="UP",
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
                y=plots['average']['close'][idx-(levelsPeriod+averagePeriod-2)],
                xref="x"+str(row), yref="y"+str(row), text="DOWN",
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

def calc_mrr(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True, invert = False):
    
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