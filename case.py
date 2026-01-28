from functions.read_data import read_gsheet
import streamlit as st
import pandas as pd

########################## Read Data
sheet = st.secrets["sheets"]["url"]
tab1 = st.secrets["sheets"]["tab"]

df = read_gsheet(sheet, tab1)


st.write(df)
