import streamlit as st

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