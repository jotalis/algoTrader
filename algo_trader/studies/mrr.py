import talib
import pandas as pd
import plotly.graph_objects as go

def get_mrr(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True):
    mrr_data = calc_mrr(df, averagePeriod, averagePrice, averageType, levelsPeriod, levelsUpPercent, levelsDownPercent, showSignals)
    mrr = [go.Scatter(x=mrr_data[x]['date'],y=mrr_data[x]['close'], name = x, showlegend = True) for x in mrr_data]
    return mrr

def calc_mrr(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True,):
    
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
    average_plot = pd.concat([dates, average], axis=1) 
    level_up = pd.concat([dates, level_up], axis=1)
    level_down = pd.concat([dates, level_down], axis=1)

    # Remove NaN values from all plots and reset start index
    starting_index = levelsPeriod+averagePeriod-2
    average_plot = average_plot[starting_index:].reset_index(drop=True)
    level_up = level_up[starting_index:].reset_index(drop=True)
    level_down = level_down[starting_index:].reset_index(drop=True)

    return {
        'average' :average_plot,
        'level_up': level_up,
        'level_down' :level_down
    }