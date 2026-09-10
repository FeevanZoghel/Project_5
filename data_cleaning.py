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
for i in bus_plan['start time'].head(10):
    df['Tijd'] = (pd.to_datetime(i, format='%H:%M:%S'))
    df['Uur'] = df['Tijd'].dt.hour
    df['Minuut'] = df['Tijd'].dt.minute
    df['Seconde'] = df['Tijd'].dt.second # Zet alle strings van kolom bus_plan['start time'] om naar tijd / datetime
print(df)


