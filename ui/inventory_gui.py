"""
Inventory GUI for Chronicles of Aether Gate
Provides comprehensive item management interface
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from typing import Callable, Optional, Dict, Any, List
from PIL import Image, ImageTk
import os
from ui.dialog import MessageDialog, SelectionDialog, ConfirmDialog

class InventoryGUI:
    """Advanced inventory management window"""
    
    def __init__(self, parent, player, item_manager):
        """Initialize inventory GUI"""
        self.window = tk.Toplevel(parent)
        self.window.title("Inventory - Chronicles of Aether Gate")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        self.window.minsize(1000, 700)  # Minimum size to ensure content is visible
        
        # Make window modal and position it relative to parent
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window on parent
        self.window.update_idletasks()  # Ensure window dimensions are calculated
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        window_width = 1200
        window_height = 800
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)  # Handle close button
        
        self.player = player
        self.item_manager = item_manager
        
        # Callbacks
        self.on_use_item = None
        self.on_equip_item = None
        self.on_drop_item = None
        
        # GUI elements
        self.item_buttons = {}
        self.item_icons = {}
        # Cache resized icons by path+size
        self._icon_cache = {}  # type: Dict[tuple, ImageTk.PhotoImage]
        
        self._setup_gui()
        self._refresh_inventory()
        
    def _setup_gui(self):
        """Set up the inventory interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎒 INVENTORY 🎒", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Top section: Player stats and equipment
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Player info (left)
        player_frame = ttk.LabelFrame(top_frame, text="👤 Character", padding=10)
        player_frame.pack(side='left', fill='y', padx=(0, 5))
        
        self.player_name_label = ttk.Label(player_frame, text=self.player.name,
                                          font=("Arial", 12, "bold"))
        self.player_name_label.pack()
        
        # Player stats
        stats_text = f"""HP: {self.player.hp}/{self.player.max_hp}
Focus: {self.player.focus}/{self.player.max_focus}
ATK: {self.player.attack} | DEF: {self.player.defense}
SPD: {self.player.speed}

Aether Crystals: {self.player.aether_crystals}/3"""
        
        self.player_stats_label = ttk.Label(player_frame, text=stats_text,
                                           font=("Arial", 10))
        self.player_stats_label.pack()
        
        # Equipment section (right)
        equipment_frame = ttk.LabelFrame(top_frame, text="⚔️ Equipment", padding=10)
        equipment_frame.pack(side='right', fill='y', padx=(5, 0))
        
        # Weapon slot
        weapon_frame = ttk.Frame(equipment_frame)
        weapon_frame.pack(fill='x', pady=5)
        
        ttk.Label(weapon_frame, text="Weapon:", font=("Arial", 10, "bold")).pack(side='left')
        weapon_name = self.player.equipped_weapon.get('name', 'None') if self.player.equipped_weapon else 'None'
        self.weapon_label = ttk.Label(weapon_frame, text=weapon_name)
        self.weapon_label.pack(side='right')
        
        # Accessory slot
        accessory_frame = ttk.Frame(equipment_frame)
        accessory_frame.pack(fill='x', pady=5)
        
        ttk.Label(accessory_frame, text="Accessory:", font=("Arial", 10, "bold")).pack(side='left')
        accessory_name = self.player.equipped_accessory.get('name', 'None') if self.player.equipped_accessory else 'None'
        self.accessory_label = ttk.Label(accessory_frame, text=accessory_name)
        self.accessory_label.pack(side='right')
        
        # Unequip buttons
        ttk.Button(equipment_frame, text="Unequip Weapon", 
                  command=self._unequip_weapon).pack(fill='x', pady=2)
        ttk.Button(equipment_frame, text="Unequip Accessory",
                  command=self._unequip_accessory).pack(fill='x', pady=2)
        
        # Inventory grid
        inventory_frame = ttk.LabelFrame(main_frame, text="📦 Items", padding=10)
        inventory_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollable frame for items
        canvas = tk.Canvas(inventory_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(inventory_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Item details panel
        details_frame = ttk.LabelFrame(main_frame, text="📜 Item Details", padding=10)
        details_frame.pack(fill='x')
        
        self.item_details = tk.Text(details_frame, height=6, wrap='word',
                                   font=("Arial", 10), state='disabled')
        self.item_details.pack(fill='x')
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=(10, 0))
        
        self.use_button = ttk.Button(action_frame, text="✨ Use Item", 
                                    command=self._use_selected_item)
        self.use_button.pack(side='left', padx=(0, 5))
        
        self.equip_button = ttk.Button(action_frame, text="⚔️ Equip", 
                                      command=self._equip_selected_item)
        self.equip_button.pack(side='left', padx=5)
        
        self.drop_button = ttk.Button(action_frame, text="🗑️ Drop", 
                                     command=self._drop_selected_item)
        self.drop_button.pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="❌ Close", 
                  command=self.close).pack(side='right')
        
        # Selected item tracking
        self.selected_item = None
        
    def _refresh_inventory(self):
        """Refresh the inventory display"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.item_buttons.clear()
        self.item_icons.clear()  # Clear all icon references
        
        # Group items by type for better organization
        weapons = []
        consumables = []
        accessories = []
        key_items = []
        misc_items = []
        
        for item in self.player.inventory:
            item_type = item.get('type', 'misc')
            if item_type == 'weapon':
                weapons.append(item)
            elif item_type == 'consumable':
                consumables.append(item)
            elif item_type == 'accessory':
                accessories.append(item)
            elif item_type == 'key_item':
                key_items.append(item)
            else:
                misc_items.append(item)
        
        # Display items by category
        categories = [
            ("🔮 Key Items", key_items),
            ("⚔️ Weapons", weapons),
            ("💍 Accessories", accessories),
            ("🧪 Consumables", consumables),
            ("📦 Miscellaneous", misc_items)
        ]
        
        row = 0
        for category_name, items in categories:
            if items:  # Only show categories with items
                # Category header
                category_label = ttk.Label(self.scrollable_frame, text=category_name,
                                          font=("Arial", 12, "bold"))
                category_label.grid(row=row, column=0, columnspan=4, 
                                   sticky='w', padx=5, pady=(10, 5))
                row += 1
                
                # Items in grid (4 columns)
                col = 0
                for item in items:
                    self._create_item_button(item, row, col)
                    col += 1
                    if col >= 4:
                        col = 0
                        row += 1
                
                if col > 0:  # If we're not at the start of a new row
                    row += 1
        
        # Update equipment labels
        weapon_name = self.player.equipped_weapon.get('name', 'None') if self.player.equipped_weapon else 'None'
        self.weapon_label.config(text=weapon_name)
        
        accessory_name = self.player.equipped_accessory.get('name', 'None') if self.player.equipped_accessory else 'None'
        self.accessory_label.config(text=accessory_name)
        
        # Update player stats
        stats_text = f"""HP: {self.player.hp}/{self.player.max_hp}
