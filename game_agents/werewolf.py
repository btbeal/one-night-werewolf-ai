import textwrap
from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.common_tools import NightActionResult
from game_agents.base_agent import BaseAgent
from .agent_registry import register_agent


def see_werewolf_allies(game_context: GameContext, werewolf_player_id: int) -> NightActionResult:
    """
    Nightime action: since you are the werewolf, once at the beginning of the game (during the night phase),
    you can see who the other werewolves are (your teammates). If you are the only werewolf, you are the lone werewolf but you 
    can look at one card in the middle! If this is a werewolf, you may look at another card in the middle. 
    
    Args:
        game_context: Current game state
        werewolf_player_id: ID of the werewolf
    
    Returns:
        NightActionResult with other werewolf information
    """
    all_werewolves = game_context.get_players_with_role(Role.WEREWOLF)
    other_werewolves = [ww_id for ww_id in all_werewolves if ww_id != werewolf_player_id]
    
    if not other_werewolves:
        return NightActionResult(
            True,
            "You looked for other werewolves but found none. You are the lone werewolf!",
            {"other_werewolves": [], "is_lone_werewolf": True}
        )
    
    werewolf_names = []
    for ww_id in other_werewolves:
        player = game_context.get_player(ww_id)
        if player:
            werewolf_names.append(player.player_name)
    
    werewolf_list = ", ".join(werewolf_names)
    
    return NightActionResult(
        True,
        f"You looked for other werewolves and found: {werewolf_list}",
        {
            "other_werewolves": other_werewolves,
            "werewolf_names": werewolf_names,
            "is_lone_werewolf": False
        }
    )

@register_agent(Role.WEREWOLF)
class WerewolfAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)
    
    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""You are playing a game of One Night Werewolf!

                You are playing as {self.player_name} and your initial role is Werewolf.

                Your role is to deceive the villagers and avoid being voted out. 
                You are on the werewolf team and win if no werewolves are eliminated during the day phase.

                During the night, you saw who the other werewolves are (if any). Work together with them to mislead the villagers, 
                but be subtle about it.

                Your strategy should be to:
                1. Blend in with the villagers
                2. Cast suspicion on innocent players
                3. Defend other werewolves without being obvious
                4. Claim to be a villager role

                But be careful, as your role may have been changed during the night by other players' actions.

                It is now morning -- time to deceive!"""
        )
