from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult, validate_player_exists, resolve_player_name_to_id
import textwrap

# Robber tool definition
ROBBER_SWAP_TOOL = {
    "type": "function",
    "function": {
        "name": "robber_swap",
        "description": "As the Robber, swap your card with another player and learn your new role (nighttime only)",
        "parameters": {
            "type": "object",
            "properties": {
                "target_player_name": {
                    "type": "string",
                    "description": "Name of the player to swap cards with"
                }
            },
            "required": ["target_player_name"]
        }
    }
}

@register_agent(Role.ROBBER)
class RobberAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai, tools=[ROBBER_SWAP_TOOL])
        self.nighttime_tool = ROBBER_SWAP_TOOL.get("function", {}).get("name")

    def execute_night_action(self, game_context: GameContext):
        """Robber has no automatic night action - they must use the robber_swap tool"""
        return "As the Robber, you must choose which player to swap cards with using the robber_swap tool."

    def _get_system_prompt(self, game_context: GameContext = None):
        if game_context and game_context.is_nighttime:
            return self._get_nighttime_prompt(game_context)
        else:
            return self._get_daytime_prompt(game_context)
    
    def _get_nighttime_prompt(self, game_context: GameContext):
        player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            Other players in the game are:
            {player_list}

            It is now nighttime and you must use the "robber_swap" tool to swap your card with another player and learn your new role.
            
            Usage: robber_swap with {{"target_player_name": "<player_name>"}}

            Choose wisely!"""
        )
    
    def _get_daytime_prompt(self, game_context: GameContext = None):
        night_knowledge = ""
        if self.personal_knowledge:
            night_knowledge = f"\n\nWhat you learned during the night phase:\n" + "\n".join(f"- {knowledge}" for knowledge in self.personal_knowledge)
        
        player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            Other players in the game are:
            {player_list}

            At night, you used your special abilities to swap your card with another player and learn your new role:
            {night_knowledge}

            Your strategy depends on your new role:
            - If you're now a villager role: Help find the werewolves
            - If you're now a werewolf: Try to blend in and avoid detection (while also protecting those werewolfs from discovery)
            - Share information about the swap strategically

            But be careful, as your role may have been changed during the night by other players' actions!"""
        )

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
    
    robber_original_role = game_context.get_player_current_role(robber_player_id)
    target_original_role = game_context.get_player_current_role(target_player_id)
    
    if not robber_original_role or not target_original_role:
        return NightActionResult(False, "Could not determine player roles for swap!")
    
    success = game_context.swap_player_roles(robber_player_id, target_player_id)
    if not success:
        return NightActionResult(False, "Failed to swap cards!")
    
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


def robber_swap(game_context: GameContext, robber_player_id: int, target_player_name: str) -> str:
    """
    Robber swap tool - allows the robber to swap cards with another player
    
    Args:
        game_context: Current game state
        robber_player_id: ID of the robber making the swap
        target_player_name: Name of the player to swap cards with
    
    Returns:
        String result of the swap
    """
    success, resolution_message, target_player_id = resolve_player_name_to_id(
        game_context, target_player_name, robber_player_id
    )
    
    if not success:
        return resolution_message
    
    result = rob_player_card(game_context, robber_player_id, target_player_id)

    final_message = result.message
    if resolution_message:
        final_message = resolution_message + " " + result.message
    
    if result.success:
        robber_player = game_context.get_player(robber_player_id)
        if hasattr(robber_player, 'personal_knowledge'):
            robber_player.personal_knowledge.append(final_message)
    
    return final_message
