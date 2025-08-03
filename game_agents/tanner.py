from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap

@register_agent(Role.TANNER)
class TannerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def execute_night_action(self, game_context: GameContext):
        """Tanner has no night action"""
        return "As a Tanner, you have no special nighttime abilities."

    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle common tools (Tanner has no specific tools)"""
        return self._call_common_tool(name, args, game_context)

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

            Your win condition is unique: you ONLY win if you are voted out and eliminated. If you survive, you lose. If werewolves are eliminated and you survive, you lose.

            Your strategy should be to:
            1. Act suspicious enough to be voted out
            2. But not so suspicious that players think you're obviously the Tanner
            3. Try to seem like a werewolf without being too obvious
            4. Encourage votes against yourself subtly

            This is a delicate balance - you need to seem scummy but not like you're trying to be voted out.

            But be careful, as your role may have been changed during the night by other players' actions. If your role changed, you now have that role's win condition instead!"""
        )
