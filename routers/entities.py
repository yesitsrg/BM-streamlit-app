from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from models import (
    EntityResponse, EntityListResponse, APIResponse, DeleteResponse, 
    SearchRequest
)
from database import DatabaseManager
from middleware import require_admin, optional_auth, require_auth

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=EntityListResponse)
async def get_entities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    request: Request = None,
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get paginated list of entities with optional search"""
    try:
        db_manager = DatabaseManager()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get entities data using the corrected method
        result = db_manager.get_entities_data(
            limit=page_size,
            offset=offset,
            search_term=search
        )
        
        # Convert to response format - data already has correct column names
        entities_data = []
        for entity_item in result["data"]:
            try:
                entities_data.append(EntityResponse(**entity_item))
            except Exception as e:
                logger.error(f"Error creating EntityResponse for item {entity_item}: {e}")
                # Try with default values if required fields are missing
                entity_item_safe = {
                    'EntityName': entity_item.get('EntityName', ''),
                    'BeismanNumber': entity_item.get('BeismanNumber', ''),
                    'EntityID': entity_item.get('EntityID'),
                    'CreatedDate': entity_item.get('CreatedDate')
                }
                try:
                    entities_data.append(EntityResponse(**entity_item_safe))
                except Exception as e2:
                    logger.error(f"Error creating EntityResponse even with safe data {entity_item_safe}: {e2}")
                    continue
        
        response = EntityListResponse(
            data=entities_data,
            total_count=result["total_count"],
            current_page=result["current_page"],
            total_pages=result["total_pages"],
            search_term=search,
            has_next=result.get("has_next", False),
            has_previous=result.get("has_previous", False)
        )
        
        logger.info(f"Retrieved {len(entities_data)} entities for page {page}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving entities: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve entities: {str(e)}"
        )

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get a specific entity by ID"""
    try:
        db_manager = DatabaseManager()
        
        # Get all entities and filter by EntityID (if it exists)
        # This is a workaround since we don't have a specific get_entity_by_id method
        result = db_manager.get_entities_data(limit=1000, offset=0)
        
        entity_data = None
        for entity in result["data"]:
            if entity.get("EntityID") == entity_id:
                entity_data = entity
                break
        
        if not entity_data:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )
        
        logger.info(f"Retrieved entity {entity_id}")
        return EntityResponse(**entity_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving entity {entity_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve entity: {str(e)}"
        )

@router.delete("/{entity_id}", response_model=DeleteResponse)
async def delete_entity(
    entity_id: int,
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Delete an entity (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Check if entity exists first
        result = db_manager.get_entities_data(limit=1000, offset=0)
        entity_exists = any(entity.get("EntityID") == entity_id for entity in result["data"])
        
        if not entity_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )
        
        # Delete the entity using corrected method
        success = db_manager.delete_entity(entity_id)
        
        if success:
            logger.info(f"Entity {entity_id} deleted by {user.get('username')}")
            return DeleteResponse(
                success=True,
                message="Entity deleted successfully",
                deleted_id=entity_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to delete entity"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete entity: {str(e)}"
        )

@router.post("/search", response_model=EntityListResponse)
async def search_entities(
    search_request: SearchRequest,
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Advanced search for entities"""
    try:
        db_manager = DatabaseManager()
        
        # Calculate offset
        offset = (search_request.page - 1) * search_request.page_size
        
        # Get entities data with search using corrected method
        result = db_manager.get_entities_data(
            limit=search_request.page_size,
            offset=offset,
            search_term=search_request.search_term
        )
        
        # Convert to response format
        entities_data = []
        for entity_item in result["data"]:
            try:
                entities_data.append(EntityResponse(**entity_item))
            except Exception as e:
                logger.error(f"Error creating EntityResponse for item {entity_item}: {e}")
                continue
        
        response = EntityListResponse(
            data=entities_data,
            total_count=result["total_count"],
            current_page=result["current_page"],
            total_pages=result["total_pages"],
            search_term=search_request.search_term,
            has_next=result.get("has_next", False),
            has_previous=result.get("has_previous", False)
        )
        
        logger.info(f"Search returned {len(entities_data)} entities for term: {search_request.search_term}")
        return response
        
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search entities: {str(e)}"
        )

@router.get("/export/csv")
async def export_entities_csv(
    search: Optional[str] = Query(None, description="Search term for filtering"),
    user: Dict[str, Any] = Depends(require_admin)
):
    """Export entities data as CSV (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Get all entities data (no pagination for export)
        if search:
            all_entities = db_manager.search_entities(search)
        else:
            all_entities = db_manager.get_all_entities(limit=10000)  # Large limit for export
        
        if not all_entities:
            raise HTTPException(
                status_code=404,
                detail="No entities found for export"
            )
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        
        # Use actual column names from data
        fieldnames = list(all_entities[0].keys()) if all_entities else ['EntityName', 'BeismanNumber']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_entities)
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV response
        from fastapi.responses import Response
        
        timestamp = db_manager.get_current_timestamp().replace('/', '-').replace(' ', '_').replace(':', '-')
        filename = f"beisman_entities_export_{timestamp}.csv"
        
        logger.info(f"Entities CSV export generated by {user.get('username')}: {len(all_entities)} records")
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting entities CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export entities: {str(e)}"
        )

@router.get("/stats/summary")
async def get_entities_stats(
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get entities statistics summary"""
    try:
        db_manager = DatabaseManager()
        
        # Get total count
        total_entities = db_manager.get_entities_count()
        
        stats = {
            "total_entities": total_entities,
            "timestamp": db_manager.get_current_timestamp()
        }
        
        # Add admin-specific stats if user is admin
        if user and user.get('is_admin'):
            stats.update({
                "database_status": "connected" if db_manager.test_connection() else "disconnected",
                "last_update": db_manager.get_current_timestamp()
            })
        
        logger.info(f"Entities stats retrieved: {total_entities} total entities")
        
        return APIResponse(
            success=True,
            message="Entities statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting entities stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entities statistics: {str(e)}"
        )

@router.post("/bulk-delete", response_model=APIResponse)
async def bulk_delete_entities(
    entity_ids: list[int],
    request: Request,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Bulk delete multiple entities (Admin only)"""
    try:
        if not entity_ids:
            raise HTTPException(
                status_code=400,
                detail="No entity IDs provided"
            )
        
        if len(entity_ids) > 100:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete more than 100 entities at once"
            )
        
        db_manager = DatabaseManager()
        
        deleted_count = 0
        failed_deletes = []
        
        for entity_id in entity_ids:
            try:
                success = db_manager.delete_entity(entity_id)
                if success:
                    deleted_count += 1
                else:
                    failed_deletes.append(entity_id)
            except Exception as e:
                logger.error(f"Failed to delete entity {entity_id}: {e}")
                failed_deletes.append(entity_id)
        
        message = f"Successfully deleted {deleted_count} entities"
        if failed_deletes:
            message += f", failed to delete {len(failed_deletes)} entities (IDs: {failed_deletes})"
        
        logger.info(f"Bulk delete completed by {user.get('username')}: {deleted_count} deleted, {len(failed_deletes)} failed")
        
        return APIResponse(
            success=True,
            message=message,
            data={
                "deleted_count": deleted_count,
                "failed_count": len(failed_deletes),
                "failed_ids": failed_deletes
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

@router.get("/types/list")
async def get_entity_types(
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get list of unique entity types"""
    try:
        db_manager = DatabaseManager()
        
        # Get all entities to extract unique types
        all_entities = db_manager.get_all_entities(limit=10000)
        
        entity_types = set()
        for entity in all_entities:
            entity_type = entity.get("EntityType")
            if entity_type:
                entity_types.add(entity_type)
        
        types_list = sorted(list(entity_types))
        
        logger.info(f"Retrieved {len(types_list)} unique entity types")
        
        return APIResponse(
            success=True,
            message="Entity types retrieved successfully",
            data={
                "entity_types": types_list,
                "count": len(types_list)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting entity types: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entity types: {str(e)}"
        )

@router.get("/filter/by-type")
async def filter_entities_by_type(
    entity_type: str = Query(..., description="Entity type to filter by"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Filter entities by type"""
    try:
        db_manager = DatabaseManager()
        
        # Get all entities and filter in Python (since EntityType might not exist in your schema)
        all_entities = db_manager.get_all_entities(limit=10000)
        
        # Filter by entity type (if the column exists)
        filtered_entities = [
            entity for entity in all_entities 
            if entity.get("EntityType", "").lower() == entity_type.lower()
        ]
        
        # Apply pagination
        total_count = len(filtered_entities)
        offset = (page - 1) * page_size
        paginated_entities = filtered_entities[offset:offset + page_size]
        
        # Convert to response format
        entities_data = []
        for entity_item in paginated_entities:
            try:
                entities_data.append(EntityResponse(**entity_item))
            except Exception as e:
                logger.error(f"Error creating EntityResponse for item {entity_item}: {e}")
                continue
        
        total_pages = (total_count + page_size - 1) // page_size
        
        response = EntityListResponse(
            data=entities_data,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            search_term=f"Type: {entity_type}",
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        logger.info(f"Filtered {len(entities_data)} entities by type: {entity_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error filtering entities by type: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to filter entities: {str(e)}"
        )

@router.get("/map/{map_number}")
async def get_entities_for_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    user: Optional[Dict[str, Any]] = Depends(optional_auth)
):
    """Get all entities associated with a specific map"""
    try:
        db_manager = DatabaseManager()
        
        # Use the corrected method from your Streamlit code
        entities_data = db_manager.get_entities_for_map(map_number)
        
        if not entities_data:
            return APIResponse(
                success=True,
                message="No entities found for this map",
                data={"entities": [], "map_number": map_number}
            )
        
        logger.info(f"Retrieved {len(entities_data)} entities for map {map_number}")
        
        return APIResponse(
            success=True,
            message=f"Found {len(entities_data)} entities for map {map_number}",
            data={
                "entities": entities_data,
                "map_number": map_number,
                "count": len(entities_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting entities for map {map_number}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entities for map: {str(e)}"
        )

@router.post("/map/{map_number}/add", response_model=APIResponse)
async def add_entity_to_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    entity_name: str = Query(..., description="Name of entity to add"),
    request: Request = None,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Add an entity to a map (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Use the corrected method from your Streamlit code
        success, message = db_manager.add_entity_to_map(map_number, entity_name)
        
        if success:
            logger.info(f"Entity '{entity_name}' added to map {map_number} by {user.get('username')}")
            return APIResponse(
                success=True,
                message=message,
                data={
                    "map_number": map_number,
                    "entity_name": entity_name
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding entity to map: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add entity to map: {str(e)}"
        )

@router.delete("/map/{map_number}/{entity_name}", response_model=APIResponse)
async def remove_entity_from_map(
    map_number: str,  # CHANGED: from int to str to handle "003-A" format
    entity_name: str,
    request: Request = None,
    user: Dict[str, Any] = Depends(require_admin)
):
    """Remove an entity from a map (Admin only)"""
    try:
        db_manager = DatabaseManager()
        
        # Use the corrected method from your Streamlit code
        success, message = db_manager.remove_entity_from_map(map_number, entity_name)
        
        if success:
            logger.info(f"Entity '{entity_name}' removed from map {map_number} by {user.get('username')}")
            return APIResponse(
                success=True,
                message=message,
                data={
                    "map_number": map_number,
                    "entity_name": entity_name
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing entity from map: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove entity from map: {str(e)}"
        )