from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

@register_agent(Role.HUNTER)
class HunterAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def execute_night_action(self, game_context: GameContext):
        """Hunter has no night action"""
        return "As a Hunter, you have no special nighttime abilities."

    def _get_system_prompt(self, game_context: GameContext = None):
        night_knowledge = ""
        if self.personal_knowledge:
            night_knowledge = f"\n\nWhat you learned during the night phase:\n" + "\n".join(f"- {knowledge}" for knowledge in self.personal_knowledge)
        
        player_list = ""
        if game_context:
            player_list = game_context.get_other_player_names_in_text(self.player_id)
        
        return textwrap.dedent(
            f"""You are playing One Night Werewolf with the initial role of {self.initial_role}! Your name is {self.player_name}.

            {player_list}{night_knowledge}

            You had no action during the night, but you have a powerful ability: if you are eliminated, the player you voted for is also eliminated.

            Your strategy should be to:
            1. Be very careful about who you vote for
            2. Use your elimination threat as leverage in discussions
            3. Try to identify werewolves before committing to a vote
            4. Consider that werewolves might try to eliminate you to trigger your ability

            You are on the villager team and want to eliminate werewolves.

            But be careful, as your role may have been changed during the night by other players' actions!"""
        )
