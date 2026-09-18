import pandas as pd
import streamlit as st

df = pd.read_excel('Bus_Plan_Cleaned.xlsx')


def check_columns(df):
    """
    
    Checken of de kolommen uit de gegeven dataset correct zijn

    Hij checkt per kolom of die data mist / of er spelfouten in de kolomnamen zitten.

    En print dan ook waar de fout zit


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
            st.error(f'The columns called "{i}" is missing')
            fout = True

    if fout == False:
        st.success('all columns are correct')


def only_check_columns(df):
    '''
    
    alleen kolommen checken
    return:
         alleen of kolommen fout zijn? of correct.
    
    '''

    fout = False
    
    columns = df.columns.tolist()
    good_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

    for i in columns:
        if i not in good_columns:
            st.error(f'The column {i} is misspelled or missing')
            fout = True

    if fout == False:
        st.successs('all columns are correct')



def tijden_check(df):
    kolommen = ['start time', 'end time']

    for kolom in kolommen:
        fout = False

        for tijd in df[kolom]:
            tijd = str(tijd)

            try:
                uren = int(tijd[0:2])
                minuten = int(tijd[3:5])
                seconden = int(tijd[6:8])

                if uren < 0 or uren > 23:
                    fout = True

                if minuten < 0 or minuten > 59:
                    fout = True

                if seconden < 0 or seconden > 59:
                    fout = True

                if tijd[2] != ':' or tijd[5] != ':':
                    fout = True

            except:
                fout = True

        if fout:
            st.error(f'Invalid values found in "{kolom}"')
        else:
            st.success(f'All values in "{kolom}" are valid')