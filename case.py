from functions.read_data import read_gsheet
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


st.set_page_config(layout="wide")

########################## Read Data
sheet = st.secrets["sheets"]["url"]
tab1 = st.secrets["sheets"]["tab"]

df = read_gsheet(sheet, tab1)


st.write(df)



############################################################ Overview
st.title("Forecasting Model")

st.markdown(
    """
This forecast has **two fundamental layers**:

1. **Visible Pipeline**: opportunities already in-flight in CRM.
2. **Expected Pipeline**: opportunities we *expect to be created* as time goes on.
"""
)






############################################################ Assumptions
with st.expander("Notable assumptions", expanded=False):
    c1, c2 = st.columns([1, 2], vertical_alignment="center")
    with c1:
        forecast_today = st.date_input("Today")
    with c2:
        st.space("medium")
        st.caption(
            "This date anchors everything below (recent windows, pipeline aging, timing logic). "
        )
    
    st.markdown(
        """        
- **Bookings = Closed Won ΔARR** (Closed Lost does not change ARR).   
"""
    )




tab1, tab2, tab3 = st.tabs(["Visible Pipeline", "Expected Pipeline", "Total Forecast"])


############################################################ Visible Pipeline
with tab1:
    st.header("Visible Pipeline")
    
    st.markdown(
        """
    We already have pipeline, so the question is: **how much of it will actually book**
    
    For each open opportunity, we estimate an **Expected Booked ΔARR** using three probability components:
    """
    )
    
    st.latex(
        r"""
        \text{Expected Booked ARR}_{\text{opp}}
        \;=\;
        \text{ARR}_{\text{opp}}
        \times P(\text{win})
        \times P(\text{stage})
        \times P(\text{hygiene})
        """
    )
    
    
    st.markdown(
        """
    Where:
    - **P(win)** = “Does this kind of opp usually close won?” (based on key factors)
    - **P(stage)** = “Given its current stage, what’s the implied chance of winning?”
    - **P(hygiene)** = “Is this opp maintained realistically (or is it stale / messy)?”
    """
    )
    
    
    
    
    
    ############################################################ Other Probabilities
    with st.expander("Other probabilities (what we’d do in a real build)", expanded=False):
        st.markdown(
            """
    In a real forecasting system, we’d go deeper than three hand-built probabilities.
    
    **What I’d do with more time + better data:**
    - Train an **ML classifier** (e.g., Random Forest) using **opportunity history** (stage movement, timing, activity, source, rep behavior, etc.).
    - Output wouldn’t just be a probability, it would be a **classification per opportunity** (likely win/loss) plus **drivers** (why).
    - This matters because opps have tons of interlaced variables: rep, motion, timing, client context, lead source… all interacting.
    
    I’ve built forecasts like that before with **dozens of features**. It’s powerful (I've gotten results up to **96%** accuracy), but for this case study, I’m keeping it simple.
    """
        )
    
        st.divider()
        st.markdown(
            """
    **Timing extension (also real-world):**
    - **Add probability the close date is accurate**.
    - If close dates are often wrong, I'd then model the slippage as a distribution:
      - % that slip 1 month, 2 months, etc.
    - Then **spread forecasted bookings** into future months accordingly.
    """
        )
    
    
    
    
    
    ############################################################ Probability of Closed Won based on Variables

    closed_won_count = (df["Stage"] == "Closed Won").sum()
    closed_lost_count = (df["Stage"] == "Closed Lost").sum()
    
    global_win_rate = closed_won_count / (closed_won_count + closed_lost_count)
    
    st.metric("Global Win Rate", f"{global_win_rate:.1%}")
    st.caption(f"Closed Won: {closed_won_count:,} | Closed Lost: {closed_lost_count:,}")
    
    
    # -------------------------
    # Win rate per month
    # -------------------------
    def win_rate_by_month(df):
        tmp = df[df["Stage"].isin(["Closed Won", "Closed Lost"])].copy()
        tmp["month"] = pd.to_datetime(tmp["Close Date"]).dt.to_period("M").dt.to_timestamp()
    
        g = tmp.groupby(["month", "Stage"], as_index=False).agg(
            opp_count=("Stage", "size"),
            arr_sum=("ARR", "sum"),
        )
    
        c = g.pivot(index="month", columns="Stage", values="opp_count").fillna(0).reset_index()
        a = g.pivot(index="month", columns="Stage", values="arr_sum").fillna(0).reset_index()
    
        out = c.merge(a, on="month", suffixes=("_count", "_arr"))
    
        out["Closed Won_count"] = out.get("Closed Won_count", 0)
        out["Closed Lost_count"] = out.get("Closed Lost_count", 0)
        out["Closed Won_arr"] = out.get("Closed Won_arr", 0.0)
        out["Closed Lost_arr"] = out.get("Closed Lost_arr", 0.0)
    
        denom = out["Closed Won_count"] + out["Closed Lost_count"]
        out["win_rate"] = out["Closed Won_count"] / denom.where(denom != 0, pd.NA)
    
        return out.sort_values("month")
    
    
    def plot_monthly_win_rate_bar(monthly_df, color="#636EFA"):
        fig = go.Figure(
            go.Bar(
                x=monthly_df["month"],
                y=monthly_df["win_rate"],
                marker=dict(color=color),
                hovertemplate=(
                    "<b>%{x|%b %y}</b><br>"
                    "Win rate: %{y:.0%}<br><br>"
                    "Closed Won: %{customdata[0]:,.0f} opps<br>"
                    "Won ARR: $%{customdata[1]:,.0f}<br>"
                    "Closed Lost: %{customdata[2]:,.0f} opps<br>"
                    "Lost ARR: $%{customdata[3]:,.0f}"
                    "<extra></extra>"
                ),
                customdata=monthly_df[
                    ["Closed Won_count", "Closed Won_arr", "Closed Lost_count", "Closed Lost_arr"]
                ].values,
            )
        )
    
        fig.update_layout(
            title="Monthly Win Rate (Closed Outcomes Only)",
            xaxis=dict(title=None, tickformat="%b %y", showgrid=False),
            yaxis=dict(title="Win Rate", tickformat=".0%", range=[0, 1], showgrid=True),
            margin=dict(l=40, r=40, t=60, b=40),
            height=420,
            showlegend=False,
        )
        return fig
    
    

        
    





    
    st.subheader("Probability of Closed Won based on variables")
    
    st.markdown(
        """
    If we just apply one blanket close rate of **{:.1%}** we’ll miss meaningful GTM variation.
    But we also don’t want tiny buckets that lie to us.

    To understand where that variation actually comes from, the chart below shows how the realized close rate has moved over time.
    """.format(global_win_rate)
    )



    # color picker
    monthly_wr = win_rate_by_month(df)
    
    color = st.color_picker("Bar color", "#636EFA")
    st.plotly_chart(plot_monthly_win_rate_bar(monthly_wr, color=color), width="stretch")



    st.markdown(
        """
    
    So the approach is:
    - Use **recent closed opps** (default: **last 12 months**) to reflect current reality
    - Calculate a **baseline win rate**
    - Then test which columns **deviate most** from that baseline
    """
    )
    
    st.markdown("**What we’ll compute (tables coming next):**")
    st.markdown(
        """
    - Baseline win rate (last 12 months)
    - Win rate by:
      - Segment
      - Industry
      - Source / motion (Inbound, XDR, Paid, etc.)
      - Lead type (if applicable)
      - Any other fields that look meaningful + have enough volume
    """
    )
    
    st.caption(
        "Goal: identify the **top 3 drivers** that move win rate the most (without overfitting)."
    )
    
    st.markdown(
        """
    Once we find the top movers, we build a **small win-rate matrix** on those drivers.
    
    **Sparse data fallback (important):**
    - Some combinations will have low counts → unreliable.
    - When counts are low, we **default to the nearest average** (hierarchical fallback):
      - 3-variable slice → 2-variable slice → 1-variable slice → baseline
    """
    )
    
    st.caption(
        "This is basically: use the most specific view that has enough data, otherwise roll up."
    )
    
    st.markdown(
        """
    **Why not regression here?**
    - It’s valid, but it’s not the best fit for this case study:
      - Correlated GTM signals can make coefficients misleading
      - It’s harder to explain and defend quickly
      - We want stable + transparent logic that works even under sparse data
    """
    )
    
    # -------------------------
    # P(stage)
    # -------------------------
    st.subheader("2. Probability based on stage")
    
    st.markdown(
        """
    Stage matters because it encodes progress.
    
    We can map **MaintainX-style stages** to something consistent (Salesforce default-style) and assign a stage factor.
    """
    )
    
    with st.expander("In reality: stage history (better than static stage)", expanded=False):
        st.markdown(
            """
    If we had **stage history**, we’d estimate:
    - Stage-to-stage conversion
    - Time-in-stage patterns
    - Drop-off points
    - Rep-specific / segment-specific stage velocity
    
    That’s more accurate than a static stage multiplier.
    """
        )
    
    # -------------------------
    # P(hygiene)
    # -------------------------
    st.subheader("3. Probability based on hygiene")
    
    st.markdown(
        """
    Pipeline hygiene is underrated but huge.
    
    Examples of low-hygiene opps:
    - Close date is in the past
    - No meaningful activity for a long time
    - Stuck in the same stage forever
    - Missing key fields that normally correlate with deal progress
    
    For these, we apply a conservative weight (example placeholder: **10%** win chance).
    """
    )
    
    # -------------------------
    # Combining
    # -------------------------
    st.subheader("1.5 Combining into a single per-opportunity weight")
    
    st.markdown(
        """
    Once we have **P(win)**, **P(stage)**, and **P(hygiene)**, each opportunity gets a single weight.
    
    Then:
    - **Expected Booked ΔARR (per opp)** = ΔARR × combined probability
    - Aggregate across opps to produce a **bookings forecast curve**
    """
    )
    
    st.markdown("**Outputs we’ll show (tables/plots later):**")
    st.markdown(
        """
    - Opportunity-level table with:
      - ΔARR
      - P(win), P(stage), P(hygiene)
      - Combined probability
      - Expected Booked ΔARR
    - Aggregated forecast by month / quarter
    """
    )











