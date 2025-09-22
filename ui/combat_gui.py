"""
Combat GUI for Chronicles of Aether Gate
Provides the interface for turn-based combat with steampunk styling
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Dict, Any

from ui.dialog import MessageDialog
from ui.theme.theme_engine import theme
from ui.theme.widgets import SteampunkButton, SteampunkFrame
from ui.theme.additional_widgets import SteampunkProgressBar, SteampunkLabel
from ui.theme.effects import CombatEffects

class CombatGUI:
    """Combat interface window with steampunk aesthetics"""
    
    def __init__(self, parent):
        """Initialize combat GUI"""
        self.window = tk.Toplevel(parent)
        self.window.title("Combat - Chronicles of Aether Gate")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        self.window.minsize(1000, 650)  # Minimum size to ensure content is visible
        self.window.configure(bg=theme.get_color('background'))
        
        # Make window modal and position it
        self.window.transient(parent)
        try:
            self.window.grab_set()
        except tk.TclError:
            # Skip grab_set in headless/testing environment
            pass
        
        # Center window on parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        window_width = 900
        window_height = 600
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
        
        # Handle window close button
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        # Callbacks for combat actions
        self.on_attack = None
        self.on_ability = None
        self.on_item = None
        self.on_flee = None
        
        # Store player inventory for item selection
        self.player_inventory = []
        
        # Initialize effects system
        self.effects = CombatEffects(self.window)
        
        self._setup_gui()
    
    def set_callbacks(self, on_attack: Callable = None, on_ability: Callable = None, 
                     on_item: Callable = None, on_flee: Callable = None):
        """Set callback functions for combat actions"""
        self.on_attack = on_attack
        self.on_ability = on_ability
        self.on_item = on_item
        self.on_flee = on_flee
    
    def _setup_gui(self):
        """Set up the combat interface with steampunk styling"""
        # Main container with metallic frame
        main_frame = SteampunkFrame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title with glowing effect
        title_label = SteampunkLabel(
            main_frame,
            text="⚔️ COMBAT ⚔️",
            font_style='title'
        )
        title_label.pack(pady=(0, 10))
        
        # Combat status frame (player and enemy stats)
        status_frame = SteampunkFrame(main_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        # Player status (left side)
        player_frame = SteampunkFrame(status_frame, title="🛡️ Player")
        player_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.player_name_label = SteampunkLabel(
            player_frame,
            text="Aether Warden",
            font_style='heading'
        )
        self.player_name_label.pack()
        
        # Player HP bar with metallic effect
        self.player_hp_frame = tk.Frame(player_frame, bg=theme.get_color('background'))
        self.player_hp_frame.pack(fill='x', pady=5)
        
        SteampunkLabel(self.player_hp_frame, text="HP:").pack(side='left')
        self.player_hp_bar = SteampunkProgressBar(
            self.player_hp_frame,
            width=200,
            style='primary'
        )
        self.player_hp_bar.pack(side='left', padx=(5, 0))
        self.player_hp_label = SteampunkLabel(self.player_hp_frame, text="100/100")
        self.player_hp_label.pack(side='right')
        
        # Player Focus bar with aether glow
        self.player_focus_frame = tk.Frame(player_frame, bg=theme.get_color('background'))
        self.player_focus_frame.pack(fill='x', pady=5)
        
        SteampunkLabel(self.player_focus_frame, text="Focus:").pack(side='left')
        self.player_focus_bar = SteampunkProgressBar(
            self.player_focus_frame,
            width=200,
            style='accent'
        )
        self.player_focus_bar.pack(side='left', padx=(5, 0))
        self.player_focus_label = SteampunkLabel(self.player_focus_frame, text="5/5")
        self.player_focus_label.pack(side='right')
        
        # Player stats with metallic styling
        self.player_stats_label = SteampunkLabel(
            player_frame,
            text="ATK: 10 | DEF: 5 | SPD: 6"
        )
        self.player_stats_label.pack(pady=5)
        
        # Player status effects with glowing indicators
        self.player_status_label = SteampunkLabel(
            player_frame,
            text="Status: None",
            font_style='small'
        )
        self.player_status_label.pack(pady=5)
        
        # Enemy status (right side)
        enemy_frame = SteampunkFrame(status_frame, title="👹 Enemy")
        enemy_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.enemy_name_label = SteampunkLabel(
            enemy_frame,
            text="Unknown Enemy",
            font_style='heading'
        )
        self.enemy_name_label.pack()
        
        # Enemy HP bar with danger glow
        self.enemy_hp_frame = tk.Frame(enemy_frame, bg=theme.get_color('background'))
        self.enemy_hp_frame.pack(fill='x', pady=5)
        
        SteampunkLabel(self.enemy_hp_frame, text="HP:").pack(side='left')
        self.enemy_hp_bar = SteampunkProgressBar(
            self.enemy_hp_frame,
            width=200,
            style='error'
        )
        self.enemy_hp_bar.pack(side='left', padx=(5, 0))
        self.enemy_hp_label = SteampunkLabel(self.enemy_hp_frame, text="50/50")
        self.enemy_hp_label.pack(side='right')
        
        # Enemy stats
        self.enemy_stats_label = SteampunkLabel(
            enemy_frame,
            text="ATK: ? | DEF: ? | SPD: ?"
        )
        self.enemy_stats_label.pack(pady=5)
        
        # Combat log with scrolling parchment effect
        log_frame = SteampunkFrame(main_frame, title="📜 Combat Log")
        log_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        log_scroll_frame = tk.Frame(log_frame, bg=theme.get_color('background'))
        log_scroll_frame.pack(fill='both', expand=True)
        
        self.log_scrollbar = tk.Scrollbar(log_scroll_frame)
        self.log_scrollbar.pack(side='right', fill='y')
        
        self.combat_log = tk.Text(
            log_scroll_frame,
            height=10,
            yscrollcommand=self.log_scrollbar.set,
            bg=theme.get_color('background'),
            fg=theme.get_color('text'),
            font=theme.get_font('body'),
            relief='sunken',
            borderwidth=1
        )
        self.combat_log.pack(side='left', fill='both', expand=True)
        self.log_scrollbar.config(command=self.combat_log.yview)
        self.combat_log.config(state='disabled')
        
        # Action buttons with steampunk styling
        actions_frame = SteampunkFrame(main_frame, title="⚡ Actions")
        actions_frame.pack(fill='x', pady=(0, 10))
        
        # Action buttons with gear decorations
        button_frame = tk.Frame(actions_frame, bg=theme.get_color('background'))
        button_frame.pack(fill='x')
        
        self.attack_button = SteampunkButton(
            button_frame,
            text="⚔️ Attack",
            command=self._on_attack_clicked,
            width=150
        )
        self.attack_button.pack(side='left', padx=5)
        
        self.abilities_button = SteampunkButton(
            button_frame,
            text="🔥 Abilities",
            command=self._on_abilities_clicked,
            width=150
        )
        self.abilities_button.pack(side='left', padx=5)
        
        self.items_button = SteampunkButton(
            button_frame,
            text="🧪 Items",
            command=self._on_items_clicked,
            width=150
        )
        self.items_button.pack(side='left', padx=5)
        
        self.flee_button = SteampunkButton(
            button_frame,
            text="🏃 Flee",
            command=self._on_flee_clicked,
            width=150
        )
        self.flee_button.pack(side='left', padx=5)
        
        # Turn indicator with glowing effect
        self.turn_frame = tk.Frame(actions_frame, bg=theme.get_color('background'))
        self.turn_frame.pack(fill='x', pady=(10, 0))
        
        self.turn_label = SteampunkLabel(
            self.turn_frame,
            text="🎯 Your Turn",
            font_style='subtitle'
        )
        self.turn_label.pack()
    
    def _get_enemy_position(self):
        """Get the center position of the enemy frame for effects"""
        enemy_x = self.enemy_hp_frame.winfo_x() + self.enemy_hp_frame.winfo_width() // 2
        enemy_y = self.enemy_hp_frame.winfo_y() + self.enemy_hp_frame.winfo_height() // 2
        return enemy_x, enemy_y
    
    def _on_attack_clicked(self):
        """Handle attack button click with effect"""
        if self.on_attack:
            x, y = self._get_enemy_position()
            self.effects.attack_effect(x, y)
            self.on_attack()
    
    def _on_abilities_clicked(self):
        """Handle abilities button click with effects"""
        abilities = ["power_strike", "defensive_stance", "aether_blast", "heal"]
        ability = self._show_selection_dialog("Select Ability", abilities)
        if ability and self.on_ability:
            x, y = self._get_enemy_position()
            if ability == "heal":
                self.effects.heal_effect(x, y)
            else:
                self.effects.ability_effect(x, y)
            self.on_ability(ability)
    
    def _on_items_clicked(self):
        """Handle items button click with effects"""
        items = []
        for item in self.player_inventory:
            if item.get("type") == "consumable":
                items.append(item.get("name"))
        
        if not items:
            dialog = MessageDialog(self.window, "No Items", "You have no usable items!")
            dialog.show()
            return
        
        def get_item_description(item_name):
            for item in self.player_inventory:
                if item.get("name") == item_name:
                    return f"{item.get('description', 'No description')} [{item.get('count', 1)}x]"
            return "No description available"
        
        selected_item = self._show_selection_dialog_with_description(
            "Select Item",
            items,
            get_item_description
        )
        
        if selected_item and self.on_item:
            x, y = self._get_enemy_position()
            if "heal" in selected_item.lower() or "potion" in selected_item.lower():
                self.effects.heal_effect(x, y)
            self.on_item(selected_item)
    
    def _on_flee_clicked(self):
        """Handle flee button click"""
        from ui.dialog import ConfirmDialog
        dialog = ConfirmDialog(self.window, "Flee Combat", "Are you sure you want to flee?")
        if dialog.show():
            if self.on_flee:
                self.on_flee()
    
    def _show_selection_dialog(self, title: str, options: list) -> str:
        """Show a steampunk-styled selection dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        # Calculate appropriate height based on number of options
        min_height = 250
        height = max(min_height, 150 + len(options) * 35)
        dialog.geometry(f"350x{height}")
        dialog.transient(self.window)
        try:
            dialog.grab_set()
        except tk.TclError:
            # Skip grab_set in headless/testing environment
            pass
        dialog.configure(bg=theme.get_color('background'))
        
        # Center the dialog on parent window
        self._center_dialog_on_parent(dialog)
        
        selected_value = tk.StringVar()
        
        SteampunkLabel(
            dialog,
            text=f"Choose {title.lower()}:",
            font_style='heading'
        ).pack(pady=10)
        
        for option in options:
            tk.Radiobutton(
                dialog,
                text=option.replace("_", " ").title(),
                variable=selected_value,
                value=option,
                bg=theme.get_color('background'),
                fg=theme.get_color('text'),
                selectcolor=theme.get_color('accent'),
                activebackground=theme.get_color('background'),
                activeforeground=theme.get_color('accent'),
                font=theme.get_font('body')
            ).pack(anchor='w', pady=2)
        
        button_frame = tk.Frame(dialog, bg=theme.get_color('background'))
        button_frame.pack(pady=20)
        
        def on_ok():
            dialog.destroy()
        
        def on_cancel():
            selected_value.set("")
            dialog.destroy()
        
        SteampunkButton(
            button_frame,
            text="OK",
            command=on_ok,
            width=100
        ).pack(side='left', padx=5)
        
        SteampunkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=100
        ).pack(side='left', padx=5)
        
        dialog.wait_window()
        return selected_value.get()
    
    def _show_selection_dialog_with_description(self, title: str, options: list, get_description) -> str:
        """Show a steampunk-styled selection dialog with descriptions"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        # Calculate appropriate height based on number of options
        min_height = 350
        height = max(min_height, 200 + len(options) * 35)
        dialog.geometry(f"500x{height}")
        dialog.transient(self.window)
        try:
            dialog.grab_set()
        except tk.TclError:
            # Skip grab_set in headless/testing environment
            pass
        dialog.configure(bg=theme.get_color('background'))
        
        # Center the dialog on parent window
        self._center_dialog_on_parent(dialog)
        
        selected_value = tk.StringVar()
        description_var = tk.StringVar()
        
        SteampunkLabel(
            dialog,
            text=f"Choose {title.lower()}:",
            font_style='heading'
        ).pack(pady=10)
        
        content_frame = SteampunkFrame(dialog)
        content_frame.pack(fill='both', expand=True, padx=10)
        
        options_frame = SteampunkFrame(content_frame)
        options_frame.pack(side='left', fill='both', expand=True)
        
        desc_frame = SteampunkFrame(content_frame, title="Description")
        desc_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        desc_label = SteampunkLabel(
            desc_frame,
            textvariable=description_var,
            wraplength=200
        )
        desc_label.pack(pady=5, padx=5)
        
        def on_select():
            item = selected_value.get()
            if item:
                description_var.set(get_description(item))
        
        for option in options:
            tk.Radiobutton(
                options_frame,
                text=option.replace("_", " ").title(),
                variable=selected_value,
                value=option,
                command=on_select,
                bg=theme.get_color('background'),
                fg=theme.get_color('text'),
                selectcolor=theme.get_color('accent'),
                activebackground=theme.get_color('background'),
                activeforeground=theme.get_color('accent'),
                font=theme.get_font('body')
            ).pack(anchor='w', pady=2)
        
        button_frame = tk.Frame(dialog, bg=theme.get_color('background'))
        button_frame.pack(pady=20)
        
        def on_ok():
            dialog.destroy()
        
        def on_cancel():
            selected_value.set("")
            dialog.destroy()
        
        SteampunkButton(
            button_frame,
            text="OK",
            command=on_ok,
            width=100
        ).pack(side='left', padx=5)
        
        SteampunkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=100
        ).pack(side='left', padx=5)
        
        dialog.wait_window()
        return selected_value.get()
    
    def update_combat_state(self, combat_state: Dict[str, Any], player_stats: Dict[str, Any], enemy_stats: Dict[str, Any]):
        """Update the display with current combat state"""
        # Store player inventory
        self.player_inventory = player_stats.get("inventory", [])
        
        # Update player display
        self.player_name_label.configure(text=player_stats["name"])
        
        # Player HP bar
        player_hp_percent = (player_stats["hp"] / player_stats["max_hp"]) * 100
        self.player_hp_bar.set(player_hp_percent)
        self.player_hp_label.configure(text=f"{player_stats['hp']}/{player_stats['max_hp']}")
        
        # Player Focus bar
        player_focus_percent = (player_stats["focus"] / player_stats["max_focus"]) * 100
        self.player_focus_bar.set(player_focus_percent)
        self.player_focus_label.configure(text=f"{player_stats['focus']}/{player_stats['max_focus']}")
        
        # Player stats
        self.player_stats_label.configure(
            text=f"ATK: {player_stats['attack']} | DEF: {player_stats['defense']} | SPD: {player_stats['speed']}"
        )
        
        # Status effects
        if player_stats.get("status_effects"):
            effects = [f"{effect} ({turns})" for effect, turns in player_stats["status_effects"].items()]
            status_text = "Status: " + ", ".join(effects)
        else:
            status_text = "Status: None"
        self.player_status_label.configure(text=status_text)
        
        # Update enemy display
        self.enemy_name_label.configure(text=enemy_stats["name"])
        
        # Enemy HP bar
        enemy_hp_percent = (enemy_stats["hp"] / enemy_stats["max_hp"]) * 100
        self.enemy_hp_bar.set(enemy_hp_percent)
        self.enemy_hp_label.configure(text=f"{enemy_stats['hp']}/{enemy_stats['max_hp']}")
        
        # Enemy stats
        self.enemy_stats_label.configure(
            text=f"ATK: {enemy_stats['attack']} | DEF: {enemy_stats['defense']} | SPD: {enemy_stats['speed']}"
        )
        
        # Update turn indicator
        current_turn = combat_state["current_turn"]
        if current_turn == "player":
            self.turn_label.configure(text="🎯 Your Turn")
            self._enable_action_buttons(True)
        elif current_turn == "enemy":
            self.turn_label.configure(text="👹 Enemy Turn")
            self._enable_action_buttons(False)
        else:
            self.turn_label.configure(text="Combat Over")
            self._enable_action_buttons(False)
    
    def _enable_action_buttons(self, enabled: bool):
        """Enable or disable action buttons with visual feedback"""
        state = "normal" if enabled else "disabled"
        for button in [self.attack_button, self.abilities_button, self.items_button]:
            button.configure(state=state)
            if state == "disabled":
                button.configure(bg=theme.get_color('disabled'))
            else:
                button.configure(bg=theme.get_color('primary'))
        
        # Flee always available
        self.flee_button.configure(state="normal")
        self.flee_button.configure(bg=theme.get_color('primary'))
    
    def add_log_message(self, message: str):
        """Add a message to the combat log with styling"""
        self.combat_log.configure(state='normal')
        self.combat_log.insert(tk.END, message + "\n")
        self.combat_log.configure(state='disabled')
        self.combat_log.see(tk.END)
    
    def clear_log(self):
        """Clear the combat log"""
        self.combat_log.configure(state='normal')
        self.combat_log.delete('1.0', tk.END)
        self.combat_log.configure(state='disabled')
    
    def show_combat_result(self, title: str, message: str):
        """Show combat result in a themed dialog"""
        dialog = MessageDialog(self.window, title, message)
        dialog.show()
    
    def _center_dialog_on_parent(self, dialog):
        """Center a dialog window on its parent window"""
        try:
            dialog.update_idletasks()
            parent = self.window
            
            # Get parent window dimensions and position
            pw, ph = parent.winfo_width(), parent.winfo_height()
            px, py = parent.winfo_x(), parent.winfo_y()
            
            # Get dialog dimensions
            w = dialog.winfo_width() or dialog.winfo_reqwidth()
            h = dialog.winfo_height() or dialog.winfo_reqheight()
            if w <= 1:
                w = dialog.winfo_reqwidth()
            if h <= 1:
                h = dialog.winfo_reqheight()
            
            # Calculate centered position
            x = px + max((pw - w) // 2, 0)
            y = py + max((ph - h) // 2, 0)
            
            # Set the position
            dialog.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            # Safe fallback position
            dialog.geometry("+200+200")
    
    def close(self):
        """Close the combat window"""
        self.window.destroy()
