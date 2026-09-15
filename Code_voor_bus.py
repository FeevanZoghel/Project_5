print('Hello World')
#Matthijs

import pandas as pd 

bp = pd.read_excel('Bus_Planning.xlsx')
print(bp.head())

dm = pd.read_excel('DistanceMatrix.xlsx')
print(dm.head())

tt = pd.read_excel('Timetable.xlsx')
print(tt.head())


total_distance = 0 

start_dis       = dm['start']
end_dis         = dm['end']
min_travel_time = dm['min_travel_time']
max_travel_time = dm['max_travel_time']
distance_m      = dm['distance_m']
distance_km     = distance_m/1000

































































































# Bas
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
line_400,line_401























































