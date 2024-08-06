#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 16:16:01 2024

@author: Lerberber
"""
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"

#tabular
def get_soil_moisture_data(station_triplet, begin_date, end_date):
    """
    Fetches soil moisture data for the specified station triplet and date range.
    """
    params = {
        "stationTriplets": station_triplet,
        "elements": "SMS",
        "duration": "DAILY",
        "beginDate": begin_date,
        "endDate": end_date,
        "centralTendencyType": "ALL",
        "returnFlags": False
    }
    url = f"{BASE_URL}/data"
    response = requests.get(url, params=params)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


# # tabularize and order in water years 
# def process_and_save():
    



# #takes historic data up until a certain point and compares it to "current data"
# def similar_years():
    
    


# #returns this as a column 









# Example usage:
station_triplet = '1136:NV:SNTL	'
begin_date = '1980-10-01'
end_date = '2023-12-31'
soil_moisture_data = get_soil_moisture_data(station_triplet, begin_date, end_date)
# soil_moisture_df = process_soil_moisture_data(soil_moisture_data)
# print(soil_moisture_df.head())
