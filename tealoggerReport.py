# -*- coding: utf-8 -*-
"""
Created on Friday 20th December 2019

@author: adam.rees

Purpose of the script:
    Analyse the cups of tea logged by tealogger.py
"""

import datetime
import time
import sys
import os
import sqlite3
import configparser
import numpy
import matplotlib.pyplot as plt

"""
Get path for configuration file for tealogger.py and read file
"""
path = "BrewConfig.ini"

try:
    config = configparser.ConfigParser()
    config.read(path)
    workingDir = config.get("DIRECTORIES", "workingDir")
except Exception as e:
    print("Failed to open config file, does it exist, and is this script in the same directory as tealogger.py and the config file?")
    sys.exit(1)

# SQL Database Information
database = os.path.join(workingDir,'Teabase.db')

"""
I'm going to define the functions below
"""

# Function to connect to database
def ConnectDatabase(database):
    conn = sqlite3.connect(database,detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    return conn, c


#Function to get all data from database and store it in a numpy array.
def GetData(c):
    c.execute('SELECT createTime FROM Tea')
    data = c.fetchall()
    to_timestamp = numpy.vectorize(lambda x: x.timestamp())
    time_stamps = to_timestamp(data)
    bins, edges = numpy.histogram(time_stamps)
    left,right = edges[:-1],edges[1:]
    X = numpy.array([left,right]).T.flatten()
    Y = numpy.array([bins,bins]).T.flatten()

    plt.plot(X,Y)
    plt.show()


"""
Run the functions
"""

conn,c = ConnectDatabase(database)
GetData(c)