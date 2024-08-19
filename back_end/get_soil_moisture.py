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
import similar_years



def get_water_year_start(date):
    # Check if the month is before October
    if date.month >= 10:
        # If the date is in October or later, the start of the water year is in the same year
        water_year_start = datetime(date.year, 10, 1)
    else:
        # If the date is before October, the start of the water year is in the previous year
        water_year_start = datetime(date.year - 1, 10, 1)
    
    return water_year_start


# def sort_water_year(df):
#     # Ensure 'month_day' is the index
#     if 'month_day' not in df.columns:
#         df.reset_index(inplace=True)
#         df.rename(columns={'index': 'month_day'}, inplace=True)
        
#     # Convert 'month_day' to datetime format for sorting
#     df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')

#     # Create a new DataFrame to store reordered data
#     reordered_df = pd.DataFrame()

#     # Get the list of years available in the columns
#     years = [col for col in df.columns if col.isdigit()]

#     # Process each year's data
#     for year in years:
#         # Convert year to integer
#         year_int = int(year)
#         previous_year = str(year_int - 1)

#         # If previous year's data doesn't exist, create an empty column
#         if previous_year not in df.columns:
#             df[previous_year] = None

#         # Select data from October to December of the previous year
#         oct_to_dec = df.loc[df['month_day'].dt.month >= 10, previous_year].reset_index(drop=True)

#         # Select data from January to September of the current year
#         jan_to_sep = df.loc[df['month_day'].dt.month < 10, year].reset_index(drop=True)

#         # Combine the data to form the water year
#         water_year_data = pd.concat([oct_to_dec, jan_to_sep], ignore_index=True)

#         # Add the water year data to the new DataFrame
#         reordered_df[year] = water_year_data

#     # Reset the index of the new DataFrame to 'month_day'
#     reordered_df.index = pd.date_range(start='10/1/2000', periods=len(reordered_df), freq='D')
#     reordered_df.index = reordered_df.index.strftime('%m-%d')

#     return reordered_df

def sort_water_year(df):
    # Ensure 'month_day' is the index
    if df.index.name != 'month_day':
        if 'month_day' in df.columns:
            df.set_index('month_day', inplace=True)
        else:
            raise ValueError("'month_day' must be either an index or a column in the DataFrame.")
    
    # Convert 'month_day' to datetime format for sorting
    df.index = pd.to_datetime(df.index, format='%m-%d', errors='coerce')

    # Sort the index using a custom sort key that considers both month and day
    def water_year_sort_key(date):
        # October to December should come first, followed by January to September
        if date.month >= 10:
            # (0, day) for October, (1, day) for November, (2, day) for December
            return date.month - 10, date.day
        else:
            # (3, day) for January, (4, day) for February, ..., (11, day) for September
            return date.month + 2, date.day

    # Sort the DataFrame by the custom water year order
    df = df.sort_index(key=lambda x: x.map(water_year_sort_key))
    
    # Restore the month_day as a string index
    df.index = df.index.strftime('%m-%d')
    df = df[~df.index.isna()]



    return df



