from pydantic import BaseModel, Field
from typing import List, Dict, Set, Optional, Any
from datetime import datetime
from enum import Enum
from collections import deque


class MessageType(str, Enum):
    """Types of messages in the game"""
    CHAT = "chat"
    VOTE = "vote"
    ACCUSATION = "accusation"
    DEFENSE = "defense"


class Message(BaseModel):
    """Individual message in the conversation"""
    message_id: int
    player_id: int
    message: str
    message_type: MessageType = MessageType.CHAT
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationHistory(BaseModel):
    """Manages the complete conversation history"""
    messages: deque = Field(default_factory=deque)
    next_message_id: int = 1
    
    def add_message(
        self, 
        player_id: int, 
        message: str, 
        message_type: MessageType = MessageType.CHAT
    ) -> Message:
        """Add a new message to the conversation"""
        
        new_message = Message(
            message_id=self.next_message_id,
            player_id=player_id,
            message=message,
            message_type=message_type
        )
        
        self.messages.append(new_message)
        self.next_message_id += 1
        return new_message