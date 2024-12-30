import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    default_settings = {
        "volume": 100
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults in case new settings are added
                return {**default_settings, **settings}
        except:
            return default_settings
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2) 