import pandas as pd
import requests
from datetime import datetime, timedelta

def calculate_monthly_period(year, month):
    """
    Calculate the start and end date for the entire month.
    """
    year = int(year)
    month = int(month)
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_last_10_days_period(year, month):
    """
    Calculate the last 10 days of a given month.
    """
    end_date = datetime(year, month, 28) if month == 2 else datetime(year, month, 30)
    start_date = end_date - timedelta(days=9)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_monthly_snow_depth_average(df):
    """
    Calculate the monthly average snow depth for each year.

    Parameters:
    - df (pd.DataFrame): DataFrame containing daily snow depth data with columns 'date' and 'snow_depth'.

    Returns:
    - pd.DataFrame: DataFrame with years as the index and a single column representing the monthly average snow depth.
    """
    # Ensure 'date' is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract the year and month from the 'date' column
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')  # Get month name (e.g., "February")
    
    # Calculate the monthly average snow depth for each year
    monthly_avg = df.groupby('year').agg({
        'snow_depth': 'mean'
    }).rename(columns={'snow_depth': f"{df['month'].iloc[0]} snow depth average"})
    
    return monthly_avg



def get_parameters(station_triplet, begin_date, end_date):
    return {
        "stationTriplets": station_triplet,
        "elements": "SNWD",
        "duration": "DAILY",
        "beginDate": begin_date,
        "endDate": end_date,
        "centralTendencyType": "ALL",
        "returnFlags": False
    }

def get_station_data(params, BASE_URL):
    url = f"{BASE_URL}/data"
    response = requests.get(url, params=params)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []



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

def calculate_snow_depth_averages(df, last_10_days_start, last_10_days_end):
    """
    Calculate average snow depth for the entire month and for the last 10 days of the month.
    """
    # Convert last_10_days_start and last_10_days_end to datetime
    last_10_days_start = datetime.strptime(last_10_days_start, '%Y-%m-%d').date()
    last_10_days_end = datetime.strptime(last_10_days_end, '%Y-%m-%d').date()
    
    # Calculate monthly average
    monthly_avg = df.groupby('year').agg({
        'snow_depth': 'mean'
    }).rename(columns={'snow_depth': 'monthly_avg_snow_depth'}).reset_index()
    
    # Calculate last 10 days average
    last_10_days_data = df[(df['date'] >= last_10_days_start) & (df['date'] <= last_10_days_end)]
    last_10_days_avg = last_10_days_data.groupby('year').agg({
        'snow_depth': 'mean'
    }).rename(columns={'snow_depth': 'last_10_days_avg_snow_depth'}).reset_index()
    
    # Merge the two averages
    combined_avg = pd.merge(monthly_avg, last_10_days_avg, on='year', how='outer')
    
    return combined_avg


# def calculate_snow_coverage_indicator(df, current_year):
#     """
#     Calculate the snow coverage indicator comparing last 10 days of the month with historical averages.
    
#     """
#     df = df.reset_index()

#     historical_avg = df[df['year'] != current_year]['last_10_days_avg_snow_depth'].mean()

#     df['snow_coverage_indicator'] = df.apply(lambda row: 
#                                               "++" if row['last_10_days_avg_snow_depth'] > 1.2 * historical_avg else
#                                               "+" if row['last_10_days_avg_snow_depth'] > 1.1 * historical_avg else
#                                               "=" if 0.9 * historical_avg <= row['last_10_days_avg_snow_depth'] <= 1.1 * historical_avg else
#                                               "-" if row['last_10_days_avg_snow_depth'] < 0.9 * historical_avg else
#                                               "--", axis=1)
    
#     return df

# def calculate_last_10_days_avg(df, current_year):
#     """
#     Calculate the average snow depth for the last 10 days of each month and the snow coverage indicator.

#     Parameters:
#     - df (pd.DataFrame): DataFrame containing daily snow depth data with columns 'date' and 'snow_depth'.
#     - current_year (int): The year to compare against for the snow coverage indicator.

#     Returns:
#     - pd.DataFrame: DataFrame with years as the index, a column for the last 10 days' average snow depth, 
#                     and a column for the snow coverage indicator.
#     """
#     # Ensure 'date' is in datetime format
#     df['date'] = pd.to_datetime(df['date'])
    
#     # Extract the year and month from the 'date' column
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.strftime('%B')  # Get month name (e.g., "February")
    
#     # Find the last day of the month for each date
#     df['last_day'] = df['date'] + pd.offsets.MonthEnd(0)
    
#     # Calculate the date for 10 days before the end of the month
#     df['last_10_days_start'] = df['last_day'] - pd.Timedelta(days=9)
    
#     # Filter the data to only include the last 10 days of the month
#     last_10_days_df = df[df['date'] >= df['last_10_days_start']]
    
#     # Calculate the average snow depth for the last 10 days for each year
#     last_10_days_avg = last_10_days_df.groupby('year').agg({
#         'snow_depth': 'mean'
#     }).rename(columns={'snow_depth': f"Last 10 days {df['month'].iloc[0]} avg snow depth"})
    
#     # Calculate snow coverage indicator
#     last_10_days_avg = calculate_snow_coverage_indicator(last_10_days_avg, current_year)
    
#     return last_10_days_avg

