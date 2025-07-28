from typing import Dict
from game_context.game_context import GameContext
from game_context.roles import Role


class NightActionResult:
    """Result of a night action"""
    def __init__(self, success: bool, message: str, data: Dict = None):
        self.success = success
        self.message = message
        self.data = data or {}


def validate_player_exists(game_context: GameContext, player_id: int, error_message: str = None) -> tuple[bool, str]:
    """
    Validate that a player exists in the game context
    
    Args:
        game_context: Current game state
        player_id: ID of the player to validate
        error_message: Custom error message (optional)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    player = game_context.get_player(player_id)
    if not player:
        message = error_message or f"Player {player_id} not found!"
        return False, message
    return True, ""


def validate_different_players(player1_id: int, player2_id: int, error_message: str = None) -> tuple[bool, str]:
    """
    Validate that two player IDs are different
    
    Args:
        player1_id: First player ID
        player2_id: Second player ID
        error_message: Custom error message (optional)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if player1_id == player2_id:
        message = error_message or "You must select two different players!"
        return False, message
    return True, ""


def validate_center_position(position: int) -> tuple[bool, str]:
    """
    Validate center card position
    
    Args:
        position: Center card position to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not 0 <= position <= 2:
        return False, "Center position must be 0, 1, or 2!"
    return True, ""