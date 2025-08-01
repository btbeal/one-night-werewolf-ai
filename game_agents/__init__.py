# One Night Werewolf AI Agents
"""
This package contains all the AI agents for different roles in One Night Werewolf.

Each agent is configured with role-specific instructions and strategies.
The agents use the OpenAI Agents SDK to participate in the game.

Common Tools:
- common_tools.py: Shared functionality including NightActionResult class and validation utilities

Night Action Tools:
Each agent file that has night actions also contains the corresponding tool functions:
- seer.py: see_player_card(), see_center_cards()
- robber.py: rob_player_card()
- troublemaker.py: troublemaker_swap()
- drunk.py: drunk_swap_center()
- werewolf.py: see_werewolf_allies()
- minion.py: see_all_werewolves()
- mason.py: see_mason_allies()
- insomniac.py: check_final_role()

Roles without night actions: villager, hunter, tanner
"""

# Import our BaseAgent system
from .base_agent import BaseAgent, ONWAgentResponse
from .agent_registry import ROLE_TO_AGENT_CLASS

# Import specific agent classes
from .werewolf import WerewolfAgent
from .villager import VillagerAgent

__all__ = [
    'BaseAgent',
    'ONWAgentResponse',
    'ROLE_TO_AGENT_CLASS',
    'WerewolfAgent',
    'VillagerAgent'
] 