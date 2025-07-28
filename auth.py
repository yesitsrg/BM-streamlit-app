# auth.py
"""
Authentication module for Beisman Maps Management System
"""

import streamlit as st
from config import AUTH_CONFIG
from database import db_manager

class AuthManager:
    """
    Handles all authentication-related operations
    """
    
    def __init__(self):
        pass

    def validate_credentials(self, username, password):
        """
        Validate admin credentials
        """
        user = db_manager.get_user_by_username(username)
        if user is not None and user.PasswordHash == password:
            return True
        return False
    
    def login(self, username, password):
        """
        Perform login operation
        """
        if not username or not password:
            return False, "Please enter username and password"
        
        if self.validate_credentials(username, password):
            st.session_state.admin_logged_in = True
            st.session_state.current_page = 'admin_panel'
            st.session_state.show_admin_login = False
            st.session_state.login_error = ''
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
    
    def logout(self):
        """
        Perform logout operation
        """
        st.session_state.current_page = 'home'
        st.session_state.show_admin_login = False
        st.session_state.login_error = ''
        st.session_state.admin_logged_in = False
    
    def is_admin_logged_in(self):
        """
        Check if admin is logged in
        """
        return st.session_state.get('admin_logged_in', False)
    
    def require_admin_login(self):
        """
        Decorator/function to require admin login
        """
        if not self.is_admin_logged_in():
            st.session_state.current_page = 'home'
            st.session_state.show_admin_login = True
            return False
        return True

# Create a global instance
auth_manager = AuthManager()