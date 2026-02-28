import streamlit as st
import pandas as pd
import altair as alt
from utils.data_utils import load_data, get_daily_standings, load_home_away_data

PL_2324_data, PL_2425_data = load_data()
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)
full_home_away = load_home_away_data()

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* Target the main container */
    .block-container {
        max-width: 2000px;
        padding-top: 2rem;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Optional: Center your headers and subheaders for a cleaner look */
    h1, h2, h3 {
        text-align: center;
    }
    
    /* Center the chart container itself */
    .stVegaLiteChart {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.header("How does Premier League team performance differ between the two seasons?")
st.write("""
First, we examine the differences in team performance across the two seasons by looking at their league position over time. 
The charts below show the league position of each team across each day (not matchday) for each season and thus also 
shows the actual amount of time that each team spent at each position. The x-axis shows the day of the season, 
while the y-axis identifies the league position that an individual team held at the end of that day.

The charts are interactive, meaning that by clicking on a team, the lines for that team across both teams will be highlighted. 
Alternatively, you can select a team using the dropdown menu below the charts. By selecting a team, you can also see the 
total points and goal differential for that team across both seasons, allowing you to compare how the team's overall 
attacking and defensive performances differed and translated into points.

Teams that only show one bar in those graphs were either relegated after the 2023–2024 season or were promoted 
for the 2024–2025 season.""")

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
            width="container",
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
    
    st.altair_chart(q1_visuals, use_container_width=True)

PL_2324_data, PL_2425_data = load_data()
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

render(standings_2324, standings_2425)

st.write("""From the charts above, we can observe that there is a significant overlap between the performances of individual teams across the two seasons. 
For example, we observe that Arsenal, Manchester City all were in the top 3 at the end of both seasons and were all consistently near the top for the majority of both seasons.  
Similarly, we can observe that numerous teams maintained positions in mid-table positions across both seasons, such as Bourenmouth, Brighton, and Crystal Palace. 

We can also observe that the six teams relegated across both seasons (Burnley, Sheffield United, Luton Town, Southampton, Ipswich Town, and Leicester) all maintained positions near the bottom of the table for near the duration of their respective seasons in which they were relegated. 
We do not observe many teams with significant differences in whole-season performances across both seasons, although there are a few, including Nottingham Forest, which finished the 2023-2024 season in 16th place but finished the 2024-2025 season in 8th place, Everton, which finished the 2023-2024 season in 17th place but finished the 2024-2025 season in 12th place, and Tottenham which finished the 2023-2024 season in 5th placed but finished the 2024-2025 season in 17th place. 
There are not many instances of extreme changes in table position within a seasons outside the first few matches, although the most prominent example of inter-season consistent performance changes appears to be Tottenham in the 2024-2025 season, which maintained spots in the top half of the table for the first half of the season but steadily declined in table position throughout the second half of the season.
Overall, the charts suggest that there is a significant amount of consistency in team performance across both seasons, with most teams maintaining similar positions across both seasons and relative consistency in terms of table position within each season.""")

st.header("How consistent is a team’s attacking performance over time within a season?")
st.subheader('Directions: Select Attacking Statistic Type and Team Below')

st.write("""
In this section, I examine the consistency of teams' attacking performances across the two seasons.
The first chart shows the 30-day rolling average of an attacking performance statistic of a selected team (via the dropdown menu) across the two seasons, while the second chart shows the 30-day rolling average of the selected attackign statistic for that team across the two seasons.
The attacking performance statistic can be selected by using the respective second dropdown menus for each chart, which inclue the following options: goals for (GF), shots taken by the selected team (Shots For), shots taken on target by the selected team (Shots on Target), and the number of corners taken by the selected team (Corners).
The individual points for each match are also plotted on the charts, allowing you to see how each attacking performance statistic fluctuated across games, while the line represents the 30-day rolling average of that statistic, allowing you to see the overall trends in that attacking statistic across the season.
By comparing the two charts, you can observe how the consistency of a team's attacking performance may have changed across both seasons 
             """)


def render_q2_separated(df1, df2):
    team_list = sorted(list(set(df1['Team'].unique()) | set(df2['Team'].unique())))
    dropdown_team = alt.binding_select(options=team_list, labels=team_list, name='Select Team (Q2): ')
    selection_q2 = alt.selection_point(fields=['Team'], bind=dropdown_team, value='Arsenal', name='team_sel_q2')

    attacking_stats = ['GF','Shots For','Shots on Target','Corners']
    dropdown_stats_type = alt.binding_select(options=attacking_stats, labels=attacking_stats, name='Select Attacking Stat: ')
    selection_attack_stats = alt.param(value='GF', bind=dropdown_stats_type, name='stat_choice')

    # 2023-2024 
    df1_sorted = df1[df1['Date'] <= '2024-06-30'].sort_values('Date')
    
    base_1 = alt.Chart(df1_sorted).transform_filter(
        selection_q2
    ).transform_calculate(
        selected_val=f"datum[stat_choice]")

    points_1 = base_1.mark_point(filled=True, size=50
                                ).encode(
            x = alt.X('Date:T', 
                    title='Date'),
            y = alt.Y('selected_val:Q', 
                    title='Selected Attacking Stat'),
            color = alt.Color('Team:N', title = 'Team'),
            tooltip =[ alt.Tooltip('Date:T', title='Date'),
                alt.Tooltip('Team:N', title='Team'),
                alt.Tooltip('selected_val:Q', 
                            title='Selected Attacking Stat')])

    line_1 = base_1.transform_window(
            rolling_avg='mean(selected_val)',
            frame=[-30, 0]
            ).mark_line(interpolate='monotone',size = 3).encode(
                x='Date:T',
                y=alt.Y('rolling_avg:Q', title='30-Day Rolling Average'),
                color='Team:N')

    chart_1 = (line_1 + points_1).add_params(selection_q2, selection_attack_stats).properties(
        width=800, 
        height=700,
        padding={"top": 70}, 
        title=alt.TitleParams(
            text=alt.ExprRef("stat_choice + ' 30-Day Rolling Average 2023-2024'"), 
            fontSize=24,
            anchor='start',
            offset=100))

    #2024-2025
    df2_sorted = df2[df2['Date'] >= '2024-07-01'].sort_values('Date')

    base_2 = alt.Chart(df2_sorted).transform_filter(
        selection_q2
    ).transform_calculate(
        selected_val=f"datum[stat_choice]")

    points_2 = base_2.mark_point(filled=True, size=50
                                ).encode(
            x = alt.X('Date:T', 
                    title='Date'),
            y = alt.Y('selected_val:Q', 
                    title='Selected Attacking Stat'),
            color = alt.Color('Team:N', title = 'Team'),
            tooltip =[ alt.Tooltip('Date:T', title='Date'),
                alt.Tooltip('Team:N', title='Team'),
                alt.Tooltip('selected_val:Q', 
                            title='Selected Attacking Stat')])

    line_2 = base_2.transform_window(
            rolling_avg='mean(selected_val)',
            frame=[-30, 0]
            ).mark_line(interpolate='monotone',size = 3).encode(
                x='Date:T',
                y=alt.Y('rolling_avg:Q', title='30-Day Rolling Average'),
                color='Team:N')

    chart_2 = (line_2 + points_2).add_params(selection_q2, selection_attack_stats).properties(
        width=800, height=700,
        padding={"top": 70}, 
        title=alt.TitleParams(
            text=alt.ExprRef("stat_choice + ' 30-Day Rolling Average 2024-2025'"), 
            fontSize=24,
            anchor='start',
            offset=100)).configure_axis(
        titlePadding=40)
    

    st.altair_chart(chart_1, use_container_width=True)
    st.write("---") 
    st.altair_chart(chart_2, use_container_width=True)

render_q2_separated(standings_2324, standings_2425)

st.write("""
By examining the charts above, we can observe that many of the observations about teams' table positions made in the first section also hold for their attacking performance consistency.
For example, we can see that Arsenal, Manchester City, and Liverpool, all had relatively strong attacking performances across both seasons, as all three teams rarely had their 30-day rolling average of goals drop below 2.0 goals per game, while the average shots per game for each team rarely went below 18 for all three teams across both seasons, which is significantly greater than the league average.
We can also observe that changes in these attacking statistics often have material changes on league position, although changes in goals for expectadely appear to have the greatest affect on league position.
For example, near the end of the 2023-2024 season (Februaury through April 2024), Arsenal had a nearly 100 percent increase in their 30-day rolling average of goals for (from 2 to 4 goals per game), which coincided with a rise in league position from fourth in January to first in March.
However, this substantial increase in goals for was not entirely matched by a significant increase in shots for, which during that timeframe only increased on average from 19 to 20, and shots on target for, which during that time rose on average from 5.5 to 7.5 per game.
The larger incrase in goals per game being correlated more with an increase in goals on target per game illustrates that an increase in the quality of chances created (proxied by shots on target) may have been more influential in Arsenal's rise to the top of the table than an increase in the quantity of chances created (which shots for can be a proxy for). 
Arsenal's 2023-2024 rise late in the season also did not appear to be positively correlated with corner kicks, as Arsenal actually had a decrease in corners per game during that time, suggesting that an increase in corner kicks is not always correlated with an increase in chances or points.
Since the increase in goals for was also not entirely explained by an increase in shots on target, since the increase in goals for led to a substantial increase in the standings for Arsenal during this time, this also suggests that shot efficiency plays an important role, if not a more important role, in determining a team's performance than merely the quality and quantity of chances created.
         
Other teams' attacking performances also appear to match with their trends in league position.
For example, Tottenham's decline in league position during the 2024-2025 season appears to be correlated with a decline in their attacking performance, as their steady decline in league position throughout the season was matched by steady declines in goals for, shots for, shots on target for, and corners for. 
However, not all changes in league performance appear to be entirely explained by changes in attacking performance.
For example, Nottingham Forest's dramatic rise from 16th place in the 2023-2024 season to 8th place in the 2024-2025 season does not appear to be entirely explained by an increase in attacking performance, as their 30-day rolling average for goals for, shots for, and shots on target for were all only moderately better (about 10-20 percent better on average) in the 2024-2025 season than in their 2023-2024 season.
""")


full_home_away = load_home_away_data()



#Q3 Dropdown
st.header("How does home advantage manifest across teams and seasons (pt. 1)?")

st.write("""
Next, I examine how home advantage manifests itself across teams in both seasons. 
The first chart below shows the cumulative points earned at home and away for each team across both seasons, wiht the x-axis showing the cumulative points earned at home, the y-axis showing the cumulattive points earned away, and the color the points showing which season the points were earned in.
Thus, teams in the Premier League in both seasons will have two points on the chart, on for each season.
By selecting a team in the dropdown menu, you can see that team's points for both seasons highlighted on the chart, allowing you to compare how a team's home and away forms differed across both seasons.
Below the scatterplot are two bar charts that show the average home and away goals per season for the selected team, allowing you to gain another perspective of the data on how a team's home and away forms differed.
""")

st.subheader('Directions: Select team through dropdown menu')

def render_q3_dropdown(full_home_away):
    team_list = sorted(full_home_away['Team'].unique().tolist())
    
    selection_drop = alt.selection_point(
        fields=['Team'],
        bind=alt.binding_select(options=team_list, labels=team_list, name='Select Team: '),
        value='Arsenal',
        name='selection_drop' 
    )

    points_home_advantage_by_team = alt.Chart(full_home_away).mark_circle(size=100).encode(
        x=alt.X('CumPts_Home:Q', title='Home Points'),
        y=alt.Y('CumPts_Away:Q', title='Away Points'),
        color=alt.Color('Season:N', title='Season'),
        opacity=alt.condition(selection_drop, alt.value(1), alt.value(0.3)),
        tooltip=[alt.Tooltip('Team:N'), alt.Tooltip('CumPts_Home:Q'), alt.Tooltip('CumPts_Away:Q')]
    ).properties(
        width=900, height=800,
        title=alt.TitleParams(
            text='Linked Home and Away Points By Team and Season',
            fontSize=20, anchor='middle',
            subtitle='Use dropdown below to select team:')
    ).add_params(selection_drop)

    bar_home = alt.Chart(full_home_away).mark_bar().transform_filter(selection_drop).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Home):Q', title="Average Home Goals"),
        color='Season:N'
    ).properties(width=400, height=400, title='Average Home Goals by Season')

    bar_away = alt.Chart(full_home_away).mark_bar().transform_filter(selection_drop).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Away):Q', title="Average Away Goals"),
        color='Season:N'
    ).properties(width=400, height=400, title='Average Away Goals by Season')

    st.altair_chart(points_home_advantage_by_team & (bar_home | bar_away), use_container_width=True)

