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
from testen import gantt_chart_bus

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

        # Data check
        check_all(df)

        # Feasibility checks
        st.subheader("Feasibility checks")

        checks = {
            "Minimum SOC is maintained": check_min_SOC(df),
            "SOH is correct": check_SOH(85),
            "Start and end locations match": check_end_begin_loc(df),
            "Minimum charging time is maintained": check_min_charging_time(df),
            "Charging speed is correct": check_charging_speed(df),
            "No overlapping trips": check_overlapping_trips(df)
        }

        for naam, resultaat in checks.items():

            col1, col2 = st.columns([8, 1])

            with col1:
                st.write(naam)

            with col2:
                st.checkbox(
                    "",
                    value=resultaat,
                    disabled=True,
                    key=naam
                )

        # Gantt chart
        gantt_chart_bus(df)

        # Planning
        st.subheader("Ingelezen planning")
        st.dataframe(df.head(10))
    
    
    ########STUKJE VAN MATTHIJS#################


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