Focus: {self.player.focus}/{self.player.max_focus}
ATK: {self.player.attack} | DEF: {self.player.defense}
SPD: {self.player.speed}

Aether Crystals: {self.player.aether_crystals}/3"""
        
        self.player_stats_label.config(text=stats_text)
        
    def _create_item_button(self, item: Dict[str, Any], row: int, col: int):
        """Create an item button with icon and tooltip"""
        item_frame = ttk.Frame(self.scrollable_frame, relief='ridge', padding=2)
        item_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        
        # Generate a unique key for this item to ensure proper reference management
        item_key = f"{item.get('name', 'unknown')}_{id(item)}"
        
        # Try to load item icon
        icon_path = os.path.join("data/images", item.get('icon', 'default_item.png'))
        try:
            cache_key = (icon_path, 48, 48)
            icon = self._icon_cache.get(cache_key)
            if icon is None:
                img = Image.open(icon_path)
                img = img.resize((48, 48), Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self._icon_cache[cache_key] = icon
        except Exception:
            # Create a simple colored square if no icon
            img = Image.new('RGB', (48, 48), color=self._get_rarity_color(item.get('rarity', 'common')))
            icon = ImageTk.PhotoImage(img)
        
        # Item button
        item_button = ttk.Button(item_frame, image=icon,
                                command=lambda i=item: self._select_item(i))
        item_button.pack()
        
        # Keep reference to prevent garbage collection - use unique key
        self.item_icons[item_key] = icon
        
        # Item name label
        name_label = ttk.Label(item_frame, text=item.get('name', 'Unknown')[:12],
                              font=("Arial", 8), justify='center')
        name_label.pack()
        
        # Tooltip on hover
        self._create_tooltip(item_button, self._get_item_tooltip(item))
        
    def _get_rarity_color(self, rarity: str) -> str:
        """Get color based on item rarity"""
        colors = {
            'common': '#808080',    # Gray
            'uncommon': '#1eff00',  # Green
            'rare': '#0070dd',      # Blue
            'epic': '#a335ee',      # Purple
            'legendary': '#ff8000'  # Orange
        }
        return colors.get(rarity, '#808080')
    
    def _get_item_tooltip(self, item: Dict[str, Any]) -> str:
        """Generate tooltip text for an item"""
        tooltip = f"**{item.get('name', 'Unknown Item')}**\n"
        tooltip += f"Type: {item.get('type', 'misc').title()}\n"
        tooltip += f"Rarity: {item.get('rarity', 'common').title()}\n\n"
        tooltip += f"{item.get('description', 'No description.')}\n"
        
        stats = item.get('stats', {})
        if stats:
            tooltip += "\n**Effects:**\n"
            for stat, value in stats.items():
                if stat == "attack_bonus":
                    tooltip += f"• +{value} Attack\n"
                elif stat == "defense_bonus":
                    tooltip += f"• +{value} Defense\n"
                elif stat == "focus_bonus":
                    tooltip += f"• +{value} Max Focus\n"
                elif stat == "heal_amount":
                    tooltip += f"• Heals {value} HP\n"
                elif stat == "focus_restore":
                    tooltip += f"• Restores {value} Focus\n"
        
        return tooltip
    
    def _create_tooltip(self, widget, text: str):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _select_item(self, item: Dict[str, Any]):
        """Select an item and show its details"""
        self.selected_item = item
        
        # Show item details
        details_text = self._get_item_tooltip(item)
        
        self.item_details.config(state='normal')
        self.item_details.delete('1.0', tk.END)
        self.item_details.insert('1.0', details_text)
        self.item_details.config(state='disabled')
        
        # Update button states
        item_type = item.get('type', 'misc')
        
        # Use button
        can_use = item_type in ['consumable', 'weapon', 'accessory']
        self.use_button.config(state='normal' if can_use else 'disabled')
        
        # Equip button
        can_equip = item_type in ['weapon', 'accessory']
        self.equip_button.config(state='normal' if can_equip else 'disabled')
        
        # Drop button (always enabled for selected item)
        self.drop_button.config(state='normal')
    
    def _use_selected_item(self):
        """Use the selected item"""
        if not self.selected_item:
            messagebox.showwarning("No Item Selected", "Please select an item first.")
            return
        
        item_name = self.selected_item.get('name', '')
        item_type = self.selected_item.get('type', '')
        
        if item_type == 'consumable':
            # Use consumable
            result = self._use_consumable(self.selected_item)
            messagebox.showinfo("Item Used", result)
            
            # Remove from inventory if not stackable
            if not self.selected_item.get('stackable', False):
                self.player.remove_item(item_name)
            
            self.selected_item = None
            self._refresh_inventory()
            
        elif item_type in ['weapon', 'accessory']:
            # Equip the item
            self._equip_selected_item()
        
        else:
            messagebox.showinfo("Cannot Use", f"You cannot use {item_name}.")
    
    def _use_consumable(self, item: Dict[str, Any]) -> str:
        """Use a consumable item"""
        stats = item.get('stats', {})
        results = []
        
        if 'heal_amount' in stats:
            healed = self.player.heal(stats['heal_amount'])
            results.append(f"Healed {healed} HP")
        
        if 'focus_restore' in stats:
            restored = self.player.restore_focus(stats['focus_restore'])
            results.append(f"Restored {restored} Focus")
        
        if results:
            return f"✨ {item.get('name', 'Item')} used! " + ", ".join(results)
        else:
            return f"❓ {item.get('name', 'Item')} had no effect."
    
    def _equip_selected_item(self):
        """Equip the selected item"""
        if not self.selected_item:
            MessageDialog(self.window, "No Item Selected", "Please select an item first.").show()
            return
        
        item_type = self.selected_item.get('type', '')
        item_name = self.selected_item.get('name', '')
        
        if item_type == 'weapon':
            if self.player.equip_weapon(self.selected_item):
                self.player.remove_item(item_name)  # Remove from inventory after equipping
                MessageDialog(self.window, "Item Equipped", f"⚔️ Equipped {item_name}!").show()
                self._refresh_inventory()
            else:
                MessageDialog(self.window, "Equip Failed", f"Cannot equip {item_name}", modal=True).show()
        
        elif item_type == 'accessory':
            if self.player.equip_accessory(self.selected_item):
                self.player.remove_item(item_name)  # Remove from inventory after equipping
                MessageDialog(self.window, "Item Equipped", f"💍 Equipped {item_name}!").show()
                self._refresh_inventory()
            else:
                MessageDialog(self.window, "Equip Failed", f"Cannot equip {item_name}", modal=True).show()
    
    def _drop_selected_item(self):
        """Drop the selected item"""
        if not self.selected_item:
            MessageDialog(self.window, "No Item Selected", "Please select an item first.").show()
            return
        
        item_name = self.selected_item.get('name', '')
        
        dialog = ConfirmDialog(self.window, "Drop Item", 
                            f"Are you sure you want to drop {item_name}?")
        
        if dialog.show():
            self.player.remove_item(item_name)
            MessageDialog(self.window, "Item Dropped", f"🗑️ Dropped {item_name}").show()
            
            self.selected_item = None
            self._refresh_inventory()
    
    def _unequip_weapon(self):
        """Unequip current weapon"""
        if self.player.equipped_weapon:
            weapon = self.player.unequip_weapon()
            if weapon:
                self.player.add_item(weapon)  # Add unequipped weapon back to inventory
                MessageDialog(self.window, "Weapon Unequipped", 
                            f"Unequipped {weapon.get('name', 'weapon')}").show()
                self._refresh_inventory()
        else:
            MessageDialog(self.window, "No Weapon", 
                        "No weapon is currently equipped.").show()
    
    def _unequip_accessory(self):
        """Unequip current accessory"""
        if self.player.equipped_accessory:
            accessory = self.player.unequip_accessory()
            if accessory:
                self.player.add_item(accessory)  # Add unequipped accessory back to inventory
                MessageDialog(self.window, "Accessory Unequipped", 
                            f"Unequipped {accessory.get('name', 'accessory')}").show()
                self._refresh_inventory()
        else:
            MessageDialog(self.window, "No Accessory", 
                        "No accessory is currently equipped.").show()
    
    def set_callbacks(self, on_use_item: Callable = None, on_equip_item: Callable = None, 
                     on_drop_item: Callable = None):
        """Set callback functions"""
        self.on_use_item = on_use_item
        self.on_equip_item = on_equip_item
        self.on_drop_item = on_drop_item
    
    def close(self):
        """Close the inventory window"""
        self.window.destroy()
