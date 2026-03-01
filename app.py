import streamlit as st
from utils.data_utils import load_data, get_daily_standings

st.set_page_config(
    page_title="Premier League Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Premier League Interactive Dashboard: 2023 - 2025")

st.markdown("""
### Welcome to the Premier League Analysis Tool
Throughout the dashboard I explore the performance of teams in the Premier League across the 2023-2024 and 2024-2025 seasons. I will in addition explore team attacking performance and the home advantage that teams received.

""")
