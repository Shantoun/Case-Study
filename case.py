import streamlit as st
import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

info = json.loads(st.secrets["gcp_service_account"]["raw_json"])

creds = Credentials.from_service_account_info(info, scopes=scopes)
gc = gspread.authorize(creds)

sh = gc.open_by_url(SHEET_URL)
ws = sh.worksheet(SHEET_TAB_NAME)

rows = ws.get_all_values()
df = pd.DataFrame(rows[1:], columns=rows[0])

st.write(df)
