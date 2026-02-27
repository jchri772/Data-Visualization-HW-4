import streamlit as st
import altair as alt
import pandas as pd
from charts.charts import create_pl_dashboard

def get_daily_standings(df):
    return daily_df 

def home_away_stats(df):
    return home_df, away_df
df_2324 = pd.read_csv("PL-season-2324.csv")
df_2425 = pd.read_csv("PL-season-2425.csv")
df_2324['Date'] = pd.to_datetime(df_2324['Date'], dayfirst=True)
df_2425['Date'] = pd.to_datetime(df_2425['Date'], dayfirst=True)

standings_2324 = get_daily_standings(df_2324)
standings_2425 = get_daily_standings(df_2425)

h23, a23 = home_away_stats(df_2324)
h24, a24 = home_away_stats(df_2425)

m23 = pd.merge(h23[h23['Date'] == h23['Date'].max()], a23[a23['Date'] == a23['Date'].max()], on='Team', suffixes=('_Home', '_Away'))
m24 = pd.merge(h24[h24['Date'] == h24['Date'].max()], a24[a24['Date'] == a24['Date'].max()], on='Team', suffixes=('_Home', '_Away'))
m23['Season'], m24['Season'] = '23-24', '24-25'
full_home_away = pd.concat([m23, m24])

st.set_page_config(layout="wide")
st.title("Premier League Story: 2023 - 2025")

dashboard = create_pl_dashboard(standings_2324, standings_2425, full_home_away)

st.altair_chart(dashboard, use_container_width=True)