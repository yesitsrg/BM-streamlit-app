# components.py
"""
UI components module for Beisman Maps Management System
"""

import streamlit as st
import pandas as pd
from utils import format_cell_value

class UIComponents:
    """
    Reusable UI components for the application
    """
    
    @staticmethod
    def render_window_header(title):
        """
        Render Windows-style header
        """
        st.markdown(f"""
        <div class="windows-header">
            <div class="header-title">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_main_container_start():
        """
        Start main container
        """
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    @staticmethod
    def render_main_container_end():
        """
        End main container
        """
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_content_area_start():
        """
        Start content area
        """
        st.markdown('<div class="content-area">', unsafe_allow_html=True)
    
    @staticmethod
    def render_content_area_end():
        """
        End content area
        """
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_admin_button_container(button_text, button_key, on_click=None):
        """
        Render admin button in header
        """
        st.markdown('<div class="admin-button-container">', unsafe_allow_html=True)
        if st.button(button_text, key=button_key):
            if on_click:
                on_click()
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_nav_links():
        """
        Render navigation links
        """
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="nav-links">
            <a href="#" class="nav-link">Browse Maps</a>
            <a href="#" class="nav-link">Browse Entities</a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_form_container_start():
        """
        Start form container
        """
        st.markdown('<div style="display: flex; justify-content: center; margin-top: 50px;">', unsafe_allow_html=True)
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    @staticmethod
    def render_form_container_end():
        """
        End form container
        """
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_form_header(title):
        """
        Render form header
        """
        st.markdown(f'<div class="form-header">{title}</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_login_error(error_message):
        """
        Render login error message
        """
        if error_message:
            st.markdown(f'<div class="login-error">{error_message}</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_search_container():
        """
        Render search container
        """
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([6, 1.5, 1.5])
        
        with col1:
            search_term = st.text_input("Search:", placeholder="Enter search term...", key="search_input")
        
        with col2:
            search_button = st.button("Search")
        
        with col3:
            reset_button = st.button("Reset")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return search_term, search_button, reset_button
    
    @staticmethod
    def render_results_container_start():
        """
        Start results container
        """
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    @staticmethod
    def render_results_container_end():
        """
        End results container
        """
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_data_table(data):
        """
        Render data table with details links
        """
        if data is None or data.empty:
            return "<p style='text-align: center; padding: 20px;'>No data available to display.</p>"
        
        html_table = '<table class="dataframe" style="width: 100%; border-collapse: collapse;">'
        
        # Header
        html_table += '<tr style="background: #c0c0c0;">'
        html_table += '<th style="border: 1px solid #808080; padding: 4px; text-align: left;">Details</th>'
        for col in data.columns:
            html_table += f'<th style="border: 1px solid #808080; padding: 4px; text-align: left;">{col}</th>'
        html_table += '</tr>'
        
        # Data rows
        for idx, row in data.iterrows():
            html_table += '<tr>'
            html_table += '<td style="border: 1px solid #808080; padding: 4px;"><a href="#" style="color: #0000ff; text-decoration: underline;">Details</a></td>'
            for col in data.columns:
                cell_value = format_cell_value(row[col])
                html_table += f'<td style="border: 1px solid #808080; padding: 4px;">{cell_value}</td>'
            html_table += '</tr>'
        
        html_table += '</table>'
        return html_table
    
    @staticmethod
    def render_status_message(message_type, message, icon=""):
        """
        Render status message
        """
        if message_type == "success":
            st.success(f"{icon} {message}")
        elif message_type == "error":
            st.error(f"{icon} {message}")
        elif message_type == "warning":
            st.warning(f"{icon} {message}")
        elif message_type == "info":
            st.info(f"{icon} {message}")
    
    @staticmethod
    def render_back_button(text, key, on_click=None):
        """
        Render back button
        """
        if st.button(text, key=key):
            if on_click:
                on_click()
    
    @staticmethod
    def render_admin_nav_buttons():
        """
        Render admin navigation buttons
        """
        col1, col2, col3 = st.columns(3)
        
        buttons_clicked = {}
        
        with col1:
            buttons_clicked['browse_maps'] = st.button("Browse Maps", key="nav_browse_maps")
            buttons_clicked['insert_map'] = st.button("Insert New Map", key="nav_insert")
        
        with col2:
            buttons_clicked['browse_entities'] = st.button("Browse Entities", key="nav_browse_entities")
            buttons_clicked['update_delete'] = st.button("Update/Delete Maps", key="nav_update")
        
        with col3:
            buttons_clicked['delete_entities'] = st.button("Delete Entities", key="nav_delete")
        
        return buttons_clicked
    
    @staticmethod
    def render_admin_session_info():
        """
        Render admin session information
        """
        st.markdown('<div style="margin-top: 20px; padding: 10px; text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 11px; font-family: MS Sans Serif, sans-serif; color: #000080;">Administrator Session Active</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Create a global instance
ui_components = UIComponents()