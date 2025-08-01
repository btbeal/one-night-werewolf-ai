from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from .messages import ConversationHistory
from .roles import Role

if TYPE_CHECKING:
    from game_agents.base_agent import BaseAgent


class GameContext(BaseModel):
    """Complete game context including all players and conversation"""
    players: Dict[int, Any] = Field(default_factory=dict)
    conversation: ConversationHistory = Field(default_factory=ConversationHistory)
    center_cards: List[Role] = Field(default_factory=list)
    
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
            
        return True
    
    def get_valid_vote_targets(self, player_id: int) -> List[int]:
        """Get list of valid vote targets for a player"""
        player = self.get_player(player_id)
        if not player:
            return []
            
        return [p.player_id for p in self.players.values() if p.player_id != player_id]
    
    def initialize_center_cards(self, center_role_enums: List[Role]) -> None:
        """Initialize center cards"""
        self.center_cards = center_role_enums.copy()
        if len(self.center_cards) != 3:
            raise ValueError("Must have exactly 3 center cards")
    
    def get_player_current_role(self, player_id: int) -> Optional[Role]:
        """Get the current role of a player from the agent"""
        player = self.get_player(player_id)
        if player:
            return Role(player.current_role.lower())
        return None
    
    def set_player_role(self, player_id: int, role: Role) -> None:
        """Set/update a player's role (used for swapping)"""
        player = self.get_player(player_id)
        if player:
            player.current_role = role.value
    
    def get_center_card_role(self, position: int) -> Optional[Role]:
        """Get the role of a center card at given position (0, 1, or 2)"""
        if 0 <= position < len(self.center_cards):
            return self.center_cards[position]
        return None
    
    def set_center_card_role(self, position: int, role: Role) -> None:
        """Set/update a center card role (used for swapping)"""
        if 0 <= position < len(self.center_cards):
            self.center_cards[position] = role
    
    def get_role_assignments_summary(self) -> Dict[str, Any]:
        """Get a summary of all role assignments"""
        player_roles = {pid: player.current_role for pid, player in self.players.items()}
        center_cards = [role.value for role in self.center_cards]
        return {
            "player_roles": player_roles,
            "center_cards": center_cards
        }