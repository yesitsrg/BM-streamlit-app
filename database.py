# database.py
"""
Database operations module for Beisman Maps Management System
"""

import pandas as pd
import streamlit as st
from config import DATABASE_CONFIG

# Check if pyodbc is available
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

class DatabaseManager:
    """
    Handles all database operations for the Beisman Maps Management System
    """
    
    def __init__(self):
        self.conn_string = DATABASE_CONFIG['conn_string']
        self.timeout = DATABASE_CONFIG['timeout']
        self.table_name = DATABASE_CONFIG['table_name']
    
    def is_available(self):
        """
        Check if database functionality is available
        """
        return PYODBC_AVAILABLE
    
    def get_connection(self):
        """
        Get database connection
        """
        if not PYODBC_AVAILABLE:
            return None
        try:
            conn = pyodbc.connect(self.conn_string, timeout=self.timeout)
            return conn
        except Exception:
            return None
    
    def test_connection(self):
        """
        Test database connection
        """
        conn = self.get_connection()
        if conn:
            conn.close()
            return True
        return False
    
    @st.cache
    def get_beisman_data(_self):
        """
        Retrieve all data from the beisman table
        """
        if not PYODBC_AVAILABLE:
            return pd.DataFrame()
        
        conn = _self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            query = f"SELECT * FROM {_self.table_name}"
            df = pd.read_sql(query, conn)
            return df
        except Exception:
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()
    
    def search_maps(self, search_term):
        """
        Search for maps based on search term
        """
        if not search_term or not search_term.strip():
            return self.get_beisman_data()
        
        data = self.get_beisman_data()
        if data.empty:
            return data
        
        mask = data.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        return data[mask]

    def get_map_by_track_number(self, track_number):
        """
        Get map details by track number
        """
        if not PYODBC_AVAILABLE:
            return pd.DataFrame()

        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()

        try:
            query = f"SELECT * FROM {self.table_name} WHERE Number = ?"
            df = pd.read_sql(query, conn, params=[track_number])
            return df
        except Exception:
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()
    
    def insert_map(self, map_data):
        """
        Insert new map data into the database
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"
        
        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        try:
            # Implementation for insert operation
            # This is a placeholder - actual implementation depends on table structure
            cursor = conn.cursor()
            # cursor.execute("INSERT INTO ... VALUES (?)", map_data)
            # conn.commit()
            return True, "Map inserted successfully"
        except Exception as e:
            return False, f"Error inserting map: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def update_map(self, map_id, map_data):
        """
        Update existing map data
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"
        
        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        try:
            # Implementation for update operation
            # This is a placeholder - actual implementation depends on table structure
            cursor = conn.cursor()
            # cursor.execute("UPDATE ... SET ... WHERE id = ?", (map_data, map_id))
            # conn.commit()
            return True, "Map updated successfully"
        except Exception as e:
            return False, f"Error updating map: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def delete_map(self, map_id):
        """
        Delete map from database
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"
        
        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        try:
            # Implementation for delete operation
            # This is a placeholder - actual implementation depends on table structure
            cursor = conn.cursor()
            # cursor.execute("DELETE FROM ... WHERE id = ?", (map_id,))
            # conn.commit()
            return True, "Map deleted successfully"
        except Exception as e:
            return False, f"Error deleting map: {str(e)}"
        finally:
            if conn:
                conn.close()

# Create a global instance
db_manager = DatabaseManager()