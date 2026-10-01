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
    check_overlapping_trips,
    status_check
)
from berekeningen_cleaned import (
    gantt_chart_bus,
    calculate_distances_and_kpis,
    calculate_waiting_time_kpis,
    calculate_energy_consumption_kpis
)


import streamlit as st
import pandas as pd



st.markdown("""
<style>

/* Grote Feasibility container */
.st-key-box_feasibility {
    border: 3px solid #EA3323 !important;
    border-radius: 12px !important;
    background-color: white !important;
}

/* Tekst donker */
.st-key-box_feasibility h1,
.st-key-box_feasibility h2,
.st-key-box_feasibility h3,
.st-key-box_feasibility p,
.st-key-box_feasibility span {
    color: #1F1F1F !important;
}


/* Battery card */
.st-key-box_battery {
    background-color: #F5F6F7 !important;
    border-top: 5px solid #EA3323 !important;
    border-radius: 10px !important;
    padding: 18px !important;
}


/* Planning card */
.st-key-box_planning {
    background-color: #F5F6F7 !important;
    border-top: 5px solid #EA3323 !important;
    border-radius: 10px !important;
    padding: 18px !important;
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

                if 'tt' in st.session_state:

                    df2 = st.session_state['tt']

                    status_check(
                        "All required trips",
                        check_req_trips(df1, df2)
                    )

    else:
        st.info("Upload the timetable to check all required trips.")

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)
        df2 = st.session_state['tt']

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)
        df3 = st.session_state['dm']


elif keuze == "Visualisaties":

    st.title("Planning results")

    if (
    'bp' in st.session_state
    and 'tt' in st.session_state
    and 'dm' in st.session_state
):

        bp = st.session_state['bp']
        tt = st.session_state['tt']
        dm = st.session_state['dm']

        # KPI's berekenen
        total_distance_m, total_distance_km, deployed_buses_count, t_material_total = calculate_distances_and_kpis(
            bp, dm, tt
        )

        tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus = calculate_waiting_time_kpis(
            bp, deployed_buses_count
        )

        total_consumption = calculate_energy_consumption_kpis(bp)
        col1, col2 = st.columns([3, 8])

        with col1:
            st.subheader("KPIs")

            st.metric(
                "Number of buses used 🚌",
                deployed_buses_count
            )

            st.metric('Average waiting time', f'{avg_waiting_time_per_bus:.2f} min/bus')

            st.metric(
                "Material trips 🛠️", f'{t_material_total} trips'
            )

            st.metric('Material trip distance', f'{total_distance_km:.3f} km')

            st.metric('Charging time', f'min')

            st.metric('Energy consumption', f'{total_consumption:.2f} kWh')


            st.metric(
                "Total driving distance ↔️",
                f"{total_distance_km:.2f} km"
            )

        with col2:
            st.subheader("Bus planning")

            gantt_chart_bus(bp)