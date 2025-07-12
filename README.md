# Beisman Maps Management System

A modular Streamlit application for managing Beisman Maps with a Windows 95-style interface.

## Project Structure

```
beisman_maps/
├── main.py                 # Main application entry point
├── config.py               # Configuration settings
├── styles.py               # CSS styles
├── database.py             # Database operations
├── auth.py                 # Authentication management
├── utils.py                # Utility functions
├── components.py           # Reusable UI components
├── pages.py                # Page handlers
├── router.py               # Application routing
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Module Overview

### Core Modules

1. **config.py** - Centralized configuration management
   - Database connection settings
   - Authentication credentials
   - Application settings
   - Session state defaults

2. **styles.py** - CSS styling
   - Windows 95-style interface
   - Responsive design elements
   - Custom component styling

3. **database.py** - Database operations
   - Connection management
   - CRUD operations
   - Data retrieval and search
   - Error handling

4. **auth.py** - Authentication system
   - Login/logout functionality
   - Credential validation
   - Session management
   - Admin access control

5. **utils.py** - Utility functions
   - Session state management
   - Navigation helpers
   - Text formatting
   - App rerun compatibility

6. **components.py** - Reusable UI components
   - Window headers
   - Forms and containers
   - Data tables
   - Navigation elements
   - Status messages

7. **pages.py** - Page handlers
   - Individual page logic
   - User interactions
   - Data display
   - Form handling

8. **router.py** - Application routing
   - Page navigation
   - Access control
   - Route management

9. **main.py** - Application entry point
   - Page configuration
   - Style loading
   - Application initialization

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection in `config.py`

3. Run the application:
```bash
streamlit run main.py
```

## Features

- **Windows 95-style Interface**: Authentic retro styling
- **Admin Authentication**: Secure login system
- **Database Integration**: SQL Server connectivity
- **Map Browsing**: Search and display maps
- **Modular Architecture**: Easy to extend and maintain
- **Error Handling**: Robust error management

## Usage

1. **Main Screen**: Access Browse Maps and Browse Entities
2. **Admin Login**: Click "Admin Login" (default: admin/admin)
3. **Admin Panel**: Access all administrative functions
4. **Browse Maps**: Search and view map data
5. **CRUD Operations**: Insert, update, delete functionality (placeholders ready)

## Extending the Application

### Adding New Pages

1. Create page handler method in `pages.py`
2. Add route in `router.py`
3. Add navigation button in appropriate parent page

### Adding New Database Operations

1. Add method to `DatabaseManager` class in `database.py`
2. Call from appropriate page handler
3. Handle success/error states

### Adding New UI Components

1. Add static method to `UIComponents` class in `components.py`
2. Use in page handlers for consistent styling

### Configuration Changes

1. Update appropriate section in `config.py`
2. Import and use in relevant modules

## Database Schema

The application expects a SQL Server database with the following:
- Database: `tempdb` (configurable)
- Table: `BeismanDB.dbo.beisman` (configurable)
- Connection: Windows Authentication (configurable)

## Security Notes

- Default admin credentials should be changed in production
- Database connection uses Windows Authentication
- Session state is not persistent across browser sessions

## Development

The modular structure makes it easy to:
- Add new functionality
- Modify existing features
- Test individual components
- Maintain code quality

Each module has a specific responsibility and can be developed independently while maintaining the overall application architecture.

## Future Enhancements

Ready-to-implement features:
- Insert new maps
- Update existing maps
- Delete maps
- Browse entities
- Delete entities
- Advanced search filters
- Data export functionality
- User role management