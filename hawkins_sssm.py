
# coding: utf-8

# In[5]:

import pandas as pd
import numpy as np
import datetime
import argparse
import sys
import os.path
from scipy.stats.mstats import gmean
import scipy


# creating dataframe for retrieving the provided details on stocks from "Table1" 
columns = ['Stock Symbol', 'Type', 'Last Dividend', 'Fixed Dividend', 'Par Value']
data = np.array([('TEA', 'Common', 0, np.nan, 100), 
                 ('POP', 'Common', 8, np.nan, 100), 
                 ('ALE', 'Common', 23, np.nan, 60), 
                 ('GIN', 'Preferred', 8, 0.02, 100), 
                 ('JOE', 'Common', 13, np.nan, 250)])             
GBCE = pd.DataFrame(data, columns=columns)

# creating the dataframe for saving trades. 
# but first I'm checking for a pickle of previously saved trades. If it's there I don't want to create the dataframe
local_file_path = sys.path[0]
pickle_location = local_file_path + '\\recorded_trades.pkl'
if os.path.exists(pickle_location) == False:
    columns = ['Stock Symbol', 'Time of trade', 'Quantity traded', 'Buy or Sell Indicator', 'Traded price']
    recorded_trades = pd.DataFrame(columns=columns)
    
    
else:
    recorded_trades = "look for dataframe on local directory"

def calculate_dividend_yield(GBCE, stock, price):
    '''
    For given stock, iven any price as input, calculate the dividend yield
    
    For 'commmon' stocks: last dividend / price
    
    For 'preferred stocs: (fixed dividends .par value) / price
    '''
    # make a selection of the stock the user selected, accounting for lower case
    selected_stock = GBCE.loc[GBCE['Stock Symbol'] == stock.upper()]
    
    # retrieve whether the stock is common or preferred, last dividend and par value
    stock_type = selected_stock.iloc[0]['Type']
    last_dividend = int(selected_stock.iloc[0]['Last Dividend'])
    par_value = int(selected_stock.iloc[0]['Par Value'])

    # run common or preferred dividend yield calculation based on type of stock
    if stock_type == 'Common':
        dividend_yield = last_dividend / price
    
    elif stock_type == "Preferred":
        fixed_dividend = float(selected_stock.iloc[0]['Fixed Dividend'])
        dividend_yield = (fixed_dividend * par_value) / price
    
    return dividend_yield
    
    
def calculate_P_E_ratio(GBCE, stock, price):
    '''
    For given stock, given any price as input,  calculate the P/E Ratio 
    
    P/E Ratio = price / dividend
    '''
    # find the dividend from calculate_dividend_yield function and calculate p/e ratio 
    dividend = calculate_dividend_yield(GBCE, stock, price)
    if dividend != 0:
        P_E_ratio = price / dividend
        return P_E_ratio
    # not all stocks had have a dividend. Can't divide by zero
    else: 
        P_E_ratio = "Last dividend is zero"
        return P_E_ratio

def record_trade(recorded_trades, stock, quantity, transaction_type, price, pickle_location):
    '''
    Record a trade, with timestamp, quantity of shares, buy or sell indicator and traded price 
    '''
    # find the current data and time. 
    timestamp = datetime.datetime.now()
    
    # create a temporary dataframe to save the current transaction in order to append it to all recorded transactions df
    columns = ['Stock Symbol', 'Time of trade', 'Quantity traded', 'Buy or Sell Indicator', 'Traded price']
    data = np.array([(stock, timestamp, quantity, transaction_type, price)])             
    new_transaction = pd.DataFrame(data, columns=columns)
    
    # if this is the first time running this code there a pickle of recorded trades will not exist on the user's computer
    if type(recorded_trades) != str:
        # append new transaction to recorded transactions
        recorded_trades = recorded_trades.append(new_transaction, ignore_index=True)
        recorded_trades['Traded price'] = recorded_trades['Traded price'].astype(int)
        recorded_trades['Quantity traded'] = recorded_trades['Quantity traded'].astype(int)
        recorded_trades.to_pickle(pickle_location)
    
    else:
        recorded_trades = pd.read_pickle(pickle_location)
        recorded_trades = recorded_trades.append(new_transaction, ignore_index=True)
        recorded_trades['Traded price'] = recorded_trades['Traded price'].astype(int)
        recorded_trades['Quantity traded'] = recorded_trades['Quantity traded'].astype(int)
        recorded_trades.to_pickle(pickle_location)
    return recorded_trades


