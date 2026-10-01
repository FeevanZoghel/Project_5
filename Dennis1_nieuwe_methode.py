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


# 1. Dataframes uitprinten
print(bus_plan_org)

# 2. Maximaal aantal buscombinaties bepalen
n = 1

# 3. Dataframe aanmaken voor alle toegelaten buscombinaties
bus_comb = pd.DataFrame({'Bus Combination': [],
                         'Pass / Fail': [],
                         'Total Score': []})

# 4. Lijst aanmaken voor alle bustypen
num_buses = 50

def run_all_feasibility_checks(bp, tt):
    """Run all feasibility checks and return a summary dictionary."""
    # Call charging constraint function once to extract battery errors, speeds and soh
    empty_buses, total_usage, number_charging_speeds, assumed_soh_percentage, quick_speed, slow_speed = check_charging_constraint_and_speeds(bp)

    # all functions of feasibility checks
    results = {
        "location_continuity": check_location_continuity(bp),
        "bus_overlap": check_bus_overlap(bp),
        "required_trips": check_required_trips(bp, tt),
        "charging_duration": check_valid_charging_duration(bp),
        "battery_feasibility": empty_buses,
        "number_charging_speeds": number_charging_speeds,
        "assumed_soh_percentage": assumed_soh_percentage,
        "quick_recharge_speed": quick_speed,
        "slow_recharge_speed": slow_speed
    }
    
    # Correct evaluation of all pass conditions
    all_passed = (
        len(results["location_continuity"]) == 0 and
        len(results["bus_overlap"]) == 0 and
        results["required_trips"] is True and
        results["charging_duration"] == 0 and
        len(results["battery_feasibility"]) == 0 and
        results["number_charging_speeds"] == 2 and
        (85 <= results["assumed_soh_percentage"] <= 95)
    )
    
    feasiblity_result = ("PASS" if all_passed else "FAIL")
    bus_comb.loc[x, 'Bus Combination'] = bus_sequence
    bus_comb.loc[x, 'Pass / Fail'] = feasiblity_result
    print(feasiblity_result)

# 5. Buscombinaties bepalen in dataframe; met binaire getallen voor variabelen
# Beslisvariabele: 	B_b = Bus b rijdt wél (a=1)  of niet (a=0)  in rooster, voorbeeld uitkomst: (1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1)
x = 0
for i in range(n):
    bussen = []
    bus_sequence = str() # Te bepalen sequence voor bussen aanmaken
    bus_numbers_list = []
    for j in range(num_buses): # Sequentie genereren van binaire variabelen voor bussen
        bin_waarde = np.random.choice([0,1], p = [0, 1]) # Binaire waarde genereren voor busnummer i
        bus_numbers_list.append(bin_waarde)
        bus_sequence = bus_sequence + str(int(bin_waarde)) # Binaire waarde toevoegen aan 'bus_sequence'
    print(bus_sequence, '\n')

    # 6. Voor iedere buscombinatie nagaan of die voldoet aan gestelde eisen
    index1 = 0 # Index aanmaken die de index van de beslisvariabele bijhoudt
    for i in bus_sequence:
        getal = bus_numbers_list[index1]*(index1+1) # Getal bepalen
        bussen.append(int(getal)) # Getal toevoegen aan 'bussen'
        index1 += 1
    Bus_Planning_New = bus_plan_org[bus_plan_org['bus'].isin(bussen)] # Dataframe filtreren op random geselecteerde kolommen van 'bussen'
    run_all_feasibility_checks(Bus_Planning_New, tt) # Feasiblity-check uitvoeren op vernieuwde busplanning met andere buscombinatie
    x += 1

print(bus_comb)
print(bus_comb[bus_comb['Pass / Fail'] == 'PASS'])

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


