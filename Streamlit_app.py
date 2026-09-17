import streamlit as st

st.title("Mijn app")

st.sidebar.title("Menu")

keuze = st.sidebar.selectbox(
    "Kies een pagina",
    ["Home", "Data", "Resultaten"]
)

if keuze == "Home":
    st.header("Home")
    st.write("Welkom!")

elif keuze == "Data":
    st.header("Data")
    st.write("Hier komt de data.")

elif keuze == "Resultaten":
    st.header("Resultaten")
    st.write("Hier komen de resultaten.")