import streamlit as st
import pandas as pd
import altair as alt
from utils.data_utils import load_data, get_daily_standings, load_home_away_data
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

st.header("How consistent is a team’s attacking performance over time within a season?")
st.subheader('Directions: Select Attacking Statistic Type At Bottom')
def render_q2(standings_2324, standings_2425):
    df1 = standings_2324
    df2 = standings_2425
    team_list = sorted(list(set(df1['Team'].unique()) | set(df2['Team'].unique())))

    dropdown_team_q2 = alt.binding_select(options=team_list, labels=team_list, name='Select Team (Q2): ')
    selection_q2 = alt.selection_point(fields=['Team'], bind=dropdown_team_q2, value='Arsenal', name='team_sel_q2')

    attacking_stats = ['GF','Shots For','Shots on Target','Corners']
    dropdown_stats_type = alt.binding_select(options=attacking_stats, labels=attacking_stats, name='Select Attacking Stat: ')
    selection_attack_stats = alt.param(value='GF', bind=dropdown_stats_type, name='stat_choice')

    attacking_charts = []
    years = ['2023-2024', '2024-2025']
    for i, df in enumerate((standings_2324, standings_2425)):
        base = alt.Chart(df).transform_filter(
            selection_q2).transform_calculate(
            selected_val=f"datum[stat_choice]")

        points = base.mark_point(filled=True, size=50).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('selected_val:Q', title='Selected Attacking Stat'),
            color=alt.Color('Team:N', title='Team'),
            tooltip=[alt.Tooltip('Date:T'), alt.Tooltip('Team:N'), alt.Tooltip('selected_val:Q')])

        line = base.transform_window(
            rolling_avg='mean(selected_val)',
            frame=[-30, 0]
        ).mark_line(interpolate='monotone', size=3).encode(
            x='Date:T',
            y=alt.Y('rolling_avg:Q'),
            color='Team:N')

        combined = (line + points).add_params(selection_q2, selection_attack_stats).properties(
            width=600, height=400,
            title=alt.TitleParams(text=alt.ExprRef("stat_choice + ' 30-Day Rolling Average " + years[i] + "'"), fontSize=24, anchor='middle'))
        attacking_charts.append(combined)
    
    q2_visuals = alt.vconcat(*attacking_charts)
    
    st.altair_chart(q2_visuals, use_container_width=False)

render_q2(standings_2324, standings_2425)


full_home_away = load_home_away_data()

#Q3 Dropdown
st.header("How does home advantage manifest across teams and seasons (pt. 1)?")
st.subheader('Directions: Select team through dropdown menu')

def render_q3_dropdown(full_home_away):
    team_list = sorted(full_home_away['Team'].unique().tolist())
    
    selection_drop = alt.selection_point(
        fields=['Team'],
        bind=alt.binding_select(options=team_list, labels=team_list, name='Select Team: '),
        value='Arsenal',
        name='team_sel_drop'
    )

    points_home_advantage_by_team = alt.Chart(full_home_away).mark_circle(size=100).encode(
        x=alt.X('CumPts_Home:Q', title='Home Points'),
        y=alt.Y('CumPts_Away:Q', title='Away Points'),
        color=alt.Color('Season:N', title='Season'),
        opacity=alt.condition(selection_drop, alt.value(1), alt.value(0.1)),
        tooltip=[alt.Tooltip('Team:N'), alt.Tooltip('CumPts_Home:Q'), alt.Tooltip('CumPts_Away:Q')]
    ).properties(
        width=600, height=600,
        title=alt.TitleParams(
            text='Linked Home and Away Points By Team and Season',
            fontSize=20, anchor='middle',
            subtitle='Home and away goals charts are linked to selection from prior parts - alternatively click below to select team:')
    ).add_params(selection_drop)

    bar_home = alt.Chart(full_home_away).mark_bar().transform_filter(selection_drop).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Home):Q', title="Home Goals"),
        color='Season:N'
    ).properties(width=280, height=400, title='Home Goals by Season', anchor = 'middle')

    bar_away = alt.Chart(full_home_away).mark_bar().transform_filter(selection_drop).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Away):Q', title="Away Goals"),
        color='Season:N'
    ).properties(width=280, height=400, title='Away Goals by Season', anchor = 'middle')

    st.altair_chart(points_home_advantage_by_team & (bar_home | bar_away), use_container_width=False)

render_q3_dropdown(full_home_away)

#Q3 Brush
st.header("How does home advantage manifest across teams and seasons (pt. 2 - Drag to Populate)?")
st.subheader('Directions: Highlight over area of teams to populate average home and away goals tables below:')

def render_q3_drag(full_home_away):
    brush = alt.selection_interval(encodings=['x', 'y'], name='drag_brush')

    points_home_advantage_drag = alt.Chart(full_home_away).mark_circle(size=100).encode(
        x=alt.X('CumPts_Home:Q', title='Home Points'),
        y=alt.Y('CumPts_Away:Q', title='Away Points'),
        color=alt.Color('Season:N', title='Season'),
        tooltip=[alt.Tooltip('Team:N'), alt.Tooltip('CumPts_Home:Q'), alt.Tooltip('CumPts_Away:Q')]
    ).properties(
        width=600, height=600
    ).add_params(brush)
    
    bar_home_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Home):Q', title="Average Home Goals"),
        color='Season:N'
    ).properties(width=280, height=400, title='Average Home Goals by Season', anchor = 'middle')

    bar_away_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Away):Q', title="Average Away Goals"),
        color='Season:N'
    ).properties(width=280, height=400, title='Average Away Goals by Season', anchor = 'middle')

    st.altair_chart(points_home_advantage_drag & (bar_home_drag | bar_away_drag), use_container_width=False)

render_q3_drag(full_home_away)