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



        

        
        
        
    
            


  
if __name__ == "__main__":
   sorted_avg_data = pd.read_csv('sorted_water_year_avg.csv', index_col=0)
   sorted_med_data = pd.read_csv('sorted_water_year_med.csv', index_col=0)
   # 
   datasets = [sorted_avg_data, sorted_med_data]
   similar_years_across = find_similar_years_across_datasets('2024', datasets, 3, 1, threshold=0.85, n=7)
   years = [year for year, value in similar_years_across]


    # Load the sorted data and set the correct index
    
    # sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
    # filename = 'prec.csv'
    # elements = "WTEQ"
    # duration = "DAILY"
    # end_date = datetime.now().strftime("%Y-%m-%d")
    # central_tendency_type = "AVERAGE"