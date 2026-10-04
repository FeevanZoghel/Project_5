import streamlit as st

st.markdown("""
<style>

/* Alleen het grafische radio-element verbergen */
[data-testid="stRadioOption"] > div:not([data-testid="stMarkdownContainer"]) > div {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)