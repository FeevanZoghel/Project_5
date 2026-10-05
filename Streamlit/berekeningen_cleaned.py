# Code_for_bus_cleaned

# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import time

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Data importing
bp = pd.read_excel('Bus_Plan_Cleaned.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Feasibility checks

# checks minimum battery value per bus (min 10%)
def check_battery_feasibility(bp, start_battery=300):
    """Check if any bus falls below the minimum required battery capacity threshold."""
    assumed_soh_percentage = 85
    min_battery_value = (300 / assumed_soh_percentage * 100) * 0.1  # 10% of real capacity
    planning_sor = bp.sort_values(['bus', 'start time'])
    
    empty_bus = []
    total_usage = []
    # Sort by busses
    for bus, bus_data in planning_sor.groupby('bus'):
        battery = start_battery
        
        for battery_lose in bus_data['energy consumption']:
            battery -= battery_lose
            # Add a bus to empty_bus if battery < 10% of SOH-value and it hasn't already been placed there
            if battery < min_battery_value and bus not in empty_bus:
                empty_bus.append(bus)
        total_usage.append((bus, battery))
    # Feasibility-outcome
    if empty_bus:
        print("\nFEASIBILITY ERROR")
        for emptybus in empty_bus:
            print(f'There is not enough energy for bus {emptybus}')
    else:
        print("\nFEASIBILITY CHECK PASSED")

    for bus, battery in total_usage:
        print(f'Bus number {bus} has a battery content of {battery:.2f} kWh, when finishes his routes')

    return empty_bus, total_usage, assumed_soh_percentage

# checks whether no bus starts a trip before finishing the previous
def check_bus_overlap(bp):
    """Verify that no bus is scheduled for overlapping trips."""
    planning_sor1 = bp.sort_values(['bus', 'start time']).reset_index(drop=True)
    bus_overlap = []
    # check consecutive bus trips
    for bus, bus_data in planning_sor1.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data)):
            if i == len(bus_data) - 1:
                break
            # overlap occurs if current trip end time > next trip start time
            if bus_data['end time'][i] > bus_data['start time'][i + 1] and bus not in bus_overlap:
                bus_overlap.append(bus)
    # Feasibility-outcome
    if bus_overlap:
        print("\nFEASIBILITY ERROR")
        for busoverlap in bus_overlap:
            print(f'Overlap found at bus {busoverlap}')
    else:
        print("\nFEASIBILITY CHECK PASSED")

    return bus_overlap

# checks whether trip arrival matches next trip departure
def check_location_continuity(bp):
    """Verify that trip arrival locations match the next trip departure locations."""
    planning_sor1 = bp.sort_values(['bus', 'start time']).reset_index(drop=True)
    discontinuities = []
    # Check for every bus
    for bus, bus_data in planning_sor1.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data)):
            if i == len(bus_data) - 1:
                break
            # If end location of trip i is not equal to start location of trip i+1 -> discontinuity
            if bus_data['end location'][i] != bus_data['start location'][i + 1]:
                discontinuities.append((bus, i, bus_data['end location'][i], bus_data['start location'][i + 1]))
    # Feasibility-outcome
    if discontinuities:
        print("\nFEASIBILITY ERROR")
        for bus, i, end_loc, start_loc in discontinuities:
            print(f'For bus number {bus} begin and end are not the same, trip {i} ends at {end_loc} and trip {i + 1} begins at {start_loc}')
    else:
        print("\nFEASIBILITY CHECK PASSED")

    return discontinuities

# calculates charging session count and duration (>=15 min)
def check_valid_charging_duration(bp):
    """Check and summarize charging sessions that meet the 15-minute threshold."""
    bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
    bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))
    bp['idle_duration_min'] = (bp['end_dt'] - bp['start_dt']).dt.total_seconds() / 60

    # categorize idle trips/periods into valid charging sessions and not valid charging sessions 
    valid_charging_trips = bp[(bp['activity'] == 'idle') & (bp['idle_duration_min'] >= 15)]
    not_valid_charging_trips = bp[(bp['activity'] == 'idle') & (bp['idle_duration_min'] < 15)]
    valid_charging_time = valid_charging_trips['idle_duration_min'].sum()
    # feasibility-outcome
    if len(not_valid_charging_trips) > 0:
        print("\nFEASIBILITY ERROR")
    else:
        print("\nFEASIBILITY CHECK PASSED")

    print(f'Number of charges with duration of 15 minutes or longer: {len(valid_charging_trips)}')
    print(f'Number of charges with duration under 15 minutes: {len(not_valid_charging_trips)}')
    print(f'Total valid charging time: {valid_charging_time:.0f} minutes')

    return len(not_valid_charging_trips)

