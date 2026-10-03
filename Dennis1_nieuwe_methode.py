# Code_improved_bus_plan
import contextlib
import sys
from Code_for_bus_cleaned import check_charging_constraint_and_speeds, check_location_continuity, check_bus_overlap, check_required_trips, check_valid_charging_duration 

# Code_improved_bus_plan
# Dennis
# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
from datetime import datetime, timedelta
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

# 2. Zoekgebieden bepalen
min_aantal_bussen = 0
max_aantal_bussen = 20
min_totale_wachttijd_uren = 0
max_totale_wachttijd_uren = 8.42
min_totale_afstand_mt_km = 0
max_totale_afstand_mt_km = 3624.00

# 3. Voor iedere bus een schema berekenen

# 4. Dictionary aanmaken waarin je per reis het energieverbruik berekent
ec_trip = dict({'aptbst400': 12.3,
                'bstapt400': 12.8496,
                'aptbst401': 10.86,
                'bstapt400': 10.8036})

bus_number = 1
index1 = 0
for i in range (len(tt['start'].head(1))):
    start_loc_tt = tt['start'][index1]
    end_loc_tt = tt['end'][index1]
    dep_time_tt = tt['departure_time'][index1]
    line_tt = tt['line'][index1]
    end_time_tt = dm['max_travel_time'][index1]
    activity_tt = 'service trip'

    filter123 = dm[
    (dm['start'] == start_loc_tt) &
    (dm['end'] == end_loc_tt) & 
    (dm['line'] == line_tt)]

    energy_consumption_tt = (float(filter123['distance_m'] / 1000 * 1.2))
    dep_time_tt = str(dep_time_tt)

    driving_time_tt = float(filter123['max_travel_time'])
    driving_time_tt = str(driving_time_tt)
    driving_time_tt = (f'00:{driving_time_tt[0:2]}')
    
    dep_time_tt = datetime.strptime(dep_time_tt, "%H:%M")
    drive_time = dt.datetime.strptime(driving_time_tt, '%H:%M')
    end_time = (dep_time_tt - datetime(1900,1,1)) + (drive_time - datetime(1900,1,1))
    end_time = '0'+ str(end_time)

    print(end_time, activity_tt, energy_consumption_tt, bus_number)

    # Alles samenvoegen tot een gehele filterwijziging

    ibp.loc[index1, 'start location'] = start_loc_tt
    ibp.loc[index1, 'end location'] = end_loc_tt
    ibp.loc[index1, 'start time'] = dep_time_tt
    ibp.loc[index1, 'line'] = line_tt
    ibp.loc[index1, 'end time'] = end_time
    ibp.loc[index1, 'activity'] = 'service trip'
    ibp.loc[index1, 'energy consumption'] = energy_consumption_tt
    ibp.loc[index1, 'bus'] = bus_number

print(ibp)


