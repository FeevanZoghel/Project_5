import streamlit as st

st.markdown("""
<style>

/* Alleen het radio-rondje verbergen, tekst blijft staan */
[data-testid="stRadioOption"] > div > div:first-child {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)