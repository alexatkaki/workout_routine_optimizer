import os
import json
import streamlit as st
from ui import main as ui_main

# Set page config
st.set_page_config(
    page_title="Workout Routine Optimizer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)            
            
# Run the application
if __name__ == "__main__":
    ui_main()