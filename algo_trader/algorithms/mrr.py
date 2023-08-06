import talib

def get_mrr(data, averagePeriod = 14, averagePrice = 'close', averageType = 'SMA', levelsPeriod = 35, levelsUpPercent = 90, levelsDownPercent = 10, showSignals = True):
    data = data[averagePrice]
    average = talib.SMA(data, timeperiod = averagePeriod)
    min_average = min(average, max(levelsPeriod, 1))
    max_average = max(average, max(levelsPeriod, 1))
    level_up = min_average + (max_average - min_average) * levelsUpPercent / 100
    level_down = min_average + (max_average - min_average) * levelsDownPercent / 100

    return [data, level_up, level_down]



