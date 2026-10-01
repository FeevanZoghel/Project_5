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
from berekeningen_cleaned import (
    gantt_chart_bus,
    calculate_distances_and_kpis,
    calculate_waiting_time_kpis,
    calculate_energy_consumption_kpis
)

# from testen import status_check

import streamlit as st
import pandas as pd

st.markdown("""
<style>
[class*="st-key-box_"] {
    border: 3px solid #EA3323 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Menu")
# st.write('hello world')


keuze = st.sidebar.selectbox("Kies een pagina", ["Data Check", "Visualisaties"])



if keuze == "Data Check":

    st.title("Transdev Planning Checker")

    bestand1 = st.file_uploader(
        'Upload een busplanning',
        type=['xlsx'],
        accept_multiple_files=False
    )

    bestand2 = st.file_uploader(
        'Upload een timetable',
        type=['xlsx'],
        accept_multiple_files=False
    )

    bestand3 = st.file_uploader(
        'Upload de distance matrix',
        type=['xlsx'],
        accept_multiple_files=False
    )

    # Bestanden apart opslaan
    if bestand1 is not None:
        st.session_state['bp'] = pd.read_excel(bestand1)

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)


    # Alleen uitvoeren als busplanning aanwezig is
    if 'bp' in st.session_state:

        df1 = st.session_state['bp']

        check_all(df1)

        with st.container(border=True, key="box_feasibility"):

            st.subheader("Feasibility checks")

            col1, col2 = st.columns(2)

            # -----------------------------
            # BATTERY & CHARGING
            # -----------------------------
            with col1:

                st.markdown("🔋 **Battery & charging**")

                status_check(
                    "Minimum SOC is maintained (10%)",
                    check_min_SOC(df1)
                )

                status_check(
                    "SOH is correct (between 85% and 95%)",
                    check_SOH(85)
                )

                status_check(
                    "Minimum charging time (15 minutes)",
                    check_min_charging_time(df1)
                )

                status_check(
                    "Charging speed is correct",
                    check_charging_speed(df1)
                )


            # -----------------------------
            # PLANNING
            # -----------------------------
            with col2:

                st.markdown("📍 **Planning**")

                status_check(
                    "Start and end locations match",
                    check_end_begin_loc(df1)
                )

                status_check(
                    "No overlapping trips",
                    check_overlapping_trips(df1)
                )

                status_check(
                    "All required trips",
                    check_req_trips(df1, df2)
                )  

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)
        df2 = st.session_state['tt']

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)
        df3 = st.session_state['dm']


elif keuze == "Visualisaties":

    st.title("Planning results")

    if 'bp' in st.session_state:

        bp = st.session_state['bp']

        col1, col2 = st.columns([3, 8])

        with col1:
            st.subheader("KPIs")

            st.metric("Buses used 🚌", " ")

            st.metric("Total distance ↔️", " km")

            st.metric("Energy consumption 🔋", " kWh")

            st.metric("Average waiting time ⏳", " min")

        with col2:
            st.subheader("Bus planning")

            gantt_chart_bus(bp)