def calculate_snow_coverage_indicator(df, current_year):
    """
    Calculate the snow coverage indicator comparing last 10 days of the month with historical averages.
    """
    df = df.reset_index()

    # Rename the column temporarily to a generic name
    df.rename(columns={df.columns[1]: 'last_10_days_avg_snow_depth'}, inplace=True)

    historical_avg = df[df['year'] != current_year]['last_10_days_avg_snow_depth'].mean()

    df['snow_coverage_indicator'] = df.apply(lambda row: 
                                              "++" if row['last_10_days_avg_snow_depth'] > 1.2 * historical_avg else
                                              "+" if row['last_10_days_avg_snow_depth'] > 1.1 * historical_avg else
                                              "=" if 0.9 * historical_avg <= row['last_10_days_avg_snow_depth'] <= 1.1 * historical_avg else
                                              "-" if row['last_10_days_avg_snow_depth'] < 0.9 * historical_avg else
                                              "--", axis=1)
    
    return df

def calculate_last_10_days_avg(df, current_year):
    """
    Calculate the average snow depth for the last 10 days of each month and the snow coverage indicator.

    Parameters:
    - df (pd.DataFrame): DataFrame containing daily snow depth data with columns 'date' and 'snow_depth'.
    - current_year (int): The year to compare against for the snow coverage indicator.

    Returns:
    - pd.DataFrame: DataFrame with years as the index, a column for the last 10 days' average snow depth, 
                    and a column for the snow coverage indicator.
    """
    # Ensure 'date' is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract the year and month from the 'date' column
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')  # Get month name (e.g., "February")
    
    # Find the last day of the month for each date
    df['last_day'] = df['date'] + pd.offsets.MonthEnd(0)
    
    # Calculate the date for 10 days before the end of the month
    df['last_10_days_start'] = df['last_day'] - pd.Timedelta(days=9)
    
    # Filter the data to only include the last 10 days of the month
    last_10_days_df = df[df['date'] >= df['last_10_days_start']]
    
    # Calculate the average snow depth for the last 10 days for each year
    last_10_days_avg = last_10_days_df.groupby('year').agg({
        'snow_depth': 'mean'
    })

    # Temporarily rename the column for consistency
    last_10_days_avg.rename(columns={'snow_depth': 'last_10_days_avg_snow_depth'}, inplace=True)
    
    # Calculate snow coverage indicator
    last_10_days_avg = calculate_snow_coverage_indicator(last_10_days_avg, current_year)

    # Rename the column back to include the month name
    last_10_days_avg.rename(columns={'last_10_days_avg_snow_depth': f"Last 10 days {df['month'].iloc[0]} avg snow depth"}, inplace=True)
    
    return last_10_days_avg



def aggregate_station_data(df):
    """
    Aggregates data from multiple stations for the same date.
    """
    aggregated_df = df.groupby('date').agg({
        'value': 'mean'
    }).rename(columns={'value': 'snow_depth'}).reset_index()
    return aggregated_df

def calculate_snow_depth_averages(df, last_10_days_start, last_10_days_end):
    """
    Calculate average snow depth for the entire month and for the last 10 days of the month.
    """
    # Convert last_10_days_start and last_10_days_end to datetime
    last_10_days_start = datetime.strptime(last_10_days_start, '%Y-%m-%d').date()
    last_10_days_end = datetime.strptime(last_10_days_end, '%Y-%m-%d').date()
    
    # Calculate monthly average
    monthly_avg = df['snow_depth'].mean()
    
    # Calculate last 10 days average
    last_10_days_data = df[(df['date'] >= last_10_days_start) & (df['date'] <= last_10_days_end)]
    last_10_days_avg = last_10_days_data['snow_depth'].mean()
    
    return monthly_avg, last_10_days_avg

def get_snow_coverage_data(years, month, day, current_year, stations, BASE_URL):
    all_snow_coverage_df = pd.DataFrame()    
    years.append(current_year)
    
    for year in years:
        data_frames = []
        month_start, month_end = calculate_monthly_period(year, month)
        # last_10_days_start, last_10_days_end = calculate_last_10_days_period(year, month)
                

        for station in stations:
            print(f"Fetching data for station: {station} for year: {year}")
            params = get_parameters(station, month_start, month_end)
            data = get_station_data(params, BASE_URL)

            if data:
                df = relevant_data(data)

                if not df.empty:
                    df['year'] = year  # Ensure the year is included in the DataFrame
                    data_frames.append(df)
            else:
                print(f"No data returned for station: {station}")

        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            all_snow_coverage_df = pd.concat([all_snow_coverage_df, combined_df], ignore_index=True)
    
    #aggregate daily data
    daily_agg = aggregate_station_data(all_snow_coverage_df)
    #aggregate monthly data and add to col
    monthly_avg  = calculate_monthly_snow_depth_average(daily_agg)
    
    #aggregate last 10 days average 
    ten_day_avgs = calculate_last_10_days_avg(daily_agg, current_year)
    ten_day_avgs['year'] = ten_day_avgs['year'].astype(int)
    ten_day_avgs.set_index('year', inplace=True)
    
    combined_df = pd.merge(monthly_avg, ten_day_avgs, left_index=True, right_index=True, how='outer')
    # Set the index to the year and ensure it is an integer
  
    
    return combined_df

# Example usage:
# if __name__ == "__main__":
#     years = [2006, 2017, 1999, 2020, 2019, 1997, 1993, 1982]
#     curr_year = 2024
#     sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
#     BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    
#     snow_coverage_df = get_snow_coverage_data(years, 2, 28, curr_year, sntl_owy, BASE_URL)
