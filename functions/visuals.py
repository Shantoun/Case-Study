import plotly.graph_objects as go
import pandas as pd



def plot_monthly_win_rate_line(monthly_df, color, reliable_date):
    fig = go.Figure(
        go.Scatter(
            x=monthly_df["month"],
            y=monthly_df["win_rate"],
            mode="lines+markers",
            line=dict(width=3, color=color),
            marker=dict(size=7, color=color),
            customdata=monthly_df[["Closed Won", "Closed Lost"]].values,
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Win rate: %{y:.0%}<br>"
                "Closed Won: %{customdata[0]:,.0f}<br>"
                "Closed Lost: %{customdata[1]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    reliable_date = reliable_date
    if (monthly_df["month"] == reliable_date).any():
        y_jan = monthly_df.loc[
            monthly_df["month"] == reliable_date, "win_rate"
        ].iloc[0]

        fig.add_annotation(
            x=reliable_date,
            y=y_jan,
            text="<b>Reliable from Jan 2024 (enough data points)</b>",
            showarrow=True,
            arrowhead=3,
            ax=0,
            ay=80,
        )

    fig.update_layout(
        title="Monthly Win Rate",
        xaxis=dict(
            title=None,
            tickformat="%b %y",
            showgrid=False,
            fixedrange=True,
        ),
        yaxis=dict(
            title="Win Rate",
            tickformat=".0%",
            range=[0, 1],
            showgrid=True,
            fixedrange=True,
        ),
        dragmode=False,
        margin=dict(l=40, r=40, t=60, b=40),
        height=420,
        showlegend=False,
    )

    return fig
