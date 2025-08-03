from typing import List
from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult, validate_player_exists, resolve_player_name_to_id
import textwrap

# Seer tool definition
SEER_INVESTIGATE_TOOL = {
    "type": "function",
    "function": {
        "name": "seer_investigate",
        "description": "As the Seer, investigate either another player's card or two center cards (nighttime only)",
        "parameters": {
            "type": "object",
            "properties": {
                "investigation_type": {
                    "type": "string",
                    "enum": ["player", "center"],
                    "description": "Type of investigation: 'player' to look at another player's card, 'center' to look at center cards"
                },
                "target_player_name": {
                    "type": "string",
                    "description": "Name of the player to investigate (required when investigation_type='player')"
                },
                "card_positions": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 0, "maximum": 2},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Exactly 2 center card positions to investigate (required when investigation_type='center')"
                }
            },
            "required": ["investigation_type"]
        }
    }
}

@register_agent(Role.SEER)
class SeerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai, tools=[SEER_INVESTIGATE_TOOL])
        self.nighttime_tool = SEER_INVESTIGATE_TOOL.get("function", {}).get("name")

    def execute_night_action(self, game_context: GameContext):
        """Seer has no automatic night action - they must use the seer_investigate tool"""
        return "As the Seer, you must choose what to investigate using the seer_investigate tool."

    def _get_system_prompt(self, game_context: GameContext = None):
        if game_context and game_context.is_nighttime:
            return self._get_nighttime_prompt(game_context)
        else:
            return self._get_daytime_prompt(game_context)
    
    def _get_nighttime_prompt(self, game_context: GameContext):
        player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            Other players at the table are:
            {player_list}

            It is now nighttime and you must use the "seer_investigate" tool to gain information. You have two options:

            1. Look at another player's card:
               investigation_type: "player", target_player_name: "<player_name>"
               
            2. Look at two center cards:
               investigation_type: "center", card_positions: [<pos1>, <pos2>]
               (positions are 0, 1, or 2)

            Choose wisely!"""
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

            Other players in the game are:
            {player_list}

            At night, you used your special investigative abilities to gain information:
            {night_knowledge}

            You started on the villager team and want to eliminate werewolves.

            Your role is to determine the identity of the werewolf (or werewolves!) and help eliminate them. To do this, you will collaborate with all the players, while the werewolf players will try to deceive you.

            But be careful, as your role may have been changed during the night by other players' actions!"""
        )

def see_player_card(game_context: GameContext, seer_player_id: int, target_player_id: int) -> NightActionResult:
    """
    Seer looks at another player's card
    
    Args:
        game_context: Current game state
        seer_player_id: ID of the seer
        target_player_id: ID of the player whose card to see
    
    Returns:
        NightActionResult with the target's role information
    """
    if target_player_id == seer_player_id:
        return NightActionResult(False, "You cannot look at your own card!")
    
    is_valid, error_msg = validate_player_exists(game_context, target_player_id)
    if not is_valid:
        return NightActionResult(False, error_msg)
    
    target_player = game_context.get_player(target_player_id)
    target_role = game_context.get_player_current_role(target_player_id)
    
    if not target_role:
        return NightActionResult(False, f"Could not determine {target_player.player_name}'s role!")
    
    return NightActionResult(
        True, 
        f"You looked at {target_player.player_name}'s card and saw they are the {target_role.value.title()}",
        {"target_player": target_player_id, "role_seen": target_role.value}
    )


def see_center_cards(game_context: GameContext, seer_player_id: int, card_positions: List[int]) -> NightActionResult:
    """
    Seer looks at center cards (must be exactly 2 cards)
    
    Args:
        game_context: Current game state
        seer_player_id: ID of the seer
        card_positions: List of center card positions to look at (0, 1, or 2)
    
    Returns:
        NightActionResult with center card information
    """
    if len(card_positions) != 2:
        return NightActionResult(False, "You must look at exactly 2 center cards!")
    
    if not all(0 <= pos <= 2 for pos in card_positions):
        return NightActionResult(False, "Center card positions must be 0, 1, or 2!")
    
    roles_seen = []
    for pos in card_positions:
        role = game_context.get_center_card_role(pos)
        if role:
            roles_seen.append(role.value.title())
        else:
            return NightActionResult(False, f"Could not determine center card at position {pos}!")
    
    return NightActionResult(
        True,
        f"You looked at center cards {card_positions} and saw: {', '.join(roles_seen)}",
        {"center_positions": card_positions, "roles_seen": roles_seen}
    )


def seer_investigate(game_context: GameContext, seer_player_id: int, investigation_type: str, target_player_name: str = None, card_positions: list = None) -> str:
    """
    Seer investigate tool - allows the seer to investigate either a player or center cards
    
    Args:
        game_context: Current game state
        seer_player_id: ID of the seer making the investigation
        investigation_type: 'player' or 'center'
        target_player_name: Player name to investigate (required for 'player' type)
        card_positions: List of 2 center card positions (required for 'center' type)
    
    Returns:
        String result of the investigation
    """
    if investigation_type == 'player':
        if target_player_name is None:
            return "Error: target_player_name required for player investigation"
        
        # Resolve player name to ID
        success, resolution_message, target_player_id = resolve_player_name_to_id(
            game_context, target_player_name, seer_player_id
        )
        
        if not success:
            return resolution_message
        
        result = see_player_card(game_context, seer_player_id, target_player_id)
        
        # Add duplicate name warning if needed
        final_message = result.message
        if resolution_message:  # There was a duplicate name warning
            final_message = resolution_message + " " + result.message
        
    elif investigation_type == 'center':
        if not card_positions:
            return "Error: card_positions required for center card investigation"
        
        result = see_center_cards(game_context, seer_player_id, card_positions)
        final_message = result.message
        
    else:
        return "Error: investigation type must be 'player' or 'center'"
    
    # Add successful results to the seer's personal knowledge
    if result.success:
        # Find the seer agent and add to their knowledge
        seer_player = game_context.get_player(seer_player_id)
        if hasattr(seer_player, 'personal_knowledge'):
            seer_player.personal_knowledge.append(final_message)
    
    return final_message
