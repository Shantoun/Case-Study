import pandas as pd



def win_rate_by_month(df, forecast_today):
    tmp = df[df["Stage"].isin(["Closed Won", "Closed Lost"])].copy()
    tmp["Close Date"] = pd.to_datetime(tmp["Close Date"])


    tmp = tmp[tmp["Close Date"] <= pd.to_datetime(forecast_today)]

    tmp["month"] = tmp["Close Date"].dt.to_period("M").dt.to_timestamp()

    out = (
        tmp.groupby(["month", "Stage"])["Stage"]
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values("month")
    )

    out["Closed Won"] = out.get("Closed Won", 0)
    out["Closed Lost"] = out.get("Closed Lost", 0)

    denom = out["Closed Won"] + out["Closed Lost"]
    out["win_rate"] = out["Closed Won"] / denom.where(denom != 0, pd.NA)

    return out
