import streamlit as st
import base64
from pathlib import path

# Afbeeldingen
data_check_path = Path(__file__).parent / "Data_check_icon.png"
visualisations_path = Path(__file__).parent / "visualisations_icon.png"

# Afbeeldingen omzetten zodat CSS ze kan gebruiken
with open(data_check_path, "rb") as f:
    data_check_icon = base64.b64encode(f.read()).decode()

with open(visualisations_path, "rb") as f:
    visualisations_icon = base64.b64encode(f.read()).decode()


st.markdown("""
<style>

/* Alleen de radio-rondjes verbergen */
[data-testid="stRadioOption"] > div:first-of-type {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)

st.sidebar.markdown("""
<div class="sidebar-title">
    Main Menu
</div>
<div class="sidebar-line"></div>
""", unsafe_allow_html=True)


keuze = st.sidebar.radio(
    "Navigation",
    ["Data Check", "Visualisations"],
    label_visibility="collapsed"
)

st.markdown("""
<style>

/* Alleen de radio-rondjes verbergen */
[data-testid="stRadioOption"] > div:first-of-type {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>

/* ================================
   RADIO BOLLETJES → EIGEN ICONEN
   ================================ */



/* DATA CHECK ICOON */
[data-testid="stSidebar"] [data-testid="stRadio"]
label:nth-of-type(1) [role="radio"] > div:first-child {{
    background-image: url("data:image/png;base64,{data_check_icon}") !important;
}}


/* VISUALISATIONS ICOON */
[data-testid="stSidebar"] [data-testid="stRadio"]
label:nth-of-type(2) [role="radio"] > div:first-child {{
    background-image: url("data:image/png;base64,{visualisations_icon}") !important;
}}

</style>
""", unsafe_allow_html=True)