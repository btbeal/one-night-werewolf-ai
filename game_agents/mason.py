from game_context.game_context import GameContext
from game_context.roles import Role
from game_agents.common_tools import NightActionResult
from game_agents.agent_registry import register_agent
from game_agents.base_agent import BaseAgent
import textwrap


@register_agent(Role.MASON)
class MasonAgent(BaseAgent):
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool):
        super().__init__(player_id, player_name, initial_role, is_ai)

    def execute_night_action(self, game_context: GameContext):
        """Execute the automatic mason night action and update personal knowledge"""
        mason_result = see_mason_allies(game_context, self.player_id)
        self.personal_knowledge.append(mason_result.message)
        return mason_result.message

    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        """Handle common tools (Mason has no specific tools)"""
        return self._call_common_tool(name, args, game_context)

    def _get_system_prompt(self):
        night_knowledge = ""
        if self.personal_knowledge:
            night_knowledge = f"\n\nWhat you learned during the night phase:\n" + "\n".join(f"- {knowledge}" for knowledge in self.personal_knowledge)
        
        return textwrap.dedent(
            f"""You are playing a game of One Night Werewolf and have been assigned the role of a Mason! Your name is {self.player_name}.

            You are on the villager team and want to eliminate werewolves. Masons know each other and can work together.

            {night_knowledge}

            Your strategy should be to:
            1. Coordinate with other Masons if they exist
            2. Use your confirmed villager allies to build trust
            3. Help identify werewolves as a trusted group
            4. If you're the only Mason, use that information strategically

            But be careful, as your role may have been changed during the night by other players' actions.

            It is now morning -- time to work with your Mason allies!"""
        )
    
def see_mason_allies(game_context: GameContext, mason_player_id: int) -> NightActionResult:
    """
    Mason sees other masons
    
    Args:
        game_context: Current game state
        mason_player_id: ID of the mason
    
    Returns:
        NightActionResult with other mason information
    """
    all_masons = game_context.get_players_with_role(Role.MASON)
    
    other_masons = [mason_id for mason_id in all_masons if mason_id != mason_player_id]
    
    if not other_masons:
        return NightActionResult(
            True,
            "You looked for other masons but found none. You are the only mason! The masons are always played in pairs. So, the other mason must have started as a center card.",
            {"other_masons": [], "is_only_mason": True}
        )
    
    mason_names = []
    for mason_id in other_masons:
        player = game_context.get_player(mason_id)
        if player:
            mason_names.append(player.player_name)
    
    mason_list = ", ".join(mason_names)
    
    return NightActionResult(
        True,
        f"You looked for other masons and found: {mason_list}",
        {
            "other_masons": other_masons,
            "mason_names": mason_names,
            "is_only_mason": False
        }
    )