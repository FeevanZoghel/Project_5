import pandas as pd
import streamlit as st

# df = pd.read_excel('Bus_Plan_Cleaned.xlsx')
# tt = pd.read_excel('Timetable.xlsx')
# dm = pd.read_excel('DistanceMatrix.xlsx')


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

def only_start_end_times(df):
    start_time = pd.to_timedelta(df['start time'].astype(str))
    end_time = pd.to_timedelta(df['end time'].astype(str))

    end = False
    lijst = []

    for i in range(len(df)):
        verschil = end_time[i] - start_time[i]
        if verschil <= pd.Timedelta(0):
            lijst.append(verschil)

    if len(lijst) != 0:
        end = False
    else:
        end = True

    return end 

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

def start_end_times(df):
    start_time = pd.to_timedelta(df['start time'].astype(str))
    end_time = pd.to_timedelta(df['end time'].astype(str))

    end = False

    for i in range(len(df)):
        verschil = end_time[i] - start_time[i]
        if verschil <= pd.Timedelta(0):
            st.error(f'Row {i+2} has an infeasible start and end time')
            end = False
        else:
            end = True

    return end

def check_min_SOC_print(df):
    assumed_soh = 85
    begincapacity = 300
    min_battery_value = (300 / assumed_soh * 100) * 0.1

    planning_sor = df.sort_values(['bus', 'start time'])

    fout = False

    for bus, bus_data in planning_sor.groupby('bus'):
        battery = begincapacity
        min_battery = begincapacity

        for battery_lose in bus_data['energy consumption']:
            battery -= battery_lose

            if battery < min_battery:
                min_battery = battery

        if min_battery < min_battery_value:
            st.error(
                f'Bus {bus}: battery drops to {min_battery:.2f} kWh. '
                f'Minimum allowed is {min_battery_value:.2f} kWh.'
            )
            fout = True

    if fout:
        return False

    return True
`
def check_end_begin_loc_print(df):

    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)

    fout = False

    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data) - 1):

            end_location = bus_data['end location'][i]
            next_start_location = bus_data['start location'][i + 1]

            if end_location != next_start_location:

                st.error(
                    f'Bus {bus}: location mismatch. '
                    f'Trip ends at "{end_location}", but the next trip '
                    f'starts at "{next_start_location}".'
                )

                fout = True

    if fout:
        return False


    return True
def status_check(tekst, goed):

    if goed:
        kleur = "#4CAF50"
        symbool = "✓"
    else:
        kleur = "#EA3323"
        symbool = "✕"

    html = f"""
<div style="background:#F3F4F6; border-radius:10px; padding:10px 14px; margin:10px 0; display:flex; align-items:center; gap:14px; width:100%; box-sizing:border-box;">
    <div style="width:32px; height:32px; min-width:32px; border-radius:6px; background:{kleur}; color:white; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:bold; line-height:1;">
        {symbool}
    </div>
    <span style="font-size:16px; color:#222222; font-weight:500;">
        {tekst}
    </span>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


##################DEFENITIES FOR FEASIBILITY CHECKS##########################


def check_min_SOC(df):
    assumed_soh = 85
    begincapacity = 300
    min_battery_value = (300 / assumed_soh * 100) * 0.1  # 10% of real capacity
    planning_sor = df.sort_values(['bus', 'start time'])
    
    
    # Sort by busses
    for bus, bus_data in planning_sor.groupby('bus'):
        battery = begincapacity
        
        for battery_lose in bus_data['energy consumption']:
            battery -= battery_lose
            if battery <min_battery_value:
                return False 

    return True

def check_SOH(assumed_soh):
    if 85<= assumed_soh <= 95:
        return True
    else: 
        return False

def check_end_begin_loc(df):
    
    planning = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    
    # Check for every bus
    for bus, bus_data in planning.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)
        for i in range(len(bus_data)):
            if i == len(bus_data) - 1:
                break
            # If end location of trip i is not equal to start location of trip i+1 -> discontinuity
            if bus_data['end location'][i] != bus_data['start location'][i + 1]:
                return False
            
    return True

def check_req_trips(df, tt):
    
    number_of_required_trips = len(tt)
    service_trips_in_planning = df[df['activity'] == 'service trip']
    num_planned_trips = len(service_trips_in_planning)
    # feasibility-outcome
    if number_of_required_trips == num_planned_trips:
        return True
    else:
        numb_missing_trips = number_of_required_trips - num_planned_trips
        return False

def check_min_charging_time(df):
    df['start_dt'] = pd.to_datetime('2026-01-01 ' + df['start time'].astype(str))
    df['end_dt'] = pd.to_datetime('2026-01-01 ' + df['end time'].astype(str))
    df['charging_duration_min'] = (df['end_dt'] - df['start_dt']).dt.total_seconds() / 60

    for idx, row in df.iterrows():
        if row['activity']== 'charging' and row['charging_duration_min']< 15: 
            return False 

    return True 

def check_charging_speed(df):

    quick_recharge_speed = 450 / 60 # kWh/min
    slow_recharge_speed = 60 / 60   # kWh/min
    charging_speeds = [quick_recharge_speed, slow_recharge_speed]
    number_charging_speeds = len(charging_speeds)
    begincapacity = 300

    planning = df.sort_values(['bus', 'start time'])

    for bus, bus_data in planning.groupby('bus'):
        battery = begincapacity
        for idx, row in bus_data.iterrows():
            if row['activity'] == 'charging':
                charging_duration = (pd.to_timedelta(str(row['end time']))- pd.to_timedelta(str(row['start time']))).total_seconds() / 60   
                charging_speed = abs(row['energy consumption']) / charging_duration

                if battery < 270:
                    if charging_speed != quick_recharge_speed:
                        return False
                else:
                    if charging_speed != slow_recharge_speed:
                        return False
                    
            battery -= row['energy consumption']
    return True
def check_overlapping_trips(df):
    
    planning_sor1 = df.sort_values(['bus', 'start time']).reset_index(drop=True)
    for bus, bus_data in planning_sor1.groupby('bus'):
        bus_data = bus_data.reset_index(drop=True)

        for i in range(len(bus_data)):
            for j in range(i+1, len(bus_data)):
                if bus_data['end time'][i] > bus_data['start time'][j]:
                    return False

    return True


def check_all(df):
    '''
    De check van alles
    Ff in een def gezet, want dan kan je makkelijk terughalen
    '''
    kolommen_correct = only_check_columns(df)
    energy_correct = only_energy_check(df)
    tijden_correct = only_times_check(df)
    eind_tijden_correct = only_start_end_times(df)
    min_SOC_correct = check_min_SOC(df)
    locations_correct = check_end_begin_loc(df)

    if kolommen_correct is True and energy_correct is True and tijden_correct is True and eind_tijden_correct is True and min_SOC_correct is True and locations_correct is True:
        st.success('De data is compleet')
    else:
        st.error('Data is incorrect')
        with st.expander('Click here for details'):

            with st.container(height=400):

                check_columns(df)
                times_check(df)
                energy_check(df)
                start_end_times(df)
                check_min_SOC_print(df)
                check_end_begin_loc_print(df)