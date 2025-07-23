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
            # Create header
            col_map = {"Details": 1, "Number": 2, "Drawer": 2, "PropertyDetails": 4}
            cols = st.columns(list(col_map.values()))
            for i, col_name in enumerate(col_map.keys()):
                cols[i].write(f"**{col_name}**")

            for index, row in filtered_data.iterrows():
                cols = st.columns(list(col_map.values()))
                if cols[0].button("Details", key=f"details_{row['Number']}"):
                    st.session_state.selected_track_number = row['Number']
                    navigate_to_page('browse_entities')
                    rerun_app()
                
                cols[1].write(row['Number'])
                cols[2].write(row['Drawer'])
                cols[3].write(row['PropertyDetails'])
            
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
        Show map details page
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Map Information")
        ui_components.render_content_area_start()

        if 'selected_track_number' in st.session_state:
            track_number = st.session_state.selected_track_number
            # This assumes a function get_map_by_track_number exists in db_manager
            # and returns a DataFrame.
            map_details_df = db_manager.get_map_by_track_number(track_number)

            if map_details_df is not None and not map_details_df.empty:
                map_details = map_details_df.iloc[0]
                
                st.markdown("---")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write("Trace Number")
                    st.write("Drawer")
                    st.write("Description")
                with col2:
                    st.write(f"{map_details.get('Number', 'N/A')}")
                    st.write(f"{map_details.get('Drawer', 'N/A')}")
                    st.write(f"{map_details.get('PropertyDetails', 'N/A')}")

                st.markdown("---")

                st.info("No clients associated with this map.")
                
                st.markdown("---")

                # Bottom navigation links
                cols = st.columns(6)
                with cols[0]:
                    if st.button("Home", key="detail_home"):
                        navigate_to_page('home')
                with cols[1]:
                    if st.button("Back", key="detail_back"):
                        navigate_to_page('browse_maps')
                with cols[2]:
                    if st.button("Browse Maps", key="detail_browse_maps"):
                        navigate_to_page('browse_maps')
                with cols[3]:
                    if st.button("Browse Entities", key="detail_browse_entities"):
                        navigate_to_page('browse_entities')
                with cols[4]:
                    if st.button("Insert Map", key="detail_insert_map"):
                        navigate_to_page('insert_map')
                with cols[5]:
                    if st.button("Update/Delete", key="detail_update_delete"):
                        st.session_state.selected_track_number = track_number
                        navigate_to_page('update_delete')
                
                # Second row of links
                cols2 = st.columns(6) # Use same number of columns for alignment
                with cols2[0]:
                    if st.button("Maps", key="detail_maps"):
                        navigate_to_page('browse_maps')
                with cols2[1]:
                    if st.button("Delete Entities", key="detail_delete_entities"):
                        navigate_to_page('delete_entities')

            else:
                st.warning(f"Could not find details for map with track number: {track_number}")
                if st.button("← Back to Browse Maps"):
                    navigate_to_page('browse_maps')

        else:
            st.warning("No map selected. Please go back to 'Browse Maps' and click 'Details' on a map.")
            if st.button("← Browse Maps"):
                navigate_to_page('browse_maps')

        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_insert_map(self):
        """
        Show insert map page
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Insert New Map")
        ui_components.render_content_area_start()

        ui_components.render_back_button(
            "← Back to Admin Panel",
            "back_to_admin_insert",
            lambda: navigate_to_page('admin_panel')
        )

        st.write("---")

        trace_number = st.text_input("Trace Number:")
        drawer = st.text_input("Drawer:")
        description = st.text_area("Description:")

        st.write("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Insert", key="insert_map_button"):
                if trace_number and drawer and description:
                    success, message = db_manager.insert_map(trace_number, drawer, description)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields.")

        with col2:
            if st.button("Cancel", key="cancel_insert_map_button"):
                navigate_to_page('admin_panel')

        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
    def show_update_delete(self):
        """
        Show update/delete maps page
        """
        ui_components.render_main_container_start()
        ui_components.render_window_header("Update/Delete Map")
        ui_components.render_content_area_start()

        ui_components.render_back_button(
            "← Back to Admin Panel",
            "back_to_admin_update",
            lambda: navigate_to_page('admin_panel')
        )

        st.write("---")

        if 'selected_track_number' in st.session_state:
            track_number = st.session_state.selected_track_number
            map_details_df = db_manager.get_map_by_track_number(track_number)

            if map_details_df is not None and not map_details_df.empty:
                map_details = map_details_df.iloc[0]

                # Display current map details in editable fields
                st.subheader("Update Map Details")
                new_trace_number = st.text_input("Trace Number:", value=map_details.get('Number', ''))
                new_drawer = st.text_input("Drawer:", value=map_details.get('Drawer', ''))
                new_description = st.text_area("Description:", value=map_details.get('PropertyDetails', ''))

                st.write("---")

                # Manage Entities
                st.subheader("Manage Entities")
                entities_df = db_manager.get_entities_for_map(track_number)
                
                if entities_df is not None and not entities_df.empty:
                    st.write("Entities associated with this map:")
                    for index, entity in entities_df.iterrows():
                        col1, col2 = st.columns([4, 1])
                        col1.write(entity['EntityName'])
                        if col2.button(f"Remove {entity['EntityName']}", key=f"remove_entity_{entity['EntityName']}"):
                            db_manager.remove_entity_from_map(track_number, entity['EntityName'])
                            st.experimental_rerun()
                else:
                    st.write("No entities associated with this map.")

                # Add new entity
                new_entity_name = st.text_input("Add new entity:", key="new_entity_name")
                if st.button("Add Entity"):
                    if new_entity_name:
                        success, message = db_manager.add_entity_to_map(track_number, new_entity_name)
                        if success:
                            st.success(message)                            
                            st.experimental_rerun()
                        else:
                            st.error(message)

                st.write("---")

                # Update and Delete buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Map", key="update_map_button"):
                        success, message = db_manager.update_map(track_number, new_trace_number, new_drawer, new_description)
                        if success:
                            st.success(message)
                            if track_number != new_trace_number:
                                st.session_state.selected_track_number = new_trace_number
                                st.experimental_rerun()
                        else:
                            st.error(message)
                with col2:
                    with st.expander("Delete Map", expanded=False):
                        st.warning("This action is permanent. It will delete the map and all associated entities.")
                        if st.button("Confirm Permanent Deletion", key="confirm_delete_map_button"):
                            success, message = db_manager.delete_map(track_number)
                            if success:
                                st.success(message)
                                navigate_to_page('admin_panel')
                            else:
                                st.error(message)
            else:
                st.warning("Could not find map details.")
        else:
            st.warning("No map selected.")

        ui_components.render_content_area_end()
        ui_components.render_main_container_end()
    
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