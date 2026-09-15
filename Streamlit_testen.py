import streamlit as st
import pandas as pd

st.title("Mijn eerste app")
st.write("Hallo wereld!")

st.title('Bus planning')
bus_planning = pd.read_excel('Bus Planning.xlsx')
st.write(bus_planning.head(10))

st.title('Distance Matrix')
distance_matrix = pd.read_excel('DistanceMatrix.xlsx')
st.write(distance_matrix.head(10))

st.title('Timetable')
time_table = pd.read_excel('Timetable.xlsx')
st.write(time_table.head(10))

