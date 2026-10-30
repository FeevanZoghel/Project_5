# Importing relevant Python libraries
import pandas as pd 
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import time

# Start calculating calculation time of this code
t_start = time.perf_counter()

# Data importing
bp = pd.read_excel('Bus_Plan_Cleaned.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
tt = pd.read_excel('Timetable.xlsx')

# Dataframe for improved bus plan
ibp = pd.DataFrame(columns=['start location', 'end location','start time','end time','activity','line','energy consumption','total battery bus' ,'total travel time','bus'])

# Sort timetable, starting the day at 05:07 (dit stukje is met chat gemaakt)
tt['sort_time'] = pd.to_datetime(tt['departure_time'], format='%H:%M')
tt.loc[tt['sort_time'].dt.time < pd.Timestamp('05:07').time(), 'sort_time'] += pd.Timedelta(days=1)
tt = tt.sort_values(by='sort_time').reset_index(drop=True)


# lege set met bussen aanmaken
bussen = []
battery = {}
charging_start = {}

# Beginwaardes
assumed_battery_value = 85
max_battery = 300 * assumed_battery_value / 100
charging_limit = 0.9 * max_battery
fast_charge_per_min = 450 / 60
slow_charge_per_min = 60 / 60
min_battery_value = max_battery * 0.1




def add_activity(ibp, bus, start_location, end_location, start_time, end_time,
                 activity, line, energy, battery_value, total_travel_time):
    """Voeg een activiteit van een bus als nieuwe rij aan het busplan toe.

    Args:
        ibp: DataFrame met het busplan dat wordt bijgewerkt.
        bus: Identificatie van de bus.
        start_location: Vertreklocatie van de activiteit.
        end_location: Aankomstlocatie van de activiteit.
        start_time: Starttijd van de activiteit.
        end_time: Eindtijd van de activiteit.
        activity: Type activiteit, bijvoorbeeld een rit of laadbeurt.
        line: Lijnnummer, of None als de activiteit niet bij een lijn hoort.
        energy: Energieverbruik (negatief bij energie die wordt opgeladen).
        battery_value: Batterijcapaciteit van de bus na de activiteit.
        total_travel_time: Totale reistijd van de bus tot en met deze activiteit.
    """

    new_index = len(ibp)

    ibp.loc[new_index] = [start_location, end_location, start_time, end_time, activity, line, energy, battery_value, total_travel_time, bus]

def charging_buses(bussen_opladen, ibp, battery, charging_start, start_time,
                         benodigde_energy, charging_limit, fast_charge_per_min,
                         slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip):
    """Verwerk bussen die moeten laden en registreer laad- of materiaalritten.

    Bussen die voldoende lang hebben geladen en genoeg energie hebben voor de
    volgende rit worden aan ``beschikbare_bussen`` toegevoegd. De planning,
    batterijlading en laadtijden worden waar nodig bijgewerkt.

    Args:
        bussen_opladen: Bus-ID's die voor de volgende rit worden gecontroleerd.
        ibp: DataFrame met het busplan dat wordt bijgewerkt.
        battery: Batterijlading per bus, bijgewerkt tijdens deze functie.
        charging_start: Starttijd van het laden per bus, bijgewerkt tijdens
            deze functie.
        start_time: Geplande starttijd van de volgende rit.
        benodigde_energy: Minimale energie die nodig is voor die rit.
        charging_limit: Batterijniveau tot waar snel wordt geladen.
        fast_charge_per_min: Snelheid van snel laden in energie-eenheden per
            minuut.
        slow_charge_per_min: Snelheid van langzaam laden in energie-eenheden
            per minuut.
        max_battery: Maximale batterijcapaciteit.
        beschikbare_bussen: Lijst die wordt aangevuld met beschikbare bussen.
        dm: DataFrame met reistijden tussen locaties.
        bp: DataFrame met energieverbruik per rit.
        trip: Volgende rit waarvoor een bus nodig is.
    """

    for bus in bussen_opladen:
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1, :]

        # bus staat al bij de garage
        if last_activity['end location'] == 'ehvgar':

            if bus not in charging_start:
                charging_start[bus] = last_activity['end time']

            else:
                charging_time = (start_time - charging_start[bus]).total_seconds() / 60
                battery_start = battery[bus]

                #niet meer dan 100% opladen en vershillende oplaad snelheden
                if battery_start < charging_limit:
                    tijd_tot_90 = (charging_limit - battery_start) / fast_charge_per_min
                    tijd_tot_100 = tijd_tot_90 + (max_battery - charging_limit) / slow_charge_per_min
                else:
                    tijd_tot_100 = (max_battery - battery_start) / slow_charge_per_min

                charging_time = min(charging_time, tijd_tot_100)

                if battery_start < charging_limit:
                    tijd_tot_90 = (charging_limit - battery_start) / fast_charge_per_min

                    if charging_time <= tijd_tot_90:
                        charged_energy = charging_time * fast_charge_per_min
                    else:
                        remaining_time = charging_time - tijd_tot_90
                        charged_energy = (charging_limit - battery_start) + remaining_time * slow_charge_per_min

                else:
                    charged_energy = charging_time * slow_charge_per_min

                battery_after_charging = min(max_battery, battery_start + charged_energy)
                charged_energy = battery_after_charging - battery_start

                # minstens 15 minuten opladen
                charging_end = charging_start[bus] + pd.Timedelta(minutes=charging_time)
                idle_energy = max(0, (start_time - charging_end).total_seconds()/3600)*5
                if (charging_time >= 15 and battery_after_charging- idle_energy >= benodigde_energy):
                    battery[bus] = battery_after_charging
                    # Charging activity toevoegen aan de planning
                    charging_end = charging_start[bus] + pd.Timedelta(minutes=charging_time)

                    add_activity(ibp, bus, 'ehvgar', 'ehvgar', charging_start[bus], charging_end, 'charging', None, -charged_energy, battery[bus], last_activity['total travel time'])
                    

                    if last_activity['end location'] == trip['start']:
                        beschikbare_bussen.append(bus)
                    del charging_start[bus]
        else:
            
            material_start = last_activity['end location']
            dm_material = dm[(dm['start'] == material_start) & (dm['end'] == 'ehvgar')]

            material_travel_time = (dm_material['min_travel_time'].iloc[0]+dm_material['max_travel_time'].iloc[0])/2
            material_energy = bp[(bp['start location'] == material_start) & (bp['end location'] == 'ehvgar') &(bp['activity'] == 'material trip')]['energy consumption'].mean()
            material_start_time = last_activity['end time']
            material_end_time = material_start_time + pd.Timedelta(minutes=material_travel_time)

            battery[bus] -= material_energy

            add_activity(ibp, bus, material_start, 'ehvgar', material_start_time, material_end_time, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)

            charging_start[bus] = material_end_time

