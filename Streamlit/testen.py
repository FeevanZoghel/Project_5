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

def distances_and_kpis(bp,dm,tt):

    '''
    
    Maakt de berekeningen voor de KPI's generiek.

    Haalt de lijnen, startlocaties, eindlocaties en afstanden automatisch
    uit de Distance Matrix, Timetable en Bus Planning.

    Berekent:
        - totale afstand van service trips
        - totale afstand van material trips
        - totale gereden afstand
        - aantal gebruikte bussen
        - totaal aantal material trips

    Hierdoor hoeven lijnnummers en locaties niet handmatig in de code te worden gezet.

    return:
        total_distance_m
        total_distance_km
        deployed_buses_count
        t_material_total

    '''

    lines                   = dm['line'].dropna().unique()
    material_dm             = dm[dm['line'].isna()]
    material_trips          = bp[bp['activity'] == 'material trip']
    deployed_buses_count    = bp['bus'].nunique()
    
    distances               = {}
    material_distances      = {}    

    d_service_total_m       = 0
    d_material_total        = 0
    t_material_total        = 0

    total_distance_m        = 0
    total_distance_km       = 0

    for i in lines:
        line = dm[dm['line'] == i]

        for rij, trip in line.iterrows():

            start = trip['start']
            end = trip['end']
            distance = trip['distance_m']

            distances[(i,start,end)] = distance

            print(f'Distance from {start} to {end} (line {i}): {distance:.4f}')
    
    for rij, trip in tt.iterrows():

        line = trip['line']
        start = trip['start']
        end = trip['end']

        distance = distances[(line,start,end)]

        d_service_total_m += distance
        d_service_total_km = d_service_total_m / 1000

        print(f'Total service trip distance of the lines (meters): {d_service_total_m:.2f}')
        print(f'Total service trip distance of the lines (kilometers): {d_service_total_km:.2f}')

    for rij,trip in material_dm.iterrows():

        start = trip['start']
        end = trip['end']
        distance = trip['distance_m']

        material_distances[(start,end)] = distance

    for rij, trip in material_trips.iterrows():

        start = trip['start location']
        end = trip['end location']

        distance = material_distances[(start, end)]

        d_material_total += distance
        t_material_total += 1

    total_distance_m = d_service_total_m + d_material_total
    total_distance_km = total_distance_m / 1000

    print(f'Total distance of service trips and material trips (meters): {total_distance_m:.2f}')
    print(f'Total distance of service trips and material trips (kilometers): {total_distance_km:.2f}')

    print(f'Total distance of material trips: {d_material_total:.2f}')

    print(f'The number of busses used: {deployed_buses_count}.')

    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total

def waiting_time_kpis(bp, deployed_buses_count):
    """
    
    Berekent de wachttijd van alle bussen.

    Selecteert automatisch alle activiteiten met 'idle' en berekent
    het verschil tussen de starttijd en eindtijd.

    Berekent:
        - totale wachttijd in minuten
        - totale wachttijd in uren
        - gemiddelde wachttijd per gebruikte bus

    return:
        tot_waiting_time_min
        tot_waiting_time_hours
        avg_waiting_time_per_bus

    """

    start_time = pd.to_timedelta(bp['start time'].astype(str))
    end_time = pd.to_timedelta(bp['end time'].astype(str))

    idle = bp[bp['activity'] == 'idle']

    waiting_time = end_time[idle.index] - start_time[idle.index]

    tot_waiting_time_min = waiting_time.dt.total_seconds().sum() / 60
    tot_waiting_time_hours = tot_waiting_time_min / 60
    avg_waiting_time_per_bus = tot_waiting_time_min / deployed_buses_count

    print(f'Total waiting time in minutes: {tot_waiting_time_min:.2f}')
    print(f'Total waiting time in hours: {tot_waiting_time_hours:.2f}')
    print(f'Average waiting time per bus (minutes): {avg_waiting_time_per_bus:.2f}')

    return tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus

def calculate_energy_consumption_kpis(bp):
    '''

    Berekent het energieverbruik per bus en van alle bussen samen.

    Alleen positieve waarden worden meegenomen, omdat negatieve
    waarden het opladen van de batterij aangeven.

    De functie werkt generiek voor elk aantal bussen en ritten.

    return:
        total_consumption
    
    '''
    planning_sor = bp.sort_values(['bus', 'start time'])
    total_consumption = 0
    # for every bus
    for bus, bus_data in planning_sor.groupby('bus'):
        total_consumption_bus = 0
        for energy in bus_data['energy consumption']:
            if energy > 0:
                total_consumption_bus += energy
        total_consumption += total_consumption_bus
        print(f'Bus {bus} used {total_consumption_bus:.2f} kWh')

    print(f'All busses uses a total of {total_consumption:.2f} kWh')
    # return KPI-value
    return total_consumption

def gantt_chart_bus(bp):
    '''
    Maakt een Gantt-chart van de busplanning.

    Elke horizontale rij stelt een bus voor.
    Elke balk stelt een activiteit voor van start time tot end time.
    '''

    fig,ax = plt.subplots(figsize = (16,7))

    planning = bp.sort_values(['bus', 'start time'])

    start_times = pd.to_timedelta(planning['start time'].astype(str))
    end_times = pd.to_timedelta(planning['end time'].astype(str))

    for i in range(len(planning)):

        bus = planning.iloc[i]['bus']
        activity = planning.iloc[i]['activity']

        start = start_times.iloc[i].total_seconds() / 3600
        end = end_times.iloc[i].total_seconds() / 3600


        duration = end-start

        ax.barh(bus, duration, left = start, height = 0.6, edgecolor = 'black', alpha = 0.6)

    ax.grid(axis = 'x', linestyle = '--', alpha = 0.7)
    ax.set_axisbelow(True)

    ax.set_xlabel('Time')
    ax.set_ylabel('Bus')
    ax.set_title('Gantt chart bus planning')

    plt.tight_layout()
    st.pyplot(fig)

gantt_chart_bus(bp)