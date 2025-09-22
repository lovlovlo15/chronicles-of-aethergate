"""
World loader for Chronicles of Aether Gate
Loads rooms, items, and other game data from JSON files
"""

import json
import os

def load_rooms(filename="data/rooms.json"):
    """Load room data from JSON file"""
    try:
        if not os.path.exists(filename):
            return {}
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data
    
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}

def load_enemies(filename="data/enemies.json"):
    """Load enemy data from JSON file"""
    try:
        if not os.path.exists(filename):
            return {}
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data
    
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}

def load_items(filename="data/items.json"):
    """Load item data from JSON file"""
    try:
        if not os.path.exists(filename):
            return {}
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return {}
