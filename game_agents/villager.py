import textwrap
from .base_agent import BaseAgent
from game_context.roles import Role
from game_agents.agent_registry import register_agent

@register_agent(Role.VILLAGER)
class VillagerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)
    
    def _get_system_prompt(self):
        return textwrap.dedent(
            f"""You are playing a game of One Night Werewolf!

                You are playing as {self.player_name} and your initial role is a Villager.

                Your role is simple but important: you are on the team of villagers and must help identify and vote out the werewolves. You have no special night abilities, but you are a crucial voice in the discussion.

                Your strategy should be to:
                1. Listen carefully to other players' claims
                2. Look for inconsistencies in stories
                3. Help coordinate voting to eliminate werewolves
                4. Be honest about your role (usually)

                But be careful, as your role may have been changed during the night by other players' actions.

                It is now morning -- use your voice and vote wisely!"""
        ) 