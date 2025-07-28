from agents import Agent, Runner
from dotenv import load_dotenv
import os
from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult, validate_player_exists, validate_different_players

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# TROUBLEMAKER NIGHT ACTION TOOLS
def troublemaker_swap(game_context: GameContext, troublemaker_player_id: int, player1_id: int, player2_id: int) -> NightActionResult:
    """
    Troublemaker swaps two other players' cards (without looking)
    
    Args:
        game_context: Current game state
        troublemaker_player_id: ID of the troublemaker
        player1_id: First player to swap
        player2_id: Second player to swap
    
    Returns:
        NightActionResult with swap confirmation
    """
    if player1_id == troublemaker_player_id or player2_id == troublemaker_player_id:
        return NightActionResult(False, "You cannot include yourself in the swap!")
    
    is_valid, error_msg = validate_different_players(player1_id, player2_id)
    if not is_valid:
        return NightActionResult(False, error_msg)
    
    # Validate both players exist
    for player_id in [player1_id, player2_id]:
        is_valid, error_msg = validate_player_exists(game_context, player_id)
        if not is_valid:
            return NightActionResult(False, error_msg)
    
    player1 = game_context.get_player(player1_id)
    player2 = game_context.get_player(player2_id)
    
    # Get original roles (for our own knowledge, but Troublemaker doesn't see them)
    player1_original_role = game_context.get_player_current_role(player1_id)
    player2_original_role = game_context.get_player_current_role(player2_id)
    
    # Perform the actual swap
    success = game_context.swap_player_roles(player1_id, player2_id)
    if not success:
        return NightActionResult(False, "Failed to swap cards!")
    
    return NightActionResult(
        True,
        f"You swapped {player1.player_name}'s and {player2.player_name}'s cards",
        {
            "swapped_players": [player1_id, player2_id],
            "player1_name": player1.player_name,
            "player2_name": player2.player_name,
            # These are for game state tracking, but Troublemaker doesn't know them
            "player1_had": player1_original_role.value if player1_original_role else "unknown",
            "player2_had": player2_original_role.value if player2_original_role else "unknown"
        }
    )


troublemaker = Agent(
    name="troublemaker",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Troublemaker!

    During the night, you swapped the cards of two other players (without looking at them). Those players now have each other's original roles, but they don't know about the swap.

    [NIGHT ACTION RESULT PLACEHOLDER - to be filled with actual swap details]

    Your strategy should be to:
    1. Reveal your swap information strategically
    2. Help create confusion that benefits the village
    3. Watch for reactions when you reveal the swap
    4. Help identify werewolves based on how players react

    You are on the villager team and want to eliminate werewolves.

    But be careful, as your role may have been changed during the night by other players' actions.

    It is now morning -- time to reveal the chaos you've created!
    """,
    model="gpt-4o-mini",
) 