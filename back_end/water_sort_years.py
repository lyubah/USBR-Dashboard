import pandas as pd

# Load the pivoted data
# df= pd.read_csv('def_med_for_sim.csv', index_col='month_day')

# df_avg = pd.read_csv('def_avg_for_sim.csv', index_col='month_day')

# # Function to sort data by water year
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

# # Apply the function to sort data by water year
df= pd.read_csv('def_med.csv', index_col='month_day')
df_avg = pd.read_csv('def_avg_for_sim.csv', index_col='month_day')




sorted_df = sort_water_year(df)
sorted_df_avg = sort_water_year(df_avg)

# Save the sorted DataFrame to a new CSV file
# sorted_df.to_csv('sorted_water_year_med.csv')
sorted_df_avg.to_csv('sorted_water_year_avg.csv')

