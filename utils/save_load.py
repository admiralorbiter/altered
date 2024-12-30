import json
import os
from datetime import datetime

SAVE_FOLDER = "saves"

def ensure_save_folder():
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def save_game(game_state, slot=None):
    ensure_save_folder()
    
    # Generate filename with timestamp if no slot specified
    if slot is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"save_{timestamp}.json"
    else:
        filename = f"save_slot_{slot}.json"
    
    filepath = os.path.join(SAVE_FOLDER, filename)
    
    # Collect game state data
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
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    return filepath

def load_game(filepath):
    with open(filepath, 'r') as f:
        save_data = json.load(f)
    return save_data

def get_save_files():
    ensure_save_folder()
    saves = []
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