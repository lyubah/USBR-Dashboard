import pandas as pd
import requests
from datetime import datetime, timedelta

#Steps to improve accuracy of the data




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

def get_station_data(params, BASE_URL):
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
            value = record.get('value')
            average = record.get('average')
            if value is not None and average is not None:  # Include only records with value and average
                records.append({
                    'stationTriplet': station_triplet,
                    'date': record['date'],
                    'value': value,
                    'average': average
                })
    df = pd.DataFrame(records)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is in datetime format
    return df

def calculate_122_day_period(year, month, day):
    year = int(year)
    month = int(month)
    day= int(day)
    start_date = datetime(year, month, day)
    end_date = start_date + timedelta(days=121)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def calculate_percent_normal(df):
    # print("DataFrame to calculate percent normal:")
    # print(df.head())
    
    total_precipitation = df['value'].sum()
    total_average_precipitation = df['average'].sum()
    percent_normal = (total_precipitation / total_average_precipitation) * 100
    return pd.DataFrame({
        'year': [df['date'].dt.year.iloc[0]],
        'percent_normal': [percent_normal]
    })


def get_percent_normal_prec(years, month, day, stations, BASE_URL):
    all_percent_normal_df = pd.DataFrame()
    
    for year in years:
        start_date, end_date = calculate_122_day_period(year, month, day)
        
        # print(f"Start Date: {start_date}, End Date: {end_date}")
        
        # Fetch data for each station
        data_frames = []
        for station in stations:
            # print(f"Fetching data for station: {station}")
            params = get_parameters(station, start_date, end_date)
            data = get_station_data(params, BASE_URL)
            if data:
                df = process_data(data)
                # print(f"Processed data for station: {station}")
                print(df.head())
                if not df.empty:
                    data_frames.append(df)
            else:
                print(f"No data returned for station: {station}")
        
        if data_frames:
            combined_df = pd.concat(data_frames)
            percent_normal_df = calculate_percent_normal(combined_df)
            all_percent_normal_df = pd.concat([all_percent_normal_df, percent_normal_df], ignore_index=True)
        
    all_percent_normal_df =  all_percent_normal_df.set_index('year').astype(int)
            

    
    return all_percent_normal_df

        
      

# # Example usage:
# if __name__ == "__main__":
#     years = [2006, 2017, 1999, 2020, 2019, 1997, 1993, 1982]
#     sntl_owy = ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL']
#     BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    
#     percent_normal_df = get_percent_normal_prec(years, 3, 15, sntl_owy, BASE_URL)
#     if not percent_normal_df.empty:
#         print("Percent normal data for all years:\n", percent_normal_df)
#         percent_normal_df.to_csv('percent_normal_data.csv', index=False)
