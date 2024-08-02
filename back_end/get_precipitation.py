#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:55:39 2024

@author: Lerberber
"""
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cdist
from scipy.stats import pearsonr, entropy
import requests
from datetime import datetime, timedelta

from similar_years import *


def get_parameters(station_triplet, begin_date, end_date):
    return {
        "stationTriplets": station_triplet,
        "elements": "PREC",
        "duration": "DAILY",
        "beginDate": begin_date,
        "endDate": end_date,
        "centralTendencyType": "AVERAGE",
        "returnFlags": False
    }

def get_station_data(params):
    url = f"{BASE_URL}/data"
    response = requests.get(url, params=params)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def process_data(station_data):
    """
    Extracts relevant data from the JSON response.
    """
    records = []
    for station in station_data:
        station_triplet = station['stationTriplet']
        for record in station['data'][0]['values']:
            average = record.get('average')
            if average is not None:  # Only include records with average values
                records.append({
                    'stationTriplet': station_triplet,
                    'date': record['date'],
                    'value': record['value'],
                    'average': average
                })
    return pd.DataFrame(records)


def calculate_122_day_period(year, month, day):
    start_date = datetime.datetime(year, month, day)
    end_date = start_date + timedelta(days=121)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')



def calculate_average(df):
    total_precipitation = df['value'].sum()
    total_average_precipitation = df['average'].sum()
    percent_of_average = (total_precipitation / total_average_precipitation) * 100
    return percent_of_average


# def get_average(year, month, date, stations):
#     # Fetch data for each station
#     data_frames = []
#     begin_date = '2016-03-01'
#     # end_date = '2016-06-30'

#     for station in sntl_owy:
#         params = get_parameters(station, begin_date, end_date)
#         data = get_station_data(params)
#         if data:
#             df = process_data(data)
#             data_frames.append(df)
            
#     # Combine all data frames
#     combined_df = pd.concat(data_frames)
#     average = calculate_average(df)



def get_average(year, month, day, stations):
    start_date, end_date = calculate_122_day_period(year, month, day)
    
    # Fetch data for each station
    data_frames = []
    for station in stations:
        params = get_parameters(station, start_date, end_date)
        data = get_station_data(params)
        if data:
            df = process_data(data)
            if not df.empty:
                data_frames.append(df)
    
    # Combine all data frames
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df.to_csv('2019.csv')
        average = calculate_average(combined_df)
        return average
    else:
        print("No data available with average values for the selected stations and date range.")
        return None



years = ['2006', '2017', '1999', '2020', '2019', '1997', '1993', '1982']
sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"

average_precipitation = get_average(2019, 3, 1, sntl_owy)
average_precipitation


# combined_df.to_csv('precipUnAgg.csv')
