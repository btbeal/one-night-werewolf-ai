from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap
from game_agents.common_tools import NightActionResult


@register_agent(Role.INSOMNIAC)
class InsomniacAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
            You are playing a game of One Night Werewolf and have been assigned the role of the Insomniac! Your name is {self.player_name}.

            At the end of the night, you woke up and checked your card to see if it had changed. 

            Your strategy should be to:
            1. Share information about whether your role changed
            2. If it changed, figure out who might have caused the change
            3. Help identify players who performed night actions
            4. Use your information to help the village

            You are on the villager team and want to eliminate werewolves.

            It is now morning -- share what you learned from your restless night!
            """
        )


def check_final_role(game_context: GameContext, insomniac_player_id: int) -> NightActionResult:
    """
    Insomniac checks their final role after all night actions
    
    Args:
        game_context: Current game state
        insomniac_player_id: ID of the insomniac
    
    Returns:
        NightActionResult with final role information
    """
    current_role = game_context.get_player_current_role(insomniac_player_id)
    original_role = game_context.get_player_original_role(insomniac_player_id)
    
    if not current_role:
        return NightActionResult(False, "Could not determine your current role!")
    
    if not original_role:
        return NightActionResult(False, "Could not determine your original role!")
    
    role_changed = current_role != original_role
    
    if role_changed:
        message = f"You checked your card and you are now: {current_role.value.title()} (you were originally {original_role.value.title()})"
    else:
        message = f"You checked your card and you are still: {current_role.value.title()}"
    
    return NightActionResult(
        True,
        message,
        {
            "final_role": current_role.value,
            "original_role": original_role.value,
            "role_changed": role_changed
        }
    )
