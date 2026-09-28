# Code_improved_bus_plan
# Dennis

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
bus_plan_org = pd.read_excel('Bus_Planning.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','bus'])
print(ibp)

# 1. Dataframes uitprinten
print(bus_plan_org)

# 2. Maximaal aantal buscombinaties bepalen
n = 1

# 3. Dataframe aanmaken voor alle buscombinaties
bus_comb = pd.DataFrame({})

# 4. Lijst aanmaken voor alle bustypen
num_buses = len(bus_plan_org['bus'].unique())

bussen = []
# 5. Buscombinaties bepalen in dataframe
# Beslisvariabele: 	B_b = Bus b rijdt wél (a=1)  of niet (a=0)  in rooster, voorbeeld uitkomst: (1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1)
x = 0
for i in range(n):
    bus_sequence = [] # 6. Te bepalen sequence voor bussen aanmaken
    for j in range(num_buses):
        bin_waarde = np.random.choice([0,1], p = [0.50, 0.50])
        bus_sequence.append(int(bin_waarde))
    print(bus_sequence, '\n')

    # 6. Voor iedere buscombinatie nagaan of die voldoet aan gestelde eisen
    index = 0
    for i in bus_sequence:
        getal = bus_sequence[index]*(index+1)
        bussen.append(getal)
        index += 1
    print(bussen)
    print(bus_plan_org[bus_plan_org['bus'] == 1])


# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')