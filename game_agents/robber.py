from agents import Agent, Runner
from dotenv import load_dotenv
import os
from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult, validate_player_exists

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# ROBBER NIGHT ACTION TOOLS
def rob_player_card(game_context: GameContext, robber_player_id: int, target_player_id: int) -> NightActionResult:
    """
    Robber swaps their card with another player and sees their new role
    
    Args:
        game_context: Current game state
        robber_player_id: ID of the robber
        target_player_id: ID of the player to rob from
    
    Returns:
        NightActionResult with swap information and new role
    """
    if target_player_id == robber_player_id:
        return NightActionResult(False, "You cannot rob from yourself!")
    
    is_valid, error_msg = validate_player_exists(game_context, target_player_id)
    if not is_valid:
        return NightActionResult(False, error_msg)
    
    target_player = game_context.get_player(target_player_id)
    
    # Get the roles before swapping
    robber_original_role = game_context.get_player_current_role(robber_player_id)
    target_original_role = game_context.get_player_current_role(target_player_id)
    
    if not robber_original_role or not target_original_role:
        return NightActionResult(False, "Could not determine player roles for swap!")
    
    # Perform the actual swap
    success = game_context.swap_player_roles(robber_player_id, target_player_id)
    if not success:
        return NightActionResult(False, "Failed to swap cards!")
    
    # Get the new role (what the robber now has)
    new_role = game_context.get_player_current_role(robber_player_id)
    
    return NightActionResult(
        True,
        f"You swapped cards with {target_player.player_name} and your new role is {new_role.value.title()}",
        {
            "target_player": target_player_id,
            "new_role": new_role.value,
            "target_now_has": robber_original_role.value,
            "robber_original_role": robber_original_role.value
        }
    )


robber = Agent(
    name="robber",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Robber!

    During the night, you swapped your card with another player and looked at your new role. You now know what role you have become and what role the other player now has.

    [NIGHT ACTION RESULT PLACEHOLDER - to be filled with actual swap details]

    Your strategy depends on your new role:
    - If you're now a villager role: Help find the werewolves
    - If you're now a werewolf: Try to blend in and avoid detection
    - Share information about the swap strategically

    Remember: The player you swapped with now has your original Robber card, but they don't know about the swap.

    It is now morning -- use your knowledge wisely!
    """,
    model="gpt-4o-mini",
) 