# calculate the energy usage of busses (takes the quick recharge speed and slow recharge speed into account)
def check_charging_constraint_and_speeds(bp, start_battery=300):
    """Simulate battery levels throughout the day considering quick and slow charging speeds."""
    bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
    bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))
    bp['idle_duration_min'] = (bp['end_dt'] - bp['start_dt']).dt.total_seconds() / 60

    planning_sor = bp.sort_values(['bus', 'start time'])
    assumed_soh_percentage = 85
    min_battery_value = (300 / assumed_soh_percentage * 100) * 0.1 # same formula used
    # 2 Charging rates in kWh: quick one and slow one
    quick_recharge_speed = 450 / 60
    slow_recharge_speed = 60 / 60
    charging_speeds = [quick_recharge_speed, slow_recharge_speed]
    number_charging_speeds = len(charging_speeds)

    # Feasibility check for number of charging speeds
    if number_charging_speeds != 2:
        print("\nFEASIBILITY ERROR")
        print(f"Expected 2 charging speeds (quick & slow), but found {number_charging_speeds}.")
    empty_bus = []
    total_usage = []
    # for every bus
    for bus, bus_data in planning_sor.groupby('bus'):
        battery = start_battery
        
        for idx, row in bus_data.iterrows():
            if row['activity'] == 'idle' and row['idle_duration_min'] >= 15:
                time_avail = row['idle_duration_min']
                # use quick_recharge_speed if energy of a bus < 270 kWh
                if battery < 270:
                    needed_energy = 270 - battery
                    time_needed = needed_energy / quick_recharge_speed
                    if time_avail <= time_needed:
                        battery += time_avail * quick_recharge_speed
                        time_avail = 0
                    else:
                        battery = 270
                        time_avail -= time_needed
                # use slow_recharge_speed if 270 kWh < energy of a bus < 300 kWh
                if time_avail > 0 and battery < 300:
                    battery += min(time_avail * slow_recharge_speed, 300 - battery)

            else:
                if row['activity'] != 'idle':
                    battery -= row['energy consumption']

            if battery < min_battery_value and bus not in empty_bus:
                empty_bus.append(bus)

        total_usage.append((bus, battery))

    # Feasibility outcome
    if empty_bus:
        print("\nFEASIBILITY ERROR")
        print(f'Number of busses that came below 10% battery capacity: {len(empty_bus)}')
        print(f'Busses that were below 10% battery capacity: {empty_bus}')
    else:
        print("\nFEASIBILITY CHECK PASSED")
        print('All busses were above at least 10% battery capacity.')

    for bus_id, final_batt in total_usage:
        print(f'Bus {bus_id} has final battery level: {final_batt:.2f} kWh')
        if (final_batt > 300) or (final_batt < 0):
            print(f'Bus {bus_id} has a final battery level that is not possible (above 300 kWh or under 0 kWh). \nThe battery level is: {final_batt:.2f} kWh')

    return empty_bus, total_usage, number_charging_speeds, assumed_soh_percentage, quick_recharge_speed, slow_recharge_speed

# checks whether the required trips are all included in the schedule
def check_required_trips(bp, tt):
    """Check if all required timetable trips are included in the schedule."""
    # compare number of service trips in planning with number of required service trips in planning
    number_of_required_trips = len(tt)
    service_trips_in_planning = bp[bp['activity'] == 'service trip']
    num_planned_trips = len(service_trips_in_planning)
    # feasibility-outcome
    if number_of_required_trips == num_planned_trips:
        print("\nFEASIBILITY CHECK PASSED")
        print('All required trips are included in the schedule.')
    else:
        print("\nFEASIBILITY ERROR")
        numb_missing_trips = number_of_required_trips - num_planned_trips
        print(f'There are {numb_missing_trips} trips missing in the schedule.')

    return number_of_required_trips == num_planned_trips


# Calculating KPI values

# calculates energy consumption per bus and total energy consumption of all busses
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

# defines all distances from service trips and material trips, calculates the number of busses used, calculates total driven distance of all busses and calculates the number of trips
def calculate_distances_and_kpis(bp, dm, tt):
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

    d_material_total_km = d_material_total / 1000 

    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total, d_material_total, d_material_total_km


# calculate total waiting time and the average waiting time per bus
def calculate_waiting_time_kpis(bp, deployed_buses_count):
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

# Functions for all feasibility checks and kpi calculations
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
    print("\nOVERALL FEASIBILITY RESULT:", "PASSED" if all_passed else "FAILED")
    return results

def run_all_kpi_calculations(bp, dm, tt):
    """Run all KPI calculations and return a summary dictionary."""
    total_energy = calculate_energy_consumption_kpis(bp)
    total_dist_m, total_dist_km, deployed_buses, tot_material_trips, d_material_total, d_material_total_km = calculate_distances_and_kpis(bp, dm, tt)
    wait_min, wait_hours, avg_wait_per_bus = calculate_waiting_time_kpis(bp, deployed_buses)
    
    # All functions used for kpi's
    kpis = {
        "total_energy_kwh": total_energy,
        "total_distance_m": total_dist_m,
        "total_distance_km": total_dist_km,
        "deployed_buses_count": deployed_buses,
        "total_material_trips": tot_material_trips,
        "total_waiting_time_min": wait_min,
        "total_waiting_time_hours": wait_hours,
        "avg_waiting_time_per_bus_min": avg_wait_per_bus
    }
    print("\nKPI CALCULATIONS COMPLETED")
    return kpis

