# Code_improved_bus_plan
# Bas

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

# Importing relevant data files
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','bus'])
print(ibp)

# Most important variables
weight_number_busses = 0.5
weight_idle_trips = 0.3
weight_dist_material_trips = 0.2 

# Checking sum of weights
sum_of_weights = weight_number_busses+weight_idle_trips+weight_dist_material_trips
if round(sum_of_weights,3)!=1.0:
    raise ValueError(f"De gewichten moeten samen exact 1.0 zijn! De gewichten zijn nu samen: {sum_of_weights}")

# Objective function
























































































































# Dennis

# 1. Dataframes uitprinten
print(ibo)









# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')