def get_parameters(station_triplets, year, current_date):
    """
    Collects common parameters for both stations and data endpoints.
    """
    elements = 'SMS:*'
    duration = "DAILY"
    
    # Get the start date of the water year based on the current date
    start_date = get_water_year_start(current_date).strftime('%Y-%m-%d')
    
    # Ensure current_date is in the correct string format
    current_date_str = current_date.strftime('%Y-%m-%d')
    
    central_tendency_type = "ALL"
    return_flags = False
    
    params = {
        "stationTriplets": station_triplets,
        "elements": elements,
        "duration": duration,
        "beginDate": start_date,
        "endDate": current_date_str,
        "centralTendencyType": central_tendency_type,
        "returnFlags": return_flags
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

# def aggregate_by_average(df):
#     """
#     Aggregates the data by date using average.
#     """
#     if not pd.api.types.is_datetime64_any_dtype(df['date']):
#         df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
#     average_aggregation = df.groupby('year').agg({
#         'value': 'mean',
#         # 'average': 'mean',
#         # 'median': 'mean'
#     }).reset_index()

#     return average_aggregation
def aggregate_by_average(df):
    """
    Aggregates the data by date using average.
    """
    # Ensure 'date' is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    # Extract 'month_day' and 'year' for aggregation
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    # df['year'] = df['date'].dt.year
    
    # Group by 'month_day' and 'year' and calculate the average of 'value'
    average_aggregation = df.groupby(['month_day', 'year']).agg({
        'value': 'mean'
    }).reset_index()

    return average_aggregation

# def aggregate_by_median(df):
#     """
#     Aggregates the data by date using median.
#     """
#     if not pd.api.types.is_datetime64_any_dtype(df['date']):
#         df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
#     median_aggregation = df.groupby('date').agg({
#         'value': 'median',
#         # 'average': 'median',
#         # 'median': 'median'
#     }).reset_index()

#     return median_aggregation


# def calculate_moisture_difference(current_year, data):
#     """
#     Calculate the difference in soil moisture between the current year and historical years.
    
#     Parameters:
#     - current_year (str): The year to compare against.
#     - data (pd.DataFrame): The DataFrame containing water year ordered soil moisture percentage.
    
#     Returns:
#     - pd.DataFrame: A DataFrame with the moisture differences and qualitative assessments.
#     """
#     current_year = str(current_year)
#     current_year_data = data[current_year].dropna().values
#     results = []

#     for col_year in data.columns:
#         if col_year != current_year:
#             historical_year_data = data[col_year].dropna().values
            
#             # Calculate differences: positive means historical year was more moist
#             differences = historical_year_data - current_year_data
            
#             # Summarize the differences
#             mean_difference = differences.mean()  # Mean of the differences
#             if mean_difference > 0:
#                 qualitative_metric = '+'  # More moist historically
#             elif mean_difference < 0:
#                 qualitative_metric = '-'  # Less moist historically
#             else:
#                 qualitative_metric = '='  # About the same

#             results.append((col_year, mean_difference, qualitative_metric))
    
#     # Create a DataFrame with the results
#     results_df = pd.DataFrame(results, columns=['year', 'soi_moisture_ (mean_difference)', 'soil moisture similarity']).set_index('year')

#     return results_df

def calculate_moisture_difference(current_year, data, similarity_threshold=.8):
    """
    Calculate the difference in soil moisture between the current year and historical years.
    
    Parameters:
    - current_year (str): The year to compare against.
    - data (pd.DataFrame): The DataFrame containing water year ordered soil moisture percentage.
    - similarity_threshold (float): The threshold within which differences are considered "about the same".
    
    Returns:
    - pd.DataFrame: A DataFrame with the moisture differences and qualitative assessments.
    """
    current_year = int(current_year)
    
    
    current_year_data = data[current_year].dropna().values
    results = []

    for col_year in data.columns:
        if col_year != current_year:
            historical_year_data = data[col_year].dropna().values
            
            # Calculate differences: positive means historical year was more moist
            differences = historical_year_data - current_year_data
            
            # Summarize the differences
            mean_difference = differences.mean().round(2)  # Mean of the differences
            abs_mean_difference = abs(mean_difference)  # Absolute mean difference
            
            # Determine qualitative metric
            if abs_mean_difference <= similarity_threshold:
                qualitative_metric = '='  # About the same
            elif mean_difference > 0:
                qualitative_metric = '+'  # More moist historically
            else:
                qualitative_metric = '-'  # Less moist historically

            results.append((col_year, mean_difference, qualitative_metric))
    
    # Create a DataFrame with the results
    results_df = pd.DataFrame(results, columns=['year', 'Average Soil Moisture Difference (%)', 'Soil Moisture Similarity Indicator']).set_index('year')

    return results_df



def preprocess_agg_data(df):
    """
    Pivots the DataFrame so that each year is a column, with 'month_day' as the index.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing 'month_day', 'year', and 'value'.
    
    Returns:
    pd.DataFrame: A pivoted DataFrame with years as columns and 'month_day' as the index.
    """
    # Pivot the DataFrame
    pivot_df = df.pivot(index='month_day', columns='year', values='value')
    
    # Optional: Fill any missing values (e.g., NaN) with 0 or other strategy
    pivot_df = pivot_df.fillna(0)
    
    # Reset the index if needed, but typically we'll leave month_day as the index
    # pivot_df.reset_index(inplace=True)
    
    return pivot_df
    
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
    # agg_med_df = aggregate_by_median(df)
    
    # Preprocess aggregated data
    agg_avg_df = preprocess_agg_data(agg_avg_df)
    # agg_med_df = preprocess_agg_data(agg_med_df)
    
    # Pivot the data
    # pivoted_values_avg = pivot_data(agg_avg_df, 'value')
    # pivoted_values_med = pivot_data(agg_med_df, 'value')
    
    # Sort data by water year
    sorted_avg = sort_water_year(agg_avg_df)
    # sorted_median = sort_water_year(pivoted_values_med)
    
    return sorted_avg 

def get_soil(station_lists, BASE_URL, month, day, year, years):
    soil_moisture = pd.DataFrame()
    current_year = year 
    years.append(current_year)
    
    for year in years:        
        # Fetch data for each station
        data_frames = []
        curr_date = datetime(int(year), month, day)

        for station in station_lists:
            print(f"Fetching data for station: {station} for year: {year}")
            params = get_parameters(station, year, curr_date)
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
            soil_moisture = pd.concat([soil_moisture, combined_df], ignore_index=True)
        
    df = process_and_save_aggregated_data(soil_moisture)
    
    #
 
    # Compare 2024 to other years
    similar_years_df = calculate_moisture_difference(current_year, df)
    
    # Identify missing years
    missing_years = set(years) - set(similar_years_df.index)
    # Create a DataFrame with missing years
    missing_data = pd.DataFrame({
        'year': list(missing_years),
        'Average Soil Moisture Difference (%)': float('nan'),
        'Soil Moisture Similarity Indicator': float('nan')
    }).set_index('year')
    
    # Append the missing data to similar_years_df
    similar_years_df = pd.concat([similar_years_df, missing_data])
    similar_years_df.drop(index=current_year, inplace=True)
        # Convert the index to numeric (integer in this case)
    similar_years_df.index = similar_years_df.index.astype(int)

    
    # similar_years_df = similar_years_df.reindex(years)
    return similar_years_df

        
        # piv_tab = process_and_save_aggregated_data(soil_moisture)
    
    # START HERE
    # convert to water year:
        
    # sorted_avg, sorted_median = process_and_save_aggregated_data(all_observed_flow)
    
    #get averages and medians from values
    
    # get distance using values 
    
        




# # Example usage
# if __name__ == "__main__":
#     BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
#     station_lists = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
#     month = 3
#     day = 1
#     year = 2024 
#     years = ['1999', '2023', '2017', '1997', '2006', '2004', '2002']
    
    
#     soil = get_soil(station_lists, BASE_URL, month, day, year, years)
#     soil




