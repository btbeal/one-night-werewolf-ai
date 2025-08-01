from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult, validate_player_exists, validate_different_players
import textwrap


@register_agent(Role.TROUBLEMAKER)
class TroublemakerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
            You are playing a game of One Night Werewolf and have been assigned the role of the Troublemaker! Your name is {self.player_name}.

            During the night, you swapped the cards of two other players (without looking at them). Those players now have each other's original roles, but they don't know about the swap.

            Your strategy should be to:
            1. Reveal your swap information strategically
            2. Help create confusion that benefits the village
            3. Watch for reactions when you reveal the swap
            4. Help identify werewolves based on how players react

            You are on the villager team and want to eliminate werewolves.

            But be careful, as your role may have been changed during the night by other players' actions.

            It is now morning -- time to reveal the chaos you've created!
            """
        )

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
    
    for player_id in [player1_id, player2_id]:
        is_valid, error_msg = validate_player_exists(game_context, player_id)
        if not is_valid:
            return NightActionResult(False, error_msg)
    
    player1 = game_context.get_player(player1_id)
    player2 = game_context.get_player(player2_id)
    
    player1_original_role = game_context.get_player_current_role(player1_id)
    player2_original_role = game_context.get_player_current_role(player2_id)
    
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
            "player1_had": player1_original_role.value if player1_original_role else "unknown",
            "player2_had": player2_original_role.value if player2_original_role else "unknown"
        }
    )
