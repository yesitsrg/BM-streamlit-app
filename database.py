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
    def get_beisman_data(self):
        """
        Retrieve all data from the beisman table
        """
        if not PYODBC_AVAILABLE:
            return pd.DataFrame()
        
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            query = f"SELECT * FROM {self.table_name}"
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
    
    def insert_map(self, trace_number, drawer, description):
        """
        Insert new map data into the database
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"

        # Check if the tracking number already exists
        if not self.get_map_by_track_number(trace_number).empty:
            return False, f"Tracking number {trace_number} already exists in the database."

        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} (Number, Drawer, PropertyDetails) VALUES (?, ?, ?)",
                           (trace_number, drawer, description))
            conn.commit()

            # Verify the insertion
            if not self.get_map_by_track_number(trace_number).empty:
                return True, "Map data inserted successfully."
            else:
                return False, "Failed to verify data insertion."
        except Exception as e:
            return False, f"Error inserting data: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def update_map(self, old_trace_number, new_trace_number, new_drawer, new_description):
        """
        Update existing map data
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"
        
        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {self.table_name} SET Number = ?, Drawer = ?, PropertyDetails = ? WHERE Number = ?",
                           (new_trace_number, new_drawer, new_description, old_trace_number))
            conn.commit()
            return True, "Map updated successfully"
        except Exception as e:
            return False, f"Error updating map: {str(e)}"
        finally:
            if conn:
                conn.close()

    def delete_map(self, track_number):
        """
        Delete map from database
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"
        
        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            # First, delete associated entities
            cursor.execute("DELETE FROM BeismanDB.dbo.Entities WHERE BeismanNumber = ?", (track_number,))
            # Then, delete the map
            cursor.execute(f"DELETE FROM {self.table_name} WHERE Number = ?", (track_number,))
            conn.commit()
            return True, "Map deleted successfully"
        except Exception as e:
            return False, f"Error deleting map: {str(e)}"
        finally:
            if conn:
                conn.close()

    def get_entities_for_map(self, track_number):
        """
        Get all entities for a given map
        """
        if not PYODBC_AVAILABLE:
            return pd.DataFrame()

        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()

        try:
            query = "SELECT EntityName FROM BeismanDB.dbo.Entities WHERE BeismanNumber = ?"
            df = pd.read_sql(query, conn, params=[track_number])
            return df
        except Exception:
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    def add_entity_to_map(self, track_number, entity_name):
        """
        Add a new entity for a map
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"

        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO BeismanDB.dbo.Entities (BeismanNumber, EntityName) VALUES (?, ?)",
                           (track_number, entity_name))
            conn.commit()
            return True, "Entity added successfully."
        except Exception as e:
            return False, f"Error adding entity: {str(e)}"
        finally:
            if conn:
                conn.close()

    def remove_entity_from_map(self, track_number, entity_name):
        """
        Remove an entity associated with a map
        """
        if not PYODBC_AVAILABLE:
            return False, "Database not available"

        conn = self.get_connection()
        if conn is None:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Entities WHERE BeismanNumber = ? AND EntityName = ?",
                           (track_number, entity_name))
            conn.commit()
            return True, "Entity removed successfully."
        except Exception as e:
            return False, f"Error removing entity: {str(e)}"
        finally:
            if conn:
                conn.close()

# Create a global instance
db_manager = DatabaseManager()