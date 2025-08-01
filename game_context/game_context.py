from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from .messages import ConversationHistory
from .roles import Role

if TYPE_CHECKING:
    from game_agents.base_agent import BaseAgent


class GameContext(BaseModel):
    """Complete game context including all players and conversation"""
    players: Dict[int, Any] = Field(default_factory=dict)  # Use Any instead of forward reference for now
    conversation: ConversationHistory = Field(default_factory=ConversationHistory)
    # role_assignments removed - not needed for current implementation
    
    class Config:
        arbitrary_types_allowed = True
    
    
    def get_player(self, player_id: int) -> Optional[Any]:
        """Get a player by ID"""
        return self.players.get(player_id)
    
    def get_player_by_name(self, player_name: str) -> Optional[Any]:
        """Get a player by name"""
        for player in self.players.values():
            if player.player_name == player_name:
                return player
        return None
    
    def set_player_vote(self, player_id: int, vote_target: int) -> bool:
        """Set a player's vote target if valid"""
        player = self.get_player(player_id)
        if not player:
            return False
            
        target = self.get_player(vote_target)
        if not target or target.player_id == player_id:
            return False
            
        # Note: You might want to add a vote_target attribute to BaseAgent
        # For now, we'll just return True to indicate the vote is valid
        return True
    
    def get_valid_vote_targets(self, player_id: int) -> List[int]:
        """Get list of valid vote targets for a player"""
        player = self.get_player(player_id)
        if not player:
            return []
            
        return [p.player_id for p in self.players.values() if p.player_id != player_id]
    
    # Role management methods removed - not needed for current implementation