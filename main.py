"""
Main game controller for Chronicles of Aether Gate
Handles game state, room navigation, and GUI updates
"""

import tkinter as tk
import os
import sys
from ui.gui import GameGUI
from engine.world_loader import load_rooms
from models.player import Player
from engine.item_manager import ItemManager
from engine.combat import CombatEngine
from ui.combat_gui import CombatGUI
from ui.inventory_gui import InventoryGUI
from engine.save_load import SaveLoadManager
from engine.victory import VictoryManager
from ui.save_load_gui import SaveLoadGUI
from engine.sound_manager import SoundManager


class Game:
    def __init__(self, root):
        """Initialize the game"""
        try:
            self.root = root
            self.gui = GameGUI(root)
            self.player = Player("Aether Warden")
            self.item_manager = ItemManager()
            self.save_manager = SaveLoadManager()
            self.victory_manager = VictoryManager()

            # Sound manager (optional; falls back gracefully)
            self.sound = SoundManager(enabled=True)
            
            # Start background music if available
            try:
                bg_file = os.path.join("data", "sounds", "background.mp3")
                if os.path.exists(bg_file):
                    self.sound.play_music(bg_file, loop=True, volume=0.2)
            except Exception:
                pass  # Background music is optional
            
            self.rooms = load_rooms()
            if not self.rooms:
                raise Exception("Could not load room data! Check data/rooms.json")
            
            self._connect_buttons()
            self._setup_keyboard_shortcuts()
            
            # Set starting room
            self.current_room_key = "entrance"
            self.current_enemy = None
            
            self.update_room()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise  # Re-raise the exception so launcher can handle it
    
    def _connect_buttons(self):
        """Connect GUI buttons to game methods"""
        # Navigation buttons
        self.gui.btn_north.config(command=lambda: self.move("north"))
        self.gui.btn_south.config(command=lambda: self.move("south"))
        self.gui.btn_east.config(command=lambda: self.move("east"))
        self.gui.btn_west.config(command=lambda: self.move("west"))
        
        # Action buttons
        self.gui.btn_inventory.config(command=self.show_inventory)
        self.gui.btn_take.config(command=self.take_item)
        self.gui.btn_fight.config(command=self._fight_current_enemy) # Connecting the Fight button to a function that fights the current room's enemy
        self.gui.btn_help.config(command=self.show_help)
        self.gui.btn_save.config(command=self.save_game)
        self.gui.btn_load.config(command=self.load_game)
        self.gui.btn_quit.config(command=self.quit_game)
    
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for better accessibility"""
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_game())
        self.root.bind('<Control-o>', lambda e: self.load_game())
        self.root.bind('<Control-i>', lambda e: self.show_inventory())
        self.root.bind('<Control-h>', lambda e: self.show_help())
        self.root.bind('<Control-q>', lambda e: self.quit_game())
        self.root.bind('<Control-m>', lambda e: self._toggle_sound())
        
        # Arrow key navigation
        self.root.bind('<Up>', lambda e: self.move('north'))
        self.root.bind('<Down>', lambda e: self.move('south'))
        self.root.bind('<Left>', lambda e: self.move('west'))
        self.root.bind('<Right>', lambda e: self.move('east'))
        
        # Game action shortcuts
        self.root.bind('<KeyPress-f>', lambda e: self._handle_fight_key())
        self.root.bind('<KeyPress-F>', lambda e: self._handle_fight_key())
        self.root.bind('<KeyPress-t>', lambda e: self._handle_take_key())
        self.root.bind('<KeyPress-T>', lambda e: self._handle_take_key())
        
        # Focus the window so it can receive key events
        self.root.focus_set()
    
    def _toggle_sound(self):
        """Toggle sound on/off."""
        state = self.sound.toggle()
        self.gui.show_message("Sound", f"🔊 Sound {'enabled' if state else 'disabled'}")
        
        # When enabling, play a short confirmation beep
        if state:
            try:
                self.sound.play('menu')
            except Exception as e:
                print(f"⚠️ Error playing confirmation sound: {e}")
        
        # Note: Background music resume is handled automatically by SoundManager.toggle()
    
    def _handle_fight_key(self):
        """Handle F key press for fighting"""
        # Check if there's an enemy in the current room
        room = self.rooms.get(self.current_room_key, {})
        if 'enemy' in room:
            enemy_id = room['enemy']
            self.start_combat(enemy_id)
        else:
            self.gui.show_message("No Enemy", "There are no enemies to fight in this room.")
    
    def _handle_take_key(self):
        """Handle T key press for taking items"""
        self.take_item()

    def _fight_current_enemy(self):
        """Fight the enemy in the current room"""
        if hasattr(self, 'current_enemy') and self.current_enemy:
            self.start_combat(self.current_enemy)
        else:
            self.gui.show_message("No Enemy", "There's no enemy to fight here.")

    def update_room(self):
        """Update the GUI to show the current room"""
        room = self.rooms.get(self.current_room_key, {})
        
        # Get room info
        room_name = room.get('name', 'Unknown Room')
        room_desc = room.get('desc', 'An empty room.')
        exits = room.get('exits', {})
        
        # Format description
        full_description = f"{room_name}\n{'='*len(room_name)}\n\n{room_desc}"
        
        # Add exit information
        if exits:
            exit_names = list(exits.keys())
            full_description += f"\n\n🚪 Available exits: {', '.join(exit_names)}"
        else:
            full_description += "\n\n🚫 No exits available."
        
        # Add items in room
        # Get display names for items
        room_items = self.item_manager.get_item_names_in_room(self.current_room_key)
        
        if room_items:
            full_description += f"\n\n🎒 Items here: {', '.join(room_items)}"

        # Check if room has an enemy
        room_enemy = room.get('enemy', None)
        if room_enemy:
            # There's an enemy - show the fight button and remember the enemy
            full_description += f"\n\n⚔️ A {room_enemy} blocks your path!"
            self.current_enemy = room_enemy
            self._show_fight_button()
        else:
            # No enemy - hide the fight button and clear current enemy
            self.current_enemy = None
            self._hide_fight_button()
            
        # --------- ENEMY & ITEM LOGIC ----------
        # Take-Item button logic
        if room_enemy:
            # Enemy present ⇒ disable pickup
            self.gui.btn_take.config(state='disabled')
        else:
            # No enemy: enable only if items exist
            if room_items:
                self.gui.btn_take.config(state='normal')
            else:
                self.gui.btn_take.config(state='disabled')

        # Update GUI
        self.gui.set_room_description(full_description)
        
        # Set room image
        image_folder = "data/images"
        image_filename = f"{self.current_room_key}.png"
        image_path = os.path.join(image_folder, image_filename)
        self.gui.set_room_image(image_path)

        # Mark room as visited
        self.player.visit_room(self.current_room_key)
        
        # Update navigation buttons
        self.gui.update_navigation_buttons(exits)

        # Check if this is the victory room with all crystals
        if room.get('victory_room') and self.player.aether_crystals >= 3:
            victory_message = """🔮 THE AETHER GATE AWAKENS! 🔮

    With all three Aether Crystals in your possession, the gate responds to your presence!

    The crystals float from your inventory and slot perfectly into the gate's frame. 
    Energy cascades through the crystalline archway as ancient mechanisms whir to life.

    The portal stabilizes, revealing glimpses of distant worlds beyond!

    🎉 MISSION COMPLETE! 🎉

    Click 'Quit' to see your final victory statistics."""

            self.gui.show_message("🏆 VICTORY ACHIEVED! 🏆", victory_message)
            
            # Trigger victory check
            self.check_victory_conditions()
            return
        
        elif room.get('victory_room'):
            # In victory room but don't have enough crystals
            crystals_needed = 3 - self.player.aether_crystals
            full_description += f"\n\n💎 The gate remains dormant. You need {crystals_needed} more Aether Crystal{'s' if crystals_needed != 1 else ''} to activate it."
        
        # Standard victory check for other conditions
        self.check_victory_conditions()
    
    def _show_fight_button(self):
        """Show the fight button in the correct position"""
        self.gui.btn_fight.pack(side='left', padx=5, before=self.gui.btn_help)

    def _hide_fight_button(self):
        """Hide the fight button"""
        self.gui.btn_fight.pack_forget()
    
    def move(self, direction):
        """Move the player in a given direction"""
        room = self.rooms.get(self.current_room_key, {})
        exits = room.get('exits', {})
        
        if direction in exits:
            # Valid move
            next_room_key = exits[direction]
            
            if next_room_key in self.rooms:
                self.current_room_key = next_room_key
                self.update_room()
            else:
                error_msg = f"Room '{next_room_key}' not found in game data!"
                self.gui.show_error("Navigation Error", error_msg)
        else:
            # Invalid move
            self.gui.show_message("Cannot Go There", f"You cannot go {direction} from here.")
    
    def show_inventory(self):
        """Show advanced inventory GUI"""
        try:
            inventory_gui = InventoryGUI(self.root, self.player, self.item_manager)
            inventory_gui.set_callbacks(
                on_use_item=self._inventory_use_item,
                on_equip_item=self._inventory_equip_item,
                on_drop_item=self._inventory_drop_item
            )
        except Exception as e:
            self.gui.show_error("Inventory Error", f"Failed to open inventory: {e}")

    def _inventory_use_item(self, item_name: str):
        """Handle item use from inventory"""
        pass

    def _inventory_equip_item(self, item_name: str):
        """Handle item equip from inventory"""
        pass

    def _inventory_drop_item(self, item_name: str):
        """Handle item drop from inventory"""
        pass


    def take_item(self):
        """Take an item from the current room"""
        room_items = self.item_manager.get_room_items(self.current_room_key)
        
        if not room_items:
            self.gui.show_message("No Items", "There are no items to take in this room.")
            return
        
        # Get display names for selection
        item_display_names = self.item_manager.get_item_names_in_room(self.current_room_key)
        
        if len(room_items) == 1:
            # Only one item, take it automatically
            item = self.item_manager.take_item_from_room(self.current_room_key, room_items[0])
            if item:
                self.player.add_item(item.to_dict())
                self.gui.show_message("Item Taken", f"📦 You picked up: {item.name}")
                self.sound.play('pickup')
                self.update_room()  # Refresh room description
        else:
            # Multiple items - show selection dialog
            selected = self.gui.show_item_selection(item_display_names)
            if selected is not None:  # None means they cancelled
                selected_id = room_items[selected]  # Get the ID of the selected item
                item = self.item_manager.take_item_from_room(self.current_room_key, selected_id)
                if item:
                    self.player.add_item(item.to_dict())
                    self.gui.show_message("Item Taken", f"📦 You picked up: {item.name}")
                    self.sound.play('pickup')
                    self.update_room()  # Refresh room description

    def start_combat(self, enemy_id: str):
        """Start combat with an enemy"""
        try:
            # Create combat engine
            self.combat_engine = CombatEngine(self.player, enemy_id)
            
            # Create combat GUI
            self.combat_gui = CombatGUI(self.root)
            
            # Set combat callbacks
            self.combat_gui.set_callbacks(
                on_attack=self._combat_attack,
                on_ability=self._combat_ability,
                on_item=self._combat_item,
                on_flee=self._combat_flee
            )
            
            # Initialize combat display
            self._update_combat_display()
            
            # If enemy starts first, schedule enemy turn automatically
            if not self.combat_engine.is_player_turn():
                self.root.after(1000, self._enemy_turn)
        
        except Exception as e:
            self.gui.show_error("Combat Error", f"Failed to start combat: {e}")

    def _combat_attack(self):
        """Handle player attack in combat"""
        if hasattr(self, 'combat_engine'):
            result = self.combat_engine.player_attack()
            self.combat_gui.add_log_message(result)
            self._process_combat_turn()

    def _combat_ability(self, ability_name: str):
        """Handle player ability use in combat"""
        if hasattr(self, 'combat_engine'):
            result = self.combat_engine.player_use_ability(ability_name)
            self.combat_gui.add_log_message(result)
            self._process_combat_turn()

    def _combat_item(self, item_name: str):
        """Handle player item use in combat"""
        if hasattr(self, 'combat_engine'):
            result = self.combat_engine.player_use_item(item_name)
            self.combat_gui.add_log_message(result)
            self._process_combat_turn()

    def _combat_flee(self):
        """Handle player fleeing from combat"""
        self.combat_gui.add_log_message("🏃 You fled from combat!")
        self._end_combat("fled")

    def _process_combat_turn(self):
        """Process the next turn in combat"""
        if not hasattr(self, 'combat_engine'):
            return
        
        self._update_combat_display()
        
        if self.combat_engine.is_combat_over():
            winner = self.combat_engine.get_winner()
            if winner == "player":
                # Player won - remove enemy from room and give loot
                current_room = self.rooms.get(self.current_room_key, {})
                if 'enemy' in current_room:
                    del current_room['enemy']  # Remove enemy from room
                
                # Give loot (simplified)
                loot = ["Experience gained!", "Victory!"]
                self.combat_gui.show_combat_result(winner, loot)
                
                # Close combat windows
                if hasattr(self, 'combat_gui'):
                    self.combat_gui.close()
                    delattr(self, 'combat_gui')
                
                if hasattr(self, 'combat_engine'):
                    delattr(self, 'combat_engine')
                
                # Update room description after combat windows are closed
                self.update_room()
                
                # Auto-save after combat victory
                game_state = {"current_room": self.current_room_key}
                self.save_manager.save_game(self.player, game_state, "auto_save")
            else:
                # Handle other combat end cases (enemy win, etc)
                self._end_combat(winner)
        else:
            # After any player action, check if we need to trigger enemy turn
            # Update display first to show correct turn state
            self._update_combat_display()
            
            # Then check if it's enemy's turn and schedule enemy action
            if not self.combat_engine.is_player_turn():
                # Enemy turn after a short delay
                self.root.after(1500, self._enemy_turn)

    def _enemy_turn(self):
        """Execute enemy turn"""
        if hasattr(self, 'combat_engine'):
            result = self.combat_engine.enemy_turn()
            self.combat_gui.add_log_message(result)
            self._update_combat_display()
            
            if self.combat_engine.is_combat_over():
                self._end_combat(self.combat_engine.get_winner())

    def _update_combat_display(self):
        """Update the combat GUI display"""
        if hasattr(self, 'combat_gui') and hasattr(self, 'combat_engine'):
            combat_state = self.combat_engine.get_combat_state()
            player_stats = combat_state["player"]
            enemy_stats = combat_state["enemy"]
            self.combat_gui.update_combat_state(combat_state, player_stats, enemy_stats)

    def _end_combat(self, winner: str):
        """End combat and clean up for non-player victory scenarios"""
        if winner == "enemy":
            # Player lost
            self.combat_gui.show_combat_result(winner)
            
            # Close combat GUI
            if hasattr(self, 'combat_gui'):
                self.combat_gui.close()
                delattr(self, 'combat_gui')
            
            if hasattr(self, 'combat_engine'):
                delattr(self, 'combat_engine')
                
            # Check for defeat condition after closing combat
            self.root.after(1000, self.check_defeat_condition)
        elif winner == "fled":
            # Player fled - just close combat
            if hasattr(self, 'combat_gui'):
                self.combat_gui.close()
                delattr(self, 'combat_gui')
            
            if hasattr(self, 'combat_engine'):
                delattr(self, 'combat_engine')
    
    def show_help(self):
        """Show comprehensive help information"""
        help_text = """🎮 CHRONICLES OF AETHER GATE - Complete Guide

    🎯 OBJECTIVE:
    Collect 3 Aether Crystals and reach the Gate Chamber to win!

    🚶 NAVIGATION:
    • Use arrow buttons to move between rooms
    • Only available exits will be enabled
    • Explore all rooms to find items and crystals

    ⚔️ COMBAT:
    • Fight button appears when enemies are present
    • Turn-based combat with strategic abilities
    • Use Focus points for special attacks
    • Consumables can heal HP and restore Focus
    • Victory removes enemies from rooms permanently

    🎒 INVENTORY & ITEMS:
    • Click 'Take Item' to collect items in rooms
    • Open inventory to view, use, and equip items
    • Weapons and accessories boost your stats
    • Consumables heal HP and restore Focus
    • Key items like Aether Crystals are needed for victory

    💾 SAVE & LOAD:
    • Save your progress anytime
    • Multiple save slots available
    • Auto-save after combat victories
    • Load previous saves to retry challenges

    🏆 VICTORY CONDITIONS:
    • PRIMARY: Collect all 3 Aether Crystals
    • BONUS: Explore all rooms, defeat enemies
    • Reach the Gate Chamber with crystals to win

    📍 ROOM LOCATIONS:
    • Entrance Hall (starting point)
    • Clockwork Hallway (central hub)  
    • Crystal Laboratory (crystals & magic items)
    • Mechanical Armory (weapons & combat gear)
    • Gate Chamber (final destination)

    💡 TIPS:
    • Equipment changes your combat stats immediately
    • Some enemies have special abilities and AI patterns
    • Healing items are limited - use them wisely
    • Explore thoroughly - some rooms have multiple items
    • Save before difficult fights!

    🎊 ACHIEVEMENTS:
    • Crystal Master: Collect all crystals
    • Explorer: Visit all rooms
    • Warrior: Defeat multiple enemies
    • Untouchable: Complete without damage
    • Tactical Genius: Minimize damage taken

    Good luck, Aether Warden! ✨"""
        
        try:
            from ui.dialog import HelpDialog
            # Play a soft menu sound when opening help
            try:
                self.sound.play('menu')
            except Exception:
                pass
            HelpDialog(self.root)  # modal; centers itself
        except Exception:
            # Safe fallback to simple message
            self.gui.show_message("Help", help_text)

    
    def save_game(self):
        """Show save game GUI"""
        try:
            # Create current game state
            game_state = {
                "current_room": self.current_room_key,
                "rooms": self.rooms,
                "item_manager_state": {
                    "room_items": self.item_manager.room_items
                },
                "version": "1.0"
            }
            
            # Show save GUI
            save_gui = SaveLoadGUI(self.root, self.save_manager, mode="save")
            save_gui.set_callbacks(on_save=lambda name: self._perform_save(name, game_state))
            
        except Exception as e:
            self.gui.show_error("Save Error", f"Failed to open save dialog: {e}")

    def _perform_save(self, save_name: str, game_state: dict):
        """Actually perform the save operation"""
        if self.save_manager.save_game(self.player, game_state, save_name):
            self.gui.show_message("Game Saved", f"💾 Game saved as '{save_name}'!")
        else:
            self.gui.show_error("Save Failed", "Failed to save the game.")

    def load_game(self):
        """Show load game GUI"""
        try:
            load_gui = SaveLoadGUI(self.root, self.save_manager, mode="load")
            load_gui.set_callbacks(on_load=self._perform_load)
            
        except Exception as e:
            self.gui.show_error("Load Error", f"Failed to open load dialog: {e}")

    def _perform_load(self, save_name: str):
        """Actually perform the load operation"""
        save_data = self.save_manager.load_game(save_name)
        
        if not save_data:
            self.gui.show_error("Load Failed", "Failed to load the game.")
            return
        
        try:
            # Restore player
            self.player = Player.from_dict(save_data['player'])
            
            # Restore game state
            game_state = save_data['game_state']
            self.current_room_key = game_state.get('current_room', 'entrance')
            
            # Restore rooms state (preserves defeated enemies)
            if 'rooms' in game_state:
                self.rooms = game_state['rooms']
            
            # Restore item manager state
            if 'item_manager_state' in game_state:
                item_state = game_state['item_manager_state']
                if 'room_items' in item_state:
                    self.item_manager.room_items = item_state['room_items']
            
            # Update GUI
            self.update_room()
            
            self.gui.show_message("Game Loaded", f"📂 Loaded '{save_name}' successfully!")
            
        except Exception as e:
            self.gui.show_error("Load Error", f"Failed to restore game state: {e}")

    def check_victory_conditions(self):
        """Check if player has won the game"""
        has_won, victory_type, achievements = self.victory_manager.check_victory_conditions(self.player)
        
        if has_won:
            victory_message = self.victory_manager.get_victory_message(victory_type, achievements, self.player)
            self.gui.show_message("🎉 VICTORY! 🎉", victory_message)
            self.sound.play('victory')
            
            # Auto-save victory state
            game_state = {
                "current_room": self.current_room_key,
                "victory_achieved": True,
                "victory_type": victory_type,
                "achievements": achievements
            }
            self.save_manager.auto_save(self.player, game_state)
            
            return True
        
        return False

    def check_defeat_condition(self):
        """Check if player has been defeated"""
        if self.victory_manager.check_defeat_condition(self.player):
            defeat_message = self.victory_manager.get_defeat_message(self.player)
            self.gui.show_message("💀 DEFEAT 💀", defeat_message)
            self.sound.play('defeat')
            
            # Offer to load a save
            if self.gui.confirm_quit():
                self.load_game()
            
            return True
        
        return False

    def quit_game(self):
        """Quit the game with confirmation"""
        if self.gui.confirm_quit():
            print("👋 Thanks for playing Chronicles of Aether Gate!")
            self.root.quit()

def main():
    """Main entry point"""
    print("🔮 Starting Chronicles of Aether Gate...")
    
    # Verify required folders exist
    if not os.path.exists("data"):
        print("❌ Error: 'data' folder not found!")
        sys.exit(1)
    
    if not os.path.exists("data/images"):
        print("⚠️ Warning: 'data/images' folder not found. Creating it...")
        os.makedirs("data/images", exist_ok=True)
    
    # Create and run the game
    root = tk.Tk()
    game = Game(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Game interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
