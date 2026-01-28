import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes,
)

gc = gspread.authorize(creds)

# open by URL (easiest)
sh = gc.open_by_url(SHEET_URL)

ws = sh.worksheet(SHEET_TAB_NAME)  # or sh.sheet1
rows = ws.get_all_values()

df = pd.DataFrame(rows[1:], columns=rows[0])

st.write(df)
