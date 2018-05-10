#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 19:34:44 2018

@author: brinaseidel

This program reads in the list of metro stations and combines it with data on the line, latitude, and longitude from the WMATA API.
"""

import os
import pandas as pd


# ****************************
# Read in the bikeshare data
# ****************************
bikes = pd.read_csv("Input Data/2017-Q1-Trips-History-Data.csv")
bikes.head()
colnames = ["trip_time", "start_time", "end_time", "start_loc", "start_loc_name", "end_loc", "end_loc_name", "bike_num", "subscription"]
bikes.columns = colnames

# ****************************
# Get a unique list of stations
# ****************************
stations = list(bikes.start_loc.value_counts().index)
print(len(stations))

# ****************************
# Merge in the latitude and longitude
# ****************************

# Read in stations dataset
stationsdf = pd.read_csv("Input Data/Capital_Bike_Share_Locations.csv")
stationsdf.head()
stationsdf = stationsdf[["TERMINAL_NUMBER", "LATITUDE", "LONGITUDE"]]
stationsdf.columns = ["start_loc", "lat", "lon"]

# Merge with our list of stations - we will do this just to make sure that station spelling etc. is the same in both datasets
stations = pd.DataFrame(stations)
stations.columns = ["start_loc"]
stations["in_trip_data"] = 1 # This marks that the station is in our trip dataset

bikeshare_stations = pd.merge(stations, stationsdf, how="outer", on=["start_loc"])

# Count cases that were in the stations list but not in our trip data
bikeshare_stations.in_trip_data.value_counts(dropna=False)  # 38 cases

# Check cases in trip data but not in station data
print(bikeshare_stations[bikeshare_stations["lon"].isnull()])   # 1 case - whatever, we'll drop this

# Drop cases that did not merge
bikeshare_stations = bikeshare_stations[bikeshare_stations.in_trip_data == 1]
bikeshare_stations = bikeshare_stations[bikeshare_stations["lon"].isnull()==False]
# Update index after droppping values
bikeshare_stations.index = range(len(bikeshare_stations))

# ****************************
# Read in the list of metro stations from the metro API, with latitude and longitude
# ****************************
import http.client

headers = {
    'api_key': 'e546c4e7a7a746c994d6864e23849ee6',
}
try:
    conn = http.client.HTTPSConnection('api.wmata.com')
    conn.request("GET", "/Rail.svc/json/jStations?%s", "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
    
# Put into a data frame
temp = pd.read_json(data)
temp.head() # Weirdly, each row seems to be a dictionary

# Define a program to pull the station name, line, latitude, and longitude from the dictionaries
def get_station_data(dict):
    name = dict["Name"]
    lat = dict["Lat"]
    lon = dict["Lon"]
    line = dict["LineCode1"]
    return name, lat, lon, line

# Create lists in which we'll store the station data
name = []
lat = []
lon = []
line = []

# Loop through all rows of the station data
for i in range(0, len(temp)):
    name_temp, lat_temp, lon_temp, line_temp = get_station_data(temp.Stations[i])
    name.append(name_temp)
    lat.append(lat_temp)
    lon.append(lon_temp)
    line.append(line_temp)
# Combine all metro data in a data frame
metro = pd.DataFrame(
    {'name': name,
     'lat': lat,
     'lon': lon,
     'line': line
    })
metro.head()

# ****************************
# Calculate the distance bewteen each bikeshare station and each metro station,
# and return a list of bikeshare stations marked by:
#   - whether they are within half a mile of each line
#   - the shortest distance to each line
# ****************************
bikeshare_stations["red"] = 0
bikeshare_stations["blue"] = 0
bikeshare_stations["green"] = 0
bikeshare_stations["orange"] = 0
bikeshare_stations["yellow"] = 0
bikeshare_stations["silver"] = 0

bikeshare_stations["red_dist"] = 1000.0
bikeshare_stations["blue_dist"] = 1000.0
bikeshare_stations["green_dist"] = 1000.0
bikeshare_stations["orange_dist"] = 1000.0
bikeshare_stations["yellow_dist"] = 1000.0
bikeshare_stations["silver_dist"] = 1000.0

from geopy.distance import vincenty

# Loop through bikeshare stations
for i in range(0, len(bikeshare_stations)):

    # Loop through metro stations
    for j in range(0, len(metro)):
        
        # Calculate distance between this bikeshare station and this metro station
        dist = vincenty((bikeshare_stations.lat[i], bikeshare_stations.lon[i]), (metro.lat[j], metro.lon[j])).miles
        
        # Update the dummy marking whether the bikeshare station is within half a mile of a metro station of each line
        if dist <= 0.5:
            if metro.line[j] == "RD":
                bikeshare_stations.at[i, "red"] = 1
            elif metro.line[j] == "BL":
                bikeshare_stations.at[i, "blue"] = 1
            elif metro.line[j] == "GR":
                bikeshare_stations.at[i, "green"] = 1
            elif metro.line[j] == "OR":
                bikeshare_stations.at[i, "orange"] = 1
            elif metro.line[j] == "SV":
                bikeshare_stations.at[i, "silver"] = 1
            elif metro.line[j] == "YL":
                bikeshare_stations.at[i, "yellow"] = 1  
        
        # Update the minimum distance between this station and each line
        if metro.line[j] == "RD" and bikeshare_stations.red_dist[i] > dist:
            bikeshare_stations.at[i, "red_dist"] = dist
        elif metro.line[j] == "BL" and bikeshare_stations.blue_dist[i] > dist:
            bikeshare_stations.at[i, "blue_dist"] = dist
        elif metro.line[j] == "GR" and bikeshare_stations.green_dist[i] > dist:
            bikeshare_stations.at[i, "green_dist"] = dist
        elif metro.line[j] == "OR" and bikeshare_stations.orange_dist[i] > dist:
            bikeshare_stations.at[i, "orange_dist"] = dist
        elif metro.line[j] == "SV" and bikeshare_stations.silver_dist[i] > dist:
            bikeshare_stations.at[i, "silver_dist"] = dist
        elif metro.line[j] == "YL" and bikeshare_stations.yellow_dist[i] > dist:
            bikeshare_stations.at[i, "yellow_dist"] = dist
            
bikeshare_stations.head()
bikeshare_stations.describe()
# Show count of cases that are not within half a mile of metro
print(bikeshare_stations[(bikeshare_stations.red==0) & (bikeshare_stations.blue==0) 
    & (bikeshare_stations.green==0) & (bikeshare_stations.orange==0) 
    & (bikeshare_stations.silver==0) & (bikeshare_stations.yellow==0)].count())

# ****************************
# Save the results
# ****************************
bikeshare_stations=bikeshare_stations.drop(["in_trip_data"], axis=1)
bikeshare_stations.to_csv("Output Data/Bikeshare Stations.csv", index=False)
