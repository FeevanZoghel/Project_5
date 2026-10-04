import streamlit as st

st.markdown("""
<style>

/* Verberg uitsluitend het radio-rondje */
[data-testid="stRadioOption"] > div > div {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)