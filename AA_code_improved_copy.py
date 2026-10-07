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
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','total battery bus' ,'total travel time','bus'])

# Sort timetable, starting the day at 05:07 (dit stukje is met chat gemaakt)
tt['sort_time'] = pd.to_datetime(tt['departure_time'], format='%H:%M')
tt.loc[tt['sort_time'].dt.time < pd.Timestamp('05:07').time(), 'sort_time'] += pd.Timedelta(days=1)
tt = tt.sort_values(by='sort_time').reset_index(drop=True)


# lege set met bussen aanmaken
bussen = []
battery = {}
charging_start = {}


def check_charging_buses(bussen_opladen, ibp, battery, charging_start, start_time,
                         benodigde_energy, charging_limit, fast_charge_per_min,
                         slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip):

    for bus in bussen_opladen:
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1, :]

        # bus staat al bij de garage
        if last_activity['end location'] == 'ehvgar':

            if bus not in charging_start:
                charging_start[bus] = last_activity['end time']

            else:
                charging_time = (start_time - charging_start[bus]).total_seconds() / 60
                battery_start = battery[bus]

                if battery_start < charging_limit:
                    tijd_tot_90 = (charging_limit - battery_start) / fast_charge_per_min

                    if charging_time <= tijd_tot_90:
                        charged_energy = charging_time * fast_charge_per_min
                    else:
                        remaining_time = charging_time - tijd_tot_90
                        charged_energy = (charging_limit - battery_start) + remaining_time * slow_charge_per_min

                else:
                    charged_energy = charging_time * slow_charge_per_min

                battery_after_charging = min(max_battery, battery_start + charged_energy)

                if (charging_time >= 15 and battery_after_charging >= benodigde_energy):
                    battery[bus] = battery_after_charging
                    # Charging activity toevoegen aan de planning
                    new_index = len(ibp)

                    ibp.loc[new_index, 'start location'] = 'ehvgar'
                    ibp.loc[new_index, 'end location'] = 'ehvgar'
                    ibp.loc[new_index, 'start time'] = charging_start[bus]
                    ibp.loc[new_index, 'end time'] = start_time
                    ibp.loc[new_index, 'activity'] = 'charging'
                    ibp.loc[new_index, 'line'] = None
                    ibp.loc[new_index, 'energy consumption'] = -charged_energy
                    ibp.loc[new_index, 'bus'] = bus
                    ibp.loc[new_index, 'total battery bus'] = battery[bus]
                    ibp.loc[new_index, 'total travel time'] = last_activity['total travel time']

                    if last_activity['end location'] == trip['start']:
                        beschikbare_bussen.append(bus)
                    del charging_start[bus]
        else:
            
            material_start = last_activity['end location']
            dm_material = dm[(dm['start'] == material_start) & (dm['end'] == 'ehvgar')]

            material_travel_time = dm_material['max_travel_time'].iloc[0]
            material_energy = bp[(bp['start location'] == material_start) & (bp['end location'] == 'ehvgar') &(bp['activity'] == 'material trip')]['energy consumption'].mode().iloc[0]
            material_start_time = last_activity['end time']
            material_end_time = material_start_time + pd.Timedelta(minutes=material_travel_time)

            new_index = len(ibp)

            ibp.loc[new_index, 'start location'] = material_start
            ibp.loc[new_index, 'end location'] = 'ehvgar'
            ibp.loc[new_index, 'start time'] = material_start_time
            ibp.loc[new_index, 'end time'] = material_end_time
            ibp.loc[new_index, 'activity'] = 'material trip'
            ibp.loc[new_index, 'line'] = None
            ibp.loc[new_index, 'energy consumption'] = material_energy
            ibp.loc[new_index, 'bus'] = bus

            battery[bus] -= material_energy
            ibp.loc[new_index, 'total battery bus'] = battery[bus]
            ibp.loc[new_index, 'total travel time'] = material_travel_time
            charging_start[bus] = material_end_time





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
        new_index = len(ibp)
        ibp.loc[new_index, 'start location']        = trip['start']
        ibp.loc[new_index, 'end location']          = trip['end']
        ibp.loc[new_index, 'start time']            = start_time
        ibp.loc[new_index, 'end time']              = end_time
        ibp.loc[new_index, 'line']                  = trip['line']
        ibp.loc[new_index, 'bus']                   = bussen[0]
        ibp.loc[new_index, 'activity']              = 'service trip'
        ibp.loc[new_index, 'energy consumption']    = energy_consumption
        ibp.loc[new_index, 'total travel time']     = travel_time
        battery['bus1']                             = 300-ibp.loc[new_index, 'energy consumption']
        ibp.loc[new_index, 'total battery bus']     = battery['bus1']
          
        continue

    # beginwaardes
    assumed_battery_value   = 85
    max_battery             = 300
    charging_limit          = 0.9*max_battery
    fast_charge_per_min     = 450 / 60   # 7.5 kWh per minuut
    slow_charge_per_min     = 60 / 60    # 1 kWh per minuut
    min_battery_value       = (300 / assumed_battery_value * 100) * 0.1
    material_energy         = bp[(bp['start location'] == trip['end']) & (bp['end location'] == 'ehvgar') & (bp['activity'] == 'material trip')]['energy consumption'].mode().iloc[0]

    
    if trip['end'] =='ehvgar':
        benodigde_energy = energy_consumption +min_battery_value
    else: 
         benodigde_energy = energy_consumption +material_energy+min_battery_value
    
    beschikbare_bussen = []
    bussen_opladen = []

    # Bussen die al aan het laden zijn opnieuw controleren
    for bus in charging_start:
        bussen_opladen.append(bus)

    # kijkt of een bus beschikbaar is
    for bus in bussen:
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1, :]


        if (last_activity['end time'] <= start_time and 
            last_activity['end location']== trip['start']):
            if battery[bus] >= benodigde_energy:
                beschikbare_bussen.append(bus)
            else:
                if bus not in bussen_opladen:
                    bussen_opladen.append(bus)

    check_charging_buses(bussen_opladen, ibp, battery, charging_start, start_time, benodigde_energy, charging_limit, fast_charge_per_min, slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip)
    
    
    
