import streamlit as st
import pandas as pd
import altair as alt
from utils.data_utils import load_data, get_daily_standings

def render(standings_2324, standings_2425):
    st.header("Q1: How does team performance differ between the two seasons?")

    # ---- Streamlit dropdown for highlighting ----
    team_list = sorted(set(standings_2324["Team"]) | set(standings_2425["Team"]))
    selected_team = st.selectbox("Select Team to Highlight:", team_list, index=team_list.index("Arsenal"))

    titles = ["Premier League Table Bump Chart 23-24", "Premier League Table Bump Chart 24-25"]
    charts = []

    for df, title in zip([standings_2324, standings_2425], titles):
        # We pass the WHOLE dataframe 'df' so all lines are drawn
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Day of the Season"),
            y=alt.Y("Rank:O", title="League Rank", sort="ascending"),
            color=alt.Color("Team:N", legend=None), # Color by team
            # This is the secret sauce: 
            # If the team matches the dropdown, full opacity. Otherwise, faded.
            opacity=alt.condition(
                alt.datum.Team == selected_team, 
                alt.value(1.0), 
                alt.value(0.15)
            ),
            # Make the selected team's line thicker
            strokeWidth=alt.condition(
                alt.datum.Team == selected_team, 
                alt.value(4), 
                alt.value(1)
            ),
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

    # Bump charts vertically stacked
    st.altair_chart(alt.vconcat(*charts), use_container_width=True)

    # ---- Comparison Bars (Keep these filtered to the specific team) ----
    df1_final = standings_2324[standings_2324["Date"] == standings_2324["Date"].max()].copy()
    df2_final = standings_2425[standings_2425["Date"] == standings_2425["Date"].max()].copy()
    df1_final["Season"], df2_final["Season"] = "2023/2024", "2024/2025"

    df_comp = pd.concat([df1_final, df2_final])
    df_comp = df_comp[df_comp["Team"] == selected_team]

    total_points_bar = alt.Chart(df_comp).mark_bar().encode(
        x=alt.X("Season:N"),
        y=alt.Y("CumPts:Q", title="Total Points"),
        color="Season:N"
    ).properties(width=300, height=300, title="Points Comparison")

    total_gd_bar = alt.Chart(df_comp).mark_bar().encode(
        x=alt.X("Season:N"),
        y=alt.Y("CumGD:Q", title="Goal Differential"),
        color="Season:N"
    ).properties(width=300, height=300, title="GD Comparison")

    st.altair_chart(total_points_bar | total_gd_bar, use_container_width=True)

# --- Execution ---
PL_2324_data, PL_2425_data = load_data()
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

render(standings_2324, standings_2425)