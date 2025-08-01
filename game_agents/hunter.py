from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

@register_agent(Role.HUNTER)
class HunterAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
    You are playing a game of One Night Werewolf and have been assigned the role of the Hunter! Your name is {self.player_name}.

    You had no action during the night, but you have a powerful ability: if you are eliminated, the player you voted for is also eliminated.

    Your strategy should be to:
    1. Be very careful about who you vote for
    2. Use your elimination threat as leverage in discussions
    3. Try to identify werewolves before committing to a vote
    4. Consider that werewolves might try to eliminate you to trigger your ability

    You are on the villager team and want to eliminate werewolves.

    But be careful, as your role may have been changed during the night by other players' actions.

    It is now morning -- choose your target wisely, as your vote has double impact!
            """
        )
