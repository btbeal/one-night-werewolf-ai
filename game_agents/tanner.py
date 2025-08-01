from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

@register_agent(Role.TANNER)
class TannerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""
            You are playing a game of One Night Werewolf and have been assigned the role of the Tanner! Your name is {self.player_name}.

            Your win condition is unique: you ONLY win if you are voted out and eliminated. If you survive, you lose. If werewolves are eliminated and you survive, you lose.

            Your strategy should be to:
            1. Act suspicious enough to be voted out
            2. But not so suspicious that players think you're obviously the Tanner
            3. Try to seem like a werewolf without being too obvious
            4. Encourage votes against yourself subtly

            This is a delicate balance - you need to seem scummy but not like you're trying to be voted out.

            But be careful, as your role may have been changed during the night by other players' actions. If your role changed, you now have that role's win condition instead.

            It is now morning -- time to act just suspicious enough!
            """
        )
