"""
Enemy classes for Chronicles of Aether Gate
Handles enemy stats, AI behavior, and combat abilities
"""

from typing import Dict, List, Any, Tuple
import random

class Enemy:
    """Base enemy class for all game enemies"""
    
    def __init__(self, enemy_id: str, data: Dict[str, Any]):
        """Initialize enemy with data from JSON"""
        self.id = enemy_id
        self.name = data.get("name", "Unknown Enemy")
        
        # Initialize stats
        stats = data.get("stats", {})
        self.max_hp = stats.get("hp", 20)
        self.hp = self.max_hp
        self.attack = stats.get("attack", 5)
        self.defense = stats.get("defense", 1)
        self.speed = stats.get("speed", 3)
        self.focus = stats.get("focus", 2)
        self.max_focus = self.focus
        
        # Initialize abilities and AI
        self.abilities = data.get("abilities", [])
        self.ability_cooldowns = {}
        self.ai_pattern = data.get("ai_pattern", "basic")
        self.status_effects = {}
        self.description = data.get("description", "")
        self.loot = data.get("loot", [])
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Restore HP (for some enemies with healing abilities)"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        
        return healed
    
    def is_alive(self) -> bool:
        """Check if enemy is still alive"""
        return self.hp > 0
    
    def can_use_ability(self, ability_name: str) -> bool:
        """Check if ability is off cooldown and enemy has focus"""
        if ability_name not in self.abilities:
            return False
        
        # Check cooldown
        if ability_name in self.ability_cooldowns:
            if self.ability_cooldowns[ability_name] > 0:
                return False
        
        # Check focus cost (basic abilities cost 1-2 focus)
        focus_cost = self._get_ability_focus_cost(ability_name)
        return self.focus >= focus_cost
    
    def _get_ability_focus_cost(self, ability_name: str) -> int:
        """Get focus cost for an ability"""
        costs = {
            "power_strike": 2,
            "defensive_stance": 1,
            "quick_strike": 1,
            "energy_discharge": 3,
            "repair_self": 2,
            "berserker_rage": 3
        }
        return costs.get(ability_name, 1)
    
    def use_ability(self, ability_name: str, target=None) -> Tuple[str, int]:
        """Use an ability and return (action_description, damage_dealt)"""
        if not self.can_use_ability(ability_name):
            return f"{self.name} cannot use {ability_name}!", 0
        
        # Pay focus cost
        focus_cost = self._get_ability_focus_cost(ability_name)
        self.focus -= focus_cost
        
        # Set cooldown
        self.ability_cooldowns[ability_name] = self._get_ability_cooldown(ability_name)
        
        # Execute ability
        return self._execute_ability(ability_name, target)
    
    def _get_ability_cooldown(self, ability_name: str) -> int:
        """Get cooldown turns for an ability"""
        cooldowns = {
            "power_strike": 2,
            "defensive_stance": 3,
            "quick_strike": 1,
            "energy_discharge": 4,
            "repair_self": 3,
            "berserker_rage": 5
        }
        return cooldowns.get(ability_name, 2)
    
    def _execute_ability(self, ability_name: str, target=None) -> Tuple[str, int]:
        """Execute a specific ability"""
        if ability_name == "power_strike":
            damage = int(self.attack * 1.5)
            return f"🔥 {self.name} unleashes a devastating power strike!", damage
        
        elif ability_name == "defensive_stance":
            self.status_effects["defensive"] = 2
            return f"🛡️ {self.name} takes a defensive stance!", 0
        
        elif ability_name == "quick_strike":
            damage = int(self.attack * 0.8)
            return f"⚡ {self.name} strikes with lightning speed!", damage
        
        elif ability_name == "energy_discharge":
            damage = int(self.attack * 1.2)
            return f"💥 {self.name} releases a burst of energy!", damage
        
        elif ability_name == "repair_self":
            healed = self.heal(15)
            return f"🔧 {self.name} performs emergency repairs! (+{healed} HP)", 0
        
        elif ability_name == "berserker_rage":
            self.status_effects["berserker"] = 3
            damage = int(self.attack * 2.0)
            return f"😡 {self.name} enters a berserker rage!", damage
        
        else:
            return f"{self.name} uses {ability_name}!", self.attack
    
    def choose_action(self, player_hp: int, player_defense: int, player_focus: int) -> Dict[str, Any]:
        """AI decision making - returns action to take"""
        # Update cooldowns
        for ability in list(self.ability_cooldowns.keys()):
            self.ability_cooldowns[ability] -= 1
            if self.ability_cooldowns[ability] <= 0:
                del self.ability_cooldowns[ability]
        
        # Update status effects
        self._update_status_effects()
        
        # Strategic AI based on patterns and traits
        if self.ai_pattern == "aggressive":
            return self._aggressive_ai(player_hp, player_defense)
        elif self.ai_pattern == "defensive":
            return self._defensive_ai(player_hp, player_defense)
        elif self.ai_pattern == "tactical":
            return self._tactical_ai(player_hp, player_defense, player_focus)
        elif self.ai_pattern == "hit_and_run":
            return self._hit_and_run_ai(player_hp, player_defense)
        else:
            return self._basic_ai(player_hp, player_defense)
    
    def _aggressive_ai(self, player_hp: int, player_defense: int) -> Dict[str, Any]:
        """Aggressive AI - prioritizes high damage"""
        # Always try to use most powerful attack
        if self.can_use_ability("power_strike"):
            return {"type": "ability", "name": "power_strike"}
        elif self.can_use_ability("berserker_rage"):
            return {"type": "ability", "name": "berserker_rage"}
        else:
            return {"type": "attack"}
    
    def _defensive_ai(self, player_hp: int, player_defense: int) -> Dict[str, Any]:
        """Defensive AI - prioritizes survival"""
        # Heal if low HP
        if self.hp < self.max_hp * 0.3 and self.can_use_ability("repair_self"):
            return {"type": "ability", "name": "repair_self"}
        
        # Use defensive stance if available
        if "defensive" not in self.status_effects and self.can_use_ability("defensive_stance"):
            return {"type": "ability", "name": "defensive_stance"}
        
        return {"type": "attack"}
    
    def _tactical_ai(self, player_hp: int, player_defense: int, player_focus: int) -> Dict[str, Any]:
        """Tactical AI - adapts to player state"""
        # If player is low HP, go for the kill
        if player_hp < 30:
            if self.can_use_ability("power_strike"):
                return {"type": "ability", "name": "power_strike"}
        
        # If player has high focus, use defensive moves
        if player_focus >= 3:
            if self.can_use_ability("defensive_stance"):
                return {"type": "ability", "name": "defensive_stance"}
        
        # If enemy is low HP, heal or go all-out
        if self.hp < self.max_hp * 0.4:
            if self.can_use_ability("repair_self"):
                return {"type": "ability", "name": "repair_self"}
            elif self.can_use_ability("berserker_rage"):
                return {"type": "ability", "name": "berserker_rage"}
        
        return {"type": "attack"}
    
    def _hit_and_run_ai(self, player_hp: int, player_defense: int) -> Dict[str, Any]:
        """Hit and run AI - quick attacks"""
        if self.can_use_ability("quick_strike"):
            return {"type": "ability", "name": "quick_strike"}
        return {"type": "attack"}
    
    def _basic_ai(self, player_hp: int, player_defense: int) -> Dict[str, Any]:
        """Basic AI - simple attack pattern"""
        # 30% chance to use ability if available
        if random.random() < 0.3 and self.abilities:
            available_abilities = [ability for ability in self.abilities if self.can_use_ability(ability)]
            if available_abilities:
                ability = random.choice(available_abilities)
                return {"type": "ability", "name": ability}
        
        return {"type": "attack"}
    
    def _update_status_effects(self):
        """Update status effects each turn"""
        expired_effects = []
        
        for effect, duration in self.status_effects.items():
            self.status_effects[effect] = duration - 1
            
            if self.status_effects[effect] <= 0:
                expired_effects.append(effect)
        
        # Remove expired effects
        for effect in expired_effects:
            del self.status_effects[effect]
            print(f"⏰ {self.name}'s {effect} effect expired")
    
    def get_effective_attack(self) -> int:
        """Get attack power with status effect modifiers"""
        attack = self.attack
        
        if "berserker" in self.status_effects:
            attack = int(attack * 1.5)
        
        return attack
    
    def get_effective_defense(self) -> int:
        """Get defense with status effect modifiers"""
        defense = self.defense
        
        if "defensive" in self.status_effects:
            defense = int(defense * 1.5)
        
        return defense
    
    def get_stats(self) -> Dict[str, Any]:
        """Return formatted stats"""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "focus": self.focus,
            "abilities": self.abilities,
            "status_effects": list(self.status_effects.keys()),
            "ai_pattern": self.ai_pattern
        }
    
    def get_loot(self) -> List[str]:
        """Get items dropped when defeated"""
        return self.loot.copy()
    
    def __str__(self) -> str:
        status = f" [{', '.join(self.status_effects.keys())}]" if self.status_effects else ""
        return f"{self.name} (HP: {self.hp}/{self.max_hp}){status}"


