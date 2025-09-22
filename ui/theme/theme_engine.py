"""
Theme engine for Chronicles of Aether Gate
Manages custom styling and visual effects
"""

class AethergateTheme:
    """Main theme class that manages colors, fonts, and visual effects"""
    
    # Theme Colors
    COLORS = {
        'primary': '#B87333',     # Bronze
        'secondary': '#CFB53B',   # Aged Gold
        'accent': '#4DEEEA',      # Aether Blue
        'background': '#2C3539',  # Dark Steel
        'text': '#E8E5E1',       # Steam White
        'disabled': '#666666',    # Disabled Gray
        'error': '#FF4444',      # Error Red
        'success': '#44FF44',    # Success Green
    }
    
    # Glow Colors
    GLOW_COLORS = {
        'aether': ('#4DEEEA', '#2C7A78'),  # Aether (normal, dark)
        'energy': ('#FFD700', '#B8860B'),  # Energy (normal, dark)
        'steam': ('#FFFFFF', '#AAAAAA'),   # Steam (normal, dark)
        'heal': ('#44FF44', '#228822'),    # Heal (normal, dark)
    }
    
    # Font Configurations
    FONTS = {
        'title': ('Constantia', 24, 'bold'),
        'subtitle': ('Constantia', 18, 'bold'),
        'heading': ('Constantia', 14, 'bold'),
        'body': ('Helvetica', 12, 'normal'),
        'small': ('Helvetica', 10, 'normal'),
    }
    
    # Widget Styles
    STYLES = {
        'button': {
            'padding': (20, 10),
            'cornerRadius': 10,
            'borderWidth': 2,
        },
        'frame': {
            'borderWidth': 2,
            'padding': 10,
            'relief': 'ridge',
        },
        'entry': {
            'padding': 5,
            'borderWidth': 1,
        }
    }
    
    @classmethod
    def get_color(cls, name: str) -> str:
        """Get a color by name"""
        return cls.COLORS.get(name, cls.COLORS['primary'])
    
    @classmethod
    def get_font(cls, style: str) -> tuple:
        """Get a font configuration by style"""
        return cls.FONTS.get(style, cls.FONTS['body'])
    
    @classmethod
    def get_style(cls, widget: str) -> dict:
        """Get style configuration for a widget type"""
        return cls.STYLES.get(widget, {})
    
    @classmethod
    def get_glow(cls, type_: str) -> tuple:
        """Get glow colors for effects"""
        return cls.GLOW_COLORS.get(type_, cls.GLOW_COLORS['aether'])

# Global theme instance
theme = AethergateTheme()
