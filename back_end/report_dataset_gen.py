#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 20:37:41 2024

@author: Lerberber
"""


"""
Collecting historical data: 
    
- Similar SWE years
How to fine this unregualted run off (hydromet tools) -- finds volume in the range of dates
- find unregulated run-off for these years ( volume in 1000 AF) Percent of normal 1991 -2020 period 
- percipitation -- basin conditions for one month -- percent average for 122 period (USBR)
- snow similarity -- 
- soil moisture -- 


"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cdist
from scipy.stats import pearsonr, entropy
import requests
from datetime import datetime
from similar_years import *
from daily_data import *
# from get_precipitation import get_precipitation_data
# from get_soil_moisture import *
from get_precipitation import * 
from observed_flow import *
from get_soil_moisture import *
from snow_data import * 




def color_based_on_similarity(score):
    """
    Assign a color based on the similarity score.
    The closer the score is to 0, the more similar the years are.
    """
    if score < 0.6:
        return 'green'
    elif score < 0.7:
        return 'yellow'
    elif score < 0.8:
        return 'orange'
    else:
        return 'red'

def generate_report_data(basin, station_list, date):
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    # Convert date string to datetime object
    date = pd.to_datetime(date)
    # Get the year, month, and day from the date
    year = date.year
    month = date.month
    day = date.day
    
    df = []
    current_df = pd.DataFrame()  # DataFrame to hold current year data
    graph_data = pd.DataFrame() 
     
    
    #Note to self... Include current year of comparison in dataset or hover capability
    
    #collect daily values for snow water equivalent 
    wteq_avg , wteq_med = get_daily_water_year(BASE_URL, station_list, 'WTEQ', date)
    
    

    #Find similar years for snow water equivalent
    # Load the sorted data and set the correct index
    # sorted_avg_data = pd.read_csv('sorted_water_year_avg.csv', index_col=0)
    # sorted_med_data = pd.read_csv('sorted_water_year_med.csv', index_col=0)
    datasets = [wteq_avg, wteq_med]
    
    #get average WTEQ SCORE for current year and append it  
    
    
    similar_years_scores = find_similar_years_across_datasets(year, datasets, month, day, threshold=0.90, n=8)



    
    # Define the score column name
    score_column_name = 'WTEQ_similarity_score_Wasserstein'
    
    # Create the DataFrame
    df = pd.DataFrame(similar_years_scores, columns=['year', 'month', 'day', score_column_name])
    # take similar_years and get WTEQ DATA for each year append it to graph data. 
    # Set the 'year' column as the index
    df.set_index('year', inplace=True)
    df.index = df.index.astype(int)
    
    # Drop the 'month' and 'day' columns as they are not needed for now
    df.drop(columns=['month', 'day'], inplace=True)
    
    # Apply color based on similarity score
    df['color'] = df[score_column_name].apply(color_based_on_similarity)
    

    # ADD WTEQ DATA TO GRAPH DF 
    years = df['year'].to_list()
    # years.append(str(year))
    graph_years = years + [year]
    # Iterate over each year in graph_years and collect the WTEQ data
    for similar_year in graph_years:
        # Extract the WTEQ data for the current year/column
        year_data = wteq_avg[wteq_avg.index.year == similar_year]
        year_data_med = wteq_med[wteq_med.index.year == similar_year]
        
        # Add the data to the graph_data DataFrame as columns
        graph_data[str(similar_year) + '_WTEQ_avg'] = year_data.values
        graph_data[str(similar_year) + '_WTEQ_med'] = year_data_med.values
    
    # Add the date index for the graph_data
    graph_data['date'] = wteq_avg.index.strftime('%m-%d')
    
    

    
   
    # get precipitation 
    prec = get_percent_normal_prec(years, month, day, station_list, BASE_URL)
    
    # Set 'year' as index for both DataFrames and convert to integer
    merged_df = df.merge(prec, left_index=True, right_index=True, how='left')
    merged_df.rename(columns={'percent_normal': '122 day Precipitation(%)'}, inplace=True)
    
    obsv_flow = get_observed_flow(station_list, BASE_URL, month, day, years)
    # Set 'year' as index for both DataFrames and convert to integer
    merged_df = merged_df.merge(obsv_flow, left_index=True, right_index=True, how='left')
    # obsv_flow.rename(columns={'value': '122-Day Mean Stream Volume (SRVOO)'}, inplace=True)
    # Rename the column if needed
    # years
    # year
    soil_moisture = get_soil(station_list, BASE_URL, month, day, year, years)
    # soil_moisture
    merged_df = merged_df.merge(soil_moisture, left_index=True, right_index=True, how='left')    
  
    
    snow_depth =  get_snow_coverage_data(years, month, day, year, station_list, BASE_URL)
    merged_df = merged_df.merge(snow_depth, left_index=True, right_index=True, how='left')  
    
    
    # merged_df
    merged_df.reset_index(inplace=True)
    
    
    return merged_df
    
    
    
    
    

#     # Perocesses it 

if __name__ == "__main__":
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    sntl_owy =  ['336:NV:SNTL','13183000:OR:USGS','13174500:NV:USGS','13181000:OR:USGS', '1262:NV:SNTL', '548:NV:SNTL', 
                                  '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
    # end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = '2024-03-16'
    
    df = generate_report_data('basin', sntl_owy, end_date)
     
    