def garage_to_trip(bus, trip, start_time, ibp, battery, dm, bp):
    """Plan een materiaalrit van de garage naar de startlocatie van een rit.

    Trekt het energieverbruik van de batterij af en registreert de
    materiaalrit in het busplan. Er wordt niets toegevoegd als de busrit
    vanuit de garage vertrekt.

    Args:
        bus: Identificatie van de bus.
        trip: Volgende dienstregelingrit, met ten minste ``start`` en ``line``.
        start_time: Starttijd van de dienstregelingrit.
        ibp: DataFrame met het busplan dat wordt bijgewerkt.
        battery: Batterijlading per bus, bijgewerkt voor de materiaalrit.
        dm: DataFrame met reistijden tussen locaties.
        bp: DataFrame met energieverbruik per materiaalrit.
    """
    if trip['start'] == 'ehvgar':
            return
    
    dm_material = dm[(dm['start']=='ehvgar') & (dm['end'] == trip['start'])]
    material_travel_time = (dm_material['min_travel_time'].iloc[0]+dm_material['max_travel_time'].iloc[0])/2
    material_start_time = start_time - pd.Timedelta(minutes = material_travel_time)
    material_end_time = material_start_time+pd.Timedelta(minutes = material_travel_time)
    material_energy = bp[(bp['start location'] == 'ehvgar') & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].mean()
    battery[bus] -= material_energy
    
    add_activity(ibp, bus, 'ehvgar', trip['start'], material_start_time, material_end_time, 'material trip', trip['line'], material_energy, battery[bus], material_travel_time)
    
def check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=False):
    """Bereken de benodigde materiaalrit naar de startlocatie van een rit.

    Als ``toevoegen`` waar is en er een materiaalrit nodig is, wordt deze aan
    het busplan toegevoegd en van de batterij afgetrokken.

    Args:
        bus: Identificatie van de bus.
        last_activity: Laatste geplande activiteit van de bus.
        trip: Volgende dienstregelingrit, met ten minste ``start``.
        ibp: DataFrame met het busplan.
        battery: Batterijlading per bus; alleen bijgewerkt als de rit wordt
            toegevoegd.
        dm: DataFrame met reistijden tussen locaties.
        bp: DataFrame met energieverbruik per materiaalrit.
        toevoegen: Bepaalt of een benodigde materiaalrit ook wordt
            geregistreerd.

    Returns:
        Een tuple met de benodigde reistijd in minuten en het energieverbruik.
    """
    if last_activity['end location'] == trip['start']:
        material_travel_time = 0
        material_energy = 0
    else: 
        dm_material = dm[(dm['start'] == last_activity['end location']) & (dm['end'] == trip['start'])]
        material_travel_time = (dm_material['min_travel_time'].iloc[0] + dm_material['max_travel_time'].iloc[0]) / 2
        material_energy = bp[(bp['start location'] == last_activity['end location']) & (bp['end location'] == trip['start']) & (bp['activity'] == 'material trip')]['energy consumption'].mean()
    
    aankomsttijd = last_activity['end time'] + pd.Timedelta(minutes=material_travel_time)
    if toevoegen and material_travel_time >0:
        battery[bus] -= material_energy
        add_activity(ibp, bus, last_activity['end location'], trip['start'], last_activity['end time'], aankomsttijd, 'material trip', None, material_energy, battery[bus], last_activity['total travel time'] + material_travel_time)
    
    return material_travel_time, material_energy

