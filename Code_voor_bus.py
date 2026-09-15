print('Hello World')
#Matthijs

import pandas as pd 

bp = pd.read_excel('Bus_Planning.xlsx')
# print(bp.head())

dm = pd.read_excel('DistanceMatrix.xlsx')
# print(dm.head())

tt = pd.read_excel('Timetable.xlsx')
# print(tt.head())


total_distance = 0 

start_dis       = dm['start']
end_dis         = dm['end']
min_travel_time = dm['min_travel_time']
max_travel_time = dm['max_travel_time']
distance_m      = dm['distance_m']
distance_km     = distance_m/1000

start_battery = 300 # start waarde van 85%
min_waarde_battery = (300/85 *100)*.1 # 10 % van de echte waarde aanwezig zijn
planning = bp.sort_values(['bus','start time']) #sorteerd per bus, per begintijd op chronologische volgorde
print(planning)


print(min_waarde_battery)






# if battery<min_waarde_battery:
#     print('de bus is leeg')






















































































# Bas
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
line_400,line_401























































