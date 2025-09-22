"""
Item classes for Chronicles of Aether Gate
Handles weapons, consumables, accessories, and key items
"""

from typing import Dict, Any, Optional

class Item:
    """Base item class for all game items"""
    
    def __init__(self, item_id: str, data: Dict[str, Any]):
        """Initialize item from JSON data"""
        self.id = item_id
        self.name = data.get("name", "Unknown Item")
        self.description = data.get("description", "A mysterious object.")
        self.type = data.get("type", "misc")
        self.stats = data.get("stats", {})
        self.value = data.get("value", 0)  # For future trading system
        self.stackable = data.get("stackable", False)
        self.usable = self.type in ["consumable", "weapon", "accessory"]
        
        # Visual properties
        self.icon = data.get("icon", "default_item.png")
        self.rarity = data.get("rarity", "common")  # common, uncommon, rare, legendary
        
    def use(self, player) -> str:
        """Use item on player - returns result message"""
        if not self.usable:
            return f"❌ You can't use the {self.name}."
        
        if self.type == "consumable":
            return self._use_consumable(player)
        elif self.type == "weapon":
            return self._equip_weapon(player)
        elif self.type == "accessory":
            return self._equip_accessory(player)
        
        return f"🔍 You examine the {self.name}."
    
    def _use_consumable(self, player) -> str:
        """Handle consumable items"""
        messages = []
        
        # Healing effects
        if "heal_amount" in self.stats:
            healed = player.heal(self.stats["heal_amount"])
            if healed > 0:
                messages.append(f"💚 Restored {healed} HP")
        
        # Focus restoration
        if "focus_restore" in self.stats:
            restored = player.restore_focus(self.stats["focus_restore"])
            if restored > 0:
                messages.append(f"🔵 Restored {restored} Focus")
        
        # Status effects
        if "cure_poison" in self.stats and self.stats["cure_poison"]:
            if "poisoned" in player.status_effects:
                del player.status_effects["poisoned"]
                messages.append(f"🧪 Cured poison")
        
        # Temporary buffs
        if "buff_attack" in self.stats:
            player.add_status_effect("attack_buffed", self.stats["buff_duration"])
            messages.append(f"⚔️ Attack increased temporarily")
        
        if messages:
            return f"✨ Used {self.name}! " + ", ".join(messages)
        else:
            return f"❓ {self.name} had no effect."
    
    def _equip_weapon(self, player) -> str:
        """Handle weapon equipping"""
        if player.equip_weapon(self.to_dict()):
            return f"⚔️ Equipped {self.name}!"
        else:
            return f"❌ Cannot equip {self.name}."
    
    def _equip_accessory(self, player) -> str:
        """Handle accessory equipping"""
        if player.equip_accessory(self.to_dict()):
            return f"💍 Equipped {self.name}!"
        else:
            return f"❌ Cannot equip {self.name}."
    
    def get_tooltip(self) -> str:
        """Get detailed item information for tooltips"""
        tooltip = f"**{self.name}**\n"
        tooltip += f"Type: {self.type.title()}\n"
        tooltip += f"Rarity: {self.rarity.title()}\n\n"
        tooltip += f"{self.description}\n"
        
        if self.stats:
            tooltip += "\n**Effects:**\n"
            for stat, value in self.stats.items():
                if stat == "attack_bonus":
                    tooltip += f"• +{value} Attack\n"
                elif stat == "defense_bonus":
                    tooltip += f"• +{value} Defense\n"
                elif stat == "focus_bonus":
                    tooltip += f"• +{value} Max Focus\n"
                elif stat == "heal_amount":
                    tooltip += f"• Heals {value} HP\n"
                elif stat == "focus_restore":
                    tooltip += f"• Restores {value} Focus\n"
        
        return tooltip
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "stats": self.stats,
            "value": self.value,
            "stackable": self.stackable,
            "icon": self.icon,
            "rarity": self.rarity
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


# Specialized item subclasses
class Weapon(Item):
    """Weapon item subclass"""
    def __init__(self, item_id: str, data: Dict[str, Any]):
        super().__init__(item_id, data)
        self.damage = self.stats.get("attack_bonus", 0)
        self.special_effect = self.stats.get("special", None)
        self.durability = data.get("durability", 100)


class Consumable(Item):
    """Consumable item subclass"""
    def __init__(self, item_id: str, data: Dict[str, Any]):
        super().__init__(item_id, data)
        self.heal_power = self.stats.get("heal_amount", 0)
        self.focus_power = self.stats.get("focus_restore", 0)
        self.stackable = True  # Consumables are always stackable


class KeyItem(Item):
    """Key item subclass for story items"""
    def __init__(self, item_id: str, data: Dict[str, Any]):
        super().__init__(item_id, data)
        self.is_victory_item = self.stats.get("victory_item", False)
    
    def use(self, player) -> str:
        if self.is_victory_item:
            return f"🔮 The {self.name} pulses with otherworldly energy. You need to reach the Aether Gate to use it."
        return f"📜 The {self.name} seems important, but you're not sure how to use it here."


class Accessory(Item):
    """Accessory item subclass"""
    def __init__(self, item_id: str, data: Dict[str, Any]):
        super().__init__(item_id, data)
        self.slot = data.get("slot", "general")  # ring, necklace, etc.


# Factory function to create items
def create_item(item_id: str, data: Dict[str, Any]) -> Item:
    """Factory function to create the appropriate item subclass"""
    item_type = data.get("type", "misc")
    
    if item_type == "weapon":
        return Weapon(item_id, data)
    elif item_type == "consumable":
        return Consumable(item_id, data)
    elif item_type == "key_item":
        return KeyItem(item_id, data)
    elif item_type == "accessory":
        return Accessory(item_id, data)
    else:
        return Item(item_id, data)



