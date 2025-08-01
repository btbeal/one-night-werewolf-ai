from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult, validate_center_position
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

@register_agent(Role.DRUNK)
class DrunkAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
    You are playing a game of One Night Werewolf and have been assigned the role of the Drunk! Your name is {self.player_name}.

    During the night, you were required to swap your card with one of the center cards, but you didn't look at your new role. You have no idea what role you now have!

    Your strategy should be to:
    1. Be honest about being the original Drunk
    2. Explain that you don't know your current role
    3. Try to figure out what role you might have based on game flow
    4. Help the village as best you can with limited information

    But be careful, because you could be a werewolf by grabbing a werewolf card from the center during the night.

    It is now morning -- time to figure out what team you're on, and rally the other players to your cause!
    """
        )

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

    drunk_original_role = game_context.get_player_current_role(drunk_player_id)
    center_original_role = game_context.get_center_card_role(center_position)
    
    if not drunk_original_role or not center_original_role:
        return NightActionResult(False, "Could not determine roles for swap!")

    success = game_context.swap_player_with_center(drunk_player_id, center_position)
    if not success:
        return NightActionResult(False, "Failed to swap with center card!")
    
    new_role = game_context.get_player_current_role(drunk_player_id)
    
    return NightActionResult(
        True,
        f"You swapped your card with center position {center_position}",
        {
            "center_position": center_position,
            "new_role": "Unknown",
            "actual_new_role": new_role.value if new_role else "unknown",
            "drunk_original_role": drunk_original_role.value,
            "center_had": center_original_role.value
        }
    )