# -------------------------
# Expected Pipeline
# -------------------------
with tab2:
    st.header("Expected Pipeline")
    
    st.markdown(
        """
    Visible pipeline is only part of the story.
    
    Expected pipeline is **what historically tends to show up later**:
    - Renewals / expansions (existing customers)
    - Net-new opportunities that get created over time
    """
    )
    
    st.subheader("2.1 Existing customers: renewals / expansions (expected creation)")
    
    st.markdown(
        """
    This part is more **client-level** than opportunity-level.
    
    The idea:
    - Look at historical cadence (how often customers renew / expand)
    - Estimate **when** they’re likely to generate a new opp
    - Then estimate the **sales cycle** (time-to-close) for that opp
    """
    )
    
    st.markdown("**What we’ll compute (later):**")
    st.markdown(
        """
    - Typical time from:
      - New business → first expansion
      - Expansion → next expansion
      - Renewal cycles (if tracked)
    - Expected ΔARR distributions for these events (simple averages/medians first)
    - Segment / industry splits where volume supports it
    """
    )
    
    st.subheader("2.2 Net-new creation trend")
    
    st.markdown(
        """
    We can also estimate expected pipeline from net-new creation trends.
    
    Simple approach:
    - Look at net-new opp **created volume** over time
    - Assume the trend continues (conservatively)
    - Use the historical **time-to-close** distribution to translate “created” → “booked”
    """
    )
    
    st.caption("If we detect seasonality we’ll allocate by that pattern; otherwise we peanut-butter.")












# -------------------------
# Total
# -------------------------
with tab3:
    st.header("Total Forecast")
    
    st.markdown(
        """
    At the end we combine the two layers:
    
    - **Visible Pipeline forecast** (expected bookings from what exists now)
    - **Expected Pipeline forecast** (expected bookings from pipeline that typically appears later)
    
    Together, this produces a single expected bookings curve.
    
    Next we’ll plug in:
    - the tables
    - the charts
    - the scenario toggles (base / best / worst)
    """
    )
