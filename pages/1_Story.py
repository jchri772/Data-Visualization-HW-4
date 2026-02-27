import streamlit as st
import pandas as pd
import altair as alt
from utils.data_utils import load_data, get_daily_standings

st.header("How does team performance differ between the two seasons?")
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

    q1_visuals = alt.vconcat(alt.vconcat(*charts), (total_points_bar | total_gd_bar))
    
    st.altair_chart(q1_visuals, use_container_width=False)

PL_2324_data, PL_2425_data = load_data()
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

render(standings_2324, standings_2425)

st.header("Q2")
def render_q2(standings_2324, standings_2425):
    # --- DATA SETUP ---
    df1 = standings_2324
    df2 = standings_2425
    team_list = sorted(list(set(df1['Team'].unique()) | set(df2['Team'].unique())))

    # --- HEADERS ---
    title_q2 = alt.Chart(pd.DataFrame({'text':['Q2: How consistent is a team’s attacking performance over time within a season?']})
                         ).mark_text(align='left', 
                                     fontSize=30, fontWeight='bold').encode(text='text:N').properties(height=100)

    subtitle_q2 = alt.Chart(pd.DataFrame({'text': ['Directions: Select Attacking Statistic Type At Bottom']})
                         ).mark_text(align='left', 
                                     fontSize=18).encode(text='text:N').properties(height=10)

    header_q2 = (title_q2 & subtitle_q2).properties(spacing=2)

    # --- SELECTIONS (Isolated to Q2) ---
    dropdown_team = alt.binding_select(options=team_list, labels=team_list, name='Select Team: ')
    selection_q2_team = alt.selection_point(fields=['Team'], bind=dropdown_team, value='Arsenal')

    attacking_stats = ['GF','Shots For','Shots on Target','Corners']
    dropdown_stats_type = alt.binding_select(options=attacking_stats, 
                                      labels= attacking_stats, 
                                      name='Select Attacking Stat: ')
    
    selection_attack_stats = alt.param(value='GF', 
                                       bind=dropdown_stats_type, 
                                       name='stat_choice')

    # --- CHART GENERATION ---
    attacking_charts = []
    years = ['2023-2024', '2024-2025']
    for i, df in enumerate((standings_2324, standings_2425)):

            base = alt.Chart(df).transform_filter(
                selection_q2_team).transform_calculate(
                selected_val=f"datum[stat_choice]"
                )

            points = base.mark_point(filled=True, size=50
                                    ).encode(
                x = alt.X('Date:T', title='Date'),
                y = alt.Y('selected_val:Q', title='Selected Attacking Stat'),
                color = alt.Color('Team:N', title = 'Team'),
                tooltip =[ alt.Tooltip('Date:T', title='Date'),
                    alt.Tooltip('Team:N', title='Team'),
                    alt.Tooltip('selected_val:Q', title='Selected Attacking Stat')])

            line = base.transform_window(
                rolling_avg='mean(selected_val)',
                frame=[-30, 0]
                ).mark_line(interpolate='monotone',size = 3).encode(
                    x='Date:T',
                    y=alt.Y('rolling_avg:Q', title='30-Day Rolling Average'),
                    color='Team:N')

            combined = (line + points).add_params(selection_q2_team, selection_attack_stats).properties(
                width=600,
                height=400,
                title=alt.TitleParams(text=alt.ExprRef("stat_choice + ' 30-Day Rolling Average " + years[i] + "'"),
                        fontSize=24))
    
            attacking_charts.append(combined)

    q2_visuals = alt.vconcat(header_q2, alt.hconcat(*attacking_charts))
    st.altair_chart(q2_visuals, use_container_width=False)