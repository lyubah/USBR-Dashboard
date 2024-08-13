#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 13:51:35 2024

@author: Lerberber
"""
import requests
import pandas as pd
from datetime import datetime
# from data_comparison import sort_water_year
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from daily_data import * 
from datetime import datetime, timedelta
import requests
import pandas as pd




def get_average(df):
   return df.groupby('year')['value'].mean()

    




def calculate_122_day_period(year, month, day):
    year = int(year)
    month = int(month)
    day= int(day)
    start_date = datetime(year, month, day)
    end_date = start_date + timedelta(days=121)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def get_parameters(station_triplets, start_date, end_date):
    """
    Collects common parameters for both stations and data endpoints.
    """
    elements = '*'
    duration = "DAILY"
    central_tendency_type = "ALL"
    return_flags = False
    params = {
        "stationTriplets": station_triplets,
        "elements": elements,
        "duration": duration,
        "beginDate": start_date,
        "endDate": end_date,
        "centralTendencyType": central_tendency_type,
        "returnFlags": False
    }
    return params

def get_station_data(params, BASE_URL):
    """
    Retrieves observational data from the stations using the data endpoint.
    """
    endpoint = "data"
    url = f"{BASE_URL}/{endpoint}"
    
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    full_url = f"{url}?{query_string}"
    
    response = requests.get(full_url)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


def relevant_data(data):
    """
    Extracts relevant data from the JSON response and returns a DataFrame.
    Note: may not want average and median values.
    """
    relevant_data = []
    for station in data:
        station_triplet = station['stationTriplet']
        for record in station['data']:
            element_code = record['stationElement']['elementCode']
            for value in record['values']:
                date = datetime.strptime(value['date'], '%Y-%m-%d').date()
                average = -1 if value.get('average') is None else value['average']
                median = -1 if value.get('median') is None else value['median']
                relevant_data.append({
                    'stationTriplet': station_triplet,
                    'elementCode': element_code,
                    'date': date,
                    'year': date.year,
                    'month': date.month,
                    'month_day': date.strftime('%m-%d'),
                    'value': value['value'],
                    'average': average,
                    'median': median
                })
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(relevant_data)
    
    return df

def get_observed_flow(station_lists, BASE_URL, month, day, years):
    
    all_observed_flow = pd.DataFrame()

    stations = [station for station in station_lists if "USGS" in station]
    
    for year in years:
        start_date, end_date = calculate_122_day_period(year, month, day)
        
        print(f"Start Date: {start_date}, End Date: {end_date}")
        
        # Fetch data for each station
        data_frames = []
        for station in stations:
            print(f"Fetching data for station: {station}")
            params = get_parameters(station, start_date, end_date)
            data = get_station_data(params, BASE_URL)
            if data:
                df = relevant_data(data)
                print(f"Processed data for station: {station}")
                if not df.empty:
                    data_frames.append(df)
            else:
                print(f"No data returned for station: {station}")
        
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            
            all_observed_flow = pd.concat([all_observed_flow, combined_df], ignore_index=True)
    
    # START HERE
    # get an average for each year 
    df = get_average(all_observed_flow)
    df.rename('122-Day Mean Stream Volume (SRVOO)', inplace=True)
 
    
    
        
    return df




# # Example usage
# if __name__ == "__main__":
#     BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
#     station_lists = ['336:NV:SNTL', '13183000:OR:USGS', '13174500:NV:USGS', '13181000:OR:USGS']
#     month = 3
#     day = 1
#     years = ['1999', '2023', '2017', '1997', '2006', '2004', '2002']
    
#     observed_flow_data = get_observed_flow(station_lists, BASE_URL, month, day, years)
#     print(observed_flow_data.head())