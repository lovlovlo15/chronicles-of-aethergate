"""Smoke test for core game components - ensures basic functionality works"""

import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.player import Player
from models.enemy import Enemy
from engine.combat import CombatEngine


def test_combat_gui_smoke():
    """Smoke test that exercises core combat system"""
    # Create test player and enemy
    player = Player("Test Hero")
    player.max_health = 100
    player.health = 100
    player.attack_power = 15
    player.defense = 5
    
    # Create combat engine with enemy ID
    combat_engine = CombatEngine(player, "steam_golem")
    
    # Test that combat engine is created successfully
    assert combat_engine is not None
    assert combat_engine.player == player
    assert combat_engine.enemy is not None
    
    # Test basic combat operations don't crash
    try:
        # Test player attack
        combat_engine.player_attack()
        
        # Test that combat state is tracked
        assert hasattr(combat_engine, 'combat_log')
        assert len(combat_engine.combat_log) > 0
        
        # Test passed if we got here without exceptions
        assert True
        
    except Exception as e:  
        pytest.fail(f"Combat system smoke test failed: {e}")
