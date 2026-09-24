#URL:
#https://project5-jmfoec4ruxwpczdw5mf76w.streamlit.app/

from DataFrame_check import check_all

from Berekeningen import bus_energy_check


import streamlit as st
import pandas as pd

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


elif keuze == "Data_check":
    st.header("Data")
    st.write("Hier komt de data.")
    st.title("Transdev Planning Checker")

    bestand = st.file_uploader("Upload een busplanning", type=["xlsx"])

    if bestand is not None:
        df = pd.read_excel(bestand)

        check_all(df)
        tijden_check(df)

        st.subheader("Ingelezen planning")
        st.dataframe(df.head(10))




elif keuze == "Gegevens (KPI)":
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
