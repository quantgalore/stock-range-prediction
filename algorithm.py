# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 21:54:02 2022

@author: Quant Galore
"""

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import statistics
import random
import numpy
import math
from datetime import timedelta


def round_to_multiple(number, multiple):
    return multiple * round(number / multiple)

# Backtests

def Find_Optimal():
    
    Asset_1 = yf.download(tickers = '^GSPC', start = '2022-07-24', end = '2022-09-02', interval = '15m')
    
    Underlying = Asset_1.reset_index()
    Underlying = Underlying.rename(columns = {'Datetime':'Date'})
    Underlying['Returns'] = Underlying['Adj Close'].pct_change().fillna(0)
    Underlying['Returns'] = numpy.log(1 + Underlying['Returns'])
    
    Differences = []
    Range_Percents = []
    

    for aa in range(5, len(Underlying), 5):
        try:
                
                Prediction_Dates = []
                
                head_size = 0
                
                Actual = []
                Predicted = []
                Ranges = []
                Range_Spreads = []
                
                period_size = aa
                for a in range(2, round(len(Underlying))):  
                    try:
                        Simulated_Prices = []
                        
                        TPlusOne = pd.DataFrame(Underlying['Adj Close'][head_size:head_size + period_size])
                        TPlusOne_Original = pd.DataFrame(Underlying[head_size:head_size + period_size])
                        TPlusOne['Returns'] = TPlusOne.pct_change().fillna(0)
                        TPlusOne['Returns'] = numpy.log(1 + TPlusOne['Returns'])
                        Daily_Vol = numpy.std(TPlusOne['Returns'])
                        Drift = TPlusOne['Returns'].tail(2).mean() * 10000
                        
                        Last_Value = TPlusOne.tail(1)['Adj Close'].iloc[0]
                        
                        
                        for c in range(0, 10000):
                            
                            if (c % 2) == 0:
                                # PlusOneDay = round_to_multiple((Last_Value + Last_Value * random.uniform(-Daily_Vol, Daily_Vol)) + Drift , 5)
                                PlusOneDay = Last_Value - Last_Value * abs(random.uniform(-Daily_Vol, Daily_Vol) * -1) - abs((Drift * 0.50))
                                
                            else:
                                # PlusOneDay = round_to_multiple((Drift * TPlusOne) + (TPlusOne + TPlusOne * random.uniform(-Daily_Vol, Daily_Vol)), 5)
                                # PlusOneDay = round_to_multiple((Last_Value - Last_Value * random.uniform(-Daily_Vol, Daily_Vol)) - Drift , 5)
                                PlusOneDay = Last_Value + Last_Value * abs(random.uniform(-Daily_Vol, Daily_Vol)) + abs((Drift * 0.50))
                                
                            Simulated_Prices.append(PlusOneDay)
                        
                        Simulated_Prices = pd.DataFrame(Simulated_Prices)
                        Simulated_Prices = Simulated_Prices.sort_values(by = 0)
                        
                        NextDayEstimate = pd.DataFrame(Simulated_Prices[0]).mean()
                        NextDayEstimate = round_to_multiple(NextDayEstimate.iloc[0], 5)
                        
                        QuartileOne = math.floor(Simulated_Prices[0].quantile([0.25]).iloc[0]) - NextDayEstimate * (Daily_Vol)#round_to_multiple(NextDayEstimate * (Daily_Vol * 2), 5)
                        QuartileThree = math.ceil(Simulated_Prices[0].quantile([0.75]).iloc[0]) + NextDayEstimate * (Daily_Vol)#round_to_multiple(NextDayEstimate * (Daily_Vol * 2) , 5)
                        
                        Range_Spread = round(((QuartileThree - NextDayEstimate) +  (NextDayEstimate - QuartileOne)) / 2)
                        
                        # if Range_Spread >= 9999999 + NextDayEstimate * (Daily_Vol* 3):
                        #     head_size = head_size + 1
                        #     continue
                        # else:
                        
                        Prediction_Date = str(Underlying['Date'][head_size+(period_size+1)])
                            
                        Prediction_Dates.append(Prediction_Date)
                    
                        print('\nNext Day(',Prediction_Date,') Estimated Price:', NextDayEstimate)
                        print('Expected Range:', QuartileOne, 'to', QuartileThree)
                        
                        Realized = Underlying['Adj Close'][head_size + period_size+1]
                        
                        Actual.append(Realized)
                        print('Actual:', Realized)
                        
                        Predicted.append(NextDayEstimate)
                        
                        print('Difference:',( abs(Realized - NextDayEstimate) / NextDayEstimate)  * 100, '%')
                        
                        print('Period of Days:', period_size)
                        
                        if Realized >= QuartileOne and Realized <= QuartileThree:
                            Within_Range = 'True'
                        else:
                            Within_Range = 'False'
                        
                        Range_String = 'Was Price Within Range?: ' + str(Within_Range)
                        
                        print(Range_String)
                        
                        Ranges.append(Within_Range)
                        
                        print('Range Spread:', Range_Spread, '$')
                        
                        Range_Spreads.append(Range_Spread)

                        head_size = head_size + 1
                            
                            
                               
                    except Exception as _:
                        break
            
            
                Predicted_Actual = pd.concat([pd.DataFrame(Actual), pd.DataFrame(Predicted)], axis = 1)
                Predicted_Actual.columns = ['Actual','Predicted']
                Predicted_Actual['Difference'] = abs(Predicted_Actual['Actual'] - Predicted_Actual['Predicted'])
                Average_Difference = Predicted_Actual['Difference'].mean() / Predicted_Actual['Actual'].mean()
                
                
                Difference_String = '\nAverage Difference: ' + str(Average_Difference *100) + ' %' + ' Period: ' + str(period_size) + ' Days'    
                Differences.append(Difference_String)
                
                print(Difference_String)
                
                Range_DataFrame = pd.concat([pd.DataFrame(Ranges)])
                Range_DataFrame.columns = ['Boolean']
                
                Times_Within = len(Range_DataFrame[Range_DataFrame['Boolean'] == 'True'])
                
                Range_Text = 'Within Range: ' + str(Times_Within / len(Range_DataFrame) * 100) + '% of the time ' + 'for the ' + str(period_size) + ' Day Period' + ' Trade Count: ' + str(len(Ranges)) + ' Average Range Spread: ' + str(round_to_multiple(numpy.mean(Range_Spreads) , 5))
                Range_Percents.append(Range_Text)
                
                print(Range_Text)

        except:
            
            break
        
# Live Calculations

def Kalshi_Calc():
    
    while 1:
    
        Kalshi_Data = yf.download(tickers = '^GSPC', start = '2022-07-24', end = '2022-09-04', interval = '15m')
        
        Underlying = Kalshi_Data.reset_index()
        Underlying = Underlying.rename(columns = {'Datetime':'Date'})
        Underlying['Returns'] = Underlying['Adj Close'].pct_change().fillna(0)
        Underlying['Returns'] = numpy.log(1 + Underlying['Returns'])
        
        Expected_Ranges = []
        
        for aa in range(5, len(Underlying), int((len(Underlying) / 3))):
            
            head_size = 0
            
            period_size = aa
            
            for a in range(2, round(len(Underlying))):  
                    Simulated_Prices = []
                    
                    TPlusOne = pd.DataFrame(Underlying['Adj Close'][head_size:head_size + period_size])
                    TPlusOne_Original = pd.DataFrame(Underlying[head_size:head_size + period_size])
                    TPlusOne['Returns'] = TPlusOne.pct_change().fillna(0)
                    TPlusOne['Returns'] = numpy.log(1 + TPlusOne['Returns'])
                    Daily_Vol = numpy.std(TPlusOne['Returns'])
                    Drift = TPlusOne['Returns'].tail(2).mean() * 10000
                    
                    Last_Value = Underlying.tail(1)['Adj Close'].iloc[0]
                    
                    
                    for c in range(0, 10000):
                        
                        if (c % 2) == 0:
                            # PlusOneDay = round_to_multiple((Last_Value + Last_Value * random.uniform(-Daily_Vol, Daily_Vol)) + Drift , 5)
                            PlusOneDay = Last_Value - Last_Value * abs(random.uniform(-Daily_Vol, Daily_Vol) * -1) - abs((Drift * 0.50))
                            
                        else:
                            # PlusOneDay = round_to_multiple((Drift * TPlusOne) + (TPlusOne + TPlusOne * random.uniform(-Daily_Vol, Daily_Vol)), 5)
                            # PlusOneDay = round_to_multiple((Last_Value - Last_Value * random.uniform(-Daily_Vol, Daily_Vol)) - Drift , 5)
                            PlusOneDay = Last_Value + Last_Value * abs(random.uniform(-Daily_Vol, Daily_Vol)) + abs((Drift * 0.50))
                            
                        Simulated_Prices.append(PlusOneDay)
                    
                    # Simulated_Prices = pd.DataFrame(Simulated_Prices)
                    Simulated_Prices.sort()
                    
                    NextDayEstimate = numpy.mean(Simulated_Prices)
                    NextDayEstimate = round_to_multiple(NextDayEstimate, 5)
                    
                    QuartileOne = math.floor(pd.DataFrame(Simulated_Prices)[0].quantile([0.25])) - NextDayEstimate * (Daily_Vol)#round_to_multiple(NextDayEstimate * (Daily_Vol * 2), 5)
                    QuartileThree = math.ceil(pd.DataFrame(Simulated_Prices)[0].quantile([0.75])) + NextDayEstimate * (Daily_Vol)#round_to_multiple(NextDayEstimate * (Daily_Vol * 2) , 5)
                    
                    Range_Spread = round(((QuartileThree - NextDayEstimate) +  (NextDayEstimate - QuartileOne)) / 2)
                    
                    if Underlying['Date'][head_size + (period_size)] == Underlying['Date'].tail(1).iloc[0]:
    
                        Prediction_Date  = Underlying['Date'].tail(1).iloc[0] + timedelta(minutes = 15)
        
                        Expected_Range_String = str(QuartileOne) + ' to ', str(QuartileThree) + ' On ' + str(Prediction_Date) + ' Period Size: ' + str(period_size)
                    
                        Expected_Ranges.append(Expected_Range_String)
                        
                        print(QuartileOne, 'to', QuartileThree, 'on', Prediction_Date, 'Last:', str(Last_Value), 'Spread:', str(Range_Spread))
                        
                        break
                    else:
                        pass
                       
                    head_size = head_size + 1
