# server/battle_engine.py
import os
import json
import random
from dataclasses import dataclass
from typing import Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NPCS_PATH = os.path.join(DATA_DIR, "npcs.json")
MOVES_PATH = os.path.join(DATA_DIR, "moves.json")

with open(NPCS_PATH, "r", encoding="utf-8") as f:
    NPCS = json.load(f)

with open(MOVES_PATH, "r", encoding="utf-8") as f:
    MOVES = json.load(f)

@dataclass
class Status:
    name: str = "Healthy"
    turns: int = 0

@dataclass
class Combatant:
    key: str
    name: str
    level: int
    max_hp: int
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    status: Status

def build_combatant(key: str, level: int = 50) -> Combatant:
    p = NPCS[key.lower()]
    # basic level scaling
    hp = int(p["hp"] * (1 + (level - p.get("level", 50)) / 100)) + 10
    attack = int(p["attack"] * (1 + (level - p.get("level",50)) / 100))
    defense = int(p["defense"] * (1 + (level - p.get("level",50)) / 100))
    sp_attack = int(p["sp_attack"] * (1 + (level - p.get("level",50)) / 100))
    sp_defense = int(p["sp_defense"] * (1 + (level - p.get("level",50)) / 100))
    speed = int(p["speed"] * (1 + (level - p.get("level",50)) / 100))
    return Combatant(
        key=key.lower(),
        name=p["name"],
        level=level,
        max_hp=hp,
        hp=hp,
        attack=attack,
        defense=defense,
        sp_attack=sp_attack,
        sp_defense=sp_defense,
        speed=speed,
        status=Status()
    )

def choose_move_auto(combatant: Combatant) -> str:
    # choose highest power damaging move by default
    moves = NPCS[combatant.key]["moves"]
    best = moves[0]
    best_power = -1
    for m in moves:
        info = MOVES.get(m, {})
        power = info.get("power", 0)
        if info.get("category") in ("Physical", "Special") and power > best_power:
            best_power = power
            best = m
    return best

def apply_status_effects(combatant: Combatant, log: List[str]):
    if combatant.status.name == "Burn":
        dmg = max(1, combatant.max_hp // 16)
        combatant.hp = max(0, combatant.hp - dmg)
        log.append(f"{combatant.name} takes {dmg} burn damage (HP: {combatant.hp}/{combatant.max_hp}).")
    elif combatant.status.name == "Poison":
        dmg = max(1, combatant.max_hp // 12)
        combatant.hp = max(0, combatant.hp - dmg)
        log.append(f"{combatant.name} takes {dmg} poison damage (HP: {combatant.hp}/{combatant.max_hp}).")
    elif combatant.status.name == "Stunned":
        # stun duration handled elsewhere
        pass

def calc_damage(attacker: Combatant, defender: Combatant, move_name: str) -> int:
    move = MOVES.get(move_name, {})
    if not move or move.get("category") == "Status" or move.get("power", 0) == 0:
        return 0
    atk_stat = attacker.sp_attack if move.get("category") == "Special" else attacker.attack
    def_stat = defender.sp_defense if move.get("category") == "Special" else defender.defense
    base = (((2 * attacker.level) / 5) + 2) * move.get("power", 1) * atk_stat / max(1, def_stat) / 50 + 2
    rand = random.uniform(0.85, 1.0)
    damage = int(base * rand)
    return max(1, damage)

def simulate_battle(npc_a: str, npc_b: str, level: int = 50, seed: int = None, max_turns: int = 200) -> Dict:
    if seed is not None:
        random.seed(seed)
    a = build_combatant(npc_a, level)
    b = build_combatant(npc_b, level)

    log: List[str] = []
    actions: List[Dict] = []
    log.append(f"Battle start: {a.name} (HP {a.hp}) vs {b.name} (HP {b.hp}), Level {level}")
    turn = 1

    while a.hp > 0 and b.hp > 0 and turn <= max_turns:
        log.append(f"--- Turn {turn} ---")
        # apply ongoing status effects first
        apply_status_effects(a, log); apply_status_effects(b, log)
        # determine order by speed (stun halves speed as example)
        a_speed = a.speed * (0.5 if a.status.name == "Stunned" else 1.0)
        b_speed = b.speed * (0.5 if b.status.name == "Stunned" else 1.0)
        order = [(a, b)] if a_speed >= b_speed else [(b, a)]
        if a_speed == b_speed:
            order = [(a, b), (b, a)]
        for attacker, defender in order:
            if attacker.hp <= 0 or defender.hp <= 0:
                continue
            # if stunned, skip action and reduce stun turns
            if attacker.status.name == "Stunned" and attacker.status.turns > 0:
                log.append(f"{attacker.name} is stunned and cannot act this turn.")
                attacker.status.turns -= 1
                if attacker.status.turns == 0:
                    attacker.status.name = "Healthy"
                actions.append({
                    "turn": turn,
                    "actor": attacker.name,
                    "action": "stunned",
                    "target": None,
                    "damage": 0,
                    "status_applied": "Stunned (skipped)"
                })
                continue
            mv = choose_move_auto(attacker)
            mv_info = MOVES.get(mv, {})
            dmg = calc_damage(attacker, defender, mv)
            defender.hp = max(0, defender.hp - dmg)
            log.append(f"{attacker.name} used {mv}, dealing {dmg} to {defender.name} ({defender.hp}/{defender.max_hp}).")
            status_applied = None
            # try apply status effects from move
            if mv_info.get("burn_chance") and defender.status.name == "Healthy":
                if random.random() < mv_info["burn_chance"]:
                    defender.status.name = "Burn"; defender.status.turns = 3
                    status_applied = "Burn"
                    log.append(f"{defender.name} was burned!")
            if mv_info.get("poison_chance") and defender.status.name == "Healthy":
                if random.random() < mv_info["poison_chance"]:
                    defender.status.name = "Poison"; defender.status.turns = 5
                    status_applied = status_applied or "Poison"
                    log.append(f"{defender.name} was poisoned!")
            if mv_info.get("stun_chance") and defender.status.name == "Healthy":
                if random.random() < mv_info["stun_chance"]:
                    defender.status.name = "Stunned"; defender.status.turns = 1
                    status_applied = status_applied or "Stunned"
                    log.append(f"{defender.name} was stunned!")
            actions.append({
                "turn": turn,
                "actor": attacker.name,
                "action": mv,
                "target": defender.name,
                "damage": dmg,
                "status_applied": status_applied,
                "actor_hp": attacker.hp,
                "target_hp": defender.hp
            })
            if defender.hp <= 0:
                log.append(f"{defender.name} has fallen!")
                break
        turn += 1

    winner = a.name if a.hp > 0 else b.name
    return {
        "winner": winner,
        "turns": turn - 1,
        "log": log,
        "actions": actions
    }
