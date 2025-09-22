"""
Custom themed widgets for Chronicles of Aether Gate
"""

import tkinter as tk
from typing import Optional, Callable, Any
import math

from .theme_engine import theme

class SteampunkButton(tk.Canvas):
    """Custom steampunk-styled button with glow effects"""
    
    def __init__(
        self, 
        parent: Any,
        text: str,
        command: Optional[Callable] = None,
        width: int = 200,
        height: int = 40,
        style: str = 'primary'
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=theme.get_color('background')
        )
        
        self.text = text
        self.command = command
        self.style = style
        self.width = width
        self.height = height
        
        # State
        self.pressed = False
        self.hover = False
        self._glow_intensity = 0.0
        
        # Animation
        self._animation_id = None
        
        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # Initial draw
        self._draw()
    
    def _draw(self):
        """Draw the button with current state"""
        try:
            self.delete('all')  # Clear canvas
            
            # Get colors based on state
            if self.pressed:
                main_color = theme.get_color('accent')
                glow_color = theme.GLOW_COLORS['aether'][0]
            elif self.hover:
                main_color = theme.get_color('secondary')
                glow_color = theme.GLOW_COLORS['energy'][0]
            else:
                main_color = theme.get_color('primary')
                glow_color = theme.GLOW_COLORS['steam'][0]
        except tk.TclError:
            return  # Widget destroyed
        
        # Draw button background with metallic effect
        self.create_rectangle(
            2, 2, self.width-2, self.height-2,
            fill=main_color,
            outline=theme.get_color('accent'),
            width=2,
            stipple='gray50'
        )
        
        # Add gear decorations
        self._draw_gears()
        
        # Add glow effect
        if self._glow_intensity > 0:
            self._draw_glow(glow_color)
        
        # Draw text
        self.create_text(
            self.width/2,
            self.height/2,
            text=self.text,
            fill=theme.get_color('text'),
            font=theme.get_font('body')
        )
    
    def _draw_gears(self):
        """Draw decorative gears on the button"""
        # Left gear
        self._draw_gear(20, self.height/2, 8, 8)
        # Right gear
        self._draw_gear(self.width-20, self.height/2, 8, 8)
    
    def _draw_gear(self, x: int, y: int, radius: int, teeth: int):
        """Draw a single gear"""
        points = []
        for i in range(teeth * 2):
            angle = i * math.pi / teeth
            r = radius if i % 2 == 0 else radius * 0.7
            points.append(x + r * math.cos(angle))
            points.append(y + r * math.sin(angle))
        
        self.create_polygon(
            points,
            fill=theme.get_color('secondary'),
            outline=theme.get_color('accent'),
            width=1
        )
    
    def _draw_glow(self, glow_color):
        """Draw glow effect"""
        # Split color into RGB components
        rgb = [int(glow_color[1:3], 16), int(glow_color[3:5], 16), int(glow_color[5:7], 16)]
        
        # Apply glow intensity
        alpha = self._glow_intensity
        glow_rgb = [
            min(255, int(c + (255 - c) * alpha))
            for c in rgb
        ]
        
        # Convert back to hex color
        glow_color_hex = f'#{glow_rgb[0]:02x}{glow_rgb[1]:02x}{glow_rgb[2]:02x}'
            
        self.create_rectangle(
            2, 2, self.width-2, self.height-2,
            fill=theme.get_color('accent'),
            outline=glow_color_hex,
            width=2
        )
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.hover = True
        self._start_glow()
        self._draw()
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.hover = False
        self.pressed = False
        self._stop_glow()
        self._draw()
    
    def _on_press(self, event):
        """Handle mouse press"""
        self.pressed = True
        self._glow_intensity = 1.0
        self._draw()
    
    def _on_release(self, event):
        """Handle mouse release"""
        if self.pressed and self.command:
            self.command()
        self.pressed = False
        self._draw()
    
    def _start_glow(self):
        """Start glow animation"""
        if self._animation_id:
            self.after_cancel(self._animation_id)
        self._animate_glow()
    
    def _stop_glow(self):
        """Stop glow animation"""
        if self._animation_id:
            try:
                self.after_cancel(self._animation_id)
            except tk.TclError:
                pass  # Widget already destroyed
        self._glow_intensity = 0.0
        try:
            self._draw()
        except tk.TclError:
            pass  # Widget already destroyed
            
    def destroy(self):
        """Clean up widget"""
        self._stop_glow()
        try:
            super().destroy()
        except tk.TclError:
            pass  # Already destroyed
    
    def _animate_glow(self):
        """Animate the glow effect"""
        if not hasattr(self, '_glow_time'):
            self._glow_time = 0
        self._glow_time += 50  # 50ms per frame
        
        self._glow_intensity = 0.5 + math.sin(self._glow_time / 500) * 0.5
        self._draw()
        self._animation_id = self.after(50, self._animate_glow)

class SteampunkFrame(tk.Frame):
    """Custom steampunk-styled frame with metallic borders"""
    
    def __init__(
        self,
        parent: Any,
        title: Optional[str] = None,
        **kwargs
    ):
        style = theme.get_style('frame')
        super().__init__(
            parent,
            borderwidth=style['borderWidth'],
            relief=style['relief'],
            padx=style['padding'],
            pady=style['padding'],
            bg=theme.get_color('background'),
            **kwargs
        )
        
        if title:
            label = tk.Label(
                self,
                text=title,
                font=theme.get_font('heading'),
                fg=theme.get_color('text'),
                bg=theme.get_color('background')
            )
            label.pack(anchor='nw', pady=(0, 5))
