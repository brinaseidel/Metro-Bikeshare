#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 12:48:11 2018

@author: brinaseidel

This program combines the bikeshare data, the metro delay data, and additional features such as weather.  
"""
import os
import pandas as pd
import datetime 
import numpy as np

# ****************************
# Read in the prepared bikeshare data
# ****************************
bikes = pd.read_csv("Output Data/Bikeshare Ride Counts.csv")
bikes.head()
bikes.describe()
bikes.time_bin = pd.to_datetime(bikes.time_bin)

# ****************************
# Add in dummies for metro lines & distance to each line
# ****************************

# Read in the bikeshare station -level data prepared in get_station_list.py
stations = pd.read_csv("Output Data/Bikeshare Stations.csv")
stations.head()
stations.drop(["lat", "lon"], axis=1, inplace=True)
bikes = pd.merge(bikes, stations, how="left", on=["start_loc"])

# ****************************
# Add in explanatory variable: metro delays
# ****************************
disrupt = pd.read_csv("Output Data/Metro Disruptions.csv")
disrupt.head()
disrupt.describe()

# Format dates and times
disrupt.time = disrupt.time.str.replace("a.m.", "AM")
disrupt.time = disrupt.time.str.replace("p.m.", "PM")
disrupt["dt"] = disrupt.date+" "+disrupt.time
disrupt["dt"] = pd.to_datetime(disrupt["dt"])
disrupt = disrupt[disrupt.dt.isnull() == False]
disrupt.index = range(len(disrupt))
# Mark time bins
def round_time(to_round):
    return to_round - datetime.timedelta(minutes=to_round.minute % 20,
                             seconds=to_round.second,
                             microseconds=to_round.microsecond)
disrupt["time_bin"]= disrupt.dt.apply(round_time)
disrupt[["dt", "time_bin"]].head()
disrupt.drop(["date", "dis", "time", "dt"], axis=1, inplace=True)

# "Reshape" sort of, by hand, so that there's only one color marked per line
disrupt = disrupt[["red", "orange", "yellow", "green", "blue", "silver", "delay", "time_bin"]]
for i in range(0, len(disrupt)):
    total = disrupt.red[i] + disrupt.orange[i] + disrupt.yellow[i] + disrupt.green[i] + disrupt.blue[i] + disrupt.silver[i]
    for j in range(0, total-1):
        if disrupt.red[i] == 1:
            disrupt.loc[i, "red"] = 0
            disrupt.loc[len(disrupt)]  = [1, 0, 0, 0, 0, 0, disrupt.delay[i], disrupt.time_bin[i]]
        elif disrupt.orange[i] == 1:
            disrupt.loc[i, "orange"] = 0
            disrupt.loc[len(disrupt)]  = [0, 1, 0, 0, 0, 0, disrupt.delay[i], disrupt.time_bin[i]]
        elif disrupt.yellow[i] == 1:
            disrupt.loc[i, "yellow"] = 0
            disrupt.loc[len(disrupt)]  = [0, 0, 1, 0, 0, 0, disrupt.delay[i], disrupt.time_bin[i]]
        elif disrupt.green[i] == 1:
            disrupt.loc[i, "green"] = 0
            disrupt.loc[len(disrupt)]  = [0, 0, 0, 1, 0, 0, disrupt.delay[i], disrupt.time_bin[i]]
        elif disrupt.blue[i] == 1:
            disrupt.loc[i, "blue"] = 0
            disrupt.loc[len(disrupt)]  = [0, 0, 0, 0, 1, 0, disrupt.delay[i], disrupt.time_bin[i]]
        elif disrupt.silver[i] == 1:
            disrupt.loc[i, "silver"] = 0
            disrupt.loc[len(disrupt)]  = [0, 0, 0, 0, 0, 1, disrupt.delay[i], disrupt.time_bin[i]]            

# Mark total delay time on each line in each time bin
disrupt["delaytime"] = disrupt.groupby(["time_bin", "red","orange", "yellow", "green", "blue", "silver"]).delay.transform('sum')

# Keep only necessary variables
disrupt = disrupt[["time_bin", "red", "orange", "yellow", "green", "blue", "silver", "delaytime"]]
disrupt.drop_duplicates(inplace=True)

# Merge by time and line, updating the "delay" varible with the longest delay fo any line within half a mile of the stop
bikes["delay"] = 0
bikes = pd.merge(bikes, disrupt[["time_bin", "red", "delaytime"]][disrupt.red==1], on=["time_bin", "red"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

bikes = pd.merge(bikes, disrupt[["time_bin", "orange", "delaytime"]][disrupt.orange==1], on=["time_bin", "orange"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

bikes = pd.merge(bikes, disrupt[["time_bin", "yellow", "delaytime"]][disrupt.yellow==1], on=["time_bin", "yellow"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

bikes = pd.merge(bikes, disrupt[["time_bin", "green", "delaytime"]][disrupt.green==1], on=["time_bin", "green"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

bikes = pd.merge(bikes, disrupt[["time_bin", "blue", "delaytime"]][disrupt.blue==1], on=["time_bin", "blue"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

bikes = pd.merge(bikes, disrupt[["time_bin", "silver", "delaytime"]][disrupt.silver==1], on=["time_bin", "silver"], how="left")
bikes.loc[bikes.delaytime > bikes.delay , "delay"] = bikes.loc[bikes.delaytime > bikes.delay, "delaytime"] 
bikes.drop("delaytime", axis=1, inplace=True)

# ****************************
# Add in control variables: # of docks per station
# ****************************

# Read in the station attribute list
stationsdf = pd.read_csv("Input Data/Capital_Bike_Share_Locations.csv")
stationsdf.head()
stationsdf = stationsdf[["TERMINAL_NUMBER", "NUMBER_OF_BIKES", "NUMBER_OF_EMPTY_DOCKS"]]
stationsdf.columns = ["start_loc", "n_bikes", "n_empty_docks"]
stationsdf["n_docks"] = stationsdf.n_bikes + stationsdf.n_empty_docks
stationsdf = stationsdf[["start_loc", "n_docks"]]

# Merge in the number of docks
bikes = pd.merge(bikes, stationsdf, on=["start_loc"], how="left")

# ****************************
# Add in control variable: daily precipitation data
# ****************************

# Read in the precipitation data
precip = pd.read_csv("Input Data/Daily Precipitation Data.csv")
colnames = ["station", "date", "precip", "snow", "snow_depth"]
precip.columns = colnames
precip["date"] = pd.to_datetime(precip.date)
precip.drop("station", axis=1, inplace=True)

# Make day variable for merging
bikes["date"] = bikes.time_bin.dt.date
bikes.date = pd.to_datetime(bikes.date)

# Merge data frames
bikes = pd.merge(bikes, precip, on="date", how="left")

# ****************************
# Add in control variable: hourly temperature data
# ****************************

# Read in the temperature data
temp = pd.read_csv("Input Data/Hourly Temperature Data.csv")
temp.head()
temp.date = temp.date.apply(str)
temp.date = temp.date.apply(lambda x: x[4:6]+"/"+x[6:8]+"/"+x[0:4])
temp.hour = temp.hour/100
temp.hour = temp.hour.apply(int)
temp.hour = temp.hour.apply(str)
temp.date = temp.date + " " + temp.hour + ":00"
temp.date = pd.to_datetime(temp.date)

# Make date-hour  variable for merging
def round_time(to_round):
    return to_round - datetime.timedelta(minutes=to_round.minute % 60,
                             seconds=to_round.second,
                             microseconds=to_round.microsecond)
bikes["date"]= bikes.time_bin.apply(round_time)

bikes = pd.merge(bikes, temp, on="date", how="left")
bikes.drop(["date", "hour",], axis=1, inplace=True)
# ****************************
# Save the data
# ****************************
bikes.to_csv("Output Data/Bikeshare Ride Counts with Features.csv", index=False)
