import streamlit as st
import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials

# scopes = [
#     "https://www.googleapis.com/auth/spreadsheets.readonly",
#     "https://www.googleapis.com/auth/drive.readonly",
# ]

# info = json.loads(st.secrets["gcp_service_account"]["raw_json"])

# creds = Credentials.from_service_account_info(info, scopes=scopes)
# gc = gspread.authorize(creds)


# SHEET_URL = st.secrets["sheets"]["url"]
# SHEET_TAB_NAME = st.secrets["sheets"]["tab"]

# sh = gc.open_by_url(SHEET_URL)
# ws = sh.worksheet(SHEET_TAB_NAME)

# rows = ws.get_all_values()
# df = pd.DataFrame(rows[1:], columns=rows[0])

# st.write(df)




def google_sheet_to_df(sheet_url, tab_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    info = json.loads(st.secrets["gcp_service_account"]["raw_json"])
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)

    sh = gc.open_by_url(sheet_url)
    ws = sh.worksheet(tab_name)

    rows = ws.get_all_values()
    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows[1:], columns=rows[0])





sheet = st.secrets["sheets"]["url"]
tab1 = st.secrets["sheets"]["tab"]

df = google_sheet_to_df(sheet, tab1)


st.write(df)
