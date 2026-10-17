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

# Beginwaardes
assumed_battery_value = 85
max_battery = 300 * assumed_battery_value / 100
charging_limit = 0.9 * max_battery
fast_charge_per_min = 450 / 60
slow_charge_per_min = 60 / 60
min_battery_value = max_battery * 0.1




def add_activity(ibp, bus, start_location, end_location, start_time, end_time,
                 activity, line, energy, battery_value, total_travel_time):

    new_index = len(ibp)

    ibp.loc[new_index] = [start_location, end_location, start_time, end_time, activity, line, energy, battery_value, total_travel_time, bus]

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
                    add_activity(ibp, bus, 'ehvgar', 'ehvgar', charging_start[bus], start_time, 'charging', None, -charged_energy, battery[bus], last_activity['total travel time'])

                    if last_activity['end location'] == trip['start']:
                        beschikbare_bussen.append(bus)
                    del charging_start[bus]
        else:
            
            material_start = last_activity['end location']
            dm_material = dm[(dm['start'] == material_start) & (dm['end'] == 'ehvgar')]

            material_travel_time = (dm_material['min_travel_time'].iloc[0]+dm_material['max_travel_time'].iloc[0])/2
            material_energy = bp[(bp['start location'] == material_start) & (bp['end location'] == 'ehvgar') &(bp['activity'] == 'material trip')]['energy consumption'].mean()
            material_start_time = last_activity['end time']
            material_end_time = material_start_time + pd.Timedelta(minutes=material_travel_time)

            battery[bus] -= material_energy

            add_activity(ibp, bus, material_start, 'ehvgar', material_start_time, material_end_time, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)

            charging_start[bus] = material_end_time

def garage_to_trip(bus, trip, start_time, ibp, battery, dm, bp):
    if trip['start'] == 'ehvgar':
            return
    
    dm_material = dm[(dm['start']=='ehvgar') & (dm['end'] == trip['start'])]
    material_travel_time = (dm_material['min_travel_time'].iloc[0]+dm_material['max_travel_time'].iloc[0])/2
    material_start_time = start_time - pd.Timedelta(minutes = material_travel_time)
    material_end_time = material_start_time+pd.Timedelta(minutes = material_travel_time)
    material_energy = bp[(bp['start location'] == 'ehvgar') & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].mean()
    battery[bus] -= material_energy
    
    add_activity(ibp, bus, 'ehvgar', trip['start'], material_start_time, material_end_time, 'material trip', trip['line'], material_energy, battery[bus], material_travel_time)
    
def check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=False):
    if last_activity['end location'] == trip['start']:
        material_travel_time = 0
        material_energy = 0
    else: 
        dm_material = dm[(dm['start'] == last_activity['end location']) & (dm['end'] == trip['start'])]
        material_travel_time = (dm_material['min_travel_time'].iloc[0] + dm_material['max_travel_time'].iloc[0]) / 2
        material_energy = bp[(bp['start location'] == last_activity['end location']) & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].mean()
    
    aankomsttijd = last_activity['end time'] + pd.Timedelta(minutes=material_travel_time)
    if toevoegen and material_travel_time >0:
        battery[bus] -= material_energy
        add_activity(ibp, bus, last_activity['end location'], trip['start'], last_activity['end time'], aankomsttijd, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)
    
    return material_travel_time, material_energy

def calculate_idle_time(bus, start_time, ibp, battery, toevoegen = False):
    
    last_activity = ibp[ibp['bus'] == bus].iloc[-1]

    idle_start = last_activity['end time']
    idle_end = start_time

    idle_hours = max(0, (idle_end - idle_start).total_seconds() / 3600) # nooit een negatieve wachttijd
    idle_energy = idle_hours * 5  # 5 kwh energie verbruik 
    if toevoegen and idle_hours>0:
        battery[bus] -= idle_energy
        add_activity(ibp, bus, last_activity['end location'], last_activity['end location'], idle_start, idle_end, 'idle', None, idle_energy, battery[bus], last_activity['total travel time'])

    return idle_energy








