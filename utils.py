# utils.py
"""
Utility functions module for Beisman Maps Management System
"""

import streamlit as st
import pandas as pd
from config import SESSION_DEFAULTS, APP_CONFIG

def init_session_state():
    """
    Initialize session state variables
    """
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

def rerun_app():
    """
    Compatibility function for app rerun
    """
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.legacy_caching.clear_cache()

def navigate_to_page(page_name):
    """
    Navigate to a specific page
    """
    st.session_state.current_page = page_name
    rerun_app()

def show_admin_login_form():
    """
    Show admin login form
    """
    st.session_state.show_admin_login = True
    st.session_state.login_error = ''
    rerun_app()

def hide_admin_login_form():
    """
    Hide admin login form
    """
    st.session_state.show_admin_login = False
    st.session_state.login_error = ''
    rerun_app()

def set_login_error(error_message):
    """
    Set login error message
    """
    st.session_state.login_error = error_message
    rerun_app()

def truncate_text(text, max_length=None):
    """
    Truncate text to specified length
    """
    if max_length is None:
        max_length = APP_CONFIG['cell_max_length']
    
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def format_cell_value(value):
    """
    Format cell value for display
    """
    if pd.isna(value):
        return ""
    
    text = str(value)
    return truncate_text(text)

def get_current_page():
    """
    Get current page from session state
    """
    return st.session_state.get('current_page', 'home')

def is_admin_logged_in():
    """
    Check if admin is logged in
    """
    return st.session_state.get('admin_logged_in', False)

def show_login_form():
    """
    Check if login form should be shown
    """
    return st.session_state.get('show_admin_login', False)

def get_login_error():
    """
    Get login error message
    """
    return st.session_state.get('login_error', '')

def reset_search_input():
    """
    Reset search input
    """
    if 'search_input' in st.session_state:
        st.session_state.search_input = ""