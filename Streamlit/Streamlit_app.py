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


# Dikkere border van st.container(border=True)
st.markdown("""
<style>
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-width: 3px !important;
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

        with st.container(border=True):
            st.subheader("Feasibility checks")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("🔋 Battery & charging")

                st.checkbox(
                    "Minimum SOC is maintained (10%)",
                    value=check_min_SOC(df1),
                    disabled=True
                )

                st.checkbox(
                    "SOH is correct (between 85% and 95%)",
                    value=check_SOH(85),
                    disabled=True
                )

                st.checkbox(
                    "Minimum charging time (15 minutes)",
                    value=check_min_charging_time(df1),
                    disabled=True
                )

                st.checkbox(
                    "Charging speed is correct",
                    value=check_charging_speed(df1),
                    disabled=True
                )

            with col2:
                st.markdown("📍 Planning")

                st.checkbox(
                    "Start and end locations match",
                    value=check_end_begin_loc(df1),
                    disabled=True
                )

                st.checkbox(
                    "No overlapping trips",
                    value=check_overlapping_trips(df1),
                    disabled=True
                )

                # Deze check heeft OOK de timetable nodig
                if 'tt' in st.session_state:

                    df2 = st.session_state['tt']

                    st.checkbox(
                        "All Required trips",
                        value=check_req_trips(df1, df2),
                        disabled=True
                    )

                else:
                    st.write("Upload the timetable to check all required trips.")

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)
        df2 = st.session_state['tt']

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)
        df3 = st.session_state['dm']
 
    # Planning
    # with st.container(border=True):
    #     st.subheader("Ingelezen planning")
    #     st.write(df.head(10))



    # Gantt chart
    with st.container(border=True):
        st.subheader("Bus planning overview")
        gantt_chart_bus(df)


elif keuze == "Visualisaties":
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
