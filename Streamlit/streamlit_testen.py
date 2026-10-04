import streamlit as st

st.markdown("""
<style>

/* Verberg het radio-icoon volledig */
[data-testid="stRadio"] [role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Voor nieuwere Streamlit-versies */
[data-testid="stRadio"] [role="radiogroup"] label [data-testid="stMarkdownContainer"] {
    margin-left: 0 !important;
}

</style>
""", unsafe_allow_html=True)

genre = st.radio(
    "What's your favorite movie genre",
    ["Comedy", "Drama", "Documentary"]
)

st.write("You selected:", genre)