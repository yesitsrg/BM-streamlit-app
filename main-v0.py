"""
Beisman Maps FastAPI Application
New Mexico Highlands University

A modern web application for managing Beisman Maps with Windows 95 aesthetic.
Migrated from Streamlit to FastAPI + HTML/CSS - Replicating exact navigation pattern.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Import application modules
from database import DatabaseManager
from routers import auth, maps, entities

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beisman_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database instance
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global db_manager
    
    # Startup
    logger.info("Starting Beisman Maps Application...")
    
    # Initialize database
    db_manager = DatabaseManager()
    try:
        if db_manager.test_connection():
            logger.info("✅ Database connection successful")
        else:
            logger.warning("❌ Database connection failed - Check configuration")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    # Create static directories if they don't exist
    static_dirs = ["static", "static/css", "static/js", "static/images"]
    for dir_path in static_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    logger.info("🚀 Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Beisman Maps Application...")
    if db_manager:
        db_manager.close_connection()
    logger.info("👋 Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Beisman Maps Application",
    description="A Windows 95-style web application for managing Beisman Maps - New Mexico Highlands University",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(entities.router, prefix="/api/entities", tags=["Entities"])

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    logger.error(f"Internal server error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": "Please contact the system administrator"
        }
    )

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_main_page():
    """Serve the main HTML page with dynamic navigation pattern"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Beisman Maps - New Mexico Highlands University</title>
        <meta name="description" content="Beisman Maps management system for New Mexico Highlands University">
        <meta name="author" content="New Mexico Highlands University">
        <link rel="stylesheet" href="/static/css/windows95.css">
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
    </head>
    <body>
        <div id="app" class="app-container">
            <!-- Main Windows 95 Container -->
            <div class="main-container">
                <!-- Header Section with Logo/Icon Placeholder -->
                <div class="header-section">
                    <div class="header-logo">
                        <img src="/static/css/nmhu-logo.png" alt="New Mexico Highlands University Logo" class="logo-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="logo-placeholder" style="display: none;">
                            <span class="logo-text">New Mexico Highlands University</span>
                        </div>
                    </div>
                </div>

                <!-- Windows 95 Header with Title Bar -->
                <div class="windows-header">
                    <div class="header-title" id="page-title">Beisman Map Menu</div>
                    <!-- Admin Button Container (Top Right) -->
                    <div class="admin-button-container">
                        <a href="#" id="admin-link" class="admin-link">Admin Login</a>
                    </div>
                </div>

                <!-- Main Content Area (Dynamic) -->
                <div class="content-area" id="content-area">
                    <!-- Content will be dynamically loaded here based on current page -->
                    <!-- This replicates the exact pattern from your Streamlit app -->
                    
                    <!-- Default Home Screen Content -->
                    <div id="home-content" class="page-content">
                        <div class="nav-container">
                            <!-- JavaScript will replace this content -->
                            <div class="loading-text">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Login Modal (Windows 95 Style) -->
        <div id="login-modal" class="modal hidden">
            <div class="modal-backdrop" onclick="closeLoginModal()"></div>
            <div class="modal-content windows-dialog">
                <div class="windows-header">
                    <div class="header-title">Administrator Login</div>
                    <button class="close-button" onclick="closeLoginModal()">×</button>
                </div>
                <div class="dialog-body">
                    <form id="login-form">
                        <div class="form-group">
                            <label for="username">Username:</label>
                            <input type="text" id="username" name="username" class="windows-input" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Password:</label>
                            <input type="password" id="password" name="password" class="windows-input" required>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="windows-button primary">OK</button>
                            <button type="button" class="windows-button" onclick="closeLoginModal()">Cancel</button>
                        </div>
                        <div id="login-error" class="login-error hidden"></div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Loading overlay -->
        <div id="loading-overlay" class="loading-overlay hidden">
            <div class="loading-content">
                <div class="loading-text">Loading...</div>
            </div>
        </div>

        <!-- JavaScript Application -->
        <script src="/static/js/app.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    try:
        db_status = db_manager.test_connection() if db_manager else False
        
        health_data = {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "timestamp": db_manager.get_current_timestamp() if db_manager else None,
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        status_code = 200 if db_status else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "success": db_status,
                "message": "System is healthy" if db_status else "System degraded - database issues",
                "data": health_data
            }
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Health check failed",
                "data": {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": None
                }
            }
        )

@app.get("/api/info", tags=["System"])
async def app_info():
    """Application information endpoint"""
    return {
        "name": "Beisman Maps Application",
        "version": "1.0.0",
        "description": "FastAPI-based map management system with Windows 95 aesthetic",
        "university": "New Mexico Highlands University",
        "tech_stack": {
            "backend": "FastAPI",
            "frontend": "HTML/CSS/JavaScript",
            "database": "SQL Server",
            "authentication": "Session-based"
        },
        "features": [
            "Browse Maps",
            "Browse Entities", 
            "Admin Authentication",
            "CRUD Operations",
            "Data Export",
            "Windows 95 Theme"
        ],
        "admin_credentials": {
            "note": "Default credentials should be changed in production",
            "username": "admin",
            "password": "admin"
        }
    }

if __name__ == "__main__":
    # Development server configuration
    print("=" * 60)
    print("  🏫 Beisman Maps Application")
    print("  🎓 New Mexico Highlands University")
    print("=" * 60)
    print("  🚀 Starting development server...")
    print("  📍 Application: http://localhost:8000")
    print("  📚 API Docs: http://localhost:8000/docs")
    print("  ❤️  Health Check: http://localhost:8000/api/health")
    print("  🔑 Default Admin: admin/admin")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )