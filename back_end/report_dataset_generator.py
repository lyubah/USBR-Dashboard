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
from get_soil_moisture import get_soil_moisture_data

def generate_report_data(basin, station_list, date):
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    # Convert date string to datetime object
    date = pd.to_datetime(date)
    # Get the year, month, and day from the date
    year = date.year
    month = date.month
    day = date.day
    
    df = []
     
    
    #collect daily values for snow water equivalent 
    wteq_avg , wteq_med = get_daily_water_year(BASE_URL, station_list, 'WTEQ', end_date)

    #Find similar years for snow water equivalent
    # Load the sorted data and set the correct index
    # sorted_avg_data = pd.read_csv('sorted_water_year_avg.csv', index_col=0)
    # sorted_med_data = pd.read_csv('sorted_water_year_med.csv', index_col=0)
    datasets = [wteq_avg, wteq_med]
    similar_years_scores = find_similar_years_across_datasets(current_year, datasets, month, day, threshold=0.85, n=8)
        
    
    
    
    
    
#     #collect daily values for soil
#     get_daily_water_year(BASE_URL, sntl_lst, elements, end_date)
    
#     # Get precipitatoin 
#     soil_moisture_data = get_soil_moisture_data(basin, year, month, day)
    
#     # Find similar years
#     similar_years = find_similar_years(basin, year, month, day)
    
#     # Sort water years
#     water_years = sort_water_years(daily_data)
    
#     # Compare data
#     comparison_data = compare_data(daily_data, similar_years)
    
#     # Combine all data into a DataFrame
#     report_data = pd.DataFrame({
#         'Year': similar_years,
#         'Daily Data': daily_data,
#         'Precipitation Data': precipitation_data,
#         'Soil Moisture Data': soil_moisture_data,
#         'Comparison Data': comparison_data,
#         'Water Years': water_years
#     })
    
#     return report_data



# # grabs daily data for just wteq 


# # Perocesses it 

if __name__ == "__main__":
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL',  '549:NV:SNTL','573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL', '476:NV:SNTL', '1201:NV:SNTL',  ]
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    generate_report_data('basin', sntl_owy, end_date)
    
