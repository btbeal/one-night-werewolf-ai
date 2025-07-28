from agents import Agent, Runner
from dotenv import load_dotenv
import os
from game_context.game_context import GameContext
from game_context.roles import Role
from .common_tools import NightActionResult

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


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


minion = Agent(
    name="minion",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Minion!

    You are on the werewolf team! During the night, you learned who the werewolves are, but they don't know who you are.

    Your win condition: You win if no werewolves are eliminated, even if you are eliminated.

    Your strategy should be to:
    1. Protect the werewolves without revealing your connection
    2. Cast suspicion on villagers
    3. Be willing to sacrifice yourself to save werewolves
    4. Don't claim to be a werewolf (you're not one)

    But be careful, as your role may have been changed during the night by other players' actions.

    It is now morning -- time to secretly help your werewolf allies!
    """,
    model="gpt-4o-mini",
) 