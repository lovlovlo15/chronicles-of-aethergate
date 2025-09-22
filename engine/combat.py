"""
Combat Engine for Chronicles of Aether Gate
Handles turn-based strategic combat with abilities and status effects
"""

from typing import Dict, List, Any, Optional
import random
from models.enemy import create_enemy
from engine.world_loader import load_enemies

class CombatEngine:
    """Manages turn-based combat between player and enemies"""
    
    def __init__(self, player, enemy_id: str):
        """Initialize combat with player and enemy"""
        self.player = player
        self.enemy_data = load_enemies()
        
        if enemy_id not in self.enemy_data:
            raise ValueError(f"Enemy {enemy_id} not found!")
        
        self.enemy = create_enemy(enemy_id, self.enemy_data[enemy_id])
        self.turn_queue = []
        self.current_turn = 0
        self.combat_log = []
        self.combat_active = True
        
        self._setup_turn_order()
        self.log_message(f"⚔️ Combat begins! {self.player.name} vs {self.enemy.name}")
    
    def _setup_turn_order(self):
        """Set up turn order based on speed stats"""
        # Create turn queue based on speed
        player_speed = self.player.speed
        enemy_speed = self.enemy.speed
        
        # Determine who goes first
        if player_speed >= enemy_speed:
            self.turn_queue = ["player", "enemy"]
        else:
            self.turn_queue = ["enemy", "player"]
        
        # Add some randomness for equal speeds
        if player_speed == enemy_speed:
            random.shuffle(self.turn_queue)
        
        self.log_message(f"Turn order: {' → '.join(self.turn_queue)}")
    
    def get_current_turn(self) -> str:
        """Get whose turn it is"""
        if not self.combat_active:
            return "none"
        return self.turn_queue[self.current_turn % len(self.turn_queue)]
    
    def is_player_turn(self) -> bool:
        """Check if it's the player's turn"""
        return self.get_current_turn() == "player"
    
    def is_combat_over(self) -> bool:
        """Check if combat has ended"""
        return not self.combat_active or not self.player.is_alive() or not self.enemy.is_alive()
    
    def get_winner(self) -> Optional[str]:
        """Get the winner of combat"""
        if not self.is_combat_over():
            return None
        
        if self.player.is_alive():
            return "player"
        elif self.enemy.is_alive():
            return "enemy"
        else:
            return "draw"
    
    def player_attack(self) -> str:
        """Execute player basic attack"""
        if not self.is_player_turn():
            return "❌ Not your turn!"
        
        damage = self.player.attack
        actual_damage = self.enemy.take_damage(damage)
        
        # Track total damage dealt by player
        self.player.total_damage_dealt += actual_damage
        
        message = f"⚔️ {self.player.name} attacks {self.enemy.name} for {actual_damage} damage!"
        self.log_message(message)
        
        self._end_turn()
        return message
    
    def player_use_ability(self, ability_name: str) -> str:
        """Execute player ability"""
        if not self.is_player_turn():
            return "❌ Not your turn!"
        
        # Define player abilities
        abilities = {
            "power_strike": {"focus_cost": 2, "damage_multiplier": 1.5, "description": "🔥 Devastating strike"},
            "defensive_stance": {"focus_cost": 1, "damage_multiplier": 0, "description": "🛡️ Defensive position"},
            "aether_blast": {"focus_cost": 3, "damage_multiplier": 1.3, "description": "💥 Magical energy blast"},
            "heal": {"focus_cost": 2, "heal_amount": 25, "description": "💚 Self healing"}
        }
        
        if ability_name not in abilities:
            return f"❌ Unknown ability: {ability_name}"
        
        ability = abilities[ability_name]
        focus_cost = ability["focus_cost"]
        
        if not self.player.spend_focus(focus_cost):
            return f"❌ Not enough focus! Need {focus_cost}, have {self.player.focus}"
        
        # Execute ability
        if ability_name == "heal":
            healed = self.player.heal(ability["heal_amount"])
            message = f"{ability['description']}: {self.player.name} heals for {healed} HP!"
        elif ability_name == "defensive_stance":
            self.player.add_status_effect("defensive", 2)
            message = f"{ability['description']}: {self.player.name} takes a defensive stance!"
        else:
            damage = int(self.player.attack * ability["damage_multiplier"])
            actual_damage = self.enemy.take_damage(damage)
            
            # Track total damage dealt by player
            self.player.total_damage_dealt += actual_damage
            
            message = f"{ability['description']}: {actual_damage} damage to {self.enemy.name}!"
        
        self.log_message(message)
        self._end_turn()
        return message
    
    def player_use_item(self, item_name: str) -> str:
        """Use an item from player's inventory"""
        if not self.is_player_turn():
            return "❌ Not your turn!"
        
        # Find item in inventory
        for item in self.player.inventory:
            if item.get("name") == item_name and item.get("type") == "consumable":
                # Use the item
                result = self._use_consumable_item(item)
                
                # Remove item from inventory if it's not stackable
                if not item.get("stackable", False):
                    self.player.remove_item(item_name)
                
                self.log_message(f"💊 Used {item_name}: {result}")
                self._end_turn()
                return result
        
        return f"❌ {item_name} not found or not usable!"
    
    def _use_consumable_item(self, item: Dict[str, Any]) -> str:
        """Use a consumable item and return result message"""
        stats = item.get("stats", {})
        results = []
        
        if "heal_amount" in stats:
            healed = self.player.heal(stats["heal_amount"])
            results.append(f"+{healed} HP")
        
        if "focus_restore" in stats:
            restored = self.player.restore_focus(stats["focus_restore"])
            results.append(f"+{restored} Focus")
        
        return ", ".join(results) if results else "No effect"
    
    def enemy_turn(self) -> str:
        if self.get_current_turn() != "enemy":
            return ""
        
        action = self.enemy.choose_action(
            self.player.hp,
            self.player.defense,
            self.player.focus
        )

        message = ""
        if action["type"] == "attack":
            damage = self.enemy.get_effective_attack()
            actual_damage = self.player.take_damage(damage)
            message = f"👹 {self.enemy.name} attacks {self.player.name} for {actual_damage} damage!"
        
        elif action["type"] == "ability":
            ability_name = action["name"]
            result, damage = self.enemy.use_ability(ability_name, self.player)
            if damage > 0:
                actual_damage = self.player.take_damage(damage)
                message = f"{result} {actual_damage} damage to {self.player.name}!"
            else:
                message = result
        
        else:
            message = "❓ Enemy tried unknown action."
        
        self.log_message(message)
        self._end_turn()
        return message

    
    def _end_turn(self):
        """End current turn and update game state"""
        # Update status effects
        self.player.update_status_effects()
        self.enemy._update_status_effects()
        
        # Check for combat end
        if not self.player.is_alive():
            self.combat_active = False
            self.log_message(f"💀 {self.player.name} has been defeated!")
        elif not self.enemy.is_alive():
            self.combat_active = False
            self._handle_victory()
        else:
            # Next turn
            self.current_turn += 1
    
    def _handle_victory(self):
        """Handle player victory"""
        self.log_message(f"🎉 {self.enemy.name} defeated!")
        
        # Award experience/items
        self.player.enemies_defeated += 1
        
        # Drop loot
        loot = self.enemy.get_loot()
        if loot:
            self.log_message(f"💰 {self.enemy.name} dropped: {', '.join(loot)}")
    
    def log_message(self, message: str):
        """Add a message to the combat log"""
        self.combat_log.append(message)
    
    def get_combat_log(self) -> List[str]:
        """Get all combat messages"""
        return self.combat_log.copy()
    
    def get_combat_state(self) -> Dict[str, Any]:
        """Get current combat state for GUI"""
        return {
            "player": self.player.get_stats(),
            "enemy": self.enemy.get_stats(),
            "current_turn": self.get_current_turn(),
            "combat_active": self.combat_active,
            "winner": self.get_winner(),
            "log": self.get_combat_log()
        }


