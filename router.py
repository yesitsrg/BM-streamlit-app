# router.py
"""
Application router module for Beisman Maps Management System
"""

import streamlit as st
from pages import page_handlers
from utils import get_current_page, is_admin_logged_in, show_login_form

class AppRouter:
    """
    Handles application routing and page navigation
    """
    
    def __init__(self):
        self.page_handlers = page_handlers
    
    def route(self):
        """
        Route to appropriate page based on session state
        """
        try:
            current_page = get_current_page()
            admin_logged_in = is_admin_logged_in()
            show_login = show_login_form()
            
            # Show admin login form
            if show_login:
                self.page_handlers.show_admin_login_screen()
                return
            
            # Admin-only pages
            if current_page == 'admin_panel' and admin_logged_in:
                self.page_handlers.show_admin_panel()
            elif current_page == 'browse_maps' and admin_logged_in:
                self.page_handlers.show_browse_maps()
            elif current_page == 'browse_entities' and admin_logged_in:
                self.page_handlers.show_browse_entities()
            elif current_page == 'insert_map' and admin_logged_in:
                self.page_handlers.show_insert_map()
            elif current_page == 'update_delete' and admin_logged_in:
                self.page_handlers.show_update_delete()
            elif current_page == 'delete_entities' and admin_logged_in:
                self.page_handlers.show_delete_entities()
            else:
                # Default to main screen
                self.page_handlers.show_main_screen()
                
        except Exception as e:
            st.error(f"Routing error: {str(e)}")
            # Fallback to main screen on error
            self.page_handlers.show_main_screen()

# Create a global instance
app_router = AppRouter()

# Streamlit compatibility fixes
def fix_streamlit_cache():
    """
    Fix for st.cache_data compatibility issues
    """
    # For older Streamlit versions, use st.cache instead of st.cache_data
    if not hasattr(st, 'cache_data'):
        st.cache_data = st.cache
    
    # For session state compatibility
    if 'session_state' not in dir(st):
        class SessionState:
            def __init__(self):
                self._state = {}
            
            def __getattr__(self, name):
                return self._state.get(name, None)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    self._state[name] = value
        
        st.session_state = SessionState()

# Call the fix function
fix_streamlit_cache()