def calculate_idle_time(bus, start_time, ibp, battery, toevoegen = False):
    """Bereken het energieverbruik terwijl een bus stilstaat.

    Als ``toevoegen`` waar is, wordt de stilstand als activiteit geregistreerd
    en wordt het energieverbruik van de batterij afgetrokken.

    Args:
        bus: Identificatie van de bus.
        start_time: Tijd waarop de volgende activiteit begint.
        ibp: DataFrame met het busplan.
        battery: Batterijlading per bus; alleen bijgewerkt als de stilstand
            wordt toegevoegd.
        toevoegen: Bepaalt of de stilstand in het busplan wordt geregistreerd.

    Returns:
        Het energieverbruik tijdens de stilstand.
    """
    last_activity = ibp[ibp['bus'] == bus].iloc[-1]

    idle_start = last_activity['end time']
    idle_end = start_time

    idle_hours = max(0, (idle_end - idle_start).total_seconds() / 3600) # nooit een negatieve wachttijd
    idle_energy = idle_hours * 5  # 5 kwh energie verbruik 
    if toevoegen and idle_hours>0:
        battery[bus] -= idle_energy
        add_activity(ibp, bus, last_activity['end location'], last_activity['end location'], idle_start, idle_end, 'idle', None, idle_energy, battery[bus], last_activity['total travel time'])

    return idle_energy







# alle trips aan een bus toewijzen 
for i in range(len(tt)):
    trip = tt.iloc[i,:]
    
    dm_trip = dm[(dm['start'] == trip['start']) &(dm['end'] == trip['end']) &(dm['line'] == trip['line'])]
    energy_consumption = bp[(bp['start location'] == trip['start']) & (bp['end location'] == trip['end']) & (bp['line'] == trip['line']) &(bp['activity'] == 'service trip')]['energy consumption'].mean()


    start_time = trip['sort_time']
    travel_time = (dm_trip['min_travel_time'].iloc[0]+dm_trip['max_travel_time'].iloc[0])/2
    end_time = start_time + pd.Timedelta(minutes=travel_time)
    # als er geen bussen maakt het een nieuwe bus aan
    if len(bussen) == 0:
        bussen.append('bus1')
        battery['bus1'] = max_battery
        #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden
        garage_to_trip('bus1', trip, start_time, ibp, battery, dm, bp)
        
        
        new_index = len(ibp)
        ibp.loc[new_index, 'start location']        = trip['start']
        ibp.loc[new_index, 'end location']          = trip['end']
        ibp.loc[new_index, 'start time']            = start_time
        ibp.loc[new_index, 'end time']              = end_time
        ibp.loc[new_index, 'line']                  = trip['line']
        ibp.loc[new_index, 'bus']                   = bussen[0]
        ibp.loc[new_index, 'activity']              = 'service trip'
        ibp.loc[new_index, 'energy consumption']    = energy_consumption
        ibp.loc[new_index, 'total travel time']     = travel_time
        battery['bus1']                             -= energy_consumption
        ibp.loc[new_index, 'total battery bus']     = battery['bus1']
          
        continue

    material_energy         = bp[(bp['start location'] == trip['end']) & (bp['end location'] == 'ehvgar') & (bp['activity'] == 'material trip')]['energy consumption'].mean()

    
    if trip['end'] =='ehvgar':
        benodigde_energy = energy_consumption +min_battery_value
    else: 
         benodigde_energy = energy_consumption +material_energy+min_battery_value
    
    beschikbare_bussen = []
    bussen_opladen = []

    # Bussen die al aan het laden zijn opnieuw controleren
    for bus in charging_start:
        bussen_opladen.append(bus)

    # kijkt of een bus beschikbaar is
    for bus in bussen:
        if bus in charging_start:
            continue
        
        bus_planning = ibp[ibp['bus'] == bus]
        last_activity = bus_planning.iloc[-1, :]

        material_travel_time, material_energy = check_material_trip(bus, last_activity, trip, ibp, battery, dm, bp)
        idle_energy = calculate_idle_time(bus, start_time - pd.Timedelta(minutes=material_travel_time), ibp, battery)


        if (last_activity['end time'] + pd.Timedelta(minutes=material_travel_time) <= start_time):
            if battery[bus] >= benodigde_energy + material_energy + idle_energy:
                beschikbare_bussen.append(bus)
            else:
                if bus not in bussen_opladen:
                    bussen_opladen.append(bus)

    charging_buses(bussen_opladen, ibp, battery, charging_start, start_time, benodigde_energy, charging_limit, fast_charge_per_min, slow_charge_per_min, max_battery, beschikbare_bussen, dm, bp, trip)
    
    
    