for i in range(len(tt)):
    trip = tt.iloc[i,:]
    
    dm_trip = dm[(dm['start'] == trip['start']) &(dm['end'] == trip['end']) &(dm['line'] == trip['line'])]
    energy_consumption = bp[(bp['start location'] == trip['start']) & (bp['end location'] == trip['end']) & (bp['line'] == trip['line']) &(bp['activity'] == 'service trip')]['energy consumption'].mean()


    start_time = trip['sort_time']
    travel_time = (dm_trip['min_travel_time'].iloc[0]+dm_trip['max_travel_time'].iloc[0])/2
    end_time = start_time + pd.Timedelta(minutes=travel_time)
    # als er geen bussen maakt het een nieuwe bus aan
    if len(bussen) == 0:
        bussen.append('bus1')
        battery['bus1'] = max_battery
        #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden
        garage_to_trip('bus1', trip, start_time, ibp, battery, dm, bp)
        
        
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
        battery['bus1']                             -= energy_consumption
        ibp.loc[new_index, 'total battery bus']     = battery['bus1']
          
        continue

    material_energy         = bp[(bp['start location'] == trip['end']) & (bp['end location'] == 'ehvgar') & (bp['activity'] == 'material trip')]['energy consumption'].mean()

    
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

        material_travel_time, material_energy = check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp)
        idle_energy = calculate_idle_time(bus, start_time - pd.Timedelta(minutes=material_travel_time), ibp, battery)


        if (last_activity['end time'] + pd.Timedelta(minutes=material_travel_time) <= start_time):
            if battery[bus] >= benodigde_energy + material_energy + idle_energy:
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
        battery[nieuwe_bus] = max_battery

        #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden
        garage_to_trip(nieuwe_bus, trip, start_time, ibp, battery, dm, bp)

        gekozen_bus = nieuwe_bus
        nieuwe_bus_aangemaakt = True

    # kiest de bus met de hoogste traveltijd 
    else:
            gekozen_bus = max(
                beschikbare_bussen,
                key=lambda b: ibp[ibp['bus'] == b].iloc[-1]['end time']
            )
            nieuwe_bus_aangemaakt = False

            last_activity = ibp[ibp['bus'] == gekozen_bus].iloc[-1, :]
            check_material_trip(gekozen_bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=True)
            calculate_idle_time(gekozen_bus, start_time, ibp, battery, toevoegen = True)
            
            # Haal de huidige totale reistijd van de gekozen bus op
            hoogste_travel_tijd = ibp[ibp['bus'] == gekozen_bus].iloc[-1]['total travel time']

    
    battery[gekozen_bus] -= energy_consumption
    if nieuwe_bus_aangemaakt:
        total_travel_time = travel_time
    else:
        total_travel_time = hoogste_travel_tijd + travel_time

    add_activity(ibp, gekozen_bus, trip['start'], trip['end'], start_time, end_time, 'service trip', trip['line'], energy_consumption, battery[gekozen_bus], total_travel_time)



# de bussen naar de garage terug laten rijden 
for bus in bussen: 
    last_activity = ibp[ibp['bus'] == bus].iloc[-1]

    if last_activity['end location']!= 'ehvgar':
        trip_gar = {'start': 'ehvgar'} # normaal de volgende trip doorgeven, nu het alle trips gereden, dus de 'volgende' trip moet starten bij ehvgar wat de eindlocatie is
        material_travel_time, material_energy = check_material_trip(bus, last_activity, trip_gar, ibp, battery, dm, bp, toevoegen = True )




































# # dit voegt de idle time toe
# for bus in ibp['bus'].unique():
#     bus_planning = ibp[ibp['bus'] == bus].sort_values('start time').copy()
#     for i in range(len(bus_planning) - 1):
#         current = bus_planning.iloc[i]
#         next_activity = bus_planning.iloc[i + 1]
#         idle_start = current['end time']
#         idle_end = next_activity['start time']
#         if idle_end > idle_start:
#             idle_hours = (idle_end - idle_start).total_seconds() / 3600
#             idle_energy = idle_hours * 5
#             new_index = len(ibp)
#             ibp.loc[new_index] = {
#                 'start location': current['end location'],
#                 'end location': current['end location'],
#                 'start time': idle_start,
#                 'end time': idle_end,
#                 'activity': 'idle',
#                 'line': None,
#                 'energy consumption': idle_energy,
#                 'total battery bus': current['total battery bus'] - idle_energy,
#                 'total travel time': current['total travel time'],
#                 'bus': bus
#             }
# ibp = ibp.sort_values(['bus', 'start time']).reset_index(drop=True)

print(ibp)
















#Loading functions from other file
print('voor import')
from Code_for_bus_cleaned import (run_all_feasibility_checks,run_all_kpi_calculations,export_results_to_excel)
print('na import')
feasibility_results = run_all_feasibility_checks(ibp, tt)
kpi_results = run_all_kpi_calculations(ibp, dm, tt)

ibp[['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']].to_excel('AA_improved_bus_planning.xlsx', index = False)

output_filename = 'Improved_plan_Feasibility_and_KPI_results.xlsx'
output = export_results_to_excel(feasibility_results, kpi_results, filename=output_filename)
output



t_end = time.perf_counter()
computation_time = t_end - t_start

print(f'Computation time: {computation_time:.2f} seconds.')