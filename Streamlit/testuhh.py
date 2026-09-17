import pandas as pd
import streamlit as st

df = pd.read_excel('Bus_Plan_Cleaned.xlsx')


def check_columns(df):
    """
    
    Checken of de kolommen uit de gegeven dataset correct zijn

    Hij checkt per kolom of die data mist / of er spelfouten in de kolomnamen zitten.


    """
    fout = False

    columns = df.columns.tolist()
    good_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

    for i in columns:
        if i not in good_columns:
            st.error(f'The name of column "{i}" is wrong')
            fout = True

    for i in good_columns:
        if i not in columns:
            st.error(f'The columns called "{}" is missing')
            fout = True

    if fout == False:
        st.succes('all columns are correct')




