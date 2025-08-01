# One Night Werewolf Game Context Package
"""
This package manages all game context including messages, roles, game state, and sessions.

Modules:
- messages: Message types and conversation history
- roles: Role definitions and assignment tracking
- game_state: Game and player state management  
- game_context: Main context that ties everything together
- session: OpenAI SDK session implementation
"""

from .messages import Message, ConversationHistory
from .roles import Role, RoleAssignment
from .game_context import GameContext

__all__ = [
    'Message', 
    'ConversationHistory',
    'Role',
    'RoleAssignment',
    'GameContext'
]