def calculate_volume_weighted_stock(pickle_location):
    '''
    Calculate Volume Weighted Stock Price based on trades in past 15 minutes 
    (all traded prices x quantity) / quantity
    '''
    # user may not have registered any trades yet
    if os.path.exists(pickle_location) == True:
        
        # fid the time from 15 minutes ago and find all saved trades from the pickle
        time_15_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
        recorded_trades = pd.read_pickle(pickle_location)
        
        # make sure date times are in fact date times in recorded trades and mas anything that's earlier than 15 minutes ago
        recorded_trades['Time of trade'] = pd.to_datetime(recorded_trades['Time of trade'])  
        mask = (recorded_trades['Time of trade'] > time_15_minutes_ago)
        recorded_trades = recorded_trades.loc[mask]
        
        # if there are trades but non in the last 15 minutes i'll get an empty dataframe and crash. 
        if recorded_trades.shape[0] > 0:
        
            # run the VWSP calculation
            recorded_trades['Total trade cost'] = recorded_trades['Traded price'] + recorded_trades['Quantity traded']
            total_trade_cost = sum(recorded_trades['Total trade cost'])
            total_number_trades = sum(recorded_trades['Quantity traded'])
            volume_weighted_stock_price = total_trade_cost / total_number_trades
            return   int(volume_weighted_stock_price)
        
        else:
            return "There are no trades recorded"
    else:
        return "There are no trades recorded"

def calculate_geometric_mean(pickle_location):
    '''
    square root^n (price1*price2*price3)
    '''
    recorded_trades = pd.read_pickle(pickle_location)
    recorded_trades['Traded price'] = recorded_trades['Traded price'].astype(int)
    geo = scipy.stats.mstats.gmean(recorded_trades['Traded price'])
    return geo
    
    
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dividend",  help="Enter stock symbol to find dividend yield")
parser.add_argument("-r", "--ratio", help="Enter stock symbol to find the P/E ratio")
parser.add_argument("-t", "--trade", help="Enter stock symbol to record a trade")
parser.add_argument("--vwsp", action='store_true', help="Enter '--vwsp' to find Volume Weighted Stock Price based on trades in past 15 minutes")
parser.add_argument("--geo", action='store_true', help="Enter '--geo' GBCE All Share Index using the geometric mean of prices for all stocks")
args = parser.parse_args()

if args.dividend:
    args.price = int(input('Enter price: '))
    dividend_yield = calculate_dividend_yield(GBCE, args.dividend, args.price)
    print (" Dividend yield:")
    print (dividend_yield)

elif args.ratio:
    args.price = float(input('Enter price: '))
    peRatio = calculate_P_E_ratio(GBCE, args.ratio, args.price)
    print ("P/E Ratio:")
    print (peRatio)

elif args.trade:
    args.transaction_type = (input("Enter 'buy' or 'sell' "))
    args.price = float(input('Enter price: '))
    args.quantity = float(input('Enter quantity: '))
    trades = record_trade(recorded_trades, args.trade, args.quantity, args.transaction_type, args.price, pickle_location)
    print ("Trade recorded")

elif args.vwsp == True:
    volume_weighted_stock_price = calculate_volume_weighted_stock(pickle_location)
    print ("Volume weighted stock price:")
    print (volume_weighted_stock_price)
    
elif args.geo == True:
    geo = calculate_geometric_mean(pickle_location)
    print ("Geometric mean:")
    print (geo)


# In[ ]:




# In[ ]:



