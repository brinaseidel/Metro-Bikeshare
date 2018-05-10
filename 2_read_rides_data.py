#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 20:38:32 2017

@author: brinaseidel

This program reads in and combines the bikeshare data for all years of interest,
then transforms it so that we have a count of the # of rides from each station in each time period.
"""
import os
import pandas as pd
import datetime 
import numpy as np

# ****************************
# Read in the bikeshare data for each quarter
# ****************************

# Define a program to format dates
def lookup(date_series):
    dates = {date:pd.to_datetime(date) for date in date_series.unique()}
    return date_series.map(dates)

# First format
bikes_format1 = pd.read_csv("Input Data/2015-Q1-Trips-History-Data.csv")
colnames = ["trip_time", "start_time", "start_loc_name", "end_time", "end_loc_name", "bike_num", "subscription"]
bikes_format1.columns = colnames
bikes_temp = pd.read_csv("Input Data/2015-Q2-Trips-History-Data.csv")
bikes_temp.columns = colnames
bikes_format1 = bikes_format1.append(bikes_temp, ignore_index=True)
bikes_format1['start_time'] = lookup(bikes_format1['start_time'])
        
# Second format -- has different columns
bikes_format2 = pd.read_csv("Input Data/2015-Q3-cabi-trip-history-data.csv")
colnames = ["trip_time", "start_time", "end_time", "start_loc", "start_loc_name", "end_loc", "end_loc_name", "bike_num", "subscription"]
bikes_format2.columns = colnames
bikes_format2['start_time'] = lookup(bikes_format2['start_time'])
bikes_files_format2 = ["Input Data/2015-Q4-Trips-History-Data.csv",
                       "Input Data/2016-Q1-Trips-History-Data.csv",
                       "Input Data/2016-Q2-Trips-History-Data.csv",
                       "Input Data/2016-Q3-Trips-History-Data-1.csv", "Input Data/2016-Q3-Trips-History-Data-2.csv", 
                       "Input Data/2016-Q4-Trips-History-Data.csv", 
                       "Input Data/2017-Q1-Trips-History-Data.csv", 
                       "Input Data/2017-Q2-Trips-History-Data.csv", 
                       "Input Data/2017-Q3-Trips-History-Data.csv", 
                       "Input Data/2017-Q4-Trips-History-Data.csv"]
for file in bikes_files_format2 :
        print(file)
        bikes_temp = pd.read_csv(file)
        bikes_temp.columns = colnames
        # Format dates
        bikes_temp['start_time']= lookup(bikes_temp['start_time'])
        # Append
        bikes_format2=bikes_format2.append(bikes_temp, ignore_index=True)
        print(bikes_format2.shape)

# Standardize station names in all the format 2 observations        
        
# Add station codes to the first format so that it matches the second format
# First, create a crosswalk of station names and codes
bikes_format1.start_loc_name = bikes_format1.start_loc_name.apply(str.strip)
bikes_format2.start_loc_name = bikes_format2.start_loc_name.apply(str.strip)
loc_crosswalk = bikes_format2[["start_loc", "start_loc_name"]].drop_duplicates()
bikes_format1 = pd.merge(bikes_format1, loc_crosswalk, how="left", on=["start_loc_name"])
# Drop end location columns, which we don't need
bikes_format2.drop("end_loc", axis=1, inplace=True)     
# Re-order format 1
bikes_format1 = bikes_format1[["trip_time", "start_time", "end_time", "start_loc", "start_loc_name", "end_loc_name"]]
# Append the two formats
bikes = bikes_format2.append(bikes_format1)

# Drop the cases we can't find a code for
bikes = bikes[bikes.start_loc.isnull() == False]
bikes.index = range(len(bikes))

# ****************************
# Standardize station names within each code for our station code-name crosswalk
# ****************************

# Re-create the crosswalk
loc_crosswalk = bikes[["start_loc", "start_loc_name"]].drop_duplicates()

# Count the # of station names per code
loc_crosswalk.sort_values("start_loc", inplace=True)
loc_crosswalk["counts"] = loc_crosswalk.groupby("start_loc").transform("count")
print(loc_crosswalk[loc_crosswalk.counts > 1])

# Pick just one name per code 
loc_crosswalk = loc_crosswalk[["start_loc", "start_loc_name"]].drop_duplicates("start_loc")

# ****************************
# Collapse to count the number of rides starting at each station in each twenty-minute period
# ****************************

# First, mark twenty-minute periods
def round_time(to_round):
    return to_round - datetime.timedelta(minutes=to_round.minute % 20,
                             seconds=to_round.second,
                             microseconds=to_round.microsecond)
bikes["time_bin"]= bikes.start_time.apply(round_time)
bikes[["start_time", "time_bin"]].head(20)

# Collapse to get the # of rides from each station in each twenty-minute period
bikes = bikes.groupby(["time_bin", "start_loc"]).size().reset_index(name='counts')
bikes.head(10)

# ****************************
# Keep only stations within half a mile of a metro station
# ****************************

# Read in the bikeshare station -level data prepared in get_station_list.py
stations = pd.read_csv("Output Data/Bikeshare Stations.csv")
stations.head()
stations["near_metro"] = np.where((stations.red==0) & (stations.blue==0) 
    & (stations.green==0) & (stations.orange==0) 
    & (stations.silver==0) & (stations.yellow==0), 0, 1)

# Merge station data with trip data
bikes = pd.merge(bikes, stations[["start_loc", "near_metro"]], how="outer", on=["start_loc"])

# Count the cases that are not within a quarter mile of metro
bikes.near_metro.value_counts(dropna=False)  

# Drop those cases
bikes = bikes[bikes.near_metro == 1]
# Update index after droppping values
bikes.index = range(len(bikes))
bikes = bikes[["start_loc", "time_bin", "counts"]]

# ****************************
# Fill in zeros for all missing station-time pairs
# ****************************

times = []
time = datetime.datetime(2015, 1, 1, 0, 0, 0)
end_time = datetime.datetime(2017, 12, 31, 23, 59, 59)
while time <= end_time:
    times.append(time)
    time = time + datetime.timedelta(minutes=20)
locs = bikes.start_loc.unique()

# Make a data frame with all possible combinations of start time and location
import itertools
combined = [locs, times]
bikes_temp = pd.DataFrame(columns = ["start_loc", "time_bin"], data=list(itertools.product(*combined)))
bikes = pd.merge(bikes, bikes_temp, on=["start_loc", "time_bin"], how="outer")
bikes.counts=bikes.counts.fillna(0)

# ****************************
# Save the bikes data
# ****************************
bikes.to_csv("Output Data/Bikeshare Ride Counts.csv", index=False)
