import streamlit as st
import base64
from pathlib import Path

# PNG bestanden inladen
data_check_icon = base64.b64encode(
    Path("Data_check_icon.png").read_bytes()
).decode()

visualisations_icon = base64.b64encode(
    Path("visualisations_icon.png").read_bytes()
).decode()


st.markdown(f"""
<style>

/* =========================
   STANDAARD RADIO-BALLETJE
   ========================= */

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


/* =========================
   DATA CHECK
   ========================= */

[data-testid="stRadioOption"]:nth-of-type(1) > div > div:first-child {{
    background-image: url("data:image/png;base64,{data_check_icon}") !important;
}}


/* =========================
   VISUALISATIONS
   ========================= */

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