#########################hier niet aankomen#############################
    # als er geen bus beschikbaar is dan een nieuwe bus toevoegen
    nieuwe_bus_aangemaakt = False

    if len(beschikbare_bussen)==0:

        nieuwe_bus = 'bus' + str(len(bussen) + 1)
        bussen.append(nieuwe_bus)
        battery[nieuwe_bus] = max_battery

        #laat de bus beginnen bij garage en zo nodig naar trip locatie rijden
        garage_to_trip(nieuwe_bus, trip, start_time, ibp, battery, dm, bp)

        gekozen_bus = nieuwe_bus
        nieuwe_bus_aangemaakt = True

    # kiest de bus met de hoogste traveltijd 
    else:
            gekozen_bus = max(beschikbare_bussen, key=lambda b: ibp[ibp['bus'] == b].iloc[-1]['end time'])
            nieuwe_bus_aangemaakt = False

            last_activity = ibp[ibp['bus'] == gekozen_bus].iloc[-1, :]
            check_material_trip(gekozen_bus, last_activity, trip, ibp, battery, dm, bp, toevoegen=True)
            calculate_idle_time(gekozen_bus, start_time, ibp, battery, toevoegen = True)
            
            # Haal de huidige totale reistijd van de gekozen bus op
            hoogste_travel_tijd = ibp[ibp['bus'] == gekozen_bus].iloc[-1]['total travel time']

    
    battery[gekozen_bus] -= energy_consumption
    if nieuwe_bus_aangemaakt:
        total_travel_time = travel_time
    else:
        total_travel_time = hoogste_travel_tijd + travel_time

    add_activity(ibp, gekozen_bus, trip['start'], trip['end'], start_time, end_time, 'service trip', trip['line'], energy_consumption, battery[gekozen_bus], total_travel_time)



# de bussen naar de garage terug laten rijden en daarna laten laden.
for bus in bussen: 
    last_activity = ibp[ibp['bus'] == bus].iloc[-1]

    if last_activity['end location']!= 'ehvgar':
        trip_gar = {'start': 'ehvgar'} # normaal de volgende trip doorgeven, nu het alle trips gereden, dus de 'volgende' trip moet starten bij ehvgar wat de eindlocatie is
        material_travel_time, material_energy = check_material_trip(bus, last_activity, trip_gar, ibp, battery, dm, bp, toevoegen = True )

    if battery[bus] < max_battery:
        last_activity = ibp[ibp['bus'] == bus].iloc[-1]
        battery_start = battery[bus]
        if battery_start < charging_limit:
            tijd_tot_90 = (charging_limit - battery_start) / fast_charge_per_min
            charging_time = tijd_tot_90 + (max_battery - charging_limit) / slow_charge_per_min
        else:
            charging_time = (max_battery - battery_start) / slow_charge_per_min



        #dit zorgt ervoor dat er geen feasibility error is, omdat op het eind de bussen wel anders onder de 15 minuten laten zit
        charging_time = max(15, charging_time)
        charging_end = last_activity['end time'] + pd.Timedelta(minutes=charging_time)
        charged_energy = max_battery - battery_start

        battery[bus] = max_battery

        add_activity(ibp, bus, 'ehvgar', 'ehvgar', last_activity['end time'], charging_end, 'charging', None, -charged_energy, battery[bus], last_activity['total travel time'])


print(ibp)
















#Loading functions from other file
print('voor import')
from Code_for_bus_cleaned import (run_all_feasibility_checks,run_all_kpi_calculations,export_results_to_excel)
print('na import')
feasibility_results = run_all_feasibility_checks(ibp, tt)
kpi_results = run_all_kpi_calculations(ibp, dm, tt)





ibp[['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']].to_excel('BRO.xlsx', index = False)

output_filename = 'Improved_plan_Feasibility_and_KPI_results.xlsx'
output = export_results_to_excel(feasibility_results, kpi_results, filename=output_filename)
output



t_end = time.perf_counter()
computation_time = t_end - t_start

print(f'Computation time: {computation_time:.2f} seconds.')