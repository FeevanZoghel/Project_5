#URL:
# https://project5-improvedtool.streamlit.app/

from solver import solve_bus_planning
from io import BytesIO
import time
import textwrap

from DataFrame_check import validate_bus_planning

from pathlib import Path

BASE_DIR = Path(__file__).parent

from feasibility_checks import (
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
    calculate_charging_time_kpis,
    calculate_average_activity_times
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


def load_css(filename, **variables):
    """
    Loads a CSS file and replaces dynamic placeholders with their values.

    Argument:
        filename (str): Name of the CSS file located in the styles directory.
        **variables: Dynamic values to insert into the CSS.

    Returns:
        None: Applies the CSS styling directly to the Streamlit application.
    """
    css_path = base_path / "styles" / filename
    css = css_path.read_text(encoding="utf-8")

    for name, value in variables.items():
        css = css.replace("{{" + name + "}}", str(value))

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def load_html(filename, **variables):
    """
    Loads an HTML template and replaces dynamic placeholders.

    Args:
        filename (str): Name of the HTML file in the templates directory.
        **variables: Dynamic values to insert into the HTML.

    Returns:
        str: HTML content with the placeholders replaced.
    """
    html_path = base_path / "templates" / filename
    html = html_path.read_text(encoding="utf-8")

    for name, value in variables.items():
        html = html.replace("{{" + name + "}}", str(value))

    return html.strip()


load_css(
    "sidebar.css",
    data_check_icon=data_check_icon,
    visualisations_icon=visualisations_icon
)
load_css("main.css")

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


sidebar_html = load_html(
    "sidebar.html",
    bus_sidebar_icon=bus_sidebar_icon,
    energy_sidebar_icon=energy_sidebar_icon,
    bar_chart_sidebar_icon=bar_chart_sidebar_icon
)

st.sidebar.markdown(
    sidebar_html,
    unsafe_allow_html=True
)

load_css("data_check.css")

if keuze == "Data Check":
    st.title("Transdev Planning Checker")
    st.write("Upload the planning files below to validate the schedule and view the feasibility results.")

    def upload_file(label, key):
        uploaded_file = st.file_uploader(
            label,
            type=['xlsx'],
            accept_multiple_files=False,
            key=f"upload_{key}"
        )

        if uploaded_file is not None:
            st.session_state[f"{key}_filename"] = uploaded_file.name

        elif key in st.session_state and f"{key}_filename" in st.session_state:
            st.caption(f"✓ Loaded file: {st.session_state[f'{key}_filename']}")

        return uploaded_file

    bestand1 = upload_file("Upload busplanning", "bp")
    bestand2 = upload_file("Upload timetable", "tt")
    bestand3 = upload_file("Upload distance matrix", "dm")
    
    uploaded_files = {'bp': bestand1, 'tt': bestand2, 'dm': bestand3}

    for key, file in uploaded_files.items():
        if file is not None:
            file_signature = (file.name, file.size, file.getvalue())

            if st.session_state.get(f"{key}_file_signature") != file_signature:
                try:
                    df = pd.read_excel(file)
                    df.columns = df.columns.astype(str).str.strip().str.lower()

                    if key == 'bp':
                        df = df.rename(columns={'unnamed: 5': 'line'})

                    st.session_state[key] = df
                    st.session_state[f"{key}_file_signature"] = file_signature

                    st.session_state.pop("improved_bp", None)
                    st.session_state.pop("improved_soh", None)

                except Exception as e:
                    st.error(f"Could not read {key}: {e}")

    files_ready = all(key in st.session_state for key in ['bp', 'tt', 'dm'])
    data_valid = False

    if files_ready:
        bp = st.session_state['bp']
        tt = st.session_state['tt']
        dm = st.session_state['dm']
        input_errors = []

        if bp.empty:
            input_errors.append("Bus planning is empty.")
        if tt.empty:
            input_errors.append("Timetable is empty.")
        if dm.empty:
            input_errors.append("Distance matrix is empty.")

        required_bp = [
            'start location', 'end location', 'start time', 'end time',
            'activity', 'line', 'energy consumption', 'bus'
        ]
        required_tt = ['line', 'start', 'end']
        required_dm = ['line', 'start', 'end', 'distance_m']

        for name, df, required in [
            ('Bus planning', bp, required_bp),
            ('Timetable', tt, required_tt),
            ('Distance matrix', dm, required_dm)
        ]:
            missing = [col for col in required if col not in df.columns]
            if missing:
                input_errors.append(f"{name}: missing columns: {', '.join(missing)}.")
            if df.columns.duplicated().any():
                input_errors.append(f"{name}: duplicate column names.")

        if not input_errors:
            bus_numbers = pd.to_numeric(bp['bus'], errors='coerce')
            invalid_buses = bus_numbers.isna() | (bus_numbers % 1 != 0) | (bus_numbers <= 0)
            for index in bp.index[invalid_buses]:
                input_errors.append(f"Row {index + 2}: invalid bus number.")

            energy = pd.to_numeric(bp['energy consumption'], errors='coerce')
            for index in bp.index[energy.isna()]:
                input_errors.append(f"Row {index + 2}: invalid energy consumption.")

            for col in ['start location', 'end location', 'activity']:
                invalid = bp[col].isna() | bp[col].astype(str).str.strip().eq('')
                for index in bp.index[invalid]:
                    input_errors.append(f"Row {index + 2}: missing {col}.")

            for name, df in [('Timetable', tt), ('Distance matrix', dm)]:
                for col in ['start', 'end']:
                    invalid = df[col].isna() | df[col].astype(str).str.strip().eq('')
                    for index in df.index[invalid]:
                        input_errors.append(f"{name}, row {index + 2}: missing {col}.")

            invalid_tt_lines = tt['line'].isna()
            for index in tt.index[invalid_tt_lines]:
                input_errors.append(f"Timetable, row {index + 2}: missing line.")

            distances = pd.to_numeric(dm['distance_m'], errors='coerce')
            invalid_distances = distances.isna() | (distances < 0)
            for index in dm.index[invalid_distances]:
                input_errors.append(f"Distance matrix, row {index + 2}: invalid distance.")

        
        if input_errors:
            st.error("The uploaded data contains errors.")
            with st.expander("Click here for details", expanded=True):
                with st.container(height=400):
                    for error in input_errors:
                        st.error(error)
        else:
            validation_bp = bp.copy()
            validation_bp['bus'] = bus_numbers.astype(int)
            validation_bp['energy consumption'] = energy
            data_valid = validate_bus_planning(validation_bp)
            if data_valid:
                st.session_state['bp'] = validation_bp

    col_energy, col_SoH = st.columns([2, 4], vertical_alignment="center")
    with col_energy:
        energy_method = st.selectbox(
            "Select an energy estimation method for material trips",
            ["Mean", "Min", "Max"],
            index=0
        ).lower()
    with col_SoH:
        SoH = st.slider(
            "Select the State of Health (SoH) (%)",
            min_value=0,
            max_value=100,
            value=85,
            step=1
        )

    st.markdown("### Improve bus planning")

    if st.button("Optimize", type="primary", disabled=not data_valid):
        progress_bar = st.progress(0, text="Preparing optimization...")
        start_time = time.monotonic()

        def update_progress(completed, total, phase):
            if phase == "Completed":
                progress_bar.progress(100, text="Optimization completed!")
                return
            if phase == "Returning buses to the garage":
                progress_bar.progress(95, text="95% — Returning buses to the garage...")
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
                text=f"Optimizing bus planning... {percentage}% — {remaining_text}"
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
            improved_bp['bus'] = improved_bp['bus'].astype(int)
            st.session_state["improved_bp"] = improved_bp
            st.session_state["improved_soh"] = SoH
            material_trips = improved_bp[improved_bp["activity"] == "material trip"]
            total_time = time.monotonic() - start_time
            progress_bar.progress(100, text=f"Optimization completed in {total_time:.1f} seconds!")
            st.success("Improved bus planning generated successfully!")
        except Exception as e:
            progress_bar.empty()
            st.error(f"Solver failed: {e}")

    if data_valid and 'improved_bp' in st.session_state:
        export_bp = st.session_state['improved_bp'][[
            'start location', 'end location', 'start time', 'end time',
            'activity', 'line', 'energy consumption', 'bus'
        ]].copy()
        export_bp['bus'] = export_bp['bus'].astype(int)
        for col in ['start time', 'end time']:
            export_bp[col] = pd.to_datetime(export_bp[col], errors='coerce').dt.strftime('%H:%M:%S')
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_bp.to_excel(writer, sheet_name='Improved Planning', index=False)
        st.download_button(
            label="Download improved bus planning",
            data=output.getvalue(),
            file_name="Improved_Bus_Planning.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("### Improved planning feasibility")

        with st.container(border=True, key="box_feasibility"):
            col_title, col_radio, col_logo = st.columns(
                [4.5, 2, 0.5],
                vertical_alignment="center"
            )

            with col_title:
                st.markdown(
                    '<div class="feasibility-title">Feasibility checks</div>',
                    unsafe_allow_html=True
                )


            with col_radio:
                planning_choice = st.radio(
                    "Select bus planning",
                    ["Original planning", "Improved planning"],
                    index = 1,
                    horizontal=True,
                    label_visibility="collapsed",
                    key="feasibility_planning_choice"
                )
            with col_logo:
                st.image("https://www.transdev.com/uploads/2026/09/logo.png", width=80)

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
                validation_df[col] = pd.to_datetime(validation_df[col], errors='coerce').dt.strftime('%H:%M:%S')

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

            with st.container(key="check_cards"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="column-title">🔋 Battery & charging</div>', unsafe_allow_html=True)
                    status_check("Minimum SOC is maintained (10%)", feasibility_results["Minimum SOC"])
                    status_check("SOH is correct (between 85% and 95%)", feasibility_results["SOH"])
                    status_check("Minimum charging time (15 minutes)", feasibility_results["Minimum charging time"])
                    status_check("Charging speed is correct", feasibility_results["Charging speed"])
                with col2:
                    st.markdown('<div class="column-title">📍 Planning</div>', unsafe_allow_html=True)
                    status_check("Start and end locations match", feasibility_results["Location continuity"])
                    status_check("No overlapping trips", feasibility_results["Overlapping trips"])
                    if "Required trips" in feasibility_results:
                        status_check("All required trips", feasibility_results["Required trips"])
                    else:
                        st.info("Upload the timetable to check all required trips.")

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
                        if "Required trips" in feasibility_results and not feasibility_results["Required trips"]:
                            show_required_trip_errors(df1, df2)

elif keuze == "Visualisations":

    st.markdown("""
    <style>

    /* =========================================
       1. MAIN DASHBOARD
    ========================================= */
    .block-container {
        padding-top: 2rem !important;
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

    /* Voorkom dat de Gantt-kolom wordt uitgerekt */
    [data-testid="stColumn"]:has(.st-key-chart_card) {
        align-self: flex-start !important;
        height: auto !important;
    }
    
    /* Gantt-kaart: hoogte aanpassen aan inhoud */
    .st-key-chart_card {
        height: fit-content !important;
        min-height: 0 !important;
        align-self: flex-start !important;
    }

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

    /* ===== KPI AND DIFFERENCE ALIGNMENT ===== */

    /* KPI and Difference values: same font size */
    .st-key-kpi_card .kpi-value,
    .st-key-kpi_difference .kpi-value {
        font-size: 24px !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        overflow-wrap: normal !important;
    }

    /* Keep percentages on one line */
    .st-key-kpi_difference .kpi-value {
        white-space: nowrap !important;
    }
    /* Consistent card heights */
    .st-key-kpi_card .kpi-box,
    .st-key-kpi_difference .kpi-box {
        min-height: 110px !important;
        box-sizing: border-box !important;
    }

    /* Consistent labels */
    .st-key-kpi_card .kpi-label,
    .st-key-kpi_difference .kpi-label {
        min-height: 42px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Avoid oversized spacing between cards */
    .st-key-kpi_card .kpi-box,
    .st-key-kpi_difference .kpi-box {
        margin-bottom: 10px !important;
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
                "Improved planning"
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

        average_activity_times = calculate_average_activity_times(bp)
        average_activity_times = {
            str(activity).strip().lower(): value
            for activity, value in average_activity_times.items()
        }
        average_service_time = average_activity_times.get('service trip', 0)
        average_material_time = average_activity_times.get('material trip', 0)
        average_charging_time = average_activity_times.get('charging', 0)
        average_idle_time = average_activity_times.get('idle', 0)

        total_consumption = calculate_energy_consumption_kpis(bp)


        # Differences between improved and original planning
        has_improved = 'improved_bp' in st.session_state

        def percentage_difference(original, current):
            if pd.isna(original) or pd.isna(current):
                return "N/A"
            if original == 0:
                return "0.0%" if current == 0 else "N/A"
            return f"{((current - original) / original * 100):+.1f}%"

        if has_improved:
            (
                _,
                original_distance,
                original_buses,
                original_material,
                _,
                original_material_km
            ) = calculate_distances_and_kpis(original_bp, dm, tt)

            _, _, original_waiting = calculate_waiting_time_kpis(
                original_bp, original_buses
            )
            _, original_charging = calculate_charging_time_kpis(original_bp)
            original_energy = calculate_energy_consumption_kpis(original_bp)

            original_activity_times = {
                str(activity).strip().lower(): value
                for activity, value in calculate_average_activity_times(original_bp).items()
            }

            (
                _,
                improved_distance,
                improved_buses,
                improved_material,
                _,
                improved_material_km
            ) = calculate_distances_and_kpis(improved_bp, dm, tt)

            _, _, improved_waiting = calculate_waiting_time_kpis(
                improved_bp, improved_buses
            )
            _, improved_charging = calculate_charging_time_kpis(improved_bp)
            improved_energy = calculate_energy_consumption_kpis(improved_bp)

            buses_diff = percentage_difference(original_buses, improved_buses)
            waiting_diff = percentage_difference(original_waiting, improved_waiting)
            material_diff = percentage_difference(original_material, improved_material)
            charging_diff = percentage_difference(original_charging, improved_charging)
            energy_diff = percentage_difference(original_energy, improved_energy)

        # Reusable KPI card
        def show_kpi(label, value, icon=None, difference=None):
            icon_html = (
                f'<img src="data:image/png;base64,{icon}" class="kpi-icon">'
                if icon else ""
            )
            difference_html = (
                f'<span style="font-size:14px;color:#667085;font-weight:500;">'
                f' ({difference})</span>'
                if difference is not None else ""
            )
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">
                    {icon_html}
                    {label}
                </div>
                <div class="kpi-value">
                    {value}{difference_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Main dashboard
        with st.container(key="results_dashboard"):

            col_title, col_logo = st.columns(
                [8, 2], vertical_alignment="center"
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
                st.image(logo_path, use_container_width=True)

            col_kpi, col_chart = st.columns(
                [4, 7],
                gap="medium",
                vertical_alignment="top"
            )

            # ===== MAIN KPIs =====
            with col_kpi:
                with st.container(key="kpi_selection"):
                    if has_improved:
                        col_kpi_values, col_diff = st.columns([2, 2])
                    else:
                        col_kpi_values = st.container()

                    with col_kpi_values:
                        with st.container(key="kpi_card"):
                            st.markdown(
                                '<div class="section-title">KPIs</div>',
                                unsafe_allow_html=True
                            )

                            show_kpi(
                                "Number of buses used",
                                f"{deployed_buses_count}",
                                number_bus_used_icon
                            )
                            show_kpi(
                                "Average waiting time",
                                f"{avg_waiting_time_per_bus:.2f} min/bus",
                                waiting_time_icon
                            )
                            show_kpi(
                                "Material trips",
                                f"{t_material_total} trips",
                                material_icon
                            )
                            show_kpi(
                                "Charging time",
                                f"{total_charging_time_hours:.2f} hours",
                                charging_time_icon
                            )
                            show_kpi(
                                "Energy consumption",
                                f"{total_consumption:.2f} kWh",
                                driving_distance_icon
                            )

                    # ===== MAIN DIFFERENCES =====
                    if has_improved:
                        with col_diff:
                            with st.container(key="kpi_difference"):
                                st.markdown(
                                    '<div class="section-title">Difference</div>',
                                    unsafe_allow_html=True
                                )

                                show_kpi(
                                    "Number of buses used",
                                    buses_diff,
                                    number_bus_used_icon
                                )
                                show_kpi(
                                    "Average waiting time",
                                    waiting_diff,
                                    waiting_time_icon
                                )
                                show_kpi(
                                    "Material trips",
                                    material_diff,
                                    material_icon
                                )
                                show_kpi(
                                    "Charging time",
                                    charging_diff,
                                    charging_time_icon
                                )
                                show_kpi(
                                    "Energy consumption",
                                    energy_diff,
                                    driving_distance_icon
                                )

            # ===== GANTT CHART =====
            with col_chart:
                with st.container(key="chart_card"):

                    with st.container(key="chart_header"):
                        col_chart_title, col_planning = st.columns(
                            [1, 3],
                            vertical_alignment="center"
                        )

                        with col_chart_title:
                            st.markdown(
                                '<div class="chart-header-title">'
                                'Bus planning</div>',
                                unsafe_allow_html=True
                            )

                        with col_planning:
                            if has_improved:
                                st.radio(
                                    "Select bus planning",
                                    ["Original planning", "Improved planning"],
                                    index=1,
                                    horizontal=True,
                                    label_visibility="collapsed",
                                    key="planning_choice"
                                )

                    all_buses = sorted(
                        bp["bus"].dropna().unique().tolist()
                    )

                    selection_key = f"selected_buses_{planning_choice}"

                    if selection_key not in st.session_state:
                        st.session_state[selection_key] = all_buses.copy()

                    st.session_state[selection_key] = [
                        bus for bus in st.session_state[selection_key]
                        if bus in all_buses
                    ]

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
                            "Select buses and click Apply selection "
                            "to display the Gantt chart."
                        )

        # ===== ADDITIONAL KPIs BELOW THE DASHBOARD =====
        # This section is outside results_dashboard and its columns.

        with st.container(key="additional_kpis_section"):
            if "show_more_kpis" not in st.session_state:
                st.session_state["show_more_kpis"] = False

            show_more = st.session_state["show_more_kpis"]

            button_label = (
                "Show fewer KPIs ▲"
                if show_more else "Show more KPIs ▼"
            )

            if st.button(
                button_label,
                key="toggle_more_kpis",
                use_container_width=True
            ):
                st.session_state["show_more_kpis"] = not show_more
                st.rerun()

            if st.session_state["show_more_kpis"]:
                additional_kpis = [
                    (
                        "Average service trip time",
                        average_service_time,
                        "min/trip",
                        waiting_time_icon,
                        "service trip"
                    ),
                    (
                        "Average idle time",
                        average_idle_time,
                        "min/period",
                        waiting_time_icon,
                        "idle"
                    ),
                    (
                        "Material trip distance",
                        d_material_total_km,
                        "km",
                        material_distance_icon,
                        None
                    ),
                    (
                        "Average material trip time",
                        average_material_time,
                        "min/trip",
                        material_icon,
                        "material trip"
                    ),
                    (
                        "Average charging time",
                        average_charging_time,
                        "min/session",
                        charging_time_icon,
                        "charging"
                    ),
                    (
                        "Total driving distance",
                        total_distance_km,
                        "km",
                        energy_consumption_icon,
                        None
                    )
                ]

                with st.container(key="additional_kpis"):
                    st.markdown("""
                    <div style="
                        color: #FFFFFF;
                        font-size: 26px;
                        font-weight: 700;
                        margin-bottom: 15px;
                    ">
                        Additional KPIs
                    </div>
                    """, unsafe_allow_html=True)

                    cols = st.columns(3, gap="medium")

                    for i, (label, value, unit, icon, activity) in enumerate(additional_kpis):
                        difference = None

                        if has_improved:
                            if activity is not None:
                                difference = percentage_difference(
                                    original_activity_times.get(activity, float("nan")),
                                    value
                                )
                            elif label == "Material trip distance":
                                difference = percentage_difference(
                                    original_material_km,
                                    value
                                )
                            elif label == "Total driving distance":
                                difference = percentage_difference(
                                    original_distance,
                                    value
                                )

                        with cols[i % 3]:
                            show_kpi(
                                label,
                                f"{value:.2f} {unit}",
                                icon,
                                difference
                            )

    else:
        st.warning(
            "Upload the bus planning, timetable and distance matrix "
            "on the Data Check page first."
        )
