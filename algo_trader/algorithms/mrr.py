import talib
import pandas as pd
def get_mrr(df, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True):
    
    #Get specified data of candlestick
    data = df[averagePrice]
    #Get Series of dates
    dates = df['date']
    #Get moving average and convert to series with label 'averagePrice'
    average = talib.SMA(data, timeperiod = averagePeriod).rename(averagePrice)
    # PLOT 1
    #Concatenate dates and average to make a dataframe
    average_plot = pd.concat([dates, average], axis=1)[averagePeriod-1:].reset_index(drop=True) #plot
    
    #Define averages
    min_average = min(average[(len(average) - max(levelsPeriod, 1)):]) 
    max_average = max(average[(len(average) - max(levelsPeriod, 1)):])
    # PLOT 2
    level_up = min_average + (max_average - min_average) * levelsUpPercent / 100 #plot
    
    # PLOT 3
    level_down = min_average + (max_average - min_average) * levelsDownPercent / 100 #plot

    return [average_plot, level_up, level_down]



