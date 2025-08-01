from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.common_tools import NightActionResult
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
from game_agents.common_tools import NightActionResult
import textwrap


@register_agent(Role.MINION)    
class MinionAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
            You are playing a game of One Night Werewolf and have been assigned the role of the Minion! Your name is {self.player_name}.

            You are on the werewolf team! During the night, you learned who the werewolves are, but they don't know who you are.

            Your win condition: You win if no werewolves are eliminated, even if you are eliminated.

            Your strategy should be to:
            1. Protect the werewolves without revealing your connection
            2. Cast suspicion on villagers
            3. Be willing to sacrifice yourself to save werewolves
            4. Don't claim to be a werewolf (you're not one)
            """
        )

def see_all_werewolves(game_context: GameContext, minion_player_id: int) -> NightActionResult:
    """
    Minion sees all werewolves
    
    Args:
        game_context: Current game state
        minion_player_id: ID of the minion
    
    Returns:
        NightActionResult with werewolf information
    """
    all_werewolves = game_context.get_players_with_role(Role.WEREWOLF)
    
    if not all_werewolves:
        return NightActionResult(
            True,
            "You looked for werewolves but found none! There are no werewolves among the players.",
            {"werewolves": [], "werewolf_names": [], "no_werewolves": True}
        )
    
    werewolf_names = []
    for ww_id in all_werewolves:
        player = game_context.get_player(ww_id)
        if player:
            werewolf_names.append(player.player_name)
    
    werewolf_list = ", ".join(werewolf_names)
    
    return NightActionResult(
        True,
        f"You identified the werewolves: {werewolf_list}",
        {
            "werewolves": all_werewolves,
            "werewolf_names": werewolf_names,
            "no_werewolves": False
        }
    )
