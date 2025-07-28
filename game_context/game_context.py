from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from .messages import ConversationHistory
from .roles import Role, RoleAssignment
from .game_state import GameState, PlayerState


class GameContext(BaseModel):
    """Complete game context including all players and conversation"""
    game_state: GameState
    players: Dict[int, PlayerState] = Field(default_factory=dict)
    conversation: ConversationHistory = Field(default_factory=ConversationHistory)
    role_assignments: RoleAssignment = Field(default_factory=RoleAssignment)
    
    def add_player(self, player_id: int, player_name: str, is_ai: bool = False) -> PlayerState:
        """Add a new player to the game"""
        player = PlayerState(
            player_id=player_id,
            player_name=player_name,
            is_ai=is_ai
        )
        self.players[player_id] = player
        return player
    
    def get_player(self, player_id: int) -> Optional[PlayerState]:
        """Get a player by ID"""
        return self.players.get(player_id)
    
    def set_player_vote(self, player_id: int, vote_target: int) -> bool:
        """Set a player's vote target if valid"""
        player = self.get_player(player_id)
        if not player:
            return False
            
        target = self.get_player(vote_target)
        if not target or target.player_id == player_id:
            return False
            
        player.vote_target = vote_target
        return True
    
    def get_valid_vote_targets(self, player_id: int) -> List[int]:
        """Get list of valid vote targets for a player"""
        player = self.get_player(player_id)
        if not player:
            return []
            
        return [p.player_id for p in self.players.values() if p.player_id != player_id]
    
    # Role management methods
    def initialize_game_roles(self, player_role_assignments: Dict[int, Role], center_cards: List[Role]) -> None:
        """Initialize the game with role assignments"""
        self.role_assignments.initialize_roles(player_role_assignments, center_cards)
    
    def get_player_current_role(self, player_id: int) -> Optional[Role]:
        """Get the current role of a player"""
        return self.role_assignments.get_player_role(player_id)
    
    def get_player_original_role(self, player_id: int) -> Optional[Role]:
        """Get the original role of a player"""
        return self.role_assignments.get_original_player_role(player_id)
    
    def get_center_card_role(self, position: int) -> Optional[Role]:
        """Get the current role of a center card"""
        return self.role_assignments.get_center_card(position)
    
    def swap_player_roles(self, player1_id: int, player2_id: int) -> bool:
        """Swap roles between two players (for Troublemaker)"""
        return self.role_assignments.swap_player_cards(player1_id, player2_id)
    
    def swap_player_with_center(self, player_id: int, center_position: int) -> bool:
        """Swap player role with center card (for Robber/Drunk)"""
        return self.role_assignments.swap_player_with_center(player_id, center_position)
    
    def get_players_with_role(self, role: Role) -> List[int]:
        """Get all players who currently have a specific role"""
        return self.role_assignments.get_players_with_role(role)
    
    def get_role_assignments_summary(self) -> Dict[str, Any]:
        """Get a complete summary of all role assignments"""
        return self.role_assignments.get_all_roles_summary()