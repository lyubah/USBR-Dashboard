import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cdist
from scipy.stats import pearsonr, entropy
import requests
from datetime import datetime

def get_parameters(station_triplets):
    """
    Collects common parameters for both stations and data endpoints.
    """
    elements = "WTEQ"
    duration = "DAILY"
    begin_date = '1980-10-01'
    end_date = datetime.now().strftime("%Y-%m-%d")
    central_tendency_type = "ALL"
    return_flags = False
    params = {
        "stationTriplets": station_triplets,
        "elements": elements,
        "duration": duration,
        "beginDate": begin_date,
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
    Extracts relevant data from the JSON response.
    Note: may not want average and median values. 
    """
    relevant_data = []
    for station in data:
        station_triplet = station['stationTriplet']
        for record in station['data']:
            for value in record['values']:
                date = datetime.strptime(value['date'], '%Y-%m-%d').date()
                average = -1 if value.get('average') is None else value['average']
                median = -1 if value.get('median') is None else value['median']
                relevant_data.append({
                    'stationTriplet': station_triplet,
                    'date': date,
                    'year': date.year,
                    'month': date.month,
                    'value': value['value'],
                    'average': average,
                    'median': median
                })
    return relevant_data

def process_SNTL(sntl_lst, BASE_URL):
    """
    Processes the SNOTEL data for the list of stations.
    """
    failed_sntl = []
    headers = ['stationTriplet', 'date', 'year', 'month', 'value', 'average', 'median']
    df = pd.DataFrame(columns=headers)

    for station in sntl_lst:
        params = get_parameters(station)
        data = get_station_data(params, BASE_URL)
        if not data:
            failed_sntl.append(station)
        else:
            data_relevant = relevant_data(data)
            temp_df = pd.DataFrame(data_relevant)
            df = pd.concat([df, temp_df], ignore_index=True)
            
    return df, failed_sntl

def save_to_csv(sntl_lst, filename, BASE_URL):
    """
    Saves the SNOTEL data to a CSV file.
    """
    df, failed_sntl = process_SNTL(sntl_lst, BASE_URL)
    df.to_csv(filename, index=False)
    
    if failed_sntl:
        print(f"Failed stations: {failed_sntl}. Data saved to {filename}.")
    else:
        print(f"All stations' data retrieved. Data saved to {filename}.")

def aggregate_by_average(df):
    """
    Aggregates the data by date using average.
    """
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    average_aggregation = df.groupby('date').agg({
        'value': 'mean',
        'average': 'mean',
        'median': 'mean'
    }).reset_index()

    return average_aggregation

def aggregate_by_median(df):
    """
    Aggregates the data by date using median.
    """
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    median_aggregation = df.groupby('date').agg({
        'value': 'median',
        'average': 'median',
        'median': 'median'
    }).reset_index()

    return median_aggregation

def process_and_save_aggregated_data(file_path):
    """
    Opens a CSV file, aggregates the data using average and median, and saves the results.
    """
    # Load the dataset
    data = pd.read_csv(file_path)
    
    
    # Aggregate data by average and median
    average_aggregated = aggregate_by_average(data)
    median_aggregated = aggregate_by_median(data)
    
    # Construct new filenames
    base_filename = file_path.rsplit('.', 1)[0]  # Remove file extension
    average_filename = f"{base_filename}_agg_average.csv"
    median_filename = f"{base_filename}_agg_median.csv"
    
    # Save the aggregated DataFrames to new CSV files
    average_aggregated.to_csv(average_filename, index=False)
    median_aggregated.to_csv(median_filename, index=False)
    
    print(f"Aggregated data saved to {average_filename} and {median_filename}")

def main():
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
    filename = 'daily_owy.csv'
    
    
    # Save raw data to CSV
    save_to_csv(sntl_owy, filename, BASE_URL)
    
    # Process and save aggregated data
    process_and_save_aggregated_data(filename)

if __name__ == "__main__":
    main()

