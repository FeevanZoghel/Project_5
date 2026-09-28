# Code_improved_bus_plan

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

# Calculating computation time of this code
t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')