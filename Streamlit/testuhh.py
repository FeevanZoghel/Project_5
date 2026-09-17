import pandas as pd

df = pd.read_excel('Bus_Plan_Cleaned.xlsx')


def Check_columns(df):
    """
    
    Checken of de kolommen uit de gegeven dataset correct zijn

    return: 
        True als kolommen goed zijn
        False als kolommen anders zijn
    
    miss per kolom checken? dus dan weet je ook welke er mis is

    """
    columns = df.columns.tolist()
    good_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

    return columns == good_columns