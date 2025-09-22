"""
Item Manager for Chronicles of Aether Gate
Handles item creation, management, and room placement
"""

from typing import Dict, List, Any, Optional
from models.item import create_item, Item
from engine.world_loader import load_items

class ItemManager:
    """Manages all items in the game"""
    
    def __init__(self):
        """Initialize the item manager"""
        self.item_data = load_items()
        self.room_items = {}  # room_id -> list of item_ids
        self._setup_room_items()
        

    
    def _setup_room_items(self):
        """Set up which items appear in which rooms"""
        self.room_items = {
            "entrance": ["healing_tonic"],  # Starting item
            "hallway": [],  # Safe transit area
            "laboratory": ["mana_potion", "focus_crystal", "aether_crystal"],  # First crystal
            "armory": ["steam_blade", "repair_kit", "steam_gauntlets", "aether_crystal"],  # Second crystal
            "gate_chamber": ["aether_crystal"]  # Third crystal - final challenge
        }
        

    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Create an item instance from its ID"""
        if item_id not in self.item_data:
            print(f"❌ Item not found: {item_id}")
            return None
        
        return create_item(item_id, self.item_data[item_id])
    
    def get_room_items(self, room_id: str) -> List[str]:
        """Get list of item IDs in a room"""
        return self.room_items.get(room_id, []).copy()
    
    def take_item_from_room(self, room_id: str, item_id: str) -> Optional[Item]:
        """Remove and return an item from a room"""
        if room_id not in self.room_items:
            return None
        
        if item_id in self.room_items[room_id]:
            self.room_items[room_id].remove(item_id)
            item = self.get_item(item_id)
            print(f"📦 Took {item.name if item else item_id} from {room_id}")
            return item
        
        return None
    
    def add_item_to_room(self, room_id: str, item_id: str):
        """Add an item to a room"""
        if room_id not in self.room_items:
            self.room_items[room_id] = []
        
        if item_id not in self.room_items[room_id]:
            self.room_items[room_id].append(item_id)
            print(f"📍 Added {item_id} to {room_id}")
    
    def get_item_names_in_room(self, room_id: str) -> List[str]:
        """Get display names of items in a room"""
        item_ids = self.get_room_items(room_id)
        names = []
        
        for item_id in item_ids:
            item = self.get_item(item_id)
            if item:
                names.append(item.name)
        
        return names


