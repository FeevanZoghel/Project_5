# Code_for_bus_cleaned

# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import time

# Start calculating calculation time of this code
start_time = time.perf_counter()

# Data importing
bp = pd.read_excel('Bus_Planning.xlsx')
# print(bp.head()) outcomment this to check whether file is read in well
dm = pd.read_excel('DistanceMatrix.xlsx')
# print(dm.head()) outcomment this to check whether file is read in well
tt = pd.read_excel('Timetable.xlsx')
# print(tt.head()) outcomment this to check whether file is read in well

# Relevant variables for the code
total_distance = 0 

start_dis           = dm['start']
end_dis             = dm['end']
min_travel_time     = dm['min_travel_time']
max_travel_time     = dm['max_travel_time']
distance_m          = dm['distance_m']
distance_km         = distance_m/1000

start_plan          = bp['start location']
end_plan            = bp['end location']
start_time          = bp['start time']
end_time            = bp['end time']
activity            = bp['activity']
line                = bp['line']
energy_consumption  = bp['energy consumption']
bus_number          = bp['bus'].unique()

start_battery       = 300 # starting value of 85% (assuming minimum)
min_battery_value   = (300/85 *100)*.1 # 10 % of true capacity must be present
planning_sor        = bp.sort_values(['bus','start time']) # sorts per bus, per start time in chronological order
empty_bus           = []
total_usage         = []

# Checks per bus if it does not consume more than allowed (no negative energy or lower than 10%) & checks energy level when routes are finished
for bus, bus_data in planning_sor.groupby('bus'): 
    battery = start_battery

    for battery_lose in bus_data['energy consumption']:
        battery -=battery_lose

        if battery<min_battery_value and bus not in empty_bus:
            empty_bus.append(bus)
    total_usage.append((bus,battery))
for emptybus in empty_bus:
    print(f'There is not enough energy for bus {emptybus}')
for bus, battery in total_usage:
    print(f'Bus number {bus} has a battery content of {battery:.2f} kWh, when finishes his routes') 

# Calculates total consumption per bus, and overall total consumption of all buses combined
total_consumption       = 0
total_consumption_bus   = 0
for bus, bus_data in planning_sor.groupby('bus'): 
    for energy in bus_data['energy consumption']:
        if energy >0:
            total_consumption_bus += energy
    total_consumption+=total_consumption_bus
    print(f'Bus {bus} used {total_consumption_bus:.2f} kWh')
print(f'All busses uses a total of {total_consumption:.2f} kWh')

# Checks per bus if there are overlapping trips
planning_sor1       = bp.sort_values(['bus','start time']).reset_index(drop =True) # sorts per bus, per start time in chronological order
bus_overlap         = [] 

for bus, bus_data in planning_sor1.groupby('bus'):
    bus_data = bus_data.reset_index(drop=True)

    for i in range(len(bus_data)):
        if i==len(bus_data)-1:
                    break
        if bus_data['end time'][i]>bus_data['start time'][i+1] and bus not in bus_overlap:
            bus_overlap.append(bus)         
for busoverlap in bus_overlap:        
    print(f'Overlap found at bus {busoverlap}')

# Checks per bus if the end station is the start station of the next iteration
for bus, bus_data in planning_sor1.groupby('bus'):
    bus_data = bus_data.reset_index(drop=True)
    for i in range(len(bus_data)):
        if i==len(bus_data)-1:
                    break
        if bus_data['end location'][i]!=bus_data['start location'][i+1]:
            print(f'For bus number{bus} begin and end are not the same, trip {i} ends at {bus_data["end location"][i]} and trip {i+1} begins at {bus_data["start location"][i+1]} ')


# Total distance of the buses

# Select timetable (the required timetable)
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
d_ar_to_st400 = line_400['distance_m'].iloc[0]
d_st_to_ar400 = line_400['distance_m'].iloc[1]

d_ar_to_st401 = line_401['distance_m'].iloc[0]
d_st_to_ar401 = line_401['distance_m'].iloc[1]

print(f'Distance for airport to station (line 400):{d_ar_to_st400:.2f}')
print(f'Distance from station to airport (line 400):{d_st_to_ar400:.2f}')
print(f'Distance from airport to station (line 401): {d_ar_to_st401:.2f}')
print(f'Distance from station to aiport (line 401): {d_st_to_ar401:.2f}')

# 2 routes for line 400
t_ar_to_st400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# 2 routes for line 401
t_ar_to_st401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# Total distance per line and total of the 2 lines (for service trips)
d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)

d_service_total_m = d_400+d_401
d_service_total_km = d_service_total_m/1000

print(f'Total service trip distance of lines 400 and 401 (meters): {d_service_total_m:.2f}')
print(f'Total service trip distance of lines 400 and 401 (kilometers): {d_service_total_km:.2f}')
# Material trips still need to be added!


# Now add material trips 
# Types of material trips: Station-Garage and vice versa, Airport-Garage and vice versa
t_bst_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvgar')])
t_gar_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvbst')])

t_apt_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvgar')])
t_gar_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvapt')])

t_apt_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvbst')])
t_bst_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvapt')])