#########################hier niet aankomen#############################
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
    new_index = len(ibp)
    ibp.loc[new_index, 'start location']        = trip['start']
    ibp.loc[new_index, 'end location']          = trip['end']
    ibp.loc[new_index, 'start time']            = start_time
    ibp.loc[new_index, 'end time']              = end_time
    ibp.loc[new_index, 'line']                  = trip['line']
    ibp.loc[new_index, 'bus']                   = gekozen_bus
    ibp.loc[new_index, 'activity']              = 'service trip'
    ibp.loc[new_index, 'energy consumption']    = energy_consumption
    battery[gekozen_bus]                = battery[gekozen_bus]-energy_consumption
    ibp.loc[new_index, 'total battery bus']     = battery[gekozen_bus] 
    if nieuwe_bus_aangemaakt: 
        ibp.loc[new_index, 'total travel time'] = travel_time
    else: 
        ibp.loc[new_index, 'total travel time'] = hoogste_travel_tijd +travel_time



print(ibp)

# Define column names
excel_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

# Create a dataframe with these column names and export to Excel
df_improved_plan = ibp[excel_columns]
df_improved_plan['start time'] = pd.to_datetime(df_improved_plan['start time']).dt.strftime('%H:%M:%S')
df_improved_plan['end time'] = pd.to_datetime(df_improved_plan['end time']).dt.strftime('%H:%M:%S')
df_improved_plan.to_excel('Improved_Bus_Planning_version_B.xlsx', index=False)

print("The improved bus plan has succesfully been saved in Excel format!")













#Loading functions from other file
from Code_for_bus_cleaned import (run_all_feasibility_checks,run_all_kpi_calculations,export_results_to_excel)
feasibility_results = run_all_feasibility_checks(ibp, tt)
kpi_results = run_all_kpi_calculations(ibp, dm, tt)



output_filename = 'Improved_plan_Feasibility_and_KPI_results.xlsx'
output = export_results_to_excel(feasibility_results, kpi_results, filename=output_filename)
output


t_end = time.perf_counter()
computation_time = t_end - t_start

print(f'Computation time: {computation_time:.2f} seconds.')