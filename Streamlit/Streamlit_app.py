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
    calculate_energy_consumption_kpis,
    calculate_charging_time_kpis
)

from pathlib import Path
import streamlit as st
import pandas as pd



st.markdown("""
<style>


/* Feasibility buitenvak */
.st-key-box_feasibility {
    background: white !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
    padding: 10px !important;
}

/* Donkere tekst */
.st-key-box_feasibility h1,
.st-key-box_feasibility h2,
.st-key-box_feasibility h3,
.st-key-box_feasibility p,
.st-key-box_feasibility span {
    color: #222 !important;
}

/* Battery + Planning cards */
.st-key-check_cards [data-testid="stColumn"] {
    background: white !important;
    border-top: 5px solid #EA3323 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,.12) !important;
}

.st-key-check_cards [data-testid="stHorizontalBlock"] {
    gap: 28px !important;
}

/* Uploadvak */
[data-testid="stFileUploaderDropzone"] {
    background: #F2F2F2 !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
}

/* Uploadknop */
[data-testid="stFileUploaderDropzone"] button {
    background: white !important;
    color: #222 !important;
    border: 2px solid #EA3323 !important;
    border-radius: 10px !important;
}

/* Tekst uploadvak */
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #555 !important;
}

/* Geüpload bestand: wit */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] div {
    background: white !important;
    color: #222 !important;
}

/* Tekst geüpload bestand */
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] p {
    color: #222 !important;
}

/* Knoppen/icoontjes */
[data-testid="stFileUploader"] button {
    border-color: #EA3323 !important;
}

/* Pagina blijft zwart */
[data-testid="stAppViewContainer"] {
    background: #0E1117 !important;
}


/* Expander / Click here for details wit */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 2px solid #EA3323 !important;
    border-radius: 12px !important;
}

/* Expander tekst donker */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    color: #222222 !important;
}

[data-testid="stAlert"] {
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
}

/* ===== ACHTERGROND HELE PAGINA ===== */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background:
        radial-gradient(
            circle at 85% 10%,
            rgba(234, 51, 35, 0.30) 0%,
            rgba(234, 51, 35, 0.12) 20%,
            transparent 45%
        ),
        linear-gradient(
            135deg,
            #0E1117 0%,
            #1A1D24 55%,
            #090B0F 100%
        ) !important;
    background-attachment: fixed !important;
}
/* Hele expander wit */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* Bovenste balk: "Click here for details" */
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover {
    background-color: #FFFFFF !important;
    color: #222222 !important;
}

/* Tekst + pijltje in header donker */
[data-testid="stExpander"] summary * {
    color: #222222 !important;
    fill: #222222 !important;
}

/* Inhoud ook wit */
[data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
}

/* Titel Feasibility checks */
.st-key-box_feasibility h3 {
    font-size: 50px !important;
    font-weight: 700 !important;
}

.column-title {
    font-size: 20px;
    font-weight: 700;
    color: #222222;
    padding-bottom: 12px;
    margin-bottom: 18px;
    border-bottom: 2px solid #E5E5E5;
    position: relative;
}

.column-title::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 70px;
    height: 3px;
    background: #EA3323;
    border-radius: 3px;
}

.feasibility-title {
    font-size: 34px;
    font-weight: 700;
    color: #222222;
    padding-bottom: 14px;
    margin-bottom: 20px;
    border-bottom: 2px solid #E5E5E5;
    position: relative;
}

.feasibility-title {
    font-size: 34px;
    font-weight: 700;
    color: #222222;
    padding-bottom: 14px;
    margin-bottom: 20px;
    position: relative;
}

/* Lichtgrijze lijn */
.feasibility-title::before {
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    width: 120px; /* ← hiermee maak je de grijze lijn korter/langer */
    height: 2px;
    background: #E5E5E5;
}

/* Rode lijn */
.feasibility-title::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    width: 60px;
    height: 4px;
    background: #EA3323;
    border-radius: 3px;
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

        st.markdown("""
        <style>
        .block-container {
            max-width: 60%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

        df1 = st.session_state['bp']

        check_all(df1)

        with st.container(border=True, key="box_feasibility"):

            col_title, col_logo = st.columns([5, 1], vertical_alignment="center")

            with col_title:
                st.markdown("""
                <div class="feasibility-title">
                    Feasibility checks
                </div>
                """, unsafe_allow_html=True)

            with col_logo:
                st.image(
                    "https://www.transdev.com/uploads/2026/09/logo.png",
                    width=80
                )
            # De echte cards
            with st.container(key="check_cards"):

                col1, col2 = st.columns(2)

                # -----------------------------
                # BATTERY & CHARGING
                # -----------------------------
                with col1:

                    st.markdown("""
                    <div class="column-title">
                        🔋 Battery & charging
                    </div>
                    """, unsafe_allow_html=True)

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

                    st.markdown("""
                    <div class="column-title">
                        📍 Planning
                    </div>
                    """, unsafe_allow_html=True)

                    status_check(
                        "Start and end locations match",
                        check_end_begin_loc(df1)
                    )

                    status_check(
                        "No overlapping trips",
                        check_overlapping_trips(df1)
                    )

                    if "tt" in st.session_state:

                        df2 = st.session_state["tt"]

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

    st.markdown("""
        <style>
        .block-container {
            max-width: 95%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

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
        total_distance_m, total_distance_km, deployed_buses_count, t_material_total, d_material_total = calculate_distances_and_kpis(
            bp, dm, tt
        )

        tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus = calculate_waiting_time_kpis(
            bp, deployed_buses_count            
        )

        total_charging_time_min, total_charging_time_hours = calculate_charging_time_kpis(bp)

        total_consumption = calculate_energy_consumption_kpis(bp)
        col1, col2, col3 = st.columns([5, 4, 9])

        with col1:
            st.subheader("KPIs")

            st.metric("Number of buses used 🚌",deployed_buses_count)

            st.metric('Average waiting time', f'{avg_waiting_time_per_bus:.2f} min/bus')

            st.metric("Material trips 🛠️", f'{t_material_total} trips')

            st.metric('Material trip distance', f'{d_material_total:.3f} km')

        with col2 :

            st.metric('Charging time', f'{total_charging_time_hours:.2f} hours')

            st.metric('Energy consumption', f'{total_consumption:.2f} kWh')

            st.metric("Total driving distance ↔️", f"{total_distance_km:.2f} km")

        with col3:

            st.image(
            "https://www.transdev.com/uploads/2026/09/logo.png",
            width=60
            )

            st.subheader("Bus planning")

            gantt_chart_bus(bp)