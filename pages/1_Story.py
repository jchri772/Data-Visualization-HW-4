import streamlit as st
import pandas as pd
import altair as alt


def render(standings_2324, standings_2425):

    df1 = standings_2324
    df2 = standings_2425

    st.header("Q1: How does team performance differ between the two seasons?")

    # ---- Streamlit dropdown ----
    team_list = sorted(set(df1["Team"]) | set(df2["Team"]))
    team = st.selectbox("Select Team:", team_list, index=team_list.index("Arsenal"))

    # ---- Filter dataframes ----
    df1_team = df1[df1["Team"] == team]
    df2_team = df2[df2["Team"] == team]

    # ---- Line charts ----
    titles = ["Premier League Table Bump Chart 23-24", "Premier League Table Bump Chart 24-25"]
    charts = []

    for df, title in zip([df1_team, df2_team], titles):
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Day of the Season"),
            y=alt.Y("Rank:O", title="League Rank", sort="ascending"),
            tooltip=[
                alt.Tooltip("Date:T", title="Match Date"),
                alt.Tooltip("Team:N", title="Team"),
                alt.Tooltip("Rank:O", title="Position"),
                alt.Tooltip("CumPts:Q", title="Total Points"),
            ],
        ).properties(
            width=900,
            height=400,
            title=title
        )

        charts.append(chart)

    bump_charts = alt.vconcat(*charts)

    # ---- Final season comparison bars ----
    df1_final = df1[df1["Date"] == df1["Date"].max()].copy()
    df2_final = df2[df2["Date"] == df2["Date"].max()].copy()

    df1_final["Season"] = "2023/2024"
    df2_final["Season"] = "2024/2025"

    df_by_team_comp = pd.concat([df1_final, df2_final])
    df_by_team_comp = df_by_team_comp[df_by_team_comp["Team"] == team]

    total_points_bar = alt.Chart(df_by_team_comp).mark_bar().encode(
        x=alt.X("Season:N", title="Season"),
        y=alt.Y("CumPts:Q", title="Season Points Total"),
    ).properties(width=300, height=300, title="Total Points By Season")

    total_gd_bar = alt.Chart(df_by_team_comp).mark_bar().encode(
        x=alt.X("Season:N", title="Season"),
        y=alt.Y("CumGD:Q", title="Season Goal Differential"),
    ).properties(width=300, height=300, title="Goal Difference By Season")

    bars = total_points_bar | total_gd_bar

    # ---- Render in Streamlit ----
    st.altair_chart(bump_charts, use_container_width=True)
    st.altair_chart(bars, use_container_width=True)

from utils.data_utils import load_data, get_daily_standings

# 1. Load and process data locally for this page
PL_2324_data, PL_2425_data = load_data()
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

# 2. Call your render function
render(standings_2324, standings_2425)