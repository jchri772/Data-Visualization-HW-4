import streamlit as st
from io import load_data, get_daily_standings
import story

st.set_page_config(page_title="Premier League Dashboard", layout="wide")

st.title("Premier League Interactive Dashboard")

PL_2324_data, PL_2425_data = load_data()

standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

story.render(standings_2324, standings_2425)