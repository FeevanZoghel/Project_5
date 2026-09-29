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

def calculate_distances_and_kpis(bp, dm, tt):
    """Calculate total service/deadhead distances, trip counts, and active buses."""
    # select the distance from the distance matrix, for each line

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
    # calculate total service trip distance seperatly for line 400 and for line 401
    d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
    d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)

    d_service_total_m = d_400 + d_401
    d_service_total_km = d_service_total_m / 1000

    print(f'Total service trip distance of lines 400 and 401 (meters): {d_service_total_m:.2f}')
    print(f'Total service trip distance of lines 400 and 401 (kilometers): {d_service_total_km:.2f}')

    # find the material trips and corresponding distances
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
    # calculate total material trips distance
    d_material_total = (t_bst_to_gar * d_bst_to_gar) + (t_gar_to_bst * d_gar_to_bst) + (t_apt_to_gar * d_apt_to_gar) + (t_gar_to_apt * d_gar_to_apt)
    # calculate total distance
    total_distance_m = d_service_total_m + d_material_total
    total_distance_km = total_distance_m / 1000

    print(f'Total distance of service trips and material trips (meters): {total_distance_m:.2f}')
    print(f'Total distance of service trips and material trips (kilometers): {total_distance_km:.2f}')
    print(f'Total distance of material trips:{d_material_total:.2f}')
    # number of busses used
    deployed_buses_count = bp['bus'].nunique()
    print(f'The number of busses used:{deployed_buses_count}.')
    print(f'Total distance (kilometers): {total_distance_km:.2f}.')
    print(f'Total distance (meters):{total_distance_m:.2f}.')
    
    t_material_total = t_bst_to_gar + t_gar_to_bst + t_apt_to_gar + t_gar_to_apt + t_apt_to_bst + t_bst_to_apt
    print(f'Total of material trips: {t_material_total}')
    # return KPI-values
    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total



def clean(bp,dm,tt):

    lines = dm['line'].dropna().unique()

    distances = {}

    for i in lines:
        line = dm[dm['line'] == i]

        for rij, trip in line.iterrows():

            start = trip['start']
            end = trip['end']
            distance = trip['distance_m']

            distances[(i,start,end)] = distance

            print(f'Distance from {start} to {end} (line {i}): {distance:.4f}')


    d_service_total_m = 0

    for rij, trip in tt.iterrows():

        line = trip['line']
        start = trip['start']
        end = trip['end']

        distance = distances[(line,start,end)]

        d_service_total_m += distance
        d_service_total_km = d_service_total_m / 1000

        print(f'Total service trip distance of the lines (meters): {d_service_total_m:.2f}')
        print(f'Total service trip distance of the lines (kilometers): {d_service_total_km:.2f}')


    material_distances = {}

    material_dm = dm[dm['line'].isna()]

    for rij,trip in material_dm.iterrows():

        start = trip['start']
        end = trip['end']
        distance = trip['distance_m']

        material_distances[(start,end)] = distance

    d_material_total = 0
    t_material_total = 0

    total_distance_m = 0
    total_distance_km = 0

    material_trips = bp[bp['activity'] == 'material trip']

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

    print(f'Total distance of material trips:{d_material_total:.2f}')

    deployed_buses_count = bp['bus'].nunique()
    print(f'The number of busses used:{deployed_buses_count}.')

    return total_distance_m, total_distance_km, deployed_buses_count, t_material_total

clean(bp,dm,tt)    