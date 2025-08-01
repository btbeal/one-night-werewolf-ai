from pydantic import BaseModel, Field
from typing import List, Dict, Set, Optional, Any
from datetime import datetime
from enum import Enum
from collections import deque


class Message(BaseModel):
    """Individual message in the conversation"""
    message_id: int
    player_id: int
    player_name: str
    public_response: str
    private_thoughts: str = ""
    tool_calls: List[Dict] = Field(default_factory=list)
    raw_response: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationHistory(BaseModel):
    """Manages the complete conversation history"""
    messages: deque = Field(default_factory=deque)
    next_message_id: int = 1
    
    def add_agent_response(
        self,
        player_id: int,
        player_name: str,
        public_response: str,
        private_thoughts: str = "",
        tool_calls: List[Dict] = None,
        raw_response: str = ""
    ) -> Message:
        """Add a full agent response to the conversation"""
        
        new_message = Message(
            message_id=self.next_message_id,
            player_id=player_id,
            player_name=player_name,
            public_response=public_response,
            private_thoughts=private_thoughts,
            tool_calls=tool_calls or [],
            raw_response=raw_response
        )
        
        self.messages.append(new_message)
        self.next_message_id += 1
        return new_message
    
    def get_public_conversation_history(self) -> str:
        """Get only the public conversation history (what players actually said)"""
        return self._get_plain_text_conversation_history(include_private_thoughts=False, include_tool_calls=False)
    
    def get_full_conversation_history(self) -> str:
        """Get the full conversation history including private thoughts and tool calls (for debugging)"""
        return self._get_plain_text_conversation_history(include_private_thoughts=True, include_tool_calls=True)
    
    def get_player_private_thoughts(self, player_id: int) -> List[str]:
        """Get all private thoughts for a specific player"""
        return [
            message.private_thoughts 
            for message in self.messages 
            if message.player_id == player_id and message.private_thoughts.strip()
        ]
    
    def _get_plain_text_conversation_history(self, include_private_thoughts: bool = False, include_tool_calls: bool = False) -> str:
        """Get conversation history as plain text, with optional private thoughts and tool calls"""
        if not self.messages:
            return "No conversation history yet."
            
        formatted = []
        for message in self.messages:
            if message.public_response.strip():
                formatted.append(f"{message.player_name}: {message.public_response}")
            
            if include_private_thoughts and message.private_thoughts.strip():
                formatted.append(f"[{message.player_name}'s private thoughts: {message.private_thoughts}]")
            
            if include_tool_calls and message.tool_calls:
                for tool_call in message.tool_calls:
                    formatted.append(f"[{message.player_name} used tool {tool_call['name']}: {tool_call.get('result', 'No result')}]")
        
        return "\n".join(formatted)