#URL:
#https://project5-jmfoec4ruxwpczdw5mf76w.streamlit.app/

from DataFrame_check import (
    check_all,
    check_min_SOC,
    check_SOH,
    check_end_begin_loc,
    check_req_trips,
    check_min_charging_time,
    check_charging_speed,
    check_overlapping_trips
)

from Berekeningen import bus_energy_check
from berekeningen_cleaned import gantt_chart_bus

import streamlit as st
import pandas as pd

st.sidebar.title("Menu")
st.write('hello world')


keuze = st.sidebar.selectbox(
    "Kies een pagina",
    ["Home", "Data_check", "Gegevens (KPI)"]
)

if keuze == "Home":
    st.header("Home")
    st.write("Welkom!")
    st.title("Mijn Streamlit App")
    st.write("Welkom bij mijn app!")
    st.subheader("Voer je gegevens in")
    naam = st.text_input("Wat is je naam?")
    leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120)
    keuze = st.selectbox(
        "Kies een optie",
        ["Optie 1", "Optie 2", "Optie 3"]
    )
    if keuze == 'Optie 3':
        st.write('Kies niet deze')
    # Checkbox
    akkoord = st.checkbox("Ik ga akkoord")
    # Knop
    if st.button("Versturen"):
        st.write("Hallo", naam)
        st.write("Je bent", leeftijd, "jaar oud.")
        st.write("Je koos:", keuze)
    # DataFrame maken
    df = pd.DataFrame({
        "Naam": ["Jan", "Piet", "Sophie"],
        "Leeftijd": [21, 24, 19]
    })
    # DataFrame laten zien
    st.subheader("Data")
    st.dataframe(df)
    # Alleen eerste rijen
    st.write("Eerste twee rijen:")
    st.dataframe(df.head(2))


elif keuze == "Data_check":

    st.title("Transdev Planning Checker")
    bestand = st.file_uploader("Upload een busplanning", type=["xlsx"])

    if bestand is not None:
        df = pd.read_excel(bestand)

        bestand2 = st.file_uploader('upload een timetable', type = ['xlsx'])
        df2 = pd.read_excel(bestand2)

        # Data check
        with st.container(border=True):
            check_all(df)

        # Planning
        with st.container(border=True):
            st.subheader("Ingelezen planning")
            st.dataframe(df.head(10))
        
        # Feasibility checks
        with st.container(border=True):
            st.subheader("Feasibility checks")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("🔋 Battery & charging")
                
                st.checkbox("Minimum SOC is maintained (10%)", value=check_min_SOC(df), disabled=True )
                st.checkbox("SOH is correct (between 85% and 95%)", value=check_SOH(85), disabled=True)
                st.checkbox("Minimum charging time (15 minutes)", value=check_min_charging_time(df), disabled=True)
                st.checkbox("Charging speed is correct", value=check_charging_speed(df), disabled=True)


            with col2:
                st.markdown("📍 Planning")

                st.checkbox("Start and end locations match", value=check_end_begin_loc(df), disabled=True)
                st.checkbox("No overlapping trips", value=check_overlapping_trips(df), disabled=True)
                st.checkbox("All Required trips", value = check_req_trips(df,df2), disabled = True)

        # Gantt chart
        with st.container(border=True):
            st.subheader("Bus planning overview")
            gantt_chart_bus(df)

        
    
    
    


elif keuze == "Gegevens (KPI)":
    bestand = st.file_uploader("Upload een busplanning", type=["xlsx"])

    if bestand is not None:
        df = pd.read_excel(bestand)

        check_all(df)
        keuze2 = st.selectbox("What do you want to see?",
        ["Energy Consumption", "Een andere die ik nog niet heb bedacht"]
        )

        if keuze2 == "Energy Consumption":
            st.subheader('Energy consumption from busses:')
            bus_energy_check(df)
