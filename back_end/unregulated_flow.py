#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 16:26:17 2024

@author: Lerberber
"""

# Mock data for demonstration
def get_mock_streamflow_data():
    # Replace this with actual data retrieval
    inflow_data = [100, 150, 200, 250]  # Inflow data (cubic feet per second)
    outflow_data = [80, 120, 160, 200]  # Outflow data (cubic feet per second)
    return inflow_data, outflow_data


def get_mock_storage_data():
    # Replace this with actual data retrieval
    start_storage = 1000  # Start storage volume (cubic feet)
    end_storage = 1100    # End storage volume (cubic feet)
    return start_storage, end_storage

def get_mock_storage_data():
    # Replace this with actual data retrieval
    start_storage = 1000  # Start storage volume (cubic feet)
    end_storage = 1100    # End storage volume (cubic feet)
    return start_storage, end_storage


def calculate_unregulated_flow(inflow, outflow, start_storage, end_storage):
    change_in_storage = end_storage - start_storage
    unregulated_flow = sum(outflow) - sum(inflow) + change_in_storage
    return unregulated_flow

