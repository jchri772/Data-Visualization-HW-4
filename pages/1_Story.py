import streamlit as st
import altair as alt
import pandas as pd
from charts.charts import create_pl_dashboard

# --- 1. DATA PROCESSING FUNCTIONS (From your app.py) ---
def get_daily_standings(df):    
    cols_to_exclude = ['HTAG', 'HTR', 'HTHG', 'Referee'] 
    home_df = df.drop(columns=cols_to_exclude).copy().rename(columns={'HomeTeam': 'Team', 'FTHG': 'GF', 'FTAG': 'GA', 'HS': 'Shots For', 'AS': 'Opposition Shots', 'HST': 'Shots on Target', 'AST': 'Opposition Shots on Target', 'HF': 'Fouls', 'AF': 'Opposition Fouls', 'HC': 'Corners', 'AC': 'Corners Against', 'HY': 'Yellow Cards', 'AY': 'Opposition Yellow Cards', 'HR': 'Red Cards', 'AR': 'Opposition Red Cards' })
    away_df = df.drop(columns=cols_to_exclude).copy().rename(columns={'AwayTeam': 'Team', 'FTAG': 'GF', 'FTHG': 'GA', 'AS': 'Shots For', 'HS': 'Opposition Shots', 'AST': 'Shots on Target', 'HST': 'Opposition Shots on Target', 'AF': 'Fouls', 'HF': 'Opposition Fouls', 'AC': 'Corners', 'HC': 'Corners Against', 'AY': 'Yellow Cards', 'HY': 'Opposition Yellow Cards', 'AR': 'Red Cards', 'HR': 'Opposition Red Cards'})
    home_df['Pts'], away_df['Pts'] = 0, 0
    home_df.loc[home_df['FTR'] == 'H', 'Pts'] = 3
    home_df.loc[home_df['FTR'] == 'D', 'Pts'] = 1
    away_df.loc[away_df['FTR'] == 'A', 'Pts'] = 3
    away_df.loc[away_df['FTR'] == 'D', 'Pts'] = 1
    stats = pd.concat([home_df, away_df]).sort_values('Date')
    stats['GD'] = stats['GF'] - stats['GA']
    to_exclude = ['Date', 'Team', 'FTR', 'Div']
    stat_cols = [c for c in stats.columns if c not in to_exclude and pd.api.types.is_numeric_dtype(stats[c])]
    cum_cols = [f'Cum{c}' for c in stat_cols]
    stats[cum_cols] = stats.groupby('Team')[stat_cols].cumsum()
    grid = pd.MultiIndex.from_product([sorted(stats['Date'].unique()), stats['Team'].unique()], names=['Date', 'Team']).to_frame(index=False)
    daily = pd.merge(grid, stats[['Date', 'Team'] + stat_cols + cum_cols], on=['Date', 'Team'], how='left')
    daily[cum_cols] = daily.groupby('Team')[cum_cols].ffill().fillna(0)
    daily = daily.sort_values(by=['Date', 'CumPts', 'CumGD', 'CumGF'], ascending=[True, False, False, False])
    daily['Rank'] = daily.groupby('Date').cumcount() + 1
    return daily.reset_index(drop=True)

def home_away_stats(df):    
    # ... (Your home_away_stats logic from app.py)
    # Keeping it short for brevity, but ensure the full code from your app.py is here
    # It must return results[0], results[1]
    results = []
    # [Insert the loop and processing from your app.py here]
    return results[0], results[1]

# --- 2. LOAD & CALCULATE DATA ---
PL_2324_data = pd.read_csv("PL-season-2324.csv")
PL_2425_data = pd.read_csv("PL-season-2425.csv")
PL_2324_data['Date'] = pd.to_datetime(PL_2324_data['Date'], dayfirst=True)
PL_2425_data['Date'] = pd.to_datetime(PL_2425_data['Date'], dayfirst=True)

# These define the variables the dashboard needs
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

h23, a23 = home_away_stats(df_2324)
h24, a24 = home_away_stats(df_2425)

# Merging logic to create full_home_away
m23 = pd.merge(h23[h23['Date'] == h23['Date'].max()], a23[a23['Date'] == a23['Date'].max()], on='Team', suffixes=('_Home', '_Away'))
m24 = pd.merge(h24[h24['Date'] == h24['Date'].max()], a24[a24['Date'] == a24['Date'].max()], on='Team', suffixes=('_Home', '_Away'))
m23['Season'], m24['Season'] = '23-24', '24-25'
full_home_away = pd.concat([m23, m24])

# --- 3. RENDER DASHBOARD ---
st.set_page_config(layout="wide")
st.title("Premier League Story: 2023 - 2025")

# This now works because standings_2324, etc., are defined above
dashboard = create_pl_dashboard(standings_2324, standings_2425, full_home_away)
st.altair_chart(dashboard, use_container_width=True)