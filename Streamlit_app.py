import streamlit as st
import pandas as pd

st.title("Mijn app")

st.sidebar.title("Menu")

keuze = st.sidebar.selectbox(
    "Kies een pagina",
    ["Home", "Data", "Resultaten"]
)

if keuze == "Home":
    st.header("Home")
    st.write("Welkom!")
    # Titel
    st.title("Mijn Streamlit App")
    # Gewone tekst
    st.write("Welkom bij mijn app!")
    # Subkopje
    st.subheader("Voer je gegevens in")
    # Tekst invoeren
    naam = st.text_input("Wat is je naam?")
    # Getal invoeren
    leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120)
    # Keuze maken
    keuze = st.selectbox(
        "Kies een optie",
        ["Optie 1", "Optie 2", "Optie 3"]
    )
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

        st.subheader("Ingelezen planning")
        st.dataframe(df.head())

        if st.button("Check planning"):
            st.write("Planning wordt gecontroleerd...")

elif keuze == "Resultaten":
    st.header("Resultaten")
    st.write("Hier komen de resultaten.")