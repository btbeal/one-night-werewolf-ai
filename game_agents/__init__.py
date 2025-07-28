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

# Import Agent and Runner from the external openai-agents package
try:
    from agents import Agent, Runner
except ImportError as e:
    # Provide a helpful error message if openai-agents is not installed
    raise ImportError(
        "Could not import Agent and Runner from openai-agents package. "
        "Make sure 'openai-agents' is installed with: pip install openai-agents"
    ) from e

# Import all agents for easy access
from .seer import seer
from .werewolf import werewolf
from .villager import villager
from .robber import robber
from .troublemaker import troublemaker
from .tanner import tanner
from .drunk import drunk
from .insomniac import insomniac
from .minion import minion
from .mason import mason
from .hunter import hunter

__all__ = [
    # External classes from openai-agents package
    'Agent',
    'Runner',
    # Local agent instances
    'seer',
    'werewolf', 
    'villager',
    'robber',
    'troublemaker', 
    'tanner',
    'drunk',
    'insomniac',
    'minion',
    'mason',
    'hunter'
] 