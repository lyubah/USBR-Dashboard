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


def pivot_data(df, value_column):
    """
    Pivots the data to have 'month_day' as index and years as columns.
    """
    pivot_df = df.pivot(index='month_day', columns='year', values=value_column)
    pivot_df.reset_index(inplace=True)
    return pivot_df

def preprocess_agg_data(df):
    """
    Preprocesses the aggregated data by converting 'date' to datetime, extracting 'month_day' and 'year'.
    """
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows where date conversion failed
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    df['year'] = df['date'].dt.year
    return df.drop(columns=['date'])


def aggregate_by_average(df):
    """
    Aggregates the data by date using average.
    """
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    average_aggregation = df.groupby('date').agg({
        'value': 'mean'
    }).reset_index()

    return average_aggregation

def aggregate_by_median(df):
    """
    Aggregates the data by date using median.
    """
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    median_aggregation = df.groupby('date').agg({
        'value': 'median'
    }).reset_index()

    return median_aggregation

def pivot_data(df, value_column):
    """
    Pivots the data to have 'month_day' as index and years as columns.
    """
    pivot_df = df.pivot(index='month_day', columns='year', values=value_column)
    pivot_df.reset_index(inplace=True)
    return pivot_df

def process_and_save_aggregated_data(df):
    """
    Aggregates the data using average and median, preprocesses, pivots, and sorts by water year.
    """
    # Aggregate data by average and median
    agg_avg_df = aggregate_by_average(df)
    agg_med_df = aggregate_by_median(df)
    
    # Preprocess aggregated data
    agg_avg_df = preprocess_agg_data(agg_avg_df)
    agg_med_df = preprocess_agg_data(agg_med_df)
    
    # Pivot the data
    pivoted_values_avg = pivot_data(agg_avg_df, 'value')
    pivoted_values_med = pivot_data(agg_med_df, 'value')
    
    # Fill NA values with 0
    pivoted_values_avg = pivoted_values_avg.fillna(0)
    pivoted_values_med = pivoted_values_med.fillna(0)
  
  # Convert columns to strings
    pivoted_values_avg.columns = pivoted_values_avg.columns.astype(str)
    pivoted_values_med.columns = pivoted_values_med.columns.astype(str)
     
    
    # Sort data by water year
    sorted_avg = sort_water_year(pivoted_values_avg)
    sorted_median = sort_water_year(pivoted_values_med)
    
    return sorted_avg, sorted_median




def sort_water_year(df):
    # Ensure 'month_day' is the index
    if 'month_day' not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'month_day'}, inplace=True)
        
    # Convert 'month_day' to datetime format
    df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')

    # Create a new DataFrame to store reordered data
    reordered_df = pd.DataFrame()

    # Process each year's data
    for year in :
        # Create the column names as strings
        current_year = str(year)
        previous_year = str(year - 1)

        # If previous year column does not exist, create an empty column
        if previous_year not in df.columns:
            df[previous_year] = None

        # Select data from October to December of the previous year
        oct_to_dec = df.loc[df['month_day'].dt.month >= 10, previous_year].reset_index(drop=True)

        # Select data from January to September of the current year
        jan_to_sep = df.loc[df['month_day'].dt.month < 10, current_year].reset_index(drop=True)

        # Combine the data to form the water year
        water_year_data = pd.concat([oct_to_dec, jan_to_sep], ignore_index=True)

        # Add the water year data to the new DataFrame
        reordered_df[current_year] = water_year_data

    # Reset the index of the new DataFrame to 'month_day'
    reordered_df.index = pd.date_range(start='10/1/2000', periods=len(reordered_df), freq='D')
    reordered_df.index = reordered_df.index.strftime('%m-%d')

    return reordered_df

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
    elements = 'SMS:*'
    duration = "DAILY"
    central_tendency_type = "ALL"
    return_flags = False
    begin_date = 
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
    Extracts relevant data from the JSON response.
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
                    'element': element_code,
                    'date': date,
                    'year': date.year,
                    'month': date.month,  
                    'value': value['value'],
                    'average': average,
                    'median': median
                })
    return pd.DataFrame(relevant_data)

# def relevant_data(data):
#     """
#     Extracts relevant data from the JSON response.
#     """
#     relevant_data = []
#     for station in data:
#         station_triplet = station['stationTriplet']
#         for record in station['data']:
#             element_code = record['stationElement']['elementCode']  # Extract the element code
#             for value in record['values']:
#                 year = value['year']
#                 month = value['month']
#                 date = datetime(year, month, 1)  # Create date from year and month
#                 average = -1 if value.get('average') is None else value['average']
#                 median = -1 if value.get('median') is None else value['median']
#                 relevant_data.append({
#                     'stationTriplet': station_triplet,
#                     'element': element_code,  # Add the element code to the record
#                     'date': date,
#                     'year': year,
#                     'month': month,
#                     'value': value['value'],
#                     'average': average,
#                     'median': median
#                 })
#     return pd.DataFrame(relevant_data)

def get_soil(station_lists, BASE_URL, month, day, years):
    
    soil_moisture = pd.DataFrame()    

    # stations = [station for station in station_lists if "SNTL" in station]
    
    for year in years:
        start_date, end_date = calculate_122_day_period(year, month, day)
        
        print(f"Start Date: {start_date}, End Date: {end_date}")
        
        # Fetch data for each station
        data_frames = []
        for station in station_lists:
            print(f"Fetching data for station: {station}")
            params = get_parameters(station, start_date, end_date)
            data = get_station_data(params, BASE_URL)
            if data:
                df = relevant_data(data)
                print(f"Processed data for station: {station}")
                print(df.head())
                if not df.empty:
                    data_frames.append(df)
            else:
                print(f"No data returned for station: {station}")
        
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            soil_moisture = pd.concat([all_observed_flow, combined_df], ignore_index=True)
    
    # START HERE
    # convert to water year:
        soil_moisture
    # sorted_avg, sorted_median = process_and_save_aggregated_data(all_observed_flow)
    
    #get averages and medians from values
    
    # get distance using values 
    
        
    return  sorted_avg, sorted_media




# Example usage
if __name__ == "__main__":
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    station_lists = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
    month = 3
    day = 1
    years = ['1999', '2023', '2017', '1997', '2006', '2004', '2002']
    
    soil = get_soil(station_lists, BASE_URL, month, day, years)








# # Example usage:
# station_triplet = '1136:NV:SNTL	'
# begin_date = '1980-10-01'
# end_date = '2023-12-31'
# soil_moisture_data = get_soil_moisture_data(station_triplet, begin_date, end_date)
# soil_moisture_df = process_soil_moisture_data(soil_moisture_data)
# print(soil_moisture_df.head())
