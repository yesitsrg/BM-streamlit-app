# pages.py
"""
Page handlers module for Beisman Maps Management System
"""

import streamlit as st
from components import ui_components
from database import db_manager
from auth import auth_manager
from utils import navigate_to_page, show_admin_login_form, hide_admin_login_form, set_login_error, reset_search_input, rerun_app

class PageHandlers:
    """
    Handles all page rendering and logic
    """
    
    def show_main_screen(self):
        """
        Show main screen
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Beisman Map Menu")
        
        # Admin login button
        ui_components.render_admin_button_container(
            "Admin Login", 
            "admin_login_header", 
            show_admin_login_form
        )
        
        ui_components.render_content_area_start()
        ui_components.render_nav_links()
        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_admin_login_screen(self):
        """
        Show admin login screen
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Beisman Map Menu - Admin Login")
        ui_components.render_content_area_start()
        
        # Back button
        ui_components.render_back_button(
            "← Back to Main Menu",
            "back_to_main",
            lambda: (hide_admin_login_form(), navigate_to_page('home'))
        )
        
        # Login form
        ui_components.render_form_container_start()
        ui_components.render_form_header("Administrator Login")
        
        username = st.text_input("Username:", key="admin_username", value="")
        password = st.text_input("Password:", type="password", key="admin_password", value="")
        
        ui_components.render_login_error(st.session_state.get('login_error', ''))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("OK", key="login_ok"):
                success, message = auth_manager.login(username, password)
                if success:
                    rerun_app()
                else:
                    set_login_error(message)
        
        with col2:
            if st.button("Cancel", key="login_cancel"):
                hide_admin_login_form()
                navigate_to_page('home')
        
        ui_components.render_form_container_end()
        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_admin_panel(self):
        """
        Show admin panel
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Beisman Map Menu - Admin Panel")
        
        # Logout button
        ui_components.render_admin_button_container(
            "Logout",
            "admin_logout_header",
            auth_manager.logout
        )
        
        ui_components.render_content_area_start()
        
        # Navigation buttons
        buttons_clicked = ui_components.render_admin_nav_buttons()
        
        # Handle navigation
        if buttons_clicked['browse_maps']:
            navigate_to_page('browse_maps')
        elif buttons_clicked['browse_entities']:
            navigate_to_page('browse_entities')
        elif buttons_clicked['insert_map']:
            navigate_to_page('insert_map')
        elif buttons_clicked['update_delete']:
            navigate_to_page('update_delete')
        elif buttons_clicked['delete_entities']:
            navigate_to_page('delete_entities')
        
        ui_components.render_admin_session_info()
        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_browse_maps(self):
        """
        Show browse maps page
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Browse Beisman Maps")
        ui_components.render_content_area_start()
        
        # Back button
        ui_components.render_back_button(
            "← Back to Admin Panel",
            "back_to_admin",
            lambda: navigate_to_page('admin_panel')
        )
        
        # Database connection status
        if db_manager.is_available():
            if db_manager.test_connection():
                ui_components.render_status_message("success", "Database connection successful", "✅")
            else:
                ui_components.render_status_message("error", "Database connection failed - using offline mode", "❌")
        else:
            ui_components.render_status_message("error", "pyodbc module is not installed. Please install it using: pip install pyodbc", "⚠️")
        
        # Search section
        search_term, search_button, reset_button = ui_components.render_search_container()
        
        # Handle search and data retrieval
        if reset_button:
            reset_search_input()
            filtered_data = db_manager.get_beisman_data()
            rerun_app()
        elif search_button or search_term:
            filtered_data = db_manager.search_maps(search_term)
        else:
            filtered_data = db_manager.get_beisman_data()
        
        # Results section
        ui_components.render_results_container_start()
        
        if filtered_data is not None and not filtered_data.empty:
            table_html = ui_components.render_data_table(filtered_data)
            st.markdown(table_html, unsafe_allow_html=True)
            
            record_count = len(filtered_data)
            if search_term:
                ui_components.render_status_message("info", f"Found {record_count} record(s) matching '{search_term}'", "🔍")
            else:
                ui_components.render_status_message("info", f"Displaying {record_count} total record(s)", "📊")
        else:
            if search_term:
                ui_components.render_status_message("warning", "No records found matching your search criteria.", "🔍")
            else:
                ui_components.render_status_message("warning", "No data available in the database.", "📭")
        
        ui_components.render_results_container_end()
        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_browse_entities(self):
        """
        Show browse entities page
        """
        self.show_placeholder_page("Browse Entities", "Browse Entities")
    
    def show_insert_map(self):
        """
        Show insert map page
        """
        self.show_placeholder_page("Insert New Map", "Insert New Map")
    
    def show_update_delete(self):
        """
        Show update/delete maps page
        """
        self.show_placeholder_page("Update/Delete Maps", "Update/Delete Maps")
    
    def show_delete_entities(self):
        """
        Show delete entities page
        """
        self.show_placeholder_page("Delete Entities", "Delete Entities")
    
    def show_placeholder_page(self, title, message):
        """
        Show placeholder page for future functionality
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header(title)
        ui_components.render_content_area_start()
        
        ui_components.render_back_button(
            "← Back to Admin Panel",
            f"back_to_admin_{title.lower().replace(' ', '_')}",
            lambda: navigate_to_page('admin_panel')
        )
        
        ui_components.render_status_message("info", f"{message} functionality will be implemented here.")
        
        ui_components.render_content_area_end()
        ui_components.render_main_container_end()

# Create a global instance
page_handlers = PageHandlers()