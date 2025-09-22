"""
Main Menu for Chronicles of Aether Gate
Professional title screen with game options
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class MainMenu:
    """Main menu title screen"""
    
    def __init__(self, parent):
        """Initialize main menu"""
        self.root = parent
        self._image_cache = {}

        # Callbacks
        self.on_new_game = None
        self.on_load_game = None
        self.on_quit = None
        
        self._setup_menu()
        
    def _setup_menu(self):
        """Set up the main menu interface"""
        # Main container - pack into the parent window directly
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)
        
        # Title section
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(expand=True, fill='x', pady=(50, 30))
        
        # Game title
        title_label = ttk.Label(title_frame, text="CHRONICLES OF", 
                            font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="AETHER GATE", 
                                font=("Arial", 32, "bold"))
        subtitle_label.pack()
        
        # Version info
        version_label = ttk.Label(title_frame, text="Version 1.0", 
                                font=("Arial", 10))
        version_label.pack(pady=(5, 0))
        
        # Try to load a background image or create a simple design
        self._setup_visual_elements(self.main_frame)
        
        # Menu buttons
        menu_frame = ttk.Frame(self.main_frame)
        menu_frame.pack(expand=True, pady=20)
        
        # Create stylish menu buttons
        button_style = {"width": 20, "padding": (10, 5)}
        
        new_game_btn = ttk.Button(menu_frame, text="🚀 New Game", 
                                command=self._new_game, **button_style)
        new_game_btn.pack(pady=5)
        
        load_game_btn = ttk.Button(menu_frame, text="📂 Load Game", 
                                command=self._load_game, **button_style)
        load_game_btn.pack(pady=5)
        
        help_btn = ttk.Button(menu_frame, text="❓ Help", 
                            command=self._show_help, **button_style)
        help_btn.pack(pady=5)
        
        credits_btn = ttk.Button(menu_frame, text="👨‍💻 Credits", 
                                command=self._show_credits, **button_style)
        credits_btn.pack(pady=5)
        
        quit_btn = ttk.Button(menu_frame, text="🚪 Quit", 
                            command=self._quit_game, **button_style)
        quit_btn.pack(pady=(20, 5))
        
        # Footer
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(side='bottom', fill='x', pady=10)
        
        footer_label = ttk.Label(footer_frame, 
                                text="A steampunk text adventure RPG", 
                                font=("Arial", 10, "italic"))
        footer_label.pack()

        
    def _setup_visual_elements(self, parent):
        """Add visual elements to the menu"""
        visual_frame = ttk.Frame(parent)
        visual_frame.pack(pady=20)
        
        # Try to load the game logo
        try:
            logo_path = os.path.join("data", "images", "game_logo.png")
            if os.path.exists(logo_path):
                cache_key = (logo_path, 200, 200)
                logo_photo = self._image_cache.get(cache_key)
                if logo_photo is None:
                    img = Image.open(logo_path)
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(img)
                    self._image_cache[cache_key] = logo_photo
                
                logo_label = ttk.Label(visual_frame, image=logo_photo)
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack()
            else:
                # Fallback ASCII art
                ascii_art = """
        ⚙️    🔮    ⚙️
        ╔═══════╗
        ║ AETHER ║
        ║  GATE  ║
        ╚═══════╝
        ⚙️    🔮    ⚙️
                """
                art_label = ttk.Label(visual_frame, text=ascii_art, 
                                    font=("Courier", 12), justify='center')
                art_label.pack()
        except Exception as e:
            print(f"Could not load logo: {e}")
            # Fallback to ASCII art
            ascii_art = """
        ⚙️    🔮    ⚙️
        ╔═══════╗
        ║ AETHER ║
        ║  GATE  ║
        ╚═══════╝
        ⚙️    🔮    ⚙️
            """
            art_label = ttk.Label(visual_frame, text=ascii_art, 
                                font=("Courier", 12), justify='center')
            art_label.pack()
      
    def _new_game(self):
        """Start a new game"""
        print("🚀 New Game clicked in MainMenu")
        if self.on_new_game:
            self.on_new_game()
        
    def _load_game(self):
        """Load a saved game"""
        print("📂 Load Game clicked in MainMenu")
        if self.on_load_game:
            self.on_load_game()
            
    def _show_help(self):
        """Show game help"""
        from ui.dialog import HelpDialog
        dialog = HelpDialog(self.root)
        dialog.show()
        
    def _show_credits(self):
        """Show game credits"""
        credits_text = """🎮 CHRONICLES OF AETHER GATE
        
👨‍💻 DEVELOPMENT:
• Game Design & Programming
• User Interface Development  
• Combat System Implementation
• Save/Load System Architecture

🛠️ TECHNOLOGIES USED:
• Python 3.12
• Tkinter GUI Framework
• ttkbootstrap for modern styling
• Pillow (PIL) for image handling
• JSON for data storage

🎨 ASSETS:
• AI-generated room illustrations
• AI-generated item icons
• Custom enemy portraits
• Original game design

📝 SPECIAL THANKS:
• The Python community
• Open source contributors
• Steampunk genre inspiration

🎊 THANK YOU FOR PLAYING!

This game was created as a portfolio project 
demonstrating Python GUI development, 
game architecture, and software engineering skills.

Version 1.0 - 2025"""
        
        messagebox.showinfo("Credits", credits_text)
        
    def _quit_game(self):
        """Quit the application"""
        print("🚪 Quit clicked in MainMenu")
        if self.on_quit:
            self.on_quit()
                
    def set_callbacks(self, on_new_game=None, on_load_game=None, on_quit=None):
        """Set callback functions"""
        self.on_new_game = on_new_game
        self.on_load_game = on_load_game
        self.on_quit = on_quit
