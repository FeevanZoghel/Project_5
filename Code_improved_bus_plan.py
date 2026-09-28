# Code_improved_bus_plan
# Bas

# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import math
import time

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Importing relevant data files
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','bus'])
print(ibp)

# Weights and weight error
w_busses = 0.5
w_idle = 0.3
w_material = 0.2 

sum_of_weights = w_busses+w_idle+w_material
if round(sum_of_weights,3)!=1.0:
    raise ValueError(f"De gewichten moeten samen exact 1.0 zijn! De gewichten zijn nu samen: {sum_of_weights}")

# Most important variables
start_location = ibp['start location']
end_location = ibp['end location']
start_time = ibp['start time']
end_time = ibp['end time']
activity = ibp['activity']
line = ibp['line']
energy_consumption = ibp['energy consumption']
bus = ibp['bus']

# Objective function (using normalized scores)
total_distance_m, total_distance_km, deployed_buses_count, t_material_total = calculate_distances_and_kpis(ibp, dm, tt)
material_connections = dm[
    ((dm['start'] == 'ehvbst') & (dm['end'] == 'ehvgar')) |
    ((dm['start'] == 'ehvgar') & (dm['end'] == 'ehvbst')) |
    ((dm['start'] == 'ehvapt') & (dm['end'] == 'ehvgar')) |
    ((dm['start'] == 'ehvgar') & (dm['end'] == 'ehvapt'))
]

min_busses, max_busses = 10, 20

if 'idle_duration_min' in ibp.columns and not ibp['idle_duration_min'].empty:
    min_idle, max_idle = ibp['idle_duration_min'].min(), ibp['idle_duration_min'].max()
    idle_trip_score = ibp['idle_duration_min'].mean()
else:
    min_idle, max_idle = 0, 100
    idle_trip_score = 0

min_material, max_material = 0,material_connections['distance_m'].max()
material_trips = ibp[ibp['activity'] == 'material trip'] if 'activity' in ibp.columns else pd.DataFrame()
if not material_trips.empty and 'distance_m' in material_trips.columns:
    material_trip_score = material_trips['distance_m'].max()
else:
    material_trip_score = 0

numb_busses = deployed_buses_count

norm_busses = (numb_busses - min_busses) / (max_busses - min_busses) if max_busses != min_busses else 0
norm_idle = (idle_trip_score - min_idle) / (max_idle - min_idle) if max_idle != min_idle else 0
norm_material = (material_trip_score - min_material) / (max_material - min_material) if max_material != min_material else 0

total_score = (w_busses * norm_busses) + (w_idle * norm_idle) + (w_material * norm_material)


# Number of trips per bus
trips_per_bus = ibp.groupby('bus').size()


# Checking whether the solution is feasible
feasibility_results = run_all_feasibility_checks(ibp, tt)

is_feasible = (
    len(feasibility_results["location_continuity"]) == 0 and
    len(feasibility_results["bus_overlap"]) == 0 and
    feasibility_results["required_trips"] is True and
    feasibility_results["charging_duration"] == 0 and
    len(feasibility_results["battery_feasibility"]) == 0 and
    feasibility_results["number_charging_speeds"] == 2 and
    (85 <= feasibility_results["assumed_soh_percentage"] <= 95)
)

if is_feasible:
    print("The busplan is feasible. You can calculate the objective value now.")
else:
    print("The busplan is not feasible. The objective value can now not be calculated.")





















































































































# Dennis

# 1. Dataframes uitprinten
print(ibo)









# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')