# Specialized enemy subclasses
class ClockworkSentinel(Enemy):
    """Heavily armored defensive enemy"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__("clockwork_sentinel", data)
        self.armor_plating = True
    
    def take_damage(self, damage: int) -> int:
        """Enhanced defense due to armor plating"""
        # Armor plating reduces damage by an additional 2
        actual_damage = max(1, damage - (self.defense + 2))
        self.hp = max(0, self.hp - actual_damage)
        print(f"🛡️ {self.name}'s armor deflects some damage! Took {actual_damage} damage!")
        return actual_damage


class RogueAutomaton(Enemy):
    """Fast, evasive hit-and-run enemy"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__("rogue_automaton", data)
        self.evasion_chance = 0.2  # 20% chance to dodge
    
    def take_damage(self, damage: int) -> int:
        """Has a chance to evade attacks"""
        if random.random() < self.evasion_chance:
            print(f"💨 {self.name} dodges the attack!")
            return 0
        
        return super().take_damage(damage)


class SteamGolem(Enemy):
    """Powerful but slow tank enemy"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__("steam_golem", data)
        self.steam_pressure = 3  # Can build up for powerful attacks
    
    def choose_action(self, player_hp: int, player_defense: int, player_focus: int = 0) -> Dict[str, Any]:
        """Steam Golem builds pressure for devastating attacks"""
        self.steam_pressure += 1
        
        # Release steam for massive damage every 3 turns
        if self.steam_pressure >= 3:
            self.steam_pressure = 0
            return {"type": "ability", "name": "steam_blast"}
        
        return super().choose_action(player_hp, player_defense, player_focus)


# Factory function to create enemies
def create_enemy(enemy_id: str, data: Dict[str, Any]) -> Enemy:
    """Factory function to create the appropriate enemy subclass"""
    if enemy_id == "clockwork_sentinel":
        return ClockworkSentinel(data)
    elif enemy_id == "rogue_automaton":
        return RogueAutomaton(data)
    elif enemy_id == "steam_golem":
        return SteamGolem(data)
    else:
        return Enemy(enemy_id, data)



