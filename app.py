import streamlit as st
import importlib.util
import sys
from utils.data_utils import load_data, get_daily_standings

# Import the render function from the numeric filename
spec = importlib.util.spec_from_file_location("story", "pages/1_Story.py")
story = importlib.util.module_from_spec(spec)
sys.modules["story"] = story
spec.loader.exec_module(story)

st.set_page_config(page_title="Premier League Dashboard", layout="wide")
st.title("Premier League Interactive Dashboard")

# 1. Load the raw CSV data
PL_2324_data, PL_2425_data = load_data()

# 2. Process the data into standings
standings_2324 = get_daily_standings(PL_2324_data)
standings_2425 = get_daily_standings(PL_2425_data)

# 3. Pass the processed data to your story.py logic
story.render(standings_2324, standings_2425)