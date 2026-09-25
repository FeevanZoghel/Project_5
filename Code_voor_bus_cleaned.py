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
t_start = time.perf_counter()

# Data importing
bp = pd.read_excel('Bus_Planning.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Feasibility checks

# checks minimum battery value per bus (min 10%)
def check_battery_feasibility(bp, start_battery=300):
    """Check if any bus falls below the minimum required battery capacity threshold."""
    min_battery_value = (300 / 85 * 100) * 0.1  # 10% of real capacity
    planning_sor = bp.sort_values(['bus', 'start time'])
    
    empty_bus = []
    total_usage = []

    for bus, bus_data in planning_sor.groupby('bus'):
        battery = start_battery

        for battery_lose in bus_data['energy consumption']:
            battery -= battery_lose

            if battery < min_battery_value and bus not in empty_bus:
                empty_bus.append(bus)
        total_usage.append((bus, battery))

    if empty_bus:
        print("\nFEASIBILITY ERROR")
        for emptybus in empty_bus:
            print(f'There is not enough energy for bus {emptybus}')
    else:
        print("\nFEASIBILITY CHECK PASSED")

    for bus, battery in total_usage:
        print(f'Bus number {bus} has a battery content of {battery:.2f} kWh, when finishes his routes')

    return empty_bus, total_usage

# checks whether no bus starts a trip before finishing the previous
def check_bus_overlap(bp):
    """Verify that no bus is scheduled for overlapping trips."""
    planning_sor1 = bp.sort_values(['bus', 'start time']).reset_index(drop=True)
    bus_overlap = []

    for bus, bus_data in planning_sor1.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data)):
            if i == len(bus_data) - 1:
                break
            if bus_data['end time'][i] > bus_data['start time'][i + 1] and bus not in bus_overlap:
                bus_overlap.append(bus)

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

    for bus, bus_data in planning_sor1.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data)):
            if i == len(bus_data) - 1:
                break
            if bus_data['end location'][i] != bus_data['start location'][i + 1]:
                discontinuities.append((bus, i, bus_data['end location'][i], bus_data['start location'][i + 1]))

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

    valid_charging_trips = bp[(bp['activity'] == 'idle') & (bp['idle_duration_min'] >= 15)]
    not_valid_charging_trips = bp[(bp['activity'] == 'idle') & (bp['idle_duration_min'] < 15)]
    valid_charging_time = valid_charging_trips['idle_duration_min'].sum()

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
    min_battery_value = (300 / 85 * 100) * 0.1

    quick_recharge_speed = 450 / 60
    slow_recharge_speed = 60 / 60

    empty_bus = []
    total_usage = []

    for bus, bus_data in planning_sor.groupby('bus'):
        battery = start_battery

        for idx, row in bus_data.iterrows():
            if row['activity'] == 'idle' and row['idle_duration_min'] >= 15:
                time_avail = row['idle_duration_min']

                if battery < 270:
                    needed_energy = 270 - battery
                    time_needed = needed_energy / quick_recharge_speed
                    if time_avail <= time_needed:
                        battery += time_avail * quick_recharge_speed
                        time_avail = 0
                    else:
                        battery = 270
                        time_avail -= time_needed

                if time_avail > 0 and battery < 300:
                    battery += min(time_avail * slow_recharge_speed, 300 - battery)

            else:
                if row['activity'] != 'idle':
                    battery -= row['energy consumption']

            if battery < min_battery_value and bus not in empty_bus:
                empty_bus.append(bus)

        total_usage.append((bus, battery))

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

    return empty_bus, total_usage

# checks whether the required trips are all included in the schedule
def check_required_trips(bp, tt):
    """Check if all required timetable trips are included in the schedule."""
    number_of_required_trips = len(tt)
    service_trips_in_planning = bp[bp['activity'] == 'service trip']
    num_planned_trips = len(service_trips_in_planning)

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
    """Calculate individual and fleet-wide total energy consumption in kWh."""
    planning_sor = bp.sort_values(['bus', 'start time'])
    total_consumption = 0

    for bus, bus_data in planning_sor.groupby('bus'):
        total_consumption_bus = 0
        for energy in bus_data['energy consumption']:
            if energy > 0:
                total_consumption_bus += energy
        total_consumption += total_consumption_bus
        print(f'Bus {bus} used {total_consumption_bus:.2f} kWh')

    print(f'All busses uses a total of {total_consumption:.2f} kWh')
    return total_consumption

