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

    def execute_night_action(self, game_context: GameContext):
        """Insomniac automatically checks their final role at the end of the night"""
        result = check_final_role(game_context, self.player_id, self.initial_role)
        
        if result.success:
            self.personal_knowledge.append(result.message)
        
        return result.message

    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle common tools (Insomniac has no specific tools)"""
        return self._call_common_tool(name, args, game_context)

    def _get_system_prompt(self, game_context: GameContext = None):
        night_knowledge = ""
        if self.personal_knowledge:
            night_knowledge = f"\n\nWhat you learned during the night phase:\n" + "\n".join(f"- {knowledge}" for knowledge in self.personal_knowledge)
        
        player_list = ""
        if game_context:
            player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            {player_list}{night_knowledge}

            As the Insomniac, you woke up at the end of the night to check your final role.

            Your strategy should be to:
            1. Share information about whether your role changed
            2. If it changed, figure out who might have caused the change
            3. Help identify players who performed night actions
            4. Use your information to help the village

            You are on the villager team and want to eliminate werewolves (unless your role changed to werewolf)."""
        )


def check_final_role(game_context: GameContext, insomniac_player_id: int, initial_role: str) -> NightActionResult:
    """
    Insomniac checks their final role after all night actions
    
    Args:
        game_context: Current game state
        insomniac_player_id: ID of the insomniac
        initial_role: The insomniac's original role at game start
    
    Returns:
        NightActionResult with final role information
    """
    current_role = game_context.get_player_current_role(insomniac_player_id)
    
    if not current_role:
        return NightActionResult(False, "Could not determine your current role!")
    
    role_changed = current_role.value.lower() != initial_role.lower()
    
    if role_changed:
        message = f"You checked your card and you are now: {current_role.value.title()} (you were originally {initial_role.title()})"
    else:
        message = f"You checked your card and you are still: {current_role.value.title()}"
    
    return NightActionResult(
        True,
        message,
        {
            "final_role": current_role.value,
            "initial_role": initial_role,
            "role_changed": role_changed
        }
    )
