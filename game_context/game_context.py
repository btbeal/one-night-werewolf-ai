from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from .messages import ConversationHistory
from .roles import Role

# Define the order in which roles act during the night phase
NIGHT_PHASE_ORDER = [
    "werewolf",      # Werewolves see each other
    "minion",        # Minion sees werewolves  
    "mason",         # Masons see each other
    "seer",          # Seer looks at player or center cards
    "robber",        # Robber swaps with player
    "troublemaker",  # Troublemaker swaps two other players
    "drunk",         # Drunk swaps with center card
    "insomniac"      # Insomniac checks their final role
]

if TYPE_CHECKING:
    from game_agents.base_agent import BaseAgent


class GameContext(BaseModel):
    """Complete game context including all players and conversation"""
    players: Dict[int, Any] = Field(default_factory=dict)
    conversation: ConversationHistory = Field(default_factory=ConversationHistory)
    center_cards: List[Role] = Field(default_factory=list)
    
    # Phase tracking
    is_nighttime: bool = True  # Game starts in nighttime phase
    night_phase_order: List[str] = Field(default_factory=lambda: NIGHT_PHASE_ORDER.copy())
    night_actions_completed: Dict[str, bool] = Field(default_factory=dict)
    
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
    
    def get_players_with_role(self, role: Role) -> List[int]:
        """Get list of player IDs who have the specified role"""
        return [
            player_id for player_id, player in self.players.items()
            if player.current_role.lower() == role.value.lower()
        ]
    
    # Phase management methods
    def set_nighttime(self, is_night: bool) -> None:
        """Set the current game phase"""
        self.is_nighttime = is_night
        if is_night:
            # Reset night actions when entering night phase
            self.night_actions_completed.clear()
    
    def mark_night_action_completed(self, role: str) -> None:
        """Mark a role's nighttime action as completed"""
        self.night_actions_completed[role] = True
    
    def is_night_action_completed(self, role: str) -> bool:
        """Check if a role's nighttime action has been completed"""
        return self.night_actions_completed.get(role, False)
    
    def get_next_night_role(self) -> Optional[str]:
        """Get the next role that should act during the night phase"""
        for role in self.night_phase_order:
            if not self.is_night_action_completed(role):
                # Check if any player has this role
                for player in self.players.values():
                    if player.current_role.lower() == role:
                        return role
        return None  # All night actions completed

    def get_other_player_names(self, excluding_player_id: int) -> List[str]:
        """Get list of other players' names, excluding the specified player"""
        return [
            player.player_name for player_id, player in self.players.items() 
            if player_id != excluding_player_id
        ]

    def get_other_player_names_in_text(self, excluding_player_id: int) -> str:
        """Get list of other players' names, excluding the specified player, in text format"""
        other_players = self.get_other_player_names(excluding_player_id)
        if other_players:
            return f"The names of the other players in the game are: {', '.join(other_players)}"
        return ""