# defines all distances from service trips and material trips, calculates the number of busses used, calculates total driven distance of all busses and calculates the number of trips
def calculate_distances_and_kpis(bp, dm, tt):
    """Calculate total service/deadhead distances, trip counts, and active buses."""
    line_400 = dm[dm['line'] == 400]
    line_401 = dm[dm['line'] == 401]
    d_ar_to_st400 = line_400['distance_m'].iloc[0]
    d_st_to_ar400 = line_400['distance_m'].iloc[1]
    d_ar_to_st401 = line_401['distance_m'].iloc[0]
    d_st_to_ar401 = line_401['distance_m'].iloc[1]

    print(f'Distance for airport to station (line 400):{d_ar_to_st400:.2f}')
    print(f'Distance from station to airport (line 400):{d_st_to_ar400:.2f}')
    print(f'Distance from airport to station (line 401): {d_ar_to_st401:.2f}')
    print(f'Distance from station to aiport (line 401): {d_st_to_ar401:.2f}')

    t_ar_to_st400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
    t_st_to_ar400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])
    t_ar_to_st401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
    t_st_to_ar401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

    d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
    d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)

    d_service_total_m = d_400 + d_401
    d_service_total_km = d_service_total_m / 1000

    print(f'Total service trip distance of lines 400 and 401 (meters): {d_service_total_m:.2f}')
    print(f'Total service trip distance of lines 400 and 401 (kilometers): {d_service_total_km:.2f}')

    t_bst_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvgar')])
    t_gar_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvbst')])
    t_apt_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvgar')])
    t_gar_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvapt')])
    t_apt_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvbst')])
    t_bst_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvapt')])

    d_bst_to_gar = dm[(dm['start'] == 'ehvbst') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]
    d_gar_to_bst = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvbst')]['distance_m'].iloc[0]
    d_apt_to_gar = dm[(dm['start'] == 'ehvapt') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]
    d_gar_to_apt = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvapt')]['distance_m'].iloc[0]

    d_material_total = (t_bst_to_gar * d_bst_to_gar) + (t_gar_to_bst * d_gar_to_bst) + (t_apt_to_gar * d_apt_to_gar) + (t_gar_to_apt * d_gar_to_apt)

    total_distance_m = d_service_total_m + d_material_total
    total_distance_km = total_distance_m / 1000

    print(f'Total distance of service trips and material trips (meters): {total_distance_m:.2f}')
    print(f'Total distance of service trips and material trips (kilometers): {total_distance_km:.2f}')
    print(f'Total distance of material trips:{d_material_total:.2f}')

    deployed_buses_count = bp['bus'].nunique()
    print(f'The number of busses used:{deployed_buses_count}.')
    print(f'Total distance (kilometers): {total_distance_km:.2f}.')
    print(f'Total distance (meters):{total_distance_m:.2f}.')

    t_material_total = t_bst_to_gar + t_gar_to_bst + t_apt_to_gar + t_gar_to_apt + t_apt_to_bst + t_bst_to_apt
    print(f'Total of material trips: {t_material_total}')

    return total_distance_m, total_distance_km, deployed_buses_count

# calculate total waiting time and the average waiting time per bus
def calculate_waiting_time_kpis(bp, deployed_buses_count):
    """Calculate total fleet idle time and average waiting time per deployed bus."""
    bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
    bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))

    idle = bp[bp['activity'] == 'idle']
    tot_waiting_time_min = (idle['end_dt'] - idle['start_dt']).dt.total_seconds().sum() / 60
    tot_waiting_time_hours = tot_waiting_time_min / 60
    avg_waiting_time_per_bus = tot_waiting_time_min / deployed_buses_count

    print(f'Total waiting time in minutes: {tot_waiting_time_min:.2f}')
    print(f'Total waiting time in hours: {tot_waiting_time_hours:.2f}')
    print(f'Average waiting time per bus (minutes): {avg_waiting_time_per_bus:.2f}')

    return tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus


