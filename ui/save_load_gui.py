"""
Save/Load GUI for Chronicles of Aether Gate
Provides interface for managing game saves
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, simpledialog
from typing import Callable

class SaveLoadGUI:
    """Save/Load management window"""
    
    def __init__(self, parent, save_manager, mode="save"):
        """Initialize save/load GUI
        
        Args:
            parent: Parent window
            save_manager: SaveLoadManager instance
            mode: 'save' or 'load'
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"{'Save' if mode == 'save' else 'Load'} Game - Chronicles of Aether Gate")
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window on parent
        self._center_on_parent(parent)
        
        self.save_manager = save_manager
        self.mode = mode
        self.selected_save = None
        
        # Callbacks
        self.on_save = None
        self.on_load = None
        
        self._setup_gui()
        self._refresh_save_list()
        
    def _setup_gui(self):
        """Set up the save/load interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_text = "💾 SAVE GAME" if self.mode == "save" else "📂 LOAD GAME"
        title_label = ttk.Label(main_frame, text=title_text, 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Save files list
        list_frame = ttk.LabelFrame(main_frame, text="Save Files", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview for save files
        columns = ('name', 'player', 'room', 'date')
        self.save_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.save_tree.heading('name', text='Save Name')
        self.save_tree.heading('player', text='Player')
        self.save_tree.heading('room', text='Current Room')
        self.save_tree.heading('date', text='Date Modified')
        
        self.save_tree.column('name', width=150)
        self.save_tree.column('player', width=120)
        self.save_tree.column('room', width=150)
        self.save_tree.column('date', width=130)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.save_tree.yview)
        self.save_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.save_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.save_tree.bind('<<TreeviewSelect>>', self._on_select_save)
        self.save_tree.bind('<Double-1>', self._on_double_click)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        if self.mode == "save":
            self.action_button = ttk.Button(button_frame, text="💾 Save Game", 
                                           command=self._save_game)
            self.new_save_button = ttk.Button(button_frame, text="📝 New Save", 
                                             command=self._new_save)
            self.new_save_button.pack(side='left', padx=(0, 5))
        else:
            self.action_button = ttk.Button(button_frame, text="📂 Load Game", 
                                           command=self._load_game)
        
        self.action_button.pack(side='left', padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="🗑️ Delete", 
                                       command=self._delete_save)
        self.delete_button.pack(side='left', padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="🔄 Refresh", 
                                        command=self._refresh_save_list)
        self.refresh_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.close).pack(side='right')
        
        # Initially disable action buttons
        self._update_button_states()
    
    def _refresh_save_list(self):
        """Refresh the list of save files"""
        # Clear existing items
        for item in self.save_tree.get_children():
            self.save_tree.delete(item)
        
        # Get save files
        save_files = self.save_manager.get_save_files()
        print(f"📋 Found {len(save_files)} save files")
        
        # Populate treeview
        for save_info in save_files:
            print(f"📝 Processing save: {save_info}")
            
            # Extract individual values
            save_name = save_info['name']
            player_name = save_info['player_name']
            current_room = save_info['current_room']
            modified_str = save_info['modified_str']
            
            print(f"📝 Inserting: name='{save_name}', player='{player_name}', room='{current_room}', date='{modified_str}'")
            
            # Insert as tuple of separate values, not a single list
            self.save_tree.insert('', 'end', values=(
                save_name,      # Column 0
                player_name,    # Column 1
                current_room,   # Column 2
                modified_str    # Column 3
            ))
        
        # Update button states
        self._update_button_states()
        print(f"✅ Refreshed save list with {len(save_files)} saves")

    
    def _on_select_save(self, event):
        """Handle save file selection"""
        selection = self.save_tree.selection()
        if selection:
            item = self.save_tree.item(selection[0])
            values = item['values']
            
            print(f"🎯 Raw selection values: {values}")
            print(f"🎯 Values type: {type(values)}")
            
            if values and len(values) > 0:
                # Get the first column (save name) only
                self.selected_save = str(values[0])
                print(f"✅ Selected save name: '{self.selected_save}'")
            else:
                self.selected_save = None
                print("❌ No values in selection")
        else:
            self.selected_save = None
            print("❌ No save selected")
        
        self._update_button_states()

    
    def _on_double_click(self, event):
        """Handle double-click on save file"""
        if self.selected_save:
            if self.mode == "save":
                self._save_game()
            else:
                self._load_game()
    
    def _update_button_states(self):
        """Update button enabled/disabled states"""
        has_selection = self.selected_save is not None
        
        if self.mode == "save":
            self.action_button.config(state='normal' if has_selection else 'disabled')
        else:
            self.action_button.config(state='normal' if has_selection else 'disabled')
        
        self.delete_button.config(state='normal' if has_selection else 'disabled')
    
    def _save_game(self):
        """Handle save game action"""
        if not self.selected_save:
            messagebox.showwarning("No Selection", "Please select a save slot.")
            return
        
        # Confirm overwrite if save exists
        if messagebox.askyesno("Confirm Save", 
                              f"Overwrite save '{self.selected_save}'?"):
            if self.on_save:
                self.on_save(self.selected_save)
            self.close()
    
    def _new_save(self):
        """Create a new save with custom name"""
        save_name = simpledialog.askstring("New Save", "Enter save name:")
        if save_name:
            # Clean the save name
            save_name = "".join(c for c in save_name if c.isalnum() or c in (' ', '-', '_')).strip()
            if save_name:
                if self.on_save:
                    self.on_save(save_name)
                self.close()
    
    def _load_game(self):
        """Handle load game action"""
        if not self.selected_save:
            messagebox.showwarning("No Selection", "Please select a save file to load.")
            return
        
        save_name = str(self.selected_save).strip()
        print(f"📂 Loading game from: '{save_name}'")
        
        if self.on_load:
            self.on_load(save_name)
        self.close()
    
    def _delete_save(self):
        """Handle delete save action"""
        if not self.selected_save:
            messagebox.showwarning("No Selection", "Please select a save file to delete.")
            return
        
        print(f"🗑️ Attempting to delete save: '{self.selected_save}'")
        print(f"🗑️ Save type: {type(self.selected_save)}")
        
        # Ensure we have a string, not a list
        save_name = str(self.selected_save) if self.selected_save else ""
        
        if not save_name:
            messagebox.showerror("Error", "Invalid save file name.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                            f"Delete save '{save_name}'?\n\nThis cannot be undone."):
            
            print(f"🗑️ Deleting save file: '{save_name}'")
            
            if self.save_manager.delete_save(save_name):
                messagebox.showinfo("Deleted", f"Save '{save_name}' deleted successfully.")
                self.selected_save = None  # Clear selection
                self._refresh_save_list()
                print(f"✅ Save '{save_name}' deleted successfully")
            else:
                messagebox.showerror("Error", f"Failed to delete save file '{save_name}'.")
                print(f"❌ Failed to delete save '{save_name}'")

    
    def set_callbacks(self, on_save: Callable = None, on_load: Callable = None):
        """Set callback functions"""
        self.on_save = on_save
        self.on_load = on_load
    
    def _center_on_parent(self, parent):
        """Center this window on its parent window"""
        try:
            self.window.update_idletasks()
            
            # Get parent window dimensions and position
            pw, ph = parent.winfo_width(), parent.winfo_height()
            px, py = parent.winfo_x(), parent.winfo_y()
            
            # Get dialog dimensions
            w = self.window.winfo_width() or self.window.winfo_reqwidth()
            h = self.window.winfo_height() or self.window.winfo_reqheight()
            if w <= 1:
                w = self.window.winfo_reqwidth()
            if h <= 1:
                h = self.window.winfo_reqheight()
            
            # Calculate centered position
            x = px + max((pw - w) // 2, 0)
            y = py + max((ph - h) // 2, 0)
            
            # Set the position
            self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            # Safe fallback position
            self.window.geometry("+200+200")
    
    def close(self):
        """Close the save/load window"""
        self.window.destroy()
