import streamlit as st

st.markdown("""
<style>

/* Verberg alleen het daadwerkelijke radio-icoontje */
[data-testid="stRadioOption"] [data-baseweb="radio"] {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)