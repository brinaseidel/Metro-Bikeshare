#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 16:09:38 2018

@author: brinaseidel

This program scrapes the WMATA website to collect information on metro delays.

"""


import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
pd.options.mode.chained_assignment = None

# ****************************
# Collect links to scrape
# ****************************

dates = []
links = []

# Loop through 2012-2016
    
for year in range(2012, 2017):
    
    # Download the webpage with links to each day of this month
    url = "https://www.wmata.com/service/daily-report/archives.cfm?year={}".format(year)
    r = requests.get(url)
    
    # Convert HTML into a structured Soup object
    b = BeautifulSoup(r.text, "lxml")
    
    # Pull links and store in a list
    b_links = b.find(id="CS_Element_interiorcontainer").find("ul").findAll("a")
    
    # Loop through the list of link tags and take out the date and the link
    for link in b_links[2:]:
        print(link.text)
        dates.append(link.text)
        links.append("https://www.wmata.com" + link["href"])
        
# Loop through each month of 2017
for month in range(1, 13):
    
    # Download the webpage with links to each day of this month
    url = "https://www.wmata.com/service/daily-report/list.cfm?currentmonth={}&currentyear={}".format(month, 2017)
    r = requests.get(url)
    
    # Convert HTML into a structured Soup object
    b = BeautifulSoup(r.text, "lxml")
    
    # Pull links and store in a list
    b_links = b.find(id="cs_control_2897").findAll("a")
    
    # Loop through the list of link tags and take out the date and the link
    for link in b_links[2:]:
        print(link.text)
        dates.append(link.text)
        links.append("https://www.wmata.com" + link["href"])
    
# ****************************
# Visit links and scrape disruption data
# ****************************

disruptions = []
disruption_date = []

for i, url in enumerate(links):
    
    print(dates[i])
    
    # Download the webpage with disruptions listed
    r = requests.get(url)
    
    # Convert HTML into a structured Soup object
    b = BeautifulSoup(r.text, "lxml")
    
    # Format for months before december 2017
    if dates[i][0:8] != "December" and dates[i][-4:] == "2017" :
        # Find all paragraph breaks in the main text
        b_br = b.find(id="cs_control_2897").findAll("br")
        
        # Loop through all paragraph breaks and examine the next sibling after each paragraph brak
        for br in b_br:
            
            next_s = br.nextSibling
            
            # Store the text as a disruption if the next sibling is not br
            if next_s != None:
                if next_s.name != "br" and next_s.name != "p" and next_s.name != "xc2":
                    disruptions.append(next_s)
                    disruption_date.append(dates[i])

    else:
        # Find all <p> tags
        b_p = b.find(id="cs_control_2897")       
        if b_p == None:
            b_p = b.find(id="CS_CCF_3660_3664")
        b_p = b_p.findAll("p")  
        # Loop through all p tags and pull the text
        for p in b_p:
            disruptions.append(p.text.replace("\n", " "))
            disruption_date.append(dates[i])
            
# ****************************
# Create data frame of disruptions and clean the disruption text to get what we're interested in
# NOTE: Some of this code is from Mark Delcambre, accessed via Github
# ****************************
                
# Make data frame
d = pd.DataFrame({"date": disruption_date,
                  "dis": disruptions})
d["time"] = ""
d["red"] = 0
d["orange"] = 0
d["yellow"] = 0
d["green"] = 0
d["blue"] = 0
d["silver"] = 0
d["delay"] = ""

# Trim disruptions
d.dis = d.dis.str.strip()

# Drop lines that should not have been read in
d = d[d["dis"]!="\n"]
d = d[d["dis"]!="\xc2\xa0"]
d = d[d["dis"]!="Report Archives"]
d = d[d["dis"].str.contains("expressed")==False]
d = d[d["dis"].str.contains("schedule adherence")==False]
d = d[d["dis"]!=""]

# Update index after droppping values
d.index = range(len(d))
d.dis = d.dis.replace("\xc2\xa0", "")
d.dis = d.dis.replace("*", "")

# Drop the cases where trains were expressed

# Define a fuction to parse the text of each disruption 
import re
time_regex = re.compile(r'^(\d{1,2}:\d\d (?:a\.m\.|p\.m\.))')
delay_regex1 = re.compile(r'(\d+)-minute delay')
delay_regex2 = re.compile(r'delayed (.\d?) minutes')
delay_regex3 = re.compile(r'delays up to (.\d?) minute')
delay_regex4 = re.compile(r'(\d+)-minute gap')
delay_regex5 = re.compile(r'delayed (.\d?) due')
delay_regex6 = re.compile(r'delay up to (.\d?) minutes')
delay_regex7 = re.compile(r'held (.\d?) minutes')
delay_regex8 = re.compile(r'delays up to(.\d?) minutes')
delay_regex9 = re.compile(r'delays of up to(.\d?) minutes')

def parse(disruption):
    """Function to parse the disruption strings into a tuple of data.
    Args:
        disruption (string)
    Returns:
        tuple of time, color dummies, delay
    """
    # Start time of disruption
    time = time_regex.search(disruption).group(1)
    
    # Color 
    red = 0
    orange = 0
    yellow = 0
    green = 0
    blue = 0
    silver = 0
    if "Red" in disruption:
        red = 1
    if "Orange" in disruption:
        orange = 1
    if "Yellow" in disruption:
        yellow = 1
    if "Green" in disruption:
        green = 1
    if "Blue" in disruption:
        blue = 1
    if "Silver" in disruption:
        silver = 1
        
    # Delay time
    delay = delay_regex1.search(disruption)
    if delay == None:
        delay = delay_regex2.search(disruption)
    if delay == None:
        delay = delay_regex3.search(disruption)
    if delay == None:
        delay = delay_regex4.search(disruption)
    if delay == None:
        delay = delay_regex5.search(disruption)
    if delay == None:
        delay = delay_regex6.search(disruption)
    if delay == None:
        delay = delay_regex7.search(disruption)
    if delay == None:
        delay = delay_regex8.search(disruption)
    if delay == None:
        delay = delay_regex9.search(disruption)               
    delay = delay.group(1)

    return time, red, orange, yellow, green, blue, silver, delay

# Parse the scraped disruptions
for i in range(0, len(d)):
    try:
        d.time[i], d.red[i], d.orange[i], d.yellow[i], d.green[i], d.blue[i], d.silver[i], d.delay[i] = parse(d.dis[i])
    except:
       print(d.dis[i])

# ****************************
# Drop cases we couldn't parse
# ****************************
print(d.shape)
d = d[d.time!=""]
d.index = range(len(d))
print(d.shape)

# ****************************
# Save the results
# ****************************

d.to_csv("Output Data/Metro Disruptions.csv", index=False)

# ****************************
# Produce some graphs
# ****************************
d = pd.read_csv("Output Data/Metro Disruptions.csv")
d.time = d.time.str.replace("a.m.", "AM")
d.time = d.time.str.replace("p.m.", "PM")
d["dt"] = d.date+" "+d.time
d["dt"] = pd.to_datetime(d["dt"])
d = d[d.dt.isnull() == False]
d.index = range(len(d))

# Number of delays per year
d["year"] = d["dt"].apply(lambda x: x.year)
d_years = d.groupby("year").size().reset_index(name='delays')
fig1 = d_years.plot("year", "delays", color="#E3492D", marker='.', markersize=10, legend=False)
fig1.set_xlabel("Year")  
fig1.set_ylabel("# of Delays")                                    
fig1 
fig = fig1.get_figure()              
fig.savefig('Output Data/Delays by Year.png', transparent=True)

# Mean delaytie
fig2=d.delay.hist(color="#E3492D", bins=30)
fig2.set_ylabel("# of Delays")  
fig2.set_xlabel("Length of Delay (Minutes)") 
fig2
fig = fig2.get_figure()              
fig.savefig('Output Data/Delay Time Histogram.png', transparent=True)
