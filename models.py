"""
Pydantic Models - Fixed to match exact Streamlit database column structure
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Authentication Models
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    remember_me: bool = False

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_info: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class UserSession(BaseModel):
    username: str
    is_admin: bool
    display_name: str
    session_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None

# Map Models - Using exact column names: Number, Drawer, PropertyDetails
class MapBase(BaseModel):
    Number: Optional[str] = Field(None, max_length=50)  # Changed from MapName to Number
    Drawer: Optional[str] = Field(None, max_length=255)  # Keep as is
    PropertyDetails: Optional[str] = Field(None, max_length=1000)  # Changed from Description to PropertyDetails
    
class MapCreate(MapBase):
    """Model for creating a new map"""
    Number: str = Field(..., min_length=1, max_length=50)  # Number is required
    
    # Allow FastAPI format input and convert to database format
    MapName: Optional[str] = Field(None, max_length=50)  # For FastAPI compatibility
    Description: Optional[str] = Field(None, max_length=1000)  # For FastAPI compatibility
    Location: Optional[str] = Field(None, max_length=255)  # For FastAPI compatibility
    CreatedBy: Optional[str] = Field(None, max_length=100)  # For FastAPI compatibility

class MapUpdate(MapBase):
    """Model for updating an existing map"""
    pass

class MapResponse(MapBase):
    """Model for map response - matches exact database columns"""
    Number: str  # Primary key - required in response
    Drawer: Optional[str] = None
    PropertyDetails: Optional[str] = None
    CreatedDate: Optional[str] = None  # If this column exists
    ModifiedDate: Optional[str] = None  # If this column exists
    
    class Config:
        from_attributes = True

class MapListResponse(BaseModel):
    """Response model for paginated map list"""
    data: List[MapResponse]
    total_count: int
    current_page: int
    total_pages: int
    search_term: Optional[str] = None
    has_next: bool = False
    has_previous: bool = False

# Entity Models - Using exact column names: EntityName, BeismanNumber
class EntityBase(BaseModel):
    EntityName: Optional[str] = Field(None, max_length=255)
    BeismanNumber: Optional[str] = Field(None, max_length=50)  # References map Number
    
class EntityResponse(EntityBase):
    """Model for entity response - matches exact database columns"""
    EntityName: str  # Required in response
    BeismanNumber: str  # Required in response
    EntityID: Optional[int] = None  # If this column exists
    CreatedDate: Optional[str] = None  # If this column exists
    
    class Config:
        from_attributes = True

class EntityListResponse(BaseModel):
    """Response model for paginated entity list"""
    data: List[EntityResponse]
    total_count: int
    current_page: int
    total_pages: int
    search_term: Optional[str] = None
    has_next: bool = False
    has_previous: bool = False

# Search and Pagination Models
class SearchRequest(BaseModel):
    search_term: Optional[str] = Field(None, max_length=255)
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=1000)

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=1000)
    search: Optional[str] = Field(None, max_length=255)

# API Response Models
class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    database: str
    timestamp: Optional[str] = None
    error: Optional[str] = None

# Delete Models
class DeleteRequest(BaseModel):
    """Model for delete operations"""
    id: int = Field(..., ge=1)
    confirm: bool = Field(True)

class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    success: bool
    message: str
    deleted_id: Optional[int] = None

# Session Models
class SessionInfo(BaseModel):
    """Session information model"""
    is_authenticated: bool
    is_admin: bool
    username: Optional[str] = None
    display_name: Optional[str] = None
    session_id: Optional[str] = None

# Form Data Models (for frontend forms)
class MapFormData(BaseModel):
    """Model for map form data from frontend - converts between formats"""
    # Accept both formats for compatibility
    Number: Optional[str] = Field(None, min_length=1, max_length=50)
    Drawer: Optional[str] = Field(None, max_length=255)
    PropertyDetails: Optional[str] = Field(None, max_length=1000)
    
    # FastAPI format (will be converted)
    MapName: Optional[str] = Field(None, min_length=1, max_length=50)
    Description: Optional[str] = Field(None, max_length=1000)
    Location: Optional[str] = Field(None, max_length=255)
    CreatedBy: Optional[str] = Field(None, max_length=100)
    
    class Config:
        populate_by_name = True

# Status and Error Models
class StatusMessage(BaseModel):
    """Model for status messages displayed in the golden box"""
    type: str = Field(..., pattern="^(error|warning|info|success)$")  # Fixed: pattern instead of regex
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None
    show_suggestions: bool = True
    
class DatabaseError(BaseModel):
    """Model for database error information"""
    error_code: str
    error_message: str
    timestamp: str
    session_id: Optional[str] = None
    suggested_actions: List[str] = [
        "Wait a few minutes and try again",
        "Check your internet connection", 
        "Go back to the previous page",
        "Contact the system administrator"
    ]

# Navigation Models
class NavigationState(BaseModel):
    """Model for tracking navigation state"""
    current_page: str
    page_title: str
    is_admin_page: bool = False
    breadcrumbs: List[str] = []

# Validation Models
class ValidationError(BaseModel):
    """Model for validation errors"""
    field: str
    message: str
    value: Optional[Any] = None

class ValidationResponse(BaseModel):
    """Response model for validation results"""
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[str] = []

# Streamlit Compatibility Models
class StreamlitMapData(BaseModel):
    """Model that matches Streamlit's expected map data format"""
    trace_number: str = Field(..., min_length=1)
    drawer: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    
    def to_database_format(self) -> Dict[str, Any]:
        """Convert to database column format"""
        return {
            'Number': self.trace_number,
            'Drawer': self.drawer,
            'PropertyDetails': self.description
        }

class StreamlitEntityData(BaseModel):
    """Model that matches Streamlit's expected entity data format"""
    entity_name: str = Field(..., min_length=1)
    beisman_number: str = Field(..., min_length=1)
    
    def to_database_format(self) -> Dict[str, Any]:
        """Convert to database column format"""
        return {
            'EntityName': self.entity_name,
            'BeismanNumber': self.beisman_number
        }

# Conversion helper functions
def convert_fastapi_to_db_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert FastAPI format to database format"""
    db_data = {}
    
    # Map conversions
    if 'MapName' in data:
        db_data['Number'] = data['MapName']
    if 'Description' in data:
        db_data['PropertyDetails'] = data['Description']
    if 'Location' in data:
        db_data['Drawer'] = data['Location']
    
    # Keep database format fields as-is
    for key in ['Number', 'Drawer', 'PropertyDetails', 'CreatedBy']:
        if key in data:
            db_data[key] = data[key]
    
    return db_data

def convert_db_to_response_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert database format to response format"""
    # Database format is already correct, just ensure all expected fields exist
    response_data = data.copy()
    
    # Ensure required fields exist
    if 'Number' not in response_data:
        response_data['Number'] = ''
    if 'Drawer' not in response_data:
        response_data['Drawer'] = ''
    if 'PropertyDetails' not in response_data:
        response_data['PropertyDetails'] = ''
    
    return response_data
