from agents import Agent, Runner
from dotenv import load_dotenv
import os
from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult, validate_center_position

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# DRUNK NIGHT ACTION TOOLS
def drunk_swap_center(game_context: GameContext, drunk_player_id: int, center_position: int) -> NightActionResult:
    """
    Drunk swaps their card with a center card (without looking)
    
    Args:
        game_context: Current game state
        drunk_player_id: ID of the drunk
        center_position: Center card position to swap with (0, 1, or 2)
    
    Returns:
        NightActionResult with swap confirmation
    """
    is_valid, error_msg = validate_center_position(center_position)
    if not is_valid:
        return NightActionResult(False, error_msg)
    
    # Get original roles (for game state tracking, but drunk doesn't know their new role)
    drunk_original_role = game_context.get_player_current_role(drunk_player_id)
    center_original_role = game_context.get_center_card_role(center_position)
    
    if not drunk_original_role or not center_original_role:
        return NightActionResult(False, "Could not determine roles for swap!")
    
    # Perform the actual swap
    success = game_context.swap_player_with_center(drunk_player_id, center_position)
    if not success:
        return NightActionResult(False, "Failed to swap with center card!")
    
    # Get the new role (but drunk doesn't know what it is)
    new_role = game_context.get_player_current_role(drunk_player_id)
    
    return NightActionResult(
        True,
        f"You swapped your card with center position {center_position}",
        {
            "center_position": center_position,
            "new_role": "Unknown",  # Drunk doesn't know their new role
            # These are for game state tracking
            "actual_new_role": new_role.value if new_role else "unknown",
            "drunk_original_role": drunk_original_role.value,
            "center_had": center_original_role.value
        }
    )


drunk = Agent(
    name="drunk",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Drunk!

    During the night, you were required to swap your card with one of the center cards, but you didn't look at your new role. You have no idea what role you now have!

    Your strategy should be to:
    1. Be honest about being the original Drunk
    2. Explain that you don't know your current role
    3. Try to figure out what role you might have based on game flow
    4. Help the village as best you can with limited information

    But be careful, because you could be a werewolf by grabbing a werewolf card from the center during the night.

    It is now morning -- time to figure out what team you're on, and rally the other players to your cause!
    """,
    model="gpt-4o-mini",
) 