"""
Base dialog class for all popup windows in the game
"""

import tkinter as tk
import ttkbootstrap as ttk

class GameDialog(tk.Toplevel):
    """Base class for all game dialogs"""
    
    def __init__(self, parent, title, modal=True):
        """Initialize a dialog window"""
        super().__init__(parent)
        self._parent = parent
        
        # Basic window setup
        self.title(title)
        self.transient(parent)  # Dialog will minimize when parent minimizes
        
        # Initial position near parent; proper centering available via center_on_parent()
        try:
            self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")
        except Exception:
            # Fallback if parent isn't mapped yet
            self.geometry("+100+100")
        
        # Make modal by default
        if modal:
            self.grab_set()  # Make window modal
            
        # Configure window
        self.resizable(False, False)  # Prevent resizing
        self.protocol("WM_DELETE_WINDOW", self.close)  # Handle close button
        
        # Bind click outside to close if not modal
        if not modal:
            self.bind("<FocusOut>", lambda e: self.close())
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill='both', expand=True)
        
        # Result storage
        self.result = None

    def center_on_parent(self):
        """Center this dialog on its parent window."""
        try:
            self.update_idletasks()
            p = self._parent
            pw, ph = p.winfo_width(), p.winfo_height()
            px, py = p.winfo_x(), p.winfo_y()
            # Use current size or requested size if not yet laid out
            w = self.winfo_width() or self.winfo_reqwidth()
            h = self.winfo_height() or self.winfo_reqheight()
            if w <= 1:
                w = self.winfo_reqwidth()
            if h <= 1:
                h = self.winfo_reqheight()
            x = px + max((pw - w) // 2, 0)
            y = py + max((ph - h) // 2, 0)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            # Safe fallback position
            self.geometry("+120+120")
    
    def close(self):
        """Close the dialog"""
        self.destroy()
    
    def show(self):
        """Show dialog and return result"""
        # Wait for window to be destroyed
        self.wait_window()
        return self.result

class MessageDialog(GameDialog):
    """Dialog for showing messages"""
    
    def __init__(self, parent, title, message, modal=True):
        super().__init__(parent, title, modal)
        
        # Add message
        ttk.Label(self.main_frame, text=message, wraplength=400).pack(pady=10)
        
        # Add OK button
        ttk.Button(self.main_frame, text="OK", command=self.close).pack(pady=10)
        
        # Center the dialog on parent
        self.center_on_parent()

class SelectionDialog(GameDialog):
    """Dialog for selecting from a list of options"""
    
    def __init__(self, parent, title, message, options, modal=True):
        super().__init__(parent, title, modal)
        
        # Add message
        ttk.Label(self.main_frame, text=message, 
                 font=("Arial", 12)).pack(pady=10)
        
        # Variable to store the selection
        self.selected = tk.IntVar()
        self.selected.set(-1)  # Default to no selection
        
        # Add radio buttons for each option
        for i, option in enumerate(options):
            ttk.Radiobutton(self.main_frame, text=option, value=i,
                          variable=self.selected).pack(pady=2, padx=20, anchor='w')
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10, fill='x')
        
        # Add OK and Cancel buttons
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side='left', padx=10, expand=True)
        ttk.Button(btn_frame, text="Cancel", command=self.close).pack(side='right', padx=10, expand=True)
        
        # Center the dialog on parent
        self.center_on_parent()
    
    def _on_ok(self):
        """Handle OK button click"""
        if self.selected.get() >= 0:
            self.result = self.selected.get()
            self.close()

class ConfirmDialog(GameDialog):
    """Dialog for confirmation messages"""
    
    def __init__(self, parent, title, message, modal=True):
        super().__init__(parent, title, modal)
        
        # Add message
        ttk.Label(self.main_frame, text=message, wraplength=300).pack(pady=10)
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10, fill='x')
        
        # Add Yes and No buttons
        ttk.Button(btn_frame, text="Yes", command=self._on_yes).pack(side='left', padx=10, expand=True)
        ttk.Button(btn_frame, text="No", command=self._on_no).pack(side='right', padx=10, expand=True)
        
        # Center the dialog on parent
        self.center_on_parent()
    
    def _on_yes(self):
        """Handle Yes button click"""
        self.result = True
        self.close()
    
    def _on_no(self):
        """Handle No button click"""
        self.result = False
        self.close()

