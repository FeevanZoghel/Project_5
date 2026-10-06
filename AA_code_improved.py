# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import time

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Data importing
bp = pd.read_excel('Bus_Plan_Cleaned.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','total travel time','bus'])

# Sort timetable, starting the day at 05:07 (dit stukje is met chat gemaakt)
tt['sort_time'] = pd.to_datetime(tt['departure_time'], format='%H:%M')
tt.loc[tt['sort_time'].dt.time < pd.Timestamp('05:07').time(), 'sort_time'] += pd.Timedelta(days=1)
tt = tt.sort_values(by='sort_time').reset_index(drop=True)


# lege set met bussen aanmaken
bussen = []



trip = tt.iloc[0,:]

dm_trip = dm[(dm['start'] == trip['start']) &(dm['end'] == trip['end']) &(dm['line'] == trip['line'])]
energy_consumption = bp[(bp['start location'] == trip['start']) & (bp['end location'] == trip['end']) & (bp['line'] == trip['line']) &(bp['activity'] == 'service trip')]['energy consumption'].mode().iloc[0]

battery = {}


if len(bussen) == 0:
    bussen.append('bus1')
    battery['bus1'] = 300
    start_time = pd.to_datetime(trip['departure_time'], format='%H:%M')
    travel_time = dm_trip['max_travel_time'].iloc[0]
    end_time = start_time + pd.Timedelta(minutes=travel_time)

    ibp.loc[0, 'start location'] = trip['start']
    ibp.loc[0, 'end location'] = trip['end']
    ibp.loc[0, 'start time'] = start_time
    ibp.loc[0, 'end time'] = end_time
    ibp.loc[0, 'line'] = trip['line']
    ibp.loc[0, 'bus'] = bussen[0]
    ibp.loc[0, 'activity'] = 'service trip'
    ibp.loc[0, 'energy consumption'] = energy_consumption
    ibp.loc[0, 'total travel time']  = travel_time
    battery['bus1'] = 300-ibp.loc[0, 'energy consumption']
    


trip2 = tt.iloc[1, :]

start_time_trip2 = pd.to_datetime(trip2['departure_time'], format='%H:%M')
energy_trip2 = bp[(bp['start location'] == trip2['start']) & (bp['end location'] == trip2['end']) & (bp['line'] == trip2['line']) & (bp['activity'] == 'service trip')]['energy consumption'].mode().iloc[0]

benodigde_energy = energy_trip2


beschikbare_bussen = []
for bus in bussen:
    bus_planning = ibp[ibp['bus'] == bus]
    last_activity = bus_planning.iloc[-1, :]

    if (last_activity['end time'] <= start_time_trip2 and 
        last_activity['end location']== trip2['start'] 
        and battery[bus]>= energy_trip2):
        beschikbare_bussen.append(bus)






# kiest de bus met de hoogste traveltijd

gekozen_bus = None
hoogste_travel_tijd = -1

for bus in beschikbare_bussen:
    bus_planning = ibp[ibp['bus'] == bus]
    last_activity = bus_planning.iloc[-1, :]

    total_travel_time = last_activity['total travel time']

    if total_travel_time> hoogste_travel_tijd:
        hoogste_travel_tijd = total_travel_time
        gekozen_bus = bus

print(gekozen_bus)



































































































from Code_for_bus_cleaned import (run_all_feasibility_checks,run_all_kpi_calculations,export_results_to_excel)








t_end = time.perf_counter()
computation_time = t_end - t_start

print(f'Computation time: {computation_time:.2f} seconds.')