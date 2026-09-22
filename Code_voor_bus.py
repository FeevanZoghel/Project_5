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
empty_bus           = []
total_usage         = []

# kijkt per bus of het niet meer verbruikt dan mag (geen negatieve energie of lager dan 10 %) & het kijkt hoeveel energie een bus heeft als het klaar is met zijn routes
for bus, bus_data in planning_sor.groupby('bus'): 
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


#berekend het total verbruik per bus, en het algehele totale verbruik van alle bussen bij elkaar.
total_consumption       = 0
total_consumption_bus   = 0
for bus, bus_data in planning_sor.groupby('bus'): 
    for energy in bus_data['energy consumption']:
        if energy >0:
            total_consumption_bus += energy
    total_consumption+=total_consumption_bus
    print(f'Bus {bus} used {total_consumption_bus:.2f} kWh')
print(f'All busses uses a total of {total_consumption:.2f} kWh')

# kijkt per bus of het geen overlappende trips heeft
planning_sor1       = bp.sort_values(['bus','start time']).reset_index(drop =True) #sorteerd per bus, per begintijd op chronologische volgorde
bus_overlap         = [] 

for bus, bus_data in planning_sor1.groupby('bus'):
    bus_data = bus_data.reset_index(drop=True)

    for i in range(len(bus_data)):
        if i==len(bus_data)-1:
                    break
        if bus_data['end time'][i]>bus_data['start time'][i+1] and bus not in bus_overlap:
            bus_overlap.append(bus)         
for busoverlap in bus_overlap:        
    print(f'Overlap gevonden bij bus {busoverlap}')

#kijkt per bus of het eindstation ook wel het begin station is van de volgende iteratie
for bus, bus_data in planning_sor1.groupby('bus'):
    bus_data = bus_data.reset_index(drop=True)
    for i in range(len(bus_data)):
        if i==len(bus_data)-1:
                    break
        if bus_data['end location'][i]!=bus_data['start location'][i+1]:
            print(f'For bus number{bus} begin and end are not the same, rit {i} ends at {bus_data['end location'][i]} en rit {i+1} begins at {bus_data['start location'][i+1]} ')
 




























































































# Bas


# Totale afstand van de bussen

# Dienstregeling selecteren (de verplichte dienstregeling)
line_400 = dm[dm['line']==400]
line_401 = dm[dm['line']==401]
d_ar_to_st400 = line_400['distance_m'].iloc[0]
d_st_to_ar400 = line_400['distance_m'].iloc[1]

d_ar_to_st401 = line_401['distance_m'].iloc[0]
d_st_to_ar401 = line_401['distance_m'].iloc[1]

print(f'Distance for airport to station (line 400):{d_ar_to_st400:.2f}')
print(f'Distance from station to airport (line 400):{d_st_to_ar400:.2f}')
print(f'Distance from airport to station (line 401): {d_ar_to_st401:.2f}')
print(f'Distance from station to aiport (line 401): {d_st_to_ar401:.2f}')

