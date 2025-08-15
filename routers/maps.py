from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from models import (
    MapCreate, MapUpdate, MapResponse, MapListResponse, 
    APIResponse, DeleteResponse, SearchRequest, convert_fastapi_to_db_format
)
from database import DatabaseManager
from middleware import require_admin, optional_auth, require_auth

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=MapListResponse)
async def get_maps(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    request: Request = None,
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get paginated list of maps with optional search"""
    try:
        db_manager = DatabaseManager()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get maps data using the corrected method
        result = db_manager.get_maps_data(
            limit=page_size,
            offset=offset,
            search_term=search
        )
        
        # Convert to response format - data already has correct column names
        maps_data = []
        for map_item in result["data"]:
            try:
                maps_data.append(MapResponse(**map_item))
            except Exception as e:
                logger.error(f"Error creating MapResponse for item {map_item}: {e}")
                continue
        
        response = MapListResponse(
            data=maps_data,
            total_count=result["total_count"],
            current_page=result["current_page"],
            total_pages=result["total_pages"],
            search_term=search,
            has_next=result.get("has_next", False),
            has_previous=result.get("has_previous", False)
        )
        
        logger.info(f"Retrieved {len(maps_data)} maps for page {page}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving maps: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve maps: {str(e)}"
        )

@router.get("/{map_number}", response_model=MapResponse)
async def get_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get a specific map by Number (not MapID)"""
    try:
        db_manager = DatabaseManager()
        
        # Use the corrected method that uses Number as primary key
        map_data = db_manager.get_map_by_track_number(map_number)
        
        if not map_data:
            raise HTTPException(
                status_code=404,
                detail=f"Map with Number {map_number} not found"
            )
        
        logger.info(f"Retrieved map {map_number}")
        return MapResponse(**map_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving map {map_number}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve map: {str(e)}"
        )

@router.post("", response_model=APIResponse)
async def create_map(
    map_data: MapCreate,
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Create a new map (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Convert Pydantic model to dict and handle format conversion
        map_dict = map_data.dict(exclude_none=True)
        
        # Convert FastAPI format to database format if needed
        db_format = convert_fastapi_to_db_format(map_dict)
        
        # Ensure we have the required Number field
        if not db_format.get('Number'):
            if map_dict.get('MapName'):
                db_format['Number'] = map_dict['MapName']
            else:
                raise HTTPException(status_code=400, detail="Number (or MapName) is required")
        
        # Set created by to current user if not provided
        if not db_format.get('CreatedBy'):
            db_format['CreatedBy'] = user.get('username')
        
        # Insert the map using corrected method
        success = db_manager.insert_map(db_format)
        
        if success:
            logger.info(f"Map '{db_format.get('Number')}' created by {user.get('username')}")
            return APIResponse(
                success=True,
                message="Map created successfully",
                data={"map_number": db_format.get('Number')}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to create map - Number might already exist"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating map: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create map: {str(e)}"
        )

@router.put("/{map_number}", response_model=APIResponse)
async def update_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    map_data: MapUpdate,
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Update an existing map (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Check if map exists using Number
        existing_map = db_manager.get_map_by_track_number(map_number)
        if not existing_map:
            raise HTTPException(
                status_code=404,
                detail=f"Map with Number {map_number} not found"
            )
        
        # Convert Pydantic model to dict, excluding None values
        update_dict = map_data.dict(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=400,
                detail="No update data provided"
            )
        
        # Convert to database format
        db_format = convert_fastapi_to_db_format(update_dict)
        
        # Add modification tracking
        db_format['ModifiedBy'] = user.get('username')
        
        # Update the map using corrected method
        success = db_manager.update_map(map_number, db_format)
        
        if success:
            logger.info(f"Map {map_number} updated by {user.get('username')}")
            return APIResponse(
                success=True,
                message="Map updated successfully",
                data={"map_number": map_number}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to update map"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating map {map_number}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update map: {str(e)}"
        )

@router.delete("/{map_number}", response_model=DeleteResponse)
async def delete_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Delete a map (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Check if map exists using Number
        existing_map = db_manager.get_map_by_track_number(map_number)
        if not existing_map:
            raise HTTPException(
                status_code=404,
                detail=f"Map with Number {map_number} not found"
            )
        
        # Delete the map using corrected method
        success = db_manager.delete_map(map_number)
        
        if success:
            logger.info(f"Map {map_number} deleted by {user.get('username')}")
            return DeleteResponse(
                success=True,
                message="Map deleted successfully",
                deleted_id=None  # Changed: can't use int for string IDs
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to delete map"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting map {map_number}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete map: {str(e)}"
        )

@router.post("/search", response_model=MapListResponse)
async def search_maps(
    search_request: SearchRequest,
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Advanced search for maps"""
    try:
        db_manager = DatabaseManager()
        
        # Calculate offset
        offset = (search_request.page - 1) * search_request.page_size
        
        # Get maps data with search using corrected method
        result = db_manager.get_maps_data(
            limit=search_request.page_size,
            offset=offset,
            search_term=search_request.search_term
        )
        
        # Convert to response format
        maps_data = []
        for map_item in result["data"]:
            try:
                maps_data.append(MapResponse(**map_item))
            except Exception as e:
                logger.error(f"Error creating MapResponse for item {map_item}: {e}")
                continue
        
        response = MapListResponse(
            data=maps_data,
            total_count=result["total_count"],
            current_page=result["current_page"],
            total_pages=result["total_pages"],
            search_term=search_request.search_term,
            has_next=result.get("has_next", False),
            has_previous=result.get("has_previous", False)
        )
        
        logger.info(f"Search returned {len(maps_data)} maps for term: {search_request.search_term}")
        return response
        
    except Exception as e:
        logger.error(f"Error searching maps: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search maps: {str(e)}"
        )

@router.get("/export/csv")
async def export_maps_csv(
    search: Optional[str] = Query(None, description="Search term for filtering"),
    user: Dict[str, Any] = Depends(require_admin)
):
    """Export maps data as CSV (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Get all maps data (no pagination for export)
        if search:
            all_maps = db_manager.search_maps(search)
        else:
            all_maps = db_manager.get_beisman_data(limit=10000)  # Large limit for export
        
        if not all_maps:
            raise HTTPException(
                status_code=404,
                detail="No maps found for export"
            )
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        
        # Use actual column names from data
        fieldnames = list(all_maps[0].keys()) if all_maps else ['Number', 'Drawer', 'PropertyDetails']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_maps)
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV response
        from fastapi.responses import Response
        
        timestamp = db_manager.get_current_timestamp().replace('/', '-').replace(' ', '_').replace(':', '-')
        filename = f"beisman_maps_export_{timestamp}.csv"
        
        logger.info(f"Maps CSV export generated by {user.get('username')}: {len(all_maps)} records")
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting maps CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export maps: {str(e)}"
        )

@router.get("/stats/summary")
async def get_maps_stats(
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get maps statistics summary"""
    try:
        db_manager = DatabaseManager()
        
        # Get total count
        total_maps = db_manager.get_beisman_data_count()
        
        stats = {
            "total_maps": total_maps,
            "timestamp": db_manager.get_current_timestamp()
        }
        
        # Add admin-specific stats if user is admin
        if user and user.get('is_admin'):
            stats.update({
                "database_status": "connected" if db_manager.test_connection() else "disconnected",
                "last_update": db_manager.get_current_timestamp()
            })
        
        logger.info(f"Maps stats retrieved: {total_maps} total maps")
        
        return APIResponse(
            success=True,
            message="Maps statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting maps stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get maps statistics: {str(e)}"
        )

@router.post("/bulk-delete", response_model=APIResponse)
async def bulk_delete_maps(
    map_numbers: list[str],  # CHANGED: from list[int] to list[str] to handle "003-A" format
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Bulk delete multiple maps (Admin only)"""
    try:
        if not map_numbers:
            raise HTTPException(
                status_code=400,
                detail="No map numbers provided"
            )
        
        if len(map_numbers) > 100:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete more than 100 maps at once"
            )
        
        db_manager = DatabaseManager()
        
        deleted_count = 0
        failed_deletes = []
        
        for map_number in map_numbers:
            try:
                success = db_manager.delete_map(map_number)
                if success:
                    deleted_count += 1
                else:
                    failed_deletes.append(map_number)
            except Exception as e:
                logger.error(f"Failed to delete map {map_number}: {e}")
                failed_deletes.append(map_number)
        
        message = f"Successfully deleted {deleted_count} maps"
        if failed_deletes:
            message += f", failed to delete {len(failed_deletes)} maps (Numbers: {failed_deletes})"
        
        logger.info(f"Bulk delete completed by {user.get('username')}: {deleted_count} deleted, {len(failed_deletes)} failed")
        
        return APIResponse(
            success=True,
            message=message,
            data={
                "deleted_count": deleted_count,
                "failed_count": len(failed_deletes),
                "failed_numbers": failed_deletes
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete: {str(e)}"
        )