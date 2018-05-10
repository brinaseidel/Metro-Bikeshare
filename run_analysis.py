#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:03:17 2018

@author: brinaseidel
"""

import os
import pandas as pd
import datetime 
import numpy as np
import matplotlib.pyplot as plt
os.chdir("/Users/brinaseidel/Documents/School/GA Data Science/Final Project")

# ****************************
# Read in the prepared bikeshare data with features
# ****************************
bikes = pd.read_csv("Output Data/Bikeshare Ride Counts with Features.csv")
bikes.head()
bikes.time_bin = pd.to_datetime(bikes.time_bin)
bikes.drop(["red", "orange", "yellow", "green", "blue", "silver"], axis=1, inplace=True)
# ****************************
# Add some features
# ****************************

# Day of week
bikes["day"] = bikes.time_bin.dt.dayofweek
day_dummies = pd.get_dummies(bikes.day, prefix='day')
day_dummies.drop('day_0', axis=1, inplace=True)
bikes = pd.concat([bikes, day_dummies], axis=1)

# Hour
bikes["hour"] = bikes.time_bin.dt.hour
hour_dummies = pd.get_dummies(bikes.hour, prefix='hour')
hour_dummies.drop(["hour_0", "hour_1", "hour_2", "hour_3", "hour_4"], axis=1, inplace=True)
bikes = pd.concat([bikes, hour_dummies], axis=1)

# Hour
bikes["hour"] = bikes.time_bin.dt.hour
hour_dummies = pd.get_dummies(bikes.hour, prefix='hour')
hour_dummies.drop(["hour_0", "hour_1", "hour_2", "hour_3", "hour_4"], axis=1, inplace=True)
bikes = pd.concat([bikes, hour_dummies], axis=1)

# Distance to metro
bikes["min_dist"] = bikes[["red_dist", "orange_dist", "yellow_dist", "green_dist", "blue_dist", "silver_dist"]].min(axis=1)
bikes.drop(["red_dist", "orange_dist", "yellow_dist", "green_dist", "blue_dist", "silver_dist"], axis=1, inplace=True)

# Major delay dummy
bikes["major_delay"] = bikes.delay > 8
bikes.major_delay = 1*bikes.major_delay

# Lagged delay
bikes.sort_values(["start_loc", "time_bin"], axis=0, inplace = True)
bikes["delay_lag"] = bikes.groupby('start_loc')['delay'].shift(1)
bikes[["delay", "delay_lag"]].head(-50)
bikes["major_delay_lag"] = bikes.groupby('start_loc')['major_delay'].shift(1)

# ****************************
# Drop cases with missing data
# ****************************
bikes = bikes.dropna(axis=0, how="any")

# ****************************
# Linear regression model
# ****************************
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split

# Define a function to split data into train and test, run a linear regerssion, and calculate RMSE for test data
def lin_reg_tts(df, feature_cols):
    X = df[feature_cols]
    y = df[["counts"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=123)
    linreg = LinearRegression()
    linreg.fit(X_train, y_train)
    y_pred = linreg.predict(X_test)
    print(pd.Series(list(zip(feature_cols, linreg.coef_[0]))))
    return np.sqrt(metrics.mean_squared_error(y_test, y_pred))

# Basic model
feature_cols = ["min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay
feature_cols = ["delay", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay x distance from metro
bikes["delayxdist"] = bikes.delay * bikes.min_dist
feature_cols = ["delay", "min_dist", "delayxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay dummy
feature_cols = ["major_delay", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Major delay interaction
bikes["major_delayxdist"] = bikes.major_delay * bikes.min_dist
feature_cols = ["major_delay", "min_dist", "major_delayxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

feature_cols = ["delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged delay
feature_cols = ["delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged major delay
feature_cols = ["major_delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged delay interaction
bikes["delay_lagxdist"] = bikes.delay_lag * bikes.min_dist
feature_cols = ["delay_lag", "min_dist", "delay_lagxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged major delay interaction
bikes["major_delay_lagxdist"] = bikes.major_delay_lag * bikes.min_dist
feature_cols = ["major_delay_lag", "min_dist", "major_delay_lagxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# ****************************
# Ridge
# ****************************
from sklearn.linear_model import Ridge

def ridge_reg_tts(feature_cols, alpha):
    X = bikes[feature_cols]
    y = bikes[["counts"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=123)
    ridgereg = Ridge(alpha=alpha,normalize=True)
    ridgereg.fit(X_train, y_train)
    y_pred = ridgereg.predict(X_test)
    delay_lag_coef.append(ridgereg.coef_[0][0])
    print(pd.Series(list(zip(feature_cols, ridgereg.coef_[0]))))
    return np.sqrt(metrics.mean_squared_error(y_test, y_pred))

feature_cols = ["delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
alpha_ridge = [1e-5,  1e-4, 1e-3, 1e-2, 1, 10]
ridge_rmse = []
delay_lag_coef = []
for alpha in alpha_ridge:
    print("Alpha: ", alpha)
    ridge_rmse.append(ridge_reg_tts(feature_cols, alpha))
    print(ridge_rmse[len(ridge_rmse)-1])

fig3 = plt.gca()
fig3.plot(alpha_ridge, ridge_rmse, color="#E3492D",)
fig3.set_xscale('log')
fig3.set_ylabel("RMSE")  
fig3.set_xlabel("Alpha") 
fig3
fig = fig3.get_figure()              
fig.savefig('Output Data/Ridge RMSE.png', transparent=True)

fig4 = plt.gca()
fig4.plot(alpha_ridge, delay_lag_coef, color="#E3492D",)
fig4.set_xscale('log')
fig4.set_ylabel("Lagged Delay Time Coeff")  
fig4.set_xlabel("Alpha") 
fig4
fig = fig4.get_figure()              
fig.savefig('Output Data/Ridge Coeffs.png', transparent=True)

# ****************************
# Linreg using sample for hours when metro is open 
# ****************************
bikes = bikes[(bikes.hour>=5)]

# Basic model
feature_cols = ["min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay
feature_cols = ["delay", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay x distance from metro
bikes["delayxdist"] = bikes.delay * bikes.min_dist
feature_cols = ["delay", "min_dist", "delayxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# With delay dummy
feature_cols = ["major_delay", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Major delay interaction
bikes["major_delayxdist"] = bikes.major_delay * bikes.min_dist
feature_cols = ["major_delay", "min_dist", "major_delayxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged delay
feature_cols = ["delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged major delay
feature_cols = ["major_delay_lag", "min_dist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged delay interaction
bikes["delay_lagxdist"] = bikes.delay_lag * bikes.min_dist
feature_cols = ["delay_lag", "min_dist", "delay_lagxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# Lagged major delay interaction
bikes["major_delay_lagxdist"] = bikes.major_delay_lag * bikes.min_dist
feature_cols = ["major_delay_lag", "min_dist", "major_delay_lagxdist", "n_docks", "precip", "snow", "snow_depth", "temp", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", 
                "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"]
lin_reg_tts(bikes, feature_cols)

# ****************************
# ARIMA
# ****************************

from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm

station=bikes[bikes.start_loc == 31603]
station.index = station.time_bin
arima = sm.tsa.ARIMA(endog=station['counts'],exog=station[['delay']],order=[3,1,3])
results=arima.fit()
print(results.summary())


