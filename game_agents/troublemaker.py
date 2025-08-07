from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult, validate_player_exists, validate_different_players, resolve_player_name_to_id
import textwrap

# Troublemaker tool definition
TROUBLEMAKER_SWAP_TOOL = {
    "type": "function",
    "function": {
        "name": "troublemaker_swap",
        "description": "As the Troublemaker, swap the cards of two other players (nighttime only)",
        "parameters": {
            "type": "object",
            "properties": {
                "player1_name": {
                    "type": "string",
                    "description": "Name of the first player to swap cards with"
                },
                "player2_name": {
                    "type": "string",
                    "description": "Name of the second player to swap cards with"
                }
            },
            "required": ["player1_name", "player2_name"],
            "additionalProperties": False
        },
        "strict": True
    }
}

@register_agent(Role.TROUBLEMAKER)
class TroublemakerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai, nighttime_tools=[TROUBLEMAKER_SWAP_TOOL])
        self.nighttime_tool = TROUBLEMAKER_SWAP_TOOL.get("function", {}).get("name")

    def execute_night_action(self, game_context: GameContext):
        """Troublemaker has no automatic night action - they must use the troublemaker_swap tool"""
        return "As the Troublemaker, you must choose which two players to swap using the troublemaker_swap tool."
    
    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle Troublemaker-specific tools and common tools"""
        if not self.is_tool_available(name, game_context):
            return f"The tool '{name}' is not available during the current game phase."
        
        if name == "troublemaker_swap":
            result = troublemaker_swap(
                game_context=game_context,
                troublemaker_player_id=self.player_id,
                player1_name=args.get('player1_name'),
                player2_name=args.get('player2_name')
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

            It is now nighttime and you must use the "troublemaker_swap" tool to swap the cards of two other players.
            
            Usage: troublemaker_swap with {{"player1_name": "<player_name>", "player2_name": "<player_name>"}}
            
            Choose strategically - you won't see their cards, but the swap will create chaos that can help the village!"""
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

            During the night, you swapped the cards of two other players (without looking at them). Those players now have each other's original roles, but they don't know about the swap.

            Your strategy should be to:
            1. Reveal your swap information strategically
            2. Help create confusion that benefits the village
            3. Watch for reactions when you reveal the swap
            4. Help identify werewolves based on how players react

            You are on the villager team and want to eliminate werewolves.

            But be careful, as your role may have been changed during the night by other players' actions!"""
        )

def swap_two_players(game_context: GameContext, troublemaker_player_id: int, player1_id: int, player2_id: int) -> NightActionResult:
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


def troublemaker_swap(game_context: GameContext, troublemaker_player_id: int, player1_name: str, player2_name: str) -> str:
    """
    Troublemaker swap tool - allows the troublemaker to swap two other players' cards
    
    Args:
        game_context: Current game state
        troublemaker_player_id: ID of the troublemaker making the swap
        player1_name: Name of the first player to swap
        player2_name: Name of the second player to swap
    
    Returns:
        String result of the swap
    """
    # Resolve player names to IDs
    success1, resolution_message1, player1_id = resolve_player_name_to_id(
        game_context, player1_name, troublemaker_player_id
    )
    
    if not success1:
        return resolution_message1
    
    success2, resolution_message2, player2_id = resolve_player_name_to_id(
        game_context, player2_name, troublemaker_player_id
    )
    
    if not success2:
        return resolution_message2
    
    # Perform the swap
    result = swap_two_players(game_context, troublemaker_player_id, player1_id, player2_id)
    
    # Combine any duplicate name warnings
    warnings = []
    if resolution_message1:
        warnings.append(resolution_message1)
    if resolution_message2:
        warnings.append(resolution_message2)
    
    final_message = result.message
    if warnings:
        final_message = " ".join(warnings) + " " + result.message
    
    return final_message
