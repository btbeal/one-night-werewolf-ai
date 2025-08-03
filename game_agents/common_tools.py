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


def resolve_player_name_to_id(game_context: GameContext, target_name: str, requesting_player_id: int) -> tuple[bool, str, int]:
    """
    Resolve a player name to player ID, handling duplicates
    
    Args:
        game_context: Current game state
        target_name: Name of the player to find
        requesting_player_id: ID of the player making the request (excluded from search)
    
    Returns:
        (success, message, player_id)
    """
    # Find all players with matching name (excluding the requesting player)
    matching_players = []
    for player_id, player in game_context.players.items():
        if player_id != requesting_player_id and player.player_name.lower() == target_name.lower():
            matching_players.append((player_id, player))
    
    if not matching_players:
        return False, f"No player found with name '{target_name}'", -1
    
    if len(matching_players) == 1:
        return True, "", matching_players[0][0]
    
    # Multiple players with same name - for now, use first match
    # In a real game, you'd ask for clarification
    player_names = [f"{player.player_name} (ID: {pid})" for pid, player in matching_players]
    return True, f"Multiple players named '{target_name}' found: {', '.join(player_names)}. Using first match.", matching_players[0][0]