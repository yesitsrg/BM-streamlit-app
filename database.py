"""
Database Manager Module - Fixed to match exact Streamlit column structure
Handles all database operations for the Beisman Maps application.
"""

import pyodbc
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
from contextlib import contextmanager
from dataclasses import dataclass

# Configure module logger
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    server: str = "localhost"
    database: str = "BeismanDB"
    maps_table: str = "BeismanDB.dbo.beisman"
    entities_table: str = "BeismanDB.dbo.Entities"
    users_table: str = "BeismanDB.dbo.Users"
    use_windows_auth: bool = True
    connection_timeout: int = 30
    command_timeout: int = 30

class DatabaseManager:
    """
    Main database manager class - Matches exact Streamlit implementation
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database manager with configuration"""
        self.config = config or self._load_config_from_env()
        self._connection_string = self._build_connection_string()
        
        # Admin user credentials (matches your auth.py)
        self.admin_users = {
            "admin": "admin",  # Change this in production!
        }
        
        logger.info("DatabaseManager initialized")

    def _load_config_from_env(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        return DatabaseConfig(
            server=os.getenv('DB_SERVER', '.\\SQLEXPRESS'),
            database=os.getenv('DB_DATABASE', 'BeismanDB'),
            maps_table=os.getenv('DB_MAPS_TABLE', 'BeismanDB.dbo.beisman'),
            entities_table=os.getenv('DB_ENTITIES_TABLE', 'BeismanDB.dbo.Entities'),
            users_table=os.getenv('DB_USERS_TABLE', 'BeismanDB.dbo.Users'),
            use_windows_auth=os.getenv('DB_USE_WINDOWS_AUTH', 'true').lower() == 'true',
            connection_timeout=int(os.getenv('DB_CONNECTION_TIMEOUT', '10')),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', '30'))
        )

    def _build_connection_string(self) -> str:
        """Build SQL Server connection string"""
        if self.config.use_windows_auth:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config.server};"
                f"DATABASE={self.config.database};"
                f"Trusted_Connection=yes;"
                f"Connection Timeout={self.config.connection_timeout};"
            )
        else:
            raise NotImplementedError("SQL Server authentication not implemented")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            logger.debug("Establishing database connection")
            connection = pyodbc.connect(self._connection_string, timeout=self.config.connection_timeout)
            connection.autocommit = False
            yield connection
            
        except pyodbc.Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected database error: {e}")
            raise
            
        finally:
            if connection:
                try:
                    connection.close()
                    logger.debug("Database connection closed")
                except:
                    pass

    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                success = result is not None and result[0] == 1
                
                if success:
                    logger.info("Database connection test successful")
                else:
                    logger.warning("Database connection test failed - no result")
                    
                return success
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_current_timestamp(self) -> str:
        """Get current timestamp from database server"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT GETDATE()")
                result = cursor.fetchone()
                
                if result and result[0]:
                    return result[0].strftime("%m/%d/%Y, %I:%M:%S %p")
                else:
                    return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
                    
        except Exception as e:
            logger.warning(f"Failed to get database timestamp: {e}")
            return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

    # Authentication Methods (matching your auth.py)
    
    def validate_admin_credentials(self, username: str, password: str) -> bool:
        """Validate admin login credentials"""
        if not username or not password:
            return False
            
        # First try hardcoded credentials
        is_valid = (username in self.admin_users and 
                   self.admin_users[username] == password)
        
        # If not found in hardcoded, try database
        if not is_valid:
            user = self.get_user_by_username(username)
            if user is not None and hasattr(user, 'PasswordHash'):
                is_valid = user.PasswordHash == password
        
        if is_valid:
            logger.info(f"Valid admin credentials for user: {username}")
        else:
            logger.warning(f"Invalid admin credentials for user: {username}")
            
        return is_valid

    def get_user_by_username(self, username: str):
        """Get user by username from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT * FROM {self.config.users_table} WHERE Username = ?"
                cursor.execute(query, [username])
                
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    # Convert row to object-like structure
                    class UserRecord:
                        pass
                    
                    user = UserRecord()
                    for i, col in enumerate(columns):
                        setattr(user, col, row[i])
                    return user
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user {username}: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        if username in self.admin_users:
            return {
                "username": username,
                "is_admin": True,
                "display_name": "Administrator",
                "created_date": datetime.now().strftime("%m/%d/%Y"),
                "last_login": self.get_current_timestamp()
            }
        return None

    # Maps Operations (using correct column names: Number, Drawer, PropertyDetails)
    
    def get_beisman_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve maps data with pagination - matches Streamlit method signature"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query with pagination - ORDER BY Number (not MapID)
                query = f"SELECT * FROM {self.config.maps_table} ORDER BY Number OFFSET ? ROWS"
                params = [offset]
                
                if limit is not None:
                    query += " FETCH NEXT ? ROWS ONLY"
                    params.append(limit)
                
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                maps_data = []
                for row in rows:
                    map_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in map_dict.items():
                        if isinstance(value, datetime):
                            map_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            map_dict[key] = ""
                    maps_data.append(map_dict)
                
                logger.info(f"Retrieved {len(maps_data)} maps")
                return maps_data
                
        except Exception as e:
            logger.error(f"Error retrieving maps data: {e}")
            return []

    def get_beisman_data_count(self) -> int:
        """Get the total number of records in the beisman table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT COUNT(*) FROM {self.config.maps_table}"
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Error getting maps count: {e}")
            return 0

    def get_maps_data(self, limit: int = 50, offset: int = 0, 
                     search_term: Optional[str] = None) -> Dict[str, Any]:
        """FastAPI-compatible maps data retrieval"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query with optional search
                base_query = f"SELECT * FROM {self.config.maps_table}"
                count_query = f"SELECT COUNT(*) FROM {self.config.maps_table}"
                params = []
                
                if search_term:
                    # Use exact column names from your Streamlit code
                    search_condition = """
                        WHERE [Number] LIKE ? 
                        OR [Drawer] LIKE ? 
                        OR [PropertyDetails] LIKE ?
                    """
                    base_query += search_condition
                    count_query += search_condition
                    
                    search_pattern = f"%{search_term}%"
                    params = [search_pattern, search_pattern, search_pattern]
                
                # Add ordering and pagination using Number (not MapID)
                base_query += " ORDER BY [Number] OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, limit])
                
                # Get total count
                count_params = params[:-2] if search_term else []
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data
                cursor.execute(base_query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                maps_data = []
                for row in rows:
                    map_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in map_dict.items():
                        if isinstance(value, datetime):
                            map_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            map_dict[key] = ""
                    maps_data.append(map_dict)
                
                # Calculate pagination info
                total_pages = (total_count + limit - 1) // limit
                current_page = (offset // limit) + 1
                
                result = {
                    "data": maps_data,
                    "total_count": total_count,
                    "current_page": current_page,
                    "total_pages": total_pages,
                    "has_next": current_page < total_pages,
                    "has_previous": current_page > 1
                }
                
                logger.info(f"Retrieved {len(maps_data)} maps (page {current_page}/{total_pages})")
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving maps data: {e}")
            return {"data": [], "total_count": 0, "current_page": 1, "total_pages": 0, "has_next": False, "has_previous": False}

    def get_map_by_track_number(self, track_number: int) -> Optional[Dict[str, Any]]:
        """Get map details by track number - matches Streamlit method"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT * FROM {self.config.maps_table} WHERE [Number] = ?"
                cursor.execute(query, [track_number])
                
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    map_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in map_dict.items():
                        if isinstance(value, datetime):
                            map_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            map_dict[key] = ""
                    
                    logger.debug(f"Retrieved map {track_number}")
                    return map_dict
                
                logger.debug(f"Map {track_number} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving map {track_number}: {e}")
            return None

    def get_map_by_id(self, map_number: int) -> Optional[Dict[str, Any]]:
        """Alias for get_map_by_track_number for FastAPI compatibility"""
        return self.get_map_by_track_number(map_number)

    def search_maps(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for maps based on search term - matches Streamlit method"""
        if not search_term or not search_term.strip():
            return self.get_beisman_data()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Search across all text columns
                query = f"""
                    SELECT * FROM {self.config.maps_table} 
                    WHERE CAST([Number] AS VARCHAR) LIKE ? 
                    OR [Drawer] LIKE ? 
                    OR [PropertyDetails] LIKE ?
                    ORDER BY [Number]
                """
                
                search_pattern = f"%{search_term}%"
                params = [search_pattern, search_pattern, search_pattern]
                
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                maps_data = []
                for row in rows:
                    map_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in map_dict.items():
                        if isinstance(value, datetime):
                            map_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            map_dict[key] = ""
                    maps_data.append(map_dict)
                
                logger.info(f"Search returned {len(maps_data)} maps for term: {search_term}")
                return maps_data
                
        except Exception as e:
            logger.error(f"Error searching maps: {e}")
            return []

    def insert_map(self, map_data: Dict[str, Any]) -> bool:
        """Insert a new map record - compatible with both Streamlit and FastAPI"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Handle both Streamlit format (trace_number, drawer, description) 
                # and FastAPI format (MapName, Location, Description)
                if 'MapName' in map_data:
                    # FastAPI format
                    trace_number = map_data.get('MapName')
                    drawer = map_data.get('Location', '')
                    description = map_data.get('Description', '')
                else:
                    # Streamlit format or direct parameters
                    trace_number = map_data.get('Number') or map_data.get('trace_number')
                    drawer = map_data.get('Drawer') or map_data.get('drawer')
                    description = map_data.get('PropertyDetails') or map_data.get('description')
                
                if not trace_number:
                    raise ValueError("Trace number is required")
                
                # Check if the tracking number already exists
                existing = self.get_map_by_track_number(trace_number)
                if existing:
                    logger.warning(f"Tracking number {trace_number} already exists")
                    return False
                
                # Insert with correct column names
                query = f"INSERT INTO {self.config.maps_table} ([Number], [Drawer], [PropertyDetails]) VALUES (?, ?, ?)"
                cursor.execute(query, [trace_number, drawer or '', description or ''])
                conn.commit()
                
                # Verify the insertion
                if self.get_map_by_track_number(trace_number):
                    logger.info(f"Successfully inserted new map: {trace_number}")
                    return True
                else:
                    logger.error("Failed to verify map insertion")
                    return False
                    
        except Exception as e:
            logger.error(f"Error inserting map: {e}")
            return False

    def update_map(self, map_number: int, map_data: Dict[str, Any]) -> bool:
        """Update an existing map record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic UPDATE query using correct column names
                update_fields = []
                values = []
                
                if 'Drawer' in map_data:
                    update_fields.append('[Drawer] = ?')
                    values.append(map_data['Drawer'])
                
                if 'PropertyDetails' in map_data or 'Description' in map_data:
                    update_fields.append('[PropertyDetails] = ?')
                    values.append(map_data.get('PropertyDetails') or map_data.get('Description'))
                
                if not update_fields:
                    logger.warning("No valid data provided for map update")
                    return False
                
                query = f"UPDATE {self.config.maps_table} SET {', '.join(update_fields)} WHERE [Number] = ?"
                values.append(map_number)
                
                cursor.execute(query, values)
                rows_affected = cursor.rowcount
                conn.commit()
                
                success = rows_affected > 0
                if success:
                    logger.info(f"Successfully updated map {map_number}")
                else:
                    logger.warning(f"Map update for Number {map_number} affected 0 rows")
                
                return success
                
        except Exception as e:
            logger.error(f"Error updating map {map_number}: {e}")
            return False

    def delete_map(self, map_number: int) -> bool:
        """Delete a map record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, delete associated entities
                cursor.execute(f"DELETE FROM {self.config.entities_table} WHERE [BeismanNumber] = ?", [map_number])
                
                # Then, delete the map using Number (not MapID)
                cursor.execute(f"DELETE FROM {self.config.maps_table} WHERE [Number] = ?", [map_number])
                rows_affected = cursor.rowcount
                conn.commit()
                
                success = rows_affected > 0
                if success:
                    logger.info(f"Successfully deleted map {map_number}")
                else:
                    logger.warning(f"Map deletion for Number {map_number} affected 0 rows")
                
                return success
                
        except Exception as e:
            logger.error(f"Error deleting map {map_number}: {e}")
            return False

    # Entity Operations (using correct column names: EntityName, BeismanNumber)
    
    def get_all_entities(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all entities from the database - matches Streamlit method"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = f"SELECT * FROM {self.config.entities_table} ORDER BY [EntityName] OFFSET ? ROWS"
                params = [offset]
                
                if limit is not None:
                    query += " FETCH NEXT ? ROWS ONLY"
                    params.append(limit)
                    
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                entities_data = []
                for row in rows:
                    entity_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in entity_dict.items():
                        if isinstance(value, datetime):
                            entity_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            entity_dict[key] = ""
                    entities_data.append(entity_dict)
                
                logger.info(f"Retrieved {len(entities_data)} entities")
                return entities_data
                
        except Exception as e:
            logger.error(f"Error retrieving entities: {e}")
            return []

    def get_entities_count(self) -> int:
        """Get the total number of entities in the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT COUNT(*) FROM {self.config.entities_table}"
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting entities count: {e}")
            return 0

    def get_entities_data(self, limit: int = 50, offset: int = 0, 
                         search_term: Optional[str] = None) -> Dict[str, Any]:
        """FastAPI-compatible entities data retrieval"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query with optional search
                base_query = f"SELECT * FROM {self.config.entities_table}"
                count_query = f"SELECT COUNT(*) FROM {self.config.entities_table}"
                params = []
                
                if search_term:
                    search_condition = " WHERE [EntityName] LIKE ? OR CAST([BeismanNumber] AS VARCHAR) LIKE ?"
                    base_query += search_condition
                    count_query += search_condition
                    
                    search_pattern = f"%{search_term}%"
                    params = [search_pattern, search_pattern]
                
                # Add ordering and pagination
                base_query += " ORDER BY [EntityName] OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, limit])
                
                # Get total count
                count_params = params[:-2] if search_term else []
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data
                cursor.execute(base_query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                entities_data = []
                for row in rows:
                    entity_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in entity_dict.items():
                        if isinstance(value, datetime):
                            entity_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            entity_dict[key] = ""
                    entities_data.append(entity_dict)
                
                # Calculate pagination info
                total_pages = (total_count + limit - 1) // limit
                current_page = (offset // limit) + 1
                
                result = {
                    "data": entities_data,
                    "total_count": total_count,
                    "current_page": current_page,
                    "total_pages": total_pages,
                    "has_next": current_page < total_pages,
                    "has_previous": current_page > 1
                }
                
                logger.info(f"Retrieved {len(entities_data)} entities (page {current_page}/{total_pages})")
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving entities data: {e}")
            return {"data": [], "total_count": 0, "current_page": 1, "total_pages": 0, "has_next": False, "has_previous": False}

    def search_entities(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for entities based on entity name - matches Streamlit method"""
        if not search_term or not search_term.strip():
            return self.get_all_entities()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = f"SELECT * FROM {self.config.entities_table} WHERE [EntityName] LIKE ? ORDER BY [EntityName]"
                search_pattern = f"%{search_term}%"
                
                cursor.execute(query, [search_pattern])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                entities_data = []
                for row in rows:
                    entity_dict = dict(zip(columns, row))
                    # Convert datetime objects to strings
                    for key, value in entity_dict.items():
                        if isinstance(value, datetime):
                            entity_dict[key] = value.strftime("%m/%d/%Y %I:%M:%S %p")
                        elif value is None:
                            entity_dict[key] = ""
                    entities_data.append(entity_dict)
                
                logger.info(f"Search returned {len(entities_data)} entities for term: {search_term}")
                return entities_data
                
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []

    def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Note: This assumes EntityID exists. If not, we might need to delete by EntityName + BeismanNumber
                cursor.execute(f"DELETE FROM {self.config.entities_table} WHERE [EntityID] = ?", [entity_id])
                rows_affected = cursor.rowcount
                conn.commit()
                
                success = rows_affected > 0
                if success:
                    logger.info(f"Successfully deleted entity {entity_id}")
                else:
                    logger.warning(f"Entity deletion for ID {entity_id} affected 0 rows")
                
                return success
                
        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            return False

    def get_entities_for_map(self, track_number: int) -> List[Dict[str, Any]]:
        """Get all entities for a given map"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = f"SELECT [EntityName] FROM {self.config.entities_table} WHERE [BeismanNumber] = ?"
                cursor.execute(query, [track_number])
                
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                entities_data = []
                for row in rows:
                    entity_dict = dict(zip(columns, row))
                    entities_data.append(entity_dict)
                
                return entities_data
                
        except Exception as e:
            logger.error(f"Error getting entities for map {track_number}: {e}")
            return []

    def add_entity_to_map(self, track_number: int, entity_name: str) -> tuple[bool, str]:
        """Add a new entity for a map"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"INSERT INTO {self.config.entities_table} ([BeismanNumber], [EntityName]) VALUES (?, ?)",
                              [track_number, entity_name])
                conn.commit()
                
                logger.info(f"Successfully added entity {entity_name} to map {track_number}")
                return True, "Entity added successfully."
                
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return False, f"Error adding entity: {str(e)}"

    def remove_entity_from_map(self, track_number: int, entity_name: str) -> tuple[bool, str]:
        """Remove an entity associated with a map"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"DELETE FROM {self.config.entities_table} WHERE [BeismanNumber] = ? AND [EntityName] = ?",
                              [track_number, entity_name])
                rows_affected = cursor.rowcount
                conn.commit()
                
                if rows_affected > 0:
                    logger.info(f"Successfully removed entity {entity_name} from map {track_number}")
                    return True, "Entity removed successfully."
                else:
                    return False, "Entity not found."
                
        except Exception as e:
            logger.error(f"Error removing entity: {e}")
            return False, f"Error removing entity: {str(e)}"

    def close_connection(self):
        """Close database connection - compatibility method"""
        # This is handled by context managers, but keeping for compatibility
        pass

# Create a global instance
db_manager = DatabaseManager()
