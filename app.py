# main.py
"""
Main application entry point for Beisman Maps Management System

"""

import streamlit as st
from config import APP_CONFIG
from styles import get_css_styles
from utils import init_session_state
from router import app_router

def configure_page():
    """
    Configure Streamlit page settings
    """
    st.set_page_config(
        page_title=APP_CONFIG['page_title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
    )

def load_styles():
    """
    Load CSS styles
    """
    st.markdown(get_css_styles(), unsafe_allow_html=True)

def main():
    """
    Main application function
    """
    try:
        # Configure page
        configure_page()
        
        # Load styles
        load_styles()
        
        # Initialize session state
        init_session_state()
        
        # Route to appropriate page
        app_router.route()
        
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please check your setup and try refreshing the page.")

if __name__ == "__main__":
    main()