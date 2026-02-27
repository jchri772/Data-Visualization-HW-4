import streamlit as st
import altair as alt
import pandas as pd
from charts.charts import create_pl_dashboard

st.set_page_config(layout="wide")

st.title("Premier League Story: 2023 - 2025")

dashboard = create_pl_dashboard(standings_2324, standings_2425, full_home_away)

st.altair_chart(dashboard, use_container_width=True)