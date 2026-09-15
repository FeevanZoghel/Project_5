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
planning_sor        = bp.sort_values(['bus','start time']) #sorteerd per bus, per begintijd op chronologische volgorde
print(planning_sor)
empty_bus           = []
total_usage         = []

for bus, bus_data in planning_sor.groupby('bus'): # kijkt per bus of het niet meer verbruikt dan mag (geen negatieve energie of lager dan 10 %) & het kijkt hoeveel energie een bus heeft als het klaar is met zijn routes
    battery = start_battery

    for battery_lose in bus_data['energy consumption']:
        battery -=battery_lose

        if battery<min_waarde_battery and bus not in empty_bus:
            empty_bus.append(bus)
    total_usage.append((bus,battery))

for emptybus in empty_bus:
    print(f'Er is niet genoeg energy voor bus {emptybus}')
for bus, battery in total_usage:
    print(f'Bus number {bus} has a battery content of {battery:.2f} kWh, when finishes his routes') 

total_consumption = 0 
for bus, bus_data in planning_sor.groupby('bus'): #berekend het total verbruik per bus, en het algehele totale verbruik van alle bussen bij elkaar.
    total_consumption_bus = 0
    for energy in bus_data['energy consumption']:
        if energy >0:
            total_consumption_bus += energy
    total_consumption+=total_consumption_bus
    print(f'Bus {bus} used {total_consumption_bus:.2f} kWh')
print(f'All busses uses a total of {total_consumption:.2f} kWh')
    
    




























































































# Bas


# Totale afstand van de bussen

# verplichte dienstregeling selecteren
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

# totale afstand per lijn en totaal (van de service trips)
d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)

d_service_total_m = d_400+d_401
d_service_total_km = d_service_total_m/1000

print(d_service_total_km,d_service_total_m) # Material trips moeten nog toegevoegd worden!

# Nu material trips toevoegen 
# soorten material trips: Station-Garage en andersom, Airport-Garage en andersom,
t_bst_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvgar')])
t_gar_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvbst')])

t_apt_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvgar')])
t_gar_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvapt')])

# Afstanden van de verschillende soorten material trips
d_bst_to_gar = dm[(dm['start'] == 'ehvbst') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 1650 m
d_gar_to_bst = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvbst')]['distance_m'].iloc[0]  # 1650 m

d_apt_to_gar = dm[(dm['start'] == 'ehvapt') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 9000 m
d_gar_to_apt = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvapt')]['distance_m'].iloc[0]  # 9000 m

# Totale afstand materials tripps
d_material_total = (t_bst_to_gar * d_bst_to_gar) + (t_gar_to_bst * d_gar_to_bst) + (t_apt_to_gar * d_apt_to_gar) + (t_gar_to_apt * d_gar_to_apt)

# Toevoegen aan de totale afstand
total_distance_m = d_service_total_m+d_material_total
total_distance_km = total_distance_m/1000

print(total_distance_m,total_distance_km,d_material_total)


# Bus 85% vol is 300 kwh


# KPI's

# Berekening aantal bussen
aantal_ingezette_bussen = bp['bus'].nunique()

# Berekening totale rijafstand: net berekend

# Lege/material trips
t_material_total = t_bst_to_gar + t_gar_to_bst + t_apt_to_gar + t_gar_to_apt + t_apt_to_bst + t_bst_to_apt

# Berekening wachttijd

# Berekening energiegebruik (Matthijs)

# Oplaadtijd (Matthijs)










































