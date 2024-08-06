#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 13:04:57 2024

@author: Lerberber


- The purpose of this file is to convert the dataframes to a simliar dataset used in the graphing of the usbr data sets
- the indeces are supposed to be as follows: date-month , years , avg 
- from there we will use the eucledian distances. 

"""

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
# from daily_data import * 

# original_data = pd.read_csv('owyhee_aws.csv')
# agg_average_data = pd.read_csv('daily_owy_agg_average.csv')
# agg_median_data = pd.read_csv('daily_owy_agg_median.csv')
# daily_pulled = pd.read_csv('daily_owy.csv')


# Convert 'date' column to datetime and extract month and day for indexing
def preprocess_agg_data(df):
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows where date conversion failed
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    df['year'] = df['date'].dt.year
    return df

# agg_avg_df = preprocess_agg_data(agg_average_data).drop(columns=['date'])
# agg_med_df = preprocess_agg_data(agg_median_data).drop(columns=['date'])

# Pivot the data to have 'month_day' as index and years as columns
def pivot_data(df, value_column):
    pivot_df = df.pivot(index='month_day', columns='year', values=value_column)
    pivot_df.reset_index(inplace=True)

    return pivot_df

# pivoted_values_avg = pivot_data(agg_avg_df, 'value')
# pivoted_values_med = pivot_data(agg_med_df, 'value')





# Function to sort data by water year
def sort_water_year(df):
    # Convert 'month_day' to datetime format
    df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')
    # df = df.dropna(subset=['month_day'])  # Drop rows where date conversion failed
    
    # Adjust the dates to align with the water year
    df['adjusted_date'] = df['month_day'].apply(lambda x: x.replace(year=2000) if x.month >= 10 else x.replace(year=2001))
    
    # Sort by the adjusted date
    df = df.sort_values('adjusted_date')
    
    # Convert 'month_day' back to string format and set it as index
    df['month_day'] = df['month_day'].dt.strftime('%m-%d')
    df.set_index('month_day', inplace=True)
    df.drop(columns=['adjusted_date'], inplace=True)
    
    # # Drop the 'adjusted_date' column
    # df.drop(columns=[1980, 'adjusted_date'], inplace=True)
    df = df.iloc[:-1]
    
    return df

# # Function to sort data by water year
# def sort_water_year(df):
#     # Convert 'month_day' to datetime format
#     df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')
    
#     # Adjust the dates to align with the water year
#     df['adjusted_date'] = df['month_day'].apply(lambda x: x.replace(year=2000) if x.month >= 10 else x.replace(year=2001))
    
#     # Sort by the adjusted date
#     df = df.sort_values('adjusted_date')
    
#     # Convert 'month_day' back to string format and set it as index
#     df['month_day'] = df['month_day'].dt.strftime('%m-%d')
#     df.set_index('month_day', inplace=True)
    
#     # Drop the 'adjusted_date' column
#     df.drop(columns=['adjusted_date'], inplace=True)
    
#     # Adjust column names to reflect the water year
#     new_columns = {col: col + 1 for col in df.columns if isinstance(col, int)}
#     df = df.rename(columns=new_columns)
    
#     return df
 
# df_avg = sort_water_year(pivoted_values_avg)
# df_med = sort_water_year(pivoted_values_med)

# df_med.to_csv("def_med_for_sim.csv")
# df_avg.to_csv("def_avg_for_sim.csv")


# original_data = original_data.iloc[: , :-9]
# # compare  original_data, df_avg, and df_med
# original_data.head()

# original_data.head()