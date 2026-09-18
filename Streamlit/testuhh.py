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
        st.success('all columns are correct')



def tijden_check(df):

    kolommen = ['start time', 'end time']

    for kolom in kolommen:

        uren = []
        minuten = []
        seconden = []
        dubbele_tekens = []
        fout = False

        for i in df[kolom]:
            i = str(i)

            uren.append(int(i[0:2]))
            minuten.append(int(i[3:5]))
            seconden.append(int(i[6:len(i)]))

            if i[2] == ':' and i[5] == ':':
                dubbele_tekens.append(':')

        for uur in uren:
            if uur < 0 or uur > 23:
                fout = True

        for minuut in minuten:
            if minuut < 0 or minuut > 59:
                fout = True

        for seconde in seconden:
            if seconde < 0 or seconde > 59:
                fout = True

        if len(dubbele_tekens) != len(df[kolom]):
            fout = True


        if fout:
            st.error(f'One or more times in "{kolom}" contain inconsistencies')
        else:
            st.success(f'All times in "{kolom}" are correct')