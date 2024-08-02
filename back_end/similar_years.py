#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:16:24 2024
@author: Lerberber
"""
import pandas as pd
from scipy.stats import wasserstein_distance
import datetime
import numpy as np
from scipy.integrate import simps




# sorted_avg_data.reset_index(inplace=True)
# sorted_med_data.reset_index(inplace=True)

# sorted_avg_data.rename(columns={'index': 'month_day'}, inplace=True)
# sorted_med_data.rename(columns={'index': 'month_day'}, inplace=True)



def select_data_up_to_date(data, month, day):
    # Create a comparison date string in the format 'MM-DD'
    end_date_str = f'{month:02d}-{day:02d}'
    
    # Find the index of the row corresponding to the end_date_str
    end_idx = data[data['month_day'] == end_date_str].index[0]
    
    # Select all rows up to and including end_idx
    period_data = data.iloc[:end_idx + 1]
    
    return period_data

# Function to calculate Wasserstein distance
def calculate_wasserstein_distance(current_year_data, historical_year_data):
    return wasserstein_distance(current_year_data, historical_year_data)

def find_similar_years(current_year, data, month, day, n=5):
    period_data = select_data_up_to_date(data, month, day)
    current_year_data = period_data[current_year].dropna().values
    distances = []
    
    for col_year in period_data.columns:
        if col_year not in ['month_day', current_year]:
            historical_year_data = period_data[col_year].dropna().values
            distance = calculate_wasserstein_distance(current_year_data, historical_year_data)
            distances.append((col_year, distance))
    
    distances.sort(key=lambda x: x[1])
    
    return distances[:n]

def find_similar_years_across_datasets(current_year, datasets, month, day, threshold=None, n=5):
    similar_years_all = []

      
    for data in datasets:
        # prep dataset 
        data.reset_index(inplace=True)
        data.rename(columns={'index': 'month_day'}, inplace=True)
        
        similar_years = find_similar_years(current_year, data, month, day, n)
        similar_years_all.extend(similar_years)
    
    # Filter unique years that meet the threshold
    unique_similar_years = {year: score for year, score in similar_years_all if score <= threshold}
    sorted_years = sorted(unique_similar_years.items(), key=lambda x: x[1])

    return [(year, month, day, score) for year, score in sorted_years]

# Example usage


# Load the sorted data and set the correct index
sorted_avg_data = pd.read_csv('sorted_water_year_avg.csv', index_col=0)
sorted_med_data = pd.read_csv('sorted_water_year_med.csv', index_col=0)

datasets = [sorted_avg_data, sorted_med_data]

similar_years_across = find_similar_years_across_datasets('2024', datasets, 3, 1, threshold=0.85, n=7)
# print("Similar Years Across Datasets:", similar_years_across)


# def select_data_up_to_date(data, month, day):
#     # Create a comparison date string in the format 'MM-DD'
#     end_date_str = f'{month:02d}-{day:02d}'
    
#     # Find the index of the row corresponding to the end_date_str
#     end_idx = data[data['month_day'] == end_date_str].index[0]
    
#     # Select all rows up to and including end_idx
#     period_data = data.iloc[:end_idx + 1]
    
#     return period_data



# # Function to calculate Wasserstein distance
# def calculate_wasserstein_distance(current_year_data, historical_year_data):
#     return wasserstein_distance(current_year_data, historical_year_data)



# def find_similar_years(current_year, data, month, day,threshold, n=5):
    
#     period_data = select_data_up_to_date(data, month, day)
    
#     current_year_data = period_data[current_year].dropna().values
#     distances = []
#     for col_year in period_data.columns:
#         if col_year not in ['month_day', current_year]:
#             historical_year_data = period_data[col_year].dropna().values
#             # min_length = min(len(current_year_data), len(historical_year_data))
#             # distance = calculate_wasserstein_distance(current_year_data[:min_length], historical_year_data[:min_length])
#             distance = calculate_wasserstein_distance(current_year_data, historical_year_data)

#             distances.append((col_year, distance))
#     distances.sort(key=lambda x: x[1])
    
#     #  # Filter results based on the threshold
#     # if threshold is not None:
#     #     distances = [year for year in distances if year[1] <= threshold]
   
    
#     return distances[:n]




# # Example usage:
# # Example: Find top 5 similar years to 2024 up to March 1st
# similar_years_partial = find_similar_years('2024', sorted_med_data, 3, 1,None, n=6)
# print("Partial Year Similarities:", similar_years_partial)


# # Example: Find top 5 similar years to 2024 up to March 1st
# similar_years_partial = find_similar_years('2024', sorted_avg_data, 3, 1, None, n=6)
# print("Partial Year Similarities:", similar_years_partial)



# Area Under the Curve
# # Function to calculate AUC
# def calculate_auc(data):
#     return simps(data)



# def find_similar_years_by_auc(current_year, data, month, day, n=5):
#     period_data = select_data_up_to_date(data, month, day)
#     current_year_data = period_data[current_year].dropna().values
#     current_year_auc = calculate_auc(current_year_data)
    
#     distances = []
    
#     for col_year in period_data.columns:
#         if col_year not in ['month_day', current_year]:
#             historical_year_data = period_data[col_year].dropna().values
#             historical_year_auc = calculate_auc(historical_year_data)
#             auc_diff = abs(current_year_auc - historical_year_auc)
#             distances.append((col_year, auc_diff))
    
#     distances.sort(key=lambda x: x[1])
    
#     return distances[:n]

# # Example usage
# similar_years_partial = find_similar_years_by_auc('2024', sorted_med_data, 3, 1, n=6)
# print("Partial Year Similarities by AUC:", similar_years_partial)

# similar_years_partial = find_similar_years_by_auc('2024', sorted_avg_data, 3, 1, n=6)
# print("Partial Year Similarities by AUC:", similar_years_partial)


 



# AREA UNDER THE CURVE + EMD 

# def select_data_up_to_date(data, month, day):
#     # Create a comparison date string in the format 'MM-DD'
#     end_date_str = f'{month:02d}-{day:02d}'
    
#     # Find the index of the row corresponding to the end_date_str
#     end_idx = data[data['month_day'] == end_date_str].index[0]
    
#     # Select all rows up to and including end_idx
#     period_data = data.iloc[:end_idx + 1]
    
#     return period_data

# # Function to calculate AUC
# def calculate_auc(data):
#     return simps(data)

# # Function to calculate Wasserstein distance
# def calculate_wasserstein_distance(current_year_data, historical_year_data):
#     return wasserstein_distance(current_year_data, historical_year_data)

# # Function to combine AUC and EMD into a single score
# def combine_auc_emd(current_year_data, historical_year_data):
#     auc_diff = abs(calculate_auc(current_year_data) - calculate_auc(historical_year_data))
#     emd = calculate_wasserstein_distance(current_year_data, historical_year_data)
#     combined_score = auc_diff + emd
#     return combined_score

# def find_similar_years(current_year, data, month, day, threshold=None, n=5):
#     period_data = select_data_up_to_date(data, month, day)
#     current_year_data = period_data[current_year].dropna().values
#     distances = []
    
#     for col_year in period_data.columns:
#         if col_year not in ['month_day', current_year]:
#             historical_year_data = period_data[col_year].dropna().values
#             min_length = min(len(current_year_data), len(historical_year_data))
#             combined_score = combine_auc_emd(current_year_data[:min_length], historical_year_data[:min_length])
#             distances.append((col_year, combined_score))
    
#     distances.sort(key=lambda x: x[1])
    
#     # Filter results based on the threshold
#     if threshold is not None:
#         distances = [year for year in distances if year[1] <= threshold]
    
#     return distances[:n]

# # Example usage
# similar_years_partial = find_similar_years('2024', sorted_med_data, 3, 1, threshold= 9 , n=10)
# print("Partial Year Similarities with Combined AUC and EMD:", similar_years_partial)

# similar_years_partial = find_similar_years('2024', sorted_avg_data, 3, 1, threshold= 10, n=10)
# print("Partial Year Similarities with Combined AUC and EMD:", similar_years_partial)
