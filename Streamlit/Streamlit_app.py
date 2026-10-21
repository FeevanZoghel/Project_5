#URL:
# https://project5-improvedtool.streamlit.app/

from solver import solve_bus_planning
from io import BytesIO
import time
import textwrap

from DataFrame_check import validate_bus_planning

from feasibility_checks import (
    ASSUMED_SOH,
    validate_minimum_soc,
    validate_soh,
    validate_location_continuity,
    validate_required_trips,
    validate_minimum_charging_time,
    validate_charging_speed,
    validate_no_overlapping_trips,
    show_minimum_soc_errors,
    show_location_continuity_errors,
    show_required_trip_errors,
    show_minimum_charging_time_errors,
    show_charging_speed_errors,
    show_overlapping_trip_errors,
    status_check
)

from calculations import (
    calculate_distances_and_kpis,
    calculate_waiting_time_kpis,
    calculate_energy_consumption_kpis,
    calculate_charging_time_kpis
)

from visualisations import gantt_chart_bus

from pathlib import Path
import base64
import streamlit as st
import pandas as pd
base_path = Path(__file__).parent
image_path = base_path / "images"

number_bus_used_path = image_path / "number_bus_used.png"
waiting_time_path = image_path / "waiting_time.png"
material_path = image_path / "Material.png"
material_distance_path = image_path / "material_distance.png"
charging_time_path = image_path / "charging_time.png"
energy_consumption_path = image_path / "energy_consumption.png"
driving_distance_path = image_path / "driving_distance.png"
logo_path = image_path / "Logo_Transdev.png"
bar_chart_sidebar_path = image_path / "Bar_chart_sidebar.png"
bus_sidebar_path = image_path / "Bus_sidebar.png"
energy_sidebar_path = image_path / "energy_sidebar.png"

with open(number_bus_used_path, "rb") as file:
    number_bus_used_icon = base64.b64encode(file.read()).decode()

with open(waiting_time_path, "rb") as file:
    waiting_time_icon = base64.b64encode(file.read()).decode()

with open(material_path, "rb") as file:
    material_icon = base64.b64encode(file.read()).decode()

with open(material_distance_path, "rb") as file:
    material_distance_icon = base64.b64encode(file.read()).decode()

with open(charging_time_path, "rb") as file:
    charging_time_icon = base64.b64encode(file.read()).decode()

with open(energy_consumption_path, "rb") as file:
    energy_consumption_icon = base64.b64encode(file.read()).decode()

with open(driving_distance_path, "rb") as file:
    driving_distance_icon = base64.b64encode(file.read()).decode()

with open(bar_chart_sidebar_path, "rb") as file:
    bar_chart_sidebar_icon = base64.b64encode(file.read()).decode()

with open(bus_sidebar_path, "rb") as file:
    bus_sidebar_icon = base64.b64encode(file.read()).decode()

with open(energy_sidebar_path, "rb") as file:
    energy_sidebar_icon = base64.b64encode(file.read()).decode()

data_check_icon = base64.b64encode(
    (image_path / "data_check_icon.png").read_bytes()
).decode()

visualisations_icon = base64.b64encode(
    (image_path / "visualisations_icon.png").read_bytes()
).decode()

