import os
from agents import Agent, Runner
from dotenv import load_dotenv
from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.common_tools import NightActionResult

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def see_werewolf_allies(game_context: GameContext, werewolf_player_id: int) -> NightActionResult:
    """
    Werewolf sees other werewolves
    
    Args:
        game_context: Current game state
        werewolf_player_id: ID of the werewolf
    
    Returns:
        NightActionResult with other werewolf information
    """
    # Find all players with werewolf role
    all_werewolves = game_context.get_players_with_role(Role.WEREWOLF)
    
    # Remove self from the list
    other_werewolves = [ww_id for ww_id in all_werewolves if ww_id != werewolf_player_id]
    
    if not other_werewolves:
        return NightActionResult(
            True,
            "You looked for other werewolves but found none. You are the lone werewolf!",
            {"other_werewolves": [], "is_lone_werewolf": True}
        )
    
    # Get names of other werewolves
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


werewolf = Agent(
    name="werewolf",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Werewolf!

    Your role is to deceive the villagers and avoid being voted out. You are on the werewolf team and win if no werewolves are eliminated during the day phase.

    During the night, you saw who the other werewolves are (if any). Work together with them to mislead the villagers, but be subtle about it.

    Your strategy should be to:
    1. Blend in with the villagers
    2. Cast suspicion on innocent players
    3. Defend other werewolves without being obvious
    4. Claim to be a villager role

    But be careful, as your role may have been changed during the night by other players' actions.

    It is now morning -- time to deceive!
    """,
    model="gpt-4o-mini",
)

if __name__ == "__main__":
    print(Runner.run_sync(werewolf, "You're the first player to go! What would you like to say to the group?"))

