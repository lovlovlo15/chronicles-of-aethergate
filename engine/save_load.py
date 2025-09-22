"""
Save/Load system for Chronicles of Aether Gate
Handles game state persistence with JSON files
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from models.player import Player

class SaveLoadManager:
    """Manages save and load operations for the game"""
    
    def __init__(self, save_directory='saves'):
        self.save_directory = save_directory
        
        # Create saves directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)
    
    def save_game(self, player: Player, game_state: Dict[str, Any], save_name: str = None) -> bool:
        """Save the current game state"""
        try:
            # Generate save name if not provided
            if not save_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"save_{timestamp}"
            
            # Create save data
            save_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "player": player.to_dict(),
                "game_state": game_state
            }
            
            # Save to file
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Load a saved game"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return save_data
            
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return None
    
    def get_save_files(self) -> list:
        """Get list of available save files"""
        try:
            saves = []
            
            if not os.path.exists(self.save_directory):
                return saves
            
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json') and filename != '.gitkeep':
                    save_name = filename[:-5]  # Remove .json extension
                    save_path = os.path.join(self.save_directory, filename)
                    
                    print(f"📁 Processing file: {filename} -> save_name: '{save_name}'")
                    
                    # Get file info
                    file_stats = os.stat(save_path)
                    modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                    
                    # Try to get additional info from save file
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                            player_data = save_data.get('player', {})
                            game_state = save_data.get('game_state', {})
                            
                            player_name = player_data.get('name', 'Unknown')
                            current_room = game_state.get('current_room', 'Unknown')
                            
                        saves.append({
                            'name': save_name,
                            'player_name': player_name,
                            'current_room': current_room,
                            'modified': modified_time,
                            'modified_str': modified_time.strftime("%Y-%m-%d %H:%M")
                        })
                        
                        print(f"✅ Added save: name='{save_name}', player='{player_name}', room='{current_room}'")
                        
                    except Exception as e:
                        print(f"⚠️ Error reading save file {filename}: {e}")
                        # Still add it with unknown data
                        saves.append({
                            'name': save_name,
                            'player_name': 'Corrupted',
                            'current_room': 'Unknown',
                            'modified': modified_time,
                            'modified_str': modified_time.strftime("%Y-%m-%d %H:%M")
                        })
            
            # Sort by modification time (newest first)
            saves.sort(key=lambda x: x['modified'], reverse=True)
            
            print(f"📋 Total saves found: {len(saves)}")
            return saves
            
        except Exception as e:
            print(f"❌ Error getting save files: {e}")
            import traceback
            traceback.print_exc()
            return []

    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        try:
            print(f"🗑️ SaveLoadManager.delete_save called with: '{save_name}'")
            print(f"🗑️ Save name type: {type(save_name)}")
            
            # Ensure we have a clean string
            if isinstance(save_name, list):
                print(f"❌ Error: save_name is a list: {save_name}")
                return False
            
            save_name = str(save_name).strip()
            if not save_name:
                print("❌ Error: Empty save name")
                return False
            
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            print(f"🗑️ Looking for save file at: {save_path}")
            
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"✅ Deleted save file: {save_path}")
                return True
            else:
                print(f"❌ Save file not found at: {save_path}")
                # List all files in save directory for debugging
                if os.path.exists(self.save_directory):
                    files = os.listdir(self.save_directory)
                    print(f"📁 Files in save directory: {files}")
                return False
                
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            import traceback
            traceback.print_exc()
            return False


