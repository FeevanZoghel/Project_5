import streamlit as st
import pandas as pd

from DataFrame_check import check_columns
from DataFrame_check import only_check_columns
from DataFrame_check import tijden_check

st.sidebar.primaryColor('blue')

st.title("Mijn app")

st.sidebar.title("Menu")

keuze = st.sidebar.selectbox(
    "Kies een pagina",
    ["Home", "Data", "Resultaten"]
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

        kolommen_correct = only_check_columns(df)

        if kolommen_correct == False:
            if st.button('Click here for details'):
                check_columns(df)

            tijden_check(df)

            st.subheader("Ingelezen planning")
            st.dataframe(df.head(10))

            if st.button("Check planning"):
                st.write("Planning wordt gecontroleerd...")


elif keuze == "Resultaten":
    st.header("Resultaten")
    st.write("Hier komen de resultaten.")