class HelpDialog(GameDialog):
    """Dialog for displaying game help"""
    
    def __init__(self, parent):
        super().__init__(parent, "Help - Chronicles of Aether Gate", modal=True)
        
        # Set minimum size and make resizable
        self.minsize(600, 500)
        self.resizable(True, True)
        
        # Configure main frame for expansion
        self.main_frame.pack_configure(padx=20, pady=20)
        
        # Create scrollable text area with better layout
        help_container = ttk.Frame(self.main_frame)
        help_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(help_container)
        scrollbar.pack(side='right', fill='y')
        
        # Add text widget with better formatting and spacing
        self.help_text = tk.Text(help_container, 
                                wrap='word', 
                                yscrollcommand=scrollbar.set,
                                font=("Arial", 11),  # Better font for readability
                                padx=20, pady=15,
                                relief='flat',
                                bg='white',
                                selectbackground='#e3f2fd',
                                width=80,  # Wider text area
                                height=30)  # Taller text area
        self.help_text.pack(side='left', fill='both', expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.help_text.yview)
        
        # Add help content
        self._add_help_content()
        
        # Make text widget read-only
        self.help_text.config(state='disabled')
        
        # Add OK button at the bottom
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="OK", command=self.close,
                   width=20).pack(anchor='center')
        
        # Center dialog on screen with larger default size for better readability
        self.geometry("1200x800")
        self.minsize(1000, 700)  # Minimum size to ensure content is visible
        self.center_on_parent()
    
    def _add_help_content(self):
        """Add formatted help content with better styling"""
        # Configure text tags with better fonts and colors
        self.help_text.tag_configure('title', 
                                     font=("Arial", 18, "bold"), 
                                     justify='center',
                                     foreground='#2c3e50',
                                     spacing3=20)
        self.help_text.tag_configure('section', 
                                     font=("Arial", 14, "bold"), 
                                     foreground='#0066cc',
                                     spacing1=10,
                                     spacing3=5)
        self.help_text.tag_configure('text', 
                                     font=("Arial", 11),
                                     foreground='#333333',
                                     lmargin1=20,
                                     lmargin2=20,
                                     spacing1=2)
        
        # Title
        self._add_section("CHRONICLES OF AETHER GATE\nComplete Game Guide\n\n", 'title')
        
        # Objective
        self._add_section("🎯 OBJECTIVE\n", 'section')
        self._add_text("Collect 3 Aether Crystals and reach the Gate Chamber to win!\n\n")
        
        # Navigation
        self._add_section("🚶 NAVIGATION\n", 'section')
        self._add_text("• Use arrow buttons to move between rooms\n")
        self._add_text("• Only available exits will be enabled\n")
        self._add_text("• Explore all rooms to find items and crystals\n\n")
        
        # Combat
        self._add_section("⚔️ COMBAT\n", 'section')
        self._add_text("• Fight button appears when enemies are present\n")
        self._add_text("• Turn-based combat with strategic abilities\n")
        self._add_text("• Use Focus points for special attacks\n")
        self._add_text("• Consumables can heal HP and restore Focus\n")
        self._add_text("• Victory removes enemies from rooms permanently\n\n")
        
        # Inventory
        self._add_section("🎒 INVENTORY & ITEMS\n", 'section')
        self._add_text("• Click 'Take Item' to collect items in rooms\n")
        self._add_text("• Open inventory to view, use, and equip items\n")
        self._add_text("• Weapons and accessories boost your stats\n")
        self._add_text("• Consumables heal HP and restore Focus\n")
        self._add_text("• Key items like Aether Crystals are needed for victory\n\n")
        
        # Save & Load
        self._add_section("💾 SAVE & LOAD\n", 'section')
        self._add_text("• Save your progress anytime\n")
        self._add_text("• Multiple save slots available\n")
        self._add_text("• Auto-save after combat victories\n")
        self._add_text("• Load previous saves to retry challenges\n\n")
        
        # Victory Conditions
        self._add_section("🏆 VICTORY CONDITIONS\n", 'section')
        self._add_text("• PRIMARY: Collect all 3 Aether Crystals\n")
        self._add_text("• BONUS: Explore all rooms, defeat enemies\n")
        self._add_text("• Reach the Gate Chamber with crystals to win\n\n")
        
        # Room Locations
        self._add_section("📍 ROOM LOCATIONS\n", 'section')
        self._add_text("• Entrance Hall (starting point)\n")
        self._add_text("• Clockwork Hallway (central hub)\n")
        self._add_text("• Crystal Laboratory (crystals & magic items)\n")
        self._add_text("• Mechanical Armory (weapons & combat gear)\n")
        self._add_text("• Gate Chamber (final objective)\n\n")
        
        # Controls
        self._add_section("🎮 KEYBOARD SHORTCUTS\n", 'section')
        self._add_text("• Arrow Keys: Move between rooms\n")
        self._add_text("• Ctrl+I: Open Inventory\n")
        self._add_text("• Ctrl+S: Save Game\n")
        self._add_text("• Ctrl+O: Load Game\n")
        self._add_text("• Ctrl+H: Show Help\n")
        self._add_text("• Ctrl+M: Toggle Sound On/Off\n")
        self._add_text("• F: Fight (when enemies present)\n")
        self._add_text("• T: Take Item (when items available)\n")

        # Sound Controls
        self._add_section("🔊 SOUND CONTROLS\n", 'section')
        self._add_text("• Press Ctrl+M to toggle sound on or off.\n")
        self._add_text("• If you don't hear sound: install 'pygame' for richer audio, or ensure a system audio player like 'paplay' or 'aplay' is available.\n")
        self._add_text("• The game falls back to a system bell if audio backends aren't available.\n\n")
    
    def _add_section(self, text, tag):
        """Add section with specified tag"""
        self.help_text.insert('end', text, tag)
    
    def _add_text(self, text):
        """Add regular text"""
        self.help_text.insert('end', text, 'text')
