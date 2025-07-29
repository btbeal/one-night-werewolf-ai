from pydantic import BaseModel, Field
from typing import Optional


class GameState(BaseModel):
    """Current state of the game"""
    current_round: int = 1
    players_ready_to_vote: int = 0
    is_game_over: bool = False


class PlayerState(BaseModel):
    """State of an individual player"""
    player_id: int
    player_name: str
    initial_role: str
    character_being_claimed: Optional[str] = None
    ready_to_vote: bool = False
    is_ai: bool = False
    vote_target: Optional[int] = None