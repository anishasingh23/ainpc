# server/models.py
from pydantic import BaseModel
from typing import List, Optional

class BattleAction(BaseModel):
    turn: int
    actor: str
    action: str
    target: Optional[str] = None
    damage: Optional[int] = None
    status_applied: Optional[str] = None
    actor_hp: Optional[int] = None
    target_hp: Optional[int] = None

class BattleRequest(BaseModel):
    npc_a: str
    npc_b: str
    level: Optional[int] = 50
    seed: Optional[int] = None
    max_turns: Optional[int] = 200

class BattleResponse(BaseModel):
    winner: str
    turns: int
    log: List[str]
    actions: List[BattleAction]
