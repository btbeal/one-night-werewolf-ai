from typing import List
from .messages import MessageType
from .game_context import GameContext


class GameSession:
    """Custom session implementation following the Session protocol for OpenAI Agents SDK."""
    # See notes here: https://github.com/openai/openai-agents-python

    def __init__(self, session_id: str, game_context: GameContext):
        self.session_id = session_id
        self.game_context = game_context

    async def get_items(self, limit: int | None = None) -> List[dict]:
        """Retrieve conversation history for the session"""
        messages = self.game_context.conversation.messages

        items = []
        for msg in messages:
            item = {
                "role": "user" if msg.player_id > 0 else "assistant",
                "content": msg.message,
                "timestamp": msg.timestamp.isoformat(),
                "message_id": msg.message_id,
                "player_id": msg.player_id,
                "message_type": msg.message_type.value
            }
            items.append(item)

        if limit is not None:
            items = items[-limit:]  # Get the most recent items
            
        return items

    async def add_items(self, items: List[dict]) -> None:
        """Store new items for the session"""
        for item in items:
            player_id = item.get("player_id", 0) 
            message = item.get("content", "")
            message_type_str = item.get("message_type", "chat")

            try:
                message_type = MessageType(message_type_str)
            except ValueError:
                message_type = MessageType.CHAT

            self.game_context.conversation.add_message(
                player_id=player_id,
                message=message,
                message_type=message_type
            )

    async def pop_item(self) -> dict | None:
        """Remove and return the most recent item from the session"""
        if not self.game_context.conversation.messages:
            return None
            
        # Remove and get the last message
        last_message = self.game_context.conversation.messages.pop()
        
        # Convert to dict format
        item = {
            "role": "user" if last_message.player_id > 0 else "assistant",
            "content": last_message.message,
            "timestamp": last_message.timestamp.isoformat(),
            "message_id": last_message.message_id,
            "player_id": last_message.player_id,
            "message_type": last_message.message_type.value
        }
        
        return item

    async def clear_session(self) -> None:
        """Clear all items for the session"""
        self.game_context.conversation.messages.clear()
        self.game_context.conversation.next_message_id = 1

    def get_game_context(self) -> GameContext:
        """Get the underlying game context"""
        return self.game_context