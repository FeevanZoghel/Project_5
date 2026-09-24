import pandas as pd
import streamlit as st

df = pd.read_excel('Bus_Plan_Cleaned.xlsx')

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
            fout = True
            return False

    if fout is False:
        return True

def only_times_check(df):
    '''

    Checkt per rij of er een foutieve tijd zit
    Tijden moeten format HH:MM:SS hebben

    Gebruik gemaakt van try, except.    
        Dat is eigenlijk een beetje if-statements, maar ipv dat die een foutmelding geeft werkt dit wel
        python probeert de code uit te voeren, en als ie een foutmelding geeft doet die de 'except'

    Enumerate geeft zowel de waarde als de rij.

    De definitie print uit in welke rij en kolom de foutieve tijd zit.

    '''

    kolommen = ['start time', 'end time']

    for kolom in kolommen:

        uren = []
        minuten = []
        seconden = []
        dubbele_tekens = []
        fout = False

        for rij, i in enumerate(df[kolom]):
            i = str(i)

            try:
                uren.append(int(i[0:2]))
                minuten.append(int(i[3:5]))
                seconden.append(int(i[6:8]))

                if i[2] == ':' and i[5] == ':':
                    dubbele_tekens.append(':')

            except:
                fout = True

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


    if fout == False:
        return True
    else:
        return False

def only_energy_check(df):
    '''
    Checkt rij voor rij:
        Als de bus aan het opladen is moet/mag de energy consumption negatief zijn.
        Als de bus niet aan het opladen is moet de energy consumption positief zijn.

    Rij, row df.iterrows()
        Hij gaat rij voor rij door de DataFrame heen
    '''

    fout = False

    for rij, row in df.iterrows():

        if row['activity'] == 'charging':
            if row['energy consumption'] >= 0:
                fout = True
                return False

        else:
            if row['energy consumption'] <= 0:
                fout = True
                return False

    if fout == False:
        return True

def times_check(df):
    kolommen = ['start time', 'end time']
    fout = False
    
    for kolom in kolommen:

        uren = []
        minuten = []
        seconden = []
        dubbele_tekens = []

        for rij, i in enumerate(df[kolom]):
            i = str(i)

            try:
                uren.append(int(i[0:2]))
                minuten.append(int(i[3:5]))
                seconden.append(int(i[6:8]))

                if i[2] == ':' and i[5] == ':':
                    dubbele_tekens.append(':')

            except:
                fout = True
                st.error(f'Row {rij + 2} in column "{kolom}" has an invalid time: "{i}"')                

        for uur in uren:
            if uur < 0 or uur > 23:
                fout = True
                st.error(f'Column "{kolom}" contains an invalid minute: "{minuut}"')

        for minuut in minuten:
            if minuut < 0 or minuut > 59:
                fout = True
                st.error(f'Column "{kolom}" contains an invalid minute: "{minuut}"')

        for seconde in seconden:
            if seconde < 0 or seconde > 59:
                fout = True
                st.error(f'Column "{kolom}" contains an invalid minute: "{minuut}"')

        if len(dubbele_tekens) != len(df[kolom]):
            fout = True

    if fout == False:
        return True
    else:
        return False

def energy_check(df):
    fout = False

    for rij, row in df.iterrows():

        if row['activity'] == 'charging':
            if row['energy consumption'] >= 0:
                st.error(
                    f'Row {rij + 2}: charging has an incorrect energy consumption'
                )
                fout = True
                return False

        else:
            if row['energy consumption'] <= 0:
                st.error(
                    f'Row {rij + 2}: {row["activity"]} has an incorrect energy consumption'
                )
                fout = True
                return False

    if fout == False:
        return True

def check_columns(df):
    """
    
    Checken of de kolommen uit de gegeven dataset correct zijn

    Hij checkt per kolom of die data mist / of er spelfouten in de kolomnamen zitten.

    En print dan ook waar de fout zit


    """
    fout = False

    columns = df.columns.tolist()
    good_columns = ['start location', 'end location', 'start time', 'end time', 'activity', 'line', 'energy consumption', 'bus']

    if len(columns) != len(good_columns):
        st.error("The number of columns is incorrect")
        fout = True

    else:
        for i in range(len(columns)):
            if columns[i] != good_columns[i]:
                st.error(f'Column "{columns[i]}" is wrong. It should be "{good_columns[i]}".')
                fout = True

    if fout == False:
        return True

def tijden_check(df):
    start_time = pd.to_timedelta(df['start time'].astype(str))
    end_time = pd.to_timedelta(df['end time'].astype(str))

    for i in range(len(df)):
        verschil = end_time[i] - start_time[i]
        if verschil <= 0:
            st.error(f'Row {i} has a wrong start or end time')
            return False
        else:
            return True
        

def check_all(df):
    '''
    De check van alles
    Ff in een def gezet, want dan kan je makkelijk terughalen
    '''
    kolommen_correct = only_check_columns(df)
    energy_correct = only_energy_check(df)
    tijden_correct = only_times_check(df)


    if kolommen_correct is True and energy_correct is True and tijden_correct is True :
        st.success('De data is compleet')
    else:
        st.error('Data is incorrect')
        if st.button('Click here for details'):
            check_columns(df)
            times_check(df)
            energy_check(df)
