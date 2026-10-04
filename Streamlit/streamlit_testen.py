import streamlit as st

st.markdown(
    """
    <style>
    /* Verberg alleen de standaard radio-cirkels */
    div[role="radiogroup"] div[role="radio"] > div:first-child {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)