from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult, validate_center_position, resolve_player_name_to_id
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

# Drunk tool definition
DRUNK_SWAP_TOOL = {
    "type": "function",
    "function": {
        "name": "drunk_swap",
        "description": "As the Drunk, swap your card with a center card (nighttime only)",
        "parameters": {
            "type": "object",
            "properties": {
                "center_position": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 2,
                    "description": "Center card position to swap with (0, 1, or 2)"
                }
            },
            "required": ["center_position"]
        }
    }
}

@register_agent(Role.DRUNK)
class DrunkAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai, tools=[DRUNK_SWAP_TOOL])
        self.nighttime_tool = DRUNK_SWAP_TOOL.get("function", {}).get("name")

    def execute_night_action(self, game_context: GameContext):
        """Drunk has no automatic night action - they must use the drunk_swap tool"""
        return "As the Drunk, you must choose which center card to swap with using the drunk_swap tool."
    
    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle Drunk-specific tools and common tools"""
        if not self.is_tool_available(name, game_context):
            return f"The tool '{name}' is not available during the current game phase."
        
        if name == "drunk_swap":
            result = drunk_swap(
                game_context=game_context,
                drunk_player_id=self.player_id,
                center_position=args.get('center_position')
            )
            
            if result and isinstance(result, str) and not result.startswith("Error:"):
                self.personal_knowledge.append(result)
            
            return result
        else:
            return self._call_common_tool(name, args, game_context)

    def _get_system_prompt(self, game_context: GameContext = None):
        if game_context and game_context.is_nighttime:
            return self._get_nighttime_prompt(game_context)
        else:
            return self._get_daytime_prompt(game_context)
    
    def _get_nighttime_prompt(self, game_context: GameContext):
        player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            {player_list}

            It is now nighttime and you must use the "drunk_swap" tool to swap your card with a center card.
            
            Usage: drunk_swap with {{"center_position": <0, 1, or 2>}}
            
            Choose wisely - you won't see either card, so you'll have no idea what your new role is!"""
        )
    
    def _get_daytime_prompt(self, game_context: GameContext = None):
        night_knowledge = ""
        if self.personal_knowledge:
            night_knowledge = f"\n\nWhat you learned during the night phase:\n" + "\n".join(f"- {knowledge}" for knowledge in self.personal_knowledge)
        
        player_list = ""
        if game_context:
            player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            {player_list}{night_knowledge}

            During the night, you swapped your card with a center card, but you didn't look at your new role. You have no idea what role you now have!

            Your strategy should be to:
            1. Be honest about being the original Drunk
            2. Explain that you don't know your current role
            3. Try to figure out what role you might have based on game flow
            4. Help the village as best you can with limited information

            But be careful, because you could be a werewolf now if you grabbed a werewolf card from the center during the night!"""
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


def drunk_swap(game_context: GameContext, drunk_player_id: int, center_position: int) -> str:
    """
    Drunk swap tool - allows the drunk to swap with a center card
    
    Args:
        game_context: Current game state
        drunk_player_id: ID of the drunk making the swap
        center_position: Center card position to swap with (0, 1, or 2)
    
    Returns:
        String result of the swap
    """
    result = drunk_swap_center(game_context, drunk_player_id, center_position)
    return result.message

