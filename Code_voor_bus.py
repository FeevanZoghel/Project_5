print('Hello World')
#Matthijs

import pandas as pd 

df = pd.read_excel('Bus_Planning.xlsx')
print(df.head())

dm = pd.read_excel('DistanceMatrix.xlsx')
print(dm.head())

total_distance = 0 

start_dis       = dm['start']
end_dis         = dm['end']
min_travel_time = dm['min_travel_time']
max_travel_time = dm['max_travel_time']
distance_m      = dm['distance_m']
distance_km     = distance_m/1000

































































































# Bas























