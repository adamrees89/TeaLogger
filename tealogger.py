# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 13:45:38 2019

@author: adam.rees

Purpose of the script:
    Log number of cups 'o tea over time
"""

#Import modules
import datetime
import time #Used for the sleep functions
import argparse
import os
import sqlite3

"""
Set up and call argparse the later FunctionMap relates the modeChoices
list to the Functions defined within this script
"""
modeChoices = ["newCuppa", "countToday", "countWeek", "countYear"]
parser = argparse.ArgumentParser()
parser.add_argument("mode",
                    help="Which mode?",
                    choices = modeChoices)
parser.add_argument("-t", "--t", "-tea",
                    help="Number of cups of tea",
                    default=1)
parser.parse_args()
args = parser.parse_args()

#SQL Database Information
workingDir = 'S:\Adam Rees'
database = os.path.join(workingDir,'Teabase.db')

#Function to connect to database
def ConnectDatabase(database):
    conn = sqlite3.connect(database,detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    table_sql = f"""CREATE TABLE Tea
                (id PRIMARY KEY,
                createTime TIMESTAMP,
                beverage TEXT,
                count INTEGER)"""
    try:
        c.execute(table_sql)
    except:
        pass
        
    return conn, c

#Function to close connection and commit data
def CloseCommitDatabase(conn):
    conn.commit()
    conn.close()

#Function to call another function
def Decision(mode):
    FunctionMap = {"newCuppa":AddTea,
                   "countToday":TodayTotal,
                   "countWeek":WeekTotal,
                   "countYear":AnnualTotal}
    FunctionMap[mode]()

#Function to add a cup to the sqlite3 file
def AddTea():
    count = args.t
    print("Ran the AddTea Function")
    conn, c = ConnectDatabase(database)
    insert_sql = f"""INSERT INTO Tea
                (createTime, beverage, count) VALUES (?,?,?)
                """
    data = [datetime.datetime.now(),"tea",count]
    c.execute(insert_sql,data)
    CloseCommitDatabase(conn)

#Code to avoid repeating the totalling functions
def SQLCounting(selectsql):
    conn, c = ConnectDatabase(database)
    c.execute(selectsql)
    TeaTotal = c.fetchone()[0]
    CloseCommitDatabase(conn)
    
    return TeaTotal

#Function to display today's running total
def TodayTotal():
    select_sql = """
        SELECT SUM(count) from Tea 
        where createTime > date('now', '-1 day')
        """
    TeaTotal = SQLCounting(select_sql)
    print(TeaTotal)

#Function to display this weeks running total
def WeekTotal():
    select_sql = """
        SELECT SUM(count) from Tea 
        where createTime > date('now', '-7 days')
        """
    TeaTotal = SQLCounting(select_sql)
    print(TeaTotal)

#Function to display this years running total
def AnnualTotal():
    select_sql = """
        SELECT SUM(count) from Tea 
        where createTime > date('now', '-1 year')
        """
    TeaTotal = SQLCounting(select_sql)
    print(TeaTotal)


#Check the script name and run the functions as required
if __name__ == "__main__":
    Decision(args.mode)