# Functions for all feasibility checks and kpi calculations
def run_all_feasibility_checks(bp, tt):
    """Run all feasibility checks and return a summary dictionary."""
    results = {
        "location_continuity": check_location_continuity(bp),
        "bus_overlap": check_bus_overlap(bp),
        "required_trips": check_required_trips(bp, tt),
        "charging_duration": check_valid_charging_duration(bp),
        "battery_feasibility": check_charging_constraint_and_speeds(bp)[0]
    }
    
    # Correct evaluation of all pass conditions
    all_passed = (
        len(results["location_continuity"]) == 0 and
        len(results["bus_overlap"]) == 0 and
        results["required_trips"] is True and
        results["charging_duration"] == 0 and
        len(results["battery_feasibility"]) == 0
    )
    
    print("\nOVERALL FEASIBILITY RESULT:", "PASSED" if all_passed else "FAILED")
    return results


def run_all_kpi_calculations(bp, dm, tt):
    """Run all KPI calculations and return a summary dictionary."""
    total_energy = calculate_energy_consumption_kpis(bp)
    total_dist_m, total_dist_km, deployed_buses = calculate_distances_and_kpis(bp, dm, tt)
    wait_min, wait_hours, avg_wait_per_bus = calculate_waiting_time_kpis(bp, deployed_buses)
    
    kpis = {
        "total_energy_kwh": total_energy,
        "total_distance_m": total_dist_m,
        "total_distance_km": total_dist_km,
        "deployed_buses_count": deployed_buses,
        "total_waiting_time_min": wait_min,
        "total_waiting_time_hours": wait_hours,
        "avg_waiting_time_per_bus_min": avg_wait_per_bus
    }
    
    print("\nKPI CALCULATIONS COMPLETED")
    return kpis

# Exporting the results to excel file
def export_results_to_excel(feasibility_results, kpi_results, filename='Bus_Planning_Results.xlsx'):
    """Export feasibility checks summary and KPIs to Excel."""
    loc_errors = len(feasibility_results["location_continuity"])
    overlap_errors = len(feasibility_results["bus_overlap"])
    missing_trips = 0 if feasibility_results["required_trips"] else 1
    invalid_charges = feasibility_results["charging_duration"]
    battery_errors = len(feasibility_results["battery_feasibility"])

    feasibility_summary = [
        {"Check": "Location Continuity", "Errors": loc_errors, "Status": "Passed" if loc_errors == 0 else "Failed"},
        {"Check": "Bus Overlap", "Errors": overlap_errors, "Status": "Passed" if overlap_errors == 0 else "Failed"},
        {"Check": "Required Trips", "Errors": missing_trips, "Status": "Passed" if missing_trips == 0 else "Failed"},
        {"Check": "Charging Duration (>=15 min)", "Errors": invalid_charges, "Status": "Passed" if invalid_charges == 0 else "Failed"},
        {"Check": "Battery Capacity (>=10%)", "Errors": battery_errors, "Status": "Passed" if battery_errors == 0 else "Failed"}
    ]

    with pd.ExcelWriter(filename) as writer:
        pd.DataFrame(feasibility_summary).to_excel(writer, sheet_name='Feasibility', index=False)
        pd.DataFrame(list(kpi_results.items()), columns=['KPI', 'Value']).to_excel(writer, sheet_name='KPIs', index=False)
    
    print(f"Results saved to {filename}")

# Using above functions in practice 
feasibility_results = run_all_feasibility_checks(bp, tt)
kpi_results = run_all_kpi_calculations(bp, dm, tt)
export_results_to_excel(feasibility_results, kpi_results)

# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')