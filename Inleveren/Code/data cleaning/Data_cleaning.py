import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import numpy as np
import math as m
import scipy.stats as sp
from datetime import datetime as dt

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "Input data"

bus_plan = pd.read_excel(INPUT_DIR / "Original_bus_plan.xlsx")


# Step 1: detect inaccuracies in the data, except for the columns 'start time', 'end time', and 'energy consumption'

# Step 1.1: create a new list called 'columns'
columns = ['start location', 'end location', 'activity', 'line', 'bus']

# Step 1.2: create dictionary
unique_values_dict = dict()

# Step 1.3: iterate through all data in the columns listed in 'columns' to detect inconsistencies and add them to the dataframe
for column in columns:
    unique = bus_plan[column].unique()
    unique_values_dict[column] = unique  # Step 1.4: add all unique values obtained to the dataframe
    print(f' {column} = {unique_values_dict[column]}')  # Step 1.5: print the dictionary containing unique values

# NO INCONSISTENCIES, ERRORS, OR INACCURACIES DETECTED

# Step 2: clean the 'start time', 'end time', and 'energy consumption' columns
df = pd.DataFrame({})

# Step 2: check whether any unusual times are hidden in the dataset

# Step 2.1.1: create a function that checks whether any unusual times are present in the dataset
def check_times(column):

    # Create lists for hours, minutes, seconds, and separator characters
    hours = []
    minutes = []
    seconds = []
    separators = []

    for value in column:  # Iterate through all times in the 'start_time' column
        value = str(value)  # Convert time to string

        hours.append(int(value[0:2]))  # Add hours to the 'hours' list
        minutes.append(int(value[3:5]))  # Add minutes to the 'minutes' list
        seconds.append(int(value[6:len(value)]))  # Add seconds to the 'seconds' list

        if value[2] == ':' and value[5] == ':':
            separators.append(':')  # Add separator character to the list

    for hour in hours:
        if hour < 0 or hour > 23:  # Check for invalid values and report them if found
            print(f' hour is incorrect ({hour})')

    for minute in minutes:
        if minute < 0 or minute > 60:  # Check for invalid values and report them if found
            print(f' minute is incorrect ({minute})')

    for second in seconds:
        if second < 0 or second > 60:  # Check for invalid values and report them if found
            print(f' second is incorrect ({second})')

    if len(separators) != len(bus_plan['start time']):
        print('One or more time values contain inconsistencies')

# Use the function to check for errors, inconsistencies, and irregularities in the columns
check_times(bus_plan['start time'])
check_times(bus_plan['end time'])

# NO INCONSISTENTIES FOUND

# Step 3: verify whether energy consumption corresponds to the trip type
bus_plan[bus_plan['energy consumption'] < 0]  # Check whether energy is only added during charging

# ERROR FOUND IN ROW 28 OF DATAFRAME

# In row 28, energy can never be charged during a material trip. This is corrected here.
filtered1 = bus_plan[bus_plan['activity'] == 'material trip']  # Apply filter 1: select material trips
filtered2 = bus_plan[bus_plan['start location'] == 'ehvbst']  # Apply filter 2: select start location 'ehvbst'
filtered3 = bus_plan[bus_plan['end location'] == 'ehvgar']  # Apply filter 3: select end location 'ehvgar'

filtered123 = bus_plan[
    (bus_plan['activity'] == 'material trip') &
    (bus_plan['start location'] == 'ehvbst') &
    (bus_plan['end location'] == 'ehvgar')
]  # Combine all filters into a single filter

print(filtered123)  # Display filtered results clearly

bus_plan.loc[28, 'energy consumption'] = 1.98  # Change energy consumption value from -157.5 to +1.98 based on filter 'filtered123'.

print(bus_plan.head(30))  # Verify that the modification was successful

# ERROR CORRECTED IN ROW 28, NO ERRORS FOUND

# Step 4: check for outliers in trips; determined manually that no further checks are required.

# NO OUTLIERS FOUND

# Step 5: check that no negative values occur for 'material trips', 'service trips' or 'idle trips'
filtered45 = bus_plan[
    (bus_plan['activity'] == 'charging') &
    (bus_plan['start location'] == 'ehvgar') &
    (bus_plan['end location'] == 'ehvgar')
]  # Combine all filters into a single filter

print(filtered45)

# NO NEGATIVE VALUES FOUND FOR 'MATERIAL TRIPS', 'SERVICE TRIPS' OR 'IDLE TRIPS'

# Calculations:
# Row 29: 15:16 - 14:55 = 0:21 hours.
# Row 49: 21:32 - 21:04 = 0:28 hours.
# Charging rate = 210 / 28 min = 7.5 energy units per minute. This rate applies to all rows.
# Row 29: 21 min * 7.5 = -157.5 energy units added to the SOC.

# Step 6: check that no positive values occur during 'charging'
bus_plan.loc[29, 'energy consumption'] = -157.5  # Change energy consumption value from +1.98 to -157.5 based on filter 'filtered45'.

(bus_plan.head(30))  # Verify that the modification was successful

filtered6 = bus_plan[
    (bus_plan['activity'] != 'charging') &
    (bus_plan['energy consumption'] <= 0)
]  # Combine all filters into a single filter

print(filtered6)  # No non-charging trips indicate battery charging according to the dataframe. All checks have been completed.

# NO POSITIVE VALUES FOUND DURING CHARGING

# Step 7: export dataframe to an Excel file
bus_plan.to_excel(
    INPUT_DIR / "Bus_Plan_Cleaned.xlsx",
    index=False
)

# END RESULT: NO ERRORS FOUND
print('NO ERRORS FOUND, DATA CLEANING SUCCESFULLY COMPLETED')