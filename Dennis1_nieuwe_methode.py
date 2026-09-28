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
for start_tijd in bus_plan_org['start time'].head(5):
    start_tijd = pd.to_datetime(start_tijd,format='%H:%M')
    print(start_tijd)
for eind_tijd in bus_plan_org['end time'].head(5):
    eind_tijd = pd.to_datetime(eind_tijd,format='%H:%M')
    print(eind_tijd)

# Feasibility-check 1: begin-, eindbestemming, vertrektijd en lijn moeten hetzelfde zijn
index1 = 0
for i in range (len(tt['start'].head(1))):
    start_loc_tt = tt['start'][index1]
    end_loc_tt = tt['end'][index1]
    dep_time_tt = tt['departure_time'][index1]
    line_tt = tt['line'][index1]
    print(start_loc_tt, end_loc_tt, dep_time_tt, line_tt)
    index2 = 0
    for j in range (len(bus_plan_org['start location'])):
        waarde = bus_plan_org.iloc[index2]
        if start_loc_tt in waarde and end_loc_tt in waarde and dep_time_tt in waarde and line_tt in waarde:
            print(index2, start_loc_tt, end_loc_tt, dep_time_tt, line_tt)
        index2 += 1
