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
            elif current_page == 'map_details' and admin_logged_in:
                self.page_handlers.show_map_details()
            else:
                # Default to main screen
                self.page_handlers.show_main_screen()
                
        except Exception as e:
            st.error(f"Routing error: {str(e)}")
            # Fallback to main screen on error
            self.page_handlers.show_main_screen()

# Create a global instance
app_router = AppRouter()

