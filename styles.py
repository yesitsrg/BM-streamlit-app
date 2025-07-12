# styles.py
"""
CSS styles module for Beisman Maps Management System
"""

def get_css_styles():
    """
    Returns the complete CSS styles for the application
    """
    return """
    <style>
        .stApp {
            background-color: #c0c0c0;
            font-family: "MS Sans Serif", sans-serif;
        }
        
        .main-container {
            background-color: #c0c0c0;
            margin: 20px auto;
            max-width: 1000px;
            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .windows-header {
            background: linear-gradient(to bottom, #0054e3 0%, #0054e3 3px, #0054e3 100%);
            padding: 4px 8px;
            height: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0;
        }
        
        .header-title {
            color: white;
            font-size: 11px;
            font-weight: bold;
            margin: 0;
            font-family: "MS Sans Serif", sans-serif;
            padding-left: 4px;
        }
        
        .content-area {
            background-color: #c0c0c0;
            padding: 8px;
            margin: 0;
        }
        
        .nav-container {
            background-color: #c0c0c0;
            padding: 10px;
            margin: 10px 0;
        }
        
        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 5px;
            align-items: flex-start;
        }
        
        .nav-link {
            color: #000080;
            text-decoration: underline;
            font-size: 11px;
            font-family: "MS Sans Serif", sans-serif;
            cursor: pointer;
            background: none;
            border: none;
            padding: 2px 0;
            text-align: left;
        }
        
        .nav-link:hover {
            color: #800080;
        }
        
        .admin-button-container {
            position: absolute;
            top: 24px;
            right: 32px;
            z-index: 10;
        }
        
        .stButton > button {
            all: unset;
            background: linear-gradient(to bottom, #dfdfdf 0%, #c0c0c0 100%) !important;
            color: black !important;
            border: 1px outset #c0c0c0 !important;
            font-size: 11px !important;
            font-family: "MS Sans Serif", sans-serif !important;
            border-radius: 0 !important;
            padding: 2px 8px !important;
            min-width: 60px !important;
            height: 20px !important;
            cursor: pointer !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(to bottom, #e0e0e0 0%, #d0d0d0 100%) !important;
        }
        
        .stButton > button:active {
            border: 1px inset #c0c0c0 !important;
            background: linear-gradient(to bottom, #c0c0c0 0%, #dfdfdf 100%) !important;
        }
        
        .form-container {
            background-color: #c0c0c0;
            border: 2px inset #c0c0c0;
            padding: 20px;
            width: 300px;
            margin: 0 auto;
        }
        
        .form-header {
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: 'MS Sans Serif', sans-serif;
        }
        
        .login-error {
            color: #800000;
            font-size: 10px;
            font-family: "MS Sans Serif", sans-serif;
            margin-top: 8px;
            text-align: center;
        }
        
        /* Browse Maps specific styles */
        .search-container {
            background: #f0f0f0;
            padding: 0.5rem;
            border: 1px solid #808080;
            margin-bottom: 1rem;
        }
        
        .results-container {
            background: #ffffff;
            border: 1px solid #808080;
            padding: 0;
        }
        
        .stTextInput > div > div > input {
            border: 2px inset #d0d0d0;
            border-radius: 0px;
            padding: 0.2rem;
            font-size: 0.9rem;
            height: 31px;
        }
        
        .dataframe {
            border: 1px solid #808080;
            font-size: 0.8rem;
            font-family: Arial, sans-serif;
        }
        
        .dataframe th {
            background: #c0c0c0;
            border: 1px solid #808080;
            padding: 0.2rem;
            font-weight: bold;
            text-align: left;
        }
        
        .dataframe td {
            border: 1px solid #808080;
            padding: 0.2rem;
            text-align: left;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """