# config.py
"""
Configuration module for Beisman Maps Management System
"""

# Database configuration
DATABASE_CONFIG = {
    'conn_string': (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=tempdb;"
        "Trusted_Connection=yes;"
    ),
    'timeout': 10,
    'table_name': 'BeismanDB.dbo.beisman'
}

# Authentication configuration
AUTH_CONFIG = {
    'admin_username': 'admin',
    'admin_password': 'admin'
}

# Application configuration
APP_CONFIG = {
    'page_title': 'Beisman Maps Management System',
    'page_icon': '🗺️',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed',
    'max_width': 1000,
    'cell_max_length': 100
}

# Session state defaults
SESSION_DEFAULTS = {
    'current_page': 'home',
    'show_admin_login': False,
    'login_error': '',
    'admin_logged_in': False,
    'admin_section': 'main'
}