"""
Victory condition system for Chronicles of Aether Gate
Handles win/lose conditions and game completion
"""

from typing import Dict, Any, List, Tuple
from models.player import Player

class VictoryManager:
    """Manages victory conditions and game ending"""
    
    def __init__(self):
        """Initialize victory manager"""
        self.victory_conditions = {
            "aether_crystals": 3,  # Need 3 crystals to win
            "required_rooms": ["entrance", "hallway", "laboratory", "armory"],  # Must visit all
            "min_enemies_defeated": 2  # Must defeat at least 2 enemies
        }
        
        print("🏆 Victory Manager initialized")
    
    def check_victory_conditions(self, player: Player) -> Tuple[bool, str, List[str]]:
        """Check if player has won the game
        
        Returns:
            Tuple of (has_won, victory_type, achievements)
        """
        achievements = []
        victory_messages = []
        
        # Check Aether Crystals (main victory condition)
        crystals_needed = self.victory_conditions["aether_crystals"]
        if player.aether_crystals >= crystals_needed:
            victory_messages.append(f"🔮 Collected all {crystals_needed} Aether Crystals!")
            achievements.append("Crystal Master")
        
        # Check room exploration
        required_rooms = set(self.victory_conditions["required_rooms"])
        visited_rooms = player.visited_rooms
        if required_rooms.issubset(visited_rooms):
            achievements.append("Explorer")
            victory_messages.append("🗺️ Explored the entire facility!")
        
        # Check combat achievements
        min_enemies = self.victory_conditions["min_enemies_defeated"]
        if player.enemies_defeated >= min_enemies:
            achievements.append("Warrior")
            victory_messages.append(f"⚔️ Defeated {player.enemies_defeated} enemies!")
        
        # Bonus achievements
        if player.total_damage_taken == 0:
            achievements.append("Untouchable")
            victory_messages.append("🛡️ Completed without taking damage!")
        
        if player.total_damage_taken < 20:
            achievements.append("Tactical Genius")
            victory_messages.append("🧠 Minimized damage taken!")
        
        if len(visited_rooms) >= len(required_rooms):
            achievements.append("Thorough Explorer")
        
        # Determine victory
        main_victory = player.aether_crystals >= crystals_needed
        
        if main_victory:
            victory_type = "complete" if len(achievements) >= 3 else "standard"
            return True, victory_type, achievements
        
        return False, "none", achievements
    
    def get_victory_message(self, victory_type: str, achievements: List[str], player: Player) -> str:
        """Generate victory message based on achievements"""
        if victory_type == "complete":
            message = """🎉 COMPLETE VICTORY! 🎉

You have mastered the mysteries of the Aether Gate!

The ancient facility hums with renewed energy as the three Aether Crystals 
resonate in perfect harmony. The dimensional gateway stabilizes, revealing 
vistas of distant worlds waiting to be explored.

Your tactical prowess and thorough exploration have unlocked the full 
potential of this remarkable discovery. The knowledge you've gained here 
will echo through the ages.

The Chronicles of Aether Gate conclude with your triumph!"""

        elif victory_type == "standard":
            message = """🎊 VICTORY! 🎊

You have successfully gathered the three Aether Crystals!

The gateway flickers to life, its mechanisms responding to the crystals' 
power. Though your journey through the facility was swift, you've 
accomplished the primary mission.

The Aether Gate stands ready to unlock new frontiers of discovery.

Well done, Aether Warden!"""

        else:
            message = "🎯 Mission Incomplete\n\nYou still need to gather the Aether Crystals to activate the gate."
        
        # Add achievements
        if achievements:
            message += f"\n\n🏆 ACHIEVEMENTS UNLOCKED:\n"
            for achievement in achievements:
                message += f"• {achievement}\n"
        
        # Add final stats
        message += f"""
📊 FINAL STATISTICS:
• Rooms Explored: {len(player.visited_rooms)}
• Enemies Defeated: {player.enemies_defeated}
• Damage Taken: {player.total_damage_taken}
• Damage Dealt: {player.total_damage_dealt}
• Items Collected: {len(player.inventory)}

Thank you for playing Chronicles of Aether Gate!"""
        
        return message
    
    def check_defeat_condition(self, player: Player) -> bool:
        """Check if player has lost the game"""
        return not player.is_alive()
    
    def get_defeat_message(self, player: Player) -> str:
        """Generate defeat message"""
        return f"""💀 DEFEAT 💀

The Aether Gate's guardians have proven too powerful...

Your journey ends here, but your courage will be remembered.
The mysteries of the gate remain locked, waiting for another 
brave soul to uncover their secrets.

📊 Your Statistics:
• Rooms Explored: {len(player.visited_rooms)}
• Enemies Defeated: {player.enemies_defeated}
• Damage Dealt: {player.total_damage_dealt}
• Aether Crystals Found: {player.aether_crystals}/3

Better luck next time, Aether Warden!"""



