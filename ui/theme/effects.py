"""
Visual effects system for Chronicles of Aether Gate
"""

import tkinter as tk
from typing import Optional, List, Tuple
import math
import random
from .theme_engine import theme

class Particle:
    """A single particle for effects"""
    def __init__(
        self,
        x: float,
        y: float,
        velocity_x: float,
        velocity_y: float,
        lifetime: float,
        color: str,
        size: float = 2.0
    ):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
    
    def update(self, dt: float) -> bool:
        """Update particle position and lifetime"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        return self.lifetime > 0

class ParticleSystem:
    """A system for managing particle effects"""
    def __init__(self, parent: tk.Widget):
        """Initialize the particle system"""
        # If parent is a Toplevel window, create a canvas inside it
        if isinstance(parent, tk.Toplevel):
            # Wait for the window to be created
            parent.update_idletasks()
            
            # Create an overlay canvas with system color that will appear transparent
            self.canvas = tk.Canvas(
                parent,
                width=parent.winfo_width(),
                height=parent.winfo_height(),
                highlightthickness=0,
                bg=parent.cget('bg'),  # Match parent's background
            )
            self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            # Use the provided canvas directly
            self.canvas = parent
            
        self._particles: List[Particle] = []
        self._animation_id = None
    
    def emit_burst(self, x: float, y: float, count: int = 10, spread: float = math.pi/2,
                   velocity: float = 5.0, lifetime: float = 1.0, color: str = "#FFD700"):
        """Create a burst of particles at a point"""
        try:
            for _ in range(count):
                angle = random.uniform(-spread/2, spread/2)
                velocity_x = velocity * math.cos(angle)
                velocity_y = velocity * math.sin(angle)
                
                particle = Particle(x, y, velocity_x, velocity_y, lifetime, color)
                particle_id = self.canvas.create_oval(
                    x-2, y-2, x+2, y+2,
                    fill=color,
                    outline=""
                )
                self._particles.append((particle, particle_id))
                
            # Start animation if not already running
            if not self._animation_id:
                self._animate()
        except (tk.TclError, AttributeError):
            # Canvas was destroyed or some other error
            self._cleanup()

    def _animate(self):
        """Animate all particles"""
        try:
            to_remove = []
            
            for particle, particle_id in self._particles:
                if particle.update():
                    self.canvas.coords(
                        particle_id,
                        particle.x-2, particle.y-2,
                        particle.x+2, particle.y+2
                    )
                    
                    # Update opacity (as solid color)
                    opacity = particle.lifetime / particle.max_lifetime
                    r = int(int(particle.color[1:3], 16) * opacity)
                    g = int(int(particle.color[3:5], 16) * opacity)
                    b = int(int(particle.color[5:7], 16) * opacity)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    self.canvas.itemconfig(particle_id, fill=color)
                else:
                    to_remove.append((particle, particle_id))
            
            # Remove dead particles
            for particle, particle_id in to_remove:
                try:
                    self.canvas.delete(particle_id)
                except tk.TclError:
                    pass  # Item already deleted
                self._particles.remove((particle, particle_id))
                
            if self._particles:
                self._animation_id = self.canvas.after(16, self._animate)
            else:
                self._animation_id = None
                
        except tk.TclError:
            # Canvas was destroyed
            self._cleanup()
            
    def _cleanup(self):
        """Clean up animation and particles"""
        if self._animation_id:
            try:
                self.canvas.after_cancel(self._animation_id)
            except tk.TclError:
                pass
        self._animation_id = None
        
        # Clear existing particles
        for _, particle_id in self._particles:
            try:
                self.canvas.delete(particle_id)
            except tk.TclError:
                pass
        self._particles.clear()
    
    def _animate(self):
        """Update all particles"""
        dt = 0.016  # Assume 60fps
        
        try:
            # Update particles
            to_remove = []
            
            for particle, particle_id in self._particles:
                if particle.update(dt):
                    # Update particle display
                    self.canvas.coords(
                        particle_id,
                        particle.x-particle.size,
                        particle.y-particle.size,
                        particle.x+particle.size,
                        particle.y+particle.size
                    )
                    
                    # Update color alpha based on lifetime
                    opacity = particle.lifetime / particle.max_lifetime
                    r = int(int(particle.color[1:3], 16) * opacity)
                    g = int(int(particle.color[3:5], 16) * opacity)
                    b = int(int(particle.color[5:7], 16) * opacity)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.canvas.itemconfig(particle_id, fill=color)
                else:
                    to_remove.append((particle, particle_id))
            
            # Remove dead particles
            for particle, particle_id in to_remove:
                try:
                    self.canvas.delete(particle_id)
                except tk.TclError:
                    pass  # Item already deleted
                self._particles.remove((particle, particle_id))
                
            if self._particles:
                self._animation_id = self.canvas.after(16, self._animate)
            else:
                self._animation_id = None
                
        except tk.TclError:
            # Canvas was destroyed
            self._cleanup()

class CombatEffects:
    """Visual effects system for combat"""
    def __init__(self, canvas: tk.Canvas):
        """Initialize with a canvas"""
        self.particle_system = ParticleSystem(canvas)
    
    def attack_effect(self, x: float, y: float):
        """Create an attack effect"""
        # Impact particles
        self.particle_system.emit_burst(
            x, y,
            count=15,
            spread=math.pi/3,
            velocity=8,
            lifetime=0.5,
            color=theme.GLOW_COLORS['energy'][0]
        )

    def heal_effect(self, x: float, y: float):
        """Create a healing effect"""
        # Healing particles
        self.particle_system.emit_burst(
            x, y,
            count=20,
            spread=2*math.pi,
            velocity=3,
            lifetime=1.5,
            color=theme.GLOW_COLORS['heal'][0]
        )

    def ability_effect(self, x: float, y: float):
        """Create an ability effect"""
        # Ability particles
        self.particle_system.emit_burst(
            x, y,
            count=25,
            spread=2*math.pi,
            velocity=6,
            lifetime=1.0,
            color=theme.GLOW_COLORS['aether'][0]
        )
