from typing import List
from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult, validate_player_exists
import textwrap

@register_agent(Role.SEER)
class SeerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
            You are playing a game of One Night Werewolf and have been assigned the role of the Seer! Your name is {self.player_name}.

            Your role, as someone who is on the team of villagers, is to determine the identity of the werewolf (or werewolves!).
            To do this, you will collaborate with all the players, while the werewolf players will try to deceive you.

            But be careful, as your role may have been changed in the night. 

            During the night, you saw the identity of player 1. They were the Troublemaker.

            It is now morning -- best of luck!
            """
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
