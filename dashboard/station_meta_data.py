#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 16:34:36 2024

@author: Lerberber
"""

import requests

BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"

def get_stations_metadata(base_url=BASE_URL):
    """
    Fetches a list of reservoir metadata for the specified HUC region based on network codes.
    """
    endpoint = "stations"
    
    params = {
        "networkCodes": "*",   
        "activeOnly": "true"
    }
    
    url = f"{base_url}/{endpoint}"
    
    response = requests.get(url, params=params)
    
    # print(f"{'Success!' if response.ok else 'Failed!'} - {url}")
    if response.ok:
        data = response.json()
        return [station['stationTriplet'] for station in data if 'stationTriplet' in station]
    return []



# stations_metadata = get_stations_metadata()