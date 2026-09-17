import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import numpy as np
import math as m
import scipy.stats as sp
from datetime import datetime as dt

bus_plan = pd.read_excel('Bus Planning.xlsx')

# Stap 1: opsporen van onnauwkeurigheden in data, behalve voor kolommen 'start time', 'end time' en 'energy consumption'

# Stap 1.1: nieuwe lijst 'kolommen' aanmaken
kolommen = ['start location', 'end location', 'activity', 'line', 'bus']

# Stap 1.2: dictionary aanmaken
dict1 = dict()

# Stap 1.3: itereren over alle data per kolom in lijst 'kolommen' voor onnauwkeurigheden en toevoegen aan dataframe
for i in kolommen:
    unique = bus_plan[i].unique()
    dict1[i] = unique # Stap 1.4: alle verkregen unieke waarden toevoegen aan dataframe
    print(f' {i} = {dict1[i]}') # Stap 1.5: dictionary met unieke waarden uitprinten

# Geen inconsistenties, fouten of onnauwkeurigheden opgespoord

# Stap 2: voor 'start time', 'end time' en 'energy consumption' kolommen cleanen
df = pd.DataFrame({})

# Stap 2: controleren of er vreemde tijden in set verstopt zitten

# Stap 2.1.1: functie aanmaken die controleert of er geen 'vreemde' tijden in set verstopt zitten

def tijden_check(kolom):
    # lijsten aanmaken van uren, minuten, seconden en dubbele tekens
    uren = []
    minuten = []
    seconden = []
    dubbele_tekens = []
    for i in kolom: # Voor alle tijden itereren in kolom 'start_time'
        i = str(i) # Tijd omzetten naar string
        uren.append(int(i[0:2])) # Uren van tijd toevoegen aan lijst 'uren'
        minuten.append(int(i[3:5])) # Uren van tijd toevoegen aan lijst 'uren'
        seconden.append(int(i[6:len(i)])) # Uren van tijd toevoegen aan lijst 'uren'
        if i[2] == ':' and i[5] == ':':
            dubbele_tekens.append(':') # Dubbel teken toevoegen aan lijst 'dubbele_tekens'
    for uur in uren:
       if uur < 0 or uur > 23: # Controleren of de getallen geen inconsistenties bevatten, indien wel wordt de fout gemeld
           print(uur)
    for minuut in minuten:
       if minuut < 0 or minuut > 60: # Controleren of de getallen geen inconsistenties bevatten, indien wel wordt de fout gemeld
           print(minuut)
    for seconde in seconden:
       if seconde < 0 or seconde > 60: # Controleren of de getallen geen inconsistenties bevatten, indien wel wordt de fout gemeld
           print(seconde)
    if len(dubbele_tekens) != len(bus_plan['start time']):
        print('Een of meerdere tijden bevatten inconsistenties')
    
tijden_check(bus_plan['start time']) # Met deze functies worden alle fouten, inconsistenties en onregelmatigheden in de kolommen gecheckt
tijden_check(bus_plan['end time'])

# Stap 3: controleren of energieconsumptie overeenkomt met type trip
bus_plan[bus_plan['energy consumption'] < 0] # Checken of er inderdaad alleen energie wordt opgeladen tijdens het laden: fout in regel 28 # In regel 28: tijdens materiaaltrip kan er nooit energie worden opgeladen. Dit wordt hier hersteld.


filtered1 = bus_plan[bus_plan['activity'] == 'material trip'] # Filter 1 aanbrengen; sorteren op material trips
filtered2 = bus_plan[bus_plan['start location'] == 'ehvbst'] # Filter 2 aanbrengen; sorteren op startlocatie 'ehvbst'
filtered3 = bus_plan[bus_plan['end location'] == 'ehvgar'] # Filter 3 aanbrengen; sorteren op eindlocatie 'ehvgar'
filtered123 = bus_plan[
    (bus_plan['activity'] == 'material trip') &
    (bus_plan['start location'] == 'ehvbst') & 
    (bus_plan['end location'] == 'ehvgar')] # Alles samenvoegen tot een gehele filterwijziging

print(filtered123) # Resultaten filter overzichtelijk maken
bus_plan.loc[28, 'energy consumption'] = 1.98 # Waarde van -157.5 energieconsumptie-eenheden aangepast tot + 1.98, uitgaande van gebruikt filter 'filter123'
print(bus_plan.head(30)) # Controleren of wijziging succesvol is verlopen; ja.

# Stap 4: controleren of er geen uitschieters in ritten zitten: zelf beoordeeld dat er geen verdere check hiervoor nodig is.

# Stap 5: df omzetten in Excel-bestand
bus_plan.to_excel('Bus_Plan_Cleaned.xlsx', index = False)