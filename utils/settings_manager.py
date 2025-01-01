import json
import os

# Path to the settings file that stores user preferences
SETTINGS_FILE = "settings.json"

def load_settings():
    """
    Load user settings from a JSON file, falling back to defaults if needed.
    
    Returns:
        dict: A dictionary containing the application settings, merged with defaults
    """
    # Define default settings that will be used if file is missing or corrupted
    default_settings = {
        "volume": 100
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            # Attempt to read and parse the settings file
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults in case new settings are added
                return {**default_settings, **settings}
        except:
            # Return defaults if there's any error reading or parsing the file
            return default_settings
    return default_settings

def save_settings(settings):
    """
    Save the current settings to a JSON file.
    
    Args:
        settings (dict): Dictionary containing the current application settings
    """
    # Write settings to file with proper formatting
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2) 