#URL:
#https://project5-jmfoec4ruxwpczdw5mf76w.streamlit.app/

import streamlit as st
import pandas as pd

from DataFrame_check import check_columns
from DataFrame_check import times_check
from DataFrame_check import energy_check
from DataFrame_check import only_check_columns
from DataFrame_check import only_times_check
from DataFrame_check import only_energy_check
from DataFrame_check import check_all

from Berekeningen import bus_energy_check


st.sidebar.title("Menu")

keuze = st.sidebar.selectbox(
    "Kies een pagina",
    ["Home", "Data_check", "Gegevens (KPI)"]
)

if keuze == "Home":
    st.header("Home")
    st.write("Welkom!")
    st.title("Mijn Streamlit App")
    st.write("Welkom bij mijn app!")
    st.subheader("Voer je gegevens in")
    naam = st.text_input("Wat is je naam?")
    leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120)
    keuze = st.selectbox(
        "Kies een optie",
        ["Optie 1", "Optie 2", "Optie 3"]
    )
    if keuze == 'Optie 3':
        st.write('Kies niet deze')
    # Checkbox
    akkoord = st.checkbox("Ik ga akkoord")
    # Knop
    if st.button("Versturen"):
        st.write("Hallo", naam)
        st.write("Je bent", leeftijd, "jaar oud.")
        st.write("Je koos:", keuze)
    # DataFrame maken
    df = pd.DataFrame({
        "Naam": ["Jan", "Piet", "Sophie"],
        "Leeftijd": [21, 24, 19]
    })
    # DataFrame laten zien
    st.subheader("Data")
    st.dataframe(df)
    # Alleen eerste rijen
    st.write("Eerste twee rijen:")
    st.dataframe(df.head(2))


elif keuze == "Data":
    st.header("Data")
    st.write("Hier komt de data.")
    st.title("Transdev Planning Checker")

    bestand = st.file_uploader("Upload een busplanning", type=["xlsx"])

    if bestand is not None:
        df = pd.read_excel(bestand)

        check_all(df)

        st.subheader("Ingelezen planning")
        st.dataframe(df.head(10))

        if st.button("Check planning"):
            st.write("Planning wordt gecontroleerd...")


elif keuze == "Gegevens (KPI)":
    bestand = st.file_uploader("Upload een busplanning", type=["xlsx"])

    if bestand is not None:
        df = pd.read_excel(bestand)

        check_all(df)

        st.subheader('Energy consumption from busses:')
        bus_energy_check(df)


