"""
Additional custom widgets for Chronicles of Aether Gate
"""

import tkinter as tk
from typing import Optional
from .theme_engine import theme

class SteampunkProgressBar(tk.Canvas):
    """Custom steampunk-styled progress bar"""
    
    def __init__(
        self,
        parent,
        width: int = 200,
        height: int = 20,
        style: str = 'primary'
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=theme.get_color('background')
        )
        
        self.width = width
        self.height = height
        self.style = style
        self._value = 0
        
        # Draw initial state
        self._draw()
    
    def _draw(self):
        """Draw the progress bar"""
        self.delete('all')
        
        # Draw background
        self.create_rectangle(
            0, 0, self.width, self.height,
            fill=theme.get_color('background'),
            outline=theme.get_color('accent'),
            width=1
        )
        
        # Draw progress
        if self._value > 0:
            bar_width = int(self.width * self._value / 100)
            self.create_rectangle(
                2, 2, bar_width-2, self.height-2,
                fill=theme.get_color(self.style),
                stipple='gray25'
            )
            
            # Add metallic effect
            gradient_steps = 5
            for i in range(gradient_steps):
                y = i * self.height / gradient_steps
                self.create_line(
                    2, y, bar_width-2, y,
                    fill=theme.get_color('accent'),
                    stipple='gray50'
                )
    
    def set(self, value: float):
        """Set progress value (0-100)"""
        self._value = max(0, min(100, value))
        self._draw()

class SteampunkLabel(tk.Label):
    """Custom steampunk-styled label"""
    
    def __init__(
        self,
        parent,
        text: str = "",
        font_style: str = 'body',
        **kwargs
    ):
        super().__init__(
            parent,
            text=text,
            font=theme.get_font(font_style),
            fg=theme.get_color('text'),
            bg=theme.get_color('background'),
            **kwargs
        )
