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

# Stap 2.1: controleren of er vreemde tijden in set verstopt zitten

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

# Stap 2.2: controleren of energieconsumptie overeenkomt met type trip
activities = [] # Lijst 'activities' toevoegen
energies = [] # Lijst 'energies' toevoegen
for i in bus_plan['activity']: # Itereren over kolom 'activity' in bus_plan
    activities.append(i) # Alle waarden toevoegen aan kolom 'activities'
for i in bus_plan['energy consumption']: # Itereren over kolom 'energy consumption' in bus_plan
    energies.append(i) # Alle waarden toevoegen aan kolom 'energies'
act_con = pd.DataFrame({'activity': activities, 
                        'energy consumption': energies}) # Dataframe 'act_con' aanmaken

print(act_con[act_con['energy consumption'] < 0]) # Checken of er inderdaad alleen energie wordt opgeladen tijdens het laden: fout in regel 28
print(act_con[20:40]) # In regel 28: tijdens materiaaltrip kan er nooit energie worden opgeladen. Dit wordt hier hersteld.

filtered = (act_con[act_con['activity'] == 'material trip'])
print(filtered)
