import pandas as pd

df = pd.read_excel('bus_plan_gecleaned.xlsx')
print(df.columns)

if df.columns is not ['start location', 'end location', 'start time', 'end time', 'activity',
       'line', 'energy consumption', 'bus']:
    print('dinge')
else:
    print('Werkt wel!')
