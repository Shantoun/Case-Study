############################################################ Function to Read Google Sheets
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


def read_gsheet(sheet_url, tab_name):
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
