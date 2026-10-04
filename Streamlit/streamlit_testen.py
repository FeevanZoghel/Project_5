import streamlit as st

import streamlit as st

# Custom CSS to hide the radio circles/dots
st.markdown(
    """
    <style>
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    div[role="radiogroup"] label {
        margin-right: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Standard Streamlit radio component
genre = st.radio("What's your favorite movie genre", ["Comedy", "Drama", "Documentary"])

st.write("You selected:", genre)
