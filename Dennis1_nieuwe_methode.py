# Code_improved_bus_plan
import contextlib
import sys

# Code_improved_bus_plan
# Dennis
# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import datetime as dt
import time
import warnings
warnings.filterwarnings("ignore")

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Importing relevant data files
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')
bus_plan_org = pd.read_excel('Bus_Planning.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','bus'])

# Data cleanen voor start- en eindtijden in 'Bus_Planning.xlsx'
import datetime as dt
index1 = 0
bus_plan_org['start time'] = bus_plan_org['start time'].astype(str)
dep_times = []
for i in range (len(bus_plan_org['start time'])):
    dep_time_bp = bus_plan_org['start time'][index1]
    dep_time_bp = str(dep_time_bp)
    dep_bp = dt.datetime.strptime(dep_time_bp, '%H:%M:%S')
    dep_bp = dep_bp.strftime('%H:%M')
    dep_times.append(dep_bp)
    index1 += 1

print(dep_times)
# Feasibility-check 1: begin-, eindbestemming, vertrektijd en lijn moeten hetzelfde zijn
index1 = 0
for i in range (len(tt['start'].head(1))):
    start_loc_tt = tt['start'][index1]
    end_loc_tt = tt['end'][index1]
    dep_time_tt = tt['departure_time'][index1]
    line_tt = tt['line'][index1]

    index2 = 0
    for j in range (len(bus_plan_org['start location'])):
        waarde = bus_plan_org.iloc[index2]
        waarde_tijd = dep_times[index2]
        print(waarde)
        if start_loc_tt in waarde and end_loc_tt in waarde and line_tt in waarde:
            if dep_time_tt in waarde_tijd:
                print(index2, start_loc_tt, dep_time_tt, end_loc_tt, line_tt)
        index2 += 1