# 2 trajecten van lijn 400
t_ar_to_st400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar400 = len(tt[(tt['line'] == 400) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# 2 trajecten van lijn 401
t_ar_to_st401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvapt') & (tt['end'] == 'ehvbst')])
t_st_to_ar401 = len(tt[(tt['line'] == 401) & (tt['start'] == 'ehvbst') & (tt['end'] == 'ehvapt')])

# Totale afstand per lijn en totaal van de 2 lijnen (van de service trips)
d_400 = (t_ar_to_st400 * d_ar_to_st400) + (t_st_to_ar400 * d_st_to_ar400)
d_401 = (t_ar_to_st401 * d_ar_to_st401) + (t_st_to_ar401 * d_st_to_ar401)

d_service_total_m = d_400+d_401
d_service_total_km = d_service_total_m/1000

print(f'Total service trip distance of lines 400 and 401 (meters): {d_service_total_m:.2f}')
print(f'Total service trip distance of lines 400 and 401 (kilometers): {d_service_total_km:.2f}')
# Material trips moeten nog toegevoegd worden!


# Nu material trips toevoegen 
# Soorten material trips: Station-Garage en andersom, Airport-Garage en andersom,
t_bst_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvgar')])
t_gar_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvbst')])

t_apt_to_gar = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvgar')])
t_gar_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvgar') & (bp['end location'] == 'ehvapt')])

t_apt_to_bst = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvapt') & (bp['end location'] == 'ehvbst')])
t_bst_to_apt = len(bp[(bp['activity'] == 'material trip') & (bp['start location'] == 'ehvbst') & (bp['end location'] == 'ehvapt')])

# Afstanden van de verschillende soorten material trips
d_bst_to_gar = dm[(dm['start'] == 'ehvbst') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 1650 m
d_gar_to_bst = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvbst')]['distance_m'].iloc[0]  # 1650 m

d_apt_to_gar = dm[(dm['start'] == 'ehvapt') & (dm['end'] == 'ehvgar')]['distance_m'].iloc[0]  # 9000 m
d_gar_to_apt = dm[(dm['start'] == 'ehvgar') & (dm['end'] == 'ehvapt')]['distance_m'].iloc[0]  # 9000 m

# Totale afstand materials tripps berekenen
d_material_total = (t_bst_to_gar * d_bst_to_gar) + (t_gar_to_bst * d_gar_to_bst) + (t_apt_to_gar * d_apt_to_gar) + (t_gar_to_apt * d_gar_to_apt)

# Totale afstand = afstand service trips + afstand material trips
total_distance_m = d_service_total_m+d_material_total
total_distance_km = total_distance_m/1000

print(f'Total distance of service trips and material trips (meters): {total_distance_m:.2f}')
print(f'Total distance of service trips and material trips (kilometers): {total_distance_km:.2f}')
print(f'Total distance of material trips:{d_material_total:.2f}')

# Overige KPI's berekenen
# Berekening aantal bussen
aantal_ingezette_bussen = bp['bus'].nunique()
print(f'The number of busses used:{aantal_ingezette_bussen}.')

# Berekening totale rijafstand: net berekend
print(f'Total distance (kilometers): {total_distance_km:.2f}.')
print(f'Total distance (meters):{total_distance_m:.2f}.')

# Total aantal material trips berekenen
t_material_total = t_bst_to_gar + t_gar_to_bst + t_apt_to_gar + t_gar_to_apt + t_apt_to_bst + t_bst_to_apt
print(f'Total of material trips: {t_material_total}')

# Wachttijd berekenen met behulp van idle
# Dataframe aanmaken om wachttijd te bepalen
bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))

# Berekening wachttijd in minuten en uren
idle = bp[bp['activity'] == 'idle']
tot_waiting_time_min = (idle['end_dt'] - idle['start_dt']).dt.total_seconds().sum() / 60
tot_waiting_time_hours = tot_waiting_time_min/60
avg_waiting_time_per_bus= tot_waiting_time_min/aantal_ingezette_bussen # minuten

print(f'Total waiting time in minutes: {tot_waiting_time_min:.2f}')
print(f'Total waiting time in hours: {tot_waiting_time_hours:.2f}')
print(f'Average waiting time per bus (minutes): {avg_waiting_time_per_bus:.2f}')

# Minimale oplaadtijd van 15 minuten
# Oplaadtijd (oplaadduur) eerst berekenen 
# Dan checken of de not_valid_charging_trips 0 is. Dit moet namelijk 0 zijn.

bp['idle_duration_min'] = (bp['end_dt']-bp['start_dt']).dt.total_seconds()/60
valid_charging_trips = bp[(bp['activity']=='idle')&(bp['idle_duration_min']>=15)]
not_valid_charging_trips = bp[(bp['activity']=='idle')&(bp['idle_duration_min']<15)]
valid_charging_time = valid_charging_trips['idle_duration_min'].sum()

print(f'Aantal keer opladen met een oplaadduur van 15 minuten of langer: {len(valid_charging_trips)}')
print(f'Aantal keer opladen met een oplaadduur van maximaal 15 minuten: {len(not_valid_charging_trips)}')
print(f'Totale geldige oplaadttijd: {valid_charging_time:.0f} minuten')

# Charging constraint: checken oplaadsnelheden 
# Hierin is 10% accu verwerkt en de laadsnelheden

# Relevante variabelen, oplaadsnelheden en lege lijsten
bp['start_dt'] = pd.to_datetime('2026-01-01 ' + bp['start time'].astype(str))
bp['end_dt'] = pd.to_datetime('2026-01-01 ' + bp['end time'].astype(str))
bp['idle_duration_min'] = (bp['end_dt'] - bp['start_dt']).dt.total_seconds() / 60

planning_sor = bp.sort_values(['bus', 'start time'])

quick_recharge_speed = 450 / 60  # oplaadsnelheid tot 90% van battery capacity
slow_recharge_speed = 60 / 60    # oplaadsnelheid van de laatste 10% van de battery capacity

empty_bus = []
total_usage = []

# Energie opladen en energieverbruik voor de bussen
for bus, bus_data in planning_sor.groupby('bus'): 
    battery = start_battery

    for idx, row in bus_data.iterrows():
        # Opladen als de bus oplaad (bij 'idle') en bij een minimale oplaadduur van 15 min
        if row['activity'] == 'idle' and row['idle_duration_min'] >= 15:
            time = row['idle_duration_min']
            
            # Snel opladen tot 270 kWh (90% van de batery capacity)
            if battery < 270:
                needed_energy = 270 - battery
                time_needed = needed_energy/ quick_recharge_speed
                if time <= time_needed:
                    battery += time * quick_recharge_speed
                    time = 0
                else:
                    battery = 270
                    time -= time_needed
            
            # Langzaam opladen boven de 270 kWh (tot de 300 kWh)
            if time > 0 and battery < 300:
                battery += min(time * slow_recharge_speed, 300 - battery)

        # Energieverbruik tijdens het rijden aftrekken van de battery
        else:
            if row['activity'] != 'idle':
                battery -= row['energy consumption']

        # Veiligheidsmarge van 10% checken voor de bus
        if battery < min_waarde_battery and bus not in empty_bus:
            empty_bus.append(bus)

    total_usage.append((bus, battery))

# Resultaten tonen
# Aantal bussen tonen die minder dan 10% batterijcapaciteit hebben
if empty_bus:
    print(f'Busses that come under 10% battery capacity: len({empty_bus})')
else:
    print('All busses were above at least 10% battery capacity.')

# Batterijniveau van de bussen aan het einde van het rittenschema tonen
for bus_id, final_batt in total_usage:
    print(f'Bus {bus_id} has final battery level: {final_batt:.2f} kWh')
    # checken of er onmogelijke batterijniveau's zijn
    if (final_batt>300) or (final_batt < 0):
        print(f'Bus {bus_id} has a final battery level that is not possible (above 300 kWh or under 0 kWh). \nThe battery level is: {final_batt:.2f} kWh')
    else:
        pass

