import pandas as pd
import altair as alt
import warnings

def create_pl_dashboard(standings_2324, standings_2425, full_home_away):
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ########### Q1 ###########
    df1 = standings_2324
    df2 = standings_2425

    header_q1 = alt.Chart(pd.DataFrame({'text':
                                        ['Q1: How does team performance differ between the two seasons?']})
                         ).mark_text(align='left',
        fontSize=30,
        fontWeight='bold',).encode(text='text:N').properties(
        height=100)

    team_list = sorted(list(set(df1['Team'].unique()) | set(df2['Team'].unique())))
    dropdown = alt.binding_select(options=team_list, 
                                      labels= team_list, 
                                      name='Select Team: ')
        
    selection = alt.selection_point(
        fields=['Team'],
        bind=dropdown,
        on='click',
        value='Arsenal')

    charts = []
    titles = ["Premier League Table Bump Chart 23-24", "Premier League Table Bump Chart 24-25"]
    for i, df in enumerate((standings_2324, standings_2425)):
            chart = alt.Chart(df).mark_line(point=True).encode(
                x= alt.X('Date:T',title = 'Day of the Season'),
                y = alt.Y('Rank:O', 
                          title = 'League Rank',
                          sort = 'ascending'),
                color = alt.Color('Team:N', legend = alt.Legend(title = 'Team')),
                tooltip=[alt.Tooltip('Date:T', title='Match Date'),
                    alt.Tooltip('Team:N', title='Team'),
                    alt.Tooltip('Rank:O', title='Position'),
                    alt.Tooltip('CumPts:Q', title='Total Points')],
                opacity=alt.condition(selection, alt.value(1), alt.value(0.25)),
            ).add_params( 
                selection
            ).properties(
                width=800, # Adjusted width for better web display
                height=500,
                title=titles[i])
            charts.append(chart)

    df1_final = df1[df1['Date'] == df1['Date'].max()].copy()
    df2_final = df2[df2['Date'] == df2['Date'].max()].copy()

    df1_final['Season'] = '2023/2024'
    df2_final['Season'] = '2024/2025'

    df_by_team_comp = pd.concat([df1_final, df2_final])

    #Season Points Total
    total_points_bar = alt.Chart(df_by_team_comp).mark_bar().transform_filter(
            selection).encode(
            x=alt.X('Season:N', 
                    title="Season"),
            y=alt.Y('CumPts:Q', 
                title="Season Points Total")).properties(width=400, height=400, title = 'Total Points By Season')

    #Season Goal Differential
    total_gd_bar = alt.Chart(df_by_team_comp).mark_bar().transform_filter(
            selection).encode(
            x=alt.X('Season:N', 
                    title="Season"),
            y=alt.Y('CumGD:Q', 
                title="Season Cumulative Goal Differential")).properties(width=400, height=400, title = 'Goal Difference By Season')


    q1_visuals = alt.vconcat(header_q1, alt.vconcat(*charts), (total_points_bar | total_gd_bar))

    ########### Q2 ###########

    title_q2 = alt.Chart(pd.DataFrame({'text':['Q2: How consistent is a team’s attacking performance over time within a season?']})
                         ).mark_text(align='left', 
                                     fontSize=30, fontWeight='bold').encode(text='text:N').properties(height=100)

    subtitle_q2 = alt.Chart(pd.DataFrame({'text': ['Directions: Select Attacking Statistic Type At Bottom']})
                         ).mark_text(align='left', 
                                     fontSize=18).encode(text='text:N').properties(height=10)

    header_q2 = (title_q2 & subtitle_q2).properties(spacing=2)

    attacking_stats = ['GF','Shots For','Shots on Target','Corners']
    dropdown_stats_type = alt.binding_select(options=attacking_stats, 
                                      labels= attacking_stats, 
                                      name='Select Attacking Stat: ')
        
    selection_attack_stats = alt.param(value='GF', 
                                               bind=dropdown_stats_type, 
                                               name='stat_choice')

    attacking_charts = []
    years = ['2023-2024', '2024-2025']
    for i, df in enumerate((standings_2324, standings_2425)):

            base = alt.Chart(df).transform_filter(
                selection).transform_calculate(
                selected_val=f"datum[stat_choice]"
                )

            points = base.mark_point(filled=True, size=50
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

            line = base.transform_window(
                rolling_avg='mean(selected_val)',
                frame=[-30, 0]
                ).mark_line(interpolate='monotone',size = 3).encode(
                    x='Date:T',
                    y=alt.Y('rolling_avg:Q', title='30-Day Rolling Average'),
                    color='Team:N')

            combined = (line + points).properties(
                width=600,
                height=400,
                title=alt.TitleParams(text=alt.ExprRef("stat_choice + ' 30-Day Rolling Average " + years[i] + "'"),
                        fontSize=24))
        
            attacking_charts.append(combined)


    ########### Q3 ###########

    header_q3 = alt.Chart(pd.DataFrame({'text':
                                        ['Q3: How does home advantage manifest across teams and seasons?']})
                         ).mark_text(align='left',
        fontSize=30,
        fontWeight='bold',).encode(text='text:N').properties(
        height=100)

    points_home_advantage_by_team = alt.Chart(full_home_away).mark_circle(size = 100).encode(
        x = alt.X('CumPts_Home:Q', 
                        title='Home Points'),
        y = alt.Y('CumPts_Away:Q', 
                        title='Away Points'),
        color = alt.Color('Season:N', title = 'Season'),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        tooltip =[alt.Tooltip('Team:N', title='Team'),
                  alt.Tooltip('CumPts_Home:Q', title='Home Points'),
                  alt.Tooltip('CumPts_Away:Q', title='Away Points'),
                  alt.Tooltip('Rank_Home:N', title='Home Rank'),
                  alt.Tooltip('Rank_Away:N', title='Away Rank'), 
                  alt.Tooltip('Season:N', title='Season')]
        ).properties(width=600,
                height=600,
                title=alt.TitleParams(text='Linked Home and Away Points By Team and Season',
                        fontSize=20,       
                        anchor='middle', 
                        subtitle = 'Home and away goals charts are linked to selection from prior parts - alternatively click below to select team:')
                    ).add_params(selection)

    bar_chart_home_goals_by_team = alt.Chart(full_home_away).mark_bar().transform_filter(selection 
        ).encode(
            x=alt.X('Season:N', title="Season"),
            y=alt.Y('mean(CumGF_Home):Q', title="Average Home Goals"),
            color='Season:N').properties(
        width=280, height=400, title = 'Average Home Goals by Season')

    bar_chart_away_goals_by_team = alt.Chart(full_home_away).mark_bar().transform_filter(selection 
        ).encode(
            x=alt.X('Season:N', title="Season"),
            y=alt.Y('mean(CumGF_Away):Q', title="Average Away Goals"),
            color='Season:N').properties(
        width=280, height=400, title = 'Average Away Goals by Season')

    dashboard_home_away_linked = points_home_advantage_by_team & (bar_chart_home_goals_by_team | bar_chart_away_goals_by_team)

    brush = alt.selection_interval(encodings=['x', 'y'])

    points_home_advantage_drag = alt.Chart(full_home_away).mark_circle(size = 100).encode(
        x = alt.X('CumPts_Home:Q', 
                        title='Home Points'),
        y = alt.Y('CumPts_Away:Q', 
                        title='Away Points'),
        color = alt.Color('Season:N', title = 'Season'),
        tooltip =[alt.Tooltip('Team:N', title='Team'),
                  alt.Tooltip('CumPts_Home:Q', title='Home Points'),
                  alt.Tooltip('CumPts_Away:Q', title='Away Points'),
                  alt.Tooltip('Rank_Home:N', title='Home Rank'),
                  alt.Tooltip('Rank_Away:N', title='Away Rank'), 
                  alt.Tooltip('Season:N', title='Season')]
        ).properties(width=600,
                height=600,
                title=alt.TitleParams(text='Drag-To-Populate Home and Away Points By Team and Season',
                        fontSize=20,       
                        anchor='middle',
                        subtitle = 'Highlight over area of teams to populate average home and away goals tables below:')
                    ).add_params(brush)
        
    bar_chart_home_goals_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush 
        ).encode(
            x=alt.X('Season:N', title="Season"),
            y=alt.Y('mean(CumGF_Home):Q', title="Average Home Goals"),
            color='Season:N').properties(
        width=280, height=400, title = 'Average Home Goals by Season')

    bar_chart_away_goals_drag = alt.Chart(full_home_away).mark_bar().transform_filter(brush 
        ).encode(
            x=alt.X('Season:N', title="Season"),
            y=alt.Y('mean(CumGF_Away):Q', title="Average Away Goals"),
            color='Season:N').properties(
        width=280, height=400, title = 'Average Away Goals by Season')


    dashboard_home_away_drag = points_home_advantage_drag & (bar_chart_home_goals_drag | bar_chart_away_goals_drag)

    dashboard = alt.vconcat(
        q1_visuals,
        header_q2,
        alt.vconcat(*attacking_charts),
        header_q3,
        dashboard_home_away_linked,
        dashboard_home_away_drag,
        spacing=40
    ).add_params(
        selection, 
        selection_attack_stats).resolve_scale(color='independent')

    return dashboard