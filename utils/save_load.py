import json
import os
from datetime import datetime

# Constants
SAVE_FOLDER = "saves"

def ensure_save_folder():
    """Create the saves directory if it doesn't already exist."""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def save_game(game_state, slot=None):
    """Save the current game state to a JSON file.
    
    Args:
        game_state: The current state of the game containing entities and items
        slot: Optional slot number for save files. If None, uses timestamp
    
    Returns:
        filepath: Path to the saved game file
    """
    ensure_save_folder()
    
    # Generate filename with timestamp if no slot specified
    if slot is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"save_{timestamp}.json"
    else:
        filename = f"save_slot_{slot}.json"
    
    filepath = os.path.join(SAVE_FOLDER, filename)
    
    # Collect game state data - only saves entities/items that have to_dict method
    save_data = {
        "entities": [
            entity.to_dict() for entity in game_state.entity_manager.entities
            if hasattr(entity, 'to_dict')
        ],
        "items": [
            item.to_dict() for item in game_state.entity_manager.items
            if hasattr(item, 'to_dict')
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    # Save to file in JSON format with pretty printing (indent=2)
    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    return filepath

def load_game(filepath):
    """Load a saved game from a JSON file.
    
    Args:
        filepath: Path to the save file to load
    
    Returns:
        dict: The loaded save data containing entities, items, and timestamp
    """
    with open(filepath, 'r') as f:
        save_data = json.load(f)
    return save_data

def get_save_files():
    """Get a list of all save files in the saves directory.
    
    Returns:
        list: List of dictionaries containing save file information,
              sorted by timestamp (newest first)
    """
    ensure_save_folder()
    saves = []
    # Collect information about each save file
    for filename in os.listdir(SAVE_FOLDER):
        if filename.endswith('.json'):
            filepath = os.path.join(SAVE_FOLDER, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                saves.append({
                    'filepath': filepath,
                    'filename': filename,
                    'timestamp': data['timestamp']
                })
    return sorted(saves, key=lambda x: x['timestamp'], reverse=True) 