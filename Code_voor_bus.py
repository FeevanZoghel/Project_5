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


# Totale afstand van de bussen

# verplichte dienstregeling
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
d_ar_to_st400 = line_400['distance_m'].iloc[0]
d_st_to_ar400 = line_400['distance_m'].iloc[1]

d_ar_to_st401 = line_401['distance_m'].iloc[0]
d_st_to_ar401 = line_401['distance_m'].iloc[1]

print(d_ar_to_st400,d_st_to_ar400,d_ar_to_st401,d_st_to_ar401)

# Verplichte dienstregeling
# Lijn 400
t_ar_to_st400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# Lijn 401
t_ar_to_st401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# totale afstand per lijn en totaal
d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)
d_total_km = d_400+d_401
d_total_m = d_total_km/1000

print(d_total_km,d_total_m)


# Bus 85% vol is 300 kwh


















































