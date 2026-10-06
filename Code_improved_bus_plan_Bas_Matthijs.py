# Code_improved_bus_plan_Bas_Matthijs

# Importing relevant Python libraries
import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Import feasibility and KPI functions from your other file
from Code_for_bus_cleaned import (
    run_all_feasibility_checks,
    run_all_kpi_calculations,
    export_results_to_excel
)

# Start computation timer
t_start = time.perf_counter()

# Data import
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Clean column names
tt.columns = tt.columns.str.strip().str.lower()
dm.columns = dm.columns.str.strip().str.lower()


t_end = time.perf_counter()
computation_time = t_end - t_start
print(f'Computation time: {computation_time:.2f} seconds.')