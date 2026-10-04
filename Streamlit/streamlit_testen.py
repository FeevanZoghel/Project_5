import streamlit as st

st.markdown(
    """
    <style>
    [data-testid="stRadio"] [role="radiogroup"] [role="radio"] > div:first-child {
        display: none !important;
    }

    [data-testid="stRadio"] [role="radio"] svg {
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