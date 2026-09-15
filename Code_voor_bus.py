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


# Totale afstand van de bussen
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
d_ar_to_st400 = line_400['distance_m'].iloc[0]
d_st_to_ar400 = line_400['distance_m'].iloc[1]

d_ar_to_st401 = line_401['distance_m'].iloc[0]
d_st_to_ar401 = line_401['distance_m'].iloc[1]

print(d_ar_to_st400,d_st_to_ar400,d_ar_to_st401,d_st_to_ar401)

t_ar_to_st400 = tt[]
t_st_to_ar400 = tt[]
t_ar_to_st401 = tt[]
t_st_to_ar401 = tt[]



# Bus 85% vol is 300 kwh


















