def calculate_charging_time_kpis(bp):
    '''
    Berekent de totale laadtijd van alle bussen.

    Selecteert automatisch alle activiteiten met 'charging'
    en berekent het verschil tussen start time en end time.

    return:
        total_charging_time_min
        total_charging_time_hours
    '''

    start_time = pd.to_timedelta(bp['start time'].astype(str))
    end_time = pd.to_timedelta(bp['end time'].astype(str))

    charging = bp[bp['activity'] == 'charging']

    charging_time = end_time[charging.index] - start_time[charging.index]

    total_charging_time_min = charging_time.dt.total_seconds().sum() / 60
    total_charging_time_hours = total_charging_time_min / 60

    return total_charging_time_min, total_charging_time_hours

# Exporting the results to excel file
def export_results_to_excel(feasibility_results, kpi_results, filename='Feasibility_and_KPI_results_busplan.xlsx'):
    """Export feasibility checks summary and KPIs to Excel."""
    loc_errors = len(feasibility_results["location_continuity"])
    overlap_errors = len(feasibility_results["bus_overlap"])
    missing_trips = 0 if feasibility_results["required_trips"] else 1
    invalid_charges = feasibility_results["charging_duration"]
    battery_errors = len(feasibility_results["battery_feasibility"])
    num_speeds = feasibility_results["number_charging_speeds"]
    speed_errors = 0 if num_speeds == 2 else 1
    
    soh_val = feasibility_results["assumed_soh_percentage"]
    soh_errors = 0 if (85 <= soh_val <= 95) else 1

    quick_speed = feasibility_results["quick_recharge_speed"]
    slow_speed = feasibility_results["slow_recharge_speed"]

    # Check overall pass status
    total_errors = loc_errors + overlap_errors + missing_trips + invalid_charges + battery_errors + soh_errors + speed_errors
    overall_status = "PASSED" if total_errors == 0 else "FAILED"

    # Get a feasibility summary
    feasibility_summary = [
        {"Check": "Location of end of trip and new trip match", "Errors": loc_errors, "Status": "Passed" if loc_errors == 0 else "Failed"},
        {"Check": "No Bus Overlap", "Errors": overlap_errors, "Status": "Passed" if overlap_errors == 0 else "Failed"},
        {"Check": "Required Trips of lines 400 and 401 included in bus plan", "Errors": missing_trips, "Status": "Passed" if missing_trips == 0 else "Failed"},
        {"Check": "Charging Duration is at least 15 min", "Errors": invalid_charges, "Status": "Passed" if invalid_charges == 0 else "Failed"},
        {"Check": "Number of Charging Speeds is equal to 2", "Errors": speed_errors, "Status": "Passed" if speed_errors == 0 else "Failed"},
        {"Check": f"Charging speeds configured (Quick (0-90% battery capacity): {quick_speed:.2f} kWh/min, Slow (90-100% battery capacity): {slow_speed:.2f} kWh/min)", "Errors": 0, "Status": "Passed"},
        {"Check": "Assumed SOH percentage between 85% and 95%", "Errors": soh_errors, "Status": "Passed" if soh_errors == 0 else "Failed"},
        {"Check": "Battery Capacity at least 10%", "Errors": battery_errors, "Status": "Passed" if battery_errors == 0 else "Failed"},
        {"Check": "Overall status bus plan", "Errors": total_errors, "Status": overall_status}
    ]
        
    # export into an Excel file
    with pd.ExcelWriter(filename) as writer:
        pd.DataFrame(feasibility_summary).to_excel(writer, sheet_name='Feasibility_checks', index=False)
        pd.DataFrame(list(kpi_results.items()), columns=['KPI', 'KPI-value']).to_excel(writer, sheet_name='KPI_values', index=False)  
    print(f"Results saved a file named {filename}, which is on the same folder as this .py-file.")

# Using above functions in practice 
feasibility_results = run_all_feasibility_checks(bp, tt)
kpi_results = run_all_kpi_calculations(bp, dm, tt)
export_results_to_excel(feasibility_results, kpi_results)

# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')

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

    planning.loc[planning['start_hour'] < 5, 'start_hour'] += 24
    planning.loc[planning['end_hour'] <= 5, 'end_hour'] += 24

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

    for i in range(0, len(bussen), 20):
        groepen.append(bussen[i:i + 20])

    # Maak voor iedere groep een aparte grafiek
    for groep in groepen:

        fig, ax = plt.subplots(figsize=(18, 8))

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
                label = label
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


        # Tijd-as
        uren = range(5, 30)

        ax.set_xlim(5, 29)

        ax.set_xticks(uren)
        ax.set_xticklabels([f'{uur % 24:02d}:00' for uur in uren])

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
            f'Improved bus plan'
        )

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.08),
            ncol=4
        )

        plt.tight_layout()

        st.pyplot(fig)