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

# Dataframe for improved bus plan; voor alle rijen van de busplanning die in het rooster voorkomen
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

# Feasibility-check 1: begin-, eindbestemming, vertrektijd en lijn moeten hetzelfde zijn

index0 = 0
for i in (bus_plan_org['line']):
    if pd.isna(i):
        bus_plan_org.loc[index0, 'line'] = 0
    else:
        bus_plan_org.loc[index0, 'line'] = int(i)
    index0 += 1

index1 = 0
bus_plan_org['line'] = bus_plan_org['line'].astype(int).map(int)
for i in range (len(tt['start'])):
    start_loc_tt = tt['start'][index1]
    end_loc_tt = tt['end'][index1]
    dep_time_tt = tt['departure_time'][index1]
    line_tt = tt['line'][index1]

    index2 = 0
    for j in range (len(bus_plan_org['start location'])):
        rij = bus_plan_org.iloc[index2]
        start_loc_bp = (bus_plan_org['start location'][index2])
        end_loc_bp = (bus_plan_org['end location'][index2])
        line_bp = (bus_plan_org['line'][index2])
        waarde_tijd = dep_times[index2]
        if start_loc_tt in start_loc_bp:
            if end_loc_tt in end_loc_bp:
                    if dep_time_tt in waarde_tijd:
                        ibp.loc[index2] = rij 
        index2 += 1
    index1 += 1
print(ibp) # Hierin komen alle benodigde lijnen volgens het rooster in te staan
print(len(ibp))
# Alle lijnen van de busplanning staan in het rooster, wat betekent dat alle lijnen nodig zijn
print(bus_plan_org[bus_plan_org['start time'] == '06:04:00'])