render_q3_dropdown(full_home_away)

st.write("""
From the charts above, we can first observe that the number of home points earned in a season is strongly correlated with the number of away points earned in a season, while the number of home goals scored in a season is also strongly correlated with the number of away goals scored in a season.
Additionally, while not true for all teams, most gained more points at home than away and score more goals at home than away, which is consistent with the commonly held belief of home advantage in football.
The scale of home advantage however appears to differ across teams. 
While the points and goals difference is existent but not particularly large for most teams, some teams have a larger home advantage, such as Newcastle in the 2023-2024 season, which collected 40 points at home and scored 50 goals at home but only collected 20 points away and scored only a bit more than 35 goals. 
Additionally, in the 2023-2024 season, Liverpool had a much stronger home than away form, collecting 48 points and scoring also nearly 50 goals at home but only 34 points and scoring 37 goals away from home.         

However, there are some teams that appear to have had better away forms than home forms across the seasons.
For example, two teams in their respective relegation seasons, Burnley in 2023-2024 and Ipswich in 2024-2025, both had stronger away than home records, with Burnley taking 14 points away and 10 at home and Ipswich taking 15 points away but only 7 points at home.
""")


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
        width=900, height=800
    ).add_params(brush)
    
    bar_home_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Home):Q', title="Average Home Goals"),
        color='Season:N'
    ).properties(width=400, height=400, title='Average Home Goals by Season')

    bar_away_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush).encode(
        x=alt.X('Season:N', title="Season"),
        y=alt.Y('mean(CumGF_Away):Q', title="Average Away Goals"),
        color='Season:N'
    ).properties(width=400, height=400, title='Average Away Goals by Season')

    st.altair_chart(points_home_advantage_drag & (bar_home_drag | bar_away_drag), use_container_width=True)

render_q3_drag(full_home_away)