import asyncio
from datetime import datetime
import streamlit as st
import os
import openai
from typing import List, Sequence
from videoint import videoint


# Set page size
st.set_page_config(
    page_title="Gen Video AI Application Validation",
    page_icon=":rocket:",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)

# Load your CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to load the CSS
load_css("styles.css")

# st.logo("images/agenticaiimg.jpeg")
# st.sidebar.image("agenticaiimg.jpeg", use_container_width=True)

# Sidebar navigation
nav_option = st.sidebar.selectbox("Navigation", ["Home", 
                                                 "Video" 
                                                 , "About"])

# Display the selected page
if nav_option == "Video":
    videoint()
elif nav_option == "About":
    videoint() 