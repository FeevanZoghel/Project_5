import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sp
import math
import time

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Data importing
# bp = pd.read_excel('Bus_Plan_Cleaned.xlsx')
# dm = pd.read_excel('DistanceMatrix.xlsx')
# tt = pd.read_excel('Timetable.xlsx')

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
    Maakt Gantt-charts van de busplanning.

    Elke horizontale rij stelt een bus voor.
    Elke balk stelt een activiteit voor van start time tot end time.

    De bussen worden verdeeld over grafieken met maximaal
    vijf bussen per grafiek.
    '''

    planning = bp.sort_values(['bus', 'start time'])

    start_times = pd.to_timedelta(planning['start time'].astype(str))
    end_times = pd.to_timedelta(planning['end time'].astype(str))

    planning = planning.copy()
    planning['start_hour'] = start_times.dt.total_seconds() / 3600
    planning['end_hour'] = end_times.dt.total_seconds() / 3600

    kleuren = {
        'service trip': 'skyblue',
        'material trip': 'orange',
        'idle': 'lightgrey',
        'charging': 'yellowgreen'
    }

    # Alle unieke bussen
    bussen = sorted(planning['bus'].unique())

    # Verdeel de bussen in groepen van maximaal 10
    groepen = []

    for i in range(0, len(bussen), 10):
        groepen.append(bussen[i:i + 10])

    # Maak voor iedere groep een aparte grafiek
    for groep in groepen:

        fig, ax = plt.subplots(figsize=(20, 10))

        planning_groep = planning[planning['bus'].isin(groep)]

        bus_posities = {}

        for i in range(len(groep)):
            bus_posities[groep[i]] = i

        activiteiten_in_legenda = []

        for i in range(len(planning_groep)):

            trip = planning_groep.iloc[i]

            bus = trip['bus']
            activity = trip['activity']

            start = trip['start_hour']
            end = trip['end_hour']

            duration = end - start

            y = bus_posities[bus]

            if activity not in activiteiten_in_legenda:
                label = activity
                activiteiten_in_legenda.append(activity)
            else:
                label = None

            ax.barh(
                y,
                duration,
                left=start,
                height=0.8,
                color=kleuren[activity],
                edgecolor='grey',
                linewidth=1,
                label=label
            )

            # Tekst in de balken
            if activity == 'service trip':

                line = trip['line']

                ax.text(
                    start + duration / 2,
                    y,
                    f'{int(line)}',
                    ha='center',
                    va='center',
                    fontsize=8
                )

            elif activity == 'charging':

                ax.text(
                    start + duration / 2,
                    y,
                    'Charging',
                    ha='center',
                    va='center',
                    fontsize=7
                )

            elif activity == 'material trip':

                ax.text(
                    start + duration / 2,
                    y,
                    'Material',
                    ha='center',
                    va='center',
                    fontsize=7
                )

        # Tijd-as
        eerste_uur = int(planning['start_hour'].min())
        laatste_uur = int(planning['end_hour'].max()) + 1

        uren = range(eerste_uur, laatste_uur + 1)

        ax.set_xticks(uren)
        ax.set_xticklabels([f'{uur:02d}:00' for uur in uren])

        # Busnummers
        ax.set_yticks(range(len(groep)))
        ax.set_yticklabels([f'Bus {bus}' for bus in groep])

        # Tijd bovenaan
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')

        ax.grid(axis='x', linestyle='-', alpha=0.4)
        ax.set_axisbelow(True)

        ax.set_xlabel('Time')
        ax.set_ylabel('Bus')

        ax.set_title(
            f'Gantt chart bus {groep[0]} - {groep[-1]}'
        )

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )

        plt.tight_layout()

        st.pyplot(fig)