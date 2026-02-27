import altair as alt
import pandas as pd
import streamlit as st
from utils.data_utils import load_data, get_daily_standings, load_home_away_data



def render(standings_2324, standings_2425):
    df1 = standings_2324
    df2 = standings_2425

    team_list = sorted(list(set(df1['Team'].unique()) | set(df2['Team'].unique())))
    dropdown = alt.binding_select(options=team_list, labels=team_list, name='Select Team: ')
    
    selection = alt.selection_point(
        fields=['Team'],
        bind=dropdown,
        on='click',
        value='Arsenal')

    charts = []
    titles = ["Premier League Table Bump Chart 23-24", "Premier League Table Bump Chart 24-25"]
    for i, df in enumerate((standings_2324, standings_2425)):
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('Date:T', title='Day of the Season'),
            y=alt.Y('Rank:O', title='League Rank', sort='ascending'),
            color=alt.Color('Team:N', legend=alt.Legend(title='Team')),
            tooltip=[
                alt.Tooltip('Date:T', title='Match Date'),
                alt.Tooltip('Team:N', title='Team'),
                alt.Tooltip('Rank:O', title='Position'),
                alt.Tooltip('CumPts:Q', title='Total Points')
            ],
            opacity=alt.condition(selection, alt.value(1), alt.value(0.25)),
        ).add_params(
            selection
        ).properties(
            width=2000,
            height=500,
            title=titles[i])
        charts.append(chart)

    df1_final = df1[df1['Date'] == df1['Date'].max()].copy()
    df2_final = df2[df2['Date'] == df2['Date'].max()].copy()

    df1_final['Season'] = '2023/2024'
    df2_final['Season'] = '2024/2025'

    df_by_team_comp = pd.concat([df1_final, df2_final])

    total_points_bar = alt.Chart(df_by_team_comp).mark_bar().transform_filter(
        selection).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('CumPts:Q', title="Season Points Total")
    ).properties(width=400, height=400, title='Total Points By Season')

    total_gd_bar = alt.Chart(df_by_team_comp).mark_bar().transform_filter(
        selection).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('CumGD:Q', title="Season Cumulative Goal Differential")
    ).properties(width=400, height=400, title='Goal Difference By Season')

    q1_visuals = alt.vconcat(
        alt.vconcat(*charts).resolve_scale(x='independent'), 
        (total_points_bar | total_gd_bar)
    ).add_params(selection)
    
    return q1_visuals 