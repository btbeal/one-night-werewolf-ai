from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class Role(str, Enum):
    """All possible roles in One Night Werewolf"""
    # Village team
    VILLAGER = "villager"
    SEER = "seer"
    ROBBER = "robber"
    TROUBLEMAKER = "troublemaker"
    DRUNK = "drunk"
    INSOMNIAC = "insomniac"
    MASON = "mason"
    HUNTER = "hunter"
    
    # Werewolf team
    WEREWOLF = "werewolf"
    MINION = "minion"
    
    # Solo team
    TANNER = "tanner"


class RoleAssignment(BaseModel):
    """Tracks role assignments and swaps throughout the game"""
    player_roles: Dict[int, Role] = Field(default_factory=dict)
    original_player_roles: Dict[int, Role] = Field(default_factory=dict)
    center_roles: List[Role] = Field(default_factory=list)
    original_center_roles: List[Role] = Field(default_factory=list)
    
    def initialize_roles(self, player_roles: Dict[int, Role], center_cards: List[Role]) -> None:
        """Initialize the role assignments at game start"""
        self.player_roles = player_roles.copy()
        self.original_player_roles = player_roles.copy()
        self.center_roles = center_cards.copy()
        self.original_center_roles = center_cards.copy()
    
    def get_player_role(self, player_id: int) -> Optional[Role]:
        """Get current role of a player"""
        return self.player_roles.get(player_id)
    
    def get_original_player_role(self, player_id: int) -> Optional[Role]:
        """Get original role of a player"""
        return self.original_player_roles.get(player_id)
    
    def get_center_card(self, position: int) -> Optional[Role]:
        """Get current center card at position (0, 1, or 2)"""
        if 0 <= position < len(self.center_roles):
            return self.center_roles[position]
        return None
    
    def get_original_center_card(self, position: int) -> Optional[Role]:
        """Get original center card at position (0, 1, or 2)"""
        if 0 <= position < len(self.original_center_roles):
            return self.original_center_roles[position]
        return None
    
    def swap_player_cards(self, player1_id: int, player2_id: int) -> bool:
        """Swap cards between two players"""
        if player1_id not in self.player_roles or player2_id not in self.player_roles:
            return False
        
        # Perform the swap
        role1 = self.player_roles[player1_id]
        role2 = self.player_roles[player2_id]
        
        self.player_roles[player1_id] = role2
        self.player_roles[player2_id] = role1
        
        return True
    
    def swap_player_with_center(self, player_id: int, center_position: int) -> bool:
        """Swap player card with center card"""
        if player_id not in self.player_roles:
            return False
        
        if not (0 <= center_position < len(self.center_roles)):
            return False
        
        # Perform the swap
        player_role = self.player_roles[player_id]
        center_role = self.center_roles[center_position]
        
        self.player_roles[player_id] = center_role
        self.center_roles[center_position] = player_role
        
        return True
    
    def get_players_with_role(self, role: Role) -> List[int]:
        """Get all player IDs who currently have a specific role"""
        return [player_id for player_id, player_role in self.player_roles.items() 
                if player_role == role]
    
    def get_all_roles_summary(self) -> Dict[str, Any]:
        """Get a summary of all current role assignments"""
        return {
            "player_roles": {str(pid): role.value for pid, role in self.player_roles.items()},
            "center_cards": [role.value for role in self.center_roles],
            "original_player_roles": {str(pid): role.value for pid, role in self.original_player_roles.items()},
            "original_center_cards": [role.value for role in self.original_center_roles]
        }