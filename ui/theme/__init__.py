"""
Theme initialization and button creation for Chronicles of Aether Gate
"""

from typing import Callable, Optional
from .widgets import SteampunkButton

def create_action_button(
    parent,
    text: str,
    command: Optional[Callable] = None,
    width: int = 150,
    height: int = 40
) -> SteampunkButton:
    """Create a steampunk-styled action button"""
    return SteampunkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height
    )
