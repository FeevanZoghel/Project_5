#URL:
#https://project5-jmfoec4ruxwpczdw5mf76w.streamlit.app/

from DataFrame_check_nieuw import (
    validate_bus_planning,
    validate_minimum_soc,
    validate_soh,
    validate_location_continuity,
    validate_required_trips,
    validate_minimum_charging_time,
    validate_charging_speed,
    validate_no_overlapping_trips,
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

/* ===== FEASIBILITY ===== */
.st-key-box_feasibility {background:white !important; border:3px solid #EA3323 !important; border-radius:14px !important; padding:10px !important;}

.st-key-box_feasibility h1, .st-key-box_feasibility h2, .st-key-box_feasibility h3, .st-key-box_feasibility p, .st-key-box_feasibility span {color:#222 !important;}

.st-key-check_cards [data-testid="stColumn"] {background:white !important; border-top:5px solid #EA3323 !important; border-radius:12px !important; padding:18px 20px !important; box-shadow:0 4px 14px rgba(0,0,0,.12) !important;}

.st-key-check_cards [data-testid="stHorizontalBlock"] {gap:28px !important;}


/* ===== UPLOAD ===== */
[data-testid="stFileUploaderDropzone"] {background:#F2F2F2 !important; border:3px solid #EA3323 !important; border-radius:14px !important;}

[data-testid="stFileUploaderDropzone"] button {background:white !important; color:#222 !important; border:2px solid #EA3323 !important; border-radius:10px !important;}

[data-testid="stFileUploaderDropzone"] span, [data-testid="stFileUploaderDropzone"] small {color:#555 !important;}

[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFile"] div {background:white !important; color:#222 !important;}

[data-testid="stFileUploaderFile"] span, [data-testid="stFileUploaderFile"] small, [data-testid="stFileUploaderFile"] p {color:#222 !important;}

[data-testid="stFileUploader"] button {border-color:#EA3323 !important;}


/* ===== ACHTERGROND ===== */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {background:radial-gradient(circle at 85% 10%, rgba(234,51,35,.30) 0%, rgba(234,51,35,.12) 20%, transparent 45%), linear-gradient(135deg,#0E1117 0%,#1A1D24 55%,#090B0F 100%) !important; background-attachment:fixed !important;}


/* ===== ERROR + DETAILS ===== */
[data-testid="stAlert"] {border:3px solid #EA3323 !important; border-radius:14px !important;}

[data-testid="stExpander"] {background:white !important; border:3px solid #EA3323 !important; border-radius:14px !important; overflow:hidden !important;}

[data-testid="stExpander"] details, [data-testid="stExpander"] summary, [data-testid="stExpander"] summary:hover, [data-testid="stExpanderDetails"] {background:white !important;}

[data-testid="stExpander"] summary, [data-testid="stExpander"] p, [data-testid="stExpander"] span {color:#222 !important;}

[data-testid="stExpander"] summary * {color:#222 !important; fill:#222 !important;}


/* ===== TITELS ===== */
.st-key-box_feasibility h3 {font-size:50px !important; font-weight:700 !important;}

.column-title {font-size:20px; font-weight:700; color:#222; padding-bottom:12px; margin-bottom:18px; border-bottom:2px solid #E5E5E5; position:relative;}

.column-title::after {content:""; position:absolute; left:0; bottom:-2px; width:70px; height:3px; background:#EA3323; border-radius:3px;}

.feasibility-title {font-size:34px; font-weight:700; color:#222; padding-bottom:14px; margin-bottom:20px;}

/* ===== SIDEBAR ===== */

[data-testid="stSidebar"] {
    width: 225px !important;
    min-width: 225px !important;
    max-width: 225px !important;
    background: linear-gradient(
        180deg,
        #11151C 0%,
        #171C23 55%,
        #0D1117 100%
    ) !important;
}

/* Inhoud sidebar */
[data-testid="stSidebarContent"] {
    padding: 12px 12px !important;
}

/* Menu titel */
.menu-title {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 700;
    margin: 18px 0 14px 0;
}

/* Menu */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 4px;
}

/* Menu-item */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100%;
    min-height: 40px;
    padding: 8px 10px !important;
    margin: 0 !important;
    border-radius: 7px;
    background: transparent;
    cursor: pointer;
    transition: all 0.15s ease;
}

/* Verberg standaard radio button */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none;
}

/* Tekst */
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    display: flex;
    align-items: center;
    color: #AEB3BC !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    margin: 0 !important;
}

/* Icoon algemeen */
[data-testid="stSidebar"] div[role="radiogroup"] label p::before {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    margin-right: 9px;
    font-size: 18px;
    color: #AEB3BC;
}

/* Data Check icoon */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1) p::before {
    content: "☑";
}

/* Visualisations icoon */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2) p::before {
    content: "";
    display: inline-block;
    width: 20px;
    height: 20px;
    margin-right: 9px;

    background-image: url("https://t3.ftcdn.net/jpg/20/16/27/88/360_F_2016278862_3B6pXVB6lUCykBGBi5PnGD3spWBJStgY.webp");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

/* Hover */
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.05);
}

/* Geselecteerde pagina */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(
        90deg,
        #FF2D3D 0%,
        #FF344E 100%
    ) !important;
    box-shadow: 0 3px 8px rgba(255,45,61,0.22);
}

/* Geselecteerde tekst */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 500 !important;
}

/* Geselecteerd icoon */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p::before {
    color: #FFFFFF !important;
}
/* Verberg de echte radio buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
    margin-left: 0 !important;
}

/* Verberg Streamlit radio-cirkel */
[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)




st.sidebar.markdown('<div class="menu-title">Menu</div>', unsafe_allow_html=True)

keuze = st.sidebar.radio(
    "Navigation",
    ["Data Check", "Visualisations"],
    label_visibility="collapsed"
)
if keuze == "☑  Data Check":
    keuze = "Data Check"
else:
    keuze = "Visualisations"




if keuze == "Data Check":


    st.title("Transdev Planning Checker")
    st.write('Upload the planning files below to validate the schedule and view the feasibility results.')

    bestand1 = st.file_uploader(
        'Upload busplanning',
        type=['xlsx'],
        accept_multiple_files=False
    )

    bestand2 = st.file_uploader(
        'Upload timetable',
        type=['xlsx'],
        accept_multiple_files=False
    )

    bestand3 = st.file_uploader(
        'Upload distance matrix',
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

        validate_bus_planning(df1)

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

                with col1:
                    st.markdown("""
                    <div class="column-title">
                        🔋 Battery & charging
                    </div>
                    """, unsafe_allow_html=True)

                    status_check(
                        "Minimum SOC is maintained (10%)",
                        validate_minimum_soc(df1)
                    )

                    status_check(
                        "SOH is correct (between 85% and 95%)",
                        validate_soh(85)
                    )

                    status_check(
                        "Minimum charging time (15 minutes)",
                        validate_minimum_charging_time(df1)
                    )

                    status_check(
                        "Charging speed is correct",
                        validate_charging_speed(df1)
                    )

                with col2:
                    st.markdown("""
                    <div class="column-title">
                        📍 Planning
                    </div>
                    """, unsafe_allow_html=True)

                    status_check(
                        "Start and end locations match",
                        validate_location_continuity(df1)
                    )

                    status_check(
                        "No overlapping trips",
                        validate_no_overlapping_trips(df1)
                    )

                    if "tt" in st.session_state:
                        df2 = st.session_state["tt"]

                        status_check(
                            "All required trips",
                            validate_required_trips(df1, df2)
                        )

                    else:
                        st.info("Upload the timetable to check all required trips.")

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)
        df2 = st.session_state['tt']

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)
        df3 = st.session_state['dm']

elif keuze == "Visualisations":

    st.markdown("""
    <style>

    /* Visualisations page wider */
    .block-container {
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Main white dashboard */
    .st-key-results_dashboard {
        background: white !important;
        border-radius: 14px !important;
        border-top: 7px solid #EA3323 !important;
        padding: 25px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.20) !important;
    }

    /* All text inside dashboard */
    .st-key-results_dashboard h1,
    .st-key-results_dashboard h2,
    .st-key-results_dashboard h3,
    .st-key-results_dashboard p,
    .st-key-results_dashboard span,
    .st-key-results_dashboard label {
        color: #1F1F1F !important;
    }

    /* Subtitle */
    .results-subtitle {
        color: #667085 !important;
        font-size: 17px;
        margin-top: -12px;
        margin-bottom: 22px;
    }

    /* KPI and chart cards */
    .st-key-kpi_card,
    .st-key-chart_card {
        background: #FAFAFA !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08) !important;
    }

    /* Section titles */
    .section-title {
        font-size: 26px;
        font-weight: 700;
        color: #1F1F1F;
        padding-bottom: 12px;
        margin-bottom: 15px;
        border-bottom: 2px solid #E5E5E5;
        position: relative;
    }

    .section-title::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -2px;
        width: 65px;
        height: 4px;
        background: #EA3323;
        border-radius: 3px;
    }

    /* Individual KPI blocks */
    .kpi-box {
        background: #F4F5F7;
        border-left: 5px solid #EA3323;
        border-radius: 9px;
        padding: 10px 14px;
        margin-bottom: 9px;
    }

    .kpi-label {
        font-size: 13px;
        color: #555 !important;
        margin-bottom: 1px;
    }

    .kpi-value {
        font-size: 24px;
        line-height: 1.15;
        font-weight: 700;
        color: #171A21 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    if (
        'bp' in st.session_state
        and 'tt' in st.session_state
        and 'dm' in st.session_state
    ):

        bp = st.session_state['bp']
        tt = st.session_state['tt']
        dm = st.session_state['dm']

        # KPI calculations
        total_distance_m, total_distance_km, deployed_buses_count, t_material_total, d_material_total, d_material_total_km = calculate_distances_and_kpis(
            bp, dm, tt
        )

        tot_waiting_time_min, tot_waiting_time_hours, avg_waiting_time_per_bus = calculate_waiting_time_kpis(
            bp, deployed_buses_count
        )

        total_charging_time_min, total_charging_time_hours = calculate_charging_time_kpis(bp)

        total_consumption = calculate_energy_consumption_kpis(bp)

        # Main dashboard
        with st.container(key="results_dashboard"):

            # Header
            col_title, col_logo = st.columns([8, 2])

            with col_title:
                st.title("Planning results")
                st.markdown(
                    '<div class="results-subtitle">'
                    'Overview of the key performance indicators and the planned bus schedule.'
                    '</div>',
                    unsafe_allow_html=True
                )

            with col_logo:
                st.image(
                    "https://www.transdev.com/uploads/2026/09/logo.png",
                    width=80
                )

            # KPI + Gantt chart
            col_kpi, col_chart = st.columns([2.4, 7.6], gap="medium")

            # -------------------------
            # KPI CARD
            # -------------------------
            with col_kpi:

                with st.container(key="kpi_card"):

                    st.markdown(
                        '<div class="section-title">KPIs</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">🚌 Number of buses used</div>
                        <div class="kpi-value">{deployed_buses_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">🕐 Average waiting time</div>
                        <div class="kpi-value">{avg_waiting_time_per_bus:.2f} min/bus</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">🛠️ Material trips</div>
                        <div class="kpi-value">{t_material_total} trips</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">📍 Material trip distance</div>
                        <div class="kpi-value">{d_material_total_km:.3f} km</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">⚡ Charging time</div>
                        <div class="kpi-value">{total_charging_time_hours:.2f} hours</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">🔋 Energy consumption</div>
                        <div class="kpi-value">{total_consumption:.2f} kWh</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-box">
                        <div class="kpi-label">🛣️ Total driving distance</div>
                        <div class="kpi-value">{total_distance_km:.2f} km</div>
                    </div>
                    """, unsafe_allow_html=True)

            # -------------------------
            # GANTT CHART CARD
            # -------------------------
            with col_chart:

                with st.container(key="chart_card"):

                    st.markdown(
                        '<div class="section-title">Bus planning</div>',
                        unsafe_allow_html=True
                    )

                    gantt_chart_bus(bp)

    else:
        st.warning(
            "Upload the bus planning, timetable and distance matrix on the Data Check page first."
        )