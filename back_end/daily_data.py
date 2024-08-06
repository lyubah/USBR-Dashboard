import requests
import pandas as pd
from datetime import datetime
# from data_comparison import sort_water_year
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


# def sort_water_year(df):
#     # Convert 'month_day' to datetime format
#     df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')
#     # df = df.dropna(subset=['month_day'])  # Drop rows where date conversion failed
    
#     # Adjust the dates to align with the water year
#     df['adjusted_date'] = df['month_day'].apply(lambda x: x.replace(year=2000) if x.month >= 10 else x.replace(year=2001))
    
#     # Sort by the adjusted date
#     df = df.sort_values('adjusted_date')
    
#     # Convert 'month_day' back to string format and set it as index
#     df['month_day'] = df['month_day'].dt.strftime('%m-%d')
#     df.set_index('month_day', inplace=True)
#     df.drop(columns=['adjusted_date'], inplace=True)
    
#     # # Drop the 'adjusted_date' column
#     # df.drop(columns=[1980, 'adjusted_date'], inplace=True)
#     df = df.iloc[:-1]
    
#     return df

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
    for year in range(1981, 2025):
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


def get_parameters(station_triplets, end_date, elements):
    """
    Collects common parameters for both stations and data endpoints.
    """
    duration = "DAILY"
    begin_date = '1980-10-01'
    params = {
        "stationTriplets": station_triplets,
        "elements": elements,
        "duration": duration,
        "beginDate": begin_date,
        "endDate": end_date,
        "centralTendencyType": "ALL",
        "returnFlags": False
    }
    return params

def get_station_data(BASE_URL, params):
    """
    Retrieves observational data from the stations using the data endpoint.
    """
    endpoint = "data"
    url = f"{BASE_URL}/{endpoint}"
    
    query_string = "&".join([f"{key}={','.join(value) if isinstance(value, list) else value}" for key, value in params.items()])
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
                    'month_day': date.strftime('%m-%d'),
                    'value': value['value'],
                    'average': average,
                    'median': median
                })
    return relevant_data

def process_SNTL(BASE_URL, sntl_lst, elements, end_date):
    """
    Processes the SNOTEL data for the list of stations.
    """
    failed_sntl = []
    headers = ['stationTriplet', 'date', 'year', 'month', 'month_day', 'value', 'average', 'median']
    df = pd.DataFrame(columns=headers)

    for station in sntl_lst:
        params = get_parameters(station, end_date, elements)
        data = get_station_data(BASE_URL, params)
        if not data:
            failed_sntl.append(station)
        else:
            data_relevant = relevant_data(data)
            temp_df = pd.DataFrame(data_relevant)
            df = pd.concat([df, temp_df], ignore_index=True)
            
    return df, failed_sntl

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

def preprocess_agg_data(df):
    """
    Preprocesses the aggregated data by converting 'date' to datetime, extracting 'month_day' and 'year'.
    """
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows where date conversion failed
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    df['year'] = df['date'].dt.year
    return df.drop(columns=['date'])

def pivot_data(df, value_column):
    """
    Pivots the data to have 'month_day' as index and years as columns.
    """
    pivot_df = df.pivot(index='month_day', columns='year', values=value_column)
    pivot_df.reset_index(inplace=True)
    return pivot_df

def process_and_save_aggregated_data(df, elements):
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

def get_daily_water_year(BASE_URL, sntl_lst, elements, end_date):
    """
    Runs the entire data processing pipeline for the specified stations and elements.
    """
    # Retrieve and process data
    df, failed_sntl = process_SNTL(BASE_URL, sntl_lst, elements, end_date)
    
    if not df.empty:
        # Aggregate, preprocess, pivot, and sort data by water year
        sorted_avg, sorted_median = process_and_save_aggregated_data(df, elements)
        
        # Save the sorted DataFrames to CSV files if needed
        sorted_avg.to_csv(f'sorted_water_year_avg_{elements}.csv')
        sorted_median.to_csv(f'sorted_water_year_med_{elements}.csv')
        
        print(f"Data processed successfully for elements: {elements}")
    else:
        print("No data available to process.")
    
    if failed_sntl:
        return (f"{elements} was not found in the following: {failed_sntl}")
    return sorted_avg, sorted_median 


def main():
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
    filename = 'daily_owy.csv'
    end_date = datetime.now().strftime("%Y-%m-%d")

    
    
    # Save raw data to CSV
    # save_to_csv(sntl_owy, filename, BASE_URL)
    
    # Process and save aggregated data
    get_daily_water_year(BASE_URL, sntl_owy, 'WTEQ', end_date)

if __name__ == "__main__":
    main()