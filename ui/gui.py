"""
GUI module for Chronicles of Aether Gate
Handles the main game interface with room images, descriptions, and navigation
"""

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from ui.dialog import MessageDialog, SelectionDialog, ConfirmDialog

class GameGUI:
    def __init__(self, root):
        """Initialize the main game GUI"""
        self.root = root
        self.root.title("Chronicles of Aether Gate")
        # Don't override geometry - respect fullscreen from launcher
        self.root.resizable(True, True)
        
        # Keep reference to current image to prevent garbage collection
        self.current_image = None
        # Simple cache for resized PhotoImages keyed by (path, width, height)
        self._image_cache = {}
        
        self._setup_gui()
    
    def _setup_gui(self):
        """Set up all GUI elements"""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Chronicles of Aether Gate", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Image frame at the top
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(pady=(0, 10))
        
        # Room image label
        self.room_image_label = ttk.Label(self.image_frame, text="Loading room image...")
        self.room_image_label.pack()
        
        # Text frame for room description
        self.text_frame = ttk.Frame(main_frame)
        self.text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollable text area for room description
        self.text_scroll = ttk.Scrollbar(self.text_frame)
        self.text_scroll.pack(side='right', fill='y')
        
        self.room_desc = tk.Text(self.text_frame, height=12, wrap='word', 
                                font=("Arial", 12), state='disabled',
                                yscrollcommand=self.text_scroll.set)
        self.room_desc.pack(side='left', fill='both', expand=True)
        self.text_scroll.config(command=self.room_desc.yview)
        
        # Navigation buttons frame
        self.nav_frame = ttk.LabelFrame(main_frame, text="Navigation", padding=10)
        self.nav_frame.pack(fill='x', pady=(0, 10))
        
        # Create navigation buttons
        self.btn_north = ttk.Button(self.nav_frame, text="⬆️ North", width=12)
        self.btn_south = ttk.Button(self.nav_frame, text="⬇️ South", width=12)
        self.btn_east = ttk.Button(self.nav_frame, text="➡️ East", width=12)
        self.btn_west = ttk.Button(self.nav_frame, text="⬅️ West", width=12)
        
        # Arrange buttons in a cross pattern
        self.btn_north.grid(row=0, column=1, padx=5, pady=5)
        self.btn_west.grid(row=1, column=0, padx=5, pady=5)
        self.btn_east.grid(row=1, column=2, padx=5, pady=5)
        self.btn_south.grid(row=2, column=1, padx=5, pady=5)
        
        # Center the grid
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons frame
        self.action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        self.action_frame.pack(fill='x')
        
        self.btn_inventory = ttk.Button(self.action_frame, text="🎒 Inventory")
        self.btn_take = ttk.Button(self.action_frame, text="🎒 Take Item")
        self.btn_fight = ttk.Button(self.action_frame, text="⚔️ Fight")
        self.btn_help = ttk.Button(self.action_frame, text="❓ Help")
        self.btn_save = ttk.Button(self.action_frame, text="💾 Save")
        self.btn_load = ttk.Button(self.action_frame, text="📂 Load")
        self.btn_quit = ttk.Button(self.action_frame, text="🚪 Quit")
        
        
        self.btn_inventory.pack(side='left', padx=5)
        self.btn_take.pack(side='left', padx=5)
        # btn_fight packing is handled dynamically
        self.btn_help.pack(side='left', padx=5)
        self.btn_save.pack(side='left', padx=5)
        self.btn_load.pack(side='left', padx=5)
        self.btn_quit.pack(side='right', padx=5)
        # Hide fight button initially
        self.btn_fight.pack_forget()
    
    def set_room_description(self, description):
        """Update the room description text"""
        
        self.room_desc.config(state='normal')
        self.room_desc.delete('1.0', tk.END)
        self.room_desc.insert(tk.END, description)
        self.room_desc.config(state='disabled')
    
    def set_room_image(self, image_path):
        """
        Display the room image, with fallback to default image on error
        """
        try:
            # Try to load the specified image
            img = Image.open(image_path)

        except Exception as e:
            try:
                # Fallback to default image
                img = Image.open("data/images/default.png")
            except Exception as e2:
                # If even default fails, show text message
                self.room_image_label.config(image='', text="[Image not available]")
                self.current_image = None
                return
        
        # Resize image to fit nicely in the GUI and use cached PhotoImage if available
        target_size = (400, 300)
        cache_key = (getattr(img, 'filename', image_path), *target_size)
        cached = self._image_cache.get(cache_key)
        if cached is None:
            resized = img.resize(target_size, Image.Resampling.LANCZOS)
            cached = ImageTk.PhotoImage(resized)
            self._image_cache[cache_key] = cached
        self.current_image = cached
        
        # Display the image
        self.room_image_label.config(image=self.current_image, text="")
    
    def update_navigation_buttons(self, exits):
        """Enable/disable navigation buttons based on available exits"""
        # Disable all buttons first
        self.btn_north.config(state="disabled")
        self.btn_south.config(state="disabled")
        self.btn_east.config(state="disabled")
        self.btn_west.config(state="disabled")
        
        # Enable buttons for available exits
        if "north" in exits:
            self.btn_north.config(state="normal")
        if "south" in exits:
            self.btn_south.config(state="normal")
        if "east" in exits:
            self.btn_east.config(state="normal")
        if "west" in exits:
            self.btn_west.config(state="normal")
    
    def show_message(self, title, message):
        """Show an info message box"""
        dialog = MessageDialog(self.root, title, message)
        dialog.show()
        
    def show_item_selection(self, items):
        """Show a dialog for selecting an item from a list"""
        dialog = SelectionDialog(self.root, "Select an Item", 
                               "Which item would you like to take?", items)
        return dialog.show()
        self.root.wait_window(dialog)
        
        return result  # Will be None if cancelled, otherwise the index of the selected item
    
    def show_error(self, title, message):
        """Show an error dialog"""
        messagebox.showerror(title, message)
    
    def confirm_quit(self):
        """Ask user to confirm before quitting"""
        return messagebox.askyesno("Quit Game", "Are you sure you want to quit?")
