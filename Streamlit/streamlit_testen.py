import streamlit as st
import base64
from pathlib import Path

# Map waarin dit Python-bestand staat
base_path = Path(__file__).parent

# PNG bestanden inladen
data_check_icon = base64.b64encode(
    (base_path / "Data_check_icon.png").read_bytes()
).decode()

visualisations_icon = base64.b64encode(
    (base_path / "visualisations_icon.png").read_bytes()
).decode()


st.markdown(f"""
<style>

/* Basis voor de iconen */
[data-testid="stRadioOption"] > div > div:first-child {{
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;

    border: none !important;
    border-radius: 0 !important;

    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}}

/* Data Check icoon */
[data-testid="stRadioOption"]:nth-of-type(1) > div > div:first-child {{
    background-image: url("data:image/png;base64,{data_check_icon}") !important;
}}

/* Visualisations icoon */
[data-testid="stRadioOption"]:nth-of-type(2) > div > div:first-child {{
    background-image: url("data:image/png;base64,{visualisations_icon}") !important;
}}

</style>
""", unsafe_allow_html=True)


keuze = st.radio(
    "Navigation",
    ["Data Check", "Visualisations"]
)

st.write("Je koos:", keuze)