# Distances of different types of material trips
d_bst_to_gar = dm[(dm['start'] == 'ehvbst') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 1650 m
d_gar_to_bst = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvbst')]['distance_m'].iloc[0]  # 1650 m

d_apt_to_gar = dm[(dm['start'] == 'ehvapt') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 9000 m
d_gar_to_apt = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvapt')]['distance_m'].iloc[0]  # 9000 m

# Calculate total material trips distance
d_material_total = (t_bst_to_gar * d_bst_to_gar) + (t_gar_to_bst * d_gar_to_bst) + (t_apt_to_gar * d_apt_to_gar) + (t_gar_to_apt * d_gar_to_apt)

# Total distance = service trips distance + material trips distance
total_distance_m = d_service_total_m+d_material_total
total_distance_km = total_distance_m/1000

print(f'Total distance of service trips and material trips (meters): {total_distance_m:.2f}')
print(f'Total distance of service trips and material trips (kilometers): {total_distance_km:.2f}')
print(f'Total distance of material trips:{d_material_total:.2f}')

# Calculate remaining KPIs
# Calculate number of buses
deployed_buses_count = bp['bus'].nunique()
print(f'The number of busses used:{deployed_buses_count}.')

# Calculate total driving distance: just calculated
print(f'Total distance (kilometers): {total_distance_km:.2f}.')
print(f'Total distance (meters):{total_distance_m:.2f}.')

# Calculate total number of material trips
t_material_total = t_bst_to_gar + t_gar_to_bst + t_apt_to_gar + t_gar_to_apt + t_apt_to_bst + t_bst_to_apt
print(f'Total of material trips: {t_material_total}')

# Calculate waiting time using idle
# Create dataframe to determine waiting time
bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))

# Calculate waiting time in minutes and hours
idle = bp[bp['activity'] == 'idle']
tot_waiting_time_min = (idle['end_dt'] - idle['start_dt']).dt.total_seconds().sum() / 60
tot_waiting_time_hours = tot_waiting_time_min/60
avg_waiting_time_per_bus= tot_waiting_time_min/deployed_buses_count # minutes

print(f'Total waiting time in minutes: {tot_waiting_time_min:.2f}')
print(f'Total waiting time in hours: {tot_waiting_time_hours:.2f}')
print(f'Average waiting time per bus (minutes): {avg_waiting_time_per_bus:.2f}')

# Minimum charging time of 15 minutes
# First calculate charging time (charging duration)
# Then check if not_valid_charging_trips is 0. This must be 0.

bp['idle_duration_min'] = (bp['end_dt']-bp['start_dt']).dt.total_seconds()/60
valid_charging_trips = bp[(bp['activity']=='idle')&(bp['idle_duration_min']>=15)]
not_valid_charging_trips = bp[(bp['activity']=='idle')&(bp['idle_duration_min']<15)]
valid_charging_time = valid_charging_trips['idle_duration_min'].sum()

print(f'Number of charges with duration of 15 minutes or longer: {len(valid_charging_trips)}')
print(f'Number of charges with duration under 15 minutes: {len(not_valid_charging_trips)}')
print(f'Total valid charging time: {valid_charging_time:.0f} minutes')

# Charging constraint: check charging speeds
# Includes 10% battery margin and charging speeds

# Relevant variables, charging speeds, and empty lists
bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))
bp['idle_duration_min'] = (bp['end_dt'] - bp['start_dt']).dt.total_seconds() / 60

planning_sor = bp.sort_values(['bus', 'start time'])

quick_recharge_speed = 450 / 60  # charging speed up to 90% of battery capacity
slow_recharge_speed = 60 / 60    # charging speed for final 10% of battery capacity

empty_bus = []
total_usage = []

# Energy charging and consumption for buses
for bus, bus_data in planning_sor.groupby('bus'): 
    battery = start_battery

    for idx, row in bus_data.iterrows():
        # Charge if bus is charging ('idle') with minimum duration of 15 min
        if row['activity'] == 'idle' and row['idle_duration_min'] >= 15:
            time = row['idle_duration_min']
            
            # Fast charge up to 270 kWh (90% of battery capacity)
            if battery < 270: # 90%*300=270
                needed_energy = 270 - battery
                time_needed = needed_energy/ quick_recharge_speed
                if time <= time_needed:
                    battery += time * quick_recharge_speed # fast charge bus as much as possible
                    time = 0 # available idle time used
                else:
                    battery = 270
                    time -= time_needed
            
            # Slow charge above 270 kWh (up to max 300 kWh)
            if time > 0 and battery < 300:
                battery += min(time * slow_recharge_speed, 300 - battery)

        # Subtract energy consumption during driving (when bus is active)
        else:
            if row['activity'] != 'idle':
                battery -= row['energy consumption']

        # Check safety margin of 10% for the bus
        if battery < min_battery_value and bus not in empty_bus:
            empty_bus.append(bus)

    total_usage.append((bus, battery))

# Show results
# Display number of buses falling below 10% battery capacity
if empty_bus:
    print(f'Number of busses that came below 10% battery capacity: {len(empty_bus)}')
    print(f'Busses that were below 10% battery capacity: {empty_bus}')
else:
    print('All busses were above at least 10% battery capacity.')

# Display battery level of buses at end of schedule
for bus_id, final_batt in total_usage:
    print(f'Bus {bus_id} has final battery level: {final_batt:.2f} kWh')
    # check for impossible battery levels
    if (final_batt>300) or (final_batt < 0):
        print(f'Bus {bus_id} has a final battery level that is not possible (above 300 kWh or under 0 kWh). \nThe battery level is: {final_batt:.2f} kWh')
    else:
        pass

# Check if all required trips are included in code
# Ensures all required trips from provided plan are present
number_of_required_trips = len(tt)

service_trips_in_planning = bp[bp['activity'] == 'service trip']
num_planned_trips = len(service_trips_in_planning)

if number_of_required_trips == num_planned_trips:
    print('All required trips are included in the schedule.')
else:
    numb_missing_trips = number_of_required_trips - num_planned_trips
    print(f'There are {numb_missing_trips} trips missing in the schedule.')


# Calculating computation time of this code
end_time = time.perf_counter()
computation_time = end_time-start_time

print(f'Computation time: {computation_time:.2f} seconds.')