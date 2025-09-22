"""
Game Launcher for Chronicles of Aether Gate
Handles main menu and game initialization
"""

import tkinter as tk
import sys
import os
from ui.main_menu import MainMenu
from engine.sound_manager import SoundManager

class GameLauncher:
    """Manages game startup and menu flow"""
    
    def __init__(self):
        """Initialize the game launcher"""
        self.root = None
        self.main_menu = None
        self.game = None
        
    def start(self):
        """Start the application"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Chronicles of Aether Gate")
        
        # Maximize the window
        try:
            self.root.state('zoomed')
        except tk.TclError:
            # Fallback: set to screen size
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        
        self.root.resizable(True, True)
        
        # Prevent window from closing abruptly
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Initialize background music (if available)
        try:
            # Prepare a SoundManager instance bound to launcher window lifetime
            self.sound = SoundManager(enabled=True)
            # Prefer a local file if you've downloaded it to data/sounds/background.mp3
            bg_local = os.path.join("data", "sounds", "background.mp3")
            if os.path.exists(bg_local):
                result = self.sound.play_music(bg_local, loop=True, volume=0.2)
                if result:
                    print("🎵 Background music started")
                else:
                    print("⚠️ Background music failed to start")
        except Exception as e:
            print(f"⚠️ Background music initialization failed: {e}")

        # Show main menu
        self.show_main_menu()
        
        # Start the main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Game interrupted. Goodbye!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    def on_window_close(self):
        """Handle window close button"""
        print("🚪 Window close requested")
        if tk.messagebox.askyesno("Quit", "Are you sure you want to quit Chronicles of Aether Gate?"):
            self.quit_application()
            

        
    def show_main_menu(self):
        """Display the main menu"""
        print("📋 Showing main menu...")
        
        # Clear the window but don't destroy the root
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Reset window properties (keep fullscreen)
        self.root.title("Chronicles of Aether Gate")
        
        # Create main menu
        self.main_menu = MainMenu(self.root)
        self.main_menu.set_callbacks(
            on_new_game=self.start_new_game,
            on_load_game=self.start_with_load,
            on_quit=self.quit_application
        )
        
        print("✅ Main menu displayed")
        
    def start_new_game(self):
        """Start a new game"""
        print("🚀 Starting new game...")
        
        try:
            # Clear the window
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Reset window for game (keep fullscreen)
            self.root.title("Chronicles of Aether Gate - Game")
            
            # Import and create game
            print("📦 Importing Game class...")
            from main import Game
            
            print("🎮 Creating Game instance...")
            self.game = Game(self.root)
            
            print("✅ Game started successfully!")
            
            # Override quit to return to menu instead of closing
            def quit_to_menu():
                print("🔙 Quit to menu requested...")
                try:
                    if hasattr(self.game, 'gui') and hasattr(self.game.gui, 'confirm_quit'):
                        if self.game.gui.confirm_quit():
                            self.show_main_menu()
                    else:
                        if tk.messagebox.askyesno("Quit Game", "Return to main menu?"):
                            self.show_main_menu()
                except Exception as e:
                    print(f"Error in quit_to_menu: {e}")
                    self.show_main_menu()
            
            # Replace the game's quit function
            if hasattr(self.game, 'quit_game'):
                self.game.quit_game = quit_to_menu
            
        except Exception as e:
            print(f"❌ Failed to start game: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error and return to menu
            error_msg = f"Failed to start game:\n\n{str(e)}\n\nCheck console for details."
            tk.messagebox.showerror("Game Start Error", error_msg)
            self.show_main_menu()
    
    def start_with_load(self):
        """Start game and show load dialog"""
        print("📂 Starting with load...")
        
        # First start the normal game
        self.start_new_game()
        
        # Then show load dialog after a brief delay
        if hasattr(self, 'game') and self.game:
            self.root.after(1000, lambda: self.game.load_game() if hasattr(self.game, 'load_game') else None)
    
    def quit_application(self):
        """Quit the entire application"""
        print("👋 Thanks for playing Chronicles of Aether Gate!")
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)

def main():
    """Main entry point"""
    # Verify we're in the right directory
    if not os.path.exists("data"):
        print("❌ Error: Please run this from the game directory containing the 'data' folder")
        sys.exit(1)
        
    # Create and start the launcher
    launcher = GameLauncher()
    launcher.start()

if __name__ == "__main__":
    main()
