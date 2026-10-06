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
print(tt.columns)
print(tt.head())


# lege set met bussen aanmaken
bussen = []
battery = {}

for i in range(len(tt)):
    trip = tt.iloc[i,:]
    
    dm_trip = dm[(dm['start'] == trip['start']) &(dm['end'] == trip['end']) &(dm['line'] == trip['line'])]
    energy_consumption = bp[(bp['start location'] == trip['start']) & (bp['end location'] == trip['end']) & (bp['line'] == trip['line']) &(bp['activity'] == 'service trip')]['energy consumption'].mode().iloc[0]

    start_time = trip['sort_time']
    travel_time = dm_trip['max_travel_time'].iloc[0]
    end_time = start_time + pd.Timedelta(minutes=travel_time)
    # als er geen bussen maakt het een nieuwe bus aan
    if len(bussen) == 0:
        bussen.append('bus1')
        battery['bus1'] = 300
        

        ibp.loc[i, 'start location']        = trip['start']
        ibp.loc[i, 'end location']          = trip['end']
        ibp.loc[i, 'start time']            = start_time
        ibp.loc[i, 'end time']              = end_time
        ibp.loc[i, 'line']                  = trip['line']
        ibp.loc[i, 'bus']                   = bussen[0]
        ibp.loc[i, 'activity']              = 'service trip'
        ibp.loc[i, 'energy consumption']    = energy_consumption
        ibp.loc[i, 'total travel time']     = travel_time
        battery['bus1'] = 300-ibp.loc[i, 'energy consumption']
        
        continue


    beschikbare_bussen = []
    for bus in bussen:
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1, :]


        if (last_activity['end time'] <= start_time and 
            last_activity['end location']== trip['start'] 
            and battery[bus]>= energy_consumption):
            beschikbare_bussen.append(bus)


    # als er geen bus beschikbaar is dan een nieuwe bus toevoegen
    nieuwe_bus_aangemaakt = False
    if len(beschikbare_bussen)==0:
        nieuwe_bus = 'bus' + str(len(bussen) + 1)
        bussen.append(nieuwe_bus)
        battery[nieuwe_bus] = 300
        gekozen_bus = nieuwe_bus
        nieuwe_bus_aangemaakt = True

    # kiest de bus met de hoogste traveltijd
    else:
        gekozen_bus = None
        hoogste_travel_tijd = -1

        for bus in beschikbare_bussen:
            bus_planning = ibp[ibp['bus'] == bus]
            last_activity = bus_planning.iloc[-1, :]

            total_travel_time = last_activity['total travel time']

            if total_travel_time> hoogste_travel_tijd:
                hoogste_travel_tijd = total_travel_time
                gekozen_bus = bus

    ibp.loc[i, 'start location'] = trip['start']
    ibp.loc[i, 'end location'] = trip['end']
    ibp.loc[i, 'start time'] = start_time
    ibp.loc[i, 'end time'] = end_time
    ibp.loc[i, 'line'] = trip['line']
    ibp.loc[i, 'bus'] = gekozen_bus
    ibp.loc[i, 'activity'] = 'service trip'
    ibp.loc[i, 'energy consumption'] = energy_consumption
    if nieuwe_bus_aangemaakt: 
        ibp.loc[i, 'total travel time'] = travel_time
    else: 
        ibp.loc[i, 'total travel time'] = hoogste_travel_tijd +travel_time



print(ibp)










































































































t_end = time.perf_counter()
computation_time = t_end - t_start

print(f'Computation time: {computation_time:.2f} seconds.')