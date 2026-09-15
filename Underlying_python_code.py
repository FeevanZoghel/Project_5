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

start_dis           = dm['start']
end_dis             = dm['end']
min_travel_time     = dm['min_travel_time']
max_travel_time     = dm['max_travel_time']
distance_m          = dm['distance_m']
distance_km         = distance_m/1000

start_plan          = bp['start location']
end_plan            = bp['end location']
start_time          = bp['start time']
end_time            = bp['end time']
activity            = bp['activity']
line                = bp['line']
energy_consumption  = bp['energy consumption']
bus_number          = bp['bus'].unique()

start_battery       = 300 # start waarde van 85% (gaan uit van het minimum)
min_waarde_battery  = (300/85 *100)*.1 # 10 % van de echte waarde aanwezig zijn
planning_sor1        = bp.sort_values(['bus','start time']).reset_index(drop =True) #sorteerd per bus, per begintijd op chronologische volgorde
print(planning_sor1)

# bus_overlap = []
# for bus, bus_data in planning_sor1.groupby('bus'):
#     bus_data = bus_data.reset_index(drop=True)

#     for i in range(len(bus_data)):
#         if i==len(bus_data)-1:
#                     break
#         if bus_data['end time'][i]>bus_data['start time'][i+1] and bus not in bus_overlap:
#             bus_overlap.append(bus)         
# for busoverlap in bus_overlap:        
#     print(f'Overlap gevonden bij bus {busoverlap}')

for bus, bus_data in planning_sor1.groupby('bus'):
    bus_data = bus_data.reset_index(drop=True)

    for i in range(len(bus_data)):
        if i==len(bus_data)-1:
                    break
        if bus_data['end location'][i]!=bus_data['start location'][i+1]:
            print(f'for bus number{bus} , rit {i} eindigt op {bus_data['end location'][i]} en rit {i+1} begint op {bus_data['start location'][i+1]} ')









































