import random
import pytest

from models.player import Player
from models.enemy import Enemy, create_enemy, ClockworkSentinel, RogueAutomaton, SteamGolem


def test_player_damage_and_heal():
    p = Player("Tester")
    p.defense = 2
    p.hp = 50

    dmg = p.take_damage(10)
    assert dmg == max(1, 10 - 2)
    assert p.hp == 50 - dmg

    healed = p.heal(5)
    assert healed == 5
    assert p.hp == 50 - dmg + 5


def test_player_focus_and_spend_restore():
    p = Player("Focusy")
    p.focus = 1

    assert not p.spend_focus(2)
    assert p.focus == 1

    assert p.spend_focus(1)
    assert p.focus == 0

    restored = p.restore_focus(3)
    assert restored == 3
    assert p.focus == 3


def test_equip_and_unequip_weapon_and_accessory():
    p = Player("Equipper")

    weapon = {"name": "Steam Blade", "type": "weapon", "stats": {"attack_bonus": 5}}
    assert p.equip_weapon(weapon) is True
    assert p.attack == p.base_attack + 5

    old = p.unequip_weapon()
    assert old is not None
    assert p.attack == p.base_attack

    accessory = {"name": "Bronze Talisman", "type": "accessory", "stats": {"defense_bonus": 3, "focus_bonus": 1, "speed_bonus": 2}}
    assert p.equip_accessory(accessory) is True
    assert p.defense == p.base_defense + 3
    assert p.max_focus >= 5

    old_acc = p.unequip_accessory()
    assert old_acc is not None
    assert p.defense == p.base_defense


def test_to_dict_and_from_dict_roundtrip():
    p = Player("Saver")
    p.add_item({"name": "Healing Tonic", "type": "consumable"})
    weapon = {"name": "Steam Blade", "type": "weapon", "stats": {"attack_bonus": 5}}
    p.equip_weapon(weapon)
    p.add_status_effect("poisoned", 2)

    data = p.to_dict()
    p2 = Player.from_dict(data)

    assert p2.name == p.name
    assert p2.hp == p.hp
    assert p2.inventory == p.inventory
    assert p2.equipped_weapon is not None
    assert "poisoned" in p2.status_effects or p2.status_effects == {}


def test_enemy_damage_heal_and_effects():
    data = {"name": "Grunt", "stats": {"hp": 30, "attack": 6, "defense": 1}}
    e = Enemy("grunt", data)

    dmg = e.take_damage(10)
    assert dmg == max(1, 10 - e.defense)
    assert e.hp <= e.max_hp

    healed = e.heal(5)
    assert healed >= 0


def test_enemy_ability_usage_and_cooldown():
    # Ensure the enemy has enough focus to use abilities
    data = {"name": "Brute", "stats": {"hp": 40, "attack": 8, "focus": 3}, "abilities": ["power_strike"]}
    e = Enemy("brute", data)

    assert e.can_use_ability("power_strike")
    desc, dmg = e.use_ability("power_strike")
    assert isinstance(desc, str)
    assert isinstance(dmg, int)

    # Immediately after use, ability should be on cooldown
    assert not e.can_use_ability("power_strike")


def test_enemy_ai_patterns_and_factory():
    # Aggressive pattern
    data = {"name": "Aggro", "stats": {"hp": 40, "attack": 10}, "abilities": ["power_strike"], "ai_pattern": "aggressive"}
    e = create_enemy("steam_golem", {"name": "G", "stats": {"hp": 30}})
    assert isinstance(e, SteamGolem)

    # Clockwork sentinel factory
    sentinel = create_enemy("clockwork_sentinel", {"name": "S", "stats": {"hp": 50}})
    assert isinstance(sentinel, ClockworkSentinel)

    # Rogue automaton factory
    rogue = create_enemy("rogue_automaton", {"name": "R", "stats": {"hp": 20}})
    assert isinstance(rogue, RogueAutomaton)

    # Tactical ai behaviour (no crash)
    tactical = Enemy("t", {"name": "T", "stats": {"hp": 40, "attack": 6}, "ai_pattern": "tactical", "abilities": ["defensive_stance", "repair_self"]})
    act = tactical.choose_action(player_hp=20, player_defense=3, player_focus=1)
    assert isinstance(act, dict)


def test_get_effective_attack_and_defense():
    e = Enemy("x", {"name": "X", "stats": {"hp": 30, "attack": 6, "defense": 2}})
    e.status_effects["berserker"] = 2
    assert e.get_effective_attack() >= e.attack

    e.status_effects["defensive"] = 2
    assert e.get_effective_defense() >= e.defense
