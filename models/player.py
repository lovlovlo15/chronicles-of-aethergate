"""
Player class for Chronicles of Aether Gate
Manages player stats, inventory, progression, and game state
"""

import json
from typing import Dict, List, Any, Optional

class Player:
    def __init__(self, name: str = "Aether Warden"):
        """Initialize a new player character"""
        self.name = name
        
        # Core Stats
        self.max_hp = 100
        self.hp = self.max_hp
        self.max_focus = 5  # Used for special abilities
        self.focus = self.max_focus
        
        # Combat Stats
        self.base_attack = 10
        self.base_defense = 5
        self.base_speed = 6
        
        # Current effective stats (base + equipment bonuses)
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.speed = self.base_speed
        
        # Game Progress
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_accessory = None
        self.current_room = "entrance"
        self.visited_rooms = set()
        
        # Victory Progress
        self.aether_crystals = 0  # Need 3 to win
        self.enemies_defeated = 0
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        
        # Status Effects
        self.status_effects = {}  # {"poisoned": 3, "buffed": 2} (turns remaining)
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to player, accounting for defense"""
        # Calculate actual damage (minimum 1)
        actual_damage = max(1, damage - self.defense)
        
        # Apply damage
        self.hp = max(0, self.hp - actual_damage)
        self.total_damage_taken += actual_damage
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Restore HP up to maximum"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        
        return healed
    
    def restore_focus(self, amount: int) -> int:
        """Restore focus points for abilities"""
        old_focus = self.focus
        self.focus = min(self.max_focus, self.focus + amount)
        restored = self.focus - old_focus
        
        if restored > 0:
            print(f"🔵 {self.name} restored {restored} Focus! Focus: {self.focus}/{self.max_focus}")
        
        return restored
    
    def spend_focus(self, amount: int) -> bool:
        """Try to spend focus points. Returns True if successful"""
        if self.focus >= amount:
            self.focus -= amount
            return True
        return False
    
    def add_item(self, item: Dict[str, Any]) -> bool:
        """Add item to inventory"""
        # Check for special victory items
        if item.get("type") == "key_item" and "aether crystal" in item.get("name", "").lower():
            self.aether_crystals += 1
            print(f"🔮 Found Aether Crystal! ({self.aether_crystals}/3)")
        
        self.inventory.append(item)
        print(f"🎒 Added {item.get('name', 'Unknown Item')} to inventory")
        return True
    
    def remove_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Remove item from inventory by name"""
        for i, item in enumerate(self.inventory):
            if item.get("name") == item_name:
                removed_item = self.inventory.pop(i)
                print(f"🗑️ Removed {item_name} from inventory")
                return removed_item
        return None
    
    def equip_weapon(self, weapon: Dict[str, Any]) -> bool:
        """Equip a weapon and update stats"""
        if weapon.get("type") != "weapon":
            return False
        
        # Unequip current weapon first (add it back to inventory)
        if self.equipped_weapon:
            old_weapon = self.unequip_weapon()
            if old_weapon:
                self.add_item(old_weapon)
        
        # Equip new weapon
        self.equipped_weapon = weapon
        attack_bonus = weapon.get("stats", {}).get("attack_bonus", 0)
        self.attack = self.base_attack + attack_bonus
        
        return True
    
    def unequip_weapon(self) -> Optional[Dict[str, Any]]:
        """Unequip current weapon"""
        if not self.equipped_weapon:
            return None
        
        old_weapon = self.equipped_weapon
        self.equipped_weapon = None
        self.attack = self.base_attack
        
        print(f"🔄 Unequipped {old_weapon.get('name', 'Unknown Weapon')}")
        return old_weapon
    
    def equip_accessory(self, accessory: Dict[str, Any]) -> bool:
        """Equip an accessory and update stats"""
        if accessory.get("type") != "accessory":
            return False
        
        # Unequip current accessory first (add it back to inventory)
        if self.equipped_accessory:
            old_accessory = self.unequip_accessory()
            if old_accessory:
                self.add_item(old_accessory)
        
        # Equip new accessory
        self.equipped_accessory = accessory
        stats = accessory.get("stats", {})
        
        # Apply stat bonuses
        if "defense_bonus" in stats:
            self.defense = self.base_defense + stats["defense_bonus"]
        if "focus_bonus" in stats:
            self.max_focus += stats["focus_bonus"]
            self.focus = min(self.focus + stats["focus_bonus"], self.max_focus)
        if "speed_bonus" in stats:
            self.speed = self.base_speed + stats["speed_bonus"]
        
        return True
    
    def unequip_accessory(self) -> Optional[Dict[str, Any]]:
        """Unequip current accessory"""
        if not self.equipped_accessory:
            return None
        
        old_accessory = self.equipped_accessory
        self.equipped_accessory = None
        
        # Reset stats to base values (will recalculate with weapon if equipped)
        self.defense = self.base_defense
        self.max_focus = 5  # Base focus
        self.speed = self.base_speed
        
        print(f"🔄 Unequipped {old_accessory.get('name', 'Unknown Accessory')}")
        return old_accessory
    
    def visit_room(self, room_id: str):
        """Mark a room as visited"""
        self.visited_rooms.add(room_id)
        self.current_room = room_id
    
    def is_alive(self) -> bool:
        """Check if player is still alive"""
        return self.hp > 0
    
    def has_won(self) -> bool:
        """Check victory condition"""
        return self.aether_crystals >= 3
    
    def can_use_ability(self, focus_cost: int) -> bool:
        """Check if player has enough focus for an ability"""
        return self.focus >= focus_cost
    
    def add_status_effect(self, effect: str, duration: int):
        """Add a temporary status effect"""
        self.status_effects[effect] = duration
        print(f"✨ {self.name} is now {effect} for {duration} turns")
    
    def update_status_effects(self):
        """Update status effects (call each turn)"""
        expired_effects = []
        
        for effect, duration in self.status_effects.items():
            self.status_effects[effect] = duration - 1
            
            if self.status_effects[effect] <= 0:
                expired_effects.append(effect)
            else:
                # Apply ongoing effect
                if effect == "poisoned":
                    self.take_damage(3)
                elif effect == "regenerating":
                    self.heal(5)
        
        # Remove expired effects
        for effect in expired_effects:
            del self.status_effects[effect]
            print(f"⏰ {effect} effect expired")
    
    def get_stats(self) -> Dict[str, Any]:
        """Return formatted stats for display"""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "focus": self.focus,
            "max_focus": self.max_focus,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "crystals": self.aether_crystals,
            "inventory": self.inventory,
            "inventory_count": len(self.inventory),
            "rooms_visited": len(self.visited_rooms),
            "enemies_defeated": self.enemies_defeated,
            "equipped_weapon": self.equipped_weapon.get("name", "None") if self.equipped_weapon else "None",
            "equipped_accessory": self.equipped_accessory.get("name", "None") if self.equipped_accessory else "None",
            "status_effects": self.status_effects
        }
    
    def get_inventory_summary(self) -> List[str]:
        """Get a list of inventory item names"""
        return [item.get("name", "Unknown Item") for item in self.inventory]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player state to dictionary for saving"""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "focus": self.focus,
            "max_focus": self.max_focus,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_speed": self.base_speed,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_accessory": self.equipped_accessory,
            "current_room": self.current_room,
            "visited_rooms": list(self.visited_rooms),
            "aether_crystals": self.aether_crystals,
            "enemies_defeated": self.enemies_defeated,
            "total_damage_dealt": self.total_damage_dealt,
            "total_damage_taken": self.total_damage_taken,
            "status_effects": self.status_effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary (for loading)"""
        player = cls(data.get("name", "Aether Warden"))
        
        # Restore all saved attributes
        player.hp = data.get("hp", 100)
        player.max_hp = data.get("max_hp", 100)
        player.focus = data.get("focus", 5)
        player.max_focus = data.get("max_focus", 5)
        player.base_attack = data.get("base_attack", 10)
        player.base_defense = data.get("base_defense", 5)
        player.base_speed = data.get("base_speed", 6)
        player.inventory = data.get("inventory", [])
        player.equipped_weapon = data.get("equipped_weapon")
        player.equipped_accessory = data.get("equipped_accessory")
        player.current_room = data.get("current_room", "entrance")
        player.visited_rooms = set(data.get("visited_rooms", []))
        player.aether_crystals = data.get("aether_crystals", 0)
        player.enemies_defeated = data.get("enemies_defeated", 0)
        player.total_damage_dealt = data.get("total_damage_dealt", 0)
        player.total_damage_taken = data.get("total_damage_taken", 0)
        player.status_effects = data.get("status_effects", {})
        
        # Recalculate effective stats
        player.attack = player.base_attack
        player.defense = player.base_defense
        player.speed = player.base_speed
        
        if player.equipped_weapon:
            player.equip_weapon(player.equipped_weapon)
        if player.equipped_accessory:
            player.equip_accessory(player.equipped_accessory)
        
        return player
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return f"{self.name} (HP: {self.hp}/{self.max_hp}, Focus: {self.focus}/{self.max_focus}, ATK: {self.attack}, DEF: {self.defense})"



