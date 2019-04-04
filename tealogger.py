# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 13:45:38 2019

@author: adam.rees

Purpose of the script:
    Log number of cups 'o tea over time
"""

# Import modules
import datetime
import time
import sys
import argparse
import os
import sqlite3
import configparser

"""
Set up configuration file.
"""
path = "config.ini"


def createConfig(path):
    txt = input("Enter the proposed location of the teabase.db file: ")
    config = configparser.ConfigParser()
    config['DIRECTORIES'] = {'workingDir': txt}

    with open(path, "w") as config_file:
        config.write(config_file)

    print("Updated Configuration, closing")
    time.sleep(1)
    sys.exit(0)

"""
Set up and call argparse the later FunctionMap relates the modeChoices
list to the Functions defined within this script
"""
modeChoices = ["Cuppa", "24Hr", "Today", "Week",
               "Year", "Counts", "Config"]
parser = argparse.ArgumentParser()
parser.add_argument("mode",
                    help="Which mode?",
                    choices = modeChoices)
parser.add_argument("-t", "--t", "-tea",
                    help="Number of cups of tea",
                    default=1)
parser.parse_args()
args = parser.parse_args()

if not os.path.exists(path):
    createConfig(path)

config = configparser.ConfigParser()
config.read(path)
workingDir = config.get("DIRECTORIES", "workingDir")

# SQL Database Information
database = os.path.join(workingDir,'Teabase.db')

# Function to connect to database
def ConnectDatabase(database):
    conn = sqlite3.connect(database,detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    table_sql = f"""CREATE TABLE Tea
                (id integer PRIMARY KEY,
                createTime TIMESTAMP,
                beverage TEXT,
                count INTEGER)"""
    try:
        c.execute(table_sql)
    except:
        pass
        
    return conn, c


# Function to close connection and commit data
def CloseCommitDatabase(conn):
    conn.commit()
    conn.close()


# Function to call another function
def Decision(mode, path):
    FunctionMap = {"Cuppa": AddTea,
                   "24Hr": TwentyFourTotal,
                   "Today": TodayTotal,
                   "Week": WeekTotal,
                   "Year": AnnualTotal,
                   "Counts": RunTotals,
                   "Config": createConfig}
    func = FunctionMap[mode]

    if mode == "Config":
        func(path)
    elif mode == "Cuppa":
        func(args.t)
    else:
        func()


# Function to add a cup to the sqlite3 file
def AddTea(count):
    conn, c = ConnectDatabase(database)
    insert_sql = f"""INSERT INTO Tea
                (createTime, beverage, count) VALUES (?,?,?)
                """
    data = [datetime.datetime.now(),"tea",count]
    c.execute(insert_sql,data)
    CloseCommitDatabase(conn)
    print(f"Ran the AddTea Function, added: {count} cups O'Tea")


# Code to avoid repeating the totalling functions
def SQLCounting(selectsql):
    conn, c = ConnectDatabase(database)
    c.execute(selectsql)
    TeaTotal = c.fetchone()[0]
    CloseCommitDatabase(conn)

    return TeaTotal


# Function to display today's running total
def TwentyFourTotal():
    select_sql = """
                SELECT SUM(count) from Tea
                where createTime > date('now', '-1 day')
                """
    TeaTotal = SQLCounting(select_sql)
    print(f"You have drunk {TeaTotal} cups in the last 24 hours!")


def TodayTotal():
    d = datetime.datetime.now()
    midnight = datetime.datetime(d.year, d.month, d.day, 1, 0, 0, 0)
    epoch = midnight.timestamp()
    select_sql = f"""
                 SELECT SUM(count) from Tea
                 where createTime > datetime({epoch},'unixepoch')
                 """
    TeaTotal = SQLCounting(select_sql)
    print(f"You have drunk {TeaTotal} cups today!")


# Function to display this weeks running total
def WeekTotal():
    select_sql = """
                 SELECT SUM(count) from Tea
                 where createTime > date('now', '-7 days')
                 """
    TeaTotal = SQLCounting(select_sql)
    print(f"You have drunk {TeaTotal} cups this week!")


# Function to display this years running total
def AnnualTotal():
    select_sql = """
                 SELECT SUM(count) from Tea
                 where createTime > date('now', '-1 year')
                 """
    TeaTotal = SQLCounting(select_sql)
    print(f"You have drunk {TeaTotal} cups this year!")


# Function to run the other functions
def RunTotals():
    TodayTotal()
    TwentyFourTotal()
    WeekTotal()
    AnnualTotal()


# Check the script name and run the functions as required
if __name__ == "__main__":
        Decision(args.mode, path)