st.markdown(f'''
<style>

    /* JOUW BESTAANDE CSS VOOR DE ICONEN */
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {{
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;

        border: none !important;
        border-radius: 0 !important;

        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
    }}

    /* Stipje verwijderen */
    [data-testid="stSidebar"]
    [data-testid="stRadioOption"] > div > div:first-child > * {{
        display: none !important;
    }}

    /* Data Check icoon */
    [data-testid="stSidebar"]
    [data-testid="stRadioGroup"] > div:nth-child(1)
    [data-testid="stRadioOption"] > div > div:first-child {{
        background-image: url("data:image/png;base64,{data_check_icon}") !important;
    }}

    /* Visualisations icoon */
    [data-testid="stSidebar"]
    [data-testid="stRadioGroup"] > div:nth-child(2)
    [data-testid="stRadioOption"] > div > div:first-child {{
        background-image: url("data:image/png;base64,{visualisations_icon}") !important;
    }}


    /* ========================================
       HIERONDER KOMT DE NIEUWE STYLING
       ======================================== */

    /* Sidebar achtergrond */
    [data-testid="stSidebar"] {{
        background-color: #111820 !important;
    }}

    /* Main Menu */
    [data-testid="stSidebar"] .sidebar-title {{
        color: #F5F5F5 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }}

    /* Lijntje */
    [data-testid="stSidebar"] .sidebar-line {{
        height: 1px !important;
        background-color: #38404A !important;
        margin-bottom: 18px !important;
    }}

    /* Menu-opties */
    [data-testid="stSidebar"] [data-testid="stRadioOption"] {{
        padding: 9px 12px !important;
        border-radius: 6px !important;
        margin-bottom: 5px !important;
    }}

    /* Niet geselecteerde tekst */
    [data-testid="stSidebar"]
    [data-testid="stRadioOption"]
    [data-testid="stMarkdownContainer"] p {{
        color: #AEB4BC !important;
        font-size: 20px !important;
    }}

    /* Geselecteerde rode balk */
    [data-testid="stSidebar"]
    [data-selected="true"] > [data-testid="stRadioOption"] {{
        background-color: #FF2D3F !important;
        border-radius: 6px !important;
    }}

    /* Geselecteerde tekst wit */
    [data-testid="stSidebar"]
    [data-selected="true"] > [data-testid="stRadioOption"]
    [data-testid="stMarkdownContainer"] p {{
        color: white !important;
        font-weight: 600 !important;
    }}
        
    /* ===== ABOUT THIS TOOL ===== */

    .sidebar-about-title {{
        color: #FFFFFF;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 12px;
    }}

    .sidebar-about-description {{
        color: #B7BEC8;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 18px;
    }}

    .sidebar-about-card {{
        background-color: #222B35;
        border: 1px solid #303B47;
        border-radius: 10px;
        padding: 16px;
    }}

    .sidebar-about-item {{
        display: flex;
        align-items: center;
        gap: 12px;
        color: #E5E7EB;
        font-size: 14px;
        padding: 9px 0;
    }}


    .sidebar-about-icon {{
        width: 22px;
        height: 22px;
        object-fit: contain;
        flex-shrink: 0;
    }}


    .sidebar-footer {{
        color: #89939F;
        font-size: 12px;
        text-align: center;
        margin-top: 24px;
    }}

</style>
''', unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-title">
    Menu
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

keuze = st.sidebar.radio(
    "Navigation",
    ["Data Check", "Visualisations"],
    label_visibility="collapsed"
)

st.sidebar.divider()




st.sidebar.markdown(
    f"""
<div class="sidebar-about-title">About this tool</div>

<div class="sidebar-about-description">
A planning optimization dashboard for electric bus operations.
</div>

<div class="sidebar-about-card">
<div class="sidebar-about-item">
<img src="data:image/png;base64,{bus_sidebar_icon}" class="sidebar-about-icon">
<span>Electric bus scheduling</span>
</div>
<div class="sidebar-about-item">
<img src="data:image/png;base64,{energy_sidebar_icon}" class="sidebar-about-icon">
<span>Battery feasibility</span>
</div>
<div class="sidebar-about-item">
<img src="data:image/png;base64,{bar_chart_sidebar_icon}" class="sidebar-about-icon">
<span>Performance analysis</span>
</div>
</div>

<div class="sidebar-footer">
Fontys · Applied Mathematics
</div>
""",
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* ===== FEASIBILITY ===== */
.st-key-box_feasibility {
    background: white !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
    padding: 10px !important;
}

.st-key-box_feasibility h1,
.st-key-box_feasibility h2,
.st-key-box_feasibility h3,
.st-key-box_feasibility p,
.st-key-box_feasibility span {
    color: #222 !important;
}

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


/* ===== UPLOAD ===== */
[data-testid="stFileUploaderDropzone"] {
    background: #F2F2F2 !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: white !important;
    color: #222 !important;
    border: 2px solid #EA3323 !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #555 !important;
}

[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] div {
    background: white !important;
    color: #222 !important;
}

[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] p {
    color: #222 !important;
}

[data-testid="stFileUploader"] button {
    border-color: #EA3323 !important;
}


/* ===== BACKGROUND ===== */
html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background:
        radial-gradient(
            circle at 85% 10%,
            rgba(234,51,35,.30) 0%,
            rgba(234,51,35,.12) 20%,
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


/* ===== ERROR + DETAILS ===== */
[data-testid="stAlert"] {
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] {
    background: white !important;
    border: 3px solid #EA3323 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpanderDetails"] {
    background: white !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    color: #222 !important;
}

[data-testid="stExpander"] summary * {
    color: #222 !important;
    fill: #222 !important;
}


/* ===== TITLES ===== */
.st-key-box_feasibility h3 {
    font-size: 50px !important;
    font-weight: 700 !important;
}

.column-title {
    font-size: 20px;
    font-weight: 700;
    color: #222;
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
    color: #222;
    padding-bottom: 14px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

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

    col_energy, col_SoH = st.columns([2, 4], vertical_alignment="center")

    with col_energy:
        energy_method = st.selectbox(
            "Select an energy estimation method for material trips",
            ["Mean", "Min", "Max"],
            index=0
        )

        energy_method = energy_method.lower()

    with col_SoH:
        SoH = st.slider(
            "Select the State of Health (SoH) (%)",
            min_value=0,
            max_value=100,
            value=85,
            step=5
        )

    st.markdown("### Improve bus planning")

    files_ready = all(
        key in st.session_state for key in ['bp', 'tt', 'dm']
    )

    if st.button("Optimize", type="primary", disabled=not files_ready):

        progress_bar = st.progress(
            0,
            text="Preparing optimization..."
        )

        start_time = time.monotonic()

        def update_progress(completed, total, phase):

            if phase == "Completed":
                progress_bar.progress(
                    100,
                    text="Optimization completed!"
                )
                return

            if phase == "Returning buses to the garage":
                progress_bar.progress(
                    95,
                    text="95% — Returning buses to the garage..."
                )
                return

            percentage = int(95 * completed / max(total, 1))

            elapsed = time.monotonic() - start_time

            if completed > 0:
                remaining = elapsed / completed * (total - completed)
                remaining_text = f"Estimated {remaining:.0f} seconds remaining"
            else:
                remaining_text = "Calculating remaining time..."

            progress_bar.progress(
                percentage,
                text=(
                    f"Optimizing bus planning... {percentage}% "
                    f"— {remaining_text}"
                )
            )

        try:

            improved_bp = solve_bus_planning(
                st.session_state["bp"],
                st.session_state["dm"],
                st.session_state["tt"],
                assumed_battery_value=SoH,
                energy_method=energy_method,
                progress_callback=update_progress
            )

            st.session_state["improved_bp"] = improved_bp
            st.session_state["improved_soh"] = SoH

            material_trips = improved_bp[
                improved_bp["activity"] == "material trip"
            ]

            total_time = time.monotonic() - start_time

            progress_bar.progress(
                100,
                text=f"Optimization completed in {total_time:.1f} seconds!"
            )

            st.success(
                "Improved bus planning generated successfully!"
            )

        except Exception as e:
            progress_bar.empty()
            st.error(f"Solver failed: {e}")

    if 'improved_bp' in st.session_state:

        export_bp = st.session_state['improved_bp'][[
            'start location', 'end location', 'start time', 'end time',
            'activity', 'line', 'energy consumption', 'bus'
        ]].copy()

        export_bp['bus'] = export_bp['bus'].astype(int)

        for col in ['start time', 'end time']:
            export_bp[col] = pd.to_datetime(
                export_bp[col]
            ).dt.strftime('%H:%M:%S')

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_bp.to_excel(
                writer,
                sheet_name='Improved Planning',
                index=False
            )

        st.download_button(
            label="Download improved bus planning",
            data=output.getvalue(),
            file_name="Improved_Bus_Planning.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if 'improved_bp' in st.session_state:

        st.markdown("### Improved planning feasibility")

        st.markdown("""
        <style>
        .block-container {
            max-width: 80%;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .st-key-error_details {
            max-height: 360px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)

        validate_bus_planning(validation_df)
        
        with st.container(border=True, key="box_feasibility"):

            col_title, col_radio, col_logo = st.columns(
                [3, 3, 1],
                vertical_alignment="center"
            )

            with col_title:
                st.markdown("""
                <div class="feasibility-title">
                    Feasibility checks
                </div>
                """, unsafe_allow_html=True)

            with col_radio:
                planning_choice = st.radio(
                    "Select bus planning",
                    ["Original planning", "Improved planning"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="feasibility_planning_choice"
                )

            with col_logo:
                st.image(
                    "https://www.transdev.com/uploads/2026/09/logo.png",
                    width=80
                )

            if planning_choice == 'Original planning':
                df1 = st.session_state['bp']
                check_soh = 85
            else:
                df1 = st.session_state['improved_bp']
                check_soh = st.session_state.get('improved_soh', 85)

            validation_df = df1[[
                'start location', 'end location', 'start time', 'end time',
                'activity', 'line', 'energy consumption', 'bus'
            ]].copy()

            for col in ['start time', 'end time']:
                validation_df[col] = pd.to_datetime(
                    validation_df[col]
                ).dt.strftime('%H:%M:%S')



            # Calculate feasibility results
            feasibility_results = {
                "Minimum SOC": validate_minimum_soc(df1, check_soh),
                "SOH": validate_soh(check_soh),
                "Minimum charging time": validate_minimum_charging_time(df1),
                "Charging speed": validate_charging_speed(df1, check_soh),
                "Location continuity": validate_location_continuity(df1),
                "Overlapping trips": validate_no_overlapping_trips(df1)
            }

            if 'tt' in st.session_state:
                df2 = st.session_state['tt']
                feasibility_results["Required trips"] = validate_required_trips(df1, df2)

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
                        feasibility_results["Minimum SOC"]
                    )

                    status_check(
                        "SOH is correct (between 85% and 95%)",
                        feasibility_results["SOH"]
                    )

                    status_check(
                        "Minimum charging time (15 minutes)",
                        feasibility_results["Minimum charging time"]
                    )

                    status_check(
                        "Charging speed is correct",
                        feasibility_results["Charging speed"]
                    )

                with col2:
                    st.markdown("""
                    <div class="column-title">
                        📍 Planning
                    </div>
                    """, unsafe_allow_html=True)

                    status_check(
                        "Start and end locations match",
                        feasibility_results["Location continuity"]
                    )

                    status_check(
                        "No overlapping trips",
                        feasibility_results["Overlapping trips"]
                    )

                    if "Required trips" in feasibility_results:
                        status_check(
                            "All required trips",
                            feasibility_results["Required trips"]
                        )
                    else:
                        st.info("Upload the timetable to check all required trips.")

            # Feasibility error messages
            if not all(feasibility_results.values()):

                st.error("The bus planning is not feasible.")

                with st.expander("Click here for details"):

                    with st.container(key="error_details"):

                        if not feasibility_results["Minimum SOC"]:
                            show_minimum_soc_errors(df1, check_soh)

                        if not feasibility_results["SOH"]:
                            st.error("SOH must be between 85% and 95%.")

                        if not feasibility_results["Minimum charging time"]:
                            show_minimum_charging_time_errors(df1)

                        if not feasibility_results["Charging speed"]:
                            show_charging_speed_errors(df1, check_soh)

                        if not feasibility_results["Location continuity"]:
                            show_location_continuity_errors(df1)

                        if not feasibility_results["Overlapping trips"]:
                            show_overlapping_trip_errors(df1)

                        if (
                            "Required trips" in feasibility_results
                            and not feasibility_results["Required trips"]
                        ):
                            show_required_trip_errors(df1, df2)

    if bestand2 is not None:
        st.session_state['tt'] = pd.read_excel(bestand2)
        df2 = st.session_state['tt']

    if bestand3 is not None:
        st.session_state['dm'] = pd.read_excel(bestand3)
        df3 = st.session_state['dm']

elif keuze == "Visualisations":


    
    st.markdown("""
    <style>

    /* =========================================
       1. MAIN DASHBOARD
    ========================================= */

    .block-container {
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    .st-key-results_dashboard {
        background: #FFFFFF !important;
        border-radius: 14px !important;
        border-top: 7px solid #EA3323 !important;
        padding: 25px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.20) !important;
    }

    .st-key-results_dashboard h1,
    .st-key-results_dashboard h2,
    .st-key-results_dashboard h3,
    .st-key-results_dashboard p,
    .st-key-results_dashboard span,
    .st-key-results_dashboard label {
        color: #1F1F1F !important;
    }

    .results-subtitle {
        color: #667085 !important;
        font-size: 17px;
        margin-top: -12px;
        margin-bottom: 22px;
    }


    /* =========================================
       2. KPI AND CHART CARDS
    ========================================= */

    .st-key-kpi_card,
    .st-key-chart_card,
    .st-key-kpi_difference {
        background: #FAFAFA !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08) !important;
    }

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

    .kpi-box {
        background: #F4F5F7;
        border-left: 5px solid #EA3323;
        border-radius: 9px;
        padding: 10px 14px;
        margin-bottom: 9px;
    }

    .kpi-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #555555 !important;
        margin-bottom: 1px;
    }

    .kpi-value {
        font-size: 24px;
        line-height: 1.15;
        font-weight: 700;
        color: #171A21 !important;
    }

    .kpi-icon {
        width: 28px;
        height: 28px;
        object-fit: contain;
    }


    /* =========================================
       3. GANTT CHART HEADER
    ========================================= */

    .st-key-chart_header {
        position: relative;
        border-bottom: 2px solid #E5E5E5 !important;
        padding-bottom: 12px !important;
        margin-bottom: 15px !important;
    }

    .st-key-chart_header::after {
        content: "";
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 65px;
        height: 4px;
        background: #EA3323;
        border-radius: 3px;
    }

    .chart-header-title {
        font-size: 26px;
        font-weight: 700;
        color: #1F1F1F;
        white-space: nowrap;
    }

    .st-key-chart_header [data-testid="stHorizontalBlock"] {
        width: 100% !important;
    }


    /* =========================================
       4. PLANNING RADIO BUTTONS
    ========================================= */

    .st-key-planning_choice {
        width: 100% !important;
    }

    .st-key-planning_choice [data-testid="stRadioGroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: flex-end !important;
        width: 100% !important;
        padding-right: 0 !important;
        gap: 20px !important;
    }

    .st-key-chart_header [data-testid="stRadio"] label p {
        font-size: 13px !important;
        color: #222222 !important;
        white-space: nowrap;
    }

    .st-key-chart_card [data-testid="stRadio"] {
        margin: 0 !important;
    }

    .st-key-planning_choice [data-testid="stRadioOption"]
    > div > div:first-child {
        background: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 50% !important;
    }

    .st-key-planning_choice [data-testid="stRadioOption"]:hover
    > div > div:first-child {
        background: #000000 !important;
        border-color: #000000 !important;
    }

    .st-key-planning_choice [data-testid="stRadioOption"][data-selected="true"]
    > div > div:first-child {
        background: #000000 !important;
        border-color: #000000 !important;
    }


    /* =========================================
       5. COMPACT BUS TOOLBAR
    ========================================= */

    .st-key-bus_toolbar {
        background: transparent !important;
        padding: 4px 0 8px 0 !important;
    }

    /* Main selection button */
    .st-key-bus_toolbar [data-testid="stPopover"] button {
        background: #FFFFFF !important;
        color: #222222 !important;
        border: 1px solid #DADDE2 !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }

    .st-key-bus_toolbar [data-testid="stPopover"] button:hover {
        background: #F8F9FA !important;
        border-color: #EA3323 !important;
    }

    .st-key-bus_toolbar [data-testid="stPopover"] button * {
        color: #222222 !important;
    }

    /* Select all and Clear buttons */
    .st-key-bus_toolbar [data-testid="stButton"] button {
        background: #F4F5F7 !important;
        color: #374151 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }

    .st-key-bus_toolbar [data-testid="stButton"] button:hover {
        background: #E9ECEF !important;
        border-color: #CBD5E1 !important;
        color: #222222 !important;
    }


    /* =========================================
       6. POPOVER PANEL
    ========================================= */

    [data-testid="stPopoverBody"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        color: #222222 !important;
    }

    [data-testid="stPopoverBody"] > div,
    [data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }

    [data-testid="stPopoverBody"] p,
    [data-testid="stPopoverBody"] label {
        color: #222222 !important;
    }


    /* =========================================
       7. BUS MULTISELECT - LIGHT GRAY DESIGN
    ========================================= */

    /*
       Actual Streamlit structure:
       stMultiSelect
         > div[data-rac]
           > div[data-rac][role="group"]
             > stMultiSelectTagsContainer
               > selected tags + input
    */

    /* Outer combobox: one light-gray background */
    div[class*="st-key-bus_multiselect_"]
    [data-testid="stMultiSelect"] > div[data-rac] {
        background: #F3F4F6 !important;
        border: 1px solid #DADDE2 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }

    /* Inner group: no extra border */
    div[class*="st-key-bus_multiselect_"]
    [data-testid="stMultiSelect"] > div[data-rac]
    > div[role="group"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Tags container */
    div[class*="st-key-bus_multiselect_"]
    [data-testid="stMultiSelectTagsContainer"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        gap: 5px !important;
        padding: 3px 5px !important;
    }

    /* Remove visual styling from empty input */
    div[class*="st-key-bus_multiselect_"]
    [data-testid="stMultiSelectTagsContainer"] input {
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        border-radius: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;
    }

    /* Focused input */
    div[class*="st-key-bus_multiselect_"]
    [data-testid="stMultiSelectTagsContainer"] input:focus {
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Selected bus chips */
    div[class*="st-key-bus_multiselect_"]
    [data-baseweb="tag"] {
        background: #EA3323 !important;
        border: none !important;
        border-radius: 5px !important;
        margin: 2px !important;
    }

    /* Chip text */
    div[class*="st-key-bus_multiselect_"]
    [data-baseweb="tag"] span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Chip remove icons */
    div[class*="st-key-bus_multiselect_"]
    [data-baseweb="tag"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Clear-all and dropdown buttons */
    div[class*="st-key-bus_multiselect_"]
    [data-rac] button {
        background: transparent !important;
        border: none !important;
        border-radius: 5px !important;
        box-shadow: none !important;
        padding: 4px !important;
    }

    div[class*="st-key-bus_multiselect_"]
    [data-rac] button svg {
        color: #667085 !important;
        fill: #667085 !important;
    }

    div[class*="st-key-bus_multiselect_"]
    [data-rac] button:hover {
        background: #E5E7EB !important;
    }


    /* =========================================
       8. DROPDOWN OPTIONS
    ========================================= */

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [data-baseweb="menu"] > div,
    [role="listbox"] {
        background-color: #FFFFFF !important;
        color: #222222 !important;
    }

    [role="option"] {
        background-color: #FFFFFF !important;
        color: #222222 !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background-color: #F3F4F6 !important;
    }

    [role="option"] * {
        color: #222222 !important;
    }


    /* =========================================
       9. APPLY SELECTION BUTTON
    ========================================= */

    [data-testid="stPopoverBody"]
    [data-testid="stBaseButton-primary"] {
        background: #EA3323 !important;
        color: #FFFFFF !important;
        border: 1px solid #EA3323 !important;
        border-radius: 8px !important;
    }

    [data-testid="stPopoverBody"]
    [data-testid="stBaseButton-primary"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stPopoverBody"]
    [data-testid="stBaseButton-primary"]:hover {
        background: #D92D20 !important;
        border-color: #D92D20 !important;
    }

    </style>
    """, unsafe_allow_html=True)


    # Custom bus icon in compact toolbar
    st.markdown(f"""
    <style>

    .st-key-bus_toolbar [data-testid="stPopover"] button::before {{
        content: "";
        display: inline-block;
        width: 22px;
        height: 22px;
        flex-shrink: 0;

        background-image: url("data:image/png;base64,{bus_sidebar_icon}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;

        margin-right: 8px;
    }}

    </style>
    """, unsafe_allow_html=True)


    if (
        'bp' in st.session_state
        and 'tt' in st.session_state
        and 'dm' in st.session_state
    ):

        original_bp = st.session_state['bp']
        tt = st.session_state['tt']
        dm = st.session_state['dm']

        # Select the planning
        if 'improved_bp' in st.session_state:
            improved_bp = st.session_state['improved_bp']

            planning_choice = st.session_state.get(
                "planning_choice",
                "Original planning"
            )

            if planning_choice == "Improved planning":
                bp = improved_bp
            else:
                bp = original_bp

        else:
            planning_choice = "Original planning"
            bp = original_bp

        # KPIs of the selected planning
        (
            total_distance_m,
            total_distance_km,
            deployed_buses_count,
            t_material_total,
            d_material_total,
            d_material_total_km
        ) = calculate_distances_and_kpis(bp, dm, tt)

        (
            tot_waiting_time_min,
            tot_waiting_time_hours,
            avg_waiting_time_per_bus
        ) = calculate_waiting_time_kpis(
            bp,
            deployed_buses_count
        )

        (
            total_charging_time_min,
            total_charging_time_hours
        ) = calculate_charging_time_kpis(bp)

        total_consumption = calculate_energy_consumption_kpis(bp)

        # Differences between improved and original planning
        if 'improved_bp' in st.session_state:

            (
                _,
                original_distance,
                original_buses,
                original_material,
                _,
                original_material_km
            ) = calculate_distances_and_kpis(original_bp, dm, tt)

            _, _, original_waiting = calculate_waiting_time_kpis(
                original_bp,
                original_buses
            )

            _, original_charging = calculate_charging_time_kpis(
                original_bp
            )

            original_energy = calculate_energy_consumption_kpis(
                original_bp
            )

            (
                _,
                improved_distance,
                improved_buses,
                improved_material,
                _,
                improved_material_km
            ) = calculate_distances_and_kpis(improved_bp, dm, tt)

            _, _, improved_waiting = calculate_waiting_time_kpis(
                improved_bp,
                improved_buses
            )

            _, improved_charging = calculate_charging_time_kpis(
                improved_bp
            )

            improved_energy = calculate_energy_consumption_kpis(
                improved_bp
            )

            buses_diff = original_buses - improved_buses
            buses_diff_perc = 100 - (
                improved_buses / original_buses * 100
            )

            waiting_diff = original_waiting - improved_waiting
            waiting_diff_perc = 100 - (
                improved_waiting / original_waiting * 100
            )

            material_diff = original_material - improved_material
            material_diff_perc = 100 - (
                improved_material / original_material * 100
            )

            material_km_diff = (
                original_material_km - improved_material_km
            )
            material_km_diff_perc = 100 - (
                improved_material_km / original_material_km * 100
            )

            charging_diff = original_charging - improved_charging
            charging_diff_perc = 100 - (
                improved_charging / original_charging * 100
            )

            energy_diff = original_energy - improved_energy
            energy_diff_perc = 100 - (
                improved_energy / original_energy * 100
            )

            distance_diff = original_distance - improved_distance
            distance_diff_perc = 100 - (
                improved_distance / original_distance * 100
            )

        # Main dashboard
        with st.container(key="results_dashboard"):

            # Header
            col_title, col_logo = st.columns(
                [8, 2],
                vertical_alignment="center"
            )

            with col_title:
                st.title("Planning results")
                st.markdown(
                    '<div class="results-subtitle">'
                    'Overview of the key performance indicators '
                    'and the planned bus schedule.'
                    '</div>',
                    unsafe_allow_html=True
                )

            with col_logo:
                st.image(
                    logo_path,
                    use_container_width=True
                )

            # KPI + Gantt chart
            col_kpi, col_chart = st.columns(
                [4, 7],
                gap="medium"
            )

            # KPI CARD
            with col_kpi:

                with st.container(key="kpi_selection"):

                    col_kpi_values, col_diff = st.columns([2, 2])

                    with col_kpi_values:

                        with st.container(key="kpi_card"):

                            st.markdown(
                                '<div class="section-title">KPIs</div>',
                                unsafe_allow_html=True
                            )

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{number_bus_used_icon}" class="kpi-icon">
                                    Number of buses used
                                </div>
                                <div class="kpi-value">{deployed_buses_count}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{waiting_time_icon}" class="kpi-icon">
                                    Average waiting time
                                </div>
                                <div class="kpi-value">{avg_waiting_time_per_bus:.2f} min/bus</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{material_icon}" class="kpi-icon">
                                    Material trips
                                </div>
                                <div class="kpi-value">{t_material_total} trips</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{material_distance_icon}" class="kpi-icon">
                                    Material trip distance
                                </div>
                                <div class="kpi-value">{d_material_total_km:.3f} km</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{charging_time_icon}" class="kpi-icon">
                                    Charging time
                                </div>
                                <div class="kpi-value">{total_charging_time_hours:.2f} hours</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{driving_distance_icon}" class="kpi-icon">
                                    Energy consumption
                                </div>
                                <div class="kpi-value">{total_consumption:.2f} kWh</div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="kpi-box">
                                <div class="kpi-label">
                                    <img src="data:image/png;base64,{energy_consumption_icon}" class="kpi-icon">
                                    Total driving distance
                                </div>
                                <div class="kpi-value">{total_distance_km:.2f} km</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Difference card
                    if 'improved_bp' in st.session_state:

                        with col_diff:

                            with st.container(key="kpi_difference"):

                                st.markdown(
                                    '<div class="section-title">Difference</div>',
                                    unsafe_allow_html=True
                                )

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{number_bus_used_icon}" class="kpi-icon">
                                        Number of buses used
                                    </div>
                                    <div class="kpi-value">+{buses_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{waiting_time_icon}" class="kpi-icon">
                                        Average waiting time
                                    </div>
                                    <div class="kpi-value">{waiting_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{material_icon}" class="kpi-icon">
                                        Material trips
                                    </div>
                                    <div class="kpi-value">+{material_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{material_distance_icon}" class="kpi-icon">
                                        Material trip distance
                                    </div>
                                    <div class="kpi-value">+{material_km_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{charging_time_icon}" class="kpi-icon">
                                        Charging time
                                    </div>
                                    <div class="kpi-value">{charging_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{driving_distance_icon}" class="kpi-icon">
                                        Energy consumption
                                    </div>
                                    <div class="kpi-value">+{energy_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <div class="kpi-box">
                                    <div class="kpi-label">
                                        <img src="data:image/png;base64,{energy_consumption_icon}" class="kpi-icon">
                                        Total driving distance
                                    </div>
                                    <div class="kpi-value">+{distance_diff_perc:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)

            # GANTT CHART
            with col_chart:

                with st.container(key="chart_card"):

                    # Bus planning title + planning selection
                    with st.container(key="chart_header"):

                        col_chart_title, col_planning = st.columns(
                            [1, 3],
                            vertical_alignment="center"
                        )

                        with col_chart_title:
                            st.markdown(
                                '<div class="chart-header-title">Bus planning</div>',
                                unsafe_allow_html=True
                            )

                        with col_planning:
                            if 'improved_bp' in st.session_state:
                                st.radio(
                                    "Select bus planning",
                                    ["Original planning", "Improved planning"],
                                    horizontal=True,
                                    label_visibility="collapsed",
                                    key="planning_choice"
                                )


                    # Bus selection
                    all_buses = sorted(
                        bp["bus"].dropna().unique().tolist()
                    )

                    selection_key = f"selected_buses_{planning_choice}"

                    # Initially display all buses
                    if selection_key not in st.session_state:
                        st.session_state[selection_key] = all_buses.copy()

                    # Keep only valid bus numbers
                    st.session_state[selection_key] = [
                        bus for bus in st.session_state[selection_key]
                        if bus in all_buses
                    ]

                    # Compact toolbar
                    with st.container(key="bus_toolbar"):

                        col_select, col_all, col_clear = st.columns(
                            [5, 1.4, 1.4],
                            gap="small",
                            vertical_alignment="center"
                        )

                        with col_select:
                            with st.popover(
                                f"{len(st.session_state[selection_key])} buses selected",
                                use_container_width=True
                            ):

                                st.markdown("**Select buses to display**")

                                with st.form(key=f"bus_form_{planning_choice}"):

                                    selected_buses = st.multiselect(
                                        "Select buses",
                                        options=all_buses,
                                        default=st.session_state[selection_key],
                                        label_visibility="collapsed",
                                        key=f"bus_multiselect_{planning_choice}"
                                    )

                                    apply_selection = st.form_submit_button(
                                        "Apply selection",
                                        type="primary",
                                        use_container_width=True
                                    )

                                if apply_selection:
                                    st.session_state[selection_key] = selected_buses.copy()
                                    st.rerun()

                        with col_all:
                            if st.button(
                                "Select all",
                                key=f"select_all_{planning_choice}",
                                use_container_width=True
                            ):
                                st.session_state[selection_key] = all_buses.copy()
                                st.rerun()

                        with col_clear:
                            if st.button(
                                "Clear",
                                key=f"clear_buses_{planning_choice}",
                                use_container_width=True
                            ):
                                st.session_state[selection_key] = []
                                st.rerun()

                

                    # Display Gantt chart
                    if st.session_state[selection_key]:

                        chart_title = (
                            "Original bus plan"
                            if planning_choice == "Original planning"
                            else "Improved bus plan"
                        )

                        gantt_chart_bus(
                            bp,
                            title=chart_title,
                            selected_buses=st.session_state[selection_key]
                        )

                    else:
                        st.info(
                            "Select buses and click Apply selection to display the Gantt chart."
                        )
    else:
        st.warning(
            "Upload the bus planning, timetable and distance matrix "
            "on the Data Check page first."
        )
