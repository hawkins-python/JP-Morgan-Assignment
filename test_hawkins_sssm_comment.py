
# coding: utf-8

# In[1]:





import unittest
import pandas as pd
import numpy as np
import os
import os.path
import sys

from pandas.util.testing import assert_frame_equal
from scipy.stats.mstats import gmean
import scipy

from hawkins_sssm import calculate_dividend_yield
from hawkins_sssm import calculate_P_E_ratio
from hawkins_sssm import record_trade
from hawkins_sssm import calculate_volume_weighted_stock
from hawkins_sssm import calculate_geometric_mean



class hawkins_sssmTestCase(unittest.TestCase):
    """Tests for `hawkins_sssm.py`."""
    def test_ale_99_calculate_dividend_yield(self):
        '''
        To test calculate_dividend I'm going to fake some user inputs and check that I get the correct result
        '''
        # creating dataframe for retrieving the provided details on stocks from "Table1" 
        columns = ['Stock Symbol', 'Type', 'Last Dividend', 'Fixed Dividend', 'Par Value']
        data = np.array([('TEA', 'Common', 0, np.nan, 100), 
                 ('POP', 'Common', 8, np.nan, 100), 
                 ('ALE', 'Common', 23, np.nan, 60), 
                 ('GIN', 'Preferred', 8, 0.02, 100), 
                 ('JOE', 'Common', 13, np.nan, 250)])   
        GBCE = pd.DataFrame(data, columns=columns)
        stock = 'ale'
        price = 10
        assert(calculate_dividend_yield(GBCE, stock, price) == 2.3)

        
    def test_ale_99_calculate_P_E_ratio(self):
        '''
        To test calculate_P_E_ratio I'm going to fake some user inputs and check that I get the correct result
        '''
        # creating dataframe for retrieving the provided details on stocks from "Table1" 
        columns = ['Stock Symbol', 'Type', 'Last Dividend', 'Fixed Dividend', 'Par Value']
        data = np.array([('TEA', 'Common', 0, np.nan, 100), 
                 ('POP', 'Common', 8, np.nan, 100), 
                 ('ALE', 'Common', 23, np.nan, 60), 
                 ('GIN', 'Preferred', 8, 0.02, 100), 
                 ('JOE', 'Common', 13, np.nan, 250)])   
        GBCE = pd.DataFrame(data, columns=columns)
        # user inputs
        stock = 'gin'
        price = 5
        assert(calculate_P_E_ratio(GBCE, stock, price) == 12.5)
        
    def test_record_trades(self):
        '''
        To test I'm going to create a dummy data frame with three trades. Then run those three trades and compare the 
        two data frames
        '''
        
        #get the local file path and delete the test pickle if it exists
        local_file_path = sys.path[0]
        pickle_location = local_file_path + '\\recorded_trades_unit_test.pkl'
        if os.path.exists(pickle_location) == True:
            os.remove(pickle_location)
        # empty dataframe to save to. 
        columns = ['Stock Symbol', 'Time of trade', 'Quantity traded', 'Buy or Sell Indicator', 'Traded price']
        recorded_trades = pd.DataFrame(columns=columns)
        recorded_trades.to_pickle(pickle_location)
        
        # create a dummy dataframe that has 'recorded' trades to compare my result with
        data = np.array([('tea', 'some_date_time', 88, 'buy', 108), ('gin','some_date_time', 44, 'sell', 40), ('pop', 'some_date_time', 88, 'buy', 99)])   
        correct_df_for_comparison = pd.DataFrame(data, columns=columns)
        correct_df_for_comparison['Quantity traded'] = correct_df_for_comparison['Quantity traded'].astype(int)
        correct_df_for_comparison['Traded price'] = correct_df_for_comparison['Traded price'].astype(int)
        
        # loop through 3 dummy trades and run function record_trade
        trades_to_record = [['tea', 88, 'buy', 108], ['gin', 44, 'sell', 40], ['pop', 88, 'buy', 99]]
        for stock, quantity, transaction_type, price in trades_to_record:
            recorded_trades = pd.read_pickle(pickle_location)
            returned_df = record_trade(recorded_trades, stock, quantity, transaction_type, price, pickle_location)
        
        # As I can't create the dummy dataframe at the exact time the real frame is created I drop this column for comparison
        returned_df = returned_df.drop('Time of trade', 1)
        correct_df_for_comparison = correct_df_for_comparison.drop('Time of trade', 1)            
        assert_frame_equal(returned_df, correct_df_for_comparison)

    def test_calculate_volume_weighted_stock(self):
        '''
        to test I'm going to create a dummy dataframe with three entries with timestamps earlier than 15 minutes ago.
        Then run TWO trades using function record_trades. If the calculation is only run on the last two the 
        answer should be '2'
        
        '''
        # grab the file location and delte the pickle if it's there. If it's already there it will affect my results
        local_file_path = sys.path[0]
        pickle_location = local_file_path + '\\recorded_trades_unit_test.pkl'
        if os.path.exists(pickle_location) == True:
            os.remove(pickle_location)
            
        # create the dataframe I'm going to add my two new trades to.     
        columns = ['Stock Symbol', 'Time of trade', 'Quantity traded', 'Buy or Sell Indicator', 'Traded price']
        data = np.array([('gin', '2012-10-03 15:35:46.461491', 10000, 'buy', 10000), 
                         ('gin','2012-10-03 15:35:46.461491', 200000, 'sell', 20000), 
                         ('pop', '2012-10-03 15:35:46.461491', 30000, 'buy', 30000)])        
   
        recorded_trades = pd.DataFrame(data, columns=columns)
        recorded_trades['Time of trade'] = pd.to_datetime(recorded_trades['Time of trade'])
        recorded_trades.to_pickle(pickle_location)
        
        # record two trades
        trades_to_record = [['tea', 80, 'buy', 100], ['gin', 40, 'sell', 40]]
        for stock, quantity, transaction_type, price in trades_to_record:
            recorded_trades = pd.read_pickle(pickle_location)
            returned_df = record_trade(recorded_trades, stock, quantity, transaction_type, price, pickle_location)

        # ensure only the last two trades were included in the calculation
        vwsp = calculate_volume_weighted_stock(pickle_location)
        assert(vwsp == 2)
        
    def test_calculate_geometric_mean(self):
        '''
        Very simple test. Dummy a few trades. Save that to pickle. Then run the gmean function in scipy 
        in the test and in the function. If the results match it works
        '''
        # delete the pickle if it's already there. Existing pickle would affect my results. 
        local_file_path = sys.path[0]
        pickle_location = local_file_path + '\\recorded_trades_unit_test.pkl'
        if os.path.exists(pickle_location) == True:
            os.remove(pickle_location)
        
        # create and save the data frame to run gmean on 
        columns = ['Stock Symbol', 'Time of trade', 'Quantity traded', 'Buy or Sell Indicator', 'Traded price']
        data = np.array([('gin', '2012-10-03 15:35:46.461491', 10000, 'buy', 10), 
                         ('gin','2012-10-03 15:35:46.461491', 200000, 'sell', 10), 
                         ('pop', '2012-10-03 15:35:46.461491', 30000, 'buy', 10)])        
        
        recorded_trades = pd.DataFrame(data, columns=columns)
        recorded_trades['Time of trade'] = pd.to_datetime(recorded_trades['Time of trade'])
        recorded_trades.to_pickle(pickle_location)
        recorded_trades['Traded price'] = recorded_trades['Traded price'].astype(int)
        geo = scipy.stats.mstats.gmean(recorded_trades['Traded price'])
        # check that both calculations match
        assert(calculate_geometric_mean(pickle_location) == geo)

        
if __name__ == '__main__':
    unittest.main()




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



