import textwrap
from .base_agent import BaseAgent
from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.agent_registry import register_agent

@register_agent(Role.VILLAGER)
class VillagerAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)
    
    def execute_night_action(self, game_context: GameContext):
        """Villager has no night action"""
        return "As a Villager, you have no special nighttime abilities."
    
    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle common tools (Villager has no specific tools)"""
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

            Your role is simple but important: you are on the team of villagers and must help identify and vote out the werewolves. You have no special night abilities, but you are a crucial voice in the discussion.

            Your strategy should be to:
            1. Listen carefully to other players' claims
            2. Look for inconsistencies in stories
            3. Help coordinate voting to eliminate werewolves
            4. Be honest about your role (usually)

            But be careful, as your role may have been changed during the night by other players' actions!"""
        ) 